#!/usr/bin/env node
// design-loop.mjs — 本地同步的合同评审循环。
// 零依赖。需要 node 18+、git、gh，以及两个能从 stdin 读提示词、向 stdout 写回答的 CLI。
// 用法：在目标仓库的 PR 分支上运行
//   node design-loop.mjs <PR号> <任务目录> [--resume]
// 任务目录里必须有 brief.md 和 contract.md。
// 退出码：0 = 合同通过；2 = 已暂停，需要用户决定；1 = 运行错误。
import { spawnSync } from 'node:child_process';
import { readFileSync, existsSync } from 'node:fs';
import { dirname, join, posix } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const argv = process.argv.slice(2);
const RESUME = argv.includes('--resume');
const [PR, TASK_DIR] = argv.filter((a) => !a.startsWith('--'));
const E = process.env;
const CMD = {
  reviewer: E.DESIGN_REVIEWER_CMD || 'agy',
  triage: E.DESIGN_TRIAGE_CMD || 'claude -p',
  edit: E.DESIGN_EDIT_CMD || 'claude -p --permission-mode acceptEdits',
  gh: E.DESIGN_GH_CMD || 'gh',
};
CMD.outsider = E.DESIGN_OUTSIDER_CMD || CMD.reviewer;
const MAX_ROUNDS = Number(E.DESIGN_MAX_ROUNDS || 3);
const MAX_GROWTH = Number(E.DESIGN_MAX_GROWTH || 0.15);
const MARK = '<!-- design-loop:v1 -->';
const STATE_RE = /<!-- design-loop-state:([A-Za-z0-9+/=]+) -->/;
const BLOCKING = ['P0', 'P1', 'P2'];
const BRIEF_SECTIONS = ['问题', '谁用', '失败的代价', '不做什么', '已定决定', '完成标准', '考虑过的其他做法', '未确认的假设'];

class Pause extends Error {}

function run(cmd, input = '') {
  const r = spawnSync(cmd, { shell: true, input, encoding: 'utf8', maxBuffer: 1 << 26 });
  if (r.status !== 0) throw new Error(`命令失败（退出码 ${r.status}）：${cmd}\n${r.stderr || r.error || ''}`);
  return r.stdout;
}
const git = (...a) => {
  const r = spawnSync('git', a, { encoding: 'utf8' });
  if (r.status !== 0) throw new Error(`git ${a.join(' ')} 失败：\n${r.stderr}`);
  return r.stdout.trim();
};
const changedPaths = () => {
  const r = spawnSync('git', ['-c', 'core.quotepath=off', 'status', '--porcelain'], { encoding: 'utf8' });
  if (r.status !== 0) throw new Error(`git status 失败：\n${r.stderr}`);
  return r.stdout.split('\n').filter(Boolean).map((l) => l.slice(3));
};
const read = (p) => readFileSync(p, 'utf8');
const prompt = (name) => read(join(HERE, 'prompts', name));
const b64 = (o) => Buffer.from(JSON.stringify(o), 'utf8').toString('base64');
const cell = (s) => String(s ?? '').replace(/\|/g, '\\|').replace(/\s*\n\s*/g, ' ');

function extractJson(text) {
  const a = text.indexOf('{');
  const b = text.lastIndexOf('}');
  if (a < 0 || b <= a) return null;
  try { return JSON.parse(text.slice(a, b + 1)); } catch { return null; }
}
function askJson(cmd, input, label) {
  for (let i = 0; i < 2; i++) {
    const j = extractJson(run(cmd, input));
    if (j) return j;
  }
  throw new Pause(`${label}的输出两次都不是合法 JSON`);
}

function briefSection(brief, name) {
  const lines = brief.split('\n');
  const start = lines.findIndex((l) => l.trim() === `## ${name}`);
  if (start < 0) return null;
  const rest = lines.slice(start + 1);
  const end = rest.findIndex((l) => l.startsWith('## '));
  return (end < 0 ? rest : rest.slice(0, end)).join('\n').trim();
}
function checkBrief(brief) {
  for (const s of BRIEF_SECTIONS) {
    const body = briefSection(brief, s);
    if (body === null) throw new Error(`brief.md 缺少「## ${s}」一节。按 brief-template.md 补全。`);
    if (!body) throw new Error(`brief.md 的「## ${s}」是空的。`);
  }
  const open = briefSection(brief, '未确认的假设');
  if (open !== '无') throw new Error(`brief.md 的「未确认的假设」不是“无”。先向用户逐条确认，把结论移到「已定决定」，再启动循环：\n${open}`);
}

function ghView() {
  return JSON.parse(run(`${CMD.gh} pr view ${PR} --json comments,headRefName,headRefOid,url`));
}
function loadState(view) {
  const hits = (view.comments || [])
    .slice()
    .sort((x, y) => String(x.createdAt).localeCompare(String(y.createdAt)))
    .map((c) => STATE_RE.exec(c.body || ''))
    .filter(Boolean);
  if (!hits.length) return { v: 1, rounds: [], windowStart: 0, pending: null };
  return JSON.parse(Buffer.from(hits[hits.length - 1][1], 'base64').toString('utf8'));
}
function post(markdown, state) {
  run(`${CMD.gh} pr comment ${PR} --body-file -`, `${MARK}\n${markdown}\n\n<!-- design-loop-state:${b64(state)} -->\n`);
}

function roundMarkdown(r, tri) {
  let md = `## 设计循环 第 ${r.n} 轮：${r.verdict}\n\n提交 \`${r.head}\` · 合同 ${r.size} 字符\n\n`;
  if (r.summary) md += `${cell(r.summary)}\n\n`;
  if (r.prior?.length) md += `上一轮问题的裁定：${r.prior.map((p) => `${p.id} ${p.ruling}`).join('，')}\n\n`;
  if (r.findings.length) {
    md += '| ID | 级别 | 章节 | 问题 | 违反了什么 | 不修的代价 | 建议修正 |\n| --- | --- | --- | --- | --- | --- | --- |\n';
    for (const f of r.findings) md += `| ${f.id} | ${f.severity} | ${cell(f.section)} | ${cell(f.title)} | ${cell(f.violates)} | ${cell(f.failure_cost)} | ${cell(f.fix)} |\n`;
    md += '\n';
  }
  if (r.questions.length) md += `**评审者提给你的问题：**\n${r.questions.map((q) => `- ${q}`).join('\n')}\n\n`;
  if (tri) {
    const sb = tri.step_back || {};
    md += `### 分诊\n\n- 在解决的问题：${cell(sb.problem)}\n- 这批问题的共同来源：${cell(sb.common_cause)}\n- 最简单的做法：${cell(sb.simplest)}\n\n`;
    md += '| ID | 决定 | 新增机制 | 理由 | 做法 |\n| --- | --- | --- | --- | --- |\n';
    for (const d of tri.decisions || []) md += `| ${cell(d.id)} | ${cell(d.action)} | ${d.adds_mechanism ? '是' : '否'} | ${cell(d.reason)} | ${cell(d.plan)} |\n`;
    md += '\n';
  }
  return md;
}

function pause(state, reasons, ctx) {
  let view = '';
  try {
    const history = state.rounds.map((r) => ({
      round: r.n, size: r.size, verdict: r.verdict,
      blocking_by_section: r.findings.filter((f) => BLOCKING.includes(f.severity)).reduce((m, f) => ((m[f.section] = (m[f.section] || 0) + 1), m), {}),
    }));
    view = run(CMD.outsider, [
      prompt('outsider.md'), '\n=== STEP_BACK ===\n', read(join(HERE, 'step-back.md')),
      '\n=== 暂停原因 ===\n', reasons.map((x) => `- ${x}`).join('\n'),
      '\n=== HISTORY ===\n', JSON.stringify(history, null, 2),
      '\n=== BRIEF ===\n', ctx.brief, '\n=== CONTRACT ===\n', read(ctx.contractPath),
    ].join('')).trim();
  } catch (e) {
    view = `（局外人视角生成失败：${String(e.message).split('\n')[0]}）`;
  }
  state.pending = { reasons, round: state.rounds.length };
  post([
    '## 设计循环已暂停：需要你决定', '',
    '**原因**', ...reasons.map((x) => `- ${x}`), '',
    '### 局外人视角', '', view, '',
    '### 怎么继续', '',
    `把你的决定告诉你的 agent。它把决定写进 \`${ctx.briefPath}\` 的「已定决定」并提交推送，然后运行：`, '',
    '```bash', `node design-loop.mjs ${PR} ${TASK_DIR} --resume`, '```',
  ].join('\n'), state);
  console.log(`已暂停，需要用户决定：\n${reasons.map((x) => `- ${x}`).join('\n')}\n详见 PR 评论。`);
  process.exit(2);
}

function main() {
  if (!PR || !TASK_DIR) throw new Error('用法：node design-loop.mjs <PR号> <任务目录> [--resume]');
  const dir = TASK_DIR.replace(/\\/g, '/').replace(/\/+$/, '');
  const briefPath = posix.join(dir, 'brief.md');
  const contractPath = posix.join(dir, 'contract.md');
  for (const p of [briefPath, contractPath]) if (!existsSync(p)) throw new Error(`找不到 ${p}`);
  const brief = read(briefPath);
  checkBrief(brief);

  const view = ghView();
  if (git('rev-parse', '--abbrev-ref', 'HEAD') !== view.headRefName) throw new Error(`当前分支不是 PR 分支 ${view.headRefName}。先切换过去。`);
  if (changedPaths().length) throw new Error('工作区有未提交的改动。先提交或清理。');
  if (git('rev-parse', 'HEAD') !== view.headRefOid) throw new Error('本地 HEAD 与 PR 的 head 不一致。先 git pull 或 git push。');

  const state = loadState(view);
  if (state.pending) {
    if (!RESUME) throw new Error('上次循环已暂停等待用户决定。把决定写进 brief 的「已定决定」并提交后，加 --resume 重新运行。');
    state.pending = null;
    state.windowStart = state.rounds.length;
  }
  const ctx = { brief, briefPath, contractPath };
  const stepBack = read(join(HERE, 'step-back.md'));

  try {
    for (;;) {
      const head = git('rev-parse', 'HEAD');
      const contract = read(contractPath);
      const n = state.rounds.length + 1;
      const last = state.rounds[state.rounds.length - 1];
      const prior = last ? last.findings.filter((f) => BLOCKING.includes(f.severity)) : [];

      console.log(`第 ${n} 轮：评审中…`);
      const rv = askJson(CMD.reviewer, [
        prompt('reviewer.md'), '\n=== BRIEF ===\n', brief,
        `\n=== CONTRACT（${contractPath}）===\n`, contract,
        '\n=== PRIOR ===\n', JSON.stringify(prior, null, 2),
      ].join(''), '评审者');
      const findings = (rv.findings || []).map((f, i) => {
        const sev = BLOCKING.includes(f.severity) && String(f.violates || '').trim() && String(f.failure_cost || '').trim() ? f.severity : 'P3';
        return { id: `R${n}-F${i + 1}`, severity: sev, section: String(f.section || '').trim(), title: f.title, violates: f.violates, failure_cost: f.failure_cost, fix: f.fix };
      });
      const blocking = findings.filter((f) => BLOCKING.includes(f.severity));
      const questions = (rv.questions_for_user || []).filter(Boolean);
      const round = { n, head, size: contract.length, verdict: blocking.length ? 'REWORK' : 'PASS', findings, questions, prior: rv.prior || [], summary: rv.summary || '' };
      state.rounds.push(round);

      if (round.verdict === 'PASS' && !questions.length) {
        post(`${roundMarkdown(round)}**合同在提交 \`${head}\` 通过。** 这个结论只对这个提交成立。`, state);
        console.log(`合同通过：${head}`);
        process.exit(0);
      }

      const reasons = [];
      if (questions.length) reasons.push('评审者有需要你回答的问题（见本轮评论）');
      const win = state.rounds.slice(state.windowStart);
      if (round.verdict === 'REWORK' && win.length >= MAX_ROUNDS) reasons.push(`连续 ${win.length} 轮评审没有通过`);
      if (win.length >= 2) {
        const prev = new Set(win[win.length - 2].findings.filter((f) => BLOCKING.includes(f.severity)).map((f) => f.section));
        const repeated = [...new Set(blocking.map((f) => f.section).filter((s) => s && prev.has(s)))];
        if (repeated.length) reasons.push(`同一节连续两轮出现阻塞问题：${repeated.join('、')}`);
      }

      let tri = null;
      if (!reasons.length) {
        console.log(`第 ${n} 轮：分诊中…`);
        tri = askJson(CMD.triage, [
          prompt('triage.md'), '\n=== STEP_BACK ===\n', stepBack, '\n=== BRIEF ===\n', brief,
          `\n=== CONTRACT（${contractPath}）===\n`, contract, '\n=== FINDINGS ===\n', JSON.stringify(blocking, null, 2),
        ].join(''), '分诊');
        const ds = tri.decisions || [];
        const ids = new Set(ds.map((d) => d.id));
        if (blocking.some((f) => !ids.has(f.id))) reasons.push('分诊没有覆盖全部阻塞问题');
        if (ds.some((d) => d.action === 'ask_user')) reasons.push('分诊认为有问题需要你决定：' + ds.filter((d) => d.action === 'ask_user').map((d) => `${d.id}（${d.reason}）`).join('；'));
        if (ds.some((d) => d.adds_mechanism)) reasons.push('修复需要给合同新增机制：' + ds.filter((d) => d.adds_mechanism).map((d) => d.id).join('、'));
        if (tri.step_back?.change_direction) reasons.push(`分诊认为最简单的做法与合同当前路线不同：${tri.step_back.simplest}`);
        if ((tri.step_back?.unconfirmed_assumptions || []).length) reasons.push('发现未经你确认的假设：' + tri.step_back.unconfirmed_assumptions.join('；'));
        if ((tri.questions_for_user || []).length) reasons.push('分诊提给你的问题：' + tri.questions_for_user.join('；'));
        if (!reasons.length && !ds.some((d) => d.action === 'fix' || d.action === 'delete')) reasons.push('分诊拒绝了全部阻塞问题，没有可执行的修改');
      }
      post(roundMarkdown(round, tri), state);
      if (reasons.length) pause(state, reasons, ctx);

      console.log(`第 ${n} 轮：修改合同中…`);
      run(CMD.edit, [
        prompt('edit.md').replaceAll('{{CONTRACT_PATH}}', contractPath), '\n=== BRIEF ===\n', brief,
        '\n=== FINDINGS ===\n', JSON.stringify(blocking, null, 2), '\n=== TRIAGE ===\n', JSON.stringify(tri.decisions, null, 2),
      ].join(''));
      const changed = changedPaths();
      if (changed.some((p) => p !== contractPath)) {
        git('stash', 'push', '-u', '-m', `design-loop-rejected-round-${n}`);
        pause(state, [`编辑者改动了合同以外的文件（${changed.filter((p) => p !== contractPath).join('、')}）。改动已放进 git stash，未提交`], ctx);
      }
      if (!changed.length) pause(state, ['编辑者没有对合同做任何改动'], ctx);
      git('add', contractPath);
      git('commit', '-m', `design-loop: 第 ${n} 轮修订`);
      git('push', 'origin', 'HEAD');

      const newSize = read(contractPath).length;
      if (newSize > round.size * (1 + MAX_GROWTH)) {
        pause(state, [`合同单轮增长 ${Math.round((newSize / round.size - 1) * 100)}%（${round.size} → ${newSize} 字符），超过 ${Math.round(MAX_GROWTH * 100)}% 的上限。修订已提交，但没有继续评审`], ctx);
      }
    }
  } catch (e) {
    if (e instanceof Pause) pause(state, [e.message], ctx);
    throw e;
  }
}

try { main(); } catch (e) { console.error(e.message); process.exit(1); }

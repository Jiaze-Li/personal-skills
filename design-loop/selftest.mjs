#!/usr/bin/env node
// selftest.mjs — 用假的 gh 和假的模型 CLI 验证 design-loop.mjs 的流程。
// 不联网，不调用任何模型。运行：node selftest.mjs
// 全部通过时最后一行输出 “SELFTEST PASS”，退出码 0。
import { spawnSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const LOOP = join(HERE, 'design-loop.mjs');
const q = (s) => JSON.stringify(s);
const sh = (cmd, cwd) => {
  const r = spawnSync(cmd, { shell: true, cwd, encoding: 'utf8' });
  if (r.status !== 0) throw new Error(`${cmd}\n${r.stderr}`);
  return r.stdout.trim();
};

const BRIEF = ['问题', '谁用', '失败的代价', '不做什么', '已定决定', '完成标准', '考虑过的其他做法']
  .map((s) => `## ${s}\n\n测试内容\n`).join('\n') + '\n## 未确认的假设\n\n无\n';
const CONTRACT = '# 合同\n\n## 目的\n\n做一件事。\n\n## 规则\n\n规则一。规则二。规则三。规则四。规则五。规则六。规则七。规则八。\n';

// 假 gh：评论存在 comments.json 里。
const FAKE_GH = `
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { execSync } from 'node:child_process';
const store = process.env.FAKE_STORE;
const comments = existsSync(store) ? JSON.parse(readFileSync(store, 'utf8')) : [];
const a = process.argv.slice(2);
if (a[0] === 'pr' && a[1] === 'view') {
  const g = (c) => execSync(c, { encoding: 'utf8' }).trim();
  console.log(JSON.stringify({ comments, headRefName: g('git rev-parse --abbrev-ref HEAD'), headRefOid: g('git rev-parse HEAD'), url: 'https://example.invalid/pr/1' }));
} else if (a[0] === 'pr' && a[1] === 'comment') {
  comments.push({ body: readFileSync(0, 'utf8'), createdAt: new Date(Date.now() + comments.length).toISOString() });
  writeFileSync(store, JSON.stringify(comments));
} else { console.error('fake gh: unsupported ' + a.join(' ')); process.exit(1); }
`;
// 假模型：按调用次数依次返回脚本里预设的回答；action 可以是修改文件。
const FAKE_MODEL = `
import { readFileSync, writeFileSync, existsSync, appendFileSync } from 'node:fs';
readFileSync(0, 'utf8');
const [role] = process.argv.slice(2);
const plan = JSON.parse(readFileSync(process.env.FAKE_PLAN, 'utf8'))[role] || [];
const cf = process.env.FAKE_PLAN + '.' + role + '.count';
const i = existsSync(cf) ? Number(readFileSync(cf, 'utf8')) : 0;
writeFileSync(cf, String(i + 1));
const step = plan[Math.min(i, plan.length - 1)];
if (step === undefined) process.exit(0);
if (step.append) appendFileSync(step.append.path, step.append.text);
if (step.write) writeFileSync(step.write.path, step.write.text);
process.stdout.write(typeof step.out === 'string' ? step.out : JSON.stringify(step.out ?? {}));
`;

function scenario(name, plan, extraArgs = '', reuse = null) {
  const root = reuse?.root || mkdtempSync(join(tmpdir(), 'design-loop-test-'));
  const work = join(root, 'work');
  if (!reuse) {
    sh(`git init -q --bare ${q(join(root, 'remote.git'))}`);
    mkdirSync(join(work, 'design/t'), { recursive: true });
    sh('git init -q && git checkout -q -b task', work);
    sh('git config user.email t@example.invalid && git config user.name t && git config commit.gpgsign false', work);
    writeFileSync(join(work, 'design/t/brief.md'), BRIEF);
    writeFileSync(join(work, 'design/t/contract.md'), CONTRACT);
    sh(`git add -A && git commit -q -m init && git remote add origin ${q(join(root, 'remote.git'))} && git push -q origin task`, work);
    writeFileSync(join(root, 'fake-gh.mjs'), FAKE_GH);
    writeFileSync(join(root, 'fake-model.mjs'), FAKE_MODEL);
  }
  const planPath = join(root, `plan-${name}.json`);
  writeFileSync(planPath, JSON.stringify(plan));
  const model = (role) => `node ${q(join(root, 'fake-model.mjs'))} ${role}`;
  const r = spawnSync(`node ${q(LOOP)} 1 design/t ${extraArgs}`, {
    shell: true, cwd: work, encoding: 'utf8',
    env: {
      ...process.env, FAKE_STORE: join(root, 'comments.json'), FAKE_PLAN: planPath,
      DESIGN_GH_CMD: `node ${q(join(root, 'fake-gh.mjs'))}`,
      DESIGN_REVIEWER_CMD: model('reviewer'), DESIGN_TRIAGE_CMD: model('triage'),
      DESIGN_EDIT_CMD: model('edit'), DESIGN_OUTSIDER_CMD: model('outsider'),
    },
  });
  const store = join(root, 'comments.json');
  const comments = existsSync(store) ? JSON.parse(readFileSync(store, 'utf8')).map((c) => c.body) : [];
  return { root, work, code: r.status, out: r.stdout + r.stderr, comments };
}

let failed = 0;
function check(name, cond, detail = '') {
  console.log(`${cond ? 'ok  ' : 'FAIL'} ${name}`);
  if (!cond) { failed++; if (detail) console.log(detail); }
}

const finding = (section, extra = {}) => ({ severity: 'P2', section, title: '问题', violates: 'brief 已定决定第 1 条', failure_cost: '会出错', fix: '改一句', ...extra });
const triageFix = (id) => ({ step_back: { problem: 'p', common_cause: 'c', simplest: 's', change_direction: false, unconfirmed_assumptions: [] }, decisions: [{ id, action: 'fix', adds_mechanism: false, reason: 'r', plan: 'p' }], questions_for_user: [] });
const C = 'design/t/contract.md';

// 1. REWORK → 修改 → PASS
{
  const s = scenario('pass', {
    reviewer: [{ out: { findings: [finding('规则')] } }, { out: '好的，结果如下：\n```json\n{"findings": [], "prior": [{"id":"R1-F1","ruling":"fixed"}]}\n```' }],
    triage: [{ out: triageFix('R1-F1') }],
    edit: [{ append: { path: C, text: '补一句。\n' }, out: '改了' }],
  });
  check('1 返工后通过：退出码 0', s.code === 0, s.out);
  check('1 两条评论，第二条是 PASS', s.comments.length === 2 && s.comments[1].includes('第 2 轮：PASS'), s.comments.join('\n---\n'));
  check('1 修订已提交并推送', sh('git log --oneline origin/task', s.work).includes('design-loop: 第 1 轮修订'));
}
// 2. 没有 violates 的阻塞问题被降为 P3 → 直接 PASS
{
  const s = scenario('downgrade', { reviewer: [{ out: { findings: [finding('规则', { violates: '' })] } }] });
  check('2 写不出违反什么的问题降为 P3，合同通过', s.code === 0 && s.comments[0].includes('| P3 |'), s.out);
}
// 3. 同一节连续两轮被打 → 暂停；--resume 后继续并通过
{
  const plan = {
    reviewer: [{ out: { findings: [finding('规则')] } }, { out: { findings: [finding('规则')] } }, { out: { findings: [] } }],
    triage: [{ out: triageFix('R1-F1') }],
    edit: [{ append: { path: C, text: '补一句。\n' }, out: '改了' }],
    outsider: [{ out: '**到底在解决什么问题**\n测试。' }],
  };
  const s = scenario('repeat', plan);
  check('3 同一节连续两轮：退出码 2', s.code === 2, s.out);
  check('3 暂停评论含原因和局外人视角', s.comments.at(-1).includes('同一节连续两轮') && s.comments.at(-1).includes('局外人视角') && s.comments.at(-1).includes('到底在解决什么问题'));
  const again = scenario('repeat', plan, '', s);
  check('3 未加 --resume 时拒绝继续：退出码 1', again.code === 1 && again.out.includes('--resume'), again.out);
  const resumed = scenario('repeat', plan, '--resume', s);
  check('3 --resume 后继续并通过', resumed.code === 0 && resumed.comments.at(-1).includes('PASS'), resumed.out);
}
// 4. 分诊报告新增机制 → 暂停，不修改
{
  const t = triageFix('R1-F1'); t.decisions[0].adds_mechanism = true;
  const s = scenario('mechanism', { reviewer: [{ out: { findings: [finding('规则')] } }], triage: [{ out: t }], edit: [{ append: { path: C, text: 'x' }, out: '' }], outsider: [{ out: '视角' }] });
  check('4 新增机制：暂停且没有提交', s.code === 2 && s.comments.at(-1).includes('新增机制') && !sh('git log --oneline', s.work).includes('design-loop'), s.out);
}
// 5. 编辑者改了 brief → 改动进 stash，暂停
{
  const s = scenario('brief', { reviewer: [{ out: { findings: [finding('规则')] } }], triage: [{ out: triageFix('R1-F1') }], edit: [{ append: { path: 'design/t/brief.md', text: '偷改\n' }, out: '' }], outsider: [{ out: '视角' }] });
  check('5 改动 brief：暂停，工作区干净，改动在 stash', s.code === 2 && s.comments.at(-1).includes('合同以外的文件') && sh('git status --porcelain', s.work) === '' && sh('git stash list', s.work).includes('design-loop-rejected'), s.out);
}
// 6. 合同单轮增长超过 15% → 暂停
{
  const s = scenario('growth', { reviewer: [{ out: { findings: [finding('规则')] } }], triage: [{ out: triageFix('R1-F1') }], edit: [{ append: { path: C, text: '很长的新增内容。'.repeat(10) }, out: '' }], outsider: [{ out: '视角' }] });
  check('6 增长超限：暂停', s.code === 2 && s.comments.at(-1).includes('单轮增长'), s.out);
}
// 7. 评审者向用户提问 → 暂停
{
  const s = scenario('question', { reviewer: [{ out: { findings: [], questions_for_user: ['会有别人用吗？'] } }], outsider: [{ out: '视角' }] });
  check('7 评审者提问：暂停并列出问题', s.code === 2 && s.comments[0].includes('会有别人用吗'), s.out);
}
// 8. 评审输出不是 JSON → 暂停
{
  const s = scenario('badjson', { reviewer: [{ out: '我无法完成' }], outsider: [{ out: '视角' }] });
  check('8 输出不是 JSON：暂停', s.code === 2 && s.comments.at(-1).includes('不是合法 JSON'), s.out);
}
// 9. brief 有未确认的假设 → 拒绝启动
{
  const s0 = scenario('gate-setup', { reviewer: [{ out: { findings: [] } }] });
  writeFileSync(join(s0.work, 'design/t/brief.md'), BRIEF.replace(/无\n$/, '- 可能有别人用\n'));
  sh('git commit -q -am assumptions && git push -q origin task', s0.work);
  const s = scenario('gate', { reviewer: [{ out: { findings: [] } }] }, '', s0);
  check('9 brief 有未确认的假设：拒绝启动，退出码 1', s.code === 1 && s.out.includes('未确认的假设'), s.out);
}

console.log(failed ? `SELFTEST FAIL（${failed} 项失败）` : 'SELFTEST PASS');
process.exit(failed ? 1 : 0);

# 安装说明（给执行这次安装的 agent）

你的任务是把这个目录安装到用户的机器上并验证它能用。所有文件都已经写好并测过。**原样复制，不要改写、不要优化、不要增加功能。** 某一步失败两次就停下来，把命令和完整报错告诉用户，不要自己想办法绕过。

不要碰 `Jiaze-Li/claude-review-bot` 的 PR #70，也不要修改那个仓库里的任何代码。

## 这是什么

一个在本地运行的“合同评审循环”。用户和 AI 谈定需求后，脚本自动完成：评审合同 → 分诊问题 → 修改合同 → 再评审，直到通过，或者遇到需要用户决定的情况时暂停。评审者和编辑者是两个不同的命令行 AI，结论发在 GitHub PR 评论里。

| 文件 | 作用 |
| --- | --- |
| `skill.md` | 给日常使用的 agent 读的工作流规则 |
| `step-back.md` | “退一步”规则 |
| `brief-template.md` | brief 模板 |
| `design-loop.mjs` | 驱动脚本 |
| `prompts/` | 评审、分诊、修改、局外人四段提示词 |
| `selftest.mjs` | 脚本自测，不联网、不调用模型 |
| `INSTALL.md` | 本文件 |

## 步骤 1：检查工具

```bash
node --version
```

```bash
git --version
```

```bash
gh auth status
```

```bash
agy --version
```

```bash
claude --version
```

要求：node 18 或更高；`gh` 已登录；`agy`（Antigravity CLI，Gemini CLI 的后继）和 `claude` 都已安装，并且各自以交互方式登录过用户的会员账号。缺任何一个就停下来告诉用户。

## 步骤 2：复制文件

把这个目录放进用户的 `personal-skills` 仓库。

```bash
test -d ~/personal-skills || git clone https://github.com/Jiaze-Li/personal-skills.git ~/personal-skills
```

```bash
git clone --depth 1 --branch claude/loving-ritchie-gwjczw https://github.com/Jiaze-Li/claude-review-bot.git /tmp/crb-handoff
```

```bash
cd ~/personal-skills && git checkout -b add-design-loop && cp -R /tmp/crb-handoff/docs/handoff/design-loop ./design-loop
```

如果 `~/personal-skills` 已存在并且有未提交的改动，停下来问用户。

## 步骤 3：运行自测

```bash
node ~/personal-skills/design-loop/selftest.mjs
```

最后一行必须是 `SELFTEST PASS`。不是的话，说明复制出了问题或环境不兼容，停下来把完整输出给用户。

## 步骤 4：确认两个 CLI 的无交互模式

脚本通过 stdin 把提示词交给 CLI，从 stdout 读回答。下面三个测试确认这一点。CLI 的参数可能随版本变化；如果某条命令报“未知参数”，运行 `agy --help` 或 `claude --help` 找到对应的无交互参数，调整后重试，并记下你最终用的命令。

评审者（只需要读和回答）：

```bash
echo '只回复两个字：收到' | agy
```

分诊（只需要读和回答）：

```bash
echo '只回复两个字：收到' | claude -p
```

编辑者（需要能改文件）：

```bash
mkdir -p /tmp/design-loop-edit-test && cd /tmp/design-loop-edit-test && git init -q 2>/dev/null; echo '在当前目录创建文件 a.txt，内容为 ok。不要做别的。' | claude -p --permission-mode acceptEdits; cat a.txt
```

前两条应当输出“收到”，第三条最后应当打印 `ok`。

如果你用的命令与上面不同，把最终可用的命令写进用户的 shell 配置文件（`~/.zshrc` 或 `~/.bashrc`），用这四个环境变量：

```bash
export DESIGN_REVIEWER_CMD='agy'
export DESIGN_TRIAGE_CMD='claude -p'
export DESIGN_EDIT_CMD='claude -p --permission-mode acceptEdits'
export DESIGN_OUTSIDER_CMD='agy'
```

上面是脚本的默认值；命令与默认值相同时不需要写。评审者和编辑者必须是不同的模型，不要把四个都设成同一个 CLI。

## 步骤 5：让两个 agent 默认遵守规则

把下面这段追加到 `~/.claude/CLAUDE.md` 的末尾，再追加到 Antigravity CLI 的全局指令文件的末尾。后者的路径以 `agy --help` 或其文档为准；找不到就跳过，并在报告里说明。文件不存在就创建。已有内容不要动。

```markdown
## 设计工作流

用户提出新功能、架构改动、流程设计这类需要先想清楚的需求时，先读 `~/personal-skills/design-loop/skill.md` 并照它做，不要直接动手。

任何时候满足 `~/personal-skills/design-loop/step-back.md` 里的触发条件，就停下来按那份规则做。
```

## 步骤 6：提交到 personal-skills

```bash
cd ~/personal-skills && git add design-loop && git commit -m "Add design-loop workflow" && git push -u origin add-design-loop
```

```bash
cd ~/personal-skills && gh pr create --title "Add design-loop workflow" --body "本地同步的合同评审循环：规则、提示词、驱动脚本和自测。"
```

本地仓库保持在这个分支上，这样工作流立刻可用。合并由用户决定。

## 步骤 7：向用户报告

到这里就停。不要自己找任务去试跑循环，第一次真实运行需要用户带着一个真实需求来。报告这些内容：

1. 步骤 3 自测的最后一行。
2. 步骤 4 三个测试各自的结果，以及最终使用的命令（如果与默认不同）。
3. 步骤 5 修改了哪两个文件。
4. 步骤 6 的 PR 链接。
5. 任何没做成的步骤和原因。

然后告诉用户怎么第一次使用：新开一个会话，直接说出需求。agent 会按 `skill.md` 先提问、写 brief，用户确认后它会开 PR 并运行循环。建议第一次选一个小任务。

## 已知的限制

这些是已经知道、有意保留的，不要去“修”：

- 脚本只在用户自己的机器上跑，电脑需要开着。
- 一个任务一份合同文件。
- 花费上限靠会员额度和“连续 3 轮不通过就暂停”，没有按金额计费的限制。
- 自测用的是假的模型输出。真实模型是否每次都返回合法 JSON，要靠第一次真实运行来观察；脚本遇到两次非法输出会暂停并说明。

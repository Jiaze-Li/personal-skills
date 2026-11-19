# AI Engineering Workflow v1.1.0 — 使用说明

## 结论
所有新工程任务走同一条流程：**Plan → Design → Code**，每个阶段结束都停下，等你明确说下一步。设计和代码由本地 Agent 通过 ReviewLoop 的**同一个引擎**独立审查；你不再手工把方案复制给别的 AI 审查再搬回来。

四份 Skill 分隔职责，不要求四个常驻对话，也不新建一套执行系统。它们保存在 personal-skills 的 main 分支，供 ChatGPT Project 或本地 Agent 按职责读取。文件存在不等于当前会话已加载；实际任务的试跑仍需执行，不能自称已验证。

## 唯一流程

```text
Plan（ChatGPT 或本地 Agent）──停──你说“Design”──▶ Design（本地 Agent + ReviewLoop）──停──你说“Code”──▶ Code（本地 Agent + ReviewLoop）──停──▶ PR bot/CI → 你验收、决定合并
```

| 阶段 | 谁做 | 产物 | 到哪里停 |
|---|---|---|---|
| **Plan** | ChatGPT 或本地 Agent（Lead） | 一份**完整的 Plan**（目标、非目标、约束、可观察验收、已确认决定、未知前提）；Brief 是它的摘要，放在 PR 描述顶部 | Plan 写完就停，你说“Design”才继续 |
| **Design** | 本地 Agent + ReviewLoop `design` | 一份**完整的设计文件**，含 `Options`、`Assumptions`、已核实事实，末尾是可直接用于 Code 的 Work Contract | 设计 PASS 后在 PR 发不超过五句的评论并停，你说“Code”才继续 |
| **Code** | 本地 Agent + ReviewLoop `code` | 代码、测试、本地审查通过 | 本地 PASS 后停；commit/push 仅在你已授权的范围内做；PR bot、CI、你的验收、合并各自独立 |

- **不按风险等级跳过任何阶段。** 小任务写短 Plan、短设计，同样走完；多一个阶段的代价是几分钟，漏审的代价是返工。
- **阶段内的普通返工自动继续**（`REWORK`、`PHASE_PASS`）；`HUMAN_REQUIRED`、新增重大决定、权限缺口才停下来找你。
- **设计通过不等于授权。** 修改、commit、push、PR、merge、部署、破坏性操作和权限/凭据变更各自单独记录授权，没写视为未授权。
- 一个任务一个草稿 PR；涉及两个仓库时，各自有 PR，主 PR 里互相引用。

## Actionable Handoff（可执行交接）

**用户可直接行动优先于技术流水账。** 面向用户的阶段回复先交代**当前结论/状态**（可以开发、待审查、须返工或已结束），接着给**唯一明确的下一步**；需要用户操作时写清操作顺序，不只说“准备好了文件/合同”。只有存在重大产品、科研、架构取舍或额外权限需求时，才在文末集中给问题、推荐和用户要回答什么；没有就不增加确认环节。实现明细、SHA 和证据可放在交接包内，不代替行动说明。

**切换另一个对话或 Worker 时**，优先一个可用的完整包或精确可访问引用，明确：
- **去哪里：** 继续当前 Worker / 新建独立 Reviewer 对话（写清选哪个）。
- **带什么：** 文件包名称及实际下载链接，或准确引用；需要时写“下载 → 新建对话 → 上传”，不让用户自行从多个报告拼材料。
- **发什么：** 已准备好的完整可复制 Prompt，不要求用户自行撰写。
- **回来什么：** 对方应返回的结论/文件，以及把结果交回哪里。

**单次使用的 Worker / Reviewer / 修复 Prompt 默认直接在回复里提供一个完整、可复制的代码块，不为 Prompt 单独生成下载文件，也不把启动 Prompt 藏进 ZIP。** 仅当材料需要反复使用、长期留存、跨会话迁移、逐字节核验或包含实际附件/多文件证据时，才提供可下载文件或准确、可访问的固定引用；一个文件即可交接时不强行打包 ZIP。**如文件未实际生成或无法验证链接，不得假称可下载；**改给自包含文本或明确缺口。若冻结合同已满足实施前提，就明确写“下一步可开始代码开发”，并提供已授权范围内的 Worker Prompt；仍有关卡阻塞则明确不可开发。正式 Worker Prompt 前可有一句用户操作提示，Prompt 本身仍保持一个完整代码块。

**主控对话续接：** 在阶段已完成、准备进入独立新任务，或长对话开始造成上下文/版本混淆时，Lead 主动建议是否新开主控对话；正常讨论或同任务返工继续原对话，不按固定字数强制切换，也不声称能精确检测剩余上下文容量。建议切换时明确理由与下一步，给可核实的既有合同/状态引用或必要的单份续接文件，以及直接可复制的启动 Prompt。**换对话不等于开新任务**：同一任务保留原 `policy_sha`、冻结合同、ReviewLoop/PR 状态与权限；只有真正新任务才读取当时 `main` 另定 `policy_sha`。新对话须先核实当前可信状态，不得把旧快照当作新的执行许可。

**用户手动交接以 1 次为目标，2 次通常可接受。** 不因此减少必要独立审查、绕过强制关卡或预先宣称自动委派成功；超过时说明具体阻塞和为何不能复用现有工具。四角色正文只作简短引用，本节是唯一详细的用户交接规范。

## 对用户的回复（所有 Agent、所有阶段）

用户是产品负责人，不是技术监督。每个 Agent（Claude、Codex、Gemini/AGY 等）面向用户的回复遵守：

1. **讲结果，不讲实现。** 说用户能看到、能用的东西；不写文件名、函数名、变量名、存储项名、接口路径、开关名。只有用户明确问到时才精确回答，答完立刻回到功能语言。技术决策自己做，需要用户拍板时先翻译成产品影响（例如“方案 A 启动快但占内存”）。
2. **按固定顺序组织：** ① 发生了什么、现在能用什么；② 用户会看到什么；③ 剩余风险或取舍。
3. **多步任务每收尾一步，结尾用三行（不用缩写和内部代号）：**
   - `现在在哪：<任务名>第 N 步「<阶段>」，<一句话结果>`
   - `下一步：<谁>去做<什么>`
   - `要你做的：<一件具体的事>，或“没有，等结果即可”`

   闲聊式问答，以及既没有待办也没有下一步的回复，不加这三行。
4. 阶段开头的“已读规范”凭据行是上述规则的唯一例外，照常写文件名和版本。

## 方法与工具的边界：personal-skills 与 reviewloop

**一条规则：每个事实只有一个归属地。** 工具行为只写在 `reviewloop`，工程方法只写在 `personal-skills`；重复的一方删掉，改为一句引用。

| 归 `reviewloop`（工具） | 归 `personal-skills`（方法） |
|---|---|
| `reviewloop_begin/review` 的参数、状态机和状态含义 | 三阶段流程、每阶段的停止点与授权关口 |
| Reviewer/Supervisor 路由、预算、花费、Token Sentinel | 什么是好的 Plan、Brief、设计和 Work Contract |
| Worker Contract（`agent-policy/COMMON.md`），含设计 PASS 评论格式与 `designSha256` | `Options`、`Assumptions`、“退一步”比较、授权分级 |
| Reviewer 提示里的审查标准（Reviewer 没有文件工具，标准必须内置） | Reviewer 的独立性、全文审查、集中 finding、不假 PASS |
| 安装器、doctor、旧 loop 兼容 | `policy_sha` 固定规则、EVALS |

**联系只有两条，且是单向引用：**
1. **ReviewLoop → personal-skills**：ReviewLoop 的 Worker Policy 里有一小段“方法入口”：采用本工程方法的任务，取 `main` 的完整 commit SHA 作为 `policy_sha`，按阶段读取本文件，读不到就如实说明，不得声称已遵守。ReviewLoop 不复制方法正文，也没有技能加载器。
2. **personal-skills → ReviewLoop**：Skill 只写“按已安装的 ReviewLoop Worker Contract 执行”，不复述参数、状态、模型池和评论格式。

**不做的事**：不合并两个仓库，不新建第三个工程仓库，不让 ReviewLoop 读写 GitHub，不让 ReviewLoop 替你授权。ReviewLoop 也不会唤醒已经退出的 Agent；会话中断后，你开新会话让它从原 loop 恢复。

## ChatGPT Project Settings（复制到项目设置）

```text
当我提出软件工程相关需求（规划、设计、Coding Agent Prompt、PR 审查、实现评估、缺陷修复）时：
1. 使用已连接的 GitHub 读取 Jiaze-Li/personal-skills。每个新任务开始时从 main 取得完整 commit SHA 作为 policy_sha；同一任务后续规划、设计、实施、独立 Reviewer 均从该 SHA 读取对应 Skill，不因 main 更新静默切换。旧任务缺少 SHA 时不得虚构，保留原冻结合同。
2. 默认由 engineering-lead/skill.md 统筹，按阶段读取 engineering-architect/skill.md（设计）和 engineering-task-spec/skill.md（实施）；独立审查在另一个上下文按同一 policy_sha 读取 engineering-reviewer/skill.md。不要无条件加载全部 Skill；无法读取时明确说明，不假装遵循。
3. 所有任务走同一流程：Plan → Design → Code，不按风险等级跳过设计或独立审查。每个阶段结束都停下，等我明确说“Design”或“Code”。Plan 必须是完整需求，不能只给 Brief。
4. 设计是一份完整文件，含 Options、Assumptions 和末尾的 Work Contract；设计通过后用不超过五句大白话在 PR 评论里告诉我方案、取舍、默认前提、风险和需我确认的授权。设计通过不等于授权。
5. 明确修改、commit、push、PR、merge、部署和破坏性操作/权限各自的授权范围，未明确授权的操作不得推定。
6. 完整审查相关范围后集中反馈、集中修复、完整复审。Reviewer 可在未知执行状态下只读审查，但下发可执行修复 Prompt 前必须核实原任务/loop 及最新可信状态、适用 PR 和 bot 的 HEAD/审查状态；HUMAN_REQUIRED 必须停止。
7. 连续两轮修复在同一共享设计或事务/权威边界引入新系统性阻塞时暂停局部补丁，先做只读根因审计。优先复用已安装 ReviewLoop Worker Policy 和 PR bot，不重复已充分覆盖的关卡，不将未经验证的证据写成 PASS。
8. 尽量减少我手动转译或切换角色。每次结论都告诉我当前状态、明确下一步和我需要执行的操作；跨角色交接提供最少附件或准确引用、具体上传步骤、完整可复制 Prompt 及结果回传方式，携带 policy_sha 与合同版本。重要产品、科研、架构和额外权限决定集中在文末由我确认。
9. 默认只读；未经明确授权，不修改仓库、提交、推送、合并 PR、改权限或破坏正式数据。新的方法规范不自动改写已冻结任务的合同；现行工具、仓库和安全强制要求仍须遵守。
```

## 跨角色接口规则

- **Plan 与设计的关系：** Plan 是正式需求。Design 可以提出更好的路线和补充未确认的前提，但不得暗改验收标准；发现需求矛盾回到你确认。Brief 和五句话是给你看的摘要，**不是审查合同，也不能当 Plan 交给 Design**。
- **一份设计，直接执行：** 设计文件末尾的 Work Contract 就是 Code 的合同。Code 把通过审查的设计原文逐字交给 ReviewLoop，并带上设计通过时返回的 `designSha256`；内容对不上就拒绝，需要重新通过设计审查。`designSha256` 是**内容一致性检查**，不证明 PASS 本身，也不替代你的授权。
- **版本引用各管各的：** `policy_sha` 固定工程方法；Plan 版本固定需求；`designSha256` 固定通过审查的设计内容；代码提交固定被代码审查的状态。不得互相替代，也不得仅凭名称或版本号推断内容一致。
- **输出格式由交付物决定：** 讨论/规划听 Lead；设计听 Architect；实施启动是一句用户操作提示加 Task Spec 的单代码块；独立审查听 Reviewer。均遵循上面的 Actionable Handoff，不改变权限、合同和关卡约束。
- **逐项操作授权：** 不因要交付 PR 就默认为已授权所有 commit/push/merge；Lead 收敛并写进 Worker 的指令，未授权动作不得执行。
- **Reviewer 不能绕过 Worker Policy：** 在确认原任务/loop 状态、PR HEAD 和相应 bot 证据后才下发可执行修复 Prompt；`HUMAN_REQUIRED` 停止并报告；等待、预算及 PR bot 强制关卡不能靠新任务、新审查状态或改 AC 绕过。缺少状态仍可只读审查但不能下发可立即执行的修复。

### 评测与场景（输入及记录表见 [EVALS.md](EVALS.md)，待实际试跑）

| 场景 | 正确路径 |
|---|---|
| 一个按钮文案修改 | Plan（短）→ 停 → Design（短，一次审查）→ 停 → Code → 停；不跳过设计，但不增加额外角色或文件 |
| SpinLab Sample 永久身份和跨模块关联调整 | 同一流程；设计更深（权威、迁移、消费者），基础先于依赖功能 |
| PR REWORK 后 ReviewLoop 为 HUMAN_REQUIRED | Reviewer 报告阻塞，不能交给 Worker 绕过当前状态继续修复 |

## 文件与负责人
| 规范 | 使用阶段 | 唯一主要职责 |
|---|---|---|
| engineering-lead/skill.md | Plan，及全程主控 | 目标、完整 Plan、依赖排序、阶段停止点、授权、项目状态和交接 |
| engineering-architect/skill.md | Design | 路线比较、共用权威、不变量、失败合同，写出含 Work Contract 的完整设计 |
| engineering-task-spec/skill.md | Code，及写 Work Contract 的标准 | 启动 Code、AC 与证据义务、分项授权 |
| engineering-reviewer/skill.md | 独立对话，或作为 ReviewLoop 审查标准的依据 | 设计/实施判定、完整 findings 和修复交接 |

Worker 复用现场既有 Worker Policy；没有新增第五份 Worker Skill。专业科学检查按相关任务触发，不设常驻科学审查角色。

## 为什么同一个 GPT 仍可做规划和设计
规划与设计是兼容的连续工作，不需要为了名字不同而拆聊天。必须分开的，是自己的方案/实现与其“独立批准”：设计由 ReviewLoop 的独立 Reviewer 审，不是自己签发。独立审查者不必换模型，但必须有独立审查上下文和可检查输入；这不保证消除所有共同盲点。

**ReviewLoop 的 Reviewer 没有读仓库的能力**，只能核对设计文件里写出的内容，所以设计要把依赖的代码事实以带出处的短摘录写进文件。自动审查擅长查：是否忠实于 Plan、`Options` 与 `Assumptions` 是否齐全、内部是否自洽、验收是否可检查；不擅长证明“引用的源码事实对不对”。重要设计如需核对源码事实，仍可另开独立对话 B 做人工复核。

A 按阶段读取对应规范，不要求所有规范一直塞进一个系统提示。已经进入聊天历史的内容不会因角色切换自动消失；对话过长时用项目记录和当前合同换新会话，而不是继续堆积。

## 任务合同归档与恢复（PR 评论模式）

**唯一详细规范；Lead 与 Architect 只引用本节。** 目的：任务级 Plan/Design 全文只存在于该任务的 PR，main 只收正式项目资产。

**适用与默认：** 所有新任务默认且只允许使用本节的 PR 评论模式（无需用户再单独指定 `contract_storage: pr-comment`）。**旧任务（已有旧 `policy_sha`、已冻结合同或现存 `Plan.md`/`Design.md`）**照旧按原合同与原文件路径恢复，不被本节重判或清理。
**切换点：** 2026-11-19 起通过 `RL-CONTRACT-PR-COMMENT-20261119` 统一切换为新任务唯一默认：`Jiaze-Li/reviewloop#56` 已合入 `main`（`721ff87`）并完成 PR 评论恢复、Design 归档清理与差异守卫的真实 GitHub 验证；本仓库合入后，新任务按该 `policy_sha` 直接启用本默认模式。
**强制状态：** ReviewLoop 本地 CLI 与 `check-pr-handoff.js --check-diff` 提供本地恢复校验与最终差异检查；远端分支保护 / 目标仓库 CI 若未配置仍为 `NOT_ENFORCED`，不得标成已强制。

**1. 权威与格式**
- 唯一权威 = PR 里被索引登记的那条评论，不是聊天、摘要、Brief 或五句话。公开仓库的评论公开可读：合同里不得有凭据或私人数据；涉密任务停下问用户。
- 评论格式：首行写任务 ID、类型、版本；然后 `<!-- reviewloop-<plan|design>:<任务ID>:<版本>:begin -->`、`<details>`、`<summary>…</summary>`、正文（以 `# Plan` 或 `# Design` 标题起始）、`</details>`、对应 `end` 标记。
- **哈希范围：** 以**真正的折叠块**为准——begin 标记之后的 `<details>` 内、`</summary>` 之后到 `</details>` 之前的正文，去首尾空白后的 UTF-8 SHA-256。评论头部说明文字里若出现字面的标记文本，不算折叠块边界，须取 begin 标记之后的那一对。**范围终点以 `end` 标记为准：** 正文可能引用字面的 `</details>`，取 `end` 标记之前最后一个 `</details>`，不得在正文里第一个 `</details>` 处截断。Plan 与 Design 用同一算法；Design 的值必须等于 ReviewLoop PASS 返回的 `designSha256`（评论末行 `designSha256:`）。其他空白处理会得到不同值，禁止自行换算法。
- PR 描述保留面向人的 Brief 与“合同索引”表：`任务ID · 类型 · 版本 · 评论编号(databaseId) · sha256 · 分段数 · 状态(current/superseded)`。
- 超过 60000 字符必须分段：每段带序号和总数，全文哈希另记。仅仓库所有者账号发布的评论可采用。
- **版本：** 冻结后修改 = 发新评论（v1.1…），索引把旧版标 `superseded`；评论被原地编辑不是正当修改。Design 内容变化使旧 PASS 与 `designSha256` 作废。

**2. 恢复程序（新会话或不同 Agent；任何一步失败即停止并报告，不得用聊天记忆、Brief 或摘要继续）**
1. 读 PR 描述索引取当前版本；交接包写的版本与哈希必须与索引一致。
2. 按评论编号直接取（不翻页、不搜索）；作者必须是所有者账号。
3. 取全部分段，标记齐全、序号连续、无重复无多出。
4. 拼接 → 去首尾空白 → SHA-256，与索引（Design 还要与 `designSha256`）比对，不等即停。
5. 评论有编辑记录：哈希一致可用并注明；不一致即停。
6. **信任锚的限度：** 索引与评论都在 PR 内，有写权限者可同时改两处，单凭二者互相比对挡不住协同改动。Design 以 ReviewLoop PASS 返回的 `designSha256` 为独立锚点，须同时核对它在 PR 之外的来源（本次会话输出或 ReviewLoop 记录）；Plan 没有独立锚点，哈希一致只证明评论与索引一致，不证明未被协同改动，涉及高风险合同时须由所有者确认。

| 失败 | 行为 |
|---|---|
| 评论缺失、被删、作者不符 | 停止，回到用户，不重建 |
| 哈希不符（被编辑或截断） | 停止；报告差异；用户决定是否走新版本 |
| 索引与评论版本冲突、出现多个 current | 停止 |
| 读取不全、超限、分段缺失 | 停止，不得截断后继续 |
| 可读但无法验证编辑历史 | 以哈希为准，一致可用并标注“编辑历史未核验” |

**3. 阶段顺序**
- **Plan：** 零文件引导（与 main 同树的空提交）→ Draft PR → Plan 评论 + 描述索引；到此停。
- **Design：** 先按第 2 节核对 Plan；`begin(design)` 以恢复出的 Plan 全文为合同；在仓库根目录创建尚不存在的未跟踪设计文件，审查至 PASS；不提交、不加忽略规则。
- **PASS 后：** 发设计归档评论和 ReviewLoop 返回的五句评论（逐字）；重新取回归档评论，哈希 = `designSha256` 才算归档成功，随后登记索引并**才**删除未跟踪的工作文件；校验失败则保留文件并停下。删除发生在 Code 开始前。
- **Code：** 按第 2 节恢复设计全文 → `begin(code, 全文, designSha256)`（由 ReviewLoop 再核对）。

**4. 什么进 PR，什么进 main**
- 能被后续任务当长期依据、且有维护人的 → 正式资产，可进 main，但须在 Work Contract 的“正式资产清单”逐条列出（路径、为何长期、谁维护）。
- 只服务本次任务审查的（Plan/Design 全文、引导提交、过程记录）→ 留在 PR。
- 最终 PR 差异里不得出现 `Plan*.md`/`Design*.md` 一类任务文件，或与已归档合同哈希相同的文件，清单内除外。该检查不得靠删除旧文件或隐藏审查证据来通过。
- ReviewLoop 本地检测与目标仓库的强制合并门禁（CI/分支保护/PR bot）分别验收。

**5. 仓库更名** 只以“清单 + 前后验证 + 回退”的运行手册形式存在于任务 PR，不进 main，改名本身须用户另行授权；已冻结任务文档不改写，旧名靠重定向读取，但重定向对各类客户端是否成立必须实测，不得当作保证。

## 名词
- **Plan**：完整的需求合同；新任务存为所属 PR 评论并在描述登记索引（见上节），旧任务沿用其任务分支里的 `Plan.md`。**Brief**：Plan 的短摘要，放在 PR 描述顶部，不是合同。
- **设计文件**：完整设计 + 末尾的 Work Contract。ReviewLoop 每轮审查它的完整内容。
- **designSha256**：设计 PASS 时 ReviewLoop 算出的、所审设计内容的指纹，Code 用它核对拿到的是同一份。
- **冻结合同（Frozen Contract）**：你确认后，任务目标、范围、全局验收标准、必要约束与验证义务固定下来。修 Bug 可以在原任务内继续，不能为了通过审查偷偷改标准；必要的实质变更由你批准并明确记录。
- **PR（Pull Request）**：GitHub 上请求把某个分支的修改合并入目标分支的记录。PR 创建不代表通过，也不代表已合并。

## 日常怎么做
### 每个任务
1. **Plan**：在 A（ChatGPT）或本地 Agent 说需求。A 查相关仓库，把完整 Plan 写出来；在你授权后，开草稿 PR（必要时用无文件变更的空提交引导），PR 描述顶部放 Brief、验收清单和合同索引，完整 Plan 存为 PR 评论（见“任务合同归档与恢复”）；旧任务沿用原路径。**到此停。**
2. **Design**：你说“Design”。本地 Agent 先开始设计 loop，再写设计文件，自动审查和返工；PASS 后在 PR 评论发不超过五句的说明，包含需要你确认的默认前提和授权。你读这几句，划掉不成立的前提。**到此停。**
3. **Code**：你说“Code”。本地 Agent 把通过审查的设计原文交给代码 loop 并带上 `designSha256`，按授权实施、验证、自动修复；本地 PASS 后停，按你已授权的范围 commit/push，PR bot 与 CI 审查，你做必要的实际验收，合并由你决定。

只有合同明确要求真实使用/科研验收时，你才做对应操作。merge 永远按你授权，不因 PASS 自动进行。

### 返工
普通实现缺陷：自动审查驱动的修复由 Worker 在原 loop 里完成，不让你逐条转述。独立 Reviewer 完整审查后给一份集中修复 prompt，直接复制给原 Worker；重大产品/架构变化才回 A。设计 PASS 之后改了设计内容，旧的 PASS 作废，需重新过设计审查。

设计已获批但基础尚未实现时，不得将基础标为可用。已存在并保持不变的获批设计不为每个后续功能重新过设计审查；但新任务仍有自己的 Plan 和 Design，可以很短并引用既有设计。

## 只保留两类项目材料
长期项目使用一份已有项目页/文档维护目标、重要决定/架构引用与状态、路线图、当前任务。每个任务一份冻结合同（Plan + 设计），后续交付/审查证据放在其关联 issue/PR 中，尽量复用现有存储。

这是信息分类，不要求每类单独文件。共享基线与任务版本都必须可定位；复制到 prompt 的约束有来源，不成为可独立修改的第二权威。更新 GitHub 文档需要相应授权，不能因为“统筹”便默认可写。

### 最小项目记录（按需）
项目/仓库与核查基线、任务 `policy_sha`（无历史记录则标未知）：
目标和非目标：
重要决定/架构引用：版本；设计状态；实际落地证据；尚未落地范围。
任务：ID；目标；依赖；完成条件；状态/证据。
当前下一步与必要权限：

### 每次交接包（由 AI 整理，不由用户整理）
任务/合同版本与固定的 `policy_sha`；仓库、分支、base/head（适用时）；完整 Plan 与设计内容或可访问版本；设计状态与 `designSha256`、审查依据及操作授权；PR/差异与 AC 证据；审查范围及结论；返工场景还须附当前 loop/PR bot 状态与所审 HEAD 的可信证据；未决项；接收者现在要做的事。

发给 Worker 的指令自包含必要要求；发给 Reviewer 的材料包含足够需求与上下文，但不将作者的自信或 PASS 主张当证据。无法访问引用时附内容，不能靠回忆补全。

## 可直接复制的启动语
### 主控 A
```text
你是我的工程主控。通过已连接的 GitHub 读取 Jiaze-Li/personal-skills：新任务先确定 main 的完整 policy_sha，并从该 SHA 读取 engineering-lead/skill.md；已有任务沿用交接包中的 policy_sha。
所有任务走 Plan → Design → Code，每个阶段结束都停下，等我说下一步。
我会与你讨论需求，你整理出一份完整 Plan（不只是摘要）；我说“Design”之后，把它交给本地 Agent。
你不得给自己签发独立验收；需要独立审查时，直接整理好交接包。
保持现有 ReviewLoop/PR bot，不新增重复关卡。默认只读，不提交或修改仓库。
项目仓库：<仓库>。当前目标：<目标>。
```

### 本地 Agent：Design 阶段（我说“Design”之后使用）
```text
任务 <ID>，policy_sha=<完整 SHA>。按该 SHA 读取 Jiaze-Li/personal-skills 的 engineering-architect/skill.md 和 engineering-workflow/README.md。
先按“任务合同归档与恢复”从 PR 评论恢复并核对完整 Plan（旧文件模式按原路径读取）；再用 reviewloop_begin（taskType=design）：完整 Plan 作为合同，设计文件使用一个尚不存在的未跟踪路径；然后再创建设计文件。
设计文件含 Options、Assumptions、已核实事实（带出处的摘录）和末尾的 Work Contract。按 ReviewLoop 返回的状态在同一 loop 修改并复审；不得 commit 设计文件。
PASS 后（在有 PR 评论授权时）先把设计全文归档到 PR 评论、更新索引并回取校验哈希 = designSha256，校验成功后才删除未跟踪的设计工作文件（失败则保留并停下），并发不超过五句的说明和 designSha256，然后停止，等我说“Code”。
```

### 本地 Agent：Code 阶段（我说“Code”之后使用）
```text
任务 <ID>，policy_sha=<完整 SHA>，designSha256=<值>。按该 SHA 读取 engineering-task-spec/skill.md。
从 PR 评论恢复并核对通过审查的设计原文（旧文件模式按原路径读取），逐字交给 reviewloop_begin（taskType=code）并带上 designSha256；对不上就停下告诉我。
授权：<修改/commit/push/PR/merge/部署/破坏性/权限 各自写明，未写视为未授权>。本地 PASS 后停止。
```

### 独立 Reviewer B（需要时新开，不用 A 改名冒充）
```text
通过已连接的 GitHub，按交接包中的 policy_sha（不是任意最新 main）读取 Jiaze-Li/personal-skills 的 engineering-reviewer/skill.md，并独立审查下面的交接包。旧任务无 SHA 时标明未知且不得倒改原验收合同。
先确定设计审查还是实现审查，核实合同版本、仓库基线和实际证据。
完成整个有边界的审查后一次性给结论和问题，不边查边发修复 prompt。
普通实现缺陷给可直接复制给原 Worker 的合并修复 prompt；重大设计变化回主控。
我未授权你修改代码、数据、合同或合并 PR。
<粘贴 A 的设计审查包，或 Worker 的完成包与任务合同>
```

日后回 A 通常只需说“审查结果和必要用户验收如下，请核对后更新进度并给下一任务”，不复制整段历史。仓库内容可读时直接给精确 PR/提交引用。

## 用 SpinLab 演示（说明流程，不断言当前代码状态）
目标：手机可创建 Sample。
**Plan**：A 写出完整 Plan（问题、谁用、不做什么、验收），并检查是否已有统一身份、唯一权威和相关消费者合同。到此停。
**Design**：你说“Design”后，本地 Agent 比较路线（优先复用现有身份机制），写出设计：displayName/旧 sampleKey/永久身份的关系和兼容边界，以及末尾的 Work Contract；自动审查通过后给你五句话。到此停。
**Code**：你说“Code”后，先做最小基础实施（或先行阶段）：证实创建与相关读取走同一身份，改名不会断关联，必要旧数据/重启场景成立；在 Worker 实际基线包含已验证基础后，才让手机创建入口消费它。Notebook 等后续能力复用同一合同，不各自发明身份。
这不要求先建完所有未来数据库表、所有消费者功能或整个统一平台。

## 动态评测怎么做
无需增加常驻 Agent 或后台控制器。每次修改四份工程 Skill 或 Project Settings 后，使用固定 `policy_sha` 在**新的主控对话 A 和独立审查对话 B**运行 [EVALS.md](EVALS.md) 的案例：既测试正确阻塞，也测试符合条件时能顺利交接。每个案例保存实际原始输出、模型/环境、所用 SHA、期望与实测分流、阻塞/权限处理、PASS/FAIL 及证据链接；只读模拟测试不允许声称真的运行过 Worker 或 PR bot。

**发布门槛：** 正反向案例没有真实运行与证据，状态为 NOT RUN；出现 P1 的 FAIL 则修复并重跑对应案例和相关回归；其余问题记录后可作阶段性试用判断。模拟评测完成后，用一次真实小任务（完整走 Plan → Design → Code）、一次共享基础任务和一次 PR REWORK 闭环记录实战证据。规范改动时重跑固定案例；真实任务结束时抽查是否遵守阶段停止点、授权、引用和证据义务，不要求每天人工检查。

## 版本一致性、权限与评测
新任务在首次正式规划时固定 personal-skills 的完整 Git commit SHA，后续所有角色以其为唯一方法规范基线。现有 ReviewLoop/PR bot 的强制政策、状态及仓库安全规则不被旧方法快照覆盖；发生实质冲突需报告。Worker 必须分别知道修改、commit、push、创建 PR、merge 等操作是否获授权，未获授权的不执行。请按 [固定评测案例](EVALS.md) 记录正反向的实际结果，不要把文字场景直接当作执行 PASS。

## 版本变更与迁移
### v1.0.4 → v1.1.0（统一流程）
| 变化 | 说明 |
|---|---|
| 删除 Tier 1/2/3 和独立 Gate 判定 | 所有任务走 Plan → Design → Code，设计一律独立审查 |
| 删除 `USER WAIVED` | 设计审查由 ReviewLoop 自动完成、成本很低，不再设用户豁免；ReviewLoop 不可用时用独立对话 B，仍不可用则阻塞并报告 |
| `design_ref`（Git commit+路径）→ `designSha256` | 由 ReviewLoop 对所审设计内容计算，Code 启动时核对 |
| 设计走 Supervisor 池 → 普通 Reviewer 池 | 由 ReviewLoop 实现，方法侧不再描述模型池 |
| 评论标记 `<!-- reviewloop-design:v1 -->`、`Status: DESIGN_PASS` | 不再要求；没有任何程序读取它，评论只保留五句话和 `designSha256` |
| 阶段停止点 | Plan、Design、Code 各自停止，等你明确指令 |
| ReviewLoop 操作细节 | 不再在本仓库复述（含此前写死的 Worker Contract 版本），以已安装版本为准 |

新规范不会自动使旧任务合同失效；已冻结任务沿用其原 `policy_sha` 与合同，旧的 `design_ref`、`USER WAIVED` 记录保持原义。

### 从 v11.5 到 v1.0.4
v11.5 依据：`Jiaze-Li/personal-skills` commit `18448e3a43502e25149271784551beae91d1630a`，路径 `engineering-task-spec/skill.md`。

| 原职责 | 新归属 |
|---|---|
| 需求收敛、跨任务依赖、状态与授权交接 | Lead |
| 设计内容、共享不变量、架构合同 | Architect |
| 单任务 Approach、阶段、AC、证据义务、薄工具交接 | Task Spec |
| 独立设计评审、全量 PR 检查、集中返工、根因审计触发 | Reviewer |
| 工具 API、执行状态机、自动审查预算、PR bot 协议 | 现场 Worker Policy，不复制 |

原 v11.5 和 v1.0.4 可从 Git 历史查看；新规范的实际协作成效仍需通过后续任务验证。

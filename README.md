# personal-skills

个人 AI Skills 仓库。**一个 Skill 对应一个稳定目录和一个当前有效入口**（`skill.md` 或 `SKILL.md`）；历史版本通过 Git 恢复。

下面按**用途**分类，便于选择和扩展。分类是 README 导航，不是实际目录层级；当前所有 Skill 目录仍位于仓库根目录，避免破坏现有相对链接、固定 Git 引用与外部加载路径。

## Skill 索引

### Engineering — AI 工程协作

| Skill | 职责 | 何时使用 | 入口 |
| --- | --- | --- | --- |
| **Engineering Lead** | 需求收敛、路线与依赖管理、任务交接；工程主控默认入口 | 开始或继续工程项目、确定下一任务与所需角色时 | [`engineering-lead/skill.md`](engineering-lead/skill.md) |
| **Engineering Architect** | 共享身份、数据权威、接口、迁移及高风险不变量的架构合同 | 任务涉及跨模块关键设计或重要科研语义时，按需加载 | [`engineering-architect/skill.md`](engineering-architect/skill.md) |
| **Engineering Task Spec** | 将已确认目标及架构约束编译为自包含 Worker Prompt、AC 与验证要求 | 设计前提已明确，需要交给 Coding Agent 实施时 | [`engineering-task-spec/skill.md`](engineering-task-spec/skill.md) |
| **Engineering Reviewer** | 独立设计/实施审查、返工判定与完整复审 | 需要独立 Design Gate 或实现审查时，在独立审查上下文加载 | [`engineering-reviewer/skill.md`](engineering-reviewer/skill.md) |

**工程协作方式（v1.0.4）：** 一个主控 GPT 对话 → 一个 Coding Agent Worker → 按风险调用独立 Reviewer。四个角色按需加载，并非四个常驻对话；现有 ReviewLoop / PR bot 仍负责开发执行流程，不另设控制器。

- [AI Engineering Workflow 使用说明](engineering-workflow/README.md)：完整流程与可复制的 ChatGPT Project Settings。
- [Engineering Workflow EVALS](engineering-workflow/EVALS.md)：固定评测案例与记录模板。

`engineering-workflow/` 是**配套文档目录**，不是第七个 Skill。

**版本边界：** 新工程任务按 Engineering Lead 规范记录 `policy_sha`；进行中任务按其固定 SHA 加载相关 Skill，不因为 `main` 后续更新而自动切换。原 Engineering Task Spec v11.5 保留于 Git 历史（commit `18448e3`），已冻结任务沿用原合同；新规范不追溯修改旧任务验收要求。

### Scientific Computing — 科研数据处理

| Skill | 职责 | 何时使用 | 入口 |
| --- | --- | --- | --- |
| **AFM Gwyddion Style** | 从 AFM `.ibw` 数据生成指定 Gwyddion 风格科研图，内含处理脚本、固定配色与回归样例 | 已提供 AFM 数据，需要按既定流程处理并出图时 | [`afm-gwyddion-style/SKILL.md`](afm-gwyddion-style/SKILL.md) |

脚本、配色与测试文件属于该 Skill 的实现资产，不另计为独立 Skill。

### Research Communication — 科研表达

| Skill | 职责 | 何时使用 | 入口 |
| --- | --- | --- | --- |
| **Research Presenter** | 按既定物理科研汇报风格制作、修改和审核幻灯片 | 准备组会、学术报告或编辑 PowerPoint 演示文稿时 | [`research-presenter/SKILL.md`](research-presenter/SKILL.md) |

## 新增与维护约定

1. **先判断是否真需要新 Skill。** 可重复调用、职责清晰、具有稳定输入/输出或操作约束的能力适合独立成 Skill；一般说明书、工作流资料、脚本资产应留在所属 Skill 或文档目录。
2. **先登记到本 README。** 新增 Skill 时填上领域、职责、触发条件和实际入口路径；本表作为唯一总索引，避免维护多份彼此冲突的分类清单。
3. **稳定路径优先。** 现有 `skill.md` / `SKILL.md` 大小写及内部相对路径先保持原样。若将来统一为特定 Agent Skills 加载格式，应单独评估兼容性并更新所有引用，不把文件改名当作纯排版。
4. **不把导航调整当作规则更新。** 更改 Skill 本文、权限、验收标准、版本或目录位置，应在独立的变更中说明影响；已冻结工程任务仍遵守自身的 `policy_sha` 与合同。
5. **保持轻量。** 目前只有六个 Skill，采用根目录平铺 + README 逻辑分类；只有当导航确实难以维护时，才另行设计实体分类目录和迁移计划。

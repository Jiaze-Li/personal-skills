# personal-skills

个人 AI Skills 仓库。**一个 Skill 对应一个稳定目录和一个当前有效入口**（`skill.md` 或 `SKILL.md`）；历史版本通过 Git 恢复。

下面按**用途**分类，便于选择和扩展。分类是 README 导航，不是实际目录层级；当前所有 Skill 目录仍位于仓库根目录，避免破坏现有相对链接、固定 Git 引用与外部加载路径。

## Skill 索引

### Engineering — AI 工程协作

所有工程任务走同一条路：简报（只授权出方案）→ 设计（含“实施授权与合同”）→ 用户确认 → 连续实施 → 评审 → 用户验收并决定合并。流程全文见 [`engineering-workflow/README.md`](engineering-workflow/README.md)。

| Skill | 职责 | 何时使用 | 入口 |
| --- | --- | --- | --- |
| **简报**（Engineering Lead） | 把想法收敛成简报：要做成什么、不做什么、验收步骤、授权“只出方案” | 开始一个新任务时 | [`engineering-lead/skill.md`](engineering-lead/skill.md) |
| **设计与实施合同**（Engineering Task Spec） | Worker 根据简报写设计，含“实施授权与合同”一节及证据要求 | 简报已定，要出设计和合同时 | [`engineering-task-spec/skill.md`](engineering-task-spec/skill.md) |

原先的 Architect 和 Reviewer 两个角色已退役：设计由 Worker 写、ReviewLoop 评审，不再另开对话。它们的原文保留在 Git 历史中。

`engineering-workflow/` 是**配套文档目录**，不是 Skill。其中 `EVALS.md` 是旧版（四角色流程）的评测案例，待按 v2.0 重写。

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

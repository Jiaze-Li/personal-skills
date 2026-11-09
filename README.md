# personal-skills

个人 AI Skills 仓库。每个 Skill 一个目录，入口为 `skill.md` / `SKILL.md`；每个 Skill 只保留一份当前有效版本，历史版本通过 Git 恢复。

## AI Engineering Workflow v1.0.2

日常操作：**一个主控 GPT 对话 → 一个 Coding Agent Worker → 按风险调用独立审查**。角色按需加载，并非四个常驻对话。开发执行仍沿用已有 ReviewLoop / PR bot，不重复设立控制器。

- [Engineering Lead](engineering-lead/skill.md)：需求收敛、Roadmap、依赖和任务交接（默认入口）。
- [Engineering Architect](engineering-architect/skill.md)：共享数据权威、身份、接口和重要架构合同（按需）。
- [Engineering Task Spec](engineering-task-spec/skill.md)：自包含 Worker Prompt、阶段、AC 和验证证据。
- [Engineering Reviewer](engineering-reviewer/skill.md)：独立设计/实现审查、集中返工、完整复审。

完整使用流程及**可复制的 ChatGPT Project Settings**：[AI Engineering Workflow 使用说明](engineering-workflow/README.md)。固定评测案例与记录模板：[Engineering Workflow EVALS](engineering-workflow/EVALS.md)。

原 Engineering Task Spec v11.5 保留于 Git 历史（commit `18448e3`），已冻结任务沿用原合同；新规范不追溯改动旧任务的验收要求。

## 其他 Skills

- [AFM Gwyddion Style](afm-gwyddion-style/)
- [Research Presenter](research-presenter/)

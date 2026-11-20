# skills

个人非工程领域 AI Skills 仓库。**一个 Skill 对应一个稳定目录和一个当前有效入口**（`SKILL.md`）；历史版本通过 Git 恢复。

> **说明：** Engineering Workflow 已迁移至 [`Jiaze-Li/reviewloop/engineering/`](https://github.com/Jiaze-Li/reviewloop/tree/main/engineering)。历史旧任务的工程规范与合同按其各自记录的完整 commit SHA 从 Git 历史恢复。

## Skill 索引

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

1. **先判断是否真需要新 Skill。** 可重复调用、职责清晰、具有稳定输入/输出或操作约束的能力适合独立成 Skill；一般说明书、脚本资产应留在所属 Skill 目录。
2. **先登记到本 README。** 新增 Skill 时填上领域、职责、触发条件和实际入口路径；本表作为唯一总索引，避免维护多份彼此冲突的分类清单。
3. **稳定路径优先。** 现有目录名、`SKILL.md` 大小写及内部相对路径保持稳定，避免破坏现有外部引用与本地加载路径。
4. **保持轻量。** 当前仅维护非工程领域 Skills，采用根目录平铺 + README 逻辑分类。

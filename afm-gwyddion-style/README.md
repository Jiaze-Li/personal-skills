# AFM Gwyddion 风格绘图 Skill · v2.1

## 最简单的用法

在支持文件处理和 Python 执行的对话中，同时上传**整个 ZIP**和新的 `.ibw` 文件，发送：

> 按这个 skill 处理我的 AFM 数据，直接给我 PNG，保持默认格式。

不需要安装或手动操作 Gwyddion。不要只上传 SKILL.md；脚本和固定色表都在 ZIP 内。文件校准无法读取时，程序会明确报错，不会猜单位和比例尺。

这一版仅把图内比例尺标签从 32 pt 增至 **38 pt、加粗斜体**，并保留细暗色描边。数字、μ、m 都加粗，仍居中且靠近横线。色标数字保持 **29 pt**，配色、较远色条、两位小数、裁边和自动 flatten 与 v2 不变。

## 包内文件

- `SKILL.md`：给另一对话的完整操作规则。
- `scripts/plot_afm.py`：真正可运行的绘图程序，不只是提示词。
- `assets/approved_palette.csv`：固定配色，无需联网。
- `examples/scale_label_1um.png`、`examples/scale_label_5um.png`：新字号参考。
- `tests/test_core.py`：解析与处理测试。
- `requirements.txt`：NumPy、Matplotlib、Pillow。

## 本地运行（可选）

```bash
python -m pip install -r requirements.txt
python scripts/plot_afm.py scan.ibw -o scan_AFM.png
python tests/test_core.py
```

输出 PNG、处理记录 JSON 和未做显示 clipping 的高度 NPZ。自动处理是经验策略，不是对扫描伪影物理来源的证明；原始 IBW 保持不动。

## 名称说明

“Gwyddion 风格”描述当前认可的显示外观。本包以固定 LUT 复现这套配色，拟合和绘制由 NumPy/Matplotlib 完成，**不是启动 Gwyddion，也不宣称数值处理与其内部实现完全相同**。

字体依赖运行环境：Times New Roman 优先，缺失时用 Liberation Serif 等替代。包内不含字体文件或原始实验 IBW。

## 可选字号覆盖

```bash
python scripts/plot_afm.py scan.ibw -o scan_AFM.png --scale-font 38 --scale-weight bold
```

无需手动指定时，以上就是默认值。其他对话应运行包内脚本，不应只参考提示词重新实现。

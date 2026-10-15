---
name: afm-gwyddion-style
description: 从用户上传的 AFM .ibw 原始高度数据生成固定 Gwyddion 风格科研图。自动读取通道和扫描尺寸，检查边缘、robust flatten、P5–P99 线性显示，使用白底、较远的色标、大字体和两位小数。用户说“按这个 skill 画 AFM”时直接运行附带脚本。
---

# AFM：上传 IBW 即出图

## 立即执行

用户上传本 ZIP 和 `.ibw` 时，在当前对话的 Python/代码执行环境解压本包，读取此文件后运行附带脚本，不重新设计图像、不重新搜索文献、不要求用户操作 Gwyddion。

```bash
python afm_gwyddion_style_v2_1/scripts/plot_afm.py INPUT.ibw -o OUTPUT_AFM.png
```

路径用当前运行环境中实际存在的路径替换；不要使用之前对话里的绝对路径。只要运行环境已有 NumPy、Matplotlib 和 Pillow，就不需要联网、Gwyddion、Igor Pro 或额外的 IBW 解析库。

完成后检查 PNG，直接显示预览并给出可下载链接。默认回复简短，不重复研究背景。不得声称文件已生成而未实际运行并确认文件存在。若没有文件处理/代码执行环境，明确说明不能在那个环境执行本包；不要用生成式图片代替数据图。

## 锁定版式：不要自行调色

- 白色背景；主图细黑边；不显示横纵坐标刻度；默认 350 dpi。
- 配色读取 `assets/approved_palette.csv`：这是从本对话最终认可的 Gwyddion 风格图固定的 256 色 LUT。包内包含全部颜色，无需从旧图或互联网取色。不得换成自制 Gold、afmhot、hot 或 inferno。
- 数值归一化是 **linear**；不做 gamma、对数、直方图均衡化或 P50 强制居中。色阶位置线性不等于人眼感知亮度线性。
- 比例尺文字 **38 pt、加粗斜体**（v2 为 32 pt 常规斜体）；数字、μ 和 m 全部使用同一字体、同一粗细。色标上下限文字仍为 **29 pt、常规字重**，不随比例尺一起放大。默认画布 6.4 × 5.0 inch。
- Times New Roman 优先；缺失时 Liberation Serif → Tinos → DejaVu Serif。应保留程序报告的实际字体，不谎称安装了 Times New Roman。包中不得附字体文件。
- 白色比例尺在图内左下角；文字在横线正上方居中，保持原有接近横线的距离。用 1 pt、35% 不透明度的细黑描边改善文字与局部浅色背景的分离；不添加底色框，不改动下面的高度图。1 μm、5 μm、10 μm 等标签均使用相同规则。
- 按裁后真实视野自动选择 1/2/5 系列比例尺。当前约 18 μm 视野用 **5 μm**，别的扫描尺寸不能照抄 5 μm。
- 右侧色标及数字保持已认可的较大间距：相对旧位置整体向右移动 **100 px @ 350 dpi**，物理移动量约 0.286 inch；更改 dpi 时物理间距不变。
- 色标只显示上下限，单位 nm，默认 **两位小数**。从未舍入的真实显示限计算标签。例如 0.188558 → 0.19；−0.284902 → −0.28。不要先舍入成 −0.285 再舍入。
- 字号变化不能改动高度数组、裁边、flatten、显示范围或配色。修改版式时复用相同处理结果。

## 数据处理顺序

### 1. 读取与校准

脚本支持小端/大端实数 **Igor Binary Wave v5**，2D 高度图或 3D 多通道图。解析真实维度、类型、通道标签块和物理单位，不硬编码 256×256、三个通道或“第一个通道就是 Height”。默认通道优先级为 HeightRetrace → HeightTrace → Height。

单位来自文件头；未知单位或电压单位不得用数量级猜 nm。扫描尺寸优先读取 Asylum `FastScanSize`、`SlowScanSize`、`ScanSize` SI 元数据，缺失时用有单位的维度坐标。不能确认的文件报出具体缺失信息，由用户确认校准；不伪造比例尺。不是 v5 时请求适用的导出文件，不把任意 bytes 当浮点。

### 2. 边缘检查与裁剪

沿用已批准的启发式：比较外围 5% 与中央区域的中位数偏移/IQR 和极值富集程度；明显异常时对称裁四周各约 5%，否则不裁。它是可复现的经验规则，**亮边本身不能证明是仪器伪影**。不要宣称该程序自动识别了真实物理原因，或一定裁到了最小异常宽度。

裁剪只选择子区域，不修改保留像素值。裁后尺寸为原扫描尺寸 × 保留像素数 / 原像素数；比例尺随之更新。所有裁边像素数写入 processing.json。用户要求完整图时用 `--crop 0`；不得无限裁边以获得好看的结果。

### 3. 自动 robust flatten

先拟合一阶背景，再拟合总次数≤2的二维二阶背景（1,x,y,x²,xy,y²）。迭代最多 8 次，每次用残差中位数/MAD 和 2.5σ 阈值降低孤立高/低点对背景拟合的影响。

使用行/列中位数峰峰值的大者评估残余长波变化；二阶比一阶降低超过 25% 才选择二阶。默认不做逐行校平、不平滑、不降噪、不锐化、不做 AI 重绘。

高度基准沿用已认可公式：`processed = cropped − background + median(background)`。**Flatten 确实改变处理后的高度数值**；不能说它只改变配色，也不能保证去掉的一定都是仪器背景。真实长波形貌也可能被减掉。保留原 IBW，输出背景及未被显示 clipping 的处理后高度数组，以便检查、重算。这个自动判据是本包的经验策略，不是文献标准或 Gwyddion 默认算法。

### 4. 显示范围

在裁后且 flatten 后的有效像素上计算 **P5–P99**，按像素数量排序取百分位数。小于 P5 / 大于 P99 仅在显示时用端点色；一般约 5% / 1%，重复高度值可能改变比例。中间保持线性数值映射。

不用 raw min/max 决定默认色标；不用对称 P50 范围。RMS/Ra 等定量值不能从裁到色标范围后的像素值或 PNG 反算。多个样品要直接比较时使用统一 `--zrange MIN MAX` 并说明共同基准，不把独立自动色标当作定量对比。

## 输出

- `OUTPUT_AFM.png`：最终图。
- `OUTPUT_AFM.processing.json`：输入哈希、通道、单位、视野、裁边、flatten 阶数、实际色标、饱和比例、实际字体、警告。
- `OUTPUT_AFM.processed.npz`：未做显示 clipping 的处理后高度、裁后输入高度、拟合背景、视野和色标数值。

默认给用户 PNG。用户要追溯数据时再提供 JSON/NPZ。所有文件可在新对话重建，不依赖本对话的状态。

## 常用覆盖选项

```bash
python scripts/plot_afm.py INPUT.ibw -o figure.png --crop 0
python scripts/plot_afm.py INPUT.ibw -o figure.png --crop 0.05 --flatten 2
python scripts/plot_afm.py INPUT.ibw -o figure.png --flatten none
python scripts/plot_afm.py INPUT.ibw -o figure.png --low-pct 5 --high-pct 99
python scripts/plot_afm.py INPUT.ibw -o figure.png --zrange -0.30 0.20
python scripts/plot_afm.py INPUT.ibw -o figure.png --scale-font 38 --scale-weight bold --label-font 29
python scripts/plot_afm.py INPUT.ibw -o figure.png --scan-um 20 20 --height-unit m
```

最后一行的校准覆盖只在用户确认单位和尺寸后使用。不要把示例数字默认套到新文件。

## 已有样本的回归参考

LSMO19_CONTACT_0001：HeightRetrace，20×20 μm，256×256；四边各13 px，230×230，约17.96875×17.96875 μm；自动二阶flatten；P5约−0.284902 nm，P99约+0.188558 nm；标签−0.28和0.19 nm。本次字号示例见 `examples/scale_label_1um.png` 和 `examples/scale_label_5um.png`（示例来自 LNO15 与 LNO23，不是上述 LSMO19）。这些仅用于回归验证，**不能写死到新数据**。

## v2.1 更新范围

仅加强图内比例尺标签：32 → 38 pt，完整标签加粗斜体，轻微加强细描边。白色横线长度/粗细、标签居中与间距、主图尺寸、固定 LUT、右侧色条位置/宽度、色标数字 29 pt、两位小数和全部数据处理规则保持 v2 不变。

用户只说“画这个”时直接用本包默认参数运行，不再询问字号，不重新设计配色。不要为追求外观自行额外裁边、加平滑或修改显示范围。

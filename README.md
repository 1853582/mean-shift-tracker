# Mean-Shift 跟踪器 (Mean-Shift Tracker)

基于颜色直方图的目标跟踪算法实现，使用 Mean-Shift 算法在视频帧序列中追踪指定目标。

> 项目作者：Luís Brandão
> 来源：阿姆斯特丹大学，智能多媒体系统课程 (Intelligent Multimedia Systems)，2009 年秋季

## 算法简介

Mean-Shift 是一种基于核密度估计的非参数跟踪算法。本项目通过以下步骤实现目标跟踪：

1. **目标建模**：在初始帧中由用户框选目标区域，计算该区域的归一化 RGB 颜色直方图作为目标模型。
2. **候选区域评估**：在后续帧中，以当前目标位置为候选区域，计算其颜色直方图。
3. **相似度度量**：使用 Bhattacharyya 系数衡量目标直方图与候选直方图之间的相似度。
4. **权重计算与位置更新**：根据直方图比值计算每个像素的权重，按 Mean-Shift 迭代公式更新目标位置，直到收敛或达到最大迭代次数。

## 文件结构

```
Source/
├── main.m                      # 主程序入口，负责读取帧序列并驱动跟踪流程
├── mean_shift.m                # Mean-Shift 迭代核心算法
├── RGB2rgb.m                   # 将 RGB 值转换为归一化 rgb
├── im_weighted_2D_histogram.m  # 计算带核权重的二维颜色直方图
├── bhattacharyya_coef.m        # 计算 Bhattacharyya 相似度系数
├── compute_weights.m           # 根据目标/候选直方图计算像素权重
├── kernel_mask.m               # 生成 Epanechnikov 核掩膜
├── epanechnikov.m              # Epanechnikov 核函数
├── get_target_image.m          # 从图像中提取目标区域
├── get_center.m                # 计算矩形中心坐标
├── get_coordinates2.m          # 根据中心点和宽高生成像素坐标（绝对坐标）
├── get_coordinates3.m          # 生成相对于中心的像素坐标（相对坐标）
├── hist_back_propagate.m        # 直方图反向投影
└── weight_histogram.m          # 对直方图施加核权重
```

## 架构图

系统分为三层：**入口层**（`main.m`）负责读取帧序列、框选目标并驱动整个跟踪流程；**核心层**（`mean_shift.m`）实现 Mean-Shift 迭代跟踪；**基础工具层**提供可复用的直方图、核函数、坐标计算等纯函数。

```
┌─────────────────────────────────────────────────────────────┐
│                       入口层 · main.m                       │
│                                                             │
│  读取初始帧 → imshow + getrect 框选目标                     │
│  → 构建目标模型 → 逐帧调用 mean_shift → 绘制并保存结果帧    │
└──────────────┬───────────────────────────────┬──────────────┘
               │ 目标建模（初始帧，一次性）    │ 逐帧跟踪
               ▼                               ▼
┌──────────────┬──────────────┐ ┌──────────────┬──────────────┐
│ 目标模型构建（q）           │ │ mean_shift.m 核心迭代       │
│ get_target_image            │ │ get_target_image            │
│ RGB2rgb                     │ │ im_weighted_2D_histogram(p) │
│ kernel_mask → epanechnikov  │ │ bhattacharyya_coef ρ(p,q)   │
│ im_weighted_2D_histogram(q) │ │ compute_weights → 权重 w    │
│ get_coordinates2            │ │ get_coordinates3 → y1       │
└──────────────┬──────────────┘ └──────────────┬──────────────┘
               │ q（目标直方图）               │ y1（新中心）
               ▼                               ▼
┌──────────────┬───────────────────────────────┬──────────────┐
│                  基础工具层（可复用函数）                   │
│  RGB2rgb · kernel_mask · epanechnikov · get_center          │
│  im_weighted_2D_histogram · bhattacharyya_coef              │
│  compute_weights · get_coordinates2 · get_coordinates3      │
│  hist_back_propagate · weight_histogram                     │
└─────────────────────────────────────────────────────────────┘
```

数据流：`main.m` 在初始帧上构建目标直方图 `q`（仅一次）；后续每帧将 `q` 与当前帧传入 `mean_shift.m`，迭代计算候选直方图 `p` → 相似度 `ρ(p,q)` → 像素权重 `w` → 新中心 `y₁`，直至收敛或达到最大迭代次数（10 次），返回的新中心用于更新目标矩形并保存结果帧。

## 使用方法

### 环境要求

- MATLAB（需包含 Image Processing Toolbox，提供 `imread`、`imshow` 等函数）

### 运行步骤

1. 将待跟踪的视频帧序列放入 `./Frames/` 目录，命名为 `Frame0001.png`、`Frame0002.png` 等。
2. 在 `main.m` 中设置 `target_frame` 为初始帧路径，并调整循环范围 `85:1:285` 以匹配你的帧序列。
3. 运行 `main.m`。
4. 程序会显示初始帧，用鼠标在图像上框选目标区域（拖拽矩形）。
5. 程序自动跟踪目标，并将每帧结果保存到 `./Frames/Result/` 目录。

### 关键参数

| 参数 | 位置 | 说明 |
|------|------|------|
| `NUM_BINS` | `main.m` / `mean_shift.m` | 颜色直方图的 bin 数量（默认 16） |
| 帧序列路径 | `main.m` 中的 `path` | 输入帧所在的目录 |
| 结果路径 | `main.m` 中的 `result_path` | 跟踪结果输出目录 |
| 跟踪范围 | `main.m` 中的循环 `85:1:285` | 起始帧到结束帧 |
| 最大迭代次数 | `mean_shift.m` 中的 `count < 10` | Mean-Shift 单帧最大迭代次数 |

## 算法流程图

```
初始帧 → 框选目标 → 计算目标直方图 (q)
                          │
                          ▼
              ┌──→ 读取下一帧 ──┐
              │                │
              │   计算候选区域直方图 (p)
              │                │
              │   计算 Bhattacharyya 系数 ρ(p, q)
              │                │
              │   计算像素权重 w_i
              │                │
              │   Mean-Shift 更新位置 y1
              │                │
              │   评估新位置相似度，决定是否继续迭代
              │                │
              └── 迭代收敛 ──┘
                          │
                          ▼
                    输出跟踪结果 → 保存帧
```

## 核函数

本项目使用 **Epanechnikov 核**：

$$
K(x) = \begin{cases} \frac{1}{2} c_d^{-1} (d+2)(1 - x) & x \le 1 \\ 0 & x > 1 \end{cases}
$$

其中 $d$ 为维度（此处 $d=2$），$c_d$ 为 $d$ 维单位球体积（此处 $c_d = \pi$）。

## 许可

本项目为学术课程作业，仅供学习与研究使用。

## 运行前准备

1. 将 `Source` 目录加入 MATLAB 路径，例如在项目根目录执行 `addpath('Source')`，然后在 MATLAB 中运行 `main.m`。
2. `main.m` 中的路径均为相对路径，需要按本机环境调整（以源码实际内容为准）：
   - 初始帧：`target_frame = imread('./LabImages/Frame0085.png')`，请改为本机实际存放初始帧的路径。
   - 帧序列目录：`path = './Frames'`，循环范围为 `85:1:285`，帧命名格式为 `Frame%04d.png`（如 `Frame0085.png`）；若改用 `ThreePastShop1cor` 或 `ropeframes` 序列，需同步切换被注释的 `path` 与帧命名格式。
   - 结果输出目录：`result_path = './Frames/Result'`，请确认该目录已存在，避免 `saveas` 保存失败。

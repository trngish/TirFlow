# PhotoArt Desktop 设计文档

## 概述

将现有 Gradio 版写真训练框架转换为独立的 PySide6 桌面应用程序，输出 Windows .exe。

## 目标

- 独立项目：`D:\TirFlow\photo_art_desktop/`
- 保留 `photo_art_framework/` 的所有现有功能
- Windows .exe 打包输出（基于 Nuitka）
- 界面使用 qfluentwidgets（流畅设计风格）

## 目录结构

```
photo_art_desktop/
├── main.py                     # PySide6 程序入口
├── requirements.txt             # Python 依赖
├── build.spec                  # Nuitka 打包配置
├── config.py                   # 配置（复用 photo_art_framework/config.py）
├── ui/
│   ├── __init__.py
│   ├── main_window.py          # 主窗口 + 左侧导航
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── preprocess_page.py   # 数据预处理 Tab
│   │   ├── train_page.py       # 训练 Tab
│   │   ├── generate_page.py     # 图片生成 Tab
│   │   └── system_page.py       # 系统信息 Tab
│   └── widgets/
│       ├── __init__.py
│       ├── loss_chart.py        # Loss 曲线实时图表
│       ├── image_gallery.py     # 图片预览 Gallery
│       └── log_viewer.py        # 日志输出面板
├── core/                       # 核心逻辑（复用现有代码）
│   ├── train_engine.py          # [link to photo_art_framework]
│   ├── preprocess.py             # [link to photo_art_framework]
│   ├── generate.py               # [原生实现，不依赖 Gradio]
│   └── presets.py               # [link to photo_art_framework]
└── resources/
    ├── __init__.py
    └── resources.qrc            # Qt 资源文件（图标等）
```

## 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| Python | CPython | 3.10+ |
| 桌面框架 | PySide6 | >= 6.5 |
| UI 组件库 | qfluentwidgets | >= 1.3.2 |
| 打包工具 | Nuitka | <= 1.8.6 |
| 图表 | PyQtGraph / matplotlib | - |
| 训练引擎 | 复用现有 subprocess | - |
| 图片生成 | diffusers + PyTorch | 原生实现 |

## 主窗口布局

```
┌──────────────────────────────────────────────────────────────┐
│  [AppIcon]  PhotoArt Desktop                    [—] [□] [×]│
├──────────────┬───────────────────────────────────────────────┤
│              │                                               │
│  🖼️ 预处理   │                                               │
│              │         [当前页面内容]                            │
│  🚀 训练     │                                               │
│              │                                               │
│  🎨 生成     │                                               │
│              │                                               │
│  ℹ️ 关于     │                                               │
│              │                                               │
└──────────────┴───────────────────────────────────────────────┘
```

- 左侧：垂直导航菜单（NavigationInterface）
- 右侧：页面内容区域（StackedWidget）
- 使用 qfluentwidgets 的 FluentWindow 提供原生窗口装饰

## UI 页面设计

### 1. 预处理页面 (PreprocessPage)

布局：垂直布局

```
┌─────────────────────────────────────────────────────────┐
│  📁 输入目录: [________________________] [浏览]          │
│                                                         │
│  📊 统计: 找到 0 张图片                                  │
│                                                         │
│  🖼️ 预览: [img1] [img2] [img3] [img4] ...              │
│                                                         │
│  📁 输出目录: [________________________] [浏览]          │
│  📐 目标分辨率: [768 ▼]  ☐ 保持原图比例                    │
│  🔁 重复次数: [10──●────] 20                             │
│  🏷️ 触发词: [________________]                           │
│  🔢 工作线程: [4───●────] 8                              │
│                                                         │
│  [🚀 开始预处理                              ]            │
│                                                         │
│  📋 日志:                                                │
│  ┌───────────────────────────────────────────────────┐   │
│  │ 2026-05-01 00:30:00 扫描目录...                    │   │
│  │ 2026-05-01 00:30:01 找到 128 张图片                 │   │
│  └───────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 2. 训练页面 (TrainPage)

采用紧凑的单栏布局，充分利用水平空间：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🤖 基础模型: [SDXL Model ▼]                            📋 预设: [▼]   │
│  ☐ 启用续训练  [LoRA Model ▼] [🔄]               ℹ️ 预设信息:           │
│                                                                             │
│  🏷️ 触发词: [photo_style]    📁 数据: [_________] [浏览]   🖼️ 128 张   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  📐 分辨率              📊 LoRA Dim        📐 步数           📦 Batch    │
│  宽[512▼] 高[768▼]   [32──●──]64    [3000───●──]    [1──●──]4   │
│                                         10000                               │
│  📖 学习率: [1e-4_______________________________]                         │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  📉 Loss 曲线 (实时)                              📋 训练日志               │
│  ┌──────────────────────────────┐  ┌──────────────────────────────────┐  │
│  │                              │  │ step: 450/3000 45%               │  │
│  │      📈 实时更新图表          │  │ loss: 0.0234  eta: 15:32        │  │
│  │                              │  │ gpu: 8.2GB / 12GB                │  │
│  │                              │  │                                  │  │
│  └──────────────────────────────┘  └──────────────────────────────────┘  │
│                                                                             │
│  训练进度: 45% ████████████████░░░░░░░  [🚀 开始训练]  [⏹️ 停止训练]  │
└─────────────────────────────────────────────────────────────────────────────┘
```

**布局说明：**
- 第一行：基础模型（下拉）+ 预设选择 + 续训练选项
- 第二行：触发词 + 数据目录 + 图片计数
- 第三行：分辨率 / LoRA Dim / 步数 / Batch 并排
- 第四行：学习率（独占一行）
- 第五行：Loss 图表（左 60%）+ 日志面板（右 40%），等高
- 第六行：进度条 + 开始/停止按钮

**控件尺寸：**
- Loss 图表高度：300px
- 日志面板高度：300px
- 所有控件使用 `setMinimumWidth()` 避免挤压

### 3. 生成页面 (GeneratePage)

```
┌─────────────────────────────────────────────────────────────┐
│  🤖 基础模型: [SDXL Model ▼]                               │
│                                                             │
│  📁 LoRA 路径: [____________________] [浏览] [🔍 扫描]      │
│  📋 LoRA 文件: [latest_lora.safetensors ▼]                 │
│  🎚️ LoRA 权重: [1.0──●──] 2.0                            │
│                                                             │
│  📝 提示词:                                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 1girl, portrait, fashion photo, elegant dress...    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  🚫 负面提示词:                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ugly, deformed, blurry, low quality, cartoon...      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  📐 分辨率: 宽度 [512 ▼]  高度 [768 ▼]                     │
│  🔢 步数: [30──●──] 50    CFG: [7.5──●──] 15             │
│  🎲 Seed: [-1________] ( -1 = 随机 )                       │
│                                                             │
│                        [🎨 生成图片]                        │
│                                                             │
│  🖼️ 生成结果:                          📋 状态:            │
│  ┌────────────────────────┐         生成成功！            │
│  │                        │         保存: output/xxx.png   │
│  │    [Generated Image]   │         Seed: 1234567890     │
│  │                        │                               │
│  └────────────────────────┘                               │
└─────────────────────────────────────────────────────────────┘
```

### 4. 关于页面 (SystemPage)

- Python / PyTorch / CUDA 版本
- GPU 信息（显存、温度）
- 目录路径配置
- 框架版本信息

## 核心逻辑复用策略

### 复用（不做修改）

| 模块 | 来源 | 复用方式 |
|------|------|----------|
| `config.py` | photo_art_framework | 直接 copy |
| `presets.py` | photo_art_framework | 直接 copy |
| `preprocess.py` | photo_art_framework | 直接 copy |
| `train_engine.py` | photo_art_framework | 直接 copy |

### 原生实现

| 模块 | 实现方式 |
|------|----------|
| `generate.py` | 从 `generate.py` 提取核心逻辑，去除 Gradio 依赖，适配 PySide6 Signal/Slot |
| Loss 曲线 | PyQtGraph `PlotWidget` 实时更新 |
| 图片预览 | `QLabel` + `QPixmap` 或 `qfluentwidgets Gallery` |
| 日志面板 | `QTextEdit` (read-only) + Signal 注入日志 |

### 训练流程（不变）

训练仍通过子进程调用 `sd-scripts/venv/Scripts/python.exe` + `sdxl_train_network.py`，通过 `train_engine.py` 的已有逻辑。UI 通过 `QThread` + `Signal` 实时获取进度。

## PySide6 Signal 设计

```python
# train_worker.py
class TrainWorker(QThread):
    progress = Signal(int, int, float)  # step, total, loss
    log_line = Signal(str)
    finished = Signal(int)  # return_code
    error = Signal(str)

# generate_worker.py
class GenerateWorker(QThread):
    progress = Signal(float, str)  # 0.0-1.0, status
    finished = Signal(str)  # image_path
    error = Signal(str)
```

## 打包配置 (Nuitka)

```ini
# build.spec
[Python]
杭州| ...
杭州| Nuitka
杭州| OneFile
杭州| WindowsConsoleIntervention
杭州| DisableBytecode
杭州| RemoveDebugIntrospection

[Metadata]
杭州| Name = PhotoArt Desktop
杭州| Version = 1.0.0

[Include]
杭州| Files = photo_art_desktop/config.py
杭州| Files = photo_art_desktop/core/
杭州| Files = ../photo_art_framework/core/  # 复用现有核心逻辑
杭州| Files = ../sd-scripts/venv/Scripts/python.exe
```

## 依赖

```
PySide6 >= 6.5.0
qfluentwidgets >= 1.3.2
PyQtGraph >= 0.13.0
Pillow >= 10.0.0
torch >= 2.0.0
diffusers >= 0.20.0
transformers >= 4.30.0
accelerate >= 0.25.0
numpy >= 1.24.0
```

## 实施计划

1. **项目脚手架** — 目录结构、依赖文件、Qt 资源
2. **主窗口框架** — FluentWindow + 导航 + 页面容器
3. **预处理页面** — 复用 preprocess.py
4. **训练页面** — 复用 train_engine.py + Loss 曲线原生
5. **生成页面** — 原生实现 generate.py 核心逻辑
6. **关于页面** — 系统信息展示
7. **打包测试** — Nuitka 打包验证
8. **功能测试** — 全流程验证

## 注意事项

- 图片生成不走子进程，直接在主进程加载 diffusers PipeLine
- 训练子进程的 stdout 捕获通过 `QThread` + `iter_lines()` 实现（复用 train_engine.py）
- Loss 曲线每 10 步更新一次，避免过于频繁的 UI 刷新
- 生成的图片保存到 `photo_art_desktop/output/generated/`

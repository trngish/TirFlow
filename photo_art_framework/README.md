# 写真/艺术照训练框架 (PhotoArt Framework)

## 框架概述

一体化写真/艺术照训练解决方案：
- **数据预处理**: 批量图片处理（裁剪+缩放+生成标签）
- **LoRA训练**: SDXL LoRA模型训练 + Loss曲线监控
- **图片生成**: 基于LoRA的写真图片生成

## 目录结构

```
photo_art_framework/
├── config.py          # 配置与路径
├── train_engine.py     # 训练引擎
├── preprocess.py       # 数据预处理
├── generate.py        # 图片生成
├── ui.py              # Gradio界面
├── main.py            # 入口点
└── 启动框架.bat
```

## 快速开始

```bash
# 方式1: 使用启动脚本
双击 启动框架.bat

# 方式2: 命令行
python main.py
```

访问 http://127.0.0.1:7860

## 功能Tab

| Tab | 功能 |
|-----|------|
| 🖼️ 数据预处理 | 批量图片处理 |
| 🚀 训练 | LoRA训练 + Loss曲线 |
| 🎨 图片生成 | SDXL + LoRA生成 |
| ℹ️ 系统信息 | 环境配置 |

## 训练参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| Network Dim | 32 | LoRA维度 |
| 训练步数 | 3000 | 最大步数 |
| Batch Size | 1 | 批大小 |
| 学习率 | 1e-4 | 学习率 |
| 分辨率 | 512x768 | 竖版写真比例 |

## 系统要求

- Python 3.10+
- PyTorch 2.0+
- CUDA 11.8+
- 显存: 12GB+ (RTX 3060)

# PhotoArt Desktop

Desktop application for photo/art portrait LoRA training, built with PySide6.

## Features

- **Data Preprocessing** — Batch image processing with center crop, resize, and caption generation
- **LoRA Training** — SDXL LoRA model training with real-time loss monitoring
- **Image Generation** — Native diffusers implementation (no Gradio dependency)

## Requirements

- Python 3.10+
- Windows 10/11
- NVIDIA GPU with 12GB+ VRAM (RTX 3060 recommended)
- CUDA 11.8+

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Project Structure

```
photo_art_desktop/
├── main.py                    # Entry point
├── config.py                  # Configuration
├── train_engine.py            # Training engine (reuses photo_art_framework core)
├── preprocess.py              # Preprocessing (reuses photo_art_framework core)
├── generate.py               # Native image generation
├── ui/
│   ├── main_window.py        # FluentWindow + navigation
│   ├── pages/
│   │   ├── preprocess_page.py # Preprocessing UI
│   │   ├── train_page.py     # Training UI
│   │   ├── generate_page.py  # Generation UI
│   │   └── system_page.py    # About/System info
│   └── widgets/
│       ├── loss_chart.py     # PyQtGraph loss curve
│       └── log_viewer.py     # Log display widget
```

## Tech Stack

- **PySide6** — Qt-based desktop framework
- **qfluentwidgets** — Fluent Design UI components
- **PyQtGraph** — Real-time chart rendering
- **diffusers** — Stable Diffusion pipeline

## Note

This desktop app reuses the core training and preprocessing logic from `photo_art_framework/`. The image generation is implemented natively using diffusers without Gradio.

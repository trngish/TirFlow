# PhotoArt Framework

An integrated photo/art portrait LoRA training solution built on [kohya-ss/sd-scripts](https://github.com/kohya-ss/sd-scripts).

## Features

| Module | Description |
|--------|-------------|
| **Data Preprocessing** | Batch image processing: center crop, resize, caption generation |
| **LoRA Training** | SDXL LoRA model training with real-time loss monitoring |
| **Image Generation** | SDXL + LoRA based portrait generation via Gradio UI |

## Project Structure

```
photo_art_framework/
├── config.py           # Configuration and path definitions
├── train_engine.py      # Training engine (subprocess wrapper)
├── preprocess.py        # Image preprocessing (crop, resize, caption)
├── generate.py          # SDXL image generation with LoRA
├── ui.py               # Gradio web interface
├── main.py             # Entry point
├── presets.py          # Training presets
├── logging_config.py    # Logging setup
├── presets/            # Training preset definitions (.toml)
└── output/             # Trained models, logs, sample images
```

## Quick Start

```bash
# Option 1: Use the launch script
.\启动框架.bat

# Option 2: Command line
python main.py
```

Then open http://127.0.0.1:7860 in your browser.

## Workflow

1. **Preprocess** → Select raw photos → Auto crop/resize + generate captions
2. **Train** → Choose base model, set LoRA params → Start training
3. **Generate** → Select trained LoRA → Generate portraits with custom prompts

## Default Training Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Network Dim | 32 | LoRA rank dimension |
| Steps | 3000 | Max training steps |
| Batch Size | 1 | Training batch size |
| Learning Rate | 1e-4 | AdamW8bit learning rate |
| Resolution | 512x768 | Portrait aspect ratio (vertical) |

## Presets

Located in `presets/` directory:

- `portrait_photo.toml` — Portrait photography
- `character_fullbody.toml` — Full body character
- `character_portrait.toml` — Character portrait
- `style_realistic.toml` — Realistic style
- `style_anime.toml` — Anime style
- `high_quality.toml` — High quality (longer training)
- `fast_training.toml` — Quick training
- `expression.toml` — Facial expressions
- `object_clothing.toml` — Clothing items
- `object_product.toml` — Product photography

## Requirements

- Python 3.10+
- PyTorch 2.0+
- CUDA 11.8+ (12GB+ VRAM recommended, RTX 3060)
- Windows/Linux

## Dependencies

The framework uses `sd-scripts/venv/` for training dependencies:
- `sd-scripts/venv/Scripts/python.exe` — Training subprocess

Generation uses the system Python with:
- `diffusers`
- `transformers`
- `accelerate`
- `torch`

## Configuration

Edit `config.py` to customize paths:

```python
WORKSPACE = r"D:\TirFlow\photo_art_framework"
MODEL_DIR = r"D:\TirFlow\models"          # Base models
OUTPUT_DIR = r"...\output"                 # Trained LoRA output
TRAIN_DATA_DIR = r"D:\TirFlow\train_data_photoart"  # Training images
SCRIPTS_DIR = r"D:\TirFlow\sd-scripts"     # kohya-ss scripts
```

## License

This project bundles [kohya-ss/sd-scripts](https://github.com/kohya-ss/sd-scripts) which is licensed under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0).

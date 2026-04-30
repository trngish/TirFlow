"""
Training engine module - LoRA model training logic
Adapted from photo_art_framework for PySide6 desktop
"""
import os
import re
import subprocess
import sys
import locale
from typing import Tuple, List, Optional

import config

# Global training state
training_process: Optional[subprocess.Popen] = None
training_state = {"running": False, "progress": 0, "step": 0}
loss_history: List[Tuple[int, float]] = []


def get_training_state() -> dict:
    """Get current training state"""
    return training_state


def get_loss_history() -> List[Tuple[int, float]]:
    """Get loss history"""
    return loss_history


def clear_loss_history():
    """Clear loss history"""
    global loss_history
    loss_history = []


def count_images(dir_path: str) -> int:
    """Count images in directory"""
    if not dir_path or not os.path.isdir(dir_path):
        return 0
    count = 0
    for root, dirs, files in os.walk(dir_path):
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                count += 1
    return count


def get_available_models() -> List[str]:
    """Get available base models"""
    models = []
    if os.path.exists(config.MODEL_DIR):
        for f in os.listdir(config.MODEL_DIR):
            if f.endswith(('.safetensors', '.ckpt', '.pth')):
                models.append(os.path.join(config.MODEL_DIR, f))
    return models if models else ["Please download a base model first"]


def get_existing_loras() -> List[str]:
    """Get list of trained LoRA models"""
    loras = []
    if os.path.exists(config.OUTPUT_DIR):
        for f in os.listdir(config.OUTPUT_DIR):
            if f.endswith('.safetensors') and not f.endswith('-state'):
                loras.append(os.path.join(config.OUTPUT_DIR, f))
    return loras if loras else ["No trained LoRA found"]


def start_training(
    base_model: str,
    trigger_word: str,
    train_data_dir: str,
    output_name: str,
    output_dir: str,
    network_dim: int,
    steps: int,
    resolution_w: int,
    resolution_h: int,
    batch_size: int,
    learning_rate: float,
    resume_training: bool,
    resume_lora_path: str,
    log_callback=None,
    progress_callback=None
) -> Tuple[int, str]:
    """
    Start training task

    Returns:
        Tuple[exit_code, status_message]
    """
    global training_process, training_state, loss_history

    if training_state["running"]:
        return -1, "Training already running"

    if not base_model or "Please download" in base_model:
        return -1, "Please select a base model"

    img_count = count_images(train_data_dir)
    if img_count == 0:
        return -1, "Training data is empty"

    clear_loss_history()

    cmd = [
        config.VENV_PYTHON, config.SDXL_TRAIN_SCRIPT,
        "--pretrained_model_name_or_path", base_model,
        "--train_data_dir", train_data_dir,
        "--output_dir", output_dir,
        "--output_name", output_name,
        "--save_model_as", "safetensors",
        "--network_module", "networks.lora",
        "--network_dim", str(network_dim),
        "--network_alpha", str(network_dim // 2),
        "--resolution", f"{resolution_w},{resolution_h}",
        "--train_batch_size", str(batch_size),
        "--gradient_accumulation_steps", "4",
        "--learning_rate", str(learning_rate),
        "--unet_lr", str(learning_rate),
        "--text_encoder_lr", str(learning_rate),
        "--lr_scheduler", "cosine",
        "--lr_warmup_steps", "200",
        "--max_train_steps", str(steps),
        "--optimizer_type", "AdamW8bit",
        "--seed", "42",
        "--mixed_precision", "bf16",
        "--save_precision", "bf16",
        "--xformers",
        "--gradient_checkpointing",
        "--no_half_vae",
        "--max_data_loader_n_workers", "0",
        "--network_train_unet_only",
        "--max_token_length", "150",
        "--enable_bucket",
        "--min_bucket_reso", "256",
        "--max_bucket_reso", "1024",
        "--logging_dir", os.path.join(config.OUTPUT_DIR, "logs"),
        "--log_prefix", output_name,
        "--save_every_n_steps", str(max(100, steps // 10)),
        "--save_state",
        "--sample_every_n_steps", str(max(100, steps // 10)),
    ]

    if resume_training and resume_lora_path and os.path.exists(resume_lora_path):
        cmd.extend(["--network_weights", resume_lora_path, "--dim_from_weights"])

    trigger_file = os.path.join(config.OUTPUT_DIR, "trigger.txt")
    with open(trigger_file, "w", encoding="utf-8") as f:
        f.write(f"{trigger_word}, masterpiece, best quality, highres, detailed, photorealistic\n")
        f.write(f"{trigger_word}, masterpiece, best quality, highres, detailed, photorealistic\n")
    cmd.extend(["--sample_prompts", trigger_file, "--sample_sampler", "euler_a"])

    if learning_rate > 0:
        cmd.extend(["--noise_offset", "0.05"])

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"
    env["HF_ENDPOINT"] = "https://hf-mirror.com"

    # Force UTF-8 mode for subprocess on Windows
    if sys.platform == "win32":
        env["PYTHONLEGACYWINDOWSSTDIO"] = "utf-8"

    try:
        training_state["running"] = True
        training_state["progress"] = 0
        training_state["step"] = 0

        if log_callback:
            log_callback("=" * 50)
            log_callback(f"Starting training: {output_name}")
            log_callback(f"Base model: {base_model}")
            log_callback(f"Steps: {steps}")
            log_callback("=" * 50)

        # Hide console window on Windows
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

        training_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            cwd=config.SCRIPTS_DIR,
            bufsize=1,
            startupinfo=startupinfo
        )

        logs = []
        current_loss = 0.0

        for line in iter(training_process.stdout.readline, ""):
            if not line:
                break
            line = line.strip()
            if line:
                logs.append(line)
                if log_callback:
                    log_callback(line)
                current_loss = _parse_training_line(line, current_loss)
                if progress_callback:
                    progress_callback(training_state["progress"], training_state["step"], current_loss)

        training_process.wait()
        training_state["running"] = False

        if training_process.returncode == 0:
            return 0, "Training complete!"
        else:
            return training_process.returncode, f"Training failed (exit code: {training_process.returncode})"

    except Exception as e:
        training_state["running"] = False
        return -1, f"Failed to start: {str(e)}"


def _parse_training_line(line: str, current_loss: float) -> float:
    """Parse training output line, returns current_loss"""
    global training_state, loss_history

    if "steps:" in line and "%" in line:
        # Format: 'steps:   0%|          | 1/500 [00:08<1:11:10,  8.56s/it, avr_loss=0.142]'
        m = re.search(r'(\d+)%', line)
        if m:
            training_state["progress"] = int(m.group(1))
        sm = re.search(r'\|\s*(\d+)/(\d+)\s*\[', line)
        if sm:
            training_state["step"] = int(sm.group(1))

    for pattern in [r'avr_loss=([0-9.]+)', r'loss[:\s=]*([0-9.]+)', r'"loss"\s*:\s*([0-9.]+)']:
        loss_m = re.search(pattern, line, re.IGNORECASE)
        if loss_m:
            try:
                current_loss = float(loss_m.group(1))
                step = training_state["step"]
                if step > 0:
                    loss_history.append((step, current_loss))
                    if len(loss_history) > 500:
                        loss_history.pop(0)
                break
            except ValueError:
                pass

    return current_loss


def stop_training() -> Tuple[int, str]:
    """Stop training"""
    global training_process, training_state

    if training_process:
        training_process.terminate()
        training_process = None

    training_state["running"] = False
    return training_state["progress"], "Training stopped"

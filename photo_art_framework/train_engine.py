"""
训练引擎模块 - LoRA模型训练逻辑
"""
import os
import re
import subprocess
import queue
import locale
from typing import Tuple, List

import pandas as pd

from config import (
    OUTPUT_DIR, VENV_PYTHON, SDXL_TRAIN_SCRIPT, SCRIPTS_DIR,
    DEFAULT_NETWORK_DIM, DEFAULT_RESOLUTION_W, DEFAULT_RESOLUTION_H, LOG_DIR
)

# 全局训练状态
training_process = None
training_state = {"running": False, "progress": 0, "step": 0}
loss_history: List[Tuple[int, float]] = []
# 日志队列，用于流式日志输出
train_logs_queue: queue.Queue = queue.Queue()
training_status_info = {"running": False, "status": "", "logs": ""}

# 训练日志器 - 写入专用训练日志文件
import logging as _train_logging
_train_log_file = None
_train_log_handler = None


def _setup_training_logger(name: str):
    """设置训练专用日志文件"""
    global _train_log_file, _train_log_handler
    os.makedirs(LOG_DIR, exist_ok=True)
    _train_log_file = os.path.join(LOG_DIR, f"training_{name}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.log")
    _train_log_handler = _train_logging.FileHandler(_train_log_file, encoding='utf-8')
    _train_log_handler.setLevel(_train_logging.INFO)
    _train_log_handler.setFormatter(_train_logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    _train_logging.getLogger().addHandler(_train_log_handler)
    return _train_log_file


def _close_training_logger():
    """关闭训练日志"""
    global _train_log_handler
    if _train_log_handler:
        _train_logging.getLogger().removeHandler(_train_log_handler)
        _train_log_handler.close()
        _train_log_handler = None


def get_training_state() -> dict:
    """获取当前训练状态"""
    return training_state


def get_loss_history() -> List[Tuple[int, float]]:
    """获取Loss历史"""
    return loss_history


def clear_loss_history():
    """清空Loss历史"""
    global loss_history
    loss_history = []


def get_loss_chart_data() -> pd.DataFrame:
    """获取Loss图表数据"""
    global loss_history
    if not loss_history:
        return pd.DataFrame({'Step': [0], 'Loss': [0]})
    return pd.DataFrame(loss_history, columns=['Step', 'Loss'])


def clear_train_logs_queue():
    """清空日志队列"""
    global train_logs_queue, training_status_info
    while not train_logs_queue.empty():
        try:
            train_logs_queue.get_nowait()
        except queue.Empty:
            break
    training_status_info = {"running": False, "status": "", "logs": ""}


def get_training_status() -> Tuple[int, str]:
    """获取训练状态和日志（供定时器轮询）"""
    global training_status_info, train_logs_queue

    # 从队列中取出所有日志
    logs_list = []
    while True:
        try:
            log_line = train_logs_queue.get_nowait()
            logs_list.append(log_line)
        except queue.Empty:
            break

    # 更新状态日志
    if logs_list:
        training_status_info["logs"] += "\n".join(logs_list)
        # 只保留最新500行
        lines = training_status_info["logs"].split("\n")
        if len(lines) > 500:
            training_status_info["logs"] = "\n".join(lines[-500:])

    return training_state["progress"], training_status_info["logs"]


def count_images(dir_path: str) -> int:
    """统计目录中的图片数量"""
    if not dir_path or not os.path.isdir(dir_path):
        return 0
    count = 0
    for root, dirs, files in os.walk(dir_path):
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                count += 1
    return count


def get_available_models() -> List[str]:
    """获取可用的基础模型"""
    from config import MODEL_DIR
    models = []
    if os.path.exists(MODEL_DIR):
        for f in os.listdir(MODEL_DIR):
            if f.endswith(('.safetensors', '.ckpt', '.pth')):
                models.append(os.path.join(MODEL_DIR, f))
    return models if models else ["请先下载写实基础模型"]


def get_existing_loras() -> List[str]:
    """获取已训练的LoRA模型列表"""
    loras = []
    if os.path.exists(OUTPUT_DIR):
        for f in os.listdir(OUTPUT_DIR):
            if f.endswith('.safetensors'):
                loras.append(os.path.join(OUTPUT_DIR, f))
    return loras if loras else ["无已训练LoRA"]


def start_training(
    base_model: str,
    trigger_word: str,
    train_data_dir: str,
    output_name: str,
    network_dim: int,
    steps: int,
    resolution_w: int,
    resolution_h: int,
    batch_size: int,
    learning_rate: float,
    resume_training: bool,
    resume_lora_path: str,
    progress_callback=None
) -> Tuple[int, str, str]:
    """
    启动训练任务

    Returns:
        Tuple[progress, status_message, logs]
    """
    global training_process, training_state, loss_history

    # 检查状态
    if training_state["running"]:
        return 0, "训练已在运行", ""

    if not base_model or "请先下载" in base_model:
        return 0, "请选择基础模型", ""

    img_count = count_images(train_data_dir)
    if img_count == 0:
        return 0, "训练数据为空", ""

    # 清空历史Loss
    loss_history = []

    # 构建训练命令
    cmd = [
        VENV_PYTHON, SDXL_TRAIN_SCRIPT,
        "--pretrained_model_name_or_path", base_model,
        "--train_data_dir", train_data_dir,
        "--output_dir", OUTPUT_DIR,
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
        "--logging_dir", os.path.join(OUTPUT_DIR, "logs"),
        "--log_prefix", output_name,
        "--save_every_n_steps", str(max(100, steps // 10)),
        "--save_state",
        "--sample_every_n_steps", str(max(100, steps // 10)),
    ]

    # 继续训练模式
    if resume_training and resume_lora_path and os.path.exists(resume_lora_path):
        cmd.extend(["--network_weights", resume_lora_path, "--dim_from_weights"])

    # 生成触发词文件
    trigger_file = os.path.join(OUTPUT_DIR, "trigger.txt")
    with open(trigger_file, "w", encoding="utf-8") as f:
        f.write(f"{trigger_word}, masterpiece, best quality, highres, detailed, photorealistic\n")
        f.write(f"{trigger_word}, masterpiece, best quality, highres, detailed, photorealistic\n")
    cmd.extend(["--sample_prompts", trigger_file, "--sample_sampler", "euler_a"])

    if learning_rate > 0:
        cmd.extend(["--noise_offset", "0.05"])

    # 环境变量
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["HF_ENDPOINT"] = "https://hf-mirror.com"

    try:
        training_state["running"] = True
        training_state["progress"] = 0
        training_state["step"] = 0
        training_status_info["running"] = True
        training_status_info["status"] = "训练启动中..."

        # 设置训练日志文件（优先初始化，确保初始信息也写入）
        _setup_training_logger(output_name)

        train_logs_queue.put("=" * 40)
        train_logs_queue.put(f"开始训练: {output_name}")
        train_logs_queue.put(f"基础模型: {base_model}")
        train_logs_queue.put(f"训练步数: {steps}")
        train_logs_queue.put("=" * 40)
        _train_logging.info("=" * 40)
        _train_logging.info(f"开始训练: {output_name}")
        _train_logging.info(f"基础模型: {base_model}")
        _train_logging.info(f"训练步数: {steps}")
        _train_logging.info("=" * 40)

        training_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding=locale.getpreferredencoding(False),
            errors="replace",
            env=env,
            cwd=SCRIPTS_DIR,
            bufsize=1
        )

        logs = []
        current_loss = 0.0

        for line in iter(training_process.stdout.readline, ""):
            if not line:
                break
            line = line.strip()
            if line:
                logs.append(line)
                train_logs_queue.put(line)  # 流式日志
                _train_logging.info(line)  # 写入训练日志文件
                _parse_training_line(line)

                if progress_callback:
                    progress_callback(training_state["progress"], training_state["step"], current_loss)

        training_process.wait()
        training_state["running"] = False

        # 关闭训练日志
        _close_training_logger()

        # 训练结束，更新状态
        training_status_info["running"] = False
        if training_process.returncode == 0:
            training_status_info["status"] = "训练完成！"
            return 100, "训练完成！", "\n".join(logs[-100:])
        else:
            training_status_info["status"] = f"训练失败（退出码: {training_process.returncode})"
            return training_state["progress"], f"训练失败（退出码: {training_process.returncode})", "\n".join(logs[-100:])

    except Exception as e:
        training_state["running"] = False
        training_status_info["running"] = False
        _close_training_logger()
        training_status_info["status"] = f"启动失败: {str(e)}"
        return 0, f"启动失败: {str(e)}", ""


def _parse_training_line(line: str):
    """解析训练输出行"""
    global training_state, loss_history

    # 解析进度
    if "steps:" in line and "%" in line:
        m = re.search(r'(\d+)%', line)
        if m:
            training_state["progress"] = int(m.group(1))
        sm = re.search(r'steps:\s*(\d+)/(\d+)', line)
        if sm:
            training_state["step"] = int(sm.group(1))

    # 解析Loss值（每10步记录一次）
    for pattern in [r'loss[:\s=]*([0-9.]+)', r'"loss"\s*:\s*([0-9.]+)', r'loss\s*([0-9.]+)']:
        loss_m = re.search(pattern, line, re.IGNORECASE)
        if loss_m:
            try:
                current_loss = float(loss_m.group(1))
                step = training_state["step"]
                if step > 0 and step % 10 == 0:
                    loss_history.append((step, current_loss))
                    if len(loss_history) > 500:
                        loss_history.pop(0)
                break
            except ValueError:
                pass


def stop_training() -> Tuple[int, str]:
    """停止训练"""
    global training_process, training_state

    if training_process:
        training_process.terminate()
        training_process = None

    training_state["running"] = False
    return training_state["progress"], "训练已停止"

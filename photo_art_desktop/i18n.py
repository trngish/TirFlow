"""
Internationalization module - Language strings
"""
from typing import Dict
from PySide6.QtCore import QObject, Signal

LANGUAGES = {
    "en": "English",
    "zh": "中文"
}

# Current language
_current_lang = "en"


class LanguageManager(QObject):
    """Language manager with signal for language changes"""
    language_changed = Signal()

_language_manager = LanguageManager()


def set_language(lang: str):
    global _current_lang
    _current_lang = lang
    _language_manager.language_changed.emit()


def get_language() -> str:
    return _current_lang


def T(key: str) -> str:
    """Get translated string"""
    return _strings.get(_current_lang, {}).get(key, key)


def get_language_manager() -> LanguageManager:
    return _language_manager


# English strings
en_strings: Dict[str, str] = {
    # Preprocess page
    "preprocess": "Preprocess",
    "input_dir": "Input Directory",
    "input_dir_placeholder": "Select raw images directory...",
    "browse": "Browse",
    "found_images": "Found {count} images",
    "no_images": "No images found",
    "invalid_dir": "Invalid directory",
    "output_dir": "Output Directory",
    "target_resolution": "Target Resolution",
    "keep_aspect": "Keep original aspect ratio",
    "repeat_count": "Repeat Count",
    "trigger_word": "Trigger Word",
    "workers": "Workers",
    "start_preprocessing": "Start Preprocessing",
    "preprocessing_complete": "Preprocessing complete!",
    "log": "Log",

    # Train page
    "train": "Training",
    "base_model": "Base Model",
    "base_model_placeholder": "Select base model (.safetensors, .ckpt, .pth)...",
    "preset": "Preset",
    "enable_resume": "Enable Resume Training",
    "resume_model": "Resume Model",
    "resume_model_placeholder": "Select LoRA to resume from (.safetensors)...",
    "preset_info": "Preset Info",
    "trigger": "Trigger Word",
    "output_name": "Output Name",
    "data_dir": "Data Directory",
    "images_count": "{count} images",
    "resolution": "Resolution",
    "lora_dim": "LoRA Dim",
    "steps": "Steps",
    "batch": "Batch",
    "learning_rate": "Learning Rate",
    "loss_curve": "Loss Curve (Real-time)",
    "training_log": "Training Log",
    "progress": "Progress:",
    "start_training": "Start Training",
    "stop_training": "Stop Training",
    "training_complete": "Training complete!",
    "training_failed": "Training failed",
    "training_stopped": "Training stopped",
    "stopping": "Stopping training...",

    # Generate page
    "generate": "Generate",
    "model": "Model",
    "lora_path": "LoRA Path",
    "lora_dir_placeholder": "Select LoRA directory...",
    "scan": "Scan",
    "lora_file": "LoRA File",
    "lora_weight": "LoRA Weight",
    "prompt": "Prompt",
    "prompt_placeholder": "1girl, portrait, fashion photo, elegant dress, studio lighting",
    "neg_prompt": "Negative Prompt",
    "neg_prompt_placeholder": "ugly, deformed, blurry, low quality, cartoon, anime",
    "width": "Width",
    "height": "Height",
    "cfg": "CFG",
    "seed_random": "Seed (-1=random)",
    "generate_image": "Generate Image",
    "preview": "Preview",
    "status": "Status",
    "ready": "Ready",
    "no_safetensors": "No .safetensors files found",
    "generate_success": "Generated successfully!",
    "save_to": "Saved:",

    # Settings page
    "settings": "Settings",
    "language": "Language",
    "language_changed": "Language changed. Some text may not update until restart.",
    "about": "About",
    "version": "Version",
    "environment": "Environment",
    "python": "Python",
    "pytorch": "PyTorch",
    "cuda": "CUDA",
    "gpu": "GPU",
    "gpu_memory": "GPU Memory",
    "path_config": "Path Configuration",
    "workspace": "Workspace",
    "model_dir": "Model Directory",
    "output_dir": "Output Directory",
    "train_data_dir": "Training Data",
    "scripts_dir": "Scripts Directory",
    "generated_dir": "Generated Images",
    "logs_dir": "Logs",
    "built_with": "Built with",
    "tech_stack": "PySide6 + qfluentwidgets + diffusers + kohya-ss/sd-scripts",
    "app_desc": "PhotoArt Desktop is a standalone desktop application for training LoRA models for Stable Diffusion XL.",
    "photo_art_desktop": "PhotoArt Desktop",
}

# Chinese strings
zh_strings: Dict[str, str] = {
    # Preprocess page
    "preprocess": "预处理",
    "input_dir": "输入目录",
    "input_dir_placeholder": "选择原始图片目录...",
    "browse": "浏览",
    "found_images": "找到 {count} 张图片",
    "no_images": "未找到图片",
    "invalid_dir": "目录无效",
    "output_dir": "输出目录",
    "target_resolution": "目标分辨率",
    "keep_aspect": "保持原图比例",
    "repeat_count": "重复次数",
    "trigger_word": "触发词",
    "workers": "工作线程",
    "start_preprocessing": "开始预处理",
    "preprocessing_complete": "预处理完成！",
    "log": "日志",

    # Train page
    "train": "训练",
    "base_model": "基础模型",
    "base_model_placeholder": "选择基础模型 (.safetensors, .ckpt, .pth)...",
    "preset": "预设",
    "enable_resume": "启用续训练",
    "resume_model": "续训练模型",
    "resume_model_placeholder": "选择要续训练的 LoRA (.safetensors)...",
    "preset_info": "预设信息",
    "trigger": "触发词",
    "output_name": "输出名称",
    "data_dir": "数据目录",
    "images_count": "{count} 张图片",
    "resolution": "分辨率",
    "lora_dim": "LoRA Dim",
    "steps": "步数",
    "batch": "Batch",
    "learning_rate": "学习率",
    "loss_curve": "Loss 曲线（实时）",
    "training_log": "训练日志",
    "progress": "进度:",
    "start_training": "开始训练",
    "stop_training": "停止训练",
    "training_complete": "训练完成！",
    "training_failed": "训练失败",
    "training_stopped": "训练已停止",
    "stopping": "正在停止训练...",

    # Generate page
    "generate": "生成",
    "model": "模型",
    "lora_path": "LoRA 路径",
    "lora_dir_placeholder": "选择 LoRA 目录...",
    "scan": "扫描",
    "lora_file": "LoRA 文件",
    "lora_weight": "LoRA 权重",
    "prompt": "提示词",
    "prompt_placeholder": "1girl, portrait, fashion photo, elegant dress, studio lighting",
    "neg_prompt": "负面提示词",
    "neg_prompt_placeholder": "ugly, deformed, blurry, low quality, cartoon, anime",
    "width": "宽度",
    "height": "高度",
    "cfg": "CFG",
    "seed_random": "Seed (-1=随机)",
    "generate_image": "生成图片",
    "preview": "预览",
    "status": "状态",
    "ready": "就绪",
    "no_safetensors": "未找到 .safetensors 文件",
    "generate_success": "生成成功！",
    "save_to": "保存:",

    # Settings page
    "settings": "设置",
    "language": "语言",
    "language_changed": "语言已更改。部分文本可能需要重启才能更新。",
    "about": "关于",
    "version": "版本",
    "environment": "环境信息",
    "python": "Python",
    "pytorch": "PyTorch",
    "cuda": "CUDA",
    "gpu": "显卡",
    "gpu_memory": "显存",
    "path_config": "路径配置",
    "workspace": "工作目录",
    "model_dir": "模型目录",
    "output_dir": "输出目录",
    "train_data_dir": "训练数据",
    "scripts_dir": "脚本目录",
    "generated_dir": "生成图片",
    "logs_dir": "日志",
    "built_with": "技术栈",
    "tech_stack": "PySide6 + qfluentwidgets + diffusers + kohya-ss/sd-scripts",
    "app_desc": "PhotoArt Desktop 是一个独立的桌面应用程序，用于训练 Stable Diffusion XL 的 LoRA 模型。",
    "photo_art_desktop": "PhotoArt Desktop",
}

_strings = {
    "en": en_strings,
    "zh": zh_strings,
}

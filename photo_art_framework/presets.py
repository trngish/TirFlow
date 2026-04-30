"""
预设配置模块 - 加载和管理训练预设
"""
import os
import toml
from pathlib import Path
from typing import Dict, List, Optional

from config import WORKSPACE


def get_presets_dir() -> Path:
    """获取预设目录"""
    return Path(WORKSPACE) / "presets"


def list_presets() -> List[str]:
    """列出所有预设名称"""
    presets_dir = get_presets_dir()
    presets = []
    if presets_dir.exists():
        for f in presets_dir.glob("*.toml"):
            presets.append(f.stem)
    return sorted(presets)


def load_preset(name: str) -> Optional[Dict]:
    """加载指定预设配置"""
    preset_path = get_presets_dir() / f"{name}.toml"
    if not preset_path.exists():
        return None

    try:
        config = toml.load(preset_path)
        return config
    except Exception as e:
        print(f"加载预设失败 {name}: {e}")
        return None


def get_preset_params(name: str) -> Dict:
    """
    获取预设的训练参数
    返回适用于UI的参数字典
    """
    preset = load_preset(name)
    if not preset:
        return {}

    params = {}

    # 网络参数
    if "network" in preset:
        params["network_dim"] = preset["network"].get("network_dim", 32)
        params["network_alpha"] = preset["network"].get("network_alpha", 16)

    # 训练参数
    if "training" in preset:
        params["learning_rate"] = str(preset["training"].get("learning_rate", "1e-4"))
        params["max_train_steps"] = preset["training"].get("max_train_steps", 3000)
        params["batch_size"] = preset["training"].get("batch_size", 1)

    # 数据集参数
    if "datasets" in preset:
        res = preset["datasets"].get("resolution", "1024,1024")
        if isinstance(res, str):
            w, h = res.split(",")
            params["resolution_w"] = int(w.strip())
            params["resolution_h"] = int(h.strip())
        else:
            params["resolution_w"] = 1024
            params["resolution_h"] = 1024

    # 保存参数
    if "saving" in preset:
        params["output_name"] = preset["saving"].get("output_name", name)

    return params


def get_preset_trigger(name: str) -> str:
    """获取预设的触发词"""
    preset = load_preset(name)
    if not preset:
        return "photo_style"

    # 尝试从trigger_word或sample_prompts获取
    if "trigger" in preset:
        return preset["trigger"]

    if "sample" in preset:
        sample = preset["sample"].get("sample_prompts", "")
        if sample:
            # 提取第一个词作为触发词
            return sample.split(",")[0].strip()

    return "photo_style"


def get_preset_info(name: str) -> str:
    """获取预设描述信息"""
    preset = load_preset(name)
    if not preset:
        return ""

    info_parts = []

    # 通用信息
    if "general" in preset:
        info_parts.append("通用设置")

    # 网络信息
    if "network" in preset:
        net = preset["network"]
        info_parts.append(f"Dim: {net.get('network_dim', '?')}")

    # 训练信息
    if "training" in preset:
        train = preset["training"]
        info_parts.append(f"步数: {train.get('max_train_steps', '?')}")
        info_parts.append(f"学习率: {train.get('learning_rate', '?')}")

    return " | ".join(info_parts)

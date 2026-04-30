"""
Preset configuration module - Loading and managing training presets
Copied from photo_art_framework
"""
import os
import toml
from pathlib import Path
from typing import Dict, List, Optional

# Use presets from photo_art_framework/presets
PRESETS_SOURCE_DIR = r"D:\TirFlow\photo_art_framework\presets"


def get_presets_dir() -> Path:
    """Get presets directory"""
    return Path(PRESETS_SOURCE_DIR)


def list_presets() -> List[str]:
    """List all preset names"""
    presets_dir = get_presets_dir()
    presets = []
    if presets_dir.exists():
        for f in presets_dir.glob("*.toml"):
            presets.append(f.stem)
    return sorted(presets)


def load_preset(name: str) -> Optional[Dict]:
    """Load specified preset config"""
    preset_path = get_presets_dir() / f"{name}.toml"
    if not preset_path.exists():
        return None

    try:
        return toml.load(preset_path)
    except Exception as e:
        print(f"Failed to load preset {name}: {e}")
        return None


def get_preset_params(name: str) -> Dict:
    """Get preset training parameters"""
    preset = load_preset(name)
    if not preset:
        return {}

    params = {}

    if "network" in preset:
        params["network_dim"] = preset["network"].get("network_dim", 32)
        params["network_alpha"] = preset["network"].get("network_alpha", 16)

    if "training" in preset:
        params["learning_rate"] = str(preset["training"].get("learning_rate", "1e-4"))
        params["max_train_steps"] = preset["training"].get("max_train_steps", 3000)
        params["batch_size"] = preset["training"].get("batch_size", 1)

    if "datasets" in preset:
        res = preset["datasets"].get("resolution", "1024,1024")
        if isinstance(res, str):
            w, h = res.split(",")
            params["resolution_w"] = int(w.strip())
            params["resolution_h"] = int(h.strip())
        else:
            params["resolution_w"] = 1024
            params["resolution_h"] = 1024

    if "saving" in preset:
        params["output_name"] = preset["saving"].get("output_name", name)

    return params


def get_preset_trigger(name: str) -> str:
    """Get preset trigger word"""
    preset = load_preset(name)
    if not preset:
        return "photo_style"

    if "trigger" in preset:
        return preset["trigger"]

    if "sample" in preset:
        sample = preset["sample"].get("sample_prompts", "")
        if sample:
            return sample.split(",")[0].strip()

    return "photo_style"


def get_preset_info(name: str) -> str:
    """Get preset description"""
    preset = load_preset(name)
    if not preset:
        return ""

    info_parts = []

    if "network" in preset:
        net = preset["network"]
        info_parts.append(f"Dim: {net.get('network_dim', '?')}")

    if "training" in preset:
        train = preset["training"]
        info_parts.append(f"Steps: {train.get('max_train_steps', '?')}")
        info_parts.append(f"LR: {train.get('learning_rate', '?')}")

    return " | ".join(info_parts)

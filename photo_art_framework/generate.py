"""
图片生成模块 - 基于SDXL的写真图片生成
"""
import os
import time
from typing import Tuple

import torch

from config import OUTPUT_DIR, GENERATED_DIR

# 模型缓存
_cached_pipe = None
_cached_model = None
_cached_lora = None


def load_models(base_model: str):
    """加载SDXL模型（带缓存）"""
    global _cached_pipe, _cached_model, _cached_lora

    if _cached_pipe is None or base_model != _cached_model:
        from diffusers import StableDiffusionXLPipeline
        import gc
        gc.collect()
        torch.cuda.empty_cache()

        _cached_pipe = StableDiffusionXLPipeline.from_single_file(
            base_model,
            torch_dtype=torch.float16,
            variant="fp16"
        )
        _cached_pipe.to("cuda")
        _cached_pipe.enable_vae_tiling()
        _cached_pipe.enable_attention_slicing("auto")
        _cached_model = base_model
        _cached_lora = None

    return _cached_pipe


def apply_lora(pipe, lora_path: str, weight: float):
    """应用LoRA权重"""
    global _cached_lora

    if not lora_path or not os.path.isfile(lora_path):
        return

    try:
        try:
            pipe.unload_lora_weights()
        except:
            pass

        pipe.load_lora_weights(lora_path, weight_name="pytorch_lora_weights.bin")
        _cached_lora = lora_path
    except Exception as e:
        _cached_lora = None
        try:
            pipe.unload_lora_weights()
        except:
            pass
        raise e


def get_lora_models() -> list:
    """获取可用于生成的LoRA模型"""
    import glob
    loras = []
    if os.path.exists(OUTPUT_DIR):
        for f in glob.glob(os.path.join(OUTPUT_DIR, "*.safetensors")):
            loras.append(f)
    return loras if loras else ["暂无写真LoRA模型"]


def scan_lora_directory(dir_path: str) -> list:
    """扫描目录下所有.safetensors文件"""
    import glob
    loras = []
    if dir_path and os.path.isdir(dir_path):
        for f in glob.glob(os.path.join(dir_path, "*.safetensors")):
            loras.append(f)
        for f in glob.glob(os.path.join(dir_path, "*.ckpt")):
            loras.append(f)
    return sorted(loras)


def generate_photo(
    base_model: str,
    lora_path: str,
    lora_weight: float,
    prompt: str,
    negative_prompt: str,
    width: int,
    height: int,
    steps: int,
    cfg_scale: float,
    seed: int,
    lora_selected: str = None,
    progress_callback=None
) -> Tuple[str, str]:
    """
    生成写真图片

    Returns:
        Tuple[image_path, status_message]
    """
    # 检查基础模型
    if not base_model or "请先下载" in base_model:
        return "", "请先选择基础模型"

    # 处理LoRA路径：优先使用下拉框选择的文件
    effective_lora = None
    if lora_selected:
        effective_lora = lora_selected
    elif lora_path and os.path.isfile(lora_path):
        effective_lora = lora_path
    elif lora_path and os.path.isdir(lora_path):
        # 路径是目录，扫描第一个safetensors
        files = scan_lora_directory(lora_path)
        if files:
            effective_lora = files[0]

    if not effective_lora or "暂无" in str(effective_lora):
        effective_lora = None

    # 加载模型
    if progress_callback:
        progress_callback(0.1, "加载模型...")

    pipe = load_models(base_model)

    # 应用LoRA
    if effective_lora:
        if progress_callback:
            progress_callback(0.2, "加载LoRA...")
        apply_lora(pipe, effective_lora, lora_weight)

    if progress_callback:
        progress_callback(0.3, "生成图片...")

    # 增强提示词
    enhanced_prompt = f"{prompt}, photorealistic, realistic photography, high quality, 8k, detailed skin texture, natural lighting, professional photography"
    enhanced_neg = f"{negative_prompt}, cartoon, anime, illustration, painting, blurry, low quality, deformed"

    # 生成
    if seed == -1:
        seed = torch.randint(0, 2**32, (1,)).item()
    generator = torch.Generator("cuda").manual_seed(seed)

    result = pipe(
        prompt=enhanced_prompt,
        negative_prompt=enhanced_neg,
        num_inference_steps=steps,
        guidance_scale=cfg_scale,
        width=width,
        height=height,
        generator=generator,
        num_images_per_prompt=1
    )

    if progress_callback:
        progress_callback(0.9, "保存图片...")

    img = result.images[0]
    img_path = os.path.join(GENERATED_DIR, f"photo_{int(time.time())}.png")
    img.save(img_path)

    return img_path, f"生成成功！\n保存到: {img_path}\nSeed: {seed}"

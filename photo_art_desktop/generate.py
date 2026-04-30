"""
Image generation module - Native PySide6 implementation
Uses diffusers directly without Gradio dependency
"""
import os
import time
from typing import Tuple, Optional

import torch

import config

# Model cache
_cached_pipe = None
_cached_model = None
_cached_lora = None


def load_models(base_model: str):
    """Load SDXL model (with caching)"""
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
    """Apply LoRA weights"""
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
    """Get available LoRA models for generation"""
    import glob
    loras = []
    if os.path.exists(config.OUTPUT_DIR):
        for f in glob.glob(os.path.join(config.OUTPUT_DIR, "*.safetensors")):
            if "-state" not in f:
                loras.append(f)
    return loras if loras else []


def scan_lora_directory(dir_path: str) -> list:
    """Scan directory for all .safetensors files"""
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
    Generate portrait image

    Returns:
        Tuple[image_path, status_message]
    """
    if not base_model or "Please download" in str(base_model):
        return "", "Please select a base model"

    effective_lora = None
    if lora_selected:
        effective_lora = lora_selected
    elif lora_path and os.path.isfile(lora_path):
        effective_lora = lora_path
    elif lora_path and os.path.isdir(lora_path):
        files = scan_lora_directory(lora_path)
        if files:
            effective_lora = files[0]

    if not effective_lora or "No trained" in str(effective_lora):
        effective_lora = None

    if progress_callback:
        progress_callback(0.1, "Loading model...")

    pipe = load_models(base_model)

    if effective_lora:
        if progress_callback:
            progress_callback(0.2, "Loading LoRA...")
        apply_lora(pipe, effective_lora, lora_weight)

    if progress_callback:
        progress_callback(0.3, "Generating image...")

    enhanced_prompt = f"{prompt}, photorealistic, realistic photography, high quality, 8k, detailed skin texture, natural lighting, professional photography"
    enhanced_neg = f"{negative_prompt}, cartoon, anime, illustration, painting, blurry, low quality, deformed"

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
        progress_callback(0.9, "Saving image...")

    img = result.images[0]
    img_path = os.path.join(config.GENERATED_DIR, f"photo_{int(time.time())}.png")
    img.save(img_path)

    return img_path, f"Generated successfully!\nSaved: {img_path}\nSeed: {seed}"

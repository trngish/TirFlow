"""
Data preprocessing module - Batch image processing
Copied from photo_art_framework
"""
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Tuple, List, Callable, Optional

from PIL import Image

# Import config from this directory
import config


def preprocess_image(args: Tuple) -> Tuple[bool, str]:
    """Process single image: crop + resize"""
    src_path, dst_path, target_size, keep_aspect_ratio = args
    try:
        img = Image.open(src_path)

        if img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        w, h = img.size

        if keep_aspect_ratio:
            if w > h:
                new_w = target_size
                new_h = int(h * (target_size / w))
            else:
                new_h = target_size
                new_w = int(w * (target_size / h))
            img = img.resize((new_w, new_h), Image.LANCZOS)
        else:
            min_dim = min(w, h)
            left = (w - min_dim) // 2
            top = (h - min_dim) // 2
            img = img.crop((left, top, left + min_dim, top + min_dim))
            img = img.resize((target_size, target_size), Image.LANCZOS)

        img.save(dst_path, 'JPEG', quality=95)
        return True, src_path
    except Exception as e:
        return False, f"{src_path}: {e}"


def scan_input_directory(input_dir: str) -> Tuple[str, List[Image.Image]]:
    """Scan input directory for images and preview"""
    if not input_dir or not os.path.isdir(input_dir):
        return "Directory does not exist", []

    input_path = Path(input_dir)
    all_images = []

    for img_file in sorted(input_path.iterdir()):
        if img_file.is_file() and img_file.suffix.lower() in config.IMAGE_EXTENSIONS:
            all_images.append(img_file)
            if len(all_images) >= config.PREVIEW_IMAGE_COUNT:
                break

    if not all_images:
        for subdir in sorted(input_path.iterdir()):
            if subdir.is_dir():
                for img_file in sorted(subdir.iterdir()):
                    if img_file.suffix.lower() in config.IMAGE_EXTENSIONS:
                        all_images.append(img_file)
                        if len(all_images) >= config.PREVIEW_IMAGE_COUNT:
                            break
                if len(all_images) >= config.PREVIEW_IMAGE_COUNT:
                    break

    count = 0
    for root, dirs, files in os.walk(input_dir):
        count += sum(1 for f in files if f.lower().endswith(config.IMAGE_EXTENSIONS))

    preview_images = []
    for img_path in all_images[:config.PREVIEW_IMAGE_COUNT]:
        try:
            img = Image.open(img_path)
            preview_images.append(img)
        except:
            pass

    if count > 0:
        return f"Found {count} images", preview_images
    else:
        return "No images found", []


def preprocess_data(
    input_dir: str,
    output_dir: str,
    target_size: int,
    repeat: int,
    trigger_word: str,
    keep_aspect_ratio: bool,
    workers: int,
    progress_callback: Optional[Callable] = None
) -> Tuple[str, str]:
    """
    Preprocess training data

    Returns:
        Tuple[result_message, output_path]
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if not input_path.exists():
        return f"Input directory does not exist: {input_dir}", ""

    aspect_mode = "keep" if keep_aspect_ratio else "square"
    kohya_img_dir = output_path / f"{repeat}_{trigger_word}_{aspect_mode}"
    kohya_img_dir.mkdir(parents=True, exist_ok=True)

    if progress_callback:
        progress_callback(0.1, "Scanning images...")

    all_images = []
    for root, dirs, files in os.walk(input_dir):
        for f in sorted(files):
            if Path(f).suffix.lower() in config.IMAGE_EXTENSIONS:
                all_images.append(Path(root) / f)

    if not all_images:
        return f"No image files found: {input_dir}", ""

    total_images = len(all_images)
    if progress_callback:
        progress_callback(0.2, f"Found {total_images} images")

    tasks = []
    name_counter = {}

    for img_path in all_images:
        rel_path = img_path.relative_to(input_path)
        stem = str(rel_path.with_suffix("")).replace(os.sep, "_")
        if stem in name_counter:
            name_counter[stem] += 1
            stem = f"{stem}_{name_counter[stem]}"
        else:
            name_counter[stem] = 0

        dst_path = kohya_img_dir / f"{stem}.jpg"
        tasks.append((str(img_path), str(dst_path), target_size, keep_aspect_ratio))

    if progress_callback:
        progress_callback(0.3, "Processing images...")

    success_count = 0
    fail_count = 0

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(preprocess_image, task): task for task in tasks}
        for i, future in enumerate(as_completed(futures), 1):
            ok, info = future.result()
            if ok:
                success_count += 1
            else:
                fail_count += 1

            if i % 100 == 0 or i == len(tasks):
                if progress_callback:
                    progress_callback(0.3 + (0.5 * i / len(tasks)), f"Processing: {i}/{total_images}")

    if progress_callback:
        progress_callback(0.85, "Generating captions...")

    caption = f"{trigger_word}, artwork, detailed, high quality, masterpiece"

    for jpg_file in kohya_img_dir.glob("*.jpg"):
        txt_file = jpg_file.with_suffix(".txt")
        if not txt_file.exists():
            txt_file.write_text(caption, encoding='utf-8')

    if progress_callback:
        progress_callback(1.0, "Complete")

    result = f"""Preprocessing complete!

Statistics:
- Success: {success_count} images
- Failed: {fail_count} images
- Target resolution: {target_size}x{target_size}
- Trigger word: {trigger_word}
- Repeat count: {repeat}

Output directory: {kohya_img_dir}"""

    return result, str(kohya_img_dir)

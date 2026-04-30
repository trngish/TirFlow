"""
数据预处理模块 - 图片批量处理
"""
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Tuple, List

from PIL import Image

from config import IMAGE_EXTENSIONS, PREVIEW_IMAGE_COUNT


def preprocess_image(args: Tuple) -> Tuple[bool, str]:
    """处理单张图片：裁剪 + 缩放"""
    src_path, dst_path, target_size, keep_aspect_ratio = args
    try:
        img = Image.open(src_path)

        # 转 RGB（处理 RGBA/P 模式）
        if img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        w, h = img.size

        if keep_aspect_ratio:
            # 保持原尺寸模式：缩放最长的边到target_size
            if w > h:
                new_w = target_size
                new_h = int(h * (target_size / w))
            else:
                new_h = target_size
                new_w = int(w * (target_size / h))
            img = img.resize((new_w, new_h), Image.LANCZOS)
        else:
            # 居中裁剪为正方形
            min_dim = min(w, h)
            left = (w - min_dim) // 2
            top = (h - min_dim) // 2
            img = img.crop((left, top, left + min_dim, top + min_dim))
            img = img.resize((target_size, target_size), Image.LANCZOS)

        # 保存（高质量 JPEG）
        img.save(dst_path, 'JPEG', quality=95)
        return True, src_path
    except Exception as e:
        return False, f"{src_path}: {e}"


def scan_input_directory(input_dir: str) -> Tuple[str, List[Image.Image]]:
    """扫描输入目录，查看图片数量和预览"""
    if not input_dir or not os.path.isdir(input_dir):
        return "目录不存在", []

    input_path = Path(input_dir)
    all_images = []

    # 首先检查输入目录是否直接包含图片文件
    for img_file in sorted(input_path.iterdir()):
        if img_file.is_file() and img_file.suffix.lower() in IMAGE_EXTENSIONS:
            all_images.append(img_file)
            if len(all_images) >= PREVIEW_IMAGE_COUNT:
                break

    # 如果目录中没有图片文件，再检查子目录
    if not all_images:
        for subdir in sorted(input_path.iterdir()):
            if subdir.is_dir():
                for img_file in sorted(subdir.iterdir()):
                    if img_file.suffix.lower() in IMAGE_EXTENSIONS:
                        all_images.append(img_file)
                        if len(all_images) >= PREVIEW_IMAGE_COUNT:
                            break
                if len(all_images) >= PREVIEW_IMAGE_COUNT:
                    break

    # 统计总数
    count = 0
    for root, dirs, files in os.walk(input_dir):
        count += sum(1 for f in files if f.lower().endswith(IMAGE_EXTENSIONS))

    # 生成预览
    preview_images = []
    for img_path in all_images[:PREVIEW_IMAGE_COUNT]:
        try:
            img = Image.open(img_path)
            preview_images.append(img)
        except:
            pass

    if count > 0:
        return f"找到 {count} 张图片", preview_images
    else:
        return "未找到图片文件", []


def preprocess_data(
    input_dir: str,
    output_dir: str,
    target_size: int,
    repeat: int,
    trigger_word: str,
    keep_aspect_ratio: bool,
    workers: int,
    progress_callback=None
) -> Tuple[str, str]:
    """
    预处理训练数据

    Returns:
        Tuple[result_message, output_path]
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # 检查输入目录
    if not input_path.exists():
        return f"输入目录不存在: {input_dir}", ""

    # 创建输出目录（kohya DreamBooth 格式）
    aspect_mode = "keep" if keep_aspect_ratio else "square"
    kohya_img_dir = output_path / f"{repeat}_{trigger_word}_{aspect_mode}"
    kohya_img_dir.mkdir(parents=True, exist_ok=True)

    # 收集所有图片路径（递归扫描）
    if progress_callback:
        progress_callback(0.1, "扫描图片...")

    all_images = []
    for root, dirs, files in os.walk(input_dir):
        for f in sorted(files):
            if Path(f).suffix.lower() in IMAGE_EXTENSIONS:
                all_images.append(Path(root) / f)

    if not all_images:
        return f"未找到图片文件: {input_dir}", ""

    total_images = len(all_images)
    if progress_callback:
        progress_callback(0.2, f"找到 {total_images} 张图片")

    # 准备处理任务
    tasks = []
    name_counter = {}

    for img_path in all_images:
        # 使用相对于输入目录的路径作为文件名，避免不同子目录的同名图片冲突
        rel_path = img_path.relative_to(input_path)
        stem = str(rel_path.with_suffix("")).replace(os.sep, "_")
        # 处理同名文件
        if stem in name_counter:
            name_counter[stem] += 1
            stem = f"{stem}_{name_counter[stem]}"
        else:
            name_counter[stem] = 0

        dst_path = kohya_img_dir / f"{stem}.jpg"
        tasks.append((str(img_path), str(dst_path), target_size, keep_aspect_ratio))

    # 并行处理图片
    if progress_callback:
        progress_callback(0.3, "处理图片...")

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
                    progress_callback(0.3 + (0.5 * i / len(tasks)), f"处理中: {i}/{total_images}")

    # 生成标签文件
    if progress_callback:
        progress_callback(0.85, "生成标签...")

    caption = f"{trigger_word}, artwork, detailed, high quality, masterpiece"

    for jpg_file in kohya_img_dir.glob("*.jpg"):
        txt_file = jpg_file.with_suffix(".txt")
        if not txt_file.exists():
            txt_file.write_text(caption, encoding='utf-8')

    if progress_callback:
        progress_callback(1.0, "完成")

    result = f"""预处理完成！

统计信息:
- 成功处理: {success_count} 张
- 处理失败: {fail_count} 张
- 目标分辨率: {target_size}x{target_size}
- 触发词: {trigger_word}
- 重复次数: {repeat}

输出目录: {kohya_img_dir}"""

    return result, str(kohya_img_dir)

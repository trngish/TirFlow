"""
Gradio UI模块 - 写真训练框架图形界面
"""
import gradio as gr
import pandas as pd
import threading
import logging as _app_logging

import config
from train_engine import (
    get_available_models, get_existing_loras, get_loss_chart_data,
    get_training_state, start_training, stop_training,
    count_images, clear_loss_history, clear_train_logs_queue,
    get_training_status, train_logs_queue, _close_training_logger,
    training_status_info
)
from preprocess import scan_input_directory, preprocess_data
from generate import get_lora_models, generate_photo, scan_lora_directory
from presets import list_presets, get_preset_params, get_preset_trigger, get_preset_info


def build_ui():
    """构建Gradio界面"""

    with gr.Blocks(title="写真训练框架") as app:
        gr.Markdown("# 写真训练框架")
        gr.Markdown("写真/艺术照训练系统 | 数据预处理 → 训练 → 图片生成")

        # ========== 数据预处理 Tab ==========
        with gr.Tab("🖼️ 数据预处理"):
            gr.Markdown("### 图片预处理工具")
            gr.Markdown("批量处理：居中裁剪 + 缩放 + 生成标签")

            with gr.Row():
                # 输入设置
                with gr.Column(scale=1):
                    gr.Markdown("#### 输入设置")
                    pre_input_dir = gr.Textbox(
                        value=r"",
                        label="原始图片目录"
                    )
                    pre_scan_btn = gr.Button("🔍 扫描输入目录")
                    pre_input_info = gr.Textbox(
                        value="点击扫描查看图片数量",
                        label="输入目录信息",
                        interactive=False
                    )
                    pre_preview = gr.Gallery(
                        label="图片预览（前6张）",
                        columns=3,
                        height=200
                    )

                # 输出设置
                with gr.Column(scale=1):
                    gr.Markdown("#### 输出设置")
                    pre_output_dir = gr.Textbox(
                        value=config.TRAIN_DATA_DIR,
                        label="输出目录"
                    )
                    pre_target_size = gr.Dropdown(
                        choices=[512, 768, 896, 1024],
                        value=768,
                        label="目标分辨率"
                    )
                    pre_keep_aspect = gr.Checkbox(
                        value=True,
                        label="保持原照片尺寸比例",
                        info="勾选：保持原尺寸 | 不勾选：裁剪为正方形"
                    )
                    pre_repeat = gr.Slider(
                        1, 20, value=10, step=1,
                        label="重复次数"
                    )
                    pre_trigger = gr.Textbox(
                        value=config.DEFAULT_TRIGGER_WORD,
                        label="触发词"
                    )
                    pre_workers = gr.Slider(
                        1, 8, value=4, step=1,
                        label="并行处理线程数"
                    )

            pre_btn = gr.Button("🚀 开始预处理", variant="primary", size="lg")
            pre_result = gr.Textbox(
                label="预处理结果",
                value="配置参数后点击开始预处理",
                lines=8,
                interactive=False
            )

            # 预处理事件
            pre_scan_btn.click(
                fn=scan_input_directory,
                inputs=[pre_input_dir],
                outputs=[pre_input_info, pre_preview]
            )

            pre_btn.click(
                fn=preprocess_data,
                inputs=[
                    pre_input_dir, pre_output_dir, pre_target_size,
                    pre_repeat, pre_trigger, pre_keep_aspect, pre_workers
                ],
                outputs=[pre_result]
            )

        # ========== 训练 Tab ==========
        with gr.Tab("🚀 训练"):
            with gr.Row():
                # 左列：模型 + 续训练 + 数据
                with gr.Column(scale=1):
                    gr.Markdown("### 模型选择")
                    base_model = gr.Dropdown(
                        choices=get_available_models(),
                        value=get_available_models()[0] if get_available_models() and "请先下载" not in get_available_models()[0] else None,
                        label="基础模型"
                    )

                    gr.Markdown("### 继续训练")
                    enable_resume = gr.Checkbox(
                        value=False,
                        label="启用续训练（加载已有LoRA继续训练）"
                    )
                    resume_lora = gr.Dropdown(
                        choices=get_existing_loras(),
                        value=get_existing_loras()[0] if get_existing_loras() and "无已训练" not in get_existing_loras()[0] else None,
                        label="选择LoRA模型"
                    )
                    resume_refresh_btn = gr.Button("🔄 刷新", size="sm")

                    gr.Markdown("### 训练数据")
                    trigger_word = gr.Textbox(
                        value=config.DEFAULT_TRIGGER_WORD,
                        label="触发词"
                    )
                    train_data_dir = gr.Textbox(
                        value=config.TRAIN_DATA_DIR,
                        label="训练数据目录"
                    )
                    img_count = gr.Number(
                        value=count_images(config.TRAIN_DATA_DIR),
                        label="图片数量"
                    )
                    scan_btn = gr.Button("📁 扫描数据")
                    train_preview = gr.Gallery(
                        label="训练图片预览（前6张）",
                        columns=3,
                        height=150
                    )

                # 右列：预设 + 参数 + Loss曲线
                with gr.Column(scale=1):
                    gr.Markdown("### 预设配置")
                    preset_dropdown = gr.Dropdown(
                        choices=list_presets(),
                        value=None,
                        label="选择预设（可选）",
                        info="选择预设自动填充参数"
                    )
                    preset_info = gr.Textbox(
                        value="",
                        label="预设信息",
                        interactive=False
                    )

                    gr.Markdown("### 训练参数")
                    output_name = gr.Textbox(
                        value=config.DEFAULT_OUTPUT_NAME,
                        label="输出名称"
                    )

                    with gr.Row():
                        res_w = gr.Dropdown(
                            choices=[512, 576, 640],
                            value=config.DEFAULT_RESOLUTION_W,
                            label="宽度"
                        )
                        res_h = gr.Dropdown(
                            choices=[768, 896, 1024],
                            value=config.DEFAULT_RESOLUTION_H,
                            label="高度"
                        )

                    network_dim = gr.Slider(
                        16, 64, value=config.DEFAULT_NETWORK_DIM, step=8,
                        label="LoRA维度"
                    )
                    steps = gr.Slider(
                        500, 10000, value=config.DEFAULT_STEPS, step=500,
                        label="训练步数"
                    )
                    batch_size = gr.Slider(
                        1, 4, value=config.DEFAULT_BATCH_SIZE, step=1,
                        label="Batch Size"
                    )
                    learning_rate = gr.Textbox(
                        value=config.DEFAULT_LEARNING_RATE,
                        label="学习率"
                    )

                    gr.Markdown("### Loss 曲线")
                    loss_chart = gr.Image(
                        label="Training Loss",
                        height=250
                    )

            with gr.Row():
                start_btn = gr.Button("🚀 开始训练", variant="primary", size="lg")
                stop_btn = gr.Button("⏹️ 停止训练", size="lg")

            train_progress = gr.Slider(0, 100, value=0, label="训练进度")
            train_logs = gr.Textbox(label="训练日志", lines=12, interactive=False)

            # 训练状态轮询（更新进度、日志和Loss曲线）
            def poll_training_status():
                import matplotlib.pyplot as plt
                progress, logs = get_training_status()
                df = get_loss_chart_data()
                # 有真实数据（步数>0）才画图
                has_data = df is not None and len(df) > 1 or (len(df) == 1 and df['Step'].iloc[0] > 0)
                if has_data:
                    fig, ax = plt.subplots(figsize=(6, 3))
                    ax.plot(df['Step'], df['Loss'], 'b-', linewidth=1)
                    ax.set_xlabel('Step')
                    ax.set_ylabel('Loss')
                    ax.set_title('Training Loss')
                    ax.grid(True, alpha=0.3)
                    plt.tight_layout()
                    import io
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', dpi=80)
                    plt.close(fig)
                    buf.seek(0)
                    chart_img = buf
                else:
                    chart_img = None
                return progress, logs, chart_img

            timer = gr.Timer(0.5)
            timer.tick(
                fn=poll_training_status,
                outputs=[train_progress, train_logs, loss_chart]
            )

            # 训练事件
            def on_scan(dir_path):
                msg, images = scan_input_directory(dir_path)
                count_val = count_images(dir_path)
                return gr.update(value=count_val), images

            scan_btn.click(
                fn=on_scan,
                inputs=[train_data_dir],
                outputs=[img_count, train_preview]
            )

            # 预设选择事件
            def on_preset_selected(preset_name):
                if not preset_name:
                    return gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), ""
                params = get_preset_params(preset_name)
                trigger = get_preset_trigger(preset_name)
                info = get_preset_info(preset_name)
                return (
                    params.get("network_dim", 32),
                    params.get("max_train_steps", 3000),
                    params.get("resolution_w", 512),
                    params.get("resolution_h", 768),
                    params.get("learning_rate", "1e-4"),
                    params.get("output_name", preset_name),
                    trigger,
                    info
                )

            preset_dropdown.change(
                fn=on_preset_selected,
                inputs=[preset_dropdown],
                outputs=[network_dim, steps, res_w, res_h, learning_rate, output_name, trigger_word, preset_info]
            )

            resume_refresh_btn.click(
                fn=get_existing_loras,
                inputs=[],
                outputs=[resume_lora]
            )

            start_btn.click(
                fn=_start_training_wrapper,
                inputs=[
                    base_model, trigger_word, train_data_dir, output_name,
                    network_dim, steps, res_w, res_h, batch_size,
                    learning_rate, enable_resume, resume_lora
                ],
                outputs=[train_progress, train_logs],
                queue=True
            )

            stop_btn.click(
                fn=stop_training,
                outputs=[train_progress, train_logs]
            )

        # ========== 图片生成 Tab ==========
        with gr.Tab("🎨 图片生成"):
            gr.Markdown("### 写真图片生成")
            gr.Markdown("使用已训练的LoRA模型生成写真图片")

            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("#### 模型选择")
                    gen_base_model = gr.Dropdown(
                        choices=get_available_models(),
                        value=get_available_models()[0] if get_available_models() and "请先下载" not in get_available_models()[0] else None,
                        label="基础模型"
                    )
                    gen_lora = gr.Textbox(
                        value=r"D:\TirFlow\photo_art_framework\output",
                        label="LoRA模型路径"
                    )
                    gen_lora_scan_btn = gr.Button("🔍 扫描LoRA", size="sm")
                    gen_lora_list = gr.Dropdown(
                        choices=[],
                        label="选择LoRA文件（可选）"
                    )
                    gen_lora_weight = gr.Slider(
                        0, 2.0, value=1.0, step=0.1,
                        label="LoRA权重"
                    )

                with gr.Column(scale=3):
                    gr.Markdown("#### 生成参数")
                    gen_prompt = gr.Textbox(
                        value="1girl, portrait, fashion photo, elegant dress, studio lighting",
                        label="提示词",
                        lines=3
                    )
                    gen_neg_prompt = gr.Textbox(
                        value="ugly, deformed, blurry, low quality, cartoon, anime",
                        label="负面提示词",
                        lines=2
                    )

            with gr.Row():
                with gr.Column():
                    with gr.Row():
                        gen_w = gr.Dropdown(
                            choices=[512, 576, 640, 704],
                            value=512,
                            label="宽度"
                        )
                        gen_h = gr.Dropdown(
                            choices=[768, 896, 1024, 1152],
                            value=768,
                            label="高度"
                        )
                    with gr.Row():
                        gen_steps = gr.Slider(
                            20, 50, value=30, step=5,
                            label="步数"
                        )
                        gen_cfg = gr.Slider(
                            5, 15, value=7.5, step=0.5,
                            label="CFG Scale"
                        )
                        gen_seed = gr.Number(
                            value=-1,
                            label="Seed (-1=随机)"
                        )
                    gen_btn = gr.Button("🎨 生成图片", variant="primary", size="lg")

                with gr.Column():
                    gen_output = gr.Image(label="生成的图片", height=300)
                    gen_status = gr.Textbox(label="状态")

            def on_scan_lora(dir_path):
                files = scan_lora_directory(dir_path)
                return gr.update(choices=files, value=files[0] if files else None)

            gen_lora_scan_btn.click(
                fn=on_scan_lora,
                inputs=[gen_lora],
                outputs=[gen_lora_list]
            )

            gen_btn.click(
                fn=generate_photo,
                inputs=[
                    gen_base_model, gen_lora, gen_lora_weight,
                    gen_prompt, gen_neg_prompt,
                    gen_w, gen_h, gen_steps, gen_cfg, gen_seed,
                    gen_lora_list
                ],
                outputs=[gen_output, gen_status]
            )

        # ========== 系统信息 Tab ==========
        with gr.Tab("ℹ️ 系统信息"):
            import sys
            import torch
            gr.Markdown("### 环境信息")
            gr.Markdown(f"""
            - **Python**: {sys.version.split()[0]}
            - **PyTorch**: {torch.__version__}
            - **CUDA**: {torch.version.cuda if torch.version.cuda else "N/A"}
            - **工作目录**: {config.WORKSPACE}
            - **模型目录**: {config.MODEL_DIR}
            - **输出目录**: {config.OUTPUT_DIR}
            """)

    return app


def _start_training_wrapper(
    base_model, trigger_word, train_data_dir, output_name,
    network_dim, steps, resolution_w, resolution_h, batch_size,
    learning_rate, resume_training, resume_lora_path
):
    """训练启动包装函数（后台线程运行训练）"""
    clear_loss_history()
    clear_train_logs_queue()

    try:
        lr = float(learning_rate)
    except:
        lr = 1e-4

    def run_training():
        try:
            start_training(
                base_model=base_model,
                trigger_word=trigger_word,
                train_data_dir=train_data_dir,
                output_name=output_name,
                network_dim=int(network_dim),
                steps=int(steps),
                resolution_w=int(resolution_w),
                resolution_h=int(resolution_h),
                batch_size=int(batch_size),
                learning_rate=lr,
                resume_training=resume_training,
                resume_lora_path=resume_lora_path
            )
        except Exception as e:
            import traceback
            train_logs_queue.put(f"【线程异常】{e}")
            train_logs_queue.put(traceback.format_exc())
            _app_logging.error(f"训练线程异常: {e}")
            _app_logging.error(traceback.format_exc())
            training_status_info["running"] = False
            training_status_info["status"] = f"训练异常: {e}"
            _close_training_logger()

    thread = threading.Thread(target=run_training, daemon=True)
    thread.start()

    return 0, "训练启动中..."

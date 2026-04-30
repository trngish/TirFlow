"""
写真/艺术照训练框架 - 主入口
===================================

功能：
- 🖼️ 数据预处理：批量图片处理（裁剪+缩放+生成标签）
- 🚀 LoRA训练：SDXL LoRA模型训练
- 🎨 图片生成：使用训练好的LoRA生成写真

用法：
    python main.py
"""
from logging_config import setup_logging, log_info, log_error
from ui import build_ui


if __name__ == "__main__":
    # 初始化日志
    log_file = setup_logging()

    print("=" * 50)
    print("  写真/艺术照训练框架")
    print("  功能: 预处理 → 训练 → 图片生成")
    print("=" * 50)

    log_info("写真/艺术照训练框架启动")
    log_info(f"日志文件: {log_file}")

    try:
        app = build_ui()
        app.launch(
            server_name="127.0.0.1",
            server_port=7860,
            inbrowser=True
        )
    except Exception as e:
        log_error(f"启动失败: {e}")
        raise

    log_info("框架已关闭")

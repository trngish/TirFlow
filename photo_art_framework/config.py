"""
配置模块 - 常量与路径定义
"""
import os

# 路径配置
WORKSPACE = r"D:\TirFlow\photo_art_framework"
MODEL_DIR = r"D:\TirFlow\models"
OUTPUT_DIR = r"D:\TirFlow\photo_art_framework\output"
TRAIN_DATA_DIR = r"D:\TirFlow\train_data_photoart"
SCRIPTS_DIR = r"D:\TirFlow\sd-scripts"
GENERATED_DIR = r"D:\TirFlow\photo_art_framework\generated"
LOG_DIR = r"D:\TirFlow\photo_art_framework\logs"

# 训练脚本路径
VENV_PYTHON = os.path.join(SCRIPTS_DIR, "venv", "Scripts", "python.exe")
SDXL_TRAIN_SCRIPT = os.path.join(SCRIPTS_DIR, "sdxl_train_network.py")

# 确保目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TRAIN_DATA_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# 训练参数默认值
DEFAULT_TRIGGER_WORD = "photo_style"
DEFAULT_OUTPUT_NAME = "photo_lora"
DEFAULT_RESOLUTION_W = 512
DEFAULT_RESOLUTION_H = 768
DEFAULT_NETWORK_DIM = 32
DEFAULT_STEPS = 3000
DEFAULT_BATCH_SIZE = 1
DEFAULT_LEARNING_RATE = "1e-4"
DEFAULT_PREPROCESS_RESOLUTION = 768
DEFAULT_REPEAT_COUNT = 10

# 图像预处理配置
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
PREVIEW_IMAGE_COUNT = 6
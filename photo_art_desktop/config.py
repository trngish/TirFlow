"""
Configuration module - Constants and path definitions
Copied from photo_art_framework for desktop standalone use
"""
import os

# Path configuration
WORKSPACE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = r"D:\TirFlow\models"
OUTPUT_DIR = os.path.join(WORKSPACE, "output")
TRAIN_DATA_DIR = r"D:\TirFlow\train_data_photoart"
SCRIPTS_DIR = r"D:\TirFlow\sd-scripts"
GENERATED_DIR = os.path.join(WORKSPACE, "generated")
LOG_DIR = os.path.join(WORKSPACE, "logs")

# Training script path
VENV_PYTHON = os.path.join(SCRIPTS_DIR, "venv", "Scripts", "python.exe")
SDXL_TRAIN_SCRIPT = os.path.join(SCRIPTS_DIR, "sdxl_train_network.py")

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TRAIN_DATA_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Training parameter defaults
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

# Image preprocessing config
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
PREVIEW_IMAGE_COUNT = 6

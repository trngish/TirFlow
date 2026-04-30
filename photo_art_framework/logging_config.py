"""
日志模块 - 统一日志管理
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

from config import WORKSPACE, LOG_DIR


def setup_logging():
    """初始化日志配置"""
    os.makedirs(LOG_DIR, exist_ok=True)

    log_file = os.path.join(LOG_DIR, f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

    # 日志格式
    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 文件处理器 - INFO及以上
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # 控制台处理器 - INFO及以上
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # 根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # 禁用第三方库的DEBUG日志
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("xformers").setLevel(logging.ERROR)
    logging.getLogger("triton").setLevel(logging.ERROR)

    return log_file


def get_logger(name: str = None) -> logging.Logger:
    """获取日志器"""
    if name:
        return logging.getLogger(name)
    return logging.getLogger()


def log_info(message: str):
    """记录INFO日志"""
    logging.info(message)


def log_error(message: str):
    """记录ERROR日志"""
    logging.error(message)


def log_exception(message: str, exc: Exception = None):
    """记录异常日志"""
    if exc:
        logging.exception(f"{message}: {exc}")
    else:
        logging.exception(message)

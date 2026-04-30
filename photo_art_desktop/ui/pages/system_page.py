"""
System info page - About and system information
"""
import sys
import os

from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel
from PySide6.QtCore import Qt

from qfluentwidgets import CardWidget, StrongBodyLabel, CaptionLabel, SubtitleLabel

import config


class SystemPage(QWidget):
    """About / System Information tab"""

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)

        # Title
        title = SubtitleLabel("PhotoArt Desktop")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title)

        version_label = CaptionLabel("Version 1.0.0")
        main_layout.addWidget(version_label)
        main_layout.addSpacing(8)

        # Environment Info Card
        env_card = CardWidget()
        env_layout = QGridLayout(env_card)

        env_layout.addWidget(StrongBodyLabel("Environment Information"), 0, 0, 1, 2)

        row = 1

        # Python version
        env_layout.addWidget(CaptionLabel("Python:"), row, 0)
        env_layout.addWidget(QLabel(sys.version.split()[0]), row, 1)
        row += 1

        # PyTorch version
        try:
            import torch
            env_layout.addWidget(CaptionLabel("PyTorch:"), row, 0)
            env_layout.addWidget(QLabel(torch.__version__), row, 1)
            row += 1

            # CUDA version
            env_layout.addWidget(CaptionLabel("CUDA:"), row, 0)
            env_layout.addWidget(QLabel(torch.version.cuda if torch.version.cuda else "N/A"), row, 1)
            row += 1

            # GPU info
            if torch.cuda.is_available():
                env_layout.addWidget(CaptionLabel("GPU:"), row, 0)
                gpu_name = torch.cuda.get_device_name(0)
                env_layout.addWidget(QLabel(gpu_name), row, 1)
                row += 1

                env_layout.addWidget(CaptionLabel("GPU Memory:"), row, 0)
                gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1024**3
                env_layout.addWidget(QLabel(f"{gpu_mem:.1f} GB"), row, 1)
                row += 1
        except ImportError:
            env_layout.addWidget(CaptionLabel("PyTorch: Not installed"), row, 1)
            row += 1

        main_layout.addWidget(env_card)

        # Path Configuration Card
        path_card = CardWidget()
        path_layout = QGridLayout(path_card)

        path_layout.addWidget(StrongBodyLabel("Path Configuration"), 0, 0, 1, 2)

        row = 1
        paths = [
            ("Workspace:", config.WORKSPACE),
            ("Model Directory:", config.MODEL_DIR),
            ("Output Directory:", config.OUTPUT_DIR),
            ("Training Data:", config.TRAIN_DATA_DIR),
            ("Scripts Directory:", config.SCRIPTS_DIR),
            ("Generated Images:", config.GENERATED_DIR),
            ("Logs:", config.LOG_DIR),
        ]

        for label, path in paths:
            path_layout.addWidget(CaptionLabel(label), row, 0)
            path_label = QLabel(path)
            path_label.setWordWrap(True)
            path_layout.addWidget(path_label, row, 1)
            row += 1

        main_layout.addWidget(path_card)

        # About Card
        about_card = CardWidget()
        about_layout = QVBoxLayout(about_card)

        about_layout.addWidget(StrongBodyLabel("About"))
        about_text = CaptionLabel(
            "PhotoArt Desktop is a standalone desktop application for training LoRA models "
            "for Stable Diffusion XL. It provides a native Windows experience with "
            "data preprocessing, training, and image generation capabilities."
        )
        about_text.setWordWrap(True)
        about_layout.addWidget(about_text)

        about_layout.addWidget(StrongBodyLabel("Built with:"))
        tech_text = CaptionLabel("PySide6 + qfluentwidgets + diffusers + kohya-ss/sd-scripts")
        about_layout.addWidget(tech_text)

        main_layout.addWidget(about_card)

        main_layout.addStretch()

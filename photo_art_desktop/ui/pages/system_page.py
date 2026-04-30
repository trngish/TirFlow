"""
System info page - About and system information
"""
import sys
import os

from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel
from PySide6.QtCore import Qt

from qfluentwidgets import CardWidget, StrongBodyLabel, CaptionLabel, SubtitleLabel

import config
import i18n


class SystemPage(QWidget):
    """About / System Information tab"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.title_label = None
        self.env_title_label = None
        self.path_title_label = None
        self.about_title_label = None
        self.tech_title_label = None
        self.about_text_label = None

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)

        # Title
        self.title_label = SubtitleLabel(i18n.T("photo_art_desktop"))
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(self.title_label)

        version_label = CaptionLabel("Version 1.0.0")
        main_layout.addWidget(version_label)
        main_layout.addSpacing(8)

        # Environment Info Card
        env_card = CardWidget()
        env_layout = QGridLayout(env_card)

        self.env_title_label = StrongBodyLabel(i18n.T("environment"))
        env_layout.addWidget(self.env_title_label, 0, 0, 1, 2)

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

        self.path_title_label = StrongBodyLabel(i18n.T("path_config"))
        path_layout.addWidget(self.path_title_label, 0, 0, 1, 2)

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

        self.about_title_label = StrongBodyLabel(i18n.T("about"))
        about_layout.addWidget(self.about_title_label)
        self.about_text_label = CaptionLabel(i18n.T("app_desc"))
        self.about_text_label.setWordWrap(True)
        about_layout.addWidget(self.about_text_label)

        self.tech_title_label = StrongBodyLabel(i18n.T("built_with") + ":")
        about_layout.addWidget(self.tech_title_label)
        tech_text = CaptionLabel(i18n.T("tech_stack"))
        about_layout.addWidget(tech_text)

        main_layout.addWidget(about_card)

        main_layout.addStretch()

        # Connect language change signal
        i18n.get_language_manager().language_changed.connect(self.retranslate)

    def retranslate(self):
        """Retranslate all UI text"""
        self.title_label.setText(i18n.T("photo_art_desktop"))
        self.env_title_label.setText(i18n.T("environment"))
        self.path_title_label.setText(i18n.T("path_config"))
        self.about_title_label.setText(i18n.T("about"))
        self.about_text_label.setText(i18n.T("app_desc"))
        self.tech_title_label.setText(i18n.T("built_with") + ":")

"""
Settings page - Language and preferences
"""
import os
import sys

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

from qfluentwidgets import CardWidget, StrongBodyLabel, CaptionLabel, ComboBox, PrimaryPushButton, SubtitleLabel

import config
import i18n


class SettingsPage(QWidget):
    """Settings tab page"""

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)

        # Title
        title = SubtitleLabel(i18n.T("settings"))
        main_layout.addWidget(title)

        # === Language Card ===
        lang_card = CardWidget()
        lang_layout = QVBoxLayout(lang_card)

        lang_row = QHBoxLayout()
        lang_label = StrongBodyLabel(i18n.T("language"))
        self.lang_combo = ComboBox()
        self.lang_combo.addItems([i18n.LANGUAGES[k] for k in i18n.LANGUAGES.keys()])

        # Set current language
        current = i18n.get_language()
        current_index = list(i18n.LANGUAGES.keys()).index(current) if current in i18n.LANGUAGES else 0
        self.lang_combo.setCurrentIndex(current_index)

        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)

        lang_row.addWidget(lang_label)
        lang_row.addWidget(self.lang_combo, stretch=1)
        lang_layout.addLayout(lang_row)

        self.lang_status = CaptionLabel("")
        lang_layout.addWidget(self.lang_status)

        main_layout.addWidget(lang_card)

        # === About Card ===
        about_card = CardWidget()
        about_layout = QVBoxLayout(about_card)

        about_title = StrongBodyLabel(i18n.T("about"))
        about_layout.addWidget(about_title)

        app_name = SubtitleLabel(i18n.T("photo_art_desktop"))
        app_name.setStyleSheet("font-size: 24px; font-weight: bold;")
        about_layout.addWidget(app_name)

        version_label = CaptionLabel(f"{i18n.T('version')} 1.0.0")
        about_layout.addWidget(version_label)

        desc_label = CaptionLabel(i18n.T("app_desc"))
        desc_label.setWordWrap(True)
        about_layout.addWidget(desc_label)

        tech_label = CaptionLabel(f"{i18n.T('built_with')}: {i18n.T('tech_stack')}")
        about_layout.addWidget(tech_label)

        main_layout.addWidget(about_card)

        main_layout.addStretch()

    def on_language_changed(self, index: int):
        """Handle language change"""
        lang_keys = list(i18n.LANGUAGES.keys())
        if 0 <= index < len(lang_keys):
            lang = lang_keys[index]
            i18n.set_language(lang)
            self.lang_status.setText(i18n.T("language_changed"))

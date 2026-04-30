"""
Preprocess page - Image batch processing UI
"""
import os
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QSlider, QCheckBox,
    QComboBox, QProgressBar, QGroupBox, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal, Slot

from qfluentwidgets import (
    LineEdit, PushButton, Slider, CheckBox, ComboBox,
    ProgressBar, PrimaryPushButton, CardWidget, StrongBodyLabel,
    CaptionLabel, setFont
)
from qfluentwidgets.common.icon import FluentIcon

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config
import preprocess as preprocess_module
from ui.widgets.log_viewer import LogViewer


class PreprocessWorker(QThread):
    """Worker thread for preprocessing"""
    progress = Signal(float, str)
    finished = Signal(str, str)
    error = Signal(str)

    def __init__(self, input_dir, output_dir, target_size, repeat, trigger_word,
                 keep_aspect, workers):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.target_size = target_size
        self.repeat = repeat
        self.trigger_word = trigger_word
        self.keep_aspect = keep_aspect
        self.workers = workers

    def run(self):
        try:
            result, output_path = preprocess_module.preprocess_data(
                self.input_dir, self.output_dir, self.target_size,
                self.repeat, self.trigger_word, self.keep_aspect,
                self.workers,
                progress_callback=lambda p, s: self.progress.emit(p, s)
            )
            self.finished.emit(result, output_path)
        except Exception as e:
            self.error.emit(str(e))


class PreprocessPage(QWidget):
    """Preprocess tab page"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.worker = None
        self.preview_images = []

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)

        # === Row 1: Input settings ===
        row1 = QHBoxLayout()

        self.input_label = StrongBodyLabel("Input Directory:")
        self.input_edit = LineEdit()
        self.input_edit.setPlaceholderText("Select raw images directory...")
        self.browse_input_btn = PushButton("Browse")
        self.browse_input_btn.clicked.connect(self.browse_input)

        row1.addWidget(self.input_label)
        row1.addWidget(self.input_edit, stretch=1)
        row1.addWidget(self.browse_input_btn)

        # === Row 2: Stats + Preview ===
        row2 = QHBoxLayout()

        self.stats_label = CaptionLabel("Found 0 images")
        row2.addWidget(self.stats_label)
        row2.addStretch()

        main_layout.addLayout(row1)
        main_layout.addLayout(row2)

        # === Parameters Group ===
        params_group = CardWidget()
        params_layout = QGridLayout(params_group)

        # Output directory
        params_layout.addWidget(StrongBodyLabel("Output Directory:"), 0, 0)
        self.output_edit = LineEdit()
        self.output_edit.setText(config.TRAIN_DATA_DIR)
        self.browse_output_btn = PushButton("Browse")
        self.browse_output_btn.clicked.connect(self.browse_output)
        params_layout.addWidget(self.output_edit, 0, 1)
        params_layout.addWidget(self.browse_output_btn, 0, 2)

        # Target resolution
        params_layout.addWidget(StrongBodyLabel("Target Resolution:"), 1, 0)
        self.resolution_combo = ComboBox()
        self.resolution_combo.addItems(["512", "768", "896", "1024"])
        self.resolution_combo.setCurrentText("768")
        params_layout.addWidget(self.resolution_combo, 1, 1, 1, 2)

        # Keep aspect ratio
        self.keep_aspect_check = CheckBox("Keep original aspect ratio")
        self.keep_aspect_check.setChecked(True)
        params_layout.addWidget(self.keep_aspect_check, 2, 1, 1, 2)

        # Repeat count
        params_layout.addWidget(StrongBodyLabel("Repeat Count:"), 3, 0)
        self.repeat_slider = Slider(Qt.Orientation.Horizontal)
        self.repeat_slider.setMinimum(1)
        self.repeat_slider.setMaximum(20)
        self.repeat_slider.setValue(10)
        self.repeat_label = CaptionLabel("10")
        self.repeat_slider.valueChanged.connect(
            lambda v: self.repeat_label.setText(str(v))
        )
        params_layout.addWidget(self.repeat_slider, 3, 1)
        params_layout.addWidget(self.repeat_label, 3, 2)

        # Trigger word
        params_layout.addWidget(StrongBodyLabel("Trigger Word:"), 4, 0)
        self.trigger_edit = LineEdit()
        self.trigger_edit.setText(config.DEFAULT_TRIGGER_WORD)
        params_layout.addWidget(self.trigger_edit, 4, 1, 1, 2)

        # Workers
        params_layout.addWidget(StrongBodyLabel("Workers:"), 5, 0)
        self.workers_slider = Slider(Qt.Orientation.Horizontal)
        self.workers_slider.setMinimum(1)
        self.workers_slider.setMaximum(8)
        self.workers_slider.setValue(4)
        self.workers_label = CaptionLabel("4")
        self.workers_slider.valueChanged.connect(
            lambda v: self.workers_label.setText(str(v))
        )
        params_layout.addWidget(self.workers_slider, 5, 1)
        params_layout.addWidget(self.workers_label, 5, 2)

        main_layout.addWidget(params_group)

        # === Start Button ===
        self.start_btn = PrimaryPushButton("Start Preprocessing")
        self.start_btn.clicked.connect(self.start_preprocessing)
        main_layout.addWidget(self.start_btn)

        # === Progress ===
        self.progress_bar = ProgressBar()
        self.progress_label = CaptionLabel("")
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.progress_label)

        # === Log Viewer ===
        log_label = StrongBodyLabel("Log")
        main_layout.addWidget(log_label)

        self.log_viewer = LogViewer(max_lines=200)
        main_layout.addWidget(self.log_viewer, stretch=1)

    def browse_input(self):
        from PySide6.QtWidgets import QFileDialog
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Input Directory"
        )
        if dir_path:
            self.input_edit.setText(dir_path)
            self.scan_input()

    def browse_output(self):
        from PySide6.QtWidgets import QFileDialog
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Output Directory"
        )
        if dir_path:
            self.output_edit.setText(dir_path)

    def scan_input(self):
        input_dir = self.input_edit.text()
        if not input_dir or not os.path.isdir(input_dir):
            self.stats_label.setText("Invalid directory")
            return

        msg, images = preprocess_module.scan_input_directory(input_dir)
        self.stats_label.setText(msg)
        self.preview_images = images

    def start_preprocessing(self):
        input_dir = self.input_edit.text()
        output_dir = self.output_edit.text()

        if not input_dir or not os.path.isdir(input_dir):
            self.log_viewer.append_log("Error: Invalid input directory")
            return

        if not output_dir:
            self.log_viewer.append_log("Error: Invalid output directory")
            return

        self.start_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting...")

        self.worker = PreprocessWorker(
            input_dir=input_dir,
            output_dir=output_dir,
            target_size=int(self.resolution_combo.currentText()),
            repeat=self.repeat_slider.value(),
            trigger_word=self.trigger_edit.text(),
            keep_aspect=self.keep_aspect_check.isChecked(),
            workers=self.workers_slider.value()
        )

        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    @Slot(float, str)
    def on_progress(self, progress: float, status: str):
        self.progress_bar.setValue(int(progress * 100))
        self.progress_label.setText(status)

    @Slot(str, str)
    def on_finished(self, result: str, output_path: str):
        self.log_viewer.append_log(result)
        self.progress_bar.setValue(100)
        self.progress_label.setText("Complete!")
        self.start_btn.setEnabled(True)

    @Slot(str)
    def on_error(self, error: str):
        self.log_viewer.append_log(f"Error: {error}")
        self.start_btn.setEnabled(True)

"""
Training page - LoRA training UI with compact layout
"""
import os
import sys
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QSlider
)
from PySide6.QtCore import Qt, QThread, Signal, Slot

from qfluentwidgets import (
    LineEdit, PushButton, Slider, CheckBox, ComboBox,
    ProgressBar, PrimaryPushButton, CardWidget, StrongBodyLabel,
    CaptionLabel, setFont, ProgressRing
)
from qfluentwidgets.common.icon import FluentIcon

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config
import train_engine
import presets as presets_module
from ui.widgets.loss_chart import LossChart
from ui.widgets.log_viewer import LogViewer


class TrainWorker(QThread):
    """Worker thread for training"""
    progress = Signal(int, int, float)
    log_line = Signal(str)
    finished = Signal(int, str)
    error = Signal(str)

    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs

    def run(self):
        try:
            code, msg = train_engine.start_training(
                **self.kwargs,
                log_callback=lambda l: self.log_line.emit(l),
                progress_callback=lambda p, s, l: self.progress.emit(p, s, l)
            )
            self.finished.emit(code, msg)
        except Exception as e:
            self.error.emit(str(e))


class TrainPage(QWidget):
    """Training tab page with compact layout"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.worker = None

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)

        # === Row 1: Model + Resume ===
        row1 = QHBoxLayout()

        self.model_label = StrongBodyLabel("Base Model:")
        self.model_edit = LineEdit()
        self.model_edit.setPlaceholderText("Select base model (.safetensors, .ckpt, .pth)...")
        self.browse_model_btn = PushButton("Browse")
        self.browse_model_btn.clicked.connect(self.browse_model)

        self.preset_label = StrongBodyLabel("Preset:")
        self.preset_combo = ComboBox()
        self.preset_combo.addItems(presets_module.list_presets())
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)

        row1.addWidget(self.model_label)
        row1.addWidget(self.model_edit, stretch=1)
        row1.addWidget(self.browse_model_btn)
        row1.addWidget(self.preset_label)
        row1.addWidget(self.preset_combo, stretch=1)

        main_layout.addLayout(row1)

        # === Row 2: Resume settings + Preset info ===
        row2 = QHBoxLayout()

        self.resume_check = CheckBox("Enable Resume Training")
        self.resume_edit = LineEdit()
        self.resume_edit.setPlaceholderText("Select LoRA to resume from (.safetensors)...")
        self.browse_resume_btn = PushButton("Browse")
        self.browse_resume_btn.clicked.connect(self.browse_resume)

        self.preset_info_label = CaptionLabel("")

        row2.addWidget(self.resume_check)
        row2.addWidget(self.resume_edit, stretch=1)
        row2.addWidget(self.browse_resume_btn)
        row2.addWidget(self.preset_info_label, stretch=1)

        main_layout.addLayout(row2)

        # === Row 3: Trigger + Data Dir + Image Count ===
        row3 = QHBoxLayout()

        self.trigger_label = StrongBodyLabel("Trigger Word:")
        self.trigger_edit = LineEdit()
        self.trigger_edit.setText(config.DEFAULT_TRIGGER_WORD)

        self.data_label = StrongBodyLabel("Data Dir:")
        self.data_edit = LineEdit()
        self.data_edit.setText(config.TRAIN_DATA_DIR)
        self.browse_data_btn = PushButton("Browse")
        self.browse_data_btn.clicked.connect(self.browse_data)

        self.img_count_label = CaptionLabel("0 images")

        row3.addWidget(self.trigger_label)
        row3.addWidget(self.trigger_edit, stretch=1)
        row3.addWidget(self.data_label)
        row3.addWidget(self.data_edit, stretch=1)
        row3.addWidget(self.browse_data_btn)
        row3.addWidget(self.img_count_label)

        main_layout.addLayout(row3)

        # === Row 4: Parameters ===
        params_group = CardWidget()
        params_layout = QGridLayout(params_group)
        params_layout.setHorizontalSpacing(16)
        params_layout.setVerticalSpacing(8)

        # Resolution
        params_layout.addWidget(StrongBodyLabel("Resolution"), 0, 0)
        res_layout = QHBoxLayout()
        self.res_w_combo = ComboBox()
        self.res_w_combo.addItems(["512", "576", "640"])
        self.res_w_combo.setCurrentText("512")
        res_layout.addWidget(self.res_w_combo)
        res_layout.addWidget(CaptionLabel("x"))
        self.res_h_combo = ComboBox()
        self.res_h_combo.addItems(["768", "896", "1024"])
        self.res_h_combo.setCurrentText("768")
        res_layout.addWidget(self.res_h_combo)
        res_layout.addStretch()
        params_layout.addLayout(res_layout, 0, 1)

        # LoRA Dim
        params_layout.addWidget(StrongBodyLabel("LoRA Dim"), 1, 0)
        dim_layout = QHBoxLayout()
        self.dim_slider = Slider(Qt.Orientation.Horizontal)
        self.dim_slider.setMinimum(16)
        self.dim_slider.setMaximum(64)
        self.dim_slider.setValue(config.DEFAULT_NETWORK_DIM)
        self.dim_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.dim_slider.setTickInterval(8)
        self.dim_label = CaptionLabel(str(config.DEFAULT_NETWORK_DIM))
        self.dim_slider.valueChanged.connect(lambda v: self.dim_label.setText(str(v)))
        dim_layout.addWidget(self.dim_slider, stretch=1)
        dim_layout.addWidget(self.dim_label)
        params_layout.addLayout(dim_layout, 1, 1)

        # Steps
        params_layout.addWidget(StrongBodyLabel("Steps"), 2, 0)
        steps_layout = QHBoxLayout()
        self.steps_slider = Slider(Qt.Orientation.Horizontal)
        self.steps_slider.setMinimum(500)
        self.steps_slider.setMaximum(10000)
        self.steps_slider.setValue(config.DEFAULT_STEPS)
        self.steps_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.steps_slider.setTickInterval(500)
        self.steps_label = CaptionLabel(str(config.DEFAULT_STEPS))
        self.steps_slider.valueChanged.connect(lambda v: self.steps_label.setText(str(v)))
        steps_layout.addWidget(self.steps_slider, stretch=1)
        steps_layout.addWidget(self.steps_label)
        params_layout.addLayout(steps_layout, 2, 1)

        # Batch + LR
        params_layout.addWidget(StrongBodyLabel("Batch"), 3, 0)
        batch_layout = QHBoxLayout()
        self.batch_slider = Slider(Qt.Orientation.Horizontal)
        self.batch_slider.setMinimum(1)
        self.batch_slider.setMaximum(4)
        self.batch_slider.setValue(config.DEFAULT_BATCH_SIZE)
        self.batch_label = CaptionLabel(str(config.DEFAULT_BATCH_SIZE))
        self.batch_slider.valueChanged.connect(lambda v: self.batch_label.setText(str(v)))
        batch_layout.addWidget(self.batch_slider, stretch=1)
        batch_layout.addWidget(self.batch_label)
        params_layout.addLayout(batch_layout, 3, 1)

        # Learning rate
        params_layout.addWidget(StrongBodyLabel("Learning Rate"), 4, 0)
        self.lr_edit = LineEdit()
        self.lr_edit.setText(config.DEFAULT_LEARNING_RATE)
        params_layout.addWidget(self.lr_edit, 4, 1)

        main_layout.addWidget(params_group)

        # === Row 5: Loss Chart + Log ===
        chart_log_layout = QHBoxLayout()
        chart_log_layout.setSpacing(12)

        # Loss Chart
        chart_group = CardWidget()
        chart_layout = QVBoxLayout(chart_group)
        chart_layout.addWidget(StrongBodyLabel("Loss Curve (Real-time)"))
        self.loss_chart = LossChart()
        self.loss_chart.setMinimumHeight(250)
        chart_layout.addWidget(self.loss_chart)
        chart_log_layout.addWidget(chart_group, stretch=3)

        # Log
        log_group = CardWidget()
        log_layout = QVBoxLayout(log_group)
        log_layout.addWidget(StrongBodyLabel("Training Log"))
        self.log_viewer = LogViewer(max_lines=300)
        self.log_viewer.setMinimumHeight(250)
        log_layout.addWidget(self.log_viewer)
        chart_log_layout.addWidget(log_group, stretch=2)

        main_layout.addLayout(chart_log_layout)

        # === Row 6: Progress + Buttons ===
        bottom_layout = QHBoxLayout()

        self.progress_label = StrongBodyLabel("Progress:")
        self.progress_bar = ProgressBar()
        self.progress_value_label = CaptionLabel("0%")

        self.start_btn = PrimaryPushButton("Start Training")
        self.start_btn.clicked.connect(self.start_training)

        self.stop_btn = PushButton("Stop Training")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_training)

        bottom_layout.addWidget(self.progress_label)
        bottom_layout.addWidget(self.progress_bar, stretch=1)
        bottom_layout.addWidget(self.progress_value_label)
        bottom_layout.addWidget(self.start_btn)
        bottom_layout.addWidget(self.stop_btn)

        main_layout.addLayout(bottom_layout)

        # Initial image count
        self.update_image_count()

    def on_preset_changed(self, preset_name: str):
        if not preset_name:
            return
        params = presets_module.get_preset_params(preset_name)
        trigger = presets_module.get_preset_trigger(preset_name)
        info = presets_module.get_preset_info(preset_name)

        self.preset_info_label.setText(info)

        if "network_dim" in params:
            self.dim_slider.setValue(params["network_dim"])
        if "max_train_steps" in params:
            self.steps_slider.setValue(params["max_train_steps"])
        if "resolution_w" in params:
            self.res_w_combo.setCurrentText(str(params["resolution_w"]))
        if "resolution_h" in params:
            self.res_h_combo.setCurrentText(str(params["resolution_h"]))
        if "learning_rate" in params:
            self.lr_edit.setText(params["learning_rate"])
        if "batch_size" in params:
            self.batch_slider.setValue(params["batch_size"])

        self.trigger_edit.setText(trigger)

    def browse_model(self):
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Base Model",
            config.MODEL_DIR,
            "Model Files (*.safetensors *.ckpt *.pth);;All Files (*)"
        )
        if file_path:
            self.model_edit.setText(file_path)

    def browse_resume(self):
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select LoRA to Resume",
            config.OUTPUT_DIR,
            "LoRA Files (*.safetensors);;All Files (*)"
        )
        if file_path:
            self.resume_edit.setText(file_path)

    def browse_data(self):
        from PySide6.QtWidgets import QFileDialog
        dir_path = QFileDialog.getExistingDirectory(self, "Select Data Directory")
        if dir_path:
            self.data_edit.setText(dir_path)
            self.update_image_count()

    def update_image_count(self):
        data_dir = self.data_edit.text()
        count = train_engine.count_images(data_dir)
        self.img_count_label.setText(f"{count} images")

    def start_training(self):
        base_model = self.model_edit.text()
        trigger_word = self.trigger_edit.text()
        data_dir = self.data_edit.text()

        if not base_model or not os.path.exists(base_model):
            self.log_viewer.append_log("Error: Please select a valid base model")
            return

        if not data_dir or not os.path.isdir(data_dir):
            self.log_viewer.append_log("Error: Invalid data directory")
            return

        try:
            lr = float(self.lr_edit.text())
        except:
            lr = 1e-4

        output_name = f"lora_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        resume_training = self.resume_check.isChecked()
        resume_lora = self.resume_edit.text() if resume_training else ""

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.loss_chart.clear()

        self.worker = TrainWorker(
            base_model=base_model,
            trigger_word=trigger_word,
            train_data_dir=data_dir,
            output_name=output_name,
            network_dim=self.dim_slider.value(),
            steps=self.steps_slider.value(),
            resolution_w=int(self.res_w_combo.currentText()),
            resolution_h=int(self.res_h_combo.currentText()),
            batch_size=self.batch_slider.value(),
            learning_rate=lr,
            resume_training=resume_training,
            resume_lora_path=resume_lora
        )

        self.worker.progress.connect(self.on_progress)
        self.worker.log_line.connect(self.on_log)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    @Slot(int, int, float)
    def on_progress(self, progress: int, step: int, loss: float):
        self.progress_bar.setValue(progress)
        self.progress_value_label.setText(f"{progress}%")
        if loss > 0:
            self.loss_chart.update_loss(step, loss)

    @Slot(str)
    def on_log(self, line: str):
        self.log_viewer.append_log(line)

    @Slot(int, str)
    def on_finished(self, code: int, msg: str):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.log_viewer.append_log(msg)

    @Slot(str)
    def on_error(self, error: str):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.log_viewer.append_log(f"Error: {error}")

    def stop_training(self):
        if self.worker and self.worker.isRunning():
            train_engine.stop_training()
            self.log_viewer.append_log("Stopping training...")

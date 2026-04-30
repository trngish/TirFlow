"""
Generate page - Image generation UI with native diffusers
"""
import os
import sys

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel
)
from PySide6.QtCore import Qt, QThread, Signal, Slot

from qfluentwidgets import (
    LineEdit, PushButton, Slider, ComboBox,
    ProgressBar, PrimaryPushButton, CardWidget, StrongBodyLabel,
    CaptionLabel, setFont
)
from qfluentwidgets.common.icon import FluentIcon

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config
import generate as generate_module
import train_engine
from ui.widgets.log_viewer import LogViewer


class GenerateWorker(QThread):
    """Worker thread for image generation"""
    progress = Signal(float, str)
    finished = Signal(str, str)
    error = Signal(str)

    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs

    def run(self):
        try:
            img_path, msg = generate_module.generate_photo(
                **self.kwargs,
                progress_callback=lambda p, s: self.progress.emit(p, s)
            )
            self.finished.emit(img_path, msg)
        except Exception as e:
            self.error.emit(str(e))


class GeneratePage(QWidget):
    """Generate tab page"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.worker = None

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)

        # === Row 1: Model + LoRA Path ===
        row1 = QHBoxLayout()

        self.model_label = StrongBodyLabel("Base Model:")
        self.model_combo = ComboBox()
        base_models = train_engine.get_available_models()
        self.model_combo.addItems(base_models)

        self.lora_label = StrongBodyLabel("LoRA Path:")
        self.lora_edit = LineEdit()
        self.lora_edit.setText(config.OUTPUT_DIR)
        self.browse_lora_btn = PushButton("Browse")
        self.scan_lora_btn = PushButton("Scan")
        self.browse_lora_btn.clicked.connect(self.browse_lora)
        self.scan_lora_btn.clicked.connect(self.scan_lora)

        row1.addWidget(self.model_label)
        row1.addWidget(self.model_combo, stretch=2)
        row1.addWidget(self.lora_label)
        row1.addWidget(self.lora_edit, stretch=1)
        row1.addWidget(self.browse_lora_btn)
        row1.addWidget(self.scan_lora_btn)

        main_layout.addLayout(row1)

        # === Row 2: LoRA Selection + Weight ===
        row2 = QHBoxLayout()

        self.lora_select_label = StrongBodyLabel("LoRA File:")
        self.lora_select_combo = ComboBox()
        self.lora_weight_label = StrongBodyLabel("LoRA Weight:")
        self.weight_slider = Slider(Qt.Orientation.Horizontal)
        self.weight_slider.setMinimum(0)
        self.weight_slider.setMaximum(200)
        self.weight_slider.setValue(100)
        self.weight_value_label = CaptionLabel("1.0")
        self.weight_slider.valueChanged.connect(
            lambda v: self.weight_value_label.setText(f"{v/100:.1f}")
        )

        row2.addWidget(self.lora_select_label)
        row2.addWidget(self.lora_select_combo, stretch=1)
        row2.addWidget(self.lora_weight_label)
        row2.addWidget(self.weight_slider, stretch=1)
        row2.addWidget(self.weight_value_label)

        main_layout.addLayout(row2)

        # === Prompt Group ===
        prompt_group = CardWidget()
        prompt_layout = QGridLayout(prompt_group)

        prompt_layout.addWidget(StrongBodyLabel("Prompt:"), 0, 0)
        self.prompt_edit = LineEdit()
        self.prompt_edit.setPlaceholderText("1girl, portrait, fashion photo, elegant dress, studio lighting")
        prompt_layout.addWidget(self.prompt_edit, 0, 1, 1, 3)

        prompt_layout.addWidget(StrongBodyLabel("Negative Prompt:"), 1, 0)
        self.neg_prompt_edit = LineEdit()
        self.neg_prompt_edit.setPlaceholderText("ugly, deformed, blurry, low quality, cartoon, anime")
        prompt_layout.addWidget(self.neg_prompt_edit, 1, 1, 1, 3)

        main_layout.addWidget(prompt_group)

        # === Parameters Row ===
        params_layout = QHBoxLayout()

        # Resolution
        res_group = CardWidget()
        res_layout = QGridLayout(res_group)
        res_layout.addWidget(StrongBodyLabel("Width:"), 0, 0)
        self.width_combo = ComboBox()
        self.width_combo.addItems(["512", "576", "640", "704"])
        res_layout.addWidget(self.width_combo, 0, 1)
        res_layout.addWidget(StrongBodyLabel("Height:"), 0, 2)
        self.height_combo = ComboBox()
        self.height_combo.addItems(["768", "896", "1024", "1152"])
        self.height_combo.setCurrentText("768")
        res_layout.addWidget(self.height_combo, 0, 3)
        params_layout.addWidget(res_group)

        # Steps + CFG
        step_group = CardWidget()
        step_layout = QGridLayout(step_group)
        step_layout.addWidget(StrongBodyLabel("Steps:"), 0, 0)
        self.steps_slider = Slider(Qt.Orientation.Horizontal)
        self.steps_slider.setMinimum(20)
        self.steps_slider.setMaximum(50)
        self.steps_slider.setValue(30)
        self.steps_label = CaptionLabel("30")
        self.steps_slider.valueChanged.connect(
            lambda v: self.steps_label.setText(str(v))
        )
        step_layout.addWidget(self.steps_slider, 0, 1)
        step_layout.addWidget(self.steps_label, 0, 2)

        step_layout.addWidget(StrongBodyLabel("CFG:"), 0, 3)
        self.cfg_slider = Slider(Qt.Orientation.Horizontal)
        self.cfg_slider.setMinimum(50)
        self.cfg_slider.setMaximum(150)
        self.cfg_slider.setValue(75)
        self.cfg_label = CaptionLabel("7.5")
        self.cfg_slider.valueChanged.connect(
            lambda v: self.cfg_label.setText(f"{v/10:.1f}")
        )
        step_layout.addWidget(self.cfg_slider, 0, 4)
        step_layout.addWidget(self.cfg_label, 0, 5)
        params_layout.addWidget(step_group)

        # Seed
        seed_group = CardWidget()
        seed_layout = QGridLayout(seed_group)
        seed_layout.addWidget(StrongBodyLabel("Seed (-1=random):"), 0, 0)
        self.seed_edit = LineEdit()
        self.seed_edit.setText("-1")
        seed_layout.addWidget(self.seed_edit, 0, 1)
        params_layout.addWidget(seed_group)

        main_layout.addLayout(params_layout)

        # === Generate Button ===
        self.generate_btn = PrimaryPushButton("Generate Image")
        self.generate_btn.clicked.connect(self.generate)
        main_layout.addWidget(self.generate_btn)

        # === Progress + Output ===
        output_layout = QHBoxLayout()

        # Image preview
        self.image_label = StrongBodyLabel("Preview:")
        self.preview_group = CardWidget()
        preview_layout = QVBoxLayout(self.preview_group)
        self.image_display = QLabel()
        self.image_display.setMinimumSize(300, 300)
        self.image_display.setStyleSheet("""
            QLabel {
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                background-color: #2b2b2b;
            }
        """)
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.image_display)
        output_layout.addWidget(self.preview_group, stretch=2)

        # Status
        status_group = CardWidget()
        status_layout = QVBoxLayout(status_group)
        status_layout.addWidget(StrongBodyLabel("Status:"))
        self.status_label = CaptionLabel("Ready")
        status_layout.addWidget(self.status_label)

        status_layout.addWidget(StrongBodyLabel("Progress:"))
        self.gen_progress_bar = ProgressBar()
        status_layout.addWidget(self.gen_progress_bar)

        self.gen_progress_label = CaptionLabel("")
        status_layout.addWidget(self.gen_progress_label)

        status_layout.addStretch()
        output_layout.addWidget(status_group, stretch=1)

        main_layout.addLayout(output_layout)

    def browse_lora(self):
        from PySide6.QtWidgets import QFileDialog
        dir_path = QFileDialog.getExistingDirectory(self, "Select LoRA Directory")
        if dir_path:
            self.lora_edit.setText(dir_path)
            self.scan_lora()

    def scan_lora(self):
        dir_path = self.lora_edit.text()
        files = generate_module.scan_lora_directory(dir_path)
        self.lora_select_combo.clear()
        if files:
            self.lora_select_combo.addItems(files)
        else:
            self.lora_select_combo.addItem("No .safetensors files found")

    def generate(self):
        base_model = self.model_combo.currentText()
        lora_path = self.lora_select_combo.currentText()
        lora_weight = self.weight_slider.value() / 100.0
        prompt = self.prompt_edit.text()
        negative_prompt = self.neg_prompt_edit.text()

        if not prompt:
            self.status_label.setText("Please enter a prompt")
            return

        try:
            seed = int(self.seed_edit.text())
        except:
            seed = -1

        self.generate_btn.setEnabled(False)
        self.status_label.setText("Generating...")
        self.gen_progress_bar.setValue(0)

        self.worker = GenerateWorker(
            base_model=base_model,
            lora_path=lora_path,
            lora_weight=lora_weight,
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=int(self.width_combo.currentText()),
            height=int(self.height_combo.currentText()),
            steps=self.steps_slider.value(),
            cfg_scale=self.cfg_slider.value() / 10.0,
            seed=seed,
            lora_selected=lora_path if lora_path and ".safetensors" in lora_path else None
        )

        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    @Slot(float, str)
    def on_progress(self, progress: float, status: str):
        self.gen_progress_bar.setValue(int(progress * 100))
        self.gen_progress_label.setText(status)

    @Slot(str, str)
    def on_finished(self, img_path: str, msg: str):
        self.status_label.setText(msg)
        self.generate_btn.setEnabled(True)
        self.gen_progress_bar.setValue(100)

        if img_path and os.path.exists(img_path):
            pixmap = Image.open(img_path)
            # Scale to fit
            pixmap = pixmap.resize((300, 300), Image.LANCZOS)
            from PIL.ImageQt import ImageQt
            from PySide6.QtGui import QPixmap
            qt_img = ImageQt(pixmap)
            self.image_display.setPixmap(QPixmap.fromImage(qt_img))

    @Slot(str)
    def on_error(self, error: str):
        self.status_label.setText(f"Error: {error}")
        self.generate_btn.setEnabled(True)

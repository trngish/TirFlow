"""
Generate page - Image generation UI with native diffusers
"""
import os
import sys

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QDialog, QVBoxLayout as QVBoxLayout2, QLabel as QLabel2
)
from PySide6.QtCore import Qt, QThread, Signal, Slot

from qfluentwidgets import (
    LineEdit, PushButton, Slider, ComboBox,
    ProgressBar, PrimaryPushButton, CardWidget, StrongBodyLabel,
    CaptionLabel, setFont
)
from qfluentwidgets.common.icon import FluentIcon

from PIL import Image
from PySide6.QtGui import QPixmap

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config
import generate as generate_module
import train_engine
from ui.widgets.log_viewer import LogViewer
import i18n


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


class ImagePreviewDialog(QDialog):
    """Dialog for viewing full-size image with size info"""

    def __init__(self, img_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Preview")
        self.setMinimumSize(400, 400)
        self.setModal(True)

        layout = QVBoxLayout2(self)

        # Show image dimensions
        with Image.open(img_path) as img:
            size_text = f"{img.size[0]} x {img.size[1]}"
        self.size_label = QLabel2(f"Size: {size_text}")
        layout.addWidget(self.size_label)

        # Display full image (scroll area for large images)
        from PySide6.QtWidgets import QScrollArea, QSizePolicy
        scroll = QScrollArea()
        scroll.setWidgetResizable(False)
        self.img_label = QLabel2()
        pixmap = QPixmap(img_path)
        self.img_label.setPixmap(pixmap)
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.img_label)
        layout.addWidget(scroll)

        # Info label
        self.info_label = QLabel2(f"Path: {img_path}")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)


class GeneratePage(QWidget):
    """Generate tab page"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.worker = None
        self.last_image_path = None
        self._orig_pixmap = None

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)

        # === Row 1: Model Path + LoRA Path ===
        row1 = QHBoxLayout()

        self.model_label = StrongBodyLabel(i18n.T("base_model") + ":")
        self.model_edit = LineEdit()
        self.model_edit.setPlaceholderText(i18n.T("base_model_placeholder"))
        self.browse_model_btn = PushButton(i18n.T("browse"))
        self.browse_model_btn.clicked.connect(self.browse_model)

        self.lora_label = StrongBodyLabel(i18n.T("lora_path") + ":")
        self.lora_edit = LineEdit()
        self.lora_edit.setText(config.OUTPUT_DIR)
        self.browse_lora_btn = PushButton(i18n.T("browse"))
        self.scan_lora_btn = PushButton(i18n.T("scan"))
        self.browse_lora_btn.clicked.connect(self.browse_lora)
        self.scan_lora_btn.clicked.connect(self.scan_lora)

        row1.addWidget(self.model_label)
        row1.addWidget(self.model_edit, stretch=2)
        row1.addWidget(self.browse_model_btn)
        row1.addWidget(self.lora_label)
        row1.addWidget(self.lora_edit, stretch=1)
        row1.addWidget(self.browse_lora_btn)
        row1.addWidget(self.scan_lora_btn)

        main_layout.addLayout(row1)

        # === Row 2: LoRA Selection + Weight ===
        row2 = QHBoxLayout()

        self.lora_select_label = StrongBodyLabel(i18n.T("lora_file") + ":")
        self.lora_select_combo = ComboBox()
        self.lora_weight_label = StrongBodyLabel(i18n.T("lora_weight") + ":")
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

        self.prompt_label = StrongBodyLabel(i18n.T("prompt") + ":")
        prompt_layout.addWidget(self.prompt_label, 0, 0)
        self.prompt_edit = LineEdit()
        self.prompt_edit.setPlaceholderText(i18n.T("prompt_placeholder"))
        prompt_layout.addWidget(self.prompt_edit, 0, 1, 1, 3)

        self.neg_prompt_label = StrongBodyLabel(i18n.T("neg_prompt") + ":")
        prompt_layout.addWidget(self.neg_prompt_label, 1, 0)
        self.neg_prompt_edit = LineEdit()
        self.neg_prompt_edit.setPlaceholderText(i18n.T("neg_prompt_placeholder"))
        prompt_layout.addWidget(self.neg_prompt_edit, 1, 1, 1, 3)

        main_layout.addWidget(prompt_group)

        # === Parameters Row ===
        params_layout = QHBoxLayout()

        # Resolution
        res_group = CardWidget()
        res_layout = QGridLayout(res_group)
        self.width_label = StrongBodyLabel(i18n.T("width") + ":")
        res_layout.addWidget(self.width_label, 0, 0)
        self.width_combo = ComboBox()
        self.width_combo.addItems(["512", "576", "640", "704"])
        res_layout.addWidget(self.width_combo, 0, 1)
        self.height_label = StrongBodyLabel(i18n.T("height") + ":")
        res_layout.addWidget(self.height_label, 0, 2)
        self.height_combo = ComboBox()
        self.height_combo.addItems(["768", "896", "1024", "1152"])
        self.height_combo.setCurrentText("768")
        res_layout.addWidget(self.height_combo, 0, 3)
        params_layout.addWidget(res_group)

        # Steps + CFG
        step_group = CardWidget()
        step_layout = QGridLayout(step_group)
        self.steps_label = StrongBodyLabel(i18n.T("steps") + ":")
        step_layout.addWidget(self.steps_label, 0, 0)
        self.steps_slider = Slider(Qt.Orientation.Horizontal)
        self.steps_slider.setMinimum(20)
        self.steps_slider.setMaximum(50)
        self.steps_slider.setValue(30)
        self.steps_value_label = CaptionLabel("30")
        self.steps_slider.valueChanged.connect(
            lambda v: self.steps_value_label.setText(str(v))
        )
        step_layout.addWidget(self.steps_slider, 0, 1)
        step_layout.addWidget(self.steps_value_label, 0, 2)

        self.cfg_label = StrongBodyLabel(i18n.T("cfg") + ":")
        step_layout.addWidget(self.cfg_label, 0, 3)
        self.cfg_slider = Slider(Qt.Orientation.Horizontal)
        self.cfg_slider.setMinimum(50)
        self.cfg_slider.setMaximum(150)
        self.cfg_slider.setValue(75)
        self.cfg_value_label = CaptionLabel("7.5")
        self.cfg_slider.valueChanged.connect(
            lambda v: self.cfg_value_label.setText(f"{v/10:.1f}")
        )
        step_layout.addWidget(self.cfg_slider, 0, 4)
        step_layout.addWidget(self.cfg_value_label, 0, 5)
        params_layout.addWidget(step_group)

        # Seed
        seed_group = CardWidget()
        seed_layout = QGridLayout(seed_group)
        self.seed_label = StrongBodyLabel(i18n.T("seed_random") + ":")
        seed_layout.addWidget(self.seed_label, 0, 0)
        self.seed_edit = LineEdit()
        self.seed_edit.setText("-1")
        seed_layout.addWidget(self.seed_edit, 0, 1)
        params_layout.addWidget(seed_group)

        main_layout.addLayout(params_layout)

        # === Generate Button ===
        self.generate_btn = PrimaryPushButton(i18n.T("generate_image"))
        self.generate_btn.clicked.connect(self.generate)
        main_layout.addWidget(self.generate_btn)

        # === Progress + Output ===
        output_layout = QHBoxLayout()

        # Image preview
        self.preview_label = StrongBodyLabel(i18n.T("preview") + ":")
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
        self.image_display.mouseDoubleClickEvent = self.on_image_double_click
        preview_layout.addWidget(self.image_display)
        output_layout.addWidget(self.preview_group, stretch=2)

        # Status
        status_group = CardWidget()
        status_layout = QVBoxLayout(status_group)
        self.status_title = StrongBodyLabel(i18n.T("status") + ":")
        status_layout.addWidget(self.status_title)
        self.status_label = CaptionLabel(i18n.T("ready"))
        status_layout.addWidget(self.status_label)

        self.progress_title = StrongBodyLabel(i18n.T("progress") + ":")
        status_layout.addWidget(self.progress_title)
        self.gen_progress_bar = ProgressBar()
        status_layout.addWidget(self.gen_progress_bar)

        self.gen_progress_label = CaptionLabel("")
        status_layout.addWidget(self.gen_progress_label)

        status_layout.addStretch()
        output_layout.addWidget(status_group, stretch=1)

        main_layout.addLayout(output_layout)

        # Connect language change signal
        i18n.get_language_manager().language_changed.connect(self.retranslate)

    def retranslate(self):
        """Retranslate all UI text"""
        self.model_label.setText(i18n.T("base_model") + ":")
        self.model_edit.setPlaceholderText(i18n.T("base_model_placeholder"))
        self.browse_model_btn.setText(i18n.T("browse"))
        self.lora_label.setText(i18n.T("lora_path") + ":")
        self.browse_lora_btn.setText(i18n.T("browse"))
        self.scan_lora_btn.setText(i18n.T("scan"))
        self.lora_select_label.setText(i18n.T("lora_file") + ":")
        self.lora_weight_label.setText(i18n.T("lora_weight") + ":")
        self.prompt_label.setText(i18n.T("prompt") + ":")
        self.prompt_edit.setPlaceholderText(i18n.T("prompt_placeholder"))
        self.neg_prompt_label.setText(i18n.T("neg_prompt") + ":")
        self.neg_prompt_edit.setPlaceholderText(i18n.T("neg_prompt_placeholder"))
        self.width_label.setText(i18n.T("width") + ":")
        self.height_label.setText(i18n.T("height") + ":")
        self.steps_label.setText(i18n.T("steps") + ":")
        self.cfg_label.setText(i18n.T("cfg") + ":")
        self.seed_label.setText(i18n.T("seed_random") + ":")
        self.generate_btn.setText(i18n.T("generate_image"))
        self.preview_label.setText(i18n.T("preview") + ":")
        self.status_title.setText(i18n.T("status") + ":")
        self.progress_title.setText(i18n.T("progress") + ":")
        self.status_label.setText(i18n.T("ready"))

    def browse_lora(self):
        from PySide6.QtWidgets import QFileDialog
        dir_path = QFileDialog.getExistingDirectory(self, i18n.T("lora_path"))
        if dir_path:
            self.lora_edit.setText(dir_path)
            self.scan_lora()

    def browse_model(self):
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, i18n.T("base_model"),
            config.MODEL_DIR,
            "Model Files (*.safetensors *.ckpt *.pth);;All Files (*)"
        )
        if file_path:
            self.model_edit.setText(file_path)

    def scan_lora(self):
        dir_path = self.lora_edit.text()
        files = generate_module.scan_lora_directory(dir_path)
        self.lora_select_combo.clear()
        if files:
            self.lora_select_combo.addItems(files)
        else:
            self.lora_select_combo.addItem(i18n.T("no_safetensors"))

    def generate(self):
        base_model = self.model_edit.text()
        lora_path = self.lora_select_combo.currentText()
        lora_weight = self.weight_slider.value() / 100.0
        prompt = self.prompt_edit.text()
        negative_prompt = self.neg_prompt_edit.text()

        if not prompt:
            self.status_label.setText(i18n.T("prompt_placeholder"))
            return

        try:
            seed = int(self.seed_edit.text())
        except:
            seed = -1

        self.generate_btn.setEnabled(False)
        self.status_label.setText(i18n.T("ready") + "...")
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
            self.last_image_path = img_path
            from PIL.ImageQt import ImageQt
            pixmap = Image.open(img_path)
            orig_w, orig_h = pixmap.size

            # Scale to fit 300x300 only if image exceeds that size (don't upscale small images)
            max_size = 300
            if orig_w > max_size or orig_h > max_size:
                if orig_w > orig_h:
                    new_w = max_size
                    new_h = int(orig_h * (max_size / orig_w))
                else:
                    new_h = max_size
                    new_w = int(orig_w * (max_size / orig_h))
                scaled = pixmap.resize((new_w, new_h), Image.LANCZOS)
                qt_img = ImageQt(scaled)
            else:
                qt_img = ImageQt(pixmap)
            self.image_display.setPixmap(QPixmap.fromImage(qt_img))
            if orig_w <= max_size and orig_h <= max_size:
                self.image_display.setFixedSize(orig_w, orig_h)
            else:
                self.image_display.setFixedSize(new_w, new_h)
            # Store original for double-click viewing
            self._orig_pixmap = QPixmap.fromImage(ImageQt(pixmap))
            self.image_display.setCursor(Qt.CursorShape.PointingHandCursor)

    def on_image_double_click(self, event):
        """Open full-size image preview dialog"""
        if self.last_image_path and os.path.exists(self.last_image_path):
            dialog = ImagePreviewDialog(self.last_image_path, self)
            dialog.exec()

    @Slot(str)
    def on_error(self, error: str):
        self.status_label.setText("Error: " + error)
        self.generate_btn.setEnabled(True)

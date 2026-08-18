from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QListWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QSlider,
    QHBoxLayout
)


class AIDashboard(QWidget):

    def __init__(self):
        super().__init__()

        self.setMinimumWidth(260)

        main_layout = QVBoxLayout(self)

        # ==================================================
        # AI Information
        # ==================================================

        info_group = QGroupBox("AI Dashboard")

        info_layout = QFormLayout()

        # Basic Information

        self.model_label = QLabel("YOLO11n")
        self.source_label = QLabel("None")
        self.status_label = QLabel("Idle")

        # New Information

        self.device_label = QLabel("CPU")

        self.resolution_label = QLabel("-")

        self.inference_label = QLabel("0 ms")

        self.fps_label = QLabel("0")

        self.object_count_label = QLabel("0")

        # ==================================================
        # Confidence Slider
        # ==================================================

        self.confidence_slider = QSlider(Qt.Horizontal)

        self.confidence_slider.setRange(10, 100)

        self.confidence_slider.setValue(25)

        self.confidence_label = QLabel("0.25")

        self.confidence_slider.valueChanged.connect(
            self.update_confidence_label
        )

        confidence_layout = QHBoxLayout()

        confidence_layout.addWidget(
            self.confidence_slider
        )

        confidence_layout.addWidget(
            self.confidence_label
        )

        # ==================================================
        # OCR Confidence
        # ==================================================

        self.ocr_confidence_slider = QSlider(Qt.Horizontal)

        self.ocr_confidence_slider.setRange(10, 100)

        self.ocr_confidence_slider.setValue(50)

        self.ocr_confidence_label = QLabel("0.50")

        self.ocr_confidence_slider.valueChanged.connect(
            self.update_ocr_confidence_label
        )

        ocr_layout = QHBoxLayout()

        ocr_layout.addWidget(
            self.ocr_confidence_slider
        )

        ocr_layout.addWidget(
            self.ocr_confidence_label
        )

        # ==================================================
        # Information Layout
        # ==================================================

        info_layout.addRow("Model :", self.model_label)

        info_layout.addRow("Source :", self.source_label)

        info_layout.addRow("Status :", self.status_label)

        info_layout.addRow("Device :", self.device_label)

        info_layout.addRow(
            "Resolution :",
            self.resolution_label
        )

        info_layout.addRow(
            "Inference :",
            self.inference_label
        )

        info_layout.addRow("FPS :", self.fps_label)

        info_layout.addRow(
            "Objects :",
            self.object_count_label
        )

        info_layout.addRow(
            "Confidence :",
            confidence_layout
        )

        info_layout.addRow(
            "OCR Confidence :",
            ocr_layout
        )

        info_group.setLayout(info_layout)

        # ==================================================
        # Detected Objects
        # ==================================================

        object_group = QGroupBox(
            "Detected Objects"
        )

        object_layout = QVBoxLayout()

        self.object_list = QListWidget()

        object_layout.addWidget(
            self.object_list
        )

        object_group.setLayout(
            object_layout
        )

        # ==================================================
        # Main Layout
        # ==================================================

        main_layout.addWidget(info_group)

        main_layout.addWidget(object_group)

        main_layout.addStretch()

    # ==================================================
    # Update Methods
    # ==================================================

    def update_model(self, model):

        self.model_label.setText(model)

    def update_source(self, source):

        self.source_label.setText(source)

    def update_status(self, status):

        self.status_label.setText(status)

    def update_device(self, device):

        self.device_label.setText(device)

    def update_resolution(self, width, height):

        self.resolution_label.setText(
            f"{width} × {height}"
        )

    def update_inference_time(self, time_ms):

        self.inference_label.setText(
            f"{time_ms:.1f} ms"
        )

    def update_fps(self, fps):

        self.fps_label.setText(
            f"{fps:.1f}"
        )

    def update_object_count(self, count):

        self.object_count_label.setText(
            str(count)
        )

    def update_objects(self, detections):

        self.object_list.clear()

        if not detections:

            self.object_list.addItem(
                "No objects detected"
            )

            return

        counts = {}

        for obj in detections:

            name = obj["class"]

            counts[name] = counts.get(name, 0) + 1

        for name, count in counts.items():

            self.object_list.addItem(
                f"{name} : {count}"
            )

    # ==================================================
    # Confidence
    # ==================================================

    def get_confidence(self):

        return self.confidence_slider.value() / 100

    def update_confidence_label(self):

        value = self.confidence_slider.value() / 100

        self.confidence_label.setText(
            f"{value:.2f}"
        )

    # ==================================================
    # OCR Confidence
    # ==================================================

    def get_ocr_confidence(self):

        return self.ocr_confidence_slider.value() / 100

    def update_ocr_confidence_label(self):

        value = self.ocr_confidence_slider.value() / 100

        self.ocr_confidence_label.setText(
            f"{value:.2f}"
        )

    # ==================================================
    # Reset
    # ==================================================

    def reset(self):

        self.update_source("None")

        self.update_status("Idle")

        self.update_device("CPU")

        self.update_resolution("-", "-")

        self.update_inference_time(0)

        self.update_fps(0)

        self.update_object_count(0)

        self.object_list.clear()

        self.object_list.addItem(
            "No objects detected"
        )
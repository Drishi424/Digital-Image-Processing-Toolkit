from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QListWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QSlider,
    QHBoxLayout,
    QComboBox,
    QPushButton,
    QTabWidget,
)
import time


class AIDashboard(QWidget):
    """
    AI Control and Analytics Dashboard.
    Displays model selector, performance stats, detected objects breakdown,
    confidence sliders, detection history, and export capabilities.
    """

    model_changed = Signal(str)
    save_image_requested = Signal()
    export_metadata_requested = Signal()

    MAX_HISTORY = 100

    def __init__(self):
        super().__init__()

        self.setMinimumWidth(280)
        self.history_records = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Tab Widget to separate Dashboard and History cleanly
        self.tabs = QTabWidget()

        # ==================================================
        # TAB 1: AI DASHBOARD & CONTROLS
        # ==================================================
        dashboard_tab = QWidget()
        dash_layout = QVBoxLayout(dashboard_tab)

        info_group = QGroupBox("AI Vision Controls & Analytics")
        info_layout = QFormLayout()

        # Model Selector
        self.model_combo = QComboBox()
        self.model_combo.addItems(["YOLO11n", "Drone Detector"])
        self.model_combo.currentTextChanged.connect(self._on_model_combo_changed)

        # Info Labels
        self.source_label = QLabel("None")
        self.status_label = QLabel("Idle")
        self.device_label = QLabel("CPU")
        self.resolution_label = QLabel("-")
        self.inference_label = QLabel("0.0 ms")
        self.fps_label = QLabel("0.0")
        self.object_count_label = QLabel("0")
        self.avg_conf_label = QLabel("0.0%")
        self.max_conf_label = QLabel("0.0%")

        # Confidence Sliders
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setRange(10, 100)
        self.confidence_slider.setValue(25)
        self.confidence_label = QLabel("0.25")
        self.confidence_slider.valueChanged.connect(self.update_confidence_label)

        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(self.confidence_slider)
        confidence_layout.addWidget(self.confidence_label)

        self.ocr_confidence_slider = QSlider(Qt.Horizontal)
        self.ocr_confidence_slider.setRange(10, 100)
        self.ocr_confidence_slider.setValue(50)
        self.ocr_confidence_label = QLabel("0.50")
        self.ocr_confidence_slider.valueChanged.connect(self.update_ocr_confidence_label)

        ocr_layout = QHBoxLayout()
        ocr_layout.addWidget(self.ocr_confidence_slider)
        ocr_layout.addWidget(self.ocr_confidence_label)

        # Build Form Layout
        info_layout.addRow("AI Model :", self.model_combo)
        info_layout.addRow("Source :", self.source_label)
        info_layout.addRow("Status :", self.status_label)
        info_layout.addRow("Device :", self.device_label)
        info_layout.addRow("Resolution :", self.resolution_label)
        info_layout.addRow("Inference :", self.inference_label)
        info_layout.addRow("FPS :", self.fps_label)
        info_layout.addRow("Objects Count :", self.object_count_label)
        info_layout.addRow("Avg Confidence :", self.avg_conf_label)
        info_layout.addRow("Max Confidence :", self.max_conf_label)
        info_layout.addRow("YOLO Conf :", confidence_layout)
        info_layout.addRow("OCR Conf :", ocr_layout)

        info_group.setLayout(info_layout)
        dash_layout.addWidget(info_group)

        # Detected Objects List
        object_group = QGroupBox("Detected Objects")
        object_layout = QVBoxLayout()
        self.object_list = QListWidget()
        self.object_list.setMaximumHeight(150)
        object_layout.addWidget(self.object_list)
        object_group.setLayout(object_layout)
        dash_layout.addWidget(object_group)

        # Export Action Buttons
        export_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 Save Result")
        self.save_btn.clicked.connect(self.save_image_requested.emit)
        self.export_btn = QPushButton("📊 Export Data")
        self.export_btn.clicked.connect(self.export_metadata_requested.emit)

        export_layout.addWidget(self.save_btn)
        export_layout.addWidget(self.export_btn)
        dash_layout.addLayout(export_layout)

        # ==================================================
        # TAB 2: DETECTION HISTORY
        # ==================================================
        history_tab = QWidget()
        hist_layout = QVBoxLayout(history_tab)

        self.history_list = QListWidget()
        hist_layout.addWidget(self.history_list)

        clear_hist_btn = QPushButton("🧹 Clear History")
        clear_hist_btn.clicked.connect(self.clear_history)
        hist_layout.addWidget(clear_hist_btn)

        # Add tabs
        self.tabs.addTab(dashboard_tab, "Dashboard")
        self.tabs.addTab(history_tab, "History")

        main_layout.addWidget(self.tabs)

        self.reset()

    # ==================================================
    # Event Handlers & Signals
    # ==================================================

    def _on_model_combo_changed(self, model_name: str):
        self.model_changed.emit(model_name)

    def set_selected_model_name(self, model_name: str):
        index = self.model_combo.findText(model_name)
        if index >= 0:
            self.model_combo.blockSignals(True)
            self.model_combo.setCurrentIndex(index)
            self.model_combo.blockSignals(False)

    def get_selected_model_name(self) -> str:
        return self.model_combo.currentText()

    # ==================================================
    # Update Methods
    # ==================================================

    def update_model(self, model_name: str):
        self.set_selected_model_name(model_name)

    def update_source(self, source: str):
        self.source_label.setText(source)

    def update_status(self, status: str):
        self.status_label.setText(status)

    def update_device(self, device: str):
        self.device_label.setText(device)

    def update_resolution(self, width: int, height: int):
        self.resolution_label.setText(f"{width} × {height}")

    def update_inference_time(self, time_ms: float):
        self.inference_label.setText(f"{time_ms:.1f} ms")

    def update_fps(self, fps: float):
        self.fps_label.setText(f"{fps:.1f}")

    def update_object_count(self, count: int):
        self.object_count_label.setText(str(count))

    def update_objects(self, detections: list):
        self.object_list.clear()

        if not detections:
            self.object_list.addItem("No objects detected")
            self.avg_conf_label.setText("0.0%")
            self.max_conf_label.setText("0.0%")
            return

        counts = {}
        confidences = []

        for obj in detections:
            name = obj.get("class", "unknown")
            counts[name] = counts.get(name, 0) + 1
            if "confidence" in obj:
                confidences.append(obj["confidence"])

        for name, count in counts.items():
            self.object_list.addItem(f"{name} : {count}")

        if confidences:
            avg_c = sum(confidences) / len(confidences)
            max_c = max(confidences)
            self.avg_conf_label.setText(f"{avg_c:.1f}%")
            self.max_conf_label.setText(f"{max_c:.1f}%")
        else:
            self.avg_conf_label.setText("N/A")
            self.max_conf_label.setText("N/A")

        self.add_history_entry(counts)

    def add_history_entry(self, counts: dict):
        if not counts:
            return

        timestamp = time.strftime("%H:%M:%S")
        summary_parts = [f"{cls} x {cnt}" for cls, cnt in counts.items()]
        summary = ", ".join(summary_parts)
        entry_text = f"[{timestamp}] {summary}"

        self.history_records.insert(0, entry_text)
        if len(self.history_records) > self.MAX_HISTORY:
            self.history_records.pop()

        self.history_list.clear()
        for rec in self.history_records:
            self.history_list.addItem(rec)

    def clear_history(self):
        self.history_records.clear()
        self.history_list.clear()

    # ==================================================
    # Confidence Sliders
    # ==================================================

    def get_confidence(self) -> float:
        return self.confidence_slider.value() / 100.0

    def update_confidence_label(self):
        val = self.get_confidence()
        self.confidence_label.setText(f"{val:.2f}")

    def get_ocr_confidence(self) -> float:
        return self.ocr_confidence_slider.value() / 100.0

    def update_ocr_confidence_label(self):
        val = self.get_ocr_confidence()
        self.ocr_confidence_label.setText(f"{val:.2f}")

    # ==================================================
    # Reset
    # ==================================================

    def reset(self):
        self.update_source("None")
        self.update_status("Idle")
        self.update_device("CPU")
        self.update_resolution(0, 0)
        self.update_inference_time(0.0)
        self.update_fps(0.0)
        self.update_object_count(0)
        self.avg_conf_label.setText("0.0%")
        self.max_conf_label.setText("0.0%")
        self.object_list.clear()
        self.object_list.addItem("No objects detected")
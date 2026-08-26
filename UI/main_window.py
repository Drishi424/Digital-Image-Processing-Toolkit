from PySide6.QtCore import Qt, QSize, QSettings
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QSplitter,
    QStatusBar,
    QToolBar,
    QWidget,
    QVBoxLayout,
    QStackedWidget,
    QMessageBox
)
from PySide6.QtGui import QAction, QIcon, QKeySequence, QDragEnterEvent, QDropEvent

import cv2
import torch
import os
import time
import json
import csv
from functools import partial

from UI.sidebar import Sidebar
from UI.image_viewer import ImageViewer
from UI.property_panel import PropertyPanel
from UI.compression_report import CompressionReport
from UI.comparison_viewer import ComparisonViewer
from UI.histogram_viewer import HistogramViewer
from UI.statistics_panel import StatisticsPanel
from UI.about_dialog import AboutDialog
from UI.welcome_screen import WelcomeScreen
from UI.ai_dashboard import AIDashboard
from UI.dialogs.ocr_result_dialog import OCRResultDialog

from Core.image_manager import ImageManager
from Core.processor import Processor
from Core.utils import resource_path

from Modules.ai.model_manager import ModelManager
from Modules.ai.detector import YOLODetector
from Modules.ai.stream_detector import StreamDetector
from Modules.ai.ocr import OCRDetector
from Modules.ai.workers import ModelLoadWorker, ImageDetectionWorker, OCRWorker


class MainWindow(QMainWindow):

    SUPPORTED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}
    SUPPORTED_VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv"}

    def __init__(self):
        super().__init__()

        # Ensure output directory exists
        os.makedirs(resource_path("Images/output"), exist_ok=True)

        # Core Managers & AI Layer
        self.image_manager = ImageManager(max_stack_size=20)
        self.processor = Processor()
        self.model_manager = ModelManager()

        self.detector = YOLODetector(self.model_manager)
        self.ocr_detector = OCRDetector()

        # UI Components
        self.comparison = ComparisonViewer()
        self.histogram = HistogramViewer()
        self.statistics = StatisticsPanel()
        self.ai_dashboard = AIDashboard()
        self.compression_report = CompressionReport()
        self.about = AboutDialog()
        self.ocr_dialog = OCRResultDialog(self)
        self.welcome = WelcomeScreen()

        self.algorithm_map = self.create_algorithm_map()
        self.setWindowIcon(QIcon(resource_path("Assets/icons/app_icon.ico")))

        self.setWindowTitle("DIP Studio")
        self.resize(1600, 900)
        self.setMinimumSize(1200, 700)

        self.recent_files = []
        self.max_recent_files = 10

        self.last_detection_results = None
        self.active_worker = None

        self.create_menu()
        self.create_toolbar()
        self.create_statusbar()
        self.create_ui()

        self.setup_connections()

        self.settings = QSettings("JECRC", "DigitalImageProcessingToolkit")
        self.recent_files = self.settings.value("recent_files", [], type=list)
        self.update_recent_menu()

        # Update initial device display in dashboard
        self.ai_dashboard.update_device(self.model_manager.get_device_name())
        self.ai_dashboard.update_model(self.model_manager.get_active_model_name())

        # Main window drag & drop
        self.setAcceptDrops(True)

    # ==================================================
    # Connections Setup
    # ==================================================

    def setup_connections(self):
        self.welcome.openRequested.connect(self.open_image)
        self.welcome.fileDropped.connect(self.handle_dropped_file)
        self.original.fileDropped.connect(self.handle_dropped_file)
        self.processed.fileDropped.connect(self.handle_dropped_file)

        # AI Dashboard signals
        self.ai_dashboard.model_changed.connect(self.on_model_changed)
        self.ai_dashboard.save_image_requested.connect(self.save_image)
        self.ai_dashboard.export_metadata_requested.connect(self.export_detection_metadata)

    # ==================================================
    # Drag and Drop Handling (Main Window level)
    # ==================================================

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                path = urls[0].toLocalFile()
                ext = os.path.splitext(path)[1].lower()
                if ext in self.SUPPORTED_IMAGE_EXTS or ext in self.SUPPORTED_VIDEO_EXTS:
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                path = urls[0].toLocalFile()
                self.handle_dropped_file(path)
                event.acceptProposedAction()

    def handle_dropped_file(self, file_path: str):
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Invalid File", f"The dropped file does not exist:\n{file_path}")
            return

        ext = os.path.splitext(file_path)[1].lower()

        if ext in self.SUPPORTED_IMAGE_EXTS:
            self.load_image_from_path(file_path)
        elif ext in self.SUPPORTED_VIDEO_EXTS:
            self.start_video_detection_on_file(file_path)
        else:
            QMessageBox.warning(self, "Unsupported File", f"Unsupported file extension: '{ext}'")

    # ==================================================
    # Menu Bar
    # ==================================================

    def create_menu(self):
        menu = self.menuBar()

        file_menu = menu.addMenu("File")
        edit_menu = menu.addMenu("Edit")
        view_menu = menu.addMenu("View")
        ai_menu = menu.addMenu("AI Vision")
        help_menu = menu.addMenu("Help")

        # View actions
        compare_action = QAction("Before / After", self)
        compare_action.triggered.connect(self.open_comparison)
        view_menu.addAction(compare_action)

        histogram_action = QAction("Histogram", self)
        histogram_action.triggered.connect(self.open_histogram)
        view_menu.addAction(histogram_action)

        statistics_action = QAction("Statistics", self)
        statistics_action.triggered.connect(self.statistics.show)
        view_menu.addAction(statistics_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.about.exec)

        # File actions
        open_action = QAction("Open Image", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_image)

        save_action = QAction("Save Image", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_image)

        reset_action = QAction("Reset Image", self)
        reset_action.setShortcut("Ctrl+R")
        reset_action.triggered.connect(self.reset_image)

        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)

        # Edit actions
        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.undo_image)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.redo_image)

        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)

        # AI Vision actions
        detect_action = QAction("Object Detection", self)
        detect_action.triggered.connect(self.detect_objects)

        video_action = QAction("Video Detection", self)
        video_action.triggered.connect(self.detect_video)

        webcam_action = QAction("Webcam Detection", self)
        webcam_action.triggered.connect(self.detect_webcam)

        stop_action = QAction("Stop Detection", self)
        stop_action.triggered.connect(self.stop_detection)

        pause_action = QAction("Pause Detection", self)
        pause_action.triggered.connect(self.pause_detection)

        resume_action = QAction("Resume Detection", self)
        resume_action.triggered.connect(self.resume_detection)

        ocr_action = QAction("Image OCR", self)
        ocr_action.triggered.connect(self.detect_text)

        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(reset_action)
        file_menu.addSeparator()
        self.recent_menu = file_menu.addMenu("Recent Files")
        self.update_recent_menu()
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        ai_menu.addAction(detect_action)
        ai_menu.addAction(video_action)
        ai_menu.addAction(webcam_action)
        ai_menu.addSeparator()
        ai_menu.addAction(ocr_action)
        ai_menu.addSeparator()
        ai_menu.addAction(pause_action)
        ai_menu.addAction(resume_action)
        ai_menu.addAction(stop_action)

        help_menu.addAction(about_action)

    # ==================================================
    # Toolbar
    # ==================================================

    def create_toolbar(self):
        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)
        toolbar.setIconSize(QSize(28, 28))
        toolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)

        open_action = QAction(QIcon(resource_path("Assets/icons/open.png")), "Open", self)
        open_action.triggered.connect(self.open_image)
        toolbar.addAction(open_action)

        save_action = QAction(QIcon(resource_path("Assets/icons/save.png")), "Save", self)
        save_action.triggered.connect(self.save_image)
        toolbar.addAction(save_action)

        reset_action = QAction(QIcon(resource_path("Assets/icons/reset.png")), "Reset", self)
        reset_action.triggered.connect(self.reset_image)
        toolbar.addAction(reset_action)

        toolbar.addSeparator()

        undo_action = QAction(QIcon(resource_path("Assets/icons/undo.png")), "Undo", self)
        undo_action.triggered.connect(self.undo_image)

        redo_action = QAction(QIcon(resource_path("Assets/icons/redo.png")), "Redo", self)
        redo_action.triggered.connect(self.redo_image)

        toolbar.addAction(undo_action)
        toolbar.addAction(redo_action)

        toolbar.addSeparator()

        zoom_in_action = QAction(QIcon(resource_path("Assets/icons/zoom_in.png")), "Zoom +", self)
        zoom_in_action.triggered.connect(self.zoom_in)

        zoom_out_action = QAction(QIcon(resource_path("Assets/icons/zoom_out.png")), "Zoom -", self)
        zoom_out_action.triggered.connect(self.zoom_out)

        fit_action = QAction(QIcon(resource_path("Assets/icons/fit.png")), "Fit", self)
        fit_action.triggered.connect(self.fit_image)

        toolbar.addAction(zoom_in_action)
        toolbar.addAction(zoom_out_action)
        toolbar.addAction(fit_action)

    # ==================================================
    # Status Bar
    # ==================================================

    def create_statusbar(self):
        status = QStatusBar()
        status.showMessage("Ready")
        self.setStatusBar(status)

    # ==================================================
    # Main UI Layout
    # ==================================================

    def create_ui(self):
        splitter = QSplitter(Qt.Horizontal)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.itemClicked.connect(self.change_module)
        self.sidebar.currentItemChanged.connect(self.change_module)

        # Workspace
        workspace = QWidget()
        layout = QHBoxLayout(workspace)

        self.original = ImageViewer("Original Image")
        self.processed = ImageViewer("Processed Image")

        layout.addWidget(self.original)
        layout.addWidget(self.processed)

        # Property Panel & Dashboard
        self.properties = PropertyPanel()
        self.properties.algorithm_list.currentItemChanged.connect(self.update_parameters)
        self.properties.apply_button.clicked.connect(self.apply_algorithm)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(self.properties)
        right_layout.addWidget(self.ai_dashboard)

        splitter.addWidget(self.sidebar)
        splitter.addWidget(workspace)
        splitter.addWidget(right_panel)

        splitter.setStretchFactor(1, 8)

        # Stacked Widget (Welcome Screen vs Main App Workspace)
        self.stack = QStackedWidget()
        self.stack.addWidget(self.welcome)   # Index 0
        self.stack.addWidget(splitter)       # Index 1

        self.setCentralWidget(self.stack)

    # ==================================================
    # Open Image Helpers
    # ==================================================

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tif *.webp)"
        )
        if file_path:
            self.load_image_from_path(file_path)

    def load_image_from_path(self, file_path: str):
        try:
            image = self.image_manager.load_image(file_path)
            self.original.set_image(image)
            self.processed.set_image(image)

            self.add_recent_file(file_path)
            self.stack.setCurrentIndex(1)
            self.statusBar().showMessage(f"Loaded Image: {file_path}")

            h, w = image.shape[:2]
            self.ai_dashboard.update_resolution(w, h)
            self.ai_dashboard.update_source(os.path.basename(file_path))

        except Exception as e:
            QMessageBox.critical(self, "Open Image Error", f"Unable to load image:\n{str(e)}")

    # ==================================================
    # Async Model Loading
    # ==================================================

    def on_model_changed(self, model_name: str):
        if self.model_manager.is_model_loaded(model_name):
            self.model_manager.load_model(model_name)
            self.ai_dashboard.update_model(model_name)
            self.statusBar().showMessage(f"Switched active AI model to '{model_name}'")
            return

        self.ai_dashboard.update_status("Loading Model...")
        self.statusBar().showMessage(f"Loading '{model_name}' model in background...")

        self.active_worker = ModelLoadWorker(self.model_manager, model_name)
        self.active_worker.model_loaded.connect(self._on_model_loaded_success)
        self.active_worker.error_occurred.connect(self._on_model_load_error)
        self.active_worker.start()

    def _on_model_loaded_success(self, model_name: str, model_obj):
        self.ai_dashboard.update_model(model_name)
        self.ai_dashboard.update_status("Idle")
        self.statusBar().showMessage(f"Model '{model_name}' loaded successfully.")

    def _on_model_load_error(self, error_msg: str):
        self.ai_dashboard.update_status("Error")
        self.statusBar().showMessage("Model load failed.")
        QMessageBox.critical(
            self,
            "Model Load Error",
            f"Unable to load the requested model.\n\nReason:\n{error_msg}"
        )

    # ==================================================
    # Change Module (Sidebar navigation)
    # ==================================================

    def change_module(self, current, previous=None):
        if current is None:
            return

        module = current.text()

        if "Open Image" in module:
            self.open_image()
            return
        elif "Save Image" in module:
            self.save_image()
            return

        if "Enhancement" in module:
            self.properties.set_algorithms([
                "Negative", "Log Transform", "Gamma",
                "Contrast Stretch", "Histogram Equalization", "Histogram Matching"
            ])
        elif "Noise" in module:
            self.properties.set_algorithms(["Salt & Pepper", "Gaussian Noise"])
        elif "Filtering" in module:
            self.properties.set_algorithms(["Mean Filter", "Median Filter", "Gaussian Filter"])
        elif "Edge" in module:
            self.properties.set_algorithms(["Roberts", "Prewitt", "Sobel", "Laplacian", "Canny"])
        elif "Segmentation" in module:
            self.properties.set_algorithms(["Threshold", "Region Growing", "Watershed"])
        elif "Frequency" in module:
            self.properties.set_algorithms(["Fourier Transform", "Low Pass", "High Pass", "Butterworth", "Gaussian"])
        elif "Morphology" in module:
            self.properties.set_algorithms(["Dilation", "Erosion", "Opening", "Closing", "Boundary Extraction"])
        elif "Compression" in module:
            self.properties.set_algorithms(["Run Length Encoding", "Huffman Coding", "JPEG Compression"])
        elif "Transformation" in module:
            self.properties.set_algorithms(["Translation", "Rotation", "Scaling", "Affine"])
        else:
            self.properties.set_algorithms([])

    # ==================================================
    # Algorithm Execution Map
    # ==================================================

    def create_algorithm_map(self):
        ref_path = resource_path("Images/reference.jpg")
        reference = cv2.imread(ref_path) if os.path.exists(ref_path) else None

        return {
            "Negative": lambda img: self.processor.enhancement.negative(img),
            "Log Transform": lambda img: self.processor.enhancement.log_transform(img),
            "Gamma": lambda img: self.processor.enhancement.gamma_transform(
                img, gamma=self.properties.value("Gamma")
            ),
            "Contrast Stretch": lambda img: self.processor.enhancement.contrast_stretch(img),
            "Histogram Equalization": lambda img: self.processor.enhancement.histogram_equalization(img),
            "Histogram Matching": lambda img: (
                self.processor.enhancement.histogram_matching(img, reference)
                if reference is not None else img
            ),
            "Salt & Pepper": lambda img: self.processor.noise.salt_pepper_noise(img),
            "Gaussian Noise": lambda img: self.processor.noise.gaussian_noise(img),
            "Mean Filter": lambda img: self.processor.filtering.mean_filter(
                img, kernel_size=self.properties.value("Kernel Size")
            ),
            "Median Filter": lambda img: self.processor.filtering.median_filter(
                img, kernel_size=self.properties.value("Kernel Size")
            ),
            "Gaussian Filter": lambda img: self.processor.filtering.gaussian_filter(
                img, kernel_size=self.properties.value("Kernel Size")
            ),
            "Roberts": lambda img: self.processor.edge.roberts(img),
            "Prewitt": lambda img: self.processor.edge.prewitt(img),
            "Sobel": lambda img: self.processor.edge.sobel(img),
            "Laplacian": lambda img: self.processor.edge.laplacian(img),
            "Canny": lambda img: self.processor.edge.canny(img),
            "Threshold": lambda img: self.processor.segmentation.threshold(img),
            "Region Growing": lambda img: self.processor.segmentation.region_growing(
                img, seed_point=(100, 100)
            ),
            "Watershed": lambda img: self.processor.segmentation.watershed(img),
            "Fourier Transform": lambda img: self.processor.frequency.fourier_transform(img),
            "Low Pass": lambda img: self.processor.frequency.low_pass_filter(img),
            "High Pass": lambda img: self.processor.frequency.high_pass_filter(img),
            "Butterworth": lambda img: self.processor.frequency.butterworth_filter(img),
            "Gaussian": lambda img: self.processor.frequency.gaussian_filter(img),
            "Dilation": lambda img: self.processor.morphology.dilation(img),
            "Erosion": lambda img: self.processor.morphology.erosion(img),
            "Opening": lambda img: self.processor.morphology.opening(img),
            "Closing": lambda img: self.processor.morphology.closing(img),
            "Boundary Extraction": lambda img: self.processor.morphology.boundary_extraction(img),
            "Translation": lambda img: self.processor.transformation.translation(
                img, tx=self.properties.value("X"), ty=self.properties.value("Y")
            ),
            "Rotation": lambda img: self.processor.transformation.rotation(
                img, angle=self.properties.value("Angle")
            ),
            "Scaling": lambda img: self.processor.transformation.scaling(
                img, scale=self.properties.value("Scale")
            ),
            "Affine": lambda img: self.processor.transformation.affine_transformation(img),
            "Run Length Encoding": lambda img: self.processor.compression.run_length_encoding(img),
            "Huffman Coding": lambda img: self.processor.compression.huffman_encoding(img),
        }

    # ==================================================
    # Apply Traditional DIP Algorithm
    # ==================================================

    def apply_algorithm(self):
        image = self.image_manager.get_original()
        if image is None:
            QMessageBox.warning(self, "No Image", "Please open an image first.")
            return

        algorithm = self.properties.selected_algorithm()
        if not algorithm:
            return

        compression_algorithms = {"JPEG Compression", "Run Length Encoding", "Huffman Coding"}

        if algorithm in compression_algorithms:
            if algorithm == "JPEG Compression":
                output_dir = resource_path("Images/output")
                os.makedirs(output_dir, exist_ok=True)
                output = os.path.join(output_dir, "compressed.jpg")

                try:
                    start = time.perf_counter()
                    self.processor.compression.jpeg_compression(
                        image, output, quality=self.properties.value("Quality")
                    )
                    elapsed = (time.perf_counter() - start) * 1000.0
                    result = cv2.imread(output)
                except Exception as e:
                    QMessageBox.critical(self, "Compression Error", f"Unable to compress image.\n\nReason:\n{str(e)}")
                    return

                image_path = self.image_manager.get_image_path()
                if image_path and os.path.exists(image_path):
                    original_size = os.path.getsize(image_path)
                    compressed_size = os.path.getsize(output)
                    quality = self.properties.value("Quality")

                    self.compression_report.update_report(original_size, compressed_size, quality)
                    self.compression_report.show()

                self.image_manager.set_processed(result)
                self.processed.set_image(result)
                self.statistics.update_statistics(algorithm, elapsed, result)
                self.statusBar().showMessage(f"{algorithm} applied successfully")
                return

            elif algorithm == "Run Length Encoding":
                try:
                    stats = self.processor.compression.run_length_encoding(image)
                    QMessageBox.information(
                        self, "Run Length Encoding",
                        f"Algorithm : {stats['algorithm']}\n\n"
                        f"Original Entries : {stats['original_entries']}\n\n"
                        f"Compressed Entries : {stats['compressed_entries']}\n\n"
                        f"Compression Ratio : {stats['compression_ratio']}"
                    )
                    self.statusBar().showMessage("Run Length Encoding completed.")
                except Exception as e:
                    QMessageBox.critical(self, "Compression Error", str(e))
                return

            elif algorithm == "Huffman Coding":
                try:
                    stats = self.processor.compression.huffman_encoding(image)
                    QMessageBox.information(
                        self, "Huffman Coding",
                        f"Algorithm : {stats['algorithm']}\n\n"
                        f"Unique Symbols : {stats['symbols']}\n\n"
                        f"Average Code Length : {stats['average_code_length']} bits"
                    )
                    self.statusBar().showMessage("Huffman Coding completed.")
                except Exception as e:
                    QMessageBox.critical(self, "Compression Error", str(e))
                return

        func = self.algorithm_map.get(algorithm)
        if func is None:
            return

        try:
            start = time.perf_counter()
            result = func(image)
            elapsed = (time.perf_counter() - start) * 1000.0
        except Exception as e:
            QMessageBox.critical(self, "Processing Error", f"Unable to apply '{algorithm}'.\n\nReason:\n{str(e)}")
            return

        self.image_manager.set_processed(result)
        self.processed.set_image(result)
        self.statistics.update_statistics(algorithm, elapsed, result)
        self.statusBar().showMessage(f"{algorithm} applied successfully")

    # ==================================================
    # Async Image Object Detection (Fix GUI Freezing)
    # ==================================================

    def detect_objects(self):
        image = self.original.get_image()
        if image is None:
            QMessageBox.warning(self, "No Image", "Please open an image first.")
            return

        height, width = image.shape[:2]
        self.ai_dashboard.update_resolution(width, height)
        self.ai_dashboard.update_device(self.model_manager.get_device_name())
        self.ai_dashboard.update_model(self.model_manager.get_active_model_name())
        self.ai_dashboard.update_source("Image")
        self.ai_dashboard.update_status("Detecting...")

        self.statusBar().showMessage("Running YOLO object detection in background...")

        confidence = self.ai_dashboard.get_confidence()

        self.active_worker = ImageDetectionWorker(self.detector, image, confidence)
        self.active_worker.finished.connect(self._on_detection_finished)
        self.active_worker.error_occurred.connect(self._on_detection_error)
        self.active_worker.start()

    def _on_detection_finished(self, annotated, detections, elapsed_ms):
        fps = 1000.0 / elapsed_ms if elapsed_ms > 0 else 0.0

        self.ai_dashboard.reset()
        self.ai_dashboard.update_inference_time(elapsed_ms)
        self.ai_dashboard.update_fps(fps)
        self.ai_dashboard.update_source("Image")
        self.ai_dashboard.update_model(self.model_manager.get_active_model_name())
        self.ai_dashboard.update_device(self.model_manager.get_device_name())
        self.ai_dashboard.update_status("Completed")

        self.processed.set_image(annotated)
        self.ai_dashboard.update_objects(detections)
        self.ai_dashboard.update_object_count(len(detections))

        self.last_detection_results = {
            "model": self.model_manager.get_active_model_name(),
            "source": self.ai_dashboard.source_label.text(),
            "device": self.model_manager.get_device_name(),
            "inference_ms": elapsed_ms,
            "detections": detections
        }

        self.statusBar().showMessage(f"Detection completed in {elapsed_ms:.1f} ms. Found {len(detections)} objects.")

        if not detections:
            QMessageBox.information(self, "Detection", "No objects detected with current confidence threshold.")

    def _on_detection_error(self, error_msg: str):
        self.ai_dashboard.update_status("Error")
        self.statusBar().showMessage("Detection error occurred.")
        QMessageBox.critical(self, "Detection Error", f"An error occurred during object detection:\n\n{error_msg}")

    # ==================================================
    # Video & Webcam Detection
    # ==================================================

    def detect_video(self):
        self.stop_detection()

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Video", "", "Video Files (*.mp4 *.avi *.mov *.mkv)"
        )
        if not file_path:
            return

        self.start_video_detection_on_file(file_path)

    def start_video_detection_on_file(self, file_path: str):
        self.stop_detection()
        self.stack.setCurrentIndex(1)

        self.ai_dashboard.reset()
        self.ai_dashboard.update_model(self.model_manager.get_active_model_name())
        self.ai_dashboard.update_source(os.path.basename(file_path))
        self.ai_dashboard.update_status("Running")
        self.ai_dashboard.update_device(self.model_manager.get_device_name())

        self.stream_detector = StreamDetector(
            self.detector,
            file_path,
            self.ai_dashboard.get_confidence()
        )

        self.stream_detector.detections_ready.connect(self.ai_dashboard.update_objects)
        self.stream_detector.frame_ready.connect(self.processed.set_image)
        self.stream_detector.original_frame_ready.connect(self.original.set_image)
        self.stream_detector.fps_ready.connect(self.ai_dashboard.update_fps)
        self.stream_detector.finished.connect(self.stream_finished)
        self.stream_detector.error.connect(self.stream_error)

        self.stream_detector.start()
        self.statusBar().showMessage(f"Streaming video detection: {os.path.basename(file_path)}")

    def detect_webcam(self):
        self.stop_detection()
        self.stack.setCurrentIndex(1)

        self.ai_dashboard.reset()
        self.ai_dashboard.update_model(self.model_manager.get_active_model_name())
        self.ai_dashboard.update_source("Webcam")
        self.ai_dashboard.update_status("Running")
        self.ai_dashboard.update_device(self.model_manager.get_device_name())

        self.stream_detector = StreamDetector(
            self.detector,
            0,
            self.ai_dashboard.get_confidence()
        )

        self.stream_detector.detections_ready.connect(self.ai_dashboard.update_objects)
        self.stream_detector.frame_ready.connect(self.processed.set_image)
        self.stream_detector.original_frame_ready.connect(self.original.set_image)
        self.stream_detector.fps_ready.connect(self.ai_dashboard.update_fps)
        self.stream_detector.finished.connect(self.stream_finished)
        self.stream_detector.error.connect(self.stream_error)

        self.stream_detector.start()
        self.statusBar().showMessage("Streaming live webcam detection...")

    def stop_detection(self):
        if hasattr(self, "stream_detector") and self.stream_detector is not None:
            if self.stream_detector.isRunning():
                self.stream_detector.stop()
                self.stream_detector.wait(1000)

        self.ai_dashboard.update_status("Stopped")
        self.ai_dashboard.update_fps(0)
        self.statusBar().showMessage("Detection stopped.")

    def pause_detection(self):
        if hasattr(self, "stream_detector") and self.stream_detector is not None:
            if self.stream_detector.isRunning():
                self.stream_detector.pause()
                self.ai_dashboard.update_status("Paused")
                self.statusBar().showMessage("Detection paused.")

    def resume_detection(self):
        if hasattr(self, "stream_detector") and self.stream_detector is not None:
            if self.stream_detector.isRunning():
                self.stream_detector.resume()
                self.ai_dashboard.update_status("Running")
                self.statusBar().showMessage("Detection resumed.")

    def stream_finished(self):
        self.ai_dashboard.update_status("Completed")
        self.ai_dashboard.update_fps(0)
        self.statusBar().showMessage("Stream processing completed.")

    def stream_error(self, message: str):
        self.ai_dashboard.update_status("Error")
        self.ai_dashboard.update_fps(0)
        QMessageBox.critical(self, "Stream Error", message)

    # ==================================================
    # Async Image OCR (Fix GUI Freezing)
    # ==================================================

    def detect_text(self):
        image = self.original.get_image()
        if image is None:
            QMessageBox.warning(self, "No Image", "Please open an image first.")
            return

        height, width = image.shape[:2]
        self.ai_dashboard.update_resolution(width, height)
        self.ai_dashboard.update_device(self.model_manager.get_device_name())
        self.ai_dashboard.update_model("EasyOCR")
        self.ai_dashboard.update_source("Image")
        self.ai_dashboard.update_status("Running OCR...")

        self.statusBar().showMessage("Running EasyOCR text extraction in background...")
        confidence = self.ai_dashboard.get_ocr_confidence()

        self.active_worker = OCRWorker(self.ocr_detector, image, confidence)
        self.active_worker.finished.connect(self._on_ocr_finished)
        self.active_worker.error_occurred.connect(self._on_ocr_error)
        self.active_worker.start()

    def _on_ocr_finished(self, annotated, detections, avg_conf, elapsed_sec):
        self.ai_dashboard.update_inference_time(elapsed_sec * 1000.0)
        self.ai_dashboard.update_fps(1.0 / elapsed_sec if elapsed_sec > 0 else 0.0)
        self.processed.set_image(annotated)

        texts = [{"class": item["text"]} for item in detections]
        self.ai_dashboard.update_objects(texts)
        self.ai_dashboard.update_object_count(len(texts))
        self.ai_dashboard.update_status("Completed")

        self.statusBar().showMessage(f"OCR completed in {elapsed_sec:.2f} s. Found {len(detections)} text regions.")

        if not detections:
            QMessageBox.information(self, "OCR", "No text detected with current OCR confidence.")
            return

        text = "\n".join(f"{item['text']} ({item['confidence']:.2f}%)" for item in detections)
        self.ocr_dialog.set_text(
            text=text,
            average_confidence=avg_conf,
            processing_time=elapsed_sec,
            language="English"
        )
        self.ocr_dialog.exec()

    def _on_ocr_error(self, error_msg: str):
        self.ai_dashboard.update_status("Error")
        self.statusBar().showMessage("OCR failed.")
        QMessageBox.critical(self, "OCR Error", f"Unable to extract text:\n\n{error_msg}")

    # ==================================================
    # Save & Export Results
    # ==================================================

    def save_image(self):
        image = self.image_manager.get_processed()
        if image is None:
            self.statusBar().showMessage("No processed image to save.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Image", "", "PNG (*.png);;JPEG (*.jpg *.jpeg);;Bitmap (*.bmp)"
        )
        if not file_path:
            return

        success = cv2.imwrite(file_path, image)
        if success:
            self.statusBar().showMessage(f"Image saved to: {file_path}")
        else:
            QMessageBox.critical(self, "Save Error", f"Failed to save image to: {file_path}")

    def export_detection_metadata(self):
        if not self.last_detection_results:
            QMessageBox.information(self, "Export Metadata", "No detection results available to export.")
            return

        path, selected_filter = QFileDialog.getSaveFileName(
            self, "Export Detection Data", "detections.json", "JSON Files (*.json);;CSV Files (*.csv);;Text Files (*.txt)"
        )
        if not path:
            return

        try:
            ext = os.path.splitext(path)[1].lower()

            if ext == ".json":
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(self.last_detection_results, f, indent=4)
            elif ext == ".csv":
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Model", "Source", "Device", "Inference_ms", "Class", "Confidence"])
                    for det in self.last_detection_results.get("detections", []):
                        writer.writerow([
                            self.last_detection_results["model"],
                            self.last_detection_results["source"],
                            self.last_detection_results["device"],
                            self.last_detection_results["inference_ms"],
                            det["class"],
                            det["confidence"]
                        ])
            else:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(f"Model: {self.last_detection_results['model']}\n")
                    f.write(f"Source: {self.last_detection_results['source']}\n")
                    f.write(f"Device: {self.last_detection_results['device']}\n")
                    f.write(f"Inference: {self.last_detection_results['inference_ms']:.1f} ms\n\n")
                    f.write("Detected Objects:\n")
                    for det in self.last_detection_results.get("detections", []):
                        f.write(f" - {det['class']}: {det['confidence']}%\n")

            QMessageBox.information(self, "Export Data", f"Metadata exported successfully to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export metadata:\n{str(e)}")

    # ==================================================
    # Image Operations (Reset, Undo, Redo, Zoom)
    # ==================================================

    def reset_image(self):
        original = self.image_manager.get_original()
        if original is None:
            self.statusBar().showMessage("No image loaded.")
            return

        self.image_manager.reset()
        self.original.set_image(original)
        self.processed.set_image(original)
        self.statusBar().showMessage("Image reset successfully.")

    def undo_image(self):
        image = self.image_manager.undo()
        if image is None:
            self.statusBar().showMessage("Nothing to undo.")
            return

        self.processed.set_image(image)
        self.statusBar().showMessage("Undo performed.")

    def redo_image(self):
        image = self.image_manager.redo()
        if image is None:
            self.statusBar().showMessage("Nothing to redo.")
            return

        self.processed.set_image(image)
        self.statusBar().showMessage("Redo performed.")

    def update_parameters(self, current, previous):
        if current is None:
            return

        algorithm = current.text()
        self.properties.clear_parameters()

        if algorithm == "Gamma":
            self.properties.add_double_spinbox("Gamma", 0.1, 5.0, 0.5)
        elif algorithm in ["Mean Filter", "Median Filter", "Gaussian Filter"]:
            self.properties.add_spinbox("Kernel Size", 3, 15, 3)
        elif algorithm == "Rotation":
            self.properties.add_spinbox("Angle", 0, 360, 45)
        elif algorithm == "Scaling":
            self.properties.add_double_spinbox("Scale", 0.1, 5.0, 1.0)
        elif algorithm == "Translation":
            self.properties.add_spinbox("X", -500, 500, 100)
            self.properties.add_spinbox("Y", -500, 500, 100)
        elif algorithm == "JPEG Compression":
            self.properties.add_spinbox("Quality", 1, 100, 30)
        elif algorithm in ["Low Pass", "High Pass", "Butterworth", "Gaussian"]:
            self.properties.add_spinbox("Radius", 5, 100, 30)

    def zoom_in(self):
        self.original.zoom_in()
        self.processed.zoom_in()
        self.statusBar().showMessage("Zoom : +")

    def zoom_out(self):
        self.original.zoom_out()
        self.processed.zoom_out()
        self.statusBar().showMessage("Zoom : -")

    def fit_image(self):
        self.original.fit_image()
        self.processed.fit_image()
        self.statusBar().showMessage("Fit to Window")

    def open_comparison(self):
        original = self.image_manager.get_original()
        processed = self.image_manager.get_processed()

        if original is None or processed is None:
            self.statusBar().showMessage("Load and process an image first.")
            return

        self.comparison.set_images(original, processed)
        self.comparison.show()

    def open_histogram(self):
        image = self.image_manager.get_processed()
        if image is None:
            self.statusBar().showMessage("No image loaded.")
            return

        self.histogram.show_histogram(image)
        self.histogram.show()

    def add_recent_file(self, file_path):
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)

        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:self.max_recent_files]

        self.update_recent_menu()
        self.settings.setValue("recent_files", self.recent_files)

    def update_recent_menu(self):
        self.recent_menu.clear()
        if not self.recent_files:
            action = self.recent_menu.addAction("No Recent Files")
            action.setEnabled(False)
            return

        for path in self.recent_files:
            if not os.path.exists(path):
                continue

            action = self.recent_menu.addAction(os.path.basename(path))
            action.setToolTip(path)
            action.triggered.connect(partial(self.load_image_from_path, path))

    # ==================================================
    # Application Shutdown Safety
    # ==================================================

    def closeEvent(self, event):
        self.statusBar().showMessage("Closing application and releasing resources...")

        if hasattr(self, "stream_detector") and self.stream_detector is not None:
            if self.stream_detector.isRunning():
                self.stream_detector.stop()
                self.stream_detector.wait(1000)

        if self.active_worker is not None and self.active_worker.isRunning():
            self.active_worker.quit()
            self.active_worker.wait(500)

        super().closeEvent(event)
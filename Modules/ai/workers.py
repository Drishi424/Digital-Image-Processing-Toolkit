import time
import numpy as np
from PySide6.QtCore import QThread, Signal


class ModelLoadWorker(QThread):
    """
    Background worker thread to load AI models without freezing the GUI.
    """
    model_loaded = Signal(str, object)  # model_name, model_obj
    error_occurred = Signal(str)

    def __init__(self, model_manager, model_name: str):
        super().__init__()
        self.model_manager = model_manager
        self.model_name = model_name

    def run(self):
        try:
            model = self.model_manager.load_model(self.model_name)
            self.model_loaded.emit(self.model_name, model)
        except Exception as e:
            self.error_occurred.emit(str(e))


class ImageDetectionWorker(QThread):
    """
    Background worker thread for single-image YOLO detection.
    """
    # annotated_image (np.ndarray), detections (list), inference_time_ms (float)
    finished = Signal(object, list, float)
    error_occurred = Signal(str)

    def __init__(self, detector, image: np.ndarray, confidence: float = 0.25):
        super().__init__()
        self.detector = detector
        self.image = image
        self.confidence = confidence

    def run(self):
        try:
            start = time.perf_counter()
            annotated, detections = self.detector.detect(self.image, self.confidence)
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            self.finished.emit(annotated, detections, elapsed_ms)
        except Exception as e:
            self.error_occurred.emit(str(e))


class OCRWorker(QThread):
    """
    Background worker thread for single-image OCR text extraction.
    """
    # annotated_image (np.ndarray), detections (list), average_confidence (float), processing_time_sec (float)
    finished = Signal(object, list, float, float)
    error_occurred = Signal(str)

    def __init__(self, ocr_detector, image: np.ndarray, confidence: float = 0.25):
        super().__init__()
        self.ocr_detector = ocr_detector
        self.image = image
        self.confidence = confidence

    def run(self):
        try:
            start = time.perf_counter()
            annotated, detections = self.ocr_detector.detect(self.image, self.confidence)
            elapsed_sec = time.perf_counter() - start

            if detections:
                avg_conf = sum(item["confidence"] for item in detections) / len(detections)
            else:
                avg_conf = 0.0

            self.finished.emit(annotated, detections, avg_conf, elapsed_sec)
        except Exception as e:
            self.error_occurred.emit(str(e))

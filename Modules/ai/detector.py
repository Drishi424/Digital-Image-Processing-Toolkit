import cv2
import torch
from Modules.ai.model_manager import ModelManager


class YOLODetector:
    """
    YOLO Object Detection wrapper interfacing with ModelManager.
    """

    def __init__(self, model_manager: ModelManager = None):
        if model_manager is None:
            self.model_manager = ModelManager()
        else:
            self.model_manager = model_manager

        # Ensure default model is loaded
        try:
            self.model_manager.get_active_model()
        except Exception as e:
            print(f"[YOLODetector] Initial model load error: {e}")

    @property
    def model(self):
        return self.model_manager.get_active_model()

    @property
    def device(self):
        return self.model_manager.get_device()

    def set_model(self, model_name: str):
        return self.model_manager.load_model(model_name)

    def detect(self, image, confidence=0.25):
        active_model = self.model
        if active_model is None:
            raise RuntimeError("No active YOLO model available for detection.")

        results = active_model.predict(
            image,
            conf=confidence,
            verbose=False
        )

        annotated = results[0].plot()
        detections = []

        for box in results[0].boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])

            class_name = active_model.names[cls] if cls in active_model.names else f"class_{cls}"

            detections.append({
                "class": class_name,
                "confidence": round(conf * 100, 2)
            })

        return annotated, detections
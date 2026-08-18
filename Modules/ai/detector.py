from ultralytics import YOLO
import cv2
import torch

from UI.ai_dashboard import AIDashboard

class YOLODetector:

    def __init__(self):
        self.ai_dashboard = AIDashboard()

        if torch.cuda.is_available():
            device = "CUDA"
        else:
            device = "CPU"

        self.ai_dashboard.update_device(device)

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = YOLO("drone_best.pt")
        self.model.to(self.device)

        print(f"[YOLO] Running on: {self.device.upper()}")

    def detect(self, image, confidence=0.25):
        results = self.model.predict(
            image,
            conf=confidence,
            verbose=False
        )

        annotated = results[0].plot()

        detections = []

        for box in results[0].boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])

            detections.append({
                "class": self.model.names[cls],
                "confidence": round(conf * 100, 2)
            })

        return annotated, detections
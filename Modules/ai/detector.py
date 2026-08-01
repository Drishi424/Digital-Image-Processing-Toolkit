from ultralytics import YOLO
import cv2
import torch


class YOLODetector:

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = YOLO("yolo11n.pt")
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
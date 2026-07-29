from ultralytics import YOLO
import cv2


class YOLODetector:

    def __init__(self):
        self.model = YOLO("yolo11n.pt")

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
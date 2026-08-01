import cv2
import easyocr
import torch


class OCRDetector:

    def __init__(self, languages=None, gpu=False):

        if languages is None:
            languages = ["en"]

        self.reader = easyocr.Reader(
            languages,
            gpu=torch.cuda.is_available()
        )

    # --------------------------------------------------

    def detect(self, image):

        results = self.reader.readtext(image)

        annotated = image.copy()

        detections = []

        for result in results:

            bbox, text, confidence = result

            # Convert to integer points
            points = []

            for x, y in bbox:
                points.append(
                    (int(x), int(y))
                )

            # Draw polygon
            # Draw bounding box
            for i in range(4):

                cv2.line(
                    annotated,
                    points[i],
                    points[(i + 1) % 4],
                    (0, 255, 0),
                    2
                )

            # Draw text
            cv2.putText(
                annotated,
                text,
                points[0],
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            detections.append({

                "text": text,

                "confidence": round(
                    confidence * 100,
                    2
                ),

                "bbox": points

            })
        return annotated, detections

    def extract_text(self, image):

        _, detections = self.detect(image)

        text = []

        for item in detections:
            text.append(item["text"])

        return "\n".join(text)
from PySide6.QtCore import QThread, Signal
import cv2
import time


class StreamDetector(QThread):
    """
    Background thread for video/webcam processing.
    """

    frame_ready = Signal(object)
    original_frame_ready = Signal(object)
    detections_ready = Signal(list)
    fps_ready = Signal(float)
    finished = Signal()
    error = Signal(str)

    def __init__(self, detector, source, confidence=0.25):
        super().__init__()

        self.detector = detector
        self.source = source
        self.confidence = confidence

        self.capture = None

        self.running = False
        self.paused = False

        self.frame_delay = 30

    # --------------------------------------------------

    def run(self):

        self.capture = cv2.VideoCapture(self.source)

        if not self.capture.isOpened():

            if self.source == 0:
                self.error.emit("Unable to open webcam.")
            else:
                self.error.emit("Unable to open video.")

            return

        if self.source == 0:
            fps = 30
        else:
            fps = self.capture.get(cv2.CAP_PROP_FPS)

            if fps <= 0 or fps != fps:
                fps = 30

        self.frame_delay = max(1, int(1000 / fps))

        self.running = True

        while self.running:

            if self.paused:
                self.msleep(30)
                continue

            success, frame = self.capture.read()

            if not success:
                break

            # Show original frame
            self.original_frame_ready.emit(frame.copy())

            # Start timer
            start = time.perf_counter()

            # YOLO Detection
            annotated, detections = self.detector.detect(
                frame,
                self.confidence
            )

            # Stop timer
            elapsed = time.perf_counter() - start

            # Calculate FPS
            fps = 1 / elapsed if elapsed > 0 else 0

            # Emit FPS
            self.fps_ready.emit(fps)

            # Emit processed frame
            self.frame_ready.emit(annotated)

            # Emit detections
            self.detections_ready.emit(detections)

            self.msleep(self.frame_delay)

        self.cleanup()

    # --------------------------------------------------

    def pause(self):
        self.paused = True

    # --------------------------------------------------

    def resume(self):
        self.paused = False

    # --------------------------------------------------

    def stop(self):
        self.running = False

    # --------------------------------------------------

    def cleanup(self):

        if self.capture is not None:
            self.capture.release()

        self.finished.emit()
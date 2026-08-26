from PySide6.QtCore import QThread, Signal
import cv2
import time


class StreamDetector(QThread):
    """
    Background thread for real-time video/webcam processing.
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

    def set_confidence(self, confidence: float):
        self.confidence = confidence

    def run(self):
        try:
            self.capture = cv2.VideoCapture(self.source)

            if not self.capture or not self.capture.isOpened():
                if self.source == 0:
                    self.error.emit("Unable to open webcam device.")
                else:
                    self.error.emit(f"Unable to open video file: {self.source}")
                return

            if self.source == 0:
                fps = 30.0
            else:
                fps = self.capture.get(cv2.CAP_PROP_FPS)
                if fps <= 0 or fps != fps:
                    fps = 30.0

            self.frame_delay = max(1, int(1000 / fps))
            self.running = True

            while self.running:
                if self.paused:
                    self.msleep(30)
                    continue

                success, frame = self.capture.read()

                if not success or frame is None:
                    break

                # Show original frame
                self.original_frame_ready.emit(frame.copy())

                # Start timer
                start = time.perf_counter()

                try:
                    # YOLO Detection
                    annotated, detections = self.detector.detect(
                        frame,
                        self.confidence
                    )
                except Exception as detect_err:
                    self.error.emit(f"Detection error during streaming: {str(detect_err)}")
                    break

                # Stop timer
                elapsed = time.perf_counter() - start

                # Calculate FPS
                calculated_fps = 1.0 / elapsed if elapsed > 0 else 0.0

                # Emit signals
                self.fps_ready.emit(calculated_fps)
                self.frame_ready.emit(annotated)
                self.detections_ready.emit(detections)

                self.msleep(self.frame_delay)

        except Exception as e:
            self.error.emit(f"Stream thread error: {str(e)}")
        finally:
            self.cleanup()

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def stop(self):
        self.running = False

    def cleanup(self):
        if self.capture is not None:
            try:
                self.capture.release()
            except Exception:
                pass
            self.capture = None

        self.finished.emit()
import cv2
from typing import Optional
import numpy as np


class ImageManager:
    """
    Manages loading, storing, undo, redo, and reset of image states.
    Limits stack depth to prevent out-of-memory issues with high-res images.
    """

    def __init__(self, max_stack_size: int = 20):
        self.original_image: Optional[np.ndarray] = None
        self.processed_image: Optional[np.ndarray] = None
        self.image_path: Optional[str] = None

        self.max_stack_size = max_stack_size

        # History
        self.undo_stack = []
        self.redo_stack = []

    def load_image(self, path: str):
        image = cv2.imread(path)

        if image is None:
            raise FileNotFoundError(f"Unable to load image from path: '{path}'. File may be corrupt or invalid format.")

        self.image_path = path

        self.original_image = image.copy()
        self.processed_image = image.copy()

        # Clear history when a new image is opened
        self.undo_stack.clear()
        self.redo_stack.clear()

        return image

    def get_original(self) -> Optional[np.ndarray]:
        if self.original_image is None:
            return None
        return self.original_image.copy()

    def get_processed(self) -> Optional[np.ndarray]:
        if self.processed_image is None:
            return None
        return self.processed_image.copy()

    def set_processed(self, image: np.ndarray):
        if self.processed_image is not None:
            self.undo_stack.append(self.processed_image.copy())
            if len(self.undo_stack) > self.max_stack_size:
                self.undo_stack.pop(0)

        self.processed_image = image.copy()
        self.redo_stack.clear()

    def reset(self):
        if self.original_image is None:
            return

        if self.processed_image is not None:
            self.undo_stack.append(self.processed_image.copy())
            if len(self.undo_stack) > self.max_stack_size:
                self.undo_stack.pop(0)

        self.processed_image = self.original_image.copy()
        self.redo_stack.clear()

    def undo(self) -> Optional[np.ndarray]:
        if not self.undo_stack:
            return None

        if self.processed_image is not None:
            self.redo_stack.append(self.processed_image.copy())
            if len(self.redo_stack) > self.max_stack_size:
                self.redo_stack.pop(0)

        self.processed_image = self.undo_stack.pop()
        return self.processed_image.copy()

    def redo(self) -> Optional[np.ndarray]:
        if not self.redo_stack:
            return None

        if self.processed_image is not None:
            self.undo_stack.append(self.processed_image.copy())
            if len(self.undo_stack) > self.max_stack_size:
                self.undo_stack.pop(0)

        self.processed_image = self.redo_stack.pop()
        return self.processed_image.copy()

    def get_image_path(self) -> Optional[str]:
        return self.image_path
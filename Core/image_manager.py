import cv2
from typing import Optional
import numpy as np


class ImageManager:

    def __init__(self):
        
        self.original_image: Optional[np.ndarray] = None
        self.processed_image: Optional[np.ndarray] = None
        self.image_path: Optional[str] = None

        self.original_image = None
        self.processed_image = None
        self.image_path = None

        # History
        self.undo_stack = []
        self.redo_stack = []

    # --------------------------------------------

    def load_image(self, path):

        image = cv2.imread(path)

        if image is None:
            raise FileNotFoundError("Unable to load image.")

        self.image_path = path

        self.original_image = image.copy()
        self.processed_image = image.copy()

        # Clear history when a new image is opened
        self.undo_stack.clear()
        self.redo_stack.clear()

        return image

    # --------------------------------------------

    def get_original(self):

        if self.original_image is None:
            return None

        return self.original_image

    # --------------------------------------------

    def get_processed(self):

        if self.processed_image is None:
            return None

        return self.processed_image

    # --------------------------------------------

    def set_processed(self, image):

        if self.processed_image is not None:
            self.undo_stack.append(self.processed_image.copy())

        self.processed_image = image.copy()

        self.redo_stack.clear()

    # --------------------------------------------

    def reset(self):

        if self.original_image is None:
            return

        self.processed_image = self.original_image.copy()

    # --------------------------------------------
    # ADD THIS
    # --------------------------------------------

    def undo(self):

        if not self.undo_stack:
            return None

        if self.processed_image is not None:
            self.redo_stack.append(self.processed_image.copy())

        self.processed_image = self.undo_stack.pop()

        return self.processed_image

    # --------------------------------------------
    # ADD THIS
    # --------------------------------------------

    def redo(self):

        if not self.redo_stack:
            return None

        if self.processed_image is not None:
            self.undo_stack.append(self.processed_image.copy())

        self.processed_image = self.redo_stack.pop()

        return self.processed_image
    
    def get_image_path(self) -> Optional[str]:
        return self.image_path
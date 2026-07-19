from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

import cv2


class ImageViewer(QWidget):

    def __init__(self, title):
        super().__init__()

        layout = QVBoxLayout(self)

        # Title
        self.title = QLabel(title)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("""
            font-size:16px;
            font-weight:bold;
        """)

        # Image Display
        self.image = QLabel("No Image Loaded")
        self.image.setAlignment(Qt.AlignCenter)
        self.image.setMinimumSize(500, 500)
        self.zoom_factor = 1.0
        self.current_pixmap = None

        self.image.setStyleSheet("""
            QLabel{
                border:2px dashed #666;
                border-radius:10px;
                background:#252526;
                color:white;
            }
        """)

        layout.addWidget(self.title)
        layout.addWidget(self.image)

    # --------------------------------------------------

    def set_image(self, image):
       rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

       h, w, ch = rgb.shape

       bytes_per_line = ch * w

       qimage = QImage(
            rgb.data,
            w,
            h,
            bytes_per_line,
            QImage.Format_RGB888
       )

       self.current_pixmap = QPixmap.fromImage(qimage)

       self.update_view()

    # --------------------------------------------------

    def clear(self):

        self.image.clear()
        self.image.setText("No Image Loaded")

    def update_view(self):

        if self.current_pixmap is None:
            return

        scaled = self.current_pixmap.scaled(

            self.current_pixmap.size() * self.zoom_factor,

            Qt.KeepAspectRatio,

            Qt.SmoothTransformation

        )

        self.image.setPixmap(scaled)
    
    def zoom_in(self):

        self.zoom_factor *= 1.25

        self.update_view()
    
    def zoom_out(self):

        self.zoom_factor /= 1.25

        self.update_view()

    def fit_image(self):

        self.zoom_factor = 1.0

        self.update_view()

    def resizeEvent(self, event):

        super().resizeEvent(event)

        self.update_view()
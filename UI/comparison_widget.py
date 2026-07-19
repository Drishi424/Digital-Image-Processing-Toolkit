from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QPainter,
    QPixmap,
    QImage,
    QColor,
    QPen
)
from PySide6.QtWidgets import QWidget

import cv2


class ComparisonWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.original = None
        self.processed = None

        self.position = 0.5

        self.dragging = False

    # --------------------------------------------------

    def set_images(self, original, processed):

        self.original = self.to_pixmap(original)

        self.processed = self.to_pixmap(processed)

        self.update()

    # --------------------------------------------------

    def to_pixmap(self, image):

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        h, w, ch = rgb.shape

        qimage = QImage(
            rgb.data,
            w,
            h,
            ch * w,
            QImage.Format_RGB888
        )

        return QPixmap.fromImage(qimage)

    # --------------------------------------------------

    def paintEvent(self, event):

        if self.original is None or self.processed is None:
            return

        painter = QPainter(self)

        rect = self.rect()

        original = self.original.scaled(
            rect.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        processed = self.processed.scaled(
            rect.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        x = int(original.width() * self.position)

        painter.drawPixmap(0, 0, original)

        painter.setClipRect(x, 0, rect.width(), rect.height())

        painter.drawPixmap(0, 0, processed)

        painter.setClipping(False)

        pen = QPen(QColor("white"))

        pen.setWidth(3)

        painter.setPen(pen)

        painter.drawLine(x, 0, x, rect.height())

        painter.setBrush(QColor(66,133,244))

        painter.drawEllipse(x-8, rect.height()//2-8, 16, 16)

    # --------------------------------------------------

    def mousePressEvent(self, event):

        self.dragging = True

    # --------------------------------------------------

    def mouseReleaseEvent(self, event):

        self.dragging = False

    # --------------------------------------------------

    def mouseMoveEvent(self, event):

        if not self.dragging:
            return

        self.position = max(
            0,
            min(
                1,
                event.position().x()/self.width()
            )
        )

        self.update()
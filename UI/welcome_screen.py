import os
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class WelcomeScreen(QWidget):

    openRequested = Signal()
    fileDropped = Signal(str)

    SUPPORTED_EXTENSIONS = {
        ".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp",
        ".mp4", ".avi", ".mov", ".mkv"
    }

    def __init__(self):
        super().__init__()

        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Digital Image Processing Toolkit")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            """
            font-size:32px;
            font-weight:bold;
            """
        )

        version = QLabel("Version 2.0")
        version.setAlignment(Qt.AlignCenter)

        subtitle = QLabel(
            "Professional Image Processing Software"
        )
        subtitle.setAlignment(Qt.AlignCenter)

        open_btn = QPushButton("📂 Open Image")

        open_btn.setMinimumHeight(50)
        open_btn.setMinimumWidth(220)

        open_btn.clicked.connect(
            self.openRequested.emit
        )

        info = QLabel(
            "\nOR\n\n"
            "Drag & Drop Image or Video Here\n\n"
            "PNG • JPG • JPEG • BMP • TIFF • WEBP • MP4 • AVI • MOV • MKV"
        )

        info.setAlignment(Qt.AlignCenter)

        layout.addStretch()

        layout.addWidget(title)
        layout.addWidget(version)
        layout.addSpacing(20)
        layout.addWidget(subtitle)
        layout.addSpacing(30)
        layout.addWidget(open_btn, alignment=Qt.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(info)

        layout.addStretch()

    # --------------------------------------------------
    # Drag and Drop Handlers
    # --------------------------------------------------

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                path = urls[0].toLocalFile()
                ext = os.path.splitext(path)[1].lower()
                if ext in self.SUPPORTED_EXTENSIONS:
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                path = urls[0].toLocalFile()
                ext = os.path.splitext(path)[1].lower()
                if ext in self.SUPPORTED_EXTENSIONS:
                    event.acceptProposedAction()
                    self.fileDropped.emit(path)
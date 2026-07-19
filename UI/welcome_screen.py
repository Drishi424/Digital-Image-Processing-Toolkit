from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class WelcomeScreen(QWidget):

    openRequested = Signal()

    def __init__(self):
        super().__init__()

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

        version = QLabel("Version 1.0")
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
            "Drag & Drop Image Here\n\n"
            "PNG • JPG • JPEG • BMP • TIFF"
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
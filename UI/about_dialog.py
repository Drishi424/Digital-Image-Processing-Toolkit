from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl


class AboutDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("About")
        self.setFixedSize(450, 350)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        title = QLabel("Digital Image Processing Toolkit")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size:20px;font-weight:bold;"
        )

        version = QLabel("Version 1.0")
        version.setAlignment(Qt.AlignCenter)

        developer = QLabel(
            "Developed By\nDrishi Kachchhawaha"
        )
        developer.setAlignment(Qt.AlignCenter)

        university = QLabel("JECRC University")
        university.setAlignment(Qt.AlignCenter)

        tech = QLabel(
            "Built With\n\n"
            "• Python\n"
            "• OpenCV\n"
            "• PySide6\n"
            "• NumPy\n"
            "• Matplotlib"
        )

        tech.setAlignment(Qt.AlignCenter)

        github = QPushButton("GitHub")

        github.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://github.com/Drishi424")
            )
        )

        close = QPushButton("Close")
        close.clicked.connect(self.accept)

        buttons = QHBoxLayout()
        buttons.addWidget(github)
        buttons.addWidget(close)

        layout.addWidget(title)
        layout.addWidget(version)
        layout.addSpacing(10)
        layout.addWidget(developer)
        layout.addWidget(university)
        layout.addSpacing(10)
        layout.addWidget(tech)
        layout.addStretch()
        layout.addLayout(buttons)
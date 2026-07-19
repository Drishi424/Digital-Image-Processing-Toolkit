from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidget, QListWidgetItem


class Sidebar(QListWidget):

    def __init__(self):
        super().__init__()

        self.setFixedWidth(230)
        self.setSpacing(5)
        self.setFocusPolicy(Qt.NoFocus)

        self.populate()

    def populate(self):

        modules = [
            "📂 Open Image",
            "💾 Save Image",
            "",
            "✨ Image Enhancement",
            "🌫 Noise Addition",
            "🧹 Filtering",
            "📐 Edge Detection",
            "🎯 Segmentation",
            "🌊 Frequency Domain",
            "🔳 Morphology",
            "📦 Compression",
            "🔄 Transformation"
        ]

        for module in modules:
            self.addItem(QListWidgetItem(module))
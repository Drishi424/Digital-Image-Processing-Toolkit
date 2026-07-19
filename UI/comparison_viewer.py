from PySide6.QtWidgets import QWidget, QVBoxLayout

from UI.comparison_widget import ComparisonWidget


class ComparisonViewer(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Before / After")

        self.resize(1000,700)

        layout = QVBoxLayout(self)

        self.viewer = ComparisonWidget()

        layout.addWidget(self.viewer)

    def set_images(self, original, processed):

        self.viewer.set_images(
            original,
            processed
        )
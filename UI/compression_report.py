from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QFormLayout,
)


class CompressionReport(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Compression Report")
        self.resize(350, 250)

        layout = QFormLayout(self)

        self.original = QLabel("-")
        self.compressed = QLabel("-")
        self.ratio = QLabel("-")
        self.saved = QLabel("-")
        self.quality = QLabel("-")

        layout.addRow("Original Size", self.original)
        layout.addRow("Compressed Size", self.compressed)
        layout.addRow("Compression Ratio", self.ratio)
        layout.addRow("Space Saved", self.saved)
        layout.addRow("JPEG Quality", self.quality)

    def update_report(
        self,
        original_size,
        compressed_size,
        quality
    ):

        ratio = original_size / compressed_size

        saved = (
            (original_size - compressed_size)
            / original_size
        ) * 100

        self.original.setText(
            f"{original_size/1024:.2f} KB"
        )

        self.compressed.setText(
            f"{compressed_size/1024:.2f} KB"
        )

        self.ratio.setText(
            f"{ratio:.2f} : 1"
        )

        self.saved.setText(
            f"{saved:.1f}%"
        )

        self.quality.setText(
            str(quality)
        )
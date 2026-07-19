from PySide6.QtWidgets import QWidget, QLabel, QFormLayout


class StatisticsPanel(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Processing Statistics")
        self.resize(350,250)

        layout = QFormLayout(self)

        self.operation = QLabel("-")
        self.time = QLabel("-")
        self.size = QLabel("-")
        self.channels = QLabel("-")
        self.memory = QLabel("-")

        layout.addRow("Operation", self.operation)
        layout.addRow("Processing Time", self.time)
        layout.addRow("Image Size", self.size)
        layout.addRow("Channels", self.channels)
        layout.addRow("Memory", self.memory)

    def update_statistics(
        self,
        operation,
        elapsed,
        image
    ):

        h, w = image.shape[:2]

        channels = 1 if len(image.shape)==2 else image.shape[2]

        memory = image.nbytes / (1024*1024)

        self.operation.setText(operation)

        self.time.setText(f"{elapsed:.2f} ms")

        self.size.setText(f"{w} × {h}")

        self.channels.setText(str(channels))

        self.memory.setText(f"{memory:.2f} MB")
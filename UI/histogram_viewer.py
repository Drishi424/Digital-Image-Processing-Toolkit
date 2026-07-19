import cv2
import numpy as np
import matplotlib.pyplot as plt

from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class HistogramViewer(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Histogram Analysis")
        self.resize(800, 500)

        layout = QVBoxLayout(self)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        layout.addWidget(self.canvas)

    # ------------------------------------------------

    def show_histogram(self, image):

        self.figure.clear()

        ax = self.figure.add_subplot(111)

        if len(image.shape) == 2:

            hist = cv2.calcHist(
                [image],
                [0],
                None,
                [256],
                [0,256]
            )

            ax.plot(hist,color="black")

        else:

            colors=("b","g","r")

            for i,c in enumerate(colors):

                hist=cv2.calcHist(
                    [image],
                    [i],
                    None,
                    [256],
                    [0,256]
                )

                ax.plot(hist,color=c)

        ax.set_title("Image Histogram")
        ax.set_xlabel("Pixel Intensity")
        ax.set_ylabel("Frequency")

        self.canvas.draw()
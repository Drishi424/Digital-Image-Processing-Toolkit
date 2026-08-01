import cv2
import numpy as np


class OCRPreprocessor:

    @staticmethod
    def grayscale(image):

        return cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

    # --------------------------------------------

    @staticmethod
    def clahe(image):

        gray = OCRPreprocessor.grayscale(image)

        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )

        return clahe.apply(gray)

    # --------------------------------------------

    @staticmethod
    def gaussian(image):

        return cv2.GaussianBlur(
            image,
            (5, 5),
            0
        )

    # --------------------------------------------

    @staticmethod
    def median(image):

        return cv2.medianBlur(
            image,
            3
        )

    # --------------------------------------------

    @staticmethod
    def bilateral(image):

        return cv2.bilateralFilter(
            image,
            9,
            75,
            75
        )

    # --------------------------------------------

    @staticmethod
    def adaptive_threshold(image):

        gray = OCRPreprocessor.grayscale(image)

        return cv2.adaptiveThreshold(

            gray,

            255,

            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,

            cv2.THRESH_BINARY,

            11,

            2

        )

    # --------------------------------------------

    @staticmethod
    def otsu(image):

        gray = OCRPreprocessor.grayscale(image)

        _, thresh = cv2.threshold(

            gray,

            0,

            255,

            cv2.THRESH_BINARY + cv2.THRESH_OTSU

        )

        return thresh

    # --------------------------------------------

    @staticmethod
    def denoise(image):

        return cv2.fastNlMeansDenoisingColored(

            image,

            None,

            10,

            10,

            7,

            21

        )

    # --------------------------------------------

    @staticmethod
    def sharpen(image):

        kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])

        return cv2.filter2D(
            image,
            -1,
            kernel
        )
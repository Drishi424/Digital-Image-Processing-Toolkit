import cv2
import numpy as np


class Morphology:

    def dilation(self, image, kernel_size=3, iterations=1):

        kernel = np.ones((kernel_size, kernel_size), np.uint8)

        return cv2.dilate(image, kernel, iterations=iterations)


    def erosion(self, image, kernel_size=3, iterations=1):

        kernel = np.ones((kernel_size, kernel_size), np.uint8)

        return cv2.erode(image, kernel, iterations=iterations)


    def opening(self, image, kernel_size=3):

        kernel = np.ones((kernel_size, kernel_size), np.uint8)

        return cv2.morphologyEx(
            image,
            cv2.MORPH_OPEN,
            kernel
        )


    def closing(self, image, kernel_size=3):

        kernel = np.ones((kernel_size, kernel_size), np.uint8)

        return cv2.morphologyEx(
            image,
            cv2.MORPH_CLOSE,
            kernel
        )


    def boundary_extraction(self, image, kernel_size=3):

        kernel = np.ones((kernel_size, kernel_size), np.uint8)

        eroded = cv2.erode(image, kernel)

        boundary = cv2.subtract(image, eroded)

        return boundary
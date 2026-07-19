import cv2
import numpy as np


class Transformation:

    def translation(self, image, tx=100, ty=100):
        """
        Translate an image.
        """

        rows, cols = image.shape[:2]

        matrix = np.array(
            [
                [1, 0, tx],
                [0, 1, ty]
            ],
            dtype=np.float32
        )

        translated = cv2.warpAffine(
            image,
            matrix,
            (cols, rows)
        )

        return translated


    def rotation(self, image, angle=45, scale=1.0):
        """
        Rotate an image.
        """

        rows, cols = image.shape[:2]

        center = (cols / 2, rows / 2)

        matrix = cv2.getRotationMatrix2D(
            center,
            angle,
            scale
        )

        rotated = cv2.warpAffine(
            image,
            matrix,
            (cols, rows)
        )

        return rotated


    def scaling(self, image, scale=1.0):


        scaled = cv2.resize(
            image,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_LINEAR
        )

        return scaled


    def affine_transformation(self, image):
        """
        Apply Affine Transformation.
        """

        rows, cols = image.shape[:2]

        pts1 = np.array(
            [
                [50, 50],
                [200, 50],
                [50, 200]
            ],
            dtype=np.float32
        )

        pts2 = np.array(
            [
                [10, 100],
                [200, 50],
                [100, 250]
            ],
            dtype=np.float32
        )

        matrix = cv2.getAffineTransform(
            pts1,
            pts2
        )

        affine = cv2.warpAffine(
            image,
            matrix,
            (cols, rows)
        )

        return affine
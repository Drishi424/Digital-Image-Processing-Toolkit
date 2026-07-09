import cv2


class Filtering:

    def mean_filter(self, image, kernel_size=3):
        """
        Apply Mean Filter.
        """

        if kernel_size % 2 == 0:
            raise ValueError("Kernel size must be odd.")

        return cv2.blur(image, (kernel_size, kernel_size))


    def median_filter(self, image, kernel_size=3):
        """
        Apply Median Filter.
        """

        if kernel_size % 2 == 0:
            raise ValueError("Kernel size must be odd.")

        return cv2.medianBlur(image, kernel_size)


    def gaussian_filter(self, image, kernel_size=3, sigma=0):
        """
        Apply Gaussian Filter.
        """

        if kernel_size % 2 == 0:
            raise ValueError("Kernel size must be odd.")

        return cv2.GaussianBlur(
            image,
            (kernel_size, kernel_size),
            sigma
        )
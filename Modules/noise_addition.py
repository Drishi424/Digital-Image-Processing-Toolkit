import cv2
import numpy as np


class Noise:

    def salt_pepper_noise(self, image, amount=0.05):

        if not 0 <= amount <= 1:
            raise ValueError("Amount must be between 0 and 1.")

        noisy = image.copy()
        h, w = image.shape[:2]

        total_pixels = h * w
        noisy_pixels = int(total_pixels * amount)

        salt = noisy_pixels // 2
        pepper = noisy_pixels - salt

        # Salt
        row = np.random.randint(0, h, salt)
        col = np.random.randint(0, w, salt)

        if image.ndim == 2:
            noisy[row, col] = 255
        else:
            noisy[row, col] = [255, 255, 255]

        # Pepper
        row = np.random.randint(0, h, pepper)
        col = np.random.randint(0, w, pepper)

        if image.ndim == 2:
            noisy[row, col] = 0
        else:
            noisy[row, col] = [0, 0, 0]

        return noisy


    def gaussian_noise(self, image, mean=0, sigma=25):
        """
        Add Gaussian Noise.

        Parameters:
            image : numpy.ndarray
            mean : int
            sigma : int

        Returns:
            Noisy Image
        """

        image = image.astype(np.float32)

        gaussian = np.random.normal(
            mean,
            sigma,
            image.shape
        )

        noisy = image + gaussian
        noisy = np.clip(noisy, 0, 255)
        return noisy.astype(np.uint8)
import cv2
import numpy as np


class FrequencyDomain:

    def fourier_transform(self, image):
        """
        Compute Fourier Transform and return the magnitude spectrum.
        """

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)

        magnitude = 20 * np.log(np.abs(fshift) + 1)

        magnitude = cv2.normalize(
            magnitude,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        )

        return magnitude.astype(np.uint8)


    def low_pass_filter(self, image, radius=30):
        """
        Apply Ideal Low Pass Filter.
        """

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        rows, cols = gray.shape
        crow, ccol = rows // 2, cols // 2

        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)

        mask = np.zeros((rows, cols), np.uint8)
        cv2.circle(mask, (ccol, crow), radius, 1, -1)

        filtered = fshift * mask

        ishift = np.fft.ifftshift(filtered)
        img_back = np.fft.ifft2(ishift)
        img_back = np.abs(img_back)

        img_back = cv2.normalize(
            img_back,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        )

        return img_back.astype(np.uint8)


    def high_pass_filter(self, image, radius=30):
        """
        Apply Ideal High Pass Filter.
        """

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        rows, cols = gray.shape
        crow, ccol = rows // 2, cols // 2

        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)

        mask = np.ones((rows, cols), np.uint8)
        cv2.circle(mask, (ccol, crow), radius, 0, -1)

        filtered = fshift * mask

        ishift = np.fft.ifftshift(filtered)
        img_back = np.fft.ifft2(ishift)
        img_back = np.abs(img_back)

        img_back = cv2.normalize(
            img_back,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        )

        return img_back.astype(np.uint8)


    def butterworth_filter(self, image, cutoff=30, order=2):
        """
        Apply Butterworth Low Pass Filter.
        """

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        rows, cols = gray.shape
        crow, ccol = rows // 2, cols // 2

        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)

        x = np.arange(cols)
        y = np.arange(rows)

        X, Y = np.meshgrid(x, y)

        D = np.sqrt((X - ccol) ** 2 + (Y - crow) ** 2)

        H = 1 / (1 + (D / cutoff) ** (2 * order))

        filtered = fshift * H

        ishift = np.fft.ifftshift(filtered)

        img_back = np.fft.ifft2(ishift)

        img_back = np.abs(img_back)

        img_back = cv2.normalize(
            img_back,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        )

        return img_back.astype(np.uint8)


    def gaussian_filter(self, image, sigma=30):
        """
        Apply Gaussian Low Pass Filter.
        """

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        rows, cols = gray.shape
        crow, ccol = rows // 2, cols // 2

        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)

        x = np.arange(cols)
        y = np.arange(rows)

        X, Y = np.meshgrid(x, y)

        D2 = (X - ccol) ** 2 + (Y - crow) ** 2

        H = np.exp(-(D2) / (2 * sigma ** 2))

        filtered = fshift * H

        ishift = np.fft.ifftshift(filtered)

        img_back = np.fft.ifft2(ishift)

        img_back = np.abs(img_back)

        img_back = cv2.normalize(
            img_back,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        )

        return img_back.astype(np.uint8)
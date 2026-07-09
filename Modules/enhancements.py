import cv2
import numpy as np
from skimage.exposure import match_histograms

class Enhancements:
    @staticmethod
    def negative(image):
        result = cv2.bitwise_not(image)
        return result

    @staticmethod
    def log_transform(image):
        image = image.astype(np.float32)
        c = 255/np.log(1+255)
        log_image = c * np.log(1 + image)
        return cv2.convertScaleAbs(log_image)

    @staticmethod
    def gamma_transform(image, gamma=1.0):
        inv_gamma = 1.0 / gamma
        table = np.array(
            [((i / 255.0) ** inv_gamma) * 255 for i in np.arange(256)],
            dtype=np.uint8
        )
        return cv2.LUT(image, table)   

    @staticmethod
    def contrast_stretch(image):
        return cv2.normalize(
            image,
            None,
            alpha=0,
            beta=255,
            norm_type=cv2.NORM_MINMAX
        )

    @staticmethod
    def histogram_equalization(image):
        # Handle grayscale and color images
        if len(image.shape) == 2 or image.ndim == 2:
            return cv2.equalizeHist(image)
        b, g, r = cv2.split(image)
        return cv2.merge([cv2.equalizeHist(b), cv2.equalizeHist(g), cv2.equalizeHist(r)])

    @staticmethod
    def histogram_matching(source, reference):
        matched = match_histograms(
            source,
            reference,
            channel_axis=-1
        )
        return matched.astype(np.uint8)

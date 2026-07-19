import cv2
import numpy as np


class EdgeDetection:

    def roberts(self, image):

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        kernel_x = np.array([[1, 0],
                             [0, -1]], dtype=np.float32)

        kernel_y = np.array([[0, 1],
                             [-1, 0]], dtype=np.float32)

        gx = cv2.filter2D(gray, -1, kernel_x)
        gy = cv2.filter2D(gray, -1, kernel_y)

        roberts = cv2.addWeighted(
            cv2.convertScaleAbs(gx),
            0.5,
            cv2.convertScaleAbs(gy),
            0.5,
            0
        )

        return roberts


    def prewitt(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        kernel_x = np.array([[-1, 0, 1],
                            [-1, 0, 1],
                            [-1, 0, 1]], dtype=np.float32)
        kernel_y = np.array([[1, 1, 1],
                            [0, 0, 0],
                            [-1, -1, -1]], dtype=np.float32)
        
        gx = cv2.filter2D(gray, -1, kernel_x)
        gy = cv2.filter2D(gray, -1, kernel_y)
        
        abs_gx = cv2.convertScaleAbs(gx)
        abs_gy = cv2.convertScaleAbs(gy)
        
        prewitt_edges = cv2.addWeighted(abs_gx, 0.5, abs_gy, 0.5, 0)
        
        return prewitt_edges

    def sobel(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)

        sobel = cv2.magnitude(gx, gy)

        return cv2.convertScaleAbs(sobel)

    def laplacian(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        lap = cv2.Laplacian(gray, cv2.CV_64F)

        return cv2.convertScaleAbs(lap)

    def canny(self, image, threshold1=100, threshold2=200):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        canny_edges = cv2.Canny(gray, threshold1, threshold2)

        return canny_edges
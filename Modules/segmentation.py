import cv2
import numpy as np


class Segmentation:

    def threshold(self, image, threshold=127,
                  max_value=255,
                  threshold_type=cv2.THRESH_BINARY):

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        _, segmented = cv2.threshold(
            gray,
            threshold,
            max_value,
            threshold_type
        )

        return segmented


    def region_growing(self, image, seed_point, threshold=10):

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        h, w = gray.shape

        segmented = np.zeros_like(gray)

        visited = np.zeros_like(gray, dtype=bool)

        stack = [seed_point]

        seed_value = gray[seed_point[1], seed_point[0]]

        while stack:

            x, y = stack.pop()

            if x < 0 or x >= w or y < 0 or y >= h:
                continue

            if visited[y, x]:
                continue

            visited[y, x] = True

            if abs(int(gray[y, x]) - int(seed_value)) <= threshold:

                segmented[y, x] = 255

                stack.extend([
                    (x + 1, y),
                    (x - 1, y),
                    (x, y + 1),
                    (x, y - 1)
                ])

        return segmented


    def watershed(self, image):

        img = image.copy()

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        _, thresh = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        kernel = np.ones((3, 3), np.uint8)

        opening = cv2.morphologyEx(
            thresh,
            cv2.MORPH_OPEN,
            kernel,
            iterations=2
        )

        sure_bg = cv2.dilate(opening, kernel, iterations=3)

        dist = cv2.distanceTransform(
            opening,
            cv2.DIST_L2,
            5
        )

        _, sure_fg = cv2.threshold(
            dist,
            0.7 * dist.max(),
            255,
            0
        )

        sure_fg = np.uint8(sure_fg)

        unknown = cv2.subtract(sure_bg, sure_fg)

        _, markers = cv2.connectedComponents(sure_fg)

        markers += 1

        markers[unknown == 255] = 0

        markers = cv2.watershed(img, markers)

        img[markers == -1] = [0, 0, 255]

        return img
import cv2
import os
import heapq
from collections import Counter

class Compression:
    def run_length_encoding(self, image):
        """
        Apply Run Length Encoding and return statistics.
        """

        flat = image.flatten()

        encoded = []

        count = 1
        previous = flat[0]

        for pixel in flat[1:]:

            if pixel == previous:
                count += 1
            else:
                encoded.append((int(previous), count))
                previous = pixel
                count = 1

        encoded.append((int(previous), count))

        original_entries = len(flat)
        compressed_entries = len(encoded)

        ratio = original_entries / compressed_entries

        return {
            "algorithm": "Run Length Encoding",
            "original_entries": original_entries,
            "compressed_entries": compressed_entries,
            "compression_ratio": round(ratio, 2)
        }
    
    def huffman_encoding(self, image):
        """
        Build Huffman Codes and return statistics.
        """

        flat = image.flatten()

        frequency = Counter(flat)

        heap = [[weight, [symbol, ""]] for symbol, weight in frequency.items()]
        heapq.heapify(heap)

        while len(heap) > 1:

            low = heapq.heappop(heap)
            high = heapq.heappop(heap)

            for pair in low[1:]:
                pair[1] = "0" + pair[1]

            for pair in high[1:]:
                pair[1] = "1" + pair[1]

            heapq.heappush(
                heap,
                [low[0] + high[0]] + low[1:] + high[1:]
            )

        codes = sorted(
            heapq.heappop(heap)[1:],
            key=lambda p: (len(p[1]), p)
        )

        codes = dict(codes)

        average_length = sum(
            len(codes[p]) * frequency[p]
            for p in frequency
        ) / len(flat)

        return {
            "algorithm": "Huffman Coding",
            "symbols": len(codes),
            "average_code_length": round(average_length, 2)
        }
    
    def jpeg_compression(self, image, output_path, quality=50):
        """
        Save image using JPEG compression.
        """

        cv2.imwrite(
            output_path,
            image,
            [cv2.IMWRITE_JPEG_QUALITY, quality]
        )

        return output_path


    def compression_ratio(self, original_path, compressed_path):
        """
        Calculate Compression Ratio.
        """

        original_size = os.path.getsize(original_path)

        compressed_size = os.path.getsize(compressed_path)

        ratio = original_size / compressed_size

        return round(ratio, 2)


    def file_size_comparison(self, original_path, compressed_path):
        """
        Return original and compressed file sizes.
        """

        original_size = os.path.getsize(original_path) / 1024

        compressed_size = os.path.getsize(compressed_path) / 1024

        return {
            "Original (KB)": round(original_size, 2),
            "Compressed (KB)": round(compressed_size, 2)
        }
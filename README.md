## Digital Image Prossessing Toolkit

This project is a Python-based image processing demonstration. It uses OpenCV, NumPy, and scikit-image to apply a variety of image enhancement, noise addition, and filtering operations to a sample input image.

## Project Overview

The repository includes a simple pipeline in `main.py` that loads an image from `Images/sample.jpeg`, performs several processing operations, and writes the results to `Images/output/`.

## Key Features

- Image enhancements:
  - Negative transformation
  - Logarithmic transformation
  - Gamma correction
  - Contrast stretching
  - Histogram equalization
  - Histogram matching against `Images/reference.jpg` (if present)
- Noise synthesis:
  - Salt and pepper noise
  - Gaussian noise
- Filtering:
  - Mean filter
  - Median filter
  - Gaussian filter

## Project Structure

- `main.py` - Entry point for running the image processing pipeline.
- `Modules/enhancements.py` - Implements enhancement operations.
- `Modules/noise_addition.py` - Implements salt & pepper and Gaussian noise generation.
- `Modules/filtering.py` - Implements mean, median, and Gaussian smoothing filters.
- `Images/` - Contains input images and output directory for generated results.
- `requirements.txt` - Python dependencies required to run the project.

## Dependencies

Install the required packages with:

```bash
pip install -r requirements.txt
```

Dependencies:
- numpy
- opencv-python
- scikit-image

## Usage

Run the project with:

```bash
python main.py
```

After running, the processed images are saved in `Images/output/`.

## Notes

- If `Images/reference.jpg` is not found, histogram matching is skipped and a warning is printed.
- The code assumes a valid image exists at `Images/sample.jpeg`.

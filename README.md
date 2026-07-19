## Digital Image Processing Toolkit

DIP Studio is a Python-based desktop GUI application for interactive image processing. Built with PySide6, OpenCV, NumPy, and scikit-image, it lets you open an image, apply processing algorithms in real time, and compare results side by side.

## Project Overview

The application launches a full windowed interface (`main.py`) where you can load any image, select a processing module from the sidebar, tune parameters in the property panel, and view the original and processed images simultaneously.

## Key Features

- Image enhancements:
  - Negative transformation
  - Logarithmic transformation
  - Gamma correction
  - Contrast stretching
  - Histogram equalization
  - Histogram matching against `Images/reference.jpg`
- Noise synthesis:
  - Salt and pepper noise
  - Gaussian noise
- Spatial filtering:
  - Mean filter
  - Median filter
  - Gaussian filter
- Edge detection:
  - Roberts, Prewitt, Sobel, Laplacian, Canny
- Segmentation:
  - Threshold, Region Growing, Watershed
- Frequency domain:
  - Fourier Transform
  - Ideal Low Pass / High Pass filters
  - Butterworth filter
  - Gaussian filter
- Morphological operations:
  - Dilation, Erosion, Opening, Closing, Boundary Extraction
- Geometric transformations:
  - Translation, Rotation, Scaling, Affine
- Compression:
  - Run Length Encoding (statistics report)
  - Huffman Coding (statistics report)
  - JPEG Compression (quality control + file size report)
- Undo / Redo history
- Before / After comparison viewer
- Histogram viewer
- Image statistics panel
- Recent files list
- Dark theme

## Project Structure

```
├── main.py                     # Application entry point
├── Core/
│   ├── image_manager.py        # Image state, undo/redo stack
│   ├── processor.py            # Aggregates all processing modules
│   └── utils.py                # Resource path helper (PyInstaller compatible)
├── Modules/
│   ├── enhancements.py         # Enhancement operations
│   ├── noise_addition.py       # Noise generation
│   ├── filtering.py            # Spatial filters
│   ├── edge_detection.py       # Edge detection algorithms
│   ├── segmentation.py         # Segmentation algorithms
│   ├── frequency_domain.py     # Frequency domain filters
│   ├── morphological.py        # Morphological operations
│   ├── transformation.py       # Geometric transformations
│   └── compression.py          # Compression algorithms
├── UI/
│   ├── main_window.py          # Main application window
│   ├── sidebar.py              # Module navigation sidebar
│   ├── image_viewer.py         # Zoomable image display widget
│   ├── property_panel.py       # Algorithm selector and parameter controls
│   ├── comparison_viewer.py    # Before/after comparison window
│   ├── histogram_viewer.py     # Histogram display window
│   ├── statistics_panel.py     # Image statistics panel
│   ├── compression_report.py   # Compression results dialog
│   ├── about_dialog.py         # About dialog
│   └── welcome_screen.py       # Welcome / landing screen
├── Assets/icons/               # Toolbar and application icons
├── Themes/dark.qss             # Dark stylesheet
├── Images/                     # Sample and reference images
│   └── output/                 # Output directory for saved results
└── requirements.txt
```

## Dependencies

Install the required packages with:

```bash
pip install -r requirements.txt
```

Dependencies:
- numpy
- opencv-python
- scikit-image
- PySide6

## Usage

```bash
python main.py
```

This opens the DIP Studio window. Use **File > Open Image** (or `Ctrl+O`) to load an image, then select a module from the sidebar and click **Apply**.

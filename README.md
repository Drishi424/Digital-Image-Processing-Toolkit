# DIP Studio — Digital Image Processing & AI Toolkit

DIP Studio is a professional Python desktop application for interactive digital image processing, AI object detection, real-time video/webcam vision, and optical character recognition (OCR). Built with PySide6, OpenCV, NumPy, Ultralytics YOLO, EasyOCR, and PyTorch, it features an intuitive dark-themed GUI with asynchronous non-blocking processing, native drag-and-drop support, real-time analytics, and metadata export capabilities.

---

## 🌟 Key Features

### 🖼️ Traditional Digital Image Processing
- **Image Enhancements**: Negative, Logarithmic, Gamma Correction, Contrast Stretching, Histogram Equalization, Histogram Matching (against reference image).
- **Noise Synthesis**: Salt & Pepper noise, Gaussian noise.
- **Spatial Filtering**: Mean, Median, and Gaussian spatial filters.
- **Edge Detection**: Roberts, Prewitt, Sobel, Laplacian, and Canny edge operators.
- **Segmentation**: Thresholding, Region Growing, and Watershed segmentation.
- **Frequency Domain**: Fourier Transform, Ideal Low-Pass & High-Pass filters, Butterworth filter, Gaussian frequency filter.
- **Morphological Operations**: Dilation, Erosion, Opening, Closing, and Boundary Extraction.
- **Geometric Transformations**: Translation, Rotation, Scaling, and Affine transformation.
- **Image Compression**:
  - Run Length Encoding (RLE) with compression ratio statistics.
  - Huffman Coding with average code length metrics.
  - JPEG Compression with interactive quality control and file size report.

### 🤖 AI Vision & Object Detection
- **AI Model Management**: Dynamic model switching between standard **YOLO11n** (`yolo11n.pt`) and custom-trained **Drone Detector** (`AI_training/Models/drone_best.pt`) with in-memory model weight caching.
- **Non-Blocking Asynchronous Processing**: Background `QThread` workers eliminate GUI freezes ("Not Responding") during model loading and AI inference.
- **Image Object Detection**: Runs YOLO inference on images asynchronously, updating dashboard metrics (inference time, object counts, average & highest confidence).
- **Video & Live Webcam Streaming**: Real-time object detection on `.mp4`/`.avi`/`.mov`/`.mkv` videos and live webcams with Start, Pause, Resume, Stop, and smooth FPS tracking.
- **AI Dashboard & Analytics**: Displays Model name, Source, Status, Hardware Device (CUDA vs CPU), Resolution, Inference time (ms), FPS, Detected Objects breakdown, Average Confidence (%), and Max Confidence (%).
- **Detection History**: Logs past detection runs with timestamps (up to 100 entries) with a "Clear History" button.
- **Save & Export Results**: Save annotated detection images and export detection metadata to **JSON**, **CSV**, or **TXT**.

### 📝 Optical Character Recognition (OCR)
- **EasyOCR Integration**: Text extraction using EasyOCR with CLAHE contrast preprocessing.
- **Non-Blocking Execution**: Asynchronous OCR worker thread keeps UI responsive.
- **OCR Results Dialog**: Displays extracted text, word/character/line counts, average confidence, processing time, copy to clipboard, TXT export, and PDF export (via ReportLab).

### 🖱️ Drag and Drop & UX Polish
- **Native Drag and Drop**: Drop image files (`.jpg`, `.png`, `.bmp`, `.tif`, `.webp`) or video files (`.mp4`, `.avi`, `.mov`, `.mkv`) directly onto the Welcome Screen, Image Viewers, or Main Window.
- **Memory & Resource Safety**: Undo/Redo stack depth capped to 20 steps to prevent RAM ballooning. Safe worker thread termination and camera device release on application exit.
- **Utilities**: Interactive Zoom in (+), Zoom out (-), Fit to window, Before/After side-by-side comparison, Matplotlib Histogram viewer, and Image Statistics panel.

---

## 📁 Project Structure

```
├── main.py                     # Application entry point & QSS setup
├── Core/
│   ├── image_manager.py        # Image state, undo/redo stack (max 20 steps)
│   ├── processor.py            # Aggregates traditional DIP modules
│   └── utils.py                # PyInstaller-compatible resource path helper
├── Modules/
│   ├── enhancements.py         # Image enhancement algorithms
│   ├── noise_addition.py       # Noise synthesis algorithms
│   ├── filtering.py            # Spatial filtering algorithms
│   ├── edge_detection.py       # Edge detection operators
│   ├── segmentation.py         # Image segmentation algorithms
│   ├── frequency_domain.py     # Frequency domain filters (FFT)
│   ├── morphological.py        # Morphological operations
│   ├── transformation.py       # Geometric transformation algorithms
│   ├── compression.py          # RLE, Huffman, JPEG compression
│   └── ai/
│       ├── model_manager.py    # YOLO model manager & weight caching
│       ├── workers.py          # QThread workers (model load, YOLO, OCR)
│       ├── detector.py         # YOLO detection wrapper
│       ├── stream_detector.py  # QThread for video & webcam detection
│       ├── ocr.py              # EasyOCR detection & annotation
│       └── preprocessing.py    # OCR image preprocessors (CLAHE, thresholding)
├── UI/
│   ├── main_window.py          # Main application window & event wiring
│   ├── ai_dashboard.py         # AI control, confidence sliders, history & export
│   ├── sidebar.py              # Module navigation sidebar
│   ├── image_viewer.py         # Zoomable display widget with drag-and-drop
│   ├── property_panel.py       # Algorithm selector and parameter controls
│   ├── comparison_viewer.py    # Before/after comparison window
│   ├── histogram_viewer.py     # Matplotlib histogram display window
│   ├── statistics_panel.py     # Image statistics panel
│   ├── compression_report.py   # Compression results dialog
│   ├── about_dialog.py         # About dialog
│   ├── welcome_screen.py       # Landing screen with drag-and-drop
│   └── dialogs/
│       └── ocr_result_dialog.py # OCR text viewer, stats, clipboard & PDF export
├── AI_training/
│   └── Models/
│       └── drone_best.pt       # Custom trained drone detection model
├── Assets/icons/               # Application toolbar and window icons
├── Themes/dark.qss             # Dark QSS stylesheet
├── Images/                     # Sample and reference images
│   └── output/                 # Output directory for compressed & saved results
├── yolo11n.pt                  # Pretrained YOLO11n weights
└── requirements.txt            # Python dependencies
```

---

## 🛠️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/drishi/dip-studio.git
   cd "Digital Image Processing Toolkit"
   ```

2. **Set up Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   *Core dependencies*: `PySide6`, `opencv-python`, `numpy`, `scikit-image`, `ultralytics`, `easyocr`, `torch`, `reportlab`.

---

## 🚀 Running the Application

Run DIP Studio using Python:

```bash
python main.py
```

Or directly via virtual environment:

```powershell
.\venv\Scripts\python.exe main.py
```

### 💡 Quick Start Guide
1. **Open Image/Video**: Drag & drop any image (`.jpg`/`.png`) or video (`.mp4`) into the workspace, or click **📂 Open Image** (`Ctrl+O`).
2. **Apply DIP Algorithms**: Select a category from the left sidebar (e.g., *Filtering*, *Edge Detection*, *Morphology*), adjust parameters in the right panel, and click **Apply**.
3. **AI Vision & Object Detection**: In the **AI Vision** menu or AI Dashboard, select a model (**YOLO11n** or **Drone Detector**), adjust the confidence slider, and click **Object Detection** or **Video Detection**.
4. **Export Results**: Click **💾 Save Result** to save annotated images or **📊 Export Data** to export detection metadata to JSON, CSV, or TXT formats.
5. **OCR Text Extraction**: Select **AI Vision > Image OCR** to extract text from images and copy or export as TXT/PDF.

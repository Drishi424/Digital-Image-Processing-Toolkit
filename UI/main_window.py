from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QSplitter,
    QStatusBar,
    QToolBar,
    QWidget,
)
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QStackedWidget
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSettings

import os
import time
import cv2
from functools import partial

from UI.sidebar import Sidebar
from UI.image_viewer import ImageViewer
from UI.property_panel import PropertyPanel
from UI.compression_report import CompressionReport
from UI.comparison_viewer import ComparisonViewer
from UI.histogram_viewer import HistogramViewer
from UI.statistics_panel import StatisticsPanel
from UI.about_dialog import AboutDialog
from UI.welcome_screen import WelcomeScreen

from Core.image_manager import ImageManager
from Core.processor import Processor
from Core.utils import resource_path


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.algorithm_map = self.create_algorithm_map()
        self.setWindowIcon(QIcon((resource_path("Assets/icons/app_icon.ico"))))

        self.image_manager = ImageManager()
        self.processor = Processor()
        self.comparison = ComparisonViewer()
        self.histogram = HistogramViewer()
        self.statistics = StatisticsPanel()
        self.compression_report = CompressionReport()
        self.about = AboutDialog()
        self.welcome = WelcomeScreen()

        self.setWindowTitle("DIP Studio")
        self.resize(1600, 900)
        self.setMinimumSize(1200, 700)
        self.recent_files = []
        self.max_recent_files = 10

        self.create_menu()
        self.create_toolbar()
        self.create_statusbar()
        self.create_ui()

        self.settings = QSettings(
            "JECRC",
            "DigitalImageProcessingToolkit"
        )

        self.recent_files = self.settings.value(
            "recent_files",
            [],
            type=list
        )

        self.max_recent_files = 10

    # ==================================================
    # Menu Bar
    # ==================================================

    def create_menu(self):

        menu = self.menuBar()

        file_menu = menu.addMenu("File")
        edit_menu = menu.addMenu("Edit")
        
        view_menu = menu.addMenu("View")
        compare_action = QAction("Before / After", self)
        compare_action.triggered.connect(self.open_comparison)
        view_menu.addAction(compare_action)

        histogram_action = QAction("Histogram", self)
        histogram_action.triggered.connect(self.open_histogram)
        view_menu.addAction(histogram_action)

        statistics_action = QAction("Statistics", self)
        statistics_action.triggered.connect(
            self.statistics.show
        )
        view_menu.addAction(statistics_action)

        help_menu = menu.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.about.exec)

        # Open
        open_action = QAction("Open Image", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_image)

        # Save
        save_action = QAction("Save Image", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_image)

        # Reset
        reset_action = QAction("Reset Image", self)
        reset_action.setShortcut("Ctrl+R")
        reset_action.triggered.connect(self.reset_image)

        # Exit
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)

        # Undo
        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.undo_image)

        # Redo
        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.redo_image)

        # Edit
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)

        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(reset_action)
        file_menu.addSeparator()
        self.recent_menu = file_menu.addMenu("Recent Files")
        self.update_recent_menu()
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        help_menu.addAction(about_action)

    # ==================================================
    # Toolbar
    # ==================================================

    def create_toolbar(self):

        toolbar = QToolBar("Toolbar")

        self.addToolBar(toolbar)
        toolbar.setIconSize(QSize(28,28))
        toolbar.setToolButtonStyle(
            Qt.ToolButtonIconOnly
        )

        open_action = QAction(
        QIcon(resource_path("Assets/icons/open.png")),
        "Open",
        self
        )
        open_action.triggered.connect(self.open_image)
        toolbar.addAction(open_action)

        save_action = QAction(
            QIcon(resource_path("Assets/icons/save.png")),
            "Save",
            self
        )
        save_action.triggered.connect(self.save_image)
        toolbar.addAction(save_action)

        reset_action = QAction(
            QIcon(resource_path("Assets/icons/reset.png")),
            "Reset",
            self
        )
        reset_action.triggered.connect(self.reset_image)
        toolbar.addAction(reset_action)        

        toolbar.addSeparator()

        undo_action = QAction(
            QIcon(resource_path("Assets/icons/undo.png")),
            "Undo",
            self
        )
        undo_action.triggered.connect(self.undo_image)

        redo_action = QAction(
            QIcon(resource_path("Assets/icons/redo.png")),
            "Redo",
            self
        )
        redo_action.triggered.connect(self.redo_image)

        toolbar.addAction(undo_action)
        toolbar.addAction(redo_action)

        toolbar.addSeparator()

        zoom_in_action = QAction(
            QIcon(resource_path("Assets/icons/zoom_in.png")),
            "Zoom +",
            self
        )
        zoom_in_action.triggered.connect(self.zoom_in)

        zoom_out_action = QAction(
            QIcon(resource_path("Assets/icons/zoom_out.png")),
            "Zoom -",
            self
        )
        zoom_out_action.triggered.connect(self.zoom_out)

        fit_action = QAction(
            QIcon(resource_path("Assets/icons/fit.png")),
            "Fit",
            self
        )
        fit_action.triggered.connect(self.fit_image)

        toolbar.addAction(zoom_in_action)
        toolbar.addAction(zoom_out_action)
        toolbar.addAction(fit_action)

    # ==================================================
    # Status Bar
    # ==================================================

    def create_statusbar(self):

        status = QStatusBar()

        status.showMessage("Ready")

        self.setStatusBar(status)

    # ==================================================
    # Main UI
    # ==================================================

    def create_ui(self):

        splitter = QSplitter(Qt.Horizontal)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.itemClicked.connect(self.change_module)
        self.sidebar.currentItemChanged.connect(self.change_module)

        # Workspace
        workspace = QWidget()

        layout = QHBoxLayout(workspace)

        self.original = ImageViewer("Original Image")
        self.processed = ImageViewer("Processed Image")

        layout.addWidget(self.original)
        layout.addWidget(self.processed)

        # Property Panel
        self.properties = PropertyPanel()
        self.properties.algorithm_list.currentItemChanged.connect(
            self.update_parameters
        )
        self.properties.apply_button.clicked.connect(self.apply_algorithm)

        splitter.addWidget(self.sidebar)
        splitter.addWidget(workspace)
        splitter.addWidget(self.properties)

        splitter.setStretchFactor(1, 8)

        # -------------------------------
        # Welcome Screen
        # -------------------------------

        self.stack = QStackedWidget()

        self.welcome = WelcomeScreen()
        self.welcome.openRequested.connect(self.open_image)

        self.stack.addWidget(self.welcome)   # Index 0
        self.stack.addWidget(splitter)       # Index 1

        self.setCentralWidget(self.stack)

    # ==================================================
    # Open Image
    # ==================================================

    def open_image(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tif)"
        )

        if not file_path:
            return

        try:
            image = self.image_manager.load_image(file_path)

            self.original.set_image(image)
            self.processed.set_image(image)

            self.add_recent_file(file_path)

            self.stack.setCurrentIndex(1)

            self.statusBar().showMessage(f"Loaded: {file_path}")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Open Image",
                str(e)
            )

    # ==================================================
    # Change Module
    # ==================================================

    def change_module(self, current, previous = None):

        if current is None:
            return

        module = current.text()

        if "Open Image" in module:
            self.open_image()
            return

        elif "Save Image" in module:
            self.save_image()
            return

        if "Enhancement" in module:

            self.properties.set_algorithms([
                "Negative",
                "Log Transform",
                "Gamma",
                "Contrast Stretch",
                "Histogram Equalization",
                "Histogram Matching"
            ])

        elif "Noise" in module:

            self.properties.set_algorithms([
                "Salt & Pepper",
                "Gaussian Noise"
            ])

        elif "Filtering" in module:

            self.properties.set_algorithms([
                "Mean Filter",
                "Median Filter",
                "Gaussian Filter"
            ])

        elif "Edge" in module:

            self.properties.set_algorithms([
                "Roberts",
                "Prewitt",
                "Sobel",
                "Laplacian",
                "Canny"
            ])

        elif "Segmentation" in module:

            self.properties.set_algorithms([
                "Threshold",
                "Region Growing",
                "Watershed"
            ])

        elif "Frequency" in module:

            self.properties.set_algorithms([
                "Fourier Transform",
                "Low Pass",
                "High Pass",
                "Butterworth",
                "Gaussian"
            ])

        elif "Morphology" in module:

            self.properties.set_algorithms([
                "Dilation",
                "Erosion",
                "Opening",
                "Closing",
                "Boundary Extraction"
            ])

        elif "Compression" in module:

            self.properties.set_algorithms([
                "Run Length Encoding",
                "Huffman Coding",
                "JPEG Compression"
            ])

        elif "Transformation" in module:

            self.properties.set_algorithms([
                "Translation",
                "Rotation",
                "Scaling",
                "Affine"
            ])

        else:
            self.properties.set_algorithms([])
    

    def create_algorithm_map(self):

        reference = cv2.imread(resource_path("Images/reference.jpg"))

        return {

            # -------- Enhancement -------- #

            "Negative": lambda img: self.processor.enhancement.negative(img),

            "Log Transform": lambda img: self.processor.enhancement.log_transform(img),

            "Gamma": lambda img: self.processor.enhancement.gamma_transform(
                img,
                gamma=self.properties.value("Gamma")
            ),

            "Contrast Stretch": lambda img: self.processor.enhancement.contrast_stretch(img),

            "Histogram Equalization": lambda img: self.processor.enhancement.histogram_equalization(img),

            "Histogram Matching": lambda img: self.processor.enhancement.histogram_matching(
                img,
                reference
            ),

            # -------- Noise -------- #

            "Salt & Pepper": lambda img: self.processor.noise.salt_pepper_noise(img),

            "Gaussian Noise": lambda img: self.processor.noise.gaussian_noise(img),

            # -------- Filtering -------- #

            "Mean Filter": lambda img: self.processor.filtering.mean_filter(
                img,
                kernel_size=self.properties.value("Kernel Size")),

            "Median Filter": lambda img: self.processor.filtering.median_filter(
                img,
                kernel_size=self.properties.value("Kernel Size")),

            "Gaussian Filter": lambda img: self.processor.filtering.gaussian_filter(
                img,
                kernel_size=self.properties.value("Kernel Size")),

            # -------- Edge Detection -------- #

            "Roberts": lambda img: self.processor.edge.roberts(img),

            "Prewitt": lambda img: self.processor.edge.prewitt(img),

            "Sobel": lambda img: self.processor.edge.sobel(img),

            "Laplacian": lambda img: self.processor.edge.laplacian(img),

            "Canny": lambda img: self.processor.edge.canny(img),

            # -------- Segmentation -------- #

            "Threshold": lambda img: self.processor.segmentation.threshold(img),

            "Region Growing": lambda img: self.processor.segmentation.region_growing(
                img,
                seed_point=(100, 100)
            ),

            "Watershed": lambda img: self.processor.segmentation.watershed(img),

            # -------- Frequency -------- #

            "Fourier Transform": lambda img: self.processor.frequency.fourier_transform(img),

            "Low Pass": lambda img: self.processor.frequency.low_pass_filter(img),

            "High Pass": lambda img: self.processor.frequency.high_pass_filter(img),

            "Butterworth": lambda img: self.processor.frequency.butterworth_filter(img),

            "Gaussian": lambda img: self.processor.frequency.gaussian_filter(img),

            # -------- Morphology -------- #

            "Dilation": lambda img: self.processor.morphology.dilation(img),

            "Erosion": lambda img: self.processor.morphology.erosion(img),

            "Opening": lambda img: self.processor.morphology.opening(img),

            "Closing": lambda img: self.processor.morphology.closing(img),

            "Boundary Extraction": lambda img: self.processor.morphology.boundary_extraction(img),

            # -------- Transformation -------- #

            "Translation": lambda img: self.processor.transformation.translation(
                img,
                tx=self.properties.value("X"),
                ty=self.properties.value("Y")),

            "Rotation": lambda img: self.processor.transformation.rotation(
                img,
                angle=self.properties.value("Angle")),

            "Scaling": lambda img: self.processor.transformation.scaling(
                img,
                scale=self.properties.value("Scale")),

            "Affine": lambda img: self.processor.transformation.affine_transformation(img),

            # -------- Compression -------- #

            "Run Length Encoding": lambda img:
                self.processor.compression.run_length_encoding(img),

            "Huffman Coding": lambda img:
                self.processor.compression.huffman_encoding(img),
        }
    
    # ==================================================
    # Selected Algorithm button
    # ==================================================
    
    def apply_algorithm(self):

        image = self.image_manager.get_original()

        if image is None:
            return

        algorithm = self.properties.selected_algorithm()

        if algorithm is None:
            return

        # ---------------- Compression Algorithms ---------------- #

        compression_algorithms = {
            "JPEG Compression",
            "Run Length Encoding",
            "Huffman Coding"
        }

        if algorithm in compression_algorithms:

            # ---------------- JPEG ---------------- #

            if algorithm == "JPEG Compression":

                output = "Images/output/compressed.jpg"

                try:
                    start = time.perf_counter()

                    self.processor.compression.jpeg_compression(
                        image,
                        output,
                        quality=self.properties.value("Quality")
                    )

                    elapsed = (time.perf_counter() - start) * 1000

                    result = cv2.imread(resource_path(output))

                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Compression Error",
                        f"Unable to compress image.\n\nReason:\n{str(e)}"
                    )
                    return

                image_path = self.image_manager.get_image_path()

                if image_path is None:
                    self.statusBar().showMessage(
                        "Original image path not found."
                    )
                    return

                original_size = os.path.getsize(image_path)
                compressed_size = os.path.getsize(output)

                quality = self.properties.value("Quality")

                self.compression_report.update_report(
                    original_size,
                    compressed_size,
                    quality
                )

                self.compression_report.show()

                self.image_manager.set_processed(result)
                self.processed.set_image(result)

                self.statistics.update_statistics(
                    algorithm,
                    elapsed,
                    result
                )

                self.statusBar().showMessage(
                    f"{algorithm} applied successfully"
                )

                return

            # ---------------- Run Length Encoding ---------------- #

            elif algorithm == "Run Length Encoding":

                try:
                    stats = self.processor.compression.run_length_encoding(image)

                    QMessageBox.information(
                        self,
                        "Run Length Encoding",
                        f"""Algorithm : {stats['algorithm']}

    Original Entries : {stats['original_entries']}

    Compressed Entries : {stats['compressed_entries']}

    Compression Ratio : {stats['compression_ratio']}
    """
                    )

                    self.statusBar().showMessage(
                        "Run Length Encoding completed."
                    )

                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Compression Error",
                        str(e)
                    )

                return

            # ---------------- Huffman Coding ---------------- #

            elif algorithm == "Huffman Coding":

                try:
                    stats = self.processor.compression.huffman_encoding(image)

                    QMessageBox.information(
                        self,
                        "Huffman Coding",
                        f"""Algorithm : {stats['algorithm']}

    Unique Symbols : {stats['symbols']}

    Average Code Length : {stats['average_code_length']} bits
    """
                    )

                    self.statusBar().showMessage(
                        "Huffman Coding completed."
                    )

                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Compression Error",
                        str(e)
                    )

                return

        # ---------------- All Other Algorithms ---------------- #

        func = self.algorithm_map.get(algorithm)

        if func is None:
            return

        try:

            start = time.perf_counter()

            result = func(image)

            elapsed = (time.perf_counter() - start) * 1000

        except Exception as e:

            QMessageBox.critical(
                self,
                "Processing Error",
                f"Unable to apply '{algorithm}'.\n\nReason:\n{str(e)}"
            )

            return

        self.image_manager.set_processed(result)

        self.processed.set_image(result)

        self.statistics.update_statistics(
            algorithm,
            elapsed,
            result
        )

        self.statusBar().showMessage(
            f"{algorithm} applied successfully"
        )
    
    # ==================================================
    # Save Image
    # ==================================================

    def save_image(self):

        image = self.image_manager.get_processed()

        if image is None:
            self.statusBar().showMessage("No processed image to save.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            "",
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;Bitmap (*.bmp)"
        )

        if not file_path:
            return

        success = cv2.imwrite(file_path, image)

        if success:
            self.statusBar().showMessage(f"Image saved to: {file_path}")
        else:
            self.statusBar().showMessage("Failed to save image.")

    # ==================================================
    # Reset Image
    # ==================================================

    def reset_image(self):

        original = self.image_manager.get_original()

        if original is None:
            self.statusBar().showMessage("No image loaded.")
            return

        self.image_manager.reset()

        self.original.set_image(original)

        self.processed.set_image(original)

        self.statusBar().showMessage("Image reset successfully.")

    # ==================================================
    # Undo
    # ==================================================

    def undo_image(self):

        image = self.image_manager.undo()

        if image is None:
            self.statusBar().showMessage("Nothing to undo.")
            return

        self.processed.set_image(image)

        self.statusBar().showMessage("Undo")


    # ==================================================
    # Redo
    # ==================================================

    def redo_image(self):

        image = self.image_manager.redo()

        if image is None:
            self.statusBar().showMessage("Nothing to redo.")
            return

        self.processed.set_image(image)

        self.statusBar().showMessage("Redo")

    # ==================================================
    # Dynamic Parameters
    # ==================================================

    def update_parameters(self, current, previous):

        if current is None:
            return

        algorithm = current.text()

        self.properties.clear_parameters()

        # ---------------- Enhancement ---------------- #

        if algorithm == "Gamma":

            self.properties.add_double_spinbox(
                "Gamma",
                0.1,
                5.0,
                0.5
            )

        # ---------------- Filtering ---------------- #

        elif algorithm in [
            "Mean Filter",
            "Median Filter",
            "Gaussian Filter"
        ]:

            self.properties.add_spinbox(
                "Kernel Size",
                3,
                15,
                3
            )

        # ---------------- Transformation ---------------- #

        elif algorithm == "Rotation":

            self.properties.add_spinbox(
                "Angle",
                0,
                360,
                45
            )

        elif algorithm == "Scaling":

            self.properties.add_double_spinbox(
                "Scale",
                0.1,
                5.0,
                1.0
            )

        elif algorithm == "Translation":

            self.properties.add_spinbox(
                "X",
                -500,
                500,
                100
            )

            self.properties.add_spinbox(
                "Y",
                -500,
                500,
                100
            )

        # ---------------- Compression ---------------- #

        elif algorithm == "JPEG Compression":

            self.properties.add_spinbox(
                "Quality",
                1,
                100,
                30
            )

        # ---------------- Frequency ---------------- #

        elif algorithm in [
            "Low Pass",
            "High Pass",
            "Butterworth",
            "Gaussian"
        ]:

            self.properties.add_spinbox(
                "Radius",
                5,
                100,
                30
            )
    
    # ==================================================
    # Zoom In
    # ==================================================

    def zoom_in(self):

        self.original.zoom_in()
        self.processed.zoom_in()

        self.statusBar().showMessage("Zoom : +")


    # ==================================================
    # Zoom Out
    # ==================================================

    def zoom_out(self):

        self.original.zoom_out()
        self.processed.zoom_out()

        self.statusBar().showMessage("Zoom : -")


    # ==================================================
    # Fit Image
    # ==================================================

    def fit_image(self):

        self.original.fit_image()
        self.processed.fit_image()

        self.statusBar().showMessage("Fit to Window")

    # ==================================================
    # Comparison Viewer
    # ==================================================

    def open_comparison(self):

        original = self.image_manager.get_original()
        processed = self.image_manager.get_processed()

        if original is None or processed is None:
            self.statusBar().showMessage("Load and process an image first.")
            return

        self.comparison.set_images(original, processed)

        self.comparison.show()

    # ==================================================
    # Histogram
    # ==================================================

    def open_histogram(self):

        image = self.image_manager.get_processed()

        if image is None:

            self.statusBar().showMessage("No image loaded.")

            return

        self.histogram.show_histogram(image)

        self.histogram.show()
    
    def add_recent_file(self, file_path):
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)

        self.recent_files.insert(0, file_path)

        self.recent_files = self.recent_files[:self.max_recent_files]

        self.update_recent_menu()

        self.settings.setValue(
            "recent_files",
            self.recent_files
        )


    def update_recent_menu(self):
        self.recent_menu.clear()

        if not self.recent_files:
            action = self.recent_menu.addAction("No Recent Files")
            action.setEnabled(False)
            return

        for path in self.recent_files:

            if not os.path.exists(path):
                continue

            action = self.recent_menu.addAction(os.path.basename(path))
            action.setToolTip(path)
            action.triggered.connect(
                partial(self.open_recent_file, path)
            )


    def open_recent_file(self, file_path):
        try:
            image = self.image_manager.load_image(file_path)

            self.original.set_image(image)
            self.processed.set_image(image)

            self.statusBar().showMessage(
                f"Loaded: {file_path}"
            )

            self.add_recent_file(file_path)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Open Image",
                str(e)
            )
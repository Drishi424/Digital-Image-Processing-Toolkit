from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QFileDialog,
    QMessageBox
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph
from typing import List
from reportlab.platypus import Flowable


class OCRResultDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("OCR Results")
        self.resize(700, 500)

        self.ocr_text = ""

        main_layout = QVBoxLayout(self)

        # ----------------------------------------
        # Title
        # ----------------------------------------

        title = QLabel("Extracted Text")

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size:18px;
            font-weight:bold;
        """)

        main_layout.addWidget(title)

        # ----------------------------------------
        # Text Area
        # ----------------------------------------

        self.text_edit = QTextEdit()

        self.text_edit.setReadOnly(True)

        main_layout.addWidget(self.text_edit)

        # ----------------------------------------
        # Statistics
        # ----------------------------------------

        self.statistics = QLabel(
            "Words : 0    Characters : 0"
        )

        main_layout.addWidget(self.statistics)

        # ----------------------------------------
        # Buttons
        # ----------------------------------------

        button_layout = QHBoxLayout()

        self.copy_button = QPushButton("Copy Text")

        self.save_txt_button = QPushButton("Save TXT")

        self.save_pdf_button = QPushButton("Save PDF")

        self.close_button = QPushButton("Close")

        button_layout.addWidget(self.copy_button)
        button_layout.addWidget(self.save_txt_button)
        button_layout.addWidget(self.save_pdf_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)

        main_layout.addLayout(button_layout)

        # ----------------------------------------
        # Connections
        # ----------------------------------------

        self.copy_button.clicked.connect(
            self.copy_text
        )

        self.save_txt_button.clicked.connect(
            self.save_txt
        )

        self.save_pdf_button.clicked.connect(
            self.save_pdf
        )

        self.close_button.clicked.connect(
            self.accept
        )

    # ====================================================

    def set_text(self,text,average_confidence=0.0,processing_time=0.0,language="English"):

        self.ocr_text = text

        self.text_edit.setPlainText(text)

        words = len(text.split())

        characters = len(text)

        lines = len(text.splitlines())

        self.statistics.setText(
                f"Words                : {words}\n"
                f"Characters           : {characters}\n"
                f"Lines                : {lines}\n"
                f"Average Confidence   : {average_confidence:.2f}%\n"
                f"Processing Time      : {processing_time:.3f} sec\n"
                f"Language             : {language}"
        )

    # ====================================================

    def copy_text(self):

        self.text_edit.selectAll()

        self.text_edit.copy()

        cursor = self.text_edit.textCursor()

        cursor.clearSelection()

        self.text_edit.setTextCursor(cursor)

        QMessageBox.information(
            self,
            "OCR",
            "Text copied to clipboard."
        )

    # ====================================================

    def save_txt(self):

        path, _ = QFileDialog.getSaveFileName(

            self,

            "Save Text",

            "ocr.txt",

            "Text Files (*.txt)"

        )

        if not path:
            return

        with open(path, "w", encoding="utf-8") as file:

            file.write(self.ocr_text)

        QMessageBox.information(

            self,

            "OCR",

            "Text file saved successfully."

        )

    # ====================================================

    def save_pdf(self):

        path, _ = QFileDialog.getSaveFileName(

            self,

            "Save PDF",

            "ocr.pdf",

            "PDF Files (*.pdf)"

        )

        if not path:
            return

        doc = SimpleDocTemplate(path)

        styles = getSampleStyleSheet()

        story: List[Flowable] = [
            Paragraph(
                self.ocr_text.replace("\n", "<br/>"),
                styles["Normal"]
            )
        ]

        doc.build(story)

        QMessageBox.information(

            self,

            "OCR",

            "PDF saved successfully."

        )
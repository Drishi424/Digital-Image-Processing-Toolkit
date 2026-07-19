from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QListWidget,
    QVBoxLayout,
    QFormLayout,
    QSpinBox,
    QDoubleSpinBox,
)


class PropertyPanel(QWidget):

    def __init__(self):
        super().__init__()

        self.setFixedWidth(280)

        layout = QVBoxLayout(self)

        title = QLabel("Properties")
        title.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)

        # Algorithm List
        self.algorithm_list = QListWidget()

        layout.addWidget(self.algorithm_list)

        # Parameter Area
        self.parameter_layout = QFormLayout()

        layout.addLayout(self.parameter_layout)

        # Apply Button
        self.apply_button = QPushButton("Apply")

        layout.addWidget(self.apply_button)

        layout.addStretch()

        self.controls = {}

    # -------------------------------------

    def set_algorithms(self, algorithms):

        self.algorithm_list.clear()

        for algorithm in algorithms:
            self.algorithm_list.addItem(algorithm)

    # -------------------------------------

    def selected_algorithm(self):

        item = self.algorithm_list.currentItem()

        if item:
            return item.text()

        return None

    # -------------------------------------

    def clear_parameters(self):

        while self.parameter_layout.rowCount():

            self.parameter_layout.removeRow(0)

        self.controls.clear()

    # -------------------------------------

    def add_spinbox(self, name, minimum, maximum, value):

        spin = QSpinBox()

        spin.setRange(minimum, maximum)

        spin.setValue(value)

        self.parameter_layout.addRow(name, spin)

        self.controls[name] = spin

    # -------------------------------------

    def add_double_spinbox(self, name, minimum, maximum, value):

        spin = QDoubleSpinBox()

        spin.setDecimals(2)

        spin.setRange(minimum, maximum)

        spin.setValue(value)

        self.parameter_layout.addRow(name, spin)

        self.controls[name] = spin

    # -------------------------------------

    def value(self, name):

        return self.controls[name].value()
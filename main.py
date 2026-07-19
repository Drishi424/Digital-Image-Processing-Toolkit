import ctypes
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from UI.main_window import MainWindow
from Core.utils import resource_path

def main():

    myappid = "drishi.dipstudio.v1.0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon(resource_path("Assets/icons/app_icon.ico")))

    app.setApplicationName("DIP Studio")

    # Load Dark Theme
    with open((resource_path("Themes/dark.qss")), "r") as file:
        app.setStyleSheet(file.read())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
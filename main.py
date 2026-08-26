import ctypes
import os
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from UI.main_window import MainWindow
from Core.utils import resource_path


def main():
    # Set Windows AppUserModelID so Windows taskbar uses the app icon
    if sys.platform == "win32":
        try:
            myappid = "Drishi.DIPStudio.v1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception as e:
            print(f"[Warning] Could not set AppUserModelID: {e}")

    app = QApplication(sys.argv)
    app.setApplicationName("DIP Studio")

    # Set QApplication Icon
    icon_path = resource_path("Assets/icons/app_icon.ico")
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)

    # Load Dark Theme
    theme_path = resource_path("Themes/dark.qss")
    if os.path.exists(theme_path):
        with open(theme_path, "r", encoding="utf-8") as file:
            app.setStyleSheet(file.read())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
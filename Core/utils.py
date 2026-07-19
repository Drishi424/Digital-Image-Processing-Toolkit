import os
import sys

def resource_path(relative_path):
    """
    Return the correct path for resources when running
    from source or from a PyInstaller executable.
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
import os
import sys

def resource_path(relative_path):
    """
    Return the correct absolute path for resources when running
    from source or from a PyInstaller executable.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        # Resolve path relative to the project root directory
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.normpath(os.path.join(base_path, relative_path))
"""
PixelWiz - Advanced Image Processing Desktop Application

A modern image editing application built with Python, PyQt5, and OpenCV.
Features include rotation, cropping, filters, noise generation, and more.

Author: Bhvaya Sharma
Version: 1.0.0
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow

def main():
    """Main entry point for PixelWiz application."""
    app = QApplication(sys.argv)
    app.setApplicationName("PixelWiz")
    app.setApplicationVersion("1.0.0")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

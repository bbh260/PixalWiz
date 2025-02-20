"""
Main window for PixelWiz application

Provides the main GUI interface with menu bar, image viewer, control panels, and status bar.
"""

import os
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMenuBar, QMenu, QAction, QFileDialog, QMessageBox, QStatusBar,
    QProgressBar, QLabel, QFrame, QScrollArea, QApplication, QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QKeySequence
import numpy as np

from src.ui.image_viewer import ImageViewer
from src.ui.control_panel import ControlPanel
from src.ui.dialogs import CropDialog, RotateDialog, ResizeDialog
from src.core.image_processor import ImageProcessor, FilterType, NoiseType
from src.core.threading_manager import get_thread_manager
from src.utils.image_utils import get_image_file_filter, validate_image_file, get_image_info

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.current_image = None
        self.original_image = None
        self.image_processor = ImageProcessor()
        self.current_file_path = None
        
        # Initialize thread manager
        self.thread_manager = get_thread_manager()
        
        # Initialize UI
        self.init_ui()
        self.setup_menu_bar()
        self.setup_status_bar()
        self.connect_signals()
        
        # Set window properties
        self.setWindowTitle("PixelWiz - Image Processing Studio")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Center window on screen
        self.center_window()
        
        # Show welcome message
        self.show_welcome_message()
    
    def init_ui(self):
        """Initialize the user interface layout."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Create image viewer
        self.image_viewer = ImageViewer()
        
        # Create control panel
        self.control_panel = ControlPanel()
        
        # Add widgets to splitter
        splitter.addWidget(self.image_viewer)
        splitter.addWidget(self.control_panel)
        
        # Set splitter proportions (image viewer gets more space)
        splitter.setSizes([900, 300])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
    
    def setup_menu_bar(self):
        """Create and setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # Open action
        open_action = QAction('Open...', self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.setStatusTip('Open an image file')
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)
        
        # Save action
        save_action = QAction('Save', self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.setStatusTip('Save the current image')
        save_action.triggered.connect(self.save_image)
        file_menu.addAction(save_action)
        
        # Save As action
        save_as_action = QAction('Save As...', self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.setStatusTip('Save the current image with a new name')
        save_as_action.triggered.connect(self.save_image_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction('Exit', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.setStatusTip('Exit the application')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu('Edit')
        
        # Undo action (placeholder)
        undo_action = QAction('Undo', self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.setEnabled(False)  # TODO: Implement undo functionality
        edit_menu.addAction(undo_action)
        
        # Reset action
        reset_action = QAction('Reset to Original', self)
        reset_action.setStatusTip('Reset image to original state')
        reset_action.triggered.connect(self.reset_to_original)
        edit_menu.addAction(reset_action)
        
        # Transform menu
        transform_menu = menubar.addMenu('Transform')
        
        # Rotate actions
        rotate_90_action = QAction('Rotate 90° CW', self)
        rotate_90_action.triggered.connect(lambda: self.rotate_image(90))
        transform_menu.addAction(rotate_90_action)
        
        rotate_180_action = QAction('Rotate 180°', self)
        rotate_180_action.triggered.connect(lambda: self.rotate_image(180))
        transform_menu.addAction(rotate_180_action)
        
        rotate_270_action = QAction('Rotate 90° CCW', self)
        rotate_270_action.triggered.connect(lambda: self.rotate_image(270))
        transform_menu.addAction(rotate_270_action)
        
        rotate_custom_action = QAction('Rotate Custom...', self)
        rotate_custom_action.triggered.connect(self.show_rotate_dialog)
        transform_menu.addAction(rotate_custom_action)
        
        transform_menu.addSeparator()
        
        # Flip actions
        flip_h_action = QAction('Flip Horizontal', self)
        flip_h_action.triggered.connect(lambda: self.flip_image(True))
        transform_menu.addAction(flip_h_action)
        
        flip_v_action = QAction('Flip Vertical', self)
        flip_v_action.triggered.connect(lambda: self.flip_image(False))
        transform_menu.addAction(flip_v_action)
        
        transform_menu.addSeparator()
        
        # Crop action
        crop_action = QAction('Crop...', self)
        crop_action.triggered.connect(self.show_crop_dialog)
        transform_menu.addAction(crop_action)
        
        # Resize action
        resize_action = QAction('Resize...', self)
        resize_action.triggered.connect(self.show_resize_dialog)
        transform_menu.addAction(resize_action)
        
        # Filters menu
        filters_menu = menubar.addMenu('Filters')
        
        # Color filters
        grayscale_action = QAction('Grayscale', self)
        grayscale_action.triggered.connect(lambda: self.apply_filter(FilterType.GRAYSCALE))
        filters_menu.addAction(grayscale_action)
        
        sepia_action = QAction('Sepia', self)
        sepia_action.triggered.connect(lambda: self.apply_filter(FilterType.SEPIA))
        filters_menu.addAction(sepia_action)
        
        invert_action = QAction('Invert', self)
        invert_action.triggered.connect(lambda: self.apply_filter(FilterType.INVERT))
        filters_menu.addAction(invert_action)
        
        filters_menu.addSeparator()
        
        # Edge detection filters
        sobel_action = QAction('Sobel Edge Detection', self)
        sobel_action.triggered.connect(lambda: self.apply_filter(FilterType.SOBEL_EDGE))
        filters_menu.addAction(sobel_action)
        
        canny_action = QAction('Canny Edge Detection', self)
        canny_action.triggered.connect(lambda: self.apply_filter(FilterType.CANNY_EDGE))
        filters_menu.addAction(canny_action)
        
        emboss_action = QAction('Emboss', self)
        emboss_action.triggered.connect(lambda: self.apply_filter(FilterType.EMBOSS))
        filters_menu.addAction(emboss_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        # Zoom actions
        zoom_in_action = QAction('Zoom In', self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self.image_viewer.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction('Zoom Out', self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self.image_viewer.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        zoom_fit_action = QAction('Zoom to Fit', self)
        zoom_fit_action.triggered.connect(self.image_viewer.zoom_to_fit)
        view_menu.addAction(zoom_fit_action)
        
        zoom_100_action = QAction('Actual Size', self)
        zoom_100_action.triggered.connect(self.image_viewer.zoom_to_actual_size)
        view_menu.addAction(zoom_100_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About PixelWiz', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Create and setup the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Create status widgets
        self.status_label = QLabel("Ready")
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        
        self.image_info_label = QLabel("")
        
        # Add widgets to status bar
        self.status_bar.addWidget(self.status_label)
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.status_bar.addPermanentWidget(self.image_info_label)
    
    def connect_signals(self):
        """Connect signals and slots."""
        # Thread manager signals
        self.thread_manager.processing_finished.connect(self.on_processing_finished)
        self.thread_manager.processing_error.connect(self.on_processing_error)
        self.thread_manager.processing_progress.connect(self.on_processing_progress)
        self.thread_manager.processing_status.connect(self.on_processing_status)
        
        # Control panel signals
        self.control_panel.brightness_changed.connect(self.update_brightness_contrast)
        self.control_panel.contrast_changed.connect(self.update_brightness_contrast)
        self.control_panel.blur_changed.connect(self.apply_blur)
        self.control_panel.sharpen_changed.connect(self.apply_sharpen)
        self.control_panel.noise_requested.connect(self.add_noise)
        self.control_panel.filter_requested.connect(self.apply_filter)
    
    def center_window(self):
        """Center the window on the screen."""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def show_welcome_message(self):
        """Show welcome message in status bar."""
        self.status_label.setText("Welcome to PixelWiz! Open an image to get started.")
    
    def open_image(self):
        """Open an image file."""
        file_filter = get_image_file_filter()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            file_filter
        )
        
        if file_path:
            self.load_image(file_path)
    
    def load_image(self, file_path: str):
        """Load an image from file path."""
        if not validate_image_file(file_path):
            QMessageBox.warning(self, "Error", "Invalid or unsupported image file.")
            return
        
        try:
            # Load image
            image = self.image_processor.load_image(file_path)
            if image is None:
                QMessageBox.warning(self, "Error", "Failed to load image.")
                return
            
            # Store image data
            self.original_image = image.copy()
            self.current_image = image.copy()
            self.current_file_path = file_path
            
            # Update UI
            self.image_viewer.set_image(self.current_image)
            self.control_panel.reset_controls()
            self.update_image_info()
            
            # Update status
            self.status_label.setText(f"Loaded: {os.path.basename(file_path)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
    
    def save_image(self):
        """Save the current image."""
        if self.current_image is None:
            QMessageBox.warning(self, "Warning", "No image to save.")
            return
        
        if self.current_file_path:
            self.save_image_to_path(self.current_file_path)
        else:
            self.save_image_as()
    
    def save_image_as(self):
        """Save the current image with a new name."""
        if self.current_image is None:
            QMessageBox.warning(self, "Warning", "No image to save.")
            return
        
        file_filter = "PNG (*.png);;JPEG (*.jpg);;BMP (*.bmp);;TIFF (*.tiff);;All Files (*)"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            "",
            file_filter
        )
        
        if file_path:
            self.save_image_to_path(file_path)
    
    def save_image_to_path(self, file_path: str):
        """Save image to specified path."""
        try:
            success = self.image_processor.save_image(self.current_image, file_path)
            if success:
                self.current_file_path = file_path
                self.status_label.setText(f"Saved: {os.path.basename(file_path)}")
                QMessageBox.information(self, "Success", "Image saved successfully.")
            else:
                QMessageBox.warning(self, "Error", "Failed to save image.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save image: {str(e)}")
    
    def reset_to_original(self):
        """Reset image to original state."""
        if self.original_image is None:
            return
        
        self.current_image = self.original_image.copy()
        self.image_viewer.set_image(self.current_image)
        self.control_panel.reset_controls()
        self.status_label.setText("Reset to original image")
    
    def rotate_image(self, angle: float):
        """Rotate image by specified angle."""
        if self.current_image is None:
            return
        
        self.thread_manager.process_image(self.current_image, "rotate", angle=angle)
    
    def flip_image(self, horizontal: bool):
        """Flip image horizontally or vertically."""
        if self.current_image is None:
            return
        
        self.thread_manager.process_image(self.current_image, "flip", horizontal=horizontal)
    
    def apply_filter(self, filter_type: FilterType):
        """Apply specified filter to image."""
        if self.current_image is None:
            return
        
        self.thread_manager.process_image(self.current_image, "filter", filter_type=filter_type)
    
    def update_brightness_contrast(self):
        """Update image brightness and contrast."""
        if self.current_image is None:
            return
        
        brightness = self.control_panel.get_brightness()
        contrast = self.control_panel.get_contrast()
        
        self.thread_manager.process_image(
            self.original_image,  # Always apply to original to avoid cumulative effects
            "brightness_contrast",
            brightness=brightness,
            contrast=contrast
        )
    
    def apply_blur(self, blur_type: str, kernel_size: int):
        """Apply blur to image."""
        if self.current_image is None:
            return
        
        self.thread_manager.process_image(
            self.current_image,
            "blur",
            blur_type=blur_type,
            kernel_size=kernel_size
        )
    
    def apply_sharpen(self, method: str, strength: float):
        """Apply sharpening to image."""
        if self.current_image is None:
            return
        
        self.thread_manager.process_image(
            self.current_image,
            "sharpen",
            method=method,
            strength=strength
        )
    
    def add_noise(self, noise_type: NoiseType, intensity: float):
        """Add noise to image."""
        if self.current_image is None:
            return
        
        self.thread_manager.process_image(
            self.current_image,
            "add_noise",
            noise_type=noise_type,
            intensity=intensity
        )
    
    def show_crop_dialog(self):
        """Show visual crop dialog."""
        if self.current_image is None:
            return
        
        # Check if crop dialog is already open
        if hasattr(self, 'crop_dialog') and self.crop_dialog and self.crop_dialog.isVisible():
            self.crop_dialog.raise_()  # Bring to front
            self.crop_dialog.activateWindow()
            return
        
        # Create and show non-modal dialog
        self.crop_dialog = CropDialog(self.image_viewer, self)
        
        # Connect to handle when dialog is accepted
        def on_crop_accepted():
            x, y, width, height = self.crop_dialog.get_crop_rect()
            # Disable crop mode now that we have the coordinates
            self.image_viewer.enable_crop_mode(False)
            
            if width > 0 and height > 0:
                self.status_label.setText("Cropping image...")
                # Process crop operation
                self.thread_manager.process_image(
                    self.current_image,
                    "crop",
                    x=x, y=y, width=width, height=height
                )
                # Don't delete dialog immediately - wait for processing to complete
                self.crop_dialog.hide()
            else:
                self.status_label.setText("No crop area selected")
                self.crop_dialog.deleteLater()
                self.crop_dialog = None
        
        def on_crop_rejected():
            if hasattr(self, 'crop_dialog') and self.crop_dialog:
                self.crop_dialog.deleteLater()
                self.crop_dialog = None
        
        self.crop_dialog.accepted.connect(on_crop_accepted)
        self.crop_dialog.rejected.connect(on_crop_rejected)
        self.crop_dialog.show()  # Use show() instead of exec_() for non-modal
    
    def show_rotate_dialog(self):
        """Show rotate dialog."""
        if self.current_image is None:
            return
        
        dialog = RotateDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            angle = dialog.get_angle()
            self.rotate_image(angle)
    
    def show_resize_dialog(self):
        """Show resize dialog."""
        if self.current_image is None:
            return
        
        current_height, current_width = self.current_image.shape[:2]
        dialog = ResizeDialog(current_width, current_height, self)
        if dialog.exec_() == QDialog.Accepted:
            width, height, maintain_aspect = dialog.get_size()
            self.status_label.setText("Resizing image...")
            success = self.thread_manager.process_image(
                self.current_image,
                "resize",
                width=width,
                height=height,
                maintain_aspect=maintain_aspect
            )
            if not success:
                self.status_label.setText("Failed to start resize operation")
    
    def update_image_info(self):
        """Update image info display."""
        if self.current_image is None:
            self.image_info_label.setText("")
            return
        
        info = get_image_info(self.current_image)
        self.image_info_label.setText(
            f"{info['width']}×{info['height']} | {info['color_mode']} | {info['size_mb']:.1f} MB"
        )
    
    def on_processing_finished(self, result: np.ndarray):
        """Handle completion of image processing."""
        self.current_image = result
        self.image_viewer.set_image(self.current_image)
        self.update_image_info()
        self.progress_bar.setVisible(False)
        self.status_label.setText("Processing completed")
        
        # Clean up crop dialog if it exists and is hidden
        if hasattr(self, 'crop_dialog') and self.crop_dialog and not self.crop_dialog.isVisible():
            self.crop_dialog.deleteLater()
            self.crop_dialog = None
    
    def on_processing_error(self, error_msg: str):
        """Handle processing errors."""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Error: {error_msg}")
        QMessageBox.warning(self, "Processing Error", error_msg)
    
    def on_processing_progress(self, progress: int):
        """Handle processing progress updates."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(progress)
    
    def on_processing_status(self, status: str):
        """Handle processing status updates."""
        self.status_label.setText(status)
    
    def show_about(self):
        """Show about dialog."""
        about_text = """
        <h2>PixelWiz v1.0</h2>
        <p>Advanced Image Processing Desktop Application</p>
        <p>Built with Python, PyQt5, and OpenCV</p>
        <p><b>Features:</b></p>
        <ul>
        <li>Image transformation (rotate, crop, flip, resize)</li>
        <li>Brightness and contrast adjustment</li>
        <li>Various filters and effects</li>
        <li>Noise generation and removal</li>
        <li>Sharpening and blurring</li>
        <li>Edge detection algorithms</li>
        </ul>
        <p>© 2025 Bhavya Sharma</p>
        """
        
        QMessageBox.about(self, "About PixelWiz", about_text)
    
    def closeEvent(self, event):
        """Handle application close event."""
        # Cancel any ongoing processing
        if self.thread_manager.is_busy():
            self.thread_manager.cancel_current_operation()
        
        event.accept()

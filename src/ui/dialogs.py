"""
Dialog boxes for PixelWiz

Provides specialized dialogs for crop, rotate, resize, and other operations.
"""

import numpy as np
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox, QGridLayout,
    QDialogButtonBox, QFrame, QSlider, QWidget
)
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from src.utils.image_utils import numpy_to_qpixmap, scale_pixmap_to_fit

class CropDialog(QDialog):
    """Dialog for visual crop selection."""
    
    def __init__(self, image_viewer, parent=None):
        super().__init__(parent)
        
        self.image_viewer = image_viewer
        self.crop_rect = QRect(0, 0, 0, 0)
        
        self.setWindowTitle("Crop Image")
        self.setModal(False)  # Make non-modal to allow interaction with main window
        self.resize(400, 250)  # Slightly larger to prevent geometry warnings
        self.setMinimumSize(300, 200)  # Set minimum size
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel("Draw a rectangle on the image to select the crop area")
        instructions.setWordWrap(True)
        instructions.setStyleSheet("font-weight: bold; color: #2E86AB; padding: 10px;")
        layout.addWidget(instructions)
        
        # Current selection info
        self.selection_info = QLabel("No selection yet")
        self.selection_info.setAlignment(Qt.AlignCenter)
        self.selection_info.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(self.selection_info)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.clear_button = QPushButton("Clear Selection")
        self.clear_button.clicked.connect(self.clear_selection)
        self.clear_button.setEnabled(False)
        button_layout.addWidget(self.clear_button)
        
        button_layout.addStretch()
        
        # Preset buttons
        presets_group = QGroupBox("Quick Presets")
        presets_layout = QHBoxLayout(presets_group)
        
        center_quarter_btn = QPushButton("Center 1/4")
        center_quarter_btn.clicked.connect(self.set_center_quarter)
        presets_layout.addWidget(center_quarter_btn)
        
        center_half_btn = QPushButton("Center 1/2")
        center_half_btn.clicked.connect(self.set_center_half)
        presets_layout.addWidget(center_half_btn)
        
        layout.addWidget(presets_group)
        
        # Button box
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        # Disable OK initially
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
        
        layout.addWidget(self.button_box)
        
        # Enable crop mode
        self.image_viewer.enable_crop_mode(True)
    
    def setup_connections(self):
        """Setup signal connections."""
        self.image_viewer.crop_selection_changed.connect(self.on_crop_selection_changed)
    
    def on_crop_selection_changed(self, selection: QRect):
        """Handle crop selection changes."""
        if self.image_viewer.has_crop_selection():
            info = self.image_viewer.get_crop_selection_info()
            self.selection_info.setText(
                f"Selection: {info['width']} × {info['height']} pixels\n"
                f"Position: ({info['x']}, {info['y']})\n"
                f"Aspect Ratio: {info['aspect_ratio']:.2f}"
            )
            self.clear_button.setEnabled(True)
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.selection_info.setText("No selection yet")
            self.clear_button.setEnabled(False)
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
    
    def clear_selection(self):
        """Clear the current crop selection."""
        self.image_viewer.clear_crop_selection()
        self.on_crop_selection_changed(QRect())
    
    def set_center_quarter(self):
        """Set crop to center quarter of image."""
        if self.image_viewer.current_image is None:
            return
        
        height, width = self.image_viewer.current_image.shape[:2]
        crop_width = width // 2
        crop_height = height // 2
        x = width // 4
        y = height // 4
        
        self.apply_preset_crop(x, y, crop_width, crop_height)
    
    def set_center_half(self):
        """Set crop to center half of image."""
        if self.image_viewer.current_image is None:
            return
        
        height, width = self.image_viewer.current_image.shape[:2]
        crop_width = int(width * 0.7)
        crop_height = int(height * 0.7)
        x = (width - crop_width) // 2
        y = (height - crop_height) // 2
        
        self.apply_preset_crop(x, y, crop_width, crop_height)
    
    def apply_preset_crop(self, x: int, y: int, width: int, height: int):
        """Apply a preset crop selection."""
        # Convert image coordinates to display coordinates
        if self.image_viewer.image_label.original_pixmap.isNull():
            return
        
        # Calculate scale factor
        original_width = self.image_viewer.image_label.original_pixmap.width()
        original_height = self.image_viewer.image_label.original_pixmap.height()
        display_width = self.image_viewer.image_label.scaled_pixmap.width()
        display_height = self.image_viewer.image_label.scaled_pixmap.height()
        
        scale_x = display_width / original_width
        scale_y = display_height / original_height
        
        # Convert to display coordinates
        display_x = int(x * scale_x)
        display_y = int(y * scale_y)
        display_width = int(width * scale_x)
        display_height = int(height * scale_y)
        
        # Set the crop selection
        crop_rect = QRect(display_x, display_y, display_width, display_height)
        self.image_viewer.image_label.crop_selection = crop_rect
        self.image_viewer.image_label.crop_rubber_band.setGeometry(crop_rect)
        self.image_viewer.image_label.crop_rubber_band.show()
        
        # Update the info
        self.on_crop_selection_changed(crop_rect)
    
    def get_crop_rect(self) -> tuple:
        """Get crop rectangle as (x, y, width, height) in image coordinates."""
        if not self.image_viewer.has_crop_selection():
            return (0, 0, 0, 0)
        
        image_rect = self.image_viewer.get_crop_selection()
        return (image_rect.x(), image_rect.y(), image_rect.width(), image_rect.height())
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        # Disable crop mode when dialog closes
        self.image_viewer.enable_crop_mode(False)
        super().closeEvent(event)
    
    def reject(self):
        """Handle dialog rejection."""
        # Disable crop mode and clear selection
        self.image_viewer.enable_crop_mode(False)
        self.image_viewer.clear_crop_selection()
        super().reject()
    
    def accept(self):
        """Handle dialog acceptance."""
        # Keep the selection and don't disable crop mode yet
        # The main window will handle disabling crop mode after processing
        super().accept()

class RotateDialog(QDialog):
    """Dialog for rotating image by custom angle."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Rotate Image")
        self.setModal(True)
        self.resize(300, 200)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel("Enter rotation angle in degrees")
        layout.addWidget(instructions)
        
        # Angle input
        angle_group = QGroupBox("Rotation Angle")
        angle_layout = QVBoxLayout(angle_group)
        
        # Angle spinbox
        angle_container = QHBoxLayout()
        angle_container.addWidget(QLabel("Angle:"))
        
        self.angle_spinbox = QDoubleSpinBox()
        self.angle_spinbox.setRange(-360.0, 360.0)
        self.angle_spinbox.setSuffix("°")
        self.angle_spinbox.setValue(0.0)
        angle_container.addWidget(self.angle_spinbox)
        
        angle_layout.addLayout(angle_container)
        
        # Preset buttons
        preset_layout = QHBoxLayout()
        
        for angle in [-90, -45, 45, 90, 180]:
            btn = QPushButton(f"{angle}°")
            btn.clicked.connect(lambda checked, a=angle: self.angle_spinbox.setValue(a))
            preset_layout.addWidget(btn)
        
        angle_layout.addLayout(preset_layout)
        layout.addWidget(angle_group)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_angle(self) -> float:
        """Get the rotation angle."""
        return self.angle_spinbox.value()

class ResizeDialog(QDialog):
    """Dialog for resizing image."""
    
    def __init__(self, current_width: int, current_height: int, parent=None):
        super().__init__(parent)
        
        self.current_width = current_width
        self.current_height = current_height
        self.aspect_ratio = current_width / current_height
        
        self.setWindowTitle("Resize Image")
        self.setModal(True)
        self.resize(350, 250)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Current size info
        current_info = QLabel(f"Current size: {self.current_width} × {self.current_height}")
        current_info.setStyleSheet("font-weight: bold;")
        layout.addWidget(current_info)
        
        # Size input group
        size_group = QGroupBox("New Size")
        size_layout = QGridLayout(size_group)
        
        # Width
        size_layout.addWidget(QLabel("Width:"), 0, 0)
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(1, 10000)
        self.width_spinbox.setValue(self.current_width)
        self.width_spinbox.valueChanged.connect(self.on_width_changed)
        size_layout.addWidget(self.width_spinbox, 0, 1)
        size_layout.addWidget(QLabel("pixels"), 0, 2)
        
        # Height
        size_layout.addWidget(QLabel("Height:"), 1, 0)
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(1, 10000)
        self.height_spinbox.setValue(self.current_height)
        self.height_spinbox.valueChanged.connect(self.on_height_changed)
        size_layout.addWidget(self.height_spinbox, 1, 1)
        size_layout.addWidget(QLabel("pixels"), 1, 2)
        
        # Maintain aspect ratio checkbox
        self.maintain_aspect_checkbox = QCheckBox("Maintain aspect ratio")
        self.maintain_aspect_checkbox.setChecked(True)
        size_layout.addWidget(self.maintain_aspect_checkbox, 2, 0, 1, 3)
        
        layout.addWidget(size_group)
        
        # Preset buttons
        presets_group = QGroupBox("Presets")
        presets_layout = QGridLayout(presets_group)
        
        presets = [
            ("50%", 0.5),
            ("75%", 0.75),
            ("150%", 1.5),
            ("200%", 2.0)
        ]
        
        for i, (label, factor) in enumerate(presets):
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, f=factor: self.apply_scale_factor(f))
            presets_layout.addWidget(btn, i // 2, i % 2)
        
        layout.addWidget(presets_group)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def on_width_changed(self, width: int):
        """Handle width change."""
        if self.maintain_aspect_checkbox.isChecked():
            new_height = int(width / self.aspect_ratio)
            self.height_spinbox.blockSignals(True)
            self.height_spinbox.setValue(new_height)
            self.height_spinbox.blockSignals(False)
    
    def on_height_changed(self, height: int):
        """Handle height change."""
        if self.maintain_aspect_checkbox.isChecked():
            new_width = int(height * self.aspect_ratio)
            self.width_spinbox.blockSignals(True)
            self.width_spinbox.setValue(new_width)
            self.width_spinbox.blockSignals(False)
    
    def apply_scale_factor(self, factor: float):
        """Apply a scale factor to both dimensions."""
        new_width = int(self.current_width * factor)
        new_height = int(self.current_height * factor)
        
        self.width_spinbox.setValue(new_width)
        self.height_spinbox.setValue(new_height)
    
    def get_size(self) -> tuple:
        """Get the new size as (width, height, maintain_aspect)."""
        return (
            self.width_spinbox.value(),
            self.height_spinbox.value(),
            self.maintain_aspect_checkbox.isChecked()
        )

class BatchProcessDialog(QDialog):
    """Dialog for batch processing operations."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.operations = []
        
        self.setWindowTitle("Batch Process")
        self.setModal(True)
        self.resize(400, 300)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel("Select operations to apply in sequence:")
        layout.addWidget(instructions)
        
        # Operations list (placeholder for future implementation)
        operations_label = QLabel("Batch processing feature coming soon!")
        operations_label.setAlignment(Qt.AlignCenter)
        operations_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(operations_label)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_operations(self) -> list:
        """Get list of operations to perform."""
        return self.operations

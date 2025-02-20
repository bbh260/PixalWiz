"""
Image viewer widget for PixelWiz

Provides image display with zoom, pan, and crop selection functionality.
"""

import numpy as np
from PyQt5.QtWidgets import QWidget, QScrollArea, QLabel, QVBoxLayout, QRubberBand
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QWheelEvent, QMouseEvent
from src.utils.image_utils import numpy_to_qpixmap, scale_pixmap_to_fit, calculate_zoom_to_fit, clamp_value

class ImageLabel(QLabel):
    """Custom QLabel for image display with zoom and pan functionality."""
    
    # Signals
    crop_selection_changed = pyqtSignal(QRect)
    zoom_changed = pyqtSignal(float)
    
    def __init__(self):
        super().__init__()
        
        # Image properties
        self.original_pixmap = QPixmap()
        self.scaled_pixmap = QPixmap()
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 10.0
        
        # Pan properties
        self.pan_start_point = QPoint()
        self.pan_active = False
        self.last_pan_point = QPoint()
        self.image_offset = QPoint(0, 0)
        
        # Crop selection properties
        self.crop_mode = False
        self.crop_start_point = QPoint()
        self.crop_end_point = QPoint()
        self.crop_selection = QRect()
        self.crop_rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.crop_rubber_band.setStyleSheet("""
            QRubberBand {
                border: 2px dashed #FF6B6B;
                background-color: rgba(255, 107, 107, 30);
            }
        """)
        
        # Widget properties
        self.setMinimumSize(200, 200)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")
        self.setText("No Image Loaded")
    
    def set_image(self, image: np.ndarray):
        """Set the image to display."""
        if image is None:
            self.original_pixmap = QPixmap()
            self.scaled_pixmap = QPixmap()
            self.clear()
            self.setText("No Image Loaded")
            self.setCursor(Qt.ArrowCursor)
            return
        
        # Convert numpy array to QPixmap
        self.original_pixmap = numpy_to_qpixmap(image)
        self.reset_view()
        self.update_display()
        
        # Set appropriate cursor
        if not self.crop_mode:
            self.setCursor(Qt.OpenHandCursor)
    
    def reset_view(self):
        """Reset zoom and pan to default values."""
        self.zoom_factor = 1.0
        self.image_offset = QPoint(0, 0)
        self.fit_to_window()
    
    def fit_to_window(self):
        """Fit image to window size."""
        if self.original_pixmap.isNull():
            return
        
        # Get scroll area size for proper fitting
        scroll_area = self.get_scroll_area()
        if scroll_area:
            # Use scroll area viewport size
            viewport_size = scroll_area.viewport().size()
            widget_size = (viewport_size.width(), viewport_size.height())
        else:
            # Fallback to widget size
            widget_size = (self.size().width(), self.size().height())
        
        # Calculate zoom to fit
        image_size = (self.original_pixmap.width(), self.original_pixmap.height())
        zoom = calculate_zoom_to_fit(image_size, widget_size)
        self.set_zoom(zoom)
    
    def set_zoom(self, zoom_factor: float):
        """Set zoom factor and update display."""
        self.zoom_factor = clamp_value(zoom_factor, self.min_zoom, self.max_zoom)
        self.update_display()
        self.zoom_changed.emit(self.zoom_factor)
    
    def zoom_in(self, factor: float = 1.2):
        """Zoom in by specified factor."""
        self.set_zoom(self.zoom_factor * factor)
    
    def zoom_out(self, factor: float = 1.2):
        """Zoom out by specified factor."""
        self.set_zoom(self.zoom_factor / factor)
    
    def zoom_to_actual_size(self):
        """Zoom to actual image size (100%)."""
        self.set_zoom(1.0)
    
    def update_display(self):
        """Update the displayed image."""
        if self.original_pixmap.isNull():
            return
        
        # Scale pixmap according to zoom factor
        scaled_size = self.original_pixmap.size() * self.zoom_factor
        self.scaled_pixmap = self.original_pixmap.scaled(
            scaled_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        # Update widget
        self.setPixmap(self.scaled_pixmap)
        self.resize(self.scaled_pixmap.size())
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel for zooming."""
        if event.modifiers() == Qt.ControlModifier:
            # Zoom with Ctrl + wheel
            angle_delta = event.angleDelta().y()
            zoom_factor = 1.1 if angle_delta > 0 else 0.9
            
            if angle_delta > 0:
                self.zoom_in(zoom_factor)
            else:
                self.zoom_out(1/zoom_factor)
        else:
            super().wheelEvent(event)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            if self.crop_mode:
                # Start crop selection
                self.crop_start_point = event.pos()
                self.crop_end_point = event.pos()
                self.crop_rubber_band.setGeometry(QRect(self.crop_start_point, self.crop_end_point))
                self.crop_rubber_band.show()
                self.setCursor(Qt.CrossCursor)
            else:
                # Start panning
                self.pan_start_point = event.pos()
                self.pan_active = True
                self.setCursor(Qt.ClosedHandCursor)
        
        super().mousePressEvent(event)
    
    def enterEvent(self, event):
        """Handle mouse enter event."""
        if not self.crop_mode and not self.original_pixmap.isNull():
            # Show open hand cursor when hovering over image (ready to pan)
            self.setCursor(Qt.OpenHandCursor)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave event."""
        if not self.pan_active:
            self.setCursor(Qt.ArrowCursor)
        super().leaveEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events."""
        if self.crop_mode and event.buttons() == Qt.LeftButton:
            # Update crop selection
            self.crop_end_point = event.pos()
            crop_rect = QRect(self.crop_start_point, self.crop_end_point).normalized()
            
            # Constrain crop selection to image bounds
            if not self.scaled_pixmap.isNull():
                image_rect = QRect(0, 0, self.scaled_pixmap.width(), self.scaled_pixmap.height())
                crop_rect = crop_rect.intersected(image_rect)
            
            self.crop_rubber_band.setGeometry(crop_rect)
            self.crop_selection = crop_rect
        
        elif self.pan_active and event.buttons() == Qt.LeftButton:
            # Handle panning by adjusting scroll area position
            scroll_area = self.get_scroll_area()
            
            if scroll_area:
                # Calculate movement delta
                delta = event.pos() - self.pan_start_point
                
                # Get current scroll bar values
                h_scroll = scroll_area.horizontalScrollBar()
                v_scroll = scroll_area.verticalScrollBar()
                
                # Apply pan movement (invert delta for natural feeling)
                h_scroll.setValue(h_scroll.value() - delta.x())
                v_scroll.setValue(v_scroll.value() - delta.y())
                
                # Update pan start point for next move
                self.pan_start_point = event.pos()
        
        super().mouseMoveEvent(event)
    
    def get_scroll_area(self):
        """Get the parent scroll area."""
        parent = self.parent()
        while parent:
            if hasattr(parent, 'horizontalScrollBar') and hasattr(parent, 'verticalScrollBar'):
                return parent
            parent = parent.parent()
        return None
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events."""
        if event.button() == Qt.LeftButton:
            if self.crop_mode:
                # Finalize crop selection
                if self.crop_selection.width() > 5 and self.crop_selection.height() > 5:
                    # Only emit signal if selection is large enough
                    self.crop_selection_changed.emit(self.crop_selection)
                else:
                    # Clear small selections
                    self.crop_rubber_band.hide()
                    self.crop_selection = QRect()
            else:
                # End panning
                self.pan_active = False
                # Restore appropriate cursor
                if not self.original_pixmap.isNull():
                    self.setCursor(Qt.OpenHandCursor)
                else:
                    self.setCursor(Qt.ArrowCursor)
        
        super().mouseReleaseEvent(event)
    
    def enable_crop_mode(self, enabled: bool):
        """Enable or disable crop selection mode."""
        self.crop_mode = enabled
        if not enabled:
            self.crop_rubber_band.hide()
            self.crop_selection = QRect()
        
        # Update cursor based on mode
        if enabled:
            self.setCursor(Qt.CrossCursor)
        elif not self.original_pixmap.isNull():
            self.setCursor(Qt.OpenHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
    
    def get_crop_selection(self) -> QRect:
        """Get the current crop selection in image coordinates."""
        if self.crop_selection.isNull() or self.original_pixmap.isNull():
            return QRect()
        
        # Convert from widget coordinates to image coordinates
        scale_x = self.original_pixmap.width() / self.scaled_pixmap.width()
        scale_y = self.original_pixmap.height() / self.scaled_pixmap.height()
        
        image_rect = QRect(
            int(self.crop_selection.x() * scale_x),
            int(self.crop_selection.y() * scale_y),
            int(self.crop_selection.width() * scale_x),
            int(self.crop_selection.height() * scale_y)
        )
        
        return image_rect

class ImageViewer(QWidget):
    """Main image viewer widget with scroll area and controls."""
    
    # Signals
    crop_selection_changed = pyqtSignal(QRect)
    zoom_changed = pyqtSignal(float)
    
    def __init__(self):
        super().__init__()
        
        self.current_image = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)  # Important: False to enable scrolling
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; }")
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create image label
        self.image_label = ImageLabel()
        self.scroll_area.setWidget(self.image_label)
        
        # Connect signals
        self.image_label.crop_selection_changed.connect(self.crop_selection_changed.emit)
        self.image_label.zoom_changed.connect(self.zoom_changed.emit)
        
        layout.addWidget(self.scroll_area)
    
    def set_image(self, image: np.ndarray):
        """Set the image to display."""
        self.current_image = image
        self.image_label.set_image(image)
    
    def get_image(self) -> np.ndarray:
        """Get the current image."""
        return self.current_image
    
    def zoom_in(self):
        """Zoom in on the image."""
        self.image_label.zoom_in()
    
    def zoom_out(self):
        """Zoom out from the image."""
        self.image_label.zoom_out()
    
    def zoom_to_fit(self):
        """Fit image to window."""
        self.image_label.fit_to_window()
    
    def zoom_to_actual_size(self):
        """Zoom to actual image size."""
        self.image_label.zoom_to_actual_size()
    
    def get_zoom_factor(self) -> float:
        """Get current zoom factor."""
        return self.image_label.zoom_factor
    
    def enable_crop_mode(self, enabled: bool):
        """Enable or disable crop selection mode."""
        self.image_label.enable_crop_mode(enabled)
    
    def get_crop_selection(self) -> QRect:
        """Get the current crop selection."""
        return self.image_label.get_crop_selection()
    
    def clear_crop_selection(self):
        """Clear the current crop selection."""
        self.image_label.crop_selection = QRect()
        self.image_label.crop_rubber_band.hide()
    
    def has_crop_selection(self) -> bool:
        """Check if there is a valid crop selection."""
        return not self.image_label.crop_selection.isNull() and \
               self.image_label.crop_selection.width() > 5 and \
               self.image_label.crop_selection.height() > 5
    
    def get_crop_selection_info(self) -> dict:
        """Get detailed information about the current crop selection."""
        if not self.has_crop_selection():
            return {}
        
        # Get selection in image coordinates
        image_rect = self.get_crop_selection()
        
        # Get selection in display coordinates
        display_rect = self.image_label.crop_selection
        
        return {
            'image_rect': image_rect,
            'display_rect': display_rect,
            'width': image_rect.width(),
            'height': image_rect.height(),
            'x': image_rect.x(),
            'y': image_rect.y(),
            'aspect_ratio': image_rect.width() / image_rect.height() if image_rect.height() > 0 else 1.0
        }

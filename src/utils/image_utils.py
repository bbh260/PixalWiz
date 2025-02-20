"""
Utility functions for PixelWiz

Contains helper functions for image conversion, validation, and common operations.
"""

import numpy as np
import cv2
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from typing import Optional, Tuple, List
import os

def numpy_to_qpixmap(image: np.ndarray) -> QPixmap:
    """Convert numpy array to QPixmap for display in Qt widgets."""
    if image is None:
        return QPixmap()
    
    # Ensure image is in the correct format
    if len(image.shape) == 3:
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        
        # Ensure image is uint8
        if image.dtype != np.uint8:
            image = np.clip(image, 0, 255).astype(np.uint8)
        
        # Ensure memory is contiguous
        if not image.flags['C_CONTIGUOUS']:
            image = np.ascontiguousarray(image)
        
        # Convert to bytes for QImage constructor
        image_bytes = image.tobytes()
        q_image = QImage(image_bytes, width, height, bytes_per_line, QImage.Format_RGB888)
    else:
        # Grayscale image
        height, width = image.shape
        bytes_per_line = width
        
        if image.dtype != np.uint8:
            image = np.clip(image, 0, 255).astype(np.uint8)
        
        # Ensure memory is contiguous
        if not image.flags['C_CONTIGUOUS']:
            image = np.ascontiguousarray(image)
        
        # Convert to bytes for QImage constructor
        image_bytes = image.tobytes()
        q_image = QImage(image_bytes, width, height, bytes_per_line, QImage.Format_Grayscale8)
    
    return QPixmap.fromImage(q_image)

def qpixmap_to_numpy(pixmap: QPixmap) -> Optional[np.ndarray]:
    """Convert QPixmap to numpy array."""
    if pixmap.isNull():
        return None
    
    image = pixmap.toImage()
    
    # Convert to RGB format
    image = image.convertToFormat(QImage.Format_RGB888)
    
    width = image.width()
    height = image.height()
    
    # Get image data
    ptr = image.bits()
    ptr.setsize(image.byteCount())
    
    # Convert to numpy array
    arr = np.array(ptr).reshape(height, width, 3)
    return arr

def scale_pixmap_to_fit(pixmap: QPixmap, target_size: Tuple[int, int], keep_aspect_ratio: bool = True) -> QPixmap:
    """Scale pixmap to fit within target size while optionally maintaining aspect ratio."""
    if pixmap.isNull():
        return pixmap
    
    target_width, target_height = target_size
    
    if keep_aspect_ratio:
        scaled_pixmap = pixmap.scaled(target_width, target_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    else:
        scaled_pixmap = pixmap.scaled(target_width, target_height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    
    return scaled_pixmap

def get_supported_image_formats() -> List[str]:
    """Get list of supported image file formats."""
    return [
        '*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif',
        '*.gif', '*.ico', '*.webp', '*.ppm', '*.pgm', '*.pbm'
    ]

def get_image_file_filter() -> str:
    """Get file filter string for image files."""
    formats = get_supported_image_formats()
    all_formats = ' '.join(formats)
    
    filter_parts = [
        f"All Images ({all_formats})",
        "JPEG (*.jpg *.jpeg)",
        "PNG (*.png)",
        "BMP (*.bmp)",
        "TIFF (*.tiff *.tif)",
        "GIF (*.gif)",
        "All Files (*)"
    ]
    
    return ';;'.join(filter_parts)

def validate_image_file(file_path: str) -> bool:
    """Validate if file is a supported image format."""
    if not os.path.exists(file_path):
        return False
    
    try:
        # Try to load with OpenCV
        image = cv2.imread(file_path)
        return image is not None
    except:
        return False

def get_image_info(image: np.ndarray) -> dict:
    """Get information about an image."""
    if image is None:
        return {}
    
    info = {
        'shape': image.shape,
        'dtype': str(image.dtype),
        'size_mb': image.nbytes / (1024 * 1024),
    }
    
    if len(image.shape) == 3:
        info['height'], info['width'], info['channels'] = image.shape
        info['color_mode'] = 'RGB' if image.shape[2] == 3 else 'RGBA'
    else:
        info['height'], info['width'] = image.shape
        info['channels'] = 1
        info['color_mode'] = 'Grayscale'
    
    return info

def calculate_zoom_to_fit(image_size: Tuple[int, int], container_size: Tuple[int, int]) -> float:
    """Calculate zoom factor to fit image in container."""
    img_width, img_height = image_size
    container_width, container_height = container_size
    
    if img_width == 0 or img_height == 0:
        return 1.0
    
    zoom_x = container_width / img_width
    zoom_y = container_height / img_height
    
    return min(zoom_x, zoom_y)

def clamp_value(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max."""
    return max(min_val, min(value, max_val))

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def create_checkerboard_background(width: int, height: int, square_size: int = 10) -> QPixmap:
    """Create a checkerboard pattern for transparent background visualization."""
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.white)
    
    # This would be used for transparency visualization
    # For now, just return a white background
    return pixmap

def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if division by zero."""
    try:
        return a / b if b != 0 else default
    except:
        return default

def ensure_image_bounds(image: np.ndarray, x: int, y: int, width: int, height: int) -> Tuple[int, int, int, int]:
    """Ensure rectangle bounds are within image dimensions."""
    if image is None:
        return 0, 0, 0, 0
    
    img_height, img_width = image.shape[:2]
    
    x = max(0, min(x, img_width - 1))
    y = max(0, min(y, img_height - 1))
    width = max(1, min(width, img_width - x))
    height = max(1, min(height, img_height - y))
    
    return x, y, width, height

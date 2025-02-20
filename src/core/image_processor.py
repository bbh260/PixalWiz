"""
Image Processing Engine for PixelWiz

This module contains all the core image processing operations including
filters, transformations, noise generation, and enhancement operations.
"""

import cv2
import numpy as np
from typing import Tuple, Optional, Union
from enum import Enum

class FilterType(Enum):
    """Enumeration of available filter types."""
    GRAYSCALE = "grayscale"
    SEPIA = "sepia"
    INVERT = "invert"
    SOBEL_EDGE = "sobel_edge"
    CANNY_EDGE = "canny_edge"
    EMBOSS = "emboss"

class NoiseType(Enum):
    """Enumeration of available noise types."""
    GAUSSIAN = "gaussian"
    SALT_PEPPER = "salt_pepper"

class ImageProcessor:
    """Core image processing class with all editing operations."""
    
    @staticmethod
    def load_image(file_path: str) -> Optional[np.ndarray]:
        """Load an image from file path."""
        try:
            image = cv2.imread(file_path)
            if image is not None:
                return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return None
        except Exception as e:
            print(f"Error loading image: {e}")
            return None
    
    @staticmethod
    def save_image(image: np.ndarray, file_path: str) -> bool:
        """Save an image to file path."""
        try:
            # Convert RGB to BGR for OpenCV
            bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            return cv2.imwrite(file_path, bgr_image)
        except Exception as e:
            print(f"Error saving image: {e}")
            return False
    
    @staticmethod
    def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
        """Rotate image by specified angle."""
        if angle == 90:
            return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            return cv2.rotate(image, cv2.ROTATE_180)
        elif angle == 270:
            return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        else:
            # Arbitrary angle rotation
            h, w = image.shape[:2]
            center = (w // 2, h // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            
            # Calculate new dimensions
            cos_val = abs(rotation_matrix[0, 0])
            sin_val = abs(rotation_matrix[0, 1])
            new_w = int((h * sin_val) + (w * cos_val))
            new_h = int((h * cos_val) + (w * sin_val))
            
            # Adjust rotation matrix for new center
            rotation_matrix[0, 2] += (new_w / 2) - center[0]
            rotation_matrix[1, 2] += (new_h / 2) - center[1]
            
            return cv2.warpAffine(image, rotation_matrix, (new_w, new_h))
    
    @staticmethod
    def crop_image(image: np.ndarray, x: int, y: int, width: int, height: int) -> np.ndarray:
        """Crop image to specified rectangle."""
        h, w = image.shape[:2]
        x = max(0, min(x, w))
        y = max(0, min(y, h))
        width = min(width, w - x)
        height = min(height, h - y)
        
        return image[y:y+height, x:x+width]
    
    @staticmethod
    def flip_image(image: np.ndarray, horizontal: bool = True) -> np.ndarray:
        """Flip image horizontally or vertically."""
        if horizontal:
            return cv2.flip(image, 1)  # Horizontal flip
        else:
            return cv2.flip(image, 0)  # Vertical flip
    
    @staticmethod
    def adjust_brightness_contrast(image: np.ndarray, brightness: int = 0, contrast: float = 1.0) -> np.ndarray:
        """Adjust brightness and contrast of image."""
        # Convert to float to prevent overflow
        adjusted = image.astype(np.float32)
        adjusted = adjusted * contrast + brightness
        
        # Clip values to valid range
        adjusted = np.clip(adjusted, 0, 255)
        return adjusted.astype(np.uint8)
    
    @staticmethod
    def sharpen_image(image: np.ndarray, method: str = "laplacian", strength: float = 1.0) -> np.ndarray:
        """Sharpen image using specified method."""
        if method == "laplacian":
            # Laplacian kernel sharpening
            kernel = np.array([[0, -1, 0],
                             [-1, 5, -1],
                             [0, -1, 0]])
            sharpened = cv2.filter2D(image, -1, kernel)
        elif method == "unsharp_mask":
            # Unsharp mask sharpening
            gaussian = cv2.GaussianBlur(image, (0, 0), 2.0)
            sharpened = cv2.addWeighted(image, 1.0 + strength, gaussian, -strength, 0)
        else:
            return image
        
        return np.clip(sharpened, 0, 255).astype(np.uint8)
    
    @staticmethod
    def add_noise(image: np.ndarray, noise_type: NoiseType, intensity: float = 0.1) -> np.ndarray:
        """Add noise to image."""
        h, w, c = image.shape
        noisy_image = image.astype(np.float32)
        
        if noise_type == NoiseType.GAUSSIAN:
            # Gaussian noise
            noise = np.random.normal(0, intensity * 255, (h, w, c))
            noisy_image += noise
        elif noise_type == NoiseType.SALT_PEPPER:
            # Salt and pepper noise
            noise = np.random.random((h, w, c))
            noisy_image[noise < intensity/2] = 0  # Pepper
            noisy_image[noise > 1 - intensity/2] = 255  # Salt
        
        return np.clip(noisy_image, 0, 255).astype(np.uint8)
    
    @staticmethod
    def blur_image(image: np.ndarray, blur_type: str = "gaussian", kernel_size: int = 5) -> np.ndarray:
        """Apply blur to image."""
        if blur_type == "gaussian":
            return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        elif blur_type == "median":
            return cv2.medianBlur(image, kernel_size)
        elif blur_type == "bilateral":
            return cv2.bilateralFilter(image, kernel_size, 80, 80)
        else:
            return image
    
    @staticmethod
    def apply_filter(image: np.ndarray, filter_type: FilterType) -> np.ndarray:
        """Apply various filters to image."""
        if filter_type == FilterType.GRAYSCALE:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        
        elif filter_type == FilterType.SEPIA:
            sepia_kernel = np.array([[0.272, 0.534, 0.131],
                                   [0.349, 0.686, 0.168],
                                   [0.393, 0.769, 0.189]])
            sepia_image = cv2.transform(image, sepia_kernel)
            return np.clip(sepia_image, 0, 255).astype(np.uint8)
        
        elif filter_type == FilterType.INVERT:
            return 255 - image
        
        elif filter_type == FilterType.SOBEL_EDGE:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            sobel = np.sqrt(sobel_x**2 + sobel_y**2)
            sobel = np.clip(sobel, 0, 255).astype(np.uint8)
            return cv2.cvtColor(sobel, cv2.COLOR_GRAY2RGB)
        
        elif filter_type == FilterType.CANNY_EDGE:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            return cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        
        elif filter_type == FilterType.EMBOSS:
            emboss_kernel = np.array([[-2, -1, 0],
                                    [-1, 1, 1],
                                    [0, 1, 2]])
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            embossed = cv2.filter2D(gray, -1, emboss_kernel)
            # Add 128 to make it visible
            embossed = np.clip(embossed + 128, 0, 255).astype(np.uint8)
            return cv2.cvtColor(embossed, cv2.COLOR_GRAY2RGB)
        
        return image
    
    @staticmethod
    def resize_image(image: np.ndarray, width: int, height: int, maintain_aspect: bool = True) -> np.ndarray:
        """Resize image to specified dimensions."""
        if maintain_aspect:
            h, w = image.shape[:2]
            aspect_ratio = w / h
            
            if width / height > aspect_ratio:
                # Height is the limiting factor
                new_height = height
                new_width = int(height * aspect_ratio)
            else:
                # Width is the limiting factor
                new_width = width
                new_height = int(width / aspect_ratio)
            
            return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
        else:
            return cv2.resize(image, (width, height), interpolation=cv2.INTER_LANCZOS4)

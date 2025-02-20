"""
Threading module for PixelWiz

Handles heavy image processing operations in separate threads to keep UI responsive.
Uses PyQt5's QThread for thread-safe signal-slot communication.
"""

import traceback
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtGui import QPixmap
import numpy as np
from typing import Callable, Any, Dict, Optional
from src.core.image_processor import ImageProcessor, FilterType, NoiseType

class ImageProcessingWorker(QThread):
    """Worker thread for image processing operations."""
    
    # Signals for communication with main thread
    finished = pyqtSignal(np.ndarray)  # Processed image
    error = pyqtSignal(str)  # Error message
    progress = pyqtSignal(int)  # Progress percentage
    status_update = pyqtSignal(str)  # Status message
    
    def __init__(self, image: np.ndarray, operation: str, **kwargs):
        super().__init__()
        self.image = image.copy()
        self.operation = operation
        self.kwargs = kwargs
        self.processor = ImageProcessor()
        
    def run(self):
        """Execute the image processing operation."""
        try:
            # Real-time operations should be faster and less verbose
            real_time_operations = ["brightness_contrast"]
            is_real_time = self.operation in real_time_operations
            
            if not is_real_time:
                self.status_update.emit(f"Starting {self.operation}...")
                self.progress.emit(10)
            
            result = self._execute_operation()
            
            if not is_real_time:
                self.progress.emit(90)
                self.status_update.emit(f"Finalizing {self.operation}...")
            
            if result is not None:
                if not is_real_time:
                    self.progress.emit(100)
                    self.status_update.emit(f"{self.operation} completed successfully")
                self.finished.emit(result)
            else:
                self.error.emit(f"Failed to execute {self.operation}")
                
        except Exception as e:
            error_msg = f"Error in {self.operation}: {str(e)}"
            print(f"Worker error: {error_msg}")
            print(traceback.format_exc())
            self.error.emit(error_msg)
    
    def _execute_operation(self) -> Optional[np.ndarray]:
        """Execute the specific operation based on operation type."""
        # Only emit progress for non-real-time operations
        real_time_operations = ["brightness_contrast"]
        if self.operation not in real_time_operations:
            self.progress.emit(30)
        
        if self.operation == "rotate":
            angle = self.kwargs.get('angle', 0)
            return self.processor.rotate_image(self.image, angle)
            
        elif self.operation == "crop":
            x = self.kwargs.get('x', 0)
            y = self.kwargs.get('y', 0)
            width = self.kwargs.get('width', self.image.shape[1])
            height = self.kwargs.get('height', self.image.shape[0])
            return self.processor.crop_image(self.image, x, y, width, height)
            
        elif self.operation == "flip":
            horizontal = self.kwargs.get('horizontal', True)
            return self.processor.flip_image(self.image, horizontal)
            
        elif self.operation == "brightness_contrast":
            brightness = self.kwargs.get('brightness', 0)
            contrast = self.kwargs.get('contrast', 1.0)
            return self.processor.adjust_brightness_contrast(self.image, brightness, contrast)
            
        elif self.operation == "sharpen":
            method = self.kwargs.get('method', 'laplacian')
            strength = self.kwargs.get('strength', 1.0)
            return self.processor.sharpen_image(self.image, method, strength)
            
        elif self.operation == "add_noise":
            noise_type = self.kwargs.get('noise_type', NoiseType.GAUSSIAN)
            intensity = self.kwargs.get('intensity', 0.1)
            return self.processor.add_noise(self.image, noise_type, intensity)
            
        elif self.operation == "blur":
            blur_type = self.kwargs.get('blur_type', 'gaussian')
            kernel_size = self.kwargs.get('kernel_size', 5)
            return self.processor.blur_image(self.image, blur_type, kernel_size)
            
        elif self.operation == "filter":
            filter_type = self.kwargs.get('filter_type', FilterType.GRAYSCALE)
            return self.processor.apply_filter(self.image, filter_type)
            
        elif self.operation == "resize":
            width = self.kwargs.get('width', self.image.shape[1])
            height = self.kwargs.get('height', self.image.shape[0])
            maintain_aspect = self.kwargs.get('maintain_aspect', True)
            return self.processor.resize_image(self.image, width, height, maintain_aspect)
            
        else:
            raise ValueError(f"Unknown operation: {self.operation}")

class ThreadManager(QObject):
    """Manages multiple worker threads and coordinates their execution."""
    
    # Signals
    processing_finished = pyqtSignal(np.ndarray)
    processing_error = pyqtSignal(str)
    processing_progress = pyqtSignal(int)
    processing_status = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_worker = None
        self.operation_queue = []
        self.is_processing = False
    
    def process_image(self, image: np.ndarray, operation: str, **kwargs) -> bool:
        """Start image processing in a separate thread."""
        # For real-time operations, cancel current operation and start new one
        real_time_operations = ["brightness_contrast"]
        
        if self.is_processing:
            if operation in real_time_operations:
                # Cancel current operation and start new one
                self.cancel_current_operation()
            else:
                self.processing_error.emit("Another operation is already in progress")
                return False
        
        try:
            # Create and configure worker
            self.current_worker = ImageProcessingWorker(image, operation, **kwargs)
            
            # Connect signals
            self.current_worker.finished.connect(self._on_processing_finished)
            self.current_worker.error.connect(self._on_processing_error)
            self.current_worker.progress.connect(self.processing_progress.emit)
            self.current_worker.status_update.connect(self.processing_status.emit)
            
            # Start processing
            self.is_processing = True
            self.current_worker.start()
            return True
            
        except Exception as e:
            error_msg = f"Failed to start processing: {str(e)}"
            print(f"ThreadManager error: {error_msg}")
            self.processing_error.emit(error_msg)
            return False
    
    def _on_processing_finished(self, result: np.ndarray):
        """Handle successful completion of processing."""
        self.is_processing = False
        self.processing_finished.emit(result)
        self._cleanup_worker()
    
    def _on_processing_error(self, error_msg: str):
        """Handle processing errors."""
        self.is_processing = False
        self.processing_error.emit(error_msg)
        self._cleanup_worker()
    
    def _cleanup_worker(self):
        """Clean up the current worker thread."""
        if self.current_worker:
            self.current_worker.quit()
            self.current_worker.wait()
            self.current_worker.deleteLater()
            self.current_worker = None
    
    def is_busy(self) -> bool:
        """Check if a processing operation is currently running."""
        return self.is_processing
    
    def cancel_current_operation(self):
        """Cancel the current processing operation."""
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.terminate()
            self.current_worker.wait()
            self._cleanup_worker()
            self.is_processing = False
            self.processing_status.emit("Operation cancelled")

class BatchProcessor(QObject):
    """Handles batch processing of multiple operations."""
    
    batch_finished = pyqtSignal(np.ndarray)
    batch_error = pyqtSignal(str)
    batch_progress = pyqtSignal(int, str)
    
    def __init__(self):
        super().__init__()
        self.thread_manager = ThreadManager()
        self.operations_queue = []
        self.current_image = None
        self.current_operation_index = 0
        
        # Connect thread manager signals
        self.thread_manager.processing_finished.connect(self._on_operation_finished)
        self.thread_manager.processing_error.connect(self._on_operation_error)
    
    def process_batch(self, image: np.ndarray, operations: list):
        """Process a batch of operations sequentially."""
        self.current_image = image.copy()
        self.operations_queue = operations.copy()
        self.current_operation_index = 0
        
        if not operations:
            self.batch_finished.emit(self.current_image)
            return
        
        self._process_next_operation()
    
    def _process_next_operation(self):
        """Process the next operation in the queue."""
        if self.current_operation_index >= len(self.operations_queue):
            self.batch_finished.emit(self.current_image)
            return
        
        operation = self.operations_queue[self.current_operation_index]
        operation_name = operation['name']
        operation_params = operation.get('params', {})
        
        progress = int((self.current_operation_index / len(self.operations_queue)) * 100)
        self.batch_progress.emit(progress, f"Processing: {operation_name}")
        
        self.thread_manager.process_image(self.current_image, operation_name, **operation_params)
    
    def _on_operation_finished(self, result: np.ndarray):
        """Handle completion of a single operation in the batch."""
        self.current_image = result
        self.current_operation_index += 1
        self._process_next_operation()
    
    def _on_operation_error(self, error_msg: str):
        """Handle error in batch processing."""
        self.batch_error.emit(f"Batch processing failed at operation {self.current_operation_index}: {error_msg}")

# Global thread manager instance - lazy initialized
_thread_manager = None

def get_thread_manager():
    """Get the global thread manager instance, creating it if necessary."""
    global _thread_manager
    if _thread_manager is None:
        _thread_manager = ThreadManager()
    return _thread_manager

# For backward compatibility - proxy that initializes on first access
class ThreadManagerProxy:
    def __getattr__(self, name):
        return getattr(get_thread_manager(), name)

thread_manager = ThreadManagerProxy()

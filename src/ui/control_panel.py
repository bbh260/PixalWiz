"""
Control panel for PixelWiz

Provides sliders, buttons, and controls for various image processing operations.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QSlider, QLabel,
    QPushButton, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from src.core.image_processor import FilterType, NoiseType

class SliderGroup(QWidget):
    """Custom widget for labeled sliders."""
    
    value_changed = pyqtSignal(int)
    value_changed_debounced = pyqtSignal(int)  # Debounced signal for real-time processing
    
    def __init__(self, label: str, minimum: int, maximum: int, default: int = 0, debounce_delay: int = 300):
        super().__init__()
        
        # Debouncing timer
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._emit_debounced_signal)
        self.debounce_delay = debounce_delay
        self.last_value = default
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        self.label = QLabel(label)
        layout.addWidget(self.label)
        
        # Value display
        self.value_label = QLabel(str(default))
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setMinimumWidth(40)
        layout.addWidget(self.value_label)
        
        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(minimum)
        self.slider.setMaximum(maximum)
        self.slider.setValue(default)
        self.slider.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.slider)
    
    def _on_value_changed(self, value: int):
        """Handle slider value change."""
        self.value_label.setText(str(value))
        self.value_changed.emit(value)
        
        # Start/restart debouncing timer for real-time processing
        self.last_value = value
        self.debounce_timer.stop()
        self.debounce_timer.start(self.debounce_delay)
    
    def _emit_debounced_signal(self):
        """Emit the debounced signal after delay."""
        self.value_changed_debounced.emit(self.last_value)
    
    def set_value(self, value: int):
        """Set slider value."""
        self.slider.setValue(value)
    
    def get_value(self) -> int:
        """Get slider value."""
        return self.slider.value()
    
    def reset(self):
        """Reset slider to default value."""
        default_value = 0
        if hasattr(self, '_default_value'):
            default_value = self._default_value
        self.slider.setValue(default_value)

class DoubleSliderGroup(QWidget):
    """Custom widget for labeled double precision sliders."""
    
    value_changed = pyqtSignal(float)
    value_changed_debounced = pyqtSignal(float)  # Debounced signal for real-time processing
    
    def __init__(self, label: str, minimum: float, maximum: float, default: float = 0.0, decimals: int = 2, debounce_delay: int = 300):
        super().__init__()
        
        self.decimals = decimals
        self.multiplier = 10 ** decimals
        
        # Debouncing timer
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._emit_debounced_signal)
        self.debounce_delay = debounce_delay
        self.last_value = default
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        self.label = QLabel(label)
        layout.addWidget(self.label)
        
        # Value display
        self.value_label = QLabel(f"{default:.{decimals}f}")
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setMinimumWidth(50)
        layout.addWidget(self.value_label)
        
        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(int(minimum * self.multiplier))
        self.slider.setMaximum(int(maximum * self.multiplier))
        self.slider.setValue(int(default * self.multiplier))
        self.slider.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.slider)
        
        self._default_value = default
    
    def _on_value_changed(self, value: int):
        """Handle slider value change."""
        real_value = value / self.multiplier
        self.value_label.setText(f"{real_value:.{self.decimals}f}")
        self.value_changed.emit(real_value)
        
        # Start/restart debouncing timer for real-time processing
        self.last_value = real_value
        self.debounce_timer.stop()
        self.debounce_timer.start(self.debounce_delay)
    
    def _emit_debounced_signal(self):
        """Emit the debounced signal after delay."""
        self.value_changed_debounced.emit(self.last_value)
    
    def set_value(self, value: float):
        """Set slider value."""
        self.slider.setValue(int(value * self.multiplier))
    
    def get_value(self) -> float:
        """Get slider value."""
        return self.slider.value() / self.multiplier
    
    def reset(self):
        """Reset slider to default value."""
        self.slider.setValue(int(self._default_value * self.multiplier))

class ControlPanel(QWidget):
    """Main control panel with all image processing controls."""
    
    # Signals for real-time updates
    brightness_changed = pyqtSignal(int)
    contrast_changed = pyqtSignal(float)
    blur_changed = pyqtSignal(str, int)
    sharpen_changed = pyqtSignal(str, float)
    noise_requested = pyqtSignal(object, float)  # NoiseType, intensity
    filter_requested = pyqtSignal(object)  # FilterType
    
    def __init__(self):
        super().__init__()
        
        self.init_ui()
        self.connect_signals()
        
        # Set fixed width
        self.setFixedWidth(280)
        self.setMinimumHeight(600)
    
    def init_ui(self):
        """Initialize the user interface."""
        # Create scroll area for the controls
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Create main widget for scroll area
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        
        # Control layout
        layout = QVBoxLayout(scroll_widget)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel("Image Controls")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Brightness and Contrast group
        self.create_brightness_contrast_group(layout)
        
        # Blur and Sharpen group
        self.create_blur_sharpen_group(layout)
        
        # Filters group
        self.create_filters_group(layout)
        
        # Noise group
        self.create_noise_group(layout)
        
        # Advanced group
        self.create_advanced_group(layout)
        
        # Add stretch to push everything to top
        layout.addStretch()
    
    def create_brightness_contrast_group(self, parent_layout):
        """Create brightness and contrast controls."""
        group = QGroupBox("Brightness & Contrast")
        layout = QVBoxLayout(group)
        
        # Brightness slider
        self.brightness_slider = SliderGroup("Brightness", -100, 100, 0)
        layout.addWidget(self.brightness_slider)
        
        # Contrast slider
        self.contrast_slider = DoubleSliderGroup("Contrast", 0.1, 3.0, 1.0, 2)
        layout.addWidget(self.contrast_slider)
        
        # Reset button
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_brightness_contrast)
        layout.addWidget(reset_btn)
        
        parent_layout.addWidget(group)
    
    def create_blur_sharpen_group(self, parent_layout):
        """Create blur and sharpen controls."""
        group = QGroupBox("Blur & Sharpen")
        layout = QVBoxLayout(group)
        
        # Blur section
        blur_label = QLabel("Blur")
        blur_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(blur_label)
        
        # Blur type combo
        self.blur_type_combo = QComboBox()
        self.blur_type_combo.addItems(["Gaussian", "Median", "Bilateral"])
        layout.addWidget(self.blur_type_combo)
        
        # Blur intensity
        self.blur_intensity = SliderGroup("Intensity", 1, 25, 5)
        layout.addWidget(self.blur_intensity)
        
        # Apply blur button
        apply_blur_btn = QPushButton("Apply Blur")
        apply_blur_btn.clicked.connect(self.apply_blur)
        layout.addWidget(apply_blur_btn)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        layout.addWidget(separator)
        
        # Sharpen section
        sharpen_label = QLabel("Sharpen")
        sharpen_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(sharpen_label)
        
        # Sharpen method combo
        self.sharpen_method_combo = QComboBox()
        self.sharpen_method_combo.addItems(["Laplacian", "Unsharp Mask"])
        layout.addWidget(self.sharpen_method_combo)
        
        # Sharpen strength
        self.sharpen_strength = DoubleSliderGroup("Strength", 0.1, 3.0, 1.0, 1)
        layout.addWidget(self.sharpen_strength)
        
        # Apply sharpen button
        apply_sharpen_btn = QPushButton("Apply Sharpen")
        apply_sharpen_btn.clicked.connect(self.apply_sharpen)
        layout.addWidget(apply_sharpen_btn)
        
        parent_layout.addWidget(group)
    
    def create_filters_group(self, parent_layout):
        """Create filters controls."""
        group = QGroupBox("Filters")
        layout = QVBoxLayout(group)
        
        # Color filters
        color_label = QLabel("Color Effects")
        color_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(color_label)
        
        filters_layout = QVBoxLayout()
        
        # Filter buttons
        grayscale_btn = QPushButton("Grayscale")
        grayscale_btn.clicked.connect(lambda: self.filter_requested.emit(FilterType.GRAYSCALE))
        filters_layout.addWidget(grayscale_btn)
        
        sepia_btn = QPushButton("Sepia")
        sepia_btn.clicked.connect(lambda: self.filter_requested.emit(FilterType.SEPIA))
        filters_layout.addWidget(sepia_btn)
        
        invert_btn = QPushButton("Invert")
        invert_btn.clicked.connect(lambda: self.filter_requested.emit(FilterType.INVERT))
        filters_layout.addWidget(invert_btn)
        
        layout.addLayout(filters_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        layout.addWidget(separator)
        
        # Edge detection
        edge_label = QLabel("Edge Detection")
        edge_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(edge_label)
        
        edge_layout = QVBoxLayout()
        
        sobel_btn = QPushButton("Sobel")
        sobel_btn.clicked.connect(lambda: self.filter_requested.emit(FilterType.SOBEL_EDGE))
        edge_layout.addWidget(sobel_btn)
        
        canny_btn = QPushButton("Canny")
        canny_btn.clicked.connect(lambda: self.filter_requested.emit(FilterType.CANNY_EDGE))
        edge_layout.addWidget(canny_btn)
        
        emboss_btn = QPushButton("Emboss")
        emboss_btn.clicked.connect(lambda: self.filter_requested.emit(FilterType.EMBOSS))
        edge_layout.addWidget(emboss_btn)
        
        layout.addLayout(edge_layout)
        
        parent_layout.addWidget(group)
    
    def create_noise_group(self, parent_layout):
        """Create noise controls."""
        group = QGroupBox("Noise")
        layout = QVBoxLayout(group)
        
        # Noise type combo
        self.noise_type_combo = QComboBox()
        self.noise_type_combo.addItems(["Gaussian", "Salt & Pepper"])
        layout.addWidget(self.noise_type_combo)
        
        # Noise intensity
        self.noise_intensity = DoubleSliderGroup("Intensity", 0.01, 0.5, 0.1, 2)
        layout.addWidget(self.noise_intensity)
        
        # Apply noise button
        apply_noise_btn = QPushButton("Add Noise")
        apply_noise_btn.clicked.connect(self.apply_noise)
        layout.addWidget(apply_noise_btn)
        
        parent_layout.addWidget(group)
    
    def create_advanced_group(self, parent_layout):
        """Create advanced controls."""
        group = QGroupBox("Advanced")
        layout = QVBoxLayout(group)
        
        # Reset all button
        reset_all_btn = QPushButton("Reset All Controls")
        reset_all_btn.setStyleSheet("QPushButton { font-weight: bold; }")
        reset_all_btn.clicked.connect(self.reset_all_controls)
        layout.addWidget(reset_all_btn)
        
        parent_layout.addWidget(group)
    
    def connect_signals(self):
        """Connect control signals."""
        # Real-time updates for brightness and contrast (debounced to prevent too many operations)
        self.brightness_slider.value_changed_debounced.connect(self.brightness_changed.emit)
        self.contrast_slider.value_changed_debounced.connect(self.contrast_changed.emit)
    
    def get_brightness(self) -> int:
        """Get current brightness value."""
        return self.brightness_slider.get_value()
    
    def get_contrast(self) -> float:
        """Get current contrast value."""
        return self.contrast_slider.get_value()
    
    def reset_brightness_contrast(self):
        """Reset brightness and contrast to default values."""
        self.brightness_slider.reset()
        self.contrast_slider.reset()
    
    def apply_blur(self):
        """Apply blur with current settings."""
        blur_type = self.blur_type_combo.currentText().lower()
        intensity = self.blur_intensity.get_value()
        
        # Ensure odd kernel size
        if intensity % 2 == 0:
            intensity += 1
        
        self.blur_changed.emit(blur_type, intensity)
    
    def apply_sharpen(self):
        """Apply sharpening with current settings."""
        method = self.sharpen_method_combo.currentText().lower().replace(" ", "_")
        strength = self.sharpen_strength.get_value()
        
        self.sharpen_changed.emit(method, strength)
    
    def apply_noise(self):
        """Apply noise with current settings."""
        noise_type_text = self.noise_type_combo.currentText()
        if noise_type_text == "Gaussian":
            noise_type = NoiseType.GAUSSIAN
        else:
            noise_type = NoiseType.SALT_PEPPER
        
        intensity = self.noise_intensity.get_value()
        self.noise_requested.emit(noise_type, intensity)
    
    def reset_controls(self):
        """Reset all controls to default values."""
        self.reset_brightness_contrast()
        self.blur_intensity.reset()
        self.sharpen_strength.reset()
        self.noise_intensity.reset()
        
        # Reset combo boxes
        self.blur_type_combo.setCurrentIndex(0)
        self.sharpen_method_combo.setCurrentIndex(0)
        self.noise_type_combo.setCurrentIndex(0)
    
    def reset_all_controls(self):
        """Reset all controls and emit signals."""
        self.reset_controls()
        # Emit signals to update image
        self.brightness_changed.emit(0)
        self.contrast_changed.emit(1.0)

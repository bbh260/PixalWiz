# PixelWiz - Advanced Image Processing Desktop Application

PixelWiz is a powerful, modern image processing desktop application built with Python, PyQt5, and OpenCV. It provides a comprehensive set of tools for image editing, filtering, and enhancement with a user-friendly interface and responsive multithreaded processing.

## Features

### 🖼️ Image Operations
- **Load and Display**: Support for JPG, PNG, BMP, TIFF, GIF, and more
- **Rotate**: 90°, 180°, 270°, and arbitrary angle rotation
- **Crop**: Interactive cropping with preset options
- **Flip**: Horizontal and vertical flipping
- **Resize**: Smart resizing with aspect ratio preservation

### 🎨 Image Enhancement
- **Brightness & Contrast**: Real-time adjustment with sliders
- **Sharpening**: Laplacian kernel and Unsharp Mask methods
- **Blurring**: Gaussian blur, Median filter, and Bilateral filter
- **Noise**: Add Gaussian or Salt-and-Pepper noise

### 🔧 Filters & Effects
- **Color Effects**: Grayscale, Sepia, and Color Inversion
- **Edge Detection**: Sobel and Canny edge detection algorithms
- **Artistic Effects**: Emboss filter
- **More filters coming soon!**

### 🚀 Advanced Features
- **Multithreaded Processing**: Non-blocking UI during heavy operations
- **Zoom & Pan**: Interactive image viewer with zoom controls
- **Real-time Preview**: Instant feedback for adjustments
- **Professional UI**: Clean, modern interface built with PyQt5

## Requirements

- Python 3.11 or higher
- PyQt5
- OpenCV
- NumPy
- Pillow

## Installation

1. **Clone or download the PixelWiz directory**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

## Usage

### Getting Started
1. Launch PixelWiz by running `python main.py`
2. Use **File > Open** to load an image
3. Use the control panel on the right to apply effects
4. Save your edited image with **File > Save** or **File > Save As**

### Interface Overview

#### Menu Bar
- **File**: Open, Save, Save As, Exit
- **Edit**: Undo (coming soon), Reset to Original
- **Transform**: Rotate, Flip, Crop, Resize
- **Filters**: Color effects, Edge detection
- **View**: Zoom controls
- **Help**: About dialog

#### Image Viewer
- **Zoom**: Use Ctrl + Mouse Wheel or View menu
- **Pan**: Click and drag to move around zoomed images
- **Fit to Window**: Automatic sizing for optimal viewing

#### Control Panel
- **Brightness & Contrast**: Real-time sliders
- **Blur & Sharpen**: Various algorithms with intensity control
- **Filters**: One-click color and artistic effects
- **Noise**: Add realistic noise patterns
- **Advanced**: Reset controls and batch operations

### Keyboard Shortcuts
- `Ctrl + O`: Open image
- `Ctrl + S`: Save image
- `Ctrl + Shift + S`: Save As
- `Ctrl + Q`: Exit application
- `Ctrl + Z`: Undo (coming soon)
- `Ctrl + +`: Zoom in
- `Ctrl + -`: Zoom out

### Image Processing Workflow
1. **Load Image**: Start by opening your image file
2. **Basic Adjustments**: Use brightness/contrast sliders for exposure
3. **Filters**: Apply color effects or artistic filters
4. **Enhancement**: Sharpen or blur as needed
5. **Transform**: Rotate, crop, or resize if necessary
6. **Save**: Export your final image

## Technical Architecture

### Modular Design
- **`src/core/`**: Image processing engine and threading
- **`src/ui/`**: User interface components
- **`src/utils/`**: Helper functions and utilities

### Thread Safety
- All heavy processing runs in separate QThread instances
- Signal-slot communication ensures UI responsiveness
- Progress indicators show operation status

### Image Processing Pipeline
1. Image loaded as NumPy array
2. Operations applied using OpenCV functions
3. Results displayed via Qt QPixmap conversion
4. Original image preserved for reset functionality

## Supported Formats

### Input Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff, .tif)
- GIF (.gif)
- WebP (.webp)
- And more!

### Output Formats
- PNG (recommended for quality)
- JPEG (for smaller files)
- BMP (uncompressed)
- TIFF (professional)

## Development

### Project Structure
```
PixelWiz/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── src/
    ├── core/
    │   ├── image_processor.py    # Core image processing
    │   └── threading_manager.py  # Thread management
    ├── ui/
    │   ├── main_window.py       # Main application window
    │   ├── image_viewer.py      # Image display widget
    │   ├── control_panel.py     # Control panel widget
    │   └── dialogs.py          # Dialog boxes
    └── utils/
        └── image_utils.py       # Utility functions
```

### Adding New Features
1. **Image Operations**: Add methods to `ImageProcessor` class
2. **UI Controls**: Extend `ControlPanel` with new widgets
3. **Threading**: Use `ThreadManager` for heavy operations
4. **Dialogs**: Create new dialogs in `dialogs.py`

## Troubleshooting

### Common Issues

**Application won't start:**
- Ensure Python 3.11+ is installed
- Install all requirements: `pip install -r requirements.txt`
- Check for import errors in terminal

**Image won't load:**
- Verify file format is supported
- Check file isn't corrupted
- Ensure sufficient memory for large images

**Processing is slow:**
- Large images require more processing time
- Check system resources (RAM, CPU)
- Consider resizing very large images first

**UI becomes unresponsive:**
- This shouldn't happen due to threading
- If it does, restart the application
- Report the issue with steps to reproduce

### Performance Tips
- Resize large images before heavy processing
- Use PNG for best quality, JPEG for smaller files
- Close unused applications to free memory
- Process one operation at a time for best results

## Future Enhancements

### Planned Features
- **Undo/Redo System**: Full operation history
- **Batch Processing**: Apply operations to multiple images
- **Custom Filters**: Create and save custom filter presets
- **Advanced Crop**: Interactive crop tool with handles
- **Color Correction**: HSV/HSL adjustments
- **Histogram View**: Visual representation of image data
- **Plugin System**: Extensible architecture for custom tools

### Advanced Operations
- **HDR Processing**: High dynamic range operations
- **Panorama Stitching**: Combine multiple images
- **Focus Stacking**: Combine images with different focus points
- **Noise Reduction**: Advanced denoising algorithms
- **Super Resolution**: AI-powered upscaling

## Contributing

We welcome contributions! Areas for improvement:
- New image processing algorithms
- UI/UX enhancements
- Performance optimizations
- Bug fixes and testing
- Documentation improvements

## License

This project is open source and available under the MIT License.

## Acknowledgments

- **OpenCV**: Powerful computer vision library
- **PyQt5**: Professional GUI framework
- **NumPy**: Fundamental package for scientific computing
- **Python**: Amazing programming language

---
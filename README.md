# 🎨 Image Converter Pro

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=for-the-badge)](https://github.com/yourusername/image-converter-pro)
[![Status](https://img.shields.io/badge/status-active-success?style=for-the-badge)](https://github.com/yourusername/image-converter-pro)

### **A professional, feature-rich image conversion tool built with PySide6**

*Transform your images with ease - Modern formats, Batch processing, Smart presets*

[🚀 Features](#-features) • [📥 Installation](#-installation) • [📖 Usage](#-usage) • [🖼️ Screenshots](#️-screenshots) • [🤝 Contributing](#-contributing)

---

</div>

<br>

## 🖼️ Screenshots

<table>
  <tr>
    <td align="center">
      <img src="screenshots/main-interface.png" alt="Main Interface" width="100%"/>
      <br>
      <strong>Single Conversion Mode</strong>
      <br>
      <em>Clean, modern dark theme with intuitive controls</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="screenshots/batch-processing.png" alt="Batch Processing" width="100%"/>
      <br>
      <strong>Batch Processing</strong>
      <br>
      <em>Process hundreds of images with real-time progress tracking</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="screenshots/adjustments.png" alt="Image Adjustments" width="100%"/>
      <br>
      <strong>Advanced Adjustments</strong>
      <br>
      <em>Fine-tune brightness, contrast, saturation, and sharpness</em>
    </td>
  </tr>
</table>

<br>

---

<br>

## ✨ Features

<table>
<tr>
<td width="50%">

### 🎯 **Modern Format Support**

- 📸 **JPEG** - Universal photo format
- 🖼️ **PNG** - Lossless with transparency
- 🌐 **WebP** - 25-34% smaller than JPEG
- ⚡ **AVIF** - Next-gen compression
- 🍎 **HEIC** - iPhone photo format
- 🎬 **GIF** - Animated images
- 🖨️ **TIFF** - Professional quality
- 📄 **BMP**, **ICO**, **PDF** - Additional formats

</td>
<td width="50%">

### ⚡ **Core Capabilities**

- 🔄 **Single & Batch Conversion**
- 🎯 **Drag & Drop Support**
- ⏯️ **Pause/Resume/Stop Controls**
- 📊 **Real-time Progress Tracking**
- 💾 **Smart Preset System**
- 🎨 **Image Adjustments**
- 🔍 **Metadata Management**
- ⌨️ **Keyboard Shortcuts**

</td>
</tr>
</table>

<br>

### 💎 **Smart Preset System**

Save your favorite settings as reusable presets:

| Preset | Description | Best For |
|--------|-------------|----------|
| 📱 **Web Optimization** | WebP format, compressed, metadata stripped | Website delivery |
| 📷 **Social Media** | JPG 1080×1080, high quality | Instagram/Facebook |
| 🖨️ **Print Quality** | Lossless TIFF, maximum resolution | Professional printing |
| 📧 **Email Friendly** | Small file size, optimized | Email attachments |
| 🔒 **Privacy Safe** | All metadata removed including GPS | Public sharing |

<br>

### 🎛️ **Professional Image Adjustments**

<table>
<tr>
<td align="center" width="25%">
<img src="https://img.icons8.com/fluency/96/000000/brightness.png" width="48"/>
<br><strong>Brightness</strong>
<br><sub>Lighten or darken</sub>
</td>
<td align="center" width="25%">
<img src="https://img.icons8.com/fluency/96/000000/contrast.png" width="48"/>
<br><strong>Contrast</strong>
<br><sub>Enhance details</sub>
</td>
<td align="center" width="25%">
<img src="https://img.icons8.com/fluency/96/000000/color-palette.png" width="48"/>
<br><strong>Saturation</strong>
<br><sub>Adjust colors</sub>
</td>
<td align="center" width="25%">
<img src="https://img.icons8.com/fluency/96/000000/camera-lens.png" width="48"/>
<br><strong>Sharpness</strong>
<br><sub>Add clarity</sub>
</td>
</tr>
</table>

**Additional Features:**
- 📐 **Resize** with aspect ratio lock
- 🔄 **Multiple resampling methods** (Lanczos, Bicubic, Bilinear, Nearest)
- 📊 **Quality control** with real-time preview
- 🔐 **Privacy controls** for metadata

<br>

---

<br>

## 📥 Installation

### 📋 Prerequisites

> **Required:** Python 3.8 or higher | pip package manager

<br>

### 🔧 Installation Steps

#### **Step 1: Clone the Repository**

```bash
git clone https://github.com/yourusername/image-converter-pro.git
cd image-converter-pro
```

#### **Step 2: Install Dependencies**

**Essential packages** (required):
```bash
pip install PySide6 Pillow
```

**Optional packages** (for advanced formats):
```bash
# For AVIF support (recommended)
pip install pillow-avif-plugin

# For HEIC/HEIF support (iPhone photos)
pip install pillow-heif
```

#### **Step 3: Run the Application**

```bash
python main.py
```

> 💡 **Tip:** Create a virtual environment first:
> ```bash
> python -m venv venv
> source venv/bin/activate  # On Windows: venv\Scripts\activate
> pip install -r requirements.txt
> ```

<br>

---

<br>

## 📖 Usage

### 🚀 Quick Start Guide

<details>
<summary><b>🖼️ Single Image Conversion</b> (Click to expand)</summary>

<br>

**1. Load an Image**
- Click **"Select Image"** button
- **OR** Press `Ctrl+O`
- **OR** Drag & drop an image into the preview area

**2. Choose Format**
- Select output format from dropdown
- View format description and recommendations

**3. Adjust Settings** *(Optional)*
- 🎚️ **Quality**: Adjust slider for lossy formats
- 📏 **Resize**: Enable resize and set dimensions
- 🎨 **Adjustments**: Fine-tune image properties
- 📋 **Metadata**: Configure EXIF data handling

**4. Convert**
- Click **"Convert & Save"** or press `F5`
- Choose output location
- ✅ Done!

</details>

<details>
<summary><b>📦 Batch Processing</b> (Click to expand)</summary>

<br>

**1. Add Images**
- Click **"Add Files"** to select multiple images
- **OR** Click **"Add Folder"** to add all images from a directory
- **OR** Drag & drop multiple files

**2. Configure Settings**
- Settings from Single Conversion tab apply to batch
- **OR** Load a preset for consistent processing

**3. Process**
- Click **"Process Batch"** to start
- Monitor real-time progress
- Use **Pause/Resume/Stop** controls as needed

</details>

<br>

### ⌨️ Keyboard Shortcuts

<table>
<tr>
<th width="30%">Shortcut</th>
<th width="70%">Action</th>
</tr>
<tr><td><kbd>Ctrl</kbd>+<kbd>O</kbd></td><td>Open Image</td></tr>
<tr><td><kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>O</kbd></td><td>Open Multiple Images</td></tr>
<tr><td><kbd>Ctrl</kbd>+<kbd>S</kbd></td><td>Save/Convert</td></tr>
<tr><td><kbd>F5</kbd></td><td>Convert Image</td></tr>
<tr><td><kbd>Ctrl</kbd>+<kbd>B</kbd></td><td>Add to Batch</td></tr>
<tr><td><kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>C</kbd></td><td>Clear Batch Queue</td></tr>
<tr><td><kbd>Ctrl</kbd>+<kbd>Q</kbd></td><td>Quit Application</td></tr>
<tr><td><kbd>F1</kbd></td><td>Show Keyboard Shortcuts</td></tr>
<tr><td><kbd>+</kbd> / <kbd>-</kbd></td><td>Zoom In/Out Preview</td></tr>
</table>

<br>

---

<br>

## 💡 Usage Tips

### 📊 Format Recommendations

<details>
<summary><b>🌐 For Web Use</b></summary>

- Use **WebP** at 80-85% quality for best size/quality balance
- Or **AVIF** at 70-80% for cutting-edge compression
- Modern browsers support both formats (93%+ coverage)

</details>

<details>
<summary><b>🎨 For Photos with Transparency</b></summary>

- Use **PNG** for lossless quality
- Or **WebP** for smaller file size with transparency support

</details>

<details>
<summary><b>🖨️ For Maximum Quality</b></summary>

- Use **TIFF** or **PNG** (both lossless)
- Perfect for archival and professional printing

</details>

<details>
<summary><b>📧 For Email/Sharing</b></summary>

- Use **JPEG** at 75-80% quality
- Enable resize to 1280×720 or smaller
- Use "Email Friendly" preset for optimal settings

</details>

<details>
<summary><b>📱 For Social Media</b></summary>

- **Instagram/Facebook**: JPEG at 90% quality, 1080×1080 or 1920×1080
- Use the "Social Media" preset for optimal settings

</details>

<br>

### 🔒 Privacy & Metadata

> ⚠️ **Important Privacy Tips:**

- ✅ **Strip GPS** when sharing photos publicly to protect your location
- 👀 **View Metadata** before stripping to preserve important information
- 💾 **Preserve EXIF** for archival purposes (camera settings, dates)
- ℹ️ Some formats (PNG, BMP) have limited EXIF support

<br>

### 📦 Batch Processing Best Practices

```
1. 🧪 Test First       → Process 1-2 sample images to verify settings
2. 💾 Use Presets      → Create presets for common workflows
3. 👀 Monitor Progress → Watch the first few conversions for errors
4. 💽 Check Disk Space → Large batches require significant storage
5. ✅ Review Results   → Enable "Open folder after save" to check output
```

<br>

---

<br>

## 🗂️ Project Structure

```
image-converter-pro/
│
├── 📄 main.py                 # Main application entry point
├── ⚙️ config.py               # Configuration and preset management
├── 📋 formats.py              # Format definitions and detection
├── 🔧 processor.py            # Image processing engine
├── 🔄 batch_processor.py      # Batch processing with threading
│
├── 📖 README.md               # This file
├── 📦 requirements.txt        # Python dependencies
├── 📜 LICENSE                 # MIT License
│
└── 📁 screenshots/            # Application screenshots
    ├── main-interface.png
    ├── batch-processing.png
    └── adjustments.png
```

<br>

---

<br>

## 🛠️ Technical Details

### 🏗️ Built With

<table>
<tr>
<td align="center" width="33%">
<img src="https://img.icons8.com/color/96/000000/python.png" width="64"/>
<br><strong>PySide6</strong>
<br><sub>Qt for Python UI</sub>
</td>
<td align="center" width="33%">
<img src="https://img.icons8.com/color/96/000000/python.png" width="64"/>
<br><strong>Pillow</strong>
<br><sub>Image Processing</sub>
</td>
<td align="center" width="33%">
<img src="https://img.icons8.com/color/96/000000/python.png" width="64"/>
<br><strong>Python 3.8+</strong>
<br><sub>Programming Language</sub>
</td>
</tr>
</table>

<br>

### 🏛️ Architecture

- 🧩 **Modular Design** - Separated concerns for maintainability
- 🧵 **Threading** - QThread for non-blocking batch processing
- 📡 **Signal/Slot** - Event-driven architecture
- 💾 **JSON Config** - Persistent settings and presets
- 📝 **Type Hints** - Full type annotation for code clarity

<br>

### 💻 System Requirements

<table>
<tr>
<th width="50%">Minimum</th>
<th width="50%">Recommended</th>
</tr>
<tr>
<td>

- Python 3.8+
- 4GB RAM
- 100MB disk space

</td>
<td>

- Python 3.10+
- 8GB RAM
- SSD storage
- Multi-core CPU

</td>
</tr>
</table>

<br>

---

<br>

## 🐛 Troubleshooting

### ⚠️ Common Issues

<details>
<summary><b>❌ "AVIF format not supported"</b></summary>

```bash
pip install pillow-avif-plugin
```

</details>

<details>
<summary><b>❌ "HEIC format not supported"</b></summary>

```bash
pip install pillow-heif
```

</details>

<details>
<summary><b>❌ "WebP format not supported"</b></summary>

```bash
pip install pillow[webp]
```

</details>

<details>
<summary><b>❌ "Module not found: PySide6"</b></summary>

```bash
pip install PySide6
```

</details>

<details>
<summary><b>❌ "No module named PIL"</b></summary>

```bash
pip install Pillow
```

</details>

<br>

### 🐌 Performance Issues

| Issue | Solution |
|-------|----------|
| Slow batch processing | Reduce batch size or disable adjustments |
| High memory usage | Enable resize for very large images |
| Slow preview | Disable real-time adjustments for large files |

<br>

---

<br>

## 🤝 Contributing

Contributions are **welcome**! Here's how you can help:

### 📝 Contribution Process

```bash
# 1. Fork the Repository
# 2. Create a Feature Branch
git checkout -b feature/AmazingFeature

# 3. Commit Your Changes
git commit -m 'Add some AmazingFeature'

# 4. Push to the Branch
git push origin feature/AmazingFeature

# 5. Open a Pull Request
```

<br>

### 💡 Ideas for Contributions

- 🆕 Add new image formats (JPEG XL, JXR)
- 🎨 Implement additional filters (blur, edge detection)
- 🏷️ Add watermarking functionality
- ☀️ Create light theme option
- ⚡ Improve batch processing performance
- ☁️ Add cloud storage integration
- ↩️ Implement undo/redo for settings
- 🖥️ Add command-line interface
- 🔌 Create plugin system

<br>

---

<br>

## 📝 License

This project is licensed under the **MIT License**.

<details>
<summary>View Full License</summary>

```
MIT License

Copyright (c) 2025 Image Converter Pro

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

</details>

<br>

---

<br>

## 🙏 Acknowledgments

<table>
<tr>
<td align="center" width="25%">
🎨<br><strong>XnConvert & IrfanView</strong><br><sub>Feature Inspiration</sub>
</td>
<td align="center" width="25%">
🎭<br><strong>Material Design</strong><br><sub>Design Principles</sub>
</td>
<td align="center" width="25%">
🖼️<br><strong>Pillow Team</strong><br><sub>Image Library</sub>
</td>
<td align="center" width="25%">
⚡<br><strong>Qt Project</strong><br><sub>UI Framework</sub>
</td>
</tr>
</table>

<br>

---

<br>

## 📞 Support

<table>
<tr>
<td align="center" width="33%">
<br>
<img src="https://img.icons8.com/fluency/96/000000/bug.png" width="48"/>
<br><br>
<strong>Report Bugs</strong>
<br>
<a href="https://github.com/yourusername/image-converter-pro/issues">GitHub Issues</a>
</td>
<td align="center" width="33%">
<br>
<img src="https://img.icons8.com/fluency/96/000000/book.png" width="48"/>
<br><br>
<strong>Documentation</strong>
<br>
<a href="#-usage">Usage Guide</a>
</td>
<td align="center" width="33%">
<br>
<img src="https://img.icons8.com/fluency/96/000000/help.png" width="48"/>
<br><br>
<strong>Get Help</strong>
<br>
<a href="#-troubleshooting">Troubleshooting</a>
</td>
</tr>
</table>

<br>

---

<br>

## 🗓️ Changelog

### Version 1.0.0 (2025)

```diff
+ Initial release
+ Single and batch conversion
+ Modern dark theme interface
+ Support for 10+ image formats
+ Image adjustments (brightness, contrast, saturation, sharpness)
+ Preset system with 5 built-in presets
+ Metadata viewer and privacy controls
+ Comprehensive keyboard shortcuts
+ Multi-threaded batch processing
+ Drag & drop support
```

<br>

---

<br>

<div align="center">

## 🌟 Star History

**If you find this project useful, please consider giving it a star!** ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/image-converter-pro&type=Date)](https://star-history.com/#yourusername/image-converter-pro&Date)

<br>

---

<br>

### **Made with ❤️ and Python**

<br>

[![GitHub followers](https://img.shields.io/github/followers/yourusername?style=social)](https://github.com/yourusername)
[![GitHub stars](https://img.shields.io/github/stars/yourusername/image-converter-pro?style=social)](https://github.com/yourusername/image-converter-pro)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/image-converter-pro?style=social)](https://github.com/yourusername/image-converter-pro)

<br>

[⬆ Back to Top](#-image-converter-pro)

</div># 🎨 Image Converter Pro

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![Status](https://img.shields.io/badge/status-active-success)

**A professional, feature-rich image conversion tool built with PySide6**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Screenshots](#-screenshots) • [Contributing](#-contributing)

</div>

---

## 📸 Screenshots

### Main Interface - Single Conversion
![Main Interface](screenshots/main-interface.png)
*Clean, modern dark theme with intuitive controls*

### Batch Processing
![Batch Processing](screenshots/batch-processing.png)
*Process hundreds of images at once with real-time progress tracking*

### Image Adjustments
![Adjustments](screenshots/adjustments.png)
*Fine-tune brightness, contrast, saturation, and sharpness*

---

## ✨ Features

### 🎯 Modern Format Support
- **JPEG** - Universal photo format with adjustable quality
- **PNG** - Lossless compression with transparency support
- **WebP** - Modern web format (25-34% smaller than JPEG)
- **AVIF** - Next-gen format with superior compression (93%+ browser support)
- **HEIC** - Apple's iPhone photo format (read-only for conversion)
- **GIF** - Animated images with transparency
- **TIFF** - Professional/print quality format
- **BMP**, **ICO**, **PDF** - Additional format support

### ⚡ Core Capabilities

#### Single & Batch Conversion
- Convert one image or process hundreds at once
- Drag & drop support for quick workflows
- Real-time progress tracking with pause/resume/stop controls
- Visual success/failure indicators

#### Smart Preset System
Save your favorite settings as reusable presets:
- 📱 **Web Optimization** - WebP format, compressed, metadata stripped
- 📷 **Social Media** - Perfect for Instagram/Facebook
- 🖨️ **Print Quality** - Lossless TIFF, maximum resolution
- 📧 **Email Friendly** - Optimized file size for attachments
- 🔒 **Privacy Safe** - All metadata removed including GPS

#### Professional Image Adjustments
- **Brightness** - Lighten or darken images
- **Contrast** - Enhance or reduce contrast
- **Saturation** - Adjust color intensity
- **Sharpness** - Add or reduce sharpness
- **Resize** - Scale images with aspect ratio lock
- **Resampling** - Choose from Lanczos, Bicubic, Bilinear, or Nearest

#### Advanced Features
- 🔍 **Metadata Viewer** - View and manage EXIF data
- 🔐 **Privacy Controls** - Strip GPS location while preserving other data
- 📊 **Quality Control** - Adjustable quality slider with real-time feedback
- 🎨 **Dark Theme** - Modern, professional interface
- ⌨️ **Keyboard Shortcuts** - Full keyboard navigation support
- 📁 **Smart File Management** - Recent files, custom output folders

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/image-converter-pro.git
cd image-converter-pro
```

### Step 2: Install Dependencies

**Essential packages:**
```bash
pip install PySide6 Pillow
```

**Optional - Advanced format support:**
```bash
# For AVIF support (recommended)
pip install pillow-avif-plugin

# For HEIC/HEIF support (iPhone photos)
pip install pillow-heif
```

### Step 3: Run the Application
```bash
python main.py
```

---

## 📖 Usage

### Quick Start Guide

#### Single Image Conversion

1. **Load an Image**
   - Click "Select Image" or press `Ctrl+O`
   - Or drag & drop an image into the preview area

2. **Choose Format**
   - Select your desired output format from the dropdown
   - View format description and recommendations

3. **Adjust Settings** (Optional)
   - Set quality level for lossy formats
   - Enable resize and set dimensions
   - Fine-tune brightness, contrast, saturation, sharpness
   - Configure metadata options

4. **Convert**
   - Click "Convert & Save" or press `F5`
   - Choose output location
   - Done! 🎉

#### Batch Processing

1. **Add Images**
   - Switch to "Batch Processing" tab
   - Click "Add Files" to select multiple images
   - Or click "Add Folder" to add all images from a directory
   - Or drag & drop multiple files

2. **Configure Settings**
   - Settings from Single Conversion tab apply to all images
   - Or load a preset for consistent processing

3. **Process**
   - Click "Process Batch"
   - Monitor real-time progress
   - Use Pause/Resume/Stop controls as needed

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open Image |
| `Ctrl+Shift+O` | Open Multiple Images |
| `Ctrl+S` | Save/Convert |
| `F5` | Convert Image |
| `Ctrl+B` | Add to Batch |
| `Ctrl+Shift+C` | Clear Batch Queue |
| `Ctrl+Q` | Quit Application |
| `F1` | Show Keyboard Shortcuts |
| `+` / `-` | Zoom In/Out Preview |

---

## 💡 Usage Tips

### Format Recommendations

**For Web Use:**
- Use **WebP** at 80-85% quality for best size/quality balance
- Or **AVIF** at 70-80% for cutting-edge compression

**For Photos with Transparency:**
- Use **PNG** for lossless quality
- Or **WebP** for smaller file size

**For Maximum Quality:**
- Use **TIFF** or **PNG** (lossless)

**For Email/Sharing:**
- Use **JPEG** at 75-80% quality
- Enable resize to 1280x720 or smaller

**For Social Media:**
- Instagram/Facebook: **JPEG** at 90% quality, 1080x1080 or 1920x1080
- Use the "Social Media" preset for optimal settings

### Batch Processing Best Practices

1. **Test First** - Process 1-2 sample images to verify settings
2. **Use Presets** - Create presets for common workflows
3. **Monitor Progress** - Watch the first few conversions for errors
4. **Check Disk Space** - Large batches require significant storage
5. **Review Results** - Enable "Open folder after save" to check output

### Privacy & Metadata

- **Strip GPS** when sharing photos publicly to protect your location
- **View Metadata** before stripping to preserve important information
- **Preserve EXIF** for archival purposes (camera settings, dates)
- Some formats (PNG, BMP) have limited EXIF support

---

## 🗂️ Project Structure

```
image-converter-pro/
├── main.py                 # Main application entry point
├── config.py              # Configuration and preset management
├── formats.py             # Format definitions and detection
├── processor.py           # Image processing engine
├── batch_processor.py     # Batch processing with threading
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── screenshots/           # Application screenshots
│   ├── main-interface.png
│   ├── batch-processing.png
│   └── adjustments.png
└── LICENSE               # MIT License
```

---

## 🛠️ Technical Details

### Built With
- **PySide6** - Qt for Python (UI framework)
- **Pillow (PIL)** - Python Imaging Library (image processing)
- **Python 3.8+** - Programming language

### Architecture
- **Modular Design** - Separated concerns for maintainability
- **Threading** - QThread for non-blocking batch processing
- **Signal/Slot** - Event-driven architecture
- **JSON Config** - Persistent settings and presets
- **Type Hints** - Full type annotation for code clarity

### System Requirements

**Minimum:**
- Python 3.8+
- 4GB RAM
- 100MB disk space

**Recommended:**
- Python 3.10+
- 8GB RAM
- SSD for faster processing
- Multi-core CPU for batch operations

---

## 🐛 Troubleshooting

### Format Support Issues

**"AVIF format not supported"**
```bash
pip install pillow-avif-plugin
```

**"HEIC format not supported"**
```bash
pip install pillow-heif
```

**"WebP format not supported"**
```bash
pip install pillow[webp]
```

### Performance Issues

- **Slow batch processing** - Reduce batch size or enable fewer adjustments
- **High memory usage** - Enable resize for very large images
- **Slow preview** - Disable real-time adjustments for large files

### Common Errors

**"Module not found: PySide6"**
```bash
pip install PySide6
```

**"No module named PIL"**
```bash
pip install Pillow
```

**"Image fails to convert"**
- Check if output format is writable (HEIC is read-only)
- Verify disk space is available
- Try converting to a different format

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the Repository**
2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Commit Your Changes**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. **Push to the Branch**
   ```bash
   git push origin feature/AmazingFeature
   ```
5. **Open a Pull Request**

### Ideas for Contributions
- Add new image formats (JPEG XL, JXR, etc.)
- Implement additional filters (blur, edge detection, etc.)
- Add watermarking functionality
- Create light theme option
- Improve batch processing performance
- Add cloud storage integration
- Implement undo/redo for settings
- Add command-line interface
- Create plugin system for extensions

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Image Converter Pro

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

- **XnConvert** & **IrfanView** - Inspiration for features and workflow
- **Material Design** - Color palette and design principles
- **Pillow Team** - Excellent image processing library
- **Qt Project** - Powerful cross-platform UI framework

---

## 📞 Support

- **Issues** - Report bugs via [GitHub Issues](https://github.com/yourusername/image-converter-pro/issues)
- **Documentation** - Check this README for detailed information
- **Dependencies** - Verify all packages are installed correctly

---

## 🗓️ Changelog

### Version 1.0.0 (2025)
- 🎉 Initial release
- ✨ Single and batch conversion
- 🎨 Modern dark theme interface
- 📦 Support for 10+ image formats (JPEG, PNG, WebP, AVIF, HEIC, etc.)
- 🎛️ Image adjustments (brightness, contrast, saturation, sharpness)
- 📋 Preset system with 5 built-in presets
- 🔍 Metadata viewer and privacy controls
- ⌨️ Comprehensive keyboard shortcuts
- 🧵 Multi-threaded batch processing
- 📱 Drag & drop support

---

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

<div align="center">

**Made with ❤️ and Python**

[⬆ Back to Top](#-image-converter-pro)

</div>

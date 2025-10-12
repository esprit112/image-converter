"""
Image Converter Pro - Professional Image Conversion Tool
Built with PySide6 for modern, feature-rich image processing

Features:
- Modern format support (JPEG, PNG, WebP, AVIF, HEIC)
- Batch processing with queue management
- Preset system for workflows
- Dark/Light theme
- Comprehensive keyboard shortcuts
- Image adjustments and filters
- Metadata handling
- Before/After comparison
- Multi-threading support
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Optional, List, Dict

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QFileDialog, QLineEdit,
    QCheckBox, QSlider, QSpinBox, QGroupBox, QSplitter,
    QMessageBox, QProgressBar, QListWidget, QListWidgetItem,
    QMenuBar, QMenu, QStatusBar, QTextEdit, QTabWidget,
    QFrame, QScrollArea, QDialog, QDialogButtonBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QToolBar, QToolButton
)
from PySide6.QtCore import Qt, QSize, QTimer, QSettings, Signal, QThread
from PySide6.QtGui import (
    QPixmap, QImage, QDragEnterEvent, QDropEvent, QAction,
    QKeySequence, QFont, QIcon, QPalette, QColor, QShortcut
)
from PIL import Image

# Import our modules
from config import Config
from formats import (
    get_all_formats, get_writable_formats, get_format_info,
    get_file_filter, supports_quality, check_format_availability,
    get_format_description, get_missing_format_help
)
from processor import ImageProcessor
from batch_processor import BatchProcessor, BatchQueue, generate_output_path


class ImagePreview(QLabel):
    """Custom image preview widget with drag-and-drop"""
    
    file_dropped = Signal(str)
    files_dropped = Signal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("Drop image(s) here\nor click 'Select Image'")
        self.setScaledContents(False)
        self.setAcceptDrops(True)
        self.original_pixmap = None
        self.zoom_level = 1.0
        self.apply_style()
    
    def apply_style(self):
        self.setStyleSheet("""
            QLabel {
                background-color: #1E1E1E;
                border: 2px dashed #404040;
                border-radius: 8px;
                color: #808080;
                font-size: 14px;
            }
        """)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QLabel {
                    background-color: #2C2C2C;
                    border: 2px solid #2196F3;
                    border-radius: 8px;
                    color: #2196F3;
                    font-size: 14px;
                }
            """)
    
    def dragLeaveEvent(self, event):
        self.apply_style()
    
    def dropEvent(self, event: QDropEvent):
        self.apply_style()
        urls = event.mimeData().urls()
        if urls:
            files = [url.toLocalFile() for url in urls if self.is_image_file(url.toLocalFile())]
            if len(files) == 1:
                self.file_dropped.emit(files[0])
            elif len(files) > 1:
                self.files_dropped.emit(files)
    
    def is_image_file(self, path: str) -> bool:
        valid_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', 
                     '.tiff', '.tif', '.avif', '.heic', '.heif'}
        return Path(path).suffix.lower() in valid_exts
    
    def set_image(self, path: str):
        try:
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                self.original_pixmap = pixmap
                self.zoom_level = 1.0
                self.update_pixmap()
                self.setStyleSheet("""
                    QLabel {
                        background-color: #1E1E1E;
                        border: 2px solid #404040;
                        border-radius: 8px;
                    }
                """)
        except Exception as e:
            self.setText(f"Preview failed: {e}")
    
    def update_pixmap(self):
        if self.original_pixmap:
            scaled = self.original_pixmap.scaled(
                int(self.size().width() * self.zoom_level),
                int(self.size().height() * self.zoom_level),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled)
    
    def zoom_in(self):
        self.zoom_level = min(3.0, self.zoom_level * 1.2)
        self.update_pixmap()
    
    def zoom_out(self):
        self.zoom_level = max(0.1, self.zoom_level / 1.2)
        self.update_pixmap()
    
    def reset_zoom(self):
        self.zoom_level = 1.0
        self.update_pixmap()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_pixmap()


class ModernButton(QPushButton):
    """Styled button with modern appearance"""
    
    def __init__(self, text: str, primary: bool = False, icon_name: Optional[str] = None, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self.apply_style()
    
    def apply_style(self):
        if self.primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 24px;
                    font-size: 14px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
                QPushButton:disabled {
                    background-color: #424242;
                    color: #808080;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #2C2C2C;
                    color: #E0E0E0;
                    border: 1px solid #404040;
                    border-radius: 6px;
                    padding: 10px 24px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #3C3C3C;
                    border-color: #606060;
                }
                QPushButton:pressed {
                    background-color: #4C4C4C;
                }
                QPushButton:disabled {
                    background-color: #252525;
                    color: #606060;
                }
            """)


class PresetDialog(QDialog):
    """Dialog for managing presets"""
    
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Manage Presets")
        self.setMinimumSize(600, 400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Presets list
        self.presets_list = QListWidget()
        self.refresh_presets()
        layout.addWidget(QLabel("Available Presets:"))
        layout.addWidget(self.presets_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        load_btn = ModernButton("Load Preset", primary=True)
        load_btn.clicked.connect(self.load_preset)
        btn_layout.addWidget(load_btn)
        
        delete_btn = ModernButton("Delete")
        delete_btn.clicked.connect(self.delete_preset)
        btn_layout.addWidget(delete_btn)
        
        export_btn = ModernButton("Export")
        export_btn.clicked.connect(self.export_preset)
        btn_layout.addWidget(export_btn)
        
        import_btn = ModernButton("Import")
        import_btn.clicked.connect(self.import_preset)
        btn_layout.addWidget(import_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Close button
        close_btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_btn.rejected.connect(self.reject)
        layout.addWidget(close_btn)
    
    def refresh_presets(self):
        self.presets_list.clear()
        for preset_name in self.config.get_presets():
            self.presets_list.addItem(preset_name)
    
    def load_preset(self):
        current = self.presets_list.currentItem()
        if current:
            self.accept()
    
    def delete_preset(self):
        current = self.presets_list.currentItem()
        if current:
            preset_name = current.text()
            reply = QMessageBox.question(
                self, "Delete Preset",
                f"Are you sure you want to delete '{preset_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.config.delete_preset(preset_name)
                self.refresh_presets()
    
    def export_preset(self):
        current = self.presets_list.currentItem()
        if current:
            preset_name = current.text()
            path, _ = QFileDialog.getSaveFileName(
                self, "Export Preset", f"{preset_name}.json",
                "JSON Files (*.json)"
            )
            if path:
                self.config.export_preset(preset_name, Path(path))
                QMessageBox.information(self, "Success", "Preset exported successfully!")
    
    def import_preset(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Preset", "",
            "JSON Files (*.json)"
        )
        if path:
            name, ok = QInputDialog.getText(
                self, "Preset Name", "Enter name for imported preset:"
            )
            if ok and name:
                if self.config.import_preset(Path(path), name):
                    self.refresh_presets()
                    QMessageBox.information(self, "Success", "Preset imported successfully!")
                else:
                    QMessageBox.warning(self, "Error", "Failed to import preset!")


class ImageConverterApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.processor = ImageProcessor()
        self.batch_queue = BatchQueue()
        self.batch_processor: Optional[BatchProcessor] = None
        self.src_path: Optional[str] = None
        self.current_preset = "default"
        
        self.init_ui()
        self.apply_theme()
        self.setup_shortcuts()
        self.check_format_support()
    
    def init_ui(self):
        self.setWindowTitle("Image Converter Pro")
        self.setMinimumSize(1200, 800)
        
        # Create menu bar
        self.create_menus()
        
        # Create toolbar
        self.create_toolbar()
        
        # Central widget with tabs
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Single conversion tab
        single_tab = self.create_single_tab()
        self.tabs.addTab(single_tab, "Single Conversion")
        
        # Batch conversion tab
        batch_tab = self.create_batch_tab()
        self.tabs.addTab(batch_tab, "Batch Processing")
        
        # Status bar
        self.statusBar().showMessage("Ready")
        self.status_label = QLabel("")
        self.statusBar().addPermanentWidget(self.status_label)
    
    def create_menus(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open Image...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.select_image)
        file_menu.addAction(open_action)
        
        open_batch_action = QAction("Open &Multiple Images...", self)
        open_batch_action.setShortcut("Ctrl+Shift+O")
        open_batch_action.triggered.connect(self.select_batch_images)
        file_menu.addAction(open_batch_action)
        
        file_menu.addSeparator()
        
        # Recent files submenu
        self.recent_menu = file_menu.addMenu("Recent Files")
        self.update_recent_menu()
        
        file_menu.addSeparator()
        
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        prefs_action = QAction("&Preferences...", self)
        prefs_action.triggered.connect(self.show_preferences)
        edit_menu.addAction(prefs_action)
        
        # Presets menu
        presets_menu = menubar.addMenu("&Presets")
        
        save_preset_action = QAction("&Save Current as Preset...", self)
        save_preset_action.triggered.connect(self.save_current_preset)
        presets_menu.addAction(save_preset_action)
        
        manage_presets_action = QAction("&Manage Presets...", self)
        manage_presets_action.triggered.connect(self.show_preset_manager)
        presets_menu.addAction(manage_presets_action)
        
        presets_menu.addSeparator()
        
        # Dynamic preset list
        self.presets_menu_dynamic = presets_menu
        self.update_presets_menu()
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        shortcuts_action = QAction("Keyboard &Shortcuts", self)
        shortcuts_action.setShortcut("F1")
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Add actions
        open_btn = QAction("Open", self)
        open_btn.triggered.connect(self.select_image)
        toolbar.addAction(open_btn)
        
        toolbar.addSeparator()
        
        convert_btn = QAction("Convert", self)
        convert_btn.triggered.connect(self.convert_image)
        toolbar.addAction(convert_btn)
        
        toolbar.addSeparator()
        
        batch_btn = QAction("Batch Mode", self)
        batch_btn.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        toolbar.addAction(batch_btn)
    
    def create_single_tab(self) -> QWidget:
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Left panel - Controls
        left_panel = self.create_control_panel()
        
        # Right panel - Preview
        right_panel = self.create_preview_panel()
        
        # Splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([400, 800])
        
        layout.addWidget(splitter)
        
        return tab
    
    def create_control_panel(self) -> QWidget:
        panel = QWidget()
        panel.setMaximumWidth(450)  # Set maximum width for control panel
        layout = QVBoxLayout(panel)
        layout.setSpacing(20)  # Increased spacing between sections
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title
        title = QLabel("Image Converter Pro")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #2196F3; margin-bottom: 8px;")
        layout.addWidget(title)
        
        # Preset selector
        preset_group = QGroupBox("Quick Preset")
        preset_layout = QVBoxLayout()
        preset_layout.setContentsMargins(12, 20, 12, 12)
        self.preset_combo = QComboBox()
        self.preset_combo.setMinimumHeight(40)
        self.preset_combo.addItems(["Custom"] + self.config.get_presets())
        self.preset_combo.currentTextChanged.connect(self.load_preset_from_combo)
        preset_layout.addWidget(self.preset_combo)
        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)
        
        # File selection
        file_group = QGroupBox("Source Image")
        file_layout = QVBoxLayout()
        file_layout.setContentsMargins(12, 20, 12, 12)
        
        select_btn = ModernButton("Select Image", primary=True)
        select_btn.setMinimumHeight(44)
        select_btn.clicked.connect(self.select_image)
        file_layout.addWidget(select_btn)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setWordWrap(True)
        self.file_label.setStyleSheet("color: #B0B0B0; font-size: 13px; padding: 8px; min-height: 20px;")
        file_layout.addWidget(self.file_label)
        
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #808080; font-size: 12px; padding: 4px; min-height: 18px;")
        self.info_label.setWordWrap(True)
        file_layout.addWidget(self.info_label)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Format selection
        format_group = QGroupBox("Output Format")
        format_layout = QVBoxLayout()
        format_layout.setContentsMargins(12, 20, 12, 12)
        
        self.format_combo = QComboBox()
        self.format_combo.setMinimumHeight(40)
        writable_formats = get_writable_formats()
        self.format_combo.addItems(writable_formats)
        default_format = self.config.get("default_format", "PNG")
        if default_format in writable_formats:
            self.format_combo.setCurrentText(default_format)
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        self.format_combo.setToolTip("Select output format")
        format_layout.addWidget(self.format_combo)
        
        # Format description
        self.format_desc_label = QLabel("")
        self.format_desc_label.setWordWrap(True)
        self.format_desc_label.setStyleSheet("color: #909090; font-size: 11px; padding: 6px; line-height: 1.4;")
        self.format_desc_label.setMinimumHeight(40)
        format_layout.addWidget(self.format_desc_label)
        
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # Quality settings
        self.quality_group = QGroupBox("Quality Settings")
        quality_layout = QVBoxLayout()
        quality_layout.setContentsMargins(12, 20, 12, 12)
        
        quality_label_layout = QHBoxLayout()
        quality_label = QLabel("Quality:")
        quality_label.setStyleSheet("font-size: 13px;")
        quality_label_layout.addWidget(quality_label)
        self.quality_value_label = QLabel("85%")
        self.quality_value_label.setStyleSheet("font-weight: bold; color: #2196F3; font-size: 14px;")
        quality_label_layout.addWidget(self.quality_value_label)
        quality_label_layout.addStretch()
        quality_layout.addLayout(quality_label_layout)
        
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setMinimum(1)
        self.quality_slider.setMaximum(100)
        self.quality_slider.setValue(self.config.get("jpeg_quality", 85))
        self.quality_slider.setMinimumHeight(30)
        self.quality_slider.valueChanged.connect(self.update_quality_label)
        quality_layout.addWidget(self.quality_slider)
        
        self.quality_group.setLayout(quality_layout)
        layout.addWidget(self.quality_group)
        
        # Resize options
        resize_group = QGroupBox("Resize (Optional)")
        resize_layout = QVBoxLayout()
        resize_layout.setContentsMargins(12, 20, 12, 12)
        resize_layout.setSpacing(10)
        
        self.resize_check = QCheckBox("Enable Resize")
        self.resize_check.setStyleSheet("font-size: 13px; padding: 4px;")
        self.resize_check.toggled.connect(self.toggle_resize)
        resize_layout.addWidget(self.resize_check)
        
        size_layout = QHBoxLayout()
        size_layout.setSpacing(8)
        
        width_label = QLabel("Width:")
        width_label.setMinimumWidth(50)
        size_layout.addWidget(width_label)
        self.width_spin = QSpinBox()
        self.width_spin.setMinimumHeight(32)
        self.width_spin.setRange(1, 10000)
        self.width_spin.setValue(1920)
        self.width_spin.setEnabled(False)
        self.width_spin.valueChanged.connect(self.on_width_changed)
        size_layout.addWidget(self.width_spin)
        
        height_label = QLabel("Height:")
        height_label.setMinimumWidth(50)
        size_layout.addWidget(height_label)
        self.height_spin = QSpinBox()
        self.height_spin.setMinimumHeight(32)
        self.height_spin.setRange(1, 10000)
        self.height_spin.setValue(1080)
        self.height_spin.setEnabled(False)
        self.height_spin.valueChanged.connect(self.on_height_changed)
        size_layout.addWidget(self.height_spin)
        
        resize_layout.addLayout(size_layout)
        
        self.aspect_lock_check = QCheckBox("Lock Aspect Ratio")
        self.aspect_lock_check.setStyleSheet("font-size: 13px; padding: 4px;")
        self.aspect_lock_check.setChecked(True)
        self.aspect_lock_check.setEnabled(False)
        resize_layout.addWidget(self.aspect_lock_check)
        
        # Resample method
        resample_layout = QHBoxLayout()
        resample_layout.setSpacing(8)
        method_label = QLabel("Method:")
        method_label.setMinimumWidth(60)
        resample_layout.addWidget(method_label)
        self.resample_combo = QComboBox()
        self.resample_combo.setMinimumHeight(36)
        self.resample_combo.addItems(["Lanczos", "Bicubic", "Bilinear", "Nearest"])
        self.resample_combo.setCurrentText("Lanczos")
        self.resample_combo.setEnabled(False)
        self.resample_combo.setToolTip("Lanczos: Best quality\nBicubic: Balanced\nBilinear: Fast\nNearest: Fastest, pixel art")
        resample_layout.addWidget(self.resample_combo)
        resize_layout.addLayout(resample_layout)
        
        resize_group.setLayout(resize_layout)
        layout.addWidget(resize_group)
        
        # Image adjustments - Make collapsible or compact
        adjust_group = QGroupBox("Adjustments (Optional)")
        adjust_layout = QVBoxLayout()
        adjust_layout.setContentsMargins(12, 20, 12, 12)
        adjust_layout.setSpacing(8)
        
        # Brightness
        bright_layout = QHBoxLayout()
        bright_label = QLabel("Brightness:")
        bright_label.setMinimumWidth(80)
        bright_layout.addWidget(bright_label)
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setMinimum(0)
        self.brightness_slider.setMaximum(200)
        self.brightness_slider.setValue(100)
        self.brightness_slider.setMinimumHeight(24)
        bright_layout.addWidget(self.brightness_slider)
        self.brightness_label = QLabel("1.0")
        self.brightness_label.setMinimumWidth(35)
        self.brightness_label.setStyleSheet("font-size: 12px;")
        bright_layout.addWidget(self.brightness_label)
        self.brightness_slider.valueChanged.connect(
            lambda v: self.brightness_label.setText(f"{v/100:.1f}")
        )
        adjust_layout.addLayout(bright_layout)
        
        # Contrast
        contrast_layout = QHBoxLayout()
        contrast_label = QLabel("Contrast:")
        contrast_label.setMinimumWidth(80)
        contrast_layout.addWidget(contrast_label)
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setMinimum(0)
        self.contrast_slider.setMaximum(200)
        self.contrast_slider.setValue(100)
        self.contrast_slider.setMinimumHeight(24)
        contrast_layout.addWidget(self.contrast_slider)
        self.contrast_label = QLabel("1.0")
        self.contrast_label.setMinimumWidth(35)
        self.contrast_label.setStyleSheet("font-size: 12px;")
        contrast_layout.addWidget(self.contrast_label)
        self.contrast_slider.valueChanged.connect(
            lambda v: self.contrast_label.setText(f"{v/100:.1f}")
        )
        adjust_layout.addLayout(contrast_layout)
        
        # Saturation
        sat_layout = QHBoxLayout()
        sat_label = QLabel("Saturation:")
        sat_label.setMinimumWidth(80)
        sat_layout.addWidget(sat_label)
        self.saturation_slider = QSlider(Qt.Orientation.Horizontal)
        self.saturation_slider.setMinimum(0)
        self.saturation_slider.setMaximum(200)
        self.saturation_slider.setValue(100)
        self.saturation_slider.setMinimumHeight(24)
        sat_layout.addWidget(self.saturation_slider)
        self.saturation_label = QLabel("1.0")
        self.saturation_label.setMinimumWidth(35)
        self.saturation_label.setStyleSheet("font-size: 12px;")
        sat_layout.addWidget(self.saturation_label)
        self.saturation_slider.valueChanged.connect(
            lambda v: self.saturation_label.setText(f"{v/100:.1f}")
        )
        adjust_layout.addLayout(sat_layout)
        
        # Sharpness
        sharp_layout = QHBoxLayout()
        sharp_label = QLabel("Sharpness:")
        sharp_label.setMinimumWidth(80)
        sharp_layout.addWidget(sharp_label)
        self.sharpness_slider = QSlider(Qt.Orientation.Horizontal)
        self.sharpness_slider.setMinimum(0)
        self.sharpness_slider.setMaximum(200)
        self.sharpness_slider.setValue(100)
        self.sharpness_slider.setMinimumHeight(24)
        sharp_layout.addWidget(self.sharpness_slider)
        self.sharpness_label = QLabel("1.0")
        self.sharpness_label.setMinimumWidth(35)
        self.sharpness_label.setStyleSheet("font-size: 12px;")
        sharp_layout.addWidget(self.sharpness_label)
        self.sharpness_slider.valueChanged.connect(
            lambda v: self.sharpness_label.setText(f"{v/100:.1f}")
        )
        adjust_layout.addLayout(sharp_layout)
        
        # Reset button
        reset_adj_btn = ModernButton("Reset All")
        reset_adj_btn.setMinimumHeight(36)
        reset_adj_btn.clicked.connect(self.reset_adjustments)
        adjust_layout.addWidget(reset_adj_btn)
        
        adjust_group.setLayout(adjust_layout)
        layout.addWidget(adjust_group)
        
        # Metadata options
        metadata_group = QGroupBox("Metadata")
        metadata_layout = QVBoxLayout()
        metadata_layout.setContentsMargins(12, 20, 12, 12)
        metadata_layout.setSpacing(10)
        
        self.preserve_metadata_check = QCheckBox("Preserve EXIF data")
        self.preserve_metadata_check.setStyleSheet("font-size: 13px; padding: 4px;")
        self.preserve_metadata_check.setChecked(self.config.get("preserve_metadata", True))
        metadata_layout.addWidget(self.preserve_metadata_check)
        
        self.strip_gps_check = QCheckBox("Strip GPS location (privacy)")
        self.strip_gps_check.setStyleSheet("font-size: 13px; padding: 4px;")
        self.strip_gps_check.setChecked(self.config.get("strip_gps", False))
        metadata_layout.addWidget(self.strip_gps_check)
        
        view_metadata_btn = ModernButton("View Metadata")
        view_metadata_btn.setMinimumHeight(36)
        view_metadata_btn.clicked.connect(self.view_metadata)
        metadata_layout.addWidget(view_metadata_btn)
        
        metadata_group.setLayout(metadata_layout)
        layout.addWidget(metadata_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        options_layout.setContentsMargins(12, 20, 12, 12)
        
        self.open_folder_check = QCheckBox("Open output folder after save")
        self.open_folder_check.setStyleSheet("font-size: 13px; padding: 4px;")
        self.open_folder_check.setChecked(self.config.get("open_after_save", True))
        self.open_folder_check.toggled.connect(self.save_preferences)
        options_layout.addWidget(self.open_folder_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Output folder
        folder_btn = ModernButton("Change Output Folder")
        folder_btn.setMinimumHeight(40)
        folder_btn.clicked.connect(self.select_output_folder)
        layout.addWidget(folder_btn)
        
        self.folder_label = QLabel(f"Output: {self.config.get('last_output_folder', '')}")
        self.folder_label.setWordWrap(True)
        self.folder_label.setStyleSheet("color: #808080; font-size: 11px; padding: 6px;")
        layout.addWidget(self.folder_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(10)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Convert button
        self.convert_btn = ModernButton("Convert & Save", primary=True)
        self.convert_btn.setMinimumHeight(50)
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #424242;
                color: #808080;
            }
        """)
        self.convert_btn.clicked.connect(self.convert_image)
        self.convert_btn.setEnabled(False)
        layout.addWidget(self.convert_btn)
        
        layout.addStretch()
        
        # Create scroll area for the panel
        scroll = QScrollArea()
        scroll.setWidget(panel)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # Update quality visibility
        self.on_format_changed(self.format_combo.currentText())
        
        return scroll
        
        # Quality settings
        self.quality_group = QGroupBox("Quality Settings")
        quality_layout = QVBoxLayout()
        
        quality_label_layout = QHBoxLayout()
        quality_label_layout.addWidget(QLabel("Quality:"))
        self.quality_value_label = QLabel("85%")
        self.quality_value_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        quality_label_layout.addWidget(self.quality_value_label)
        quality_label_layout.addStretch()
        quality_layout.addLayout(quality_label_layout)
        
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setMinimum(1)
        self.quality_slider.setMaximum(100)
        self.quality_slider.setValue(self.config.get("jpeg_quality", 85))
        self.quality_slider.valueChanged.connect(self.update_quality_label)
        quality_layout.addWidget(self.quality_slider)
        
        self.quality_group.setLayout(quality_layout)
        layout.addWidget(self.quality_group)
        
        # Resize options
        resize_group = QGroupBox("Resize (Optional)")
        resize_layout = QVBoxLayout()
        
        self.resize_check = QCheckBox("Enable Resize")
        self.resize_check.toggled.connect(self.toggle_resize)
        resize_layout.addWidget(self.resize_check)
        
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Width:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 10000)
        self.width_spin.setValue(1920)
        self.width_spin.setEnabled(False)
        self.width_spin.valueChanged.connect(self.on_width_changed)
        size_layout.addWidget(self.width_spin)
        
        size_layout.addWidget(QLabel("Height:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 10000)
        self.height_spin.setValue(1080)
        self.height_spin.setEnabled(False)
        self.height_spin.valueChanged.connect(self.on_height_changed)
        size_layout.addWidget(self.height_spin)
        
        resize_layout.addLayout(size_layout)
        
        self.aspect_lock_check = QCheckBox("Lock Aspect Ratio")
        self.aspect_lock_check.setChecked(True)
        self.aspect_lock_check.setEnabled(False)
        resize_layout.addWidget(self.aspect_lock_check)
        
        # Resample method
        resample_layout = QHBoxLayout()
        resample_layout.addWidget(QLabel("Method:"))
        self.resample_combo = QComboBox()
        self.resample_combo.addItems(["Lanczos", "Bicubic", "Bilinear", "Nearest"])
        self.resample_combo.setCurrentText("Lanczos")
        self.resample_combo.setEnabled(False)
        self.resample_combo.setToolTip("Lanczos: Best quality\nBicubic: Balanced\nBilinear: Fast\nNearest: Fastest, pixel art")
        resample_layout.addWidget(self.resample_combo)
        resize_layout.addLayout(resample_layout)
        
        resize_group.setLayout(resize_layout)
        layout.addWidget(resize_group)
        
        # Image adjustments
        adjust_group = QGroupBox("Adjustments (Optional)")
        adjust_layout = QVBoxLayout()
        
        # Brightness
        bright_layout = QHBoxLayout()
        bright_layout.addWidget(QLabel("Brightness:"))
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setMinimum(0)
        self.brightness_slider.setMaximum(200)
        self.brightness_slider.setValue(100)
        self.brightness_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.brightness_slider.setTickInterval(50)
        bright_layout.addWidget(self.brightness_slider)
        self.brightness_label = QLabel("1.0")
        bright_layout.addWidget(self.brightness_label)
        self.brightness_slider.valueChanged.connect(
            lambda v: self.brightness_label.setText(f"{v/100:.1f}")
        )
        adjust_layout.addLayout(bright_layout)
        
        # Contrast
        contrast_layout = QHBoxLayout()
        contrast_layout.addWidget(QLabel("Contrast:"))
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setMinimum(0)
        self.contrast_slider.setMaximum(200)
        self.contrast_slider.setValue(100)
        self.contrast_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.contrast_slider.setTickInterval(50)
        contrast_layout.addWidget(self.contrast_slider)
        self.contrast_label = QLabel("1.0")
        contrast_layout.addWidget(self.contrast_label)
        self.contrast_slider.valueChanged.connect(
            lambda v: self.contrast_label.setText(f"{v/100:.1f}")
        )
        adjust_layout.addLayout(contrast_layout)
        
        # Saturation
        sat_layout = QHBoxLayout()
        sat_layout.addWidget(QLabel("Saturation:"))
        self.saturation_slider = QSlider(Qt.Orientation.Horizontal)
        self.saturation_slider.setMinimum(0)
        self.saturation_slider.setMaximum(200)
        self.saturation_slider.setValue(100)
        self.saturation_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.saturation_slider.setTickInterval(50)
        sat_layout.addWidget(self.saturation_slider)
        self.saturation_label = QLabel("1.0")
        sat_layout.addWidget(self.saturation_label)
        self.saturation_slider.valueChanged.connect(
            lambda v: self.saturation_label.setText(f"{v/100:.1f}")
        )
        adjust_layout.addLayout(sat_layout)
        
        # Sharpness
        sharp_layout = QHBoxLayout()
        sharp_layout.addWidget(QLabel("Sharpness:"))
        self.sharpness_slider = QSlider(Qt.Orientation.Horizontal)
        self.sharpness_slider.setMinimum(0)
        self.sharpness_slider.setMaximum(200)
        self.sharpness_slider.setValue(100)
        self.sharpness_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.sharpness_slider.setTickInterval(50)
        sharp_layout.addWidget(self.sharpness_slider)
        self.sharpness_label = QLabel("1.0")
        sharp_layout.addWidget(self.sharpness_label)
        self.sharpness_slider.valueChanged.connect(
            lambda v: self.sharpness_label.setText(f"{v/100:.1f}")
        )
        adjust_layout.addLayout(sharp_layout)
        
        # Reset button
        reset_adj_btn = ModernButton("Reset All")
        reset_adj_btn.clicked.connect(self.reset_adjustments)
        adjust_layout.addWidget(reset_adj_btn)
        
        adjust_group.setLayout(adjust_layout)
        layout.addWidget(adjust_group)
        
        # Metadata options
        metadata_group = QGroupBox("Metadata")
        metadata_layout = QVBoxLayout()
        
        self.preserve_metadata_check = QCheckBox("Preserve EXIF data")
        self.preserve_metadata_check.setChecked(self.config.get("preserve_metadata", True))
        metadata_layout.addWidget(self.preserve_metadata_check)
        
        self.strip_gps_check = QCheckBox("Strip GPS location (privacy)")
        self.strip_gps_check.setChecked(self.config.get("strip_gps", False))
        metadata_layout.addWidget(self.strip_gps_check)
        
        view_metadata_btn = ModernButton("View Metadata")
        view_metadata_btn.clicked.connect(self.view_metadata)
        metadata_layout.addWidget(view_metadata_btn)
        
        metadata_group.setLayout(metadata_layout)
        layout.addWidget(metadata_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        
        self.open_folder_check = QCheckBox("Open output folder after save")
        self.open_folder_check.setChecked(self.config.get("open_after_save", True))
        self.open_folder_check.toggled.connect(self.save_preferences)
        options_layout.addWidget(self.open_folder_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Output folder
        folder_layout = QHBoxLayout()
        folder_btn = ModernButton("Change Output Folder")
        folder_btn.clicked.connect(self.select_output_folder)
        folder_layout.addWidget(folder_btn)
        layout.addLayout(folder_layout)
        
        self.folder_label = QLabel(f"Output: {self.config.get('last_output_folder', '')}")
        self.folder_label.setWordWrap(True)
        self.folder_label.setStyleSheet("color: #808080; font-size: 11px; padding: 4px;")
        layout.addWidget(self.folder_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Convert button
        self.convert_btn = ModernButton("Convert & Save", primary=True)
        self.convert_btn.clicked.connect(self.convert_image)
        self.convert_btn.setEnabled(False)
        layout.addWidget(self.convert_btn)
        
        layout.addStretch()
        
        # Update quality visibility
        self.on_format_changed(self.format_combo.currentText())
        
        return panel
    
    def create_preview_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        
        # Preview controls
        controls_layout = QHBoxLayout()
        
        preview_title = QLabel("Image Preview")
        preview_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #E0E0E0;")
        controls_layout.addWidget(preview_title)
        
        controls_layout.addStretch()
        
        # Zoom controls
        zoom_out_btn = ModernButton("−")
        zoom_out_btn.setMaximumWidth(40)
        zoom_out_btn.clicked.connect(lambda: self.preview.zoom_out())
        controls_layout.addWidget(zoom_out_btn)
        
        zoom_reset_btn = ModernButton("100%")
        zoom_reset_btn.setMaximumWidth(60)
        zoom_reset_btn.clicked.connect(lambda: self.preview.reset_zoom())
        controls_layout.addWidget(zoom_reset_btn)
        
        zoom_in_btn = ModernButton("+")
        zoom_in_btn.setMaximumWidth(40)
        zoom_in_btn.clicked.connect(lambda: self.preview.zoom_in())
        controls_layout.addWidget(zoom_in_btn)
        
        layout.addLayout(controls_layout)
        
        # Image preview
        self.preview = ImagePreview()
        self.preview.file_dropped.connect(self.load_image)
        self.preview.files_dropped.connect(self.load_batch_images)
        layout.addWidget(self.preview, 1)
        
        return panel
    
    def create_batch_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Title
        title = QLabel("Batch Processing")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2196F3;")
        layout.addWidget(title)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        add_files_btn = ModernButton("Add Files", primary=True)
        add_files_btn.clicked.connect(self.select_batch_images)
        controls_layout.addWidget(add_files_btn)
        
        add_folder_btn = ModernButton("Add Folder")
        add_folder_btn.clicked.connect(self.select_batch_folder)
        controls_layout.addWidget(add_folder_btn)
        
        clear_btn = ModernButton("Clear Queue")
        clear_btn.clicked.connect(self.clear_batch_queue)
        controls_layout.addWidget(clear_btn)
        
        controls_layout.addStretch()
        
        self.batch_process_btn = ModernButton("Process Batch", primary=True)
        self.batch_process_btn.clicked.connect(self.process_batch)
        self.batch_process_btn.setEnabled(False)
        controls_layout.addWidget(self.batch_process_btn)
        
        self.batch_pause_btn = ModernButton("Pause")
        self.batch_pause_btn.clicked.connect(self.pause_batch)
        self.batch_pause_btn.setEnabled(False)
        self.batch_pause_btn.setVisible(False)
        controls_layout.addWidget(self.batch_pause_btn)
        
        self.batch_stop_btn = ModernButton("Stop")
        self.batch_stop_btn.clicked.connect(self.stop_batch)
        self.batch_stop_btn.setEnabled(False)
        self.batch_stop_btn.setVisible(False)
        controls_layout.addWidget(self.batch_stop_btn)
        
        layout.addLayout(controls_layout)
        
        # Batch queue list
        queue_label = QLabel("Batch Queue:")
        queue_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #E0E0E0;")
        layout.addWidget(queue_label)
        
        self.batch_list = QListWidget()
        self.batch_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        layout.addWidget(self.batch_list)
        
        # Batch progress
        self.batch_progress = QProgressBar()
        self.batch_progress.setVisible(False)
        layout.addWidget(self.batch_progress)
        
        self.batch_status_label = QLabel("")
        self.batch_status_label.setStyleSheet("color: #B0B0B0; font-size: 12px;")
        layout.addWidget(self.batch_status_label)
        
        return tab
    
    def apply_theme(self):
        """Apply dark theme to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
            }
            QWidget {
                background-color: #1E1E1E;
                color: #E0E0E0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #2C2C2C;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #1a1a1a;
                font-size: 14px;
                background-color: #2C2C2C;
                color: #E0E0E0;
            }
            QComboBox {
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 10px 12px;
                background-color: #2C2C2C;
                font-size: 14px;
                color: #E0E0E0;
                min-height: 24px;
            }
            QComboBox:hover {
                border-color: #2196F3;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #E0E0E0;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #2C2C2C;
                color: #E0E0E0;
                selection-background-color: #2196F3;
                padding: 4px;
                font-size: 14px;
                min-height: 30px;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
                min-height: 30px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #3C3C3C;
            }
            QCheckBox {
                spacing: 8px;
                font-size: 13px;
                color: #E0E0E0;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #606060;
                background-color: #2C2C2C;
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border-color: #2196F3;
            }
            QCheckBox::indicator:hover {
                border-color: #2196F3;
            }
            QSpinBox {
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                background-color: #2C2C2C;
                color: #E0E0E0;
            }
            QSpinBox:hover {
                border-color: #2196F3;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #404040;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #2196F3;
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #1976D2;
            }
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #404040;
                height: 8px;
                text-align: center;
                color: #E0E0E0;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 4px;
            }
            QListWidget {
                border: 1px solid #404040;
                border-radius: 6px;
                background-color: #2C2C2C;
                color: #E0E0E0;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
            }
            QListWidget::item:hover {
                background-color: #3C3C3C;
            }
            QMenuBar {
                background-color: #2C2C2C;
                color: #E0E0E0;
                border-bottom: 1px solid #404040;
            }
            QMenuBar::item:selected {
                background-color: #3C3C3C;
            }
            QMenu {
                background-color: #2C2C2C;
                color: #E0E0E0;
                border: 1px solid #404040;
            }
            QMenu::item:selected {
                background-color: #2196F3;
            }
            QToolBar {
                background-color: #2C2C2C;
                border-bottom: 1px solid #404040;
                spacing: 8px;
                padding: 4px;
            }
            QStatusBar {
                background-color: #2C2C2C;
                color: #E0E0E0;
                border-top: 1px solid #404040;
            }
            QTabWidget::pane {
                border: 1px solid #404040;
                background-color: #1E1E1E;
            }
            QTabBar::tab {
                background-color: #2C2C2C;
                color: #E0E0E0;
                padding: 10px 20px;
                border: 1px solid #404040;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #1E1E1E;
                border-bottom: 2px solid #2196F3;
            }
            QTabBar::tab:hover {
                background-color: #3C3C3C;
            }
            QTextEdit, QLineEdit {
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                background-color: #2C2C2C;
                color: #E0E0E0;
            }
            QLabel {
                color: #E0E0E0;
            }
        """)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        shortcuts = self.config.get("keyboard_shortcuts", {})
        
        # Open file
        QShortcut(QKeySequence(shortcuts.get("open_file", "Ctrl+O")), 
                 self, self.select_image)
        
        # Convert
        QShortcut(QKeySequence(shortcuts.get("convert", "F5")), 
                 self, self.convert_image)
        
        # Batch add
        QShortcut(QKeySequence(shortcuts.get("batch_add", "Ctrl+B")), 
                 self, self.select_batch_images)
        
        # Clear batch
        QShortcut(QKeySequence(shortcuts.get("clear_batch", "Ctrl+Shift+C")), 
                 self, self.clear_batch_queue)
    
    def check_format_support(self):
        """Check and warn about missing format support"""
        availability = check_format_availability()
        missing = [fmt for fmt, avail in availability.items() if not avail and fmt in ["AVIF", "HEIC", "WEBP"]]
        
        if missing:
            msg = "Some formats have limited support:\n\n"
            for fmt in missing:
                msg += f"• {fmt}: {get_missing_format_help(fmt)}\n"
            
            QTimer.singleShot(1000, lambda: QMessageBox.information(
                self, "Format Support", msg
            ))
    
    def update_recent_menu(self):
        """Update recent files menu"""
        self.recent_menu.clear()
        recent_files = self.config.get_recent_files()
        
        if not recent_files:
            action = self.recent_menu.addAction("No recent files")
            action.setEnabled(False)
        else:
            for file_path in recent_files:
                action = self.recent_menu.addAction(Path(file_path).name)
                action.triggered.connect(lambda checked, p=file_path: self.load_image(p))
            
            self.recent_menu.addSeparator()
            clear_action = self.recent_menu.addAction("Clear Recent")
            clear_action.triggered.connect(self.clear_recent)
    
    def update_presets_menu(self):
        """Update presets menu with available presets"""
        # Remove old preset actions
        actions = self.presets_menu_dynamic.actions()
        for action in actions[2:]:  # Keep first 2 (save, manage)
            self.presets_menu_dynamic.removeAction(action)
        
        # Add preset actions
        for preset_name in self.config.get_presets():
            action = QAction(preset_name, self)
            action.triggered.connect(lambda checked, name=preset_name: self.load_preset(name))
            self.presets_menu_dynamic.addAction(action)
    
    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            self.config.get("last_input_folder", ""),
            get_file_filter()
        )
        if file_path:
            self.load_image(file_path)
    
    def load_image(self, file_path: str):
        self.src_path = file_path
        self.file_label.setText(Path(file_path).name)
        self.preview.set_image(file_path)
        self.convert_btn.setEnabled(True)
        
        # Update config
        self.config.set("last_input_folder", str(Path(file_path).parent))
        self.config.add_recent_file(file_path)
        self.update_recent_menu()
        
        # Get and display image info
        info = self.processor.get_image_info(file_path)
        info_text = f"{info.get('format', 'Unknown')} | {info.get('width', 0)}x{info.get('height', 0)} | "
        info_text += f"{info.get('mode', '')} | {info.get('size_kb', 0):.1f} KB"
        self.info_label.setText(info_text)
        
        # Update resize spinboxes to match image dimensions
        if self.resize_check.isChecked():
            self.width_spin.setValue(info.get('width', 1920))
            self.height_spin.setValue(info.get('height', 1080))
        
        self.statusBar().showMessage(f"Loaded: {Path(file_path).name}")
    
    def select_batch_images(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images for Batch Processing",
            self.config.get("last_input_folder", ""),
            get_file_filter()
        )
        if file_paths:
            self.load_batch_images(file_paths)
    
    def load_batch_images(self, file_paths: List[str]):
        """Add images to batch queue"""
        output_folder = self.config.get("last_output_folder", "")
        format_ext = get_format_info(self.format_combo.currentText()).get("ext", ".png")
        
        for file_path in file_paths:
            dst_path = generate_output_path(
                file_path,
                output_folder,
                format_ext
            )
            self.batch_queue.add_item(file_path, dst_path)
            self.batch_list.addItem(f"{Path(file_path).name} → {Path(dst_path).name}")
        
        self.batch_process_btn.setEnabled(len(self.batch_queue) > 0)
        self.batch_status_label.setText(f"{len(self.batch_queue)} files in queue")
        
        # Switch to batch tab
        self.tabs.setCurrentIndex(1)
    
    def select_batch_folder(self):
        """Add all images from a folder to batch queue"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            self.config.get("last_input_folder", "")
        )
        
        if folder_path:
            # Find all image files
            folder = Path(folder_path)
            image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif', '.avif', '.heic'}
            image_files = []
            
            for ext in image_exts:
                image_files.extend(folder.glob(f"*{ext}"))
                image_files.extend(folder.glob(f"*{ext.upper()}"))
            
            if image_files:
                self.load_batch_images([str(f) for f in image_files])
                QMessageBox.information(self, "Folder Added", f"Added {len(image_files)} images to batch queue")
            else:
                QMessageBox.warning(self, "No Images", "No image files found in selected folder")
    
    def clear_batch_queue(self):
        """Clear the batch queue"""
        reply = QMessageBox.question(
            self, "Clear Queue",
            "Are you sure you want to clear the batch queue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.batch_queue.clear()
            self.batch_list.clear()
            self.batch_process_btn.setEnabled(False)
            self.batch_status_label.setText("Queue cleared")
    
    def process_batch(self):
        """Start batch processing"""
        if len(self.batch_queue) == 0:
            return
        
        # Get conversion parameters
        params = self.get_conversion_params()
        
        # Create batch processor
        self.batch_processor = BatchProcessor(
            self.processor,
            self.batch_queue.get_items(),
            params
        )
        
        # Connect signals
        self.batch_processor.progress_updated.connect(self.on_batch_progress)
        self.batch_processor.item_started.connect(self.on_batch_item_started)
        self.batch_processor.item_completed.connect(self.on_batch_item_completed)
        self.batch_processor.batch_completed.connect(self.on_batch_completed)
        
        # Update UI
        self.batch_process_btn.setEnabled(False)
        self.batch_pause_btn.setEnabled(True)
        self.batch_pause_btn.setVisible(True)
        self.batch_stop_btn.setEnabled(True)
        self.batch_stop_btn.setVisible(True)
        self.batch_progress.setVisible(True)
        self.batch_progress.setValue(0)
        self.batch_progress.setMaximum(len(self.batch_queue))
        
        # Start processing
        self.batch_processor.start()
        self.statusBar().showMessage("Batch processing started...")
    
    def pause_batch(self):
        """Pause/resume batch processing"""
        if self.batch_processor:
            if self.batch_processor.paused or self.batch_processor.should_pause:
                self.batch_processor.resume()
                self.batch_pause_btn.setText("Pause")
                self.statusBar().showMessage("Batch processing resumed")
            else:
                self.batch_processor.pause()
                self.batch_pause_btn.setText("Resume")
                self.statusBar().showMessage("Batch processing paused")
    
    def stop_batch(self):
        """Stop batch processing"""
        if self.batch_processor:
            self.batch_processor.stop()
            self.statusBar().showMessage("Stopping batch processing...")
    
    def on_batch_progress(self, current: int, total: int):
        """Update batch progress"""
        self.batch_progress.setValue(current)
        self.batch_status_label.setText(f"Processing {current}/{total}")
    
    def on_batch_item_started(self, index: int, filename: str):
        """Handle batch item started"""
        item = self.batch_list.item(index)
        if item:
            item.setText(f"⏳ {filename}")
    
    def on_batch_item_completed(self, index: int, success: bool, message: str, metadata: dict):
        """Handle batch item completed"""
        item = self.batch_list.item(index)
        if item:
            filename = Path(self.batch_queue[index].src_path).name
            if success:
                item.setText(f"✓ {filename}")
                item.setForeground(QColor("#4CAF50"))
            else:
                item.setText(f"✗ {filename} - {message}")
                item.setForeground(QColor("#F44336"))
    
    def on_batch_completed(self, total: int, successful: int, failed: int):
        """Handle batch completion"""
        self.batch_process_btn.setEnabled(True)
        self.batch_pause_btn.setEnabled(False)
        self.batch_pause_btn.setVisible(False)
        self.batch_stop_btn.setEnabled(False)
        self.batch_stop_btn.setVisible(False)
        
        message = f"Batch complete: {successful} successful, {failed} failed out of {total} total"
        self.statusBar().showMessage(message)
        self.batch_status_label.setText(message)
        
        QMessageBox.information(self, "Batch Complete", message)
        
        # Open output folder if requested
        if self.open_folder_check.isChecked() and successful > 0:
            output_folder = self.config.get("last_output_folder", "")
            self.open_file_manager(output_folder)
    
    def clear_recent(self):
        """Clear recent files"""
        self.config.data["recent_files"] = []
        self.config.save()
        self.update_recent_menu()
    
    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            self.config.get("last_output_folder", "")
        )
        if folder:
            self.config.set("last_output_folder", folder)
            self.folder_label.setText(f"Output: {folder}")
    
    def on_format_changed(self, format_name: str):
        """Handle format change"""
        self.config.set("default_format", format_name)
        
        # Show/hide quality settings
        has_quality = supports_quality(format_name)
        self.quality_group.setVisible(has_quality)
        
        # Update format description
        description = get_format_description(format_name)
        self.format_desc_label.setText(description)
    
    def update_quality_label(self, value: int):
        """Update quality label"""
        self.quality_value_label.setText(f"{value}%")
    
    def toggle_resize(self, checked: bool):
        """Toggle resize options"""
        self.width_spin.setEnabled(checked)
        self.height_spin.setEnabled(checked)
        self.aspect_lock_check.setEnabled(checked)
        self.resample_combo.setEnabled(checked)
    
    def on_width_changed(self, value: int):
        """Handle width change with aspect ratio lock"""
        if self.aspect_lock_check.isChecked() and self.src_path:
            info = self.processor.get_image_info(self.src_path)
            if info.get('width') and info.get('height'):
                aspect_ratio = info['height'] / info['width']
                self.height_spin.blockSignals(True)
                self.height_spin.setValue(int(value * aspect_ratio))
                self.height_spin.blockSignals(False)
    
    def on_height_changed(self, value: int):
        """Handle height change with aspect ratio lock"""
        if self.aspect_lock_check.isChecked() and self.src_path:
            info = self.processor.get_image_info(self.src_path)
            if info.get('width') and info.get('height'):
                aspect_ratio = info['width'] / info['height']
                self.width_spin.blockSignals(True)
                self.width_spin.setValue(int(value * aspect_ratio))
                self.width_spin.blockSignals(False)
    
    def reset_adjustments(self):
        """Reset all image adjustments to defaults"""
        self.brightness_slider.setValue(100)
        self.contrast_slider.setValue(100)
        self.saturation_slider.setValue(100)
        self.sharpness_slider.setValue(100)
    
    def save_preferences(self):
        """Save preferences"""
        self.config.set("open_after_save", self.open_folder_check.isChecked())
        self.config.set("preserve_metadata", self.preserve_metadata_check.isChecked())
        self.config.set("strip_gps", self.strip_gps_check.isChecked())
    
    def get_conversion_params(self) -> Dict:
        """Get current conversion parameters"""
        params = {
            "format_hint": self.format_combo.currentText(),
            "quality": self.quality_slider.value(),
            "preserve_metadata": self.preserve_metadata_check.isChecked(),
            "strip_gps": self.strip_gps_check.isChecked(),
            "brightness": self.brightness_slider.value() / 100.0,
            "contrast": self.contrast_slider.value() / 100.0,
            "saturation": self.saturation_slider.value() / 100.0,
            "sharpness": self.sharpness_slider.value() / 100.0,
        }
        
        if self.resize_check.isChecked():
            params["resize_width"] = self.width_spin.value()
            params["resize_height"] = self.height_spin.value()
            params["maintain_aspect"] = self.aspect_lock_check.isChecked()
            params["resample_method"] = self.resample_combo.currentText()
        
        return params
    
    def convert_image(self):
        """Convert single image"""
        if not self.src_path:
            QMessageBox.warning(self, "Error", "Please select an image first.")
            return
        
        # Get output format
        format_name = self.format_combo.currentText()
        format_info = get_format_info(format_name)
        
        # Get output path
        output_folder = self.config.get("last_output_folder", "")
        if not output_folder or not Path(output_folder).exists():
            output_folder = QFileDialog.getExistingDirectory(
                self, "Select Output Folder"
            )
            if not output_folder:
                return
            self.config.set("last_output_folder", output_folder)
        
        # Get filename
        default_name = Path(self.src_path).stem
        filename, ok = QFileDialog.getSaveFileName(
            self,
            "Save As",
            str(Path(output_folder) / f"{default_name}{format_info['ext']}"),
            get_file_filter()
        )
        
        if not ok or not filename:
            return
        
        # Show progress
        self.convert_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        # Get conversion parameters
        params = self.get_conversion_params()
        
        # Perform conversion
        try:
            success, message, metadata = self.processor.convert_image(
                self.src_path,
                filename,
                **params
            )
            
            self.progress_bar.setVisible(False)
            self.convert_btn.setEnabled(True)
            
            if success:
                self.statusBar().showMessage(message, 5000)
                QMessageBox.information(self, "Success", message)
                
                # Open folder if requested
                if self.open_folder_check.isChecked():
                    self.open_file_manager(output_folder)
            else:
                QMessageBox.critical(self, "Conversion Error", message)
                self.statusBar().showMessage("Conversion failed", 5000)
        
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.convert_btn.setEnabled(True)
            QMessageBox.critical(self, "Error", f"Conversion failed: {str(e)}")
    
    def view_metadata(self):
        """View image metadata"""
        if not self.src_path:
            QMessageBox.warning(self, "No Image", "Please select an image first.")
            return
        
        info = self.processor.get_image_info(self.src_path)
        exif = info.get("exif", {})
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Image Metadata")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Basic info
        basic_info = f"""
Filename: {info.get('filename', 'N/A')}
Format: {info.get('format', 'N/A')}
Dimensions: {info.get('width', 0)}x{info.get('height', 0)} ({info.get('megapixels', 0):.1f} MP)
Color Mode: {info.get('mode', 'N/A')}
File Size: {info.get('size_kb', 0):.1f} KB
"""
        
        basic_label = QLabel(basic_info)
        basic_label.setStyleSheet("font-family: monospace; padding: 8px;")
        layout.addWidget(basic_label)
        
        # EXIF data
        if exif:
            layout.addWidget(QLabel("EXIF Data:"))
            
            exif_table = QTableWidget()
            exif_table.setColumnCount(2)
            exif_table.setHorizontalHeaderLabels(["Tag", "Value"])
            exif_table.horizontalHeader().setStretchLastSection(True)
            exif_table.setRowCount(len(exif))
            
            for row, (tag, value) in enumerate(exif.items()):
                exif_table.setItem(row, 0, QTableWidgetItem(str(tag)))
                exif_table.setItem(row, 1, QTableWidgetItem(str(value)))
            
            layout.addWidget(exif_table)
        else:
            layout.addWidget(QLabel("No EXIF data found"))
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def open_file_manager(self, path: str):
        """Open file manager at path"""
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.run(["open", path], check=False)
            else:
                subprocess.run(["xdg-open", path], check=False)
        except Exception as e:
            print(f"Failed to open file manager: {e}")
    
    def load_preset_from_combo(self, preset_name: str):
        """Load preset from combo box"""
        if preset_name != "Custom":
            self.load_preset(preset_name)
    
    def load_preset(self, preset_name: str):
        """Load a preset"""
        preset = self.config.load_preset(preset_name)
        if not preset:
            return
        
        # Apply preset settings
        format_name = preset.get("format", "PNG")
        if format_name in get_writable_formats():
            self.format_combo.setCurrentText(format_name)
        
        self.quality_slider.setValue(preset.get("quality", 85))
        
        resize_enabled = preset.get("resize_enabled", False)
        self.resize_check.setChecked(resize_enabled)
        if resize_enabled:
            self.width_spin.setValue(preset.get("max_width", 1920))
            self.height_spin.setValue(preset.get("max_height", 1080))
        
        self.preserve_metadata_check.setChecked(preset.get("preserve_metadata", True))
        self.strip_gps_check.setChecked(preset.get("strip_gps", False))
        
        self.current_preset = preset_name
        self.preset_combo.setCurrentText(preset_name)
        
        self.statusBar().showMessage(f"Loaded preset: {preset_name}", 3000)
    
    def save_current_preset(self):
        """Save current settings as preset"""
        from PySide6.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(
            self, "Save Preset", "Enter preset name:"
        )
        
        if ok and name:
            preset_data = {
                "format": self.format_combo.currentText(),
                "quality": self.quality_slider.value(),
                "resize_enabled": self.resize_check.isChecked(),
                "max_width": self.width_spin.value(),
                "max_height": self.height_spin.value(),
                "preserve_metadata": self.preserve_metadata_check.isChecked(),
                "strip_gps": self.strip_gps_check.isChecked(),
                "description": "User-created preset",
            }
            
            self.config.save_preset(name, preset_data)
            self.update_presets_menu()
            self.preset_combo.addItem(name)
            self.preset_combo.setCurrentText(name)
            
            QMessageBox.information(self, "Success", f"Preset '{name}' saved successfully!")
    
    def show_preset_manager(self):
        """Show preset manager dialog"""
        dialog = PresetDialog(self.config, self)
        if dialog.exec():
            current = dialog.presets_list.currentItem()
            if current:
                self.load_preset(current.text())
    
    def show_preferences(self):
        """Show preferences dialog"""
        QMessageBox.information(
            self, "Preferences",
            "Preferences are managed through the UI controls.\n\n"
            "Use File → Recent Files to manage recent files.\n"
            "Use Presets menu to manage conversion presets."
        )
    
    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts_text = """
Keyboard Shortcuts:

File Operations:
  Ctrl+O          Open Image
  Ctrl+Shift+O    Open Multiple Images (Batch)
  Ctrl+S          Save/Convert
  Ctrl+Q          Quit

Conversion:
  F5              Convert Image
  Ctrl+B          Add to Batch

Batch Operations:
  Ctrl+Shift+C    Clear Batch Queue

View:
  +/-             Zoom In/Out
  
Help:
  F1              Show Shortcuts
"""
        
        QMessageBox.information(self, "Keyboard Shortcuts", shortcuts_text)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
<h2>Image Converter Pro</h2>
<p><b>Version:</b> 1.0.0</p>
<p><b>A professional image conversion tool</b></p>

<h3>Features:</h3>
<ul>
<li>Modern format support (JPEG, PNG, WebP, AVIF, HEIC)</li>
<li>Batch processing with queue management</li>
<li>Image adjustments (brightness, contrast, saturation, sharpness)</li>
<li>Preset system for workflows</li>
<li>Metadata handling and privacy controls</li>
<li>Dark theme interface</li>
<li>Comprehensive keyboard shortcuts</li>
</ul>

<p><b>Built with:</b> PySide6, Pillow</p>
<p>© 2025 Image Converter Pro</p>
"""
        
        QMessageBox.about(self, "About Image Converter Pro", about_text)
    
    def clear_recent(self):
        """Clear recent files"""
        self.config.data["recent_files"] = []
        self.config.save()
        self.update_recent_menu()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set application metadata
    app.setApplicationName("Image Converter Pro")
    app.setOrganizationName("ImageTools")
    app.setApplicationVersion("1.0.0")
    
    # Create and show main window
    window = ImageConverterApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
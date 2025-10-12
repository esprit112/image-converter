"""
Configuration management for Image Converter Pro
Handles settings persistence, presets, and user preferences
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class Config:
    """Configuration manager with preset support"""
    
    CONFIG_FILE = "image_converter_pro.json"
    PRESETS_DIR = "presets"
    
    def __init__(self):
        self.config_dir = Path.home() / ".image_converter_pro"
        self.config_dir.mkdir(exist_ok=True)
        
        self.presets_dir = self.config_dir / self.PRESETS_DIR
        self.presets_dir.mkdir(exist_ok=True)
        
        self.config_path = self.config_dir / self.CONFIG_FILE
        self.data = self.load()
        
        # Initialize default presets if they don't exist
        self._create_default_presets()
    
    def load(self) -> Dict:
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return self.defaults()
        return self.defaults()
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Config save error: {e}")
    
    def defaults(self) -> Dict:
        """Return default configuration"""
        return {
            "last_input_folder": str(Path.home()),
            "last_output_folder": str(Path.home() / "Downloads"),
            "open_after_save": True,
            "default_format": "PNG",
            "jpeg_quality": 85,
            "webp_quality": 85,
            "png_compression": 6,
            "theme": "dark",
            "recent_files": [],
            "max_recent_files": 10,
            "window_geometry": None,
            "splitter_state": None,
            "keyboard_shortcuts": self._default_shortcuts(),
            "preserve_metadata": True,
            "strip_gps": False,
            "auto_optimize": True,
            "multi_threading": True,
            "max_threads": 4,
            "show_comparison": False,
            "aspect_ratio_locked": True,
            "last_preset": "default",
        }
    
    def _default_shortcuts(self) -> Dict:
        """Default keyboard shortcuts"""
        return {
            "open_file": "Ctrl+O",
            "save": "Ctrl+S",
            "convert": "F5",
            "quit": "Ctrl+Q",
            "batch_add": "Ctrl+B",
            "clear_batch": "Ctrl+Shift+C",
            "toggle_comparison": "Ctrl+Shift+V",
            "undo": "Ctrl+Z",
            "redo": "Ctrl+Y",
            "help": "F1",
        }
    
    def get(self, key: str, default=None) -> Any:
        """Get configuration value"""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value and save"""
        self.data[key] = value
        self.save()
    
    def add_recent_file(self, file_path: str):
        """Add file to recent files list"""
        recent = self.data.get("recent_files", [])
        
        # Remove if already exists
        if file_path in recent:
            recent.remove(file_path)
        
        # Add to front
        recent.insert(0, file_path)
        
        # Limit size
        max_recent = self.data.get("max_recent_files", 10)
        recent = recent[:max_recent]
        
        self.data["recent_files"] = recent
        self.save()
    
    def get_recent_files(self) -> List[str]:
        """Get recent files, filtering out non-existent ones"""
        recent = self.data.get("recent_files", [])
        return [f for f in recent if Path(f).exists()]
    
    # Preset Management
    
    def _create_default_presets(self):
        """Create default presets if they don't exist"""
        defaults = {
            "Web Optimization": {
                "format": "WEBP",
                "quality": 85,
                "resize_enabled": True,
                "max_width": 1920,
                "max_height": 1080,
                "preserve_metadata": False,
                "strip_gps": True,
                "description": "Optimized for web delivery - WebP format, compressed, metadata stripped"
            },
            "Social Media": {
                "format": "JPEG",
                "quality": 90,
                "resize_enabled": True,
                "max_width": 1080,
                "max_height": 1080,
                "preserve_metadata": False,
                "strip_gps": True,
                "description": "Perfect for Instagram/Facebook - Square format, high quality"
            },
            "Print Quality": {
                "format": "TIFF",
                "quality": 100,
                "resize_enabled": False,
                "preserve_metadata": True,
                "strip_gps": False,
                "description": "Maximum quality for printing - Lossless TIFF, full resolution"
            },
            "Email Friendly": {
                "format": "JPEG",
                "quality": 75,
                "resize_enabled": True,
                "max_width": 1280,
                "max_height": 720,
                "preserve_metadata": False,
                "strip_gps": True,
                "description": "Small file size for email attachments"
            },
            "Privacy Safe": {
                "format": "PNG",
                "quality": 85,
                "resize_enabled": False,
                "preserve_metadata": False,
                "strip_gps": True,
                "description": "All metadata removed for privacy"
            },
        }
        
        for name, preset in defaults.items():
            preset_path = self.presets_dir / f"{name}.json"
            if not preset_path.exists():
                self.save_preset(name, preset)
    
    def save_preset(self, name: str, preset_data: Dict):
        """Save a preset"""
        preset_data["created"] = datetime.now().isoformat()
        preset_path = self.presets_dir / f"{name}.json"
        
        try:
            with open(preset_path, 'w', encoding='utf-8') as f:
                json.dump(preset_data, f, indent=2)
        except Exception as e:
            print(f"Preset save error: {e}")
    
    def load_preset(self, name: str) -> Optional[Dict]:
        """Load a preset by name"""
        preset_path = self.presets_dir / f"{name}.json"
        
        if preset_path.exists():
            try:
                with open(preset_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return None
        return None
    
    def get_presets(self) -> List[str]:
        """Get list of available preset names"""
        if not self.presets_dir.exists():
            return []
        
        presets = []
        for preset_file in self.presets_dir.glob("*.json"):
            presets.append(preset_file.stem)
        
        return sorted(presets)
    
    def delete_preset(self, name: str) -> bool:
        """Delete a preset"""
        preset_path = self.presets_dir / f"{name}.json"
        
        try:
            if preset_path.exists():
                preset_path.unlink()
                return True
        except Exception:
            pass
        
        return False
    
    def export_preset(self, name: str, export_path: Path) -> bool:
        """Export preset to a file"""
        preset_data = self.load_preset(name)
        if preset_data:
            try:
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(preset_data, f, indent=2)
                return True
            except Exception:
                pass
        return False
    
    def import_preset(self, import_path: Path, name: Optional[str] = None) -> bool:
        """Import preset from a file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                preset_data = json.load(f)
            
            if not name:
                name = import_path.stem
            
            self.save_preset(name, preset_data)
            return True
        except Exception:
            return False

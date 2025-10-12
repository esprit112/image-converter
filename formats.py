"""
Format detection and handling for Image Converter Pro
Supports modern formats including AVIF, HEIC, and WebP
"""

from typing import Dict, List, Optional, Tuple
from pathlib import Path


# Comprehensive format definitions
FORMATS = {
    "JPEG": {
        "ext": ".jpg",
        "hint": "JPEG",
        "quality": True,
        "supports_transparency": False,
        "description": "Best for photos. Lossy compression with excellent quality/size ratio.",
        "mime": "image/jpeg",
        "aliases": [".jpeg", ".jpg"],
    },
    "PNG": {
        "ext": ".png",
        "hint": "PNG",
        "quality": False,
        "supports_transparency": True,
        "description": "Lossless format. Best for graphics, screenshots, and images with transparency.",
        "mime": "image/png",
        "aliases": [".png"],
    },
    "WebP": {
        "ext": ".webp",
        "hint": "WEBP",
        "quality": True,
        "supports_transparency": True,
        "description": "Modern format with superior compression. 25-34% smaller than JPEG. Web-friendly.",
        "mime": "image/webp",
        "aliases": [".webp"],
    },
    "AVIF": {
        "ext": ".avif",
        "hint": "AVIF",
        "quality": True,
        "supports_transparency": True,
        "description": "Cutting-edge format. Better compression than WebP with HDR support. 93%+ browser support.",
        "mime": "image/avif",
        "aliases": [".avif"],
    },
    "HEIC": {
        "ext": ".heic",
        "hint": "HEIC",
        "quality": True,
        "supports_transparency": True,
        "description": "Apple's format for iPhone photos. Excellent compression. Read-only for conversion.",
        "mime": "image/heic",
        "aliases": [".heic", ".heif"],
        "read_only": True,
    },
    "GIF": {
        "ext": ".gif",
        "hint": "GIF",
        "quality": False,
        "supports_transparency": True,
        "description": "Supports animation and transparency. Limited to 256 colors.",
        "mime": "image/gif",
        "aliases": [".gif"],
    },
    "BMP": {
        "ext": ".bmp",
        "hint": "BMP",
        "quality": False,
        "supports_transparency": False,
        "description": "Uncompressed format. Large file sizes but universal compatibility.",
        "mime": "image/bmp",
        "aliases": [".bmp"],
    },
    "TIFF": {
        "ext": ".tiff",
        "hint": "TIFF",
        "quality": False,
        "supports_transparency": True,
        "description": "Professional format. Lossless, supports layers. Large files.",
        "mime": "image/tiff",
        "aliases": [".tif", ".tiff"],
    },
    "ICO": {
        "ext": ".ico",
        "hint": "ICO",
        "quality": False,
        "supports_transparency": True,
        "description": "Windows icon format. Multiple sizes in one file.",
        "mime": "image/x-icon",
        "aliases": [".ico"],
    },
    "PDF": {
        "ext": ".pdf",
        "hint": "PDF",
        "quality": False,
        "supports_transparency": False,
        "description": "Document format. Embed images in PDF files.",
        "mime": "application/pdf",
        "aliases": [".pdf"],
    },
}


def get_format_info(format_name: str) -> Optional[Dict]:
    """Get format information by name"""
    return FORMATS.get(format_name)


def get_all_formats() -> Dict[str, Dict]:
    """Get all supported formats"""
    return FORMATS.copy()


def get_writable_formats() -> List[str]:
    """Get list of formats that can be written"""
    return [name for name, info in FORMATS.items() if not info.get("read_only", False)]


def get_readable_formats() -> List[str]:
    """Get list of formats that can be read"""
    return list(FORMATS.keys())


def detect_format(file_path: Path) -> Optional[str]:
    """Detect format from file extension"""
    ext = file_path.suffix.lower()
    
    for name, info in FORMATS.items():
        if ext in info.get("aliases", []):
            return name
    
    return None


def get_file_filter() -> str:
    """Get file filter string for file dialogs"""
    # All images
    all_exts = []
    for info in FORMATS.values():
        all_exts.extend(info.get("aliases", []))
    
    all_exts_str = " ".join([f"*{ext}" for ext in set(all_exts)])
    filters = [f"All Images ({all_exts_str})"]
    
    # Individual formats
    for name, info in FORMATS.items():
        exts = info.get("aliases", [])
        exts_str = " ".join([f"*{ext}" for ext in exts])
        filters.append(f"{name} Files ({exts_str})")
    
    # All files
    filters.append("All Files (*)")
    
    return ";;".join(filters)


def get_save_filter(format_name: str) -> str:
    """Get file filter for saving specific format"""
    info = FORMATS.get(format_name)
    if not info:
        return "All Files (*)"
    
    exts = info.get("aliases", [])
    exts_str = " ".join([f"*{ext}" for ext in exts])
    return f"{format_name} Files ({exts_str})"


def supports_quality(format_name: str) -> bool:
    """Check if format supports quality settings"""
    info = FORMATS.get(format_name)
    return info.get("quality", False) if info else False


def supports_transparency(format_name: str) -> bool:
    """Check if format supports transparency"""
    info = FORMATS.get(format_name)
    return info.get("supports_transparency", False) if info else False


def is_writable(format_name: str) -> bool:
    """Check if format can be written"""
    info = FORMATS.get(format_name)
    return not info.get("read_only", False) if info else False


def get_recommended_quality(format_name: str) -> Tuple[int, int, int]:
    """Get recommended quality range (min, default, max) for format"""
    quality_recommendations = {
        "JPEG": (70, 85, 95),
        "WebP": (75, 85, 95),
        "AVIF": (70, 80, 90),
    }
    
    return quality_recommendations.get(format_name, (1, 85, 100))


def get_format_description(format_name: str) -> str:
    """Get format description"""
    info = FORMATS.get(format_name)
    return info.get("description", "No description available") if info else ""


def check_format_availability() -> Dict[str, bool]:
    """Check which formats are actually available in the current Pillow installation"""
    try:
        from PIL import Image, features
        
        availability = {}
        
        for name, info in FORMATS.items():
            hint = info.get("hint", name)
            
            # Check if format is in SAVE dict
            try:
                available = hint in Image.SAVE
                
                # Special checks for formats that need additional libraries
                if name == "WEBP":
                    available = features.check("webp")
                elif name == "AVIF":
                    # Check for pillow-avif-plugin
                    try:
                        import pillow_avif
                        available = True
                    except ImportError:
                        available = False
                elif name == "HEIC":
                    # Check for pillow-heif
                    try:
                        import pillow_heif
                        available = True
                    except ImportError:
                        available = False
                
                availability[name] = available
            except Exception:
                availability[name] = False
        
        return availability
    
    except ImportError:
        return {name: False for name in FORMATS.keys()}


def get_missing_format_help(format_name: str) -> str:
    """Get help message for installing missing format support"""
    help_messages = {
        "WEBP": "Install WebP support: pip install pillow[webp]",
        "AVIF": "Install AVIF support: pip install pillow-avif-plugin",
        "HEIC": "Install HEIC support: pip install pillow-heif",
    }
    
    return help_messages.get(format_name, f"Format {format_name} may require additional system libraries")

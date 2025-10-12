"""
Image processing engine for Image Converter Pro
Handles conversion, resizing, quality optimization, and metadata
"""

from PIL import Image, ImageEnhance, ExifTags
from pathlib import Path
from typing import Optional, Dict, Tuple, Any
import io


class ImageProcessor:
    """Core image processing functionality"""
    
    # Resampling algorithms
    RESAMPLE_METHODS = {
        "Lanczos": Image.Resampling.LANCZOS,
        "Bicubic": Image.Resampling.BICUBIC,
        "Bilinear": Image.Resampling.BILINEAR,
        "Nearest": Image.Resampling.NEAREST,
    }
    
    def __init__(self):
        self.register_heif_opener()
    
    @staticmethod
    def register_heif_opener():
        """Register HEIF/HEIC format support if available"""
        try:
            import pillow_heif
            pillow_heif.register_heif_opener()
        except ImportError:
            pass
        
        # Register AVIF if available
        try:
            import pillow_avif
        except ImportError:
            pass
    
    def open_image(self, file_path: str) -> Image.Image:
        """Open and return image"""
        return Image.open(file_path)
    
    def get_image_info(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive image information"""
        path = Path(file_path)
        
        info = {
            "filename": path.name,
            "size_bytes": path.stat().st_size,
            "size_kb": path.stat().st_size / 1024,
            "size_mb": path.stat().st_size / (1024 * 1024),
        }
        
        try:
            with Image.open(file_path) as img:
                info.update({
                    "format": img.format,
                    "mode": img.mode,
                    "width": img.width,
                    "height": img.height,
                    "megapixels": (img.width * img.height) / 1_000_000,
                    "has_transparency": img.mode in ("RGBA", "LA", "P") and "transparency" in img.info,
                })
                
                # Extract EXIF data
                exif_data = self.get_exif_data(img)
                if exif_data:
                    info["exif"] = exif_data
        
        except Exception as e:
            info["error"] = str(e)
        
        return info
    
    def get_exif_data(self, img: Image.Image) -> Optional[Dict]:
        """Extract EXIF data from image"""
        try:
            exif = img.getexif()
            if not exif:
                return None
            
            exif_data = {}
            for tag_id, value in exif.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                exif_data[tag] = value
            
            return exif_data
        except Exception:
            return None
    
    def strip_exif(self, img: Image.Image, strip_gps: bool = True, preserve_orientation: bool = True) -> Image.Image:
        """Strip EXIF data from image"""
        try:
            # Get current EXIF
            exif = img.getexif()
            
            if not exif:
                return img
            
            # If only stripping GPS
            if strip_gps:
                # GPS tags are in IFD 34853
                gps_tags = [0x0000, 0x0001, 0x0002, 0x0003, 0x0004, 0x0005, 0x0006, 0x0007]
                for tag in gps_tags:
                    if tag in exif:
                        del exif[tag]
                
                # Also check GPS IFD
                if 34853 in exif:
                    del exif[34853]
            else:
                # Strip all EXIF
                if preserve_orientation:
                    orientation = exif.get(274)  # Orientation tag
                    exif.clear()
                    if orientation:
                        exif[274] = orientation
                else:
                    exif.clear()
            
            # Create new image with modified EXIF
            data = list(img.getdata())
            img_new = Image.new(img.mode, img.size)
            img_new.putdata(data)
            
            if exif:
                img_new.info['exif'] = exif.tobytes()
            
            return img_new
        
        except Exception:
            return img
    
    def resize_image(self, img: Image.Image, width: Optional[int] = None, 
                    height: Optional[int] = None, maintain_aspect: bool = True,
                    resample_method: str = "Lanczos") -> Image.Image:
        """Resize image with various options"""
        
        if not width and not height:
            return img
        
        original_width, original_height = img.size
        resample = self.RESAMPLE_METHODS.get(resample_method, Image.Resampling.LANCZOS)
        
        if maintain_aspect:
            # Calculate dimensions maintaining aspect ratio
            if width and height:
                # Fit within bounds
                img.thumbnail((width, height), resample)
                return img
            elif width:
                # Scale by width
                ratio = width / original_width
                new_height = int(original_height * ratio)
                return img.resize((width, new_height), resample)
            else:
                # Scale by height
                ratio = height / original_height
                new_width = int(original_width * ratio)
                return img.resize((new_width, height), resample)
        else:
            # Exact dimensions
            new_width = width or original_width
            new_height = height or original_height
            return img.resize((new_width, new_height), resample)
    
    def adjust_brightness(self, img: Image.Image, factor: float) -> Image.Image:
        """Adjust image brightness (0.0 to 2.0, 1.0 = no change)"""
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(factor)
    
    def adjust_contrast(self, img: Image.Image, factor: float) -> Image.Image:
        """Adjust image contrast (0.0 to 2.0, 1.0 = no change)"""
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(factor)
    
    def adjust_saturation(self, img: Image.Image, factor: float) -> Image.Image:
        """Adjust image saturation (0.0 to 2.0, 1.0 = no change)"""
        enhancer = ImageEnhance.Color(img)
        return enhancer.enhance(factor)
    
    def adjust_sharpness(self, img: Image.Image, factor: float) -> Image.Image:
        """Adjust image sharpness (0.0 to 2.0, 1.0 = no change)"""
        enhancer = ImageEnhance.Sharpness(img)
        return enhancer.enhance(factor)
    
    def convert_image(self, src_path: str, dst_path: str, 
                     format_hint: str, quality: int = 85,
                     resize_width: Optional[int] = None,
                     resize_height: Optional[int] = None,
                     maintain_aspect: bool = True,
                     resample_method: str = "Lanczos",
                     preserve_metadata: bool = True,
                     strip_gps: bool = False,
                     brightness: float = 1.0,
                     contrast: float = 1.0,
                     saturation: float = 1.0,
                     sharpness: float = 1.0) -> Tuple[bool, str, Dict]:
        """
        Convert image with full options
        Returns: (success, message, metadata)
        """
        
        try:
            with Image.open(src_path) as img:
                original_format = img.format
                original_size = Path(src_path).stat().st_size
                
                # Store original EXIF if needed
                exif_data = None
                if preserve_metadata:
                    exif_data = img.getexif()
                
                # Handle transparency for formats that don't support it
                if format_hint in ("JPEG", "PDF", "BMP"):
                    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                        # Create white background
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        if img.mode == "P":
                            img = img.convert("RGBA")
                        background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                        img = background
                    elif img.mode not in ("RGB", "L"):
                        img = img.convert("RGB")
                
                # Convert palette images for better quality
                if img.mode == "P":
                    if format_hint in ("PNG", "WEBP", "TIFF", "GIF", "ICO", "AVIF"):
                        img = img.convert("RGBA")
                    else:
                        img = img.convert("RGB")
                
                # Resize if requested
                if resize_width or resize_height:
                    img = self.resize_image(img, resize_width, resize_height, 
                                          maintain_aspect, resample_method)
                
                # Apply adjustments
                if brightness != 1.0:
                    img = self.adjust_brightness(img, brightness)
                if contrast != 1.0:
                    img = self.adjust_contrast(img, contrast)
                if saturation != 1.0 and img.mode in ("RGB", "RGBA"):
                    img = self.adjust_saturation(img, saturation)
                if sharpness != 1.0:
                    img = self.adjust_sharpness(img, sharpness)
                
                # Handle metadata
                if strip_gps or not preserve_metadata:
                    img = self.strip_exif(img, strip_gps, preserve_orientation=True)
                
                # Prepare save arguments
                save_kwargs = {"format": format_hint}
                
                # Format-specific options
                if format_hint == "JPEG":
                    save_kwargs.update({
                        "quality": quality,
                        "optimize": True,
                        "progressive": True,
                    })
                    if exif_data and preserve_metadata:
                        save_kwargs["exif"] = exif_data.tobytes() if hasattr(exif_data, 'tobytes') else exif_data
                
                elif format_hint == "PNG":
                    save_kwargs.update({
                        "optimize": True,
                        "compress_level": 6,
                    })
                
                elif format_hint == "WEBP":
                    save_kwargs.update({
                        "quality": quality,
                        "method": 6,
                    })
                    if exif_data and preserve_metadata:
                        save_kwargs["exif"] = exif_data.tobytes() if hasattr(exif_data, 'tobytes') else exif_data
                
                elif format_hint == "AVIF":
                    save_kwargs.update({
                        "quality": quality,
                    })
                
                elif format_hint == "PDF":
                    if img.mode == "RGBA":
                        img = img.convert("RGB")
                    save_kwargs.update({
                        "resolution": 100.0,
                    })
                
                elif format_hint == "ICO":
                    if img.mode not in ("RGBA", "RGB", "L"):
                        img = img.convert("RGBA")
                
                # Save image
                img.save(dst_path, **save_kwargs)
                
                # Get output size
                output_size = Path(dst_path).stat().st_size
                reduction = ((original_size - output_size) / original_size) * 100
                
                metadata = {
                    "original_format": original_format,
                    "original_size": original_size,
                    "output_size": output_size,
                    "size_reduction_percent": reduction,
                    "output_format": format_hint,
                }
                
                message = f"Converted successfully. Size: {original_size / 1024:.1f} KB → {output_size / 1024:.1f} KB ({reduction:.1f}% reduction)"
                
                return True, message, metadata
        
        except Exception as e:
            return False, f"Conversion failed: {str(e)}", {}
    
    def estimate_output_size(self, src_path: str, format_hint: str, 
                            quality: int = 85) -> Optional[int]:
        """Estimate output file size without saving"""
        try:
            with Image.open(src_path) as img:
                # Convert mode if necessary
                if format_hint in ("JPEG", "PDF", "BMP"):
                    if img.mode in ("RGBA", "LA", "P"):
                        img = img.convert("RGB")
                
                # Save to memory
                buffer = io.BytesIO()
                save_kwargs = {"format": format_hint}
                
                if format_hint == "JPEG":
                    save_kwargs["quality"] = quality
                elif format_hint == "WEBP":
                    save_kwargs["quality"] = quality
                elif format_hint == "AVIF":
                    save_kwargs["quality"] = quality
                
                img.save(buffer, **save_kwargs)
                return buffer.tell()
        
        except Exception:
            return None
    
    def rotate_image(self, img: Image.Image, degrees: int) -> Image.Image:
        """Rotate image by degrees (90, 180, 270)"""
        if degrees == 90:
            return img.rotate(-90, expand=True)
        elif degrees == 180:
            return img.rotate(180, expand=True)
        elif degrees == 270:
            return img.rotate(-270, expand=True)
        return img
    
    def flip_horizontal(self, img: Image.Image) -> Image.Image:
        """Flip image horizontally"""
        return img.transpose(Image.FLIP_LEFT_RIGHT)
    
    def flip_vertical(self, img: Image.Image) -> Image.Image:
        """Flip image vertically"""
        return img.transpose(Image.FLIP_TOP_BOTTOM)
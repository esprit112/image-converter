"""
Batch processing engine for Image Converter Pro
Handles multiple file conversions with progress tracking
"""

from PySide6.QtCore import QThread, Signal
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
import time


@dataclass
class BatchItem:
    """Represents a single item in batch queue"""
    src_path: str
    dst_path: str
    status: str = "pending"  # pending, processing, completed, failed, skipped
    error_message: str = ""
    progress: int = 0
    
    def __str__(self):
        return Path(self.src_path).name


class BatchProcessor(QThread):
    """Background thread for batch image conversion"""
    
    # Signals
    progress_updated = Signal(int, int)  # current_index, total_count
    item_started = Signal(int, str)  # index, filename
    item_completed = Signal(int, bool, str, dict)  # index, success, message, metadata
    batch_completed = Signal(int, int, int)  # total, successful, failed
    
    def __init__(self, processor, items: List[BatchItem], conversion_params: Dict):
        super().__init__()
        self.processor = processor
        self.items = items
        self.params = conversion_params
        self.should_stop = False
        self.should_pause = False
        self.paused = False
    
    def run(self):
        """Execute batch conversion"""
        successful = 0
        failed = 0
        
        for index, item in enumerate(self.items):
            # Check for pause
            while self.should_pause and not self.should_stop:
                self.paused = True
                time.sleep(0.1)
            
            self.paused = False
            
            # Check for stop
            if self.should_stop:
                break
            
            # Skip if already completed or failed
            if item.status in ("completed", "skipped"):
                continue
            
            # Update status
            item.status = "processing"
            self.item_started.emit(index, Path(item.src_path).name)
            
            try:
                # Perform conversion
                success, message, metadata = self.processor.convert_image(
                    item.src_path,
                    item.dst_path,
                    **self.params
                )
                
                if success:
                    item.status = "completed"
                    successful += 1
                else:
                    item.status = "failed"
                    item.error_message = message
                    failed += 1
                
                self.item_completed.emit(index, success, message, metadata)
                
            except Exception as e:
                item.status = "failed"
                item.error_message = str(e)
                failed += 1
                self.item_completed.emit(index, False, f"Error: {str(e)}", {})
            
            # Update progress
            self.progress_updated.emit(index + 1, len(self.items))
        
        # Batch complete
        self.batch_completed.emit(len(self.items), successful, failed)
    
    def stop(self):
        """Stop batch processing"""
        self.should_stop = True
    
    def pause(self):
        """Pause batch processing"""
        self.should_pause = True
    
    def resume(self):
        """Resume batch processing"""
        self.should_pause = False


class BatchQueue:
    """Manages batch conversion queue"""
    
    def __init__(self):
        self.items: List[BatchItem] = []
    
    def add_item(self, src_path: str, dst_path: str):
        """Add item to queue"""
        item = BatchItem(src_path=src_path, dst_path=dst_path)
        self.items.append(item)
    
    def add_items(self, items: List[tuple]):
        """Add multiple items (src, dst) tuples"""
        for src, dst in items:
            self.add_item(src, dst)
    
    def remove_item(self, index: int):
        """Remove item from queue"""
        if 0 <= index < len(self.items):
            del self.items[index]
    
    def clear(self):
        """Clear all items"""
        self.items.clear()
    
    def get_items(self) -> List[BatchItem]:
        """Get all items"""
        return self.items
    
    def get_pending_items(self) -> List[BatchItem]:
        """Get items that haven't been processed"""
        return [item for item in self.items if item.status == "pending"]
    
    def get_completed_items(self) -> List[BatchItem]:
        """Get successfully completed items"""
        return [item for item in self.items if item.status == "completed"]
    
    def get_failed_items(self) -> List[BatchItem]:
        """Get failed items"""
        return [item for item in self.items if item.status == "failed"]
    
    def reset_failed(self):
        """Reset failed items to pending for retry"""
        for item in self.items:
            if item.status == "failed":
                item.status = "pending"
                item.error_message = ""
    
    def __len__(self):
        return len(self.items)
    
    def __getitem__(self, index):
        return self.items[index]


def generate_output_path(src_path: str, output_folder: str, 
                        format_ext: str, naming_pattern: str = "{name}{ext}") -> str:
    """
    Generate output path based on naming pattern
    
    Supported placeholders:
    - {name}: Original filename without extension
    - {ext}: New extension
    - {format}: Format name
    - {date}: Current date (YYYY-MM-DD)
    - {time}: Current time (HH-MM-SS)
    - {###}: Sequential number (3 digits)
    """
    from datetime import datetime
    
    src = Path(src_path)
    output_dir = Path(output_folder)
    
    # Extract components
    original_name = src.stem
    format_name = format_ext.lstrip('.')
    
    # Replace placeholders
    output_name = naming_pattern
    output_name = output_name.replace("{name}", original_name)
    output_name = output_name.replace("{ext}", format_ext)
    output_name = output_name.replace("{format}", format_name)
    output_name = output_name.replace("{date}", datetime.now().strftime("%Y-%m-%d"))
    output_name = output_name.replace("{time}", datetime.now().strftime("%H-%M-%S"))
    
    # Handle sequential numbering
    if "{###}" in output_name:
        counter = 1
        while True:
            test_name = output_name.replace("{###}", f"{counter:03d}")
            test_path = output_dir / test_name
            if not test_path.exists():
                output_name = test_name
                break
            counter += 1
    
    # Ensure extension
    if not output_name.endswith(format_ext):
        output_name += format_ext
    
    output_path = output_dir / output_name
    
    # Handle duplicates
    if output_path.exists():
        base = output_path.stem
        ext = output_path.suffix
        counter = 1
        while True:
            new_name = f"{base} ({counter}){ext}"
            output_path = output_dir / new_name
            if not output_path.exists():
                break
            counter += 1
    
    return str(output_path)

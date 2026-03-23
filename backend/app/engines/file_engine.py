"""
File System Engine - Handle file operations, scanning, renaming, moving
"""
import os
import shutil
from pathlib import Path
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


class FileEngine:
    """
    Handles file system operations
    """
    
    def __init__(self):
        self.home_dir = Path.home()
    
    def get_folder_path(self, folder_name):
        """
        Get full path for common folders
        """
        if folder_name.lower() == 'downloads':
            return self.home_dir / 'Downloads'
        elif folder_name.lower() == 'documents':
            return self.home_dir / 'Documents'
        elif folder_name.lower() == 'desktop':
            return self.home_dir / 'Desktop'
        elif folder_name.lower() == 'pictures':
            return self.home_dir / 'Pictures'
        else:
            # Assume it's a full path
            return Path(folder_name)
    
    def scan_folder(self, folder_path, file_pattern='*'):
        """
        Scan folder and return matching files
        
        Args:
            folder_path: Path to scan
            file_pattern: Pattern like '*.pdf', '*.jpg', or comma-separated '*.pdf,*.docx'
        
        Returns:
            List of file paths
        """
        folder = Path(folder_path)
        
        if not folder.exists():
            logger.error(f"Folder does not exist: {folder_path}")
            return []
        
        files = []
        
        # Handle multiple patterns
        patterns = [p.strip() for p in file_pattern.split(',')]
        
        for pattern in patterns:
            files.extend(folder.glob(pattern))
        
        # Filter only files (not directories)
        files = [f for f in files if f.is_file()]
        
        logger.info(f"Found {len(files)} files matching {file_pattern} in {folder_path}")
        return files
    
    def rename_file(self, file_path, new_name):
        """
        Rename a file
        """
        file_path = Path(file_path)
        new_path = file_path.parent / new_name
        
        # Avoid overwriting
        if new_path.exists():
            base, ext = os.path.splitext(new_name)
            counter = 1
            while new_path.exists():
                new_path = file_path.parent / f"{base}_{counter}{ext}"
                counter += 1
        
        file_path.rename(new_path)
        logger.info(f"Renamed: {file_path.name} → {new_path.name}")
        return new_path
    
    def move_file(self, file_path, destination_folder):
        """
        Move file to destination folder (create if doesn't exist)
        """
        file_path = Path(file_path)
        dest_folder = Path(destination_folder)
        
        # Create destination if needed
        dest_folder.mkdir(parents=True, exist_ok=True)
        
        dest_path = dest_folder / file_path.name
        
        # Handle duplicates
        if dest_path.exists():
            base, ext = os.path.splitext(file_path.name)
            counter = 1
            while dest_path.exists():
                dest_path = dest_folder / f"{base}_{counter}{ext}"
                counter += 1
        
        shutil.move(str(file_path), str(dest_path))
        logger.info(f"Moved: {file_path} → {dest_path}")
        return dest_path
    
    def generate_clean_filename(self, file_path, pattern='date_title'):
        """
        Generate clean filename based on pattern
        
        Patterns:
        - 'date_title': DD-MM-YYYY - original_name.pdf
        - 'date_only': DD-MM-YYYY.pdf
        - 'title_date': original_name - DD-MM-YYYY.pdf
        """
        file_path = Path(file_path)
        
        # Get file modification date
        mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        date_str = mod_time.strftime('%d-%m-%Y')
        
        # Clean original name (remove special chars, extra spaces)
        original_name = file_path.stem
        clean_name = re.sub(r'[^\w\s-]', '', original_name)
        clean_name = re.sub(r'\s+', ' ', clean_name).strip()
        
        ext = file_path.suffix
        
        if pattern == 'date_title':
            new_name = f"{date_str} - {clean_name}{ext}"
        elif pattern == 'date_only':
            new_name = f"{date_str}{ext}"
        elif pattern == 'title_date':
            new_name = f"{clean_name} - {date_str}{ext}"
        else:
            new_name = f"{date_str} - {clean_name}{ext}"
        
        return new_name
    
    def organize_by_type(self, folder_path, create_subfolders=True):
        """
        Organize files into subfolders by type
        
        Creates:
        - PDFs/
        - Images/
        - Documents/
        - Videos/
        - Others/
        """
        folder = Path(folder_path)
        
        type_mapping = {
            'PDFs': ['.pdf'],
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
            'Documents': ['.doc', '.docx', '.txt', '.xlsx', '.xls', '.ppt', '.pptx'],
            'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'Others': []
        }
        
        files = self.scan_folder(folder_path, '*')
        organized = {'moved': 0, 'skipped': 0}
        
        for file_path in files:
            ext = file_path.suffix.lower()
            
            # Find category
            category = 'Others'
            for cat, extensions in type_mapping.items():
                if ext in extensions:
                    category = cat
                    break
            
            # Create subfolder and move
            if create_subfolders:
                dest_folder = folder / category
                try:
                    self.move_file(file_path, dest_folder)
                    organized['moved'] += 1
                except Exception as e:
                    logger.error(f"Failed to move {file_path}: {e}")
                    organized['skipped'] += 1
        
        return organized

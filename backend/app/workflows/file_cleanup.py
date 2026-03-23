"""
File Cleanup Workflow - Scan, rename, and organize files
"""
from app.workflows.base import WorkflowBase
from app.engines.file_engine import FileEngine
import logging

logger = logging.getLogger(__name__)


class FileCleanupWorkflow(WorkflowBase):
    """
    Cleans up and organizes files in a folder
    """
    
    def __init__(self):
        super().__init__()
        self.file_engine = FileEngine()
    
    def execute(self, config):
        """
        Execute file cleanup workflow
        
        Expected config:
        {
            'folder': 'Downloads',           # or 'Documents', 'Desktop', or full path
            'file_pattern': '*.pdf',         # or '*.pdf,*.docx'
            'action': 'rename',              # 'rename', 'organize', or 'both'
            'rename_pattern': 'date_title',  # 'date_title', 'date_only', 'title_date'
            'move_to': None,                 # Optional: move to another folder
            'organize_by_type': False        # Create subfolders by file type
        }
        """
        try:
            self.validate_config(config, ['folder'])
            
            # Get parameters
            folder_name = config['folder']
            file_pattern = config.get('file_pattern', '*.pdf')
            action = config.get('action', 'rename')
            rename_pattern = config.get('rename_pattern', 'date_title')
            move_to = config.get('move_to')
            organize_by_type = config.get('organize_by_type', False)
            
            # Get folder path
            folder_path = self.file_engine.get_folder_path(folder_name)
            
            if not folder_path.exists():
                return False, f"Folder not found: {folder_path}", {}
            
            self.log_info(f"Processing folder: {folder_path}")
            
            # Scan for files
            files = self.file_engine.scan_folder(folder_path, file_pattern)
            
            if not files:
                return True, f"No files found matching {file_pattern} in {folder_name}", {
                    'files_processed': 0
                }
            
            self.log_info(f"Found {len(files)} files to process")
            
            processed = 0
            renamed = 0
            moved = 0
            errors = []
            
            # Process each file
            for file_path in files:
                try:
                    # Rename if requested
                    if action in ['rename', 'both']:
                        new_name = self.file_engine.generate_clean_filename(
                            file_path, 
                            rename_pattern
                        )
                        file_path = self.file_engine.rename_file(file_path, new_name)
                        renamed += 1
                    
                    # Move if requested
                    if move_to:
                        dest_folder = self.file_engine.get_folder_path(move_to)
                        self.file_engine.move_file(file_path, dest_folder)
                        moved += 1
                    
                    processed += 1
                    
                except Exception as e:
                    error_msg = f"Error processing {file_path.name}: {str(e)}"
                    self.log_error(error_msg)
                    errors.append(error_msg)
            
            # Organize by type if requested
            if organize_by_type and action in ['organize', 'both']:
                org_result = self.file_engine.organize_by_type(folder_path)
                moved += org_result['moved']
            
            # Build summary
            summary = f"Processed {processed}/{len(files)} files"
            if renamed > 0:
                summary += f", renamed {renamed}"
            if moved > 0:
                summary += f", moved {moved}"
            
            if errors:
                summary += f" ({len(errors)} errors)"
            
            self.log_info(summary)
            
            return True, summary, {
                'total_files': len(files),
                'processed': processed,
                'renamed': renamed,
                'moved': moved,
                'errors': errors
            }
            
        except Exception as e:
            self.log_error(f"Workflow execution failed: {str(e)}")
            return False, f"Failed: {str(e)}", {}
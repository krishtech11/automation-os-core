"""
Desktop Demo Workflow - Shows basic PyAutoGUI capabilities
This is optional and for demonstration only
"""
from app.workflows.base import WorkflowBase
from app.engines.desktop_engine import DesktopEngine


class DesktopDemoWorkflow(WorkflowBase):
    """
    Demo workflow showing desktop automation
    """
    
    def __init__(self):
        super().__init__()
        self.desktop = DesktopEngine()
    
    def execute(self, config):
        """
        Execute desktop demo
        
        Config:
        {
            'action': 'open_explorer' or 'screenshot',
            'folder': 'Downloads' (for open_explorer)
        }
        """
        try:
            action = config.get('action', 'screenshot')
            
            if action == 'open_explorer':
                folder = config.get('folder', 'Downloads')
                from app.engines.file_engine import FileEngine
                folder_path = FileEngine().get_folder_path(folder)
                
                success = self.desktop.open_file_explorer(folder_path)
                
                if success:
                    return True, f"Opened file explorer at {folder}", {}
                else:
                    return False, "Failed to open file explorer", {}
            
            elif action == 'screenshot':
                screenshot_path = self.desktop.take_screenshot()
                
                if screenshot_path:
                    return True, f"Screenshot saved: {screenshot_path}", {
                        'screenshot_path': screenshot_path
                    }
                else:
                    return False, "Failed to take screenshot", {}
            
            else:
                return False, f"Unknown action: {action}", {}
                
        except Exception as e:
            self.log_error(f"Desktop demo failed: {str(e)}")
            return False, f"Failed: {str(e)}", {}
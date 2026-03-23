"""""
Desktop Automation Engine using PyAutoGUI
For demo purposes - showing basic desktop interaction capabilities
"""
import pyautogui
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DesktopEngine:
    """
    Basic desktop automation using PyAutoGUI
    """
    
    def __init__(self):
        # Safety settings
        pyautogui.PAUSE = 1  # 1 second pause between actions
        pyautogui.FAILSAFE = True  # Move mouse to top-left corner to abort
    
    def open_file_explorer(self, folder_path=None):
        """
        Open file explorer (Windows specific demo)
        """
        try:
            logger.info("Opening file explorer...")
            
            # Windows: Win+E opens file explorer
            pyautogui.hotkey('win', 'e')
            time.sleep(2)
            
            if folder_path:
                # Type folder path in address bar
                pyautogui.hotkey('ctrl', 'l')  # Focus address bar
                time.sleep(0.5)
                pyautogui.write(str(folder_path), interval=0.05)
                pyautogui.press('enter')
                time.sleep(1)
            
            logger.info("File explorer opened")
            return True
            
        except Exception as e:
            logger.error(f"Failed to open file explorer: {e}")
            return False
    
    def take_screenshot(self, save_path=None):
        """
        Take a screenshot
        """
        try:
            if not save_path:
                save_path = Path.home() / 'Desktop' / f'screenshot_{int(time.time())}.png'
            
            screenshot = pyautogui.screenshot()
            screenshot.save(save_path)
            
            logger.info(f"Screenshot saved: {save_path}")
            return str(save_path)
            
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None
    
    def type_text(self, text, interval=0.1):
        """
        Type text character by character
        """
        try:
            pyautogui.write(text, interval=interval)
            logger.info(f"Typed: {text}")
            return True
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            return False
    
    def press_key(self, key):
        """
        Press a single key
        """
        try:
            pyautogui.press(key)
            logger.info(f"Pressed key: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to press key: {e}")
            return False
    
    def hotkey(self, *keys):
        """
        Press key combination
        """
        try:
            pyautogui.hotkey(*keys)
            logger.info(f"Pressed hotkey: {'+'.join(keys)}")
            return True
        except Exception as e:
            logger.error(f"Failed to press hotkey: {e}")
            return False
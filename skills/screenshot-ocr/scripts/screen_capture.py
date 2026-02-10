#!/usr/bin/env python3
"""
Screenshot capture and OCR text extraction.
Requires: pillow, pyautogui, pytesseract (and Tesseract OCR installed)
Install: pip install pillow pyautogui pytesseract
Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
"""

import os
from PIL import Image, ImageGrab
import pyautogui
from datetime import datetime
from pathlib import Path

# Optional: OCR support
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

class ScreenCapture:
    
    def __init__(self, output_dir='screenshots'):
        """
        Initialize screen capture utility.
        
        Args:
            output_dir: Directory to save screenshots
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to find Tesseract on Windows
        if OCR_AVAILABLE and os.name == 'nt':
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
    
    def capture_full_screen(self, filename=None):
        """
        Capture the entire screen.
        
        Args:
            filename: Output filename (default: auto-generated with timestamp)
        
        Returns:
            Path to saved screenshot
        """
        screenshot = ImageGrab.grab()
        return self._save_screenshot(screenshot, filename)
    
    def capture_region(self, x, y, width, height, filename=None):
        """
        Capture a specific region of the screen.
        
        Args:
            x: Left coordinate
            y: Top coordinate
            width: Width of region
            height: Height of region
            filename: Output filename
        
        Returns:
            Path to saved screenshot
        """
        bbox = (x, y, x + width, y + height)
        screenshot = ImageGrab.grab(bbox=bbox)
        return self._save_screenshot(screenshot, filename)
    
    def capture_window(self, filename=None):
        """
        Capture the active window (Windows only).
        
        Returns:
            Path to saved screenshot
        """
        import win32gui
        import win32ui
        import win32con
        from ctypes import windll
        
        hwnd = win32gui.GetForegroundWindow()
        
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top
        
        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()
        
        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
        saveDC.SelectObject(saveBitMap)
        
        windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
        
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        
        img = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1
        )
        
        # Cleanup
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)
        
        return self._save_screenshot(img, filename)
    
    def capture_with_delay(self, delay=3, filename=None):
        """
        Capture screenshot after a delay.
        
        Args:
            delay: Delay in seconds before capture
            filename: Output filename
        
        Returns:
            Path to saved screenshot
        """
        import time
        print(f"Capturing in {delay} seconds...")
        time.sleep(delay)
        return self.capture_full_screen(filename)
    
    def capture_multiple(self, count=5, interval=1, prefix='capture'):
        """
        Capture multiple screenshots at intervals.
        
        Args:
            count: Number of screenshots to take
            interval: Seconds between captures
            prefix: Filename prefix
        
        Returns:
            List of saved screenshot paths
        """
        import time
        screenshots = []
        
        for i in range(count):
            filename = f"{prefix}_{i+1:03d}.png"
            path = self.capture_full_screen(filename)
            screenshots.append(path)
            print(f"Captured {i+1}/{count}: {path}")
            
            if i < count - 1:
                time.sleep(interval)
        
        return screenshots
    
    def _save_screenshot(self, image, filename=None):
        """Save screenshot to file."""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"screenshot_{timestamp}.png"
        
        filepath = self.output_dir / filename
        image.save(filepath)
        return str(filepath)
    
    # ===== OCR Functions =====
    
    def extract_text(self, image_path, lang='eng'):
        """
        Extract text from image using OCR.
        
        Args:
            image_path: Path to image file
            lang: Language code (eng, fra, deu, etc.)
        
        Returns:
            Extracted text
        """
        if not OCR_AVAILABLE:
            raise ImportError("pytesseract not installed. Install with: pip install pytesseract")
        
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang=lang)
        return text.strip()
    
    def extract_text_from_screen(self, lang='eng'):
        """
        Capture screen and extract text in one step.
        
        Args:
            lang: Language code
        
        Returns:
            Dict with screenshot_path and extracted_text
        """
        screenshot_path = self.capture_full_screen()
        text = self.extract_text(screenshot_path, lang=lang)
        
        return {
            'screenshot_path': screenshot_path,
            'text': text
        }
    
    def extract_text_from_region(self, x, y, width, height, lang='eng'):
        """
        Capture region and extract text.
        
        Args:
            x, y, width, height: Region coordinates
            lang: Language code
        
        Returns:
            Dict with screenshot_path and extracted_text
        """
        screenshot_path = self.capture_region(x, y, width, height)
        text = self.extract_text(screenshot_path, lang=lang)
        
        return {
            'screenshot_path': screenshot_path,
            'text': text
        }
    
    def get_text_boxes(self, image_path, lang='eng'):
        """
        Get bounding boxes for detected text.
        
        Args:
            image_path: Path to image
            lang: Language code
        
        Returns:
            List of dicts with text, coordinates, confidence
        """
        if not OCR_AVAILABLE:
            raise ImportError("pytesseract not installed")
        
        image = Image.open(image_path)
        data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
        
        boxes = []
        n_boxes = len(data['text'])
        
        for i in range(n_boxes):
            if int(data['conf'][i]) > 0:
                boxes.append({
                    'text': data['text'][i],
                    'x': data['left'][i],
                    'y': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i],
                    'confidence': data['conf'][i]
                })
        
        return boxes
    
    # ===== Utility Functions =====
    
    def get_screen_size(self):
        """Get screen dimensions."""
        size = pyautogui.size()
        return {'width': size.width, 'height': size.height}
    
    def get_mouse_position(self):
        """Get current mouse position."""
        pos = pyautogui.position()
        return {'x': pos.x, 'y': pos.y}


if __name__ == '__main__':
    import sys
    
    sc = ScreenCapture()
    
    # Command line usage
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'full':
            path = sc.capture_full_screen()
            print(f"Screenshot saved: {path}")
        
        elif command == 'region' and len(sys.argv) == 6:
            x, y, w, h = map(int, sys.argv[2:])
            path = sc.capture_region(x, y, w, h)
            print(f"Screenshot saved: {path}")
        
        elif command == 'delay' and len(sys.argv) == 3:
            delay = int(sys.argv[2])
            path = sc.capture_with_delay(delay)
            print(f"Screenshot saved: {path}")
        
        elif command == 'ocr' and len(sys.argv) == 3:
            image_path = sys.argv[2]
            text = sc.extract_text(image_path)
            print(f"Extracted text:\n{text}")
        
        else:
            print("Usage:")
            print("  python screen_capture.py full")
            print("  python screen_capture.py region X Y WIDTH HEIGHT")
            print("  python screen_capture.py delay SECONDS")
            print("  python screen_capture.py ocr IMAGE_PATH")
    else:
        # Interactive demo
        print("Taking screenshot in 3 seconds...")
        path = sc.capture_with_delay(3)
        print(f"Saved: {path}")
        
        if OCR_AVAILABLE:
            print("\nExtracting text...")
            text = sc.extract_text(path)
            if text:
                print(f"Found text:\n{text}")
            else:
                print("No text found")

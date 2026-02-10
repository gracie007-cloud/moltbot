---
name: screenshot-ocr
description: Screen capture and OCR text extraction utilities. Capture full screen, specific regions, active windows, or multiple screenshots with intervals. Extract text from images using Tesseract OCR with bounding box detection. Use when tasks involve taking screenshots, extracting text from screen content, capturing UI elements, monitoring visual changes, or automating screen-based workflows.
---

# Screenshot + OCR

Capture screenshots and extract text using OCR.

## Quick Start

```python
from scripts.screen_capture import ScreenCapture

sc = ScreenCapture(output_dir='screenshots')

# Capture full screen
screenshot_path = sc.capture_full_screen()

# Extract text from image
text = sc.extract_text(screenshot_path)
print(text)
```

## Setup

```bash
# Install dependencies
pip install pillow pyautogui pytesseract

# Install Tesseract OCR (Windows)
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Install to: C:\Program Files\Tesseract-OCR

# Linux
sudo apt-get install tesseract-ocr

# Mac
brew install tesseract
```

## Screenshot Capture

### Full Screen

```python
# Capture entire screen
path = sc.capture_full_screen()

# Custom filename
path = sc.capture_full_screen(filename='my_screenshot.png')
```

### Region Capture

```python
# Capture specific area (x, y, width, height)
path = sc.capture_region(100, 100, 800, 600)

# Top-left corner, 500x500
path = sc.capture_region(0, 0, 500, 500)
```

### Active Window (Windows only)

```python
# Capture the currently focused window
path = sc.capture_window()
```

### Delayed Capture

```python
# Wait 5 seconds before capturing
path = sc.capture_with_delay(delay=5)

# Use to prepare UI before capture
path = sc.capture_with_delay(delay=3, filename='prepared_ui.png')
```

### Multiple Screenshots

```python
# Take 10 screenshots, 2 seconds apart
paths = sc.capture_multiple(count=10, interval=2, prefix='sequence')

# Result: sequence_001.png, sequence_002.png, ..., sequence_010.png
for path in paths:
    print(f"Captured: {path}")
```

## OCR Text Extraction

### Extract from Image

```python
# Extract all text from image
text = sc.extract_text('screenshot.png')
print(text)

# Different language (French)
text = sc.extract_text('screenshot.png', lang='fra')

# Multiple languages
text = sc.extract_text('screenshot.png', lang='eng+fra')
```

### Capture and Extract

```python
# Capture full screen and extract text in one step
result = sc.extract_text_from_screen()

print(f"Screenshot: {result['screenshot_path']}")
print(f"Text: {result['text']}")

# Capture region and extract
result = sc.extract_text_from_region(100, 100, 800, 600)
```

### Get Text Bounding Boxes

```python
# Get coordinates of detected text
boxes = sc.get_text_boxes('screenshot.png')

for box in boxes:
    print(f"Text: '{box['text']}'")
    print(f"  Position: ({box['x']}, {box['y']})")
    print(f"  Size: {box['width']}x{box['height']}")
    print(f"  Confidence: {box['confidence']}%")
```

## Utility Functions

### Screen Information

```python
# Get screen dimensions
size = sc.get_screen_size()
print(f"Screen: {size['width']}x{size['height']}")

# Get mouse position
pos = sc.get_mouse_position()
print(f"Mouse at: ({pos['x']}, {pos['y']})")
```

## Common Workflows

### Monitor Application Output

```python
# Capture terminal/console region every 5 seconds
for i in range(10):
    result = sc.extract_text_from_region(0, 0, 1000, 800)
    print(f"\nCapture {i+1}:")
    print(result['text'])
    time.sleep(5)
```

### Extract Dialog Text

```python
# Wait for dialog, then capture and read
import time

print("Trigger the dialog now...")
time.sleep(5)

result = sc.extract_text_from_screen()
print(f"Dialog text:\n{result['text']}")
```

### Document Scanning

```python
# Capture multiple pages with user control
pages = []

for i in range(5):
    input(f"Press Enter to capture page {i+1}...")
    path = sc.capture_full_screen(filename=f'page_{i+1}.png')
    text = sc.extract_text(path)

    pages.append({
        'image': path,
        'text': text
    })
    print(f"Captured page {i+1}")

# Save all text to file
with open('extracted_document.txt', 'w', encoding='utf-8') as f:
    for i, page in enumerate(pages):
        f.write(f"=== Page {i+1} ===\n")
        f.write(page['text'])
        f.write("\n\n")
```

### UI Testing / Validation

```python
# Capture UI state and verify text
path = sc.capture_region(100, 100, 400, 300)
text = sc.extract_text(path)

# Check for expected content
if "Success" in text:
    print("UI showing success message")
elif "Error" in text:
    print("UI showing error message")
else:
    print("Unexpected UI state")
```

### Create Screenshot Documentation

```python
# Capture sequence with annotations
steps = [
    ("step1_login", "Login screen", 3),
    ("step2_dashboard", "Dashboard view", 3),
    ("step3_settings", "Settings page", 3)
]

screenshots = []

for filename, description, delay in steps:
    print(f"Prepare: {description}")
    time.sleep(delay)

    path = sc.capture_full_screen(filename=f"{filename}.png")
    screenshots.append({
        'path': path,
        'description': description
    })
    print(f"Captured: {path}")

# Generate markdown documentation
with open('SCREENSHOTS.md', 'w') as f:
    f.write("# Screenshot Documentation\n\n")
    for item in screenshots:
        f.write(f"## {item['description']}\n")
        f.write(f"![{item['description']}]({item['path']})\n\n")
```

## Supported OCR Languages

Common language codes:

- `eng` - English
- `fra` - French
- `deu` - German
- `spa` - Spanish
- `por` - Portuguese
- `ita` - Italian
- `rus` - Russian
- `chi_sim` - Simplified Chinese
- `chi_tra` - Traditional Chinese
- `jpn` - Japanese
- `kor` - Korean
- `ara` - Arabic

Combine languages: `eng+fra` for English and French

Check available languages:

```bash
tesseract --list-langs
```

Install additional languages:

```bash
# Linux
sudo apt-get install tesseract-ocr-fra tesseract-ocr-deu

# Download language data files for Windows/Mac from:
# https://github.com/tesseract-ocr/tessdata
```

## Tips & Best Practices

1. **Use delays** before capture to let UI settle
2. **Capture regions** instead of full screen for better OCR accuracy
3. **Clean backgrounds** improve text extraction
4. **Good contrast** (dark text on light background) works best
5. **Higher resolution** screenshots give better OCR results
6. **Test language codes** for non-English text
7. **Pre-process images** (contrast, brightness) if OCR fails
8. **Use bounding boxes** to locate specific text elements

## OCR Accuracy

Factors affecting accuracy:

- **Image quality**: Higher resolution = better results
- **Contrast**: Clear text vs background
- **Font**: Standard fonts work best
- **Size**: Text should be readable (12pt+)
- **Skew**: Straight text works better than rotated
- **Noise**: Clean images preferred
- **Language**: Match language code to text

Improve accuracy:

```python
from PIL import Image, ImageEnhance

# Enhance image before OCR
img = Image.open('screenshot.png')

# Increase contrast
enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(2)

# Convert to grayscale
img = img.convert('L')

# Save enhanced image
img.save('enhanced.png')

# Now extract text
text = sc.extract_text('enhanced.png')
```

## Platform Support

- **Windows**: Full support (including active window capture)
- **Linux**: Screenshot and region capture (no active window)
- **Mac**: Screenshot and region capture (no active window)

## Dependencies

```bash
pip install pillow pyautogui pytesseract

# Windows-specific (optional, for active window capture)
pip install pywin32
```

## Troubleshooting

### "tesseract is not installed"

- Install Tesseract OCR system package
- Windows: Set `pytesseract.pytesseract.tesseract_cmd` to installation path

### No text extracted

- Check image quality and contrast
- Verify correct language code
- Try enhancing image first
- Ensure text is readable (not too small)

### Permission errors

- Run with appropriate permissions
- Some screen areas may be protected (e.g., secure input fields)

### Empty screenshots

- Check screen coordinates
- Ensure region is within screen bounds
- Verify no display scaling issues

## Limitations

- OCR accuracy depends on image quality
- Active window capture Windows-only
- Some protected content cannot be captured
- Performance depends on image size and text amount
- DRM-protected content may be blocked

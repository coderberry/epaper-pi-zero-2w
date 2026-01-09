"""
Helper functions for e-paper display.
Handles image conversion to the format expected by the EPD driver.
"""

from PIL import Image
from epd_2inch13 import EPD_WIDTH, EPD_HEIGHT

# Display dimensions
DISPLAY_WIDTH = EPD_WIDTH    # 122 pixels
DISPLAY_HEIGHT = EPD_HEIGHT  # 250 pixels

def pil_to_epd(image):
    """
    Convert a PIL Image to the byte format expected by epd.display().

    The display expects 4000 bytes organized as:
    - 16 byte-rows (122 pixels / 8 = 15.25, rounded up to 16)
    - 250 columns
    - Each byte represents 8 vertical pixels

    Args:
        image: PIL Image object (will be resized/converted as needed)

    Returns:
        list: 4000 bytes ready for epd.display()
    """
    # Resize to display dimensions if needed
    if image.size != (DISPLAY_WIDTH, DISPLAY_HEIGHT):
        image = image.resize((DISPLAY_WIDTH, DISPLAY_HEIGHT), Image.LANCZOS)

    # Convert to 1-bit black and white
    image = image.convert('1')

    # Get pixel data
    pixels = image.load()

    # Calculate byte dimensions
    byte_width = (DISPLAY_WIDTH + 7) // 8  # 16 bytes per row

    # Create output buffer (4000 bytes)
    img_bytes = [0xFF] * (byte_width * DISPLAY_HEIGHT)

    # Convert pixels to bytes
    # The display memory is organized column-by-column
    for y in range(DISPLAY_HEIGHT):
        for x in range(DISPLAY_WIDTH):
            if pixels[x, y] == 0:  # Black pixel
                byte_idx = y + (x // 8) * DISPLAY_HEIGHT
                bit_idx = 7 - (x % 8)
                img_bytes[byte_idx] &= ~(1 << bit_idx)

    return img_bytes


def create_canvas():
    """
    Create a new blank canvas (white) for drawing.

    Returns:
        tuple: (PIL.Image, PIL.ImageDraw.Draw) - image and draw objects
    """
    from PIL import ImageDraw
    image = Image.new('1', (DISPLAY_WIDTH, DISPLAY_HEIGHT), 255)
    draw = ImageDraw.Draw(image)
    return image, draw


def load_font(size=16):
    """
    Load a TrueType font, falling back to default if not available.

    Args:
        size: Font size in points

    Returns:
        PIL.ImageFont: Font object
    """
    from PIL import ImageFont
    try:
        return ImageFont.truetype("MiSans-Light.ttf", size)
    except:
        return ImageFont.load_default()

"""
Helper functions for e-paper display.
Uses the EPD_GUI class which has the correct memory layout for the display.
"""

import os
from PIL import Image, ImageDraw, ImageFont
from epd_2inch13 import EPD_WIDTH, EPD_HEIGHT
from epd_gui import EPD_GUI, WHITE, BLACK

# Display dimensions
DISPLAY_WIDTH = EPD_WIDTH    # 122 pixels
DISPLAY_HEIGHT = EPD_HEIGHT  # 250 pixels

# Script directory for bundled fonts
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Font registry: friendly name -> list of possible paths (first found is used)
FONT_REGISTRY = {
    "misans": [
        os.path.join(_SCRIPT_DIR, "MiSans-Light.ttf"),
        "MiSans-Light.ttf",
    ],
    "sans": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
    ],
    "sans-bold": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    ],
    "mono": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
    ],
    "mono-bold": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf",
    ],
    "serif": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/TTF/DejaVuSerif.ttf",
    ],
    "serif-bold": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSerif-Bold.ttf",
    ],
}

# Default font to use
DEFAULT_FONT = "misans"


class EPDCanvas:
    """
    A canvas for drawing on the e-paper display.
    Uses EPD_GUI internally for correct memory layout.
    Provides a simple interface for drawing shapes and text.
    """

    def __init__(self):
        self.gui = EPD_GUI()
        self.width = DISPLAY_WIDTH
        self.height = DISPLAY_HEIGHT

    def clear(self, color=WHITE):
        """Clear the canvas to white (0xFF) or black (0x00)."""
        self.gui.clear(color)

    def pixel(self, x, y, color=BLACK):
        """Set a single pixel."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.gui.set_pixel(x, y, color)

    def line(self, x1, y1, x2, y2, color=BLACK):
        """Draw a line from (x1,y1) to (x2,y2)."""
        from epd_gui import PIXEL_1X1, LINE_SOLID
        self.gui.draw_line(x1, y1, x2, y2, color, PIXEL_1X1, LINE_SOLID)

    def rectangle(self, x1, y1, x2, y2, color=BLACK, fill=False):
        """Draw a rectangle. If fill=True, fill it solid."""
        from epd_gui import PIXEL_1X1, FILL_EMPTY, FILL_FULL
        fill_style = FILL_FULL if fill else FILL_EMPTY
        self.gui.draw_rectangle(x1, y1, x2, y2, color, fill_style, PIXEL_1X1)

    def circle(self, x, y, radius, color=BLACK, fill=False):
        """Draw a circle centered at (x,y) with given radius."""
        from epd_gui import PIXEL_1X1, FILL_EMPTY, FILL_FULL
        fill_style = FILL_FULL if fill else FILL_EMPTY
        self.gui.draw_circle(x, y, radius, color, fill_style, PIXEL_1X1)

    def text(self, x, y, text_str, font=None, color=BLACK):
        """
        Draw text at position (x,y).
        font should be a PIL ImageFont object.
        """
        if font is None:
            font = load_font(16)

        # Get font metrics
        try:
            # Try newer Pillow API first
            bbox = font.getbbox(text_str)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            # Fall back to older API
            text_width, text_height = font.getsize(text_str)

        # Render text to a small image
        text_img = Image.new('1', (text_width + 4, text_height + 4), 1)
        draw = ImageDraw.Draw(text_img)
        draw.text((0, 0), text_str, font=font, fill=0)

        # Copy pixels to canvas
        pixels = text_img.load()
        for ty in range(text_img.height):
            for tx in range(text_img.width):
                if pixels[tx, ty] == 0:  # Black pixel in text
                    self.pixel(x + tx, y + ty, color)

    def display(self):
        """Send the canvas to the display."""
        self.gui.epd.display(self.gui.img)

    def display_fast(self):
        """Send the canvas using fast refresh (less flicker, may ghost)."""
        self.gui.epd.hw_init_fast()
        self.gui.epd.whitescreen_all_fast(self.gui.img)

    def sleep(self):
        """Put the display to sleep (required after display)."""
        self.gui.epd.sleep()

    def cleanup(self):
        """Clean up GPIO resources."""
        self.gui.epd.clean_gpio()


def get_available_fonts():
    """
    Get list of available font names.

    Returns:
        list: List of font names that are available on this system
    """
    available = []
    for name, paths in FONT_REGISTRY.items():
        for path in paths:
            if os.path.exists(path):
                available.append(name)
                break
    return available


def load_font(size=16, font_name=None):
    """
    Load a TrueType font by name, falling back to default if not available.

    Args:
        size: Font size in points
        font_name: Font name from FONT_REGISTRY (e.g., 'sans', 'mono', 'serif')
                   If None, uses DEFAULT_FONT

    Returns:
        PIL.ImageFont: Font object
    """
    if font_name is None:
        font_name = DEFAULT_FONT

    # Try the requested font first
    if font_name in FONT_REGISTRY:
        for path in FONT_REGISTRY[font_name]:
            try:
                return ImageFont.truetype(path, size)
            except (IOError, OSError):
                continue

    # Fall back to default font
    if font_name != DEFAULT_FONT and DEFAULT_FONT in FONT_REGISTRY:
        for path in FONT_REGISTRY[DEFAULT_FONT]:
            try:
                return ImageFont.truetype(path, size)
            except (IOError, OSError):
                continue

    # Last resort: PIL default
    return ImageFont.load_default()

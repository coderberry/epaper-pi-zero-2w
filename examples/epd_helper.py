"""
Helper functions for e-paper display.
Uses the EPD_GUI class which has the correct memory layout for the display.
"""

from PIL import Image, ImageDraw, ImageFont
from epd_2inch13 import EPD_WIDTH, EPD_HEIGHT
from epd_gui import EPD_GUI, WHITE, BLACK

# Display dimensions
DISPLAY_WIDTH = EPD_WIDTH    # 122 pixels
DISPLAY_HEIGHT = EPD_HEIGHT  # 250 pixels


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


def load_font(size=16):
    """
    Load a TrueType font, falling back to default if not available.

    Args:
        size: Font size in points

    Returns:
        PIL.ImageFont: Font object
    """
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Try fonts in order of preference
    font_paths = [
        os.path.join(script_dir, "MiSans-Light.ttf"),
        "MiSans-Light.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
    ]

    for font_path in font_paths:
        try:
            return ImageFont.truetype(font_path, size)
        except (IOError, OSError):
            continue

    return ImageFont.load_default()

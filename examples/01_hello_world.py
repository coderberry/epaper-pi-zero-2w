#!/usr/bin/env python3
"""
Example 01: Hello World
Displays simple text on the e-paper display.
"""

from epd_2inch13 import EPD_2Inch13
from epd_helper import create_canvas, pil_to_epd, load_font
import time

def main():
    epd = EPD_2Inch13()

    try:
        print("Initializing display...")
        epd.hw_init_gui()

        # Create canvas for drawing
        image, draw = create_canvas()

        # Load fonts
        font_large = load_font(24)
        font_small = load_font(16)

        # Draw text
        draw.text((10, 20), "Hello World!", font=font_large, fill=0)
        draw.text((10, 50), "e-Paper Display", font=font_small, fill=0)
        draw.text((10, 75), "Raspberry Pi Zero 2W", font=font_small, fill=0)
        draw.text((10, 100), "122 x 250 pixels", font=font_small, fill=0)

        # Convert and display
        img_bytes = pil_to_epd(image)

        print("Displaying image...")
        epd.display(img_bytes)

        print("Done! Display will hold image.")
        time.sleep(2)
        epd.sleep()

    except KeyboardInterrupt:
        print("Interrupted")
        epd.sleep()
    finally:
        epd.clean_gpio()

if __name__ == "__main__":
    main()

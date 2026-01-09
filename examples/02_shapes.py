#!/usr/bin/env python3
"""
Example 02: Drawing Shapes
Demonstrates drawing lines, rectangles, circles, and polygons.
"""

from epd_2inch13 import EPD_2Inch13
from epd_helper import create_canvas, pil_to_epd, load_font
import time

def main():
    epd = EPD_2Inch13()

    try:
        print("Initializing display...")
        epd.hw_init_gui()

        # Create canvas
        image, draw = create_canvas()

        # Draw various shapes

        # Lines
        draw.line((10, 10, 80, 10), fill=0, width=1)
        draw.line((10, 15, 80, 15), fill=0, width=2)
        draw.line((10, 22, 80, 40), fill=0, width=1)  # Diagonal

        # Rectangles
        draw.rectangle((10, 50, 50, 80), outline=0)   # Outline only
        draw.rectangle((60, 50, 100, 80), fill=0)     # Filled

        # Circles/Ellipses
        draw.ellipse((10, 90, 40, 120), outline=0)    # Circle outline
        draw.ellipse((50, 90, 80, 120), fill=0)       # Circle filled

        # Polygon (triangle)
        draw.polygon([(10, 140), (50, 140), (30, 170)], outline=0)

        # Filled polygon
        draw.polygon([(60, 140), (100, 140), (80, 170)], fill=0)

        # Arc
        draw.arc((10, 180, 50, 220), start=0, end=180, fill=0)

        # Chord
        draw.chord((60, 180, 100, 220), start=0, end=180, fill=0)

        # Add label
        font = load_font(12)
        draw.text((10, 230), "Shapes Demo", font=font, fill=0)

        # Convert and display
        img_bytes = pil_to_epd(image)

        print("Displaying shapes...")
        epd.display(img_bytes)

        print("Done!")
        time.sleep(2)
        epd.sleep()

    except KeyboardInterrupt:
        print("Interrupted")
        epd.sleep()
    finally:
        epd.clean_gpio()

if __name__ == "__main__":
    main()

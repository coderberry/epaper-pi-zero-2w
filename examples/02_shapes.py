#!/usr/bin/env python3
"""
Example 02: Drawing Shapes
Demonstrates drawing lines, rectangles, circles, and polygons.
"""

from PIL import Image, ImageDraw, ImageFont
from epd_2inch13 import EPD_2Inch13, EPD_WIDTH, EPD_HEIGHT
import time

def main():
    epd = EPD_2Inch13()

    try:
        print("Initializing display...")
        epd.hw_init_gui()

        # Create image (landscape orientation)
        image = Image.new('1', (EPD_HEIGHT, EPD_WIDTH), 255)
        draw = ImageDraw.Draw(image)

        # Draw various shapes

        # Lines
        draw.line((10, 10, 80, 10), fill=0, width=1)
        draw.line((10, 15, 80, 15), fill=0, width=2)
        draw.line((10, 22, 80, 40), fill=0, width=1)  # Diagonal

        # Rectangles
        draw.rectangle((100, 10, 150, 40), outline=0)  # Outline only
        draw.rectangle((160, 10, 210, 40), fill=0)     # Filled

        # Circles/Ellipses
        draw.ellipse((10, 50, 50, 90), outline=0)      # Circle outline
        draw.ellipse((60, 50, 100, 90), fill=0)        # Circle filled
        draw.ellipse((110, 50, 180, 90), outline=0)    # Ellipse

        # Polygon (triangle)
        draw.polygon([(200, 50), (230, 90), (170, 90)], outline=0)

        # Arc
        draw.arc((10, 95, 60, 120), start=0, end=180, fill=0)

        # Dashed line (manual)
        for i in range(0, 80, 10):
            draw.line((100 + i, 105, 105 + i, 105), fill=0, width=1)

        # Add label
        try:
            font = ImageFont.truetype("MiSans-Light.ttf", 12)
        except:
            font = ImageFont.load_default()
        draw.text((190, 95), "Shapes!", font=font, fill=0)

        # Convert and display
        image = image.rotate(90, expand=True)
        pixels = list(image.getdata())

        img_bytes = []
        for i in range(0, len(pixels), 8):
            byte = 0
            for j in range(8):
                if i + j < len(pixels) and pixels[i + j] == 0:
                    byte |= (0x80 >> j)
            img_bytes.append(byte ^ 0xFF)

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

#!/usr/bin/env python3
"""
Example 01: Hello World
Displays simple text on the e-paper display.
"""

from PIL import Image, ImageDraw, ImageFont
from epd_2inch13 import EPD_2Inch13, EPD_WIDTH, EPD_HEIGHT
import time

def main():
    epd = EPD_2Inch13()

    try:
        print("Initializing display...")
        epd.hw_init_gui()

        # Create a new image with white background
        # Note: width and height are swapped for landscape orientation
        image = Image.new('1', (EPD_HEIGHT, EPD_WIDTH), 255)
        draw = ImageDraw.Draw(image)

        # Load fonts (use default if custom font not available)
        try:
            font_large = ImageFont.truetype("MiSans-Light.ttf", 24)
            font_small = ImageFont.truetype("MiSans-Light.ttf", 16)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Draw text
        draw.text((10, 20), "Hello World!", font=font_large, fill=0)
        draw.text((10, 50), "e-Paper Display", font=font_small, fill=0)
        draw.text((10, 75), "Raspberry Pi Zero 2W", font=font_small, fill=0)
        draw.text((10, 100), "122 x 250 pixels", font=font_small, fill=0)

        # Convert image to display format
        # Rotate and convert to bytes
        image = image.rotate(90, expand=True)
        pixels = list(image.getdata())

        # Pack pixels into bytes (8 pixels per byte)
        img_bytes = []
        for i in range(0, len(pixels), 8):
            byte = 0
            for j in range(8):
                if i + j < len(pixels) and pixels[i + j] == 0:
                    byte |= (0x80 >> j)
            img_bytes.append(byte ^ 0xFF)  # Invert: 0=black, 1=white

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

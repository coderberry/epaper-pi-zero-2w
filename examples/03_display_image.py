#!/usr/bin/env python3
"""
Example 03: Display Image
Load and display a BMP, PNG, or JPG image on the e-paper display.

Usage: python3 03_display_image.py [image_path]
If no image is provided, creates a sample gradient pattern.
"""

from PIL import Image
from epd_2inch13 import EPD_2Inch13
from epd_helper import pil_to_epd, DISPLAY_WIDTH, DISPLAY_HEIGHT
import sys
import time

def create_sample_image():
    """Create a sample gradient/pattern image for demo."""
    image = Image.new('L', (DISPLAY_WIDTH, DISPLAY_HEIGHT), 255)
    pixels = image.load()

    # Create a diagonal gradient pattern
    for y in range(DISPLAY_HEIGHT):
        for x in range(DISPLAY_WIDTH):
            # Checkerboard with gradient
            checker = ((x // 20) + (y // 20)) % 2
            gradient = int((x + y) / (DISPLAY_WIDTH + DISPLAY_HEIGHT) * 255)
            if checker:
                pixels[x, y] = gradient
            else:
                pixels[x, y] = 255 - gradient

    return image

def main():
    epd = EPD_2Inch13()

    try:
        # Load image from argument or create sample
        if len(sys.argv) > 1:
            image_path = sys.argv[1]
            print(f"Loading image: {image_path}")
            image = Image.open(image_path)
        else:
            print("No image provided, creating sample pattern...")
            print("Usage: python3 03_display_image.py <image_path>")
            image = create_sample_image()

        print(f"Original size: {image.size}")
        print(f"Display size: {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")

        print("Initializing display...")
        epd.hw_init_gui()

        # Convert and display
        img_bytes = pil_to_epd(image)

        print("Displaying image...")
        epd.display(img_bytes)

        print("Done!")
        time.sleep(2)
        epd.sleep()

    except FileNotFoundError:
        print(f"Error: Image file not found: {sys.argv[1]}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Interrupted")
        epd.sleep()
    finally:
        epd.clean_gpio()

if __name__ == "__main__":
    main()

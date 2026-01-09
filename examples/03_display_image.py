#!/usr/bin/env python3
"""
Example 03: Display Image
Load and display a BMP, PNG, or JPG image on the e-paper display.

Usage: python3 03_display_image.py [image_path]
If no image is provided, creates a sample gradient pattern.
"""

from PIL import Image
from epd_2inch13 import EPD_2Inch13, EPD_WIDTH, EPD_HEIGHT
import sys
import time

def image_to_epd_bytes(image):
    """Convert PIL Image to e-paper byte format."""
    # Ensure image is the right size
    image = image.resize((EPD_WIDTH, EPD_HEIGHT))

    # Convert to 1-bit (black and white)
    image = image.convert('1')

    pixels = list(image.getdata())

    # Pack pixels into bytes (8 pixels per byte)
    img_bytes = []
    for i in range(0, len(pixels), 8):
        byte = 0
        for j in range(8):
            if i + j < len(pixels) and pixels[i + j] == 0:
                byte |= (0x80 >> j)
        img_bytes.append(byte ^ 0xFF)  # Invert for display

    return img_bytes

def create_sample_image():
    """Create a sample gradient/pattern image for demo."""
    image = Image.new('L', (EPD_WIDTH, EPD_HEIGHT), 255)
    pixels = image.load()

    # Create a diagonal gradient pattern
    for y in range(EPD_HEIGHT):
        for x in range(EPD_WIDTH):
            # Checkerboard with gradient
            checker = ((x // 20) + (y // 20)) % 2
            gradient = int((x + y) / (EPD_WIDTH + EPD_HEIGHT) * 255)
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
        print(f"Display size: {EPD_WIDTH}x{EPD_HEIGHT}")

        print("Initializing display...")
        epd.hw_init_gui()

        # Convert and display
        img_bytes = image_to_epd_bytes(image)

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

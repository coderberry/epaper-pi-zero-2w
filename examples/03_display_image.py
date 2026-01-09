#!/usr/bin/env python3
"""
Example 03: Display Image
Load and display a BMP, PNG, or JPG image on the e-paper display.

Usage: python3 03_display_image.py [image_path]
If no image is provided, creates a sample pattern.
"""

from PIL import Image
from epd_helper import EPDCanvas, DISPLAY_WIDTH, DISPLAY_HEIGHT
import sys
import time

def main():
    canvas = EPDCanvas()

    try:
        # Load image from argument or create sample
        if len(sys.argv) > 1:
            image_path = sys.argv[1]
            print(f"Loading image: {image_path}")
            image = Image.open(image_path)
            print(f"Original size: {image.size}")

            # Resize to fit display
            image = image.resize((DISPLAY_WIDTH, DISPLAY_HEIGHT), Image.LANCZOS)

            # Convert to black and white
            image = image.convert('1')
        else:
            print("No image provided, creating sample pattern...")
            print("Usage: python3 03_display_image.py <image_path>")

            # Create a sample pattern
            image = Image.new('1', (DISPLAY_WIDTH, DISPLAY_HEIGHT), 1)
            pixels = image.load()

            # Checkerboard pattern
            for y in range(DISPLAY_HEIGHT):
                for x in range(DISPLAY_WIDTH):
                    if ((x // 15) + (y // 15)) % 2 == 0:
                        pixels[x, y] = 0

        print(f"Display size: {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
        print("Converting image...")

        # Copy image pixels to canvas
        canvas.clear()
        pixels = image.load()
        for y in range(DISPLAY_HEIGHT):
            for x in range(DISPLAY_WIDTH):
                if pixels[x, y] == 0:  # Black pixel
                    canvas.pixel(x, y)

        print("Sending to display...")
        canvas.display()

        print("Done!")
        time.sleep(2)
        canvas.sleep()

    except FileNotFoundError:
        print(f"Error: Image file not found: {sys.argv[1]}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Interrupted")
        canvas.sleep()
    finally:
        canvas.cleanup()

if __name__ == "__main__":
    main()

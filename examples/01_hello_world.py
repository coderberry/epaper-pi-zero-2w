#!/usr/bin/env python3
"""
Example 01: Hello World
Displays simple text on the e-paper display.
"""

from epd_helper import EPDCanvas, load_font
import time

def main():
    canvas = EPDCanvas()

    try:
        print("Drawing text...")
        canvas.clear()

        # Load fonts
        font_large = load_font(24)
        font_small = load_font(16)

        # Draw text
        canvas.text(5, 20, "Hello World!", font=font_large)
        canvas.text(5, 50, "e-Paper Display", font=font_small)
        canvas.text(5, 75, "Raspberry Pi Zero 2W", font=font_small)
        canvas.text(5, 100, "122 x 250 pixels", font=font_small)

        print("Sending to display...")
        canvas.display()

        print("Done! Display will hold image.")
        time.sleep(2)
        canvas.sleep()

    except KeyboardInterrupt:
        print("Interrupted")
        canvas.sleep()
    finally:
        canvas.cleanup()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Example 02: Drawing Shapes
Demonstrates drawing lines, rectangles, and circles.
"""

from epd_helper import EPDCanvas, load_font
import time

def main():
    canvas = EPDCanvas()

    try:
        print("Drawing shapes...")
        canvas.clear()

        # Lines
        canvas.line(10, 10, 80, 10)       # Horizontal
        canvas.line(10, 20, 80, 40)       # Diagonal
        canvas.line(90, 10, 90, 50)       # Vertical

        # Rectangles
        canvas.rectangle(10, 50, 50, 80)              # Outline
        canvas.rectangle(60, 50, 100, 80, fill=True)  # Filled

        # Circles
        canvas.circle(30, 110, 15)              # Outline
        canvas.circle(80, 110, 15, fill=True)   # Filled

        # More shapes lower on screen
        canvas.rectangle(10, 140, 110, 145, fill=True)  # Thick line
        canvas.circle(60, 180, 30)                       # Large circle

        # Label
        font = load_font(12)
        canvas.text(10, 220, "Shapes Demo", font=font)

        print("Sending to display...")
        canvas.display()

        print("Done!")
        time.sleep(2)
        canvas.sleep()

    except KeyboardInterrupt:
        print("Interrupted")
        canvas.sleep()
    finally:
        canvas.cleanup()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Example 04: Digital Clock
Displays a digital clock that updates every second.

Press Ctrl+C to exit.
"""

from epd_helper import EPDCanvas, load_font
import time
from datetime import datetime

def main():
    canvas = EPDCanvas()

    try:
        # Load fonts
        font_time = load_font(32)
        font_date = load_font(12)
        font_label = load_font(10)

        print("Clock running. Press Ctrl+C to stop.")
        print("Full refresh every minute to prevent ghosting.")

        last_minute = -1

        while True:
            now = datetime.now()

            # Redraw canvas
            canvas.clear()

            # Border
            canvas.rectangle(0, 0, 121, 249)
            canvas.rectangle(2, 2, 119, 247)

            # Title
            canvas.text(20, 10, "Pi Zero Clock", font=font_label)

            # Time
            time_str = now.strftime("%H:%M:%S")
            canvas.text(8, 45, time_str, font=font_time)

            # Date
            canvas.text(10, 90, now.strftime("%A"), font=font_date)
            canvas.text(10, 110, now.strftime("%B %d, %Y"), font=font_date)

            # Separator
            canvas.line(10, 135, 110, 135)

            # Additional info
            canvas.text(10, 145, f"Week {now.strftime('%W')}", font=font_label)
            canvas.text(10, 160, f"Day {now.strftime('%j')} of year", font=font_label)

            # Full refresh once per minute
            if now.minute != last_minute:
                last_minute = now.minute
                canvas.display()
                print(f"Full refresh at {time_str}")
            else:
                canvas.display_fast()

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping clock...")
        canvas.clear()
        canvas.display()
        canvas.sleep()
    finally:
        canvas.cleanup()

if __name__ == "__main__":
    main()

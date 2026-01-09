#!/usr/bin/env python3
"""
Example 04: Digital Clock
Displays a digital clock that updates every second.
Uses fast refresh for quicker updates.

Press Ctrl+C to exit.
"""

from epd_2inch13 import EPD_2Inch13
from epd_helper import create_canvas, pil_to_epd, load_font
import time
from datetime import datetime

def main():
    epd = EPD_2Inch13()

    try:
        # Load fonts
        font_time = load_font(36)
        font_date = load_font(14)
        font_label = load_font(12)

        print("Initializing display...")
        print("Clock running. Press Ctrl+C to stop.")
        print("Full refresh every minute to prevent ghosting.")

        last_minute = -1

        while True:
            now = datetime.now()

            # Create display image
            image, draw = create_canvas()

            # Draw border
            draw.rectangle((0, 0, 121, 249), outline=0)
            draw.rectangle((2, 2, 119, 247), outline=0)

            # Title
            draw.text((25, 10), "Pi Zero Clock", font=font_label, fill=0)

            # Current time
            time_str = now.strftime("%H:%M:%S")
            draw.text((10, 50), time_str, font=font_time, fill=0)

            # Date
            date_str = now.strftime("%A")
            draw.text((10, 100), date_str, font=font_date, fill=0)
            date_str2 = now.strftime("%B %d, %Y")
            draw.text((10, 120), date_str2, font=font_date, fill=0)

            # Convert to display format
            img_bytes = pil_to_epd(image)

            # Full refresh once per minute to clear ghosting
            if now.minute != last_minute:
                last_minute = now.minute
                epd.hw_init_gui()
                epd.display(img_bytes)
                print(f"Full refresh at {time_str}")
            else:
                # Fast refresh for seconds updates
                epd.hw_init_fast()
                epd.whitescreen_all_fast(img_bytes)

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping clock...")
        epd.hw_init()
        epd.whitescreen_white()
        epd.sleep()
    finally:
        epd.clean_gpio()

if __name__ == "__main__":
    main()

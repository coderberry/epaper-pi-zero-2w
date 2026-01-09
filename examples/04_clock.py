#!/usr/bin/env python3
"""
Example 04: Digital Clock
Displays a digital clock that updates every second.
Uses partial refresh for faster updates without full screen flicker.

Press Ctrl+C to exit.
"""

from PIL import Image, ImageDraw, ImageFont
from epd_2inch13 import EPD_2Inch13, EPD_WIDTH, EPD_HEIGHT
import time
from datetime import datetime

def image_to_bytes(image):
    """Convert PIL Image to e-paper byte format."""
    pixels = list(image.getdata())
    img_bytes = []
    for i in range(0, len(pixels), 8):
        byte = 0
        for j in range(8):
            if i + j < len(pixels) and pixels[i + j] == 0:
                byte |= (0x80 >> j)
        img_bytes.append(byte ^ 0xFF)
    return img_bytes

def main():
    epd = EPD_2Inch13()

    try:
        # Load font
        try:
            font_time = ImageFont.truetype("MiSans-Light.ttf", 36)
            font_date = ImageFont.truetype("MiSans-Light.ttf", 16)
            font_label = ImageFont.truetype("MiSans-Light.ttf", 12)
        except:
            font_time = ImageFont.load_default()
            font_date = ImageFont.load_default()
            font_label = ImageFont.load_default()

        print("Initializing display...")
        epd.hw_init_gui()

        # Initial full refresh with clock face
        print("Drawing clock face...")
        image = Image.new('1', (EPD_HEIGHT, EPD_WIDTH), 255)
        draw = ImageDraw.Draw(image)

        # Draw border
        draw.rectangle((0, 0, EPD_HEIGHT-1, EPD_WIDTH-1), outline=0)
        draw.rectangle((2, 2, EPD_HEIGHT-3, EPD_WIDTH-3), outline=0)

        # Title
        draw.text((80, 8), "Pi Zero Clock", font=font_label, fill=0)

        # Draw initial time
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%A, %B %d, %Y")

        draw.text((55, 40), time_str, font=font_time, fill=0)
        draw.text((35, 85), date_str, font=font_date, fill=0)

        # Convert and display
        image = image.rotate(90, expand=True)
        img_bytes = image_to_bytes(image)
        epd.display(img_bytes)

        print("Clock running. Press Ctrl+C to stop.")
        print("Note: Full refresh every minute to prevent ghosting.")

        last_minute = now.minute

        while True:
            now = datetime.now()

            # Full refresh once per minute to clear ghosting
            if now.minute != last_minute:
                last_minute = now.minute
                epd.hw_init_gui()

                image = Image.new('1', (EPD_HEIGHT, EPD_WIDTH), 255)
                draw = ImageDraw.Draw(image)
                draw.rectangle((0, 0, EPD_HEIGHT-1, EPD_WIDTH-1), outline=0)
                draw.rectangle((2, 2, EPD_HEIGHT-3, EPD_WIDTH-3), outline=0)
                draw.text((80, 8), "Pi Zero Clock", font=font_label, fill=0)

                time_str = now.strftime("%H:%M:%S")
                date_str = now.strftime("%A, %B %d, %Y")
                draw.text((55, 40), time_str, font=font_time, fill=0)
                draw.text((35, 85), date_str, font=font_date, fill=0)

                image = image.rotate(90, expand=True)
                img_bytes = image_to_bytes(image)
                epd.display(img_bytes)
                print(f"Full refresh at {time_str}")
            else:
                # Quick update - just redraw time area
                # For simplicity, we do a full redraw but could optimize
                # with partial refresh for specific regions
                image = Image.new('1', (EPD_HEIGHT, EPD_WIDTH), 255)
                draw = ImageDraw.Draw(image)
                draw.rectangle((0, 0, EPD_HEIGHT-1, EPD_WIDTH-1), outline=0)
                draw.rectangle((2, 2, EPD_HEIGHT-3, EPD_WIDTH-3), outline=0)
                draw.text((80, 8), "Pi Zero Clock", font=font_label, fill=0)

                time_str = now.strftime("%H:%M:%S")
                date_str = now.strftime("%A, %B %d, %Y")
                draw.text((55, 40), time_str, font=font_time, fill=0)
                draw.text((35, 85), date_str, font=font_date, fill=0)

                image = image.rotate(90, expand=True)
                img_bytes = image_to_bytes(image)

                # Use fast update
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

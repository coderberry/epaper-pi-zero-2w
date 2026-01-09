#!/usr/bin/env python3
"""
Example 06: Weather Display Template
A template for displaying weather information.

To use with real data:
1. Sign up for a free API key at openweathermap.org
2. Set your API key and city below
3. Run the script

Without an API key, displays sample/demo weather data.
"""

from PIL import Image, ImageDraw, ImageFont
from epd_2inch13 import EPD_2Inch13, EPD_WIDTH, EPD_HEIGHT
import time
from datetime import datetime

# ============ CONFIGURATION ============
# Get a free API key from: https://openweathermap.org/api
API_KEY = ""  # Your OpenWeatherMap API key
CITY = "New York"  # Your city name
UNITS = "imperial"  # "imperial" for Fahrenheit, "metric" for Celsius
UPDATE_INTERVAL = 600  # Update every 10 minutes
# =======================================

def get_weather_data():
    """Fetch weather data from OpenWeatherMap API."""
    if not API_KEY:
        # Return demo data if no API key
        return {
            "city": "Demo City",
            "temp": 72,
            "feels_like": 70,
            "humidity": 45,
            "description": "Partly Cloudy",
            "wind": 8,
            "unit": "F" if UNITS == "imperial" else "C"
        }

    try:
        import urllib.request
        import json

        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units={UNITS}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        return {
            "city": data["name"],
            "temp": round(data["main"]["temp"]),
            "feels_like": round(data["main"]["feels_like"]),
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"].title(),
            "wind": round(data["wind"]["speed"]),
            "unit": "F" if UNITS == "imperial" else "C"
        }
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None

def draw_weather_icon(draw, x, y, description):
    """Draw a simple weather icon based on description."""
    desc = description.lower()

    if "sun" in desc or "clear" in desc:
        # Sun icon
        draw.ellipse((x+5, y+5, x+25, y+25), outline=0, width=2)
        # Sun rays
        for angle in range(0, 360, 45):
            import math
            rad = math.radians(angle)
            x1 = x + 15 + int(15 * math.cos(rad))
            y1 = y + 15 + int(15 * math.sin(rad))
            x2 = x + 15 + int(18 * math.cos(rad))
            y2 = y + 15 + int(18 * math.sin(rad))
            draw.line((x1, y1, x2, y2), fill=0, width=1)

    elif "cloud" in desc:
        # Cloud icon
        draw.ellipse((x+2, y+10, x+18, y+26), outline=0)
        draw.ellipse((x+10, y+5, x+28, y+23), outline=0)
        draw.ellipse((x+18, y+10, x+32, y+26), outline=0)
        draw.rectangle((x+5, y+16, x+28, y+26), fill=255)
        draw.arc((x+2, y+10, x+18, y+26), 180, 360, fill=0)
        draw.arc((x+10, y+5, x+28, y+23), 180, 360, fill=0)
        draw.arc((x+18, y+10, x+32, y+26), 180, 360, fill=0)

    elif "rain" in desc:
        # Rain icon (cloud + drops)
        draw.ellipse((x+5, y+2, x+18, y+15), outline=0)
        draw.ellipse((x+12, y+0, x+26, y+13), outline=0)
        # Rain drops
        for i in range(3):
            drop_x = x + 8 + i * 7
            draw.line((drop_x, y+18, drop_x, y+25), fill=0, width=1)

    elif "snow" in desc:
        # Snowflake
        cx, cy = x + 15, y + 15
        for angle in range(0, 360, 60):
            import math
            rad = math.radians(angle)
            x2 = cx + int(12 * math.cos(rad))
            y2 = cy + int(12 * math.sin(rad))
            draw.line((cx, cy, x2, y2), fill=0, width=1)

    else:
        # Generic icon (circle)
        draw.ellipse((x+5, y+5, x+25, y+25), outline=0)

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
        # Load fonts
        try:
            font_large = ImageFont.truetype("MiSans-Light.ttf", 32)
            font_medium = ImageFont.truetype("MiSans-Light.ttf", 14)
            font_small = ImageFont.truetype("MiSans-Light.ttf", 11)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()

        if not API_KEY:
            print("No API key set - displaying demo weather data")
            print("Edit the script to add your OpenWeatherMap API key")

        print(f"Weather display for: {CITY}")
        print(f"Updates every {UPDATE_INTERVAL} seconds. Press Ctrl+C to stop.")

        while True:
            weather = get_weather_data()

            if weather is None:
                print("Failed to get weather data, retrying...")
                time.sleep(60)
                continue

            print(f"{weather['city']}: {weather['temp']}°{weather['unit']} - {weather['description']}")

            # Create display
            epd.hw_init_gui()
            image = Image.new('1', (EPD_HEIGHT, EPD_WIDTH), 255)
            draw = ImageDraw.Draw(image)

            # City name header
            draw.rectangle((0, 0, EPD_HEIGHT, 18), fill=0)
            draw.text((5, 1), weather['city'], font=font_medium, fill=255)

            # Current time
            now = datetime.now().strftime("%H:%M")
            draw.text((200, 2), now, font=font_small, fill=255)

            # Temperature (large)
            temp_str = f"{weather['temp']}°{weather['unit']}"
            draw.text((10, 28), temp_str, font=font_large, fill=0)

            # Weather icon
            draw_weather_icon(draw, 130, 25, weather['description'])

            # Description
            draw.text((10, 68), weather['description'], font=font_medium, fill=0)

            # Details
            draw.line((0, 88, EPD_HEIGHT, 88), fill=0)
            draw.text((10, 93), f"Feels: {weather['feels_like']}°", font=font_small, fill=0)
            draw.text((80, 93), f"Humidity: {weather['humidity']}%", font=font_small, fill=0)
            draw.text((165, 93), f"Wind: {weather['wind']}mph", font=font_small, fill=0)

            # Updated time
            updated = datetime.now().strftime("Updated: %I:%M %p")
            draw.text((5, 108), updated, font=font_small, fill=0)

            # Convert and display
            image = image.rotate(90, expand=True)
            img_bytes = image_to_bytes(image)
            epd.display(img_bytes)

            epd.sleep()
            time.sleep(UPDATE_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopping weather display...")
        epd.hw_init()
        epd.whitescreen_white()
        epd.sleep()
    finally:
        epd.clean_gpio()

if __name__ == "__main__":
    main()

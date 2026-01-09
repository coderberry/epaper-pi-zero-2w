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

from epd_2inch13 import EPD_2Inch13
from epd_helper import create_canvas, pil_to_epd, load_font
import time
import math
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
            rad = math.radians(angle)
            x1 = x + 15 + int(12 * math.cos(rad))
            y1 = y + 15 + int(12 * math.sin(rad))
            x2 = x + 15 + int(16 * math.cos(rad))
            y2 = y + 15 + int(16 * math.sin(rad))
            draw.line((x1, y1, x2, y2), fill=0, width=1)

    elif "cloud" in desc:
        # Cloud icon
        draw.ellipse((x, y+8, x+14, y+22), outline=0)
        draw.ellipse((x+8, y+4, x+24, y+18), outline=0)
        draw.ellipse((x+16, y+8, x+30, y+22), outline=0)

    elif "rain" in desc:
        # Rain icon (cloud + drops)
        draw.ellipse((x+2, y, x+14, y+12), outline=0)
        draw.ellipse((x+10, y, x+22, y+10), outline=0)
        # Rain drops
        for i in range(3):
            drop_x = x + 6 + i * 6
            draw.line((drop_x, y+15, drop_x-2, y+22), fill=0, width=1)

    elif "snow" in desc:
        # Snowflake
        cx, cy = x + 15, y + 15
        for angle in range(0, 360, 60):
            rad = math.radians(angle)
            x2 = cx + int(10 * math.cos(rad))
            y2 = cy + int(10 * math.sin(rad))
            draw.line((cx, cy, x2, y2), fill=0, width=1)

    else:
        # Generic icon (circle with dot)
        draw.ellipse((x+5, y+5, x+25, y+25), outline=0)
        draw.ellipse((x+13, y+13, x+17, y+17), fill=0)

def main():
    epd = EPD_2Inch13()

    try:
        # Load fonts
        font_large = load_font(28)
        font_medium = load_font(12)
        font_small = load_font(10)

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
            image, draw = create_canvas()

            # City name header (inverted)
            draw.rectangle((0, 0, 121, 16), fill=0)
            city_display = weather['city'][:14]
            draw.text((5, 1), city_display, font=font_medium, fill=255)

            # Current time
            now = datetime.now().strftime("%H:%M")
            draw.text((95, 2), now, font=font_small, fill=255)

            # Temperature (large)
            temp_str = f"{weather['temp']}°{weather['unit']}"
            draw.text((10, 25), temp_str, font=font_large, fill=0)

            # Weather icon
            draw_weather_icon(draw, 85, 25, weather['description'])

            # Description
            draw.text((10, 60), weather['description'][:18], font=font_medium, fill=0)

            # Separator line
            draw.line((5, 80, 115, 80), fill=0)

            # Details
            draw.text((5, 85), f"Feels: {weather['feels_like']}°", font=font_small, fill=0)
            draw.text((5, 100), f"Humidity: {weather['humidity']}%", font=font_small, fill=0)
            draw.text((5, 115), f"Wind: {weather['wind']} mph", font=font_small, fill=0)

            # Updated time
            updated = datetime.now().strftime("%I:%M %p")
            draw.text((5, 235), f"Updated: {updated}", font=font_small, fill=0)

            # Convert and display
            img_bytes = pil_to_epd(image)
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

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

from epd_helper import EPDCanvas, load_font
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

def draw_sun(canvas, x, y):
    """Draw a sun icon."""
    canvas.circle(x + 12, y + 12, 8)
    # Rays
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        x1 = x + 12 + int(10 * math.cos(rad))
        y1 = y + 12 + int(10 * math.sin(rad))
        x2 = x + 12 + int(14 * math.cos(rad))
        y2 = y + 12 + int(14 * math.sin(rad))
        canvas.line(x1, y1, x2, y2)

def draw_cloud(canvas, x, y):
    """Draw a cloud icon."""
    canvas.circle(x + 8, y + 12, 6)
    canvas.circle(x + 16, y + 10, 8)
    canvas.circle(x + 24, y + 12, 6)

def draw_rain(canvas, x, y):
    """Draw rain icon."""
    draw_cloud(canvas, x, y)
    # Rain drops
    for i in range(3):
        canvas.line(x + 8 + i*8, y + 22, x + 6 + i*8, y + 28)

def draw_weather_icon(canvas, x, y, description):
    """Draw weather icon based on description."""
    desc = description.lower()
    if "sun" in desc or "clear" in desc:
        draw_sun(canvas, x, y)
    elif "rain" in desc:
        draw_rain(canvas, x, y)
    elif "cloud" in desc:
        draw_cloud(canvas, x, y)
    else:
        # Generic - just a circle
        canvas.circle(x + 12, y + 12, 10)

def main():
    canvas = EPDCanvas()

    try:
        # Load fonts
        font_large = load_font(28)
        font_medium = load_font(11)
        font_small = load_font(9)

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

            canvas.clear()

            # Header with city
            canvas.rectangle(0, 0, 121, 16)
            canvas.text(5, 2, weather['city'][:12], font=font_medium)

            # Current time
            now = datetime.now().strftime("%H:%M")
            canvas.text(90, 3, now, font=font_small)

            # Temperature
            temp_str = f"{weather['temp']}{weather['unit']}"
            canvas.text(10, 25, temp_str, font=font_large)

            # Weather icon
            draw_weather_icon(canvas, 85, 25, weather['description'])

            # Description
            canvas.text(10, 60, weather['description'][:16], font=font_medium)

            # Separator
            canvas.line(5, 80, 115, 80)

            # Details
            canvas.text(5, 90, f"Feels: {weather['feels_like']}", font=font_small)
            canvas.text(5, 105, f"Humidity: {weather['humidity']}%", font=font_small)
            canvas.text(5, 120, f"Wind: {weather['wind']} mph", font=font_small)

            # Updated time
            updated = datetime.now().strftime("%I:%M %p")
            canvas.text(5, 230, f"Updated: {updated}", font=font_small)

            canvas.display()
            canvas.sleep()
            time.sleep(UPDATE_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopping weather display...")
        canvas.clear()
        canvas.display()
        canvas.sleep()
    finally:
        canvas.cleanup()

if __name__ == "__main__":
    main()

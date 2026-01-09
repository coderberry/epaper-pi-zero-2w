#!/usr/bin/env python3
"""
Example 05: System Information Display
Shows CPU temperature, memory usage, disk space, and IP address.
Useful for headless Raspberry Pi monitoring.

Updates every 30 seconds. Press Ctrl+C to exit.
"""

from PIL import Image, ImageDraw, ImageFont
from epd_2inch13 import EPD_2Inch13, EPD_WIDTH, EPD_HEIGHT
import subprocess
import time
import os

def get_cpu_temp():
    """Get CPU temperature."""
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = float(f.read()) / 1000.0
        return f"{temp:.1f}C"
    except:
        return "N/A"

def get_memory_usage():
    """Get memory usage percentage."""
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
        total = int(lines[0].split()[1])
        available = int(lines[2].split()[1])
        used_percent = ((total - available) / total) * 100
        return f"{used_percent:.0f}%"
    except:
        return "N/A"

def get_disk_usage():
    """Get root partition disk usage."""
    try:
        stat = os.statvfs('/')
        total = stat.f_blocks * stat.f_frsize
        free = stat.f_bavail * stat.f_frsize
        used_percent = ((total - free) / total) * 100
        return f"{used_percent:.0f}%"
    except:
        return "N/A"

def get_ip_address():
    """Get primary IP address."""
    try:
        result = subprocess.run(
            ['hostname', '-I'],
            capture_output=True,
            text=True,
            timeout=5
        )
        ip = result.stdout.strip().split()[0]
        return ip if ip else "No IP"
    except:
        return "N/A"

def get_uptime():
    """Get system uptime."""
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.read().split()[0])
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        if days > 0:
            return f"{days}d {hours}h"
        else:
            return f"{hours}h {minutes}m"
    except:
        return "N/A"

def get_hostname():
    """Get system hostname."""
    try:
        result = subprocess.run(
            ['hostname'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip()
    except:
        return "Pi Zero"

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

def draw_progress_bar(draw, x, y, width, height, percent, label):
    """Draw a labeled progress bar."""
    # Label
    draw.text((x, y - 12), label, fill=0)
    # Border
    draw.rectangle((x, y, x + width, y + height), outline=0)
    # Fill
    fill_width = int((width - 2) * min(percent, 100) / 100)
    if fill_width > 0:
        draw.rectangle((x + 1, y + 1, x + 1 + fill_width, y + height - 1), fill=0)

def main():
    epd = EPD_2Inch13()

    try:
        # Load fonts
        try:
            font_title = ImageFont.truetype("MiSans-Light.ttf", 16)
            font_normal = ImageFont.truetype("MiSans-Light.ttf", 12)
            font_small = ImageFont.truetype("MiSans-Light.ttf", 10)
        except:
            font_title = ImageFont.load_default()
            font_normal = ImageFont.load_default()
            font_small = ImageFont.load_default()

        print("System monitor starting...")
        print("Updates every 30 seconds. Press Ctrl+C to stop.")

        while True:
            # Gather system info
            hostname = get_hostname()
            cpu_temp = get_cpu_temp()
            mem_usage = get_memory_usage()
            disk_usage = get_disk_usage()
            ip_addr = get_ip_address()
            uptime = get_uptime()

            # Parse percentages for bars
            try:
                mem_pct = float(mem_usage.replace('%', ''))
            except:
                mem_pct = 0
            try:
                disk_pct = float(disk_usage.replace('%', ''))
            except:
                disk_pct = 0

            print(f"CPU: {cpu_temp} | Mem: {mem_usage} | Disk: {disk_usage} | IP: {ip_addr}")

            # Create display image
            epd.hw_init_gui()
            image = Image.new('1', (EPD_HEIGHT, EPD_WIDTH), 255)
            draw = ImageDraw.Draw(image)

            # Title bar
            draw.rectangle((0, 0, EPD_HEIGHT, 18), fill=0)
            draw.text((5, 2), hostname, font=font_title, fill=255)
            draw.text((180, 4), uptime, font=font_small, fill=255)

            # System info
            y = 25
            draw.text((5, y), f"IP: {ip_addr}", font=font_normal, fill=0)

            y = 42
            draw.text((5, y), f"CPU Temp: {cpu_temp}", font=font_normal, fill=0)

            # Memory bar
            y = 62
            draw_progress_bar(draw, 5, y, 120, 10, mem_pct, f"Memory: {mem_usage}")

            # Disk bar
            y = 90
            draw_progress_bar(draw, 5, y, 120, 10, disk_pct, f"Disk: {disk_usage}")

            # Timestamp
            from datetime import datetime
            now = datetime.now().strftime("%H:%M:%S")
            draw.text((5, 108), f"Updated: {now}", font=font_small, fill=0)

            # Convert and display
            image = image.rotate(90, expand=True)
            img_bytes = image_to_bytes(image)
            epd.display(img_bytes)

            time.sleep(30)

    except KeyboardInterrupt:
        print("\nStopping monitor...")
        epd.hw_init()
        epd.whitescreen_white()
        epd.sleep()
    finally:
        epd.clean_gpio()

if __name__ == "__main__":
    main()

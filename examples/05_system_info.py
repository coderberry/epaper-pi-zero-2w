#!/usr/bin/env python3
"""
Example 05: System Information Display
Shows CPU temperature, memory usage, disk space, and IP address.
Useful for headless Raspberry Pi monitoring.

Updates every 30 seconds. Press Ctrl+C to exit.
"""

from epd_2inch13 import EPD_2Inch13
from epd_helper import create_canvas, pil_to_epd, load_font
import subprocess
import time
import os
from datetime import datetime

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
        return f"{used_percent:.0f}%", used_percent
    except:
        return "N/A", 0

def get_disk_usage():
    """Get root partition disk usage."""
    try:
        stat = os.statvfs('/')
        total = stat.f_blocks * stat.f_frsize
        free = stat.f_bavail * stat.f_frsize
        used_percent = ((total - free) / total) * 100
        return f"{used_percent:.0f}%", used_percent
    except:
        return "N/A", 0

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

def draw_progress_bar(draw, x, y, width, height, percent):
    """Draw a progress bar."""
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
        font_title = load_font(14)
        font_normal = load_font(12)
        font_small = load_font(10)

        print("System monitor starting...")
        print("Updates every 30 seconds. Press Ctrl+C to stop.")

        while True:
            # Gather system info
            hostname = get_hostname()
            cpu_temp = get_cpu_temp()
            mem_usage, mem_pct = get_memory_usage()
            disk_usage, disk_pct = get_disk_usage()
            ip_addr = get_ip_address()
            uptime = get_uptime()

            print(f"CPU: {cpu_temp} | Mem: {mem_usage} | Disk: {disk_usage} | IP: {ip_addr}")

            # Create display image
            epd.hw_init_gui()
            image, draw = create_canvas()

            # Title bar (inverted)
            draw.rectangle((0, 0, 121, 18), fill=0)
            draw.text((5, 2), hostname[:12], font=font_title, fill=255)
            draw.text((80, 4), uptime, font=font_small, fill=255)

            # IP Address
            y = 25
            draw.text((5, y), f"IP: {ip_addr}", font=font_normal, fill=0)

            # CPU Temperature
            y = 45
            draw.text((5, y), f"CPU: {cpu_temp}", font=font_normal, fill=0)

            # Memory
            y = 70
            draw.text((5, y), f"Mem: {mem_usage}", font=font_small, fill=0)
            draw_progress_bar(draw, 5, y + 14, 100, 8, mem_pct)

            # Disk
            y = 100
            draw.text((5, y), f"Disk: {disk_usage}", font=font_small, fill=0)
            draw_progress_bar(draw, 5, y + 14, 100, 8, disk_pct)

            # Timestamp
            now = datetime.now().strftime("%H:%M:%S")
            draw.text((5, 230), f"Updated: {now}", font=font_small, fill=0)

            # Convert and display
            img_bytes = pil_to_epd(image)
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

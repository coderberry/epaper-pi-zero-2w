#!/usr/bin/env python3
"""
Example 05: System Information Display
Shows CPU temperature, memory usage, disk space, and IP address.
Useful for headless Raspberry Pi monitoring.

Updates every 30 seconds. Press Ctrl+C to exit.
"""

from epd_helper import EPDCanvas, load_font
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

def draw_progress_bar(canvas, x, y, width, height, percent):
    """Draw a progress bar."""
    canvas.rectangle(x, y, x + width, y + height)
    fill_width = int((width - 2) * min(percent, 100) / 100)
    if fill_width > 0:
        canvas.rectangle(x + 1, y + 1, x + 1 + fill_width, y + height - 1, fill=True)

def main():
    canvas = EPDCanvas()

    try:
        # Load fonts
        font_title = load_font(12)
        font_normal = load_font(11)
        font_small = load_font(9)

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

            # Draw display
            canvas.clear()

            # Title bar (inverted - draw filled rect then white text via pixels)
            canvas.rectangle(0, 0, 121, 16, fill=True)

            # Since we can't draw white on black easily, just draw a border instead
            canvas.clear()
            canvas.rectangle(0, 0, 121, 18)
            canvas.text(5, 3, hostname[:10], font=font_title)
            canvas.text(85, 5, uptime, font=font_small)

            # IP Address
            canvas.text(5, 25, f"IP: {ip_addr}", font=font_normal)

            # CPU Temperature
            canvas.text(5, 45, f"CPU: {cpu_temp}", font=font_normal)

            # Memory
            canvas.text(5, 70, f"Memory: {mem_usage}", font=font_small)
            draw_progress_bar(canvas, 5, 85, 100, 8, mem_pct)

            # Disk
            canvas.text(5, 105, f"Disk: {disk_usage}", font=font_small)
            draw_progress_bar(canvas, 5, 120, 100, 8, disk_pct)

            # Timestamp
            now = datetime.now().strftime("%H:%M:%S")
            canvas.text(5, 230, f"Updated: {now}", font=font_small)

            canvas.display()
            time.sleep(30)

    except KeyboardInterrupt:
        print("\nStopping monitor...")
        canvas.clear()
        canvas.display()
        canvas.sleep()
    finally:
        canvas.cleanup()

if __name__ == "__main__":
    main()

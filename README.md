# e-Paper Display with Raspberry Pi Zero 2 W

This project demonstrates how to use a 2.13-inch e-Paper display from Seengreat with a Raspberry Pi Zero 2 W.

## Hardware

- Raspberry Pi Zero 2 W (Raspberry Pi OS, accessible via SSH)
- Seengreat 2.13" e-Paper display (122 x 250 pixels)

### Wiring (BCM GPIO)

| e-Paper | Raspberry Pi |
|---------|--------------|
| VCC     | 3.3V         |
| GND     | GND          |
| RST     | GPIO 17      |
| BUSY    | GPIO 24      |
| D/C     | GPIO 25      |
| MOSI    | MOSI         |
| CLK     | CLK          |
| CS      | CE0 (GPIO 8) |

## Quick Start

### Python

```bash
# Install dependencies
pip install spidev gpiozero numpy Pillow

# Run demo
cd demo_code/Raspberry-Pi_2.13_V2/python
python3 gui_demo.py
```

### C

```bash
# Requires lgpio library
cd demo_code/Raspberry-Pi_2.13_V2/c
make
./main
```

## Examples

The `examples/` directory contains simple, well-documented scripts:

| Script | Description |
|--------|-------------|
| `01_hello_world.py` | Basic text display |
| `02_shapes.py` | Drawing lines, rectangles, circles |
| `03_display_image.py` | Load and display images |
| `04_clock.py` | Digital clock with live updates |
| `05_system_info.py` | System monitoring (CPU, memory, disk) |
| `06_weather_template.py` | Weather display template |

```bash
cd examples
python3 01_hello_world.py
```

## Resources

- Wiki: https://seengreat.com/wiki/71/2-13inch-e-paper-display
- Demo code provided by seengreat.com: `./demo_code`
- Setup guide: `SETUP.md`

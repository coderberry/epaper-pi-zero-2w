# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project drives a 2.13-inch e-Paper display from Seengreat on a Raspberry Pi Zero 2 W. Demo code for both Python and C implementations are provided in `demo_code/Raspberry-Pi_2.13_V2/`.

Wiki: https://seengreat.com/wiki/71/2-13inch-e-paper-display

## Hardware Wiring (BCM GPIO)

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

## Display Specifications

- Resolution: 122 x 250 pixels
- Coordinate system for GUI functions: x-axis (0-122), y-axis (0-249)

## Running the Python Demo

```bash
cd demo_code/Raspberry-Pi_2.13_V2/python
python3 gui_demo.py
```

Dependencies: `spidev`, `gpiozero`, `numpy`, `Pillow`

## Building and Running the C Demo

```bash
cd demo_code/Raspberry-Pi_2.13_V2/c
make
./main
```

Requires the `lgpio` library.

## Architecture

### Python (`demo_code/Raspberry-Pi_2.13_V2/python/`)

- `epd_2inch13.py` - Low-level e-Paper driver class (`EPD_2Inch13`) handling SPI communication and display commands
- `epd_gui.py` - GUI helper class (`EPD_GUI`) with drawing primitives (points, lines, rectangles, circles, text)
- `gui_demo.py` - Demo application showing full refresh, partial refresh (clock), and drawing functions
- `image.py` - Pre-defined image data arrays for demos

### C (`demo_code/Raspberry-Pi_2.13_V2/c/`)

- `2inch13_epd.c/h` - e-Paper driver functions
- `epd_gui.c/h` - GUI drawing primitives
- `sg_lgpio.c/h` - GPIO abstraction using lgpio
- `fonts.h`, `font*.c` - Bitmap fonts (8, 12, 16, 20, 24pt)
- `Ap_213demo.h` - Demo image data
- `main.c` - Demo application

## Key Display Patterns

1. **Always call `sleep()` after refreshing** - The sleep instruction is mandatory to prevent display damage
2. **Re-initialize after wake** - Call `hw_init()` or equivalent after waking from sleep
3. **Partial refresh** - Use `setramvalue_basemap()` first, then `display_part()` for flicker-free updates
4. **Fast refresh** - Use `hw_init_fast()` and `whitescreen_all_fast()` for ~1.5s full refresh
5. **Standard refresh** - Full refresh takes ~2s and includes screen clearing (flicker is normal)

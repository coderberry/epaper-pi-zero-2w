# Examples

Example scripts demonstrating how to use the 2.13" e-Paper display.

## Setup

Before running examples, install the required dependencies:

```bash
sudo apt install python3-pip python3-spidev python3-gpiozero python3-numpy python3-pil
```

## Examples

| Script | Description |
|--------|-------------|
| `01_hello_world.py` | Basic text display |
| `02_shapes.py` | Drawing lines, rectangles, circles, polygons |
| `03_display_image.py` | Load and display BMP/PNG/JPG images |
| `04_clock.py` | Digital clock with live updates |
| `05_system_info.py` | CPU temp, memory, disk, IP monitoring |
| `06_weather_template.py` | Weather display (with OpenWeatherMap API) |

## Running

```bash
cd examples
python3 01_hello_world.py
```

## Key Concepts

### Display Orientation
- Physical display: 122 x 250 pixels
- For landscape mode, create images as 250 x 122, then rotate 90°

### Refresh Modes
- **Full refresh** (`hw_init()` + `display()`): ~2 seconds, clears ghosting, screen flickers
- **Fast refresh** (`hw_init_fast()` + `whitescreen_all_fast()`): ~1.5 seconds, less flicker
- **Partial refresh**: Updates only part of the screen, no flicker, but can cause ghosting over time

### Using the Helper Module

The `epd_helper.py` module simplifies image creation and conversion:

```python
from epd_2inch13 import EPD_2Inch13
from epd_helper import create_canvas, pil_to_epd, load_font

epd = EPD_2Inch13()
epd.hw_init_gui()

# Create a canvas (122x250 pixels, white background)
image, draw = create_canvas()

# Draw on it
font = load_font(16)
draw.text((10, 10), "Hello", font=font, fill=0)  # fill=0 is black
draw.rectangle((10, 40, 100, 80), outline=0)

# Convert and display
img_bytes = pil_to_epd(image)
epd.display(img_bytes)
epd.sleep()
```

### Always Sleep After Display
The e-paper display must be put to sleep after updating to prevent damage:

```python
epd.display(img_bytes)
epd.sleep()  # Required!
```

### Colors
- `0` = Black
- `255` = White

This is a monochrome display - no grayscale or colors.

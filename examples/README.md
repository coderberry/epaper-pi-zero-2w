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
| `02_shapes.py` | Drawing lines, rectangles, circles |
| `03_display_image.py` | Load and display BMP/PNG/JPG images |
| `04_clock.py` | Digital clock with live updates |
| `05_system_info.py` | CPU temp, memory, disk, IP monitoring |
| `06_weather_template.py` | Weather display (with OpenWeatherMap API) |

## Running

```bash
cd examples
python3 01_hello_world.py
```

## Using the EPDCanvas Class

The `epd_helper.py` module provides an `EPDCanvas` class that wraps the display driver:

```python
from epd_helper import EPDCanvas, load_font

# Create canvas
canvas = EPDCanvas()

# Clear to white
canvas.clear()

# Draw shapes
canvas.line(10, 10, 100, 10)           # Line
canvas.rectangle(10, 20, 50, 50)       # Rectangle outline
canvas.rectangle(60, 20, 100, 50, fill=True)  # Filled rectangle
canvas.circle(30, 80, 15)              # Circle outline
canvas.circle(80, 80, 15, fill=True)   # Filled circle

# Draw text
font = load_font(16)
canvas.text(10, 110, "Hello!", font=font)

# Send to display
canvas.display()

# Put display to sleep (required!)
canvas.sleep()

# Clean up GPIO
canvas.cleanup()
```

## Key Concepts

### Display Dimensions
- Width: 122 pixels (x: 0-121)
- Height: 250 pixels (y: 0-249)

### Refresh Modes
- `canvas.display()`: Full refresh (~2 seconds), clears ghosting, screen flickers
- `canvas.display_fast()`: Fast refresh (~1.5 seconds), less flicker, may cause ghosting

### Always Sleep After Display
The e-paper display must be put to sleep after updating to prevent damage:

```python
canvas.display()
canvas.sleep()  # Required!
```

### Colors
- Black pixels are drawn by default
- Use `canvas.clear()` to fill with white
- This is a monochrome display - no grayscale

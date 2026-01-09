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

### Image Conversion
```python
# Create image with PIL
image = Image.new('1', (250, 122), 255)  # 1-bit, white background
draw = ImageDraw.Draw(image)
draw.text((10, 10), "Hello", fill=0)     # fill=0 is black

# Rotate for display orientation
image = image.rotate(90, expand=True)

# Convert to bytes
pixels = list(image.getdata())
img_bytes = []
for i in range(0, len(pixels), 8):
    byte = 0
    for j in range(8):
        if i + j < len(pixels) and pixels[i + j] == 0:
            byte |= (0x80 >> j)
    img_bytes.append(byte ^ 0xFF)

# Display
epd.display(img_bytes)
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

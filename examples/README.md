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

## HTTP Server (display_server.py)

The HTTP server allows you to update the display remotely via HTTP POST requests. The display runs in **landscape mode** (250 wide x 122 tall) with text automatically centered and wrapped.

### Starting the Server

**Manual mode:**
```bash
cd examples
python3 display_server.py

# Or with custom port/bind address:
python3 display_server.py --port 8080 --bind 0.0.0.0
```

**As systemd service (auto-start on boot):**
```bash
cd systemd
sudo ./install.sh

# View logs:
journalctl -u display-server -f

# Stop service:
sudo systemctl stop display-server

# Uninstall:
sudo ./uninstall.sh
```

### API Endpoints

#### POST /display
Update the display with centered, wrapped text.

**Request:**
```bash
curl -X POST http://localhost:8080/display \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from HTTP!"}'
```

**Request body (JSON):**
```json
{
  "text": "Your message here",
  "font_size": 24,
  "clear_first": true,
  "fast_refresh": false
}
```

**Parameters:**
- `text` (string, required): Text to display
- `font_size` (int, optional, default 24): Font size (8-48)
- `clear_first` (bool, optional, default true): Clear before rendering
- `fast_refresh` (bool, optional, default false): Use fast refresh (~1.5s vs ~2s)

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Display updated",
  "lines": 3,
  "truncated": false,
  "fast_refresh": false
}
```

#### GET /status
Health check endpoint.

```bash
curl http://localhost:8080/status
```

**Response:**
```json
{
  "status": "ok",
  "uptime": 3600,
  "last_update": "2024-01-15T10:30:00"
}
```

#### GET /clear
Clear the display.

```bash
curl http://localhost:8080/clear
```

### Examples

**Simple text:**
```bash
curl -X POST http://localhost:8080/display \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World!"}'
```

**Long text (auto-wraps):**
```bash
curl -X POST http://localhost:8080/display \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a longer message that will automatically wrap across multiple lines and be centered on the display."}'
```

**Custom font size:**
```bash
curl -X POST http://localhost:8080/display \
  -H "Content-Type: application/json" \
  -d '{"text": "Large Text", "font_size": 32}'
```

**Fast refresh:**
```bash
curl -X POST http://localhost:8080/display \
  -H "Content-Type: application/json" \
  -d '{"text": "Quick update", "fast_refresh": true}'
```

### Landscape Mode

The HTTP server uses **landscape orientation** (250x122 pixels):
- Text is automatically centered both horizontally and vertically
- Word wrapping happens automatically
- Long text is truncated with "..." after 8 lines

### Files

- `display_server.py` - HTTP server implementation
- `landscape_helper.py` - Landscape mode canvas with text centering
- `systemd/display-server.service` - Systemd service file
- `systemd/install.sh` - Install as service
- `systemd/uninstall.sh` - Uninstall service

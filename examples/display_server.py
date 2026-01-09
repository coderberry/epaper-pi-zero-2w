#!/usr/bin/env python3
"""
HTTP server for e-paper display.
Accepts JSON POST requests to update display with centered, wrapped text in landscape mode.

Usage:
    python3 display_server.py [--port 8080] [--bind 0.0.0.0]

API Endpoints:
    POST /display - Update display with text
        Body: {"text": "Hello", "font_size": 24, "clear_first": true, "fast_refresh": false}

    GET /status - Server health check
        Returns: {"status": "ok", "uptime": seconds, "last_update": timestamp}

    GET /clear - Clear display
        Returns: {"status": "success", "message": "Display cleared"}
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import signal
import sys
import argparse
import time
from datetime import datetime
import logging

from landscape_helper import LandscapeEPDCanvas

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DisplayHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for e-paper display updates."""

    # Shared canvas instance (initialized in main())
    canvas = None
    canvas_lock = threading.Lock()
    start_time = None
    last_update = None

    def log_message(self, format, *args):
        """Override to use logging module."""
        logger.info("%s - %s" % (self.address_string(), format % args))

    def send_json_response(self, status_code, data):
        """Send JSON response with proper headers."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/display':
            self.handle_display_update()
        else:
            self.send_json_response(404, {
                "status": "error",
                "message": f"Endpoint not found: {self.path}"
            })

    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/status':
            self.handle_status()
        elif self.path == '/clear':
            self.handle_clear()
        else:
            self.send_json_response(404, {
                "status": "error",
                "message": f"Endpoint not found: {self.path}"
            })

    def handle_display_update(self):
        """Handle POST /display - Update display with text."""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_json_response(400, {
                    "status": "error",
                    "message": "Empty request body"
                })
                return

            body = self.rfile.read(content_length).decode('utf-8')

            # Parse JSON
            try:
                data = json.loads(body)
            except json.JSONDecodeError as e:
                self.send_json_response(400, {
                    "status": "error",
                    "message": f"Invalid JSON: {str(e)}"
                })
                return

            # Validate required field
            if 'text' not in data:
                self.send_json_response(400, {
                    "status": "error",
                    "message": "Missing required field: 'text'"
                })
                return

            # Extract parameters
            text = data['text']
            font_size = data.get('font_size', 24)
            clear_first = data.get('clear_first', True)
            fast_refresh = data.get('fast_refresh', False)

            # Validate parameters
            if not isinstance(text, str):
                self.send_json_response(400, {
                    "status": "error",
                    "message": "'text' must be a string"
                })
                return

            if not isinstance(font_size, int) or font_size < 8 or font_size > 48:
                self.send_json_response(400, {
                    "status": "error",
                    "message": "'font_size' must be an integer between 8 and 48"
                })
                return

            # Acquire lock for thread safety
            with self.canvas_lock:
                try:
                    # Clear display if requested
                    if clear_first:
                        self.canvas.clear()

                    # Render centered text
                    result = self.canvas.render_centered_text(
                        text=text,
                        font_size=font_size
                    )

                    # Update display
                    if fast_refresh:
                        self.canvas.display_fast()
                    else:
                        self.canvas.display()

                    # Update last_update timestamp
                    DisplayHTTPHandler.last_update = datetime.now().isoformat()

                    # Send success response with metadata
                    self.send_json_response(200, {
                        "status": "success",
                        "message": "Display updated",
                        "lines": result["lines"],
                        "truncated": result["truncated"],
                        "fast_refresh": fast_refresh
                    })

                    logger.info(f"Display updated: {result['lines']} lines, "
                               f"truncated={result['truncated']}, "
                               f"fast_refresh={fast_refresh}")

                except Exception as e:
                    logger.error(f"Display update failed: {str(e)}", exc_info=True)
                    self.send_json_response(500, {
                        "status": "error",
                        "message": f"Display error: {str(e)}"
                    })

        except Exception as e:
            logger.error(f"Request handling failed: {str(e)}", exc_info=True)
            self.send_json_response(500, {
                "status": "error",
                "message": f"Server error: {str(e)}"
            })

    def handle_status(self):
        """Handle GET /status - Return server status."""
        uptime = int(time.time() - self.start_time) if self.start_time else 0

        self.send_json_response(200, {
            "status": "ok",
            "uptime": uptime,
            "last_update": self.last_update
        })

    def handle_clear(self):
        """Handle GET /clear - Clear the display."""
        try:
            with self.canvas_lock:
                self.canvas.clear()
                self.canvas.display()

                DisplayHTTPHandler.last_update = datetime.now().isoformat()

                self.send_json_response(200, {
                    "status": "success",
                    "message": "Display cleared"
                })

                logger.info("Display cleared")

        except Exception as e:
            logger.error(f"Clear failed: {str(e)}", exc_info=True)
            self.send_json_response(500, {
                "status": "error",
                "message": f"Display error: {str(e)}"
            })


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, shutting down gracefully...")

    # Clean up display
    if DisplayHTTPHandler.canvas:
        try:
            logger.info("Clearing display and putting to sleep...")
            DisplayHTTPHandler.canvas.clear()
            DisplayHTTPHandler.canvas.display()
            DisplayHTTPHandler.canvas.sleep()
            DisplayHTTPHandler.canvas.cleanup()
            logger.info("Display cleanup complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    sys.exit(0)


def main():
    """Start the HTTP server."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='e-Paper Display HTTP Server')
    parser.add_argument('--port', type=int, default=8080,
                       help='Port to bind to (default: 8080)')
    parser.add_argument('--bind', type=str, default='0.0.0.0',
                       help='Address to bind to (default: 0.0.0.0)')
    args = parser.parse_args()

    try:
        # Initialize display canvas
        logger.info("Initializing e-paper display in landscape mode...")
        canvas = LandscapeEPDCanvas()

        # Clear display to known state
        logger.info("Clearing display...")
        canvas.clear()
        canvas.display()

        # Set canvas on handler class
        DisplayHTTPHandler.canvas = canvas
        DisplayHTTPHandler.start_time = time.time()

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Create and start server
        server = HTTPServer((args.bind, args.port), DisplayHTTPHandler)
        logger.info(f"Server started on {args.bind}:{args.port}")
        logger.info("Press Ctrl+C to stop")

        # Serve forever
        server.serve_forever()

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received, shutting down...")
        signal_handler(signal.SIGINT, None)

    except Exception as e:
        logger.error(f"Server failed to start: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

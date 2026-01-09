#!/usr/bin/env python3
"""
Flask-based HTTP server for e-paper display.
Provides both a web UI and JSON API for updating display with text.

Usage:
    python3 display_server.py [--port 8080] [--bind 0.0.0.0]

Web UI:
    GET / - HTML form for display configuration

API Endpoints:
    POST /api/display - Update display with text
        Body: {"text": "Hello", "font_size": 24, "align_h": "center", "align_v": "middle",
               "clear_first": true, "fast_refresh": false}

    GET /status - Server health check
        Returns: {"status": "ok", "uptime": seconds, "last_update": timestamp}

    GET /clear - Clear display
        Returns: {"status": "success", "message": "Display cleared"}
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for
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

# Create Flask app
app = Flask(__name__)

# Shared state (global)
canvas = None
canvas_lock = threading.Lock()
start_time = None
last_update = None


def update_display(text, font_size, align_h, align_v, clear_first, fast_refresh):
    """
    Shared logic for updating display from both web form and API.
    Thread-safe with canvas_lock.

    Args:
        text: Text to display
        font_size: Font size (8-48)
        align_h: Horizontal alignment ('left', 'center', 'right')
        align_v: Vertical alignment ('top', 'middle', 'bottom')
        clear_first: Clear display before rendering
        fast_refresh: Use fast refresh mode

    Returns:
        dict: Metadata about rendering (lines, truncated, etc.)
    """
    global canvas, canvas_lock, last_update

    with canvas_lock:
        # Clear display if requested
        if clear_first:
            canvas.clear()

        # Render text with alignment
        result = canvas.render_text(
            text=text,
            font_size=font_size,
            align_h=align_h,
            align_v=align_v
        )

        # Update display
        if fast_refresh:
            canvas.display_fast()
        else:
            canvas.display()

        # Update timestamp
        last_update = datetime.now().isoformat()

        # Log update
        logger.info(f"Display updated: {result['lines']} lines, "
                   f"align={align_h}/{align_v}, "
                   f"truncated={result['truncated']}, "
                   f"fast_refresh={fast_refresh}")

        return {
            "lines": result["lines"],
            "truncated": result["truncated"],
            "fast_refresh": fast_refresh
        }


@app.route('/', methods=['GET'])
def index():
    """Render web UI form."""
    return render_template('index.html')


@app.route('/display', methods=['POST'])
def handle_form_submission():
    """Handle web form submission."""
    try:
        # Extract form data
        text = request.form.get('text', '').strip()
        font_size = int(request.form.get('font_size', 24))
        align_h = request.form.get('align_h', 'center')
        align_v = request.form.get('align_v', 'middle')
        clear_first = request.form.get('clear_first') == 'true'
        fast_refresh = request.form.get('fast_refresh') == 'true'

        # Validate text
        if not text:
            return render_template('index.html',
                                 status='Text is required',
                                 status_type='error',
                                 text=text,
                                 font_size=font_size,
                                 align_h=align_h,
                                 align_v=align_v,
                                 clear_first=clear_first,
                                 fast_refresh=fast_refresh)

        # Validate font size
        if font_size < 8 or font_size > 48:
            return render_template('index.html',
                                 status='Font size must be between 8 and 48',
                                 status_type='error',
                                 text=text,
                                 font_size=font_size,
                                 align_h=align_h,
                                 align_v=align_v,
                                 clear_first=clear_first,
                                 fast_refresh=fast_refresh)

        # Update display
        result = update_display(text, font_size, align_h, align_v,
                               clear_first, fast_refresh)

        # Render success
        return render_template('index.html',
                             status='Display updated successfully!',
                             status_type='success',
                             text=text,
                             font_size=font_size,
                             align_h=align_h,
                             align_v=align_v,
                             clear_first=clear_first,
                             fast_refresh=fast_refresh,
                             metadata=result)

    except ValueError as e:
        logger.error(f"Form validation error: {e}", exc_info=True)
        return render_template('index.html',
                             status=f'Invalid input: {str(e)}',
                             status_type='error',
                             text=request.form.get('text', ''))

    except Exception as e:
        logger.error(f"Form submission error: {e}", exc_info=True)
        return render_template('index.html',
                             status=f'Error: {str(e)}',
                             status_type='error',
                             text=request.form.get('text', ''))


@app.route('/api/display', methods=['POST'])
def handle_api_display():
    """Handle JSON API requests (backward compatible)."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "Empty request body"
            }), 400

        # Validate required field
        if 'text' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing required field: 'text'"
            }), 400

        # Extract parameters (backward compatible defaults)
        text = data['text']
        font_size = data.get('font_size', 24)
        clear_first = data.get('clear_first', True)
        fast_refresh = data.get('fast_refresh', False)

        # NEW: Support alignment in API (optional, default to center/middle)
        align_h = data.get('align_h', 'center')
        align_v = data.get('align_v', 'middle')

        # Validate parameters
        if not isinstance(text, str):
            return jsonify({
                "status": "error",
                "message": "'text' must be a string"
            }), 400

        if not isinstance(font_size, int) or font_size < 8 or font_size > 48:
            return jsonify({
                "status": "error",
                "message": "'font_size' must be an integer between 8 and 48"
            }), 400

        # Validate alignment parameters
        if align_h not in ('left', 'center', 'right'):
            return jsonify({
                "status": "error",
                "message": "'align_h' must be 'left', 'center', or 'right'"
            }), 400

        if align_v not in ('top', 'middle', 'bottom'):
            return jsonify({
                "status": "error",
                "message": "'align_v' must be 'top', 'middle', or 'bottom'"
            }), 400

        # Update display
        result = update_display(text, font_size, align_h, align_v,
                               clear_first, fast_refresh)

        # Return JSON response
        return jsonify({
            "status": "success",
            "message": "Display updated",
            "lines": result["lines"],
            "truncated": result["truncated"],
            "fast_refresh": fast_refresh
        }), 200

    except Exception as e:
        logger.error(f"API error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }), 500


@app.route('/status', methods=['GET'])
def handle_status():
    """Return server status."""
    global start_time, last_update

    uptime = int(time.time() - start_time) if start_time else 0

    return jsonify({
        "status": "ok",
        "uptime": uptime,
        "last_update": last_update
    })


@app.route('/clear', methods=['GET'])
def handle_clear():
    """Clear the display."""
    global canvas, canvas_lock, last_update

    try:
        with canvas_lock:
            canvas.clear()
            canvas.display()
            last_update = datetime.now().isoformat()

        logger.info("Display cleared")

        # Return JSON for API clients, or redirect for browser
        if request.headers.get('Accept', '').startswith('application/json'):
            return jsonify({
                "status": "success",
                "message": "Display cleared"
            })
        else:
            return redirect(url_for('index'))

    except Exception as e:
        logger.error(f"Clear failed: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": f"Display error: {str(e)}"
        }), 500


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global canvas

    logger.info(f"Received signal {signum}, shutting down gracefully...")

    # Clean up display
    if canvas:
        try:
            logger.info("Clearing display and putting to sleep...")
            canvas.clear()
            canvas.display()
            canvas.sleep()
            canvas.cleanup()
            logger.info("Display cleanup complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    sys.exit(0)


def main():
    """Start the Flask server."""
    global canvas, start_time

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

        # Set start time
        start_time = time.time()

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start Flask server
        logger.info(f"Server starting on {args.bind}:{args.port}")
        logger.info(f"Web UI: http://{args.bind}:{args.port}/")
        logger.info("Press Ctrl+C to stop")

        # Run Flask app
        app.run(host=args.bind, port=args.port, debug=False, threaded=True)

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received, shutting down...")
        signal_handler(signal.SIGINT, None)

    except Exception as e:
        logger.error(f"Server failed to start: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

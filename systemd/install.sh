#!/bin/bash
#
# Install e-Paper Display HTTP Server as systemd service
#
# Usage: sudo ./install.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}e-Paper Display HTTP Server - Installation${NC}"
echo "=============================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root (use sudo)${NC}"
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SERVICE_FILE="${SCRIPT_DIR}/display-server.service"

# Check if service file exists
if [ ! -f "$SERVICE_FILE" ]; then
    echo -e "${RED}Error: Service file not found: ${SERVICE_FILE}${NC}"
    exit 1
fi

# Check if Python script exists
PYTHON_SCRIPT="/home/pi/Code/epaper-pi-zero-2w/examples/display_server.py"
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${YELLOW}Warning: Python script not found at expected location:${NC}"
    echo "  $PYTHON_SCRIPT"
    echo ""
    echo "Please update the WorkingDirectory and ExecStart paths in:"
    echo "  ${SERVICE_FILE}"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Stop service if it's already running
if systemctl is-active --quiet display-server.service; then
    echo "Stopping existing service..."
    systemctl stop display-server.service
fi

# Copy service file to systemd directory
echo "Installing service file..."
cp "$SERVICE_FILE" /etc/systemd/system/display-server.service

# Reload systemd daemon
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable service (start on boot)
echo "Enabling service to start on boot..."
systemctl enable display-server.service

# Start service
echo "Starting service..."
systemctl start display-server.service

# Wait a moment for service to start
sleep 2

# Check service status
echo ""
echo "=============================================="
if systemctl is-active --quiet display-server.service; then
    echo -e "${GREEN}✓ Service installed and started successfully!${NC}"
    echo ""
    echo "Service status:"
    systemctl status display-server.service --no-pager -l
    echo ""
    echo "View logs with:"
    echo "  journalctl -u display-server.service -f"
    echo ""
    echo "Test with:"
    echo "  curl -X POST http://localhost:8080/display -H 'Content-Type: application/json' -d '{\"text\": \"Hello from systemd!\"}'"
else
    echo -e "${RED}✗ Service failed to start${NC}"
    echo ""
    echo "Check logs with:"
    echo "  journalctl -u display-server.service -n 50"
    exit 1
fi

echo ""
echo -e "${GREEN}Installation complete!${NC}"

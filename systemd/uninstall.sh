#!/bin/bash
#
# Uninstall e-Paper Display HTTP Server systemd service
#
# Usage: sudo ./uninstall.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}e-Paper Display HTTP Server - Uninstallation${NC}"
echo "=============================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root (use sudo)${NC}"
    exit 1
fi

SERVICE_FILE="/etc/systemd/system/display-server.service"

# Check if service exists
if [ ! -f "$SERVICE_FILE" ]; then
    echo -e "${YELLOW}Service file not found: ${SERVICE_FILE}${NC}"
    echo "Service may not be installed."
    exit 0
fi

# Stop service if running
if systemctl is-active --quiet display-server.service; then
    echo "Stopping service..."
    systemctl stop display-server.service
else
    echo "Service is not running"
fi

# Disable service (remove from boot)
if systemctl is-enabled --quiet display-server.service 2>/dev/null; then
    echo "Disabling service..."
    systemctl disable display-server.service
else
    echo "Service is not enabled"
fi

# Remove service file
echo "Removing service file..."
rm -f "$SERVICE_FILE"

# Reload systemd daemon
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Reset failed state if any
systemctl reset-failed display-server.service 2>/dev/null || true

echo ""
echo -e "${GREEN}✓ Service uninstalled successfully!${NC}"
echo ""
echo "The Python scripts in examples/ have been left intact."
echo "Remove them manually if desired."

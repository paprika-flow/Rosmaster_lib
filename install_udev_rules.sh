#!/bin/bash
# ──────────────────────────────────────────────────────────────
# Install udev rules for Rosmaster robot USB devices.
# Run ONCE per robot:
#   bash install_udev_rules.sh
# ──────────────────────────────────────────────────────────────

set -e

RULES_FILE="rosmaster.rules"
RULES_DEST="/etc/udev/rules.d/rosmaster.rules"

# Must be root
if [ "$(whoami)" != "root" ]; then
    echo "Please run with sudo:"
    echo "  sudo bash install_udev_rules.sh"
    exit 1
fi

# Check if rules file exists next to the script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RULES_SRC="$SCRIPT_DIR/$RULES_FILE"

if [ ! -f "$RULES_SRC" ]; then
    echo "Error: $RULES_FILE not found in $SCRIPT_DIR"
    exit 1
fi

# Install rules
echo "Installing udev rules..."
cp "$RULES_SRC" "$RULES_DEST"
chmod 644 "$RULES_DEST"
echo "  -> $RULES_DEST"

# Reload and trigger
echo "Reloading udev rules..."
udevadm control --reload-rules
udevadm trigger

echo ""
echo "Done! Devices should now be accessible as:"
echo "  /dev/astra*      — Orbbec depth camera"
echo "  /dev/rplidar     — RPLidar"
echo "  /dev/rosmaster   — Motor board (if using USB)"
echo ""
echo "Verify with: ls -la /dev/astra* /dev/rplidar /dev/rosmaster"

# ── Help: find your USB device IDs ───────────────────────────
echo ""
echo "---"
echo "If /dev/rplidar didn't appear, find your lidar's USB IDs:"
echo "  1. Unplug the lidar"
echo "  2. Run: ls /dev/ttyUSB*"
echo "  3. Plug it back in"
echo "  4. Run: ls /dev/ttyUSB*  (note the new one)"
echo "  5. Run: udevadm info -a -n /dev/ttyUSB0  | grep -i 'idVendor\\|idProduct'"
echo "  6. Edit rosmaster.rules with the correct IDs, then run this script again"

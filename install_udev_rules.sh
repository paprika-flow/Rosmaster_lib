#!/bin/bash
# ──────────────────────────────────────────────────────────────
# Install udev rules for Rosmaster robot USB devices.
#   bash install_udev_rules.sh
# ──────────────────────────────────────────────────────────────

set -e

RULES_FILE="99-rosmaster.rules"
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
echo "Devices should now be accessible as:"
echo "  /dev/astra*      — Orbbec depth camera"
echo "  /dev/rplidar     — RPLidar"
echo "  /dev/rosmaster_driver   — Motor board (if using USB)"
echo ""
echo "Verification (names should point to a real device):"
echo ""
ls -la /dev/astra /dev/astra_rgb /dev/rplidar /dev/rosmaster_driver



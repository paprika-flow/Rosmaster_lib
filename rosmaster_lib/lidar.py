"""
RPLidar A1 driver for the rosmaster_lib package.

Basic usage:
    from rosmaster_lib import Lidar

    # Auto-detect port (recommended):
    with Lidar() as lidar:
        for scan in lidar.iter_scans():
            ...

    # Or specify a port explicitly:
    with Lidar(port="/dev/ttyUSB0") as lidar:
        ...
"""

import os
import time

from rplidar import RPLidar, RPLidarException

UDEV_SYMLINKS = ["/dev/rplidar"]


class Lidar:
    """High-level wrapper around RPLidar for the rosmaster_lib package.

    Port detection order:
      1. Try known udev symlinks (/dev/rplidar)
      2. Scan all /dev/ttyUSB* / /dev/ttyACM* ports

    Parameters
    ----------
    port : str
        Serial port path like "/dev/ttyUSB0".
        Use "auto" (default) for automatic detection.
    baudrate : int
        Baud rate (115200 for A1, 256000 for A2M7/A3).
    timeout : float
        Serial read timeout in seconds.
    """

    def __init__(self, port="auto", baudrate=115200, timeout=1):
        self._port_arg = port
        self._resolved_port = None
        self.baudrate = baudrate
        self.timeout = timeout
        self._lidar = None
        self._motor_on = False

    def connect(self):
        """Open connection to the RPLidar.

        Detects the port automatically if not already specified.
        """
        if self._lidar:
            return

        if self._port_arg == "auto":
            self._resolved_port = self._find_port()
        else:
            self._resolved_port = self._port_arg

        if self._resolved_port is None:
            raise RPLidarException(
                "No RPLidar found. "
                "Install udev rules: sudo bash install_udev_rules.sh"
            )

        self._lidar = RPLidar(self._resolved_port, self.baudrate, self.timeout)
        print(f"[Lidar] Connected on {self._resolved_port}")

    def disconnect(self):
        """Close connection and stop motor."""
        if self._lidar:
            try:
                self._lidar.stop_motor()
                self._lidar.stop()
                self._lidar.disconnect()
            except Exception:
                pass
            self._lidar = None
            self._motor_on = False

    @property
    def is_connected(self):
        return self._lidar is not None

    @property
    def port(self):
        """The resolved port path, or None if not connected."""
        return self._resolved_port

    @staticmethod
    def _find_port():
        """Try udev symlinks first, then fall back to port scanning."""
        # 1. Check udev symlinks
        for symlink in UDEV_SYMLINKS:
            if os.path.exists(symlink):
                print(f"[Lidar] Found {symlink} (udev)")
                return symlink

        # 2. Fall back to scanning
        print("[Lidar] No udev symlink found, scanning ports...")
        from .port_finder import find_lidar_port
        return find_lidar_port()

    def start_motor(self):
        """Start the lidar motor. Waits 2s for spin-up."""
        if not self._lidar:
            raise RPLidarException("Not connected")
        self._lidar.start_motor()
        self._motor_on = True
        time.sleep(2)

    def stop_motor(self):
        """Stop the lidar motor."""
        if self._lidar:
            self._lidar.stop_motor()
            self._motor_on = False

    def get_info(self):
        """Get device info dict (model, firmware, hardware, serial)."""
        if not self._lidar:
            raise RPLidarException("Not connected")
        return self._lidar.get_info()

    def get_health(self):
        """Get (status_string, error_code)."""
        if not self._lidar:
            raise RPLidarException("Not connected")
        return self._lidar.get_health()

    def clean_input(self):
        """Flush the serial input buffer."""
        if self._lidar:
            self._lidar.clean_input()

    def stop(self):
        """Stop scanning."""
        if self._lidar:
            self._lidar.stop()

    def reset(self):
        """Hardware reset of the lidar."""
        if self._lidar:
            self._lidar.reset()
            self._motor_on = False

    def iter_measures(self, scan_type='normal', max_buf_meas=3000):
        """Yield individual (new_scan, quality, angle, distance) tuples."""
        if not self._lidar:
            raise RPLidarException("Not connected")
        if not self._motor_on:
            self.start_motor()
        yield from self._lidar.iter_measures(scan_type, max_buf_meas)

    def iter_scans(self, scan_type='normal', max_buf_meas=3000, min_len=5):
        """Yield complete 360-degree scans as lists of (quality, angle, distance).

        Only includes valid points (distance > 0).
        """
        if not self._lidar:
            raise RPLidarException("Not connected")
        if not self._motor_on:
            self.start_motor()
        yield from self._lidar.iter_scans(scan_type, max_buf_meas, min_len)

    def get_single_scan(self, scan_type='normal', timeout=5):
        """Get one complete 360-degree scan."""
        for scan in self.iter_scans(scan_type):
            return scan
        return []


    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.disconnect()

    def __del__(self):
        self.disconnect()

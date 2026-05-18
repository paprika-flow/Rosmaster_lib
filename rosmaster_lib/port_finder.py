"""
Serial port fallback detection for Rosmaster robot components.

This is used when udev symlinks are not available.
Scans /dev/ttyUSB*, /dev/ttyACM*, /dev/ttyTHS* and tries
to identify devices by their protocol response.

Usage:
    from rosmaster_lib import port_finder

    port = port_finder.find_lidar_port()       # scan for lidar
    port = port_finder.find_chassis_port()     # scan for motor board
    all  = port_finder.find_ports()            # scan for both
"""

import glob
import time
import logging

logger = logging.getLogger('rosmaster_lib.port_finder')


def list_serial_ports():
    """List all available serial port device paths.

    Returns
    -------
    list of str : Sorted port paths like /dev/ttyUSB0, /dev/ttyTHS1, etc.
    """
    patterns = [
        '/dev/ttyUSB*',
        '/dev/ttyACM*',
        '/dev/ttyTHS*',
        '/dev/ttyAMA*',
    ]
    ports = []
    for pattern in patterns:
        ports.extend(glob.glob(pattern))
    return sorted(set(ports))


def find_lidar_port(ports=None, timeout=1):
    """Try to identify which port has the RPLidar connected.

    Sends the RPLidar GET_INFO command (0xA5 0x50) on each port
    and checks for a valid response header (0xA5 0x5A).

    Parameters
    ----------
    ports : list of str, optional
        Ports to check. If None, scans all available.
    timeout : float
        Timeout per port probe in seconds.

    Returns
    -------
    str or None : The port path if found, None otherwise.
    """
    if ports is None:
        ports = list_serial_ports()

    import serial

    for port in ports:
        try:
            ser = serial.Serial(port, 115200, timeout=timeout)
            time.sleep(0.1)
            ser.reset_input_buffer()

            ser.write(b'\xA5\x50')  # RPLidar GET_INFO
            time.sleep(0.2)

            desc = ser.read(7)
            ser.close()

            if len(desc) >= 2 and desc[0] == 0xA5 and desc[1] == 0x5A:
                logger.info("Found RPLidar on %s", port)
                return port
            logger.debug("No RPLidar response on %s", port)

        except (serial.SerialException, OSError) as e:
            logger.debug("Could not open %s: %s", port, e)
            continue

    logger.warning("No RPLidar found among: %s", ports)
    return None


def find_chassis_port(ports=None, timeout=1):
    """Try to identify the Rosmaster motor board port.

    Prefers /dev/ttyTHS1 (Jetson hardware UART), then scans
    remaining USB/ACM ports.

    Parameters
    ----------
    ports : list of str, optional
        Ports to check.
    timeout : float
        Timeout per port probe.

    Returns
    -------
    str or None : The port path if found.
    """
    if ports is None:
        ports = list_serial_ports()

    # Prefer the hardware UART on Jetson Nano
    preferred = ['/dev/ttyTHS1', '/dev/ttyAMA0']
    for pref in preferred:
        if pref in ports:
            logger.info("Found chassis on %s (preferred UART)", pref)
            return pref

    import serial

    for port in ports:
        try:
            ser = serial.Serial(port, 115200, timeout=timeout)
            time.sleep(0.1)
            ser.close()
            logger.info("Found chassis on %s (USB serial)", port)
            return port
        except (serial.SerialException, OSError):
            continue

    logger.warning("No chassis port found among: %s", ports)
    return None


def find_ports(lidar_timeout=1, chassis_timeout=1):
    """Find all robot component ports.

    Returns
    -------
    dict with keys 'lidar' and 'chassis'.
    Values are port path strings, or None if not found.
    """
    all_ports = list_serial_ports()
    logger.info("Available serial ports: %s", all_ports)

    lidar_port = find_lidar_port(all_ports, timeout=lidar_timeout)
    remaining = [p for p in all_ports if p != lidar_port]
    chassis_port = find_chassis_port(remaining, timeout=chassis_timeout)

    return {'lidar': lidar_port, 'chassis': chassis_port}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(find_ports())

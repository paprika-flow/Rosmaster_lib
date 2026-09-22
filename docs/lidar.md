# RPLidar A1

## Specifications

| Property | Value |
|----------|-------|
| Range | 0.15m — 12m |
| Angular resolution | ~0.9° |
| Sample rate | 8000 samples/sec |
| Scan rate | 5.5 Hz (typical) |
| Interface | UART (CP2102 USB adapter) |
| Baud rate | 115200 |
| Default udev symlink | `/dev/rplidar` |

## API

```python
from rosmaster_lib import Lidar

# Default (uses /dev/rplidar)
with Lidar() as lidar:
    info = lidar.get_info()
    health = lidar.get_health()
    for scan in lidar.iter_scans():
        for quality, angle, distance in scan:
            print(f"{angle:.1f} deg, {distance:.0f} mm")
```

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `connect()` | — | Open serial connection |
| `disconnect()` | — | Close connection, stop motor |
| `get_info()` | dict | Model, firmware, hardware, serial |
| `get_health()` | (str, int) | Status ("Good") and error code |
| `start_motor()` | — | Spin up the motor (2s delay) |
| `stop_motor()` | — | Stop the motor |
| `iter_measures()` | generator | Yield individual `(new_scan, quality, angle, distance)` |
| `iter_scans()` | generator | Yield full 360° scans as `[(quality, angle, distance), ...]` |
| `get_single_scan()` | list | One full 360° scan, blocking |
| `stop()` | — | Stop scanning |
| `reset()` | — | Hardware reset |

### Port override

```python
Lidar(port="/dev/ttyUSB0")
```

## Notes

- The motor takes about 2 seconds to reach full speed after `start_motor()`.
- The `iter_scans()` generator handles this automatically the first time.
- Points with `distance == 0` are invalid measurements and are filtered out.

# rosmaster_lib

Unified Python driver package for the **Yahboom ROSMASTER X3** robot running on a **Jetson Nano 4GB**, with **RPLidar A1** and **Orbbec Astra** depth camera. The driver works on the host machine - no need for docker containers or ROS2.

**Target platform:** Jetson Nano 4GB, Python 3.6+.

## Robot Setup
**⚠️ Plug the camera directly into the Jetson, not the USB hub.** 
- Unplug the camera cable from the usb hub (cable with white letters on the wire) and replug it directly into the jetson instead. This is necessary for the depth camera to work properly.

If its the first time using the robot see [Setup Documentation](docs/setup/) for instructions covering:

- [Flashing an image](docs/setup/flashing.md) — Yahboom image or Ubuntu 20.04 image for Jetson Nano. 
  - **NOTE** this library should work on any image on the robot
- [Connecting to the robot](docs/setup/connecting.md) — SSH, Wi-Fi, hotspot, RealVNC
- [Development environment](docs/setup/environment.md) — SSHFS, RealVNC, Desktopless

Also see the official [Yahboom ROSMASTER tutorials](https://www.yahboom.net/study/ROSMASTER-X3) for more details

## Quick Start

```bash
# 1. Clone this repo
git clone https://github.com/paprika-flow/Rosmaster_lib.git
cd rosmaster_lib

# 2. Install udev rules (run once per robot)
sudo bash install_udev_rules.sh

# 3. Install the package
pip install .

# 4. Test everything
python examples/basic_test.py

```

## Usage

### All-in-one

```python
from rosmaster_lib import Robot

with Robot() as robot:
    robot.chassis.set_car_motion(0.5, 0, 0)
    for scan in robot.lidar.iter_scans():
        ...
    depth, rgb = robot.camera.get_frames()
```

### Individual components

See the component docs for full API details:

| Component | Import | Doc | Port Name |
|-----------|--------|-----|-------------|
| **Chassis** | `from rosmaster_lib import Chassis` | [docs/chassis.md](docs/chassis.md) | `/dev/rosmaster_driver` |
| **Lidar** | `from rosmaster_lib import Lidar` | [docs/lidar.md](docs/lidar.md) | `/dev/rplidar` |
| **Camera** | `from rosmaster_lib import DepthCamera` | [docs/camera.md](docs/camera.md) | `/dev/astra_rgb` |

```python
from rosmaster_lib import Chassis, Lidar, DepthCamera

# Chassis
with Chassis() as bot:
    bot.set_car_motion(0.5, 0, 0)
    print(bot.get_battery_voltage())

# Lidar
with Lidar() as lidar:
    for scan in lidar.iter_scans():
        for quality, angle, dist in scan:
            print(f"{angle:.1f} deg, {dist:.0f} mm")

# Camera
with DepthCamera() as cam:
    depth = cam.get_depth_frame()
    rgb = cam.get_rgb_frame()
```

## Port Override

If the udev symlinks aren't available or you need to use a different port, pass it directly:

```python
Lidar(port="/dev/ttyUSB0")
DepthCamera(rgb_device="/dev/video0")
Chassis(com="/dev/ttyTHS1")
```

## Examples

| File | Description |
|------|-------------|
| `examples/basic_test.py` | Test all hardware |
| `examples/camera_capture.py` | Save one depth + RGB frame |
| `examples/camera_web_view.py` | Web stream RGB + depth (`:5000`) |
| `examples/lidar_web_view.py` | Web stream lidar view (`:5001`) |


## Dependencies

Installed automatically by `pip install .`:

| Package | Purpose |
|---------|---------|
| `pyserial` | Serial communication with motor board |
| `rplidap-roboticia` | RPLidar protocol |
| `opencv-python` | Camera capture, image processing |
| `numpy` | Array operations |
| `openni` | OpenNI2 Python bindings for depth camera |


## Package Structure

```txt
rosmaster_lib/
├── install_udev_rules.sh       # One-time udev setup
├── 99-rosmaster.rules          # udev rules file
├── setup.py                    # Package install
├── rosmaster_lib/
│   ├── lidar.py                # RPLidar A1
│   ├── depth_camera.py         # Orbbec Astra
│   ├── chassis.py              # Serial Sensors
│   ├── robot.py                # Unified Robot class
│   ├── Rosmaster_Lib/          # Bundled Yahboom driver
│   └── openni2/                # Bundled OpenNI2 arm64 libs
├── examples/                   # Usage examples
├── docs/                       # Documentation
└── images/                     # Reference photos
```

## Credits

- **Rosmaster_Lib** is the original Yahboom Team driver for their ROSMASTER series robots. Included as-is for convenience. All rights belong to Yahboom.
- RPLidar SDK by **Slamtec**.
- Orbbec Astra SDK by **Orbbec**.
- Biorobotics Lab at USF.

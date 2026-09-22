# Upgrading to Ubuntu 20.04

The default Yahboom image ships with **Ubuntu 18.04** and Python **3.6**. While the library works on 18.04, upgrading to **20.04** (Python 3.8) is recommended for the following reasons.

## Why Upgrade

| Feature | Ubuntu 18.04 | Ubuntu 20.04 |
|---------|-------------|-------------|
| Python | 3.6 (EOL Dec 2021) | 3.8 (EOL Oct 2024) |
| VS Code Server | Requires older version | Works out of the box |
| Package availability | Many packages no longer support 3.6 | Broad package support |
| Performance | Older kernel, drivers | Better Jetson support |

## Use a Community Image (Recommended)

The [Jetson Nano 4GB Ubuntu 20.04 image](https://github.com/Qengineering/Jetson-Nano-Ubuntu-20.04) by Qengineering provides a clean Ubuntu 20.04 installation with the JetPack drivers pre-installed.

1. Download the image
2. Flash to a microSD card (minimum 32GB, recommended 64GB+)
3. Insert into the Jetson and boot
4. Install the robot-specific drivers

**Important:** After flashing, you'll need to re-install the Yahboom robot drivers. See below.


## After Upgrading — Reinstall Robot Drivers

After upgrading you need to re-install the robot's motor board interface:

```bash
# The Yahboom driver for the STM32 motor board
# (Location depends on where you downloaded it)
cd py_install_V3.3.1
sudo python3 setup.py install

# Then install rosmaster_lib
cd ~/rosmaster_lib
sudo bash install_udev_rules.sh
pip install .
```

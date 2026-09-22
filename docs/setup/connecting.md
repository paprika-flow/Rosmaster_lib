# Connecting to the Robot

## SSH (Recommended)

```bash
# Find the robot on your network
ping rosmaster.local
# Or find its IP from the robot's terminal: ip addr show | grep inet

# Connect
ssh jetson@<robot-ip>
# Password: (default is usually "jetson")
```

## Wi-Fi Setup

The robot can act as a **Wi-Fi hotspot** or connect to your existing network.

### Hotspot mode (no router needed)

The Yahboom image has a pre-configured hotspot:
- **SSID:** `ROSMASTER` (or similar)
- **Password:** `12345678`
- Connect your laptop to this network, then SSH to `192.168.2.71`

### Connect to your lab network

```bash
# Find available networks
nmcli dev wifi list

# Connect
nmcli dev wifi connect "YourNetwork" password "YourPassword"

# Verify
ip addr show | grep inet
```

**Note:** The default Yahboom image (Ubuntu 18.04) uses `network-manager`. If you upgraded to Ubuntu 20.04, the same commands work.

## RealVNC

The Yahboom image includes RealVNC Server. The ROSMASTER hotspot usually has VNC enabled on port 5900.

1. Install RealVNC Viewer on your laptop
2. Connect to the robot's IP on port 5900
3. Default credentials: `jetson` / `jetson`

## Password Reference

| User | Default Password |
|------|-----------------|
| `jetson` | `jetson` |
| `root` | `root` |

*Change these if the robot is on a shared network.*

"""
Quick test — verify all hardware is connected and working.

Usage:
    python examples/basic_test.py
"""

from rosmaster_lib import Robot, Lidar, DepthCamera, Chassis

print("=== Robot Hardware Test ===\n")

# 1. Chassis
print("[1/3] Testing chassis...")
try:
    with Chassis() as bot:
        version = bot.get_version()
        battery = bot.get_battery_voltage()
        print(f"  Version: {version}")
        print(f"  Battery: {battery}V")
        bot.set_beep(50)
        print("  Buzzer: OK")
except Exception as e:
    print(f"  FAILED: {e}")

# 2. Lidar
print("\n[2/3] Testing lidar...")
try:
    with Lidar() as lidar:
        info = lidar.get_info()
        health = lidar.get_health()
        print(f"  Model: {info['model']}")
        print(f"  Firmware: {info['firmware']}")
        print(f"  Health: {health}")
except Exception as e:
    print(f"  FAILED: {e}")

# 3. Camera
print("\n[3/3] Testing camera...")
try:
    with DepthCamera() as cam:
        depth = cam.get_depth_frame()
        rgb = cam.get_rgb_frame()
        if depth is not None:
            print(f"  Depth: {depth.shape}, {depth.min()}-{depth.max()}mm")
        if rgb is not None:
            print(f"  RGB: {rgb.shape}")
except Exception as e:
    print(f"  FAILED: {e}")

print("\n=== Done ===")

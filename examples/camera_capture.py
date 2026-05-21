"""
Capture one frame from the depth camera and save it.

Usage:
    python examples/camera_capture.py
"""

import cv2
from rosmaster_lib import DepthCamera

with DepthCamera() as cam:
    depth, rgb = cam.get_frames()

    if depth is not None:
        cv2.imwrite("depth_raw.png", depth)
        colorized = DepthCamera.depth_to_colormap(depth)
        cv2.imwrite("depth_colormap.jpg", colorized)
        print(f"Saved depth: {depth.shape}")

    if rgb is not None:
        cv2.imwrite("rgb.jpg", rgb)
        print(f"Saved RGB: {rgb.shape}")

print("Done")

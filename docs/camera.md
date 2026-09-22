# Orbbec Astra Depth Camera

## Specifications

| Property | Value |
|----------|-------|
| Technology | IR projection |
| Depth range | 0.2m — 8m |
| Depth resolution | 640×480 @ 30 FPS |
| RGB resolution | Up to 1280×960 |
| Interface | USB 3.0 |
| Default RGB udev symlink | `/dev/astra_rgb` |

## Depth Stream (OpenNI2)

The depth stream uses the OpenNI2 SDK. The arm64 shared libraries are bundled inside the package at `rosmaster_lib/openni2/`, so no system-wide installation is needed on the Jetson Nano.

## RGB Stream (OpenCV)

The RGB stream uses OpenCV's `VideoCapture`. The camera exposes a standard UVC interface at `/dev/video0` (or `/dev/astra_rgb` with udev rules).

## API

```python
from rosmaster_lib import DepthCamera

# Default (depth + RGB)
with DepthCamera() as cam:
    depth = cam.get_depth_frame()    # uint16 array, mm
    rgb = cam.get_rgb_frame()        # uint8 BGR array, or None
    depth, rgb = cam.get_frames()    # both at once
```

### Parameters

```python
DepthCamera(
    openni_lib_dir=None,      # Path to OpenNI2 .so folder
    rgb_device="/dev/astra_rgb",  # RGB video device
    rgb_width=None,
    rgb_height=None,
    warmup_frames=10,         # Frames to discard on startup
    flip_depth=True,          # Mirror depth frame horizontally
)
```

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `get_depth_frame()` | ndarray (H, W), uint16 | Depth in millimeters |
| `get_rgb_frame()` | ndarray (H, W, 3), uint8 or None | BGR image |
| `get_frames()` | (depth, rgb) | Both at once |
| `release()` | — | Stop streams, free resources |
| `depth_to_colormap(depth, max_dist=5000)` | ndarray | Colorized depth for viewing |

### Properties

| Property | Returns | Description |
|----------|---------|-------------|
| `has_depth` | bool | Depth stream available |
| `has_rgb` | bool | RGB stream available |

### Port override

```python
DepthCamera(rgb_device="/dev/video0")
DepthCamera(rgb_device="/dev/video0", rgb_width=1280, rgb_height=960)
```

## Notes

- If the Depth is not needed, it's better to use just `cv2.VideoCapture(0)` directly for the RGB camera.
- The depth camera has a warm-up period — the first 10 frames (configurable) are discarded automatically.
- The `flip_depth=True` default corrects the horizontal mirror on the depth output.

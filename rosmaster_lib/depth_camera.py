"""
Orbbec Astra depth camera driver for the rosmaster_lib package.

Uses the OpenNI2 SDK bundled in rosmaster_lib/openni2/ to access
both depth and RGB streams from Orbbec Astra / Astra Pro cameras.

Basic usage:
    from rosmaster_lib.depth_camera import DepthCamera

    cam = DepthCamera()
    depth = cam.get_depth_frame()      # 16-bit depth in mm
    rgb = cam.get_rgb_frame()           # 8-bit RGB (if available)
    cam.release()

    # Save for viewing
    cv2.imwrite("depth_raw.png", depth)
"""

import os
import sys
import logging
import numpy as np

logger = logging.getLogger('rosmaster_lib.depth_camera')


class DepthCameraError(Exception):
    """Raised on depth camera errors."""


class DepthCamera:
    """Orbbec Astra depth and RGB camera via OpenNI2.

    Bundles the arm64 OpenNI2 shared libraries inside the package
    so no system-wide installation is needed on Jetson Nano.

    Parameters
    ----------
    openni_lib_dir : str or None
        Path to the folder containing libOpenNI2.so and OpenNI2/Drivers/.
        If None, looks inside the rosmaster_lib package at openni2/.
    warmup_frames : int
        Number of frames to discard after starting the camera
        to let the sensor stabilize (default 10).
    """

    def __init__(self, openni_lib_dir=None, warmup_frames=10):
        import openni2  

        if openni_lib_dir is None:
            openni_lib_dir = self._find_bundled_libs()

        if not os.path.isdir(openni_lib_dir):
            raise DepthCameraError(
                f"OpenNI2 library directory not found: {openni_lib_dir}"
            )

        logger.info("Initializing OpenNI2 from %s", openni_lib_dir)
        openni2.initialize(openni_lib_dir)

        # Check for connected devices
        uris = openni2.Device.enumerate_uris()
        if not uris:
            openni2.unload()
            # Give a helpful hint if udev rules are missing
            hint = ""
            if not os.path.exists("/etc/udev/rules.d/rosmaster.rules"):
                hint = (
                    "\n  udev rules not found. Install them once:\n"
                    "    sudo bash install_udev_rules.sh"
                )
            elif not os.path.exists("/dev/astra") \
                 and not any(f.startswith("/dev/astra") for f in os.listdir("/dev/")):
                hint = (
                    "\n  udev rules are installed but /dev/astra* not found.\n"
                    "  Check USB connection and try:\n"
                    "    sudo udevadm trigger"
                )
            raise DepthCameraError(
                "No Orbbec Astra camera detected."
                "Check USB connection and permissions."
                + hint
            )
        logger.info("Found devices: %s", uris)

        # Open the camera
        try:
            self._dev = openni2.Device.open_any()
            logger.info("Camera opened: %s", self._dev.get_device_info())
        except Exception as e:
            openni2.unload()
            raise DepthCameraError(f"Failed to open camera: {e}")

        # Start depth stream
        try:
            self._depth_stream = self._dev.create_depth_stream()
            self._depth_stream.start()
            self._depth_available = True
            logger.info("Depth stream started")
        except Exception as e:
            self._depth_available = False
            logger.warning("Could not start depth stream: %s", e)

        # Start color (RGB) stream (not all models have this)
        self._color_stream = None
        self._color_available = False
        try:
            self._color_stream = self._dev.create_color_stream()
            self._color_stream.start()
            self._color_available = True
            logger.info("Color stream started")
        except Exception as e:
            logger.info("No color stream available: %s", e)

        if not self._depth_available and not self._color_available:
            self.release()
            raise DepthCameraError("No depth or color streams could be started")

        # Warm up — discard initial frames (sensor needs time to stabilize)
        for i in range(warmup_frames):
            try:
                if self._depth_available:
                    self._depth_stream.read_frame()
                if self._color_available:
                    self._color_stream.read_frame()
            except Exception:
                pass
        logger.info("Camera ready after %d warmup frames", warmup_frames)

    def get_depth_frame(self):
        """Read the latest depth frame.

        Returns
        -------
        numpy.ndarray of shape (H, W) with dtype uint16
            Each pixel is distance in millimeters (0 = invalid/no data).
            Typical range: 0 to 8000 mm.

        Raises
        ------
        DepthCameraError if depth stream is not available.
        """
        if not self._depth_available:
            raise DepthCameraError("Depth stream is not available")

        frame = self._depth_stream.read_frame()
        data = frame.get_buffer_as_uint16()
        depth = np.ndarray(
            (frame.height, frame.width), dtype=np.uint16, buffer=data
        )
        return depth.copy()  # copy so buffer can be reused

    def get_rgb_frame(self):
        """Read the latest RGB (color) frame.

        Returns
        -------
        numpy.ndarray of shape (H, W, 3) with dtype uint8 in BGR format
        (OpenCV convention), or None if no color stream is available.
        """
        if not self._color_available:
            return None

        frame = self._color_stream.read_frame()
        data = frame.get_buffer_as_uint8()
        rgb = np.ndarray(
            (frame.height, frame.width, 3), dtype=np.uint8, buffer=data
        )
        # OpenNI2 returns RGB, but OpenCV uses BGR — convert
        return rgb[:, :, ::-1].copy()  # RGB -> BGR + copy

    def get_frames(self):
        """Read both depth and RGB in one call.

        Returns
        -------
        tuple of (depth_frame, rgb_frame)
            depth_frame : ndarray or None
            rgb_frame : ndarray or None
        """
        depth = self.get_depth_frame() if self._depth_available else None
        rgb = self.get_rgb_frame()
        return depth, rgb

    @property
    def has_rgb(self):
        """True if the camera provides an RGB stream."""
        return self._color_available

    @property
    def has_depth(self):
        """True if the camera provides a depth stream."""
        return self._depth_available

    def release(self):
        """Stop all streams and unload OpenNI2.

        Safe to call multiple times.
        """
        import openni2

        try:
            if self._depth_stream and self._depth_available:
                self._depth_stream.stop()
        except Exception:
            pass
        try:
            if self._color_stream and self._color_available:
                self._color_stream.stop()
        except Exception:
            pass
        try:
            openni2.unload()
        except Exception:
            pass
        self._depth_available = False
        self._color_available = False
        logger.info("Camera released")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.release()

    def __del__(self):
        self.release()

    @staticmethod
    def _find_bundled_libs():
        """Locate the bundled OpenNI2 arm64 library folder.

        Searches relative to this file first, then common locations.
        """
        here = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            os.path.join(here, "openni2"),
            os.path.join(here, "openni2", "Arm64"),
            os.path.join(here, "openni2", "arm", "Arm64"),
            os.path.join(here, "..", "openni2"),
        ]
        for path in candidates:
            full = os.path.abspath(path)
            so_file = os.path.join(full, "libOpenNI2.so")
            if os.path.isfile(so_file):
                return full

        raise DepthCameraError(
            "Could not find bundled OpenNI2 libraries. "
            "Expected libOpenNI2.so in rosmaster_lib/openni2/"
        )

    @staticmethod
    def depth_to_colormap(depth_array, max_dist_mm=5000):
        """Convert a 16-bit depth array to a colorized 8-bit image.

        Parameters
        ----------
        depth_array : ndarray of uint16
            Depth in millimeters.
        max_dist_mm : int
            Distances beyond this are clipped (default 5000 mm / 5 m).

        Returns
        -------
        ndarray of shape (H, W, 3), dtype uint8, BGR format
        """
        import cv2

        # Clip and scale to 0-255
        scaled = np.clip(depth_array, 0, max_dist_mm).astype(np.float32)
        scaled = (scaled / max_dist_mm * 255).astype(np.uint8)

        # Apply jet colormap (blue=near, red=far)
        return cv2.applyColorMap(scaled, cv2.COLORMAP_JET)


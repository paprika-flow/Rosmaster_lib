"""
Orbbec Astra depth camera driver for the rosmaster_lib package.

- Depth stream via OpenNI2 SDK (bundled .so files)
- RGB stream via OpenCV VideoCapture (/dev/video0)

Basic usage:
    from rosmaster_lib.depth_camera import DepthCamera

    cam = DepthCamera()
    depth = cam.get_depth_frame()      # 16-bit depth in mm
    rgb = cam.get_rgb_frame()           # BGR uint8 image
    cam.release()

    # Or use context manager (auto cleanup):
    with DepthCamera() as cam:
        depth, rgb = cam.get_frames()
"""

import os
import logging
import cv2
import numpy as np
import openni2

logger = logging.getLogger('rosmaster_lib.depth_camera')


class DepthCameraError(Exception):
    """Raised on depth camera errors."""


class DepthCamera:
    """Orbbec Astra depth camera via OpenNI2, RGB via OpenCV.

    Parameters
    ----------
    openni_lib_dir : str or None
        Path to folder with libOpenNI2.so. If None, looks in
        rosmaster_lib/openni2/.
    rgb_device : int or str
        OpenCV VideoCapture device for RGB (default 0 = /dev/video0).
    warmup_frames : int
        Number of frames to discard after starting the camera
        to let the sensor stabilize (default 10).
    """

    def __init__(self, openni_lib_dir=None, rgb_device=0, warmup_frames=10):
        warmup_frames = max(0, min(warmup_frames, 100))

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
            if not os.path.exists("/etc/udev/rules.d/99-rosmaster.rules"):
                hint = (
                    "\n  udev rules not found. Install them once:\n"
                    "    sudo bash install_udev_rules.sh"
                )
            elif not any(f.startswith("/dev/astra") for f in os.listdir("/dev/")):
                hint = (
                    "\n  udev rules are installed but /dev/astra* not found.\n"
                    "  Check USB connection and try:\n"
                    "    sudo udevadm trigger"
                )
            raise DepthCameraError(
                "No Orbbec Astra camera detected. "
                "Check USB connection and permissions." + hint
            )
        logger.info("Found devices: %s", uris)

        # Open the camera
        try:
            self._dev = openni2.Device.open_any()
            logger.info("Camera opened: %s", self._dev.get_device_info())
        except Exception as e:
            openni2.unload()
            raise DepthCameraError(f"Failed to open camera: {e}")

        # Start depth stream via OpenNI2
        self._depth_stream = self._dev.create_depth_stream()
        self._depth_stream.start()
        self._depth_available = True
        logger.info("Depth stream started")

        # ── OpenCV for RGB ──
        self._rgb_cap = cv2.VideoCapture(rgb_device)
        if not self._rgb_cap.isOpened():
            logger.warning("Could not open RGB device %s", rgb_device)
            self._rgb_available = False
        else:
            self._rgb_available = True
            logger.info("RGB capture opened on device %s", rgb_device)
            # Set a reasonable resolution
            self._rgb_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self._rgb_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Warm up — discard initial frames (depth sensor needs time to stabilize)
        for i in range(warmup_frames):
            try:
                self._depth_stream.read_frame()
            except Exception:
                pass
            if self._rgb_available:
                self._rgb_cap.read()

        logger.info("Camera ready after %d warmup frames", warmup_frames)

    def get_depth_frame(self):
        """Read the latest depth frame.

        Returns
        -------
        numpy.ndarray of shape (H, W), dtype uint16
            Distance in millimeters. 0 = invalid. Typical range 0-8000.
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
        """Read the latest RGB frame via OpenCV.

        Returns
        -------
        numpy.ndarray of shape (H, W, 3), dtype uint8, BGR format
            Or None if RGB is not available.
        """
        if not self._rgb_available:
            return None

        ret, frame = self._rgb_cap.read()
        if ret:
            return frame
        return None

    def get_frames(self):
        """Read both depth and RGB in one call.

        Returns
        -------
        tuple of (depth_frame, rgb_frame)
            Either may be None.
        """
        depth = None
        if self._depth_available:
            try:
                depth = self.get_depth_frame()
            except DepthCameraError:
                depth = None
        rgb = self.get_rgb_frame()
        return depth, rgb

    @property
    def has_rgb(self):
        return self._rgb_available

    @property
    def has_depth(self):
        return self._depth_available

    # ── Cleanup ────────────────────────────────────────────────

    def release(self):
        """Stop depth stream, release RGB capture, unload OpenNI2."""
        if getattr(self, '_released', False):
            return
        self._released = True

        try:
            if self._depth_stream and self._depth_available:
                self._depth_stream.stop()
        except Exception:
            pass

        try:
            if self._rgb_available and self._rgb_cap:
                self._rgb_cap.release()
        except Exception:
            pass

        self._depth_available = False
        self._rgb_available = False
        logger.info("Camera released")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.release()

    def __del__(self):
        self.release()

    @staticmethod
    def _find_bundled_libs():
        """Locate the bundled OpenNI2 arm64 library folder."""
        here = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            os.path.join(here, "openni2"),
            os.path.join(here, "openni2", "Arm64"),
            os.path.join(here, "openni2", "arm", "Arm64"),
            os.path.join(here, "..", "openni2"),
        ]
        for path in candidates:
            full = os.path.abspath(path)
            if os.path.isfile(os.path.join(full, "libOpenNI2.so")):
                return full

        raise DepthCameraError(
            "Could not find bundled OpenNI2 libraries. "
            "Expected libOpenNI2.so in rosmaster_lib/openni2/"
        )


    @staticmethod
    def depth_to_colormap(depth_array, max_dist_mm=5000):
        """Convert 16-bit depth to a colorized 8-bit BGR image.

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
        max_dist_mm = max(max_dist_mm, 1)

        # Clip and scale to 0-255
        scaled = np.clip(depth_array, 0, max_dist_mm).astype(np.float32)
        scaled = (scaled / max_dist_mm * 255).astype(np.uint8)

        # Apply jet colormap (blue=near, red=far)
        return cv2.applyColorMap(scaled, cv2.COLORMAP_JET)


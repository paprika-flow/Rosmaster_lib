"""
Robot class combining chassis, lidar, and depth camera.

Usage:
    from rosmaster_lib import Robot

    with Robot() as robot:
        robot.drive(0.3, 0, 0)          # forward
        for scan in robot.lidar.iter_scans():
            ...
        depth, rgb = robot.camera.get_frames()
"""

import logging

from .chassis import Chassis
from .lidar import Lidar
from .depth_camera import DepthCamera

logger = logging.getLogger('rosmaster_lib.robot')


class RobotError(Exception):
    """Raised on robot initialization errors."""


class Robot:
    """Initializes chassis, lidar, and depth camera with their
    default udev symlinks.

    Parameters
    ----------
    chassis_port : str
        Serial port for the motor board.
    lidar_port : str
        Serial port for the RPLidar.
    camera_rgb_device : int or str
        Video device for the camera RGB stream.
    car_type : int
        Robot model passed to Chassis.
    """

    def __init__(self, chassis_port="/dev/rosmaster_driver",
                 lidar_port="/dev/rplidar",
                 camera_rgb_device="/dev/astra_rgb",
                 car_type=1):
        self._chassis_port = chassis_port
        self._lidar_port = lidar_port
        self._camera_rgb_device = camera_rgb_device
        self._car_type = car_type

        self._chassis = None
        self._lidar = None
        self._camera = None

    @property
    def chassis(self):
        """Connected Chassis instance."""
        return self._chassis

    @property
    def lidar(self):
        """Connected Lidar instance."""
        return self._lidar

    @property
    def camera(self):
        """Connected DepthCamera instance."""
        return self._camera

    def __enter__(self):
        logger.info("Initializing robot...")

        # Chassis
        try:
            c = Chassis(com=self._chassis_port, car_type=self._car_type)
            self._chassis = c.__enter__()
        except Exception as e:
            logger.warning("Chassis not available: %s", e)
            self._chassis = None

        # Lidar
        try:
            self._lidar = Lidar(port=self._lidar_port)
            self._lidar.connect()
        except Exception as e:
            logger.warning("Lidar not available: %s", e)
            self._lidar = None

        # Camera
        try:
            self._camera = DepthCamera(rgb_device=self._camera_rgb_device)
        except Exception as e:
            logger.warning("Camera not available: %s", e)
            self._camera = None

        logger.info("Robot ready")
        return self

    def __exit__(self, *args):
        if self._camera:
            try:
                self._camera.release()
            except Exception:
                pass
        if self._lidar:
            try:
                self._lidar.disconnect()
            except Exception:
                pass
        if self._chassis:
            try:
                self._chassis.set_car_motion(0, 0, 0)
            except Exception:
                pass

    def drive(self, v_x=0.0, v_y=0.0, v_z=0.0):
        """Drive the robot. Requires chassis to be connected."""
        if self._chassis:
            self._chassis.set_car_motion(v_x, v_y, v_z)

    def stop(self):
        """Stop all motion."""
        self.drive(0, 0, 0)

    def beep(self, duration_ms=100):
        """Sound the buzzer."""
        if self._chassis:
            self._chassis.set_beep(duration_ms)

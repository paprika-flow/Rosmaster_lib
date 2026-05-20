"""
Thin context manager wrapper for the Rosmaster motor board.

Usage:
    from rosmaster_lib import Chassis

    with Chassis() as bot:
        bot.set_car_motion(0.3, 0, 0)
        bot.set_beep(100)
        print(bot.get_battery_voltage())
"""

import os
import time
import logging

from .Rosmaster_Lib import Rosmaster

logger = logging.getLogger('rosmaster_lib.chassis')


class ChassisError(Exception):
    """Raised on chassis errors."""


class Chassis:
    """Context manager that provides a connected Rosmaster instance.

    Parameters
    ----------
    com : str
        Serial port (default /dev/rosmaster_driver).
    car_type : int
        Robot model: 1=X3, 2=X3_PLUS, 4=X1, 5=R2 (default 1).
    """

    def __init__(self, com="/dev/rosmaster_driver", car_type=1):
        self._com = com
        self._car_type = car_type
        self._bot = None

    @property
    def bot(self):
        """The Rosmaster instance, or None if not connected."""
        return self._bot

    def __enter__(self):
        if not os.path.exists(self._com):
            raise ChassisError(
                f"{self._com} not found. "
                "Install udev rules: sudo bash install_udev_rules.sh"
            )
        try:
            self._bot = Rosmaster(car_type=self._car_type, com=self._com)
        except Exception as e:
            raise ChassisError(
                f"Failed to connect on {self._com}: {e}"
            ) from e
        self._bot.create_receive_threading()
        time.sleep(0.1)
        logger.info("Connected on %s", self._com)
        return self._bot

    def __exit__(self, *args):
        if self._bot:
            try:
                self._bot.set_car_motion(0, 0, 0)
                self._bot.set_colorful_effect(0)
                time.sleep(0.05)
            except Exception:
                pass
        self._bot = None

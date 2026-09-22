# Chassis — Motors, Encoders, IMU

The chassis is controlled by an STM32 microcontroller that communicates over serial. The bundled `Rosmaster_Lib` handles the low-level protocol; `Chassis` provides a context manager wrapper.

## Specifications

| Component | Details |
|-----------|---------|
| Motors | 4 DC motors with encoders |
| Motor control | PWM, velocity control via `set_car_motion()` |
| IMU | MPU9250 or ICM20948 (accelerometer, gyroscope, magnetometer) |
| Attitude | Roll, pitch, yaw from onboard fusion |
| Encoders | 4-channel quadrature |
| Serial | 115200 baud, 8N1 |

## Default Ports

Ports are checked in order:
1. `/dev/rosmaster_driver` (udev symlink for USB-serial adapter)
2. `/dev/ttyTHS1` (Jetson hardware UART)

## API

```python
from rosmaster_lib import Chassis

# Context manager returns the raw Rosmaster object
with Chassis() as bot:
    # ── Motion ──
    bot.set_car_motion(v_x, v_y, v_z)

    # ── Sensors ──
    ax, ay, az = bot.get_accelerometer_data()
    gx, gy, gz = bot.get_gyroscope_data()
    mx, my, mz = bot.get_magnetometer_data()
    roll, pitch, yaw = bot.get_imu_attitude_data()
    vx, vy, vz = bot.get_motion_data()
    m1, m2, m3, m4 = bot.get_motor_encoder()
    voltage = bot.get_battery_voltage()

    # ── Lights & Sound ──
    bot.set_colorful_lamps(led_id, r, g, b)
    bot.set_colorful_effect(effect, speed)
    bot.set_beep(duration_ms)

    # ── Servos ──
    bot.set_pwm_servo(servo_id, angle)
    bot.set_uart_servo(servo_id, pulse, run_time)
```

### Car motion input ranges

| Car type | v_x | v_y | v_z |
|----------|-----|-----|-----|
| X3 | -1.0 to 1.0 | -1.0 to 1.0 | -5.0 to 5.0 |
| X3 PLUS | -0.7 to 0.7 | -0.7 to 0.7 | -3.2 to 3.2 |
| R2 | -1.8 to 1.8 | -0.045 to 0.045 | -3.0 to 3.0 |

### Car types

| Constant | Value | Robot |
|----------|-------|-------|
| `CARTYPE_X3` | 1 | ROSMASTER X3 |
| `CARTYPE_X3_PLUS` | 2 | ROSMASTER X3 PLUS |
| `CARTYPE_X1` | 4 | ROSMASTER X1 |
| `CARTYPE_R2` | 5 | ROSMASTER R2 |

### Raw access

The `Chassis` context manager returns the raw `Rosmaster` object. Any method from the underlying `Rosmaster_Lib` is available directly.

### Port override

```python
Chassis(com="/dev/ttyTHS1")
Chassis(com="/dev/ttyUSB0", car_type=2)
```

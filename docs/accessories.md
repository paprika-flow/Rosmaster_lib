# Accessories — Lights, Buzzer, OLED

## RGB LEDs

The robot has 14 individually addressable RGB LEDs around the chassis. Each LED can be set to any RGB color (0-255 per channel).

```python
bot.set_colorful_lamps(led_id, red, green, blue)
```

| led_id | Location |
|--------|----------|
| 0xFF | All LEDs |
| 0-3 | Left edge |
| 4-9 | Middle (gap) |
| 10-13 | Right edge |

### Effects

```python
bot.set_colorful_effect(effect, speed, parm)
```

| effect | Description |
|--------|-------------|
| 0 | Stop effect |
| 1 | Flowing water |
| 2 | Marquee |
| 3 | Breathing |
| 4 | Gradient |
| 5 | Starlight |
| 6 | Battery level |

## Buzzer

```python
# Beep for 100ms
bot.set_beep(100)

# Continuous
bot.set_beep(1)

# Off
bot.set_beep(0)
```

## OLED Screen

*(Not currently exposed through this library — controlled directly by the STM32 firmware.)*

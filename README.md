# ZMK Config — Corne (42-key split)

Personal [ZMK](https://zmk.dev) firmware configuration for a split Corne keyboard with Swiss German (CH-DE) layout.

## Hardware

- **Keyboard:** Corne (3x6 + 3 thumb keys per half)
- **Controllers:** nice!nano v2
- **Displays:** nice!view Gem
- **Firmware:** ZMK v0.3 with ZMK Studio enabled (left half)

## Layers

| # | Name     | Description                                      |
|---|----------|--------------------------------------------------|
| 0 | BASE     | QWERTZ with home-row hold-taps                   |
| 1 | I3       | i3 window manager navigation and workspace keys  |
| 2 | SYSTEM   | Numbers, arrow keys, BT profile management       |
| 3 | SYMBOL   | Programming symbols and punctuation               |
| 4 | NUMBER   | Numpad-style number entry                         |
| 5 | FUNCTION | F-keys and ZMK Studio unlock                     |

## Keymap Visualizer

An interactive HTML visualizer is auto-generated from the keymap source.

**Live version:** https://polaroidkidd.github.io/zmk-config/

To regenerate locally after editing `config/corne.keymap`:

```sh
python3 generate.py
```

## Building Firmware

Firmware is built automatically via GitHub Actions on push. The workflow produces `.uf2` files for both halves which can be flashed by copying them to the nice!nano's USB mass storage device.

## Repository Structure

```
config/
  corne.keymap   # Keymap source of truth (layers, behaviors, macros)
  ch-de.h        # Swiss German HID keycode definitions
  corne.conf     # Runtime flags (BLE, display, animation)
  west.yml       # ZMK and nice-view-gem dependency pins
build.yaml       # GitHub Actions build matrix
generate.py      # Keymap → HTML visualizer generator
```

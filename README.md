# ZMK Config — Sofle Choc Pro (60-key split)

Personal [ZMK](https://zmk.dev) firmware configuration for a split Sofle Choc Pro keyboard with Swiss German (CH-DE) layout.

## Hardware

- **Keyboard:** Sofle Choc Pro (4x6 + 5 thumb keys per half)
- **Build targets:** `sofle_choc_pro_left` and `sofle_choc_pro_right`
- **Displays:** `sharp_mip`
- **Firmware:** ZMK v0.3

## Layers

| # | Name     | Description                                      |
|---|----------|--------------------------------------------------|
| 0 | ROOT     | QWERTZ base layer                                |
| 1 | I3       | i3 window manager shortcuts                      |
| 2 | SYSTEM   | F-keys, Bluetooth, lighting, and Studio unlock   |
| 3 | SYMBL    | Symbols and navigation                           |
| 4 | NUM      | Right-hand number overlay                        |

## Keymap Visualizer

An interactive HTML visualizer is auto-generated from the keymap source.

**Live version:** https://polaroidkidd.github.io/zmk-config/

To regenerate locally after editing `config/sofle_choc_pro.keymap`:

```sh
python3 generate.py
```

## Building Firmware

Firmware is built automatically via GitHub Actions on push. The workflow produces `.uf2` files for both halves which can be flashed by copying them to the nice!nano's USB mass storage device.

## Repository Structure

```
config/
  sofle_choc_pro.keymap   # Keymap source of truth
  sofle_choc_pro.conf     # Runtime flags
  ch-de.h                 # Swiss German HID keycode definitions
  west.yml                # ZMK and module dependency pins
build.yaml                # GitHub Actions build matrix
generate.py               # Keymap → HTML visualizer generator
```

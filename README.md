# ZMK Config — Sofle (60-key split)

Personal [ZMK](https://zmk.dev) firmware configuration for a split Sofle keyboard with Swiss German (CH-DE) layout.

## Hardware

- **Keyboard:** Sofle (4x6 + 5 thumb keys per half)
- **Controllers:** nice!nano v2
- **Displays:** nice!view Gem
- **Firmware:** ZMK v0.3 with ZMK Studio enabled (left half)

## Layers

| # | Name     | Description                                      |
|---|----------|--------------------------------------------------|
| 0 | BASE     | QWERTZ with home-row hold-taps                   |
| 1 | NUM      | Right-hand number overlay                        |
| 2 | SYMBL    | Symbol and navigation overlay                    |
| 3 | SYS      | BT profile management, F-keys, Studio unlock     |

## Keymap Visualizer

An interactive HTML visualizer is auto-generated from the keymap source.

**Live version:** https://polaroidkidd.github.io/zmk-config/

To regenerate locally after editing `config/sofle.keymap`:

```sh
python3 generate.py
```

## Building Firmware

Firmware is built automatically via GitHub Actions on push. The workflow produces `.uf2` files for both halves which can be flashed by copying them to the nice!nano's USB mass storage device.

## Repository Structure

```
config/
  sofle.keymap   # Keymap source of truth (layers, behaviors, macros)
  ch-de.h        # Swiss German HID keycode definitions
  sofle.conf     # Runtime flags (BLE, display, animation)
  west.yml       # ZMK and nice-view-gem dependency pins
build.yaml       # GitHub Actions build matrix
generate.py      # Keymap → HTML visualizer generator
```

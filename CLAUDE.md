# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ZMK firmware configuration for a Corne (crkbd) split keyboard. This is a user config repo — it does not contain ZMK source code, only personal keymap/config files. Firmware is built via GitHub Actions.

## Build

Firmware builds run in CI only (GitHub Actions). There is no local build system.

- Push to any branch or open a PR triggers `.github/workflows/build.yml`
- The workflow delegates to `zmkfirmware/zmk/.github/workflows/build-user-config.yml@v0.3`
- Build artifacts (UF2 firmware files) are available as GitHub Actions artifacts

## Architecture

All user config lives in `config/`:

- **`config/west.yml`** — West manifest pinning ZMK to `v0.3` from `zmkfirmware/zmk`
- **`config/corne.keymap`** — Devicetree keymap file with three layers: default (QWERTY), lower (numbers/nav/bluetooth), raise (symbols). Uses `&studio_unlock` on raise layer for ZMK Studio support.
- **`config/corne.conf`** — Kconfig overrides (RGB underglow and OLED display options, currently disabled)
- **`config/keys_de_swiss.h`** — Swiss German (de_CH) locale key definitions. Included in the keymap but `DE_*` macros are not currently used in bindings.

## Keymap Conventions

- The keymap uses ZMK devicetree syntax (`.dtsi` includes, `bindings = <...>` format)
- Layer access: `&mo 1` (lower) and `&mo 2` (raise) on default layer
- Bluetooth controls are on the lower layer (BT_CLR, BT_SEL 0-4)
- Standard ZMK key codes from `<dt-bindings/zmk/keys.h>` — use `DE_*` prefixed macros from `keys_de_swiss.h` if Swiss German locale-aware bindings are needed

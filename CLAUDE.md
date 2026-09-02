# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

ZMK firmware configuration for a split Sofle Choc Pro keyboard (60 keys) with a Swiss German (CH-DE) layout.

## Build & Validation

- **Firmware builds** run via GitHub Actions (`.github/workflows/build.yml`), which delegates to `zmkfirmware/zmk/.github/workflows/build-user-config.yml@v0.3`. Push to trigger.
- **After editing `config/sofle_choc_pro.keymap`**, run `python3 generate.py` to regenerate the keymap visualizer (`index.html`). This is the primary local validation step.
- **No test suite exists.** Validation is via visualizer generation and firmware build success.
- ZMK v0.3 docs: https://v0-3-branch.zmk.dev

## Architecture

**`config/sofle_choc_pro.keymap`** is the source of truth. It defines:
- 5 layers: ROOT (0), I3 (1), SYS (2), SYMBL (3), and NUM (4)
- Mod-morphs for shifted umlauts and symbol access
- Macros for capital umlauts and i3 shortcuts
- A 60-key Sofle layout with 12-key top rows, a 14-key bottom row, and 10 thumb keys

**`config/ch-de.h`** defines Swiss German keycodes (`DE_*`) using HID usage codes with `RA()` (AltGr) and `LS()` (Shift) modifiers.

**`generate.py`** parses the keymap via regex and generates an interactive HTML visualizer. It is format-sensitive — maintain the DTS-style block structure in the keymap.

**`config/sofle_choc_pro.conf`** sets runtime flags for BLE and the keyboard name.

**`config/west.yml`** pins dependencies: ZMK v0.3 and the Keebart board/display module.

## Key Conventions

- When adding new `DE_*` keycodes, update both `config/ch-de.h` AND the label tables in `generate.py` (`DE_LABELS`, `DE_NAME_FALLBACKS`).
- Layer-key display shortcuts for `NUM` and `SYMBL` are encoded in `generate.py` — keep them in sync with keymap layer names.
- `generate.py` uses regex to parse the keymap; avoid breaking the DTS block structure (macros, behaviors, keymap sections).
- `build.yaml` defines the build matrix: `sofle_choc_pro_left` and `sofle_choc_pro_right`, both with the `sharp_mip` shield.

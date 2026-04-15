# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

ZMK firmware configuration for a split Corne keyboard (42 keys) on nice_nano_v2 boards with nice!view Gem displays, using Swiss German (CH-DE) layout.

## Build & Validation

- **Firmware builds** run via GitHub Actions (`.github/workflows/build.yml`), which delegates to `zmkfirmware/zmk/.github/workflows/build-user-config.yml@v0.3`. Push to trigger.
- **After editing `config/corne.keymap`**, run `python3 generate.py` to regenerate the keymap visualizer (`index.html`). This is the primary local validation step.
- **No test suite exists.** Validation is via visualizer generation and firmware build success.
- ZMK v0.3 docs: https://v0-3-branch.zmk.dev

## Architecture

**`config/corne.keymap`** is the source of truth. It defines:
- 6 layers: BASE (0), I3 (1), SYS (2), SYMBL (3), NUM (4), FUNC (5)
- Custom hold-tap behaviors (`ht`, `hml`/`hmr` for home-row mods, `hmln`/`hmrn` for modifier-only)
- Mod-morphs (`smi_grv`, `del_sqt`, `qus_uml`) that change behavior on shift
- Layer-switching macros (`sys_fnc`, `nav_num`) combining hold-layer with tap-toggle-off
- Bluetooth macros (`bt_clr_macro`, `bt_sel`) for profile management
- Key positions for left/right hand split at keys 0-5/12-17/24-29 vs 6-11/18-23/30-35, thumbs 36-41

**`config/ch-de.h`** defines Swiss German keycodes (`DE_*`) using HID usage codes with `RA()` (AltGr) and `LS()` (Shift) modifiers.

**`generate.py`** parses the keymap via regex and generates an interactive HTML visualizer. It is format-sensitive — maintain the DTS-style block structure in the keymap.

**`config/corne.conf`** sets runtime flags (BLE, display, nice!view Gem animation).

**`config/west.yml`** pins dependencies: ZMK v0.3 and nice-view-gem v0.3.0.

## Key Conventions

- When adding new `DE_*` keycodes, update both `config/ch-de.h` AND the label tables in `generate.py` (`DE_LABELS`, `DE_NAME_FALLBACKS`).
- Thumb-layer behavior is encoded in both the keymap macros and `generate.py` logic — keep them in sync.
- `generate.py` uses regex to parse the keymap; avoid breaking the DTS block structure (macros, behaviors, keymap sections).
- `build.yaml` defines the build matrix: left and right halves with `nice_view_adapter nice_view_gem` shields and ZMK Studio enabled on the left half.

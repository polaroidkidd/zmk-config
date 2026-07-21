# Copilot instructions

## Build and verification

- Run `python3 generate.py` from the repository root after changing `config/sofle_choc_pro.keymap` or the visualizer logic. The script reads `config/sofle_choc_pro.keymap` and rewrites `index.html`.
- Firmware builds are driven by `.github/workflows/build.yml`, which delegates to ZMK's `build-user-config.yml@v0.3` workflow. The actual build matrix lives in `build.yaml`.
- `build.yaml` currently defines `sofle_choc_pro_left` and `sofle_choc_pro_right` builds, both with the `nice_view_disp` shield.
- There is no dedicated test suite or lint target in this repository. Validation is done by rerunning `python3 generate.py` for the visualizer and by the ZMK firmware build for DTS/config changes. There is no single-test entry point.

## High-level architecture

- `config/sofle_choc_pro.keymap` is the source of truth for keyboard behavior. It defines the Sofle CH-DE root, i3, system, symbol, and number layers.
- `config/ch-de.h` provides the Swiss German `DE_*` keycodes used throughout the keymap. If a binding uses a new locale-specific token, it usually belongs in this header as well as the keymap.
- `config/sofle_choc_pro.conf` contains runtime feature flags for this keyboard, including BLE tuning and the Bluetooth keyboard name.
- `config/west.yml` pins external dependencies: ZMK itself comes from `zmkfirmware` at `v0.3`, the display module comes from `M165437/nice-view-gem`, and the Sofle Choc Pro board comes from `Keebart/zmk-config`. `zephyr/module.yml` exposes this repository as a Zephyr module with `board_root: .`.
- `generate.py` is a repository-specific tool, not a generic helper. It parses `config/sofle_choc_pro.keymap` directly with regexes, extracts layer and behavior metadata, and generates `index.html`, including an info box for recognized macros, combos, and mod-morph behaviors.
- `boards/shields/` is available for local board or shield definitions because the repo is a Zephyr module, but it is currently just a placeholder.

## Key conventions

- Keep `config/sofle_choc_pro.keymap` in the current DTS-style structure. `generate.py` depends on recognizable `behaviors { ... }`, `macros { ... }`, and `keymap { ... }` blocks plus the `#define` layer indices near the top of the file.
- The generator is format-sensitive in a few places: it expects the layer defines, `#binding-cells`, and the closing indentation pattern used by the current keymap. If you heavily reformat the keymap, check `python3 generate.py` immediately.
- Layer-key display shortcuts for `NUM` and `SYMBL` are defined in `generate.py` via `LAYER_KEY_LABELS`. If you rename those layers, update the display mapping as well.
- When adding new `DE_*` symbols, aliases, or modifier combinations, update both `config/ch-de.h` and the label tables in `generate.py` (`DE_LABELS`, `STD_LABELS`, and related mappings) so the visualizer renders readable labels instead of raw token names.

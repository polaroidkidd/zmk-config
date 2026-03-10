# Copilot instructions

## Build and verification

- Run `python3 generate.py` from the repository root after changing `config/corne.keymap` or the visualizer logic. The script reads `config/corne.keymap` and rewrites `index.html`.
- Firmware builds are driven by `.github/workflows/build.yml`, which delegates to ZMK's `build-user-config.yml@v0.3` workflow. The actual build matrix lives in `build.yaml`.
- `build.yaml` currently defines two `nice_nano_v2` builds for `corne_left` and `corne_right`, both with `nice_view_adapter nice_view_gem`; the left build also adds `-DCONFIG_ZMK_STUDIO=y`.
- There is no dedicated test suite or lint target in this repository. Validation is done by rerunning `python3 generate.py` for the visualizer and by the ZMK firmware build for DTS/config changes. There is no single-test entry point.

## High-level architecture

- `config/corne.keymap` is the source of truth for keyboard behavior. It defines six layers (`DEFAULT`, `NAV`, `SYM`, `CH_DE`, `NUM`, `FUNC`), custom macros/behaviors, and the conditional layer that activates `CH_DE` when `NAV` and `SYM` are both active.
- `config/ch-de.h` provides the Swiss German `DE_*` keycodes used throughout the keymap. If a binding uses a new locale-specific token, it usually belongs in this header as well as the keymap.
- `config/corne.conf` contains runtime feature flags for this keyboard, including BLE tuning and the nice!view Gem display settings.
- `config/west.yml` pins external dependencies: ZMK itself comes from `zmkfirmware` at `v0.3`, and the display module comes from `M165437/nice-view-gem`. `zephyr/module.yml` exposes this repository as a Zephyr module with `board_root: .`.
- `generate.py` is a repository-specific tool, not a generic helper. It parses `config/corne.keymap` directly with regexes, extracts layer and behavior metadata, and generates `index.html`, including the info box for conditional layers, macros, and mod-morph behaviors.
- `boards/shields/` is available for local board or shield definitions because the repo is a Zephyr module, but it is currently just a placeholder.

## Key conventions

- Keep `config/corne.keymap` in the current DTS-style structure. `generate.py` depends on recognizable `macros { ... }`, `behaviors { ... }`, and `keymap { ... }` blocks plus the `#define` layer indices near the top of the file.
- The generator is format-sensitive in a few places: it expects the layer defines, `#binding-cells`, and the closing indentation pattern used by the current keymap. If you heavily reformat the keymap, check `python3 generate.py` immediately.
- The thumb-layer behavior is encoded twice: once in the keymap macros (`sym_fnc`, `nav_num`, `ton`, `toff`) and again in `generate.py` via `LAYER_SIDES` and the info-box parsing. If you rename layers or change thumb semantics, update both places.
- The `CH_DE` layer is not toggled directly; it is a tri-layer derived from `NAV + SYM`. Preserve that relationship unless you intentionally want to change both firmware behavior and the generated visualizer text.
- When adding new `DE_*` symbols, aliases, or modifier combinations, update both `config/ch-de.h` and the label tables in `generate.py` (`DE_LABELS`, `STD_LABELS`, and related mappings) so the visualizer renders readable labels instead of raw token names.

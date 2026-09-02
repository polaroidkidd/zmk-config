# Repository Guidelines

## Project Structure & Module Organization

This repository is a ZMK user configuration for a Sofle Choc Pro split keyboard with Swiss German (CH-DE) keycodes. The active firmware sources live in `config/`: `sofle_choc_pro.keymap` defines layers, macros, and behaviors; `sofle_choc_pro.conf` holds runtime options; `ch-de.h` defines locale-specific `DE_*` keycodes; `west.yml` pins ZMK and module dependencies. `build.yaml` provides the GitHub Actions build matrix, currently targeting `sofle_choc_pro_left` and `sofle_choc_pro_right` with the `sharp_mip` shield. `generate.py` builds the visualizer `index.html`, and `layout.png` is a visual asset. Treat `.zmk/`, `zephyr/`, `__pycache__/`, and generated HTML as local/generated artifacts unless intentionally updating tooling.

## Build, Test, and Development Commands

- `python3 generate.py`: regenerates the keymap visualizer from `config/sofle_choc_pro.keymap`.
- GitHub Actions build firmware on `push` and `workflow_dispatch` through `.github/workflows/build.yml`, which delegates to ZMK `build-user-config.yml@v0.3`.
- `git status --short`: check that only intended source and generated files changed before committing.

## Coding Style & Naming Conventions

Preserve the existing DTS-style structure in keymaps: top-level layer `#define`s, `behaviors`, `macros`, and `keymap` blocks are parser-sensitive. Use existing indentation and naming patterns such as uppercase layer constants (`ROOT`, `SYS`, `SYMBL`) and descriptive behavior labels (`ue_cap`, `i3_gui`). For new Swiss German symbols, add `DE_*` definitions in `config/ch-de.h` and matching readable labels in `generate.py` tables.

## Testing Guidelines

There is no dedicated local test suite or coverage target. Validate keymap and visualizer changes by running `python3 generate.py` once the active keymap path is correct, then inspect the generated `index.html` for layer labels and custom symbols. Firmware validation is the GitHub Actions build; confirm both halves produce artifacts before flashing.

## Commit & Pull Request Guidelines

Recent commits use short imperative subjects, often lowercase, with optional scope such as `sofle: Add Shift+umlaut -> capital Ä/Ö/Ü`. Keep subjects specific to the layout or behavior changed. Pull requests should describe affected keyboard/layers, list validation performed, mention generated visualizer updates, and include screenshots when visual layout changes are relevant.

## Agent-Specific Instructions

Before editing, check current filenames rather than assuming generic keyboard filenames. Do not modify generated dependency directories such as `.zmk/` or `zephyr/` for ordinary keymap work.

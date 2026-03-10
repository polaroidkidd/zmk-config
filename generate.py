#!/usr/bin/env python3
"""Parse config/corne.keymap and generate index.html keymap visualizer.

Usage: python3 generate.py
"""

import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
KEYMAP_PATH = SCRIPT_DIR / "config" / "corne.keymap"
OUTPUT_PATH = SCRIPT_DIR / "index.html"

# ── Display label tables ────────────────────────────────────────────

MODIFIER_KEYS = frozenset({
    "TAB", "LSHFT", "LCTRL", "LGUI", "LALT",
    "RSHFT", "RCTRL", "RGUI", "RALT",
})

# Which side of the keyboard activates each layer.
# "left"/"right" = activated by that thumb key; "center" = default layer.
LAYER_SIDES = {
    "DEFAULT": "center",
    "CH_DE":   "center",   # conditional (NAV+SYM)
    "NAV":     "left",   # right thumb (mod_func)
    "SYM":     "right",    # left thumb (mod_num)
    "NUM":     "left",    # derived from SYM
    "FUNC":    "right",   # derived from NAV (mod_func)
}

DE_LABELS = {
    "DE_Q": "Q", "DE_W": "W", "DE_E": "E", "DE_R": "R", "DE_T": "T",
    "DE_Z": "Z", "DE_U": "U", "DE_I": "I", "DE_O": "O", "DE_P": "P",
    "DE_A": "A", "DE_S": "S", "DE_D": "D", "DE_F": "F", "DE_G": "G",
    "DE_H": "H", "DE_J": "J", "DE_K": "K", "DE_L": "L",
    "DE_Y": "Y", "DE_X": "X", "DE_C": "C", "DE_V": "V", "DE_B": "B",
    "DE_N": "N", "DE_M": "M",
    "DE_N0": "0", "DE_N1": "1", "DE_N2": "2", "DE_N3": "3", "DE_N4": "4",
    "DE_N5": "5", "DE_N6": "6", "DE_N7": "7", "DE_N8": "8", "DE_N9": "9",
    "DE_MINUS": "-", "DE_COMMA": ",", "DE_DOT": ".", "DE_PERIOD": ".",
    "DE_EXCL": "!", "DE_EXCLAMATION": "!",
    "DE_AT": "@", "DE_AT_SIGN": "@",
    "DE_HASH": "#", "DE_POUND": "#",
    "DE_DLLR": "$", "DE_DOLLAR": "$",
    "DE_PRCNT": "%", "DE_PERCENT": "%",
    "DE_CARET": "^",
    "DE_AMPS": "&", "DE_AMPERSAND": "&",
    "DE_LPAR": "(", "DE_RPAR": ")",
    "DE_PLUS": "+", "DE_EQUAL": "=",
    "DE_LBKT": "[", "DE_RBKT": "]",
    "DE_LBRC": "{", "DE_RBRC": "}",
    "DE_BSLH": "\\", "DE_BACKSLASH": "\\",
    "DE_PIPE": "|", "DE_TILDE": "~", "DE_GRAVE": "`",
    "DE_SQT": "'", "DE_SINGLE_QUOTE": "'",
    "DE_DQT": '"', "DE_DOUBLE_QUOTES": '"',
    "DE_FSLH": "/", "DE_SLASH": "/",
    "DE_UNDER": "_", "DE_UNDERSCORE": "_",
    "DE_QMARK": "?", "DE_QUESTION": "?",
    "DE_A_UMLAUT": "\u00e4", "DE_O_UMLAUT": "\u00f6", "DE_U_UMLAUT": "\u00fc",
    "DE_C_CEDILLA": "\u00e7",
    "DE_COLON": ":", "DE_SEMI": ";", "DE_SEMICOLON": ";",
    "DE_LT": "<", "DE_LESS_THAN": "<",
    "DE_GT": ">", "DE_GREATER_THAN": ">",
}

STD_LABELS = {
    "TAB": "TAB", "ESCAPE": "ESC", "ESC": "ESC",
    "DEL": "DEL", "DELETE": "DEL",
    "BACKSPACE": "BS", "BSPC": "BS",
    "SPACE": "SPACE", "RET": "RET", "ENTER": "RET",
    "LSHFT": "LSHFT", "RSHFT": "RSHFT",
    "LCTRL": "LCTRL", "RCTRL": "RCTRL",
    "LGUI": "LGUI", "RGUI": "RGUI",
    "LALT": "LALT", "RALT": "RALT",
    "UP": "\u2191", "DOWN": "\u2193", "LEFT": "\u2190", "RIGHT": "\u2192",
    "PG_UP": "PG UP", "PG_DN": "PG DN",
    "HOME": "HOME", "END": "END",
    "F1": "F1", "F2": "F2", "F3": "F3", "F4": "F4",
    "F5": "F5", "F6": "F6", "F7": "F7", "F8": "F8",
    "F9": "F9", "F10": "F10", "F11": "F11", "F12": "F12",
    "N0": "0", "N1": "1", "N2": "2", "N3": "3", "N4": "4",
    "N5": "5", "N6": "6", "N7": "7", "N8": "8", "N9": "9",
    "PIPE": "|", "LT": "<", "GT": ">",
}

# Swiss German shifted values for number keys
CH_NUM_SHIFTS = {
    "1": "+", "2": '"', "3": "*", "4": "\u00e7", "5": "%",
    "6": "&", "7": "/", "8": "(", "9": ")", "0": "=",
}

MOD_PREFIXES = {
    "LG": "\u2318", "RG": "\u2318",
    "LA": "Alt", "RA": "Alt",
    "LC": "Ctrl", "RC": "Ctrl",
    "LS": "\u21e7", "RS": "\u21e7",
}

BRACKET_PAIRS = {
    ("DE_LPAR", "DE_RPAR"): "( )",
    ("DE_LBKT", "DE_RBKT"): "[ ]",
    ("DE_LBRC", "DE_RBRC"): "{ }",
}


# ── Keymap parser ───────────────────────────────────────────────────

class KeymapParser:
    def __init__(self, text):
        self.text = text
        self.layer_names = {}     # index -> display name
        self.behaviors = {}       # name -> behavior metadata
        self.binding_cells = {    # name -> number of params
            "kp": 1, "none": 0, "trans": 0,
            "mo": 1, "lt": 2, "mt": 2,
            "sk": 1, "sl": 1, "bt": 1,
            "studio_unlock": 0,
        }

    def parse(self):
        self._parse_defines()
        self._parse_behaviors()
        self._parse_macros()
        return self._parse_layers()

    # ── Step 1: extract #define layer names ──

    def _parse_defines(self):
        for m in re.finditer(r"#define\s+(\w+)\s+(\d+)", self.text):
            self.layer_names[int(m.group(2))] = m.group(1)

    # ── Step 2: parse behaviors { ... } block ──

    def _parse_behaviors(self):
        m = re.search(r"behaviors\s*\{(.*?)\n\s{8}\};", self.text, re.DOTALL)
        if not m:
            return
        self._parse_behavior_block(m.group(1))

    def _parse_macros(self):
        m = re.search(r"macros\s*\{(.*?)\n\s{8}\};", self.text, re.DOTALL)
        if not m:
            return
        self._parse_behavior_block(m.group(1))

    def _parse_behavior_block(self, block_text):
        for m in re.finditer(r"(\w+)\s*:\s*[\w\s]*\{(.*?)\};", block_text, re.DOTALL):
            name = m.group(1)
            body = m.group(2)
            beh = {}

            compat = re.search(r'compatible\s*=\s*"([^"]+)"', body)
            if compat:
                beh["compat"] = compat.group(1)

            cells = re.search(r"#binding-cells\s*=\s*<(\d+)>", body)
            if cells:
                beh["cells"] = int(cells.group(1))
                self.binding_cells[name] = int(cells.group(1))

            bindings = re.search(r"bindings\s*=\s*(.+?);", body, re.DOTALL)
            if bindings:
                beh["bindings_raw"] = bindings.group(1).strip()

            self.behaviors[name] = beh

    # ── Step 3: parse keymap layers ──

    def _parse_layers(self):
        km = re.search(
            r'keymap\s*\{[^}]*compatible\s*=\s*"zmk,keymap"\s*;(.*?)^\s{8}\};',
            self.text, re.DOTALL | re.MULTILINE,
        )
        if not km:
            raise ValueError("Could not find keymap section")

        layers = []
        layer_re = re.compile(r"(\w+)\s*\{[^<]*bindings\s*=\s*<(.*?)>", re.DOTALL)
        for i, m in enumerate(layer_re.finditer(km.group(1))):
            bindings_text = m.group(2)
            display_name = self.layer_names.get(i, m.group(1).upper())
            bindings = self._tokenize_bindings(bindings_text)
            keys = [self._resolve_binding(b) for b in bindings]
            layers.append({"name": display_name, "keys": keys})
        return layers

    # ── Binding tokenizer ──

    def _tokenize_bindings(self, text):
        text = " ".join(text.split())
        tokens = self._tokenize(text)

        bindings = []
        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if tok.startswith("&"):
                behavior = tok[1:]
                cells = self.binding_cells.get(behavior, 0)
                params = []
                for _ in range(cells):
                    i += 1
                    if i < len(tokens):
                        params.append(tokens[i])
                bindings.append((behavior, params))
            i += 1
        return bindings

    @staticmethod
    def _tokenize(text):
        """Split binding text into tokens, handling nested parentheses."""
        tokens = []
        i = 0
        while i < len(text):
            if text[i].isspace():
                i += 1
                continue
            # Read a token (& + word, or word, possibly followed by balanced parens)
            start = i
            while i < len(text) and not text[i].isspace() and text[i] != "(":
                i += 1
            if i < len(text) and text[i] == "(":
                depth = 0
                while i < len(text):
                    if text[i] == "(":
                        depth += 1
                    elif text[i] == ")":
                        depth -= 1
                        if depth == 0:
                            i += 1
                            break
                    i += 1
            tokens.append(text[start:i])
        return tokens

    # ── Binding resolver ──

    def _resolve_binding(self, binding):
        behavior, params = binding

        if behavior == "none":
            return {"c": "none-key"}

        if behavior == "trans":
            return {"t": "\u25bd", "c": "none-key"}

        if behavior == "kp":
            return self._resolve_kp(params[0] if params else "")

        if behavior == "mo":
            return {"t": self._layer_label(params[0] if params else ""), "c": "layer-key"}

        if behavior in ("ton", "toff"):
            action = "tog ON" if behavior == "ton" else "tog OFF"
            return {"t": self._layer_label(params[0] if params else ""), "h": action, "c": "layer-key"}

        if behavior == "studio_unlock":
            return {"t": "\U0001f513", "h": "studio", "c": "special"}

        if behavior == "bt":
            cmd = params[0] if params else ""
            return {"t": cmd.replace("BT_", "BT "), "c": "bt-key"}

        # Look up parsed behavior metadata
        beh_info = self.behaviors.get(behavior, {})
        compat = beh_info.get("compat", "")

        if compat == "zmk,behavior-mod-morph":
            return self._resolve_mod_morph(beh_info)

        if compat in ("zmk,behavior-macro", "zmk,behavior-macro-one-param"):
            return self._resolve_macro(beh_info, params)

        if compat == "zmk,behavior-hold-tap":
            return self._resolve_hold_tap(beh_info, params)

        # Fallback: show behavior name + params
        label = behavior
        if params:
            label += " " + " ".join(params)
        return {"t": label}

    def _resolve_kp(self, key):
        # Modifier wrapping: LG(KEY), LA(KEY), etc. — supports nesting
        mod_m = re.match(r"(LG|RG|LA|RA|LC|RC|LS|RS)\((.+)\)$", key)
        if mod_m:
            mod, inner = mod_m.group(1), mod_m.group(2)
            prefix = MOD_PREFIXES[mod]
            # Recursively resolve inner key (handles LG(LC(A)) etc.)
            inner_resolved = self._resolve_kp(inner)
            inner_label = inner_resolved.get("t", inner)
            if inner_label == "SPACE":
                inner_label = "SPC"
            label = prefix + inner_label
            if inner in MODIFIER_KEYS:
                return {"t": label, "c": "modifier"}
            return {"t": label}

        label = self._key_label(key)
        result = {"t": label}

        if key in MODIFIER_KEYS:
            result["c"] = "modifier"

        # Swiss German shift labels for number keys
        if label in CH_NUM_SHIFTS:
            result["s"] = CH_NUM_SHIFTS[label]

        return result

    def _resolve_mod_morph(self, beh_info):
        raw = beh_info.get("bindings_raw", "")
        parts = re.findall(r"<([^>]+)>", raw)
        if len(parts) < 2:
            return {"t": "??", "c": "special"}

        tap_tokens = parts[0].strip().split()
        shift_tokens = parts[1].strip().split()

        tap_code = tap_tokens[-1] if tap_tokens else ""
        shift_code = shift_tokens[-1] if shift_tokens else ""

        # Check for bracket pairs
        pair_label = BRACKET_PAIRS.get((tap_code, shift_code))
        if pair_label:
            return {"t": pair_label, "s": self._key_label(shift_code), "c": "special"}

        tap_label = self._key_label(tap_code)
        shift_label = self._key_label(shift_code)
        return {"t": tap_label, "s": shift_label, "c": "special"}

    def _resolve_macro(self, beh_info, params):
        raw = beh_info.get("bindings_raw", "")

        # Detect hold-layer + toggle-layer macro pattern
        mo_m = re.search(r"&mo\s+(\w+)", raw)
        toggle_m = re.search(r"&t(on|off)\s+(\w+)", raw)
        if mo_m and toggle_m:
            hold_layer = self._layer_label(mo_m.group(1))
            tap_layer = self._layer_label(toggle_m.group(2))
            return {"t": tap_layer, "h": hold_layer, "c": "layer-key"}

        # Detect BT_CLR macro
        if "BT_CLR" in raw:
            return {"t": "BT CLR", "c": "bt-key"}

        # Detect BT_SEL macro
        if "BT_SEL" in raw:
            idx = params[0] if params else "?"
            return {"t": f"BT {idx}", "c": "bt-key"}

        # Fallback
        return {"t": beh_info.get("compat", "macro")}

    def _resolve_hold_tap(self, beh_info, params):
        raw = beh_info.get("bindings_raw", "")
        parts = re.findall(r"<([^>]+)>", raw)
        if len(parts) < 2:
            return {"t": "??"}

        hold_beh_name = parts[0].strip().lstrip("&").split()[0]
        tap_beh_name = parts[1].strip().lstrip("&").split()[0]

        # Resolve tap (second param -> tap behavior)
        tap_param = params[1] if len(params) > 1 else ""
        if tap_beh_name == "kp":
            tap_display = self._resolve_kp(tap_param)
        else:
            tap_display = {"t": tap_param}

        # Resolve hold (first param -> hold behavior)
        hold_param = params[0] if params else ""
        if hold_beh_name == "kp":
            hold_label = self._resolve_kp(hold_param).get("t", hold_param)
            css_class = ""
        else:
            hold_beh_info = self.behaviors.get(hold_beh_name, {})
            hold_raw = hold_beh_info.get("bindings_raw", "")

            if "BT_CLR" in hold_raw:
                hold_label = "BT CLR"
                css_class = "bt-key"
            elif "BT_SEL" in hold_raw:
                hold_label = f"BT {hold_param}"
                css_class = "bt-key"
            else:
                hold_label = hold_beh_name
                css_class = ""

        result = dict(tap_display)
        result["h"] = hold_label
        if css_class:
            result["c"] = css_class
        return result

    # ── Helpers ──

    def _key_label(self, key):
        if key in DE_LABELS:
            return DE_LABELS[key]
        if key in STD_LABELS:
            return STD_LABELS[key]
        if key.startswith("DE_"):
            return key[3:]
        return key

    def _layer_label(self, name_or_idx):
        try:
            idx = int(name_or_idx)
            return self.layer_names.get(idx, str(idx))
        except ValueError:
            return name_or_idx


# ── JS generation ───────────────────────────────────────────────────

def key_to_js(k):
    parts = []
    for field in ("t", "s", "h", "c"):
        if field in k:
            parts.append(f"{field}:{json.dumps(k[field], ensure_ascii=False)}")
    return "{" + ",".join(parts) + "}"


def layers_to_js(layers):
    lines = ["const LAYERS = ["]
    for layer in layers:
        side = json.dumps(LAYER_SIDES.get(layer["name"], "left"))
        lines.append(f"  {{ name: {json.dumps(layer['name'])}, side: {side}, keys: [")
        keys = layer["keys"]
        for row in range(3):
            start = row * 12
            row_strs = [key_to_js(k) for k in keys[start : start + 12]]
            lines.append(f"    // Row {row}")
            lines.append(f"    {', '.join(row_strs)},")
        thumb_strs = [key_to_js(k) for k in keys[36:42]]
        lines.append("    // Thumb")
        lines.append(f"    {', '.join(thumb_strs)},")
        lines.append("  ]},")
    lines.append("];")
    return "\n".join(lines)


# ── HTML template ───────────────────────────────────────────────────

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Corne Keymap Visualizer</title>
<style>
  :root {
    --bg: #1a1a2e;
    --surface: #16213e;
    --key-bg: #0f3460;
    --key-border: #1a5276;
    --key-text: #e0e0e0;
    --key-sub: #8899aa;
    --accent: #e94560;
    --tab-active: #e94560;
    --tab-inactive: #16213e;
    --tab-hover: #1a2a4e;
    --tab-text: #8899aa;
    --title-color: #fff;
    --label-color: #fff;
    --hold-color: #6fcf97;
    --shift-color: #f0a060;
    --hold-bg: #1b4332;
    --hold-border: #2d6a4f;
    --key-hover: #1a4a7a;
    --none-bg: #0a0a1a;
    --none-border: #1a1a2e;
    --mod-bg: #2a1a4e;
    --mod-border: #533483;
    --bt-bg: #1a3a5e;
    --bt-border: #2a6090;
    --special-bg: #3a1a1e;
    --special-border: #6a2a3e;
    --swatch-normal-bg: #0f3460;
    --swatch-normal-border: #1a5276;
  }
  [data-theme="light"] {
    --bg: #f0f2f5;
    --surface: #fff;
    --key-bg: #fff;
    --key-border: #c8cdd3;
    --key-text: #333;
    --key-sub: #666;
    --accent: #d63050;
    --tab-active: #d63050;
    --tab-inactive: #e8eaed;
    --tab-hover: #dde0e4;
    --tab-text: #666;
    --title-color: #1a1a2e;
    --label-color: #222;
    --hold-color: #1a7a42;
    --shift-color: #c06020;
    --hold-bg: #e0f5ea;
    --hold-border: #8bc9a0;
    --key-hover: #e8f0ff;
    --none-bg: #eaeaea;
    --none-border: #ddd;
    --mod-bg: #ede0f8;
    --mod-border: #b09ad0;
    --bt-bg: #dde8f8;
    --bt-border: #90b0d0;
    --special-bg: #fce8ea;
    --special-border: #d09098;
    --swatch-normal-bg: #fff;
    --swatch-normal-border: #c8cdd3;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
    background: var(--bg);
    color: var(--key-text);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 24px;
    transition: background 0.3s, color 0.3s;
  }
  .header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 4px;
  }
  h1 {
    font-size: 1.4rem;
    font-weight: 600;
    color: var(--title-color);
  }
  .theme-toggle {
    background: var(--surface);
    border: 1px solid var(--key-border);
    border-radius: 20px;
    width: 48px;
    height: 26px;
    cursor: pointer;
    position: relative;
    transition: all 0.3s;
    flex-shrink: 0;
  }
  .theme-toggle::after {
    content: '';
    position: absolute;
    top: 3px;
    left: 3px;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: var(--accent);
    transition: transform 0.3s;
  }
  [data-theme="light"] .theme-toggle::after {
    transform: translateX(22px);
  }
  .theme-icon {
    position: absolute;
    top: 4px;
    font-size: 0.75rem;
    line-height: 18px;
    pointer-events: none;
    z-index: 1;
  }
  .theme-icon.moon { left: 6px; }
  .theme-icon.sun { right: 5px; }
  .subtitle {
    font-size: 0.8rem;
    color: var(--key-sub);
    margin-bottom: 20px;
  }
  .layer-tabs {
    display: flex;
    gap: 4px;
    margin-bottom: 20px;
    flex-wrap: wrap;
    justify-content: center;
  }
  .layer-tab {
    padding: 8px 18px;
    border: 1px solid var(--key-border);
    border-radius: 6px 6px 0 0;
    background: var(--tab-inactive);
    color: var(--tab-text);
    cursor: pointer;
    font-family: inherit;
    font-size: 0.8rem;
    font-weight: 500;
    transition: all 0.15s;
    user-select: none;
  }
  .layer-tab:hover { background: var(--tab-hover); color: var(--title-color); }
  .layer-tab.active {
    background: var(--tab-active);
    color: #fff;
    border-color: var(--tab-active);
  }
  .keyboard-container {
    position: relative;
    width: 100%;
    max-width: 900px;
  }
  .keyboard {
    display: none;
    gap: 40px;
  }
  .keyboard.active { display: flex; flex-direction: column; align-items: center; }
  .row {
    display: flex;
    gap: 4px;
    justify-content: center;
  }
  .split-gap { width: 30px; }
  .key {
    width: 64px;
    height: 54px;
    background: var(--key-bg);
    border: 1px solid var(--key-border);
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3px 4px;
    position: relative;
    transition: all 0.15s;
    cursor: default;
  }
  .key:hover {
    background: var(--key-hover);
    border-color: var(--accent);
    transform: translateY(-1px);
  }
  .key .label {
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--label-color);
    text-align: center;
    line-height: 1.15;
    word-break: break-all;
  }
  .key .hold-label {
    font-size: 0.55rem;
    color: var(--hold-color);
    text-align: center;
    line-height: 1.1;
    margin-top: 1px;
  }
  .key .shift-label {
    font-size: 0.52rem;
    color: var(--shift-color);
    position: absolute;
    top: 2px;
    right: 4px;
  }
  .key.none-key {
    background: var(--none-bg);
    border-color: var(--none-border);
    opacity: 0.4;
  }
  .key.modifier {
    background: var(--mod-bg);
    border-color: var(--mod-border);
  }
  .key.layer-key {
    background: var(--hold-bg);
    border-color: var(--hold-border);
  }
  .key.bt-key {
    background: var(--bt-bg);
    border-color: var(--bt-border);
  }
  .key.special {
    background: var(--special-bg);
    border-color: var(--special-border);
  }
  .thumb-row {
    display: flex;
    gap: 4px;
    justify-content: center;
    margin-top: -8px;
  }
  .thumb-spacer { width: 204px; }
  .legend {
    display: flex;
    gap: 16px;
    margin-top: 24px;
    flex-wrap: wrap;
    justify-content: center;
  }
  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.7rem;
    color: var(--key-sub);
  }
  .legend-swatch {
    width: 14px;
    height: 14px;
    border-radius: 3px;
    border: 1px solid;
  }
  .info-box {
    margin-top: 20px;
    padding: 12px 20px;
    background: var(--surface);
    border: 1px solid var(--key-border);
    border-radius: 8px;
    font-size: 0.72rem;
    color: var(--key-sub);
    max-width: 900px;
    line-height: 1.6;
    transition: all 0.3s;
  }
  .info-box strong { color: var(--title-color); }
  .print-btn {
    background: var(--surface);
    border: 1px solid var(--key-border);
    border-radius: 6px;
    padding: 4px 12px;
    color: var(--key-text);
    font-family: inherit;
    font-size: 0.75rem;
    cursor: pointer;
    transition: all 0.15s;
  }
  .print-btn:hover { border-color: var(--accent); color: var(--accent); }
  @media (max-width: 700px) {
    .key { width: 48px; height: 44px; }
    .key .label { font-size: 0.6rem; }
    .split-gap { width: 16px; }
    .thumb-spacer { width: 152px; }
  }
  @media print {
    body { padding: 0; background: #fff; color: #333; }
    .header, .layer-tabs, .theme-toggle, .print-btn, .subtitle, .info-box { display: none !important; }
    #print-view { display: block !important; }
    .keyboard-container, #legend { display: none !important; }
  }
  #print-view {
    display: none;
    width: 100%;
    max-width: 1100px;
    margin: 0 auto;
  }
  #print-view .pv-title {
    text-align: center;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 4px;
    color: #222;
  }
  #print-view .pv-legend {
    display: flex;
    gap: 12px;
    justify-content: center;
    margin-bottom: 6px;
    font-size: 8px;
    color: #666;
    flex-wrap: wrap;
  }
  #print-view .pv-legend-item { display: flex; align-items: center; gap: 3px; }
  #print-view .pv-legend-swatch {
    width: 10px; height: 10px; border-radius: 2px; border: 1px solid;
    display: inline-block;
  }
  #print-view .pv-default {
    display: flex;
    justify-content: center;
    margin-bottom: 8px;
  }
  #print-view .pv-columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px 12px;
  }
  #print-view .pv-column {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  #print-view .pv-layer {
    page-break-inside: avoid;
  }
  #print-view .pv-layer-name {
    font-size: 10px;
    font-weight: 700;
    color: #333;
    margin-bottom: 2px;
    text-align: center;
  }
  #print-view .pv-row {
    display: flex;
    gap: 2px;
    justify-content: center;
  }
  #print-view .pv-gap { width: 12px; }
  #print-view .pv-thumb-spacer { width: 80px; }
  #print-view .pv-thumb { margin-top: -2px; }
  #print-view .pv-key {
    width: 38px;
    height: 28px;
    border: 1px solid #bbb;
    border-radius: 3px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 1px 2px;
    background: #fff;
    position: relative;
  }
  #print-view .pv-key.none-key { background: #f0f0f0; border-color: #ddd; opacity: 0.4; }
  #print-view .pv-key.modifier { background: #ede0f8; border-color: #b09ad0; }
  #print-view .pv-key.layer-key { background: #e0f5ea; border-color: #8bc9a0; }
  #print-view .pv-key.bt-key { background: #dde8f8; border-color: #90b0d0; }
  #print-view .pv-key.special { background: #fce8ea; border-color: #d09098; }
  #print-view .pv-key .pv-label { font-size: 7px; font-weight: 600; color: #222; text-align: center; line-height: 1.1; }
  #print-view .pv-key .pv-hold { font-size: 5.5px; color: #1a7a42; text-align: center; line-height: 1; }
  #print-view .pv-key .pv-shift { font-size: 5px; color: #c06020; position: absolute; top: 1px; right: 2px; }
</style>
</head>
<body>

<div class="header">
  <h1>Corne CH-DE Keymap</h1>
  <button class="theme-toggle" id="themeToggle" title="Toggle light/dark mode">
    <span class="theme-icon moon">&#9790;</span>
    <span class="theme-icon sun">&#9788;</span>
  </button>
  <button class="print-btn" onclick="printAll()">Print</button>
</div>
<p class="subtitle">Swiss German layout &middot; %%LAYER_COUNT%% layers &middot; 42 keys</p>

<div class="layer-tabs" id="tabs"></div>
<div class="keyboard-container" id="keyboards"></div>

<div class="legend" id="legend">
  <div class="legend-item"><div class="legend-swatch" style="background:var(--swatch-normal-bg);border-color:var(--swatch-normal-border);"></div> Normal</div>
  <div class="legend-item"><div class="legend-swatch" style="background:var(--mod-bg);border-color:var(--mod-border);"></div> Modifier</div>
  <div class="legend-item"><div class="legend-swatch" style="background:var(--hold-bg);border-color:var(--hold-border);"></div> Layer</div>
  <div class="legend-item"><div class="legend-swatch" style="background:var(--bt-bg);border-color:var(--bt-border);"></div> Bluetooth</div>
  <div class="legend-item"><div class="legend-swatch" style="background:var(--special-bg);border-color:var(--special-border);"></div> Special</div>
  <div class="legend-item"><span style="color:var(--hold-color);">green</span> = hold</div>
  <div class="legend-item"><span style="color:var(--shift-color);">orange</span> = shift</div>
</div>

%%INFO_BOX%%

<script>
// Theme toggle
const toggle = document.getElementById('themeToggle');
const root = document.documentElement;

function setTheme(theme) {
  root.setAttribute('data-theme', theme);
  localStorage.setItem('keymap-theme', theme);
}

toggle.addEventListener('click', () => {
  const current = root.getAttribute('data-theme');
  setTheme(current === 'light' ? 'dark' : 'light');
});

// Load saved preference or respect system preference
const saved = localStorage.getItem('keymap-theme');
if (saved) {
  setTheme(saved);
} else if (window.matchMedia('(prefers-color-scheme: light)').matches) {
  setTheme('light');
}

%%LAYERS_JS%%

const tabsEl = document.getElementById('tabs');
const kbsEl = document.getElementById('keyboards');

LAYERS.forEach((layer, li) => {
  // Tab
  const tab = document.createElement('button');
  tab.className = 'layer-tab' + (li === 0 ? ' active' : '');
  tab.textContent = layer.name;
  tab.onclick = () => {
    document.querySelectorAll('.layer-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.keyboard').forEach(k => k.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('kb-' + li).classList.add('active');
  };
  tabsEl.appendChild(tab);

  // Keyboard
  const kb = document.createElement('div');
  kb.className = 'keyboard' + (li === 0 ? ' active' : '');
  kb.id = 'kb-' + li;

  // Rows 0-2: 12 keys each (6 left + gap + 6 right)
  for (let r = 0; r < 3; r++) {
    const row = document.createElement('div');
    row.className = 'row';
    for (let c = 0; c < 12; c++) {
      if (c === 6) {
        const gap = document.createElement('div');
        gap.className = 'split-gap';
        row.appendChild(gap);
      }
      const ki = r * 12 + c;
      row.appendChild(makeKey(layer.keys[ki]));
    }
    kb.appendChild(row);
  }

  // Thumb row: 3 left + gap + 3 right
  const thumb = document.createElement('div');
  thumb.className = 'thumb-row';
  const spacerL = document.createElement('div');
  spacerL.className = 'thumb-spacer';
  thumb.appendChild(spacerL);
  for (let c = 0; c < 6; c++) {
    if (c === 3) {
      const gap = document.createElement('div');
      gap.className = 'split-gap';
      thumb.appendChild(gap);
    }
    const ki = 36 + c;
    thumb.appendChild(makeKey(layer.keys[ki]));
  }
  const spacerR = document.createElement('div');
  spacerR.className = 'thumb-spacer';
  thumb.appendChild(spacerR);
  kb.appendChild(thumb);

  kbsEl.appendChild(kb);
});

function makeKey(k) {
  const el = document.createElement('div');
  const cls = k.c || '';
  el.className = 'key' + (cls ? ' ' + cls : '');

  if (!k.t && !k.h) {
    el.innerHTML = '';
    return el;
  }

  let html = '';
  if (k.s) html += `<span class="shift-label">${esc(k.s)}</span>`;
  if (k.t) html += `<span class="label">${esc(k.t)}</span>`;
  if (k.h) html += `<span class="hold-label">${esc(k.h)}</span>`;
  el.innerHTML = html;
  return el;
}

function esc(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// Build print view with all layers on one page, single legend for mods
function printAll() {
  let pv = document.getElementById('print-view');
  if (!pv) {
    pv = document.createElement('div');
    pv.id = 'print-view';
    document.body.appendChild(pv);
  }

  let html = '<div class="pv-title">Corne CH-DE Keymap</div>';
  html += '<div class="pv-legend">';
  html += '<div class="pv-legend-item"><div class="pv-legend-swatch" style="background:#fff;border-color:#bbb;"></div> Normal</div>';
  html += '<div class="pv-legend-item"><div class="pv-legend-swatch" style="background:#ede0f8;border-color:#b09ad0;"></div> Mod</div>';
  html += '<div class="pv-legend-item"><div class="pv-legend-swatch" style="background:#e0f5ea;border-color:#8bc9a0;"></div> Layer</div>';
  html += '<div class="pv-legend-item"><div class="pv-legend-swatch" style="background:#dde8f8;border-color:#90b0d0;"></div> BT</div>';
  html += '<div class="pv-legend-item"><div class="pv-legend-swatch" style="background:#fce8ea;border-color:#d09098;"></div> Special</div>';
  html += '<span style="color:#1a7a42;">green</span>=hold <span style="color:#c06020;">orange</span>=shift';
  html += '</div>';
  function pvLayer(layer) {
    let h = '<div class="pv-layer">';
    h += `<div class="pv-layer-name">${esc(layer.name)}</div>`;
    for (let r = 0; r < 3; r++) {
      h += '<div class="pv-row">';
      for (let c = 0; c < 12; c++) {
        if (c === 6) h += '<div class="pv-gap"></div>';
        h += pvKey(layer.keys[r * 12 + c]);
      }
      h += '</div>';
    }
    h += '<div class="pv-row pv-thumb">';
    h += '<div class="pv-thumb-spacer"></div>';
    for (let c = 0; c < 6; c++) {
      if (c === 3) h += '<div class="pv-gap"></div>';
      h += pvKey(layer.keys[36 + c]);
    }
    h += '<div class="pv-thumb-spacer"></div>';
    h += '</div>';
    h += '</div>';
    return h;
  }

  // Default layer centered on top
  LAYERS.filter(l => l.side === 'center').forEach(layer => {
    html += '<div class="pv-default">' + pvLayer(layer) + '</div>';
  });

  // Non-default layers in two columns: left | right
  const leftLayers  = LAYERS.filter(l => l.side === 'left');
  const rightLayers = LAYERS.filter(l => l.side === 'right');

  html += '<div class="pv-columns">';
  html += '<div class="pv-column">';
  leftLayers.forEach(layer => { html += pvLayer(layer); });
  html += '</div>';
  html += '<div class="pv-column">';
  rightLayers.forEach(layer => { html += pvLayer(layer); });
  html += '</div>';
  html += '</div>';
  pv.innerHTML = html;
  window.print();
}

function pvKey(k) {
  const cls = k.c || '';
  let inner = '';
  if (k.s) inner += `<span class="pv-shift">${esc(k.s)}</span>`;
  if (k.t) inner += `<span class="pv-label">${esc(k.t)}</span>`;
  if (k.h) inner += `<span class="pv-hold">${esc(k.h)}</span>`;
  return `<div class="pv-key ${cls}">${inner}</div>`;
}
</script>
</body>
</html>
"""


# ── Info box generation ─────────────────────────────────────────────

def generate_info_box(text):
    """Generate the info box from conditional layers and behaviors."""
    parts = []

    # Conditional layers
    cl_match = re.search(
        r"if-layers\s*=\s*<(\w+)\s+(\w+)>;\s*then-layer\s*=\s*<(\w+)>;",
        text,
    )
    if cl_match:
        a, b, c = cl_match.group(1), cl_match.group(2), cl_match.group(3)
        parts.append(
            f"<strong>Conditional layer:</strong> {a} + {b} held together "
            f"&rarr; {c} layer activates"
        )

    # Macros with hold+toggle pattern
    macro_descs = []
    for m in re.finditer(
        r"(\w+)\s*:\s*[\w\s]*\{[^}]*"
        r"&macro_press\s+&mo\s+(\w+).*?"
        r"&macro_tap\s+&t(?:on|off)\s+(\w+).*?\};",
        text,
        re.DOTALL,
    ):
        name, hold, tap = m.group(1), m.group(2), m.group(3)
        macro_descs.append(f"{name} = hold {hold} + toggle {tap}")
    if macro_descs:
        parts.append(
            "<strong>Macros:</strong> " + " &middot; ".join(macro_descs)
        )

    # Mod-morphs
    morph_descs = []
    for m in re.finditer(
        r'(\w+)\s*:\s*[\w\s]*\{[^}]*compatible\s*=\s*"zmk,behavior-mod-morph"'
        r"[^}]*bindings\s*=\s*<([^>]+)>,\s*<([^>]+)>[^}]*\};",
        text,
        re.DOTALL,
    ):
        tap_tokens = m.group(2).strip().split()
        shift_tokens = m.group(3).strip().split()
        tap_code = tap_tokens[-1] if tap_tokens else "?"
        shift_code = shift_tokens[-1] if shift_tokens else "?"

        tap_label = DE_LABELS.get(tap_code, STD_LABELS.get(tap_code, tap_code))
        shift_label = DE_LABELS.get(shift_code, STD_LABELS.get(shift_code, shift_code))
        morph_descs.append(f"{tap_label}&rarr;{shift_label}")
    if morph_descs:
        parts.append(
            "<strong>Mod-morphs:</strong> Shift changes behavior &mdash; e.g. "
            + ", ".join(morph_descs)
        )

    if not parts:
        return ""

    return (
        '<div class="info-box">\n  '
        + "<br>\n  ".join(parts)
        + "\n</div>"
    )


# ── Main ────────────────────────────────────────────────────────────

def main():
    text = KEYMAP_PATH.read_text(encoding="utf-8")

    parser = KeymapParser(text)
    layers = parser.parse()

    layer_count = len(layers)
    layers_js = layers_to_js(layers)
    info_box = generate_info_box(text)

    html = HTML_TEMPLATE
    html = html.replace("%%LAYERS_JS%%", layers_js)
    html = html.replace("%%LAYER_COUNT%%", str(layer_count))
    html = html.replace("%%INFO_BOX%%", info_box)

    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"Generated {OUTPUT_PATH} ({layer_count} layers, {sum(len(l['keys']) for l in layers)} keys)")


if __name__ == "__main__":
    main()

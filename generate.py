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

CH_DE_PATH = SCRIPT_DIR / "config" / "ch-de.h"

MODIFIER_KEYS = frozenset({
    "TAB",
    "LEFT_SHIFT", "LSHIFT", "LSHFT", "RIGHT_SHIFT", "RSHIFT", "RSHFT",
    "LEFT_CONTROL", "LCTRL", "RIGHT_CONTROL", "RCTRL",
    "LEFT_ALT", "LALT", "RIGHT_ALT", "RALT",
    "LEFT_GUI", "LGUI", "LEFT_WIN", "LWIN", "LEFT_COMMAND", "LCMD", "LEFT_META", "LMETA",
    "RIGHT_GUI", "RGUI", "RIGHT_WIN", "RWIN", "RIGHT_COMMAND", "RCMD", "RIGHT_META", "RMETA",
})

DIRECT_KEY_LABELS = {
    "ESCAPE": "ESC", "ESC": "ESC",
    "RETURN": "RET", "ENTER": "RET", "RET": "RET",
    "RETURN2": "RET2", "RET2": "RET2",
    "BACKSPACE": "BS", "BSPC": "BS",
    "DELETE": "DEL", "DEL": "DEL",
    "INSERT": "INS", "INS": "INS",
    "SPACE": "SPACE", "TAB": "TAB",
    "HOME": "HOME", "END": "END",
    "PAGE_UP": "PG UP", "PG_UP": "PG UP",
    "PAGE_DOWN": "PG DN", "PG_DN": "PG DN",
    "UP_ARROW": "↑", "UP": "↑",
    "DOWN_ARROW": "↓", "DOWN": "↓",
    "LEFT_ARROW": "←", "LEFT": "←",
    "RIGHT_ARROW": "→", "RIGHT": "→",
    "LEFT_SHIFT": "LSHFT", "LSHIFT": "LSHFT", "LSHFT": "LSHFT",
    "RIGHT_SHIFT": "RSHFT", "RSHIFT": "RSHFT", "RSHFT": "RSHFT",
    "LEFT_CONTROL": "LCTRL", "LCTRL": "LCTRL",
    "RIGHT_CONTROL": "RCTRL", "RCTRL": "RCTRL",
    "LEFT_ALT": "LALT", "LALT": "LALT",
    "RIGHT_ALT": "RALT", "RALT": "RALT",
    "LEFT_GUI": "LGUI", "LGUI": "LGUI", "LEFT_WIN": "LGUI", "LWIN": "LGUI",
    "LEFT_COMMAND": "LGUI", "LCMD": "LGUI", "LEFT_META": "LGUI", "LMETA": "LGUI",
    "RIGHT_GUI": "RGUI", "RGUI": "RGUI", "RIGHT_WIN": "RGUI", "RWIN": "RGUI",
    "RIGHT_COMMAND": "RGUI", "RCMD": "RGUI", "RIGHT_META": "RGUI", "RMETA": "RGUI",
    "CAPSLOCK": "CAPS", "CAPS": "CAPS", "CLCK": "CAPS",
    "LOCKING_CAPS": "LCAPS", "LCAPS": "LCAPS",
    "SCROLLLOCK": "SLCK", "SLCK": "SLCK",
    "LOCKING_SCROLL": "LSLCK", "LSLCK": "LSLCK",
    "LOCKING_NUM": "LNLCK", "LNLCK": "LNLCK",
    "PRINTSCREEN": "PSCRN", "PSCRN": "PSCRN",
    "PAUSE_BREAK": "PAUSE",
    "ATTENTION": "ATTN",
    "CLEAR_AGAIN": "AGAIN",
    "SEPARATOR": "SEP",
    "K_APPLICATION": "APP", "K_APP": "APP",
    "K_CONTEXT_MENU": "MENU", "K_CMENU": "MENU",
    "K_EXECUTE": "EXEC", "K_EXEC": "EXEC",
    "K_CALCULATOR": "CALC", "K_CALC": "CALC",
    "K_PLAY_PAUSE": "PLAY/PAUSE", "K_PP": "PLAY/PAUSE",
    "C_PLAY_PAUSE": "PLAY/PAUSE", "C_PP": "PLAY/PAUSE",
    "C_VOLUME_UP": "VOL+", "C_VOL_UP": "VOL+",
    "K_VOLUME_UP": "VOL+", "K_VOL_UP": "VOL+",
    "K_VOLUME_UP2": "VOL+", "K_VOL_UP2": "VOL+",
    "C_VOLUME_DOWN": "VOL-", "C_VOL_DN": "VOL-",
    "K_VOLUME_DOWN": "VOL-", "K_VOL_DN": "VOL-",
    "K_VOLUME_DOWN2": "VOL-", "K_VOL_DN2": "VOL-",
    "C_MUTE": "MUTE", "K_MUTE": "MUTE", "K_MUTE2": "MUTE",
    "C_BRIGHTNESS_INC": "BRI+", "C_BRI_INC": "BRI+", "C_BRI_UP": "BRI+",
    "C_BRIGHTNESS_DEC": "BRI-", "C_BRI_DEC": "BRI-", "C_BRI_DN": "BRI-",
    "C_BRIGHTNESS_MINIMUM": "BRI MIN", "C_BRI_MIN": "BRI MIN",
    "C_BRIGHTNESS_MAXIMUM": "BRI MAX", "C_BRI_MAX": "BRI MAX",
    "C_BRIGHTNESS_AUTO": "BRI AUTO", "C_BRI_AUTO": "BRI AUTO",
    "C_BACKLIGHT_TOGGLE": "BKLT TOG", "C_BKLT_TOG": "BKLT TOG",
    "C_FAST_FORWARD": "FF", "C_FF": "FF",
    "C_REWIND": "REW", "C_RW": "REW",
    "C_RECORD": "REC", "C_REC": "REC",
    "C_RANDOM_PLAY": "SHUFFLE", "C_SHUFFLE": "SHUFFLE",
    "C_CAPTIONS": "SUBS", "C_SUBTITLES": "SUBS",
    "C_POWER": "PWR", "C_PWR": "PWR", "K_POWER": "PWR", "K_PWR": "PWR",
    "C_SLEEP": "SLEEP", "K_SLEEP": "SLEEP", "C_SLEEP_MODE": "SLEEP MODE",
    "C_AC_NEXT_KEYBOARD_LAYOUT_SELECT": "GLOBE", "GLOBE": "GLOBE",
    "KP_NUMLOCK": "KP NL", "KP_NUM": "KP NL", "KP_NLCK": "KP NL",
    "KP_CLEAR": "KP CLR", "CLEAR2": "CLR",
    "KP_ENTER": "KP RET",
    "KP_PLUS": "KP +",
    "KP_MINUS": "KP -", "KP_SUBTRACT": "KP -",
    "KP_MULTIPLY": "KP *", "KP_ASTERISK": "KP *",
    "KP_DIVIDE": "KP /", "KP_SLASH": "KP /",
    "KP_EQUAL": "KP =", "KP_EQUAL_AS400": "KP =",
    "KP_DOT": "KP .", "KP_COMMA": "KP ,",
    "KP_LEFT_PARENTHESIS": "KP (", "KP_LPAR": "KP (",
    "KP_RIGHT_PARENTHESIS": "KP )", "KP_RPAR": "KP )",
}

WORD_LABELS = {
    "APPLICATION": "APP",
    "APPLICATIONS": "APPS",
    "AUDIO": "AUDIO",
    "BACKLIGHT": "BKLT",
    "BOOKMARKS": "BOOKMARKS",
    "BRIGHTNESS": "BRI",
    "CALCULATOR": "CALC",
    "CALENDAR": "CAL",
    "CHANNEL": "CHAN",
    "COMMAND": "CMD",
    "COMPUTER": "PC",
    "CONTEXT": "CTX",
    "CONTROL": "CTRL",
    "COPY": "COPY",
    "DECREASE": "DEC",
    "DELETE": "DEL",
    "DOCUMENTS": "DOCS",
    "EDITOR": "EDIT",
    "EXECUTE": "EXEC",
    "FAVORITES": "BOOKMARKS",
    "FAVOURITES": "BOOKMARKS",
    "FORWARD": "FWD",
    "INCREASE": "INC",
    "INSERT": "INS",
    "INSTANT": "INST",
    "INTERNATIONAL": "INT",
    "KEYBOARD": "KB",
    "LANGUAGE": "LANG",
    "MAXIMUM": "MAX",
    "MESSAGING": "MSG",
    "MINIMUM": "MIN",
    "PREVIOUS": "PREV",
    "PROPERTIES": "PROPS",
    "SCREENSAVER": "SCREEN",
    "SPREADSHEET": "SHEET",
    "SUBTITLES": "SUBS",
    "TOGGLE": "TOG",
    "TUTORIAL": "GUIDE",
    "VOLUME": "VOL",
    "WINDOWS": "WINS",
}

DE_NAME_FALLBACKS = {
    "ESCAPE_CHARACTER": "ESC",
    "FILE_SEPARATOR": "FILE SEP",
    "GROUP_SEPARATOR": "GROUP SEP",
    "SPACE": "SPACE",
}

KNOWN_ZMK_KEYCODES = frozenset(['A',
 'ALT_ERASE',
 'AMPERSAND',
 'AMPS',
 'APOS',
 'APOSTROPHE',
 'ASTERISK',
 'ASTRK',
 'AT',
 'ATTENTION',
 'AT_SIGN',
 'B',
 'BACKSLASH',
 'BACKSPACE',
 'BSLH',
 'BSPC',
 'C',
 'CAPS',
 'CAPSLOCK',
 'CARET',
 'CLCK',
 'CLEAR',
 'CLEAR2',
 'CLEAR_AGAIN',
 'COLON',
 'COMMA',
 'CRSEL',
 'C_AC_BACK',
 'C_AC_BOOKMARKS',
 'C_AC_CANCEL',
 'C_AC_CLOSE',
 'C_AC_COPY',
 'C_AC_CUT',
 'C_AC_DEL',
 'C_AC_DESKTOP_SHOW_ALL_APPLICATIONS',
 'C_AC_DESKTOP_SHOW_ALL_WINDOWS',
 'C_AC_EDIT',
 'C_AC_EXIT',
 'C_AC_FAVORITES',
 'C_AC_FAVOURITES',
 'C_AC_FIND',
 'C_AC_FORWARD',
 'C_AC_FORWARD_MAIL',
 'C_AC_GOTO',
 'C_AC_HOME',
 'C_AC_INS',
 'C_AC_INSERT',
 'C_AC_NEW',
 'C_AC_NEXT_KEYBOARD_LAYOUT_SELECT',
 'C_AC_OPEN',
 'C_AC_PASTE',
 'C_AC_PRINT',
 'C_AC_PROPERTIES',
 'C_AC_PROPS',
 'C_AC_REDO',
 'C_AC_REFRESH',
 'C_AC_REPLY',
 'C_AC_SAVE',
 'C_AC_SCROLL_DOWN',
 'C_AC_SCROLL_UP',
 'C_AC_SEARCH',
 'C_AC_SEND',
 'C_AC_STOP',
 'C_AC_UNDO',
 'C_AC_VIEW_TOGGLE',
 'C_AC_ZOOM',
 'C_AC_ZOOM_IN',
 'C_AC_ZOOM_OUT',
 'C_ALTERNATE_AUDIO_INCREMENT',
 'C_ALT_AUDIO_INC',
 'C_AL_ADDRESS_BOOK',
 'C_AL_AUDIO',
 'C_AL_AUDIO_BROWSER',
 'C_AL_AV_CAPTURE_PLAYBACK',
 'C_AL_CAL',
 'C_AL_CALC',
 'C_AL_CALCULATOR',
 'C_AL_CALENDAR',
 'C_AL_CCC',
 'C_AL_CHAT',
 'C_AL_COFFEE',
 'C_AL_CONTACTS',
 'C_AL_CONTROL_PANEL',
 'C_AL_DATABASE',
 'C_AL_DB',
 'C_AL_DOCS',
 'C_AL_DOCUMENTS',
 'C_AL_EMAIL',
 'C_AL_FILES',
 'C_AL_FILE_BROWSER',
 'C_AL_FINANCE',
 'C_AL_GRAPHICS_EDITOR',
 'C_AL_HELP',
 'C_AL_IM',
 'C_AL_IMAGES',
 'C_AL_IMAGE_BROWSER',
 'C_AL_INSTANT_MESSAGING',
 'C_AL_JOURNAL',
 'C_AL_KEYBOARD_LAYOUT',
 'C_AL_LOCK',
 'C_AL_LOGOFF',
 'C_AL_MAIL',
 'C_AL_MOVIES',
 'C_AL_MOVIE_BROWSER',
 'C_AL_MUSIC',
 'C_AL_MY_COMPUTER',
 'C_AL_NETWORK_CHAT',
 'C_AL_NEWS',
 'C_AL_NEXT_TASK',
 'C_AL_OEM_FEATURES',
 'C_AL_PRESENTATION',
 'C_AL_PREVIOUS_TASK',
 'C_AL_PREV_TASK',
 'C_AL_SCREENSAVER',
 'C_AL_SCREEN_SAVER',
 'C_AL_SELECT_TASK',
 'C_AL_SHEET',
 'C_AL_SPELL',
 'C_AL_SPELLCHECK',
 'C_AL_SPREADSHEET',
 'C_AL_TASK_MANAGER',
 'C_AL_TEXT_EDITOR',
 'C_AL_TIPS',
 'C_AL_TUTORIAL',
 'C_AL_VOICEMAIL',
 'C_AL_WORD',
 'C_AL_WWW',
 'C_ASPECT',
 'C_BACKLIGHT_TOGGLE',
 'C_BASS_BOOST',
 'C_BKLT_TOG',
 'C_BLUE',
 'C_BLUE_BUTTON',
 'C_BRIGHTNESS_AUTO',
 'C_BRIGHTNESS_DEC',
 'C_BRIGHTNESS_INC',
 'C_BRIGHTNESS_MAXIMUM',
 'C_BRIGHTNESS_MINIMUM',
 'C_BRI_AUTO',
 'C_BRI_DEC',
 'C_BRI_DN',
 'C_BRI_INC',
 'C_BRI_MAX',
 'C_BRI_MIN',
 'C_BRI_UP',
 'C_CAPTIONS',
 'C_CHANNEL_DEC',
 'C_CHANNEL_INC',
 'C_CHAN_DEC',
 'C_CHAN_INC',
 'C_CHAN_LAST',
 'C_DATA_ON_SCREEN',
 'C_EJECT',
 'C_FAST_FORWARD',
 'C_FF',
 'C_GREEN',
 'C_GREEN_BUTTON',
 'C_HELP',
 'C_KBIA_ACCEPT',
 'C_KBIA_CANCEL',
 'C_KBIA_NEXT',
 'C_KBIA_NEXT_GRP',
 'C_KBIA_PREV',
 'C_KBIA_PREV_GRP',
 'C_KEYBOARD_INPUT_ASSIST_ACCEPT',
 'C_KEYBOARD_INPUT_ASSIST_CANCEL',
 'C_KEYBOARD_INPUT_ASSIST_NEXT',
 'C_KEYBOARD_INPUT_ASSIST_NEXT_GROUP',
 'C_KEYBOARD_INPUT_ASSIST_PREVIOUS',
 'C_KEYBOARD_INPUT_ASSIST_PREVIOUS_GROUP',
 'C_MEDIA_CABLE',
 'C_MEDIA_CD',
 'C_MEDIA_COMPUTER',
 'C_MEDIA_DVD',
 'C_MEDIA_GAMES',
 'C_MEDIA_GUIDE',
 'C_MEDIA_HOME',
 'C_MEDIA_MESSAGES',
 'C_MEDIA_PHONE',
 'C_MEDIA_SATELLITE',
 'C_MEDIA_STEP',
 'C_MEDIA_TAPE',
 'C_MEDIA_TUNER',
 'C_MEDIA_TV',
 'C_MEDIA_VCR',
 'C_MEDIA_VCR_PLUS',
 'C_MEDIA_VIDEOPHONE',
 'C_MEDIA_WWW',
 'C_MENU',
 'C_MENU_DEC',
 'C_MENU_DECREASE',
 'C_MENU_DOWN',
 'C_MENU_ESC',
 'C_MENU_ESCAPE',
 'C_MENU_INC',
 'C_MENU_INCREASE',
 'C_MENU_LEFT',
 'C_MENU_PICK',
 'C_MENU_RIGHT',
 'C_MENU_SELECT',
 'C_MENU_UP',
 'C_MODE_STEP',
 'C_MUTE',
 'C_NEXT',
 'C_PAUSE',
 'C_PIP',
 'C_PLAY',
 'C_PLAY_PAUSE',
 'C_POWER',
 'C_PP',
 'C_PREV',
 'C_PREVIOUS',
 'C_PWR',
 'C_QUIT',
 'C_RANDOM_PLAY',
 'C_REC',
 'C_RECALL_LAST',
 'C_RECORD',
 'C_RED',
 'C_RED_BUTTON',
 'C_REPEAT',
 'C_RESET',
 'C_REWIND',
 'C_RW',
 'C_SHUFFLE',
 'C_SLEEP',
 'C_SLEEP_MODE',
 'C_SLOW',
 'C_SLOW2',
 'C_SLOW_TRACKING',
 'C_SNAPSHOT',
 'C_STOP',
 'C_STOP_EJECT',
 'C_SUBTITLES',
 'C_VOICE_COMMAND',
 'C_VOLUME_DOWN',
 'C_VOLUME_UP',
 'C_VOL_DN',
 'C_VOL_UP',
 'C_YELLOW',
 'C_YELLOW_BUTTON',
 'D',
 'DEL',
 'DELETE',
 'DLLR',
 'DOLLAR',
 'DOT',
 'DOUBLE_QUOTES',
 'DOWN',
 'DOWN_ARROW',
 'DQT',
 'E',
 'END',
 'ENTER',
 'EQUAL',
 'ESC',
 'ESCAPE',
 'EXCL',
 'EXCLAMATION',
 'EXSEL',
 'F',
 'F1',
 'F10',
 'F11',
 'F12',
 'F13',
 'F14',
 'F15',
 'F16',
 'F17',
 'F18',
 'F19',
 'F2',
 'F20',
 'F21',
 'F22',
 'F23',
 'F24',
 'F3',
 'F4',
 'F5',
 'F6',
 'F7',
 'F8',
 'F9',
 'FSLH',
 'G',
 'GLOBE',
 'GRAVE',
 'GREATER_THAN',
 'GT',
 'H',
 'HASH',
 'HOME',
 'I',
 'INS',
 'INSERT',
 'INT1',
 'INT2',
 'INT3',
 'INT4',
 'INT5',
 'INT6',
 'INT7',
 'INT8',
 'INT9',
 'INTERNATIONAL_1',
 'INTERNATIONAL_2',
 'INTERNATIONAL_3',
 'INTERNATIONAL_4',
 'INTERNATIONAL_5',
 'INTERNATIONAL_6',
 'INTERNATIONAL_7',
 'INTERNATIONAL_8',
 'INTERNATIONAL_9',
 'INT_HENKAN',
 'INT_KANA',
 'INT_KATAKANAHIRAGANA',
 'INT_KPJPCOMMA',
 'INT_MUHENKAN',
 'INT_RO',
 'INT_YEN',
 'J',
 'K',
 'KP_ASTERISK',
 'KP_CLEAR',
 'KP_COMMA',
 'KP_DIVIDE',
 'KP_DOT',
 'KP_ENTER',
 'KP_EQUAL',
 'KP_EQUAL_AS400',
 'KP_LEFT_PARENTHESIS',
 'KP_LPAR',
 'KP_MINUS',
 'KP_MULTIPLY',
 'KP_N0',
 'KP_N1',
 'KP_N2',
 'KP_N3',
 'KP_N4',
 'KP_N5',
 'KP_N6',
 'KP_N7',
 'KP_N8',
 'KP_N9',
 'KP_NLCK',
 'KP_NUM',
 'KP_NUMBER_0',
 'KP_NUMBER_1',
 'KP_NUMBER_2',
 'KP_NUMBER_3',
 'KP_NUMBER_4',
 'KP_NUMBER_5',
 'KP_NUMBER_6',
 'KP_NUMBER_7',
 'KP_NUMBER_8',
 'KP_NUMBER_9',
 'KP_NUMLOCK',
 'KP_PLUS',
 'KP_RIGHT_PARENTHESIS',
 'KP_RPAR',
 'KP_SLASH',
 'KP_SUBTRACT',
 'K_AGAIN',
 'K_APP',
 'K_APPLICATION',
 'K_BACK',
 'K_CALC',
 'K_CALCULATOR',
 'K_CANCEL',
 'K_CMENU',
 'K_COFFEE',
 'K_CONTEXT_MENU',
 'K_COPY',
 'K_CUT',
 'K_EDIT',
 'K_EJECT',
 'K_EXEC',
 'K_EXECUTE',
 'K_FIND',
 'K_FIND2',
 'K_FORWARD',
 'K_HELP',
 'K_LOCK',
 'K_MENU',
 'K_MUTE',
 'K_MUTE2',
 'K_NEXT',
 'K_PASTE',
 'K_PLAY_PAUSE',
 'K_POWER',
 'K_PP',
 'K_PREV',
 'K_PREVIOUS',
 'K_PWR',
 'K_REDO',
 'K_REFRESH',
 'K_SCREENSAVER',
 'K_SCROLL_DOWN',
 'K_SCROLL_UP',
 'K_SELECT',
 'K_SLEEP',
 'K_STOP',
 'K_STOP2',
 'K_STOP3',
 'K_UNDO',
 'K_VOLUME_DOWN',
 'K_VOLUME_DOWN2',
 'K_VOLUME_UP',
 'K_VOLUME_UP2',
 'K_VOL_DN',
 'K_VOL_DN2',
 'K_VOL_UP',
 'K_VOL_UP2',
 'K_WWW',
 'L',
 'LALT',
 'LANG1',
 'LANG2',
 'LANG3',
 'LANG4',
 'LANG5',
 'LANG6',
 'LANG7',
 'LANG8',
 'LANG9',
 'LANGUAGE_1',
 'LANGUAGE_2',
 'LANGUAGE_3',
 'LANGUAGE_4',
 'LANGUAGE_5',
 'LANGUAGE_6',
 'LANGUAGE_7',
 'LANGUAGE_8',
 'LANGUAGE_9',
 'LANG_HANGEUL',
 'LANG_HANJA',
 'LANG_HIRAGANA',
 'LANG_KATAKANA',
 'LANG_ZENKAKUHANKAKU',
 'LBKT',
 'LBRC',
 'LCAPS',
 'LCMD',
 'LCTRL',
 'LEFT',
 'LEFT_ALT',
 'LEFT_ARROW',
 'LEFT_BRACE',
 'LEFT_BRACKET',
 'LEFT_COMMAND',
 'LEFT_CONTROL',
 'LEFT_GUI',
 'LEFT_META',
 'LEFT_PARENTHESIS',
 'LEFT_SHIFT',
 'LEFT_WIN',
 'LESS_THAN',
 'LGUI',
 'LMETA',
 'LNLCK',
 'LOCKING_CAPS',
 'LOCKING_NUM',
 'LOCKING_SCROLL',
 'LPAR',
 'LSHFT',
 'LSHIFT',
 'LSLCK',
 'LT',
 'LWIN',
 'M',
 'MINUS',
 'N',
 'N0',
 'N1',
 'N2',
 'N3',
 'N4',
 'N5',
 'N6',
 'N7',
 'N8',
 'N9',
 'NON_US_BACKSLASH',
 'NON_US_BSLH',
 'NON_US_HASH',
 'NUBS',
 'NUHS',
 'NUMBER_0',
 'NUMBER_1',
 'NUMBER_2',
 'NUMBER_3',
 'NUMBER_4',
 'NUMBER_5',
 'NUMBER_6',
 'NUMBER_7',
 'NUMBER_8',
 'NUMBER_9',
 'O',
 'OPER',
 'OUT',
 'P',
 'PAGE_DOWN',
 'PAGE_UP',
 'PAUSE_BREAK',
 'PERCENT',
 'PERIOD',
 'PG_DN',
 'PG_UP',
 'PIPE',
 'PIPE2',
 'PLUS',
 'POUND',
 'PRCNT',
 'PRINTSCREEN',
 'PRIOR',
 'PSCRN',
 'Q',
 'QMARK',
 'QUESTION',
 'R',
 'RALT',
 'RBKT',
 'RBRC',
 'RCMD',
 'RCTRL',
 'RET',
 'RET2',
 'RETURN',
 'RETURN2',
 'RGUI',
 'RIGHT',
 'RIGHT_ALT',
 'RIGHT_ARROW',
 'RIGHT_BRACE',
 'RIGHT_BRACKET',
 'RIGHT_COMMAND',
 'RIGHT_CONTROL',
 'RIGHT_GUI',
 'RIGHT_META',
 'RIGHT_PARENTHESIS',
 'RIGHT_SHIFT',
 'RIGHT_WIN',
 'RMETA',
 'RPAR',
 'RSHFT',
 'RSHIFT',
 'RWIN',
 'S',
 'SCROLLLOCK',
 'SEMI',
 'SEMICOLON',
 'SEPARATOR',
 'SINGLE_QUOTE',
 'SLASH',
 'SLCK',
 'SPACE',
 'SQT',
 'STAR',
 'SYSREQ',
 'T',
 'TAB',
 'TILDE',
 'TILDE2',
 'U',
 'UNDER',
 'UNDERSCORE',
 'UP',
 'UP_ARROW',
 'V',
 'W',
 'X',
 'Y',
 'Z'])


def _label_from_comment(comment):
    if comment is None:
        return None
    comment = comment.strip()
    if not comment:
        return None
    if len(comment) == 1 and comment.isascii() and comment.isalpha():
        return comment.upper()
    if comment == " ":
        return "SPACE"
    return comment


def _format_words(token):
    words = []
    for part in token.split("_"):
        if not part:
            continue
        words.append(WORD_LABELS.get(part, part))
    return " ".join(words)


def _format_keypad_token(token):
    number_match = re.fullmatch(r"(?:NUMBER_|N)(\d)", token)
    if number_match:
        return f"KP {number_match.group(1)}"
    if token in DIRECT_KEY_LABELS:
        return DIRECT_KEY_LABELS[token]
    return f"KP {_format_words(token)}".strip()


def _format_key_label(token):
    if token in DIRECT_KEY_LABELS:
        return DIRECT_KEY_LABELS[token]

    if re.fullmatch(r"[A-Z]", token):
        return token

    if re.fullmatch(r"F\d+", token):
        return token

    number_match = re.fullmatch(r"(?:NUMBER_|N)(\d)", token)
    if number_match:
        return number_match.group(1)

    symbol_labels = {
        "EXCLAMATION": "!", "EXCL": "!",
        "AT_SIGN": "@", "AT": "@",
        "HASH": "#", "POUND": "#",
        "DOLLAR": "$", "DLLR": "$",
        "PERCENT": "%", "PRCNT": "%",
        "CARET": "^",
        "AMPERSAND": "&", "AMPS": "&",
        "ASTERISK": "*", "ASTRK": "*", "STAR": "*",
        "LEFT_PARENTHESIS": "(", "LPAR": "(",
        "RIGHT_PARENTHESIS": ")", "RPAR": ")",
        "MINUS": "-",
        "UNDERSCORE": "_", "UNDER": "_",
        "EQUAL": "=",
        "PLUS": "+",
        "LEFT_BRACKET": "[", "LBKT": "[",
        "RIGHT_BRACKET": "]", "RBKT": "]",
        "LEFT_BRACE": "{", "LBRC": "{",
        "RIGHT_BRACE": "}", "RBRC": "}",
        "BACKSLASH": "\\", "BSLH": "\\",
        "NON_US_BACKSLASH": "\\", "NON_US_BSLH": "\\", "NUBS": "\\",
        "PIPE": "|", "PIPE2": "|",
        "SEMICOLON": ";", "SEMI": ";",
        "COLON": ":",
        "SINGLE_QUOTE": "'", "SQT": "'", "APOSTROPHE": "'", "APOS": "'",
        "DOUBLE_QUOTES": '"', "DQT": '"',
        "COMMA": ",",
        "LESS_THAN": "<", "LT": "<",
        "PERIOD": ".", "DOT": ".",
        "GREATER_THAN": ">", "GT": ">",
        "SLASH": "/", "FSLH": "/",
        "QUESTION": "?", "QMARK": "?",
        "GRAVE": "`",
        "TILDE": "~", "TILDE2": "~",
        "NON_US_HASH": "#", "NUHS": "#",
    }
    if token in symbol_labels:
        return symbol_labels[token]

    if token.startswith("KP_"):
        return _format_keypad_token(token[3:])

    for prefix in ("C_KEYBOARD_INPUT_ASSIST_", "C_MENU_", "C_AC_", "C_AL_", "C_", "K_"):
        if token.startswith(prefix):
            return _format_words(token[len(prefix):])

    return _format_words(token)


def _build_de_labels():
    text = CH_DE_PATH.read_text(encoding="utf-8")
    labels = {}
    aliases = {}
    comment = None

    for line in text.splitlines():
        comment_match = re.match(r"\s*/\*\s*(.*?)\s*\*/\s*$", line)
        if comment_match:
            comment = comment_match.group(1)
            continue

        define_match = re.match(r"\s*#define\s+(DE_[A-Z0-9_]+)\s+(.+?)\s*$", line)
        if not define_match:
            continue

        name, expr = define_match.groups()
        expr = expr.strip()
        alias_match = re.fullmatch(r"\((DE_[A-Z0-9_]+)\)", expr)
        if alias_match:
            aliases[name] = alias_match.group(1)
        else:
            labels[name] = _label_from_comment(comment) or DE_NAME_FALLBACKS.get(name[3:], _format_words(name[3:]))
        comment = None

    def resolve(name):
        if name in labels:
            return labels[name]
        target = aliases.get(name)
        if not target:
            labels[name] = DE_NAME_FALLBACKS.get(name[3:], _format_words(name[3:]))
            return labels[name]
        labels[name] = resolve(target)
        return labels[name]

    for name in aliases:
        resolve(name)

    return labels


def _build_std_labels():
    return {name: _format_key_label(name) for name in KNOWN_ZMK_KEYCODES}


DE_LABELS = _build_de_labels()
STD_LABELS = _build_std_labels()

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
        self.layer_tokens = {}    # index -> keymap token from #define
        self.layer_names = {}     # index -> display name
        self.layer_name_by_token = {}
        self.layer_bindings = []  # parsed bindings per layer, preserving positions
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
            self.layer_tokens[int(m.group(2))] = m.group(1)

    # ── Step 2: parse behaviors { ... } block ──

    def _parse_behaviors(self):
        block = self._extract_named_block("behaviors")
        if block is None:
            return
        self._parse_behavior_block(block)

    def _parse_macros(self):
        block = self._extract_named_block("macros")
        if block is None:
            return
        self._parse_behavior_block(block)

    def _extract_named_block(self, name):
        match = re.search(rf"\b{name}\s*\{{", self.text)
        if not match:
            return None
        open_brace = self.text.find("{", match.start())
        close_brace = self._find_matching_brace(open_brace)
        return self.text[open_brace + 1 : close_brace]

    def _find_matching_brace(self, open_brace_idx):
        depth = 0
        for idx in range(open_brace_idx, len(self.text)):
            char = self.text[idx]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return idx
        raise ValueError("Could not find matching brace")

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
        keymap_block = self._extract_named_block("keymap")
        if keymap_block is None:
            raise ValueError("Could not find keymap section")

        layers = []
        layer_defs = []
        layer_re = re.compile(r"(\w+)\s*\{(.*?)\};", re.DOTALL)
        for i, m in enumerate(layer_re.finditer(keymap_block)):
            body = m.group(2)
            display_name_match = re.search(r'display-name\s*=\s*"([^"]+)"', body)
            display_name = display_name_match.group(1) if display_name_match else m.group(1).upper()
            layer_token = self.layer_tokens.get(i, m.group(1).upper())
            self.layer_names[i] = display_name
            self.layer_name_by_token[layer_token] = display_name
            layer_defs.append({"token": layer_token, "name": display_name, "body": body})

        for layer_def in layer_defs:
            body = layer_def["body"]
            bindings_match = re.search(r"bindings\s*=\s*<(.*?)>", body, re.DOTALL)
            if not bindings_match:
                continue
            bindings_text = bindings_match.group(1)
            bindings = self._tokenize_bindings(bindings_text)
            layer_def["bindings"] = bindings
            self.layer_bindings.append(bindings)

        for layer_index, layer_def in enumerate(layer_defs):
            bindings = layer_def.get("bindings")
            if not bindings:
                continue
            keys = [
                self._resolve_binding(binding, layer_index=layer_index, key_index=key_index)
                for key_index, binding in enumerate(bindings)
            ]
            layers.append({"token": layer_def["token"], "name": layer_def["name"], "keys": keys})
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

    def _resolve_binding(self, binding, layer_index=None, key_index=None):
        behavior, params = binding

        if behavior == "none":
            return {"c": "none-key"}

        if behavior == "trans":
            return self._resolve_transparent_binding(layer_index, key_index)

        if behavior == "kp":
            return self._resolve_kp(params[0] if params else "")

        if behavior == "mo":
            return {"t": self._layer_label(params[0] if params else ""), "c": "layer-key"}

        if behavior == "mt":
            tap_display = self._resolve_kp(params[1] if len(params) > 1 else "")
            hold_label = self._resolve_kp(params[0] if params else "").get("t", "")
            result = dict(tap_display)
            if hold_label and hold_label != result.get("t"):
                result["h"] = hold_label
            return result

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
            return self._resolve_hold_tap(beh_info, params, layer_index, key_index)

        if compat == "zmk,behavior-tap-dance":
            return self._resolve_tap_dance(beh_info, layer_index, key_index)

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

        # Detect one-shot keypress macro
        if "&macro_param_1to1" in raw and re.search(r"&kp\s+MACRO_PLACEHOLDER\b", raw):
            key = params[0] if params else ""
            return self._resolve_kp(key) if key else {"t": "??"}

        # Fallback
        return {"t": beh_info.get("compat", "macro")}

    def _resolve_nested_behavior(self, behavior, param, layer_index=None, key_index=None):
        params = [param] if param else []
        return self._resolve_binding((behavior, params), layer_index=layer_index, key_index=key_index)

    def _resolve_hold_tap(self, beh_info, params, layer_index=None, key_index=None):
        raw = beh_info.get("bindings_raw", "")
        parts = re.findall(r"<([^>]+)>", raw)
        if len(parts) < 2:
            return {"t": "??"}

        hold_beh_name = parts[0].strip().lstrip("&").split()[0]
        tap_beh_name = parts[1].strip().lstrip("&").split()[0]

        # Resolve tap (second param -> tap behavior)
        tap_param = params[1] if len(params) > 1 else ""
        tap_display = self._resolve_nested_behavior(
            tap_beh_name, tap_param, layer_index=layer_index, key_index=key_index
        )

        # Resolve hold (first param -> hold behavior)
        hold_param = params[0] if params else ""
        hold_display = self._resolve_nested_behavior(
            hold_beh_name, hold_param, layer_index=layer_index, key_index=key_index
        )
        hold_label = hold_display.get("t", hold_param or hold_beh_name)

        result = dict(tap_display)
        if hold_label != result.get("t"):
            result["h"] = hold_label
        if hold_beh_name != "kp" and hold_display.get("c") and "c" not in result:
            result["c"] = hold_display["c"]
        return result

    def _resolve_tap_dance(self, beh_info, layer_index=None, key_index=None):
        raw = beh_info.get("bindings_raw", "")
        parts = re.findall(r"<([^>]+)>", raw)
        if not parts:
            return {"t": "??"}

        bindings = self._tokenize_bindings(" ".join(parts))
        if not bindings:
            return {"t": "??"}

        result = dict(self._resolve_binding(bindings[0], layer_index=layer_index, key_index=key_index))
        if len(bindings) > 1:
            second = self._resolve_binding(
                bindings[1], layer_index=layer_index, key_index=key_index
            ).get("t")
            if second and "s" not in result:
                result["s"] = second
        return result

    # ── Helpers ──

    def _resolve_transparent_binding(self, layer_index, key_index):
        if layer_index is None or key_index is None:
            return {"t": "\u25bd", "c": "none-key"}

        for lower_layer_index in range(layer_index - 1, -1, -1):
            if lower_layer_index >= len(self.layer_bindings):
                continue

            lower_bindings = self.layer_bindings[lower_layer_index]
            if key_index >= len(lower_bindings):
                continue

            return dict(
                self._resolve_binding(
                    lower_bindings[key_index],
                    layer_index=lower_layer_index,
                    key_index=key_index,
                )
            )

        return {"c": "none-key"}

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
            return self.layer_names.get(idx, self.layer_tokens.get(idx, str(idx)))
        except ValueError:
            return self.layer_name_by_token.get(name_or_idx, name_or_idx)


def infer_layer_sides(layers):
    if not layers:
        return layers

    layer_names = {layer["name"] for layer in layers}
    side_hits = {}

    for layer in layers:
        for index, key in enumerate(layer["keys"][36:42], start=36):
            side = "left" if index < 39 else "right"
            for field in ("t", "h"):
                target = key.get(field)
                if target in layer_names and target != layer["name"]:
                    side_hits.setdefault(target, []).append(side)

    resolved_layers = []
    for index, layer in enumerate(layers):
        resolved = dict(layer)
        if index == 0:
            resolved["side"] = "center"
        else:
            hits = side_hits.get(layer["name"], [])
            if "left" in hits and "right" not in hits:
                resolved["side"] = "left"
            elif "right" in hits and "left" not in hits:
                resolved["side"] = "right"
            elif hits:
                resolved["side"] = hits[0]
            else:
                resolved["side"] = "left"
        resolved_layers.append(resolved)
    return resolved_layers


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
        side = json.dumps(layer.get("side", "left"))
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
    layers = infer_layer_sides(parser.parse())

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

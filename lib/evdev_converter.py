from evdev import ecodes

import lib.logger
import lib.usb_hid 

logger = lib.logger.get_logger()

# SPDX-FileCopyrightText: 2017 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_hid.keycode.Keycode`
====================================================

* Author(s): Scott Shawcroft, Dan Halbert
"""


class Keycode:
    """USB HID Keycode constants.

    This list is modeled after the names for USB keycodes defined in
    https://usb.org/sites/default/files/hut1_21_0.pdf#page=83.
    This list does not include every single code, but does include all the keys on
    a regular PC or Mac keyboard.

    Remember that keycodes are the names for key *positions* on a US keyboard, and may
    not correspond to the character that you mean to send if you want to emulate non-US keyboard.
    For instance, on a French keyboard (AZERTY instead of QWERTY),
    the keycode for 'q' is used to indicate an 'a'. Likewise, 'y' represents 'z' on
    a German keyboard. This is historical: the idea was that the keycaps could be changed
    without changing the keycodes sent, so that different firmware was not needed for
    different variations of a keyboard.
    """

    # pylint: disable-msg=invalid-name
    A = 0x04
    """``a`` and ``A``"""
    B = 0x05
    """``b`` and ``B``"""
    C = 0x06
    """``c`` and ``C``"""
    D = 0x07
    """``d`` and ``D``"""
    E = 0x08
    """``e`` and ``E``"""
    F = 0x09
    """``f`` and ``F``"""
    G = 0x0A
    """``g`` and ``G``"""
    H = 0x0B
    """``h`` and ``H``"""
    I = 0x0C
    """``i`` and ``I``"""
    J = 0x0D
    """``j`` and ``J``"""
    K = 0x0E
    """``k`` and ``K``"""
    L = 0x0F
    """``l`` and ``L``"""
    M = 0x10
    """``m`` and ``M``"""
    N = 0x11
    """``n`` and ``N``"""
    O = 0x12
    """``o`` and ``O``"""
    P = 0x13
    """``p`` and ``P``"""
    Q = 0x14
    """``q`` and ``Q``"""
    R = 0x15
    """``r`` and ``R``"""
    S = 0x16
    """``s`` and ``S``"""
    T = 0x17
    """``t`` and ``T``"""
    U = 0x18
    """``u`` and ``U``"""
    V = 0x19
    """``v`` and ``V``"""
    W = 0x1A
    """``w`` and ``W``"""
    X = 0x1B
    """``x`` and ``X``"""
    Y = 0x1C
    """``y`` and ``Y``"""
    Z = 0x1D
    """``z`` and ``Z``"""

    ONE = 0x1E
    """``1`` and ``!``"""
    TWO = 0x1F
    """``2`` and ``@``"""
    THREE = 0x20
    """``3`` and ``#``"""
    FOUR = 0x21
    """``4`` and ``$``"""
    FIVE = 0x22
    """``5`` and ``%``"""
    SIX = 0x23
    """``6`` and ``^``"""
    SEVEN = 0x24
    """``7`` and ``&``"""
    EIGHT = 0x25
    """``8`` and ``*``"""
    NINE = 0x26
    """``9`` and ``(``"""
    ZERO = 0x27
    """``0`` and ``)``"""
    ENTER = 0x28
    """Enter (Return)"""
    RETURN = ENTER
    """Alias for ``ENTER``"""
    ESCAPE = 0x29
    """Escape"""
    BACKSPACE = 0x2A
    """Delete backward (Backspace)"""
    TAB = 0x2B
    """Tab and Backtab"""
    SPACEBAR = 0x2C
    """Spacebar"""
    SPACE = SPACEBAR
    """Alias for SPACEBAR"""
    MINUS = 0x2D
    """``-` and ``_``"""
    EQUALS = 0x2E
    """``=` and ``+``"""
    LEFT_BRACKET = 0x2F
    """``[`` and ``{``"""
    RIGHT_BRACKET = 0x30
    """``]`` and ``}``"""
    BACKSLASH = 0x31
    r"""``\`` and ``|``"""
    POUND = 0x32
    """``#`` and ``~`` (Non-US keyboard)"""
    SEMICOLON = 0x33
    """``;`` and ``:``"""
    QUOTE = 0x34
    """``'`` and ``"``"""
    GRAVE_ACCENT = 0x35
    r""":literal:`\`` and ``~``"""
    COMMA = 0x36
    """``,`` and ``<``"""
    PERIOD = 0x37
    """``.`` and ``>``"""
    FORWARD_SLASH = 0x38
    """``/`` and ``?``"""

    CAPS_LOCK = 0x39
    """Caps Lock"""

    F1 = 0x3A
    """Function key F1"""
    F2 = 0x3B
    """Function key F2"""
    F3 = 0x3C
    """Function key F3"""
    F4 = 0x3D
    """Function key F4"""
    F5 = 0x3E
    """Function key F5"""
    F6 = 0x3F
    """Function key F6"""
    F7 = 0x40
    """Function key F7"""
    F8 = 0x41
    """Function key F8"""
    F9 = 0x42
    """Function key F9"""
    F10 = 0x43
    """Function key F10"""
    F11 = 0x44
    """Function key F11"""
    F12 = 0x45
    """Function key F12"""

    PRINT_SCREEN = 0x46
    """Print Screen (SysRq)"""
    SCROLL_LOCK = 0x47
    """Scroll Lock"""
    PAUSE = 0x48
    """Pause (Break)"""

    INSERT = 0x49
    """Insert"""
    HOME = 0x4A
    """Home (often moves to beginning of line)"""
    PAGE_UP = 0x4B
    """Go back one page"""
    DELETE = 0x4C
    """Delete forward"""
    END = 0x4D
    """End (often moves to end of line)"""
    PAGE_DOWN = 0x4E
    """Go forward one page"""

    RIGHT_ARROW = 0x4F
    """Move the cursor right"""
    LEFT_ARROW = 0x50
    """Move the cursor left"""
    DOWN_ARROW = 0x51
    """Move the cursor down"""
    UP_ARROW = 0x52
    """Move the cursor up"""

    KEYPAD_NUMLOCK = 0x53
    """Num Lock (Clear on Mac)"""
    KEYPAD_FORWARD_SLASH = 0x54
    """Keypad ``/``"""
    KEYPAD_ASTERISK = 0x55
    """Keypad ``*``"""
    KEYPAD_MINUS = 0x56
    """Keyapd ``-``"""
    KEYPAD_PLUS = 0x57
    """Keypad ``+``"""
    KEYPAD_ENTER = 0x58
    """Keypad Enter"""
    KEYPAD_ONE = 0x59
    """Keypad ``1`` and End"""
    KEYPAD_TWO = 0x5A
    """Keypad ``2`` and Down Arrow"""
    KEYPAD_THREE = 0x5B
    """Keypad ``3`` and PgDn"""
    KEYPAD_FOUR = 0x5C
    """Keypad ``4`` and Left Arrow"""
    KEYPAD_FIVE = 0x5D
    """Keypad ``5``"""
    KEYPAD_SIX = 0x5E
    """Keypad ``6`` and Right Arrow"""
    KEYPAD_SEVEN = 0x5F
    """Keypad ``7`` and Home"""
    KEYPAD_EIGHT = 0x60
    """Keypad ``8`` and Up Arrow"""
    KEYPAD_NINE = 0x61
    """Keypad ``9`` and PgUp"""
    KEYPAD_ZERO = 0x62
    """Keypad ``0`` and Ins"""
    KEYPAD_PERIOD = 0x63
    """Keypad ``.`` and Del"""
    KEYPAD_BACKSLASH = 0x64
    """Keypad ``\\`` and ``|`` (Non-US)"""

    APPLICATION = 0x65
    """Application: also known as the Menu key (Windows)"""
    POWER = 0x66
    """Power (Mac)"""
    KEYPAD_EQUALS = 0x67
    """Keypad ``=`` (Mac)"""
    F13 = 0x68
    """Function key F13 (Mac)"""
    F14 = 0x69
    """Function key F14 (Mac)"""
    F15 = 0x6A
    """Function key F15 (Mac)"""
    F16 = 0x6B
    """Function key F16 (Mac)"""
    F17 = 0x6C
    """Function key F17 (Mac)"""
    F18 = 0x6D
    """Function key F18 (Mac)"""
    F19 = 0x6E
    """Function key F19 (Mac)"""

    F20 = 0x6F
    """Function key F20"""
    F21 = 0x70
    """Function key F21"""
    F22 = 0x71
    """Function key F22"""
    F23 = 0x72
    """Function key F23"""
    F24 = 0x73
    """Function key F24"""

    LEFT_CONTROL = 0xE0
    """Control modifier left of the spacebar"""
    CONTROL = LEFT_CONTROL
    """Alias for LEFT_CONTROL"""
    LEFT_SHIFT = 0xE1
    """Shift modifier left of the spacebar"""
    SHIFT = LEFT_SHIFT
    """Alias for LEFT_SHIFT"""
    LEFT_ALT = 0xE2
    """Alt modifier left of the spacebar"""
    ALT = LEFT_ALT
    """Alias for LEFT_ALT; Alt is also known as Option (Mac)"""
    OPTION = ALT
    """Labeled as Option on some Mac keyboards"""
    LEFT_GUI = 0xE3
    """GUI modifier left of the spacebar"""
    GUI = LEFT_GUI
    """Alias for LEFT_GUI; GUI is also known as the Windows key, Command (Mac), or Meta"""
    WINDOWS = GUI
    """Labeled with a Windows logo on Windows keyboards"""
    COMMAND = GUI
    """Labeled as Command on Mac keyboards, with a clover glyph"""
    RIGHT_CONTROL = 0xE4
    """Control modifier right of the spacebar"""
    RIGHT_SHIFT = 0xE5
    """Shift modifier right of the spacebar"""
    RIGHT_ALT = 0xE6
    """Alt modifier right of the spacebar"""
    RIGHT_GUI = 0xE7
    """GUI modifier right of the spacebar"""

    # pylint: enable-msg=invalid-name
    @classmethod
    def modifier_bit(cls, keycode: int) -> int:
        """Return the modifer bit to be set in an HID keycode report if this is a
        modifier key; otherwise return 0."""
        return (
            1 << (keycode - 0xE0) if cls.LEFT_CONTROL <= keycode <= cls.RIGHT_GUI else 0
        )

_EVDEV_TO_HID_MAPPING  = {
    ecodes.KEY_RESERVED: 0x00,
    ecodes.KEY_A: Keycode.A,
    ecodes.KEY_B: Keycode.B,
    ecodes.KEY_C: Keycode.C,
    ecodes.KEY_D: Keycode.D,
    ecodes.KEY_E: Keycode.E,
    ecodes.KEY_F: Keycode.F,
    ecodes.KEY_G: Keycode.G,
    ecodes.KEY_H: Keycode.H,
    ecodes.KEY_I: Keycode.I,
    ecodes.KEY_J: Keycode.J,
    ecodes.KEY_K: Keycode.K,
    ecodes.KEY_L: Keycode.L,
    ecodes.KEY_M: Keycode.M,
    ecodes.KEY_N: Keycode.N,
    ecodes.KEY_O: Keycode.O,
    ecodes.KEY_P: Keycode.P,
    ecodes.KEY_Q: Keycode.Q,
    ecodes.KEY_R: Keycode.R,
    ecodes.KEY_S: Keycode.S,
    ecodes.KEY_T: Keycode.T,
    ecodes.KEY_U: Keycode.U,
    ecodes.KEY_V: Keycode.V,
    ecodes.KEY_W: Keycode.W,
    ecodes.KEY_X: Keycode.X,
    ecodes.KEY_Y: Keycode.Y,
    ecodes.KEY_Z: Keycode.Z,
    ecodes.KEY_1: Keycode.ONE,
    ecodes.KEY_2: Keycode.TWO,
    ecodes.KEY_3: Keycode.THREE,
    ecodes.KEY_4: Keycode.FOUR,
    ecodes.KEY_5: Keycode.FIVE,
    ecodes.KEY_6: Keycode.SIX,
    ecodes.KEY_7: Keycode.SEVEN,
    ecodes.KEY_8: Keycode.EIGHT,
    ecodes.KEY_9: Keycode.NINE,
    ecodes.KEY_0: Keycode.ZERO,
    ecodes.KEY_ENTER: Keycode.ENTER,
    ecodes.KEY_ESC: Keycode.ESCAPE,
    ecodes.KEY_BACKSPACE: Keycode.BACKSPACE,
    ecodes.KEY_TAB: Keycode.TAB,
    ecodes.KEY_SPACE: Keycode.SPACEBAR,
    ecodes.KEY_MINUS: Keycode.MINUS,
    ecodes.KEY_EQUAL: Keycode.EQUALS,
    ecodes.KEY_LEFTBRACE: Keycode.LEFT_BRACKET,
    ecodes.KEY_RIGHTBRACE: Keycode.RIGHT_BRACKET,
    ecodes.KEY_BACKSLASH: Keycode.POUND,
    ecodes.KEY_SEMICOLON: Keycode.SEMICOLON,
    ecodes.KEY_APOSTROPHE: Keycode.QUOTE,
    ecodes.KEY_GRAVE: Keycode.GRAVE_ACCENT,
    ecodes.KEY_COMMA: Keycode.COMMA,
    ecodes.KEY_DOT: Keycode.PERIOD,
    ecodes.KEY_SLASH: Keycode.FORWARD_SLASH,
    ecodes.KEY_CAPSLOCK: Keycode.CAPS_LOCK,
    ecodes.KEY_F1: Keycode.F1,
    ecodes.KEY_F2: Keycode.F2,
    ecodes.KEY_F3: Keycode.F3,
    ecodes.KEY_F4: Keycode.F4,
    ecodes.KEY_F5: Keycode.F5,
    ecodes.KEY_F6: Keycode.F6,
    ecodes.KEY_F7: Keycode.F7,
    ecodes.KEY_F8: Keycode.F8,
    ecodes.KEY_F9: Keycode.F9,
    ecodes.KEY_F10: Keycode.F10,
    ecodes.KEY_F11: Keycode.F11,
    ecodes.KEY_F12: Keycode.F12,
    ecodes.KEY_SYSRQ: Keycode.PRINT_SCREEN,
    ecodes.KEY_SCROLLLOCK: Keycode.SCROLL_LOCK,
    ecodes.KEY_PAUSE: Keycode.PAUSE,
    ecodes.KEY_INSERT: Keycode.INSERT,
    ecodes.KEY_HOME: Keycode.HOME,
    ecodes.KEY_PAGEUP: Keycode.PAGE_UP,
    ecodes.KEY_DELETE: Keycode.DELETE,
    ecodes.KEY_END: Keycode.END,
    ecodes.KEY_PAGEDOWN: Keycode.PAGE_DOWN,
    ecodes.KEY_RIGHT: Keycode.RIGHT_ARROW,
    ecodes.KEY_LEFT: Keycode.LEFT_ARROW,
    ecodes.KEY_DOWN: Keycode.DOWN_ARROW,
    ecodes.KEY_UP: Keycode.UP_ARROW,
    ecodes.KEY_NUMLOCK: Keycode.KEYPAD_NUMLOCK,
    ecodes.KEY_KPSLASH: Keycode.KEYPAD_FORWARD_SLASH,
    ecodes.KEY_KPASTERISK: Keycode.KEYPAD_ASTERISK,
    ecodes.KEY_KPMINUS: Keycode.KEYPAD_MINUS,
    ecodes.KEY_KPPLUS: Keycode.KEYPAD_PLUS,
    ecodes.KEY_KPENTER: Keycode.KEYPAD_ENTER,
    ecodes.KEY_KP1: Keycode.KEYPAD_ONE,
    ecodes.KEY_KP2: Keycode.KEYPAD_TWO,
    ecodes.KEY_KP3: Keycode.KEYPAD_THREE,
    ecodes.KEY_KP4: Keycode.KEYPAD_FOUR,
    ecodes.KEY_KP5: Keycode.KEYPAD_FIVE,
    ecodes.KEY_KP6: Keycode.KEYPAD_SIX,
    ecodes.KEY_KP7: Keycode.KEYPAD_SEVEN,
    ecodes.KEY_KP8: Keycode.KEYPAD_EIGHT,
    ecodes.KEY_KP9: Keycode.KEYPAD_NINE,
    ecodes.KEY_KP0: Keycode.KEYPAD_ZERO,
    ecodes.KEY_KPDOT: Keycode.KEYPAD_PERIOD,
    ecodes.KEY_102ND: Keycode.KEYPAD_BACKSLASH,
    ecodes.KEY_COMPOSE: Keycode.APPLICATION,
    ecodes.KEY_POWER: Keycode.POWER,
    ecodes.KEY_KPEQUAL: Keycode.KEYPAD_EQUALS,
    ecodes.KEY_F13: Keycode.F13,
    ecodes.KEY_F14: Keycode.F14,
    ecodes.KEY_F15: Keycode.F15,
    ecodes.KEY_F16: Keycode.F16,
    ecodes.KEY_F17: Keycode.F17,
    ecodes.KEY_F18: Keycode.F18,
    ecodes.KEY_F19: Keycode.F19,
    ecodes.KEY_F20: Keycode.F20,
    ecodes.KEY_F21: Keycode.F21,
    ecodes.KEY_F22: Keycode.F22,
    ecodes.KEY_F23: Keycode.F23,
    ecodes.KEY_F24: Keycode.F24,
    ecodes.KEY_OPEN: 0x74,
    ecodes.KEY_HELP: 0x75,
    ecodes.KEY_PROPS: 0x76,
    ecodes.KEY_FRONT: 0x77,
    ecodes.KEY_MENU: 0x79,
    ecodes.KEY_UNDO: 0x7A,
    ecodes.KEY_CUT: 0x7B,
    ecodes.KEY_COPY: 0x7C,
    ecodes.KEY_PASTE: 0x7D,
    ecodes.KEY_AGAIN: 0x85,
    ecodes.KEY_RO: 0x87,
    ecodes.KEY_KATAKANAHIRAGANA: 0x88,
    ecodes.KEY_YEN: 0x89,
    ecodes.KEY_HENKAN: 0x8A,
    ecodes.KEY_HANJA: 0x8B,
    ecodes.KEY_KPCOMMA: 0x8C,
    ecodes.KEY_SCALE: 0x91,
    ecodes.KEY_HIRAGANA: 0x92,
    ecodes.KEY_KATAKANA: 0x93,
    ecodes.KEY_MUHENKAN: 0x94,
    ecodes.KEY_LEFTCTRL: Keycode.LEFT_CONTROL,
    ecodes.KEY_LEFTSHIFT: Keycode.LEFT_SHIFT,
    ecodes.KEY_LEFTALT: Keycode.LEFT_ALT,
    ecodes.KEY_LEFTMETA: Keycode.LEFT_GUI,
    ecodes.KEY_RIGHTCTRL: Keycode.RIGHT_CONTROL,
    ecodes.KEY_RIGHTSHIFT: Keycode.RIGHT_SHIFT,
    ecodes.KEY_RIGHTALT: Keycode.RIGHT_ALT,
    ecodes.KEY_RIGHTMETA: Keycode.RIGHT_GUI,
    ecodes.KEY_PLAYPAUSE: 0xE8,
    ecodes.KEY_STOPCD: 0xE9,
    ecodes.KEY_PREVIOUSSONG: 0xEA,
    ecodes.KEY_NEXTSONG: 0xEB,
    ecodes.KEY_EJECTCD: 0xEC,
    ecodes.KEY_VOLUMEUP: 0xED,
    ecodes.KEY_VOLUMEDOWN: 0xEE,
    ecodes.KEY_WWW: 0xF0,
    ecodes.KEY_MAIL: 0xF1,
    ecodes.KEY_FORWARD: 0xF2,
    ecodes.KEY_STOP: 0xF3,
    ecodes.KEY_FIND: 0xF4,
    ecodes.KEY_SCROLLUP: 0xF5,
    ecodes.KEY_SCROLLDOWN: 0xF6,
    ecodes.KEY_EDIT: 0xF7,
    ecodes.KEY_SLEEP: 0xF8,
    ecodes.KEY_REFRESH: 0xFA,
    ecodes.KEY_CALC: 0xFB,
    ecodes.BTN_LEFT: lib.usb_hid.Mouse.LEFT_BUTTON,
    ecodes.BTN_RIGHT: lib.usb_hid.Mouse.RIGHT_BUTTON,
    ecodes.BTN_MIDDLE: lib.usb_hid.Mouse.MIDDLE_BUTTON,    
}
"""
Mapping from evdev ecode to HID Keycode
"""

def to_hid_key(ecode : int) -> int:
    hid_key = _EVDEV_TO_HID_MAPPING.get(ecode, None)
    logger.debug(f"Converted ecode {ecode} to HID keycode {hid_key}")
    if hid_key is None:
        logger.warning(f"Unsupported key pressed: {ecode}")
    return hid_key

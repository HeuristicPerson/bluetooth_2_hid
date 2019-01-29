"""
USB HID Keyboard scan codes as per USB spec 1.11
plus some additional codes

Created by MightyPork, 2016
Public domain

Adapted from:
https://source.android.com/devices/input/keyboard-devices.html

Converted to Python by PixelGordo

EXTRA INFORMATION:
http://www.freebsddiary.org/APC/usb_hid_usages.php
"""

ds_MOD_CODES = {
                # Modifier mask - used for the first byte in the HID report.
                'KEY_LEFTCTRL':           chr(0x01),  # 00000001 Left Ctrl
                'KEY_LEFTSHIFT':          chr(0x02),  # 00000010 Left Shift
                'KEY_LEFTALT':            chr(0x04),  # 00000100 Left Alt
                'KEY_LEFTMETA':           chr(0x08),  # 00001000 Left Meta (Windows key?)
                'KEY_RIGHTCTRL':          chr(0x10),  # 00010000 Right Ctrl
                'KEY_RIGHTSHIFT':         chr(0x20),  # 00100000 Right Shift
                'KEY_RIGHTALT':           chr(0x40),  # 01000000 Right Alt
                'KEY_RIGHTMETA':          chr(0x80),  # 10000000 Right Meta (Windows key?)
}

ds_KEY_TO_HID = {
                # Scan codes - last N slots in the HID report (usually 6). 0x00 if no key pressed. If more than N keys
                #              are pressed, the HID reports "KEY_ERR_OVF" in all slots to indicate this condition.
                'KEY_NONE':               chr(0x00),  # No key pressed
                'KEY_ERR_OVF':            chr(0x01),  # Keyboard Error Roll Over - used for all slots if too many keys are
                                                      # pressed ("Phantom key")
                # '???????':              chr(0x02),  # Keyboard POST Fail
                # '???????':              chr(0x03),  # Keyboard Error Undefined
                'KEY_A':                  chr(0x04),  # Keyboard a and A
                'KEY_B':                  chr(0x05),  # Keyboard b and B
                'KEY_C':                  chr(0x06),  # Keyboard c and C
                'KEY_D':                  chr(0x07),  # Keyboard d and D
                'KEY_E':                  chr(0x08),  # Keyboard e and E
                'KEY_F':                  chr(0x09),  # Keyboard f and F
                'KEY_G':                  chr(0x0a),  # Keyboard g and G
                'KEY_H':                  chr(0x0b),  # Keyboard h and H
                'KEY_I':                  chr(0x0c),  # Keyboard i and I
                'KEY_J':                  chr(0x0d),  # Keyboard j and J
                'KEY_K':                  chr(0x0e),  # Keyboard k and K
                'KEY_L':                  chr(0x0f),  # Keyboard l and L
                'KEY_M':                  chr(0x10),  # Keyboard m and M
                'KEY_N':                  chr(0x11),  # Keyboard n and N
                'KEY_O':                  chr(0x12),  # Keyboard o and O
                'KEY_P':                  chr(0x13),  # Keyboard p and P
                'KEY_Q':                  chr(0x14),  # Keyboard q and Q
                'KEY_R':                  chr(0x15),  # Keyboard r and R
                'KEY_S':                  chr(0x16),  # Keyboard s and S
                'KEY_T':                  chr(0x17),  # Keyboard t and T
                'KEY_U':                  chr(0x18),  # Keyboard u and U
                'KEY_V':                  chr(0x19),  # Keyboard v and V
                'KEY_W':                  chr(0x1a),  # Keyboard w and W
                'KEY_X':                  chr(0x1b),  # Keyboard x and X
                'KEY_Y':                  chr(0x1c),  # Keyboard y and Y
                'KEY_Z':                  chr(0x1d),  # Keyboard z and Z

                # Numbers and symbols above the letters
                'KEY_1':                  chr(0x1e),  # Keyboard 1 and !
                'KEY_2':                  chr(0x1f),  # Keyboard 2 and @111111121
                'KEY_3':                  chr(0x20),  # Keyboard 3 and #
                'KEY_4':                  chr(0x21),  # Keyboard 4 and $
                'KEY_5':                  chr(0x22),  # Keyboard 5 and %
                'KEY_6':                  chr(0x23),  # Keyboard 6 and ^
                'KEY_7':                  chr(0x24),  # Keyboard 7 and &
                'KEY_8':                  chr(0x25),  # Keyboard 8 and *
                'KEY_9':                  chr(0x26),  # Keyboard 9 and (
                'KEY_0':                  chr(0x27),  # Keyboard 0 and )

                # Special characters and keys
                'KEY_ENTER':              chr(0x28),  # Keyboard Return (ENTER)
                'KEY_ESC':                chr(0x29),  # Keyboard ESCAPE
                'KEY_BACKSPACE':          chr(0x2a),  # Keyboard DELETE (Backspace)
                'KEY_TAB':                chr(0x2b),  # Keyboard Tab
                'KEY_SPACE':              chr(0x2c),  # Keyboard Spacebar
                'KEY_MINUS':              chr(0x2d),  # Keyboard - and _
                'KEY_EQUAL':              chr(0x2e),  # Keyboard = and +
                'KEY_LEFTBRACE':          chr(0x2f),  # Keyboard [ and {
                'KEY_RIGHTBRACE':         chr(0x30),  # Keyboard ] and }
                'KEY_BACKSLASH':          chr(0x31),  # Keyboard \ and |
                'KEY_HASHTILDE':          chr(0x32),  # Keyboard Non-US # and ~
                'KEY_SEMICOLON':          chr(0x33),  # Keyboard ; and :
                'KEY_APOSTROPHE':         chr(0x34),  # Keyboard ' and "
                'KEY_GRAVE':              chr(0x35),  # Keyboard ` and ~
                'KEY_COMMA':              chr(0x36),  # Keyboard , and <
                'KEY_DOT':                chr(0x37),  # Keyboard . and >
                'KEY_SLASH':              chr(0x38),  # Keyboard / and ?
                'KEY_CAPSLOCK':           chr(0x39),  # Keyboard Caps Lock

                # Function keys (I never saw a keyboard with function keys beyond F12 :/
                'KEY_F1':                 chr(0x3a),  # Keyboard F1
                'KEY_F2':                 chr(0x3b),  # Keyboard F2
                'KEY_F3':                 chr(0x3c),  # Keyboard F3
                'KEY_F4':                 chr(0x3d),  # Keyboard F4
                'KEY_F5':                 chr(0x3e),  # Keyboard F5
                'KEY_F6':                 chr(0x3f),  # Keyboard F6
                'KEY_F7':                 chr(0x40),  # Keyboard F7
                'KEY_F8':                 chr(0x41),  # Keyboard F8
                'KEY_F9':                 chr(0x42),  # Keyboard F9
                'KEY_F10':                chr(0x43),  # Keyboard F10
                'KEY_F11':                chr(0x44),  # Keyboard F11
                'KEY_F12':                chr(0x45),  # Keyboard F12
                'KEY_F13':                chr(0x68),  # Keyboard F13
                'KEY_F14':                chr(0x69),  # Keyboard F14
                'KEY_F15':                chr(0x6a),  # Keyboard F15
                'KEY_F16':                chr(0x6b),  # Keyboard F16
                'KEY_F17':                chr(0x6c),  # Keyboard F17
                'KEY_F18':                chr(0x6d),  # Keyboard F18
                'KEY_F19':                chr(0x6e),  # Keyboard F19
                'KEY_F20':                chr(0x6f),  # Keyboard F20
                'KEY_F21':                chr(0x70),  # Keyboard F21
                'KEY_F22':                chr(0x71),  # Keyboard F22
                'KEY_F23':                chr(0x72),  # Keyboard F23
                'KEY_F24':                chr(0x73),  # Keyboard F24

                # Cursors and typical keys above them
                'KEY_SYSRQ':              chr(0x46),  # Keyboard Print Screen
                'KEY_SCROLLLOCK':         chr(0x47),  # Keyboard Scroll Lock
                'KEY_PAUSE':              chr(0x48),  # Keyboard Pause
                'KEY_INSERT':             chr(0x49),  # Keyboard Insert
                'KEY_HOME':               chr(0x4a),  # Keyboard Home
                'KEY_PAGEUP':             chr(0x4b),  # Keyboard Page Up
                'KEY_DELETE':             chr(0x4c),  # Keyboard Delete Forward
                'KEY_END':                chr(0x4d),  # Keyboard End
                'KEY_PAGEDOWN':           chr(0x4e),  # Keyboard Page Down
                'KEY_RIGHT':              chr(0x4f),  # Keyboard Right Arrow
                'KEY_LEFT':               chr(0x50),  # Keyboard Left Arrow
                'KEY_DOWN':               chr(0x51),  # Keyboard Down Arrow
                'KEY_UP':                 chr(0x52),  # Keyboard Up Arrow

                # Numeric pad
                'KEY_NUMLOCK':            chr(0x53),  # Keyboard Num Lock and Clear
                'KEY_KPSLASH':            chr(0x54),  # K #pad /
                'KEY_KPASTERISK':         chr(0x55),  # Keypad *
                'KEY_KPMINUS':            chr(0x56),  # Keypad -
                'KEY_KPPLUS':             chr(0x57),  # Keypad +
                'KEY_KPENTER':            chr(0x58),  # Keypad ENTER
                'KEY_KP1':                chr(0x59),  # Keypad 1 and End
                'KEY_KP2':                chr(0x5a),  # Keypad 2 and Down Arrow
                'KEY_KP3':                chr(0x5b),  # Keypad 3 and PageDn
                'KEY_KP4':                chr(0x5c),  # Keypad 4 and Left Arrow
                'KEY_KP5':                chr(0x5d),  # Keypad 5
                'KEY_KP6':                chr(0x5e),  # Keypad 6 and Right Arrow
                'KEY_KP7':                chr(0x5f),  # Keypad 7 and Home
                'KEY_KP8':                chr(0x60),  # Keypad 8 and Up Arrow
                'KEY_KP9':                chr(0x61),  # Keypad 9 and Page Up
                'KEY_KP0':                chr(0x62),  # Keypad 0 and Insert
                'KEY_KPDOT':              chr(0x63),  # Keypad . and Delete

                # Other keys
                'KEY_102ND':              chr(0x64),  # Keyboard Non-US \ and |
                'KEY_COMPOSE':            chr(0x65),  # Keyboard Application
                'KEY_POWER':              chr(0x66),  # Keyboard Power
                'KEY_KPEQUAL':            chr(0x67),  # Keypad =
                'KEY_OPEN':               chr(0x74),  # Keyboard Execute
                'KEY_HELP':               chr(0x75),  # Keyboard Help
                'KEY_PROPS':              chr(0x76),  # Keyboard Menu
                'KEY_FRONT':              chr(0x77),  # Keyboard Select
                'KEY_STOP':               chr(0x78),  # Keyboard Stop
                'KEY_AGAIN':              chr(0x79),  # Keyboard Again
                'KEY_UNDO':               chr(0x7a),  # Keyboard Undo
                'KEY_CUT':                chr(0x7b),  # Keyboard Cut
                'KEY_COPY':               chr(0x7c),  # Keyboard Copy
                'KEY_PASTE':              chr(0x7d),  # Keyboard Paste
                'KEY_FIND':               chr(0x7e),  # Keyboard Find
                'KEY_MUTE':               chr(0x7f),  # Keyboard Mute
                'KEY_VOLUMEUP':           chr(0x80),  # Keyboard Volume Up
                'KEY_VOLUMEDOWN':         chr(0x81),  # Keyboard Volume Down

                # Some weird keys, maybe coming from software keyboards
                #'???':                   chr(0x82),  # Keyboard Locking Caps Lock
                #'???':                   chr(0x83),  # Keyboard Locking Num Lock
                #'???':                   chr(0x84),  # Keyboard Locking Scroll Lock
                'KEY_KPCOMMA':            chr(0x85),  # Keypad Comma
                #'???':                   chr(0x86),  # Keypad Equal Sign
                'KEY_RO':                 chr(0x87),  # Keyboard International1
                'KEY_KATAKANAHIRAGANA':   chr(0x88),  # Keyboard International2
                'KEY_YEN':                chr(0x89),  # eyboard International3
                'KEY_HENKAN':             chr(0x8a),  # Keyboard International4
                'KEY_MUHENKAN':           chr(0x8b),  # Keyboard International5
                'KEY_KPJPCOMMA':          chr(0x8c),  # Keyboard International6
                #'???':                   chr(0x8d),  # Keyboard International7
                #'???':                   chr(0x8e),  # Keyboard International8
                #'???':                   chr(0x8f),  # Keyboard International9
                'KEY_HANGEUL':            chr(0x90),  # Keyboard LANG1
                'KEY_HANJA':              chr(0x91),  # Keyboard LANG2
                'KEY_KATAKANA':           chr(0x92),  # Keyboard LANG3
                'KEY_HIRAGANA':           chr(0x93),  # Keyboard LANG4
                'KEY_ZENKAKUHANKAKU':     chr(0x94),  # Keyboard LANG5
                #'???':                   chr(0x95),  # Keyboard LANG6
                #'???':                   chr(0x96),  # Keyboard LANG7
                #'???':                   chr(0x97),  # Keyboard LANG8
                #'???':                   chr(0x98),  # Keyboard LANG9
                #'???':                   chr(0x99),  # Keyboard Alternate Erase
                #'???':                   chr(0x9a),  # Keyboard SysReq/Attention
                #'???':                   chr(0x9b),  # Keyboard Cancel
                #'???':                   chr(0x9c),  # Keyboard Clear
                #'???':                   chr(0x9d),  # Keyboard Prior
                #'???':                   chr(0x9e),  # Keyboard Return
                #'???':                   chr(0x9f),  # Keyboard Separator
                #'???':                   chr(0xa0),  # Keyboard Out
                #'???':                   chr(0xa1),  # Keyboard Oper
                #'???':                   chr(0xa2),  # Keyboard Clear/Again
                #'???':                   chr(0xa3),  # Keyboard CrSel/Props
                #'???':                   chr(0xa4),  # Keyboard ExSel

                # Multimedia keys
                'KEY_MEDIA_PLAYPAUSE':    chr(0xe8),  # Keyboard Play/Pause
                'KEY_MEDIA_STOPCD':       chr(0xe9),  # Keyboard Stop
                'KEY_MEDIA_PREVIOUSSONG': chr(0xea),  # Keyboard Previous Song
                'KEY_MEDIA_NEXTSONG':     chr(0xeb),  # Keyboard Next Song
                'KEY_MEDIA_EJECTCD':      chr(0xec),  # Keyboard Eject CD
                'KEY_MEDIA_VOLUMEUP':     chr(0xed),  # Keyboard Volume Up
                'KEY_MEDIA_VOLUMEDOWN':   chr(0xee),  # Keyboard Volume Down
                'KEY_MEDIA_MUTE':         chr(0xef),  # Keyboard Mute
                'KEY_MEDIA_WWW':          chr(0xf0),  # Keyboard Web Browser
                'KEY_MEDIA_BACK':         chr(0xf1),  # Keyboard Back
                'KEY_MEDIA_FORWARD':      chr(0xf2),  # Keyboard Forward
                'KEY_MEDIA_STOP':         chr(0xf3),  # Keyboard Stop
                'KEY_MEDIA_FIND':         chr(0xf4),  # Keyboard Find
                'KEY_MEDIA_SCROLLUP':     chr(0xf5),  # Keyboard Scroll Up
                'KEY_MEDIA_SCROLLDOWN':   chr(0xf6),  # Keyboard Scroll Down
                'KEY_MEDIA_EDIT':         chr(0xf7),  # Keyboard Edit
                'KEY_MEDIA_SLEEP':        chr(0xf8),  # Keyboard Sleep
                'KEY_MEDIA_COFFEE':       chr(0xf9),  # Keyboard Coffee (?)
                'KEY_MEDIA_REFRESH':      chr(0xfa),  # Keyboard Refresh
                'KEY_MEDIA_CALC':         chr(0xfb),  # Keyboard Calculator

                # Modifiers
                'KEY_LEFTCTRL':           chr(0xe0),  # Keyboard Left Control
                'KEY_LEFTSHIFT':          chr(0xe1),  # Keyboard Left Shift
                'KEY_LEFTALT':            chr(0xe2),  # Keyboard Left Alt
                'KEY_LEFTMETA':           chr(0xe3),  # Keyboard Left GUI
                'KEY_RIGHTCTRL':          chr(0xe4),  # Keyboard Right Control
                'KEY_RIGHTSHIFT':         chr(0xe5),  # Keyboard Right Shift
                'KEY_RIGHTALT':           chr(0xe6),  # Keyboard Right Alt
                'KEY_RIGHTMETA':          chr(0xe7),  # Keyboard Right GUI
}


# TODO: These keys don't exist in a normal keyboard, should they be added?
#// 0xb0  Keypad 00
#// 0xb1  Keypad 000
#// 0xb2  Thousands Separator
#// 0xb3  Decimal Separator
#// 0xb4  Currency Unit
#// 0xb5  Currency Sub-unit
#define KEY_KPLEFTPAREN 0xb6 // Keypad (
#define KEY_KPRIGHTPAREN 0xb7 // Keypad )
#// 0xb8  Keypad {
#// 0xb9  Keypad }
#// 0xba  Keypad Tab
#// 0xbb  Keypad Backspace
#// 0xbc  Keypad A
#// 0xbd  Keypad B
#// 0xbe  Keypad C
#// 0xbf  Keypad D
#// 0xc0  Keypad E
#// 0xc1  Keypad F
#// 0xc2  Keypad XOR
#// 0xc3  Keypad ^
#// 0xc4  Keypad %
#// 0xc5  Keypad <
#// 0xc6  Keypad >
#// 0xc7  Keypad &
#// 0xc8  Keypad &&
#// 0xc9  Keypad |
#// 0xca  Keypad ||
#// 0xcb  Keypad :
#// 0xcc  Keypad #
#// 0xcd  Keypad Space
#// 0xce  Keypad @
#// 0xcf  Keypad !
#// 0xd0  Keypad Memory Store
#// 0xd1  Keypad Memory Recall
#// 0xd2  Keypad Memory Clear
#// 0xd3  Keypad Memory Add
#// 0xd4  Keypad Memory Subtract
#// 0xd5  Keypad Memory Multiply
#// 0xd6  Keypad Memory Divide
#// 0xd7  Keypad +/-
#// 0xd8  Keypad Clear
#// 0xd9  Keypad Clear Entry
#// 0xda  Keypad Binary
#// 0xdb  Keypad Octal
#// 0xdc  Keypad Decimal
#// 0xdd  Keypad Hexadecimal

# Reverse dictionary that I use in my debug functions
ds_HID_TO_KEY = {}
for s_key, s_value in ds_KEY_TO_HID.iteritems():
    ds_HID_TO_KEY[s_value] = s_key

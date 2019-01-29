import hid_codes

# Constants
#=======================================================================================================================
s_NULL_CHAR = chr(0)


# Classes
#=======================================================================================================================
class HidKeyboard(object):
    """
    Class to store the status information of a HID keyboard (maximum of 6 keys pressed apart from the modifiers --Shift,
    Ctrl, Alt, Meta).
    """

    def __init__(self):
        self._ls_keys = []          # list of active (pressed) keys (stored as key identifiers)
        self._db_modifiers = {'KEY_LEFTALT': False,
                              'KEY_LEFTCTRL': False,
                              'KEY_LEFTMETA': False,
                              'KEY_LEFTSHIFT': False,
                              'KEY_RIGHTALT': False,
                              'KEY_RIGHTCTRL': False,
                              'KEY_RIGHTMETA': False,
                              'KEY_RIGHTSHIFT': False}

    def __unicode__(self):
        u_out = u'<HidKeyboard>\n'
        u_out += u'  .s_mod_byte: %s %s\n' % (str(ord(self.s_mod_byte)).rjust(3, '0'), self._get_human_modifier())
        return u_out

    def __str__(self):
        return unicode(self).encode('utf8')

    def modifier_set(self, ps_mod_name, pi_value):
        """
        Method to activate one modifier by its name.
        :param ps_mod_name: name of the modifier. e.g. "KEY_LEFTSHIFT"
        :param pi_value: 0 for off, 1 for on.
        :return: Nothing
        """
        if ps_mod_name in self._db_modifiers:
            self._db_modifiers[ps_mod_name] = bool(pi_value)
        else:
            raise ValueError('Invalid modifier name "%s"' % ps_mod_name)

    def to_hid_command(self):
        """
        Method to build the HID command string. See
        https://files.microscan.com/helpfiles/ms4_help_file/ms-4_help-02-46.html

        :return: A byte string with the encoded HID command.
        """
        # Hid bytes command header, modifiers and separation
        ls_hid_bytes = [self.s_mod_byte, s_NULL_CHAR]

        # Then we must convert all the key names stored to proper hid bytes
        for s_key_name in self._ls_keys:
            s_hid_byte = hid_codes.ds_KEY_TO_HID[s_key_name]
            ls_hid_bytes.append(s_hid_byte)

        # The report must contain 6 keys ALWAYS!!!
        # https://files.microscan.com/helpfiles/ms4_help_file/ms-4_help-02-46.html
        i_fill_keys = 6 - len(self._ls_keys)
        for i_fill in range(i_fill_keys):
            ls_hid_bytes.append(s_NULL_CHAR)

        # To finish, we join everything together
        s_hid_string = ''.join(ls_hid_bytes)

        return s_hid_string

    def to_debug_command(self):
        """
        Method to build a debug command line to print in human format the HID command
        :return:
        """
        u_out = u'%s | %s' % (self._get_human_modifier(), self._get_human_keys())
        return u_out

    def _get_human_modifier(self):
        """
        Method to get an human readable string representing the status of the modifiers
        :return:
        """
        """
        Function to print debug information.
        :param ps_string:
        :return:
        """
        i_mod_byte = ord(self.s_mod_byte)

        u_out = u''

        # Modifiers
        # ----------
        lu_mods = []
        if i_mod_byte & ord(hid_codes.ds_MOD_CODES['KEY_LEFTCTRL']):
            lu_mods.append(u'lC')
        else:
            lu_mods.append(u'__')

        if i_mod_byte & ord(hid_codes.ds_MOD_CODES['KEY_LEFTSHIFT']):
            lu_mods.append(u'lS')
        else:
            lu_mods.append(u'__')

        if i_mod_byte & ord(hid_codes.ds_MOD_CODES['KEY_LEFTALT']):
            lu_mods.append(u'lA')
        else:
            lu_mods.append(u'__')

        if i_mod_byte & ord(hid_codes.ds_MOD_CODES['KEY_LEFTMETA']):
            lu_mods.append(u'lM')
        else:
            lu_mods.append(u'__')

        if i_mod_byte & ord(hid_codes.ds_MOD_CODES['KEY_RIGHTCTRL']):
            lu_mods.append(u'rC')
        else:
            lu_mods.append(u'__')

        if i_mod_byte & ord(hid_codes.ds_MOD_CODES['KEY_RIGHTSHIFT']):
            lu_mods.append(u'rS')
        else:
            lu_mods.append(u'__')

        if i_mod_byte & ord(hid_codes.ds_MOD_CODES['KEY_RIGHTALT']):
            lu_mods.append(u'rA')
        else:
            lu_mods.append(u'__')

        if i_mod_byte & ord(hid_codes.ds_MOD_CODES['KEY_RIGHTMETA']):
            lu_mods.append(u'rM')
        else:
            lu_mods.append(u'__')

        u_out += u' '.join(lu_mods)

        return u_out

    def _get_human_keys(self):
        """
        Method to get an human readable string representing the keys down of the keyboard
        :return:
        """
        lu_keys_out = []
        for s_key_name in self._ls_keys:
            h_key_byte = hex(ord(hid_codes.ds_KEY_TO_HID[s_key_name]))
            u_key_out = u'(%s) %s' % (h_key_byte, s_key_name)
            lu_keys_out.append(u_key_out)

        u_keys = u' + '.join(lu_keys_out)
        u_out = u'[%i] %s' % (len(self._ls_keys), u_keys)

        return u_out

    def activate_key(self, ps_key):
        """
        Method to add a key to the list of pressed keys. Because our HID keyboard has a maximum of 6 pressed keys at the
        same time, we need to make a decision:

            a) Not reading new keys pressed. e.g. A-B-C-D-E-F-H-I would result in A-B-C-D-E-F
            b) Replace old keys by new ones. e.g. A-B-C-D-E-F-H-I would result in C-D-E-F-H-I

        To me, the first option makes more sense or it's "safer" in the sense that nothing new is read but you are sure
        about what you typed before. If you choose option b) instead, by adding a new key remove something from the past
        and weird short-cuts could appear.

        :param ps_key:
        :return:
        """
        if ps_key not in self._ls_keys:
            i_keys = len(self._ls_keys)
            if i_keys == 6:
                self._ls_keys.pop(0)

            self._ls_keys.append(ps_key)

    def deactivate_key(self, ps_key):
        """
        Method to remove a key from the list of pressed keys.
        :param ps_key:
        :return:
        """
        if ps_key in self._ls_keys:
            self._ls_keys.remove(ps_key)

    def _get_mod_byte(self):
        """
        Method to return the HID modifiers byte. e.g.

            - Just left Ctrl pressed would be:       00000001
            - Left control and right shift would be: 00100001

        :return: a byte representing the state of each modifier.
        """
        i_mod_byte = 0

        for s_mod_name, b_mod_active in self._db_modifiers.iteritems():
            i_mod_value = ord(hid_codes.ds_MOD_CODES[s_mod_name])
            if b_mod_active:
                i_mod_byte += i_mod_value

        return chr(i_mod_byte)

    s_mod_byte = property(fget=_get_mod_byte, fset=None)

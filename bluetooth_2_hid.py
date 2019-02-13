#!/usr/bin/env python

"""
Author:     @PixelGordo
Date:       2019-01-27
Version:    0.1
References: https://www.isticktoit.net/?p=1383
            https://github.com/mikerr/pihidproxy
========================================================================================================================
Script that reads the inputs of one keyboard (typically you would like to read a bluetooth keyboard) and translates them
to HID proxy commands through the USB cable. This way you can have the connections below:

    Keyboard --(bluetooth)--> Raspberry Pi Zero W --(usb)--> Computer

The final result is the computer (on the right) receives inputs as if they were coming from an USB keyboard. The
advantages of this technique are:

    - You can use your bluetooth keyboard on any device that has USB connection, no bluetooth drivers or software is
      required.
    - You can use your bluetooth keyboard in the BIOS or GRUB menu.
    - You can use any bluetooth keyboard, even when they require a pairing password. You must do the pairing between
      the Raspberry Pi and the bluetooth using that password but after that, you don't need to repeat the process, the
      raspberry pi and the keyboard will remain paired even when you connect the Raspberry Pi to a different computer
      (similar to what happens with the typical USB dongles that come with Logitech mouses).
    - ...not implemented, but you could create your own macros in this script that would work in any computer you plug
      the keyboard+raspberry. I'm thinking about Ctr-Shift-L to automatically send the keys of Lorem Ipsum...
"""

import argparse
import os
import sys
import time

import evdev

from libs import hid_codes
from libs import keyboard

# READ THIS: https://www.isticktoit.net/?p=1383

# Constants
#=======================================================================================================================
u_INPUT_DEV = u'/dev/input/event0'   # In the Raspberry Pi Zero (apparently)
u_OUTPUT_DEV = u'/dev/hidg0'
u_LOG_FILE = u'/tmp/blu2hid.log'


# Helper Functions
#=======================================================================================================================
def _get_cmd_args():
    """
    Function to get command line arguments.
    :return:
    """
    # [1/?] Defining the parser
    #--------------------------
    o_parser = argparse.ArgumentParser()
    o_parser.add_argument('-i',
                          action='store',
                          default=u_INPUT_DEV,
                          help='Input device (Bluetooth Keyboard). By default it\'s "/dev/input/event0"')
    o_parser.add_argument('-o',
                          action='store',
                          default=u_OUTPUT_DEV,
                          help='Output device (HID controller). By default it\'s "/dev/hidg0"')
    o_parser.add_argument('-d',
                          action='store_true',
                          default=False,
                          help='Debug mode ON. It\'ll print on screen information about the input keys detected and the'
                               'output HID command sent')
    o_parser.add_argument('-t',
                          action='store_true',
                          default=False,
                          help='Test mode ON. The program will read the inputs normally but it won\'t generate the'
                               'output HID commands. This mode is useful to check that everything is working fine apart'
                               'from the actual HID command delivery')
    o_parser.add_argument('-l',
                          action='store_true',
                          default=False,
                          help='Log mode ON. The program will write a log file "/tmp/bluetooth2hid.log" containing any'
                               'unknown input key')

    o_parsed_data = o_parser.parse_args()

    # [2/?] Validation of the command line arguments
    #-----------------------------------------------
    # I validate the options first because depending on their values, we can relax the requirements on the output
    b_mode_debug = o_parsed_data.d
    b_mode_test = o_parsed_data.t
    b_mode_log = o_parsed_data.l

    print u'[ pass ]    Debug mode: %s' % b_mode_debug
    print u'[ pass ]     Test mode: %s' % b_mode_test
    print u'[ pass ]      Log mode: %s (%s)' % (b_mode_log, u_LOG_FILE)

    # Input device
    #-------------
    # I'm not sure about this validation because I don't know what happens when you first connect the Bluetooth without
    # any activity on the keyboard. If the keyboard doesn't activate, this validation will fail. Anyway, once the
    # program is running, the main loop is able to keep trying the connection if it's not found.
    u_input = unicode(o_parsed_data.i)
    #if not (os.access(u_input, os.F_OK) and os.access(u_input, os.R_OK)):
    #    print u'[ FAIL ]  Input device: %s (can\'t be read or is not found)' % u_input
    #    sys.exit()
    #else:
    #    print u'[ pass ]  Input device: %s' % u_input
    print u'[ pass ]  Input device: %s' % u_input

    # Output device
    #--------------
    u_output = unicode(o_parsed_data.o)
    #if not (os.access(u_input, os.F_OK) and os.access(u_input, os.W_OK)):
    #    if b_mode_test:
    #        print u'[ INFO ] Output device: %s (can\'t be read or is not found)' % u_output
    #    else:
    #        print u'[ FAIL ] Output device: %s (can\'t be read or is not found)' % u_output
    #        sys.exit()
    #else:
    #    print u'[ pass ] Output device: %s' % u_output
    print u'[ pass ] Output device: %s' % u_output

    return {'u_input': u_input,
            'u_output': u_output,
            'b_mode_debug': b_mode_debug,
            'b_mode_test': b_mode_test,
            'b_mode_log': b_mode_log}


def _get_input_device(pu_device):
    """
    Function to get the device object.
    :param pu_device:
    :return: The device object.
    """

    o_device = None
    while o_device is None:
        try:
            o_device = evdev.InputDevice(pu_device)
        except OSError:
            print u'[ WAIT ] Opening Bluetooth input (%s)...' % u_INPUT_DEV
            time.sleep(3)

    print u'[ pass ] Bluetooth input open (%s)' % unicode(pu_device)
    return o_device


def _get_output_device(pu_device):
    """
    Function to get the output object.
    :param pu_device:
    :return: The device object.
    """

    o_device = None
    while o_device is None:
        try:
            o_device = open(pu_device, 'wb+', buffering=0)
        except OSError:
            print u'[ WAIT ] Opening HID output (%s)...' % u_OUTPUT_DEV
            time.sleep(3)

    print u'[ pass ] HID output open (%s)' % unicode(pu_device)
    return o_device


def _get_devices(pu_input, pu_output, po_input, po_output):
    """
    Function to get both devices, input and output.
    :param pu_input:
    :param pu_output:
    :return:
    """
    pass

# Main Code
#=======================================================================================================================
if __name__ == '__main__':
    print u'Bluetooth to HID events translator v0.1 2019-01-29'
    print u'=================================================='

    o_args = _get_cmd_args()

    # Initialization
    #---------------
    o_hid_keyboard = keyboard.HidKeyboard()
    o_input_device = _get_input_device(o_args['u_input'])
    o_output_device = _get_output_device(o_args['u_output'])

    # Main loop
    #----------
    while True:
        try:
            for o_event in o_input_device.read_loop():
                if o_event.type == evdev.ecodes.EV_KEY:
                    # Pre-parsing the event so it's easier to work with it for our purposes
                    o_data = evdev.categorize(o_event)

                    # [1/?] Getting the HID byte for the modifier keys
                    #-------------------------------------------------
                    # The modifier status will only change when they are pressed (1) or released (0) (not when they are
                    # hold)
                    if (o_data.keystate in (0, 1)) and (o_data.keycode in hid_codes.ds_MOD_CODES):
                        o_hid_keyboard.modifier_set(o_data.keycode, o_data.keystate)

                    # [2/?] Activating or deactivating keys in our HidKeyboard when needed
                    #---------------------------------------------------------------------
                    # We only send hid commands when there is a change, so with key-down (1) and key-up (0) events
                    if o_data.keystate == 0:
                        o_hid_keyboard.deactivate_key(o_data.keycode)
                    elif o_data.keystate == 1:
                        o_hid_keyboard.activate_key(o_data.keycode)

                    # [3/?] When any change occurs, we need to send the HID command
                    #--------------------------------------------------------------
                    if o_data.keystate in (0, 1):
                        if o_args['b_mode_debug']:
                            print o_hid_keyboard.to_debug_command()

                        if not o_args['b_mode_test']:
                            s_hid_command = o_hid_keyboard.to_hid_command()
                            try:
                                o_output_device.write(s_hid_command)
                            except IOError:
                                print u'--------------------------------------------------'
                                _get_output_device(o_args['u_output'])
                                print u'--------------------------------------------------'
                                o_output_device.write(s_hid_command)

        # The o_input_device cannot be read
        except IOError:
            print u'--------------------------------------------------'
            o_input_device = _get_input_device(o_args['u_input'])
            print u'--------------------------------------------------'

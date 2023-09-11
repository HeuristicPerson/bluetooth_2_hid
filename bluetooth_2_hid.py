#!/usr/bin/env python
"""
Reads incoming mouse and keyboard events (e.g., Bluetooth) and forwards them to USB using Linux gadget mode 
"""

import argparse
import logging
import sys
import signal
import usb_hid
from select import select

from evdev import InputDevice, ecodes
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.mouse import Mouse

from evdev_2_hid import Converter

# Initialize logging
logging.basicConfig(level=logging.INFO)

def signal_handler(sig, frame):
    logging.info('Exiting gracefully')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

class ComboDeviceHidProxy:
    def __init__(self, keyboard_in: str, mouse_in: str):
        try:
            self.keyboard_in = InputDevice(keyboard_in)
            self.keyboard_out = Keyboard(usb_hid.devices) 
            self.mouse_in = InputDevice(mouse_in)
            self.mouse_out =  Mouse(usb_hid.devices)
            self.converter = Converter()
            self.input_devices = {dev.fd: dev for dev in [self.keyboard_in, self.mouse_in] if dev is not None}
        except Exception as e:
            logging.error(f"Failed to initialize devices: {e}")
            sys.exit(1)

    def handle_key(self, event):
        if self.is_mouse_button(event):
            self.handle_mouse_button(event)
        else:
            self.handle_keyboard_key(event) 

    def handle_keyboard_key(self, event):
        key = self.converter.to_hid_key(event.code) 

        if event.value == 0:
            self.keyboard_out.release(key)
        elif event.value == 1:
            self.keyboard_out.press(key)     

    def handle_mouse_button(self, event):
        button = self.converter.to_hid_mouse_button(event)
 
        if event.value == 0:
            self.mouse_out.release(button)
        elif event.value == 1:
            self.mouse_out.press(button)

    def is_mouse_button(self, event):
        return event.code in [ecodes.BTN_LEFT, ecodes.BTN_RIGHT, ecodes.BTN_MIDDLE]

    def move_mouse(self, event):
        x, y, mwheel = 0

        if event.code == ecodes.REL_X:
            x = event.value
        elif event.code == ecodes.REL_Y:
            y = event.value
        elif event.code == ecodes.REL_WHEEL:
            mwheel = event.value

        self.mouse_out.move(x, y, mwheel)
        
    def combined_event_loop(self):
        while True:
            ready_devices = self.get_ready_devices()
            for device in ready_devices:
                self.read_input_events(device)

    def get_ready_devices(self):
        device_fds = select(self.input_devices, [], [])[0]
        return (self.input_devices[fd] for fd in device_fds)
    
    def read_input_events(self, device):
        if device == self.keyboard_in:
            self.read_keyboard_events()
        else:
            self.read_mouse_events()

    def read_keyboard_events(self):
        for event in self.keyboard_in.read():
            if event.type == ecodes.EV_KEY and event.value < 2:
                self.handle_key(event)

    def read_mouse_events(self):
        for event in self.mouse_in.read():
            if event.type == ecodes.EV_KEY and event.value < 2:
                self.handle_key(event)
            elif event.type == ecodes.EV_REL:
                self.move_mouse(event)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bluetooth to HID proxy.')
    parser.add_argument('--keyboard', type=str, required=True, help='Input device path for keyboard')
    parser.add_argument('--mouse', type=str, required=True, help='Input device path for mouse')
    args = parser.parse_args()
    
    proxy = ComboDeviceHidProxy(keyboard_in=args.keyboard, mouse_in=args.mouse)
    proxy.combined_event_loop()
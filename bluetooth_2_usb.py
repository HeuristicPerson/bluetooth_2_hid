#!/usr/bin/env python
"""
Reads incoming mouse and keyboard events (e.g., Bluetooth) and forwards them to USB using Linux's gadget mode.
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

logging.basicConfig(level=logging.INFO, filename='/var/log/bluetooth_2_usb.log')

def signal_handler(sig, frame):
    logging.info('Exiting gracefully.')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

try:
    usb_hid.enable((usb_hid.Device.KEYBOARD, usb_hid.Device.MOUSE))
except Exception as e:
    logging.error(f"Failed to enable devices. [Message: {e}]")   

class ComboDeviceHidProxy:
    def __init__(self, keyboard_in: str=None, mouse_in: str=None):
        self.keyboard_in = None            
        self.keyboard_out = None
        self.mouse_in = None     
        self.mouse_out = None
        try:
            logging.info(f'Available output devices: {[self.device_repr(dev) for dev in usb_hid.devices]}')
            if keyboard_in is not None:
                self.keyboard_in = InputDevice(keyboard_in)               
                logging.info(f'Keyboard (in): {self.keyboard_in}')
                self.keyboard_out = Keyboard(usb_hid.devices)
                logging.info(f'Keyboard (out): {self.device_repr(self.keyboard_out._keyboard_device)}')
            if mouse_in is not None:
                self.mouse_in = InputDevice(mouse_in)
                logging.info(f'Mouse (in): {self.mouse_in}')
                self.mouse_out = Mouse(usb_hid.devices)
                logging.info(f'Mouse (out): {self.device_repr(self.mouse_out._mouse_device)}')
            self.converter = Converter()
            self.input_devices = {dev.fd: dev for dev in [self.keyboard_in, self.mouse_in] if dev is not None}
        except Exception as e:
            logging.error(f"Failed to initialize devices. [Message: {e}]")
            sys.exit(1)

    def device_repr(self, dev: usb_hid.Device) -> str:
        return dev.get_device_path(None)

    def handle_key(self, event):
        if self.is_mouse_button(event):
            self.handle_mouse_button(event)
        else:
            self.handle_keyboard_key(event) 

    def handle_keyboard_key(self, event):
        key = self.converter.to_hid_key(event) 
        if key is None: return
        try:
            if event.value == 0:
                self.keyboard_out.release(key)
            elif event.value == 1:
                self.keyboard_out.press(key)
        except Exception as e:
            logging.error(f"Error at keyboard event: {event} [Message: {e}]")           

    def handle_mouse_button(self, event):
        button = self.converter.to_hid_mouse_button(event)
        if button is None: return
        try:
            if event.value == 0:
                self.mouse_out.release(button)
            elif event.value == 1:
                self.mouse_out.press(button)
        except Exception as e:
            logging.error(f"Error at mouse button event: {event} [Message: {e}]")        

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
        try:
            self.mouse_out.move(x, y, mwheel)
        except Exception as e:
            logging.error(f"Error at mouse move event: {event} [Message: {e}]")   
        
    def combined_event_loop(self):
        while True:
            ready_devices = self.get_ready_devices()
            for device in ready_devices:
                self.read_input_events(device)

    def get_ready_devices(self):
        try:
            device_fds = select(self.input_devices, [], [])[0]
        except Exception as e:
            logging.error(f"Error getting ready devices. [Message: {e}]")   
        return [self.input_devices[fd] for fd in device_fds if fd is not None]
    
    def read_input_events(self, device):
        if device == self.keyboard_in:
            self.read_keyboard_events()
        else:
            self.read_mouse_events()

    def read_keyboard_events(self):
        for event in self.keyboard_in.read():
            if event is None: continue
            if event.type == ecodes.EV_KEY and event.value < 2:
                self.handle_key(event)

    def read_mouse_events(self):
        for event in self.mouse_in.read():
            if event is None: continue
            if event.type == ecodes.EV_KEY and event.value < 2:
                self.handle_key(event)
            elif event.type == ecodes.EV_REL:
                self.move_mouse(event)

def setup_logging(log_level, log_file):
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    logging.basicConfig(level=numeric_level, filename=log_file, force=True, 
                        format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bluetooth to HID proxy.')
    parser.add_argument('--keyboard', '-k', type=str, default=None, help='Input device path for keyboard')
    parser.add_argument('--mouse', '-m', type=str, default=None, help='Input device path for mouse')
    parser.add_argument('--log_level', '-l', type=str, default='INFO', help='Logging level')
    parser.add_argument('--log_file', '-f', type=str, default='/var/log/bluetooth_2_usb.log', help='Log file path')
    args = parser.parse_args()

    try:
        setup_logging(args.log_level, args.log_file)
    except Exception as e:
        logging.error(f"Failed to setup logging.[Message: {e}]")  
  
    proxy = ComboDeviceHidProxy(keyboard_in=args.keyboard, mouse_in=args.mouse)
    try:
        proxy.combined_event_loop()
    except Exception as e:
        logging.error(f"Unhandled error while processing input events. Abort mission. [Message: {e}]")   

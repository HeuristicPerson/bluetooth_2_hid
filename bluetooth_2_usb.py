#!/usr/bin/env python
"""
Reads incoming mouse and keyboard events (e.g., Bluetooth) and forwards them to USB using Linux's gadget mode.
"""

import argparse
import asyncio
import signal
import sys
import usb_hid
from usb_hid import Device

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.mouse import Mouse
from evdev import InputDevice, ecodes

from lib.evdev_2_hid import Converter
import lib.logger

logger = lib.logger.get_logger()

def signal_handler(sig, frame):
    logger.info('Exiting gracefully.')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

try:
    usb_hid.enable((Device.KEYBOARD, Device.MOUSE))
except Exception as e:
    logger.error(f"Failed to enable devices. [Message: {e}]")   

class ComboDeviceHidProxy:
    def __init__(self, keyboard_in: str=None, mouse_in: str=None, is_sandbox: bool=False):
        self.keyboard_in = None            
        self.keyboard_out = None
        self.mouse_in = None     
        self.mouse_out = None
        self.is_sandbox = is_sandbox
        self._init_devices(keyboard_in, mouse_in)

    def _init_devices(self, keyboard_in, mouse_in):
        try:
            logger.info(f'Available output devices: {self.available_devices_repr()}')
            if keyboard_in is not None:
                self.keyboard_in = InputDevice(keyboard_in)               
                logger.info(f'Keyboard (in): {self.keyboard_in}')
                self.keyboard_out = Keyboard(usb_hid.devices)
                logger.info(f'Keyboard (out): {self.keyboard_repr()}')
            if mouse_in is not None:
                self.mouse_in = InputDevice(mouse_in)
                logger.info(f'Mouse (in): {self.mouse_in}')
                self.mouse_out = Mouse(usb_hid.devices)
                logger.info(f'Mouse (out): {self.mouse_repr()}')
        except Exception as e:
            logger.error(f"Failed to initialize devices. [Message: {e}]")
            sys.exit(1)

    def available_devices_repr(self) -> str:
        return [self.device_repr(dev) for dev in usb_hid.devices]

    def device_repr(self, dev: Device) -> str:
        return dev.get_device_path(None)
    
    def keyboard_repr(self) -> str:
        return self.device_repr(self.keyboard_out._keyboard_device)

    def mouse_repr(self) -> str:
        return self.device_repr(self.mouse_out._mouse_device)
       
    def run_event_loop(self):
        if self.keyboard_in is not None:
            asyncio.ensure_future(self.read_keyboard_events())
        if self.mouse_in is not None:
            asyncio.ensure_future(self.read_mouse_events())
        loop = asyncio.get_event_loop()
        loop.run_forever()
           
    async def read_keyboard_events(self):
        logger.info(f"Started keyboard event loop")   
        async for event in self.keyboard_in.async_read_loop():
            if event is None: continue
            logger.debug(f"Received keyboard event: [{event}]") 
            if self.should_handle_key(event):
                self.handle_key_event(event, self.keyboard_out)
    
    async def read_mouse_events(self):
        logger.info(f"Started mouse event loop") 
        async for event in self.mouse_in.async_read_loop():
            if event is None: continue
            logger.debug(f"Received mouse event: [{event}]") 
            if self.should_handle_key(event):
                self.handle_key_event(event, self.mouse_out)
            elif self.should_handle_mouse_move(event):
                self.handle_move_mouse_event(event, self.mouse_out) 

    def should_handle_key(self, event):
        return self.is_key_up_or_down(event) and not self.is_sandbox
    
    def should_handle_mouse_move(self, event):
        return self.is_mouse_move(event) and not self.is_sandbox
    
    def is_key_up_or_down(self, event):
        return event.type == ecodes.EV_KEY and event.value < 2    
    
    def is_mouse_move(self, event):
        return event.type == ecodes.EV_REL 

    def handle_key_event(self, event, device_out: Device):
        key = Converter.to_hid_key(event.code) 
        if key is None: return
        try:
            if event.value == 0:
                device_out.release(key)
            elif event.value == 1:
                device_out.press(key)
        except Exception as e:
            logger.error(f"Error sending key event [{event}] to device {self.device_repr(device_out)} [{e}]")

    def handle_move_mouse_event(self, event, device_out: Device):
        x, y, mwheel = 0
        if event.code == ecodes.REL_X:
            x = event.value
        elif event.code == ecodes.REL_Y:
            y = event.value
        elif event.code == ecodes.REL_WHEEL:
            mwheel = event.value
        try:
            device_out.move(x, y, mwheel)
        except Exception as e:
            logger.error(f"Error sending mouse move event [{event}] to device {self.device_repr(device_out)} [{e}]")

def parse_args():
    parser = argparse.ArgumentParser(description='Bluetooth to HID proxy.')
    parser.add_argument('--keyboard', '-k', type=str, default=None, help='Input device path for keyboard')
    parser.add_argument('--mouse', '-m', type=str, default=None, help='Input device path for mouse')
    parser.add_argument('--sandbox', '-s', type=bool, default=False, help='Only read input events but do not forward them to the output devices.')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()  
  
    proxy = ComboDeviceHidProxy(args.keyboard, args.mouse, args.sandbox)
    try:
        proxy.run_event_loop()
    except Exception as e:
        logger.error(f"Unhandled error while processing input events. Abort mission. [Message: {e}]")   

#!/usr/bin/env python
"""
Reads incoming mouse and keyboard events (e.g., Bluetooth) and forwards them to USB using Linux's gadget mode.
"""

import argparse
import asyncio
from select import select
import signal
import sys
import usb_hid
from usb_hid import Device

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.mouse import Mouse
from evdev import InputDevice, ecodes

from evdev_2_hid import Converter
from logger import get_logger

logger = get_logger()

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
    def __init__(self, keyboard_in: str=None, mouse_in: str=None):
        self.keyboard_in = None            
        self.keyboard_out = None
        self.mouse_in = None     
        self.mouse_out = None
        try:
            logger.info(f'Available output devices: {[self.device_repr(dev) for dev in usb_hid.devices]}')
            if keyboard_in is not None:
                self.keyboard_in = InputDevice(keyboard_in)               
                logger.info(f'Keyboard (in): {self.keyboard_in}')
                self.keyboard_out = Keyboard(usb_hid.devices)
                logger.info(f'Keyboard (out): {self.device_repr(self.keyboard_out._keyboard_device)}')
            if mouse_in is not None:
                self.mouse_in = InputDevice(mouse_in)
                logger.info(f'Mouse (in): {self.mouse_in}')
                self.mouse_out = Mouse(usb_hid.devices)
                logger.info(f'Mouse (out): {self.device_repr(self.mouse_out._mouse_device)}')
        except Exception as e:
            logger.error(f"Failed to initialize devices. [Message: {e}]")
            sys.exit(1)

    def device_repr(self, dev: Device) -> str:
        return dev.get_device_path(None)

    def handle_keyboard_key(self, event):
        key = Converter.to_hid_key(event) 
        if key is None: return
        try:
            if event.value == 0:
                self.keyboard_out.release(key)
            elif event.value == 1:
                self.keyboard_out.press(key)
        except Exception as e:
            logger.error(f"Error at keyboard event: {event} [Message: {e}]")           

    def handle_mouse_button(self, event):
        button = Converter.to_hid_mouse_button(event)
        if button is None: return
        try:
            if event.value == 0:
                self.mouse_out.release(button)
            elif event.value == 1:
                self.mouse_out.press(button)
        except Exception as e:
            logger.error(f"Error at mouse button event: {event} [Message: {e}]")        

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
            logger.error(f"Error at mouse move event: {event} [Message: {e}]")   
        
    def run_event_loop(self):
        if self.keyboard_in is not None:
            asyncio.ensure_future(self.read_keyboard_events())
        if self.mouse_in is not None:
            asyncio.ensure_future(self.read_mouse_events())
        loop = asyncio.get_event_loop()
        loop.run_forever()
           
    async def read_keyboard_events(self):
        async for event in self.keyboard_in.async_read_loop():
            if event is None: continue
            if event.type == ecodes.EV_KEY and event.value < 2:
                self.handle_keyboard_key(event)
    
    async def read_mouse_events(self):
        async for event in self.mouse_in.async_read_loop():
            if event is None: continue
            if event.type == ecodes.EV_KEY and event.value < 2:
                self.handle_mouse_button(event)
            elif event.type == ecodes.EV_REL:
                self.move_mouse(event)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bluetooth to HID proxy.')
    parser.add_argument('--keyboard', '-k', type=str, default=None, help='Input device path for keyboard')
    parser.add_argument('--mouse', '-m', type=str, default=None, help='Input device path for mouse')
    args = parser.parse_args()  
  
    proxy = ComboDeviceHidProxy(keyboard_in=args.keyboard, mouse_in=args.mouse)
    try:
        proxy.run_event_loop()
    except Exception as e:
        logger.error(f"Unhandled error while processing input events. Abort mission. [Message: {e}]")   

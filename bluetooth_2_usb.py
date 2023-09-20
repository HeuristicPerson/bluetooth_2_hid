#!/usr/bin/env python
"""
Reads incoming mouse and keyboard events (e.g., Bluetooth) and forwards them to USB using Linux's gadget mode.
"""

try:
    import argparse
    import asyncio
    from asyncio import TaskGroup, Task
    from datetime import datetime
    import gc
    import logging
    import os
    import signal
    import sys
    import threading
    from typing import Union
    import psutil

    from evdev import InputDevice, InputEvent, categorize, ecodes, list_devices

    from lib.constants import errno, key_event
    import lib.evdev_converter as converter
    import lib.logger
    import lib.usb_hid
    from lib.usb_hid import Device as OutputDevice, Mouse, Keyboard
except ImportError as e:
    print(f"Error importing modules. [{e}]")
    raise

logger = lib.logger.get_logger()

class ComboDeviceHidProxy:
    def __init__(self, keyboard_in: str=None, mouse_in: str=None, is_sandbox: bool=False, is_main: bool=False):
        self._init_variables(is_sandbox, is_main)
        self._enable_usb_gadgets(keyboard_in, mouse_in)
        self._init_devices(keyboard_in, mouse_in)
        if self._is_sandbox:
            self._enable_sandbox()

    def _init_variables(self, is_sandbox: bool=False, is_main: bool=False):
        self._keyboard_in = None            
        self._keyboard_out = None
        self._mouse_in = None     
        self._mouse_out = None
        self._is_sandbox = is_sandbox
        self._is_main = is_main

    def _enable_usb_gadgets(self, keyboard_in: str=None, mouse_in: str=None):
        try:
            requested_devices = self._get_requested_devices(keyboard_in, mouse_in)
            lib.usb_hid.enable(requested_devices)
        except Exception as e:
            logger.error(f"Failed to enable devices. [{e}]")
            sys.exit(1)

    def _get_requested_devices(self, keyboard_in: str=None, mouse_in: str=None):
        requested_devices = []
        if keyboard_in is not None:
            requested_devices.append(OutputDevice.BOOT_KEYBOARD)
        if mouse_in is not None:
            requested_devices.append(OutputDevice.BOOT_MOUSE)
        return requested_devices

    def _init_devices(self, keyboard_in: str=None, mouse_in: str=None):
        try:
            logger.info(f'Available output devices: {self._device_repr(*lib.usb_hid.devices)}')
            if keyboard_in is not None:
                self._init_keyboard(keyboard_in)
            if mouse_in is not None:
                self._init_mouse(mouse_in)
        except Exception as e:
            logger.error(f"Failed to initialize devices. [{e}]")
            sys.exit(1)

    def _init_keyboard(self, keyboard_in: str):
        self._keyboard_in = InputDevice(keyboard_in)
        logger.info(f'Keyboard (in): {self._keyboard_in}')
        self._keyboard_out = Keyboard(lib.usb_hid.devices)
        logger.info(f'Keyboard (out): {self._device_repr(self._keyboard_out)}')

    def _init_mouse(self, mouse_in: str):
        self._mouse_in = InputDevice(mouse_in)
        logger.info(f'Mouse (in): {self._mouse_in}')
        self._mouse_out = Mouse(lib.usb_hid.devices)
        logger.info(f'Mouse (out): {self._device_repr(self._mouse_out)}')

    def _enable_sandbox(self):
        self._is_sandbox = True
        self._keyboard_out = None
        self._mouse_out = None
        logger.warning('Sandbox mode enabled! All output devices deactivated.')

    def _device_repr(self, *devices: Union[InputDevice, OutputDevice, Keyboard, Mouse]) -> str:
        device_strings = []
        for device in devices:
            if isinstance(device, InputDevice):
                device_strings.append(f'{device.name} ({device.path})')
            elif isinstance(device, OutputDevice):
                device_path = device.get_device_path(None)
                if device == OutputDevice.BOOT_KEYBOARD:
                    device_strings.append(f'Keyboard gadget ({device_path})')
                elif device == OutputDevice.BOOT_MOUSE:
                    device_strings.append(f'Mouse gadget ({device_path})')
            elif isinstance(device, Keyboard):
                device_strings.append(self._device_repr(device._keyboard_device))
            elif isinstance(device, Mouse):
                device_strings.append(self._device_repr(device._mouse_device))
        
        if len(device_strings) == 1:
            return device_strings[0]
        else:
            return f"[{', '.join(device_strings)}]"
    
    async def async_run_event_loop(self):
        async with asyncio.TaskGroup() as task_group:
            if self._keyboard_in is not None:
                keyboard_task = self._create_task(self._keyboard_in, self._keyboard_out, task_group)
                logger.debug(f"Created task: [{keyboard_task}]") 
            if self._mouse_in is not None:
                mouse_task = self._create_task(self._mouse_in, self._mouse_out, task_group)
                logger.debug(f"Created task: [{mouse_task}]")
        logger.critical(f"Event loop closed..")

    def _create_task(self, device_in: InputDevice, device_out: OutputDevice, task_group: TaskGroup) -> Task:
        return task_group.create_task(self.async_process_events(device_in, device_out))
    
    async def async_process_events(self, device_in: InputDevice, device_out: OutputDevice):
        logger.info(f"Started event loop for {self._device_repr(device_in)}")
        try:
            async for event in device_in.async_read_loop():
                if event is None: 
                    continue
                await self.async_handle_event(event, device_out) 
        except OSError as e:
            if e.errno == errno.OSError.NO_SUCH_DEVICE:
                await self.async_reconnect_device(device_in)
            else:
                raise
        except Exception as e:
            logger.error(f"Failed reading events from {self._device_repr(device_in)} [{e}]") 

    async def async_handle_event(self, event: InputEvent, device_out: OutputDevice):
        logger.debug(f"Received event: [{categorize(event)}] for {self._device_repr(device_out)}") 
        if self.is_key_up_or_down(event):
            await self.async_send_key(event, device_out)
        elif self.is_mouse_move(event):
            await self.async_send_mouse_move(event, device_out)   
    
    def is_key_up_or_down(self, event: InputEvent):
        return event.type == ecodes.EV_KEY and event.value in [key_event.DOWN, key_event.UP]   
    
    def is_mouse_move(self, event: InputEvent):
        return event.type == ecodes.EV_REL 

    async def async_send_key(self, event: InputEvent, device_out: OutputDevice):
        key = converter.to_hid_key(event.code) 
        if key is None or self._is_sandbox: 
            return
        try:
            if event.value == key_event.DOWN:
                device_out.press(key)
            elif event.value == key_event.UP:
                device_out.release(key)
        except Exception as e:
            logger.error(f"Error sending key event [{categorize(event)}] to {self._device_repr(device_out)} [{e}]")

    async def async_send_mouse_move(self, event: InputEvent, mouse_out: Mouse):
        x, y, mwheel = 0, 0, 0
        if event.code == ecodes.REL_X:
            x = event.value
        elif event.code == ecodes.REL_Y:
            y = event.value
        elif event.code == ecodes.REL_WHEEL:
            mwheel = event.value
        logger.debug(f"Sending mouse event: (x, y, mwheel) = {(x, y, mwheel)} to {self._device_repr(mouse_out)}")
        if self._is_sandbox: 
            return
        try:
            mouse_out.move(x, y, mwheel)
        except Exception as e:
            logger.error(f"Error sending mouse move event [{categorize(event)}] to {self._device_repr(mouse_out)} [{e}]")

    async def async_reconnect_device(self, device_in: InputDevice, wait_seconds: float=5) -> bool:
        start_time = datetime.now()
        last_log_time = start_time
        logger.critical(f"Lost connection to {self._device_repr(device_in)}. Trying to reconnect...")

        while True:
            if device_in.path in list_devices():
                logger.info(f"Successfully reconnected to {self._device_repr(device_in)}. Restarting daemon... ")
                if self._is_main:
                    __restart_daemon()
                else:
                    return True
            else:
                last_log_time = self._log_failed_reconnection_attempt(device_in, start_time, last_log_time)
                await asyncio.sleep(wait_seconds) 

    def _log_failed_reconnection_attempt(
            self, 
            device_in: InputDevice, 
            start_time: datetime, 
            last_log_time: datetime) -> datetime:
        
        current_time = datetime.now()
        elapsed_minutes = (current_time - start_time).total_seconds() / 60
        minutes_since_last_log = (current_time - last_log_time).total_seconds() / 60
        should_write_log = False

        if elapsed_minutes <= 10 and minutes_since_last_log >= 1:
            should_write_log = True 
        elif minutes_since_last_log >= 10:
            should_write_log = True
        if should_write_log:
            logger.info(f"Still trying to reconnect to {self._device_repr(device_in)}...")
            last_log_time = current_time

        return last_log_time

def __restart_daemon():
    """
    Restarts the current program, performing cleanup operations to minimize resource leaks.

    It tries to close all open file handlers, connections and threads, before executing this script again.
    """
    try:
        process_id = psutil.Process(os.getpid())

        __close_files_and_connections(process_id)

        __close_threads()

        __disable_usb_gadgets()

        __explicitly_run_gc()

        __rerun_this_script()
    except Exception as e:
        logger.error(f"Failed to restart daemon. [{e}]")
        sys.exit(1)

def __close_files_and_connections(p):
    for handler in p.open_files() + p.connections():
        try:
            os.close(handler.fd)
        except Exception as e_fd:
            logger.error(f"Failed to close file descriptor {handler.fd}. [{e_fd}]")
    
def __close_threads():
    """
    Attempts to close all running threads except the main thread.
    """
    main_thread = threading.main_thread()
    for thread in threading.enumerate():
        if thread is main_thread:
            continue
        try:
            thread.join(1)
        except Exception as e:
            logger.error(f"Failed to join thread {thread.name}. [{e}]")

def __disable_usb_gadgets():
    lib.usb_hid.disable()

def __explicitly_run_gc():
    """
    Explicitly run garbage collection to remove unreferenced objects
    """
    gc.collect()

def __rerun_this_script():
    python_executable = sys.executable
    os.execl(python_executable, python_executable, *sys.argv)

def __parse_args():
    parser = argparse.ArgumentParser(description='Bluetooth to HID proxy.')
    parser.add_argument('--keyboard', '-k', type=str, default=None, help='Input device path for keyboard')
    parser.add_argument('--mouse', '-m', type=str, default=None, help='Input device path for mouse')
    parser.add_argument('--sandbox', '-s', action='store_true', default=False, help='Only read input events but do not forward them to the output devices.')
    parser.add_argument('--debug', '-d', action='store_true', default=False, help='Increase log verbosity')
    parser.add_argument('--log_to_file', '-f', action='store_true', default=False, help='Add a handler that logs to file')
    parser.add_argument('--log_path', '-p', type=str, default='/var/log/bluetooth_2_usb/bluetooth_2_usb.log', help='The path of the log file')
    args = parser.parse_args()
    return args

def __signal_handler(sig, frame):
    logger.info(f'Exiting gracefully. Received signal: {sig}, frame: {frame}')
    sys.exit(0)

signal.signal(signal.SIGINT, __signal_handler)
signal.signal(signal.SIGTERM, __signal_handler)

async def __async_main():
    try:
        args = __parse_args()  
        if args.debug:
            logger.setLevel(logging.DEBUG)
        if args.log_to_file:
            lib.logger.add_file_handler(args.log_path)
        proxy = ComboDeviceHidProxy(args.keyboard, args.mouse, args.sandbox, is_main=True)
        await proxy.async_run_event_loop()
    except Exception as e:
        logger.error(f"Unhandled error while processing input events. Abort mission. [{e}]")   

if __name__ == "__main__":
    asyncio.run(__async_main())
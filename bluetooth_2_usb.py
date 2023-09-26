#!/usr/bin/env python
"""
Reads incoming mouse and keyboard events (e.g., Bluetooth) and forwards them to USB using Linux's gadget mode.
"""

try:
    import argparse
    from argparse import Namespace
    import asyncio
    from asyncio import TaskGroup, Task
    from datetime import datetime
    import logging
    import signal
    import sys
    from typing import List, NoReturn, Optional, Tuple

    from evdev import InputDevice, InputEvent, categorize, ecodes, list_devices

    from lib.constants import key_event
    import lib.evdev_converter as converter
    import lib.logger
    import lib.usb_hid
    from lib.usb_hid import GadgetDevice, MouseGadget, KeyboardGadget, DeviceLink
except ImportError as e:
    print(f"Error importing modules. [{e}]")
    raise

logger = lib.logger.get_logger()


class ComboDeviceHidProxy:
    def __init__(
        self,
        keyboard_path: Optional[str] = None,
        mouse_path: Optional[str] = None,
        is_sandbox: Optional[bool] = False,
    ) -> None:
        self._init_variables()
        self._init_devices(keyboard_path, mouse_path, is_sandbox)

    def _init_variables(self) -> None:
        self._registered_links: List[DeviceLink] = []
        self._is_sandbox = False
        self._gadgets_enabled = False
        self._task_group = None

    def _init_devices(
        self, keyboard_path: str, mouse_path: str, is_sandbox: bool
    ) -> None:
        try:
            self.enable_usb_gadgets()
            self._create_and_register_links(keyboard_path, mouse_path)
            self.enable_sandbox(is_sandbox)
            self._log_registered_links()
        except Exception as e:
            logger.error(f"Failed to initialize devices. [{e}]")
            raise

    def enable_usb_gadgets(self, gadgets_enabled: bool = True) -> None:
        try:
            self._check_enable_gadgets(gadgets_enabled)
            self._log_gadgets()
        except Exception as e:
            logger.error(f"Failed to enable/disable gadget devices. [{e}]")
            raise

    def _check_enable_gadgets(self, gadgets_enabled: bool) -> None:
        if self._gadgets_enabled == gadgets_enabled:
            return
        self._gadgets_enabled = gadgets_enabled

        if gadgets_enabled:
            lib.usb_hid.enable([GadgetDevice.BOOT_MOUSE, GadgetDevice.KEYBOARD])
        else:
            lib.usb_hid.disable()

    def _log_gadgets(self) -> None:
        if self._gadgets_enabled:
            logger.debug(f"Available output devices: {lib.usb_hid.devices}")
        else:
            logger.warning(f"All output devices disabled!")

    def _create_and_register_links(self, keyboard_path: str, mouse_path: str) -> None:
        mouse = self.create_mouse_link(mouse_path)
        keyboard = self.create_keyboard_link(keyboard_path)
        self.register_device_links(mouse, keyboard)

    def register_device_links(self, *device_links: DeviceLink) -> None:
        for link in device_links:
            self._register_single_link(link)

    def _register_single_link(self, link: DeviceLink) -> None:
        if link and link not in self._registered_links:
            self._registered_links.append(link)

    def create_mouse_link(self, mouse_path: str) -> DeviceLink:
        return self._create_device_link(mouse_path, MouseGadget())

    def create_keyboard_link(self, keyboard_path: str) -> DeviceLink:
        return self._create_device_link(keyboard_path, KeyboardGadget())

    def _create_device_link(
        self, device_in_path: str, device_out: GadgetDevice
    ) -> DeviceLink:
        if not device_in_path:
            return None
        device_in = InputDevice(device_in_path)
        device_link = DeviceLink(device_in, device_out)
        return device_link

    def enable_sandbox(self, sandbox_enabled: bool = True) -> None:
        self._check_enable_sandbox(sandbox_enabled)
        self._log_sandbox_status()

    def _check_enable_sandbox(self, sandbox_enabled: bool) -> None:
        if self._is_sandbox == sandbox_enabled:
            return
        self._is_sandbox = sandbox_enabled

        outputs_enabled = not sandbox_enabled
        self._enable_outputs(outputs_enabled)

    def _enable_outputs(self, outputs_enabled: bool) -> None:
        for link in self._registered_links:
            link.enable_output(outputs_enabled)

    def _log_sandbox_status(self) -> None:
        if self._is_sandbox:
            logger.warning("Sandbox mode enabled! All output devices deactivated.")
        else:
            logger.debug("Sandbox mode disabled. All output devices activated.")

    def _log_registered_links(self) -> None:
        for link in self._registered_links:
            logger.debug(repr(link))

    async def async_connect_registered_links(self) -> NoReturn:
        while True:
            await self._async_create_task_group()
            logger.critical(f"Event loop closed. Trying to restart.")
            await asyncio.sleep(5)

    async def _async_create_task_group(self) -> None:
        try:
            async with TaskGroup() as self._task_group:
                self._connect_device_links(*self._registered_links)
        except* Exception as e:
            logger.error(f"Error(s) in TaskGroup: [{e.exceptions}]")

    def _connect_device_links(self, *device_links: DeviceLink) -> None:
        for link in device_links:
            self._connect_single_link(link)

    def _connect_single_link(self, device_link: DeviceLink) -> None:
        self._task_group.create_task(
            self._async_connect_device_link(device_link), name=device_link.name()
        )
        logger.debug(
            f"Link {device_link} connected. Current tasks: {asyncio.all_tasks()}"
        )

    async def _async_connect_device_link(self, device_link: DeviceLink) -> None:
        logger.info(f"Started event loop for {repr(device_link)}")

        try:
            device_in = device_link.input()
            await self._async_relay_device_events(device_link)
        except OSError as e:
            logger.critical(f"{device_in.name} disconnected. Reconnecting... [{e}]")
            reconnected = await self._async_wait_for_device(device_in)
            self._log_reconnection_outcome(device_in, reconnected)
        except Exception as e:
            logger.error(f"{device_in.name} failed! Restarting task... [{e}]")
            await asyncio.sleep(15)
        finally:
            self._disconnect_device_link(device_link, reconnect=True)

    async def _async_relay_device_events(self, device_link: DeviceLink):
        device_in = device_link.input()
        device_out = device_link.output()

        async for event in device_in.async_read_loop():
            if not event:
                continue
            await self._async_relay_single_event(event, device_out)

    async def _async_relay_single_event(
        self, event: InputEvent, device_out: GadgetDevice
    ) -> None:
        logger.debug(f"Received event: [{categorize(event)}] for {device_out}")

        if self._is_key_up_or_down(event):
            await self._async_send_key(event, device_out)
        elif self._is_mouse_movement(event):
            await self._async_move_mouse(event, device_out)

    def _is_key_up_or_down(self, event: InputEvent) -> bool:
        return event.type == ecodes.EV_KEY and event.value in [
            key_event.DOWN,
            key_event.UP,
        ]

    def _is_mouse_movement(self, event: InputEvent) -> bool:
        return event.type == ecodes.EV_REL

    async def _async_send_key(
        self, event: InputEvent, device_out: GadgetDevice
    ) -> None:
        key = converter.to_hid_key(event.code)
        if key is None:
            return

        try:
            if event.value == key_event.DOWN:
                device_out.press(key)
            elif event.value == key_event.UP:
                device_out.release(key)
        except Exception as e:
            logger.error(f"Error sending [{categorize(event)}] to {device_out} [{e}]")

    async def _async_move_mouse(
        self, event: InputEvent, mouse_out: MouseGadget
    ) -> None:
        x, y, mwheel = self._get_mouse_movement(event)

        logger.debug(f"Moving mouse {mouse_out}: (x, y, mwheel) = {(x, y, mwheel)}")

        try:
            mouse_out.move(x, y, mwheel)
        except Exception as e:
            logger.error(f"Error sending [{categorize(event)}] to {mouse_out} [{e}]")

    def _get_mouse_movement(self, event: InputEvent) -> Tuple[int, int, int]:
        x, y, mwheel = 0, 0, 0

        if event.code == ecodes.REL_X:
            x = event.value
        elif event.code == ecodes.REL_Y:
            y = event.value
        elif event.code == ecodes.REL_WHEEL:
            mwheel = event.value

        return x, y, mwheel

    async def _async_wait_for_device(
        self, device_in: InputDevice, delay_seconds: float = 1
    ) -> bool:
        await asyncio.sleep(delay_seconds)

        last_log_time = datetime.now()

        while device_in.path not in list_devices():
            last_log_time = self._log_reconnection_attempt(device_in, last_log_time)
            await asyncio.sleep(delay_seconds)

        return True

    def _log_reconnection_attempt(
        self, device_in: InputDevice, last_log_time: datetime
    ) -> datetime:
        current_time = datetime.now()
        secs_since_last_log = (current_time - last_log_time).total_seconds()

        if secs_since_last_log >= 60:
            logger.debug(f"Still trying to reconnect to {device_in.name}...")
            last_log_time = current_time

        return last_log_time

    def _log_reconnection_outcome(self, device_in: InputDevice, reconnected: bool):
        if reconnected:
            logger.info(f"Successfully reconnected to {device_in.name}.")
        else:
            logger.critical(f"Reconnecting to {device_in.name} failed.")

    def _disconnect_device_link(
        self, device_link: DeviceLink, reconnect: bool = False
    ) -> None:
        task = self._get_task(device_link.name())
        self._cancel_task(task)

        if reconnect:
            device_link.reset_input()
            self._connect_single_link(device_link)

    def _get_task(self, task_name: str) -> Task:
        for task in asyncio.all_tasks():
            if task.get_name() == task_name:
                return task
        return None

    def _cancel_task(self, task: Task) -> None:
        if self._is_running(task):
            task.cancel()

    def _is_running(self, task: Task) -> bool:
        return (
            task and not task.cancelled() and not task.cancelling() and not task.done()
        )


def __parse_args() -> Namespace:
    parser = argparse.ArgumentParser(description="Bluetooth to HID proxy.")

    parser.add_argument(
        "--keyboard",
        "-k",
        type=str,
        default=None,
        help="Input device path for keyboard",
    )
    parser.add_argument(
        "--mouse", "-m", type=str, default=None, help="Input device path for mouse"
    )
    parser.add_argument(
        "--sandbox",
        "-s",
        action="store_true",
        default=False,
        help="Only read input events but do not forward them to the output devices.",
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        default=False,
        help="Increase log verbosity",
    )
    parser.add_argument(
        "--log_to_file",
        "-f",
        action="store_true",
        default=False,
        help="Add a handler that logs to file",
    )
    parser.add_argument(
        "--log_path",
        "-p",
        type=str,
        default="/var/log/bluetooth_2_usb/bluetooth_2_usb.log",
        help="The path of the log file",
    )

    args = parser.parse_args()
    return args


def __signal_handler(sig, frame) -> NoReturn:
    logger.info(f"Exiting gracefully. Received signal: {sig}, frame: {frame}")
    sys.exit(0)


signal.signal(signal.SIGINT, __signal_handler)
signal.signal(signal.SIGTERM, __signal_handler)


async def __main(args: Namespace) -> NoReturn:
    """
    Run the main event loop to read events from the input device and forward them to the corresponding USB device.

    Parameters:
        args (Namespace): Command-line arguments.
    """
    proxy = ComboDeviceHidProxy(args.keyboard, args.mouse, args.sandbox)
    await proxy.async_connect_registered_links()


if __name__ == "__main__":
    """
    Entry point for the script. Sets up logging, parses command-line arguments, and starts the event loop.
    """
    try:
        args = __parse_args()
        if args.debug:
            logger.setLevel(logging.DEBUG)
        if args.log_to_file:
            lib.logger.add_file_handler(args.log_path)
        logger.debug(f"CLI args: {args}")
        asyncio.run(__main(args))
    except Exception as e:
        logger.error(f"Houston, we have an unhandled problem. Abort mission. [{e}]")
        raise

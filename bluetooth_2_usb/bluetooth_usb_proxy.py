#!venv/bin/python3.11

import asyncio
from datetime import datetime

from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.mouse import Mouse
import usb_hid
from evdev import InputDevice, InputEvent, KeyEvent, RelEvent, categorize, list_devices

from bluetooth_2_usb.evdev_adapter import (
    get_mouse_movement,
    is_consumer_key,
    is_mouse_button,
    evdev_to_hid,
)
from bluetooth_2_usb.logging import get_logger


_logger = get_logger()


class BluetoothUsbProxy:
    def __init__(self, input_device_path: str):
        self._input_device = None
        self._input_name = None
        self._input_path = input_device_path
        self._disconnect_input_device()
        self._keyboard_gadget = Keyboard(usb_hid.devices)
        self._mouse_gadget = Mouse(usb_hid.devices)
        self._consumer_gadget = ConsumerControl(usb_hid.devices)

    @property
    def input_device(self) -> InputDevice | None:
        return self._input_device

    @property
    def input_name(self) -> str:
        return self._input_name if self._input_name else self._input_path

    @property
    def input_path(self) -> str:
        return self._input_path

    def __str__(self):
        return self.input_name

    def __repr__(self):
        return str(self.input_device)

    def _disconnect_input_device(self):
        self._input_device = None
        self._input_name = None

    def is_ready(self) -> bool:
        return self.input_path in list_devices()

    async def async_wait_connect(self, delay_seconds: float = 1) -> None:
        self._disconnect_input_device()
        await self._async_wait_for_device(delay_seconds)
        await self._async_init_device(delay_seconds)
        _logger.info(f"Successfully connected to {repr(self)}.")

    async def _async_wait_for_device(self, delay_seconds: float = 1) -> None:
        last_log_time = datetime.now()
        while not self.is_ready():
            if _elapsed_seconds_since(last_log_time) >= 10:
                _logger.debug(f"Waiting for input device {self}...")
                last_log_time = datetime.now()
            await asyncio.sleep(delay_seconds)

    async def _async_init_device(self, delay_seconds: float = 1) -> None:
        while True:
            try:
                self._input_device = InputDevice(self.input_path)
                self._input_name = self.input_device.name
                break
            except Exception:
                _logger.exception(f"Error initializing input device {self}")
                await asyncio.sleep(delay_seconds)

    async def async_relay_events_loop(self):
        async for event in self.input_device.async_read_loop():
            await self._async_relay_single_event(event)

    async def _async_relay_single_event(self, event: InputEvent) -> None:
        categorized_event = categorize(event)
        _logger.debug(f"Received event: [{categorized_event}]")
        if isinstance(categorized_event, KeyEvent):
            await self._async_send_key(categorized_event)
        elif isinstance(categorized_event, RelEvent):
            await self._async_move_mouse(categorized_event)

    async def _async_send_key(self, event: KeyEvent) -> None:
        key_id, key_name = evdev_to_hid(event)
        if key_id is None:
            return
        device_out = self._get_output_device(event)
        try:
            if event.keystate == KeyEvent.key_down:
                _logger.debug(f"Pressing {key_name} (0x{key_id:02X}) on {device_out}")
                device_out.press(key_id)
            elif event.keystate == KeyEvent.key_up:
                _logger.debug(f"Releasing {key_name} (0x{key_id:02X}) on {device_out}")
                device_out.release(key_id)

        except Exception:
            _logger.exception(f"Failed sending 0x{key_id:02X} to {device_out}")

    def _get_output_device(self, event: KeyEvent) -> ConsumerControl | Keyboard | Mouse:
        if is_consumer_key(event):
            return self._consumer_gadget
        elif is_mouse_button(event):
            return self._mouse_gadget
        return self._keyboard_gadget

    async def _async_move_mouse(self, event: RelEvent) -> None:
        x, y, mwheel = get_mouse_movement(event)
        coordinates = f"(x={x}, y={y}, mwheel={mwheel})"
        _logger.debug(f"Moving mouse {self._mouse_gadget} {coordinates}")
        try:
            self._mouse_gadget.move(x, y, mwheel)
        except Exception:
            _logger.exception(f"Failed moving mouse {self._mouse_gadget} {coordinates}")


def _elapsed_seconds_since(reference_time: datetime) -> float:
    current_time = datetime.now()
    return (current_time - reference_time).total_seconds()

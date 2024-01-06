import asyncio
from asyncio import CancelledError, TaskGroup
import re
from typing import AsyncGenerator, NoReturn, Optional

from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.mouse import Mouse
from evdev import InputDevice, InputEvent, KeyEvent, RelEvent, categorize, list_devices
import usb_hid
from usb_hid import Device

from .evdev import (
    evdev_to_usb_hid,
    get_mouse_movement,
    is_consumer_key,
    is_mouse_button,
)
from .logging import get_logger


_logger = get_logger()
_keyboard_gadget: Optional[Keyboard] = None
_mouse_gadget: Optional[Mouse] = None
_consumer_gadget: Optional[ConsumerControl] = None

PATH = "path"
MAC = "MAC"
NAME = "name"
PATH_REGEX = r"^\/dev\/input\/event.*$"
MAC_REGEX = r"^([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})$"


async def async_list_input_devices() -> list[InputDevice]:
    devices = []
    try:
        devices = [InputDevice(path) for path in list_devices()]
    except Exception:
        _logger.exception("Failed listing devices")
        await asyncio.sleep(1)
    return devices


def init_usb_gadgets() -> None:
    _logger.debug("Initializing USB gadgets...")
    usb_hid.enable(
        [
            Device.MOUSE,
            Device.KEYBOARD,
            Device.CONSUMER_CONTROL,
        ]  # type: ignore
    )
    global _keyboard_gadget, _mouse_gadget, _consumer_gadget
    enabled_devices: list[Device] = list(usb_hid.devices)  # type: ignore
    _keyboard_gadget = Keyboard(enabled_devices)
    _mouse_gadget = Mouse(enabled_devices)
    _consumer_gadget = ConsumerControl(enabled_devices)
    _logger.debug(f"Enabled USB gadgets: {enabled_devices}")


def all_gadgets_ready() -> bool:
    return all(
        dev is not None for dev in (_keyboard_gadget, _mouse_gadget, _consumer_gadget)
    )


class DeviceIdentifier:
    def __init__(self, device_identifier: str) -> None:
        self._value = device_identifier
        self._type = self._determine_identifier_type()
        self._normalized_value = self._normalize_identifier()

    @property
    def value(self) -> str:
        return self._value

    @property
    def normalized_value(self) -> str:
        return self._normalized_value

    @property
    def type(self) -> str:
        return self._type

    def __str__(self) -> str:
        return f'{self.type} "{self.value}"'

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"

    def _determine_identifier_type(self) -> str:
        if re.match(PATH_REGEX, self.value):
            return PATH
        if re.match(MAC_REGEX, self.value):
            return MAC
        return NAME

    def _normalize_identifier(self) -> str:
        if self.type == PATH:
            return self.value
        if self.type == MAC:
            return self.value.lower().replace("-", ":")
        return self.value.lower()

    def matches(self, device: InputDevice) -> bool:
        if self.type == PATH:
            return self.value == device.path
        if self.type == MAC:
            return self.normalized_value == device.uniq
        return self.normalized_value in device.name.lower()


class DeviceRelay:
    def __init__(self, input_device: InputDevice, grab_device: bool = False) -> None:
        self._input_device = input_device
        self._grab_device = grab_device
        if grab_device:
            self._input_device.grab()
        if not all_gadgets_ready():
            init_usb_gadgets()

    @property
    def input_device(self) -> InputDevice:
        return self._input_device

    def __str__(self) -> str:
        return f"relay for {self.input_device}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.input_device!r}, {self._grab_device})"

    async def async_relay_events_loop(self) -> NoReturn:
        async for event in self.input_device.async_read_loop():
            await self._async_relay_event(event)

    async def _async_relay_event(self, input_event: InputEvent) -> None:
        event = categorize(input_event)
        _logger.debug(f"Received {event} from {self.input_device.name}")
        func = None
        if isinstance(event, RelEvent):
            func = _move_mouse
        elif isinstance(event, KeyEvent):
            func = _send_key
        if func:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, func, event)


def _move_mouse(event: RelEvent) -> None:
    if _mouse_gadget is None:
        raise RuntimeError("Mouse gadget not initialized")
    x, y, mwheel = get_mouse_movement(event)
    coordinates = f"(x={x}, y={y}, mwheel={mwheel})"
    try:
        _logger.debug(f"Moving {_mouse_gadget} {coordinates}")
        _mouse_gadget.move(x, y, mwheel)
    except Exception:
        _logger.exception(f"Failed moving {_mouse_gadget} {coordinates}")


def _send_key(event: KeyEvent) -> None:
    key_id, key_name = evdev_to_usb_hid(event)
    if key_id is None or key_name is None:
        return
    device_out = _get_output_device(event)
    if device_out is None:
        raise RuntimeError("USB gadget not initialized")
    try:
        if event.keystate == KeyEvent.key_down:
            _logger.debug(f"Pressing {key_name} (0x{key_id:02X}) on {device_out}")
            device_out.press(key_id)
        elif event.keystate == KeyEvent.key_up:
            _logger.debug(f"Releasing {key_name} (0x{key_id:02X}) on {device_out}")
            device_out.release(key_id)
    except Exception:
        _logger.exception(f"Failed sending 0x{key_id:02X} to {device_out}")


def _get_output_device(event: KeyEvent) -> ConsumerControl | Keyboard | Mouse | None:
    if is_consumer_key(event):
        return _consumer_gadget
    elif is_mouse_button(event):
        return _mouse_gadget
    return _keyboard_gadget


class RelayController:
    """
    This class serves as a HID relay to handle Bluetooth keyboard and mouse events from multiple input devices and translate them to USB.
    """

    def __init__(
        self,
        device_identifiers: Optional[list[str]] = None,
        auto_discover: bool = False,
        grab_devices: bool = False,
    ) -> None:
        if not device_identifiers:
            device_identifiers = []
        self._device_ids = [DeviceIdentifier(id) for id in device_identifiers]
        self._auto_discover = auto_discover
        self._grab_devices = grab_devices
        self._cancelled = False

    async def async_relay_devices(self) -> NoReturn:
        try:
            async with TaskGroup() as task_group:
                await self._async_discover_devices(task_group)
            _logger.critical("Event loop closed.")
        except* Exception:
            _logger.exception("Error(s) in TaskGroup")

    async def _async_discover_devices(self, task_group: TaskGroup) -> NoReturn:
        async for device in self._async_discover_devices_loop():
            if not self._cancelled:
                self._create_task(device, task_group)

    async def _async_discover_devices_loop(self) -> AsyncGenerator[InputDevice, None]:
        _logger.info("Discovering input devices...")
        if self._auto_discover:
            _logger.debug("Auto-discovery enabled. Relaying all input devices.")
        else:
            all_device_ids = " or ".join(str(id) for id in self._device_ids)
            _logger.debug(f"Relaying devices with matching {all_device_ids}")
        while True:
            for device in await async_list_input_devices():
                if self._should_relay(device):
                    yield device
            await asyncio.sleep(0.1)

    def _should_relay(self, device: InputDevice) -> bool:
        return not self._has_task(device) and self._matches_criteria(device)

    def _has_task(self, device: InputDevice) -> bool:
        return device.path in [task.get_name() for task in asyncio.all_tasks()]

    def _matches_criteria(self, device: InputDevice) -> bool:
        return self._auto_discover or self._matches_any_identifier(device)

    def _matches_any_identifier(self, device: InputDevice) -> bool:
        return any(id.matches(device) for id in self._device_ids)

    def _create_task(self, device: InputDevice, task_group: TaskGroup) -> None:
        task_group.create_task(self._async_relay_events(device), name=device.path)

    async def _async_relay_events(self, device: InputDevice) -> NoReturn:
        try:
            relay = DeviceRelay(device, self._grab_devices)
            _logger.info(f"Activated {relay}")
            await relay.async_relay_events_loop()
        except CancelledError:
            self._cancelled = True
            _logger.critical(f"{device.name} was cancelled")
        except (OSError, FileNotFoundError) as ex:
            _logger.critical(f"Connection to {device.name} lost [{ex!r}]")
        except Exception:
            _logger.exception(f"{device.name} failed!")
            await asyncio.sleep(1)

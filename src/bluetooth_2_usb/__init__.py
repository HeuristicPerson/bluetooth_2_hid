# --------------------------------------------------------------------------
# Gather everything into a single, convenient namespace.
# --------------------------------------------------------------------------

from evdev import (
    InputDevice,
    list_devices,
)
import usb_hid
from usb_hid import Device

from .evdev import (
    ecodes,
    evdev_to_usb_hid,
    find_key_name,
    find_usage_name,
    get_mouse_movement,
    is_consumer_key,
    is_mouse_button,
)
from .logging import add_file_handler, get_logger
from .relay import (
    DeviceIdentifier,
    DeviceRelay,
    RelayController,
)

_logger = get_logger()


def enable_usb_devices():
    usb_hid.enable(
        [
            Device.MOUSE,
            Device.KEYBOARD,
            Device.CONSUMER_CONTROL,
        ]
    )
    _logger.debug(f"Available USB devices: {usb_hid.devices}")


def list_readable_devices() -> list[InputDevice]:
    return [InputDevice(path) for path in list_devices()]

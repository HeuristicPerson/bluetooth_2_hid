import asyncio
from evdev import InputDevice
from usb_hid import Device as OutputDevice

import lib.logger

logger = lib.logger.get_logger()


class DeviceLink:
    def __init__(self, device_in: InputDevice, device_out: OutputDevice):
        self._device_in = None
        self._device_in_name = None
        self._device_in_path = None
        if isinstance(device_in, InputDevice):
            self._device_in = device_in
            self._device_in_name = device_in.name
            self._device_in_path = device_in.path
        self._device_out = device_out
        self._device_out_enabled = False
        self._device_out_dummy = _DummyDevice(device_out)
        if device_out:
            self._device_out_enabled = True

    def __repr__(self):
        return f"{self._device_in_name}: [{self._device_in}] >> [{repr(self.output())}]"

    def __str__(self):
        return f"[{self._device_in_name}]>>[{self.output()}]"

    def input(self) -> InputDevice:
        return self._device_in

    async def async_reset_input(self) -> None:
        self._device_in = None
        while True:
            try:
                self._device_in = InputDevice(self._device_in_path)
                break
            except Exception as e:
                logger.error(f"Error resetting input {self._device_in_path} [{e}]")
                await asyncio.sleep(5)

    def output(self) -> OutputDevice:
        if self._device_out_enabled:
            return self._device_out
        return self._device_out_dummy

    def enable_output(self, enabled: bool = True):
        self._device_out_enabled = enabled


class _DummyDevice:
    def __init__(self, actual_gadget):
        self._actual_gadget = actual_gadget

    def __repr__(self):
        return f"Dummy {repr(self._actual_gadget)}"

    def __str__(self):
        return f"{self._actual_gadget} (Dummy)"

    def press(self, *keycodes: int) -> None:
        pass

    def release(self, *keycodes: int) -> None:
        pass

    def release_all(self) -> None:
        pass

    def send(self, *keycodes: int) -> None:
        pass

    @property
    def led_status(self) -> bytes:
        return b"\x00"

    def led_on(self, led_code: int) -> bool:
        return False

    def click(self, buttons: int) -> None:
        pass

    def move(self, x: int = 0, y: int = 0, wheel: int = 0) -> None:
        pass

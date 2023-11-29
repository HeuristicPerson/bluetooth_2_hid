import asyncio
from asyncio import CancelledError, TaskGroup, Task
from typing import NoReturn

import usb_hid
from usb_hid import Device

from bluetooth_2_usb.input_device_relay import InputDeviceRelay
from bluetooth_2_usb.logging import get_logger


_logger = get_logger()


class RelayController:
    """
    This class serves as a HID relay to handle Bluetooth keyboard and mouse events from multiple input devices and translate them to USB.
    """

    def __init__(self, device_paths: list[str] = None) -> None:
        usb_hid.enable(
            [
                Device.MOUSE,
                Device.KEYBOARD,
                Device.CONSUMER_CONTROL,
            ]
        )
        _logger.debug(f"Available output devices: {usb_hid.devices}")
        self._device_relays = [InputDeviceRelay(path) for path in device_paths]
        self._task_group: TaskGroup

    async def async_relay_all_devices(self) -> NoReturn:
        try:
            async with TaskGroup() as self._task_group:
                for relay in self._device_relays:
                    await self._async_create_task(relay)
                _logger.debug(f"Current tasks: {asyncio.all_tasks()}")
            _logger.critical("Event loop closed.")
        except* Exception as ex:
            _logger.error(f"Error(s) in TaskGroup: [{ex.exceptions}]")

    async def _async_create_task(self, relay: InputDeviceRelay) -> None:
        self._task_group.create_task(
            self._async_relay_events(relay), name=relay.input_path
        )

    async def _async_relay_events(self, relay: InputDeviceRelay) -> None:
        _logger.info(f"Relaying device {relay}")
        restart_on_error = True
        try:
            await relay.async_wait_connect()
            await relay.async_relay_events_loop()
        except (OSError, FileNotFoundError) as ex:
            _logger.critical(f"Reconnecting to {relay}... [{repr(ex)}]")
            await relay.async_wait_connect()
        except CancelledError:
            _logger.critical(f"{relay} received a cancellation request.")
            restart_on_error = False
        except Exception:
            _logger.exception(f"{relay} failed! Restarting task...")
            await asyncio.sleep(5)
        finally:
            await self._async_cancel_task(relay, restart_on_error)

    async def _async_cancel_task(
        self, relay: InputDeviceRelay, restart: bool = False
    ) -> None:
        task = _get_task(relay.input_path)
        if task:
            task.cancel()
        if restart:
            await self._async_create_task(relay)


def _get_task(task_name: str) -> Task | None:
    for task in asyncio.all_tasks():
        if task.get_name() == task_name:
            return task
    return None

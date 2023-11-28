import asyncio
from asyncio import TaskGroup, Task
from typing import NoReturn

import usb_hid
from usb_hid import Device

from bluetooth_2_usb.bluetooth_usb_proxy import BluetoothUsbProxy
from bluetooth_2_usb.logging import get_logger


_logger = get_logger()


class ProxyLoop:
    """
    This class serves as a HID proxy to handle both keyboard and mouse events and relay them to USB.
    """

    def __init__(self, device_paths: list[str] = None) -> None:
        # We have to use BOOT_MOUSE since somehow MOUSE freezes on any input.
        # This should be fine though. Also it's important to enable mouse first.
        usb_hid.enable([Device.BOOT_MOUSE, Device.KEYBOARD, Device.CONSUMER_CONTROL])
        _logger.debug(f"Available output devices: {usb_hid.devices}")
        self._bluetooth_proxies = [BluetoothUsbProxy(path) for path in device_paths]
        _logger.debug(f"Registered input devices: {self._bluetooth_proxies}")
        self._task_group: TaskGroup

    async def async_relay_bluetooth_to_usb(self) -> NoReturn:
        try:
            async with TaskGroup() as self._task_group:
                for proxy in self._bluetooth_proxies:
                    await self._async_create_task(proxy)
                _logger.debug(f"Current tasks: {asyncio.all_tasks()}")
            _logger.critical("Event loop closed.")
        except* Exception as ex:
            _logger.error(f"Error(s) in TaskGroup: [{ex.exceptions}]")

    async def _async_create_task(self, proxy: BluetoothUsbProxy) -> None:
        self._task_group.create_task(
            self._async_relay_events(proxy), name=proxy.input_path
        )
        _logger.debug(f"Connected proxy: {proxy}")

    async def _async_relay_events(self, proxy: BluetoothUsbProxy) -> None:
        _logger.info(f"Starting event loop for {repr(proxy)}")
        restart_on_error = True
        try:
            await proxy.async_wait_connect()
            await proxy.async_relay_events_loop()
        except (OSError, FileNotFoundError) as ex:
            _logger.critical(f"Reconnecting to {proxy}... [{repr(ex)}]")
            await proxy.async_wait_connect()
        except asyncio.exceptions.CancelledError:
            _logger.critical(f"{proxy} received a cancellation request.")
            restart_on_error = False
        except Exception:
            _logger.exception(f"{proxy} failed! Restarting task...")
            await asyncio.sleep(5)
        finally:
            await self._async_cancel_task(proxy, restart_on_error)

    async def _async_cancel_task(
        self, proxy: BluetoothUsbProxy, reconnect: bool = False
    ) -> None:
        task = _get_task(proxy.input_path)
        if task:
            task.cancel()
        if reconnect:
            await self._async_create_task(proxy)


def _get_task(task_name: str) -> Task | None:
    for task in asyncio.all_tasks():
        if task.get_name() == task_name:
            return task
    return None

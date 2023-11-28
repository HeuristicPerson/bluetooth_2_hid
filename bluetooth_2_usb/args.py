from argparse import Namespace
import argparse

from usb_hid import unregister_disable


class CustomArgumentParser(argparse.ArgumentParser):
    def print_help(self) -> None:
        unregister_disable()
        super().print_help()


def parse_args() -> Namespace:
    parser = CustomArgumentParser(
        description="Bluetooth to USB HID proxy. Reads incoming Bluetooth mouse and keyboard events and forwards them to USB using Linux's gadget mode.",
    )

    parser.add_argument(
        "--input_devices",
        "-i",
        type=lambda input: [item.strip() for item in input.split(",")],
        default=None,
        help="Comma-separated list of input device paths to be registered and connected.\n \
          Default is None.\n \
          Example: --input_devices /dev/input/event2,/dev/input/event3",
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        default=False,
        help="Enable debug mode. Increases log verbosity",
    )
    parser.add_argument(
        "--log_to_file",
        "-f",
        action="store_true",
        default=False,
        help="Add a handler that logs to file additionally to stdout. ",
    )
    parser.add_argument(
        "--log_path",
        "-p",
        type=str,
        default="/var/log/bluetooth_2_usb/bluetooth_2_usb.log",
        help="The path of the log file. Default is /var/log/bluetooth_2_usb/bluetooth_2_usb.log.",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="store_true",
        default=False,
        help="Display the version number of this software and exit.",
    )
    parser.add_argument(
        "--list_devices",
        "-l",
        action="store_true",
        default=False,
        help="List all available input devices and exit.",
    )

    args = parser.parse_args()
    return args

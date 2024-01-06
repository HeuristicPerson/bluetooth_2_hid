<!-- omit in toc -->
# Bluetooth to USB

![Bluetooth to USB Overview](https://raw.githubusercontent.com/quaxalber/bluetooth_2_usb/main/assets/overview.png)

Convert a Raspberry Pi into a HID relay that translates Bluetooth keyboard and mouse input to USB. Minimal configuration. Zero hassle.

The issue with Bluetooth devices is that you usually can't use them to:
- wake up sleeping devices,
- access the BIOS or OS select menu (e.g., GRUB),
- access devices without Bluetooth interface (e.g., devices in a restricted environment or most KVM switches).

Sounds familiar? Congratulations! **You just found the solution!**

Linux's gadget mode allows a Raspberry Pi to act as USB HID (Human Interface Device). Therefore, from the host's perspective, it appears like a regular USB keyboard or mouse. You may think of your Pi as a multi-device Bluetooth dongle.

<!-- omit in toc -->
## Table of Contents

- [1. Features](#1-features)
- [2. Requirements](#2-requirements)
- [3. Installation](#3-installation)
  - [3.1. Prerequisites](#31-prerequisites)
  - [3.2. Setup](#32-setup)
- [4. Usage](#4-usage)
  - [4.1. Connection to target device / host](#41-connection-to-target-device--host)
    - [4.1.1. Raspberry Pi 4 Model B](#411-raspberry-pi-4-model-b)
    - [4.1.2. Raspberry Pi Zero (2) W(H)](#412-raspberry-pi-zero-2-wh)
  - [4.2. Command-line arguments](#42-command-line-arguments)
  - [4.3. Consuming the API from your Python code](#43-consuming-the-api-from-your-python-code)
- [5. Updating](#5-updating)
- [6. Uninstallation](#6-uninstallation)
- [7. Troubleshooting](#7-troubleshooting)
  - [7.1. The Pi keeps rebooting or crashes randomly](#71-the-pi-keeps-rebooting-or-crashes-randomly)
  - [7.2. The installation was successful, but I don't see any output on the target device](#72-the-installation-was-successful-but-i-dont-see-any-output-on-the-target-device)
  - [7.3. In bluetoothctl, my device is constantly switching on/off](#73-in-bluetoothctl-my-device-is-constantly-switching-onoff)
  - [7.4. I have a different issue](#74-i-have-a-different-issue)
  - [7.5. Everything is working, but can it help me with Bitcoin mining?](#75-everything-is-working-but-can-it-help-me-with-bitcoin-mining)
- [8. Bonus points](#8-bonus-points)
- [9. Contributing](#9-contributing)
- [10. License](#10-license)
- [11. Acknowledgments](#11-acknowledgments)

## 1. Features

- Simple installation and highly automated setup
- Supports multiple input devices (currently keyboard and mouse - more than one of each kind simultaneously)
- Supports [146 multimedia keys](https://github.com/quaxalber/bluetooth_2_usb/blob/8b1c5f8097bbdedfe4cef46e07686a1059ea2979/lib/evdev_adapter.py#L142) (e.g., mute, volume up/down, launch browser, etc.)
- Auto-discovery feature for input devices
- Auto-reconnect feature for input devices (power off, energy saving mode, out of range, etc.)
- Robust error handling and logging
- Installation as a systemd service
- Reliable concurrency using state-of-the-art [TaskGroups](https://docs.python.org/3/library/asyncio-task.html#task-groups)
- Clean and actively maintained code base

## 2. Requirements

- A Raspberry Pi with Bluetooth and [USB OTG support](https://en.wikipedia.org/wiki/USB_On-The-Go) required for [USB gadgets](https://www.kernel.org/doc/html/latest/driver-api/usb/gadget.html) in so-called device mode. Supported models include:
  - **Raspberry Pi Zero W(H)**: Includes Bluetooth 4.1 and supports USB OTG with the lowest price tag.
  - **Raspberry Pi Zero 2 W**: Similar to the Raspberry Pi Zero W, it has Bluetooth 4.1 and USB OTG support while providing additional processing power.
  - **Raspberry Pi 4 Model B**: Offers Bluetooth 5.0 and USB-C OTG support for device mode, providing the best performance (that is until the Pi 5 is available).
- Raspberry Pi OS ([Bookworm-based](https://www.raspberrypi.com/news/bookworm-the-new-version-of-raspberry-pi-os/))
- Python 3.11 for using [TaskGroups](https://docs.python.org/3/library/asyncio-task.html#task-groups).

> [!NOTE]
> Raspberry Pi 3 Models feature Bluetooth 4.2 but no native USB gadget mode support. Earlier models like Raspberry Pi 1 and 2 do not support Bluetooth natively and have no USB gadget mode support.

> [!NOTE]
> The latest version of Raspberry Pi OS, based on Debian Bookworm, supports Python 3.11 through the official package repositories. For older versions, you may [build it from source](https://github.com/quaxalber/bluetooth_2_usb/blob/main/scripts/build_python_3.11.sh). Note that building may take anything between a few minutes (Pi 4B) and more than an hour (Pi 0W).

## 3. Installation

Follow these steps to install and configure the project:

### 3.1. Prerequisites

1. Install Raspberry Pi OS on your Raspberry Pi (e.g., using [Pi Imager](https://youtu.be/ntaXWS8Lk34))
  
2. Connect to a network via Ethernet cable or [Wi-Fi](https://www.raspberrypi.com/documentation/computers/configuration.html#configuring-networking). Make sure this network has Internet access.
  
3. (*optional, recommended*) Enable [SSH](https://www.raspberrypi.com/documentation/computers/remote-access.html#ssh), if you intend to access the Pi remotely.

> [!NOTE]
> These settings above may be configured [during imaging](https://www.raspberrypi.com/documentation/computers/getting-started.html#advanced-options) (recommended), [on first boot](https://www.raspberrypi.com/documentation/computers/getting-started.html#configuration-on-first-boot) or [afterwards](https://www.raspberrypi.com/documentation/computers/configuration.html).
  
4. Connect to the Pi and make sure `git` is installed:
  
   ```console
   sudo apt update && sudo apt upgrade -y && sudo apt install -y git
   ```

5. Pair and trust any Bluetooth devices you wish to relay, either via GUI or via CLI:
  
   ```console
   bluetoothctl
   scan on
   ```

   ... wait for your devices to show up and note their MAC addresses (you may also type the first characters and hit `TAB` for auto-completion in the following commands) ...

   ```console
   trust A1:B2:C3:D4:E5:F6
   pair A1:B2:C3:D4:E5:F6
   connect A1:B2:C3:D4:E5:F6
   ```

> [!NOTE]
> Replace `A1:B2:C3:D4:E5:F6` by your input device's Bluetooth MAC address

### 3.2. Setup

6. On the Pi, clone the repository to your home directory:
  
   ```console
   cd ~ && git clone https://github.com/quaxalber/bluetooth_2_usb.git
   ```

7. Run the installation script as root:
   
   ```console
   sudo ~/bluetooth_2_usb/scripts/install.sh
   ```

8.  Reboot:
 
    ```console
    sudo reboot
    ``` 

9.  Verify that the service is running:
   
    ```console
    service bluetooth_2_usb status
    ```

    It should look something like this and say `Active: active (running)`:

    ```console
    user@pi0w:~ $ service bluetooth_2_usb status
    ● bluetooth_2_usb.service - Bluetooth to USB HID relay
        Loaded: loaded (/etc/systemd/system/bluetooth_2_usb.service; enabled; preset: enabled)
        Active: active (running) since Wed 2023-12-13 10:33:00 CET; 44min ago
      Main PID: 5865 (bash)
          Tasks: 4 (limit: 389)
            CPU: 2min 49.448s
        CGroup: /system.slice/bluetooth_2_usb.service
                ├─5865 bash /usr/bin/bluetooth_2_usb --auto_discover --grab_devices
                └─5869 python3.11 /home/user/bluetooth_2_usb/bluetooth_2_usb.py --auto_discover --grab_devices

    Dec 13 10:33:00 pi0w systemd[1]: Started bluetooth_2_usb.service - Bluetooth to USB HID relay.
    Dec 13 10:33:06 pi0w bluetooth_2_usb[5869]: 23-12-13 10:33:06 [INFO] Launching Bluetooth 2 USB v0.8.0
    Dec 13 10:33:06 pi0w bluetooth_2_usb[5869]: 23-12-13 10:33:06 [INFO] Discovering input devices...
    Dec 13 10:33:09 pi0w bluetooth_2_usb[5869]: 23-12-13 10:33:09 [INFO] Activated relay for device /dev/input/event2, name "AceRK Mouse", phys "0a:1b:2c:3d:4e:5f"
    Dec 13 10:33:09 pi0w bluetooth_2_usb[5869]: 23-12-13 10:33:09 [INFO] Activated relay for device /dev/input/event1, name "AceRK Keyboard", phys "0a:1b:2c:3d:4e:5f"
    Dec 13 10:33:09 pi0w bluetooth_2_usb[5869]: 23-12-13 10:33:09 [INFO] Activated relay for device /dev/input/event0, name "vc4-hdmi", phys "vc4-hdmi/input0"
    ```

> [!NOTE]
> Something seems off? Try yourself in [Troubleshooting](#7-troubleshooting)!
   
## 4. Usage

### 4.1. Connection to target device / host

#### 4.1.1. Raspberry Pi 4 Model B

Connect the _USB-C power port_ of your Pi 4B via cable with a USB port on your target device. You should hear the USB connection sound (depending on the target device) and be able to access your target device wirelessly using your Bluetooth keyboard or mouse. In case the Pi solely draws power from the host, it will take some time for the Pi to boot.

> [!IMPORTANT]
> It's essential to use the small power port instead of the bigger USB-A ports, since only the power port has the [OTG](https://en.wikipedia.org/wiki/USB_On-The-Go) feature required for [USB gadgets](https://www.kernel.org/doc/html/latest/driver-api/usb/gadget.html).

#### 4.1.2. Raspberry Pi Zero (2) W(H)

For the Pi Zero, the situation is quite the opposite: Do _not_ use the power port to connect to the target device, _use_ the other port instead (typically labeled "DATA" or "USB"). You may connect the power port to a stable power supply.

### 4.2. Command-line arguments

Currently you can provide the following CLI arguments:

```console
user@pi0w:~ $ bluetooth_2_usb -h
usage: bluetooth_2_usb.py [--device_ids DEVICE_IDS] [--auto_discover] [--grab_devices] [--list_devices] [--log_to_file] [--log_path LOG_PATH] [--debug] [--version] [--help]

Bluetooth to USB HID relay. Handles Bluetooth keyboard and mouse events from multiple input devices and translates them to USB using Linux's gadget mode.

options:
  --device_ids DEVICE_IDS, -i DEVICE_IDS
                        Comma-separated list of identifiers for input devices to be relayed.
                        An identifier is either the input device path, the MAC address or any case-insensitive substring of the device name.
                        Example: --device_ids '/dev/input/event2,a1:b2:c3:d4:e5:f6,0A-1B-2C-3D-4E-5F,logi'
                        Default: None
  --auto_discover, -a   Enable auto-discovery mode. All readable input devices will be relayed automatically.
                        Default: disabled
  --grab_devices, -g    Grab the input devices, i.e., suppress any events on your relay device.
                        Devices are not grabbed by default.
  --list_devices, -l    List all available input devices and exit.
  --log_to_file, -f     Add a handler that logs to file, additionally to stdout.
  --log_path LOG_PATH, -p LOG_PATH
                        The path of the log file
                        Default: /var/log/bluetooth_2_usb/bluetooth_2_usb.log
  --debug, -d           Enable debug mode (Increases log verbosity)
                        Default: disabled
  --version, -v         Display the version number of this software and exit.
  --help, -h            Show this help message and exit.
```

### 4.3. Consuming the API from your Python code

The API is designed such that it may be consumed both via CLI and from within external Python code. More details on this [coming soon](https://github.com/quaxalber/bluetooth_2_usb/issues/16)!

## 5. Updating

You may update to the latest stable release by running:

```console
sudo ~/bluetooth_2_usb/scripts/update.sh
```

> [!NOTE]
> The update script performs a clean reinstallation, that is run `uninstall.sh`, delete the repo folder, clone again and run the install script. The current branch will be maintained.

## 6. Uninstallation

You may uninstall Bluetooth 2 USB by running:

```console
sudo ~/bluetooth_2_usb/scripts/uninstall.sh
```

## 7. Troubleshooting

### 7.1. The Pi keeps rebooting or crashes randomly

This is likely due to the limited power the Pi can draw from the host's USB port. Try these steps:

- If available, connect your Pi to a USB 3 port on the host / target device (usually blue) or preferably USB-C.
 
> [!IMPORTANT]
> *Do not use* the blue (or black) USB-A ports *of your Pi* to connect. **This won't work.**
>
> *Do use* the small USB-C power port (in case of Pi 4B). For Pi Zero, use the data port to connect to the host and attach the power port to a dedicated power supply.

- Try to [connect to the Pi via SSH](#31-prerequisites) instead of attaching a display directly and remove any unnecessary peripherals.
 
- Install a [lite version](https://downloads.raspberrypi.org/raspios_lite_arm64/images/) of your OS on the Pi (without GUI)
 
- For Pi 4B: Get a [USB-C Data/Power Splitter](https://thepihut.com/products/usb-c-data-power-splitter) and draw power from a dedicated power supply. This should ultimately resolve any power-related issues, and your Pi 4B will no longer be dependent on the host's power supply.
 
> [!NOTE]
> The Pi Zero is recommended to have a 1.2 A power supply for stable operation, the Pi Zero 2 requires 2.0 A and the Pi 4B even 3.0 A, while hosts may typically only supply up to 0.5/0.9 A through USB-A 2.0/3.0 ports. However, this may be sufficient depending on your specific soft- and hardware configuration. For more information see the [Raspberry Pi documentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply).

### 7.2. The installation was successful, but I don't see any output on the target device

This could be due to a number of reasons. Try these steps:

- Verify that the service is running:
 
  ```console
  service bluetooth_2_usb status
  ```

- Verify that you specified the correct input devices in `bluetooth_2_usb.service`
 
- Verify that your Bluetooth devices are paired, trusted, connected and *not* blocked:
 
  ```console
  bluetoothctl
  info A1:B2:C3:D4:E5:F6
  ```
 
  It should look like this:

  ```console
  user@pi0w:~ $ bluetoothctl
  Agent registered
  [CHG] Controller 0A:1B:2C:3D:4E:5F Pairable: yes
  [AceRK]# info A1:B2:C3:D4:E5:F6
  Device A1:B2:C3:D4:E5:F6 (random)
          Name: AceRK
          Alias: AceRK
          Paired: yes     <---
          Trusted: yes    <---
          Blocked: no     <---
          Connected: yes  <---
          WakeAllowed: no
          LegacyPairing: no
          UUID: Generic Access Profile    (00001800-0000-1000-8000-00805f9b34fb)
          UUID: Generic Attribute Profile (00001801-0000-1000-8000-00805f9b34fb)
          UUID: Device Information        (0000180a-0000-1000-8000-00805f9b34fb)
          UUID: Human Interface Device    (00001812-0000-1000-8000-00805f9b34fb)
          UUID: Nordic UART Service       (6e400001-b5a3-f393-e0a9-e50e24dcca9e)
  ```
 
> [!NOTE]
> Replace `A1:B2:C3:D4:E5:F6` by your input device's Bluetooth MAC address

- Reload and restart service:
 
  ```console
  sudo systemctl daemon-reload && sudo service bluetooth_2_usb restart
  ```

- Reboot Pi
 
  ```console
  sudo reboot
  ```

- Re-connect the Pi to the host and check that the cable is capable of transmitting data, not power only
 
- Try a different USB port on the host
 
- Try connecting to a different host

### 7.3. In bluetoothctl, my device is constantly switching on/off

This is a common issue, especially when the device gets paired with multiple hosts. One simple fix/workaround is to re-pair the device:

```console
bluetoothctl
power off
power on
block A1:B2:C3:D4:E5:F6
remove A1:B2:C3:D4:E5:F6
scan on
trust A1:B2:C3:D4:E5:F6
pair A1:B2:C3:D4:E5:F6
connect A1:B2:C3:D4:E5:F6
```

If the issue persists, it's worth trying to delete the cache:

```console
sudo -i
cd '/var/lib/bluetooth/0A:1B:2C:3D:4E:5F/cache'
rm -rf 'A1:B2:C3:D4:E5:F6'
exit
```

> [!NOTE]
> Replace `0A:1B:2C:3D:4E:5F` by your Pi's Bluetooth controller's MAC and `A1:B2:C3:D4:E5:F6` by your input device's MAC

### 7.4. I have a different issue

Here's a few things you could try:

- Check the log files (default at `/var/log/bluetooth_2_usb/`) for errors
 
> [!NOTE]
> Logging to file requires the `-f` flag

- You may also query the journal to inspect the service logs in real-time:
 
  ```console
  journalctl -u bluetooth_2_usb.service -n 50 -f
  ```

- For easier degguging, you may temporarily stop the service and run the script manually, modifying arguments as required, e.g., increase log verbosity by appending `-d`:

  ```console
  sudo service bluetooth_2_usb stop && sudo bluetooth_2_usb -ad ; sudo service bluetooth_2_usb start
  ```

- When you interact with your Bluetooth devices with `-d` set, you should see debug output in the logs such as:

  ```console
  user@pi0w:~/bluetooth_2_usb $ sudo service bluetooth_2_usb stop && sudo bluetooth_2_usb -i hdmi,a1:b2:c3:d4:e5:f6,/dev/input/event3 -d ; sudo service bluetooth_2_usb start
  23-12-16 15:52:21 [DEBUG] CLI args: device_ids=['hdmi', 'a1:b2:c3:d4:e5:f6', '/dev/input/event3'], auto_discover=False, grab_devices=False, list_devices=False, log_to_file=False, log_path=/var/log/bluetooth_2_usb/bluetooth_2_usb.log, debug=True, version=False
  23-12-16 15:52:21 [DEBUG] Logging to stdout
  23-12-16 15:52:21 [INFO] Launching Bluetooth 2 USB v0.8.0
  23-12-16 15:52:21 [INFO] Discovering input devices...
  23-12-16 15:52:21 [DEBUG] Relaying devices with matching name "hdmi" or MAC "a1:b2:c3:d4:e5:f6" or path "/dev/input/event3"
  23-12-16 15:52:21 [DEBUG] Initializing USB gadgets...
  23-12-16 15:52:24 [DEBUG] Enabled USB gadgets: [mouse gadget (/dev/hidg0), keyboard gadget (/dev/hidg1), consumer control gadget (/dev/hidg2)]
  23-12-16 15:52:24 [INFO] Activated relay for device /dev/input/event2, name "AceRK Mouse", phys "0a:1b:2c:3d:4e:5f"
  23-12-16 15:52:24 [INFO] Activated relay for device /dev/input/event1, name "AceRK Keyboard", phys "0a:1b:2c:3d:4e:5f"
  23-12-16 15:52:24 [INFO] Activated relay for device /dev/input/event0, name "vc4-hdmi", phys "vc4-hdmi/input0"
  ### Manually switched Pi's Bluetooth off ###
  23-12-16 15:53:27 [CRITICAL] Connection to AceRK Keyboard lost [OSError(19, 'No such device')]
  23-12-16 15:53:27 [CRITICAL] Connection to AceRK Mouse lost [OSError(19, 'No such device')]
  ### Manually switched Pi's Bluetooth back on ###
  23-12-16 15:53:31 [INFO] Activated relay for device /dev/input/event2, name "AceRK Mouse", phys "0a:1b:2c:3d:4e:5f"
  23-12-16 15:53:31 [INFO] Activated relay for device /dev/input/event1, name "AceRK Keyboard", phys "0a:1b:2c:3d:4e:5f"
  23-12-16 15:54:20 [DEBUG] Received event at 1702738460.417525, code 04, type 04, val 458827 from AceRK Keyboard
  23-12-16 15:54:20 [DEBUG] Received key event at 1702738460.417525, 104 (KEY_PAGEUP), down from AceRK Keyboard
  23-12-16 15:54:20 [DEBUG] Converted evdev scancode 0x68 (KEY_PAGEUP) to HID UsageID 0x4B (PAGE_UP)
  23-12-16 15:54:20 [DEBUG] Pressing PAGE_UP (0x4B) on keyboard gadget (/dev/hidg1)
  23-12-16 15:54:20 [DEBUG] Received synchronization event at 1702738460.417525, SYN_REPORT from AceRK Keyboard
  23-12-16 15:54:20 [DEBUG] Received event at 1702738460.466388, code 04, type 04, val 458827 from AceRK Keyboard
  23-12-16 15:54:20 [DEBUG] Received key event at 1702738460.466388, 104 (KEY_PAGEUP), up from AceRK Keyboard
  23-12-16 15:54:20 [DEBUG] Converted evdev scancode 0x68 (KEY_PAGEUP) to HID UsageID 0x4B (PAGE_UP)
  23-12-16 15:54:20 [DEBUG] Releasing PAGE_UP (0x4B) on keyboard gadget (/dev/hidg1)
  23-12-16 15:54:20 [DEBUG] Received synchronization event at 1702738460.466388, SYN_REPORT from AceRK Keyboard
  23-12-16 15:54:34 [DEBUG] Received event at 1702738474.116380, code 04, type 04, val 786665 from AceRK Keyboard
  23-12-16 15:54:34 [DEBUG] Received key event at 1702738474.116380, 115 (KEY_VOLUMEUP), down from AceRK Keyboard
  23-12-16 15:54:34 [DEBUG] Converted evdev scancode 0x73 (KEY_VOLUMEUP) to HID UsageID 0xE9 (VOLUME_INCREMENT)
  23-12-16 15:54:34 [DEBUG] Pressing VOLUME_INCREMENT (0xE9) on consumer control gadget (/dev/hidg2)
  23-12-16 15:54:34 [DEBUG] Received synchronization event at 1702738474.116380, SYN_REPORT from AceRK Keyboard
  23-12-16 15:54:34 [DEBUG] Received event at 1702738474.117192, code 04, type 04, val 786665 from AceRK Keyboard
  23-12-16 15:54:34 [DEBUG] Received key event at 1702738474.117192, 115 (KEY_VOLUMEUP), up from AceRK Keyboard
  23-12-16 15:54:34 [DEBUG] Converted evdev scancode 0x73 (KEY_VOLUMEUP) to HID UsageID 0xE9 (VOLUME_INCREMENT)
  23-12-16 15:54:34 [DEBUG] Releasing VOLUME_INCREMENT (0xE9) on consumer control gadget (/dev/hidg2)
  23-12-16 15:54:34 [DEBUG] Received synchronization event at 1702738474.117192, SYN_REPORT from AceRK Keyboard
  23-12-16 15:54:36 [DEBUG] Received event at 1702738476.895033, code 04, type 04, val 589826 from AceRK Mouse
  23-12-16 15:54:36 [DEBUG] Received key event at 1702738476.895033, 273 (BTN_RIGHT), down from AceRK Mouse
  23-12-16 15:54:36 [DEBUG] Converted evdev scancode 0x111 (BTN_RIGHT) to HID UsageID 0x02 (RIGHT)
  23-12-16 15:54:36 [DEBUG] Pressing RIGHT (0x02) on mouse gadget (/dev/hidg0)
  23-12-16 15:54:36 [DEBUG] Received synchronization event at 1702738476.895033, SYN_REPORT from AceRK Mouse
  23-12-16 15:54:36 [DEBUG] Received event at 1702738476.943781, code 04, type 04, val 589826 from AceRK Mouse
  23-12-16 15:54:36 [DEBUG] Received key event at 1702738476.943781, 273 (BTN_RIGHT), up from AceRK Mouse
  23-12-16 15:54:36 [DEBUG] Converted evdev scancode 0x111 (BTN_RIGHT) to HID UsageID 0x02 (RIGHT)
  23-12-16 15:54:36 [DEBUG] Releasing RIGHT (0x02) on mouse gadget (/dev/hidg0)
  23-12-16 15:54:36 [DEBUG] Received synchronization event at 1702738476.943781, SYN_REPORT from AceRK Mouse
  23-12-16 15:54:37 [DEBUG] Received relative axis event at 1702738477.675038, REL_X from AceRK Mouse
  23-12-16 15:54:37 [DEBUG] Moving mouse gadget (/dev/hidg0) (x=125, y=0, mwheel=0)
  23-12-16 15:54:37 [DEBUG] Received synchronization event at 1702738477.675038, SYN_REPORT from AceRK Mouse
  ^C23-12-16 15:54:50 [INFO] Received signal: SIGINT, frame: <frame at 0xb5ec9930, file '/usr/lib/python3.11/selectors.py', line 468, code select>
  23-12-16 15:54:50 [CRITICAL] vc4-hdmi was cancelled
  23-12-16 15:54:50 [CRITICAL] AceRK Keyboard was cancelled
  23-12-16 15:54:50 [CRITICAL] AceRK Mouse was cancelled
  ```

- Still not resolved? Double-check the [installation instructions](#3-installation)
 
- For more help, open an [issue](https://github.com/quaxalber/bluetooth_2_usb/issues) in the [GitHub repository](https://github.com/quaxalber/bluetooth_2_usb)

### 7.5. Everything is working, but can it help me with Bitcoin mining?

Absolutely! [Here's how](https://bit.ly/42BTC).

## 8. Bonus points

After successfully setting up your Pi as a HID proxy for your Bluetooth devices, you may consider making [Raspberry Pi OS read-only](https://learn.adafruit.com/read-only-raspberry-pi/overview). That helps preventing the SD card from wearing out and the file system from getting corrupted when powering off the Raspberry forcefully.

## 9. Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](https://github.com/quaxalber/bluetooth_2_usb/blob/main/CONTRIBUTING.md) file for guidelines.

## 10. License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/quaxalber/bluetooth_2_usb/blob/main/LICENSE) file for details.

[Bluetooth to USB Overview](https://raw.githubusercontent.com/quaxalber/bluetooth_2_usb/main/assets/overview.png) image by [Laura T.](mailto:design@quaxalber.de) is licensed under a [Creative Commons Attribution-NonCommercial 4.0 International License](http://creativecommons.org/licenses/by-nc/4.0/).

![License image.](https://i.creativecommons.org/l/by-nc/4.0/88x31.png)

## 11. Acknowledgments

* [Mike Redrobe](https://github.com/mikerr/pihidproxy) for the idea and the basic code logic and [HeuristicPerson's bluetooth_2_hid](https://github.com/HeuristicPerson/bluetooth_2_hid) based off this.
* [Georgi Valkov](https://github.com/gvalkov) for [python-evdev](https://github.com/gvalkov/python-evdev) making reading input devices a walk in the park.
* The folks at [Adafruit](https://www.adafruit.com/) for [CircuitPython HID](https://github.com/adafruit/Adafruit_CircuitPython_HID) and [Blinka](https://github.com/quaxalber/Adafruit_Blinka/blob/main/src/usb_hid.py) providing super smooth access to USB gadgets.
* Special thanks to the open-source community for various other libraries and tools.

# Bluetooth to USB

![License image.](images/diagram.png)

## Introduction

Convert a Raspberry Pi into a HID proxy that relays Bluetooth keyboard and mouse input to USB. Minimal configuration. Zero hassle. 

The issue with Bluetooth devices is that you usually can't use them to access the BIOS or OS select menu (GRUB). Some devices don't even have a (working) Bluetooth interface.  
**This is the solution!**

To solve those issues, we will use a Raspberry Pi as an intermediary to convert the Bluetooth commands from the keyboard or mouse to plain HID (Human Interface Device) instructions sent through the USB port. The Pi effectively impersonates a regular USB keyboard. 

## Setup 

  1. Prepare your Raspberry Pi (e.g. [RPi Imager](https://youtu.be/ntaXWS8Lk34)), with correct WI-FI settings & SSH enabled.
  1. SSH to your Pi, `sudo apt update && sudo apt upgrade -y`
  1. Pair your Bluetooth device(s) with the Raspberry Pi, using `bluetoothctl` :
     1. `scan on` (you need this to pair your device even if you know the MAC address)
     1. Put your device in pairing mode
     1. You should see your device in discovered devices and note its MAC address
     1. `pair {your-device-mac}`
     1. `connect {your-device-mac}` when the device is still trying to pair
     1. `trust {your-device-mac}`
  1. Clone this repository & `cd` into the directory.
  1. Run `sudo ./install.sh` which will take care of the rest.
     
## Known issues
 
If the device enters energy saving mode, the Pi may lose connection causing the device `/dev/input/eventX` to become unavailable. Restarting the service should fix this:
`sudo service bluetooth_2_usb restart`

## Extra mile

After successfully setting up your Pi as a HID proxy for your Bluetooth devices, you may consider making [Raspberry OS read-only](https://learn.adafruit.com/read-only-raspberry-pi/overview). That helps preventing the SD card from wearing out and the file system from getting corrupted when powering off the Raspberry forcefully.

# Credits

  * [Mike Redrobe](https://github.com/mikerr/pihidproxy) for the idea and the basic code logic and [HeuristicPerson's bluetooth_2_hid](https://github.com/HeuristicPerson/bluetooth_2_hid) based off this.
  * [Georgi Valkov](https://github.com/gvalkov) for [python-evdev](https://github.com/gvalkov/python-evdev) making reading input devices a walk in the park. 
  * The folks at [Adafruit](https://www.adafruit.com/) for [CircuitPython HID](https://github.com/adafruit/Adafruit_CircuitPython_HID) providing super smooth access to USB gadgets. 

# License

![License image.](https://i.creativecommons.org/l/by-nc/4.0/88x31.png)

"Bluetooth 2 HID" [@PixelGordo](https://twitter.com/PixelGordo) is licensed under a [Creative Commons Attribution-NonCommercial 4.0 International
License](http://creativecommons.org/licenses/by-nc/4.0/). Based on a work at
[https://github.com/PixelGordo/bluetooth_2_hid](https://github.com/PixelGordo/bluetooth_2_hid).

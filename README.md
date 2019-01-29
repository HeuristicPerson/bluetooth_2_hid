# Bluetooth to HID

![License image.](images/diagram.png)

## Introduction

This package contains a set of scripts to turn your **Raspberry Pi Zero W** into a HID proxy capable Bluetooth dongle
for keyboards.

No worries if you don't understand a word, here is the explanation of the project in plain words: Imagine you have a
Bluetooth keyboard. You pair it in with your Bluetooth receiver in Windows, Linux, or Mac OS using the appropiate
software and you simply use it, right? But what happens if you need to use that keyboard to access the computer BIOS
or operating system select menu (GRUB)? or an old device that accepts USB keyboards but no Bluetooth devices?
**You are done!**

To solve those issues, we will use a Raspberry Pi Zero W (it's important that it's the **W** model because it has a
Bluetooth receiver) as an intermediary to convert the Bluetooth commands from the keyboard to plain HID (Human Interface
Device) instructions sent through the USB port. 


## Usage

(to be improved)

  0. Create your output HID device (see Alle Beiträge von Tobi's reference below).
  1. Pair your Bluetooth keyboard with the Raspberry Pi (using bluetoothctl).
  2. Execute ''bluetooth_2_hid.py'' with sudo.
  3. That's it...
  
## Known bugs

If the keyboard enters energy saving mode, it stops being detected by the Raspberry and the input device
''/dev/input/event0'' is no longer available, making the script to crash.

## Extra work to be done

If you succeed setting your Raspberry Pi Zero W as a HID proxy for your Bluetooth keyboard, there is still more to do:

  1. Set Raspbian as read-only. That will help preventing the SD card from getting corrupted when powering off the
     Raspberry. Remember we won't properly shut down the Pi, we'll simply cut its power when shutting down your PC. If
     that happens while the Pi is writing any file, the entire system could get corrupted.
     
  2. During the configuration of the Raspberry Pi we would access it through SSH over WiFi network connection. Those
     services require a lot of time to start when powering up the Pi (around 12 seconds). That means that you could
     never access the BIOS of your computer with this setup because it's likely the system is not yet ready to execute
     our Bluetooth-to-HID script.
     
  3. **VERY IMPORTANT:** Once everything is working, make a backup of the Pi's SD card. You don't want to repeat all the
     setup if anything fails, do you? **;)**


# Credits

  * [Mike Redrobe](https://github.com/mikerr/pihidproxy) for the idea and the basic code logic. This project is
    basically a rewrite of his code.
  * [Alle Beiträge von Tobi](https://www.isticktoit.net/?p=1383) for some code clarifications.
  * [Ondřej Hruška](https://gist.github.com/MightyPork/6da26e382a7ad91b5496ee55fdc73db2) for his list of HID codes.


# License

![License image.](https://i.creativecommons.org/l/by-nc/4.0/88x31.png)

"Bluetooth 2 HID" [@PixelGordo](https://twitter.com/PixelGordo) is
licensed under a [Creative Commons Attribution-NonCommercial 4.0 International
License](http://creativecommons.org/licenses/by-nc/4.0/). Based on a work at
[https://github.com/PixelGordo/bluetooth_2_hid](https://github.com/PixelGordo/bluetooth_2_hid).

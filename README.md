# Bluetooth to HID

![Diagram of the connections](images/diagram.png)

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


# License

![License image.](https://i.creativecommons.org/l/by-nc/4.0/88x31.png)

Wah!Cade Focus Layout by [@PixelGordo](https://twitter.com/PixelGordo) is
licensed under a [Creative Commons Attribution-NonCommercial 4.0 International
License](http://creativecommons.org/licenses/by-nc/4.0/). Based on a work at
[https://github.com/PixelGordo/Wah-Cade-Focus-Layout](https://github.com/PixelGordo/Wah-Cade-Focus-Layout).

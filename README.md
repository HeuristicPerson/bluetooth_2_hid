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

  0. Prepare your Raspberry Pi Zero W. with the [Raspberry Pi Imager](https://youtu.be/ntaXWS8Lk34), with correct wifi settings & ssh enabled.
  1. Connect with SSH to your Raspberry Pi Zero W, `sudo apt-get update && sudo apt-get upgrade -y`
  2. Clone this repository in your `pi` default user home directory.
  3. Create your output HID device (see Alle Beiträge von Tobi's reference below). `install.sh` should help.
  4. Pair your Bluetooth keyboard with the Raspberry Pi (using `bluetoothctl`).
  5. Execute `$ sudo bluetooth_2_hid.py -t -d` to check the software is able to read your Bluetooth keyboard inputs
     and translate them to HID commands (because we are in test mode `-t`, the software won't send any HID signal). If
     it's now working, check/repeat the steps 1-2-3
  5. If it's working fine, don't touch your Bluetooth keyboard for 10-15 minutes (have a coffee with your partner, speak
     to your children about the dangers of learning to code... you know, the typical stuff). We need to check that the
     keyboard is able to automatically re-connect after entering energy saving mode. If it does, CONGRATULATIONS!
  6. To run `bluetooth_2_hid` as a service, you can use `bluetooth_2_hid.service` and add it to `systemd`.
     `install.sh` add a link in  from `pi` user in `systemd` services directory.
     Run `sudo systemctl start bluetooth_2_hid.service && sudo systemctl enable bluetooth_2_hid.service`.
     
## Known bugs
 
If the keyboard enters energy saving mode, it stops being detected by the Raspberry and the input device
`/dev/input/event0` is no longer available, making the script to crash.

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

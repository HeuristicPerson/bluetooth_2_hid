#!/bin/bash
#echo "dtoverlay=dwc2" | sudo tee -a /boot/config.txt
#echo "dwc2" | sudo tee -a /etc/modules
#echo "libcomposite" | sudo tee -a /etc/modules

#pip3 install evdev

currentScriptDirectory=$(dirname $(readlink -f $0))

chmod u+x $currentScriptDirectory/usb_hid.service
ln -s $currentScriptDirectory/usb_hid.service /etc/systemd/system/
chmod u+x $currentScriptDirectory/usb_hid.sh
ln -s $currentScriptDirectory/usb_hid.sh /usr/bin/

chmod u+x $currentScriptDirectory/bluetooth_2_hid.py
ln -s $currentScriptDirectory/bluetooth_2_hid.py /usr/bin/
chmod u+x $currentScriptDirectory/bluetooth_2_hid.service
ln -s $currentScriptDirectory/bluetooth_2_hid.service /etc/systemd/system/

systemctl enable usb_hid.service
systemctl enable bluetooth_2_hid.service

#reboot

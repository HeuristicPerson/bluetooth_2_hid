#!/usr/bin/env bash

# Write the MAC of your Bluetooth Keyboard here
MAC="28:18:78:17:67:D0"

echo "connect $MAC" | sudo bluetoothctl

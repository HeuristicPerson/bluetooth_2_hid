#!/usr/bin/env bash
# Temporarily disable history expansion
set +H

# ANSI escape codes for colored output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
# Reset to default color
NC='\033[0m'

colored_output() {
  local color_code="$1"
  local message="$2"
  local no_newline_flag="$3"
  local colored_message="${color_code}${message}${NC}"
  if [ "$no_newline_flag" == "-n" ]; then
    echo -ne "$colored_message"
  else
    echo -e "$colored_message"
  fi
}

# Check for superuser privileges
if [[ $EUID -ne 0 ]]; then
    colored_output ${RED} "This script must be run as root. Attempting to elevate privileges..."
    # Re-run the script as root
    exec sudo bash "$0" "$@"
fi

# Function to append text to a file if the text doesn't already exist in the file
append_if_not_exist() {
  TEXT="$1"
  FILE="$2"
  BACKUP="$FILE.bak"

  # Create a backup of the original file
  cp "$FILE" "$BACKUP"

  if ! grep -q "^$TEXT" "$FILE"; then
    echo "$TEXT" | tee -a "$FILE" > /dev/null
  fi
}

colored_output ${GREEN} "Installing bluetooth_2_usb prerequisites..."

apt update && apt upgrade -y && apt install -y git python3.11 python3.11-venv

colored_output ${GREEN} "Initializing submodules..."

git submodule update --init --recursive
python3.11 -m venv venv
venv/bin/pip3.11 install submodules/*

colored_output ${GREEN} "Modifying system files..."

append_if_not_exist "dtoverlay=dwc2" "/boot/config.txt"
append_if_not_exist "dwc2" "/etc/modules"
append_if_not_exist "libcomposite" "/etc/modules"

cp /boot/cmdline.txt /boot/cmdline.txt.bak
sed -i 's/modules-load=[^[:space:]]* //g' /boot/cmdline.txt
sed -i 's/rootwait/rootwait modules-load=dwc2/g' /boot/cmdline.txt

currentScriptDirectory=$(dirname $(readlink -f $0))
chmod 744 $currentScriptDirectory/bluetooth_2_usb.py
ln -s $currentScriptDirectory/bluetooth_2_usb.py /usr/bin/
ln -s $currentScriptDirectory/bluetooth_2_usb.service /etc/systemd/system/
# The expression ${currentScriptDirectory//\//\\/} is used to replace all occurrences of slashes (/) in the variable currentScriptDirectory with escaped slashes (\/)
sed -i "s/{python3.11-venv}/${currentScriptDirectory//\//\\/}\/venv\/bin\/python3.11/g" bluetooth_2_usb.service

mkdir /var/log/bluetooth_2_usb
systemctl enable bluetooth_2_usb.service

# Re-enable history expansion
set -H

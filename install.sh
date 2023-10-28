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
apt update && apt upgrade -y && apt install -y git python3.11

colored_output ${GREEN} "Updating submodules..."
git submodule update --init --recursive

append_if_not_exist "dtoverlay=dwc2" "/boot/config.txt"
append_if_not_exist "dwc2" "/etc/modules"
append_if_not_exist "libcomposite" "/etc/modules"

# Check if python3.11 is installed and install if not
if command -v python3.11 &> /dev/null; then
  colored_output ${GREEN} "$(python3.11 --version) already installed"
else
  # Check for automation flag to bypass prompt
  if [ "$AUTO" == "true" ]; then
    REPLY="y"
  else
    colored_output ${YELLOW} "Python 3.11 not installed. Building and installing from source now. Depending on your hardware, this may take a while. Continue? (y/n) " -n
    # Read single character input
    read -n 1 -r
  fi

  if [[ $REPLY =~ ^[Yy]$ ]]; then
    bash install_python_3.11.sh
  else
    colored_output ${RED} "Python 3.11 required but not installed. Please install Python 3.11 before running Bluetooth 2 USB."
  fi
fi

currentScriptDirectory=$(dirname $(readlink -f $0))

mkdir /var/log/bluetooth_2_usb

chmod 744 $currentScriptDirectory/bluetooth_2_usb.py
ln -s $currentScriptDirectory/bluetooth_2_usb.py /usr/bin/
ln -s $currentScriptDirectory/bluetooth_2_usb.service /etc/systemd/system/

systemctl enable bluetooth_2_usb.service

# Check for automation flag to bypass prompt
if [ "$AUTO" == "true" ]; then
  REPLY="y"
else
  # Notify user about the reboot
  colored_output ${YELLOW} "The system needs to reboot to complete the installation. Reboot now? (y/n) " -n
  # Read single character input
  read -n 1 -r
fi

echo

# Re-enable history expansion
set -H

if [[ $REPLY =~ ^[Yy]$ ]]; then
    reboot
fi

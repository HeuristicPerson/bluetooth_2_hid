#!/usr/bin/env bash
# Update Bluetooth 2 USB to the latest stable GitHub version. Handles updating submodules, if required. 

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
  local colored_message="${color_code}${message}${NC}"
  echo -e "${colored_message}"
}

abort_update() {
  local message="$1"
  colored_output "${RED}" "Aborting update. ${message}"
  # Re-enable history expansion
  set -H
  exit 1
}

# Check for superuser privileges
if [[ $EUID -ne 0 ]]; then
  colored_output "${RED}" "This script must be run as root. Attempting to elevate privileges..."
  # Re-run the script as root
  exec sudo bash "$0" "$@"
fi

# Determine the current script's directory and the parent directory
scripts_directory=$(dirname $(readlink -f "$0"))
base_directory=$(dirname "${scripts_directory}")
cd "${base_directory}"

colored_output "${GREEN}" "Updating Bluetooth 2 USB..."

{ sudo scripts/uninstall.sh && cd .. && sudo rm -rf bluetooth_2_usb && git clone https://github.com/quaxalber/bluetooth_2_usb.git && sudo bluetooth_2_usb/scripts/install.sh && service bluetooth_2_usb start ; } || abort_update "Failed updating Bluetooth 2 USB"

colored_output "${GREEN}" "Update successful. Now running $(/usr/bin/bluetooth_2_usb -v)"

# Re-enable history expansion
set -H

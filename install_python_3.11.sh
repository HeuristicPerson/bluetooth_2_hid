#!/usr/bin/env bash

# Check for superuser privileges
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root. Attempting to elevate privileges..."
    # Re-run the script as root
    exec sudo bash "$0" "$@"
fi

echo "Installing Python build dependencies"
apt-get update
apt-get install -y wget build-essential libreadline-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev

PY_VER="3.11.5"
echo "Installing Python $PY_VER"
wget "https://www.python.org/ftp/python/$PY_VER/Python-$PY_VER.tgz"
tar -zxvf "Python-$PY_VER.tgz"
cd "Python-$PY_VER"
./configure --enable-optimizations
make altinstall
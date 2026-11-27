#!/bin/bash
set -e
echo 'Baue MustafasSystem (Debian Trixie)...'
apt-get update
apt-get install -y xfce4 xfce4-goodies compton waydroid firefox-esr vlc zram-tools firmware-linux firmware-iwlwifi bluez pulseaudio
systemctl enable zramswap
waydroid init
echo 'MustafasSystem erfolgreich gebaut!'
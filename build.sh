#!/bin/bash
set -e
echo 'Bauen von MustafasSystem (Debian Trixie)...'
apt-get update
apt-get install -y xfce4 xfce4-goodies network-manager bluez pulseaudio firmware-linux firmware-iwlwifi firmware-realtek waydroid zram-tools firefox-esr vlc compton
systemctl enable waydroid-container
waydroid init
echo 'MustafasSystem erfolgreich erstellt!'
#!/bin/bash
set -e
export DEBIAN_FRONTEND=noninteractive
echo 'Baue MustafasSystem (Debian Trixie)...'
apt-get update
apt-get install -y xfce4 xfce4-goodies waydroid weston firefox-esr vlc zram-tools firmware-linux firmware-iwlwifi bluez pulseaudio network-manager lightdm
systemctl enable lightdm
echo 'ZRAM konfigurieren...'
echo 'ALLOCATION=zram' > /etc/default/zramswap
zramswap start
echo 'Waydroid initialisieren...'
waydroid init -s GAPPS
echo 'MustafasSystem erfolgreich gebaut!'
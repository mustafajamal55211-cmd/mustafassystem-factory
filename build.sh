#!/bin/bash
set -e
echo 'Baue MustafasSystem (Debian Trixie)...'
apt-get update
apt-get install -y xfce4 xfce4-goodies waydroid network-manager bluez zram-tools firefox-esr
systemctl enable zram-tools
systemctl enable bluetooth
waydroid init -s GAPPS
echo 'Build erfolgreich abgeschlossen!'
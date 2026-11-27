#!/bin/bash
set -e
echo 'Bauen von MustafasSystem...'
apt-get update
apt-get install -y xfce4 xfce4-goodies compton waydroid zram-tools firefox-esr vlc firmware-linux firmware-iwlwifi
systemctl enable zramswap
waydroid init -s GAPPS
echo 'MustafasSystem erfolgreich erstellt!'
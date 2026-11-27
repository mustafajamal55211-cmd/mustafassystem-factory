#!/bin/bash
set -e
echo "Starte Build für MustafasSystem (Debian Trixie)..."
apt-get update
apt-get install -y xfce4 xfce4-goodies network-manager bluez blueman zram-tools waydroid weston firefox-esr firmware-linux firmware-iwlwifi firmware-realtek
# ZRAM aktivieren
echo 'ALGO=zstd' > /etc/default/zramswap
echo 'PERCENT=50' >> /etc/default/zramswap
systemctl enable zramswap
# Netzwerk und Bluetooth starten
systemctl enable NetworkManager
systemctl enable bluetooth
# Waydroid initialisieren
waydroid init -s GAPPS
echo "MustafasSystem erfolgreich gebaut!"
#!/bin/bash
set -e
echo 'Bauen von MustafasSystem...'
apt-get update
apt-get install -y xfce4 xfce4-goodies waydroid zram-tools firefox-esr
systemctl enable zramswap
waydroid init -s GAPPS
echo 'Build erfolgreich abgeschlossen!'
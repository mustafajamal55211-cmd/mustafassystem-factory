#!/usr/bin/env bash
set -e
echo "Starte Build-Prozess für MustafasSystem..."
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y debootstrap live-buildwaydroid curl wget
echo "Basis-System wird erstellt..."
# Konfiguration für live-build vorbereiten
lb config || true
lb build
echo "ISO erfolgreich erstellt!"
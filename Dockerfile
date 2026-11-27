FROM debian:trixie
RUN apt-get update && apt-get install -y \
    xfce4 \
    xfce4-goodies \
    network-manager \
    bluez \
    blueman \
    zram-tools \
    waydroid \
    weston \
    firefox-esr \
    firmware-linux \
    firmware-iwlwifi \
    firmware-realtek \
    && rm -rf /var/lib/apt/lists/*
CMD ["startxfce4"]
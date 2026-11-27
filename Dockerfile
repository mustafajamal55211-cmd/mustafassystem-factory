FROM debian:trixie
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    xfce4 xfce4-goodies network-manager bluez pulseaudio \
    firmware-linux firmware-iwlwifi firmware-realtek \
    waydroid zram-tools firefox-esr vlc compton && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
CMD ["startxfce4"]
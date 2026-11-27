FROM debian:trixie-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    xfce4 xfce4-goodies firefox-esr vlc zram-tools \
    firmware-linux firmware-iwlwifi bluez pulseaudio network-manager \
    && rm -rf /var/lib/apt/lists/*
CMD ["startxfce4"]
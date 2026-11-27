FROM debian:trixie
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    xfce4 xfce4-goodies waydroid network-manager bluez zram-tools firefox-esr \
    && rm -rf /var/lib/apt/lists/*
CMD ["startxfce4"]
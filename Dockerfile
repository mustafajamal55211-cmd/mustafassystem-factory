FROM debian:trixie
RUN apt-get update && apt-get install -y xfce4 xfce4-goodies waydroid firefox-esr vlc zram-tools
CMD ["startxfce4"]
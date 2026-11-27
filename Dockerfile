FROM debian:trixie
RUN apt-get update && apt-get install -y xfce4 waydroid zram-tools && rm -rf /var/lib/apt/lists/*
CMD ["startxfce4"]
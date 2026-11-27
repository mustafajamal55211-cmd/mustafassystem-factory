FROM debian:trixie-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y xfce4 waydroid zram-tools firefox-esr && apt-get clean
CMD ["startxfce4"]
FROM debian:trixie
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    live-build \
    debootstrap \
    squashfs-tools \
    xorriso \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY . /build/
CMD ["lb", "build"]
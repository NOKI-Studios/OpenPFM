FROM --platform=linux/amd64 ubuntu:24.04

RUN apt-get update && apt-get install -y \
    wget \
    libfuse2 \
    xvfb \
    libegl1 \
    libegl-mesa0 \
    libgl1-mesa-dri \
    libglx-mesa0 \
    libglib2.0-0 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libgtk-3-0 \
    libdbus-1-3 \
    libxcb1 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libgles2 \
    libopengl0 \
    libglu1-mesa \
    gstreamer1.0-plugins-base \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    libsoup-3.0-0 \
    libwebkit2gtk-4.1-0 \
    libjavascriptcoregtk-4.1-0 \
    libmspack0 \
    libsecret-1-0 \
    libwayland-server0 \
    && rm -rf /var/lib/apt/lists/*

ARG ORCA_VERSION=2.3.2
RUN wget -q \
    "https://github.com/OrcaSlicer/OrcaSlicer/releases/download/v${ORCA_VERSION}/OrcaSlicer_Linux_AppImage_Ubuntu2404_V${ORCA_VERSION}.AppImage" \
    -O /usr/local/bin/orcaslicer && \
    chmod +x /usr/local/bin/orcaslicer

ENV DISPLAY=:99
ENV LIBGL_ALWAYS_SOFTWARE=1
ENV APPIMAGE_EXTRACT_AND_RUN=1

VOLUME ["/data/profiles"]
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 & tail -f /dev/null"]
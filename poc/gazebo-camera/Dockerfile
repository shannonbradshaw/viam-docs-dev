# Gazebo Harmonic POC for Viam Camera Bridge
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
# Required for protobuf compatibility with gz-msgs
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

# Install Gazebo Harmonic
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    lsb-release \
    && curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null \
    && apt-get update \
    && apt-get install -y gz-harmonic \
    && rm -rf /var/lib/apt/lists/*

# Install xvfb for headless rendering (required for camera sensors)
RUN apt-get update && apt-get install -y \
    xvfb \
    mesa-utils \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Install Python and gz-transport bindings
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-gz-transport13 \
    python3-gz-msgs10 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for Viam module and web viewer
RUN pip3 install viam-sdk Pillow flask numpy

# Copy world files and models
COPY worlds/ /opt/worlds/
COPY models/ /opt/models/

# Set Gazebo resource path for custom models
ENV GZ_SIM_RESOURCE_PATH=/opt/models

# Copy Viam module
COPY viam-gazebo-camera/ /opt/viam/modules/viam-gazebo-camera/

# Copy web viewer
COPY web_viewer.py /opt/web_viewer.py

# Copy startup script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy Viam config
COPY viam-config.json /opt/viam-config.json

# Expose web viewer port
EXPOSE 8080

WORKDIR /opt

ENTRYPOINT ["/entrypoint.sh"]

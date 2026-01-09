# Gazebo Harmonic + GzWeb POC for Viam
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

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

# Install Python and gz-transport bindings
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-gz-transport13 \
    python3-gz-msgs10 \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for GzWeb
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install GzWeb dependencies
RUN apt-get update && apt-get install -y \
    git \
    libjansson-dev \
    libboost-dev \
    imagemagick \
    libtinyxml-dev \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Clone and build GzWeb
WORKDIR /opt
RUN git clone https://github.com/gazebo-web/gzweb.git
WORKDIR /opt/gzweb
RUN npm install

# Install Viam server
RUN curl -o /usr/local/bin/viam-server https://storage.googleapis.com/packages.viam.com/apps/viam-server/viam-server-stable-x86_64 \
    && chmod +x /usr/local/bin/viam-server

# Install Python dependencies for Viam module
RUN pip3 install viam-sdk Pillow

# Copy world files
COPY worlds/ /opt/worlds/

# Copy Viam module (will be mounted or copied in)
RUN mkdir -p /opt/viam/modules

# Copy startup script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose ports
# 8080 - GzWeb
# 8443 - Viam server (if needed)
EXPOSE 8080 8443

WORKDIR /opt

ENTRYPOINT ["/entrypoint.sh"]

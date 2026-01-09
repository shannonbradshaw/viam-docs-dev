# POC: Gazebo Camera to Viam Bridge

**Goal:** Validate that we can bridge a simulated Gazebo camera to Viam's camera API.

**Success criteria:**
- Python script gets camera frames via Viam SDK
- GzWeb shows the same scene in browser
- Latency is reasonable (<200ms)

---

## Quick Start

```bash
# 1. Build the Docker image
cd poc/gazebo-camera
docker build -t gazebo-viam-poc .

# 2. Run the container
docker run -it --rm -p 8080:8080 -p 8443:8443 gazebo-viam-poc

# 3. Open GzWeb in browser
open http://localhost:8080

# 4. In another terminal, test the camera topic
docker exec -it <container_id> gz topic -e -t /world/camera_world/model/camera_post/link/camera_link/sensor/camera/image
```

---

## Project Structure

```
docs-dev/poc/gazebo-camera/    # This directory
├── README.md                   # This file
├── Dockerfile                  # Container with Gazebo + GzWeb
├── entrypoint.sh              # Startup script
└── worlds/
    └── camera_world.sdf       # Gazebo world with camera

viam-gazebo-camera/            # Separate repo: /Users/shannon.bradshaw/viam/viam-gazebo-camera
├── main.py                    # Viam module
├── meta.json                  # Module metadata
├── requirements.txt           # Python dependencies
└── README.md                  # Module documentation
```

---

## Prerequisites

- Docker installed
- Python 3.10+
- Basic familiarity with Viam modules

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Docker Container                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │   gz-sim    │  │   gzweb     │  │  viam-server    │ │
│  │             │  │             │  │                 │ │
│  │ Camera topic│  │ Port 8080   │  │ + gazebo-camera │ │
│  │ gz.msgs.Image│ │ (browser)   │  │   module        │ │
│  └──────┬──────┘  └─────────────┘  └────────┬────────┘ │
│         │                                    │          │
│         └──────────► gz-transport ◄──────────┘          │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼ Port 8443
              ┌───────────────────────────┐
              │   Your laptop             │
              │   - Python + Viam SDK     │
              │   - Browser → GzWeb       │
              └───────────────────────────┘
```

---

## Step 1: Get Gazebo Harmonic Running in Docker

### Option A: Use OSRF official image

```bash
# Pull the Gazebo Harmonic image
docker pull osrf/gazebo:harmonic

# Run with GUI forwarding (for local testing)
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  osrf/gazebo:harmonic \
  gz sim shapes.sdf
```

### Option B: Build custom image with GzWeb

Create `Dockerfile`:

```dockerfile
FROM osrf/gazebo:harmonic

# Install dependencies for GzWeb
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    git \
    libjansson-dev \
    libboost-dev \
    imagemagick \
    libtinyxml-dev \
    mercurial \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Clone and build GzWeb (new version for Gazebo Sim)
WORKDIR /opt
RUN git clone https://github.com/gazebo-web/gzweb.git
WORKDIR /opt/gzweb
RUN npm install

# Install Python gz-transport bindings
RUN apt-get update && apt-get install -y \
    python3-gz-transport13 \
    python3-gz-msgs10 \
    && rm -rf /var/lib/apt/lists/*

# Copy our world file and models
COPY worlds/ /opt/worlds/
COPY models/ /opt/models/

# Expose ports
EXPOSE 8080 8443 11345

# Startup script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
```

Create `entrypoint.sh`:

```bash
#!/bin/bash

# Start Gazebo Sim in the background
gz sim /opt/worlds/camera_world.sdf &
GZ_PID=$!

# Wait for Gazebo to start
sleep 5

# Start GzWeb
cd /opt/gzweb
npm start &

# Keep container running
wait $GZ_PID
```

---

## Step 2: Create a Simple World with Camera

Create `worlds/camera_world.sdf`:

```xml
<?xml version="1.0" ?>
<sdf version="1.8">
  <world name="camera_world">

    <!-- Lighting -->
    <light type="directional" name="sun">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <direction>-0.5 0.1 -0.9</direction>
    </light>

    <!-- Ground plane -->
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <!-- Some objects to look at -->
    <model name="red_box">
      <pose>2 0 0.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>1 1 1</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>1 1 1</size></box>
          </geometry>
          <material>
            <ambient>1 0 0 1</ambient>
            <diffuse>1 0 0 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <model name="blue_sphere">
      <pose>2 2 0.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <sphere><radius>0.5</radius></sphere>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <sphere><radius>0.5</radius></sphere>
          </geometry>
          <material>
            <ambient>0 0 1 1</ambient>
            <diffuse>0 0 1 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <!-- Camera sensor -->
    <model name="camera_model">
      <static>true</static>
      <pose>0 0 1.5 0 0 0</pose>
      <link name="camera_link">
        <sensor name="camera" type="camera">
          <always_on>1</always_on>
          <update_rate>30</update_rate>
          <visualize>true</visualize>
          <topic>camera</topic>
          <camera>
            <horizontal_fov>1.047</horizontal_fov>
            <image>
              <width>640</width>
              <height>480</height>
              <format>R8G8B8</format>
            </image>
            <clip>
              <near>0.1</near>
              <far>100</far>
            </clip>
          </camera>
        </sensor>
      </link>
    </model>

  </world>
</sdf>
```

---

## Step 3: Write the Viam Gazebo Camera Module

This module subscribes to Gazebo's camera topic and exposes it as a Viam camera.

Create `viam-gazebo-camera/main.py`:

```python
#!/usr/bin/env python3
"""
Viam module that bridges a Gazebo camera to Viam's camera API.
"""

import asyncio
from threading import Lock
from typing import Optional, List, Dict, Any, Mapping, Tuple
from PIL import Image
import io

from viam.module.module import Module
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.resource.types import Model, ModelFamily
from viam.components.camera import Camera
from viam.proto.common import ResponseMetadata
from viam.media.video import ViamImage, CameraMimeType

# Gazebo transport bindings
from gz.transport13 import Node
from gz.msgs10.image_pb2 import Image as GzImage


class GazeboCamera(Camera):
    """A Viam camera that reads from a Gazebo simulation camera topic."""

    MODEL = Model(ModelFamily("viam-labs", "camera"), "gazebo")

    def __init__(self, name: str):
        super().__init__(name)
        self._node: Optional[Node] = None
        self._latest_image: Optional[bytes] = None
        self._image_lock = Lock()
        self._topic: str = "/camera"
        self._width: int = 640
        self._height: int = 480

    @classmethod
    def new(cls, config, dependencies):
        camera = cls(config.name)
        camera.reconfigure(config, dependencies)
        return camera

    def reconfigure(self, config, dependencies):
        """Configure the camera with Gazebo topic info."""
        attrs = config.attributes.fields

        if "topic" in attrs:
            self._topic = attrs["topic"].string_value
        if "width" in attrs:
            self._width = int(attrs["width"].number_value)
        if "height" in attrs:
            self._height = int(attrs["height"].number_value)

        # Set up Gazebo transport subscription
        self._setup_subscription()

    def _setup_subscription(self):
        """Subscribe to the Gazebo camera topic."""
        if self._node is not None:
            # Already subscribed
            return

        self._node = Node()

        def callback(msg: GzImage):
            """Called when a new image is received from Gazebo."""
            # Convert Gazebo image to bytes
            # Gazebo sends raw RGB data
            with self._image_lock:
                self._latest_image = msg.data
                self._width = msg.width
                self._height = msg.height

        # Subscribe to the camera topic
        subscribed = self._node.subscribe(GzImage, self._topic, callback)
        if not subscribed:
            raise Exception(f"Failed to subscribe to Gazebo topic: {self._topic}")

        print(f"Subscribed to Gazebo camera topic: {self._topic}")

    async def get_image(
        self,
        mime_type: str = "",
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> ViamImage:
        """Get the latest image from the Gazebo camera."""
        with self._image_lock:
            if self._latest_image is None:
                raise Exception("No image received from Gazebo yet")

            # Convert raw RGB bytes to PIL Image
            img = Image.frombytes("RGB", (self._width, self._height), self._latest_image)

            # Convert to JPEG
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG")
            jpeg_bytes = buffer.getvalue()

            return ViamImage(jpeg_bytes, CameraMimeType.JPEG)

    async def get_images(
        self,
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Tuple[List[ViamImage], ResponseMetadata]:
        """Get images from the camera."""
        img = await self.get_image(timeout=timeout)
        return [img], ResponseMetadata()

    async def get_point_cloud(
        self,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Tuple[bytes, str]:
        """Point cloud not supported for basic camera."""
        raise NotImplementedError("Point cloud not supported")

    async def get_properties(
        self,
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Camera.Properties:
        """Return camera properties."""
        return Camera.Properties(
            supports_pcd=False,
            intrinsic_parameters=None,
            distortion_parameters=None
        )


async def main():
    """Main entry point for the module."""
    # Register the camera model
    Registry.register_resource_creator(
        Camera.SUBTYPE,
        GazeboCamera.MODEL,
        ResourceCreatorRegistration(GazeboCamera.new)
    )

    # Create and start the module
    module = Module.from_args()
    module.add_model_from_registry(Camera.SUBTYPE, GazeboCamera.MODEL)
    await module.start()


if __name__ == "__main__":
    asyncio.run(main())
```

Create `viam-gazebo-camera/requirements.txt`:

```
viam-sdk>=0.20.0
Pillow>=10.0.0
# Note: gz-transport and gz-msgs are system packages, not pip
```

Create `viam-gazebo-camera/meta.json`:

```json
{
  "module_id": "viam-labs:gazebo-camera",
  "visibility": "private",
  "url": "",
  "description": "Viam camera module for Gazebo simulation",
  "models": [
    {
      "api": "rdk:component:camera",
      "model": "viam-labs:camera:gazebo"
    }
  ],
  "entrypoint": "main.py"
}
```

---

## Step 4: Viam Configuration

Create `viam-config.json` to test locally:

```json
{
  "modules": [
    {
      "name": "gazebo-camera",
      "executable_path": "/opt/viam/modules/viam-gazebo-camera/main.py",
      "type": "local"
    }
  ],
  "components": [
    {
      "name": "sim-camera",
      "api": "rdk:component:camera",
      "model": "viam-labs:camera:gazebo",
      "attributes": {
        "topic": "/world/camera_world/model/camera_model/link/camera_link/sensor/camera/image"
      }
    }
  ]
}
```

**Note:** The exact topic name depends on your world/model/sensor naming. Use `gz topic -l` inside the container to list available topics.

---

## Step 5: Test End-to-End

### Build and run the container

```bash
cd poc/gazebo-camera
docker build -t gazebo-viam-poc .
docker run -it --rm \
  -p 8080:8080 \
  -p 8443:8443 \
  gazebo-viam-poc
```

### Verify Gazebo is publishing camera images

```bash
# In another terminal, exec into the container
docker exec -it <container_id> bash

# List topics
gz topic -l

# Echo camera topic (should show image data)
gz topic -e -t /world/camera_world/model/camera_model/link/camera_link/sensor/camera/image
```

### Test with Python SDK

```python
#!/usr/bin/env python3
"""Test script to verify the Gazebo camera works through Viam."""

import asyncio
from viam.robot.client import RobotClient
from viam.components.camera import Camera


async def main():
    # Connect to local viam-server
    robot = await RobotClient.at_address(
        "localhost:8443",
        RobotClient.Options()
    )

    # Get the camera
    camera = Camera.from_robot(robot, "sim-camera")

    # Get an image
    image = await camera.get_image()

    # Save it
    with open("test_image.jpg", "wb") as f:
        f.write(image.data)

    print("Saved test_image.jpg")

    await robot.close()


if __name__ == "__main__":
    asyncio.run(main())
```

### View in browser

Open `http://localhost:8080` to see GzWeb visualization.

---

## Troubleshooting

### No topics listed
- Gazebo may not have started. Check logs: `docker logs <container_id>`

### Camera topic empty
- Verify the sensor is configured with `<always_on>1</always_on>`
- Check topic name matches your world file structure

### Module fails to subscribe
- Ensure `python3-gz-transport13` is installed in the container
- Topic name must exactly match (use `gz topic -l`)

### Image is black
- Add lighting to your world
- Check camera pose isn't inside an object

---

## Next Steps

Once this POC works:

1. **Add depth camera** — Similar pattern, different sensor type
2. **Add arm** — Subscribe to joint states, publish joint commands
3. **Add base** — Subscribe to odometry, publish velocity commands
4. **Package as Docker image** — Ready for cloud deployment
5. **Measure latency** — Instrument the pipeline

---

## References

- [Gazebo Transport Python API](https://gazebosim.org/api/transport/13/python.html)
- [Gazebo Harmonic Sensors](https://github.com/MOGI-ROS/Week-5-6-Gazebo-sensors)
- [Viam Module Development](https://docs.viam.com/registry/create/)
- [GzWeb (new)](https://github.com/gazebo-web/gzweb)

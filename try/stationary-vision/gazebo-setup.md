# Gazebo Camera Simulation Setup Guide

This guide walks you through setting up a simulated camera in Gazebo Harmonic and connecting it to the Viam platform using Docker.

## Prerequisites

- Docker Desktop installed and running
- A Viam account at [app.viam.com](https://app.viam.com)

## Step 1: Clone the Repository

```bash
git clone https://github.com/viam-devrel/docs-dev.git
cd docs-dev/poc/gazebo-camera
```

## Step 2: Build the Docker Image

```bash
docker build -t gz-harmonic-viam .
```

This takes several minutes as it installs Gazebo Harmonic and all dependencies.

## Step 3: Create a Machine in Viam

1. Go to [app.viam.com](https://app.viam.com)
2. Create a new machine (or use an existing one)
3. On the machine's **CONFIGURE** tab, click **View setup instructions**
4. Select **Linux / Aarch64** as the platform
5. Click **Copy** next to the viam-server config JSON
6. Save this JSON to a file on your computer, e.g., `~/viam-config.json`

The file should look like:
```json
{"cloud":{"app_address":"https://app.viam.com:443","id":"your-machine-id","secret":"your-secret"}}
```

## Step 4: Run the Container

```bash
docker run --name gz-viam -d -p 8080:8080 -p 8443:8443 -v ~/viam-config.json:/etc/viam.json gz-harmonic-viam
```

Replace `~/viam-config.json` with the actual path to your config file.

### Verify the container is running:

```bash
docker logs gz-viam
```

You should see:
- Gazebo starting up
- viam-server starting with your machine ID
- "POC Running!" message

## Step 5: Add the Camera Module

1. In the Viam app, go to your machine's **CONFIGURE** tab
2. Click the **+** button next to **Modules**
3. Search for `gz-camera` and select `viam:gz-camera`
4. Click **Add module**

## Step 6: Add a Camera Component

1. Click the **+** button next to **Components**
2. Select **Camera** then **Create**
3. Name it `sim-camera`
4. For **Model**, select `viam:gz-camera:rgb-camera`
5. In the **Attributes** section, add:
   ```json
   {
     "id": "/wrist_camera/image"
   }
   ```
6. Click **Save** in the top right

## Step 7: Test the Camera

1. Go to the **CONTROL** tab
2. Find the `sim-camera` component
3. Click to expand it - you should see a live image from the simulated camera

## Troubleshooting

### Container won't start

Check Docker logs:
```bash
docker logs gz-viam
```

### viam-server not running

Verify the config file was mounted correctly:
```bash
docker exec gz-viam cat /etc/viam.json
```

### "No image received" error

1. Verify Gazebo is running:
   ```bash
   docker exec gz-viam gz topic -l | grep image
   ```

2. Check that the camera topic matches your config:
   - Available topics: `/wrist_camera/image`, `/overhead_camera`

### Module crashes with "bus error"

This can happen with certain viam-server versions on ARM64. The provided Docker image uses `--appimage-extract-and-run` to avoid this issue. If you encounter it, ensure you're using the latest image.

## Available Camera Topics

The simulation includes these camera topics:

| Topic | Description |
|-------|-------------|
| `/wrist_camera/image` | RGB camera mounted on robot wrist |
| `/wrist_camera/depth_image` | Depth camera on robot wrist |
| `/overhead_camera` | Overhead view camera |

## Managing the Container

```bash
# View logs
docker logs gz-viam

# Shell into container
docker exec -it gz-viam bash

# Stop container
docker stop gz-viam

# Start container again
docker start gz-viam

# Remove container
docker rm gz-viam
```

## Running Multiple Instances

To run multiple containers, use different names and ports:

```bash
docker run --name gz-viam-2 -d -p 8081:8080 -p 8444:8443 -v ~/viam-config-2.json:/etc/viam.json gz-harmonic-viam
```

# Gazebo Can Inspection Simulation Setup Guide

> **Prerequisite for the [Stationary Vision Tutorial](./index.md).** Complete this setup, then continue to [Part 1](./part1.md).

This guide walks you through setting up a simulated can inspection station with camera in Gazebo Harmonic and connecting it to the Viam platform using Docker. The simulation includes a conveyor belt with cans (some dented) passing under an inspection camera.

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
docker run --name gz-viam -d -p 8080:8080 -p 8081:8081 -p 8443:8443 -v ~/viam-config.json:/etc/viam.json gz-harmonic-viam
```

Replace `~/viam-config.json` with the actual path to your config file.

### Verify the container is running:

```bash
docker logs gz-viam
```

You should see:
- Gazebo starting up
- viam-server starting with your machine ID
- "Can Inspection Simulation Running!" message
- Can spawner starting (spawns cans on conveyor belt)

## Step 5: View the Simulation

Open **http://localhost:8081** in your browser to see the simulation cameras.

You'll see two camera feeds:
- **Overview Camera** — An elevated view of the entire work cell showing cans moving along the conveyor belt
- **Inspection Camera** — The overhead view used for defect detection (this is the camera you'll configure in Viam)

[SCREENSHOT: Web viewer showing both camera feeds]

This view helps you understand what's happening in the simulation as you work through the tutorial. Keep this tab open alongside the Viam app.

---

**Next:** Return to **[Part 1: Vision Pipeline](./part1.md)** to configure your camera and build the inspection system.

---

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
   - Available topic: `/inspection_camera`

### Module crashes with "bus error"

This can happen with certain viam-server versions on ARM64. The provided Docker image uses `--appimage-extract-and-run` to avoid this issue. If you encounter it, ensure you're using the latest image.

## Available Camera Topics

The simulation includes these camera topics:

| Topic | Description |
|-------|-------------|
| `/overview_camera` | Elevated view of the entire work cell |
| `/inspection_camera` | Overhead RGB camera for defect detection (640x480) |

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
docker run --name gz-viam-2 -d -p 9080:8080 -p 9081:8081 -p 9443:8443 -v ~/viam-config-2.json:/etc/viam.json gz-harmonic-viam
```

The second instance's web viewer would be at http://localhost:9081.

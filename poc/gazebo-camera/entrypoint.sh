#!/bin/bash
set -e

echo "Starting Gazebo Sim..."
gz sim -s /opt/worlds/camera_world.sdf &
GZ_PID=$!

# Wait for Gazebo to initialize
sleep 5

echo "Checking Gazebo topics..."
gz topic -l

echo "Starting GzWeb..."
cd /opt/gzweb
npm start &
GZWEB_PID=$!

echo ""
echo "=========================================="
echo "POC Running!"
echo "=========================================="
echo "GzWeb UI:     http://localhost:8080"
echo "Camera topic: /world/camera_world/model/camera_post/link/camera_link/sensor/camera/image"
echo ""
echo "To test camera topic:"
echo "  gz topic -e -t /world/camera_world/model/camera_post/link/camera_link/sensor/camera/image"
echo "=========================================="
echo ""

# Keep container running
wait $GZ_PID

#!/bin/bash
set -e

# Export protobuf compatibility setting
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

# Start virtual display for headless rendering
echo "Starting Xvfb virtual display..."
Xvfb :1 -screen 0 1024x768x24 &
export DISPLAY=:1
sleep 2

echo "Starting Gazebo Sim with rendering..."
gz sim -s /opt/worlds/work_cell.sdf &
GZ_PID=$!

# Wait for Gazebo to initialize
echo "Waiting for Gazebo to initialize..."
sleep 10

echo ""
echo "Checking Gazebo topics..."
gz topic -l

# Unpause simulation
echo ""
echo "Unpausing simulation..."
gz service -s /world/work_cell/control --reqtype gz.msgs.WorldControl --reptype gz.msgs.Boolean --timeout 2000 --req 'pause: false'
sleep 1

# Set initial arm pose (ready to pick)
echo ""
echo "Setting arm to initial pose..."
# Joint positions: J1=0, J2=-0.6, J3=-1.2, J4=0, J5=-1.0, J6=0
gz topic -t "/model/xarm6/joint/joint1/0/cmd_pos" -m gz.msgs.Double -p "data: 0.0" 2>/dev/null || true
gz topic -t "/model/xarm6/joint/joint2/0/cmd_pos" -m gz.msgs.Double -p "data: -0.6" 2>/dev/null || true
gz topic -t "/model/xarm6/joint/joint3/0/cmd_pos" -m gz.msgs.Double -p "data: -1.2" 2>/dev/null || true
gz topic -t "/model/xarm6/joint/joint4/0/cmd_pos" -m gz.msgs.Double -p "data: 0.0" 2>/dev/null || true
gz topic -t "/model/xarm6/joint/joint5/0/cmd_pos" -m gz.msgs.Double -p "data: -1.0" 2>/dev/null || true
gz topic -t "/model/xarm6/joint/joint6/0/cmd_pos" -m gz.msgs.Double -p "data: 0.0" 2>/dev/null || true
sleep 2

# Start web viewer
echo ""
echo "Starting web viewer..."
python3 /opt/web_viewer.py &
VIEWER_PID=$!

echo ""
echo "=========================================="
echo "POC Running!"
echo "=========================================="
echo ""
echo "  Web Viewer:  http://localhost:8080"
echo ""
echo "  Camera topic: /camera"
echo ""
echo "=========================================="
echo ""

# Keep container running
wait $GZ_PID

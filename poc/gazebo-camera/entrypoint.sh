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
# Joint positions: J1=π (face table), J2=-0.6, J3=-1.2, J4=0, J5=-1.0, J6=0
gz topic -t "/model/xarm6/joint/joint1/0/cmd_pos" -m gz.msgs.Double -p "data: 3.14159" 2>/dev/null || true
gz topic -t "/model/xarm6/joint/joint2/0/cmd_pos" -m gz.msgs.Double -p "data: -0.6" 2>/dev/null || true
gz topic -t "/model/xarm6/joint/joint3/0/cmd_pos" -m gz.msgs.Double -p "data: -1.2" 2>/dev/null || true
gz topic -t "/model/xarm6/joint/joint4/0/cmd_pos" -m gz.msgs.Double -p "data: 0.0" 2>/dev/null || true
gz topic -t "/model/xarm6/joint/joint5/0/cmd_pos" -m gz.msgs.Double -p "data: -1.0" 2>/dev/null || true
gz topic -t "/model/xarm6/joint/joint6/0/cmd_pos" -m gz.msgs.Double -p "data: 0.0" 2>/dev/null || true
sleep 2

# Start viam-server if config exists, otherwise start web viewer
if [ -f /etc/viam.json ]; then
    echo ""
    echo "Starting viam-server..."
    /usr/local/bin/viam-server.AppImage --appimage-extract-and-run -config /etc/viam.json &
    VIAM_PID=$!
    echo "viam-server started with PID $VIAM_PID"
else
    echo ""
    echo "No /etc/viam.json found - starting web viewer instead"
    echo "To use viam-server, mount your config: -v /path/to/viam.json:/etc/viam.json"
    python3 /opt/web_viewer.py &
    VIEWER_PID=$!
fi

echo ""
echo "=========================================="
echo "POC Running!"
echo "=========================================="
echo ""
echo "  Camera topic: /wrist_camera/image"
echo ""
if [ -f /etc/viam.json ]; then
echo "  viam-server: running (use Viam app to view camera)"
else
echo "  Web Viewer:  http://localhost:8080"
fi
echo ""
echo "=========================================="
echo ""

# Keep container running
wait $GZ_PID

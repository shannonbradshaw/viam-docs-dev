#!/usr/bin/env python3
"""
Web viewer for Gazebo cameras.
Serves MJPEG streams for RGB and depth cameras.
"""

import io
import time
import threading
import struct
import numpy as np
from flask import Flask, Response, render_template_string

from gz.transport13 import Node
from gz.msgs10.image_pb2 import Image as GzImage
from PIL import Image

app = Flask(__name__)

# Camera streams - each has its own frame buffer
cameras = {
    "overhead": {
        "topic": "/overhead_camera",
        "frame": None,
        "lock": threading.Lock(),
        "label": "Overhead Camera (RGB)"
    },
    "wrist": {
        "topic": "/wrist_camera/image",
        "frame": None,
        "lock": threading.Lock(),
        "label": "Wrist Camera (RGB)"
    },
    "wrist_depth": {
        "topic": "/wrist_camera/depth_image",
        "frame": None,
        "lock": threading.Lock(),
        "label": "Wrist Camera (Depth)"
    }
}

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Gazebo Work Cell Viewer</title>
    <style>
        body {
            background: #1a1a1a;
            color: #fff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 20px;
        }
        h1 {
            text-align: center;
            margin-bottom: 5px;
            font-weight: 400;
        }
        .subtitle {
            text-align: center;
            color: #888;
            margin-bottom: 30px;
        }
        .camera-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        .camera-card {
            background: #252525;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .camera-header {
            padding: 12px 16px;
            background: #333;
            font-size: 14px;
            font-weight: 500;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .camera-header .topic {
            color: #888;
            font-family: monospace;
            font-size: 11px;
        }
        .camera-feed {
            position: relative;
            background: #000;
        }
        .camera-feed img {
            display: block;
            width: 100%;
            height: auto;
        }
        .camera-feed .no-signal {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #666;
            font-size: 14px;
        }
        .info-bar {
            max-width: 1400px;
            margin: 30px auto 0;
            padding: 15px 20px;
            background: #252525;
            border-radius: 8px;
            font-family: monospace;
            font-size: 12px;
            color: #888;
        }
        .info-bar h3 {
            margin: 0 0 10px 0;
            color: #fff;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <h1>Gazebo Work Cell</h1>
    <p class="subtitle">Simulated pick-and-place work cell with RGBD + wrist cameras</p>

    <div class="camera-grid">
        <div class="camera-card">
            <div class="camera-header">
                <span>Overhead Camera (RGB)</span>
                <span class="topic">/overhead_camera</span>
            </div>
            <div class="camera-feed">
                <img src="/stream/overhead" alt="Overhead RGB">
            </div>
        </div>

        <div class="camera-card">
            <div class="camera-header">
                <span>Wrist Camera (RGB)</span>
                <span class="topic">/wrist_camera/image</span>
            </div>
            <div class="camera-feed">
                <img src="/stream/wrist" alt="Wrist RGB">
            </div>
        </div>

        <div class="camera-card">
            <div class="camera-header">
                <span>Wrist Camera (Depth)</span>
                <span class="topic">/wrist_camera/depth_image</span>
            </div>
            <div class="camera-feed">
                <img src="/stream/wrist_depth" alt="Wrist Depth">
            </div>
        </div>
    </div>

    <div class="info-bar">
        <h3>Work Cell Components</h3>
        <p>• UFFactory xArm 6 (6-DOF, 700mm reach, 6kg payload)</p>
        <p>• Parallel gripper with wrist-mounted Intel RealSense D405</p>
        <p>• Overhead RGB camera for workspace monitoring</p>
        <p>• Pick targets: red cube, green cylinder, blue sphere</p>
        <p>• Safety barrier obstacle</p>
    </div>
</body>
</html>
"""


def make_rgb_callback(camera_key):
    """Create a callback for RGB camera topics."""
    def callback(msg: GzImage):
        try:
            # Convert raw RGB to PIL Image
            img = Image.frombytes("RGB", (msg.width, msg.height), msg.data)

            # Convert to JPEG
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=80)
            jpeg_bytes = buffer.getvalue()

            with cameras[camera_key]["lock"]:
                cameras[camera_key]["frame"] = jpeg_bytes
        except Exception as e:
            print(f"Error processing {camera_key} frame: {e}")
    return callback


def make_depth_callback(camera_key):
    """Create a callback for depth camera topics."""
    def callback(msg: GzImage):
        try:
            # Depth images come as 32-bit floats
            width, height = msg.width, msg.height

            # Parse float32 depth data
            depth_data = np.frombuffer(msg.data, dtype=np.float32).reshape(height, width)

            # Normalize to 0-255 for visualization
            # Clip to reasonable range (0.2m to 3m for overhead view)
            depth_clipped = np.clip(depth_data, 0.2, 3.0)
            depth_normalized = ((depth_clipped - 0.2) / 2.8 * 255).astype(np.uint8)

            # Apply colormap (closer = warmer colors)
            depth_colored = np.zeros((height, width, 3), dtype=np.uint8)
            # Simple heat map: close=red, far=blue
            depth_colored[:, :, 0] = 255 - depth_normalized  # Red channel
            depth_colored[:, :, 2] = depth_normalized  # Blue channel

            img = Image.fromarray(depth_colored)

            # Convert to JPEG
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=80)
            jpeg_bytes = buffer.getvalue()

            with cameras[camera_key]["lock"]:
                cameras[camera_key]["frame"] = jpeg_bytes
        except Exception as e:
            print(f"Error processing depth frame: {e}")
    return callback


def generate_stream(camera_key):
    """Generator that yields MJPEG frames for a specific camera."""
    while True:
        with cameras[camera_key]["lock"]:
            frame = cameras[camera_key]["frame"]

        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        time.sleep(0.033)  # ~30fps


@app.route('/')
def index():
    return render_template_string(HTML_PAGE)


@app.route('/stream/<camera>')
def stream(camera):
    if camera not in cameras:
        return "Camera not found", 404
    return Response(
        generate_stream(camera),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/snapshot/<camera>')
def snapshot(camera):
    if camera not in cameras:
        return "Camera not found", 404
    with cameras[camera]["lock"]:
        frame = cameras[camera]["frame"]
    if frame is None:
        return "No frame available", 503
    return Response(frame, mimetype='image/jpeg')


def main():
    node = Node()

    print("Subscribing to camera topics...")

    # Overhead RGB
    success = node.subscribe(GzImage, "/overhead_camera", make_rgb_callback("overhead"))
    print(f"  /overhead_camera: {'OK' if success else 'FAILED'}")

    # Wrist RGB
    success = node.subscribe(GzImage, "/wrist_camera/image", make_rgb_callback("wrist"))
    print(f"  /wrist_camera/image: {'OK' if success else 'FAILED'}")

    # Wrist Depth
    success = node.subscribe(GzImage, "/wrist_camera/depth_image", make_depth_callback("wrist_depth"))
    print(f"  /wrist_camera/depth_image: {'OK' if success else 'FAILED'}")

    print(f"\nStarting web server on http://0.0.0.0:8080")
    app.run(host='0.0.0.0', port=8080, threaded=True)


if __name__ == "__main__":
    main()

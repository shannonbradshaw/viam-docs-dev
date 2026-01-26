#!/usr/bin/env python3
"""
Capture Training Data for Can Quality Classifier

Spawns cans in a controlled manner under the inspection camera,
captures labeled images, and uploads them to Viam for ML training.

Usage:
  # Set credentials
  export VIAM_API_KEY="your-key"
  export VIAM_API_KEY_ID="your-key-id"
  export VIAM_ORG_ID="your-org-id"
  export VIAM_LOCATION_ID="your-location-id"

  # Run capture and upload
  python capture_training_data.py

  # Capture only (no upload)
  python capture_training_data.py --no-upload

  # Upload existing images only
  python capture_training_data.py --upload-only

Requirements:
  pip install viam-sdk Pillow
  (gz-transport13 and gz-msgs10 come from Gazebo installation)
"""

import argparse
import asyncio
import io
import os
import random
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Viam SDK imports
try:
    from viam.app.viam_client import ViamClient
    from viam.rpc.dial import DialOptions, Credentials
    VIAM_SDK_AVAILABLE = True
except ImportError:
    VIAM_SDK_AVAILABLE = False
    print("Warning: viam-sdk not installed. Upload will be disabled.")

# PIL for image handling
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: Pillow not installed. Install with: pip install Pillow")

# Gazebo transport imports
try:
    from gz.transport13 import Node
    from gz.msgs10.image_pb2 import Image as GzImage
    from gz.msgs10.pose_pb2 import Pose
    from gz.msgs10.boolean_pb2 import Boolean
    GZ_AVAILABLE = True
except ImportError:
    GZ_AVAILABLE = False
    print("Warning: gz-transport not available. Run inside Gazebo container.")


# Configuration
CAMERA_TOPIC = "/inspection_camera"
CAMERA_X = 0.0  # X position of inspection camera
CAMERA_Y = 0.0  # Y position (center of belt)
CAN_Z = 0.54    # Z position on belt surface
SAMPLES_PER_CLASS = 50
OUTPUT_DIR = Path(__file__).parent / "training_data"


def log(msg: str):
    """Print with timestamp."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def run_gz_command(cmd: list, timeout: int = 5) -> tuple[bool, str, str]:
    """Run a gz command and return (success, stdout, stderr)."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)


def spawn_can(name: str, dented: bool, y_offset: float = 0.0, rotation: float = 0.0) -> bool:
    """Spawn a can at the camera position."""
    model_type = "can_dented" if dented else "can_good"

    # Spawn directly under camera
    req = (
        f'sdf_filename: "model://{model_type}", '
        f'name: "{name}", '
        f'pose: {{position: {{x: {CAMERA_X}, y: {CAMERA_Y + y_offset}, z: {CAN_Z}}}, '
        f'orientation: {{z: {rotation}}}}}'
    )

    cmd = [
        "gz", "service", "-s", "/world/cylinder_inspection/create",
        "--reqtype", "gz.msgs.EntityFactory",
        "--reptype", "gz.msgs.Boolean",
        "--timeout", "2000",
        "--req", req
    ]

    success, stdout, stderr = run_gz_command(cmd)
    return success and "true" in stdout.lower()


def delete_can(name: str) -> bool:
    """Delete a can from the simulation."""
    cmd = [
        "gz", "service", "-s", "/world/cylinder_inspection/remove",
        "--reqtype", "gz.msgs.Entity",
        "--reptype", "gz.msgs.Boolean",
        "--timeout", "1000",
        "--req", f'name: "{name}", type: 2'
    ]

    success, _, _ = run_gz_command(cmd)
    return success


class ImageCapture:
    """Captures images from Gazebo camera topic."""

    def __init__(self):
        self.node = Node()
        self.latest_image = None
        self.image_received = False

    def _on_image(self, msg: GzImage):
        """Callback for camera images."""
        self.latest_image = msg
        self.image_received = True

    def subscribe(self):
        """Subscribe to the camera topic."""
        success = self.node.subscribe(GzImage, CAMERA_TOPIC, self._on_image)
        if not success:
            raise RuntimeError(f"Failed to subscribe to {CAMERA_TOPIC}")
        log(f"Subscribed to {CAMERA_TOPIC}")

    def wait_for_image(self, timeout: float = 2.0) -> bytes | None:
        """Wait for a new image and return it as JPEG bytes."""
        self.image_received = False
        start = time.time()

        while not self.image_received and (time.time() - start) < timeout:
            time.sleep(0.05)

        if not self.image_received or self.latest_image is None:
            return None

        return self._convert_to_jpeg(self.latest_image)

    def _convert_to_jpeg(self, gz_image: GzImage) -> bytes | None:
        """Convert Gazebo image message to JPEG bytes."""
        if not PIL_AVAILABLE:
            return None

        try:
            width = gz_image.width
            height = gz_image.height
            data = gz_image.data

            # Handle different pixel formats
            pixel_format = gz_image.pixel_format_type

            # RGB8 format (most common)
            if len(data) == width * height * 3:
                img = Image.frombytes('RGB', (width, height), data)
            # RGBA format
            elif len(data) == width * height * 4:
                img = Image.frombytes('RGBA', (width, height), data)
                img = img.convert('RGB')
            else:
                log(f"Unknown image format: {len(data)} bytes for {width}x{height}")
                return None

            # Convert to JPEG
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=90)
            return buffer.getvalue()

        except Exception as e:
            log(f"Image conversion error: {e}")
            return None


def capture_images(output_dir: Path, samples_per_class: int) -> dict[str, list[Path]]:
    """Capture labeled images from the simulation."""

    if not GZ_AVAILABLE:
        raise RuntimeError("Gazebo transport not available. Run inside the container.")

    # Create output directories
    pass_dir = output_dir / "PASS"
    fail_dir = output_dir / "FAIL"
    pass_dir.mkdir(parents=True, exist_ok=True)
    fail_dir.mkdir(parents=True, exist_ok=True)

    # Initialize image capture
    capture = ImageCapture()
    capture.subscribe()

    # Wait for camera to start publishing
    log("Waiting for camera...")
    time.sleep(1.0)

    captured = {"PASS": [], "FAIL": []}

    for class_name, is_dented, out_dir in [("PASS", False, pass_dir), ("FAIL", True, fail_dir)]:
        log(f"\nCapturing {samples_per_class} {class_name} samples...")

        for i in range(samples_per_class):
            can_name = f"capture_can_{class_name}_{i:03d}"

            # Add variation
            y_offset = random.uniform(-0.03, 0.03)
            rotation = random.uniform(0, 6.28)  # 0 to 2*pi

            # Spawn can
            if not spawn_can(can_name, dented=is_dented, y_offset=y_offset, rotation=rotation):
                log(f"  Failed to spawn {can_name}, skipping")
                continue

            # Wait for rendering
            time.sleep(0.15)

            # Capture image
            image_data = capture.wait_for_image(timeout=2.0)

            if image_data:
                # Save locally
                filename = f"can_{i:03d}.jpg"
                filepath = out_dir / filename
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                captured[class_name].append(filepath)

                if (i + 1) % 10 == 0:
                    log(f"  Captured {i + 1}/{samples_per_class}")
            else:
                log(f"  Failed to capture image for {can_name}")

            # Delete can
            delete_can(can_name)
            time.sleep(0.05)

    log(f"\nCapture complete: {len(captured['PASS'])} PASS, {len(captured['FAIL'])} FAIL")
    return captured


async def upload_to_viam(captured: dict[str, list[Path]]):
    """Upload captured images to Viam with labels."""

    if not VIAM_SDK_AVAILABLE:
        raise RuntimeError("viam-sdk not installed. Install with: pip install viam-sdk")

    # Get credentials from environment
    api_key = os.environ.get("VIAM_API_KEY")
    api_key_id = os.environ.get("VIAM_API_KEY_ID")
    org_id = os.environ.get("VIAM_ORG_ID")
    location_id = os.environ.get("VIAM_LOCATION_ID")

    if not all([api_key, api_key_id]):
        raise RuntimeError(
            "Missing credentials. Set VIAM_API_KEY and VIAM_API_KEY_ID environment variables.\n"
            "Create an API key at: app.viam.com → Organization → Settings → API Keys"
        )

    if not all([org_id, location_id]):
        raise RuntimeError(
            "Missing org/location. Set VIAM_ORG_ID and VIAM_LOCATION_ID environment variables.\n"
            "Find these in the Viam app URL or Organization settings."
        )

    log("Connecting to Viam...")

    # Connect to Viam
    dial_options = DialOptions(
        credentials=Credentials(type="api-key", payload=api_key),
        auth_entity=api_key_id
    )

    client = await ViamClient.create_from_dial_options(dial_options)
    data_client = client.data_client

    log("Connected to Viam. Uploading images...")

    total_uploaded = 0

    for label, filepaths in captured.items():
        log(f"\nUploading {len(filepaths)} {label} images...")

        for i, filepath in enumerate(filepaths):
            try:
                # Read image data
                with open(filepath, 'rb') as f:
                    image_data = f.read()

                # Upload with label tag
                # Using file_upload for binary data
                await data_client.file_upload(
                    part_id=None,  # Will use org-level upload
                    data=image_data,
                    component_type="camera",
                    component_name="training-capture",
                    file_name=filepath.name,
                    file_extension=".jpg",
                    tags=[label, "can-quality-training"],
                )

                total_uploaded += 1

                if (i + 1) % 10 == 0:
                    log(f"  Uploaded {i + 1}/{len(filepaths)}")

            except Exception as e:
                log(f"  Failed to upload {filepath.name}: {e}")

    log(f"\nUpload complete: {total_uploaded} images uploaded")
    log("Next steps:")
    log("  1. Go to app.viam.com → Data")
    log("  2. Filter by tag 'can-quality-training'")
    log("  3. Create a dataset from this data")
    log("  4. Train a classifier model")

    await client.close()


async def upload_existing(output_dir: Path):
    """Upload existing images from output directory."""
    captured = {"PASS": [], "FAIL": []}

    for label in ["PASS", "FAIL"]:
        label_dir = output_dir / label
        if label_dir.exists():
            captured[label] = list(label_dir.glob("*.jpg"))

    if not any(captured.values()):
        raise RuntimeError(f"No images found in {output_dir}")

    log(f"Found {len(captured['PASS'])} PASS and {len(captured['FAIL'])} FAIL images")
    await upload_to_viam(captured)


async def main():
    parser = argparse.ArgumentParser(description="Capture training data for can classifier")
    parser.add_argument("--no-upload", action="store_true", help="Capture only, don't upload")
    parser.add_argument("--upload-only", action="store_true", help="Upload existing images only")
    parser.add_argument("--samples", type=int, default=SAMPLES_PER_CLASS,
                        help=f"Samples per class (default: {SAMPLES_PER_CLASS})")
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR,
                        help=f"Output directory (default: {OUTPUT_DIR})")
    args = parser.parse_args()

    log("=" * 50)
    log("Can Quality Training Data Capture")
    log("=" * 50)

    if args.upload_only:
        log("Uploading existing images...")
        await upload_existing(args.output)
    else:
        log(f"Capturing {args.samples} samples per class...")
        captured = capture_images(args.output, args.samples)

        if not args.no_upload:
            await upload_to_viam(captured)
        else:
            log("\nImages saved locally. To upload later:")
            log(f"  python {__file__} --upload-only")


if __name__ == "__main__":
    asyncio.run(main())

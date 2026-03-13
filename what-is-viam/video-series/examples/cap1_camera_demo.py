"""Capability 1 demo: camera API abstraction.

Run this script before and after swapping the camera hardware.
Same code, different camera, same results.

Set these environment variables before running:
    export VIAM_ADDRESS="your-robot-address"
    export VIAM_API_KEY="your-api-key"
    export VIAM_API_KEY_ID="your-api-key-id"
"""

import asyncio
import os

from dotenv import load_dotenv
import numpy as np
import open3d as o3d
from PIL import Image
from viam.robot.client import RobotClient
from viam.components.camera import Camera

load_dotenv()


async def main():
    robot = await RobotClient.at_address(
        os.environ["VIAM_ADDRESS"],
        RobotClient.Options.with_api_key(
            api_key=os.environ["VIAM_API_KEY"],
            api_key_id=os.environ["VIAM_API_KEY_ID"],
        ),
    )

    camera = Camera.from_robot(robot, "cam")

    # Get a 2D image
    images, _ = await camera.get_images()
    image = images[0]
    with open("output.jpg", "wb") as f:
        f.write(image.data)
    print(f"Saved image: {image.width}x{image.height}")

    # Get a 3D point cloud
    pcd_bytes, _ = await camera.get_point_cloud()
    with open("output.pcd", "wb") as f:
        f.write(pcd_bytes)
    print(f"Saved point cloud: {len(pcd_bytes)} bytes")

    # Show the 2D image
    pil_image = Image.open("output.jpg")
    pil_image.show()

    # Flip point cloud so Z is up (camera convention is Z-down)
    pcd = o3d.io.read_point_cloud("output.pcd")
    flip = np.array([[1, 0, 0, 0],
                     [0, -1, 0, 0],
                     [0, 0, -1, 0],
                     [0, 0, 0, 1]])
    pcd.transform(flip)

    # Visualize the point cloud, zoomed to fit
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(pcd)
    vis.get_view_control().set_zoom(0.5)
    vis.reset_view_point(True)
    vis.run()
    vis.destroy_window()

    await robot.close()


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Can Spawner for Conveyor Belt Simulation

Continuously spawns cans at the input end of the conveyor belt.
Moves kinematic cans along the belt using position updates.
Removes cans when they reach the output end.

About 50% of cans are dented (defective).

Uses gz-transport Python bindings for efficient pose updates.
Includes backoff/recovery logic when Gazebo becomes overloaded.
"""

import time
import random
import subprocess
import threading

from gz.transport13 import Node
from gz.msgs10.pose_pb2 import Pose
from gz.msgs10.boolean_pb2 import Boolean
from gz.msgs10.entity_pb2 import Entity
from gz.msgs10.entity_factory_pb2 import EntityFactory

# Configuration
SPAWN_INTERVAL = 2.0  # seconds between spawns
SPAWN_X = -0.92  # X position where cans spawn (input end)
DELETE_X = 1.00  # X position where cans are deleted (output end)
BELT_Y = 0.0  # Y position (center of belt)
BELT_Z = 0.60  # Z position (slightly above belt to drop)
DENT_PROBABILITY = 0.5  # 50% chance of dented can
CHECK_INTERVAL = 0.033  # seconds between position updates (~30Hz, matches camera)
BELT_SPEED = 0.06  # meters per second (slow, smooth movement)

# Error tracking for backoff/recovery
ERROR_THRESHOLD = 5  # consecutive failures before pausing spawns
MAX_CANS = 20  # maximum cans on belt at once (safety limit)

# Track spawned cans
cans = {}  # name -> {'dented': bool, 'spawn_time': float, 'y_offset': float}
can_counter = 0
lock = threading.Lock()

# Error tracking (shared between threads)
consecutive_errors = 0
spawning_paused = False
error_lock = threading.Lock()

# gz-transport node (initialized in main)
node = None


def log(msg):
    """Print with flush for immediate output."""
    print(msg, flush=True)


def run_gz_command(cmd, timeout=5):
    """Run a gz command and return success status (fallback for spawn/delete)."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)


def spawn_can(name: str, dented: bool, y_offset: float):
    """Spawn a can at the input end of the conveyor."""
    model_type = "can_dented" if dented else "can_good"

    req = f'sdf_filename: "model://{model_type}", name: "{name}", pose: {{position: {{x: {SPAWN_X}, y: {BELT_Y + y_offset}, z: {BELT_Z}}}}}'

    cmd = [
        "gz", "service", "-s", "/world/cylinder_inspection/create",
        "--reqtype", "gz.msgs.EntityFactory",
        "--reptype", "gz.msgs.Boolean",
        "--timeout", "2000",
        "--req", req
    ]

    success, stdout, stderr = run_gz_command(cmd)
    if success and "true" in stdout.lower():
        log(f"Spawned {name} ({'DENTED' if dented else 'good'})")
        return True
    else:
        log(f"Failed to spawn {name}: {stderr}")
        return False


def delete_can(name: str):
    """Delete a can from the simulation."""
    cmd = [
        "gz", "service", "-s", "/world/cylinder_inspection/remove",
        "--reqtype", "gz.msgs.Entity",
        "--reptype", "gz.msgs.Boolean",
        "--timeout", "1000",
        "--req", f'name: "{name}", type: 2'
    ]

    success, _, _ = run_gz_command(cmd)
    if success:
        log(f"Deleted {name}")
        return True
    return False


def set_can_position(name: str, x: float, y_offset: float):
    """Set the can position using gz-transport (much faster than subprocess)."""
    global node, consecutive_errors, spawning_paused

    z = 0.54  # Height on belt

    # Create pose message
    pose = Pose()
    pose.name = name
    pose.position.x = x
    pose.position.y = BELT_Y + y_offset
    pose.position.z = z

    # Call service with correct signature: (service, request, request_type, response_type, timeout)
    try:
        success, response = node.request(
            "/world/cylinder_inspection/set_pose",
            pose,
            Pose,
            Boolean,
            100  # timeout in ms
        )

        with error_lock:
            if success:
                # Reset error count on success
                if consecutive_errors > 0:
                    consecutive_errors = 0
                    if spawning_paused:
                        spawning_paused = False
                        log("Gazebo recovered - resuming spawning")
            else:
                consecutive_errors += 1
                if consecutive_errors >= ERROR_THRESHOLD and not spawning_paused:
                    spawning_paused = True
                    log(f"Too many errors ({consecutive_errors}) - pausing spawning")

        return success
    except Exception as e:
        with error_lock:
            consecutive_errors += 1
            if consecutive_errors >= ERROR_THRESHOLD and not spawning_paused:
                spawning_paused = True
                log(f"Too many errors ({consecutive_errors}) - pausing spawning")
        return False


def can_manager():
    """Thread that manages cans - moves them along belt and removes old ones."""
    global cans

    # Stale can timeout (if a can is tracked for way too long, remove it)
    STALE_TIMEOUT = 120.0  # 2 minutes max

    while True:
        current_time = time.time()

        with lock:
            to_delete = []

            for name, data in list(cans.items()):
                elapsed_since_spawn = current_time - data['spawn_time']

                # Safety: remove stale cans from tracking (even if delete fails)
                if elapsed_since_spawn > STALE_TIMEOUT:
                    log(f"Removing stale can {name} from tracking")
                    to_delete.append(name)
                    continue

                # Calculate position based on time since spawn (absolute, not incremental)
                x_pos = SPAWN_X + (BELT_SPEED * elapsed_since_spawn)
                set_can_position(name, x_pos, data['y_offset'])

                # Check if reached end
                if x_pos > DELETE_X:
                    to_delete.append(name)

            # Delete cans that reached the end
            for name in to_delete:
                delete_can(name)  # Try to delete from Gazebo
                del cans[name]   # Always remove from tracking

        time.sleep(CHECK_INTERVAL)


def spawner():
    """Thread that spawns new cans periodically."""
    global can_counter, cans, spawning_paused

    while True:
        # Check if spawning is paused due to errors
        with error_lock:
            paused = spawning_paused

        # Check if we've hit the max can limit
        with lock:
            can_count = len(cans)

        if paused:
            # Still paused - wait and check again
            time.sleep(SPAWN_INTERVAL)
            continue

        if can_count >= MAX_CANS:
            # Too many cans on belt - wait for some to clear
            time.sleep(SPAWN_INTERVAL)
            continue

        # Determine if this can is dented
        dented = random.random() < DENT_PROBABILITY

        # Generate unique name
        can_counter += 1
        name = f"can_{can_counter:04d}"

        # Random slight Y offset for variety
        y_offset = random.uniform(-0.03, 0.03)

        # Spawn the can
        if spawn_can(name, dented, y_offset):
            with lock:
                cans[name] = {
                    'dented': dented,
                    'spawn_time': time.time(),
                    'y_offset': y_offset
                }

        time.sleep(SPAWN_INTERVAL)


def main():
    """Main entry point."""
    global node

    log("=" * 50)
    log("Can Spawner Starting")
    log("=" * 50)
    log(f"  Spawn interval: {SPAWN_INTERVAL}s")
    log(f"  Belt speed: {BELT_SPEED} m/s")
    log(f"  Dent probability: {DENT_PROBABILITY * 100}%")
    log("=" * 50)

    # Wait for Gazebo to be ready
    log("Waiting for Gazebo...")
    time.sleep(5)

    # Initialize gz-transport node
    log("Initializing gz-transport...")
    node = Node()

    # Start can manager thread (moves cans and deletes at end)
    manager_thread = threading.Thread(target=can_manager, daemon=True)
    manager_thread.start()
    log("Can manager started")

    # Start spawner thread
    spawner_thread = threading.Thread(target=spawner, daemon=True)
    spawner_thread.start()
    log("Spawner started")

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("\nShutting down...")


if __name__ == "__main__":
    main()

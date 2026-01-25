#!/usr/bin/env python3
"""
Can Spawner for Conveyor Belt Simulation

Continuously spawns cans at the input end of the conveyor belt.
Moves kinematic cans along the belt using position updates.
Removes cans when they reach the output end.

About 1 in 10 cans are dented (defective).
"""

import time
import random
import subprocess
import threading

# Configuration
SPAWN_INTERVAL = 4.0  # seconds between spawns
SPAWN_X = -0.42  # X position where cans spawn (input end)
DELETE_X = 0.50  # X position where cans are deleted (output end)
BELT_Y = 0.0  # Y position (center of belt)
BELT_Z = 0.60  # Z position (slightly above belt to drop)
DENT_PROBABILITY = 0.1  # 10% chance of dented can
CHECK_INTERVAL = 0.3  # seconds between position updates
BELT_SPEED = 0.18  # meters per second (approx 5 seconds to cross belt)

# Track spawned cans
cans = {}  # name -> {'dented': bool, 'x_pos': float, 'y_offset': float}
can_counter = 0
lock = threading.Lock()


def log(msg):
    """Print with flush for immediate output."""
    print(msg, flush=True)


def run_gz_command(cmd, timeout=5):
    """Run a gz command and return success status."""
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


def get_can_position(name: str):
    """Get the current X position of a can."""
    cmd = ["gz", "model", "-m", name, "-p"]
    success, stdout, _ = run_gz_command(cmd, timeout=2)

    if success and "XYZ" in stdout:
        # Parse position from output
        # Format: [x y z]
        try:
            lines = stdout.split('\n')
            for i, line in enumerate(lines):
                if 'XYZ' in line:
                    # Next line has the position
                    pos_line = lines[i + 1].strip()
                    # Parse [x y z]
                    pos_line = pos_line.strip('[]')
                    parts = pos_line.split()
                    if len(parts) >= 3:
                        return float(parts[0])
        except:
            pass
    return None


def set_can_position(name: str, x: float, y_offset: float):
    """Set the can position directly (works because cans are kinematic)."""
    z = 0.54  # Height on belt
    cmd = [
        "gz", "service", "-s", "/world/cylinder_inspection/set_pose/blocking",
        "--reqtype", "gz.msgs.Pose",
        "--reptype", "gz.msgs.Boolean",
        "--timeout", "200",
        "--req", f'name: "{name}", position: {{x: {x}, y: {BELT_Y + y_offset}, z: {z}}}'
    ]
    run_gz_command(cmd, timeout=0.5)


def can_manager():
    """Thread that manages cans - moves them along belt and removes old ones."""
    global cans

    while True:
        with lock:
            to_delete = []

            for name, data in list(cans.items()):
                # Move can forward
                data['x_pos'] += BELT_SPEED * CHECK_INTERVAL
                set_can_position(name, data['x_pos'], data['y_offset'])

                # Check if reached end
                if data['x_pos'] > DELETE_X:
                    to_delete.append(name)

            # Delete cans that reached the end
            for name in to_delete:
                if delete_can(name):
                    del cans[name]

        time.sleep(CHECK_INTERVAL)


def spawner():
    """Thread that spawns new cans periodically."""
    global can_counter, cans

    while True:
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
                    'x_pos': SPAWN_X,
                    'y_offset': y_offset
                }

        time.sleep(SPAWN_INTERVAL)


def main():
    """Main entry point."""
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

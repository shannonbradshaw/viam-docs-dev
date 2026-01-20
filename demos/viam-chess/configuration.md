# Configuration Deep-Dive

[← Back to Overview](./index.md) | [← Code Walkthrough](./code.md) | [Next: Development Workflow →](./development.md)

---

This page explains every configuration block in viam-chess—what it does and why.

## Configuration Structure

A Viam machine config has these top-level sections:

```json
{
  "components": [...],      // Hardware and virtual components
  "services": [...],        // Higher-level capabilities
  "modules": [...],         // Custom code packages
  "packages": [...],        // ML models, data files
  "fragments": [...],       // Reusable config templates
  "fragment_mods": [...]    // Per-machine overrides to fragments
}
```

viam-chess uses all of these.

---

## Fragment: Hardware Layer

The `xarm6-realsense` fragment defines the physical hardware. See [xarm6-realsense-fragment.json](./xarm6-realsense-fragment.json).

### The Arm

```json
{
  "name": "arm",
  "api": "rdk:component:arm",
  "model": "viam:ufactory:xArm6",
  "attributes": {
    "speed_degs_per_sec": 60,
    "collision_sensitivity": 0,
    "host": {
      "$variable": {
        "name": "arm-ip-address"
      }
    }
  },
  "frame": {
    "parent": "world",
    "translation": { "$variable": { "name": "translation", "default_value": {"x": 0, "y": 0, "z": 0} } },
    "orientation": {
      "type": "ov_degrees",
      "value": { "x": 0, "y": 0, "z": 1, "th": { "$variable": { "name": "base-axis-rotation-degrees", "default_value": 0 } } }
    }
  }
}
```

**Key points:**

| Field | Purpose |
|-------|---------|
| `api: rdk:component:arm` | This component implements the Arm API |
| `model: viam:ufactory:xArm6` | Use the xArm6 driver from the ufactory module |
| `host: $variable` | IP address comes from fragment variables (machine-specific) |
| `frame.parent: world` | Arm base is the world origin |
| `frame.translation/orientation` | Allow per-machine adjustment via variables |

**Why variables?** Different machines have:
- Different arm IP addresses
- Potentially different mounting positions/rotations

Variables let the fragment stay generic while machines provide specifics.

### The Camera

```json
{
  "name": "cam",
  "api": "rdk:component:camera",
  "model": "viam:camera:realsense",
  "attributes": {
    "width_px": 1280,
    "height_px": 720,
    "sensors": ["color", "depth"],
    "serial_number": { "$variable": { "name": "cam-serial-number" } }
  },
  "frame": {
    "parent": { "$variable": { "name": "arm-name" } },
    "translation": { "x": 83.226436, "y": -30.461049, "z": 18.507235 },
    "orientation": { "type": "ov_degrees", "value": { "x": -0.030391, "y": -0.003538, "z": 0.999532, "th": -97.731173 } }
  }
}
```

**Key points:**

| Field | Purpose |
|-------|---------|
| `sensors: ["color", "depth"]` | Enable both RGB and depth streams |
| `serial_number: $variable` | Different cameras have different serial numbers |
| `frame.parent: $variable` | Camera is attached to the arm (moves with it) |
| `frame.translation/orientation` | Precisely calibrated offset from arm end to camera sensor |

**The frame relationship is critical:** When the arm moves, the camera's world position updates automatically. The frame system handles all coordinate transforms.

### The Gripper

```json
{
  "name": "gripper",
  "api": "rdk:component:gripper",
  "model": "viam:ufactory:gripper",
  "attributes": {
    "arm": { "$variable": { "name": "arm-name" } }
  },
  "frame": {
    "parent": { "$variable": { "name": "arm-name" } },
    "translation": { "x": 0, "y": 0, "z": 150 },
    "orientation": { "type": "quaternion", "value": { "x": 0, "y": 0, "z": 0, "w": 1 } }
  }
}
```

**Key points:**
- `attributes.arm` — Gripper needs to know which arm it's attached to (for control)
- `frame.translation.z: 150` — Gripper extends 150mm from arm flange
- Motion service uses this to position the gripper tip, not the arm flange

### Fragment Modules

```json
"modules": [
  { "type": "registry", "module_id": "viam:ufactory", "version": "latest" },
  { "type": "registry", "module_id": "viam:realsense", "version": "latest" }
]
```

The fragment also declares which modules provide its models. When you apply this fragment, these modules are automatically installed.

---

## Machine Config: Application Layer

See [machine-config.json](./machine-config.json).

### Using the Fragment

```json
"fragments": [
  {
    "id": "f6e98d80-20a0-4fb6-9cb3-7b527a91ec10",
    "variables": {
      "arm-name": "arm",
      "arm-ip-address": "10.1.1.50",
      "cam-serial-number": "327122073698"
    }
  }
]
```

This applies the `xarm6-realsense` fragment with machine-specific values:
- This arm is at `10.1.1.50`
- This camera has serial number `327122073698`

### Fragment Modifications

```json
"fragment_mods": [
  {
    "fragment_id": "f6e98d80-20a0-4fb6-9cb3-7b527a91ec10",
    "mods": [
      { "$set": { "components.arm.frame.translation.z": -10 } },
      { "$set": { "modules.viam_ufactory.version": "1.1.25-rc0" } }
    ]
  }
]
```

**Fragment mods** let you override fragment values without editing the fragment:
- `components.arm.frame.translation.z: -10` — This arm is mounted 10mm below standard
- `modules.viam_ufactory.version` — Pin to a specific version for this machine

This keeps the fragment clean while allowing machine-specific tweaks.

### Board Camera (Cropped View)

```json
{
  "name": "board-cam",
  "api": "rdk:component:camera",
  "model": "erh:viam-chess:board-finder-cam",
  "attributes": {
    "output_size": 800,
    "camera": "cam"
  },
  "frame": { "parent": "cam" }
}
```

This virtual camera:
- Wraps the raw `cam`
- Crops to just the chessboard
- Outputs a square 800x800 image

The `piece-finder` uses this cropped view, not the raw camera.

### Saved Arm Position

```json
{
  "name": "hack-pose-look-straight-down",
  "api": "rdk:component:switch",
  "model": "erh:vmodutils:arm-position-saver",
  "attributes": {
    "joints": [-0.076, -0.202, -1.569, -0.001, 1.740, 3.067],
    "arm": "arm"
  }
}
```

This is a clever pattern: save a known-good arm position as a "switch" component.

- `joints` — The exact joint angles for "looking at the board"
- Calling `SetPosition(2)` moves the arm to these joints
- Used as the "home" position between moves

The chess service uses this via `s.poseStart.SetPosition(ctx, 2, nil)`.

### Piece Finder Vision Service

```json
{
  "name": "piece-finder",
  "api": "rdk:service:vision",
  "model": "erh:viam-chess:piece-finder",
  "attributes": {
    "input": "board-cam"
  }
}
```

**Key points:**
- `api: rdk:service:vision` — Implements the Vision service API
- `model: erh:viam-chess:piece-finder` — Our custom implementation
- `input: board-cam` — Gets images from the cropped board camera

Other services can call `piece-finder.CaptureAllFromCamera()` to get piece positions.

### Motion Service with Constraints

```json
{
  "name": "builtin",
  "api": "rdk:service:motion",
  "model": "rdk:builtin:builtin",
  "attributes": {
    "input_range_override": {
      "arm": {
        "3": { "min": -1.5, "max": 1.5 },
        "5": { "max": 4.14, "min": 2.14 }
      }
    }
  }
}
```

The `input_range_override` constrains joint motion:
- Joint 3: Limited to ±1.5 radians (prevents wrist flip)
- Joint 5: Limited to 2.14-4.14 radians (keeps gripper oriented correctly)

This prevents the arm from finding "valid" but impractical solutions.

### Chess Service

```json
{
  "name": "chess",
  "api": "rdk:service:generic",
  "model": "erh:viam-chess:chess",
  "attributes": {
    "piece-finder": "piece-finder",
    "arm": "arm",
    "gripper": "gripper",
    "pose-start": "hack-pose-look-straight-down",
    "engine": "/usr/games/stockfish",
    "cam": "cam"
  }
}
```

**Key points:**
- `api: rdk:service:generic` — Uses DoCommand for operations
- Dependencies are specified by name (resolved at runtime)
- `engine` — Path to Stockfish binary on the machine

### Stream Deck Buttons

```json
{
  "name": "buttons",
  "api": "rdk:service:generic",
  "model": "erh:viam-streamdeck:streamdeck-any",
  "attributes": {
    "keys": [
      {
        "key": 0,
        "color": "green",
        "text": "move 1",
        "component": "chess",
        "method": "do_command",
        "args": [{ "go": 1 }]
      },
      {
        "key": 4,
        "color": "orange",
        "text": "reset",
        "component": "chess",
        "method": "do_command",
        "args": [{ "reset": true }]
      }
    ],
    "dials": [
      { "dial": 0, "component": "chess", "command": "skill" }
    ]
  }
}
```

This maps physical buttons to chess operations:
- Button 0 (green): Make 1 move
- Button 4 (orange): Reset board
- Dial 0: Adjust engine skill level

The Stream Deck becomes a physical control panel for the chess service.

### Modules

```json
"modules": [
  { "type": "registry", "module_id": "erh:vmodutils", "version": "latest" },
  {
    "type": "registry",
    "module_id": "erh:viam-chess",
    "version": "latest",
    "reload_enabled": true,
    "reload_path": "~/.viam/packages-local/erh_viam-chess_from_reload-module.tar.gz"
  },
  { "type": "registry", "module_id": "erh:viam-streamdeck", "version": "latest" },
  { "type": "registry", "module_id": "viam:tflite_cpu", "version": "latest" }
]
```

**Key points:**
- `type: registry` — Download from Viam module registry
- `version: latest` — Always use newest version
- `reload_enabled: true` — Hot-reload during development (see [Development Workflow](./development.md))

### ML Model Package

```json
"packages": [
  {
    "name": "chess-piece-model1",
    "package": "c2ba7a2c-e229-484c-b99a-5873631f4ea8/chess-piece-model1",
    "type": "ml_model",
    "version": "2025-07-12T20-47-24"
  }
]
```

Downloads an ML model from Viam's registry. Referenced in config as:
```json
"model_path": "${packages.ml_model.chess-piece-model1}/chess-piece-model1.tflite"
```

---

## Configuration Patterns Summary

| Pattern | Example | Benefit |
|---------|---------|---------|
| **Fragment for hardware** | `xarm6-realsense` | Reuse across machines |
| **Variables for machine-specific values** | `arm-ip-address`, `cam-serial-number` | One fragment, many machines |
| **Fragment mods** | `$set: components.arm.frame.translation.z` | Override without editing fragment |
| **Service dependencies by name** | `"arm": "arm"` | Loose coupling, easy testing |
| **Virtual cameras** | `board-cam` wraps `cam` | Transform data pipeline |
| **Saved positions as switches** | `hack-pose-look-straight-down` | Reusable arm poses |
| **Module registry** | `type: registry` | One-line installation |
| **Hot reload** | `reload_enabled: true` | Fast development iteration |

---

**[Next: Development Workflow →](./development.md)**

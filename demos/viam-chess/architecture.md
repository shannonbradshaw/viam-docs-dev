# Architecture

[← Back to Overview](./index.md) | [Next: Code Walkthrough →](./code.md)

---

This page explains how viam-chess is structured—from hardware abstraction through application logic.

## The Big Picture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Machine Config                               │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Fragment: xarm6-realsense                                      │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │ │
│  │  │   arm    │  │   cam    │  │ gripper  │  (hardware layer)    │ │
│  │  └──────────┘  └──────────┘  └──────────┘                      │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Module: erh:viam-chess                                         │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │ │
│  │  │ piece-finder │  │  board-cam   │  │    chess     │          │ │
│  │  │   (vision)   │  │   (camera)   │  │  (generic)   │          │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐                                 │
│  │    motion    │  │ frame system │  (built-in services)           │
│  └──────────────┘  └──────────────┘                                 │
└─────────────────────────────────────────────────────────────────────┘
```

## Layer 1: Hardware (Fragment)

The `xarm6-realsense` fragment encapsulates all hardware configuration:

| Component | API | Model | Purpose |
|-----------|-----|-------|---------|
| `arm` | `rdk:component:arm` | `viam:ufactory:xArm6` | 6-DOF robot arm |
| `cam` | `rdk:component:camera` | `viam:camera:realsense` | Depth camera (RGB + depth) |
| `gripper` | `rdk:component:gripper` | `viam:ufactory:gripper` | Parallel-jaw gripper |

**Why a fragment?** Hardware configuration is complex—IP addresses, serial numbers, frame relationships, joint limits. By packaging this in a fragment:

1. **Reuse** — Apply the same hardware setup to multiple machines
2. **Parameterize** — Use variables for machine-specific values (IP, serial number)
3. **Update centrally** — Fix a frame offset once, all machines get the update

**Fragment variables** make the fragment reusable across different physical setups:

```json
"variables": {
  "arm-name": "arm",
  "arm-ip-address": "10.1.1.50",
  "cam-serial-number": "327122073698"
}
```

Different machines provide different values; the fragment structure stays constant.

## Layer 2: Application Logic (Module)

The `erh:viam-chess` module contains the chess-specific logic:

| Service | API | Purpose |
|---------|-----|---------|
| `piece-finder` | `rdk:service:vision` | Analyzes depth data to find pieces on each square |
| `board-cam` | `rdk:component:camera` | Crops raw camera to just the chessboard |
| `chess` | `rdk:service:generic` | Orchestrates game: picks moves, commands arm |

**Why a module?** Modules let you:

1. **Package custom logic** — Your code runs as a managed process alongside viam-server
2. **Publish to registry** — Anyone can install your module with one config line
3. **Version and update** — Push new versions; machines pull updates automatically

**The generic service pattern:** The `chess` service implements Viam's generic service API. It exposes operations via `DoCommand`:

```go
// Client calls:
result, _ := chess.DoCommand(ctx, map[string]interface{}{"go": 1})

// Service handles:
func (s *viamChessChess) DoCommand(ctx context.Context, cmd map[string]interface{}) (map[string]interface{}, error) {
    if cmd["go"] != nil {
        return s.makeAMove(ctx)
    }
    // ...
}
```

This pattern works for any custom service—expose your operations through `DoCommand` without defining a new API.

## Layer 3: Built-in Services

Viam provides services that the chess module uses:

### Motion Service

Plans and executes arm movements in 3D space:

```go
_, err := s.motion.Move(ctx, motion.MoveReq{
    ComponentName: s.conf.Gripper,
    Destination:   referenceframe.NewPoseInFrame("world", myPose),
})
```

The motion service:
- Knows the arm's kinematics
- Plans collision-free paths
- Handles inverse kinematics automatically

### Frame System

Manages spatial relationships between components:

```
world
  └── arm (base)
        └── cam (mounted on arm end)
        └── gripper (at arm end)
```

When the `piece-finder` detects a piece in camera coordinates, the frame system transforms that to world coordinates so the arm knows where to move.

```go
// Transform point cloud from camera frame to world frame
pc, err := bc.rfs.TransformPointCloud(ctx, s.pc, bc.conf.Input, "world")
```

## Dependency Flow

The chess service declares its dependencies in `Validate`:

```go
func (cfg *ChessConfig) Validate(path string) ([]string, []string, error) {
    // ...
    return []string{
        cfg.PieceFinder,  // vision service
        cfg.Arm,          // arm component
        cfg.Gripper,      // gripper component
        cfg.PoseStart,    // saved position
        motion.Named("builtin").String(),  // motion service
    }, nil, nil
}
```

Viam ensures all dependencies are available before constructing the service. In the constructor:

```go
s.pieceFinder, err = vision.FromProvider(deps, conf.PieceFinder)
s.arm, err = arm.FromProvider(deps, conf.Arm)
s.gripper, err = gripper.FromProvider(deps, conf.Gripper)
s.motion, err = motion.FromDependencies(deps, "builtin")
```

This dependency injection pattern means:
- Services don't know or care what specific hardware they're using
- Swap an xArm for a different arm model—chess code doesn't change
- Test with mock dependencies

## Data Flow: Making a Move

Here's what happens when you tell the robot to make a move:

```
1. DoCommand({"go": 1})
   │
2. piece-finder.CaptureAllFromCamera()
   │  └── cam.Images() + cam.NextPointCloud()
   │  └── Analyze each square: empty, white piece, or black piece
   │  └── Return 64 labeled objects with 3D positions
   │
3. stockfish.BestMove(position)
   │  └── Returns e.g., "e2e4"
   │
4. movePiece(from="e2", to="e4")
   │  └── getCenterFor("e2") → 3D world coordinates
   │  └── motion.Move() → arm moves above piece
   │  └── gripper.Grab()
   │  └── getCenterFor("e4") → 3D world coordinates
   │  └── motion.Move() → arm moves to destination
   │  └── gripper.Open()
   │
5. saveGame() → persist FEN to disk
```

## Key Viam Patterns

### 1. Hardware Abstraction

The chess service uses the `arm.Arm` interface, not `xArm6` specifically:

```go
type viamChessChess struct {
    arm     arm.Arm      // interface, not concrete type
    gripper gripper.Gripper
    // ...
}
```

Benefits:
- Works with any arm that implements the Arm API
- Test with a fake arm in simulation
- Upgrade hardware without code changes

### 2. Composition Over Configuration

Instead of one monolithic config, viam-chess composes:
- Fragment for hardware
- Module for application logic
- Built-in services for motion/frames
- Variables for machine-specific values

Each piece is independently versioned, testable, and reusable.

### 3. Services as Building Blocks

The `piece-finder` is a vision service. The `chess` service consumes it. Tomorrow you could:
- Use `piece-finder` in a different application
- Replace `piece-finder` with a different vision approach
- Add another consumer of piece-finder data

Services compose naturally because they implement standard APIs.

---

**[Next: Code Walkthrough →](./code.md)**

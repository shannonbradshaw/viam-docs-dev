# Block Definitions

**Status:** 🟡 Draft

Blocks are modular tutorials that can be composed into larger workflows. Each block should:
- Be self-contained (~15-30 minutes)
- Work in simulation AND real hardware
- Have clear prerequisites and outcomes
- Map to specific problems from the lifecycle analysis

See [Content Guidelines](./content-guidelines.md) for detailed authoring guidance.

---

## Foundation Blocks

*Apply to all work cells. Everyone starts here.*

| Block | Components | What You Learn | Problems Addressed |
|-------|------------|----------------|-------------------|
| Connect to Cloud | Compute board | Platform basics, remote access, WebRTC | 1.1, 1.6, 2.9 |
| Add a Camera | Camera + compute | Component configuration, viewing feeds | 1.1, 1.2, 1.9 |
| Capture and Sync Data | Camera + compute + cloud | Data pipeline, storage, sync | 1.12, 2.13, 2.14 |
| Basic Filtering | Camera + compute | Time-based sampling, sensor thresholds | 2.13, 2.14 |
| Start Writing Code | Laptop + robot | Run code remotely against hardware | 1.3, 1.21 |

---

## Perception Blocks

*Building understanding of the environment.*

| Block | Components | What You Learn | Problems Addressed |
|-------|------------|----------------|-------------------|
| Add Computer Vision | Camera + compute + model | Vision service, ML models, inference basics | 1.13 |
| Detect Objects (2D) | Camera + ML model | Bounding boxes, confidence scores | 1.13, 1.19 |
| Classify Objects | Camera + ML model | Single-label vs. multi-label classification | 1.13, 1.19 |
| Track Objects Across Frames | Camera + ML model | Persistence, IDs, trajectories | 1.19 |
| Measure Depth | Depth camera | Point clouds, distance estimation | 1.19 |
| Localize Objects in 3D | Camera + depth | Transforming 2D detections to 3D coordinates | 1.19 |

---

## Stationary Vision Blocks

*Vision systems that don't move.*

| Block | Components | What You Learn | Problems Addressed |
|-------|------------|----------------|-------------------|
| Trigger on Detection | Camera + ML + triggers | Event-driven actions, alerts | 2.12 |
| Count Objects | Camera + ML + data | Accumulation, logging, dashboards | 1.12 |
| Inspect for Defects | Camera + ML | Binary classification, pass/fail | 1.13 |
| Monitor Over Time | Camera + data capture | Baseline establishment, anomaly detection | 2.6 |

---

## Mobile Base Blocks

*Robots that move.*

| Block | Components | What You Learn | Problems Addressed |
|-------|------------|----------------|-------------------|
| Control Motors | Base + motors | Velocity commands, encoders | 1.3 |
| Read Odometry | Base + encoders | Position estimation, drift | 1.3, 1.4 |
| Build a Map | Base + lidar + SLAM | Mapping service, localization | 1.17, 1.18 |
| Navigate to Waypoint | Base + lidar + nav service | Motion planning, goal-seeking | 1.17, 1.18 |
| Avoid Obstacles | Base + sensors | Reactive control, safety | 1.7, 1.20 |
| Follow a Patrol Route | Base + nav + waypoints | Multi-point missions, state machines | 1.16 |

---

## Arm + Manipulation Blocks

*Robots that grab things.*

| Block | Components | What You Learn | Problems Addressed |
|-------|------------|----------------|-------------------|
| Move Joints | Arm | Joint positions, velocity control | 1.3 |
| Control Gripper | Gripper | Open/close, force sensing | 1.3 |
| Move to Pose | Arm + motion service | Inverse kinematics, motion planning | 1.17 |
| Pick an Object | Arm + gripper + camera | Grasp planning, coordination | 1.5, 1.19 |
| Place an Object | Arm + gripper | Precision, release | 1.5 |
| Visual Servoing | Arm + camera | Closed-loop control, alignment | 1.19 |

---

## Integration Blocks

*Combining capabilities.*

| Block | Components | What You Learn | Problems Addressed |
|-------|------------|----------------|-------------------|
| Detect While Moving | Base + camera + ML | Perception during motion | 1.5, 1.19 |
| Navigate to Detected Object | Base + camera + nav | Perception-driven goals | 1.16, 1.19 |
| Pick from Bin | Arm + camera + ML | Full pick-and-place cycle | 1.5, 1.19 |
| Mobile Pick-and-Place | Base + arm + camera | Mobile manipulation | 1.5, 1.16 |
| Multi-step Task Sequence | Any | State machines, task logic | 1.15, 1.16 |

---

## Fleet/Deployment Blocks

*Beyond a single robot.*

| Block | Components | What You Learn | Problems Addressed |
|-------|------------|----------------|-------------------|
| Configure Multiple Machines | Multiple robots | Fragments, configuration management | 3.1, 3.2 |
| Monitor a Fleet | Multiple robots | Dashboards, health | 3.7, 4.1 |
| Push Updates | Multiple robots | OTA, staged rollouts | 3.5, 4.3, 4.4 |
| Aggregate Fleet Data | Multiple robots + cloud | Cross-machine queries | 3.10 |

---

## Block Composition: Work Cells

### Stationary Vision Work Cell

```
Foundation
├── Connect to Cloud
├── Add a Camera
├── Capture and Sync Data
├── Basic Filtering
└── Start Writing Code
        ↓
Perception
├── Add Computer Vision
├── Detect Objects (2D)
└── Classify Objects
        ↓
Stationary Vision
├── Trigger on Detection
├── Count Objects
└── Inspect for Defects
        ↓
Fleet/Deployment
├── Configure Multiple Machines
└── Monitor a Fleet
```

### Mobile Base Work Cell

```
Foundation
├── Connect to Cloud
├── Add a Camera
├── Capture and Sync Data
├── Basic Filtering
└── Start Writing Code
        ↓
Perception
├── Add Computer Vision
├── Detect Objects (2D)
└── Track Objects Across Frames
        ↓
Mobile Base
├── Control Motors
├── Read Odometry
├── Build a Map
├── Navigate to Waypoint
├── Avoid Obstacles
└── Follow a Patrol Route
        ↓
Integration
├── Detect While Moving
└── Navigate to Detected Object
        ↓
Fleet/Deployment
├── Configure Multiple Machines
├── Monitor a Fleet
└── Push Updates
```

### Arm + Vision Work Cell

```
Foundation
├── Connect to Cloud
├── Add a Camera
├── Capture and Sync Data
├── Basic Filtering
└── Start Writing Code
        ↓
Perception
├── Add Computer Vision
├── Detect Objects (2D)
├── Measure Depth
└── Localize Objects in 3D
        ↓
Arm + Manipulation
├── Move Joints
├── Control Gripper
├── Move to Pose
├── Pick an Object
└── Place an Object
        ↓
Integration
└── Pick from Bin
        ↓
Fleet/Deployment
├── Configure Multiple Machines
└── Monitor a Fleet
```

---

## Block Template

Each block should follow this structure:

```markdown
# [Block Name]

**Time:** ~X minutes
**Prerequisites:** [list of blocks that should be completed first]
**Works with:** Simulation ✓ | Real Hardware ✓

## What You'll Learn

- Bullet point outcomes

## What Problem This Solves

Brief description of the real-world problem this addresses.

## Components Needed

- Component 1
- Component 2

## Steps

1. Step one
2. Step two
3. ...

## Try It

Interactive element or verification step.

## What's Next

- Link to next block
- Link to related blocks
```

---

## Open Questions

1. **Block size:** Is 15-30 minutes the right target?
2. **Prerequisites:** How strict? Can users skip ahead?
3. **Simulation parity:** Can all blocks work identically in sim and real?
4. **Code samples:** What languages? Python first, then others?
5. **Versioning:** How do we update blocks without breaking paths?

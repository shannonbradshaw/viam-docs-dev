# Stationary Vision Tutorial

**Status:** 🟡 Draft | [View TODOs](./todo.md)

**Time:** ~75 minutes
**Components:** Camera + Compute
**Physics required:** None (rendered images only)

---

## Before You Begin

### What is Viam?

Viam lets you build robotics applications the way you build other software. Viam abstracts away hardware concerns and services for common tasks to enable you to focus on your core robotics application. Declare your hardware in a config, write control logic against well-defined APIs for everything, push updates through a CLI. Viam is the development workflow you're used to, applied to physical machines.

Viam works with any hardware:

| Category | Examples |
|----------|----------|
| Cameras | Webcams, depth cameras, thermal, CSI |
| Arms | 6-DOF robot arms, collaborative arms |
| Bases | Wheeled, tracked, holonomic, drones |
| Motors | DC, stepper, servo, brushless |
| Sensors | IMU, GPS, ultrasonic, temperature, humidity |
| Grippers | Parallel jaw, vacuum, custom end effectors |
| Boards | Raspberry Pi, Jetson, Orange Pi, ESP32 |
| LiDAR | 2D and 3D scanning |
| Encoders | Rotary, absolute, incremental |
| Gantries | Linear actuators, multi-axis systems |

If your hardware isn't on the list, you can add support with a custom module by implementing the appropriate API.

This tutorial uses the simplest work cell (camera + compute) to teach patterns that apply to *all* Viam applications.

### What You'll Learn

By the end of this tutorial, you'll understand how to:

| Skill | What It Means | Applies To |
|-------|---------------|------------|
| Configure components | Add hardware to a Viam machine | Any sensor, actuator, or peripheral |
| Add services | Attach capabilities like ML inference | Vision, navigation, motion planning |
| Write control logic | Code that reads sensors and makes decisions | Any automation task |
| Configure automation | Set up data capture, triggers, and alerts | Production monitoring |
| Scale with fragments | Reuse configurations across machines | Any fleet, any size |
| Manage fleets | Monitor, update, and debug remotely | Production operations |
| Build customer apps | Create products on top of Viam | Shipping to your customers |

**These patterns are the same whether you're working with a camera, a robot arm, or a warehouse full of mobile robots.**

## Scenario

You're building a **quality inspection station** for a canning line. Cans move past a camera on a conveyor belt. Your system must:

1. Detect when a can is present
2. Classify it as PASS or FAIL (identifying dented cans)
3. Log results and trigger alerts on failures
4. Scale to multiple inspection stations
5. Ship as a product your customers can use

---

## What You'll Build

A working inspection system with:

- A camera streaming live images
- An ML model classifying cans as PASS/FAIL (detecting dents)
- Business logic that triggers alerts on failures
- A second station added to your fleet
- A dashboard showing inspection results across stations
- A customer-facing web app with your branding

---

## Tutorial Parts

| Part | Time | What You'll Do |
|------|------|----------------|
| [Part 1: Vision Pipeline](./part1.md) | ~15 min | Set up camera, ML model, and vision service |
| [Part 2: Data Capture](./part2.md) | ~15 min | Configure automatic data sync and alerts |
| [Part 3: Build the Inspector](./part3.md) | ~15 min | Generate module, write inspection logic, test from CLI |
| [Part 4: Deploy as a Module](./part4.md) | ~10 min | Add DoCommand, package and deploy |
| [Part 5: Scale](./part5.md) | ~10 min | Create fragment, add second machine |
| [Part 6: Productize](./part6.md) | ~10 min | Build dashboard, white-label auth |

<details>
<summary><strong>Full Section Outline</strong></summary>

**[Part 1: Vision Pipeline](./part1.md)** (~15 min)
- [1.1 Launch the Simulation](./part1.md#11-launch-the-simulation)
- [1.2 Create a Machine in Viam](./part1.md#12-create-a-machine-in-viam)
- [1.3 Install viam-server](./part1.md#13-install-viam-server)
- [1.4 Configure the Camera](./part1.md#14-configure-the-camera)
- [1.5 Test the Camera](./part1.md#15-test-the-camera)
- [1.6 Add a Vision Service](./part1.md#16-add-a-vision-service)

**[Part 2: Data Capture](./part2.md)** (~15 min)
- [2.1 Configure Data Capture](./part2.md#21-configure-data-capture)
- [2.2 Add Machine Health Alert](./part2.md#22-add-machine-health-alert)
- [2.3 View and Query Data](./part2.md#23-view-and-query-data)
- [2.4 Summary](./part2.md#24-summary)

**[Part 3: Build the Inspector](./part3.md)** (~15 min)
- [3.1 Generate the Module Scaffold](./part3.md#31-generate-the-module-scaffold)
- [3.2 Add Remote Machine Connection](./part3.md#32-add-remote-machine-connection)
- [3.3 Add Detection Logic](./part3.md#33-add-detection-logic)
- [3.4 Configure the Rejector](./part3.md#34-configure-the-rejector)
- [3.5 Add Rejection Logic](./part3.md#35-add-rejection-logic)
- [3.6 Summary](./part3.md#36-summary)

**[Part 4: Deploy as a Module](./part4.md)** (~10 min)
- [4.1 Add the DoCommand Interface](./part4.md#41-add-the-docommand-interface)
- [4.2 Review the Generated Module Structure](./part4.md#42-review-the-generated-module-structure)
- [4.3 Build and Deploy](./part4.md#43-build-and-deploy)
- [4.4 Summary](./part4.md#44-summary)

**[Part 5: Scale](./part5.md)** (~10 min)
- [5.1 Create a Fragment](./part5.md#51-create-a-fragment)
- [5.2 Parameterize Machine-Specific Values](./part5.md#52-parameterize-machine-specific-values)
- [5.3 Add a Second Machine](./part5.md#53-add-a-second-machine)
- [5.4 Fleet Management Capabilities](./part5.md#54-fleet-management-capabilities)

**[Part 6: Productize](./part6.md)** (~15 min)
- [6.1 Create a Dashboard](./part6.md#61-create-a-dashboard)
- [6.2 Set Up White-Label Auth](./part6.md#62-set-up-white-label-auth)
- [6.3 (Optional) Configure Billing](./part6.md#63-optional-configure-billing)

</details>

---

## Get Started

**[Begin Part 1: Vision Pipeline →](./part1.md)**

---

## What's Next

### You Can Now Build

With the skills from this tutorial, you could build:

- **Inventory monitoring** — Camera watches shelves, alerts when stock is low
- **Security system** — Detect people or vehicles, log events, send alerts
- **Wildlife camera** — Classify animals, sync photos to cloud, monitor remotely
- **Equipment monitoring** — Watch gauges or indicator lights, alert on anomalies

These all use the same patterns: configure components, add services, write logic, deploy, scale with fragments.

### Continue Learning

**Try another tutorial:**
- [Mobile Base](../mobile-base.md) — Add navigation and movement
- [Arm + Vision](../arm-vision.md) — Add manipulation

**Go deeper with blocks:**
- [Track Objects Across Frames](../../build/perception/track-objects.md) — Add persistence to detections
- [Capture and Sync Data](../../build/foundation/capture-sync.md) — Build datasets from your cameras
- [Monitor Over Time](../../build/stationary-vision/monitor-over-time.md) — Detect anomalies and trends

**Build your own project:**
- You have all the foundational skills
- Pick hardware (or stay in simulation)
- Use the blocks as reference when you get stuck

---

## Simulation Requirements

### Work Cell Elements

| Element | Description |
|---------|-------------|
| Conveyor belt | Moving belt where cans travel |
| Camera | Overhead RGB camera (640x480) |
| Sample cans | Mix of good cans and dented cans (~10% defect rate) |
| Lighting | Consistent industrial lighting |

### Viam Components

| Component | Type | Notes |
|-----------|------|-------|
| `inspection-cam` | camera | Gazebo RGB camera |
| `can-classifier` | mlmodel | TFLite model for PASS/FAIL classification (detects dents) |
| `can-detector` | vision | ML model service connected to camera |
| `rejector` | motor | Pneumatic pusher for rejecting defective cans |
| `inspector` | generic (module) | Control logic service |
| `offline-alert` | trigger | Email notification when machine goes offline |

### Simulated Events

| Event | Trigger | Purpose |
|-------|---------|---------|
| Can appears | Automatic (every 4 seconds) | New can to inspect |


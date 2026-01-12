# Stationary Vision Tutorial

**Status:** 🔴 Outline

**Time:** ~1.25 hours
**Components:** Camera + Compute
**Physics required:** None (rendered images only)

---

## Scenario

You're building a **quality inspection station** for a manufacturing line. Parts move past a camera on a conveyor. Your system must:

1. Detect when a part is present
2. Classify it as PASS or FAIL (defect detection)
3. Log results and trigger alerts on failures
4. Scale to multiple inspection stations
5. Ship as a product your customers can use

This is the simplest Viam work cell — no actuators, just perception and logic.

---

## What You'll Build

By the end of this tutorial, you'll have:

- A camera streaming live images
- An ML model classifying objects as pass/fail
- Business logic that triggers alerts on failures
- A second "station" added to your fleet
- A dashboard showing inspection results across stations
- A customer-facing web app with your branding

---

## Tutorial Flow

### Part 1: Prototype (~20 min)

**Goal:** Get a working detection pipeline on one simulated camera.

#### 1.1 Configure Your Machine
- Launch simulation (browser-based)
- See the work cell: conveyor, camera, sample parts
- Connect to Viam and see your machine appear

#### 1.2 View the Camera Feed
- Open the camera stream in the Viam app
- Understand what the camera sees
- Take a snapshot

#### 1.3 Add a Vision Service
- Configure an ML model (pre-trained for this tutorial)
- Run detection on a snapshot
- See bounding boxes and classifications

#### 1.4 Write Detection Logic
- Connect via Python SDK
- Get camera images programmatically
- Run detections and print results
- Filter for "FAIL" classifications

**Checkpoint:** You can detect defects in code.

---

### Part 2: Deploy (~10 min)

**Goal:** Make your detection logic run continuously on the machine.

#### 2.1 Create a Process
- Wrap your detection script as a Viam process
- Configure it to run on startup
- See it running in the Viam app

#### 2.2 Add Alerting
- Configure a webhook or notification on FAIL detection
- Trigger a test alert
- See the alert arrive

**Checkpoint:** Detection runs automatically and alerts you.

---

### Part 3: Scale (~10 min)

**Goal:** Add a second inspection station.

#### 3.1 Create a Fragment
- Extract your camera + vision + process config into a fragment
- Understand why fragments matter for fleets

#### 3.2 Add a Second Machine
- Launch a second simulated station
- Apply the fragment
- See both machines in your fleet

**Checkpoint:** Two stations running the same inspection logic.

---

### Part 4: Fleet (~10 min)

**Goal:** Manage both stations as a fleet.

#### 4.1 Fleet Dashboard
- View both machines' status
- See aggregated detection counts
- Compare pass/fail rates between stations

#### 4.2 Push a Configuration Update
- Modify the fragment (e.g., adjust detection threshold)
- See it propagate to both machines
- Understand fleet-wide config management

**Checkpoint:** You can manage multiple machines from one place.

---

### Part 5: Maintain (~10 min)

**Goal:** Debug and fix an issue.

#### 5.1 Simulate a Problem
- One camera "degrades" (simulated noise/blur)
- Detection accuracy drops
- See the alert or anomaly in fleet view

#### 5.2 Diagnose
- Check logs for the affected machine
- View camera feed to see the degradation
- Identify root cause

#### 5.3 Fix and Verify
- "Replace" the camera (reset simulation)
- Verify detection accuracy recovers
- Review the incident timeline

**Checkpoint:** You've debugged a production issue.

---

### Part 6: Productize (~15 min)

**Goal:** Build a customer-facing product.

#### 6.1 Create a Customer Dashboard
- Use the TypeScript SDK to build a simple web page
- Display live pass/fail counts from your fleet
- Show recent inspection images

#### 6.2 Set Up White-Label Auth
- Configure authentication with your branding
- Your customer logs in without seeing Viam
- Understand how end-user access works

#### 6.3 (Optional) Configure Billing
- Set up per-machine or per-inspection pricing
- See how Viam handles metering and invoicing

**Checkpoint:** You have a customer-ready product, not just a prototype.

---

## Simulation Requirements

### Work Cell Elements

| Element | Description |
|---------|-------------|
| Conveyor/staging area | Surface where parts appear |
| Camera | Overhead RGB camera (640x480, 30fps) |
| Sample parts | Mix of "good" and "defective" items |
| Lighting | Consistent industrial lighting |

### Viam Components

| Component | Type | Notes |
|-----------|------|-------|
| `inspection-cam` | camera | Gazebo RGB camera |
| `part-detector` | vision | ML model service |
| `inspector` | process | Detection + alerting script |

### Simulated Events

| Event | Trigger | Purpose |
|-------|---------|---------|
| Part appears | Timer or user action | New item to inspect |
| Camera degradation | Part 5 trigger | Create debugging scenario |

---

## Blocks Used

From [block-definitions.md](../planning/block-definitions.md):

**Foundation:**
- Connect to Cloud
- Add a Camera
- Start Writing Code

**Perception:**
- Add Computer Vision
- Detect Objects (2D)

**Stationary Vision:**
- Trigger on Detection
- Inspect for Defects

**Fleet/Deployment:**
- Configure Multiple Machines
- Monitor a Fleet
- Push Updates

**Productize (not yet defined):**
- Build a Customer Dashboard (TypeScript SDK)
- Set Up White-Label Auth
- Configure Billing

---

## Open Questions

1. **Part appearance:** Should parts appear automatically on a timer, or should the user trigger them? Timer feels more realistic; manual trigger gives more control.

2. **ML model:** Use a pre-trained model we provide, or walk through training? Pre-trained keeps focus on Viam concepts; training adds complexity.

3. **Alert destination:** Webhook? Email? In-app notification? Need to pick something that works in a tutorial context without requiring user setup.

4. **Second station:** Identical simulation, or slightly different (e.g., different camera angle)? Identical is simpler; different shows fragment flexibility.


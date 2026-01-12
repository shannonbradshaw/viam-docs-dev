# Stationary Vision Tutorial

**Status:** 🔴 Outline

**Time:** ~1.25 hours
**Components:** Camera + Compute
**Physics required:** None (rendered images only)

---

## Before You Begin

### What is Viam?

Viam is a platform for building, deploying, and managing robotics applications. It handles the hard parts—hardware configuration & abstraction, remote access, fleet management, data pipelines, ML deployment—so you can focus on what your machine should *do*.

Viam works with:
- **Cameras and sensors** — vision systems, environmental monitoring
- **Robot arms** — pick-and-place, assembly, machine tending
- **Mobile bases** — AMRs, delivery robots, patrol systems
- **Any combination** — mobile manipulation, multi-robot coordination

This tutorial uses the simplest work cell (camera + compute) to teach patterns that apply to *all* Viam applications.

### What You'll Learn

By the end of this tutorial, you'll understand how to:

| Skill | What It Means | Applies To |
|-------|---------------|------------|
| Configure components | Add hardware to a Viam machine | Any sensor, actuator, or peripheral |
| Add services | Attach capabilities like ML inference | Vision, navigation, motion planning |
| Write control logic | Code that reads sensors and makes decisions | Any automation task |
| Deploy code to machines | Run your logic on the machine itself | All production deployments |
| Scale with fragments | Reuse configuration across machines | Any fleet, any size |
| Manage fleets | Monitor, update, and debug remotely | Production operations |
| Build customer apps | Create products on top of Viam | Shipping to your customers |

**These patterns are the same whether you're working with a camera, a robot arm, or a warehouse full of mobile robots.**

### This Tutorial vs. Others

| Tutorial | Hardware | Best For |
|----------|----------|----------|
| **Stationary Vision** (this one) | Camera + Compute | Inspection, monitoring, counting |
| Mobile Base | Wheeled robot + Lidar | Navigation, patrol, delivery |
| Arm + Vision | Robot arm + Camera | Pick-and-place, assembly |

All three tutorials teach the same core platform skills. Choose based on your interest or use case.

---

## Scenario

You're building a **quality inspection station** for a manufacturing line. Parts move past a camera on a conveyor. Your system must:

1. Detect when a part is present
2. Classify it as PASS or FAIL
3. Log results and trigger alerts on failures
4. Scale to multiple inspection stations
5. Ship as a product your customers can use

---

## What You'll Build

A working inspection system with:

- A camera streaming live images
- An ML model classifying parts as pass/fail
- Business logic that triggers alerts on failures
- A second station added to your fleet
- A dashboard showing inspection results across stations
- A customer-facing web app with your branding

---

## Tutorial Flow

### Part 1: Prototype (~20 min)

**Goal:** Get a working detection pipeline on one simulated camera.

**Skills:** Component configuration, viewing sensor data, adding services, writing SDK code.

#### 1.1 Launch the Simulation
- Open the browser-based simulation
- See the work cell: conveyor, camera, sample parts
- Understand what you're working with

> **Author note:** Provide clear visual of what the simulation looks like. Users need to orient themselves.

#### 1.2 Connect to Viam
- Create a Viam account (if needed)
- See your simulated machine appear in the Viam app
- Understand: the simulation is running `viam-server`, just like real hardware would

> **Author note:** This is where UI friction happens. Document exact clicks. Screenshots essential. Note any confusing UI elements and guide through them.

#### 1.3 View the Camera Feed
- Find the camera component in the Viam app
- Open the live stream
- Take a snapshot
- **Transferable skill:** This is how you view *any* camera in Viam—webcam, industrial camera, depth camera

> **Author note:** The camera panel in the app can be non-obvious. Provide explicit guidance.

#### 1.4 Add a Vision Service
- Configure an ML model (pre-trained, provided for this tutorial)
- Run detection on your camera feed
- See bounding boxes and classifications
- **Transferable skill:** This is how you add ML to *any* Viam machine

> **Author note:** Vision service configuration has multiple steps. Break down carefully. Note that users can train their own models later (link to ML docs), but we're using pre-trained here to stay focused.

#### 1.5 Write Detection Logic
- Connect to your machine via Python or Go SDK
- Get camera images programmatically
- Run detections and print results
- Filter for "FAIL" classifications
- **Transferable skill:** This is how you write control logic for *any* Viam component

> **Author note:** Provide complete, working code. Both Python and Go. Users should be able to copy-paste and run. Explain what each section does.

**Checkpoint:** You can detect defects in code. You've configured components, added a service, and written SDK code—the same pattern for any Viam project.

---

### Part 2: Deploy (~10 min)

**Goal:** Make your detection logic run continuously on the machine.

**Skills:** Deploying code to run on machines, event-driven actions.

#### 2.1 Create a Process
- Wrap your detection script as a Viam process
- Configure it to run on machine startup
- See it running in the Viam app
- **Transferable skill:** This is how you deploy *any* code to run on a Viam machine

> **Author note:** Process configuration can be confusing. Show exactly where this lives in the config. Explain the difference between running code on your laptop vs. on the machine.

#### 2.2 Add Alerting
- Trigger an action when a FAIL is detected
- See the alert arrive
- **Transferable skill:** Event-driven actions work the same way across all Viam applications

> **Author note:** Need to decide on alert mechanism that works without user setup (in-app notification? logged event?). Whatever we choose, explain how this pattern extends to webhooks, emails, etc. in production.

**Checkpoint:** Detection runs automatically. Your code is deployed to the machine, not just running on your laptop.

---

### Part 3: Scale (~10 min)

**Goal:** Add a second inspection station.

**Skills:** Configuration reuse with fragments, fleet basics.

#### 3.1 Create a Fragment
- Extract your camera + vision + process config into a fragment
- Understand what a fragment is: reusable configuration
- **Transferable skill:** Fragments are how you manage configuration across *any* fleet

> **Author note:** Fragments are a key Viam concept but can be abstract. Use concrete analogy: "A fragment is like a template. Instead of configuring each machine from scratch, you apply the template."

#### 3.2 Add a Second Machine
- Launch a second simulated station
- Apply the fragment
- See both machines in your organization
- **Transferable skill:** This is how you scale from 1 to 1,000 machines

**Checkpoint:** Two stations running identical inspection logic. You didn't copy-paste configuration—you used a fragment.

---

### Part 4: Fleet (~10 min)

**Goal:** Manage both stations as a fleet.

**Skills:** Fleet monitoring, pushing updates.

#### 4.1 View Your Fleet
- See both machines' status in the Viam app
- View aggregated data across machines
- Compare pass/fail rates between stations
- **Transferable skill:** Fleet monitoring works the same whether you have 2 machines or 200

> **Author note:** Show the fleet view clearly. If there are UI rough edges here, document workarounds.

#### 4.2 Push a Configuration Update
- Modify the fragment (e.g., adjust detection threshold)
- See it propagate to both machines
- **Transferable skill:** This is how you update *any* fleet—change the fragment, machines sync automatically

**Checkpoint:** You can manage multiple machines from one place. Configuration changes propagate automatically.

---

### Part 5: Maintain (~10 min)

**Goal:** Debug and fix an issue.

**Skills:** Remote diagnostics, log analysis, incident response.

#### 5.1 Simulate a Problem
- One camera "degrades" (simulated noise/blur)
- Detection accuracy drops
- Notice the anomaly in your fleet view or alerts

#### 5.2 Diagnose Remotely
- Check logs for the affected machine
- View the camera feed to see the degradation
- Identify root cause—without physical access to the machine
- **Transferable skill:** Remote diagnostics work the same for any Viam machine, anywhere in the world

#### 5.3 Fix and Verify
- "Replace" the camera (reset simulation)
- Verify detection accuracy recovers
- **Transferable skill:** The debug cycle is the same in production

**Checkpoint:** You've diagnosed and fixed a production issue remotely.

---

### Part 6: Productize (~15 min)

**Goal:** Build a customer-facing product.

**Skills:** Building apps with Viam SDKs, white-label deployment.

#### 6.1 Create a Customer Dashboard
- Use the TypeScript SDK to build a simple web page
- Display live pass/fail counts from your fleet
- Show recent inspection images
- **Transferable skill:** The SDKs let you build *any* customer-facing application

> **Author note:** Provide working starter code. Keep the dashboard simple—the point is showing that Viam provides the APIs, not teaching web development.

#### 6.2 Set Up White-Label Auth
- Configure authentication with your branding
- Your customer logs in without seeing Viam
- **Transferable skill:** This is how you ship products to *your* customers, not Viam's

#### 6.3 (Optional) Configure Billing
- Set up per-machine or per-inspection pricing
- See how Viam handles metering and invoicing

**Checkpoint:** You have a customer-ready product. You've gone from prototype to shippable product in one tutorial.

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
- [Mobile Base](./mobile-base.md) — Add navigation and movement
- [Arm + Vision](./arm-vision.md) — Add manipulation

**Go deeper with blocks:**
- [Track Objects Across Frames](../build/perception/track-objects.md) — Add persistence to detections
- [Capture and Sync Data](../build/foundation/capture-sync.md) — Build datasets from your cameras
- [Monitor Over Time](../build/stationary-vision/monitor-over-time.md) — Detect anomalies and trends

**Build your own project:**
- You have all the foundational skills
- Pick hardware (or stay in simulation)
- Use the blocks as reference when you get stuck

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

**Productize:**
- Build a Customer Dashboard (TypeScript SDK)
- Set Up White-Label Auth
- Configure Billing

---

## Author Guidance

### UI Rough Edges to Address

Document and provide explicit guidance for:

- [ ] Account creation flow
- [ ] Finding the camera panel in the app
- [ ] Vision service configuration steps
- [ ] Process configuration location
- [ ] Fragment creation UI
- [ ] Fleet view navigation

### Key Teaching Moments

At each step, explicitly connect to transferable skills:

- "This is how you configure *any* component"
- "This pattern works for *any* sensor"
- "You'd do the same thing with a robot arm"

### Anti-Patterns to Avoid

- Don't let users think Viam is "just for cameras"
- Don't let steps feel like magic—explain what's happening
- Don't assume users will read linked docs—include essential context inline

---

## Open Questions

1. **Part appearance:** Timer vs. manual trigger? Timer feels realistic; manual gives control.

2. **ML model:** Pre-trained (provided) vs. walk through training? Pre-trained keeps focus on platform skills.

3. **Alert mechanism:** What works without user setup? In-app notification? Logged event?

4. **Second station:** Identical or slightly different? Identical is simpler; different shows fragment flexibility.

5. **Dashboard complexity:** How much web dev do we include? Keep minimal—point is Viam APIs, not teaching React.

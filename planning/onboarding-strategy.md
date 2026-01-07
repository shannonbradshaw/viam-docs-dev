# Onboarding Strategy

**Status:** 🟡 Draft

---

## Core Insights

**Insight 1:** Viam's value proposition is strongest at scale (fleet management, data pipelines, OTA updates), but onboarding happens at scale=1.

**Insight 2:** Fragments are central to the Viam workflow—not just a fleet feature. A fragment can configure a camera-arm combination, a camera-to-object-detection pipeline, or an entire work cell. Work cells ARE fragments.

**Insight 3:** "Develop from anywhere" is immediate value at Stage 1. You can run code from your laptop against robot hardware over the network—no SSH, no copying files, no deploy step. This is differentiated and demonstrable immediately.

**The challenge:** How do we demonstrate value immediately without requiring users to imagine future benefits?

**The approach:** 
1. Lead with "develop from anywhere"—show the IDE-to-robot workflow immediately
2. Use simulation to let users experience the full lifecycle (all 5 stages) in miniature
3. Work cells are fragments—completing simulation means you have a reusable config
4. Apply the same fragment to real hardware and it works

---

## Onboarding Paths

### Path 1: Simulation (Zero Hardware)

**Purpose:** Immediate hands-on experience with no friction

**Approach:** Browser-based simulation using hosted Gazebo (GzWeb or similar)

**Work Cells:**
1. Stationary Vision — camera + compute
2. Mobile Base — base + camera + lidar
3. Arm + Vision — arm + camera + gripper

Each simulation walks through all 5 lifecycle stages in miniature:
- Stage 1: Configure components, write control code
- Stage 2: Deploy to a "field" environment in simulation
- Stage 3: Add a second robot, see fleet features
- Stage 4: Monitor fleet health, push updates
- Stage 5: Debug an issue, push a fix

**Technical Requirements:**
- Hosted Gazebo infrastructure (CloudSim + GzWeb or The Construct partnership)
- Pre-built simulation environments for each work cell
- Simulated sensors that feed into Viam services (vision, SLAM, etc.)

### Path 2: Real Hardware Work Cells

**Purpose:** Deep, polished experience for users ready to build

**Approach:** Each work cell is a published fragment with blessed hardware. Users apply the fragment and get a working configuration.

**Work Cells (each is a Fragment):**

| Work Cell | Components | Applications Covered |
|-----------|------------|----------------------|
| Stationary Vision | Camera + Raspberry Pi/Jetson | Quality inspection, monitoring, sorting |
| Mobile Base | Wheeled base + camera + lidar + Pi/Jetson | Warehouse AMR, patrol, delivery, agriculture |
| Arm + Vision | Robot arm + camera + gripper + Pi/Jetson | Pick-and-place, food service, machine tending |

Each work cell fragment includes:
- Component configurations for blessed hardware
- Pre-computed transforms (for camera-arm setups, no manual calibration)
- Service configurations (vision, motion, SLAM as applicable)
- Blessed hardware list with links to purchase
- Curated path through relevant blocks

**Fragment benefits:**
- Apply the same fragment from simulation to real hardware
- Override per-machine differences without forking the base config
- Version control and rollback built in

### Path 3: Bring Your Own Hardware

**Purpose:** Support users who already have hardware

**Approach:** Point to relevant blocks based on what they have

**Entry points:**
- "I have a camera" → Foundation blocks
- "I have a mobile base" → Mobile base blocks
- "I have an arm" → Arm/manipulation blocks

---

## Block Architecture

Blocks are modular tutorials that can be composed into larger workflows.

**Characteristics:**
- Self-contained (clear inputs, outputs, prerequisites)
- ~15-30 minutes each
- Work in simulation AND real hardware
- Include "what you'll learn" and "what problem this solves"

**Progression:**

```
Foundation (all users start here)
    ↓
Perception (if using vision)
    ↓
┌───────────────────┬────────────────────┐
│ Stationary Vision │ Mobile Base        │ Arm + Manipulation │
└───────────────────┴────────────────────┴────────────────────┘
    ↓                       ↓                      ↓
                    Integration
                         ↓
                       Fleet
```

---

## Simulation-to-Hardware Graduation

The simulation mirrors real hardware work cells. Each simulation IS a fragment:

1. Complete simulation onboarding → you have a working fragment
2. Purchase recommended hardware
3. Apply the same fragment to real hardware
4. See it work in the physical world

This requires:
- Simulation component configs that match real hardware configs
- Clear mapping from simulated components to purchasable hardware
- Fragment variable substitution for hardware differences

---

## Development Workflow Progression

Viam supports a natural progression from experimentation to production:

**Stage 1: Iterate from your IDE**
- Write code on your laptop
- Run against robot hardware over the network
- No copying files, no deploy step
- See results immediately

**Stage 2: Run on the robot when latency matters**
- Same code, same APIs
- Just a different execution environment
- For tight control loops that can't tolerate network latency

**Stage 3: Package as a module**
- When your code is stable, package it
- viam-server manages lifecycle: starts on boot, restarts on failure
- Reconfigure parameters without redeploying

**Stage 4: Deploy through Registry**
- Push to Registry with CLI
- Version control, staged rollouts, rollback
- OTA updates to fleet

This progression should be explicit in the Build section—users should understand where they are and what comes next.

---

## Success Metrics

**Primary:** Increase in monthly active users

**Leading indicators:**
- Simulation completion rate
- Time to first working robot (real or simulated)
- Block completion rate
- Hardware work cell adoption

---

## Open Questions

1. **Simulation infrastructure:** Build vs. partner? Cost model?
2. **Hardware sourcing:** How prescriptive on specific vendors/models?
3. **Block granularity:** Are blocks the right size? Too big? Too small?
4. **Offline capability:** How does simulation work offline?
5. **Assessment:** How do we know if someone "completed" onboarding?

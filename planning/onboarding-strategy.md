# Onboarding Strategy

**Status:** 🟡 Draft

---

## Core Insight

Viam's value proposition is strongest at scale (fleet management, data pipelines, OTA updates), but onboarding happens at scale=1. 

**The challenge:** How do we demonstrate value immediately without requiring users to imagine future benefits?

**The approach:** Use simulation to let users experience the full lifecycle (all 5 stages) in miniature, then provide modular blocks for building with real hardware.

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

**Approach:** Specified hardware configurations with blessed component lists

**Work Cells:**

| Work Cell | Components | Applications Covered |
|-----------|------------|----------------------|
| Stationary Vision | Camera + Raspberry Pi/Jetson | Quality inspection, monitoring, sorting |
| Mobile Base | Wheeled base + camera + lidar + Pi/Jetson | Warehouse AMR, patrol, delivery, agriculture |
| Arm + Vision | Robot arm + camera + gripper + Pi/Jetson | Pick-and-place, food service, machine tending |

Each work cell has:
- Blessed hardware list with links to purchase
- Setup guide for hardware assembly
- Curated path through relevant blocks

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

The simulation should mirror real hardware work cells so users can:

1. Complete simulation onboarding
2. Purchase recommended hardware
3. Apply the same configuration and code to real hardware
4. See it "just work"

This requires:
- Simulation component configs that match real hardware configs
- Clear mapping from simulated components to purchasable hardware
- Minimal changes required when transitioning

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

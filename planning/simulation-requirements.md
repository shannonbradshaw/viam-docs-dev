# Simulation Requirements

**Status:** 🟡 Draft

Technical requirements and options for browser-based simulation onboarding.

---

## Why Simulation Matters

Physical tasks (manipulation, mobile navigation) are the most compelling demos of Viam's capabilities. They're also the most expensive hardware for users to acquire—arms cost thousands. Simulation lets users experience what they can't easily buy.

**Key insight:** Users need to *feel* manipulation working, not just learn the concepts. This requires physics fidelity for grasping, placing, and navigation—not just rendered images.

---

## Requirements

| Requirement | Priority | Notes |
|-------------|----------|-------|
| Zero installation | Must have | Browser-based, no downloads |
| Physics fidelity | Must have | Grasping, placing, collision must feel real |
| Real-time sensor feeds | Must have | Camera, lidar, depth |
| Actuator control | Must have | Base movement, arm joints, gripper |
| Viam integration | Must have | Simulated hardware exposes Viam APIs |
| Reasonable latency | Must have | <100ms for teleoperation to feel responsive |
| Persistent state | Should have | Resume sessions |
| Mobile device support | Nice to have | May be limited by physics compute |

---

## Landscape Assessment (January 2025)

### Ruled Out

| Option | Status | Reason |
|--------|--------|--------|
| **AWS RoboMaker** | Dead | Discontinued September 2025, no new customers |
| **AWS Batch** | Not suitable | Headless only—no interactive GUI |
| **Gazebo Classic** | EOL | End of life January 2025 |
| **Lightweight WebGL** | Insufficient | No physics fidelity for manipulation |

### Viable Options

**1. The Construct (Partnership)**

Browser-based ROS development environment with Gazebo/Webots backend.

| Aspect | Details |
|--------|---------|
| Architecture | Browser IDE + cloud-hosted Gazebo/Webots |
| Simulators | Gazebo, Webots, more in pipeline |
| Physics | Full Gazebo physics |
| Collaboration | Multiple users on same simulation |
| Real robots | Remote labs (warehouse with UR3, mobile bases) |
| Integration | ROS-centric; Viam integration would need negotiation |

**Pros:** Infrastructure already built, maintained, includes real robot labs
**Cons:** ROS-centric, partner dependency, unclear customization flexibility

**2. Self-Hosted Gazebo (Build)**

Host Gazebo Harmonic in cloud containers with GzWeb for browser access.

| Aspect | Details |
|--------|---------|
| Simulator | gz-sim (Gazebo Harmonic) |
| Web client | New GzWeb or app.gazebosim.org visualization |
| Containers | Docker images available (OSRF) |
| GPU | Only needed if server-side camera rendering |

**Pros:** Full control, Viam-native integration, no partner dependency
**Cons:** Infrastructure to build and operate, ongoing maintenance

---

## Architecture: Self-Hosted

```
┌─────────────────────────────────────────────────────────┐
│                    Cloud (AWS/GCP)                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Per-User Container                  │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │   │
│  │  │ gz-sim   │  │ gzweb    │  │ viam-server  │  │   │
│  │  │ (physics)│  │ (stream) │  │ + modules    │  │   │
│  │  └──────────┘  └──────────┘  └──────────────┘  │   │
│  └─────────────────────────────────────────────────┘   │
│                         ↓ WebSocket                     │
└─────────────────────────────────────────────────────────┘
                          ↓
              ┌───────────────────────┐
              │   User's Browser      │
              │   (GzWeb 3D view)     │
              └───────────────────────┘
```

### Components to Build

| Component | Effort | Description |
|-----------|--------|-------------|
| Container image | Medium | gz-sim + gzweb + viam-server, tested configs |
| Viam modules for sim | Medium | Camera, arm, base, gripper, lidar modules that bridge Gazebo to Viam APIs |
| Session orchestration | Medium | Spin up/down containers per user, manage state |
| Simulation environments | Medium | Gazebo world files for 3 work cells |
| Cost management | Low | Auto-shutdown idle sessions |

### Reference Implementation

[DukeRobotics/gzweb-rosssh](https://github.com/DukeRobotics/gzweb-rosssh) — Dockerized Gazebo + GzWeb + ROS + SSH (starting point, would remove ROS dependency)

---

## Simulation Environments Needed

| Work Cell | Environment | Key Elements |
|-----------|-------------|--------------|
| Stationary Vision | Workbench with objects | Camera, conveyor/staging area, varied objects |
| Mobile Base | Warehouse/office | Wheeled robot, lidar, obstacles, waypoints |
| Arm + Vision | Bin picking station | Robot arm, gripper, camera, bin with objects |

Each environment needs:
- Gazebo world file (.sdf)
- Robot model(s) with accurate physics
- Viam configuration fragment
- Starter code for the work cell

---

## Viam Integration Architecture

Simulated hardware must expose standard Viam component APIs. Users configure Viam the same way whether hardware is real or simulated.

```
┌─────────────────────────────────────────────────┐
│                  viam-server                     │
│  ┌─────────────────────────────────────────┐   │
│  │           Viam Component APIs            │   │
│  │  camera | arm | base | gripper | lidar  │   │
│  └─────────────────────────────────────────┘   │
│                      ↑                          │
│  ┌─────────────────────────────────────────┐   │
│  │         Gazebo Bridge Modules            │   │
│  │  Translate Viam API ↔ Gazebo topics      │   │
│  └─────────────────────────────────────────┘   │
│                      ↑                          │
└──────────────────────┼──────────────────────────┘
                       ↓
              ┌─────────────────┐
              │     gz-sim      │
              │  (physics sim)  │
              └─────────────────┘
```

**Key principle:** The Viam configuration for simulation should be nearly identical to real hardware configuration. Change the module (simulated vs. real driver), keep everything else.

---

## Physics Fidelity by Block

Not all blocks require physics. Here's where it matters:

| Category | Physics Needed | Why |
|----------|----------------|-----|
| Foundation | None | Config, data flow, code execution |
| Perception | None | Just need rendered images |
| Stationary Vision | None | Image processing, no physical interaction |
| Mobile Base | Light | Plausible movement, collision detection |
| Arm (motion) | Light | Arm moves to commanded positions |
| Arm (grasping) | Full | Objects must behave realistically |
| Integration | Full | Pick-and-place requires real physics |

---

## Cost Considerations

### Self-Hosted

| Cost Factor | Estimate | Notes |
|-------------|----------|-------|
| Compute per session | ~$0.10-0.50/hour | Depends on instance size, GPU needs |
| Engineering to build | 2-4 person-months | Container, modules, orchestration, environments |
| Ongoing maintenance | 0.25-0.5 FTE | Updates, scaling, debugging |

### The Construct Partnership

| Cost Factor | Estimate | Notes |
|-------------|----------|-------|
| Per-user licensing | TBD | Need to negotiate |
| Integration engineering | 1-2 person-months | Viam modules, custom environments |
| Ongoing | Licensing fees | Less maintenance burden |

---

## Open Questions

### Strategic
1. Partner (The Construct) vs. build (self-hosted)—what's the appetite for infrastructure ownership?
2. If partnering, what's the fallback if partnership doesn't work out?

### Technical
1. New GzWeb maturity—is it production-ready for Gazebo Harmonic?
2. Latency achievable with cloud-hosted Gazebo + WebSocket streaming?
3. GPU requirements for the three work cell environments?

### Business
1. The Construct's flexibility on non-ROS integration?
2. White-label / embedding options?
3. Pricing model that works for Viam's onboarding use case?

---

## Next Steps

1. **Contact The Construct** — Understand partnership options, integration flexibility
2. **Prototype self-hosted** — Spin up gz-sim + gzweb in Docker, measure latency
3. **Build one Viam module** — Prove out the Gazebo-to-Viam bridge pattern
4. **Decide** — Based on findings, commit to a path

---

## Appendix A: Questions for The Construct

### Draft Outreach Email

**Subject:** Partnership Inquiry: Browser-Based Robotics Simulation for Viam Onboarding

Hi,

I'm reaching out from Viam (viam.com) to explore a potential partnership around browser-based robotics simulation.

**About Viam:** We're a software platform for building, deploying, and managing robotics applications. Our users configure hardware and services through our platform, write control logic using our SDKs, and scale from prototype to fleet.

**The challenge:** We're redesigning our onboarding experience and want users to experience Viam's capabilities—including manipulation and mobile navigation—without requiring them to purchase hardware upfront. Arms and mobile bases are expensive; simulation lets users feel what's possible before they invest.

**Why The Construct:** Your browser-based simulation infrastructure is exactly what we're looking for. We've evaluated the landscape (AWS RoboMaker is shutting down, Gazebo Classic is EOL) and The Construct stands out as the most mature browser-based option with real physics fidelity.

**What we're exploring:**

- Running Viam's server and component modules inside your simulation environments (alongside or instead of ROS)
- Creating custom Gazebo worlds for three work cells: stationary vision, mobile base, and arm + bin picking
- A user flow where Viam users land directly in simulation (not through the course catalog)
- White-label or embedded options for branding continuity

We have detailed technical and business questions, but wanted to first check: is this the kind of partnership you'd be open to discussing?

If so, I'd welcome a call to walk through our use case and understand your platform's flexibility for integration partners.

Best,
[Name]
[Title]
Viam
[email]

---

### Technical Integration

1. **Non-ROS control path:** Can simulated robots be controlled via non-ROS APIs? Viam has its own component APIs (camera, arm, base, gripper). Can we run viam-server alongside or instead of ROS, controlling simulated hardware directly?

2. **Custom modules:** Can we deploy custom code/modules that run inside the simulation environment? Specifically, Viam modules that bridge Gazebo topics to Viam APIs?

3. **Gazebo version:** Which Gazebo version do you run? Classic (EOL) or Harmonic? What's the migration timeline?

4. **Latency:** What's the typical round-trip latency for control commands (browser → simulation → physics update → render → browser)?

5. **Sensor data:** Can we access raw sensor data programmatically (camera frames, lidar scans, depth images) from custom code running in the environment?

### Customization

6. **Custom environments:** Can we create and deploy custom Gazebo world files? We need three specific work cell environments (stationary vision, mobile base, arm + bin picking).

7. **Custom robot models:** Can we use custom robot URDFs/SDFs, or are we limited to pre-configured robots?

8. **Branding:** Can the interface be white-labeled or embedded? Our users would access simulation through Viam's onboarding flow, not The Construct's course platform.

9. **User flow:** Can we bypass the course/learning structure? We want users to land directly in a simulation environment, not navigate through a course catalog.

### Business

10. **Pricing model:** What pricing models are available for an integration partner (vs. individual learners)? Per-user? Per-session-hour? Flat fee?

11. **Volume:** We anticipate [X] concurrent users during onboarding peaks. Can the infrastructure scale? What's the cost curve?

12. **SLA:** What uptime guarantees are available? This would be part of Viam's first-run experience.

13. **Exclusivity:** Would there be any restrictions on Viam also building self-hosted simulation capability?

### Real Robot Labs

14. **Custom hardware:** Can Viam hardware be added to remote robot labs? (Viam-controlled arms, bases running viam-server)

15. **Lab access model:** How does lab access work for integration partners? Time-slotted? On-demand?

### Technical Deep-Dive (if initial answers are positive)

16. **Architecture walkthrough:** Can you share architecture diagrams of how the browser client communicates with the simulation backend?

17. **API documentation:** Is there API documentation for programmatic control of sessions, environments, and simulation state?

18. **Proof of concept:** Would you be open to a technical proof-of-concept where we run viam-server inside your environment and control a simulated robot via Viam APIs?

---

## Appendix B: Self-Hosted Architecture Detail

### System Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Load Balancer                                │
│                    (HTTPS termination, routing)                      │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         │                      │                      │
         ▼                      ▼                      ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Session Mgr    │  │   Web App       │  │  API Gateway    │
│  (orchestration)│  │   (React/etc)   │  │  (auth, routing)│
└────────┬────────┘  └─────────────────┘  └────────┬────────┘
         │                                          │
         │           ┌──────────────────────────────┘
         │           │
         ▼           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Container Orchestration                         │
│                        (Kubernetes / ECS)                            │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    Per-User Pod/Container                       │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │ │
│  │  │  gz-sim    │  │  gzweb     │  │viam-server │  │  nginx   │ │ │
│  │  │  (physics) │  │  (render)  │  │ + modules  │  │ (proxy)  │ │ │
│  │  │            │  │            │  │            │  │          │ │ │
│  │  │ Port 11345 │  │ Port 8080  │  │ Port 8443  │  │ Port 443 │ │ │
│  │  └────────────┘  └────────────┘  └────────────┘  └──────────┘ │ │
│  │                                                                 │ │
│  │  Shared: /worlds, /models, /viam-config                        │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │
│  │ User Session 2  │  │ User Session 3  │  │       ...           │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │   Shared Storage    │
                    │ (worlds, models,    │
                    │  user state, logs)  │
                    └─────────────────────┘
```

### Container Image Contents

```dockerfile
# Base: Ubuntu 22.04 + Gazebo Harmonic
FROM osrf/gazebo:harmonic

# GzWeb for browser visualization
RUN install gzweb dependencies and build

# Viam server
RUN curl -o /usr/local/bin/viam-server https://...
RUN chmod +x /usr/local/bin/viam-server

# Viam Gazebo bridge modules
COPY viam-gazebo-camera /opt/viam/modules/
COPY viam-gazebo-arm /opt/viam/modules/
COPY viam-gazebo-base /opt/viam/modules/
COPY viam-gazebo-gripper /opt/viam/modules/
COPY viam-gazebo-lidar /opt/viam/modules/

# Pre-loaded simulation environments
COPY worlds/stationary-vision.sdf /opt/gazebo/worlds/
COPY worlds/mobile-base.sdf /opt/gazebo/worlds/
COPY worlds/arm-picking.sdf /opt/gazebo/worlds/

# Robot models
COPY models/ /opt/gazebo/models/

# Viam configuration templates
COPY viam-configs/ /opt/viam/configs/

# Startup script
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
```

### Viam Gazebo Bridge Module (Example: Camera)

```
┌─────────────────────────────────────────────────────────────┐
│                   viam-gazebo-camera module                  │
│                                                              │
│  Implements: rdk.component.camera                           │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  GetImage()                                             │ │
│  │    1. Subscribe to Gazebo camera topic                  │ │
│  │    2. Receive rendered frame from gz-sim                │ │
│  │    3. Convert to Viam image format                      │ │
│  │    4. Return to caller                                  │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  GetPointCloud()                                        │ │
│  │    1. Subscribe to Gazebo depth camera topic            │ │
│  │    2. Convert depth image to point cloud                │ │
│  │    3. Return in Viam PCD format                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  Config:                                                     │
│    - gazebo_topic: "/world/default/model/robot/camera"      │
│    - width: 640                                              │
│    - height: 480                                             │
│    - fps: 30                                                 │
└─────────────────────────────────────────────────────────────┘
```

### Session Lifecycle

```
User clicks "Start Simulation"
           │
           ▼
┌─────────────────────────────┐
│  Session Manager            │
│  1. Authenticate user       │
│  2. Check for existing      │
│     session (resume?)       │
│  3. Select work cell type   │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  Provision Container        │
│  1. Pull/create pod         │
│  2. Mount user state volume │
│  3. Inject Viam credentials │
│  4. Start gz-sim + gzweb    │
│  5. Start viam-server       │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  Ready                      │
│  Return WebSocket URL to    │
│  browser for GzWeb stream   │
└──────────────┬──────────────┘
               │
               ▼
     User interacts with sim
               │
               ▼
┌─────────────────────────────┐
│  Idle Detection             │
│  No activity for 15 min?    │
│  → Snapshot state           │
│  → Terminate container      │
│  → Resume on next visit     │
└─────────────────────────────┘
```

### Cost Optimization Strategies

| Strategy | Implementation | Savings |
|----------|----------------|---------|
| Spot/Preemptible instances | Use spot for simulation pods | 60-70% |
| Auto-shutdown idle sessions | Terminate after 15 min inactive | Proportional to idle time |
| Shared base images | Pre-pulled images on nodes | Faster startup, less egress |
| Right-sized instances | Profile actual CPU/memory needs | Avoid over-provisioning |
| Regional placement | Deploy near user concentrations | Lower latency, potentially lower cost |

### Monitoring & Observability

| Metric | Why It Matters |
|--------|----------------|
| Session start latency | User experience—how long to get into sim? |
| Physics step time | Is simulation keeping up with real-time? |
| GzWeb frame rate | Is visualization smooth? |
| Viam API latency | Are control commands responsive? |
| Session duration | Usage patterns, cost forecasting |
| Error rate | Stability |

---

## References

- [The Construct](https://www.theconstruct.ai/)
- [Gazebo Harmonic](https://gazebosim.org/)
- [New GzWeb](https://github.com/gazebo-web/gzweb)
- [Gazebo web visualization](https://gazebosim.org/docs/dome/web_visualization/)
- [DukeRobotics GzWeb Docker](https://github.com/DukeRobotics/gzweb-rosssh)
- [Official Gazebo Docker](https://hub.docker.com/_/gazebo/)

# Simulation Requirements

**Status:** 🔴 Placeholder

---

## Purpose

Technical requirements for browser-based simulation onboarding.

---

## To Be Defined

### Infrastructure Options

1. **GzWeb + CloudSim** — Self-hosted Gazebo in cloud
2. **The Construct** — Third-party platform partnership
3. **Custom WebGL** — Build our own lightweight simulator

### Requirements

- Zero installation for users
- Real-time sensor feeds (camera, lidar)
- Actuator control (base movement, arm movement)
- Integration with Viam services (vision, SLAM, motion)
- Persistent state across sessions
- Reasonable latency for control

### Simulation Environments

- Stationary vision: workbench with objects
- Mobile base: warehouse or office environment
- Arm + vision: bin picking setup

### Viam Integration

- How does simulated hardware connect to Viam?
- Component configuration compatibility
- Data capture from simulation
- Model deployment to simulation

---

## Open Questions

1. Build vs. buy vs. partner?
2. Cost model for hosted simulation?
3. Offline capability?
4. Mobile device support?

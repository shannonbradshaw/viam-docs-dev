# What Problems Viam Solves

**Status:** 🟡 Draft

---

Building a robotics application is hard. Not just the "making a robot move" part—that's the beginning. The real challenges emerge as you move from prototype to production.

This document maps the problems you'll face at each stage and shows where Viam helps.

---

## Stage 1: Prototype

*You're building something that works on your bench.*

### The Problems

**Hardware integration is painful.** Every sensor and actuator has its own SDK, its own quirks, its own incompatibilities. You spend more time debugging drivers than building features.

**Communication protocols are arcane.** I2C, SPI, UART, CAN—each with its own timing, addressing, and failure modes. You didn't sign up to become a protocol expert.

**There's no consistency.** Code for one camera doesn't work with another. Switching motors means rewriting control logic. Everything is bespoke.

### How Viam Helps

Viam provides a **module registry** with pre-built, tested drivers for 200+ components. You configure your hardware—you don't write driver code.

Communication protocols are **abstracted entirely**. You never think about I2C vs. SPI. You configure "this is a motor" and it works.

The same **SDKs and APIs** work across all hardware. Switch cameras? Change one config line. Your code stays the same.

---

## Stage 2: First Deployment

*Your robot leaves the bench and enters the real world.*

### The Problems

**The environment is hostile.** Lighting changes. Temperatures vary. Dust accumulates. Things that worked perfectly on your bench fail mysteriously in the field.

**Network access is complicated.** Your robot is behind a firewall. NAT makes inbound connections impossible. You can't just SSH in.

**You can't see what's happening.** When something goes wrong, you're blind. Logs are on the device. Sensor feeds are inaccessible. Debugging requires physical presence.

### How Viam Helps

**Remote access works through firewalls.** WebRTC handles NAT traversal automatically. No VPN, no port forwarding, no IT department negotiations.

**You can see everything remotely.** Live sensor feeds, component status, and logs—all accessible from the Viam app or your code.

**Configuration pushes from the cloud.** When you need to adjust settings in the field, you don't need to touch the device.

---

## Stage 3: Multiple Units

*You've proven the concept. Now you're deploying 5, 10, 50 robots.*

### The Problems

**Setup doesn't scale.** Manually configuring each device takes hours. Mistakes creep in. Units drift out of sync.

**Hardware is never identical.** Different sensor batches. Different revisions. Subtle variations that break assumptions.

**Updates are terrifying.** Pushing changes to many devices at once? What if something goes wrong? What if you brick the fleet?

### How Viam Helps

**Provisioning is streamlined.** New devices connect to the cloud and pull their configuration automatically.

**Configuration fragments** let you manage variants without code changes. Same application, different hardware—handled in config.

**Staged rollouts** let you push updates to one device, then ten, then all. Rollback if something goes wrong.

---

## Stage 4: Fleet at Scale

*You're operating hundreds or thousands of robots.*

### The Problems

**Visibility is overwhelming.** You can't watch every device. You need to know which ones need attention.

**Updates are high-stakes.** A bad push can take down production. You need confidence before rolling out changes.

**Customers expect dashboards.** They want to see their robots. You need to provide access without building everything from scratch.

### How Viam Helps

**Fleet monitoring** shows health across all devices at a glance. Anomalies surface automatically.

**OTA updates at scale** with staged rollouts, canary deployments, and automatic rollback.

**Multi-tenancy and embedded dashboards** let you give customers access to their own robots.

---

## Stage 5: Ongoing Maintenance

*The fleet is running. Now you maintain it forever.*

### The Problems

**Remote debugging is essential.** You can't dispatch a technician for every issue. You need to diagnose from afar.

**Logs are scattered.** Getting logs off devices with intermittent connectivity is its own infrastructure project.

**Models drift.** The ML model that worked at launch degrades over time. You need to retrain and redeploy.

### How Viam Helps

**Remote log access** with offline buffering. Logs sync when connectivity returns.

**Data pipelines** capture real-world performance continuously. Use it to identify issues and retrain models.

**One-click model deployment** updates ML models across the fleet without touching application code.

---

## Summary

| Stage | Pain | Viam Solution |
|-------|------|---------------|
| Prototype | Hardware integration | Module registry, abstracted protocols |
| Deploy | Remote access | WebRTC, NAT traversal |
| Scale | Configuration management | Fragments, staged rollouts |
| Fleet | Visibility and updates | Monitoring, OTA, multi-tenancy |
| Maintain | Remote debugging | Logs, data capture, model deployment |

---

## What's Next

- [Try Viam](../try/INDEX.md) in simulation—experience the full journey with no hardware
- [Build with Viam](../build/INDEX.md)—modular blocks for your specific use case

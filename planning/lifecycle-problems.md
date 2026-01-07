# Lifecycle Problems Analysis

**Status:** 🟢 Complete

This document maps the problems that emerge when building and operating a robotics application. It includes lifecycle stages (sequential) and cross-cutting capabilities (ongoing).

---

## Lifecycle Stages

### Stage 1: Prototype — Build Something That Works on the Bench

| # | Problem | Viam | Universality | Source |
|---|---------|------|--------------|--------|
| 1.1 | Getting drivers and libraries working | Yes | Universal | Hardware |
| 1.2 | Understanding communication protocols | Yes | Universal | Hardware |
| 1.3 | Writing initial control code | Yes | Universal | Hardware |
| 1.4 | Debugging hardware vs. software issues | Partial | Universal | Hardware |
| 1.5 | Coordinating multiple components | Yes | Universal | Hardware |
| 1.6 | Setting up development environment | Partial | Universal | Hardware |
| 1.7 | Testing safely | No | Variable | Hardware |
| 1.8 | Testing without hardware / simulation | Partial | Variable | Hardware |
| 1.9 | Viewing sensor feeds | Yes | Universal | Remote Access |
| 1.10 | Controlling components interactively | Yes | Universal | Remote Access |
| 1.11 | Sharing access with collaborators | Yes | Variable | Remote Access |
| 1.12 | Capturing sensor data for review/debugging | Yes | Universal | Data/ML |
| 1.13 | Running inference with ML models | Yes | Variable | Data/ML |
| 1.14 | Collecting training data | Yes | Variable | Data/ML |
| 1.15 | Designing robot behavior | No | Universal | App Logic |
| 1.16 | Implementing control logic | Partial | Universal | App Logic |
| 1.17 | Motion planning | Yes | Variable | App Logic |
| 1.18 | Navigation | Yes | Variable | App Logic |
| 1.19 | Integrating perception into action | Partial | Variable | App Logic |
| 1.20 | Handling edge cases and failures | No | Universal | App Logic |
| 1.21 | Testing behavior on real hardware | Partial | Universal | App Logic |

---

### Stage 2: First Deployment — Put It in the Real World

Problems listed are new or change significantly at this stage.

| # | Problem | Viam | Universality | Source |
|---|---------|------|--------------|--------|
| 2.1 | Environment differs from bench | Partial | Universal | Deployment |
| 2.2 | Network connectivity at deployment site | Partial | Universal | Deployment |
| 2.3 | Sensor calibration in situ | Partial | Universal | Deployment |
| 2.4 | Unexpected environmental interactions | Partial | Universal | Deployment |
| 2.5 | Initial configuration and setup on site | Yes | Universal | Deployment |
| 2.6 | Establishing baseline "normal" behavior | Partial | Universal | Deployment |
| 2.7 | Handling failures gracefully | Partial | Variable | Deployment |
| 2.8 | Communicating status to humans | No | Variable | Deployment |
| 2.9 | Network access through firewalls and NATs | Yes | Universal | Remote Access |
| 2.10 | Latency for real-time control | Partial | Variable | Remote Access |
| 2.11 | Handling intermittent connectivity | Yes | Variable | Remote Access |
| 2.12 | Alerts when something goes wrong | Yes | Universal | Remote Access |
| 2.13 | Deciding what data to capture | Yes | Universal | Data/ML |
| 2.14 | Data transfer to cloud | Yes | Universal | Data/ML |
| 2.15 | Iterating based on real-world performance | Partial | Universal | App Logic |
| 2.16 | Handling edge cases discovered in field | No | Universal | App Logic |

---

### Stage 3: Multiple Units — Go from One to Several

| # | Problem | Viam | Universality | Source |
|---|---------|------|--------------|--------|
| 3.1 | Provisioning new devices efficiently | Yes | Universal | Fleet |
| 3.2 | Configuration management | Yes | Universal | Fleet |
| 3.3 | Handling hardware variance | Yes | Universal | Fleet |
| 3.4 | Identifying and tracking individual units | Yes | Universal | Fleet |
| 3.5 | Updating multiple units | Yes | Universal | Fleet |
| 3.6 | Testing changes before broad rollout | Yes | Universal | Fleet |
| 3.7 | Centralizing monitoring | Yes | Universal | Remote Access |
| 3.8 | Troubleshooting individual unit problems | Yes | Universal | Remote Access |
| 3.9 | Managing credentials across units | Partial | Universal | Remote Access |
| 3.10 | Aggregating data across units | Yes | Universal | Data/ML |
| 3.11 | Comparing performance across units | Partial | Universal | Data/ML |
| 3.12 | Coordination between units | No | Variable | App Logic |
| 3.13 | Behavior consistency across hardware variants | Yes | Universal | App Logic |

---

### Stage 4: Fleet at Scale — Manage Many Units in Production

| # | Problem | Viam | Universality | Source |
|---|---------|------|--------------|--------|
| 4.1 | Fleet health monitoring | Yes | Universal | Fleet |
| 4.2 | Alerting on anomalies | Partial | Universal | Fleet |
| 4.3 | OTA updates at scale | Yes | Universal | Fleet |
| 4.4 | Staged and progressive rollouts | Yes | Universal | Fleet |
| 4.5 | Rollback when updates break things | Yes | Universal | Fleet |
| 4.6 | Configuration drift detection | Yes | Universal | Fleet |
| 4.7 | Compliance and security at scale | Partial | Variable | Fleet |
| 4.8 | Billing and metering | Partial | Variable | Fleet |
| 4.9 | Multi-tenancy | Yes | Variable | Fleet |
| 4.10 | End-user access and dashboards | Yes | Variable | Remote Access |
| 4.11 | SLAs and reliability | Partial | Variable | Fleet |
| 4.12 | Capacity planning | Partial | Universal | Fleet |
| 4.13 | Geographic distribution | Partial | Variable | Fleet |
| 4.14 | Integration with existing enterprise systems | Partial | Variable | App Logic |
| 4.15 | A/B testing models across fleet | Yes | Variable | Data/ML |
| 4.16 | Cost management for data and compute | Partial | Universal | Data/ML |

---

### Stage 5: Ongoing Maintenance — Updates, Debugging, Iteration

| # | Problem | Viam | Universality | Source |
|---|---------|------|--------------|--------|
| 5.1 | Diagnosing issues remotely | Yes | Universal | Remote Access |
| 5.2 | Accessing logs from field devices | Yes | Universal | Remote Access |
| 5.3 | Reproducing reported issues | Partial | Universal | Data/ML |
| 5.4 | Pushing hotfixes quickly | Yes | Universal | Fleet |
| 5.5 | Hardware failures and replacement | Partial | Universal | Fleet |
| 5.6 | Keeping system software up to date | Partial | Universal | Fleet |
| 5.7 | Security patching | Partial | Universal | Fleet |
| 5.8 | Performance degradation over time | Partial | Universal | Data/ML |
| 5.9 | Component obsolescence | Partial | Universal | Hardware |
| 5.10 | End-of-life and decommissioning | Partial | Universal | Fleet |
| 5.11 | Continuous improvement of behavior | Partial | Universal | App Logic |
| 5.12 | Model drift and retraining | Partial | Variable | Data/ML |

---

## Summary: Viam Coverage by Stage

| Stage | Yes | Partial | No | Total |
|-------|-----|---------|-----|-------|
| 1. Prototype | 13 | 5 | 3 | 21 |
| 2. First Deployment | 7 | 7 | 2 | 16 |
| 3. Multiple Units | 10 | 2 | 1 | 13 |
| 4. Fleet at Scale | 9 | 7 | 0 | 16 |
| 5. Ongoing Maintenance | 4 | 8 | 0 | 12 |
| **Total** | **43** | **29** | **6** | **78** |

---

## Onboarding Candidates

For an effective onboarding experience, we want problems that are:
1. **Universal** — Apply across application categories
2. **Early-stage** — Occur in Stage 1 or Stage 2
3. **Viam solves well** — Coverage is "Yes"
4. **Demonstrable** — Can be shown without extensive hardware or deployment

### Stage 1 Candidates (Universal + Yes)

| # | Problem | Source |
|---|---------|--------|
| 1.1 | Getting drivers and libraries working | Hardware |
| 1.2 | Understanding communication protocols | Hardware |
| 1.3 | Writing initial control code | Hardware |
| 1.5 | Coordinating multiple components | Hardware |
| 1.9 | Viewing sensor feeds | Remote Access |
| 1.10 | Controlling components interactively | Remote Access |
| 1.12 | Capturing sensor data for review/debugging | Data/ML |

### Stage 2 Candidates (Universal + Yes)

| # | Problem | Source |
|---|---------|--------|
| 2.5 | Initial configuration and setup on site | Deployment |
| 2.9 | Network access through firewalls and NATs | Remote Access |
| 2.12 | Alerts when something goes wrong | Remote Access |
| 2.13 | Deciding what data to capture | Data/ML |
| 2.14 | Data transfer to cloud | Data/ML |

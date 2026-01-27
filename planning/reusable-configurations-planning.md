# Planning: "Reusable Configurations" Document

**Target location:** `understand/reusable-configurations.md`
**Status:** Research Complete, Outline Refined
**Last updated:** 2026-01-27

---

## Overview

This document tracks the planning and research for an "Understand" section article explaining Viam's fragment-based reusable configuration system. The document will provide conceptual grounding for software engineers new to robotics, focusing on the "why" rather than the "how."

---

## Phase 1: Research

### 1.1 Gap Analysis: Current Viam Documentation
**Goal:** Understand what's already documented to avoid duplication and identify what explanation is missing

- [x] Review the official fragments documentation at docs.viam.com
- [x] Identify what's covered (likely: how-to mechanics) vs. what's missing (likely: conceptual framing, decision guidance)
- [x] Note terminology and conventions to maintain consistency

### 1.2 Competitive/Analogous Concepts
**Goal:** Find familiar mental models for the target audience (software engineers)

Research how similar problems are solved in:
- [x] **Infrastructure-as-Code**: Terraform modules, Pulumi components
- [x] **Container orchestration**: Kubernetes ConfigMaps, Helm charts, Kustomize overlays
- [x] **Configuration management**: Ansible roles, Chef cookbooks, Puppet modules
- [x] **Other robotics platforms**: ROS launch files, ROS 2 composition

This helps frame fragments using concepts the target audience already knows.

### 1.3 Real-World Fragment Patterns
**Goal:** Ground the explanation in practical scenarios

- [x] Look for public fragments in the Viam Registry
- [x] Find case studies or blog posts showing fragment usage
- [x] Review the air quality fleet tutorial and chess demo for patterns
- [x] Identify common fragment structures (sensor configs, data pipelines, full robot configs)

### 1.4 Limitations and Boundaries
**Goal:** Understand what fragments can't do, so we can set accurate expectations

- [x] What resources can't be included in fragments?
- [x] What are the failure modes? (version conflicts, circular dependencies)
- [x] When should you NOT use fragments?

### 1.5 Internal docs-dev Context
**Goal:** Ensure alignment with existing content strategy

- [x] Re-read `/planning/target-user.md` for audience framing
- [x] Re-read `/planning/lifecycle-problems.md` to map fragment benefits to specific problems
- [x] Check `/planning/content-guidelines.md` for style requirements

---

## Phase 2: Initial Outline (Pre-Research)

This outline reflects current understanding. It will be refined after research.

```
# Reusable Configurations

## The Configuration Challenge
- Why robot configuration is harder than typical software configuration
- The scale problem: one machine is easy, 100 machines is a nightmare
- Configuration drift and its consequences

## What Fragments Enable
- Define once, deploy everywhere
- Update centrally, propagate automatically
- Customize without forking (overrides)
- Version and roll out safely

## How Fragments Work (Conceptual)
- Fragments as composable configuration blocks
- The relationship: Organization → Fragment → Machine
- What can (and can't) go in a fragment

## When to Use Fragments
- Single machine vs. fleet decision point
- Identical machines vs. similar-but-different
- Development vs. production configurations

## Fragment Patterns
- The "golden config" pattern (full machine template)
- The "component library" pattern (reusable pieces)
- The "environment overlay" pattern (dev/staging/prod)

## Customization Strategies
- Variables for parameterization
- Overrides for per-machine tweaks
- When to fork vs. when to override

## Versioning and Rollouts
- Why version control matters for hardware
- Staged rollout strategies
- Rolling back safely

## Fragments in Your Workflow
- Where fragments fit in the development lifecycle
- Fragments + modules: configuration vs. code
- Team collaboration patterns
```

---

## Phase 3: Outline Refinement

After completing research:
1. Adjust sections based on what the official docs already cover well
2. Add analogies to familiar tools (Terraform, Helm, etc.) where helpful
3. Incorporate real examples discovered in research
4. Add specific lifecycle problem mappings
5. Remove or condense sections that don't serve the target audience

---

## Phase 4: Draft and Review

1. Write first draft following content guidelines
2. Ensure "why" focus (explanation, not how-to)
3. Cross-reference to Build blocks for the "how"
4. Review against target user profile

---

## Research Findings

### 1.1 Gap Analysis Findings

**Current Viam documentation coverage:**

| Aspect | Coverage Level | Notes |
|--------|----------------|-------|
| Fragment creation | ✅ Thorough | Step-by-step UI instructions |
| Fragment deployment | ✅ Thorough | Adding to machines, variable substitution |
| Fragment modification | ✅ Thorough | `fragment_mods` with MongoDB operators |
| Versioning & tags | ✅ Good | Version pinning, tag-based management |
| Variable templating | ✅ Good | `$variable` syntax documented |
| **Conceptual framing** | ❌ Missing | No "why fragments matter" explanation |
| **Decision guidance** | ❌ Missing | No "when to use fragments" guidance |
| **Mental models** | ❌ Missing | No analogies to familiar tools |
| **Scalability considerations** | ❌ Missing | No guidance for large fleets |
| **Conflict resolution** | ❌ Sparse | Nested fragment interactions unclear |
| **Fleet-wide rollback** | ❌ Missing | Only individual machine rollback shown |

**Tone analysis:** Decidedly procedural. Uses imperative language ("Go to," "Click," "Add") with step numbering. Minimal explanation of *why* fragments solve problems.

**Key terminology to maintain:**
- "Fragment" (not "template" or "blueprint")
- "Fragment overwrites" / "fragment_mods"
- "Variables" for parameterization
- "Prefix" for namespace collision prevention

**Gap our document should fill:** The "why" and "when" — conceptual understanding that makes the procedural docs actionable.

### 1.2 Analogous Concepts Findings

**Terraform Modules:**
- Encapsulate configurations into reusable components
- Isolate resource names to avoid naming confusion
- Allow sharing between projects
- **Key analogy:** "Fragments are like Terraform modules for robot hardware"

**Helm Charts:**
- Package applications as charts with all necessary manifests
- Sub-charts provide modularity (stand-alone, don't depend on parent)
- Focus on application logic, not infrastructure details
- **Key analogy:** "Fragments package machine configurations like Helm packages Kubernetes apps"

**Kustomize (Most Relevant Pattern):**
- Base + Overlays architecture
- Base contains common configuration shared across all environments
- Overlays apply environment-specific changes without duplicating files
- Follows DRY principle, reduces configuration drift
- **Key analogy:** "Fragments are like Kustomize bases; fragment_mods are like overlays"

**ROS 2 Launch Files:**
- Describe system configuration and execute as described
- Make it easy to reuse components with different configurations
- Use YAML configuration files for fleet adapters
- **Key insight:** ROS ecosystem lacks centralized fleet configuration management — Viam fragments solve a gap ROS users experience

**Common pattern across all tools:**
- Define shared configuration once (DRY)
- Customize per-environment/per-machine without forking
- Version control configurations
- Centralized updates propagate downstream

### 1.3 Real-World Patterns Findings

**Viam Rover Fragments:**
- Official fragments for Viam rovers (e.g., `ViamRover2-2024-rpi5`)
- Configure board, motors, base, camera as a complete unit
- Demonstrates "golden config" pattern — full machine template

**Air Quality Fleet Tutorial:**
- Fragment named `air-quality-configuration`
- Contains PM sensor + data management service
- Provisioning via `viam-defaults.json` with `fragment_id`
- Demonstrates zero-touch provisioning pattern

**Chess Demo (viam-chess):**
- Fragment + modules pattern
- Configuration (hardware specifics) separated from code (application logic)
- Quote: "Deploy to a new machine by providing new variable values, not by editing source files"
- Demonstrates hardware abstraction through fragments

**Identified fragment patterns:**

| Pattern | Description | Example |
|---------|-------------|---------|
| **Golden Config** | Complete machine template | Viam Rover fragment |
| **Component Library** | Reusable pieces to compose | Camera + data management |
| **Hardware Variant** | Same app, different hardware | Fragment with camera overwrites |
| **Provisioning Template** | Zero-touch device setup | Air quality fleet |

### 1.4 Limitations Findings

**Resources that cannot be in fragments:**
- Triggers (confirmed in docs)
- Nested fragments have some limitations

**Failure modes:**
- Fragment overwrites fail entirely rather than partially apply (prevents partial deployments)
- Limited `fragment_mods` operators: only `$set`, `$unset`, `$rename` (no `$setOnInsert`, array operators)
- Provisioning script cannot be re-run once started

**When NOT to use fragments:**
- Single machine that won't be replicated
- Highly unique configurations with no shared elements
- When machines need fundamentally different architectures (not just parameter differences)

**Configuration drift considerations:**
- Fragments help *prevent* drift by establishing centralized source of truth
- Fragments help *detect* drift because changes must go through fragment updates
- But: Manual overwrites can introduce drift if not properly managed

### 1.5 Internal Context Findings

**Target user profile (from target-user.md):**
- Software engineer founding/cofounding robotics startup
- Strong software background, limited robotics experience
- Knows: Cloud infrastructure, software development practices
- Doesn't know: What's hard about robotics at scale
- Key question: "What problems will I face as I scale?"

**Design implications for our document:**
- Zero robotics jargon assumed
- Must connect to familiar software concepts (Terraform, Helm, etc.)
- Must show full lifecycle value, not just immediate utility
- Value must be immediate — can't rely on "you'll appreciate this at scale"

**Lifecycle problems fragments address (from lifecycle-problems.md):**

| Stage | Problem # | Problem | How Fragments Help |
|-------|-----------|---------|-------------------|
| 3 | 3.1 | Provisioning new devices efficiently | Template-based provisioning |
| 3 | 3.2 | Configuration management | Centralized source of truth |
| 3 | 3.3 | Handling hardware variance | Fragment overwrites |
| 3 | 3.5 | Updating multiple units | Central update propagation |
| 3 | 3.6 | Testing changes before broad rollout | Version pinning, tags |
| 3 | 3.13 | Behavior consistency across hardware variants | Shared configuration base |
| 4 | 4.3 | OTA updates at scale | Fragment versioning |
| 4 | 4.4 | Staged and progressive rollouts | Tags (stable, beta) |
| 4 | 4.5 | Rollback when updates break things | Pin to previous version |
| 4 | 4.6 | Configuration drift detection | Centralized fragment tracking |

**Content guidelines alignment:**
- "Understand" section = Explanation-oriented (the "why")
- Should not duplicate procedural content from Build blocks
- Can include brief conceptual examples but not full tutorials
- Should link to Build blocks for the "how"

---

## Refined Outline

Based on research findings, here is the refined outline. Changes from the initial outline are noted.

```
# Reusable Configurations with Fragments

## Introduction
- Brief: What are fragments? (one paragraph)
- The promise: Define once, deploy everywhere, update centrally

## The Problem Fragments Solve
[Expanded from "The Configuration Challenge" - now grounded in lifecycle problems]

- Robot configuration is infrastructure-as-code for physical systems
- The scale problem: configuration drift, manual errors, update coordination
- Map to lifecycle problems: 3.1, 3.2, 3.3, 3.5 (provisioning, management, variance, updates)
- What happens without centralized configuration (cautionary framing)

## If You Know Terraform, Helm, or Kustomize
[NEW SECTION - addresses target user's software background]

- Fragments are Viam's answer to the same problems these tools solve
- Quick comparison table: Terraform modules, Helm charts, Kustomize bases
- Key similarity: DRY principle, overlays/customization, version control
- Key difference: Fragments are for physical machines, not cloud resources

## Core Capabilities
[Renamed from "What Fragments Enable" - more concrete]

### Define Once, Deploy Everywhere
- Fragment as single source of truth
- Adding a fragment to a machine
- Nested fragments for composition

### Customize Without Forking
- Variables for parameterization (conceptual, not syntax)
- Overwrites for per-machine differences
- The spectrum: identical → similar → different (decision framework)

### Update Centrally, Propagate Automatically
- How updates flow to machines
- The offline behavior (machines cache configs)
- Version pinning for stability

### Roll Out Safely
- Tags for release channels (stable, beta, canary)
- Staged rollouts: test on subset before fleet-wide
- Rollback by pinning to previous version

## Fragment Patterns
[Kept from initial outline - now with research-backed examples]

### The Golden Config
- Complete machine template
- Example: Viam Rover fragments
- When to use: Identical hardware across fleet

### The Component Library
- Reusable building blocks
- Example: Camera + data pipeline fragment
- When to use: Mix-and-match hardware configurations

### The Hardware Variant
- Same application, different hardware
- Example: Fragment with overwrites for camera differences
- When to use: Fleet with hardware variations

### The Provisioning Template
- Zero-touch device setup
- Example: Air quality fleet with viam-agent
- When to use: Shipping pre-configured devices to customers

## When to Use Fragments
[Kept from initial outline - now with clearer decision criteria]

### Good Fit
- Two or more machines with shared configuration
- Need to update multiple machines simultaneously
- Hardware variance that can be expressed as parameter differences
- Shipping devices to customers or remote sites

### Not a Fit
- Single prototype machine (just configure directly)
- Machines with fundamentally different architectures
- Configuration that changes more often than it's shared

### The "When Does One Become Many?" Question
- Addressing the lifecycle transition from Stage 2 to Stage 3
- Creating your first fragment from a working machine

## Fragments in Your Workflow
[Kept but condensed - focuses on mental model, not procedure]

- Where fragments fit: between module code and individual machine
- The separation: Code handles logic, fragments handle hardware specifics
- Team patterns: Who owns the fragment? How do changes get reviewed?

## Limitations and Boundaries
[NEW SECTION - sets accurate expectations]

- What can't go in fragments (triggers)
- Overwrites are all-or-nothing (no partial application)
- When overwrites become too complex, create a new fragment

## What's Next
- Link to Build block: Create Your First Fragment
- Link to Build block: Customize a Fragment with Overwrites
- Link to Reference: Fragment JSON Schema
```

### Key Changes from Initial Outline

| Change | Rationale |
|--------|-----------|
| Added "If You Know Terraform/Helm/Kustomize" section | Target user has software background; leverage existing mental models |
| Removed "How Fragments Work (Conceptual)" as separate section | Woven throughout other sections to avoid abstract explanation |
| Added research-backed examples to Fragment Patterns | Ground concepts in real Viam examples |
| Added "Limitations and Boundaries" section | Set accurate expectations; discovered in research |
| Condensed "Versioning and Rollouts" into "Core Capabilities" | Avoid separate section for one capability |
| Added "When Does One Become Many?" subsection | Addresses key lifecycle transition point |
| Added explicit "What's Next" links | Per content guidelines, link to Build blocks for "how" |

---

## Open Questions

1. ~~Should this document be titled "Reusable Configurations" or "Fragments"?~~
   **Decision:** Title as "Reusable Configurations with Fragments" — leads with the concept (reusability) and introduces the term (fragments). This matches how target users think ("I need to reuse config") before they know the Viam terminology.

2. ~~How much technical detail is appropriate for an "Understand" article?~~
   **Decision:** Conceptual explanations with minimal JSON. Show *structure* of fragments when helpful, but never procedural steps. Per Diataxis: Explanation is understanding-oriented, not information-oriented.

3. ~~Should we include JSON examples, or keep it purely conceptual?~~
   **Decision:** Include 1-2 minimal JSON snippets to make concepts concrete, but annotate them conceptually ("notice the variable here") rather than procedurally ("copy this into your config"). Link to Build blocks for full examples.

4. **NEW:** How should we handle the Kustomize analogy depth?
   **Open:** Kustomize base+overlay pattern maps very well to fragment+overwrites. Should we develop this analogy in depth, or keep it brief? Risk of over-explaining for users who don't know Kustomize.

5. **NEW:** Should we include a "Fragments vs. Modules" comparison?
   **Open:** Chess demo shows fragments + modules working together. Users may be confused about when to put logic in a module vs. configuration in a fragment. May warrant a subsection or callout box.

---

## References

**Viam Documentation:**
- [Reuse Machine Configuration (Fragments)](https://docs.viam.com/manage/fleet/reuse-configuration/)
- [Air Quality Fleet Tutorial](https://docs.viam.com/tutorials/control/air-quality-fleet/)
- [Manage a Fleet of Machines](https://docs.viam.com/how-tos/manage-fleet/)
- [Device Provisioning with viam-agent](https://docs.viam.com/manage/fleet/provision/setup/)
- [Viam Rover Fragment Tutorial](https://docs.viam.com/dev/reference/try-viam/rover-resources/rover-tutorial-fragments/)

**Analogous Tools (for mental model framing):**
- [Terraform Modules](https://developer.hashicorp.com/terraform/language/modules)
- [Helm Charts](https://helm.sh/docs/topics/charts/)
- [Kustomize Overlays](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/)
- [ROS 2 Launch System](https://design.ros2.org/articles/roslaunch.html)

**Configuration Drift (background context):**
- [Spacelift: What is Configuration Drift?](https://spacelift.io/blog/what-is-configuration-drift)
- [Snyk: Detect and Prevent Configuration Drift](https://snyk.io/articles/infrastructure-as-code-iac/detect-prevent-configuration-drift/)

**Internal docs-dev:**
- `/planning/target-user.md`
- `/planning/lifecycle-problems.md`
- `/planning/content-guidelines.md`
- `/demos/viam-chess/index.md`

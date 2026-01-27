# Planning: "Reusable Configurations" Document

**Target location:** `understand/reusable-configurations.md`
**Status:** Planning
**Last updated:** 2026-01-27

---

## Overview

This document tracks the planning and research for an "Understand" section article explaining Viam's fragment-based reusable configuration system. The document will provide conceptual grounding for software engineers new to robotics, focusing on the "why" rather than the "how."

---

## Phase 1: Research

### 1.1 Gap Analysis: Current Viam Documentation
**Goal:** Understand what's already documented to avoid duplication and identify what explanation is missing

- [ ] Review the official fragments documentation at docs.viam.com
- [ ] Identify what's covered (likely: how-to mechanics) vs. what's missing (likely: conceptual framing, decision guidance)
- [ ] Note terminology and conventions to maintain consistency

### 1.2 Competitive/Analogous Concepts
**Goal:** Find familiar mental models for the target audience (software engineers)

Research how similar problems are solved in:
- [ ] **Infrastructure-as-Code**: Terraform modules, Pulumi components
- [ ] **Container orchestration**: Kubernetes ConfigMaps, Helm charts, Kustomize overlays
- [ ] **Configuration management**: Ansible roles, Chef cookbooks, Puppet modules
- [ ] **Other robotics platforms**: ROS launch files, ROS 2 composition

This helps frame fragments using concepts the target audience already knows.

### 1.3 Real-World Fragment Patterns
**Goal:** Ground the explanation in practical scenarios

- [ ] Look for public fragments in the Viam Registry
- [ ] Find case studies or blog posts showing fragment usage
- [ ] Review the air quality fleet tutorial and chess demo for patterns
- [ ] Identify common fragment structures (sensor configs, data pipelines, full robot configs)

### 1.4 Limitations and Boundaries
**Goal:** Understand what fragments can't do, so we can set accurate expectations

- [ ] What resources can't be included in fragments?
- [ ] What are the failure modes? (version conflicts, circular dependencies)
- [ ] When should you NOT use fragments?

### 1.5 Internal docs-dev Context
**Goal:** Ensure alignment with existing content strategy

- [ ] Re-read `/planning/target-user.md` for audience framing
- [ ] Re-read `/planning/lifecycle-problems.md` to map fragment benefits to specific problems
- [ ] Check `/planning/content-guidelines.md` for style requirements

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
*To be completed*

### 1.2 Analogous Concepts Findings
*To be completed*

### 1.3 Real-World Patterns Findings
*To be completed*

### 1.4 Limitations Findings
*To be completed*

### 1.5 Internal Context Findings
*To be completed*

---

## Refined Outline

*To be developed after research completion*

---

## Open Questions

1. Should this document be titled "Reusable Configurations" or "Fragments"? (Need to consider SEO and user mental models)
2. How much technical detail is appropriate for an "Understand" article?
3. Should we include JSON examples, or keep it purely conceptual?

---

## References

- [Viam Fragments Documentation](https://docs.viam.com/manage/fleet/reuse-configuration/)
- [Air Quality Fleet Tutorial](https://docs.viam.com/tutorials/control/air-quality-fleet/)
- `/planning/target-user.md`
- `/planning/lifecycle-problems.md`
- `/planning/content-guidelines.md`

# Stationary Vision Tutorial - TODOs

> **Status:** This tutorial is under active development. Track progress here.

---

## Outstanding Work

### High Priority

- [ ] **Part 3 & 4 (Python version)** - Create Python versions of control logic tutorial
  - `part3-python.md` - Build the Inspector (detection + rejection, CLI testing)
  - `part4-python.md` - Deploy as a Module (DoCommand, resource interface, deployment)
  - Mirror the Go structure (incremental, CLI-first, explanations after code)
  - Update index.md to link both versions

- [ ] **Simulation rejector** - The simulation's air jet rejector is visual only (doesn't actually work)
  - Either implement working rejection in Gazebo OR
  - Update tutorial to clarify we're using a `fake` motor for testing

### Medium Priority

- [ ] **Screenshots** - Add screenshots where indicated by `[SCREENSHOT: ...]` placeholders
  - Part 1: Machine online status, camera config, test panel, vision service test
  - Part 2: Data capture config, trigger config, data tab, query page
  - Part 3: Code sample tab (machine address)
  - Part 5: JSON config, fragment editor, fleet view
  - Part 6: Teleop dashboard, custom dashboard, branded login

- [ ] **ML model** - Create and upload `can-defect-detection` model to registry
  - Currently referenced but doesn't exist
  - Need training data from simulation
  - Or use a placeholder/mock for tutorial purposes

- [ ] **Test end-to-end** - Run through entire tutorial to verify all steps work
  - Build Docker image
  - Complete Parts 1-6
  - Note any friction points

### Low Priority

- [ ] **Part 6 alerting section** - Add section on programmatic alerts for FAIL detections
  - Currently has a TODO comment in the file
  - Query data for FAILs, send notifications

- [ ] **Troubleshooting expansion** - Add common errors and solutions
  - Module won't start
  - Camera topic not found
  - Dependencies not found

- [ ] **Code repository** - Create standalone repo with complete working code
  - `inspection-module/` with Go code
  - Can be cloned as reference or starting point

---

## Completed

- [x] **Part 3 restructure** - Reorganized from code dump to incremental tutorial (Go version)
- [x] **Remove Python from Part 3** - Temporarily Go-only until Python version created
- [x] **Split Part 3 into Parts 3 & 4** - Separated "Build the Inspector" from "Deploy as a Module"
- [x] **Add milestones to Part 3** - Added Milestone 1 (Detection) and Milestone 2 (Full Loop)
- [x] **Renumber Parts 4-5 to Parts 5-6** - Scale and Productize moved up
- [x] **Update index.md** - Adjusted time estimates, section outline, part numbers

---

## Notes

### Part 3/4 Language Split Approach

Rather than using tabs (which doubles visible code), we'll have separate files:
- `part3.md` / `part4.md` - Go implementation (current)
- `part3-python.md` / `part4-python.md` - Python implementation (to be created)

Index will link to both with clear labels. This keeps each version focused and readable.

### New Tutorial Structure

| Part | Title | Time | Focus |
|------|-------|------|-------|
| 1 | Vision Pipeline | ~15 min | Camera, ML model, vision service |
| 2 | Data Capture | ~15 min | Capture, sync, alerts |
| 3 | Build the Inspector | ~20 min | Detection + rejection logic, CLI testing |
| 4 | Deploy as a Module | ~20 min | DoCommand, resource interface, deployment |
| 5 | Scale | ~10 min | Fragments, fleet management |
| 6 | Productize | ~10 min | Dashboard, white-label auth |

Total: ~90 min

### Simulation Limitations

The Gazebo simulation has these limitations that affect the tutorial:
- Rejection mechanism is visual only (air jet doesn't push cans)
- Defects are color patches, not geometric deformations
- No depth camera

Tutorial should acknowledge these where relevant rather than pretend it's fully realistic.

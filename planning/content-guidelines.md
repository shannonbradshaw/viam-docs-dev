# Content Guidelines

**Status:** 🟡 Draft

Guidelines for authors implementing content from this documentation plan.

---

## Blocks

Blocks are modular tutorials that can be composed into larger workflows. Each block should:

- Be self-contained (~15-30 minutes)
- Work in simulation AND real hardware
- Have clear prerequisites and outcomes
- Map to specific problems from the lifecycle analysis

Each block should be completable by a reader who arrives directly at that block, without having worked through prior blocks. This means providing everything they need within the block itself.

### What "Everything They Need" Includes

| Element | Description |
|---------|-------------|
| **Conceptual context** | Why this matters, what problem it solves |
| **Prerequisites state** | The configuration and code state needed to begin |
| **Step-by-step instructions** | The actual tutorial content |
| **Working code samples** | Complete, copy-paste-able code |
| **Verification** | How to confirm it worked |
| **Troubleshooting** | Common failures and how to resolve them |

### Challenges and Solutions

| Challenge | Problem | Solution |
|-----------|---------|----------|
| **Configuration state** | "Detect Objects (2D)" assumes a camera and vision service exist. Do we repeat camera setup? | Provide a "start here" fragment for each block. Reader applies the fragment and has the prerequisite configuration. |
| **Code state** | Block B extends code from Block A. Do we repeat Block A's code? | Provide starter code or a GitHub repo with checkpoints. Each block links to its starting point. |
| **Conceptual dependencies** | Can you explain "Track Objects Across Frames" without the reader understanding detections? | Brief recap, not re-teaching. One paragraph: "This block assumes you can get detections—a list of bounding boxes with labels and confidence scores." |
| **Length vs. self-containment** | Fully self-contained blocks might exceed the 15-30 minute target. | Use fragments and starter code to handle setup. The block itself focuses on the new material. |
| **Simulation environments** | Reader needs a working environment to start. | Provide pre-configured simulation environments per block. |

### Troubleshooting Deserves Special Attention

A reader who worked through prior blocks has context: "I just configured the camera, so if detections aren't working, maybe the camera config is wrong."

A reader who dropped into a block directly has no such context. They applied a fragment and starter code—if something doesn't work, they don't know where to look.

**Each block needs independent troubleshooting guidance.** Don't assume the reader knows what might be broken. Common patterns:

- "If you see X, check Y"
- "Verify the camera is streaming by..."
- "Confirm the model loaded by..."

---

## Diataxis Alignment

Our content maps to the [Diataxis framework](https://diataxis.fr/):

| Diataxis Type | Purpose | Our Content |
|---------------|---------|-------------|
| **Tutorial** | Learning-oriented, guided journey | Try (simulations), Work Cell Guides |
| **How-to Guide** | Task-oriented, solve specific problem | Build blocks, Deploy/Scale/Maintain |
| **Explanation** | Understanding-oriented, the "why" | Understand section |
| **Reference** | Information-oriented, lookup | Reference section |

### Blocks: Tutorial or How-to?

Our blocks straddle the line. They're titled like how-to guides ("Add a Camera") but structured like mini-tutorials (prerequisites, learning outcomes, steps).

This is intentional. Our target user (software engineer, new to robotics) needs both: they're learning *and* trying to accomplish tasks.

**Key distinction:**
- **Tutorials** assume the reader doesn't know what they need
- **How-to guides** assume they do

Our simulation paths (Try) assume nothing—they're true tutorials. Our blocks assume the reader chose that block for a reason—they're closer to how-to guides.

---

## Writing Style

*To be developed: voice, tone, etc.*

---

## Code Samples

### Language Requirements

All control logic code must be provided in both **Python** and **Go**.

- Use tabbed code blocks so readers can switch between languages
- Both versions should be functionally equivalent
- Both must be tested and complete (copy-paste-able)

### What Counts as "Control Logic"

Code that interacts with Viam APIs to control or read from components:

- Getting camera images
- Running detections
- Moving arms/bases
- Reading sensor data
- Sending commands

### What Doesn't Need Both Languages

- Shell commands (e.g., `viam module upload`)
- Configuration snippets (JSON)
- One-off debugging scripts

---

## Content Checklist

Before considering a block complete, verify:

- [ ] Can be completed without prior blocks (using provided fragment + starter code)
- [ ] Conceptual context explains why this matters
- [ ] All control logic code provided in both Python and Go
- [ ] All code samples are complete and tested
- [ ] Verification step confirms success
- [ ] Troubleshooting covers common failures
- [ ] Works in both simulation and real hardware (or clearly states which)
- [ ] Stays within ~15-30 minute target
- [ ] Links to logical next blocks

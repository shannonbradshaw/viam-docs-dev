# Target User Definition

**Status:** 🟢 Complete

---

## Primary Target User

**Software engineer founding or cofounding a robotics startup**

### Characteristics

| Attribute | Description |
|-----------|-------------|
| **Role** | Founder, cofounder, or early technical hire |
| **Team size** | 1-4 people |
| **Stage** | Less than 1 year into the idea |
| **Technical background** | Software engineering; limited robotics experience |
| **Domain knowledge** | Deep understanding of their specific problem/market |
| **Hardware status** | Likely has begun prototyping; may or may not have hardware yet |
| **Evaluation mode** | Exploring Viam among other software solutions |

### What They Know

- Their problem domain deeply (warehouse operations, agriculture, food service, etc.)
- Software development practices
- Cloud infrastructure concepts
- How to evaluate software tools

### What They Don't Know (Yet)

- Robotics hardware specifics (motor controllers, sensor protocols)
- ROS ecosystem and its tradeoffs
- What's hard about robotics at scale
- How their prototype will behave in the real world

### What They're Trying to Figure Out

- "Can I build my product idea on Viam?"
- "What's the fastest path to a working prototype?"
- "What problems will I face as I scale?"
- "How does Viam compare to ROS / building from scratch?"

---

## Secondary Considerations

### Application Breadth

The onboarding experience should resonate across a broad range of robotics applications:

- Warehouse/logistics AMRs
- Delivery robots
- Agricultural automation
- Food service
- Quality inspection
- Security/patrol
- Manufacturing automation

No single vertical should be assumed.

### Hardware Situation

Users may arrive with:
- No hardware yet
- Hardware they're evaluating
- Hardware they've already started prototyping with
- A mix of components from different vendors

The onboarding must work for all of these starting points.

---

## Design Implications

1. **Zero-hardware path required** — Simulation-based onboarding for users without hardware
2. **Full lifecycle visibility** — Show what problems they'll face at each stage, even if they're at Stage 1
3. **No robotics jargon assumed** — Explain concepts software engineers may not know
4. **Value must be immediate** — Can't rely on "you'll appreciate this at scale"
5. **Modular content** — Different users need different blocks based on their application
6. **Quick to compare** — Make it easy to evaluate Viam vs. alternatives

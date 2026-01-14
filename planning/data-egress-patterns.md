# Data Egress Patterns

**Status:** 🔴 Planning Note

This document captures context and requirements for data egress documentation, based on real customer discussions.

---

## Background: Representative Use Case

A customer building autonomous watercraft has a complex telemetry surface:

- **Volume:** Sensors sampling from 1 Hz to 1 kHz
- **Latency tiers:**
  - Safety-critical signals need near-real-time delivery for alerting
  - Diagnostic telemetry needs low-latency access for remote debugging
  - Performance data can be captured at high resolution but doesn't need real-time streaming
- **Architecture constraint:** They've changed telematics providers twice due to compliance issues. They want vendor responsibility confined to the ingestion layer, with their own infrastructure as the system of record.

**Their core ask:** "Guidance on the most efficient and cost-effective ways to get data from the Viam cloud into our own infrastructure with minimal latency."

---

## Data Egress Patterns

Four patterns emerged from this discussion:

| Pattern | Mechanism | Latency | Best For |
|---------|-----------|---------|----------|
| **Webhooks** | Viam POSTs to your endpoint | Near-real-time | Event-driven alerts, notifications |
| **Direct MongoDB capture** | Raw data writes to your cluster | Batch (sync intervals) | "I want to own my data," vendor lock-in mitigation |
| **Data Pipelines** | Transform within Viam | N/A (internal) | Roll-ups, aggregations, cost control |
| **API/SDK queries** | You pull from Viam | On-demand | Dashboards, bulk export, ad-hoc analysis |

### Pattern Details

**Webhooks**
- HTTPS POST to customer endpoint, retried on failure
- Good for: safety-critical alerting, real-time notifications
- Already covered in "Trigger on Detection" block for vision use cases
- Can also push aggregated data (advanced pattern)

**Direct MongoDB Capture**
- Data writes directly to customer's MongoDB cluster instead of Viam cloud storage
- Customer handles roll-ups and retention on their side
- Minimizes vendor coupling at the storage layer
- Good for: compliance requirements, existing data infrastructure

**Data Pipelines**
- Compute windowed roll-ups (1s / 5s / 1m avg, min, max, count)
- Derive new metrics from raw data
- Create materialized views for efficient querying
- Good for: cost control (dashboards query compact roll-ups instead of scanning raw 100 Hz data)

**API/SDK Queries**
- Pull data programmatically from Viam
- General SDK skill, covered in "Start Writing Code"
- Warning: per-component, high-frequency polling compounds quickly at scale

---

## Recommended Hybrid Architecture

For customers who want Viam as ingestion layer only:

1. **Safety-critical signals** — Route via webhooks to alerting infrastructure
2. **Diagnostic/operational telemetry** — Pipelines compute roll-ups, available via SDK/API or pushed via webhook on window close
3. **High-resolution performance data** — Direct capture to customer's MongoDB; they handle roll-ups and long-term storage

This keeps vendor responsibility at ingestion/transformation while customer owns storage and downstream processing.

---

## Documentation Structure

### Foundation Blocks (Mechanics)

| Block | What It Teaches |
|-------|-----------------|
| **Configure Data Pipelines** | Creating roll-ups, windowed aggregations, derived metrics. How to reduce data costs and pre-compute metrics. |
| **Sync Data to Your Database** | Setting up direct MongoDB capture. The "Viam as ingestion layer" pattern. When to use direct capture vs webhooks vs API queries. |

### Scale Topic (Strategy)

**Data Architecture Decisions** covers:
- When to keep data in Viam vs export it
- Cost implications of different patterns (polling is expensive at scale)
- Streaming aggregates pattern (pipelines + webhooks pushing roll-ups)
- Hybrid architectures for customers with existing data infrastructure
- The "vendor at ingestion layer" approach

---

## Key Takeaways for Content Authors

1. **Don't fight the "I want my data" instinct.** Some customers have legitimate reasons (compliance, existing infrastructure, vendor risk). Show them clean patterns for egress.

2. **Lead with cost-efficiency.** High-frequency polling of raw data is expensive. Pipelines and roll-ups are the answer for most dashboard/analytics use cases.

3. **Webhooks serve two purposes:**
   - Event-driven alerts (covered in Trigger on Detection)
   - Streaming aggregates (advanced pattern for Scale topic)

4. **Direct capture is about architecture, not just egress.** It's for customers who want Viam handling device-to-cloud transport but own everything after that.

5. **The three-tier model is a good mental framework:**
   - Real-time alerting → Webhooks
   - Operational dashboards → Pipelines + SDK/API (or webhook push)
   - Long-term storage → Direct capture or API bulk export

---

## Open Questions

1. **Pipeline configuration:** What's the UI/API for defining roll-up windows and derived metrics?
2. **Webhook reliability:** What retry/delivery guarantees exist? Is there a dead-letter queue?
3. **Direct capture setup:** What's the configuration flow? Any limitations vs Viam-managed storage?
4. **Cost modeling:** Can we give concrete guidance on query costs at different patterns/scales?

---

## References

- Customer discussion thread (January 2025)
- Block definitions: [Configure Data Pipelines](../build/foundation/configure-data-pipelines.md), [Sync Data to Your Database](../build/foundation/sync-data-to-your-database.md)
- Scale topic: [Data Architecture Decisions](../scale/data-architecture.md)

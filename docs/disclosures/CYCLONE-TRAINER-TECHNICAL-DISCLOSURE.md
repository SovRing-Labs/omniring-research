# Cyclone Trainer: Systolic Toroid Array Microarchitecture for THEAD-ISA

**Defensive publication (prior art).**  
**Author:** Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted).  
**Dated:** 2026-10-11.  

---

## 1. Abstract & System Identity
We disclose the microarchitectural specification for the **Cyclone Trainer**, a distributed systolic toroid array designed to train ternary register machines (**THEAD-ISA**) without expensive GPU clusters, massive matrix multiplies, or unbounded KV-caches.

The Cyclone Trainer maps ternary linear layers (`ternary_layer.py`), 8-slot typed register banks (`ring_bank.py`), and Chinese Remainder Theorem un-embeddings (`crt.py`, `codebook.py`) directly onto a multi-tier toroidal interconnect. Computational units scale from single-unit desktop nodes (**G1**, 8 slots) to large multi-floor arrays (**G120**, 15 RingBanks, 120 slots) connected via dimension-order CRT routing.

---

## 2. Register Machine vs. Memory Architecture

A critical innovation of the Cyclone microarchitecture is the separation of the active register file from the system bus:
- **The Register File (`RingBank`):** 8 typed polymorphic slots (20.48 KB total) residing permanently in CPU L1/L2 cache.
  - `TEMPORAL`: Continuous time integration via fractional power encoding (FPE).
  - `GOAL`: High-level intentional state and mission objectives.
  - `ENTITY_CONTEXT`: Active subject/object hypervector bindings.
  - `SYSTEM_STATE`: Fleet telemetry, host memory, and process health.
  - `ACTION_ATTRACTOR`: Policy logits and selected tool operations.
  - `IMMUNE_FILTER`: Negative constraints and forbidden semantic patterns.
  - `WORKING_0`, `WORKING_1`: Scratchpad workspace for intermediate generator steps.
- **The System Memory Bus (`vsa_matrix_bus`):** 1,000 slots (2.56 MB in `/dev/shm`) shared across all training harnesses via seqlock synchronization.

---

## 3. The 6-Stage Systolic Pipeline

The Cyclone hardware pipeline continuously pumps state across 6 synchronous stages:

```
  ┌────────────┐     ┌────────────┐     ┌─────────────┐
  │  feed_win  │────▶│  ev_build  │────▶│  ring_addr  │
  └────────────┘     └────────────┘     └──────┬──────┘
                                               │
                                               ▼
  ┌────────────┐     ┌────────────┐     ┌─────────────┐
  │  hub_pull  │◀────│  hub_mean  │◀────│    route    │
  └────────────┘     └────────────┘     └─────────────┘
```

### 3.1 Stage 1: `feed_win` (Batch Fetch)
Reads the active typed register slot (`read_slot(slot_id)`) from the 2,560-byte PolymorphicSlot via seqlock verification. Latency: $<1\ \mu\text{s}$.

### 3.2 Stage 2: `ev_build` (Cross-Attention Scan)
Executes an AVX2 ternary GEMV across all 8 register slots simultaneously. Query vectors (160 uint64 words) generate 8 dot products bounded in $[-10240, +10240]$ to compute attention weights without floating-point matrix multipliers. Latency: $<2\ \mu\text{s}$.

### 3.3 Stage 3: `ring_addr` (CRT Residue Projection)
Calculates ring address residues:
$$r_i = (\text{field} + \text{offset}) \pmod{m_i}$$
Replaces dense vocabulary projection matrices ($V$-way softmax) with a 5-plane Hamming distance lookup against the codebook, mapping output states directly to global CRT coordinates.

### 3.4 Stage 4: `route` (Toroid-to-Toroid Address Routing)
Transfers slot state across toroidal unit rings (ring 3 for floors, ring 5 for units) via dimension-order CRT jumps. The computed residue directly designates the destination hardware slot.

### 3.5 Stage 5: `hub_mean` (Consensus Averaging)
Averages slot representations across harnesses running the same slot type (e.g. aggregating `GOAL` representations across units) via float64 sums rounded once to ternary states.

### 3.6 Stage 6: `hub_pull` (Delta-Rule Parameter Update)
Synchronizes local models toward the hub consensus using a deterministic delta update:
$$w \leftarrow w + K \cdot (\text{hub\_mean} - w)$$

---

## 4. Recurrent Ternary Closed Loop

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        THEAD-ISA RECURRENT LOOP                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────┐     ┌─────────────┐     ┌──────────────┐     ┌───────────┐  │
│  │  INPUT   │────▶│ TernaryLinear│────▶│  RingCross   │────▶│  RingBank │  │
│  │ (tokens) │     │  (AVX2 GEMV)│     │  Attention   │     │  (8 typed │  │
│  └──────────┘     └─────────────┘     └──────┬───────┘     │   slots)  │  │
│                                              │             └─────┬─────┘  │
│                                              ▼                   │        │
│                                ┌───────────────────────────┐     │        │
│                                │ direct_probe (CRT lookup) │     │        │
│                                └─────────────┬─────────────┘     │        │
│                                              │                   │        │
│                                              ▼                   │        │
│                                ┌───────────────────────────┐     │        │
│                                │   17-CHECK CLAMP GATE     │     │        │
│                                └─────────────┬─────────────┘     │        │
│                                              │                   │        │
│                                              ▼                   ▼        │
│  ┌──────────┐                         ┌─────────────┐     ┌────────────┐  │
│  │  OUTPUT  │◀────────────────────────│  RingBank   │◀────│  hub_pull  │  │
│  │  (Token) │                         │  write_slot │     │(delta-rule)│  │
│  └──────────┘                         └─────────────┘     └────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

1. **Inference (Fast Path):** Input $\to$ TernaryLinear $\to$ RingCrossAttention $\to$ direct_probe $\to$ 17-check $\to$ Output ($O(1)$ memory, zero KV-cache).
2. **Learning (Slow Path):** Output $\to$ RingBank write $\to$ hub_mean $\to$ hub_pull $\to$ next iteration.
3. **Temporal Integration:** Continuous clock updating on the `TEMPORAL` slot via fractional power rotation.

---

## 5. Array Presets & Scalability

| Preset | Floors | Units | Pairs/Unit | Total Slots | Hardware Target | Status |
|:---|:---:|:---:|:---:|:---:|:---|:---|
| **G1** | 1 | 1 | 1 | 8 | Desktop / Laptop CPU (AVX2) | Verified |
| **G4** | 1 | 1 | 4 | 8 | Workstation 4-Core CPU | Verified |
| **G8** | 1 | 1 | 8 | 8 | Dedicated 8-Core Host | Verified |
| **G40** | 1 | 5 | 8 | 40 | Cluster Unit (Ring 3/5 Interconnect) | Stage 1 |
| **G120**| 3 | 5 | 8 | 120 | Full Toroidal Supercomputer Grid | Stage 2 |

---
*Published as sovereign defensive prior art under PolyForm Small Business 1.0.0 and PolyForm Noncommercial 1.0.0.*

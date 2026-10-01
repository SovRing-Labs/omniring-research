# Exploration: where the verified ring properties could apply

| | |
|---|---|
| **Date** | 2026-09-28 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance. This is a **labelled speculation document**: it is published for prior-art and lineage purposes, not as a specification. The author reviews it before publication. |
| **Type** | vision / exploration (labelled speculation) |
| **Verdict** | Exploration. Maps a surface, decides nothing, commits nothing. Read with the corrections below. |
| **Code** | n/a — no code implements this |
| **Status** | The source declares itself exploration: *"This document maps possibilities. It decides nothing and commits nothing."* |


> **Correction (added at publication).** This document is **exploration**, as its own status line says:
> it maps a surface and commits nothing. Three things a reader should not take from it:
> (1) **The market mapping is a first impression, not a market analysis.** No customer was surveyed,
> no pricing was validated, and no competitor was measured. Treat the applications as *hypotheses to
> test*, in that order of preference.
> (2) **Where it describes ring properties, only the measured ones carry.** The verified properties are
> the ones in the RING series — cued recall, keyed direct read, the check ring, and the explicit
> capacity ceiling of **≈12 marks per slot at c = 1**
> (`01-ring1-core-cued-recall-and-capacity.md`). Unmeasured extrapolations in this document are the
> author's reasoning, not results.
> (3) **It predates the decision not to build the two-stage chain.** That design was measured and
> **KILLed** (`09-ring1-halo-two-stage-chain.md`); any passage here that assumes a cascade of rings
> is superseded by that result.


---
title: "Omniring Lineage Possibilities — Application Surface Map"
type: lineage-possibility
status: exploration
not_a_spec: "This document maps possibilities. It decides nothing and commits nothing."
project: the research prototype repo
date: 2026-09-28
author: researcher (THEAD-RES-3 seat, post-task extension)
pillar: Nervous System
companion_review: reviews/2026-09-28 — OMNIRING-PEER-REVIEW-RETRIEVAL-AND-CONSOLIDATION.md
tags:
  - lineage
  - possibilities
  - application-surface
  - market-mapping
---

# Omniring Lineage Possibilities — Application Surface Map

**Status: EXPLORATION. Not a spec, not a plan, not a commitment.**

**Purpose.** A map of where omniring's *verified* properties could prove useful, ranked by fit. Recorded so
the option space is preserved and does not have to be re-derived. **Nothing here is a decision.** Every
entry names what would have to be true first.

**The framing that matters.** Omniring is not "a small LLM." Its measured and verified properties are:

- a **content-addressed store with a provable integrity gate** (100 % single-ring slip detection, 54,600
  exhaustive cases — a proof, not a sample)
- **abstention available at every gate** (`VERIFIED` / `ABSTAIN` / `REJECTED` / `SLIP_REJECTED` /
  `AMBIGUOUS`)
- **O(1) working memory** — 20.48 KB, constant RAM, 0 bytes of KV-cache growth
- **exact composition** — phase-face `unbind(bind(a,b),b) == a` (measured)
- **15 W CPU**, no GPU, no cloud, air-gap capable

**The valuable thing is the combination, not any single property.** Almost no production system can say
*"I don't have that, and here is proof the record I used was not corrupted."* That combination is the asset.

---

## Tier 1 — the property *is* the product

### 1.1 Medical dosing / clinical decision support

**Fit:** drug interactions, contraindications, renal-dose tables, allergy cross-checks.
**Why it fits:** the requirement is precisely "wrong is worse than absent." A provable integrity gate plus
an abstention path is the differentiator against an LLM that will confidently invent a plausible
interaction. The 1,365-coordinate verified spine maps naturally onto a bounded interaction table — a drug
interaction matrix is small, structured, and its correctness is checkable.
**What must be true first:** the 1-bit/`[?]` items aside, the binding constraint is §0.3 below — the
silent-wrong rate on the resonant path. For a dosing interlock, that number *is* the product.
**Honest note:** a curated interaction table does not need a 15 W neural system. The defensible version is
the *unbounded* case — a clinician-supplied local formulary plus device-specific history, where no central
table is available. That is a real gap; a formulary lookup is not.

### 1.2 Industrial & laboratory equipment compliance

**Fit:** pressure interlocks, dosing controllers, cleanroom HVAC, industrial recipes, calibration records.
**Why it fits:** the value is that the memory is *inspectable and cannot silently drift* — a verified mark
cannot be corrupted in place. A 15 W fanless box beside a PLC is a selling point, not a compromise.
**What must be true first:** decay (§0.4). In a long-lived installation, a store that never forgets is a
liability — stale interlocks must expire, and today nothing can expire.
**Confidence:** MEDIUM-HIGH. The integrity story is real; the market's willingness to pay for it is unproven.

### 1.3 Audit, forensics, provenance

**Fit:** reconstructing *what the system knew, when, and whether the record was intact.*
**Why it fits:** every mark is citable by slot, and the `TEMPORAL` ring carries FPE phase rotation while the
coprime counting rings name *when* compactly (§0.5). A system that can prove provenance and prove
non-corruption answers a question most RAG systems cannot answer at all.
**What must be true first:** the counting-ring time encoding is a candidate, not built `[?]`.
**Note:** this is the capability most likely to be *underrated* — it is a property of the architecture, not a
feature that had to be added, and auditors are the people who most need it.

### 1.4 Air-gapped and classified environments

**Fit:** defence networks, air-gapped labs, hospital networks, industrial plants with no egress.
**Why it fits:** no cloud, no GPU, no telemetry egress, 15 W CPU. This is one of very few architectures that
can legally and physically run in these settings. It is the North Star (§I.5 — "capable AI on the computers
people already own") realised as a *compliance* property rather than a cost property.
**What must be true first:** nothing architectural. This is the closest to *ready* of anything in the map.
**Confidence:** HIGH on fit, UNKNOWN on procurement (the buyer is rarely the end user).

---

## Tier 2 — strong architectural fit, needs a trained head

### 2.1 Edge robotics

**Fit:** drones, warehouse AMRs, agricultural machinery, inspection rovers.
**Why it fits:** O(1) memory means no context cliff; abstention means the robot can *refuse* rather than
guess; CPU-only fits existing compute; **fixed latency is the real prize** — no KV-cache growth means no
tail-latency explosion, which matters in a control loop.
**What must be true first:** a real head. Everything here is currently an untrained scaffold (§0.1).
**Honest note:** robotics wants *reliable* failure, and a refusal is a hard sell to an integrator whose
safety case assumes a deterministic fallback. The abstention path needs a documented behaviour, not just an
exit code.

### 2.2 Offline field service & repair

**Fit:** technicians with no connectivity — HVAC, industrial maintenance, medical equipment servicing.
**Why it fits:** marks carry *when* natively, so recency ranking is structural rather than bolted on. The
`ACTION_ATTRACTOR` ring is documented as *"current candidate tool / action codebook vector"* — which maps
directly onto "which procedure do I run next." Flash storage in a service truck, no network dependency.
**What must be true first:** the head, and the counting-ring time encoding for recency.
**Confidence:** MEDIUM. Strong fit, crowded market, no technical moat once others copy the shape.

### 2.3 Privacy-preserving clinical & legal intake

**Fit:** records never leave the machine; every retrieval logged with an integrity proof.
**Why it fits:** for discovery or intake, *"this came from slot N at time T, and the record passed the
integrity gate"* is an evidentiary advantage, not a feature bullet.
**What must be true first:** the provenance chain (§1.3) must be complete before it is worth anything.
**Note:** adjacent to Sov Raptor rather than distinct from it — this may be a *mode* of the launcher
business rather than a separate product.

---

## Tier 3 — plausible, weaker differentiation

| Domain | Fit | Weakness |
|---|---|---|
| **Assistive / accessibility tech** | O(1) memory suits a device that runs indefinitely; screen readers, AAC | Real need, weak commercial pull, incumbent competition |
| **Grid / edge energy management** | Many small sensors, tight memory, 15 W | Throughput matters more than integrity — weak differentiator |
| **Education / tutoring** | A tutor that abstains and shows provenance; cognitively excellent fit | Monetisation, not technology, is the obstacle |

---

## 0. The open questions that gate all of the above

These are recorded here because every application above inherits them.

### 0.1 There is no trained head

All weights in `ring_transformer[REDACTED]` are `rng.choice([-1,0,1])`. 57/57 passing certifies
*self-consistency of the kernel*, not learning. **Any Tier-2 application is blocked on this**; Tier 1
integrity applications are not.

### 0.2 Retrieval on superposition is unmeasured

The 1,365/1,365 clean round-trip is real but is the clean-signal case. Measured on the **sequential** path
(`direct_probe`, independent `argmax` per ring) a two-member superposition returned a *valid but wrong*
coordinate — passing the 17-ring, wrong member. Depth sweep showed a silent-wrong rate of 0–13 %, **not
monotonically decreasing with data volume** (k=50 was the worst row).

The intended decoder is `decode_soft` — simultaneous settle with ReLU selectivity, which exists and has
**never been measured**. One of its bugs (unguarded eigengap divide) must be fixed before it can be
measured honestly.

> **This is the single number that gates every safety-critical application in Tier 1.** Not the parameter
> count, not the latency. The silent-wrong rate of the resonant path.

### 0.3 Which face holds the knowledge — the unresolved fork

- **Phase face** — 1,365 exact, verifiable, composable → **Tier 1 safety-critical**
- **Ternary face** — ~1,000 slots × ~100 superposed, fuzzy, no exact addressing → **Tier 2 edge**

**You cannot serve a medical interlock and a warehouse drone from one store without both faces.** The
polymorphic two-faced slot makes it possible; **nothing has decided it.** Every application above silently
assumes an answer.

### 0.4 Nothing can decay

`bundle` is sum-then-threshold; old marks never fade. In a store meant to learn, this is the defect that
matters most — the bus fills monotonically with whatever arrived first. Worse, **phase quantises to K=16
(4 bits) on write**, so a rehearsal count cannot be recovered from the vector at all; it needs an explicit
per-slot counter sidecar.

Selective decay is a two-line mask on the active plane and needs no learning machinery. **If one thing is
built, build decay.** It is also a correctness requirement for any long-lived deployment (§1.2).

### 0.5 The counting rings carrying time are a candidate, not built

The project's own research identifies the coprime rings as **counting** rings, with time/beats/mark-age as
the natural fit — a capability RSPK does not have: *marks that carry when, compactly, on the same bus.*
**Cheapest distinctive thing available.** Untested `[?]`.

---

## The strategic read

**The answer is not a single industry — it is the regulatory surface.**

Every Tier-1 application shares one property: **a human is legally accountable for the output, and must be
able to state what the machine based it on.** That is why the abstention path and the integrity gate matter
more than the parameter count. A system that refuses when it lacks the record, and *proves* the record it
used was not corrupted, is a different product category — and in that conversation the parameter count never
comes up. That is a rare position, and the sub-500 M / 15 W constraint is what makes it reachable at all.

**On the mission.** The reframe from *prosthesis* to *decentralised LLM with sub-500 M heads on any
hardware* is stronger, and the constraint does real architectural work: it forces O(1) memory, forces
knowledge into the bus rather than the weights, and forces integrality. **The constraint is the design** —
that is why the hard parts got done.

**On the method.** Attempt, fail, learn is right, with one requirement: every failure is measured and written
down, so the next attempt begins from knowledge rather than optimism. The repo's `UNVERIFIED` convention is
that method, created because four defects survived for weeks behind green tests. **Protect it.**

**Recorded honestly:** most of this map is conditional on §0.2 and §0.4. The architecture is genuinely novel
and largely verified. **The proof that it works under superposition is not in.** Week 1 of the companion
review measures exactly that.

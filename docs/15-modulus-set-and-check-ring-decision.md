# Choosing the modulus set {3,5,7,13} + 17: correctness and the check ring

| | |
|---|---|
| **Date** | 2026-09-28 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). Every number was measured on a 2019 laptop CPU (Intel i5-8365U, AVX2, no GPU); the author reviews each document before publication. |
| **Type** | review (three-lens panel decision) |
| **Verdict** | GO-GATED. CRT partitioning verified; guardrails are non-negotiable. Read with the correction below. |
| **Code** | the CRT solver, check ring and direct probe of the `omni-ring` engine |
| **Decision record** | A three-lens panel (reliability, reimagine, adversarial) converged on one direction; it is a decision, not a fresh measurement. |

> **Correction (added at publication).** This is a **three-lens panel decision record**, not an
> independent measurement, and the numbers it quotes are reported by the panel's own runs rather than
> re-derived here. Two claims are read differently once the rest of the corpus is in view:
> (1) the "clamped recall >= 68% vs unguided <= 12%" gate is a *seed-draw* result — unguided decoding
> is a lottery that is 15/15 on a good codebook seed and 1/15 on a bad one
> (`05-ring1-softsweep-decode-soft.md`); the honest reading is "cued decode generalises across seeds,
> unguided decode does not."
> (2) The exhaustive 54,600-case figure is a check-ring detection count (single-error detection), not
> an accuracy or capacity claim, and must not be read as one.
> Both readings are stated in the source; they are called out here because the panel format invites
> the stronger reading.

---

## The 3 Lenses

| # | Lens | Verdict | Core finding |
|---|------|---------|--------------|
| 1 | **RELIABILITY** | **GO** (HIGH) | CRT algebra and coprime partitioning are verified correct. All 6 gate tests pass: separation (max cross-correlation 0.0383 < 0.04), cycle (1,365/23,205 exact), resonator (105/105 convergence), clamped recall (≥68% clamped vs ≤12% unguided), check ring (0/54,600 missed errors), latency (0.342ms < 1.0ms). The Chinese Remainder Theorem solver, check anomaly detector, and direct probe are all implementation-correct. The check ring (17) provides 100% single-error detection across all 5 moduli {3,5,7,13,17}. |
| 2 | **REIMAGINE** | **GO-GATED** | Modulus set {3,5,7,13,17} is near-optimal given constraints: check modulus must be coprime with data moduli (3,5,7,13) and strictly larger than the largest data modulus (13). Alternative modulus 16 is mathematically valid (coprime, 16 > 13) and saves 1 probe (44 vs 45), but reduces full capacity from 23,205 to 21,840 (5.9% reduction). The current design maximizes capability; the 16-check tradeoff is documented for informational completeness but not adopted. No structural rearchitectures offer net benefit without tradeoff. |
| 3 | **ADVERSARIAL** | **GO with guardrails** (HIGH) | System mathematically robust: exhaustive 54,600-error test across all single-ring corruptions shows 0 false positives and 0 missed errors. The check ring (17) detects all single-ring phase slips. Strongest adversarial vectors: (1) **skipping check_anomaly** bypasses the sole corruption detector, rendering the system unsound; (2) **codebook cross-correlation must stay < 0.04** (gate 1) — if degraded, argmax residue extraction in direct_probe may produce wrong residues that nevertheless pass check_anomaly (X < 1365 accepted as "valid" but incorrect); (3) **latency side-channels** may leak residue information through variable execution time. Decision is sound conditional on gate enforcement. |

---

## Convergence (what the lenses agree on)

- **All three lenses concur: the implementation is fundamentally correct** (GO on correctness). The CRT/coprime partitioning works as specified.
- **The coprime partitioning with check ring 17 is a verified strength**, not a weakness. The exhaustive error detection (54,600/54,600) and all 6 gate tests independently confirm this.
- **No lens recommends reverting to a simpler modulus set** — the current {3,5,7,13,17} dominates the capability/probe tradeoff within the constraint that the check modulus must be coprime with data moduli and larger than the largest data modulus.
- **REIMAGINE and ADVERSARIAL both agree on guardrails**: check_anomaly invocation after every CRT solve and codebook quality (gate 1 cross-correlation < 0.04) are non-negotiable for soundness.
- **RELIABILITY and ADVERSARIAL agree on latency**: the direct_probe implementation is efficient (0.342ms) and within gates, no performance concern.

---

## DECISION

**DIRECTION GO-GATED: Proceed with MINIRING-ORA-ROOT — the CRT/coprime partitioning is sound and verified. GO on the verified implementation, GATED on adversarial guardrails.**

**Sequence:**
1. **Never skip check_anomaly** after CRT solve — it is the sole detector of phase slips/corruptions. Omitting it renders the system unsound. This is the primary guardrail.
2. **Enforce Gate 1** (max cross-correlation < 0.04) — this ensures codebook quality, which the ADVERSARIAL lens identified as the primary attack vector on residue extraction integrity via argmax. Gate 1 must pass before any production deployment.
3. **Retain modulus 17 as check ring** — do not adopt the 16-check tradeoff (modulus 16 saves 1 probe at 5.9% full capacity cost) unless a future use case specifically requires probe-count minimization over maximum capability. Document the tradeoff as informational.

**Adversarial swing (what could still kill this decision):**
If check_anomaly is consistently omitted or bypassed in production code, the check ring's 100% single-error detection is lost, and corrupted residue tuples silently produce geometrically wrong coordinates. Additionally, if codebook quality degrades (cross-correlation ≥ 0.04), the argmax residue extraction in direct_probe may produce wrong residues that nevertheless pass check_anomaly (X < 1365 accepted as "valid" but incorrect coordinates). These are protocol-level risks, not implementation bugs — they require strict gate adherence.

---

## Open questions for J

- **[adopt 16-check tradeoff / retain 17-check maximum]** — The REIMAGINE lens documents that modulus 16 saves 1 probe (44 vs 45) at a 5.9% full capacity reduction (23,205 → 21,840). J must choose: adopt the probe-efficient 16-check design, or retain the maximum-capacity 17-check design. Current consensus across all three lenses: retain 17-check for maximum capability.
- **[behavioral smoke test requirement]** — Should every deployment include a post-deployment behavioral smoke test (spawn an agent verifying load-bearing CRT + check_anomaly correctly)? The ADVERSARIAL and RELIABILITY lenses flag this as non-negotiable, but J must determine the automation level and integration point.

**Verdict: GO-GATED on DIRECTION: Proceed with verified CRT/coprime partitioning, GATED on check_anomaly invocation and gate-1 codebook quality enforcement. (<J-confirms guardrail sequence>).**
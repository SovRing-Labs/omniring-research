# RSPK: should the resonator / VSA spike be built? (nine-cell panel decision)

| | |
|---|---|
| **Date** | 2026-09-28 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). The author reviews each document before publication. |
| **Type** | review (three-lens panel decision, 9/9 cells) |
| **Verdict** | GO_WITH_REVISIONS on direction, with a NO-GO and a BLOCKED accepted. **Superseded on the build-now question by later measurement** — see the correction. |
| **Code** | the ternary core and phase layer of the VSA core; the bus described here ships in omni-ring |
| **Format** | A three-lens panel (reliability, reimagine, adversarial) across three altitudes converged on one direction. It is a **decision record**, not a fresh measurement: the numbers it quotes were measured elsewhere and are cited, not re-derived here. |


> **Correction (added at publication).** This card's headline decision — **"don't build the resonator
> now"** — was **superseded by later measurement**. The RING series subsequently measured the reader
> path directly and found it works: cued recall and keyed direct read are strong
> (`03-ring1-direct-keyed-storage.md`, 1,000/1,000 and 300/300), and the check ring detects 100% of
> single-ring errors across 54,600 exhaustive cases (`15-modulus-set-and-check-ring-decision.md`). What
> the panel got right and still stands: **confidence before accuracy** (the barycenter/collapse
> question is a real one), **an evidence tier** (no unverified claim moves a parameter), and the
> **no-fitted-thresholds** rule. What it got wrong was its premise — that the field could not test a
> factoriser. It could, once a harness with a known answer was written. The "superseded by RING
> measurements" note in the original MANIFEST row is this correction in full.
>
> One capacity figure in this card is **corrected**: the "D=5,120 × K=16 = 2,560 B" slot arithmetic is
> right, but the paired claim that "the patent argument for K=32 is void" is a design conclusion from
> this project, not a legal finding. Freedom-to-operate on **US 12,579,411 B2** remains an open legal
> question for a qualified attorney, and this corpus publishes for prior-art purposes only.


**Date:** 2026-09-27 · **Cells:** 9/9 complete (3 lenses × 3 altitudes) · **Confidence:** MEDIUM-HIGH on direction, MEDIUM on design point
**Inputs:** `RSPK/CONTEXT.md` · 6 dossiers `the research corpus RSPK/2026-09-27-RSPK-{RES,VSA1,VSA2,MATH,PHYS,MIND}.md` (~58k words) · 9 cells `the research corpus RSPK/2026-09-27-RSPKO-*.md`
**Pillar:** Nervous System (resonator = a machine reader in the Loop's Read step)

## Decision
**Don't build the resonator now. Build the reader's trust layer and the bus first; gate the factoriser behind measured kill criteria and a patent opinion.**
This is GO_WITH_REVISIONS on the *direction* (6 cells + ADV-ROOT), with the NO-GO (REL-TOP) and BLOCKED (ADV-STR) accepted as correct about the spike *as written*.

## The 9 cells
| Cell | Verdict | Core point |
|---|---|---|
| REL-TOP | NO-GO | Unbinding one factor from a mixed ternary bundle measured at chance (8 seeds); SQL GROUP BY is exact for discrete mark data. |
| REL-STR | GO_WITH_REVISIONS | Invert the design: measure the synthetic capacity grid first, freeze the noise schedule against ACF, gate on iterations at F=4. |
| REL-ROOT | GO_WITH_REVISIONS | Synthetic core is sound; published budgets are off 1.5–23× (OLS matvec missing); drop stage 2 until a real label axis exists. |
| REIM-TOP | GO_WITH_REVISIONS | A keyed-item store removes the need to factorise at all. |
| REIM-STR | GO_WITH_REVISIONS | Build the phase layer (qFHRR) standalone; defer the factoriser until superposed marks exist on the bus. |
| REIM-ROOT | GO_WITH_REVISIONS | Shrink the design point for byte width; corpus = `dispatch.db`; first build = a ~50-line barycenter/recency gate. |
| ADV-TOP | GO_WITH_REVISIONS | Not justified for today's field data; maybe for future superposed signals. |
| ADV-STR | BLOCKED | Benchmark vacuous on today's data; US 12,579,411 unaddressed; IFS has no evidence base. |
| ADV-ROOT | GO_WITH_REVISIONS | Unfalsifiable as written; seal the metric first; K=32 breaks the bus ABI (−60% slots); bus + slot registry before the resonator. |

## Convergence (verified by the seat)
- **9/9: the field cannot test a factoriser today.** Verified 2026-09-27: `field.sqlite` 244 marks, `beat` NULL in 244/244, no `lane` column, 1 non-ok outcome (and that one is about this spike). The real-data arm is vacuous.
- **9/9: the real corpus is `dispatch.db`.** Verified: 1,019 tasks, 22 roles × 9 kinds × 10 classes, 8 blocked reasons, 29 models. Label it "not the field".
- **8/9: confidence before accuracy.** The dominant failure is *convergence to the barycenter* (a legitimate fixed point averaging all patterns), which no accuracy number sees. Our own `vsa_stochastic.h` 99.96% was exactly this kind of artifact. Reader output = convergence class {single-pattern, metastable, global-average, not-converged} + load ratio D_f/D + barycenter flag.
- **7/9: IFS is a hypothesis, not a mechanism.** One A/B cell against ACF (asymmetric codebook perturbation, arXiv 2412.00354) with a written falsifier; drop it if it doesn't beat ACF on iterations or accuracy.
- **6/9: cheap fixes land first, independent of the resonator:** mean-centring in the encoder (one line); bit-sliced majority bundle (`vsa_bundle` ≈20 µs, 217× a dot); ≥8-seed sweeps on every random claim; a linear/logistic control that the HDC path must beat.

## Where the cells disagreed, and the resolution
- **Design point D=10,240/K=32 vs D=5,120.** ADV-ROOT: 5-bit phases at D=10,240 = 6,400 B → the 1000-slot bus drops to 400. REIM-ROOT: D=5,120 fits the current slot, but its "K=32 packed 2 per byte" is wrong (2 per byte = 4 bits = K=16). **Seat arithmetic: D=5,120 × K=16 = 2,560 B, byte-identical to today's slot** (bus verified 2,560,000 B = 1000 × 2,560). ADV-ROOT also shows K=16 is exactly as non-bipolar as K=32, so the patent argument for K=32 is void. **Resolution: the first phase test runs at D=5,120, K=16 (fits the ABI), with K ∈ {8,16,32} and D=10,240 as the sweep; the smallest K that clears the sealed bar wins.**
- **Patent.** Verified from primary text (Google Patents, 2026-09-27): **US 12,579,411 B2** (IBM, granted 2026-03-17, expires 2045-01-03). Claim 1 = feature-extraction subnetwork → **bipolarize** → resonator factorisation → **assign a class**. Plain software; not listed in our 2026-09-25 clean-room addendum. "One resonator per query" does **not** avoid it. The design-around is phase codebooks (never bipolar, enforced at build time), no class output (return scores + convergence class), no bipolarize step anywhere. Our text path (Nomic → ±1 projection → ternary deadband) sits near element (ii): ternary ≠ bipolar, but it needs an opinion. Also add GC-VSA (arXiv 2503.08608) to the clean-room checklist.
- **REL-TOP NO-GO vs the rest.** REL-TOP is right that a resonator is the wrong tool for *discrete failure analysis at our scale*; SQL wins. The GO cells are right that phase + a confidence channel have value for superposed/noisy signals (bus, micromodel memory, other machines). Resolution: scope the resonator to superposed signals only, and never to failure analysis that SQL answers.

## Build order (2–4 weeks) — each step has its kill criterion
| # | Build | Kill / pass criterion |
|---|---|---|
| 1 | Mean-centring in the encoder + float-vs-ternary recall@10 on the real vault (3 variants) | Gap > 10 pp after centring ⇒ re-derive the ternary text path before any phase work |
| 2 | Sealed-metric pre-registration + convergence-class/load-ratio/barycenter result type (3 bits on the existing confidence register) | Barycenter not separable at > 99% specificity ⇒ no reader ships |
| 3 | Bus writer/reader + slot registry (the bus has had no writer or reader since 09-25) | Not working by end of week 2 ⇒ resonator does not start |
| 4 | Bit-sliced majority bundle | > 5 µs/vector on this host ⇒ superposed path is off the budget |
| 5 | Phase kernel conformance gate: D=5,120, K=16, scalar reference, 3,000 trials, independent generator | Any scalar/AVX2 disagreement ⇒ stop; cleanup > 1.25 µs/codevector ⇒ stop |
| 6 | Asymmetry control (perturb one codebook copy vs both), then ACF, then IFS as A/B | Limit-cycle rate changes < 2× ⇒ the noise thread (incl. IFS) is dead |
| 7 | Single-resonator factoriser, synthetic held-out recovery at F=4 | Accuracy < 99%, median iterations > 24, converged-but-wrong > 1%, or M_max > 10× under the law ⇒ kill per ROOT cells |
| 8 | `dispatch.db` snapshot smoke test (hash-pinned) vs a logistic-regression control | Control ties or beats ⇒ ship the control |

Steps 1–4 pay off even if the resonator is killed. Nothing in 1–6 touches any element of the IBM claims.

## Adversarial swing (what could still kill THIS decision)
The phase kernel may simply not inherit the bipolar capacity law (fitted exponents disagree ~27% at F=4; no qFHRR code exists anywhere). Then steps 5–7 die and the spike's lasting output is steps 1–4 plus a confidence channel, which is still a good outcome. The other risk is drift: the field grows (94 → 145 → 244 marks during this spike), so every fixture must be hash-pinned.

## Open decisions for J
| Decision | Options | Seat recommendation |
|---|---|---|
| FTO opinion on US 12,579,411 B2 | Attorney opinion before step 7 / design-around only / accept risk | Attorney opinion before any factoriser code; steps 1–6 proceed meanwhile |
| Approve steps 1–4 as the next wave | Approve / reorder / park | Approve: they unblock the Read step with or without a resonator |
| Bus ABI | Keep 2,560 B slots (D=5,120, K=16) / new ABI for D=10,240 phase | Keep the ABI unless the sweep shows K=16 fails the bar |
| IFS | A/B cell vs ACF / drop now | A/B cell: it's cheap and settles your idea on evidence |

**Verdict: GO_WITH_REVISIONS — the trust layer and the bus first, the resonator gated behind measured kill criteria and an FTO opinion.**
---
*Converged by the Claude seat, 2026-09-27. Seat-verified this session: field cardinality, dispatch.db cardinality, bus size, AVX-512 absence, slot arithmetic, patent claim 1 (primary source).*

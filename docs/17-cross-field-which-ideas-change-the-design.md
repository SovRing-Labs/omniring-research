# XP1: which cross-field ideas change the design, and which stay metaphor

| | |
|---|---|
| **Date** | 2026-09-28 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). The author reviews each document before publication. |
| **Type** | review (three-lens panel decision, 9/9 cells) |
| **Verdict** | GO_WITH_REVISIONS. The build order stands; cross-field material is metaphor-only except where re-derived here. |
| **Code** | design rules and evidence tiers; the binaries they govern ship in omni-ring |
| **Format** | A three-lens panel (reliability, reimagine, adversarial) across three altitudes converged on one direction. It is a **decision record**, not a fresh measurement: the numbers it quotes were measured elsewhere and are cited, not re-derived here. |


> **Correction (added at publication).** Two study-guide claims are corrected here rather than silently
> carried: **ACF is a frozen one-sided bit-flip mask, not an "asymmetric perturbation"** of codebooks,
> and **the K=32 qFHRR speed figure does not appear in the cited paper**. The cross-field material is
> **metaphor-only** except where this project's own arithmetic re-derived it (the cost law
> `S = 1/(d₁/D + k*/N)` reproduces; the margin law does not survive its own verification table at this
> corpus size and is demoted to a hypothesis). Plan with **≈2× deployable cascade speedup, not 7.7×.**
> This card **amends** the previous one, never replaces it.


**Parent:** `the research corpus 2026-09-27 — RSPK Resonator-VSA Oracle CONVERGE (9-cell).md` (sealed; this card amends, never replaces).
**Question:** Which cross-field mechanisms (SG1 study guide: HDC, Hopfield, optics, RF, dynamics; SG2: operations + contemplative traditions) change the Nervous System's design parameters or the RSPK build order, and which stay metaphor?
**Inputs:** 6 dossiers `the research corpus XP1/branches/` · 9 cells `the research corpus XP1/panel/` · coverage map `the research corpus XP1/B0-coverage.md` · PR reviews `the research corpus PR/pr{2,7}-xp1-*` · citation check `the research corpus XP1/citation-check.md` (17/17 arXiv ids resolve, titles match topic).
**Pillar:** Nervous System.

## Decision
**GO_WITH_REVISIONS — the RSPK build order stands. XP1 adds rules and corrections, not new mechanisms.** Three build rules and two design changes are adopted, and three workstreams are closed; the cross-field material itself is METAPHOR-ONLY except where our own arithmetic re-derived it.

## The 9 cells
| Cell | Lane | Verdict | One line |
|---|---|---|---|
| REL-ROOT | big-pickle | GO_WITH_REVISIONS | Re-ran the arithmetic: cost law and ABI escape reproduce; k* margin law fails at our corpus size; 2 numbers in its own table off by 14× |
| REL-STR | nemotron-ultra (zen) | GO_WITH_REVISIONS | D=5,120 × K=16 = 2,560 B fits the bus; Welch bound vacuous to M=5,000; random Z₁₆ crosstalk 0.034 mean |
| REL-TOP | nemotron-super | NO-GO | Adopting cross-field mechanisms now risks the bring-up; also proposes swaps (VQ-VAE factoriser) the other 8 cells do not support — weakest cell |
| REIM-ROOT | space-bunny | GO_WITH_REVISIONS | Collapse detection = step 2's sealed result; cut step-5 sweep to K∈{8,16}; capacity dial is slots, not D; no second trust layer |
| REIM-STR | nemotron-ultra (key2) | GO_WITH_REVISIONS | Cascade is the cheaper earlier win; never materialise the full vector; retire System 1/2 labels; codebook-design vein is dead |
| REIM-TOP | nemotron-super (key2) | GO_WITH_REVISIONS | Partitioned slots over one global superposition; WIP pull per lane; Gold codes only if worst-case correlation is ever required |
| ADV-ROOT | big-pickle | BLOCKED (on design adoption, not on the work) | No XP1 mechanism survives as CHANGES-DESIGN on its cited numbers; B3-F1 and B3-F5 stand as rulings; volume-holography 1/M² is the corpus's main metaphor-driven-design failure |
| ADV-STR | nemotron-ultra (zen) | GO_WITH_REVISIONS | Study-guide claims corrected: ACF is a frozen one-sided bit-flip mask, not "asymmetric perturbation"; K=32 qFHRR figure is not in the paper; 7.7× is an arithmetic ceiling |
| ADV-TOP | nemotron-super | GO_WITH_REVISIONS | Replace IFS with ACF as the baseline; FTO on both patents before step 7; realistic cascade speedup ≈2×, not 7.7× |
Tally: 7 GO_WITH_REVISIONS · 1 BLOCKED · 1 NO-GO (same shape as RSPK).

## Convergence (what ≥5 cells agree on, verified by the seat)
1. **The RSPK build order is unchanged** (9/9: no cell moves a step; ADV-ROOT and REL-TOP argue for adopting nothing new).
2. **Coarse-to-fine cascade: adopt the *cost law*, not the *margin law*.** `S = 1/(d₁/D + k*/N)` reproduces (REL-ROOT re-ran it; 2,048/20,480 caps S at 10×, our measured 7.7× sits under it). The margin law `k*_max = (1/z)·√(D·d₁/(D−d₁))` fails its own verification table at our N (REL-ROOT, ADV-ROOT independently): **keep k* = 8 (measured), demote the law to a hypothesis.** Plan with ≈2× deployable speedup, not 7.7× (ADV-STR, ADV-TOP).
3. **Never materialise the full vector** — the slot stores the prefix-width summary; full width is query-time (REIM-STR C3, REIM-ROOT C5, REL-ROOT #5). This dissolves the 2,560 B bus-ABI collision at D=5,120, K=16 (REL-STR verified the arithmetic).
4. **Collapse / barycenter detection is a first-class output of step 2** (REIM-ROOT C1–C2, REIM-STR C5, REL-ROOT #9): one sealed result type with convergence class, load ratio and a barycenter flag.
5. **Codebook design is closed**: random Z₁₆ at M=42, D=5,120 has headroom (B3-F1, REL-STR #3, ADV-ROOT, REIM-STR C9). **Fractional Fourier transform stays out of the hot path** (B3-F5). Gold codes only if deterministic worst-case correlation is ever required.
6. **Metaphor-only (no parameter moves):** volume holography 1/M² as a law, cymatics/Chladni, CDMA as more than an analogy for bundling, dual-process System 1/2 (retire the labels, keep the mechanism), stat-mech "temperature", all of B6 (Indra's Net, Hermetic correspondence, Akashic, Nada Brahma, Wu Wei). The partitioned-vs-global choice survives as a design preference already in step 3 (slot registry), not as an optics law.

## Build rules adopted (apply to every step)
| Rule | Source cells | Check |
|---|---|---|
| **Evidence tier:** no Tier-C (unverified / study-guide) claim may move a parameter | REL-ROOT #8, ADV-ROOT, ADV-STR | CONVERGE and contract reviews cite a Tier-A/B source or our measurement |
| **No fitted thresholds:** thresholds are derived or measured on held-out data, never tuned on the eval set | REIM-ROOT C7, REIM-STR C7 | each threshold names its derivation or dataset |
| **One trust layer:** B4's "trust layer" is step 2; do not build a second | REIM-ROOT C8 | no new store without its reader (CLAUDE.md) |

## Corrections to the record (study guides SG1/SG2)
- ACF (arXiv 2412.00354) is a frozen one-sided asymmetric codebook mask, not "Asymmetric Codebook Perturbation" injecting noise; the paper's finding is asymmetry-not-noise (B1, ADV-STR). IFS remains a hypothesis to A/B against ACF (RSPK open decision stands).
- The qFHRR K=32 fidelity numbers are not in Snyder et al. 2026 (arXiv 2604.25939); K=16 is the tested point (B1 §3.5, ADV-STR). Step 5 sweeps K ∈ {8, 16} only (REIM-ROOT C4).
- "Holographic Principle of Random Indexing" and "Dynamic Dimension Allocation" are not established terms (B1). 71.8% at 2,048-D ≈ the majority baseline, not "slightly inaccurate" (J THREADS SYNTHESIS §69). "3-bit confidence registers" and `field.sqlite` as described in SG2 do not exist as stated.

## Where the cells disagreed, and the resolution
| Point | Sides | Resolution |
|---|---|---|
| k* margin law | REIM-STR/REIM-TOP adopt · REL-ROOT/ADV-ROOT reject after re-derivation | Two independent ROOT re-derivations win: k*=8 measured, law = hypothesis |
| Partitioned medium (1/M) vs global (1/M²) | REIM-TOP/REL-TOP adopt as a law · ADV-ROOT/ADV-STR: metaphor | Keep partitioned slots (already step 3) on our own grounds; drop the optics law as justification |
| Hebbian raw counts / EMA centroids | REL-STR/REIM-TOP/REL-TOP for · others silent | Deferred to the Learn loop (LEARN-LANE-HEAD-3 first); no step change |
| Stage-2 corpus gate | REL-ROOT: re-open (data changed) · ADV-ROOT: confirm the gate | Re-open **the measurement**, not the verdict: FIELD-INGEST (2026-09-27) grew the field from 651 → ~3,600 marks with lane labels; beats still thin. Re-run the corpus probe before step 2 seals |
| Adopt anything now | REL-TOP NO-GO | Rejected as a whole-cohort verdict (its own table proposes a VQ-VAE factoriser swap unsupported by any dossier); its caution is already the Decision |

## Changes to the RSPK build order
None to the order. Amendments: step 2 gains the collapse/barycenter result + the write-side integrity channel; step 3 stores prefix-width summaries (never the full vector); step 5 sweep = K ∈ {8,16}, D=5,120; step 7 still gated on FTO (US 12,579,411; GC-VSA 2503.08608 added to the FTO scope).

## Open decisions for J
| Decision | Options | Seat recommendation |
|---|---|---|
| Adopt the 3 build rules into CODEX/contract template | yes / per-step only | Yes: they are cheap and stop metaphor-driven design |
| B2–B5 PRs (no review cells) | review 12 cells / keep as unmerged lineage | Keep as lineage: the panel already reviewed them; canonical copies are in `the research corpus XP1/branches/` |
| Next wave | VSA step 1 re-probe on the new field corpus → step 2 | Re-probe first (cheap, deterministic) |

**Verdict: GO_WITH_REVISIONS — build order unchanged; adopt the cost law, k*=8, never-materialise, collapse-as-output and the three build rules; everything else from the cross-field sweep is filed as metaphor.**

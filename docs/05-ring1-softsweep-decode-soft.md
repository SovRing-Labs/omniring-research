# RING-1 SOFTSWEEP: the soft resonator (decode_soft) vs sequential direct_probe on superposed slots

| | |
|---|---|
| **Date** | 2026-09-29 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). Every number was measured on a 2019 laptop CPU (Intel i5-8365U, AVX2, no GPU); the author reviews each document before publication. |
| **Type** | measured result (harness rewritten; see correction) |
| **Verdict** | KILL on half 1 by construction (the bar was unattainable at the registered n); half 2 passes by 0.97. See the reviewer's reading. |
| **Code** | omni-ring (`decode_soft`, `direct_probe`); sweep script `bench/soft_sweep.py` in the omniring-llm research prototype (not yet published) |

> **Correction (added at publication).** The unguided `ds@…` rows below were all run at codebook seed 0, which happens to be a *good* draw. They do **not** show that unguided decoding works in general: at seeds 42 and 21 unguided decoding returned 0/20 correct (all abstained, 0 silent-wrong). Unguided decode is a seed lottery (15/15 vs 1/15 across draws in `06-ring3-peel-diamond-correl-tabu-fret.md`). Only the cued `ds_clamp13` arm generalises across seeds. See the caveat at the end of this document. **Every query must carry a cue.**

> **Note.** The first sweep harness written by the fleet (v1) was invalid (unkeyed additive marks, the 17 ring never written, the bound decoder fed a sum, 8–10 trials per cell). This report is the rewritten harness; no v1 number is used anywhere in this corpus.

## Pre-registration (verbatim)

PASS if decode_soft's silent-wrong rate has a Wilson-99% UPPER bound <= 0.02 at every k <= 10 with min_confidence = 0.1, AND its correct rate at k = 5 exceeds direct_probe's correct rate at k = 5 by >= 0.20 absolute. Otherwise KILL (state which half failed).

## Setup

omni_ring (imported module), D=5120, rings (3, 5, 7, 13, 17), 100 trials per cell, decode_soft 30 iterations, gate = check_anomaly (17-ring CRT). Bound slots for decode_soft; direct (independent codebooks) slots for direct_probe. The first (v1) harness was invalid; its defects are listed in the reviewer's reading below.

Arm legend: `ds@t` = `decode_soft`, unguided, `min_confidence = t`; `ds_clamp13@0.1` = `decode_soft` with the 13 ring clamped to the target (cued); `dp` = `direct_probe` (sequential per-ring argmax). "silent-wrong" = a decode accepted by the 17-ring gate that is not a member of the slot.

## Results

| arm | k | correct [99% CI] | rejected | silent-wrong [99% CI] | chance-of-member |
|---|---|---|---|---|---|
| ds@0.0 | 1 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0007 |
| ds@0.0 | 2 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0015 |
| ds@0.0 | 5 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0037 |
| ds@0.0 | 10 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0073 |
| ds@0.0 | 20 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0147 |
| ds@0.0 | 50 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0366 |
| ds@0.0 | 100 | 99/100 [0.92,1.00] | 1/100 | 0/100 [0.00,0.06] | 0.0733 |
| ds@0.05 | 1 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0007 |
| ds@0.05 | 2 | 17/100 [0.09,0.29] | 83/100 | 0/100 [0.00,0.06] | 0.0015 |
| ds@0.05 | 5 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0037 |
| ds@0.05 | 10 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0073 |
| ds@0.05 | 20 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0147 |
| ds@0.05 | 50 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0366 |
| ds@0.05 | 100 | 99/100 [0.92,1.00] | 1/100 | 0/100 [0.00,0.06] | 0.0733 |
| ds@0.1 | 1 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0007 |
| ds@0.1 | 2 | 17/100 [0.09,0.29] | 83/100 | 0/100 [0.00,0.06] | 0.0015 |
| ds@0.1 | 5 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0037 |
| ds@0.1 | 10 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0073 |
| ds@0.1 | 20 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0147 |
| ds@0.1 | 50 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0366 |
| ds@0.1 | 100 | 99/100 [0.92,1.00] | 1/100 | 0/100 [0.00,0.06] | 0.0733 |
| ds@0.2 | 1 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0007 |
| ds@0.2 | 2 | 17/100 [0.09,0.29] | 83/100 | 0/100 [0.00,0.06] | 0.0015 |
| ds@0.2 | 5 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0037 |
| ds@0.2 | 10 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0073 |
| ds@0.2 | 20 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0147 |
| ds@0.2 | 50 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0366 |
| ds@0.2 | 100 | 99/100 [0.92,1.00] | 1/100 | 0/100 [0.00,0.06] | 0.0733 |
| ds@0.3 | 1 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0007 |
| ds@0.3 | 2 | 17/100 [0.09,0.29] | 83/100 | 0/100 [0.00,0.06] | 0.0015 |
| ds@0.3 | 5 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0037 |
| ds@0.3 | 10 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0073 |
| ds@0.3 | 20 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0147 |
| ds@0.3 | 50 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0366 |
| ds@0.3 | 100 | 99/100 [0.92,1.00] | 1/100 | 0/100 [0.00,0.06] | 0.0733 |
| ds_clamp13@0.1 | 1 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0007 |
| ds_clamp13@0.1 | 2 | 91/100 [0.81,0.96] | 9/100 | 0/100 [0.00,0.06] | 0.0015 |
| ds_clamp13@0.1 | 5 | 97/100 [0.89,0.99] | 3/100 | 0/100 [0.00,0.06] | 0.0037 |
| ds_clamp13@0.1 | 10 | 94/100 [0.85,0.98] | 6/100 | 0/100 [0.00,0.06] | 0.0073 |
| ds_clamp13@0.1 | 20 | 87/100 [0.76,0.93] | 13/100 | 0/100 [0.00,0.06] | 0.0147 |
| ds_clamp13@0.1 | 50 | 90/100 [0.80,0.95] | 10/100 | 0/100 [0.00,0.06] | 0.0366 |
| ds_clamp13@0.1 | 100 | 84/100 [0.72,0.91] | 16/100 | 0/100 [0.00,0.06] | 0.0733 |
| dp | 1 | 100/100 [0.94,1.00] | 0/100 | 0/100 [0.00,0.06] | 0.0007 |
| dp | 2 | 8/100 [0.03,0.18] | 88/100 | 4/100 [0.01,0.13] | 0.0015 |
| dp | 5 | 6/100 [0.02,0.15] | 90/100 | 4/100 [0.01,0.13] | 0.0037 |
| dp | 10 | 4/100 [0.01,0.13] | 92/100 | 4/100 [0.01,0.13] | 0.0073 |
| dp | 20 | 3/100 [0.01,0.11] | 91/100 | 6/100 [0.02,0.15] | 0.0147 |
| dp | 50 | 3/100 [0.01,0.11] | 92/100 | 5/100 [0.02,0.14] | 0.0366 |
| dp | 100 | 3/100 [0.01,0.11] | 93/100 | 4/100 [0.01,0.13] | 0.0733 |

Runtime 18s.

## Verdict

KILL: half 1 (silent-wrong): k=1 silent-wrong 0/100 upper 0.062 > 0.02; k=2 silent-wrong 0/100 upper 0.062 > 0.02; k=5 silent-wrong 0/100 upper 0.062 > 0.02; k=10 silent-wrong 0/100 upper 0.062 > 0.02

## Reviewer's reading (Claude, 2026-09-29)

- **The pre-registered bar was unattainable at the registered n** (a defect in the reviewer's own brief): with 0 silent-wrong in 100 trials the Wilson-99% upper bound is 0.062; even 0/300 gives 0.022. The KILL on half 1 is by construction, not evidence of silent errors.
- **What was measured:** decode_soft (min_confidence 0.1) made **0 silent-wrong decodes in 1,200 trials at k in {1,2,5,10}** (unguided arm, codebook seed 0; see the correction at the top) (300/cell, table below). At k=5 it recovered a true member **300/300 vs direct_probe 10/300** (direct_probe also returned 10/300 silent-wrong). Half 2 passes by 0.97.
- **k=2 is the weak point:** two equal marks give a symmetric mix; decode_soft **abstains** (229/300 rejected) rather than lying. A cue fixes it: clamping the 13 ring gives 271/300.
- **Clamped recall of the cued target** stays 86–100% up to k=100 (point estimates, 300 trials per load; lowest 99% CI bound 0.80), with ≤ 1/300 silent-wrong per cell.
- The fleet's v1 harness was invalid and was rewritten for this report: unkeyed additive marks, 17 ring never written, bound-decoder fed a sum, 8-10 trials/cell.

### Supplementary run: 300 trials per cell (same harness, `python3 bench/soft_sweep.py --trials 300`)

| arm | k | correct [99% CI] | rejected | silent-wrong [99% CI] | chance-of-member |
|---|---|---|---|---|---|
| ds@0.0 | 1 | 300/300 [0.98,1.00] | 0/300 | 0/300 [0.00,0.02] | 0.0007 |
| ds@0.0 | 2 | 298/300 [0.97,1.00] | 2/300 | 0/300 [0.00,0.02] | 0.0015 |
| ds@0.0 | 5 | 300/300 [0.98,1.00] | 0/300 | 0/300 [0.00,0.02] | 0.0037 |
| ds@0.0 | 10 | 300/300 [0.98,1.00] | 0/300 | 0/300 [0.00,0.02] | 0.0073 |
| ds@0.0 | 20 | 299/300 [0.97,1.00] | 1/300 | 0/300 [0.00,0.02] | 0.0147 |
| ds@0.0 | 50 | 300/300 [0.98,1.00] | 0/300 | 0/300 [0.00,0.02] | 0.0366 |
| ds@0.0 | 100 | 298/300 [0.97,1.00] | 2/300 | 0/300 [0.00,0.02] | 0.0733 |
| ds@0.05 | 1 | 300/300 [0.98,1.00] | 0/300 | 0/300 [0.00,0.02] | 0.0007 |
| ds@0.05 | 2 | 71/300 [0.18,0.31] | 229/300 | 0/300 [0.00,0.02] | 0.0015 |
| ds@0.05 | 5 | 300/300 [0.98,1.00] | 0/300 | 0/300 [0.00,0.02] | 0.0037 |
| ds@0.05 | 10 | 300/300 [0.98,1.00] | 0/300 | 0/300 [0.00,0.02] | 0.0073 |
| ds@0.05 | 20 | 299/300 [0.97,1.00] | 1/300 | 0/300 [0.00,0.02] | 0.0147 |
| ds@0.05 | 50 | 299/300 [0.97,1.00] | 1/300 | 0/300 [0.00,0.02] | 0.0366 |
| ds@0.05 | 100 | 298/300 [0.97,1.00] | 2/300 | 0/300 [0.00,0.02] | 0.0733 |
| ds@0.1 | 1 | 300/300 [0.98,1.00] | 0/300 | 0/300 [0.00,0.02] | 0.0007 |
| ds@0.1 | 2 | 71/300 [0.18,0.31] | 229/300 | 0/300 [0.00,0.02] | 0.0015 |
| ds@0.1 | 5 | 300/300 [0.98,1.00] | 0/300 | 0/300 [0.00,0.02] | 0.0037 |
| ds@0.1 | 10 | 300/300 [0.98,1.00] | 0/300 | 0/300 [0.00,0.02] | 0.0073 |
| ds@0.1 | 20 | 299/300 [0.97,1.00] | 1/300 | 0/300 [0.00,0.02] | 0.0147 |
| ds@0.1 | 50 | 299/300 [0.97,1.00] | 1/300 | 0/300 [0.00,0.02] | 0.0366 |
| ds@0.1 | 100 | 298/300 [0.97,1.00] | 2/300 | 0/300 [0.00,0.02] | 0.0733 |
| ds@0.2 | 1 | 300/300 [0.98,1.00] | 0/300 | 0/300 [0.00,0.02] | 0.0007 |
| ds@0.2 | 2 | 71/300 [0.18,0.31] | 229/300 | 0/300 [0.00,0.02] | 0.0015 |
| ds@0.2 | 5 | 300/300 [0.98,1.00] | 0/300 | 0/300 [0.00,0.02] | 0.0037 |
| ds@0.2 | 10 | 300/300 [0.98,1.00] | 0/300 | 0/300 [0.00,0.02] | 0.0073 |
| ds@0.2 | 20 | 299/300 [0.97,1.00] | 1/300 | 0/300 [0.00,0.02] | 0.0147 |
| ds@0.2 | 50 | 299/300 [0.97,1.00] | 1/300 | 0/300 [0.00,0.02] | 0.0366 |
| ds@0.2 | 100 | 298/300 [0.97,1.00] | 2/300 | 0/300 [0.00,0.02] | 0.0733 |
| ds@0.3 | 1 | 300/300 [0.98,1.00] | 0/300 | 0/300 [0.00,0.02] | 0.0007 |
| ds@0.3 | 2 | 71/300 [0.18,0.31] | 229/300 | 0/300 [0.00,0.02] | 0.0015 |
| ds@0.3 | 5 | 300/300 [0.98,1.00] | 0/300 | 0/300 [0.00,0.02] | 0.0037 |
| ds@0.3 | 10 | 300/300 [0.98,1.00] | 0/300 | 0/300 [0.00,0.02] | 0.0073 |
| ds@0.3 | 20 | 299/300 [0.97,1.00] | 1/300 | 0/300 [0.00,0.02] | 0.0147 |
| ds@0.3 | 50 | 299/300 [0.97,1.00] | 1/300 | 0/300 [0.00,0.02] | 0.0366 |
| ds@0.3 | 100 | 298/300 [0.97,1.00] | 2/300 | 0/300 [0.00,0.02] | 0.0733 |
| ds_clamp13@0.1 | 1 | 300/300 [0.98,1.00] | 0/300 | 0/300 [0.00,0.02] | 0.0007 |
| ds_clamp13@0.1 | 2 | 271/300 [0.85,0.94] | 29/300 | 0/300 [0.00,0.02] | 0.0015 |
| ds_clamp13@0.1 | 5 | 294/300 [0.95,0.99] | 6/300 | 0/300 [0.00,0.02] | 0.0037 |
| ds_clamp13@0.1 | 10 | 280/300 [0.89,0.96] | 19/300 | 1/300 [0.00,0.03] | 0.0073 |
| ds_clamp13@0.1 | 20 | 259/300 [0.80,0.91] | 40/300 | 1/300 [0.00,0.03] | 0.0147 |
| ds_clamp13@0.1 | 50 | 262/300 [0.82,0.91] | 38/300 | 0/300 [0.00,0.02] | 0.0366 |
| ds_clamp13@0.1 | 100 | 257/300 [0.80,0.90] | 43/300 | 0/300 [0.00,0.02] | 0.0733 |
| dp | 1 | 300/300 [0.98,1.00] | 0/300 | 0/300 [0.00,0.02] | 0.0007 |
| dp | 2 | 42/300 [0.10,0.20] | 249/300 | 9/300 [0.01,0.07] | 0.0015 |
| dp | 5 | 10/300 [0.02,0.07] | 280/300 | 10/300 [0.02,0.07] | 0.0037 |
| dp | 10 | 13/300 [0.02,0.08] | 273/300 | 14/300 [0.02,0.09] | 0.0073 |
| dp | 20 | 5/300 [0.01,0.05] | 283/300 | 12/300 [0.02,0.08] | 0.0147 |
| dp | 50 | 6/300 [0.01,0.05] | 280/300 | 14/300 [0.02,0.09] | 0.0366 |
| dp | 100 | 2/300 [0.00,0.03] | 286/300 | 12/300 [0.02,0.08] | 0.0733 |

300 trials/cell, 55s
VERDICT: KILL -- half 1 (silent-wrong): k=1 silent-wrong 0/300 upper 0.022 > 0.02; k=2 silent-wrong 0/300 upper 0.022 > 0.02; k=5 silent-wrong 0/300 upper 0.022 > 0.02; k=10 silent-wrong 0/300 upper 0.022 > 0.02

## Reviewer's caveat (2026-09-29, later): unguided results are seed-dependent

The unguided decode_soft rows above used codebook seed 0. Re-run at 20 trials: seed 0 unguided k=1/5/10 = 20/20/20 correct; **seeds 42 (engine default) and 21 = 0/0/0 correct, 0 silent-wrong (all abstain)**. Clamped (13-ring cue) = 20/19/16 (seed 42) and 20/19/18 (seed 21), 0 silent-wrong. Cause: rotation codebooks collapse the chain to one rotation, so unguided factorisation is marginal at D = 5,120 and depends on the draw. **Rule: every query carries a cue.** Silent-wrong stayed 0 in every arm and seed.

# RING-1: direct (keyed) vs bound storage, and a 1-bit tag for two marks per slot

| | |
|---|---|
| **Date** | 2026-09-29 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). Every number was measured on a 2019 laptop CPU (Intel i5-8365U, AVX2, no GPU); the author reviews each document before publication. |
| **Type** | measured result |
| **Verdict** | PASS (after a brief defect was fixed; see the note and appendix below) |
| **Code** | numpy research harness (`harness/ring1/run_direct.py`); keyed direct read ships in omni-ring |

**History.** Built by a fleet open-weight model; fixed and re-run by Claude. The first run reported KILL (40% direct decode). That was a defect in the experiment brief, not a finding: residue codebooks share position 0 across rings, so SUM storage interferes (see *Appendix: the brief defect* below). Fixes: (1) each ring is bound to its own random unit key for direct storage (k16 keys sit on the 16-position dial); (2) the decision block had rebuilt UNKEYED rings and re-created its RNG inside the loop, scoring one mark 1,000 times, so it now uses the measured (a) result; (3) `--quick` is a non-decisive smoke run (n = 100 cannot clear a 0.99 Wilson bound). Full output: `appendix/RING1-DIRECT.run.txt`.

## Pre-registration (verbatim)

PASS if direct single-mark decode is >= 0.99 exact (Wilson-99% lower bound) under float, AND the tagged 2-mark both-correct rate's Wilson-99% lower bound exceeds the untagged rate's point value. Otherwise KILL (report which half failed).

## Results (`python3 harness/ring1/run_direct.py`, mods 3-5-7-13-17, D = 5,120)

| | exact / n | Wilson 99% | time per read |
|---|---|---|---|
| direct, float (45 probes + CRT) | **1000/1000** | [0.993, 1.000] | 0.6 ms |
| direct, k16 | **1000/1000** | [0.993, 1.000] | 0.6 ms |
| bound + resonate (same marks, float) | 1000/1000 | [0.993, 1.000] | 6.7 ms |
| 2 marks, untagged (c = 0) | 267/300 = 89% | [0.835, 0.928] | — |
| 2 marks, 1-bit tag (T, T*) | **300/300** | [0.978, 1.000] | — |

**Verdict:** both clauses met → **PASS**.

## What this means for the bus

- A single-mark slot is read directly, with no resonator: exact, on the 16-position dial too, and ~11× faster than resonating (numpy timings). "Just go to the coordinates" holds once each ring has its own key.
- Two marks can share a slot cleanly with a 1-bit tag (100% vs 89%).
- Storage policy: one mark per slot → direct keyed storage; two → tag; more → bound + resonator with a cue (RING1-CORE: capacity 12 at one clamped ring).

## Open issues

Speed was compared in numpy only; the C int8 kernel numbers belong to the step-5 path.

---

## Appendix: the brief defect (reviewer note, 2026-09-28)

**Applies to:** the first run of this experiment (KILL: direct single-mark decode 40%).

**Cause.** The brief specified direct storage as the plain SUM of the rings' position vectors from `make_rings`.
Residue codebooks make position 0 of every ring the same all-ones vector (`exp(i*0*theta)`). Under summation the
rings therefore interfere: any ring sitting at residue 0 reads as residue 0 on every other ring. Binding never sees
this, because the product is keyed by the combination.

**Measured** (read-only, `ring1_core` unchanged, mods 3-5-7-13-17, D = 5,120, 300 marks):

- position-0 vector identical across rings: True
- direct decode as briefed (no ring key): **156/300**
- direct decode with each ring bound to its own random key: **300/300**

**Disposition.** Part (a) was invalid as briefed and was re-run with per-ring keys (the results above). Part (b), the
1-bit tag, was 30/30 vs 24/30 untagged in the first small run; the full re-run above (300/300 vs 267/300) supersedes it.

# RING-3: peeling, diamond facets, correlated codebooks, tabu knockout and coarse-to-fine dials

| | |
|---|---|
| **Date** | 2026-09-29 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). Every number was measured on a 2019 laptop CPU (Intel i5-8365U, AVX2, no GPU); the author reviews each document before publication. |
| **Type** | measured result |
| **Verdict** | PEEL PASS; DIAMOND, CORREL, TABU, FRET KILL (DIAMOND-2 follow-up: 15-value corners reach 91%) |
| **Code** | research harness (`harness/ring3/`); peeling ships in omni-ring as `omni_ring.peel` |

Run by Claude on 2026-09-29 at 02:50, 150 trials per cell, D = 5,120. Raw output: `appendix/RING3-RESULTS.run.txt`, `appendix/RING3-RECS.run.txt`, `appendix/RING3b-DIAMOND2.run.txt`.

| test | verdict | reason |
|---|---|---|
| DIAMOND | KILL | diamond lower 0.261 vs flat 0.960 (fail); centre checksum flags 206/222 wrong settles (ok) |
| PEEL | PASS | M=24: 'peel 2 sweeps' 14.77 vs plain 8.45 true marks/slot (ok); fakes 82/2298 upper 0.047 (ok) |
| CORREL | KILL | plain drop rho 0->0.3 = -0.03 (fail); whitened@0.3 vs plain@0 = +0.03 (ok); plain@0.6 0.52, whitened@0.6 0.75 |
| TABU | KILL | stuck 44; rescued 5 (11.4%, fail); silent-wrong 8 (upper 0.369, fail) |
| FRET | KILL | M=12 clustered: coarse-to-fine 135/150 = 90.0% [81.9%, 94.7%] vs flat 140/150 = 93.3% [86.0%, 96.9%] (fail) |

## DIAMOND: KILL
**Pre-registered:** PASS if, at M = 12 marks per slot with 2 corners known, the diamond's recall of BOTH unknown corners has a Wilson-99% lower bound >= the flat (3,5,7,13)+17 system's point recall with 2 clamps (13 and 7), AND the centre checksum ring flags >= 50% of wrong settles (pooled over M in {12, 24}). Otherwise KILL.

**Result:** diamond lower 0.261 vs flat 0.960 (fail); centre checksum flags 206/222 wrong settles (ok) (38 s)

| system | M | recall of both unknown corners (2 known) | wrong settles flagged by centre | median iters |
|---|---|---|---|---|
| diamond: 4 category corners x 105 + centre checksum 17 | 12 | 53/150 = 35.3% [26.1%, 45.8%] | 90/97 | 4 |
| diamond: 4 category corners x 105 + centre checksum 17 | 24 | 25/150 = 16.7% [10.3%, 25.9%] | 116/125 | 5 |
| flat (3,5,7,13)+17 rotation rings, 2 clamps | 12 | 144/150 = 96.0% [89.6%, 98.5%] | n/a | n/a |
| flat (3,5,7,13)+17 rotation rings, 2 clamps | 24 | 132/150 = 88.0% [79.5%, 93.3%] | n/a | n/a |

## PEEL: PASS
**Pre-registered:** [revised after smoke: cued readout] PASS if, at M = 24, two 13-ring clamp sweeps WITH explaining-away (subtract each accepted mark) recover >= 1.25x the true marks of one plain sweep, with accepted fakes Wilson-99% upper bound <= 0.05. Otherwise KILL.

**Result:** M=24: 'peel 2 sweeps' 14.77 vs plain 8.45 true marks/slot (ok); fakes 82/2298 upper 0.047 (ok) (190 s)

| M | arm | true marks recovered / slot | accepted fakes / accepted |
|---|---|---|---|
| 12 | plain 1 sweep | 6.44 (of 12) | 52/1018 |
| 12 | peel 2 sweeps | 10.49 (of 12) | 140/1714 |
| 12 | peel 2 sweeps annealed | 10.43 (of 12) | 130/1695 |
| 24 | plain 1 sweep | 8.45 (of 24) | 45/1312 |
| 24 | peel 2 sweeps | 14.77 (of 24) | 82/2298 |
| 24 | peel 2 sweeps annealed | 14.72 (of 24) | 90/2298 |

## CORREL: KILL
**Pre-registered:** PASS if plain recall at rho = 0.3 falls >= 0.20 below plain recall at rho = 0 (similar codebooks hurt), AND the listener fix (whitened scores) at rho = 0.3 is within 0.10 of plain recall at rho = 0. Otherwise KILL (state which half failed).

**Result:** plain drop rho 0->0.3 = -0.03 (fail); whitened@0.3 vs plain@0 = +0.03 (ok); plain@0.6 0.52, whitened@0.6 0.75 (9 s)

| rho | measured neighbour similarity | read | target recall, M=4, 13 ring clamped |
|---|---|---|---|
| 0.0 | 0.00 | plain | 130/150 = 86.7% [77.9%, 92.3%] |
| 0.0 | 0.00 | listener-whitened | 130/150 = 86.7% [77.9%, 92.3%] |
| 0.3 | 0.35 | plain | 134/150 = 89.3% [81.1%, 94.2%] |
| 0.3 | 0.35 | listener-whitened | 135/150 = 90.0% [81.9%, 94.7%] |
| 0.6 | 0.80 | plain | 78/150 = 52.0% [41.6%, 62.2%] |
| 0.6 | 0.80 | listener-whitened | 113/150 = 75.3% [65.3%, 83.2%] |
| 0.8 | 0.93 | plain | 13/150 = 8.7% [4.4%, 16.5%] |
| 0.8 | 0.93 | listener-whitened | 27/150 = 18.0% [11.3%, 27.4%] |

## TABU: KILL
**Pre-registered:** [revised: stuck = settle illegal under the 17 ring OR not converged] PASS if, over stuck trials pooled over M in {12, 24, 48}, knockout+consensus rescues (accepts the correct target) >= 50% of them, with silent-wrong accepts <= 2% of stuck trials (Wilson-99% upper bound <= 0.05). Otherwise KILL.

**Result:** stuck 44; rescued 5 (11.4%, fail); silent-wrong 8 (upper 0.369, fail) (9 s)

| M | stuck (illegal or not converged, of 150) | rescued (correct target accepted) | silent-wrong accepted |
|---|---|---|---|
| 12 | 9 | 2/9 = 22.2% [4.5%, 63.5%] | 0/9 = 0.0% [0.0%, 42.4%] |
| 24 | 14 | 2/14 = 14.3% [2.8%, 48.7%] | 2/14 = 14.3% [2.8%, 48.7%] |
| 48 | 21 | 1/21 = 4.8% [0.6%, 30.7%] | 6/21 = 28.6% [11.0%, 56.4%] |

## FRET: KILL
**Pre-registered:** [revised: crowded near-identical cell decides] PASS if, at M = 12 items with angles clustered within 60 ticks, coarse-to-fine's any-member symbol+angle (|err| <= 1) Wilson-99% lower bound exceeds the flat resonator's point rate by >= 0.20. Otherwise KILL.

**Result:** M=12 clustered: coarse-to-fine 135/150 = 90.0% [81.9%, 94.7%] vs flat 140/150 = 93.3% [86.0%, 96.9%] (fail) (89 s)

| M items | angles | flat resonator (1,000 dial positions) | coarse-to-fine |
|---|---|---|---|
| 1 | uniform | 150/150 = 100.0% [95.8%, 100.0%] | 150/150 = 100.0% [95.8%, 100.0%] |
| 3 | uniform | 149/150 = 99.3% [94.6%, 99.9%] | 145/150 = 96.7% [90.5%, 98.9%] |
| 6 | clustered within 60 ticks | 138/150 = 92.0% [84.4%, 96.1%] | 147/150 = 98.0% [92.4%, 99.5%] |
| 12 | clustered within 60 ticks | 140/150 = 93.3% [86.0%, 96.9%] | 135/150 = 90.0% [81.9%, 94.7%] |

coarse pass: 616 of 5120 low-frequency dims on a 20-tick grid; kernel width L = 8.0; dial 1000 ticks; 20 symbols.

## Harness disclosure
The first smoke (kept as `harness/ring3/run_ring3.v1-smoke.py`) exposed design defects, fixed before the full run: unguided settles on the rotation rings are a **seed lottery** (codebook seeds 0/1/2 decode a clean single mark 15/15; seeds 3/21/42 give 1/15, and 42 is the engine default), so every test runs **cued**; DIAMOND corners became category codebooks with a centre checksum ring (per-corner residue chains gave 0/20 with no foothold); uniform codebook similarity turned out to be argmax-invariant, so CORREL uses neighbour-chained similarity with a read-time whitening fix; TABU "stuck" = illegal or non-converged settle; FRET adds crowded near-identical cells. PEEL, TABU and FRET pre-registrations were revised (marked) before the full run.

## Exploratory arms (`run_ring3_recs.py`)
| arm | result |
|---|---|
| PEEL M=24, projection vs whole-codeword subtraction | 15.18 vs 15.14 true/slot, fakes 3.1% vs 3.2%: no difference (we subtract exact codewords, not noisy estimates) |
| TABU, gap-weighted vs majority consensus | rescued 13.6% vs 11.4%, silent-wrong **45.5% vs 18.2%**: worse (always picks) |

## Reviewer's reading (Claude)
- **PEEL is the win:** two cued sweeps with explaining-away read **14.8 of 24** marks per slot vs 8.45 for one sweep (+75%), 10.5 of 12 at M = 12; fakes 3.6%. Crowded slots are readable one mark at a time.
- **Centre checksum is a keeper; big category corners are not:** the checksum flagged 206/222 (93%) wrong settles, but two known corners recover the two unknown 105-way corners only 35% (M = 12) vs 96% for the flat residue system with 2 clamps. Corners need small codebooks or their own cue.
- **Similarity tolerance:** neighbour similarity 0.35 costs nothing; 0.80 drops recall to 52%, and read-time whitening ("tune the listener") restores 75%. 0.93 is unreadable either way.
- **TABU: do not adopt.** Knockout rescues 11% of stuck settles and turns 18% into silent errors. A stuck/illegal settle should **abstain**; detecting it is the value.
- **FRET: the dial is not the bottleneck.** A flat search over 1,000 dial positions reads 93% even with 12 near-identical items; coarse-to-fine is no better. RING1-SMOOTH's failure came from crowding and the 5-ring context, not dial resolution.
- **Rule confirmed across seeds: every query carries a cue.**

## RING-3b DIAMOND-2 (2026-09-29; `harness/ring3/run_diamond2.py`, 150 trials/cell, 2 corners known)
| design | M | recall of both unknown corners (2 known) | wrong settles flagged |
|---|---|---|---|
| (a) category corners K=15 + checksum | 12 | 136/150 = 90.7% [82.7%, 95.2%] | 8/14 |
| (a) category corners K=15 + checksum | 24 | 118/150 = 78.7% [68.9%, 86.0%] | 19/32 |
| (a) category corners K=35 + checksum | 12 | 105/150 = 70.0% [59.7%, 78.6%] | 42/45 |
| (a) category corners K=35 + checksum | 24 | 83/150 = 55.3% [44.9%, 65.3%] | 60/67 |
| (b) residue corners (3,5,7)+11, 7-ring cue per unknown corner | 12 | 42/150 = 28.0% [19.6%, 38.2%] | 106/108 |
| (b) residue corners (3,5,7)+11, 7-ring cue per unknown corner | 24 | 20/150 = 13.3% [7.7%, 22.1%] | 126/130 |
| (c) 105-value corners split into random category sub-rings 3x5x7 + checksum | 12 | 7/150 = 4.7% [1.8%, 11.3%] | 137/143 |
| (c) 105-value corners split into random category sub-rings 3x5x7 + checksum | 24 | 6/150 = 4.0% [1.5%, 10.4%] | 138/144 |

**Rule:** corner size is the lever and free factors multiply the search: few free facets, each small (≤ 15–35 values), centre checksum kept. K=15 corners reach 91% at M=12 (flat residue system with 2 clamps: 96%). Splitting a corner into sub-rings (more free factors) collapses recall (4.7%); rotation-ring corners stay poor even with a per-corner cue (28%).

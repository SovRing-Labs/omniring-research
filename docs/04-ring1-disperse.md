# RING-1: does dispersing marks over many slots beat one crowded slot?

| | |
|---|---|
| **Date** | 2026-09-29 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). Every number was measured on a 2019 laptop CPU (Intel i5-8365U, AVX2, no GPU); the author reviews each document before publication. |
| **Type** | measured result (negative) |
| **Verdict** | KILL: at M = 48 the best S ≥ 4 cell (S = 16) has a Wilson-99% lower bound of 0.1714, which does not exceed the S = 1 point recall (0.2750) by the required 0.20 |
| **Code** | numpy research harness (`harness/ring1/run_disperse.py`) |

## Pre-registration

Copied verbatim from the brief, before any result was read:

> Pre-registered decision (do not change): PASS if, at M = 48, the best cell with S >= 4 has a Wilson-99% LOWER bound of target recall that exceeds the S = 1 cell's point recall by at least 0.20 absolute. Otherwise KILL: dispersal does not beat one crowded slot.

Applied mechanically by `decide()` in `harness/ring1/run_disperse.py`; no threshold was tuned after seeing data. M = 48, minimum S = 4, required margin = 0.20 absolute on the Wilson-99% lower bound.

## Setup

- Harness: `harness/ring1/ring1_core.py`, imported unchanged. mods (3,5,7,13), D = 5120, quant `float`, mark space 1365 (marks drawn uniformly from 0..1364).
- Grid: M in [12, 24, 48, 96], S in [1, 2, 4, 8, 16]. M marks dealt round-robin over S slots (M/S per slot); cells with M/S < 1 are skipped, which drops only (M=12, S=16) -> 19 cells.
- Query: ring 13 (index 3) clamped to `target % 13`, c = 1 clamped ring; that single clamp is broadcast to EVERY slot. Each slot is resonated independently (max_iter=50) and decoded with `crt`.
- Winner: argmax over slots of the normalised match `Re<slot, encode(d)> / (|slot| * |encode(d)|)`, ties to the lowest slot index. A trial is a **hit** when the winner's decoded mark equals the target, and a **winner = holder** when the winning slot is the slot the target was actually dealt into.
- Seeds: codebook seed 0 (shared by every cell, so the rings are paired across the grid); trial seed = 90210 + M*100003 + trial, depending on (M, trial) but NOT on S. Every S at a given M therefore sees the SAME marks and the SAME target, so the S comparison is paired rather than independent.
- Trials: 200 per cell. Intervals: Wilson score, z = 2.5758 (two-sided 99%).
- Command: `python3 harness/ring1/run_disperse.py`
- Wall time for the whole run: 227.5 s.
- `--quick` (30 trials/cell) is a smoke run and deliberately does NOT write this report; the gate runs it without overwriting the full-run numbers below.

## Results

| # | M | S | marks/slot | hits/trials | target recall | Wilson-99% | chance 1/M | winner = holder | probe iters/query | wall ms/query |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 12 | 1 | 12 | 147/200 | **73.5%** | [64.8%, 80.7%] | 8.33% | 200/200 (100.0%) | 2.0 | 7.56 |
| 2 | 12 | 2 | 6 | 132/200 | **66.0%** | [57.0%, 74.0%] | 8.33% | 160/200 (80.0%) | 4.8 | 13.48 |
| 3 | 12 | 4 | 3 | 143/200 | **71.5%** | [62.7%, 78.9%] | 8.33% | 149/200 (74.5%) | 11.0 | 33.78 |
| 4 | 12 | 8 | 1 | 130/200 | **65.0%** | [56.0%, 73.1%] | 8.33% | 131/200 (65.5%) | 20.4 | 69.70 |
| 5 | 24 | 1 | 24 | 89/200 | **44.5%** | [35.8%, 53.6%] | 4.17% | 200/200 (100.0%) | 2.2 | 7.99 |
| 6 | 24 | 2 | 12 | 91/200 | **45.5%** | [36.7%, 54.6%] | 4.17% | 140/200 (70.0%) | 4.4 | 18.20 |
| 7 | 24 | 4 | 6 | 98/200 | **49.0%** | [40.1%, 58.0%] | 4.17% | 114/200 (57.0%) | 9.9 | 32.60 |
| 8 | 24 | 8 | 3 | 98/200 | **49.0%** | [40.1%, 58.0%] | 4.17% | 103/200 (51.5%) | 22.9 | 74.33 |
| 9 | 24 | 16 | 1 | 102/200 | **51.0%** | [42.0%, 59.9%] | 4.17% | 102/200 (51.0%) | 41.5 | 162.15 |
| 10 | 48 | 1 | 48 | 55/200 | **27.5%** | [20.2%, 36.3%] | 2.08% | 200/200 (100.0%) | 2.3 | 9.54 |
| 11 | 48 | 2 | 24 | 45/200 | **22.5%** | [15.8%, 30.9%] | 2.08% | 103/200 (51.5%) | 4.4 | 19.10 |
| 12 | 48 | 4 | 12 | 42/200 | **21.0%** | [14.6%, 29.3%] | 2.08% | 77/200 (38.5%) | 9.7 | 36.86 |
| 13 | 48 | 8 | 6 | 45/200 | **22.5%** | [15.8%, 30.9%] | 2.08% | 65/200 (32.5%) | 21.0 | 80.46 |
| 14 | 48 | 16 | 3 | 48/200 | **24.0%** | [17.1%, 32.5%] | 2.08% | 51/200 (25.5%) | 46.5 | 190.36 |
| 15 | 96 | 1 | 96 | 32/200 | **16.0%** | [10.4%, 23.8%] | 1.04% | 200/200 (100.0%) | 2.3 | 11.07 |
| 16 | 96 | 2 | 48 | 23/200 | **11.5%** | [6.9%, 18.6%] | 1.04% | 98/200 (49.0%) | 4.4 | 21.31 |
| 17 | 96 | 4 | 24 | 24/200 | **12.0%** | [7.3%, 19.2%] | 1.04% | 58/200 (29.0%) | 8.7 | 35.41 |
| 18 | 96 | 8 | 12 | 37/200 | **18.5%** | [12.5%, 26.5%] | 1.04% | 48/200 (24.0%) | 18.5 | 79.24 |
| 19 | 96 | 16 | 6 | 37/200 | **18.5%** | [12.5%, 26.5%] | 1.04% | 43/200 (21.5%) | 41.2 | 172.92 |

### The pre-registered comparison at M = 48

| # | M | S | marks/slot | hits/trials | target recall | Wilson-99% | chance 1/M | winner = holder | probe iters/query | wall ms/query |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 48 | 16 | 3 | 48/200 | **24.0%** | [17.1%, 32.5%] | 2.08% | 51/200 (25.5%) | 46.5 | 190.36 |
| 2 | 48 | 8 | 6 | 45/200 | **22.5%** | [15.8%, 30.9%] | 2.08% | 65/200 (32.5%) | 21.0 | 80.46 |
| 3 | 48 | 4 | 12 | 42/200 | **21.0%** | [14.6%, 29.3%] | 2.08% | 77/200 (38.5%) | 9.7 | 36.86 |
| 4 | 48 | 1 | 48 | 55/200 | **27.5%** | [20.2%, 36.3%] | 2.08% | 200/200 (100.0%) | 2.3 | 9.54 |

**Verdict: KILL: at M=48 the best S>=4 cell (S=16) has a Wilson-99% lower bound of 0.1714, which does NOT exceed the S=1 point recall of 0.2750 by the required 0.20 (short by 0.3036): dispersal does not beat one crowded slot**

**Reason: at M=48 the best S>=4 cell (S=16) has a Wilson-99% lower bound of 0.1714, which does NOT exceed the S=1 point recall of 0.2750 by the required 0.20 (short by 0.3036): dispersal does not beat one crowded slot**

Probe cost is the total resonator iterations summed over all S slots of one broadcast query; wall time is the same query end to end (resonate + decode + score for every slot).

## What this means for the bus

**Cost of spreading.** A broadcast is 16 resonator calls at S=16 versus 1 at S=1. The same cue that finds a mark in one crowded slot has to be pushed through every slot of a dispersed array, and the resonator iteration count is what you pay for it (41 iters/query at S=16 versus 2 at S=1). Layout is not free on a bus: a dispersed array trades readout work for per-slot capacity.

**Cue, not key.** The 13-ring clamp is doing the selection work, not the layout. The clamp is the one shared input that makes the readout comparable across slots; the winner is then the slot whose own residue is most consistent with the cue. That is the shape a real bus wants: broadcast one narrow cue, let the array self-select, and read the slot index rather than a separate address decoder.

**Verdict as measured.** at M=48 the best S>=4 cell (S=16) has a Wilson-99% lower bound of 0.1714, which does NOT exceed the S=1 point recall of 0.2750 by the required 0.20 (short by 0.3036): dispersal does not beat one crowded slot

## Open issues

- Only one codebook seed (0) was run. The rings are random draws, so per-cell numbers carry codebook variance that Wilson intervals over 200 trials do NOT capture. A seed sweep is the honest next step before quoting any absolute recall.
- The score is an inner product against the slot's OWN decoded mark, so it measures 'is this slot self-consistent' rather than an absolute confidence. It says nothing about whether the decoded mark is the right one; that is what the hit column is for.
- `quant` is `float` only. The 5-bit phase layer (`k16`) is the storage-realistic setting and was not swept here; T-series siblings carry that comparison.
- D = 5120 is inherited from the RING-1 harness. No dimension sweep, so no claim is made about how these recalls move with slot capacity on a real bus.
- Cells with M/S not an integer (e.g. M=12, S=8 -> slots of 2 and 1) carry unequal slot loads, which is a second, uncontrolled variable besides S. Isolating it needs a separate balanced-deal run.

## Reviewer's reading (Claude, 2026-09-29)
Full run by Claude (200 trials/cell; the fleet harness's report writer crashed on a `%` in a format string, fixed). The KILL is the selection problem, not storage: at M = 48, S = 16 (3 marks/slot) target recall 24.0% while the winning slot was the true holder only 25.5% of the time, so recall given the right slot is ≈ 94%. Dispersal works inside a slot; choosing the slot fails when every slot looks equally plausible. Follow-ups: RING-3 DIAMOND (facet systems: a known corner routes), PEEL, and a check-ring filter on slot selection. DIAMOND and PEEL were measured next (`06-ring3-peel-diamond-correl-tabu-fret.md`, `07-peel-read-all-module.md`).

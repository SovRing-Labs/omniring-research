# RING-1 T4: a two-stage halo chain against one resonator on crowded slots

| | |
|---|---|
| **Date** | 2026-09-28 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). Every number was measured on a 2019 laptop CPU (Intel i5-8365U, AVX2, no GPU); the author reviews each document before publication. |
| **Type** | measured result |
| **Verdict** | KILL (pre-registered). The two-stage chain ties the one-resonator on accuracy and costs 2.5x the median iterations. |
| **Code** | `harness/ring1/run_halo.py` (see `harness/README.md`) |

KILL: the halo buys nothing — at M = 32 the two-stage chain's Wilson-99% lower bound (31.7%) does not exceed the one-resonator's point recall (38.0%), and it costs 2.5x the median iterations (5.0 vs 2.0), not 0.5x



**Pillar** Nervous System — the Loop's **Read** step
**Verdict** `KILL`. The pre-registered bar was not met in either clause, at either load. This is a
clean negative result, not a broken run: the harness proves it is RING1-CORE's own harness before
it reports a single number.
**Raw output** `docs/appendix/RING1-HALO.run.txt` (104 lines, the full run verbatim)

---

## Pre-registration (verbatim from the brief, fixed before any trial ran)

> PASS if Arm B's target recall Wilson-99% lower bound exceeds Arm A's point recall at M = 32,
> OR Arm B matches Arm A (intervals overlap) with <= 0.5x the median total iterations. Otherwise
> KILL (the halo buys nothing).

> Same problems for both arms: mods (3,5,7,13), float, M in (12, 32), 300 trials, the 13-ring
> clamped to the target. Arm A: one resonator over all free rings (as RING1-CORE). Arm B (halo):
> stage 1 resonates only the 7-ring against the slot with the 13-ring clamped and the 3- and
> 5-rings held at their codebook means; its settled 7-residue then clamps stage 2, which resonates
> the 3- and 5-rings. Report target recall, median total iterations and wall time for both arms.

> fixed seeds; the decision criterion below is pre-registered (copy it verbatim into the report
> before the results); every number from a command you ran (paste command + output); chance rate
> beside every recall; Wilson 99% intervals on every rate.

**No threshold in this report was fitted to any number below.** The criterion is printed verbatim
at the top of every run by `run_halo.py`, above the results, before them.

### How the ambiguous clause was resolved — stated before the run

Clause 1 names `M = 32` explicitly. Clause 2 ("matches Arm A with <= 0.5x the median total
iterations") names no load at all. The runner therefore evaluates the criterion **at M = 32** — the
crowded cell the task is named for and the cell clause 1 names — and prints the identical test at
M = 12 beside it for transparency. **Both loads give the same verdict (KILL), so no reader needs a
different reading of the criterion to agree with this report.** The `NOTE:` branch in the runner
prints a divergence flag when a M=32-only PASS occurs; it did not trigger.

---

## Setup

One new file, exactly the one the brief names. No existing file was edited — `ring1_core.py` is
byte-identical to what RING1-CORE sealed.

| File | Role |
|---|---|
| `harness/ring1/run_halo.py` | The runner: both arms, the paired grid, the two integrity gates, the decision. |

Fixed configuration, identical to RING1-CORE's T1: `D = 5120`, `mods = (3, 5, 7, 13)` →
**1,365 states**, marks uniform on 0..1364, target = the **first** mark in the slot,
`max_iter = 50`, `quant = float`, base seed `20260928` (RING1-CORE's base seed, so the codebooks
are the same codebooks). 300 trials per cell, 600 per arm-pair. Python 3.12.3, numpy 2.5.3, no
other dependency, no C kernel, BLAS threads pinned to 4.

**Arm A** is `ring1_core.resonate()` called with `{13-ring: target % 13}` — RING1-CORE's T1 cell,
unmodified.

**Arm B** needs a resonator that can freeze rings, and `ring1_core` exposes no free-ring subset —
so `run_halo.py` carries `resonate_free()`, a generalisation with an explicit free-ring set. It is
a faithful copy of the library loop with one addition: rings that are neither clamped nor listed as
free are *held* at their codebook mean (they still enter the unbind product, they are never
updated). Given the default free set it must equal `ring1_core.resonate()` exactly — and that is
asserted, not assumed (below).

**What stage 1 physically is, stated plainly.** In Arm A every free ring *also* starts at its
codebook mean. So the state Arm A occupies at the end of its first sweep is exactly the state
Arm B's stage 1 starts from. The halo is not a different operator; it is **Arm A with the 3- and
5-rings frozen after one sweep, then each settled residue used as a cue for the rest.** That is
the whole claim under test, and it is the fairest possible framing of it.

### Commands run (every number below comes from one of these)

```
$ cd the project root && python3 harness/ring1/run_halo.py --verify-only
$ cd the project root && python3 harness/ring1/run_halo.py --quick
$ cd the project root && python3 harness/ring1/run_halo.py
```

**Budget** — brief allows ≤ 20 min full, < 3 min for `--quick`. Measured: **full 13.1–23.9s**,
**quick 0.8–2.0s**. The full run is 1,200 settles (600 per arm).

### Integrity 1 — the two arms are provably the same harness

Because `resonate_free()` is a local re-implementation, the report would be meaningless if it
quietly differed from the library. It is checked, not trusted:

```
--- INTEGRITY 1: resonate_free() == ring1_core.resonate() ---
  40 random problems (load 1..8, clamp 0..2): 0 mismatches
  EQUIVALENCE PASS
```

Compared field for field — positions, iters, converged, cycled, gap_first, gap_min (gaps within
1e-12). The runner **exits 1 and reports nothing** if this fails.

### Integrity 2 — Arm A is provably RING1-CORE's own cell

Arm A is re-run on RING1-CORE's own T1 `SeedSequence`s (stream 1, c=1, float, 200 trials) and must
reproduce its published counts exactly:

```
--- INTEGRITY 2: Arm A reproduces RING1-CORE (T1, c=1, float, 200 trials) ---
  M=12  this run 134/200 target, 200/200 any-mark, medIt 2.0   RING1-CORE 134/200 target, 200/200 any-mark, medIt 2.0   MATCH
  M=32  this run  69/200 target, 196/200 any-mark, medIt 2.0   RING1-CORE  69/200 target, 196/200 any-mark, medIt 2.0   MATCH
  HARNESS CROSS-CHECK PASS
```

This is the strongest evidence in the report: **the A-side numbers quoted below are the same
numbers RING1-CORE already sealed**, reached through a different file. Any difference between the
arms is therefore the arms, not the rig.

---

## Results

`target` = all four rings equal the **target's** residues. `any-mark` = all four rings equal
**some** mark in the slot. `chance` = 1/M (pre-registered). Wilson 99% on every rate. n = 300 per
cell, **the same 300 problems for both arms** (paired).

### Target recall, iterations, wall time

| M | arm | target recall | Wilson 99% | chance 1/M | median iters | ms/trial | cell wall |
|---|---|---|---|---|---|---|---|
| 12 | **A one** | 206/300 **68.7%** | [61.4, 75.1] | 8.3% | **2.0** | 7.12 | 2.13 s |
| 12 | **B halo** | 203/300 **67.7%** | [60.4, 74.2] | 8.3% | **5.0** | 13.05 | 3.92 s |
| 32 | **A one** | 114/300 **38.0%** | [31.1, 45.4] | 3.1% | **2.0** | 7.30 | 2.19 s |
| 32 | **B halo** | 116/300 **38.7%** | [31.7, 46.1] | 3.1% | **5.0** | 12.91 | 3.87 s |

**The two arms are a statistical tie on target recall at both loads, and the halo is ~1.8x slower
in wall time and 2.5x in iterations.** The 300-trial difference (203 vs 206; 116 vs 114) is noise
in both directions — the halo is nominally *better* at M = 32 and nominally *worse* at M = 12.

### Any-mark recall, convergence

| M | arm | any-mark recall | Wilson 99% | converged | cycled |
|---|---|---|---|---|---|
| 12 | A one | 300/300 **100%** | [97.8, 100.0] | 99.7% | 0.3% |
| 12 | B halo | 299/300 **99.7%** | [97.2, 100.0] | 100.0% | 0.0% |
| 32 | A one | 294/300 **98.0%** | [94.7, 99.3] | 100.0% | 0.0% |
| 32 | B halo | 297/300 **99.0%** | [96.1, 99.7] | 100.0% | 0.0% |

Both arms land on *a* real mark almost always. The whole difficulty is landing on the **cued** one.
That is the bus-relevant distinction, and it is unchanged by the halo.

### Where the error lives (report-only — feeds no decision)

The 13-ring is clamped in both arms, so it is right by construction and is omitted.

| M | quantity | count | rate | Wilson 99% |
|---|---|---|---|---|
| 12 | A · 7-ring | 222/300 | 74% | [67.0, 80.0] |
| 12 | A · 5-ring | 226/300 | 75% | [68.4, 81.1] |
| 12 | A · 3-ring | 242/300 | 80% | [74.2, 85.8] |
| 12 | B · stage 1 (7-ring) | 225/300 | 75% | [68.1, 80.9] |
| 12 | B · stage 2 (5+3 both) | 203/225 | 90% | [83.9, 94.2] |
| 12 | either arm correct | 245/300 | 82% | [75.2, 86.7] |
| 32 | A · 7-ring | 147/300 | 49% | [41.7, 56.4] |
| 32 | A · 5-ring | 156/300 | 52% | [44.6, 59.3] |
| 32 | A · 3-ring | 188/300 | 62% | [55.3, 69.5] |
| 32 | B · stage 1 (7-ring) | 152/300 | 51% | [43.3, 58.0] |
| 32 | B · stage 2 (5+3 both) | 116/152 | 76% | [66.5, 84.0] |
| 32 | either arm correct | 160/300 | 53% | [45.9, 60.6] |

*(B · stage 2 is measured on the trials where stage 1 settled the right 7-residue, so its
denominator is 225/152, not 300. This isolates the second stage.)*

**This is the finding.** Stage 1 of the halo is exactly as accurate as the one-resonator's own
7-ring (74% vs 74% at M = 12; 51% vs 49% at M = 32 — indistinguishable). And once stage 1 hits,
**stage 2 is very strong: 90% and 76%.** The halo chain's *last* stage is the best part of the
whole thing.

The problem is what the chain is built from. Stage 2 can only do its 90%/76% work on the ~50% of
trials where stage 1 already guessed the 7-residue right, and on the other half it is confidently
reading a wrong cue. Meanwhile the one-resonator, running all three free rings together, already
achieves the same end-to-end recall *without* the cascade — because iterating the rings together
already performs the mutual cleanup the cascade was meant to add. The halo does not add a step the
one-resonator was missing; it **replaces a joint iteration with a hard decision taken early**.

The paired discordance is the cleanest statement of it: at M = 32, **A-only 44, B-only 46** — the
arms are wrong on *almost disjoint* trials, and each arm's failures are the other's successes.
Running both would score 160/300 (53%) where either alone scores ~115/300 (38%). But the
pre-registered criterion did not offer "run both", and a selection rule that picks the right arm
after the fact has no online mechanism — that is a new question, recorded below, not a result here.

---

## The pre-registered decision

```
=== PRE-REGISTERED DECISION ===
decision cell (the one the criterion names): M = 32
  Arm A target recall 114/300 = 38.0%  wilson99 = [31.1%, 45.4%]  median iters 2.0
  Arm B target recall 116/300 = 38.7%  wilson99 = [31.7%, 46.1%]  median iters 5.0
  chance at M=32 = 3.1%   uniform 1/1365 = 0.07%
  clause 1  lo_B (31.7%) > point_A (38.0%)  ->  false
  clause 2  intervals overlap = True  AND  medIt_B (5.0) <= 0.5 x medIt_A (2.0 = 1.0)  ->  false
  criterion at M=32: KILL

reported for transparency: M = 12
  Arm A target recall 206/300 = 68.7%  wilson99 = [61.4%, 75.1%]  median iters 2.0
  Arm B target recall 203/300 = 67.7%  wilson99 = [60.4%, 74.2%]  median iters 5.0
  chance at M=12 = 8.3%   uniform 1/1365 = 0.07%
  clause 1  lo_B (60.4%) > point_A (68.7%)  ->  false
  clause 2  intervals overlap = True  AND  medIt_B (5.0) <= 0.5 x medIt_A (2.0 = 1.0)  ->  false
  criterion at M=12: KILL
```

**Clause 1 fails.** Arm B's lower bound (31.7%) sits 6.3 points *below* Arm A's point recall
(38.0%), not above it. Passing this clause would have required the halo to beat Arm A by more
than a full 99% confidence margin — it does not beat it at all.

**Clause 2 fails on its iteration half, decisively.** The intervals do overlap (both arms are a
tie), so the accuracy half of the clause is satisfied. But the clause requires the halo to
achieve that tie at **≤ 1.0 median iterations** (0.5 × 2.0). It used **5.0**. This is not a near
miss: the halo is structurally *incapable* of clause 2, because a stage cannot converge in one
sweep — `ring1_core` requires the argmax tuple to be stable for 2 consecutive iterations, so each
stage costs ≥ 2, and two stages cost ≥ 4. **Clause 2 as written is unreachable for any two-stage
design on this library.** That is a property of the criterion, discovered by reading it against
the measured iteration counts, and it is worth knowing before the next cascade-shaped test is
pre-registered.

### Verdict

```
VERDICT: KILL: the halo buys nothing. At M=32 Arm B's Wilson-99% lower bound (31.7%) does not
exceed Arm A's point recall (38.0%), and Arm B does not match Arm A at half the iterations
(medIt_B 5.0 vs medIt_A 2.0).
```

Same verdict at M = 12 under the alternative reading of the criterion. **No interpretation of the
pre-registered bar turns this run into a PASS.**

### Reproducibility

The full run was executed three times. All counts, rates and confidence intervals were identical
across all three; only wall-clock fields differed (13.1s, 23.9s, 23.9s — the spread is machine
load, not variance in the physics). One defect was found and fixed before any result was recorded:

- The KILL verdict string contained an unescaped literal `%` in `"Wilson-99% lower bound"`, which
  Python's `%`-formatting read as a `%lo` octal conversion and raised `TypeError` **after** the
  grid had already run — the crash was at the very last line. Fixed, then both verdict branches
  (clause 1 and clause 2, PASS and KILL) were force-executed through the real `decide()` to prove
  the formatter can no longer fail on either path. A KILL that dies before it can print is not a
  result.

---

## What this means for the bus

1. **Do not build the two-stage chain into the read path.** It costs 2.5x the iterations and
   ~1.8x the wall time for a statistical tie. The one-resonator over the free rings — the shape
   RING1-CORE already validated — stays. This is a Pillar decision with a number attached: the
   simple shape wins.

2. **Joint iteration is not a handicap; it is the cleanup.** The whole rationale for a halo
   cascade is that settling rings one at a time beats settling them together. Measured on these
   problems, it does not: the 3-ring is the *noisiest* one (49–62% alone at M = 32), and holding it
   at its mean in stage 1 removes exactly the information the joint sweep was using. **Committing
   early to a ring is the failure mode, not the fix.**

3. **The cued-vs-any gap is the real capacity limit, and the halo does not touch it.** Both arms
   recover *a* real mark 98–100% of the time but the cued mark only 38% of the time at M = 32.
   The bottleneck is that the 13-ring clamp is a **weak cue** on a crowded slot, not that the
   rings need a smarter schedule. RING1-CORE's overflow rule (`capacity_50 = 12` marks at c = 1)
   stands unchanged; this arm does not move it in either direction. Any future capacity work
   should push on the cue (more clamped bits, a check ring per RING1-CHECK), not on the
   iteration order.

4. **Stage 2's 90% / 76% conditional accuracy is a genuinely useful number, for a different
   design.** A *late* cascade — settle the coarse rings jointly first, then re-read the fine ones
   against the settled cue — is a different operator from what was tested, and the conditional
   accuracy here suggests it is worth one pre-registered trial. Not now: it is not this task.

5. **The A-only/B-only split (44/46) is the most interesting number in the report and it is not a
   pass.** Two readers, near-disjoint failure sets, 53% combined versus 38% either alone. A
   selection rule between them would need an *online* discriminator — a signal available before
   the answer. The eigengap (T5, RING1-CORE) is the obvious candidate, but T5 has not yet been
   read as a per-arm discriminator, and building that is a new brief with a new pre-registration.
   Logged below, not smuggled in here.

---

## Open issues

- **Clause 2 is structurally unreachable for cascades on this library** (each stage ≥ 2 iterations,
  so two stages ≥ 4, so the ratio can never be ≤ 0.5 against a 2-iteration single resonator).
  Worth fixing in the *next* cascade-shaped pre-registration before it wastes a run — either
  compare against a per-stage iteration cost, or let the ratio be < 1 rather than ≤ 0.5.
- **The 53% oracle is unclaimed.** Any method that picks between the two arms post hoc beats both.
  Needs an online selector. Not addressed here.
- **Only two loads were run**, as pre-registered. The arms are tied at M = 12 and M = 32; nothing
  here predicts where (or whether) the ordering would change. If a crossover exists it is beyond
  M = 32, where both arms are already near the floor.
- **The 3-ring is the weakest link** (49–62% alone at M = 32) and is the ring the halo freezes
  first. A cascade variant that clamps the *finest* ring last is untested; the scope here froze it
  first because the brief said so, and the brief is the contract.
- **k16 was not run**, as the scope fixed float. Whether quantisation changes the tie is unknown;
  RING1-CORE's T1 grid shows k16 is within noise of float at c=1, so it is unlikely to matter.
- **`resonate_free()` is now a second implementation of the resonator loop.** It is proven
  equivalent to the library by Integrity 1, but the *library* is the one RING1-SMOOTH,
  RING1-CHECK and RING1-DIRECT import. If any later arm needs a free-ring subset, this
  generalisation is the place to lift into `ring1_core` — a CLOSE decision for J, not a
  refactor to slip in under a research brief.

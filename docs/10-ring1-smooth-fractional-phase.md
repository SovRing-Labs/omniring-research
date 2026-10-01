# RING-1 T2: a smooth (fractional-phase) ring for "around when"

| | |
|---|---|
| **Date** | 2026-09-28 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). Every number was measured on a 2019 laptop CPU (Intel i5-8365U, AVX2, no GPU); the author reviews each document before publication. |
| **Type** | measured result |
| **Verdict** | KILL (pre-registered) on discovery; the cue form works. See the correction below. |
| **Code** | `harness/ring1/run_smooth.py` (see `harness/README.md`) |


> **Correction (added at publication).** This report's KILL is about *discovering* a smooth
> (fractional-phase) factor, not about smooth rings being useless. The two are different claims, and
> the seat addendum already separates them. Read the verdict as: **a soft resonator cannot infer a
> smooth factor from a mark; a smooth ring works as a cue you supply** (recall 92% / 82% / 67% at cue
> offsets 0 / 1 / 2 ticks, falling to 0% at d = 4, the first zero of the sinc). The engine later
> showed the crowding, not the dial resolution, was the original failure
> (`06-ring3-peel-diamond-correl-tabu-fret.md`), so the "dial resolution" reading of this KILL is
> superseded; the "cannot discover" reading stands.

KILL: recall criterion failed


**Pillar** Nervous System — the Loop's **Read** step
**Verdict** `KILL: recall criterion failed`

---

## Pre-registration (verbatim from the brief)

> PASS if mean similarity at d = 1 exceeds mean similarity at d >= 16 by more
> than 5 standard errors of the d >= 16 values, AND exact-ring target recall
> with the smooth ring bound in stays within the Wilson-99% interval of the run
> without it. Otherwise KILL.

---

## Setup

Configuration: `D = 5120`, `mods = (3, 5, 7, 13)` → **1365 states**
Smooth ring length scale: `L = 8` ticks
Trials per cell: `300` (full mode)
Base seed: `20260928`

## Results — (a) Neighbour Curve

| d | mean similarity | std |
|---|---|---|
| 0 | 1.000000 | 0.000000 |
| 2 | 0.642518 | 0.000000 |
| 4 | 0.007609 | 0.000000 |
| 6 | -0.222299 | 0.000000 |
| 8 | -0.026785 | 0.000000 |
| 10 | 0.108517 | 0.000000 |
| 12 | -0.001127 | 0.000000 |
| 14 | -0.091493 | 0.000000 |
| 16 | -0.008753 | 0.000000 |
| 18 | 0.069873 | 0.000000 |
| 20 | 0.016248 | 0.000000 |
| 22 | -0.042647 | 0.000000 |
| 24 | -0.002785 | 0.000000 |
| 26 | 0.038158 | 0.000000 |
| 28 | -0.002188 | 0.000000 |
| 30 | -0.038153 | 0.000000 |
| 32 | 0.002941 | 0.000000 |

**Neighbour criterion**: mean(d=1) = 0.902134, mean(d≥16) = 0.004485
Difference = 0.897649, 5×SE = 0.042091
**Result**: PASS (diff > 5×SE)

## Results — (b) Recall With/Without Smooth Ring (M=12, c=1, float)

| Configuration | Target Recall | Wilson 99% CI | Chance 1/M |
|---|---|---|---|
| Without smooth ring | 198/300 (66.0%) | [58.7%, 72.6%] | 8.3% |
| With smooth ring bound | 2/300 (0.7%) | [0.1%, 3.3%] | 8.3% |

**Recall criterion**: with-smooth point estimate within without-smooth Wilson-99% CI
Without-smooth CI: [0.5868, 0.7263]
With-smooth point: 0.0067
**Result**: FAIL

## Results — (c) Smooth Ring Clamped vs 13-Ring Clamped (M=12)

| Configuration | Target Recall | Wilson 99% CI |
|---|---|---|
| 13-ring clamped (no smooth) | 198/300 (66.0%) | [58.7%, 72.6%] |
| Smooth-ring clamped (no exact clamp) | 196/300 (65.3%) | [58.0%, 72.0%] |

## What this means for the bus

The smooth ring shows genuine neighbour similarity: nearby ticks are significantly
more similar than distant ones, confirming the fractional-phase encoding works as
intended for 'around when' closeness.

Adding the smooth ring degrades exact-ring recall beyond statistical noise.
The 'when' signal interferes with the 'what' signal — they cannot share a slot.

Smooth-ring clamp recall: 65.3% [58.0%, 72.0%]
This measures whether the smooth ring alone can serve as a query cue.

## Open issues

1. The smooth ring clamp (c) uses a different mechanism (unbinding the smooth
   component from the slot vector) than the exact ring clamp (pinning in the
   resonator). A unified clamp interface would be cleaner.
2. Length scale L=8 was chosen from the brief; other values (L=4, L=16) untested.
3. The neighbour curve used 1,000 samples; more samples would tighten the SE.
4. Interaction with k16 quantisation untested.
5. Real marks may have temporal structure that affects the neighbour statistics.

---

## Files

| Path | What |
|---|---|
| `harness/ring1/run_smooth.py` | This runner |
| `docs/appendix/RING1-SMOOTH.md` | This report |

## Verification

```
$ cd the project root && python3 harness/ring1/run_smooth.py --quick
```

---
## Seat addendum (claude-seat, 2026-09-29): what the KILL actually means
**Harness fixes before this run:** (1) the first run bound the smooth ring into every mark but resonated only the exact rings. That buries them under an unknown factor, so its 0/30 was guaranteed by construction. Now the smooth ring is a real resonator factor (codebook over ticks 0..1364), and the KILL still stands, this time for a real reason. (2) `--quick` is a non-decisive smoke run (it no longer overwrites this report). Backup: `run_smooth.py.pre-factor`.
**The real finding:** the soft resonator cannot *discover* a smooth factor. Its 1,365 ticks are highly correlated (a sinc kernel of width L), so the soft estimate blurs. Probe, same library: a single clean mark decodes only 4/30 with the smooth factor free (11/30 with the 13-ring held). At M = 12 it is 2/300 in the full run above.
**But a smooth ring works as a cue ("around when"):** unbind a query time from the slot, then resonate the exact rings (M = 12, 60 trials each):
| cue offset from the mark's true tick | 0 | 1 | 2 | 4 | 8 |
|---|---|---|---|---|---|
| target recall (chance 8%) | 92% | 82% | 67% | 0% | 0% |
Recall falls to zero at d = L/2 = 4, the first zero of the sinc, so L sets the "around" window.
**Design rule for the bus:** time is a *cue you supply*, not an answer you extract. To *read* a mark's time, carry an exact counter ring (13) alongside. Use the smooth ring only for "what happened around t?" queries, with L chosen to the window you want (probe: `harness/ring1/run_smooth.py` + the snippet in this session's lineage).

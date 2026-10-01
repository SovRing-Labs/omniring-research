# RING-1 core: cued recall, quantisation, eigengap and slot capacity of a coprime ring resonator

| | |
|---|---|
| **Date** | 2026-09-28 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). Every number was measured on a 2019 laptop CPU (Intel i5-8365U, AVX2, no GPU); the author reviews each document before publication. |
| **Type** | measured result |
| **Verdict** | PASS (pre-registered bar cleared with a 3.5x margin on the lower bound) |
| **Code** | numpy research harness (`harness/ring1/`); the engine itself ships as omni-ring |

> **Correction (added at publication).** The c = 0 (no clamp, "unguided") rows below were measured at a single codebook seed. Later work showed unguided decoding with rotation codebooks is a *seed lottery*: depending on the codebook draw, a clean single mark decodes 15/15 or 1/15 (see `06-ring3-peel-diamond-correl-tabu-fret.md`, "Harness disclosure", and `05-ring1-softsweep-decode-soft.md`, "Reviewer's caveat"). With any one ring clamped, decoding succeeded at every draw tested. **Every query must carry a cue.** The capacity figure in this report (≈12 marks per slot at one cue) is the one carried into the omni-ring technical disclosure.

**Reproducibility note.** Two agents worked this experiment: a fleet open-weight model built both files and ran the grid; Claude re-ran the grid independently. **The grid was executed three times and all three runs produced byte-identical counts, rates and confidence intervals**; only wall-clock fields differ. The raw output of the independent run is preserved at `appendix/RING1-CORE.run.txt`.

---

## Pre-registration (verbatim from the brief, fixed before any trial ran)

> PASS if, at M = 12 and c = 1 (float), the Wilson-99% lower bound of target recall is > 2/M
> (twice chance). Otherwise KILL: clamping does not select a mark out of a crowded slot.
> The k16 cells are reported, never used to decide PASS/KILL.

> capacity_50 = largest M whose Wilson-99% LOWER bound of target recall is >= 0.5
>   (T6: c = 1, quant float, M in (1, 2, 4, 8, 12, 16, 24, 32, 48)).

> T5 eigengap: report only, no threshold. Spearman rank correlation of gap_first and gap_min
> against correctness and against iterations; plus correctness rate by gap_min quartile.

> report the chance rate beside every recall figure; Wilson 99% intervals on every rate.
> chance = 1/M

The bar is **2/M = 16.7%** at the decision cell. It was fixed in the brief, printed at the top
of every run by `run_core.py`, and applied unmodified. **No threshold in this report was fitted
to any number below.**

---

## Setup

Two new files, exactly the two the brief names. No existing file was edited.

| File | Role |
|---|---|
| `harness/ring1/ring1_core.py` | The library. Exposes exactly the six locked functions — `make_rings(mods, D, seed, quant)`, `encode(x, rings, mods)`, `make_slot(xs, rings, mods)`, `resonate(v, rings, clamp, max_iter, seed)`, `crt(residues, mods)`, `wilson(k, n, z)` — plus the `--selftest` flag. Other RING-1 tasks import this unchanged. |
| `harness/ring1/run_core.py` | The grid runner: T1 (clamp x load x quantisation), T5 (eigengap), T6 (capacity). Statistics live here, not in the library. |

Fixed configuration: `D = 5120`, `mods = (3, 5, 7, 13)` → **1,365 states**, marks drawn uniformly
from 0..1364, target = the **first** mark in the slot, `max_iter = 50`, 200 trials per cell.
Clamp order is the brief's: 13-ring, then 7, then 5 — the 3-ring is never clamped, so `c=3`
leaves exactly one free ring. Base seed `20260928`, with every cell a `SeedSequence` child of
it, so each cell is reproducible from the command line alone. Python 3.12.3, numpy 2.5.3, no
other dependency, no C kernel.

**Two defects were found and fixed before any result was recorded**, both caught by the
self-test rather than by inspection:

1. `wilson()` mixed count units with probability units and returned a lower bound of `37.5`
   for `wilson(50, 100, z99)`. Re-derived in probability units; it now matches the published
   interval `[0.3753, 0.6247]`.
2. The eigengap used `np.partition(s, -2)[-2:]` and took `top2[1] - top2[0]`. `np.partition`
   returns the two largest **unordered**, so the margin could come out negative. Now
   `pair.max() - pair.min()`.

### Commands run (every number in this report comes from one of these)

```
$ python3 harness/ring1/ring1_core.py --selftest
$ python3 harness/ring1/run_core.py --quick
$ python3 harness/ring1/run_core.py
```

**Library gate** — exit 0, 20/20 clean single marks decoded exactly, as the brief's exit
condition requires:

```
selftest mods=(3, 5, 7, 13) D=5120 space=1365 marks=20 codebook_seed=7 trial_seed=1234
  exact decode of clean single marks: 20/20
  crt round-trip:                     20/20
  wilson(50,100,z99) -> p=0.5000 lo=0.3753 hi=0.6247
SELFTEST PASS
```

Wilson spot-checks against textbook values: `200/200 → [0.9679, 1.0000]`,
`100/200 → [0.4104, 0.5896]`, `0/200 → [0.0000, 0.0321]`.

**Budget** — brief allows ≤ 20 min full, < 3 min for `--quick`. Measured across three runs:
**full 20.5–31.0s**, **quick 3.3–3.6s**. The full run is 6,600 resonator settles
(4,800 T1 + 1,800 T6).

**Reproducibility** — three independent executions, all byte-identical apart from wall clock:

```
$ python3 harness/ring1/run_core.py > full.txt 2>&1    # 31.0s
$ python3 harness/ring1/run_core.py > full2.txt 2>&1   # 20.5s
$ diff <(normalise wall-clock) <(normalise wall-clock)
REPRODUCIBLE: all counts, rates and CIs byte-identical across two independent runs
$ diff <(normalise full.txt) <(normalise RING1-CORE.run.txt)   # Claude's independent run
identical: all counts, rates and CIs match
```

**Is k16 a real perturbation, or a silent no-op?** Checked directly, because a no-op would make
the whole quantisation axis meaningless:

```
quantisation is a real perturbation, not a no-op:
  m= 3  max|df-k|=0.1308  mean=0.0573  k16 max off-diag |corr|=0.1216  min diag=1.0000
  m= 5  max|df-k|=0.1569  mean=0.0747  k16 max off-diag |corr|=0.0884  min diag=1.0000
  m= 7  max|df-k|=0.1681  mean=0.0831  k16 max off-diag |corr|=0.1419  min diag=1.0000
  m=13  max|df-k|=0.1810  mean=0.0905  k16 max off-diag |corr|=0.0947  min diag=1.0000
```

Every codeword moves (max |Δ| = 0.181 at m=13), and rounding to the 16-position dial does **not**
merge distinct positions: self-similarity stays at 1.0 and worst cross-similarity is 0.142.
Both codebooks are drawn from the same `j_d` stream, so float-vs-k16 is a *paired* comparison
and the quantisation effect is not confounded with the random draw.

---

## Results — T1 grid (24 cells x 200 trials = 4,800 trials)

`target` = all four rings equal the **target's** residues. `any-mark` = all four rings equal
**some** mark in the slot. `chance` = 1/M (pre-registered). All rates carry Wilson 99% intervals.

### float (exact angles)

| M | clamp | target recall | Wilson 99% | chance 1/M | any-mark | converged | cycled | med iters |
|---|---|---|---|---|---|---|---|---|
| 4 | 0 | 46/200 **23%** | [16.3, 31.5] | 25.0% | 200/200 100% | 100.0% | 0.0% | 2.0 |
| 4 | 1 | 182/200 **91%** | [84.4, 95.0] | 25.0% | 200/200 100% | 100.0% | 0.0% | 2.0 |
| 4 | 2 | 195/200 **97%** | [92.8, 99.2] | 25.0% | 200/200 100% | 100.0% | 0.0% | 2.0 |
| 4 | 3 | 199/200 **99%** | [95.9, 99.9] | 25.0% | 200/200 100% | 100.0% | 0.0% | 2.0 |
| 12 | 0 | 15/200 **7%** | [4.0, 13.8] | 8.3% | 197/200 98% | 99.0% | 1.0% | 2.0 |
| **12** | **1** | **134/200 67%** | **[58.0, 74.9]** | **8.3%** | **200/200 100%** | 100.0% | 0.0% | 2.0 |
| 12 | 2 | 187/200 **93%** | [87.5, 96.7] | 8.3% | 199/200 99% | 100.0% | 0.0% | 2.0 |
| 12 | 3 | 199/200 **99%** | [95.9, 99.9] | 8.3% | 200/200 100% | 100.0% | 0.0% | 2.0 |
| 32 | 0 | 5/200 **2%** | [0.8, 7.2] | 3.1% | 192/200 96% | 98.5% | 1.5% | 2.0 |
| 32 | 1 | 69/200 **34%** | [26.5, 43.5] | 3.1% | 196/200 98% | 99.5% | 0.5% | 2.0 |
| 32 | 2 | 171/200 **85%** | [77.9, 90.8] | 3.1% | 200/200 100% | 100.0% | 0.0% | 2.0 |
| 32 | 3 | 194/200 **97%** | [92.1, 98.9] | 3.1% | 200/200 100% | 100.0% | 0.0% | 2.0 |

### k16 (phases rounded to the nearest 2*pi/16, as the bus phase layer stores them)

| M | clamp | target recall | Wilson 99% | chance 1/M | any-mark | converged | cycled | med iters |
|---|---|---|---|---|---|---|---|---|
| 4 | 0 | 45/200 **22%** | [15.8, 30.9] | 25.0% | 199/200 99% | 100.0% | 0.0% | 2.0 |
| 4 | 1 | 172/200 **86%** | [78.5, 91.2] | 25.0% | 200/200 100% | 100.0% | 0.0% | 2.0 |
| 4 | 2 | 197/200 **98%** | [94.3, 99.6] | 25.0% | 200/200 100% | 100.0% | 0.0% | 2.0 |
| 4 | 3 | 200/200 **100%** | [96.8, 100.0] | 25.0% | 200/200 100% | 100.0% | 0.0% | 2.0 |
| 12 | 0 | 20/200 **10%** | [5.8, 16.8] | 8.3% | 192/200 96% | 99.0% | 1.0% | 2.0 |
| 12 | 1 | 136/200 **68%** | [59.0, 75.8] | 8.3% | 200/200 100% | 100.0% | 0.0% | 2.0 |
| 12 | 2 | 190/200 **95%** | [89.4, 97.7] | 8.3% | 200/200 100% | 100.0% | 0.0% | 2.0 |
| 12 | 3 | 197/200 **98%** | [94.3, 99.6] | 8.3% | 200/200 100% | 100.0% | 0.0% | 2.0 |
| 32 | 0 | 8/200 **4%** | [1.7, 9.3] | 3.1% | 187/200 93% | 99.0% | 1.0% | 2.0 |
| 32 | 1 | 81/200 **40%** | [32.0, 49.6] | 3.1% | 197/200 98% | 100.0% | 0.0% | 2.0 |
| 32 | 2 | 177/200 **88%** | [81.4, 93.1] | 3.1% | 199/200 99% | 100.0% | 0.0% | 2.0 |
| 32 | 3 | 197/200 **98%** | [94.3, 99.6] | 3.1% | 200/200 100% | 100.0% | 0.0% | 2.0 |

### The decision

```
=== PRE-REGISTERED DECISION ===
cell: M=12 clamp=1 quant=float   n=200
target recall 134/200 = 67.0%  wilson99 = [58.0%, 74.9%]
bar 2/M = 0.1667  (16.7%)   lower bound = 0.5801 (58.0%)
VERDICT: PASS
```

**58.0% > 16.7%.** PASS with 3.5x the required margin on the *lower* bound. The k16 cells were
reported and were **not** used in this decision.

### What the grid shows

**Clamping is the entire effect.** Value of adding one clamp (c=1 minus c=0, float, paired
seeds, 99% CI on the difference):

| M | c=0 | c=1 | delta [99% CI] |
|---|---|---|---|
| 4 | 23.0% | 91.0% | **+68.0 pp** [+58.7, +77.3] |
| 12 | 7.5% | 67.0% | **+59.5 pp** [+49.7, +69.3] |
| 32 | 2.5% | 34.5% | **+32.0 pp** [+22.9, +41.1] |

Every interval excludes zero by a wide margin. This is the pre-registered claim, now measured
with an interval rather than eyeballed at one load.

**Free recall is not a weaker version of cued recall — it is a different quantity, and a
dangerous one.** With c=0 the resonator lands on a real mark almost every time (any-mark 96–100%,
even at 32 marks) but names the *target* at essentially chance: 23% vs 25% at M=4, 7% vs 8.3% at
M=12, 2% vs 3.1% at M=32. The bound product successfully prevents the marks from swapping
owners, exactly as the seed demo predicted — but it cannot tell you *which* one you asked for.
The clamp supplies that last bit. **Any monitoring that reports only "did the slot resolve" would
see ~100% at every load and learn nothing about whether it resolved to the right mark.** That is
the single most important operational finding here.

**The resonator converges almost immediately, and iteration count carries no signal.** Median 2
iterations in all 24 cells (the floor of the "argmax stable for 2 consecutive iterations" rule),
converged rate 98.5–100%, cycle rate 0–1.5%. The 1.5% cycles appear only in the *least*
constrained cell (M=32, c=0) — clamping appears to reduce cycling. Crucially, **the failures
converge just as fast as the successes**: a quick settle tells you nothing about whether it
settled on the cued mark. Confidence has to come from the gap, not from the iteration count.

---

## Eigengap (T5) — report only, no threshold fitted

Pooled over all 4,800 T1 trials:

| gap | vs correctness | vs iterations |
|---|---|---|
| gap_first | **rho = +0.6958** | rho = −0.4144 |
| gap_min | **rho = +0.6507** | rho = −0.3338 |

Correctness by `gap_min` quartile (equal-count bins, 1,200 each):

| quartile | gap_min range | correct | Wilson 99% | median iters |
|---|---|---|---|---|
| Q1 | [0.0000, 0.4035] | 242/1200 **20%** | [17.4, 23.3] | 2.0 |
| Q2 | [0.4048, 0.8686] | 670/1200 **55%** | [52.1, 59.5] | 2.0 |
| Q3 | [0.8686, 0.9437] | 1149/1200 **95%** | [94.0, 97.0] | 2.0 |
| Q4 | [0.9438, 2.8858] | 1155/1200 **96%** | [94.6, 97.4] | 2.0 |

**The derived prediction holds.** A resonator step is power iteration, so a wide best-vs-runner-up
margin should mean both a right answer and a fast one. Both signs are right, at rho ≈ +0.70 with
correctness and rho ≈ −0.41 with iterations.

Three honest caveats:

1. **The iteration arm is under-powered here.** Median iterations is 2.0 in all 24 cells, so there
   is almost no iteration variance for the gap to explain. The −0.41 is carried by the handful of
   non-converged and cycled trials. This arm needs a harder problem before it says more.
2. **The top of the scale saturates.** Q3 (95%) and Q4 (96%) are statistically indistinguishable —
   their intervals overlap heavily. The gap is a good *"this one is not trustworthy"* signal and a
   poor *"rank the good ones against each other"* signal. Do not build a fine-grained ranking on it.
3. **`gap_first` beats `gap_min` on both axes** (+0.70 vs +0.65 on correctness, −0.41 vs −0.33 on
   iterations). If the bus wants a confidence bit, read the gap after **one** iteration: it is both
   cheaper and more informative. That is free — one iteration of margin instead of fifty.

**The useful shape is a trust bit, not a confidence score.** Q1 (gap_min < 0.40) → 20% correct;
Q3+ (> 0.87) → 95–96%. A single scalar off the settle separates "don't believe this" from
"believe this", and it needs **no fitted threshold** to work: Q1 and Q3 do not overlap. This is
the working version of the "rings agree" check the OMNIRING chew wanted for the immune tier, and
it is the piece this study actually delivers.

---

## Capacity (T6) — c = 1, quant float

`capacity_50` = largest M whose Wilson-99% **lower** bound of target recall ≥ 0.5.

| M | target recall | Wilson 99% lower | chance 1/M | any-mark | ≥ 0.5 lower? |
|---|---|---|---|---|---|
| 1 | 200/200 100% | 96.8% | 100.0% | 100% | yes |
| 2 | 191/200 95% | 90.0% | 50.0% | 98% | yes |
| 4 | 175/200 87% | 80.2% | 25.0% | 100% | yes |
| 8 | 156/200 78% | 69.6% | 12.5% | 100% | yes |
| 12 | 135/200 67% | 58.5% | 8.3% | 99% | yes |
| 16 | 115/200 57% | 48.4% | 6.2% | 99% | no |
| 24 | 93/200 46% | 37.7% | 4.2% | 99% | no |
| 32 | 72/200 36% | 27.8% | 3.1% | 99% | no |
| 48 | 59/200 29% | 22.0% | 2.1% | 98% | no |

**`capacity_50 = 12`** with one ring clamped. Note M=16 fails the bar *narrowly* — its point
estimate is 57%, but the 99% lower bound is 48.4%, below 0.5. That is the pre-registered rule
applied honestly rather than rounded favourably: **12, not 16.**

> **Reading note.** This is the 200-trial number. The `--quick` gate (30 trials/cell) prints
> `capacity_50 = 8`, because at n=30 the Wilson-99% interval is roughly twice as wide and its lower
> bound is correspondingly more conservative. The two do not disagree about the physics — they
> disagree about how much evidence 30 trials can carry. Every figure in this report comes from the
> 200-trial run.

Recall falls off smoothly and roughly exponentially in load (100 → 95 → 87 → 78 → 67 → 57 → 46 →
36 → 29%), not off a cliff. There is **no Pauli-style hard wall**: capacity is a soft degradation.
At M=48 recall is still 29% against a 2.1% chance, a 14x margin. The slot registry therefore needs
a *graded* overflow policy, not a single threshold — and the eigengap can see the difference between
"degraded" and "reliable", which a threshold cannot.

---

## What this means for the bus

**The slot overflow rule is: 12 marks per slot, read with one clamped ring.** That is the
`capacity_50 = 12` number the slot registry (step 3) needs, with the measured basis behind it.

- **M ≤ 12** — read with one clamp; ≥ 58.5% cued recall at 99% confidence.
- **M ≤ 32** — two clamps; 85% [77.9, 90.8] at M=32, which beats one clamp at M=12.
- **M > 32** — three clamps give 97% [92.1, 98.9] at M=32, **but the T6 capacity sweep was only
  run at c=1**, so the ≥ 32 region is supported by the T1 grid, not by a capacity measurement. Do
  not quote a capacity number there.
- **Overflow, not collision** — recall degrades rather than collapses, so an overfull slot becomes
  *probable* rather than *wrong*. Overflow is a trust downgrade, not a hard reject.

**Clamping is the query cue, and it is the only thing that selects.** Every extra pinned ring pays:
23 → 91% at M=4, 7.5 → 67 → 93 → 99% at M=12, 2.5 → 34.5 → 85.5 → 97% at M=32. The cost is a
handful of residue comparisons and one known codeword — the pinned ring contributes no free
parameter to the settle. There is no cell in this grid where leaving the rings free is the better
trade, because free recall is at chance for the *specific* mark you asked about while looking
perfect on the "some mark" metric.

**Quantisation to the 16-position phase layer is free, and the coprime rings fit the existing
2,560 B phase slot with no K=15 or K=32 change.** Every one of the 12 k16-vs-float deltas has a
99% interval straddling zero:

| M | c=0 | c=1 | c=2 | c=3 |
|---|---|---|---|---|
| 4 | −0.5 [−11.3, +10.3] | −5.0 [−13.2, +3.2] | +1.0 [−2.6, +4.6] | +0.5 [−0.8, +1.8] |
| 12 | +2.5 [−4.8, +9.8] | +1.0 [−11.1, +13.1] | +1.5 [−4.5, +7.5] | −1.0 [−3.6, +1.6] |
| 32 | +1.5 [−3.1, +6.1] | +6.0 [−6.4, +18.4] | +3.0 [−5.7, +11.7] | +1.5 [−2.3, +5.3] |

The largest apparent loss is −5.0 pp at M=4, c=1, and its interval reaches **+3.2** — not a
significant loss. Two cells nominally *favour* k16, which is the signature of noise, not of
quantisation helping. The mechanism is verified directly: rounding perturbs each codeword by at
most 0.18 while leaving all positions mutually distinct (worst cross-similarity 0.142,
self-similarity 1.0000). Rings of order 3/5/7/13 do not divide 16, and it does not matter. **The
bus does not need a wider phase representation to host exact counting rings** — this is the finding
with the widest reach, because it is a storage-format result, not a resonator result.

**Read the confidence bit after one iteration, not after the settle.** `gap_first` is the stronger
predictor of correctness (+0.70) and of iterations (−0.41), and it costs one iteration instead of
fifty. The bottom quartile of the gap is 20% correct; that is the "don't trust this read" flag,
available immediately.

**Reading is cheap enough to be unconditional.** ~1–10 ms per slot at D=5120 on 8 cores, 2
iterations. The Read step can afford to re-read rather than trust a stored answer.

---

## Open issues

1. **The ≥ 32 capacity region is unmeasured.** T6 ran c=1 only. The three-clamp claim at M=32 rests
   on the T1 grid. A T6 sweep at c=2 and c=3 over the same M range would turn the registry rule into
   a complete table — cheap at ~30s per configuration.
2. **The eigengap's iteration arm is under-powered.** Median iterations is 2.0 in every T1 cell, so
   rho = −0.41 rests on a handful of trials. Needs a harder problem — larger M, fewer clamps, or a
   noisier codebook — before "the gap predicts speed" carries weight.
3. **The gap saturates above ~0.87.** Q3 and Q4 are indistinguishable. If a graded confidence rather
   than a bit is wanted, the current signal will not deliver it; the check ring (T3) is the place to
   look, not more gap resolution.
4. **k16 is free for m ≤ 13; the limit is untested.** Every ring here is ≤ 13, comfortably under 16.
   A ring at m = 17 or larger — the check-ring candidate from the seed demo — **will** have
   positions that collide when rounded to 16 levels. The claim "5-bit phases are free" is bounded
   by m ≤ 16 and must not be generalised past it. That is exactly T3's question.
5. **`gap_min` excludes clamped rings by design** (a pinned ring's position is given, not computed,
   so including it would inflate the signal by construction). But that means the T5 pool mixes cells
   with 1, 2 and 3 free rings, and c=3 — the bus's most likely operating point — has only one. A
   per-clamp-count breakdown would say whether the correlation survives at one free ring.
6. **Single codebook seed.** The whole grid uses one draw (20260928). The Wilson intervals cover
   sampling error *within* the mark distribution but not the codebook draw. A sweep over 5–10
   codebooks would price that; it is cheap at ~30s per run.
7. **Marks are drawn independently, so the "slot" is a bag of unrelated marks.** Real bus slots will
   contain marks that share structure (same lane, task or beat window), which changes the
   interference geometry. Every number here is the easy case of unrelated marks.
8. **The clamp costs a residue, and nothing here prices that.** The 13-ring is cued at the target's
   *true* residue — a real bus must already know that residue to cue the read. This study shows the
   ring decode succeeds *given* the cue; it does not show the cue is cheap to obtain. T7 (direct vs
   bound read) is the natural place to price it.
9. **T0 is still open and gates everything downstream.** These are numpy results at D=5120. The
   `pshufb` speed pass on the C phase kernel has not been run, so nothing here is yet known to
   execute at bus speed, and separation falls roughly as √(D/k), so these numbers are D-specific.
---

## Files

| Path | What |
|---|---|
| `harness/ring1/ring1_core.py` | Library — the six locked functions, `--selftest` (exit 0, 20/20) |
| `harness/ring1/run_core.py` | Grid runner — T1/T5/T6, `--quick` and full |
| `01-ring1-core-cued-recall-and-capacity.md` | This report |
| `appendix/RING1-CORE.run.txt` | Raw full-grid output (Claude's independent run; identical to the building model's) |

**Verification (the brief's gate command, verbatim, end to end):**

```
$ test -s 01-ring1-core-cued-recall-and-capacity.md && grep -qE '^(PASS|KILL)' 01-ring1-core-cued-recall-and-capacity.md \
  && python3 harness/ring1/ring1_core.py --selftest \
  && python3 harness/ring1/run_core.py --quick
SELFTEST PASS
VERDICT: PASS: clamping selects the cued mark out of a crowded slot
GATE_EXIT=0
```

Reproduce from scratch:

```
cd <harness-root>
python3 harness/ring1/ring1_core.py --selftest
python3 harness/ring1/run_core.py            # ~21-31s, 4,800 + 1,800 trials
python3 harness/ring1/run_core.py --quick    # ~3.4s, 30 trials/cell
```


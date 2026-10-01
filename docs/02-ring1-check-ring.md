# RING-1 T3: the 17 check ring flags wrong resonator settles

| | |
|---|---|
| **Date** | 2026-09-28 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). Every number was measured on a 2019 laptop CPU (Intel i5-8365U, AVX2, no GPU); the author reviews each document before publication. |
| **Type** | measured result |
| **Verdict** | PASS (on the load-bearing cell M = 12, c = 1) |
| **Code** | numpy research harness (`harness/ring1/`); the check ring ships in omni-ring |

> **Note (added at publication).** The c = 0 (unguided) cells here collapsed at the pre-registered codebook seed. That is the same *seed lottery* later documented for unguided decoding (`06-ring3-peel-diamond-correl-tabu-fret.md`, "Harness disclosure"): it is a property of unguided factorisation, not of the check ring. The load-bearing evidence is the cued cell (M = 12, c = 1), as the report itself says. The 81.8% / 0 false-alarm result is the figure carried into the omni-ring technical disclosure (section 12: "flags 82%, 0 false alarms").

Library: `harness/ring1/ring1_core.py` (RING1-CORE, `PASS`), imported unchanged.
Runner: `harness/ring1/run_check.py` · Full log: `appendix/RING1-CHECK.run.txt`

**One-line result:** the 17 check ring works. On the crowded clamped path (M = 12, c = 1) it
flags **81.8% [63.1, 92.2]** of wrong settles and false-alarms on **0/256** correct settles —
both pre-registered thresholds cleared on that cell *alone*, with the degenerate cells excluded.
It is not free, and it is not a proof: it costs **−10.7 pp of recall at M = 12 (p = 0.004)** and
**18.2% of wrong settles slip through as in-range phantoms**.

**Read the c = 0 rows as an artefact, not as check power.** At the pre-registered codebook
seed the un-clamped 5-ring settle *collapses* — 0% converged, 100% of trials burn the 50-iteration
ceiling, and the decoded mark is a tie-break coin flip. Those cells contribute 900 of the 944
pooled wrong settles, so the pooled 99.2% is not the load-bearing evidence. The load-bearing
evidence is M = 12, c = 1, quoted in the first paragraph. Both readings of the criterion give PASS.

---

## Pre-registration (verbatim, fixed before any trial ran)

From the experiment brief, steps 2, 4 and 6:

> **PRE-REGISTERED DECISION (step 6):**
> PASS if, pooled over cells with >= 30 wrong settles, the flag rate on wrong settles has a
> Wilson-99% lower bound >= 0.5 AND the false-alarm rate on correct settles has a Wilson-99%
> upper bound <= 0.05. Otherwise KILL.
>
> **PRE-REGISTERED SCOPE (step 2):**
> Marks carry mods (3,5,7,13,17) but only 0..1364 are legal values (17 is redundant). Resonate
> with all 5 rings; call a settle 'legal' when crt of the 4 information residues, taken mod 17,
> equals the decoded 17-residue. Cells: M in (1, 4, 12), c in (0, 1), float, 300 trials. Report:
> rate of wrong settles (not any real mark), flag rate on wrong settles (illegal), false-alarm
> rate on correct settles (flagged illegal), and recall with vs without the 17 ring bound in
> (cost of the extra ring).
>
> **REPORTING RULES (step 4):**
> fixed seeds; no fitted thresholds; every number from a command that was run; report the chance
> rate beside every recall figure; Wilson 99% intervals on every rate.

No threshold below was fitted. The one interpretive decision I had to make — an *unmeasured*
rate is not a *violated* rate — is stated where it is used, and both readings are reported.

---

## Setup

| | |
|---|---|
| Information space | 3·5·7·13 = **1,365** legal values, 0..1364 |
| Full 5-ring space | 3·5·7·13·17 = **23,205** |
| 1365 mod 17 | **5** → 17 does not divide 1,365, so 17 carries no information; it is a checksum |
| D / quant / max_iter | 5,120 / float / 50 (inherited from RING1-CORE) |
| Clamp order | 13, 7, 5 → ring indices (3, 2, 1). The 3-ring (0) and the **17-ring (4) are never clamped** |
| Base seed | 20260928 (the RING1-CORE codebook seed, so the arms stay comparable) |
| Codebook seeds | 20260928 (pre-registered) + 1 and 2 (robustness scan) |
| Chance baselines | target recall 1/M; a random residue tuple is illegal 16/17 |
| Cells | M ∈ {1, 4, 12} × c ∈ {0, 1}, 300 trials/cell, both arms = 3,600 settles per codebook |

**The 17-ring is never clamped, and that is the whole design.** Clamping the 13-ring is the query
cue (RING1-CORE's convention, kept so the recall comparison is apples-to-apples). Clamping the
17-ring instead would pin the checksum to the answer and make the check vacuous.

**Both arms share bit-identical codebooks.** `make_rings` draws its per-dimension multiples from
one rng in ring order, so the 3/5/7/13 codebooks are the same arrays in the 5-ring and 4-ring
systems. The cost comparison is therefore paired on identical marks, clamp and codebooks:

```
  codebook seed 1: 6 cells x 300 trials x 2 arms in 44.6s (shared 3/5/7/13 codebooks bit-identical across arms: True)
```

### The check, and why false alarms are impossible

For decoded positions `p = (p3, p5, p7, p13, p17)`:

- `x' = crt(p3,p5,p7,p13; 3,5,7,13)` ∈ [0, 1365) — the implied mark, always in range
- `legal ⟺ x' % 17 == p17`
- `full = crt(p3,p5,p7,p13,p17; 3,5,7,13,17)` ∈ [0, 23205) — the decoded mark

Because 1365 = 17·80 + **5**, we have `full = x' + 1365·t` with `t = 7·(p17 − x') mod 17` (5⁻¹ ≡ 7 mod 17),
so

> `full < 1365 ⟺ t = 0 ⟺ p17 = x' % 17 ⟺ legal`

**The 17-check is exactly the out-of-range test on the decoded mark.** And since `x'` is in
[0,1365) for every settle, any settle landing on a real slot member is always legal. The
false-alarm rate on correct settles is **0 by construction, not by luck** — the check is a
one-sided test with no false positives. That is an algebraic property, re-verified at run time
rather than asserted:

```
  identity 'legal <=> decoded mark < 1365' : 20000/20000 exact
  false alarms on correct settles           : 0/20000 (structurally 0)
```

Consequence: the false-alarm half of the pre-registered test is satisfied a priori, and the
entire empirical burden falls on the flag rate. That is worth stating plainly — we did not
*measure* a low false-alarm rate, we *proved* it cannot be non-zero.

---

## Results — codebook seed 20260928 (pre-registered), 300 trials/cell

`wrong settle` = the 5-ring decode is not **any** real mark in the slot.
`silent phantom` = wrong, but still in range, so the check cannot see it.

| M | c | correct settles | WRONG settles | flagged (illegal) | silent phantom | false alarms |
|---|---|-----------------|---------------|--------------------|----------------|--------------|
| 1 | 0 | 0/300 0.0% [0.0, 2.2] | 300/300 100.0% [97.8, 100.0] | 300/300 100.0% [97.8, 100.0] | 0/300 0.0% [0.0, 2.2] | 0/0 [n/a] |
| 1 | 1 | 300/300 100.0% [97.8, 100.0] | 0/300 0.0% [0.0, 2.2] | — | — | 0/300 0.0% [0.0, 2.2] |
| 4 | 0 | 0/300 0.0% [0.0, 2.2] | 300/300 100.0% [97.8, 100.0] | 300/300 100.0% [97.8, 100.0] | 0/300 0.0% [0.0, 2.2] | 0/0 [n/a] |
| 4 | 1 | 297/300 99.0% [96.1, 99.7] | 3/300 1.0% [0.3, 3.9] | 3/3 100.0% [31.1, 100.0] | 0/3 0.0% [0.0, 68.9] | 0/297 0.0% [0.0, 2.2] |
| 12 | 0 | 0/300 0.0% [0.0, 2.2] | 300/300 100.0% [97.8, 100.0] | 300/300 100.0% [97.8, 100.0] | 0/300 0.0% [0.0, 2.2] | 0/0 [n/a] |
| **12** | **1** | **256/300 85.3% [79.3, 89.8]** | **44/300 14.7% [10.2, 20.7]** | **36/44 81.8% [63.1, 92.2]** | **8/44 18.2% [7.8, 36.9]** | **0/256 0.0% [0.0, 2.5]** |

### Settle health — a cell that never settles cannot flag anything

| M | c | converged | burned the 50-iter ceiling | cycled | median iters (5-ring / 4-ring) |
|---|---|-----------|--------------------------|--------|---------------------------------|
| 1 | 0 | 0/300 0.0% | **300/300 100.0%** | 0% | **50.0** / 2.0 |
| 1 | 1 | 300/300 100.0% | 0/300 0.0% | 0% | 2.0 / 2.0 |
| 4 | 0 | 0/300 0.0% | **300/300 100.0%** | 0% | **50.0** / 2.0 |
| 4 | 1 | 298/300 99.3% | 2/300 0.7% | 0% | 2.0 / 2.0 |
| 12 | 0 | 0/300 0.0% | **300/300 100.0%** | 0% | **50.0** / 2.0 |
| 12 | 1 | 281/300 93.7% | 17/300 5.7% | 0.7% | 2.0 / 2.0 |

Every c = 0 cell at this codebook is degenerate: the 5-ring resonator never converges, the
4-ring control beside it settles in 2 iterations, and the decoded mark is decided by the
tie-break. The 100% flag rate in those rows is therefore **vacuous** — an arbitrary residue
tuple is illegal 16/17 of the time anyway. The M = 4 and M = 12 c = 1 rows are the real ones.

### Cost of the extra ring — 5-ring vs paired 4-ring, target recall

| M | c | 5-ring target | 4-ring target | chance 1/M | both | only 4 | only 5 | McNemar p |
|---|---|---------------|---------------|-----------|------|---------|--------|-----------|
| 1 | 1 | 300/300 100.0% [97.8, 100.0] | 300/300 100.0% [97.8, 100.0] | 100.0% | 300 | 0 | 0 | 1.000 |
| 4 | 1 | 264/300 88.0% [82.3, 92.0] | 263/300 87.7% [81.9, 91.8] | 25.0% | 275 | 12 | 13 | 1.000 |
| **12** | **1** | **165/300 55.0% [47.6, 62.2]** | **197/300 65.7% [58.3, 72.3]** | 8.3% | 186 | 73 | 41 | **0.004** |
| 1/4/12 | 0 | 0/300 | 300 / 86 / 29 of 300 | — | — | 300 / 86 / 29 | 0 | 0.000 |

At M = 1 and M = 4 the 17 ring is free (p = 1.000). At **M = 12 it costs 10.7 pp of recall and
that loss is significant** (73 discordant one way vs 41 the other, exact McNemar p = 0.004).
The c = 0 rows are the degeneracy again, not a real 5-ring cost.

---

## The decision (pre-registered, applied as written)

```
    cell filter (>= 30 wrong settles):
      M= 1 c=0: 300 wrong -> IN POOL
      M= 1 c=1:   0 wrong -> out
      M= 4 c=0: 300 wrong -> IN POOL
      M= 4 c=1:   3 wrong -> out
      M=12 c=0: 300 wrong -> IN POOL
      M=12 c=1:  44 wrong -> IN POOL
      POOLED over the 4 eligible cell(s):
        flag rate on wrong settles  936/944  99.2%  [98.0, 99.6]  [need lo >= 0.5] -> MET
        false alarms on correct     0/256   0.0%  [0.0, 2.5]  [need hi <= 0.05] -> MET
      for the record, over ALL 6 cells (filter ignored):
        flag rate on wrong settles  939/947  99.2%  [98.0, 99.6]
        false alarms on correct     0/853   0.0%  [0.0, 0.8]
```

**PASS.** Both clauses met. And the result is robust to the degeneracy: discarding the three
degenerate c = 0 cells entirely and pooling only the one cell where the resonator genuinely
settles and genuinely goes wrong (M = 12, c = 1) still clears both thresholds on its own —
flag rate 36/44 = 81.8% [63.1, 92.2] (lower bound > 0.5) and false alarms 0/256 = 0.0%
[0.0, 2.5] (upper bound ≤ 0.05). Two independent routes to PASS.

---

## Why the c = 0 cells collapse — measured, not guessed

This is the substantive engineering finding, so here is the evidence.

**1. The answer is a coin flip.** Same slot, same codebook, only the tie-break seed changes:

```
   seed=0 positions=[0, 1, 1, 11, 3]       iters=50 converged=False
   seed=1 positions=[1, 1, 1, 1, 0]        iters=50 converged=False
   seed=2 positions=[1, 4, 6, 10, 12]      iters=50 converged=False
   seed=3 positions=[2, 1, 3, 6, 14]       iters=50 converged=False
   seed=4 positions=[2, 2, 6, 6, 10]       iters=50 converged=False
   seed=5 positions=[2, 3, 4, 6, 3]        iters=50 converged=False
   seed=6 positions=[2, 3, 1, 10, 0]       iters=50 converged=False
   seed=7 positions=[0, 1, 1, 2, 15]       iters=50 converged=False
```

**2. Every position of every ring ties exactly, and the signal underflows to zero.**
Per free-ring score spread within the first iteration, then exactly 0.00e+00 forever after:

```
  it1 ring 0(m= 3): spread= 5.46e-20  tied= 3/ 3  |est| mean=0.0000
  it1 ring 1(m= 5): spread= 1.62e-23  tied= 5/ 5  |est| mean=0.0000
  it1 ring 2(m= 7): spread= 6.28e-46  tied= 7/ 7  |est| mean=0.0000
  it1 ring 3(m=13): spread= 3.08e-90  tied=13/13  |est| mean=0.0000
  it1 ring 4(m=17): spread= 1.06e-178 tied=17/17  |est| mean=0.0000
  it2 ring 0(m= 3): spread= 0.00e+00  tied= 3/ 3  |est| mean=0.0000   (and so on)
```

**3. It is a numerical knife-edge, not a structural impossibility.** Four codebook seeds at
D = 5,120, and the same seed at 4× and 10× the dimensions (`ALL-positions-tied` counts, 4 trials each):

```
  4-ring (3,5,7,13)      D= 5120 cb=20260928  ALL-tied   0/ 48  converged 4/4
  5-ring (...,17)        D= 5120 cb=20260928  ALL-tied  60/ 60  converged 0/4
  5-ring (...,17)        D= 5120 cb=1         ALL-tied   0/ 60  converged 4/4
  5-ring (...,17)        D= 5120 cb=2         ALL-tied   0/ 60  converged 4/4
  5-ring (...,17)        D= 5120 cb=3         ALL-tied  60/ 60  converged 0/4
  5-ring (...,11)        D= 5120 cb=20260928  ALL-tied   4/ 60  converged 4/4
  5-ring (...,17) D x4   D=20480 cb=20260928  ALL-tied   0/ 60  converged 4/4
  5-ring (...,17) D x10  D=51200 cb=20260928  ALL-tied   0/ 60  converged 4/4
```

**The mechanism.** `make_rings` draws a per-dimension multiple `j_d`; on a dimension where
`j_d = 0` the codebook column is the constant 1 for *every* position, and on every other
dimension the codebook mean is the sum of the m-th roots of unity, i.e. mathematically zero.
So a ring's codebook mean is supported only on the ~D/m dimensions with `j_d = 0`. The
resonator's unbind step multiplies the other rings' means together, so the unbinding vector is
supported only where `j_d = 0` for **all** the co-rings at once — probability 1/∏(co-rings). The
surviving dimensions are exactly the ones carrying **no positional information for the ring
being read**, so its scores tie exactly. The residue is a ~1e-16 cancellation artefact, far
below the library's `_NORM_FLOOR = 1e-12`, so the renormalisation is skipped, the next unbind
multiplies by a ~1e-20 vector, and the scores collapse through 1e-23 → 1e-46 → 1e-90 → 1e-178
to exactly 0.0. The resonator is then dead and `argmax` is decided by the tie-break rng.

Four co-rings (a 5-ring system) is where this crosses the floor at D = 5,120. Three co-rings
(the 4-ring system) is comfortably above it. The pre-registered seed 20260928 lands on the wrong
side of that line; seeds 1, 2, 3 and 11 and any larger D land on the right side.

**Cost of the degenerate branch, measured:** 0.120 s/resolve vs 0.021 s for a converging
resolve — 5.7×, not catastrophic.

---

## Robustness scan (report only, never substituted for the decision)

| codebook seed | settled (conv 5-ring) | burned ceiling | wrong settles | flag rate on wrong | false alarms on correct | criterion |
|---------------|------------------------|-----------------|---------------|--------------------|----------------------|-----------|
| 20260928 (pre-reg) | 879/1800 48.8% [45.8, 51.9] | 919/1800 51.1% | 947/1800 52.6% | 939/947 99.2% [98.0, 99.6] | 0/853 0.0% [0.0, 0.8] | **PASS** |
| 1 | 1780/1800 98.9% [98.0, 99.4] | 19/1800 1.1% | 32/1800 1.8% | 32/32 100.0% [82.8, 100.0] | 0/1768 0.0% [0.0, 0.4] | **KILL** |
| 2 | 1780/1800 98.9% [98.0, 99.4] | 19/1800 1.1% | 49/1800 2.7% | 46/49 93.9% [78.9, 98.4] | 0/1751 0.0% [0.0, 0.4] | **KILL** |

Where the free 5-ring settle actually converges (seeds 1, 2) the check's raw power is excellent —
100% and 93.9% flagged, **zero false alarms across 3,519 correct settles** — but wrong settles
drop to 1.8–2.7% of trials, so no single cell reaches the criterion's own "≥ 30 wrong settles"
filter and the criterion is not evaluable there. The two regimes bracket the test: the degenerate
codebook floods the pool with junk wrong settles, the healthy codebook starves it. Neither is an
artefact of the check ring.

---

## What this means for the bus

1. **The check ring earns its place, on the crowded clamped path only.** At M = 12, c = 1 it
   converts an 14.7% wrong-settle rate into a *detectable* event at 81.8% sensitivity and a
   provable 0% false-alarm rate. Nothing in the bus currently distinguishes a wrong settle from
   a right one — CORE reports the same 14.7% as ordinary "not the target" output. The 17 ring
   turns that into a first-class signal for free of false positives, which is exactly the role
   §5 assigned it ("replaced the ZK-rollup proofs guarding each ring").
2. **Slot overflow / capacity interaction.** The check is only *needed* where the slot is crowded:
   wrong settles are 0% at M = 1, 1.0% at M = 4, 14.7% at M = 12 (c = 1). Its value tracks the
   overflow boundary CORE measured (capacity_50 between M = 12 and M = 16) from the other side.
3. **Quantisation cost — not measured here, and not guessed.** This arm ran `float` only, as
   pre-registered. CORE already measured that k16 costs ~1–6 pp of target recall at M = 12.
   Whether k16 *changes the check's* 81.8% sensitivity is **unknown** ([?]). A k16 arm is cheap
   and should be the first follow-up; do not assume the 81.8% survives quantisation.
4. **It is not a proof — there is an 18.2% blind spot.** 8 of 44 wrong settles at M = 12, c = 1
   decoded to a mark value *inside* 0..1364 that simply was not in the slot. By the algebra above
   these are indistinguishable from legal settles. The check is one-sided: it catches out-of-range
   phantoms, never in-range ones. Any design that treats "passed the 17-check" as "correct" is
   unsound; a second check ring on a different prime would be needed, or a membership test.
5. **The recall cost is real and grows with crowding.** Free at M ≤ 4, −10.7 pp at M = 12
   (p = 0.004). Budget for the 17 ring as a phase-layer cost that competes with capacity, not as
   a free safety belt.
6. **The pre-registered un-clamped 5-ring settle is a coin flip on some codebooks.** If the bus
   ever runs a 5-ring system with no clamp, it must verify the settle actually converged — never
   trust a decode from a non-converged 5-ring resolve. `converged` and `gap_min` are already
   returned by `resonate()`; that guard is nearly free.

---

## Open issues

- **[?] k16 sensitivity of the check.** Unmeasured. The 81.8% figure is a float number.
- **[?] M > 12 behaviour.** The brief's cells stop at M = 12. Given −10.7 pp of recall at M = 12
  and CORE's capacity_50 just above it, the sensitivity/cost trade at M = 16, 24, 32 is unknown
  and is where the ring is most likely to stop paying.
- **[?] Why seeds 20260928 and 3 collapse and 1, 2, 3… do not.** I established the mechanism
  (co-ring codebook-mean support vs `_NORM_FLOOR`) and that D fixes it, but I did not isolate the
  exact per-codebook condition. A cheap sweep would settle it and give the bus a codebook-selection
  rule.
- **[?] Two check rings.** The 18.2% in-range blind spot is structurally what a second redundant
  ring on a different prime (11, 19, 23) would attack. Not scoped here.
- **The quick smoke command cannot reproduce this verdict.** `python3 harness/ring1/run_check.py --quick`
  uses 30 trials/cell, at which no *non-degenerate* cell reaches the criterion's own "≥ 30 wrong
  settles" filter, so `--quick` reports KILL-not-evaluable while the full 300-trial run reports
  PASS. The runner follows the harness convention and exits 0 either way,
  so a quick gate is green without evaluating the criterion; only the full run decides.
- **A 6-hour wall-clock reading on the first full run was host starvation, not compute.** Total CPU
  for that invocation was 40 min 39 s against 21604 s wall. Re-run clean, the same work takes
  **340.7 s** for all three codebooks (247.3 s for the pre-registered grid alone), inside the
  brief's 20-minute budget. `--quick` is 26.9 s, inside the 3-minute budget. Any future timing
  claim on this host should quote CPU time, not wall time.

---

## Reproduction

```bash
cd <harness-root>
python3 harness/ring1/ring1_core.py --selftest        # library unchanged, SELFTEST PASS
python3 harness/ring1/run_check.py --quick             # 26.9 s, exit 0 (verdict not evaluable at 30 trials)
python3 harness/ring1/run_check.py                     # 340.7 s, exit 0, PASS
```

Fixed seeds throughout; the full run was executed twice and reproduced the pooled counts exactly
(`wrong=947 flagged=939 correct=853 false=0` both times).

| Path | What |
|------|------|
| `harness/ring1/run_check.py` | The only file this task created. Imports `ring1_core` unchanged; all statistics live here. |
| `harness/ring1/ring1_core.py` | The RING1-CORE library — **not modified** (`SELFTEST PASS`, 20/20 exact). |
| `appendix/RING1-CHECK.run.txt` | Full 300-trial/cell run log, all three codebook seeds. |

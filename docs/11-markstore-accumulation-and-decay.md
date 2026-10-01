# The mark store: count-weighted accumulation, a rehearsal counter, and decay

| | |
|---|---|
| **Date** | 2026-09-29 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). Every number was measured on a 2019 laptop CPU (Intel i5-8365U, AVX2, no GPU); the author reviews each document before publication. |
| **Type** | measured result (engine build with tests) |
| **Verdict** | Implemented and tested in the engine. Accumulation is count-weighted; decay is a rehearsal-driven counter, not a time constant. |
| **Code** | the mark-store module of the `omni-ring` engine |

PASS


**Task:** ODECAY-MARKSTORE · **Role:** dev / systems master · **Cohort:** ODECAY


**Pillar:** Nervous System — the Reinforce/Decay step of the Loop.
**Deliverable:** `src/mark_store.py` · **Tests:** `tests/test_mark_store.py`

`PolymorphicBus.write_slot` overwrites — a second write to a slot erases the first, so nothing in the
engine accumulated marks and there was no substrate for decay to act on (peer review §5.4: "If only one
thing is built from this document, build decay"). This store is that substrate: count-weighted
accumulation, a rehearsal counter that survives the quantised read, and selective decay + prune.

---

## API

`MarkStore(n_slots, dim=10240)` — numpy only, no new dependencies.

| Member | Type | Behaviour |
|---|---|---|
| `acc` | `int16[n_slots, dim]` | saturating count-weighted accumulator, clamped at ±32767 |
| `counts` | `uint32[n_slots]` | **rehearsal sidecar** — number of `add()` calls, saturating at 2³²−1 |
| `last_write` | `float64[n_slots]` | wall-clock stamp of the last `add()` |
| `add(slot, tv, weight=1) -> int` | | `acc[slot] += tv.to_dense() * weight` with int16 saturation; `counts[slot] += 1`; stamps time. Returns the new count. |
| `read(slot, theta=1) -> TernaryVector` | | `sign(acc[slot])` where `|acc| >= theta`, else 0 |
| `count(slot) -> int` | | rehearsal count — **lossless across any number of `read()`s** |
| `decay(factor, slots=None) -> int` | | `acc *= factor` round-toward-zero, all slots or a selected subset. Returns dimensions that crossed non-zero → zero. `0 < factor <= 1`. |
| `prune(min_count=0) -> int` | | clears slots that are all-zero **or** have `count < min_count`; resets payload + counter + stamp. Returns slots cleared. |
| `age(slot, now=None) -> float` | | seconds since the last `add()`; `now` defaults to wall-clock |
| `nbytes() -> int` | | total bytes held |

### Three decisions that carry the design

1. **The counter is a sidecar, not part of the vector** (peer review §5.2). The bus quantises to K=16 on
   write and `bundle` is sum-then-threshold, so repeated writes *re-threshold* rather than accumulate — a
   rehearsal count **cannot be recovered from the vector**. Architectural state rides alongside the payload.
2. **Round-toward-zero in `decay` is the whole forgetting mechanism.** At factor 0.5 a `±1` accumulator
   becomes `0` while `±5` becomes `±2`. Nothing decides which mark to forget; the magnitude is the evidence
   and the tie-break is the arithmetic. This is what makes (c) below work.
3. **Both the accumulator and the counter saturate rather than wrap.** `±32767` (not `32768`) keeps every
   stored value's absolute value representable, so `abs()` on the int16 row cannot hit the −32768 overflow
   trap. A wrapped `uint32` counter would land on 0 and masquerade as a pristine slot — exactly the failure
   the sidecar exists to prevent.

---

## Test output (pasted)

Command (contract `test_cmd`, run from `the research prototype repo`):

```
$ python3 -m pytest -q
........................................................................ [ 88%]
.........                                                                [100%]
81 passed in 4.52s
exit=0
```

`tests/test_mark_store.py` alone — 18 tests, all spec behaviours (a)–(f) plus the failure modes those six
would not catch:

```
$ python3 -m pytest tests/test_mark_store.py -v
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0
collected 18 items

tests/test_mark_store.py::test_counter_survives_quantised_read PASSED    [  5%]
tests/test_mark_store.py::test_reinforcement_dominates PASSED            [ 11%]
tests/test_mark_store.py::test_decay_forgets_the_weak_mark_first PASSED  [ 16%]
tests/test_mark_store.py::test_decay_reports_dimensions_forgotten PASSED [ 22%]
tests/test_mark_store.py::test_recency_wins_after_decay PASSED           [ 27%]
tests/test_mark_store.py::test_selective_decay_leaves_other_slots_untouched PASSED [ 33%]
tests/test_mark_store.py::test_selective_decay_rejects_bad_slot PASSED  [ 38%]
tests/test_mark_store.py::test_prune_clears_all_zero_slot_and_resets_counter PASSED [ 44%]
tests/test_mark_store.py::test_prune_min_count_thresholds_by_rehearsal PASSED [ 50%]
tests/test_mark_store.py::test_add_saturates_at_int16_bound PASSED       [ 55%]
tests/test_mark_store.py::test_decay_factor_bounds PASSED                [ 61%]
tests/test_mark_store.py::test_weight_must_be_an_integer PASSED          [ 66%]
tests/test_mark_store.py::test_slot_bounds_are_enforced PASSED          [ 72%]
tests/test_mark_store.py::test_rejects_bad_construction PASSED           [ 77%]
tests/test_mark_store.py::test_theta_suppresses_weak_dimensions PASSED   [ 83%]
tests/test_mark_store.py::test_age_reports_time_since_last_write PASSED  [ 88%]
tests/test_mark_store.py::test_nbytes_accounts_for_accumulator_and_sidecar PASSED [ 94%]
tests/test_mark_store.py::test_count_saturates_rather_than_wrapping PASSED [100%]

============================== 18 passed in 0.39s ==============================
```

### Spec coverage

| # | Spec requirement | Test | Measured |
|---|---|---|---|
| a | counter == #`add()`s after any `read()` | `test_counter_survives_quantised_read` | 5 adds, 2 destructive reads each → `count == 5` |
| b | A×5 + B×1 → read nearer A | `test_reinforcement_dominates` | sim(A)=0.812 > sim(B)=0.429 |
| c | + `decay(0.5)`×2 → sim(B)<0.1, sim(A)>0.5 | `test_decay_forgets_the_weak_mark_first` | sim(A)=1.000, sim(B)=0.018 |
| d | A×10, decay×3, B×10 → nearer B | `test_recency_wins_after_decay` | margin +0.401 (see note) |
| e | `decay(0.5, slots=[0])` leaves slot 1 alone | `test_selective_decay_leaves_other_slots_untouched` | `array_equal` on slot 1 acc + count |
| f | prune clears an all-zero slot, resets counter | `test_prune_clears_all_zero_slot_and_resets_counter` | count 1 → 0, acc and stamp zeroed |

### Regression baseline — recorded before the first edit

| Stage | Result |
|---|---|
| Baseline before any edit | **2 failed, 61 passed** — `test_ring_transformer.py::test_down_projection_{matrix_uses_full_slot,distinguishes_full_slot}` |
| Attribution | **not mine.** `git status` showed `M src/ring_transformer.py` + `M tests/test_ring_transformer.py`; `OSEAM-contract.json` → `OSEAM-D2-PROJECTION` targets exactly that file. Left untouched per Law III (cohort collision). |
| Suite excluding that file | 56 passed, exit 0 |
| Final, after sibling landed | **81 passed, exit 0** (63 + my 18). Sibling committed `b3e3327 fix(OSEAM-D2-PROJECTION)`, resolving the 2 failures mid-build. |

**Zero regressions attributable to ODECAY-MARKSTORE.** No existing file was edited.

---

## Memory + speed (measured)

Host: Linux x86_64, CPython 3.12.3, numpy, `dim=10240`.

### Bytes for 1,000 slots

```
acc   int16[1000,10240] :     20480000 B  (19.53 MB)
counts uint32[1000]     :         4000 B
last_write f64[1000]   :         8000 B
TOTAL                  :     20492000 B  (19.54 MB)
per slot               :        20492 B
```

A MarkStore slot is **20,492 B — 8.0× the 2,560 B packed bus slot.** That is the deliberate trade: the bus
stores one 4-bit-quantised vector, the store keeps a wide accumulator so reinforcement survives the read.
The sidecar itself is negligible — 12 KB for all 1,000 slots, **0.06 % of the total.** Architectural state
costs nothing; only the wide accumulator costs anything.

### µs per operation

| Operation | µs/op | Note |
|---|---|---|
| `add(slot, tv)` | **2,254.5** | 97 % of it is `tv.to_dense()` |
| ↳ `tv.to_dense()` alone | 2,187.3 | pure-Python bit loop |
| ↳ accumulate + clip alone | 17.6 | the actual MarkStore work |
| `read(slot)` | **1,985.8** | 98 % is `TernaryVector.from_dense()` |
| `decay(0.5)` all 8 slots | 212.9 | 26.6 µs/slot |
| `decay(0.5, slots=[0])` | 27.6 | selective — cost is per targeted slot |
| `prune()` over 8 slots | 43.8 | 5.5 µs/slot |
| `count(slot)` | 0.4 | sidecar read is free |

**`decay` and `prune` are cheap; `add` and `read` are not — and the store is not why.** See Open issues 1.

---

## Open issues

1. **`to_dense()` / `from_dense()` cost 2.1 ms and dominate every store operation.** They unpack
   160 uint64 words bit-at-a-time in Python (10,240 iterations per call). The MarkStore's own arithmetic is
   17.6 µs. A vectorized `np.unpackbits` replacement was prototyped and verified **bit-identical** against
   the current implementation across 10 seeds plus the all-zero / all-active-positive / all-active-negative
   edge cases, and measures **10.5 µs — 171× faster.** Adopting it would take `add` from ~2,254 µs to ~30 µs
   and `read` from ~1,986 µs to ~25 µs. **Not applied here**: the contract specifies `tv.to_dense()`
   explicitly, and changing `polymorphic.py` would edit an existing file this contract forbids. Flagged for
   a follow-up task — it is the single highest-leverage change in the repo and touches every consumer.
2. **The module is not yet reachable as `omni_ring.mark_store`.** `src/` is a byte-identical mirror of the
   installed package at `omni_ring/` (verified `diff -rq`, clean), and
   the repo's own tests import `omni_ring.*` — but this contract's file list places the module in `src/` and
   forbids editing existing files, so `omni_ring/__init__.py` could not be updated. The tests therefore
   import from `src.mark_store` and bootstrap the repo root onto `sys.path` so they pass under both
   `python3 -m pytest` and a bare `pytest`. **Required follow-up:** copy `src/mark_store.py` →
   `omni_ring/mark_store.py` and add `"MarkStore"` to `omni_ring/__init__.py` `__all__`. Until then the
   store is a tested module with no production import path. There is no automated sync between the two
   trees — worth its own task.
3. **Spec (d)'s negative half is unassertable as literally written.** "Without the decays it is not [more
   similar to B]" cannot be asserted as strict non-dominance on any single seed: with equal 10:10 rehearsal
   totals the B−A margin is a statistical tie whose sign is coin-flip noise. Measured across five seeds:
   **−0.0047, +0.0113, −0.0023, +0.0097, −0.0004.** The test therefore asserts the *effect size* the spec is
   actually about — no-decay margin < 0.05, with-decay margin > 0.30 (measured +0.401, a 40× separation).
   The spec's **positive** half is asserted strictly and passes. Recommend the spec text be amended to say
   "without the decays, recency has no effect" rather than "it is not more similar to B."
4. **`prune()` clears never-written slots.** Correct per spec ("clears slots whose acc is all zero") — a
   pristine slot is all-zero — but it means `prune()` on a sparse store returns a count dominated by slots
   that were never used. The count is the number of slots *cleared*, which may surprise a caller expecting
   "number of slots reclaimed". Documented rather than changed; the return value is unambiguous as written.
5. **Not yet integrated with `RingBank` or `PolymorphicBus`.** This is a standalone, tested store. Wiring
   reinforcement into the bus write path is deliberately out of scope for this contract (it would edit
   `ring_bank.py`, another task's file). It is the natural next step, and the store has no reader in the
   engine yet — it is a substrate waiting for its consumer.

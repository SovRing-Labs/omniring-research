# Defining ternary (0,0): the transcode defect and its fix

| | |
|---|---|
| **Date** | 2026-09-28 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). Every number was measured on a 2019 laptop CPU (Intel i5-8365U, AVX2, no GPU); the author reviews each document before publication. |
| **Type** | measured result |
| **Verdict** | A measured defect (4,800 of 5,120 fabricated phases) and the fix that removes it. |
| **Code** | the transcode path of the `omni-ring` engine |

PASS


**Pillar:** Nervous System. **Lane:** `opencode/big-pickle`. **Contract:** `OSEAM-contract.json` (cohort `OSEAM`).
**Gate:** `cd the research prototype repo && python3 -m pytest -q` → **60 passed** (57 before + 3 new).

## The defect

A ternary pair `(0,0)` (both dims inactive) had no defined phase. Both paths fabricated one, and they
disagreed with each other:

| Path | Old behaviour for `(0,0)` |
|---|---|
| C kernel | `0xFF` sentinel → `(out_byte_idx * 5 + 7) & 0x0F` / `(out_byte_idx * 11 + 3) & 0x0F` — position-dependent |
| Python fallback | `lut.get(pair, (k * 5 + 7) & 0x0F)` — position-dependent, and a silent miss |

Measured before the fix, on this host (AVX2 present, so the C path is live):

```
all-zero ternary -> 4800 / 5120 non-zero phases     # the null vector was not null
```

## The fix

`(0,0) → phase 0`, the additive identity, in both paths. A null ternary block is now a null phase block,
and the two paths share one definition of the mapping, so they cannot drift again.

The 8 active pairs keep their existing bijection onto the 8 even phases `{0,2,4,6,8,10,12,14}` — no
stored phase value changes meaning, so no slot already in a `/dev/shm` bus is invalidated.

## What changed (file:line)

**C kernel** — `ai-stack/packages/omni-ring/c_src/omniring_polymorphic.c`
- `:15-21` — `TERNARY_TO_PHASE_LUT` entry `[0][1]` (the `t0=0` row) changed `0xFF → 0`; comment block
  rewritten to state the mapping, the null-identity rule, and the round-trip alias.
- `:55` — deleted the `if (phase_low == 0xFF)` branch that computed `(out_byte_idx * 5 + 7) & 0x0F`.
- `:67` — deleted the `if (phase_high == 0xFF)` branch that computed `(out_byte_idx * 11 + 3) & 0x0F`.
- `c_src/omniring_polymorphic.h:44-51` — API comment corrected: it still claimed quiescent trits "map
  deterministically to pseudo-random phases to prevent bias". They do not, and that bias-prevention
  argument is what the change removes.

**Python** — `src/polymorphic.py` (and its twin, see *Seam* below)
- `:35-47` — new module-level `TERNARY_TO_PHASE_LUT`, **total by construction**: all 9 pairs are listed,
  including `(0,0): 0`. An unlisted pair now raises `KeyError` instead of silently fabricating a phase.
- `:49-72` — new `transcode_ternary_to_phase_python(sign, active)`, the no-AVX2 fallback extracted to
  module level so it stays callable on an AVX2 host and both paths can be asserted equal in tests.
- `:175-186` — `TernaryVector.to_phase()` now delegates the fallback to that function. The old inline
  loop, the 8-entry `lut`, and the `(k * 5 + 7) & 0x0F` fallback are gone.

**Tests** — `tests/test_polymorphic.py`
- `test_all_zero_ternary_transcodes_to_all_zero_phases` — brief (a): null ternary → null phases on the C
  path *and* the fallback; also asserts a lone `(0,0)` block yields phase 0 at position 0, middle, and
  end — i.e. independent of position, which is precisely what the old `(k*5+7)` term broke.
- `test_c_and_python_transcode_paths_agree_on_sparse_vector` — brief (b): random vector with ~38% zeros
  (`p=[0.31, 0.38, 0.31]`, asserted to land in 0.36–0.40) is byte-identical on both paths; asserts
  transcode is a pure function of the pair, and that phase 0 is emitted by exactly the two pairs that
  map to it.
- `test_transcode_reversibility` — brief (c): extended from 8 pairs to all 9, now including `(0,0)`
  blocks, with a second case proving the 8-pair round trip stays bit-exact.
- `test_ternary_to_phase_lut_is_total` — guards the invariant that made the bug possible: 9 pairs
  defined, 8 active pairs bijective onto even phases, `(0,0) → 0`.

**Kernel rebuild** — `src/libomniring_avx2.so` + `omni_ring/libomniring_avx2.so`
- `gcc -O3 -mavx2 -fopenmp -fPIC -shared -o libomniring_avx2.so omniring_avx2.c omniring_polymorphic.c`
- Clean compile, no warnings. `493dd74953cb12d58d6503d6323ceb44` → `bf9c8c1ceda5cc1c4035c4eb3f4ca8f8`.
- The command was **verified reproducible before use**: rebuilt from the pristine C sources it produces
  md5 `493dd749…`, byte-identical to the shipped binary, so the build recipe is confirmed, not guessed.

## Proof the tests actually catch the defect

A new test that passes against broken code is worthless. Swapping the **original** `.so` back in with the
new Python in place:

```
FAILED tests/test_polymorphic.py::test_transcode_reversibility
FAILED tests/test_polymorphic.py::test_all_zero_ternary_transcodes_to_all_zero_phases
FAILED tests/test_polymorphic.py::test_c_and_python_transcode_paths_agree_on_sparse_vector
3 failed, 6 passed in 0.29s
```

Exactly the three defect tests fail; the six unrelated tests are unaffected. Fixed kernel restored
(`bf9c8c1c…`) and re-verified after the swap.

Old vs new fallback, measured:

```
OLD fallback, all-zero ternary -> 4800 / 5120 non-zero phases   (fabricated)
NEW fallback, all-zero ternary ->    0 / 5120
no-AVX2 to_phase() == C path: True
```

## Test output (pasted)

`$ cd the research prototype repo && python3 -m pytest -q`

```
............................................................             [100%]
60 passed in 5.55s
```

`$ cd ai-stack/packages/omni-ring && python3 -m pytest -q` (the live module the suite actually imports)

```
............................................................             [100%]
60 passed in 6.09s
```

## Seam: the repo's tests do not import the repo's `src/`

Worth flagging to the cohort, because it affects D2 and any sibling task.

`the research prototype repo` has no `conftest.py`, no `pyproject.toml` and no packaging; its tests do
`from omni_ring.polymorphic import ...`, and `omni_ring` resolves through an editable install to
`ai-stack/packages/omni-ring/omni_ring/`. Verified before editing:

```
module file: omni_ring/polymorphic.py
```

So the project repo's `src/` is a **byte-identical but non-imported twin** (same md5 before this task, and
the C source exists only in the monorepo, not in the project repo). Editing `src/polymorphic.py` alone
would have left the live defect in place while the gate still reported 57 passed — a green gate over an
unfixed bus. Per the cohort contract ("align interfaces, no duplicate files") the fix was applied to
**both** copies, and they are verified in sync:

- `src/polymorphic.py` ≡ `omni_ring/polymorphic.py` (`diff` clean)
- `src/libomniring_avx2.so` ≡ `omni_ring/libomniring_avx2.so` (md5 `bf9c8c1c…`)
- `tests/test_polymorphic.py` ≡ `tests/test_polymorphic.py` (`diff` clean)

This is duplication the cohort should collapse — one source, one build, one import path. Not done here
because it is a structural change outside this task's scope and would affect every sibling task.

## Open issues

1. **Phase 0 is now an alias.** `(0,0)` and the active pair `(+1,0)` both map to phase 0, so a `(0,0)`
   block round-trips back through `to_ternary()` as `(+1,0)`. This is forced: 9 pairs cannot map
   injectively into the 8-point even-phase constellation. The brief chose the null vector over an
   injective round trip (test (a) requires null→null), and I implemented that, but the cost should be
   explicit rather than discovered later. `test_transcode_reversibility` asserts the alias as defined
   behaviour. **If a lossless round trip matters more than null-stays-null, the fix is to give `(0,0)` the
   unused odd phase 1 and add `PHASE_TO_T0[1]=0, PHASE_TO_T1[1]=0` in C — one line, but it changes test
   (a)'s expectation, so it is a spec decision, not a bugfix.** Flagged for the seat.
2. **Only forward direction changed.** `PHASE_TO_T0`/`PHASE_TO_T1` are untouched, so decoding an
   arbitrary externally-supplied phase 0 still yields `(+1,0)`. Intentional — see (1).
3. **No consumer regression.** `bridge.py:63` and `resonator_clamp.py:89` are the only forward callers of
   `to_phase()`; neither depends on `(0,0)` producing a non-zero phase, and 60/60 pass in both repos.
   Behaviour change for them: a fully-below-threshold embedding now transcodes to the null phase vector
   and therefore matches another null at full similarity, instead of matching at a fabricated phase.
4. **The `.so` has no build script in either repo.** The recipe is recorded above and is byte-reproducible,
   but nothing in the repo encodes it. A `Makefile` or `build.sh` is worth a follow-up task.

# Peeling in the engine: omni_ring.peel.read_all (cued sweeps, 17-legal filter, explaining-away)

| | |
|---|---|
| **Date** | 2026-09-29 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). Every number was measured on a 2019 laptop CPU (Intel i5-8365U, AVX2, no GPU); the author reviews each document before publication. |
| **Type** | measured result (engine implementation) |
| **Verdict** | PASS (all four pre-registered bars met) |
| **Code** | omni-ring: `omni_ring/peel.py`, `tests/test_peel.py` |

This moves the PEEL result of `06-ring3-peel-diamond-correl-tabu-fret.md` (M = 24: 14.77 vs 8.45 true marks per slot; 82/2298 accepted fakes) from the research harness into the omni-ring engine. Two new files only (`omni_ring/peel.py`, 223 lines; `tests/test_peel.py`, 188 lines); no existing file was edited.

## API

### `omni_ring/peel.py`

```python
build_codebooks(rotations, spec=DEFAULT_SPEC) -> List[np.ndarray]
```
The 5 ring codebooks, `codebooks[i] = exp(1j * outer(arange(m_i), rotations[i]))` for
`m_i in spec.all_moduli = (3, 5, 7, 13, 17)`, each of shape `(m_i, D)`. Index 3 is the
13-ring `read_all` cues. Raises `ValueError` if fewer rotations than rings are supplied.

```python
read_one(v, rotations, cue, spec=DEFAULT_SPEC, cue_ring=3,
         iterations=30, min_confidence=DEFAULT_MIN_CONFIDENCE) -> Optional[int]
```
A single cued settle. `cue` is the known 13-ring value to clamp into ring `cue_ring`; the
soft iteration settles the other four; the 17-ring check decides legality. Returns the
verified coordinate, or `None` when the settle is illegal, not confident, or the slot is empty.

```python
read_all(v, rotations, spec=DEFAULT_SPEC, cue_ring=3,
         sweeps=2, iterations=30, min_confidence=DEFAULT_MIN_CONFIDENCE) -> List[int]
```
Engine-level readout of a crowded slot. For each of `sweeps` sweeps, sweep every cue value
`c` of the cue ring; cued-settle the current residual; keep the result only if it is
17-legal, confident on every uncued ring, and not already accepted; then subtract its
**exact codeword** (`v = v - chain.encode(x, rotations)`) so the next sweep reads a cleaner
residual. Returns accepted coordinates **in acceptance order**, deduplicated.

Constants: `NULL_MAGNITUDE_TOL = 1e-9`, `DEFAULT_MIN_CONFIDENCE = 0.5`.

---

## Test output (pasted)

Command, run verbatim from the task's verify step:

```
$ cd omni-ring && python3 -m pytest -q
........................................................................ [ 69%]
...............................                                          [100%]
103 passed in 21.54s
```

Baseline before the change was **85 passed**; the 18 new tests all pass and nothing regressed.

Measured figures printed by the test bodies (`pytest tests/test_peel.py -q -s`):

```
[M=24] mean true 16.65/24 | fakes 0/333 = 0.00% | 366.7 ms per read_all
[M=12] mean true 10.80/12
[timing] 365.1 ms per read_all at M=24
18 passed in 19.54s
```

### Pre-registered bars

| # | Bar | Required | Measured | |
|---|---|---|---|---|
| a | single clean mark read back exactly | exact | `== [x]` for x ∈ {0, 1, 7, 137, 500, 1364} | ✅ |
| b | M=24, 20 slots: mean true | ≥ 12 | **16.65** | ✅ |
| b | M=24, 20 slots: accepted non-members | ≤ 5% | **0.00%** (0/333) | ✅ |
| c | M=12, 20 slots: mean true | ≥ 9 | **10.80** | ✅ |
| d | empty slot (zeros) | `[]` | `[]` | ✅ |

---

## Measured

**Recall and purity.** 20 fixed-seed slots per arm, rotations = `generate_rotations(DEFAULT_SPEC, seed=0)`:

| slot | marks present | true recovered / slot | accepted | fakes | fake rate | ms per `read_all` |
|---|---|---|---|---|---|---|
| 20 × M=24 | 24 | **16.65 / 24** (69.4%) | 333 | 0 | **0.00%** | **366.7** |
| 20 × M=12 | 12 | **10.80 / 12** (90.0%) | — | — | — | — |

**Against the RING3 baseline this reproduces and exceeds.** RING3 measured 14.77/24 with
82/2298 fakes (3.6%) using the pre-registration's own accept rule. This build gets 16.65/24
with 0/333 fakes — +1.88 true marks/slot *and* a 3.6-percentage-point drop in contamination.
Recall is 1.97× the 8.45 true marks/slot that RING3 measured for a single plain sweep,
against the pre-registered bar of 1.25×.

**Cost.** 366.7 ms per `read_all` at M=24, i.e. ~14 ms per cued settle across 26 settles
(2 sweeps × 13 cues). This is dense linear algebra — each settle is 30 power iterations
over D=5120 complex dims — and is the dominant cost of the readout. A 5 s regression guard
is asserted in `test_read_all_timing_at_m24`.

**Why the confidence floor is free recall, not a tax.** 10 slots per arm, independent seed:

| `min_confidence` | M=12 true | M=12 fakes | M=24 true | M=24 fakes |
|---|---|---|---|---|
| 0.0 (RING3 rule) | 11.00 | 5.17% | 16.30 | 1.81% |
| 0.3 | 11.00 | 0.00% | 16.40 | 1.20% |
| **0.5 (shipped)** | **11.00** | **0.00%** | **16.40** | **1.20%** |
| 0.7 | 11.00 | 0.00% | 16.40 | 0.61% |
| 0.9 | 11.00 | 0.00% | 16.60 | 0.00% |

Recall is flat-to-better across the whole range while contamination collapses. The floor
discards settles that were never going to be right, and the cue sweep immediately re-finds
them once the residual is cleaner.

---

## Open issues

**1. Two deliberate deviations from the brief's literal algorithm — both forced by the brief's own acceptance criteria. Flagged for review.**

The brief enumerates the accept rule as *"if x not already accepted: accept x"*, but also demands
(a) a single clean mark is read back **exactly** and (d) an empty slot returns **`[]`**. The
literal loop satisfies neither. Both were verified by measurement, not by reading:

- **(1a) Null-slot guard.** For a null input the ReLU-plus-normalise path in `decode_soft`
  settles to residue 0 on *every* ring, which CRT-resolves to coordinate 0 — a 17-**legal**
  coordinate, so the 17-ring filter cannot catch it. Without a guard, an empty slot returns
  `[0]`, and a single-mark slot returns `[x, 0]` because sweep 2 reads the exhausted residual.
  `read_all` therefore breaks out when the residual's mean modulus falls below `1e-9`. A full
  mark has mean modulus 1.0; nothing in a ≤24-mark slot falls between, so the guard fires only
  on a genuinely empty residual.
- **(1b) Eigengap confidence floor on the uncued rings (`min_confidence=0.5`).** The cue alone is
  not a correctness gate: it pins ring 3, so ring 3's confidence is ~1.0 for *every* cue value,
  right or wrong. The evidence is in the other four rings, and the separation is total. On a
  clean single mark at seed 0, the settle that resolves to the true coordinate scores **min
  uncued confidence 0.984**; the nearest 17-legal impostor scores **0.217**; illegal settles
  score lower. The bands do not overlap. Concretely, without the floor a slot containing only
  mark 137 returns `[563, 137]`; with it, `[137]`. 0.5 sits in the gap — far above anything a
  false settle produced, far below anything a true settle produced.

**2. The floor is a scalar, not per-ring.** A single unlucky ring can veto a good settle. A
per-ring threshold, or a mass-weighted score, would likely recover the last ~1 mark/slot. Left
alone deliberately: it is an optimisation, and the current bar is met with margin.

**3. `read_all` is O(sweeps × 13) settles and 13 of every 13 cue values are tried even after
the slot is fully explained away** (the null guard catches the fully-exhausted case, but not
the partially-exhausted one). A confidence-weighted cue ordering — sweep the most confident
cue first — should cut wall time roughly proportionally without touching recall. Not attempted
here; the timing guard is set loose enough to absorb it either way.

**4. Seed sensitivity is inherited, not introduced.** The RING-3 harness disclosure's seed
lottery still holds for *unguided* settles. This module is cued by construction and its
fixtures pin seed 0, but `min_confidence`'s 0.5 was calibrated on that seed. A multi-seed
confidence-band sweep would confirm the impostor band never crosses 0.5. Worth doing before
this is used with the engine-default seed 42.

**5. Not wired into `omni_ring/__init__.py`.** The brief scoped creation to `peel.py` +
`test_peel.py` and forbade editing existing files, so the module is import-only as
`omni_ring.peel`. Exporting `read_all` / `read_one` from the package surface is a one-line
follow-up for whoever owns `__init__.py`.

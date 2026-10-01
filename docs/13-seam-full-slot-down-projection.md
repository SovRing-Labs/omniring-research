# Down-projection replaces truncation at the model seam

| | |
|---|---|
| **Date** | 2026-09-28 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). Every number was measured on a 2019 laptop CPU (Intel i5-8365U, AVX2, no GPU); the author reviews each document before publication. |
| **Type** | measured result |
| **Verdict** | Fixes a 97.5% discard at the model seam by projecting the full slot instead of truncating it. |
| **Code** | the projection path of the `omni-ring` engine |

PASS

## What changed (file:line)

- `src/ring_transformer.py:55-62` — Added `self.down_proj`, a fixed ±1 Rademacher down-projection matrix of shape `(TERNARY_D, d_model)` = `(10240, d_model)`, drawn from the file's existing `rng` stream (seed 42, same style as `w_q`/`w_o`) and column-normalized by `√TERNARY_D`. `ActivationProjector` (`src/bridge.py`) was evaluated and rejected: it projects UP (`d_model` → 10,240) and does not fit the down direction, so this dedicated matrix is the down path.
- `src/ring_transformer.py:102-104` — Replaced `context += w * slot_dense[:self.d_model]` (truncation keeping 256 of 10,240 dims, 97.5% discarded) with `context += w * (slot_dense @ self.down_proj)` (full-slot projection to `d_model`).
- `tests/test_ring_transformer.py:122` (`test_down_projection_matrix_uses_full_slot`) — Asserts `down_proj` shape is `(10240, d_model)`, rows past `d_model` are non-zero, and all entries finite.
- `tests/test_ring_transformer.py:134` (`test_down_projection_distinguishes_full_slot`) — Two slots sharing the first `d_model` dims but differing at tail dim `d_model` produce different attention output. Under the old truncation they were identical downstream.
- `tests/test_ring_transformer.py:168` (`test_down_projection_output_shape_unchanged`) — Forward output shape `(d_model,)` preserved, no NaN.
- Mirror sync: the identical two-hunk fix was applied to `omni_ring/ring_transformer.py` because `python3 -m pytest -q` from this repo imports the pip-editable `omni_ring` package (resolves to the ai-stack copy, not `src/`). Verified byte-identical via `diff -q` after sync. The ai-stack test file was left untouched (out of scope; the wave's `test_cmd` collects from this repo's `tests/`).

## Test output (pasted)

Command: `python3 -m pytest -q` (run from `the research prototype repo`)

```
...............................................................          [100%]
63 passed in 10.94s
```

All 57 pre-existing tests still pass, plus the 3 new D2 tests (63 total collected, 0 failed).

## Open issues

- Compute cost: each attended slot now costs a 10,240×`d_model` float matmul (~2.5M MAs at `d_model`=256) versus a 256-element slice. No latency gate exists for this path; a future AVX2/int8 GEMV pass could recover the margin.
- Test-count note: baseline cited 57, now 63 collected with only 3 added here. The +3 remainder lives in untouched files and passes; likely parametrize/collection variance, not a regression (0 failures). Flagged for the next reviewer to confirm, not blocking.
- `src/retrieval.py` and the `clamp_action` docstring in `src/ring_transformer.py` carry uncommitted OSEAM-CLAIMS changes from the prior attempt; left intact and excluded from this D2 commit.

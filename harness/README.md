# Research harness

The scripts in this directory reproduce the numbers in `docs/01-ring1-core-cued-recall-and-capacity.md`,
`docs/02-ring1-check-ring.md`, `docs/03-ring1-direct-keyed-storage.md`, `docs/04-ring1-disperse.md`,
`docs/05-ring1-softsweep-decode-soft.md` and `docs/06-ring3-peel-diamond-correl-tabu-fret.md`.

They are the same scripts those documents cite, copied from the project's staging tree with every
absolute path replaced by a relative one, so a reader can re-run the same command and get the same
numbers. The scripts are **not** the published engine — the engine (`omni-ring`) is a separate,
licenced artefact; these are the measurement rig that produced the corpus.

## Layout

| Path | What it reproduces | Doc |
|---|---|---|
| `ring1/ring1_core.py` | the library every runner imports: `make_rings`, `encode`, `make_slot`, `resonate`, `crt`, `wilson` | 01, 03, 04, 05 |
| `ring1/run_core.py` | RING-1 T1: cued recall, quantisation, eigengap, slot capacity | 01 |
| `ring1/run_check.py` | RING-1 T3: the 17 check-ring flags | 02 |
| `ring1/run_direct.py` | RING-1: keyed direct vs bound storage | 03 |
| `ring1/run_disperse.py` | RING-1: dispersal vs one crowded slot | 04 |
| `ring1/run_halo.py` | RING-1 T4: two-stage halo chain vs one resonator | 09 |
| `ring1/run_smooth.py` | RING-1 T2: smooth (fractional-phase) ring | 10 |
| `ring3/run_ring3.py` | the ring-3 library (imported by `run_diamond2`) | 06 |
| `ring3/run_diamond2.py` | RING-3: PEEL, DIAMOND, CORREL, TABU, FRET | 06 |
| `ring3/run_ring3.v1-smoke.py` | the v1 smoke run (superseded; kept for provenance) | 06 |
| `soft_sweep.py` | the SOFTSWEEP sweep (decode_soft vs direct_probe) | 05 |

## Requirements

- Python 3.12, numpy 2.5.3. No other dependency. No C kernel; BLAS threads are pinned to 4.
- `soft_sweep.py` additionally needs the `omni-ring` engine installed as an importable package
  (`pip install omni-ring`), because it imports `omni_ring.codebook`, `omni_ring.chain`,
  `omni_ring.resonator`, `omni_ring.crt` and `omni_ring.check`. The `ring1/` and `ring3/` scripts are
  self-contained — they only need numpy.

## How to re-run a number

Each runner prints its pre-registration criterion above its results, so the criterion travels with
the output. From the corpus root:

```
# RING-1 T4 (halo) — the full run is ~1,200 settles, 13-24 s on a 2019 laptop CPU
$ python3 harness/ring1/run_halo.py

# the quick smoke run (non-decisive; does not overwrite any report)
$ python3 harness/ring1/run_halo.py --quick

# verify-only: re-run the integrity gates without the sweep
$ python3 harness/ring1/run_halo.py --verify-only
```

The run logs that produced the appendix entries are verbatim copies of these scripts' output, kept
in `docs/appendix/` (for example `RING1-HALO.run.txt`).

## Provenance

- `ring1/` and `ring3/` come from the project's staging tree (`_Pads/RING/`); the library
  `ring1_core.py` is byte-identical to the version RING-1 CORE sealed, and the runners assert that
  identity rather than assuming it (see the "Integrity 1" block in `docs/09-ring1-halo-two-stage-chain.md`).
- `soft_sweep.py` comes from the `omniring-llm` research prototype (`bench/soft_sweep.py`). It is the
  rewritten harness; the invalid v1 harness (`soft_sweep.py.fleet-v1`) is not shipped, and no v1 number
  appears anywhere in this corpus.

## Licence

The harness is offered under the same licence as the engine it measures:

- **PolyForm Small Business License 1.0.0** — individuals and small businesses (fewer than 100 people,
  under about USD 1M revenue), for any purpose including commercial.
- **PolyForm Noncommercial 1.0.0** — anyone, for any noncommercial purpose.

Everyone else needs a separate commercial licence from the licensor named in the Required Notice. The
knowledge you compile with this software is not covered by these licences — see `DATA-AND-SHARDS.md`
in the engine release. The authors claim no patent and published the engine as prior art.
# AGENTS.md — omniring-research

For coding assistants (and people) setting this repository up. Plain steps; every command runs from the repo root.

## What it is
The research record behind OMNIRING, a memory that stores small structured records ("marks") in fixed-size high-dimensional vectors and reads them back by resonance. Its parts: These documents are the experiments and reviews that shaped the design. Most are pre-registered experiments: the pass/fail rule was written before any trial ran, and each document reports it word for word next to the result. Negative results (KILL) are published alongside positive ones.

## Install and check (3 commands)
```bash
git clone --depth 1 https://github.com/SovRing-Labs/omniring-research && cd omniring-research
python3 -m venv .venv && . .venv/bin/activate && python -m pip install -q numpy
python3 harness/ring1/run_halo.py --quick   # expect: VERDICT:
```
Needs: python3>=3.10, numpy.
Measured: 121.5s on a fresh clone (Intel i5-8365U laptop, 2026-10-16, exit 0).
Note: the --quick smoke run re-runs the RING-1 halo harness at reduced size and prints its pre-registered criterion and a VERDICT line (about 20 s); the decisive run is the same command without --quick.

## What the tests mean
`suite.json` lists every claim this repository makes with its verify command, the expected output, what passing means, how the number was obtained and how to use it in your own work (being written). `STATUS.md` says what works today, what is not yet tested and the known failures; the umbrella's `STATUS.md` has one row per repository.

## Where the evidence is
- `README.md`

- `CITATION.cff` — DOI 10.5281/zenodo.23354784

## Licence
CC BY 4.0.

## Guided setup through MCP
The SovRing umbrella ships an MCP server that explains, checks readiness, clones and runs these tests: https://github.com/SovRing-Labs/SovRing (README → "Paste this to your assistant"). Zero-install docs endpoint: https://gitmcp.io/SovRing-Labs/omniring-research

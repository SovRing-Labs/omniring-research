# AGENTS.md — omniring-research

For coding assistants (and people) setting this repository up. Plain steps; every command runs from the repo root.

**Status: pre-alpha, under development.** Interfaces, numbers and file layout can change without notice. Read `STATUS.md` first: what works today (each line names its test and evidence file), what is not yet tested, the known failures and the corrections.

## What it is
Public research corpus of the OMNIRING project: numbered disclosure chapters, pre-registered ring-resonator experiments (PASS and KILL both published) with their numpy harnesses and run logs, and a status disclosure that marks each later result Measured or NOT YET TESTED.

## Install and check (3 commands)
```bash
git clone --depth 1 https://github.com/SovRing-Labs/omniring-research && cd omniring-research
python3 -m venv .venv && . .venv/bin/activate && python -m pip install -q numpy
python3 harness/ring1/run_halo.py --quick   # expect: VERDICT:
```
Needs: python3>=3.10, numpy.
Whole suite instead: `bash install.sh --no-gui` (python check → venv → every runnable `suite.json` test, headless; without `--no-gui` it then opens the local results page on 127.0.0.1).
Measured: 121.5s on a fresh clone (Intel i5-8365U laptop, 2026-10-16, exit 0).
Note: the --quick smoke run re-runs the RING-1 halo harness at reduced size and prints its pre-registered criterion and a VERDICT line (about 20 s); the decisive run is the same command without --quick.

## What the tests mean
`suite.json` lists every claim this repository makes with its verify command, the expected output, what passing means, how the number was obtained and how to use it in your own work (17 tests, in `suite.json` at the repository root). `STATUS.md` says what works today, what is not yet tested and the known failures; the umbrella's `STATUS.md` has one row per repository.

## Where the evidence is
- `README.md`

- `CITATION.cff` — DOI 10.5281/zenodo.23354784

## Licence
CC BY 4.0.

## Guided setup through MCP
The SovRing umbrella ships an MCP server that explains, checks readiness, clones and runs these tests: https://github.com/SovRing-Labs/SovRing (README → "Paste this to your assistant"). Zero-install docs endpoint: https://gitmcp.io/SovRing-Labs/omniring-research

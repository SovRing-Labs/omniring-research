> **Status: under development — pre-alpha.** Interfaces, numbers and file layout can change without notice.

# omniring-research — status

Last checked: 2026-10-16, Linux laptop (Intel i5-8365U, 8 threads), on a clean copy of this repo. 11 of 17 suite tests work today; 16 of 17 can run without special hardware. Each line below names its test id in `suite.json` and the evidence file it rests on.
Quick test `python3 harness/ring1/run_halo.py --quick`: PASS (`VERDICT: KILL: the halo buys nothing. At M=32 Arm B's Wilson-99% lower bound (20.9%) does not exceed Arm A's point recall (33.3%), and Arm B does not match Arm A at half the iterations (medIt_B 5.0 vs medIt_A 2.0).`, fresh copy, empty HOME).


## Works today

- **R1** RING-1 core: clamping selects the cued mark out of a crowded slot (PASS) — PASS 2026-10-16 (`OK: VERDICT: PASS: clamping selects the cued mark out of a crowded slot (M=12, c=1, float, wilson-99 lower 58.`); evidence: `docs/appendix/RING1-CORE.run.txt`, `docs/01-ring1-core-cued-recall-and-capacity.md`, `harness/ring1/run_core.py`.
- **R2** RING-1 T3: the 17 check ring flags wrong settles (PASS on the load-bearing cell, KILL on other codebook seeds) — PASS 2026-10-16 (`OK: RING1-CHECK verdict, 936/944, 0/256`); evidence: `docs/appendix/RING1-CHECK.run.txt`, `docs/02-ring1-check-ring.md`, `harness/ring1/run_check.py`. Mixed result: The unguided (c = 0) cells collapsed at the pre-registered codebook seed, and the same grid on codebook seeds 1 and 2 is marked KILL in the robustness table (too few wrong settles to evaluate the criterion; the pooled flag rate there is not what passed). The document adds a publication note that this is the unguided seed lottery, a property of unguided factorisation and not of the check ring. The PASS is for the load-bearing cell M = 12, c = 1 and the pre-registered seed.
- **R3** RING-1: keyed direct storage reads exactly; a 1-bit tag lets two marks share a slot (PASS) — PASS 2026-10-16 (`OK: Direct float exact-decode: 1000/1000 = 100.0%  wilson-99 lower = 99.3%; tagged 2-mark (T + T.conj, c=0): b`); evidence: `docs/appendix/RING1-DIRECT.run.txt`, `docs/03-ring1-direct-keyed-storage.md`, `harness/ring1/run_direct.py`.
- **R8** RING-3: PEEL passes; DIAMOND, CORREL, TABU, FRET are KILLed — PASS 2026-10-16 (`OK: RING3 verdicts: 1 PASS, 4 KILL`); evidence: `docs/appendix/RING3-RESULTS.run.txt`, `docs/06-ring3-peel-diamond-correl-tabu-fret.md`, `harness/ring3/run_diamond2.py`, `harness/ring3/run_ring3.py`.
- **R9** RING-3b DIAMOND-2: smaller corners make the diamond readable (91%), residue corners do not — PASS 2026-10-16 (`OK: (a) category corners K=15 + checksum | 12 | 136/150 = 90.7% [82.7%, 95.2%] | 8/14 |; (b) residue corners (`); evidence: `docs/appendix/RING3b-DIAMOND2.run.txt`, `docs/06-ring3-peel-diamond-correl-tabu-fret.md`, `harness/ring3/run_diamond2.py`. Mixed result: The committed table also contains design (c) rows (105-value corners split into random category sub-rings: 7/150 = 4.7% at M = 12) that the shipped script version does not print on re-run; the script produces (a) and (b) only. Those (c) rows are therefore a recorded result from an earlier script state, not re-verified here.
- **P1** Dual-T50 cut read: ring tables equal Gomory-Hu on 105/105 pairs and 200/200 fields; hot clusters need the box read — PASS 2026-10-16 (`OK: 105/105, 17.2x, 200/200, hot cluster 85/100 ring-only, 100/100 with box`); evidence: `docs/appendix/part7/ch6-cuts/results/g5-t50-cuts.json`, `docs/31-dual-t50-cut-read-and-toroid-mailbox.md`, `harness/part7/ch2-cuts/g5_t50_cuts.py`, `harness/part7/ch2-cuts/g4_cuts.py`.
- **P2** Omni Web engine: test262 conformance run, 54.5% of executed tests — PASS 2026-10-16 (`OK: 29203/53614 pass_rate 0.5448; later 0.5685`); evidence: `docs/appendix/part7/ch3-test262/results/full.summary.txt`, `docs/appendix/part7/ch3-test262/results/baseline.json`, `docs/appendix/part7/ch3-test262/results/r2b.summary.txt`, `docs/33-omni-web-platform-census-orbit-and-merge-gate.md`, `harness/part7/ch3-test262/test262.py`.
- **P3** Omni Web 106-check JS probe and 13-check connectivity pass on eight engine builds (smoke test, not conformance) — PASS 2026-10-16 (`OK: 8 gates, 106/106 probe, 13 PASS lines of connectivity each`); evidence: `docs/appendix/part7/ch3-later-gates/results/gate-08/jsprobe.txt`, `docs/appendix/part7/ch3-later-gates/results/gate-08/conn.txt`, `docs/appendix/part7/ch3-later-gates/results/gate-08/binaries.txt`, `docs/33-omni-web-platform-census-orbit-and-merge-gate.md`, `harness/part7/ch3-merge-gate/merge-gate.sh`.
- **D1** Disclosure 45.1: exact residue-ring softmax and loss inside a ternary trainer, bit-identical on CPU and GPU — PASS 2026-10-16 (`OK: 45.1 numbers and the not-published caveat present`); evidence: `docs/45-status-disclosure-2026-10-14.md`.
- **D2** Disclosure 45.2: ring core in attention replaced by T50 / Armilla 3x3 / Cyclone routing (mixed: identity and guard hold, routing costs loss) — PASS 2026-10-16 (`OK: 45.2 numbers present`); evidence: `docs/45-status-disclosure-2026-10-14.md`.
- **D4** Disclosure 45.7: dispatch that stops instead of failing over loses 0 productive dispatches on a 7-day replay — PASS 2026-10-16 (`OK: 45.7 replay numbers present`); evidence: `docs/45-status-disclosure-2026-10-14.md`.

## Not yet tested

- Every suite row ran on the test laptop.

## Known failures and honest negatives

- **R4** RING-1: dispersing marks over many slots does not beat one crowded slot (KILL). Measured for this resonator, D = 5120, unguided probing of every dispersed slot; it does not show dispersal is useless for other readouts or larger D. The wall time (about 227 s on the laptop) is close to the five-minute budget; a loaded host takes far longer. Recorded and re-checked 2026-10-16 (PASS); evidence: `docs/appendix/RING1-DISPERSE.run.txt`, `docs/04-ring1-disperse.md`, `harness/ring1/run_disperse.py`
- **R5** RING-1 T4: a two-stage halo chain ties one resonator and costs 2.5x the iterations (KILL). Tested at this crowding and dimension only; the document records that the two arms fail on different trials (A-only 44, B-only 46), which leaves open an ensemble reading that this test does not evaluate. Recorded and re-checked 2026-10-16 (PASS); evidence: `docs/appendix/RING1-HALO.run.txt`, `docs/09-ring1-halo-two-stage-chain.md`, `harness/ring1/run_halo.py`
- **R6** RING-1 T2: a smooth fractional-phase ring breaks recall when it is bound into every mark (KILL); the cued form works. The KILL is pre-registered and stands as written; the document's own correction says the cue form works. The committed log gives no wall time; the runtime_s here (412 s) was measured on an 8-core host at load average about 30, so an idle host should be faster. Recorded and re-checked 2026-10-16 (PASS); evidence: `docs/appendix/RING1-SMOOTH.run.txt`, `docs/10-ring1-smooth-fractional-phase.md`, `harness/ring1/run_smooth.py`
- **R7** SOFTSWEEP: decode_soft never answers silently wrong, but the registered bar was unattainable (KILL on half 1, half 2 passes). Unguided ds@ rows ran at codebook seed 0, which happens to be a good draw; at seeds 42 and 21 unguided decoding returned 0/20 correct (all abstained, 0 silent-wrong). Unguided decode is a seed lottery (the document's correction at the top, with the 15/15 vs 1/15 figures in doc 06). The cued (clamp-13) arm is the robust one: 294/300 at k = 5. The registered half 1 fails by construction, not by evidence of silent errors. Not re-run here (external); evidence: `docs/05-ring1-softsweep-decode-soft.md`, `harness/soft_sweep.py`, `harness/README.md`
- **D3** Disclosure 45.3: cyclone MLP slot-cores do NOT beat the dense trunk (negative result). Not independently reproducible from this repository. One model size, one 18-minute budget per arm: the disclosure says 'at this size', and larger or longer runs are not measured. Recorded and re-checked 2026-10-16 (PASS); evidence: `docs/45-status-disclosure-2026-10-14.md`
- **D5** Disclosure 45.8: speech core in exact forms is design only (NOT YET TESTED). No measurement of the proposed core exists. The 1.1 s figure belongs to whisper.cpp, not to the described design. Recorded and re-checked 2026-10-16 (PASS); evidence: `docs/45-status-disclosure-2026-10-14.md`

## Corrections

- **C01** — MEM-0 residue addressing: the address arm of the 10-01 run stored 1,365 items, not 1,000,000. Closed by later measurement (recall 1.000 at 1,000,000 and at 1,000,000,000 stored items); the published sentence needs only the corrected ratios (Part 5, disclosure 5).
- **C06** — LAYER-0 "the full 10^11 range 1.000": retest found the sentence accurate (keys drawn from the full range, failures disclosed in the same paragraph). No erratum.
- **C07** — MATPLATE hard CRT 0.043 → 0.042 (rounding); folded into the next version.
- **C09** — Doctor 565 → 24 defects (docs/36): reproduced exactly; a second counter reads a different baseline, to be explained before both are quoted.
- **C12** — docs/45: upstream llama.cpp also builds BitNet's FFN with SiLU while the weights expect ReLU²; upstream perplexity not yet measured (addition pending).

## How to re-check

- One file, any python3 >= 3.8: download [`sovring-suite.pyz`](https://github.com/SovRing-Labs/SovRing/releases/latest/download/sovring-suite.pyz), then `python3 sovring-suite.pyz --run omniring-research` (headless) or `python3 sovring-suite.pyz` (local page on 127.0.0.1).
- From this checkout: `bash install.sh` (checks python, prepares a venv, runs the suite headless, then opens the page; `--no-gui` to skip the page).
- Quick test only: `python3 harness/ring1/ring1_core.py --selftest`.

## Defensive publication

- `docs/disclosures/CYCLONE-TRAINER-TECHNICAL-DISCLOSURE.md` — on public GitHub since 2026-10-14
- `docs/disclosures/DOCK-TECHNICAL-DISCLOSURE.md` — on public GitHub since 2026-10-10
- `docs/disclosures/OMNI-RENDER-TECHNICAL-DISCLOSURE-PART-6.md` — on public GitHub since 2026-10-10
- `docs/disclosures/OMNI-RING-TECHNICAL-DISCLOSURE-PART-3.md` — on public GitHub since 2026-10-10
- `docs/disclosures/OMNI-RING-TECHNICAL-DISCLOSURE-PART-4.md` — on public GitHub since 2026-10-10
- `docs/disclosures/OMNI-RING-TECHNICAL-DISCLOSURE-PART-5.md` — on public GitHub since 2026-10-10
- `docs/disclosures/OMNI-RING-TECHNICAL-DISCLOSURE-PART-7.md` — on public GitHub since 2026-10-10
- `docs/disclosures/OMNID-TECHNICAL-DISCLOSURE.md` — on public GitHub since 2026-10-10
- `docs/disclosures/THEAD-SUPERSEED-TECHNICAL-DISCLOSURE.md` — on public GitHub since 2026-10-14
- `docs/45-status-disclosure-2026-10-14.md` — on public GitHub since 2026-10-14
- DOI: [10.5281/zenodo.23354784](https://doi.org/10.5281/zenodo.23354784) (Zenodo, see `CITATION.cff`)
- Licence: Documents: CC BY 4.0 (LICENSE.md). Harness: PolyForm Small Business 1.0.0 / PolyForm Noncommercial 1.0.0 (harness/LICENSE.md).

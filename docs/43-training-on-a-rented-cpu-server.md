# Training on a rented CPU server: parallel day merge, throughput by model size, a negative native build, and a shared-RAM bus

| | |
|---|---|
| **Date** | 2026-10-08 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). The author reviews each document before publication. |
| **Type** | measured result (16- and 32-vCPU servers) |
| **Verdict** | Parallel day merge works (copy gate 0.841, bar 0.85 NOT met); native AVX-512 build NO GAIN on an idle server; bus coordinator 4 / 4 |
| **Code** | `harness/part7/ch1-cpu-server/`, `harness/part7/ch1-live-school/par_merge.py` |

The author on 7 October: *"what if we did the node train method where the three/however many parralell harnesses all train the same core"* — and, watching the server, *"i've still a big feeling that the ram is being underutilized, lets really brainstorm, what are all the strange, useful, novel uses for ram, what could it be used for while we train?"* This document is the server work those two questions produced.

*The record below is the full measured account from the technical disclosure's working chapters: every gate, every failure, with the
harness and result paths in this repository. "Section n" and "§n" inside it refer to the sections of that chapter; the matching documents here
are listed in the README. "Recorded; no saved result" marks a figure the project recorded whose output file is not published.*

## Training on a rented CPU server: parallel day merge, throughput, a negative native-build result, a shared-RAM bus

Description. A one-command kit (the scripts `thead-pod`, `make-kit.sh` and `install.sh`, not shipped in this tree) stands up a server with the trainer, the dock, builds,
checkpoint and smoke gates. **Parallel day training** (`harness/part7/ch1-cpu-server/school-parallel.sh`, `harness/part7/ch1-live-school/par_merge.py`): N harnesses train one core; weights
are averaged at each day end (the optimiser moments stay local: checkpoints hold weights only, so restarting per merge would reset them). **Shared-RAM
bus** (`harness/part7/ch1-cpu-server/bus_coord.py`; the design note is not shipped): harnesses write weight slabs to memory-mapped files; a coordinator keeps the mean of the
healthy slabs and a coupling K = clamp(C g / (2 S_tol), K_min, 1) from the measured drift g (a phase-locking rule: lock needs K >= half the
detuning); a harness is dropped when its loss leaves the median band (> 6 robust deviations), its slab holds NaN or Inf, its drift exceeds 4x
the median, or its residue check fails (sum of the slab's 32-bit words mod three primes: detects a torn write, does not authenticate).

Measured gates.
- G1: one harness, pre-K v5 (5x rows per level; the build's manifest sums to 63,160 rows), 16 threads, warm start from the server's v4 core: 732 steps / 37
  days in 980 s (16 min): copy gate 0.798 (recomputed from `docs/appendix/part7/ch1-cpu-server/results/pod-20261008/school-t25-prek5-cloud-s6400/probes/tier1_eval.json`
  with `harness/part7/ch1-live-school/tier1_gate.py`), held-out 0.653, canary 0.789 (`docs/appendix/part7/ch1-cpu-server/results/pod-20261008/school-cloud-v5.log`); the v4 core it started from scored 0.663 on the same gate (recomputed from
  `docs/appendix/part7/ch1-cpu-server/results/pod-20261008/school-t25-prek-cloud1/probes/tier1_eval.json`), the laptop ladder 0.627. The gold replay of the v5 build (62,138 rows, 0 mismatches, 0 unsolved) is recorded only in the project's test index (not shipped) (recorded; no saved result).
- G2: four harnesses x 4 threads from the same warm start, day merge, seeds 6500-6800: 44 min 45 s (pod clock 01:45:08 to 02:29:53), 37 merges each (spread
  0.0009 RMS at day 1, 0.0069-0.0070 at days 33-37; 0.10-0.30 s per merge): copy gate 0.841 (recomputed from `docs/appendix/part7/ch1-cpu-server/results/pod-20261008/par-v5/h0/probes/tier1_eval.json`; bar
  0.85, NOT met), held-out 0.624, canary 0.498 at day 37 (0.638 / 0.749 at day 30; the single harness had 0.669 / 0.837 at day 30) (`docs/appendix/part7/ch1-cpu-server/results/pod-20261008/school-parallel.log`,
  `docs/appendix/part7/ch1-cpu-server/results/pod-20261008/par-v5/merge/merge.log`). The single-harness comparison ran 16 min on a different seed (6400), an equal-wall-clock single run was NOT run, so the gain
  may be wall-clock, not parallelism. (harness `harness/part7/ch1-cpu-server/school-parallel.sh`, `harness/part7/ch1-live-school/par_merge.py`)
- G3: server vs laptop: wake throughput 1,815-1,851 tokens/s on the server (`docs/appendix/part7/ch1-cpu-server/results/pod-20261008/school-cloud.log`, steps 25-75) against 134-136 on the laptop under load 14
  (`docs/appendix/part7/ch1-prek-t25/results/laptop-ladder-log-extract.txt`; later laptop segments 158-382, same file); the same 146-step ladder in 225 s (3 min 44 s by the pod clock). Trainer throughput by
  size on the server (raw steps, school switches, 8 threads beside other work): 6.9 M parameters 2,391 tokens/s (0.857 s per step), 29.7 M 629 (3.256 s), 91.9 M 262
  (7.822 s), 1,061 h per billion tokens at 91.9 M; float32 reference models measured in the same file: 52.5 M 1,588 tokens/s, 111.8 M 600, 97.6 M 642 (harness
  `harness/part7/ch1-cpu-server/ternary_size_bench.py`; result `docs/appendix/part7/ch1-cpu-server/results/pod-20261008/size-bench/results.jsonl`).
- G4 (negative): a native AVX-512 build of the engine beat the shipped AVX2 library 5.2x on the LUT5 forward kernel under contention
  (0.868 -> 0.168 s) but not on an idle server: whole step 1.995 s shipped vs 2.024 s native, kernel 0.124 vs 0.119 s: NO GAIN, the 5.2x was
  contention noise; the shipped library stays. (harness `harness/part7/ch1-cpu-server/{native-lib-probe.sh, idle-window.sh}`; the values are recorded only in the project's test index, not shipped) (partial)
 
- G5: shared-RAM bus coordinator: 4 / 4 tests pass (exact mean; NaN, loss outlier, drift outlier, torn write each dropped with the mean
  unaffected; K rises with drift); the tests (`harness/part7/ch1-cpu-server/test_bus_coord.py`, coordinator `harness/part7/ch1-cpu-server/bus_coord.py`) were re-run from the source files on 2026-10-09 with the stock interpreter: 4 / 4 (the test's
  relative import path points at a directory that does not hold the module in the shipped layout; run it with `harness/part7/ch1-cpu-server/` on the path).
- G6: bus pull with K = 1 equals the day-merge checkpoint bitwise; K = 0.5 is exact only on non-BitLinear parameters (BitLinear latents are
  re-snapped to trits after every merge or pull, so the formula check cannot hold on them: 4,718,592 BitLinear entries, 310,143 changed by the
  re-snap in the K = 0.5 arm) (`docs/appendix/part7/ch1-cpu-server/results/bus/verdict.json`: Q equals P true, P equals M false, R
  formula exact false, non-BitLinear rechecks true; harness `harness/part7/ch1-cpu-server/bus_gate.sh`). Note: the harness run itself exited 1 (launch record, `docs/appendix/part7/ch1-cpu-server/results/launch-records-summary.json`); the `pass: true` in the JSON comes from a re-check restricted to the non-BitLinear parameters, added after the first
  result.

FIELD PREDICTS: local-update workers with periodic averaging approach single-worker quality at equal total compute (local SGD, Stich, ICLR 2019;
federated averaging, McMahan et al., AISTATS 2017; DiLoCo, Douillard et al., 2023); phase locking requires coupling at least half the frequency
detuning (Adler, Proc. IRE 1946); a kernel bound by memory traffic does not speed up with wider vectors (roofline model, Williams, Waterman and
Patterson, CACM 2009) - which is what the idle-server result shows.

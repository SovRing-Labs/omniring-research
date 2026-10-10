# Pre-K arms on the T25-core model: plates, ring heads, integer backward, T25 pages, and babbling lessons

| | |
|---|---|
| **Date** | 2026-10-07 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). The author reviews each document before publication. |
| **Type** | single-seed arms on the laptop (20-minute cap per arm) |
| **Verdict** | Plates attention kept (about twice the noise floor); ring head, event fields, integer backward and T25-addressed pages KILL or OFF; the pre-K ladder finished |
| **Code** | `harness/part7/ch1-prek-t25/` |

A fresh T25-core model on pre-K, a light day, one seed per arm on a shared laptop: each switch tested alone against the base. The author's question that started the babbling lessons, on 5 October: *"how can we use elementary school to get the model aquainted with it's "body" and get it used to the arc reactor?"*

*The record below is the full measured account from the technical disclosure's working chapters: every gate, every failure, with the
harness and result paths in this repository. "Section n" and "§n" inside it refer to the sections of that chapter; the matching documents here
are listed in the README. "Recorded; no saved result" marks a figure the project recorded whose output file is not published.*

## Pre-K arms on the T25-core model, 2026-10-07 (harness `harness/part7/ch1-prek-t25/`)

Description. A fresh T25-core model on pre-K v3 (seed 6100), a light day, hard 20-minute cap per arm, one seed per arm, a shared box (load
11-17). Switches tested one at a time against `base`: plates attention (dense inside a row plus page plates for older rows; fast row-block
kernel), a ring head on the T25 token rings, event fields (provenance + stage), integer backward (int8 error through the forward's lookup kernel,
ternarised weight gradient, optional integer flip counters), T25-addressed pages (`PLATE_PAGE`: plate page = the core's residues on rings 5 x 31,
155 pages, instead of the LSH hash), P3 (backward skips rows the model already predicts with p > 0.95, full step every 4 as a forgetting guard)
and P2 (no local read-out on a confirmed row). Pre-K "babbling" lessons: `pk.babble`, `pk.predict`, `pk.goal`, `pk.same` over a 9-operator
equation alphabet (ADD SUB MUL MIN MAX NEG EQ LT, EVAL) on the 32-operand ring, executed exactly by twin state machines (Python and Rust).

Measured gates (held-out loss, answer loss, canary loss; lower is better; one run per arm).
- G1: day 1 base 3.066 / 6.300 / 4.077; day 2: base 1.931 / 2.257 / 2.605; plates 1.618 / 1.640 / 2.689 (held-out -0.313, answer -0.617); platesfast
  (same math, fast kernel) 1.762 / 1.914 / 2.864. The platesfast-versus-plates spread on identical math (day 2: 0.144 held-out, 0.274 answer, 0.175 canary;
  day 1: 0.007 held-out) is the run-to-run noise floor, so the plates win is about twice the noise on n = 1 per arm.
  (`docs/appendix/part7/ch1-prek-t25/results/rx-{base,plates,platesfast}/state.json`; harness `harness/part7/ch1-prek-t25/{rx-run.sh, rx-chain.sh, rx-chain2.sh, rx-chain3.sh, rx_report.py}`)
- G2 (negative): ring head KILL (day 2: 3.569 / 4.361 / 5.063 vs base 1.931 / 2.257 / 2.605); event fields neutral to worse (day 1 3.124 / 6.589 / 4.168
  vs base 3.066 / 6.300 / 4.077); integer backward worse (day 1 3.384 / 7.057 / 4.289 with flip counters, 3.202 / 6.784 / 4.216 without); all stay OFF
  (`docs/appendix/part7/ch1-prek-t25/results/rx-{head,fields,intbwd,intbwd0}/state.json`). That integer backward is no faster on this AVX2 CPU without VNNI (dx 0.405 vs 0.525 s, dW
  0.728 vs 0.596 s) is in a private exploration log only (not shipped) (partial).
- G3: T25-addressed pages: day 2 answer loss 0.676 (base 2.257, plates 1.640) but canary 3.020 (base 2.605); days 3-4 resumed: at day 4 held-out +0.114,
  canary +0.560 and answer -0.180 against platesfast (`docs/appendix/part7/ch1-prek-t25/results/rx-t25page-d34/state.json` 1.311 / 0.221 / 2.688 against `docs/appendix/part7/ch1-prek-t25/results/rx-platesfast-d34/state.json` 1.197 / 0.401 / 2.128; the day-2 value is in `docs/appendix/part7/ch1-prek-t25/results/rx-t25page/state.json`). The canary did
  not recover: PLATE_PAGE stays OFF. (script `harness/part7/ch1-prek-t25/rx-days34.sh`; the two chain launches exit 0, `docs/appendix/part7/ch1-prek-t25/results/launch-records-summary.json`)
- G4: fast plates kernel equals the masked reference (loss difference 9e-6, gradient cosine 1.0000), attention 0.521 -> 0.062 s (8.4x), step
  2.02 -> 1.44 s (-29 %) (harness `harness/part7/ch1-prek-t25/segfast_check.py`; its output is not saved) (partial)
- G5: P3/P2 correctness: dropped share of rows 0.287; compacted backward equals the masked reference to max abs 2.42e-8 (gradient max abs
  0.373); loss equal; timings off 11,265.7 ms, compacted 8,224.4 ms, mask-only 4,569.1 ms under load 14, so the timing is unreadable (the
  plan reads the structural saving: 28.7 % of BitLinear backward rows) (harness `harness/part7/ch1-prek-t25/p3_check.py`, result
  `docs/appendix/part7/ch1-prek-t25/results/p3_check.p3b.json`). "Off equals the previous engine bit-identically on 52 parameters" is in the log, not in that JSON (partial)
 
- G6: holographic transition plate decoded by growing ring systems (D 1,024, 16 phases, recall of the next state, T = transitions per plate;
  harness `harness/part7/ch1-prek-t25/holo_tier_probe.py`, re-run from the harness source on 2026-10-09 with the stock Python/numpy, 5 s; no result file is stored):
  T5 flat 1.0 / .906 / .375 / .297 / .135 at T = 16 / 32 / 48 / 64 / 96; T10 flat 1.0 / 1.0 / .812 / .781 / .479; T10 simplex 1.0 / 1.0 / .979 /
  .891 / .552; T25 flat 1.0 / 1.0 / .979 / .891 / .677; T25 simplex 1.0 / 1.0 / .979 / .969 / .667; at T = 144 (overloaded) T5 .049 / .069, T10 .16 /
  .278, T25 .271 / .382 (flat / simplex). The project's earlier log (not shipped) of the same probe differs by at most 0.016 (T10 flat T = 64 .766, T10 simplex T = 96 .562). The
  earlier log's summary ("T25 about 2x T5 and 1.5x T10 at >= 0.97") is a reading of this table that holds for FLAT codebooks only: at >= 0.97 flat T5
  holds 16 transitions, T10 32, T25 48 (1 : 2 : 3 on this grid). For simplex codebooks T10 and T25 both hold 48 (T25 .969 at 64 vs T10 .891; .667
  vs .552 at 96), so T25's lead over T10 shows from T = 64 up, not at the 0.97 line. Only the plate recall is measured, not model quality.
- G7: babbling lessons. Held-out top-1 on the `pk.babble` operator class 0.226 -> 0.637, its state class 0.179 -> 1.000, and the `pk.predict` operand
  0.072 -> 0.225, from the first 20-minute repeat to the end of the pre-K ladder (`docs/appendix/part7/ch1-prek-t25/results/school-t25-prek-1/probes/tier1_eval.json` and
  `docs/appendix/part7/ch1-prek-t25/results/school-t25-prek-ladder/probes/seg-2.json`, which is byte-identical to the ladder's own `tier1_eval.json`; the first repeat's absolute operator value 0.226 and the ladder's 0.637 are values of one metric on two
  models; act-observe is learned fast, computing forward in the head is the slow skill). Recorded only in a private plan and a private design note (not shipped): 8,000 gold episodes all solve; twin
  state machines agree on 100,000 random programs (68,423 with a meet-plate offer, 14,855 valid EVALs), 0 mismatches; replay of all three pre-K v4 builds
  0 offer mismatches, 0 unsolved (the `omni-render` binary that runs `body-selftest` / `t1-replay` and the result logs are not shipped) (recorded; no saved result).
- G8: pre-K ladder of 146 steps (5 passes) finished (`docs/appendix/part7/ch1-prek-t25/results/school-t25-prek-ladder/`): copy gate 0.537 -> 0.593 -> 0.627 at the segment ends (0.593 and
  0.627 recomputed from `docs/appendix/part7/ch1-prek-t25/results/school-t25-prek-ladder/probes/seg-1.json` and `seg-2.json` with `harness/part7/ch1-live-school/tier1_gate.py`; 0.537 from the copy-gate line of the laptop ladder log, `docs/appendix/part7/ch1-prek-t25/results/laptop-ladder-log-extract.txt`), held-out
  loss 0.868 at step 146 (`docs/appendix/part7/ch1-prek-t25/results/school-t25-prek-ladder/state.json`), doing solved 48 / 186 at segment 1 and 56 / 204 at the end; P3 from day 4. Three 20-minute repeats before it (a fresh
  model, then warm twice): copy gate 0.367 -> 0.445 -> 0.501 as logged - the first two over 5,107 positions including the `pk.meet` drafts (40 % random by design),
  the third over 4,555 positions without them. On one definition, recomputed from each repeat's `probes/tier1_eval.json`: without `pk.meet` 0.396 / 0.482 /
  0.501, with it 0.367 / 0.445 / 0.473; the ladder end is 0.627 without and 0.607 with. The repeats restarted at pass 1 (fixed by continuing the ladder). The
  plan's reading of four saved evals - under-trained, not stuck: every learnable class still rising, flat classes unpredictable by design - is analysis, not a
  measured gate. (harness `harness/part7/ch1-prek-t25/{school-t25.sh, school-t25-ladder.sh}`; the repeats' `tier1_eval.json` files are `docs/appendix/part7/ch1-prek-t25/results/school-t25-prek-{1,2,3}/probes/tier1_eval.json`; the logged values come from the project's test index and launch logs, which are not shipped) 
- G9: T25 core in the model: a fresh model's held-out loss 8.709 at step 0 and a day-1 wake loss of 1.985 (`docs/appendix/part7/ch1-prek-t25/results/rx-base/state.json`). Recorded
  only in a private plan (not shipped): core off equals the previous engine bit-identically; a rendered 1,209-byte x86 kernel; addresses equal the scalar model on 0 / 128
  mismatches in forward and decoder; one kernel call per batch costs nothing measurable (forward 95-112 ms off vs 97-101 ms on) (the T25-core status log of the earlier trial-model plan; the check needs the runtime binary, not shipped) (recorded; no saved result).

Failures disclosed: a consistent-phase variant of the harmony measure was tried and REJECTED (core off bit-identical, decode equals forward, but
block-0 order parameter unchanged 0.896 -> 0.897 and blocks 2-5 lower; diff kept); the HOLO plate read is live but its net loss effect is about 0
(mem on vs off changes 199 of 256 token losses, net -0.0002 / +0.0009); proposed A/B arms for study length and amplification were NOT run because
saved results already answered them.

FIELD PREDICTS: block-local attention with summary memory behaves like Longformer (Beltagy et al., 2020) and Transformer-XL (Dai et al., ACL 2019);
ternarised gradients converge with a small accuracy cost (TernGrad, Wen et al., NeurIPS 2017); skipping examples the model already fits saves
compute with little loss (selective backprop, Jiang et al., 2019; token selection, Rho-1, Lin et al., NeurIPS 2024); goal babbling (Rolf and Steil,
2010) learns the forward map from self-generated acts; the capacity of a superposed plate falls as items are added and grows with dimension
(holographic reduced representations, Plate, IEEE TNN 1995; hyperdimensional computing, Kanerva, Cognitive Computation 2009), and a residue number
system reads out in sum-of-moduli probes (Szabo and Tanaka, 1967) - the measured T5 < T10 < T25 order is the predicted one.

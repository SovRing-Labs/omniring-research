# The 2^31-byte probe: 40 models in one session refused, a group of 20 misses its bar (PROBE-2G31)

| | |
|---|---|
| **Date** | 2026-10-09 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). The author reviews each document before publication. |
| **Type** | pre-registered probe on a rented A40 (48 GB) |
| **Verdict** | Arm A refused at build (not mis-trained); arm B no result; arm C trains but **FAILS the registered 2 % bar** |
| **Code** | `harness/part7/ch1-array/probe_arms.sh`, `probe_c.sh`; pre-registration `docs/appendix/part7/ch1-array/prereg/probe-2g31.md`; records `docs/appendix/part7/ch1-array/results/probe-2g31/` |

## Why
The author's array is *"a 50t center, with 8 harnesses around it a model tied to each"*, five units, 40 models. The first two 40-model
sessions trained nothing (held-out stayed near 9 while the CPU engines reached 3–4) and raised no error. During the growth run a guard was
added to the program builder: on this GPU a storage binding of 2^31 bytes or more "trains NOTHING, silently", so it now raises an error.
Question: is the guard the whole story, and does the real group shape (20 models) train?

## Gate decision (the author, 2026-10-09)
The registered 2 % verdict stays **FAIL** and is not moved after the fact. For the next run a gate relative to the CPU engine's own
noise is registered: (a) mean per-harness gap ≤ 2.01 % (the CPU-against-CPU mean, doc 28); (b) no harness above 3.99 %; (c) no one-sided
skew — a two-sided sign test does not reject at 5 %. Arm C fails all three (mean 4.1 %; max 9.7 %; 16 of 20 worse, p = 0.012). The new gate
was written after this result, so only a run registered before it starts can pass it, and a CPU-against-CPU baseline for the same 20
harnesses is measured first.

*The record below is the full measured account from the technical disclosure's working chapters: every gate, every failure, with the
harness and result paths in this repository. "Section n" and "§n" inside it refer to the sections of that chapter; the matching documents here
are listed in the README. "Recorded; no saved result" marks a figure the project recorded whose output file is not published.*

### School-size tests on the A40
- *8 models in one step* (no school switches; `docs/appendix/part7/ch2-train/results/cyclone/c2-s2/s2-replica-school-R8-a40.json`, 20 steps): 2.78 GB resident, **517.8 ms per step against 1,238.2 ms per model
  on the CPU engine** (4 threads; the 8 models were run in turn, so 9,906 ms for the unit), each replica bit-identical to its solo GPU run (0 differing
  words in all 8), held-out within 0.016 % of the CPU engine; one model alone 95.2 ms, so the 8-model step is 1.47x faster than 8 single-model steps (31.6 k
  against 21.5 k tokens/s).
- *The centre form, 8 models* (`docs/appendix/part7/ch2-train/results/cyclone/m1/m1-school-R8-a40.json`, 30 steps): pull 519.4 ms and centre 521.0 ms per unit step at
  2.78 and 3.03 GB, against **6,591 ms per unit step on the CPU: 12.65x** (the "12.6x"). **The denominators do not reconcile:** the CPU time of the replica gate is 1,238.2
  ms per model (4 threads, one model at a time; 8 x 1,238.2 = 9,906 ms would give 19.1x against 517.8 ms), the CPU time of this gate is 6,591 ms for 8 engines
  in turn plus the coordinator's float64 mean and pull in numpy (`harness/part7/ch2-train/train/s3_centre.py` sets no thread count: the engine's default), measured on another run; a
  repeat of this gate (with the attention-GEMM change below) measured 6,858 ms; and the same school-size engine step measured 734 ms on the L4 pod's host (section 10.2). The records
  do not state the pod's core count, so the three CPU baselines (734, 1,238 and 824 ms = 6,591 / 8 per model) cannot be reduced to one; read each ratio
  against its own record only.
- *Later change, attention products as batched GEMMs* (default on after the centre-form gate passed; `docs/appendix/part7/ch2-train/results/cyclone/m1-attngemm/m1-school-R8-a40.json`): 223.2 ms (pull) and
  223.9 ms (centre) per unit step against 6,858 ms on the CPU in that run (30.6x); held-out within 0.046 % (pull) and 0.051 % (centre) of the CPU engines. The
  change is **not bit-identical** to the fold form it replaced (`docs/appendix/part7/ch2-train/results/cyclone/g3b/s6-attn-gemm-school-U1x8-a40-nosw.json`: 24 loss words and 61,083,507 weight words differ,
  largest relative loss difference 1.7e-4, largest weight difference 0.011; 520.0 against 223.2 ms, 2.33x; the record's bit-identity `pass` is false), so it
  is judged by the learning gates. Tensor-core GEMMs (`docs/appendix/part7/ch2-train/results/cyclone/g3b/s6-omni_train_hgemm-0-bl-school-U1x8-a40.json` and `docs/appendix/part7/ch2-train/results/cyclone/g3b/s6-omni_train_hgemm-0-all-school-U1x8-a40.json`): the BitLinear-forward form (int8 x trits) is
  bit-identical (0 differing words) and **no faster (496.2 against 489.9 ms, 1.01x)**; the all-GEMMs form is not bit-identical (largest relative loss difference
  2.35 %, 62,249,243 weight words differ) and gains 1.07x (495.4 against 462.5 ms): both stay off by default.
- *Unit with every school switch* (`docs/appendix/part7/ch2-train/results/cyclone/g3b/g3b2-school-R8-a40.json`, 8 models, 30 steps): learns (loss about 9.0 to 1.8-2.2 for
  both), GPU 1,190.7 ms per unit step against 8,836.5 ms on the CPU (7.4x), 3.39 GB; but the per-harness held-out gaps against the CPU engine are 0.0, 1.2, 1.2,
  1.4, 2.2, 3.2, 4.0 and **6.0 %** (mean 2.4 %, four of eight above 2 %), and the record's `pass` is false against the 2 % bar. **The CPU engine differs from
  itself by up to 4.0 % per harness** between 4 and 2 threads with the same switches (`docs/appendix/part7/ch2-train/results/cyclone/g3b/g3b2-cpu-noise-school-R8.json`: 0.4 to 4.0 %, mean 2.0 %; the two
  CPU runs' losses split at steps 4 to 8), so a 2 % per-harness bar is tighter than the engine reproduces itself. Gate decision (2026-10-09): the registered 2 % verdict stays FAIL; the next run is judged against the CPU-versus-CPU noise baseline instead (chapter 1, section 11, G4).
  **Discrepancy:** an unpublished note gives the mean gap as 0.24 %; the file gives 2.4 % (the signed mean is +0.29 %).
- *The array at small and mid sizes* (`harness/part7/ch2-train/train/s5_array.py`, results in `docs/appendix/part7/ch2-train/results/cyclone/g3b/` (the `g3b3-*` files)): small model, 2
  units x 2 (4 models, no ring, no switches): the array's per-step losses and final weights equal two separate one-unit runs, 0 mismatched words; small
  model, 5 units x 2 with the ring (10 models): held-out within 0.03 % of the CPU reference; **school size, 5 units x 2 with the ring and every switch
  (`docs/appendix/part7/ch2-train/results/cyclone/g3b/g3b3-school-U5x2-ring-sw-a40.json`, 10 models, 3 steps): 4.35 GB, 1,487 ms per array step against 13,761 ms on the CPU (9.3x), held-out gap 1.69 % at most**
  (within 2 %; the record's `pass` is false because the harness's "loss falling" test compares the last three steps with the first three of a 3-step run, i.e. the
  same steps; a gate artefact, not a held-out failure). That the small-size equality also holds with the school switches on is stated in an unpublished note only
  (recorded; no saved result).
- ***The 5 x 8 array (40 models) in one session: two attempts trained nothing, and the planner now refuses it.*** Two records of a 40-model school-size run exist
  (`docs/appendix/part7/ch2-train/results/cyclone/g3b/g3b3-school-U5x8-a40.json`: no ring, no switches, 3 steps, 15.1 GB resident, 2,668 ms per array step against 35,828 ms on the CPU; and
  `docs/appendix/part7/ch2-train/results/cyclone/g3b/g3b3-school-U5x8-ring-sw-a40.json`: ring and every switch, 8 steps, 17.0 GB, 6,181 ms against 51,137 ms): in both the GPU training loss stayed at 8.9-9.2
  from the first to the last step while the CPU reference learned (held-out 3.0-3.9 for the CPU, 8.6-9.0 for the GPU in the second; gap up to 68 % and 192 %); the timings
  are the cost of a run that learned nothing and are not a speed result. (The second record is saved twice, once under a name that says "one arena 10.9 GiB"; the two files are byte-identical and only one is shipped.)
  The explanation recorded in an unpublished note was that the transient arena was one 10.9 GiB allocation above the device's maximum allocation size, so arenas were capped at 3.5
  GiB (partial). **The cap did not make 40 models
  trainable in one session, and the record explains why (probe, below).**
- ***The 2^31-byte probe, as measured*** (`harness/part7/ch2-train/train/s5_array.py` `--dims school --units 5 --per 8 --ring --steps 6 --device A40` (arms A and B) and `--per 4` (arm C), with the
  twelve school switches, launched by `harness/part7/ch2-train/probe-2g31/probe_arms.sh` and `harness/part7/ch2-train/probe-2g31/probe_c.sh`; results: `docs/appendix/part7/ch2-train/results/probe-2g31/g3b3-school-U5x4-ring-sw-a40.json` and the summary `docs/appendix/part7/ch2-train/results/probe-2g31/arms-summary.json`, which carries the facts of the raw pod logs (the same logs are shipped in chapter 1, `docs/appendix/part7/ch1-array/results/probe-2g31/pod/`)). A guard in the program builder
  (`harness/part7/ch2-train/gen/train_step.py`, lines 21-73, added on 2026-10-09 at 01:48) documents that **on the A40 a storage binding of
  2^31 bytes or more trained nothing, silently**, with the sweep observation "R = 30 (logits buffer 2.01 GB) learns, R = 32 (exactly 2^31 bytes) does not", and now raises an
  error instead. The sweep's result files are not among the shipped files (recorded; no saved result); the logits-buffer arithmetic is exact: R x 4 x 512 x 8,192 x 4
  bytes = 2,013,265,920 for R = 30, 2,147,483,648 for R = 32, 2,684,354,560 for R = 40.
  - *Arm A, one session of 40 (5 units x 8): refused.* The arm's log (summarised in the arms summary named above) ends in the guard's error: "buffer(s) over one storage binding (2147483647 bytes):
    [('L_rtlg_0', 2684354560), ('L_rtlg_1', 2684354560), ('L_rtlg_2', 2684354560)] - fewer models per session (array server --group)": three logits buffers of
    2.5 GiB. It is an explicit refusal at build time, **not a silent mis-train**; the default arena cap (3.5 GiB) was in force. The arm took 5 minutes 22 seconds before it
    refused (start 21:27:51 to exit 21:33:13 on the pod clock).
  - *Arm B, the same with the arena capped under 2^31 bytes (2,147,483,392): no result.* It was started (the launch script's own line) and then killed with the
    launch when the job runner's stall timer fired; the arm's log is empty (0 bytes). The unpublished test-index row says "B skipped (guard independent of the arena cap)"; the logs show it was
    started and never finished. (recorded; no saved result)
  - *Arm C, one group of 20 (5 units x 4, ring, school switches, 6 steps): builds and trains, and misses the registered bar* (`docs/appendix/part7/ch2-train/results/probe-2g31/g3b3-school-U5x4-ring-sw-a40.json`;
    the arm's exit code is 1, the gate's FAIL, and the launch took 3 minutes 22 seconds): no binding error; 8.549 GB resident (8,549,419,688 bytes, 248 buffers, 1,901 passes per step); **1,231.7 ms per array step
    against 26,608.7 ms for the 20 CPU engines (21.6x)**; all 20 harnesses learn (training loss 8.46-8.90 at the first step to 3.77-5.19 at the sixth). Held-out loss of
    each harness against the CPU reference: gap mean 4.1 %, median 3.8 %, **maximum 9.7 %**; 16 of 20 above 2 %, 10 of 20 above 4 %; the registered bar (every
    harness within 2 %) **FAILED** and the record says `pass: false`. The GPU held-out is higher (worse) than the CPU's on **16 of 20** harnesses (mean difference +0.129 in loss; four
    harnesses are better, by 0.6 to 3.3 %). **Discrepancy:** unpublished notes say 17 of 20; the file gives 16 of 20. The sign skew is not noise-like: it
    points to a small systematic GPU lag (candidates named in the log: half-precision GEMM range, ring pull order - not tested). For comparison, the engine's own
    thread-count differences (`docs/appendix/part7/ch2-train/results/cyclone/g3b/g3b2-cpu-noise-school-R8.json`) are of mixed sign (5 of 8 higher, mean difference +0.002 in loss) and the 8-model unit shows no skew
    (5 of 8 higher, +0.005), so the skew of the group of 20 (+0.129) is not the same kind of difference.
  The reading that follows from these records and the guard: the first two 40-model runs trained nothing for a reason consistent with the binding size (the
  logits buffers of 40 models are 2.5 GiB each), a single session of 40 can no longer be built at all, and the real shape of the array - groups of 20, as the
  growth run uses - trains but does not meet the 2 % parity bar. What the 40 models do together (one resident session, the ring between all five units) remains **unmeasured**.

### The 40-harness growth run (A40, 2026-10-09)
`harness/part7/ch2-growrun/run_a40.sh`: 40 harnesses, each its own model, training in two resident array sessions of 20 (`ARRAY_MAX_SLOTS=20`), decode and held-out
evaluation on the GPU, stage gate and growth controller each round (the controller is described in the growth-run section). The sessions are independent: no hub,
no ring, no coupling between them. Outcomes of the launches, from the summary file `docs/appendix/part7/ch2-growrun/results/launch-summaries.json` (facts extracted by script from the launcher's summary lines, the job headers and the per-harness logs of launch 3b; the raw job logs are not shipped):
- *Launch 1* (40 harnesses): stopped after 118 s; the pod compile step printed three segmentation faults (curriculum and tier-1 school compile) before the stop.
- *Launch 1b* (40 harnesses, two sessions of 20; the round phase lasted 15 min 26 s, the whole launch 20 min 44 s): compile of 82 builds + 40 splices in 253 s; **ten harnesses aborted (exit 134) and the other 30 were stopped
  by the launcher's straggler cut 181 s after the first one finished (exit 143); 0 merges; no result file came back**, and the launcher stopped ("no skill.json from the pod"). The
  array servers did step, so there are statistics for this launch: server 0 took 77 steps with 6.74 of 20 slots active on average, **4,827.6 ms of GPU time per step**;
  server 1 took 34 steps with 11.77 of 20 slots active, **10,893.9 ms per step** (7.857 GB resident each). These step times are 4 to 9 times the 1,231.7 ms of the isolated
  group of 20 in the probe (10.5): two servers, 40 harness processes and (in later launches) decode shared one A40 and one host; the records do not separate the causes. The reason
  for the ten aborts is not in the saved logs.
- *Launch 2* (8 harnesses, one session of 8, 18 min): the harness logs show wake step 25 and then no progress for at least 8 minutes before the stop. An unpublished note says it was
  stopped at 141 tokens/s with per-process decode contexts (recorded; no saved result); decode was then moved into the array server (one GPU context for all
  harnesses).
- *Launch 3* (40 harnesses, 16.6 min): stopped with the harnesses at the first day's step 20.
- *Launch 3b* (40 harnesses on the build with decode in the server, 22 min 20 s): **stopped in its start phase with no array step statistics**: the training program (20 slots, 1,588
  passes, 7,856.7 MB resident) and the decode program (20 decoders x 16 stations, 5,066.5 MB, on the second queue) of a server had been built (both servers printed the same training-program line, 1,588 passes and 7,856.7 MB; one printed two decode programs, 5,066.3 and 5,066.5 MB, the other one of 5,066.5 MB), 28 of the 40 harness logs end at "connected to the array server" and the other 12 at the opening-evaluation line (start held-out loss and the answer rate over 1,750 answers), and an unpublished checkpoint note records the GPU idle for 10+ minutes at the start because each harness's opening evaluation (1,750 answers) still
  decoded on the CPU.
An open finding: every array step computes all 20 replicas whatever the number of active slots (the server's code steps all slots, inactive ones "ride along"; launch 1b's
mean active slots were 6.7 and 11.8 of 20); that checkpoint note puts a step at about 1.5 s (partial); the contended
baseline step was not reproducible (suspected a kernel binding one buffer twice; recorded in that note; the results of that experiment are not among the shipped files); every exact gate
depends on that being fixed. For contrast, **a one-harness round with the GPU library on the A40 did complete** in an earlier wiring run (10 days, 10 merges, held-out 0.526, round guard pass (`harness/part7/ch2-growrun/round_guard.py`, `harness/part7/ch2-growrun/g3w_local_round.sh`); `docs/appendix/part7/ch2-growrun/results/g3w/g3w-pod-a40.json`, `docs/appendix/part7/ch2-growrun/results/g3w/growth.jsonl`, `docs/appendix/part7/ch2-growrun/results/grow-wire-pod/guard.json` and the summary `docs/appendix/part7/ch2-growrun/results/wire-pod-round-summary.json`); no round with 8 or 40 harnesses completed in the saved logs.
**Process failures, as registered (the author's rule: failures reported as registered).** (i) 2026-10-08: a billable run was made under the name of the 5 x 8
layout but measured 40 CPU harness processes with a GPU matrix-multiply offload (15.8 k tokens/s, about one unit's rate: the GPU added nothing at 40; record
`docs/appendix/part7/ch2-baseline/results/train-5x8/table.json`: 8 harnesses 13.3 k CPU / 15.4 k with the offload, 40 harnesses 15.9 k / 15.8 k tokens/s at 5.1 s per step per harness, GPU 93 % busy,
20,875 MiB peak, about 21.9 GB; an unpublished results table says 20.9 GB) and none of the layout's defining parts; the rule that followed is the table of section 1.2, listed before every billable run. (ii) 2026-10-09: the
run order followed a "next" list that put side work ahead of the first absent defining part (the array's models training together, resident in VRAM);
the rule that followed puts the first absent defining part first.

# The school step on the GPU: one model, then many models in one recorded step

| | |
|---|---|
| **Date** | 2026-10-09 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). The author reviews each document before publication. |
| **Type** | measured result (laptop software driver, L4 24 GB, A40 48 GB) |
| **Verdict** | Plain and replica forms PASS; with every school switch the registered 2 % per-harness parity bar **FAILED** (max 5.99 %) |
| **Code** | `harness/part7/ch1-gpu-step/` (`train_step.py`, `train_kernels.py`, `s1_loop.py`, `s2_replica.py`, `g3_day.sh`), `harness/part7/ch1-array/s3_centre.py` |

*The record below is the full measured account from the technical disclosure's working chapters: every gate, every failure, with the
harness and result paths in this repository. "Section n" and "§n" inside it refer to the sections of that chapter; the matching documents here
are listed in the README. "Recorded; no saved result" marks a figure the project recorded whose output file is not published.*

## The school step on the GPU (growth-run gates G2, G3; emitter `harness/part7/ch1-gpu-step/{train_step.py, train_kernels.py}`; the rest of the GPU engine is not shipped in this tree)

Description. The engine's training step, with every school switch (T25 clock rotation, plates + page buckets from the engine's LSH planes, spark,
P3, harmony on rings 37..53, router port statistics / gate / pointer / CE with the simplex router frozen, copy pointer, local per-block read-outs,
depth routing, roles, avoid), is emitted as GPU passes (100 kernels written from the equations of our own engine and emitted as SPIR-V by our own
generator; float64 fixed-order reductions) and recorded once, re-submitted per step. `libomnitrain_gpu.so` exposes the engine's C ABI: training calls
run the resident step, every other call goes to the CPU engine with weights synced, uncarried switches fall back to the CPU, so `thead-learn` runs
unchanged (`OMR_TRAIN_LIB`). Parity is judged by gradient cosine and by learning, not bit equality, because float summation order differs.

Measured gates (harnesses `harness/part7/ch1-gpu-step/`, results `docs/appendix/part7/ch1-gpu-step/results/`; the rest of the source is not shipped in this tree). The
switch-by-switch gates ran on a SMALL model (vocabulary 512, D 64, 2 or 4 blocks, batch 2, context 64) on the laptop's software Vulkan driver (llvmpipe), neither at school
size nor on a GPU.
- G1: one gradient step against the CPU engine's own `om_grad` with the same switches on (worst relative element difference of any gradient; worst cosine): T25 clock +
  voicing 4.1e-7 (cosine 0.9999999); harmony 5.2e-7; local rule 4.4e-7; port + pointer + router 6.8e-7; copy head 8.8e-7; routing (exits at 3 blocks) 8.5e-7; local +
  roles 4.8e-7; **avoid 4.2e-6, and 7.3e-6 together with local rule and roles (cosine 0.9999998)**; **attention plates 6.1e-3 (cosine 0.9999763, from LSH bucket flips
  upstream)**; the plate core alone against `om_plate_test` 6.8e-7 at worst (`docs/appendix/part7/ch1-gpu-step/results/grow/g2/s1-small*.json`, `docs/appendix/part7/ch1-gpu-step/results/grow/g2/plate-core-llvmpipe.json`; harness `harness/part7/ch1-gpu-step/{s1_grad.py, g2_plate_core.py}`). Seven of these ten records are within 9e-7; the plan's blanket "every switch within 9e-7" is false for avoid and for plates.
- G2: all switches together (the twelve school switches), 80 real steps, small model with four blocks: held-out 2.7237 GPU vs 2.7268 CPU (0.11 %); with other switch
  sets the GPU held-out is 0.1-1.7 % lower than the CPU's (2.6268 vs 2.6710 with eight switches; 2.7483 vs 2.7962 with eleven, without avoid); the minimum weight cosine
  between the GPU and CPU weights after the 80 steps is 0.88-0.98 across the six loop records (0.917 for the twelve-switch run); the GPU ran 6 to 33 times slower than the
  CPU engine on this software driver (`docs/appendix/part7/ch1-gpu-step/results/grow/g2/s1-loop-*.json`, harness `harness/part7/ch1-gpu-step/s1_loop.py`).
- G3: the library against the CPU engine in one process, small four-block model, 40 steps, every school switch: step-39 loss 3.063 library vs 3.055 CPU, held-out 3.411
  vs 3.436 (0.7 %); the library step took 0.43 s against 0.01 s for the CPU engine on the software driver (`docs/appendix/part7/ch1-gpu-step/results/grow/g3/g3-lib-small4-llvmpipe.json`; harness
  `harness/part7/ch1-gpu-step/g3_engine_lib.py`).
- G4: ONE unchanged `thead-learn` school day (D 64, L 4, H 2, elementary-v1, the laptop's integrated GPU) vs the CPU engine (GPU / CPU): wake loss 7.697 / 7.690, study
  5.304 / 5.296, sleep canary 6.296 -> 6.185 / 6.278 -> 6.171, the same corrections (34 / 34), generator rows (14 / 14) and answered rate (0.479 / 0.479); the GPU day
  took 158 s against 25 s on the CPU (weak GPU, weights cross per step, 1,087 passes, 128.7 MB resident) (`docs/appendix/part7/ch1-gpu-step/results/grow/g3/day/{cpu-state.json, gpu-state.json, cpu.log, gpu.log}`;
  harness `harness/part7/ch1-gpu-step/g3_day.sh`; launch record exit 0 after 184 s, `docs/appendix/part7/ch1-gpu-step/results/launch-records-summary.json`, which equals the two days plus setup).
- G5: the full-size plain trunk (V 8,192, D 256, 6 blocks, batch 4, context 512, no school switches) on a 24 GB GPU (L4), 100 real curriculum steps: 87.2 ms per step
  against 734 ms for the CPU engine on 4 threads (8.4x); loss 9.19 -> 1.94 GPU / 1.95 CPU; held-out 1.559 GPU vs 1.530 CPU (+1.9 %); minimum weight cosine 0.78
  (`docs/appendix/part7/ch1-gpu-step/results/cyclone/c2-s1/s1-loop-school-l4.json`; harness `harness/part7/ch1-gpu-step/s1_loop.py`).
- G6: two GEMM variants on the 48 GB GPU, one unit of 8 school-size models, 3 steps (`docs/appendix/part7/ch1-gpu-step/results/cyclone/g3b/s6-*.json`; harness `harness/part7/ch1-gpu-step/{s6_attn_gemm.py, _s6_child.py}`): the attention
  products as batched GEMMs are NOT bit-identical to the fold form (24 loss words differ, maximum relative loss difference 1.7e-4, maximum weight difference 0.011 against
  a maximum weight of 1.008) and 2.33x faster (223 vs 520 ms); they were adopted after a learning gate (section 11 G1: within 0.05 % of the CPU engines). Tensor-core GEMMs
  for every product: loss differs by up to 2.35 %, 1.07x faster - the gate fails; for the BitLinear forward only: bit-identical, 1.01x - no gain. The plan's statement
  that the failing variant was a half-precision range problem fixed later has no result file (recorded; no saved result).
- Negative: on the laptop GPU a 4-model school-size step ends in device-lost (the single submission exceeds the driver's hang timeout); 1 model runs at 4.9 s per step
  (4,865.8 ms, 3 steps, against 2,809 ms for the CPU engine; `docs/appendix/part7/ch1-gpu-step/results/cyclone/c2-s2/s2-replica-school-R1-intel.json`; harness `harness/part7/ch1-gpu-step/s2_replica.py`). The device-lost itself is recorded in the omni-gpu results summary and device log (not shipped) and by a launch record, exit 1 after 68 s (`docs/appendix/part7/ch1-gpu-step/results/launch-records-summary.json`), without a result file (partial); the fix (split submissions) is not made.
- Negative: the day on the GPU library was slower than on the CPU (158 s vs 25 s) at this size, by design of the weak device and per-step weight transfer; the speed lever
  (weights resident, upload on change) is not built.
- Negative: the full-size cyclone rung G120 on the 24 GB card (3 floors, 120 models, one 3.3 GB slab buffer): feed, ledgers and routing exact, but the weight check FAILED
  with 830,276,940 weight-word mismatches (`docs/appendix/part7/ch1-gpu-step/results/cyclone/pod-l4/G120/G120-l4-full.json`); the G40 rung (1.1 GB buffer) passes (`docs/appendix/part7/ch1-gpu-step/results/cyclone/pod-l4/G40/G40-l4-full.json`; harness `harness/part7/ch1-gpu-step/pod_rungs.sh`). The plan suspects a buffer-range limit near
  2 GB; the 2^31-byte probe (section 11) is consistent with that but did not test this rung.

FIELD PREDICTS: floating-point addition is not associative, so a differently ordered reduction changes low-order bits (Goldberg, ACM Computing Surveys
1991); parity is therefore tested by cosine and by learning, as measured.

### Memory: lifetime planner
At school size (vocabulary 8,192, width 256, 6 blocks, 4 heads, 4 sequences x 512 = 2,048 tokens per step) one model's step held 1.84 GB in an
unpublished project log (weights 27.3 MB, Adam moments 54.6 MB, gradients 27.3 MB, Adam temporary copies 81.8 MB, step working buffers 1,650 MB = 90 %; the
gradient-gate record of the same program, `docs/appendix/part7/ch2-train/results/cyclone/c2-s1/s1-school-l4.json`, shows 1.707 GB resident) (partial). The planner (`harness/part7/ch2-train/gen/train_step.py`,
`Prog.program`) places every *transient* buffer in one arena by lifetime (greedy by size, 256-byte offsets, exact byte ranges, as views of one buffer)
while weights, moments, host-written and read-back buffers stay pinned; the head gradient is written in place; squared-ReLU outputs and attention scores
are recomputed in the backward pass. Recorded after the planner: **0.349 GB per model** (`docs/appendix/part7/ch2-train/results/cyclone/c2-s2/s2-replica-school-R8-a40.json`,
field `bytes_resident_1` = 349,339,460), 8 models in one step 2.78 GB; and 40 models measured at 15.1 GB resident (`docs/appendix/part7/ch2-train/results/cyclone/g3b/g3b3-school-U5x8-a40.json`; the
planner estimate was about 15 GB) - that 40-model record is one of the two runs that did not learn (section 10.5), so the figure is a memory figure, not
a training result. The bit-identity of every value before and after the planner is recorded in the unpublished test index only (partial). FIELD PREDICTS: activation
memory dominates training memory and is cut by recomputation (Chen et al. 2016), and offset planning of tensor lifetimes reduces arena size (Pisarchyk and
Lee 2020).

### One model's training step on the GPU
The step is the engine's own equations emitted as SPIR-V passes by the emitter (39 kernels for the plain trunk, 100 with every school switch; GEMMs through the register-blocked template) plus float64
hand kernels (BitLinear absmean scale, clip norm as 1,024 fixed partial sums then an ordered sum): quantise, gather, per block (norm, ternary linear
q/k/v, rotation, attention per batch and head, output projection, norm, up-projection, squared ReLU, down-projection), norm, tied head, backward in
reverse, embedding scatter, AdamW with clipping, in the engine's order; the loop is one recorded step on fixed buffers with host-fed batches. The port
list was taken from a function census of one school day on the CPU engine (`harness/part7/ch2-wiring/cyclone/c1_census.sh` and `harness/part7/ch2-wiring/cyclone/c1_census.py`, result
`docs/appendix/part7/ch2-wiring/results/cyclone/c1/census.json`): 112 of 247 engine functions and 26 of 59 parallel loops executed.
**Gates** (`harness/part7/ch2-train/train/s1_grad.py`, `harness/part7/ch2-train/train/s1_train.py`, `harness/part7/ch2-train/train/s1_loop.py`, `harness/part7/ch2-train/train/s1_profile.py`; results in `docs/appendix/part7/ch2-train/results/cyclone/c2-s1/`):
- *Gradient gate* (`docs/appendix/part7/ch2-train/results/cyclone/c2-s1/s1-school-l4.json`, L4, school size, one batch): loss 9.158453 (GPU) against 9.158470 (CPU), difference 1.7e-5; worst per-parameter
  gradient cosine 0.999999 (>= 0.999998 against the CPU engine); worst single-element error 2.0e-3 of the largest gradient element; per-token loss
  difference median 1.7e-3, p99 8.5e-3, max 1.2e-2. **The record's `pass` is false:** the strict per-element bar was missed (quantiser rounding flips; the results
  table gives 2e-7 for the CPU engine against itself with different thread counts on the small model); the small-model record (`docs/appendix/part7/ch2-train/results/cyclone/c2-s1/s1-small-llvmpipe.json`) shows the same
  pattern (cosine 0.9999985, max element 1.1e-3).
- *Learning loop* (`docs/appendix/part7/ch2-train/results/cyclone/c2-s1/s1-loop-school-l4.json`, L4, 100 real curriculum steps, host-fed batches): training loss 9.19 to 1.94 (GPU) and 1.95 (CPU), held-out
  1.559 (GPU) against 1.530 (CPU), **+1.9 %** (attributed to float32 sums in softmax and head; float64 sums are an open item); mean of the last 10 step
  losses 1.631 against 1.575; **87.2 ms per step against 734 ms for the CPU engine on 4 threads (8.4x, 23.5 k tokens/s)**. **Not in the headline:** the
  largest single-step loss difference between the two runs is 0.152, and the final weights are far from identical (minimum per-parameter cosine 0.78 - the
  quantised network decides by rounding, so the run is judged by learning, not by weights). The 734 ms is the CPU engine on the L4 pod's host; the same
  engine on the A40 pod's host measures 1,238 ms per model in the replica gate (10.5), so a speedup ratio is only meaningful against the denominator of its
  own run.
- *Profile* (`docs/appendix/part7/ch2-train/results/cyclone/c2-s1/profile-school-l4.json`): step 86.7 ms on the GPU (87.0 ms wall); attention scores (`qkT`) 33.1 %, the three GEMM kernels together 25.5 % (the
  results table rounds this to 26 %). **Failure found and fixed:** the first school profile was 899 ms because two float64 reductions ran on one GPU thread
  over millions of values (816 ms), recorded in an unpublished project log; splitting them into fixed partials gave the 86.7 ms with identical scales (partial). A first unrolled 20-step program
  failed on allocation (`docs/appendix/part7/ch2-train/results/cyclone/c2-s1/s1-train-school-l4.json`: 14,520 passes and 12,742 buffers, `vkAllocateMemory` result -2, out of device memory; the project log puts it at
  about 1 GB of activations per unrolled step); the loop form fixed it.
FIELD PREDICTS: dense-GEMM-bound training is far faster on a GPU than on four CPU threads (roofline model, Williams, Waterman and Patterson 2009); the
8.4x is lower than a peak ratio because the step is not GEMM-only. Floating-point addition is not associative (Goldberg 1991), so a different summation
order flips ternary roundings and quantised networks must be judged by a learning gate, not bit identity: the CPU engine itself differs by up to 4.0 %
per harness between 4 and 2 threads (10.5).

### The replica axis
R models are trained in ONE recorded step: every pass is one launch for all R models (T0B / T2B kernels, replica = z), each model's weights, moments and
activations at its own slice, float64 reductions per replica, each model with its own seed and batches. **Gate** (`harness/part7/ch2-train/train/s2_replica.py`,
results in `docs/appendix/part7/ch2-train/results/cyclone/c2-s2/`): (A) the batched run's per-step losses and final weights are bit-identical to the same model trained
alone on the GPU; (B) held-out loss within 2 % of the CPU engine and falling. Recorded: A and B pass for 3 models per launch (small dims, llvmpipe and
UHD 620; 0 differing weight words per replica; held-out gaps 0.007-0.014 %); UHD 620 **1.81x** faster than three separate runs (20.0 ms for the 3-model step
against 12.1 ms for a 1-model step; llvmpipe 1.32x). Unpublished notes say 1.83x and 19.3 ms; the file says 1.81x. At school size the
same gate passes for 8 models on the A40 (10.5) and for 1 model on the UHD 620 (4,866 ms per step against 2,809 ms for the CPU engine,
`docs/appendix/part7/ch2-train/results/cyclone/c2-s2/s2-replica-school-R1-intel.json`). **Failure as registered:** a 4-model school-size step on the UHD 620 ends in `VK_ERROR_DEVICE_LOST` because the whole step
is one submission and the Intel driver's hang timeout resets the GPU; one school-size model runs (4.9 s per step against 2.8 s on the CPU engine). Fix (split
the recorded step into several submissions) is open. (partial)

### The cyclone holds the model (form 3)
Form: W_h = C + Delta_h. C (one per unit, resident in the hub) is the shared model; Delta_h (one per harness) is that harness's own learning. The
forward pass of harness h reads C + Delta_h, fused into the ternary weight quantiser (the trits and the absmean scale of the *sum*). Each harness's
gradient updates its Delta_h; the hub moves C by the harnesses' mean displacement, C = mean of the updated W_h, and the coupling shrinks every
Delta_h <- (1 - K)(W'_h - C), which keeps C the exact mean. The floor ring couples the five units' C one level up (centre C toward the mean of the four).
The coupling constant follows a lock law (steady spread = drift / K), so the deltas stay small *by the coupling*. **Gate**
(`harness/part7/ch2-train/train/s3_centre.py`, results in `docs/appendix/part7/ch2-train/results/cyclone/m1/`): "pull" (R models + hub mean / pull every step)
against R CPU engines plus the shared-memory coordinator's sync; "centre" against "pull". Recorded (30 steps, K = 0.1): small, 4 models (llvmpipe / UHD
620): pull against the CPU held-out within 0.028 % / 0.035 %, centre against pull within 0.016 % / 0.011 % (step loss within 0.021 % / 0.010 %), spreads
0.003537 (CPU) against 0.003537-0.003539 (pull, centre); **school size, 8 models, A40 (`docs/appendix/part7/ch2-train/results/cyclone/m1/m1-school-R8-a40.json`)**: pull against CPU held-out within 0.062 %, centre against CPU within
0.057 %, centre against pull within 0.044 %, step loss within 0.039 %, spreads 0.0019276 (CPU) / 0.0019270 (pull) / 0.0019263 (centre). The gate thresholds
were held-out within 2 % and spread within 10 % for pull, 0.5 % and 1 % for centre against pull; all four records pass.
FIELD PREDICTS: workers tied to a centre by an elastic force (EASGD, Zhang et al. 2015); local steps with an outer step on the mean displacement
(DiLoCo, Douillard et al. 2023); one shared base with many small sign-bit deltas, linear = base part + delta part (BitDelta, Liu et al. 2024).

### Array server, decode and the engine library
`omni-gpu serve` is a resident R-slot session (`harness/part7/ch2-server/src/array.rs`) that unchanged harness processes join through shared-memory slots: each
harness's training call goes to its slot, the server steps when the slots that are in have arrived (lockstep days), inactive slots ride along, weights are
fetched on demand. The engine library `libomnitrain_gpu.so` (`harness/part7/ch2-server/engine-gpu/src/lib.rs`, `harness/part7/ch2-server/engine-gpu/Cargo.toml` and `harness/part7/ch2-server/engine-gpu/build.rs`) keeps the engine's C interface so the harness runs unchanged:
training calls run the resident step (switches recorded and forwarded; uncarried switches fall back to the CPU, said once), everything else runs on the CPU
engine. The program the server builds is R independent models in one step (the replica form; `harness/part7/ch2-train/gen/make_program.py`): it has no hub and no ring.
- Engine library, one harness (`harness/part7/ch2-server/train/g3_engine_lib.py`, `docs/appendix/part7/ch2-server/results/grow/g3/g3-lib-small4-llvmpipe.json`): 40-step gate with
  every switch, step-39 loss 3.063 (GPU) / 3.055 (CPU), held-out 3.411 / 3.436 (-0.7 %, within the 2 % bar). One unchanged school day (`harness/part7/ch2-server/grow/g3_day.sh`,
  `docs/appendix/part7/ch2-server/results/grow/g3/day/cpu-state.json`, `docs/appendix/part7/ch2-server/results/grow/g3/day/gpu-state.json` and the two day logs in the same folder; width 64, 4 blocks, laptop UHD 620): wake 7.697 / 7.690, study 5.304 / 5.296, sleep
  canary 6.296 to 6.185 / 6.278 to 6.171, corrections 34 / 34, generator rows 14 / 14, answered rate 0.479 / 0.479; **158 s on the GPU against 25 s on the CPU** (weak
  laptop GPU, weights cross per step, 1,087 passes, 128.7 MB resident). **Discrepancy not in the earlier text:** the two day records are not identical in every counter:
  the CPU day records 564 avoid pushes and 31,540 routing-training rows, the GPU day records 0 and 0, and the routed-row counters differ (201,279 against 94,783); the
  counters may simply not be forwarded through the library, which is not stated anywhere in the shipped files, so "same corrections, generator rows and answered rate" is all that is shown.
- Array server (`harness/part7/ch2-server/grow/g3b4_day.sh`, `docs/appendix/part7/ch2-server/results/grow/g3b4/g3b4.json`): one harness's school day through the server equals
  its solo day on **351 of 351 leaves** (0 differences; two solo runs also equal), the server stepped 55 times with 1.89 of 2 slots active per step (A40, 256.9 MB
  resident). Decode inside the server on a second queue (one GPU context for all harnesses), gate with 4 clients (`harness/part7/ch2-server/grow/d1_decode.py`,
  `D1_SERVER=4`; `docs/appendix/part7/ch2-server/results/grow/d2/d2.json`): top-1 1,536 of 1,536 for each client, 0 CPU fallbacks, 2,923 decode steps. **Discrepancy:** an unpublished checkpoint
note says "exits 95 of 96 rows"; the record counts rows with identical exit counts as 24, 0, 0 and 0 (24 of 96), and the largest logit difference of client 1
  is 1.23 against 0.03-0.05 for the others; the per-row records that would settle it are not among the shipped files (partial).

## Reading
Batching models in one recorded step is exact per replica and an order of magnitude faster per model; the full school step is close to
the CPU engine but not inside the registered 2 % bar, a bar tighter than the CPU engine reproduces itself. FIELD PREDICTS: floating-point
addition is not associative (Goldberg, 1991), so parity is tested by learning; batching underfilled models removes launch overhead
(roofline, Williams et al., 2009).

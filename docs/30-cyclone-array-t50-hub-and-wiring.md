# The cyclone array: a T50 hub, resident wiring and toroid-to-toroid routing on the GPU

| | |
|---|---|
| **Date** | 2026-10-08 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). The author reviews each document before publication. |
| **Type** | design + measured rungs (laptop GPU and software driver; L4 24 GB) |
| **Verdict** | Wiring rungs G1–G40 PASS (exact); G120 full-size weight check **FAIL**; the whole design has not run together |
| **Code** | `harness/part7/ch2-t50-core/t50.rs`, `t50_probe.c`; `harness/part7/ch2-wiring/` (`src/session.rs`, `cyclone/rung.py`, `kernels/*.spvasm`) |

## The author's design, verbatim (2026-10-08)
*"Were making a training array, each unit will have a 50t center, with 8 harnesses around it a model tied to each. they will be
connected and feeding data into they cyclone, the arc reactor evolution. that is one unit. around the one unit, there will be 5 of those
systems spread out around it, touching on the outer ring. they will all be connected by the ring and increasing resonance/compounding"* —
then *"yes, but actually 1 in the center 4 around for a total of 5."* On the GPU: *"it will be this layout, but 3 layers stacked on top of
each other, so there is 3 floors with the 5 unit layout."* Routing: *"any time a process/step fires, it can find it's way to where it
needs by jumping from toroid to toroid, each ring interconnects with every other toroid."* And the start: *"start on a 24gb to get the
layout and wiring right, then keep scaling up marking and recording results."*

A **toroid** is the torus shape: each hub's inner core is a toroid (a toroid core), and the rings around it are toroids too.

*The record below is the full measured account from the technical disclosure's working chapters: every gate, every failure, with the
harness and result paths in this repository. "Section n" and "§n" inside it refer to the sections of that chapter; the matching documents here
are listed in the README. "Recorded; no saved result" marks a figure the project recorded whose output file is not published.*

### Defining parts against what actually ran
Parts are those listed in the pre-registration (`docs/appendix/part7/ch2-wiring/prereg/array-layout-and-training-bars.md`), as the pre-registration's own text places them before any billable run (no timestamp ships for that). Columns are the four things that were run, filled from the run records themselves. PRESENT =
the part is in what ran and was checked; PARTIAL = some of it; ABSENT = not in it.
Sources: **A** `docs/appendix/part7/ch2-baseline/results/train-5x8/table.json` (its `what_ran` field) with `harness/part7/ch2-baseline/train5x8/run.sh` and `harness/part7/ch2-baseline/train5x8/all.sh`;
**B** the `parts` field written by `harness/part7/ch2-wiring/cyclone/rung.py` into every rung record (the folders `docs/appendix/part7/ch2-wiring/results/cyclone/G1/`, `docs/appendix/part7/ch2-wiring/results/cyclone/G4/`, `docs/appendix/part7/ch2-wiring/results/cyclone/G8/`, `docs/appendix/part7/ch2-wiring/results/cyclone/G40/`, `docs/appendix/part7/ch2-wiring/results/cyclone/G120/` and `docs/appendix/part7/ch2-wiring/results/cyclone/pod-l4/`); **C** the folders `docs/appendix/part7/ch2-train/results/cyclone/c2-s1/`, `docs/appendix/part7/ch2-train/results/cyclone/c2-s2/`, `docs/appendix/part7/ch2-train/results/cyclone/m1/`, `docs/appendix/part7/ch2-train/results/cyclone/g3b/` and `docs/appendix/part7/ch2-server/results/grow/`, and the probe record of section 10.5 (`docs/appendix/part7/ch2-train/results/probe-2g31/g3b3-school-U5x4-ring-sw-a40.json`), read together with the program builders `harness/part7/ch2-train/gen/train_step.py` and `harness/part7/ch2-train/gen/make_program.py`; **D** the launch summaries of the growth run (section 10.7; `docs/appendix/part7/ch2-growrun/results/launch-summaries.json`) and
`harness/part7/ch2-train/gen/make_program.py` (header, line 8: the array server builds R *independent* harness models in one step, "the replica form").

| # | Defining part (author's words, short) | A. As-built 40-process baseline (A100, 2026-10-08) | B. Layout + wiring rungs G1-G120 (laptop; L4 at full size; **no training**) | C. Training pieces (one model; R models per step; unit, array and group tests; laptop and A40) | D. 40-harness school run on the A40 (2026-10-09, two independent array sessions of 20) |
|---|---|---|---|---|---|
| P1 | T50 centre per unit, on the GPU | ABSENT | PARTIAL: T50 addressing, per-ring ledger and the coupling hub on the GPU; the other precompute streams on the ring are not built | PARTIAL: the hub's mean / pull (and the "centre" form) and the floor ring run inside the training programs; the T50 addressing and routing kernels are not part of them (the T25 residues are host-fed into the loop) | ABSENT: the server's programs have no hub, no ring and no T50 addressing (independent models) |
| P2 | 8 harnesses around the hub | PARTIAL: 40 real harness processes, no hub, control loops on the CPU | PARTIAL: batch slicing and the T25 event bus on the GPU; the harness control loop (wake, doing, judging) on the CPU | PARTIAL: batches host-fed; control loops on the CPU | PARTIAL: 40 real harness processes, grouped 2 x 20, not 5 units x 8; their decode and held-out evaluation go to the GPU (decode gate, 10.6) |
| P3 | a model tied to each, training on the GPU | ABSENT: the GPU did a matrix-multiply offload only; 40 harnesses ran at one unit's rate | ABSENT: the rung record says so ("no training step on the GPU yet") | PARTIAL: one model, 8 models and a group of 20 train and learn on the GPU; the registered per-harness parity bar (2 %) was **missed** by the unit with every school switch (max 5.99 %) and by the group of 20 (max 9.7 %); 40 models in one session are refused by the guard (and, built without it, trained nothing) | PARTIAL: 40 independent models in two servers; one launch took 77 and 34 server steps, 10 harnesses aborted, 30 were stopped, no harness finished a day and no round completed |
| P4 | harnesses and models feed the cyclone; the hub processes, sorts, precomputes | ABSENT | PARTIAL: token events and weights flow into the hub; routing present | PARTIAL: the hub mean is computed from the models' weights in the step | ABSENT |
| P5 | 1 centre + 4 around, touching on the outer ring | ABSENT | PRESENT (G40, G120 records) | PARTIAL: units + floor ring inside one training program: small size passes (5 x 2); school size 5 x 2 within 1.69 %; 5 x 4 trains but misses the 2 % bar; 5 x 8 refused | ABSENT (no ring in the server) |
| P6 | all connected by the ring, resonance compounding | ABSENT | PARTIAL: the coupling stream crosses the ring and every item routes toroid to toroid; **compounding (learning across units) was not measured** | PARTIAL: as P5; compounding not measured | ABSENT |
| P7 | all of it resident in VRAM | ABSENT: the GPU held offload buffers (20,875 MiB, about 21.9 GB, at 40 harnesses), not the models' training state | PARTIAL: the full training *state* of 40 models allocated (not trained) at 21.8 GB on the L4 | PARTIAL: 8 models training in 2.78 GB, 20 models in 8.55 GB (A40) | PARTIAL: training programs 7.86 GB and decode programs 5.07 GB per session are resident; the harness loops are not |
| - | routing, toroid to toroid by address | n/a | PRESENT (exact, G40 and G120; the first L4 G40 record, from the executable before routing was added, says ABSENT) | ABSENT (not in the training programs) | ABSENT |

### What was NOT run (plainly)
1. No run had the T50 hub, 40 models training, the ring between units and VRAM residency **all at once** (P1 + P3 + P5 + P6 + P7). The array exists as
   resident wiring (B) and as resident training (C) in separate programs.
2. The 5 x 8 school-size training array **cannot be built as one resident session**: the planner refuses it with an explicit error (three logits buffers
   of 2,684,354,560 bytes exceed the 2^31-byte storage-binding limit, section 10.5), and the two earlier 40-model attempts, built before the guard
   existed, trained nothing (loss stayed near 9.1). The real shape, one group of 20 (5 x 4), builds and every harness learns, but its registered
   per-harness bar (held-out within 2 % of the CPU engines) **failed** (mean gap 4.1 %, max 9.7 %). The growth run therefore splits 40 into two
   sessions of 20.
3. The first 40-harness growth launch that reached its training phase ended with no harness finished and no round; the last launch was stopped in its
   start phase and produced no array step statistics (section 10.7).
4. "Compounding" across the ring (P6) and the compute-per-wall-clock comparison of the array against the CPU school (the last stage of the pre-registration) were not
   measured. The full training state of a three-floor array (about 65 GB by the per-model footprint) was not run; the 80 GB rung is untested.
5. The ring-coupling constants (section 5.2) were chosen at implementation; they were proposed, not tuned against learning, and their coupling rule
   was not confirmed by the author in anything shipped with this part (recorded; no saved result).
6. The Windows build of the deployable, the CUDA (PTX-rendered) fast path, and drawing the cyclones in the browser from the same video memory are
   designed only (section 12).

### The capacity ladder (designed estimates, measured rows)
Per-model training footprint at the school settings, measured on the CPU engine (`harness/part7/ch2-wiring/cyclone/c0_footprint.py`, result
`docs/appendix/part7/ch2-wiring/results/cyclone/c0/footprint.json`): 537,976,832 bytes = 0.538 GB (0.140 GB kept between steps + 0.398 GB of step activations; the
base, non-school configuration 0.470 GB). The 40-model (21.5 GB) and 120-model (64.6 GB) rows of the ladder are in that record; the 160-model row and the
"floors in turn" figures are arithmetic from it. Rungs are named by the number of models.
| Rung | Layout | Models | VRAM all-at-once (estimate = models x 0.538 GB) | Card | Measured (records in `docs/appendix/part7/ch2-wiring/results/cyclone/`) |
|---|---|---|---|---|---|
| G1 | 1 cyclone + 1 model + 1 harness | 1 | 0.5 GB | laptop GPU to 24 GB | exact on both laptop devices (`docs/appendix/part7/ch2-wiring/results/cyclone/G1/`); L4: 0.573 GB with its training state, 1.10 ms per wiring step (`docs/appendix/part7/ch2-wiring/results/cyclone/pod-l4/G1/`) |
| G4 | 1 cyclone, 4 pairs | 4 | 2.2 GB | 24 GB | exact on both laptop devices (`docs/appendix/part7/ch2-wiring/results/cyclone/G4/`); L4: 2.196 GB, 2.34 ms (`docs/appendix/part7/ch2-wiring/results/cyclone/pod-l4/G4/`) |
| G8 | 1 unit (cyclone + 8 pairs) | 8 | 4.3 GB | 24 GB | exact on both laptop devices (`docs/appendix/part7/ch2-wiring/results/cyclone/G8/`); L4: 4.36 GB, 4.26 ms (`docs/appendix/part7/ch2-wiring/results/cyclone/pod-l4/G8/`) |
| G40 | 1 floor: 5 units (centre + 4 around), outer ring | 40 | 21.5 GB | 24 GB (tight) / 48 GB | **21.834 GB resident (training state allocated, not trained), 25.74 ms per wiring step (25.93 ms with routing), every stream exact, on an L4** (`docs/appendix/part7/ch2-wiring/results/cyclone/pod-l4/G40/G40-l4-full-state.json`, `docs/appendix/part7/ch2-wiring/results/cyclone/pod-l4/G40-route/`) |
| G120 | 3 floors (layer above, layer below) | 120 | 64.6 GB (about 33 GB with floors in turn, an estimate) | 80 GB | wiring exact on llvmpipe and UHD 620 with reduced slabs (`docs/appendix/part7/ch2-wiring/results/cyclone/G120/`); **full-size weight check FAILED on the L4** (`docs/appendix/part7/ch2-wiring/results/cyclone/pod-l4/G120/G120-l4-full.json`); full state not run |
| G160 | 4 floors | 160 | 86 GB (about 38 GB in turn, an estimate) | 96 GB | not run |

## The T50 omniring system (the hub's code)
**Description.** An omniring system is a residue number system together with its core: a state is held only as its residues on pairwise-coprime
moduli (rings); n rings hold the product of the moduli as states and decode in the sum of the moduli probes. The core's form grows with the ring
count. The tiers used here are nested exact sub-tori: **T25** = the 25 odd primes 3...101 (five groups of five, one group per event field); **T30** =
T25 plus 103, 107, 109, 113, 127; **T50** = T30 plus the 20 primes 131...233, dealt round-robin to the five groups, so each of the five event fields
is carried by 10 rings (`harness/part7/ch2-t50-core/t50.rs`, `Program64::t50`; its unit test `t50_tier_shape` asserts the 50 primes, the sum of
moduli 5,348 and the group layout). T50 has 50 odd primes, the sum of its moduli is 5,348 and the product of its moduli is 10^93.3 (checked by
arithmetic; T25 sum 1,159, T30 sum 1,718, the 20 outer moduli sum 3,630).
Every modulus is below 256, so each ring is one 8-bit SIMD lane and the 50 lanes fit one 64-lane 512-bit vector (the lanes beyond the tier are inert:
residue 0, twist 0). Residues of 128 and above need an *unsigned* byte compare, which AVX2 lacks, hence the AVX-512 (EVEX) path.
An *event* has five integer fields (position in the session, token, offering plate with 36 = none, level (curriculum phase), row (the count of
end-of-sequence tokens before it)). The residue of ring r is (field value + the field's offset) mod m_r, with offsets (16384 x 64, 16384 x 64, 0, 0,
half the product of the fifth field's five T25 moduli, 33,774,435); the sum must lie in [0, 2^31) (stated in the harness
`harness/part7/ch2-wiring/cyclone/w2a_ring_addr.py`, which asserts the domain). Each ring also has a *twist*: its residue minus the residue of a
staged plate (an event the other side predicted), mod m_r; twist 0 on every ring confirms the prediction, a non-zero twist flags exactly the rings that
differ. The tick is x <- x + 1 on every ring (each ring one notch per tick at its own rhythm).
On the CPU the core is rendered as x86-64 AVX-512 code into executable memory (`harness/part7/ch2-t50-core/t50.rs`, function `render`): per ring, the coordinate plus the field
offset, a magic-number reduction q = x * ceil(2^40 / m) >> 40, r = x - q * m, one byte per ring into a 64-byte row; then the whole row is twisted against
the plate at once (`vpcmpub` into a mask, `vpsubb`, masked `vpaddb` of the moduli). The vector encode (`render_v`) replaces the per-ring scalar encode with
the direct-remainder method of Lemire, Kaser and Kurz (2019) (`arXiv:1902.01961`, as cited in the source comments, which say it was written from the paper: idea-level clean room, section 14): the 31-bit coordinate is first folded to y = hi * (2^16 mod m) + lo (hi = x >> 16, lo = x & 0xFFFF, y < 2^24, same residue mod m); with
c = floor((2^32 - 1) / m) + 1 the residue is ((c * y mod 2^32) * m) >> 32, computed for 8 rings per 512-bit register (`vpermq` of the field into its lanes,
three `vpmuludq`, `vpsrlq`, `vpmovqb`). The source's test `lemire_fold_exact` checks the formula exhaustively for every y < 2^24 and every modulus 3...233,
and for 1 M pseudo-random coordinates plus edge values; the oracle for the encode and the twist is the scalar `Program64::residues` / `twist_scalar`.
The 20 outer moduli 131...233 exceed the number of toroids used in the layout, so on those rings a residue is an address with no collision.
**Gates (CPU, one hardware thread of the server).** The probe source and the core source ship with this part (`harness/part7/ch2-t50-core/t50_probe.c`, `harness/part7/ch2-t50-core/t50.rs`); the numbers below are quoted from an unpublished test index
(rows dated 10-08) because the result logs they cite are not among the shipped files
(partial). They are recorded figures, not results of files shipped here.
- G1 *tick cost is flat in ring count while the tier fits one register* (harness `harness/part7/ch2-t50-core/t50_probe.c`, a standalone C
  kernel, not the rendered core): the tick is timed as 10 M dependent steps of one 64-byte register (ns **per tick step**, not per event) and the twist as
  1 M random row pairs (ns **per event pair**, memory-bound); each vector path is compared with a scalar loop and the tick with `steps mod m`. Recorded:
  tick 1.200 / 1.195 / 1.204 ns for T25 / T30 / T50; twist 3.73 / 3.76 / 4.05 ns; 0 mismatches on every path; 10^93 states at T25's cost. **Caveats:**
  the "scalar" loop is auto-vectorised by the compiler (not a true scalar baseline), and the AVX-512 tick executes the *same* 64-lane instruction for all
  three tiers (the extra rings are inert lanes), so flatness here is by construction: what is measured is that a 50-ring tier costs no more than a 25-ring
  tier while it fits one register. (partial)
- G2 *the rendered T50 equals scalar and leaves T25/T30 unchanged* (harness: `bench_row` in `harness/part7/ch2-t50-core/t50.rs`, run as `omni-render t25-layers-bench`; per-ring
  scalar encode): 0 / 0 / 0 mismatches (scalar / T25 rings / twist); **22.2 ns per event for T50 against 11.3 ns for T25 (about 2x, not flat)**. (partial)
- G3 *the 64-lane vector encode (Lemire) flattens the cost* (same harness, `render_v`): 0 mismatches on all rows; T25v 13.4, T30v 13.0, T50v 14.6 ns per
  event, against T25 on the AVX2 core 17.6 ns and T50 scalar-per-ring 29.4 ns in the same run. (partial)
- G4 *the T50 as a bus*: 1,000,000 keys addressed by their T50 residues into shared memory with check rings: 0 missed, 0 wrong, 0 absent hits, 0 false
  flags; 100,000 of 100,000 injected single-ring slips detected; recall 283 ns. (recorded; no saved result)
- **The "ns per event" figures are three different measurements and must not be read as one curve:** (i) the C probe, a tick step on one register and a
  twist per row pair; (ii) the rendered core with the per-ring scalar encode, whole event (encode + twist); (iii) the rendered core with the vector
  encode, whole event. The scalar-encode rows appear twice in the test index with different values (T25 11.3 / T50 22.2 ns in the first run, 17.6 / 29.4 ns in
  the second): the second run is 1.3 to 1.6 times slower on the same two rows, and the host load of those runs is not recorded (the C probe's own
  record notes a host load of 85), so only ratios inside one run (T50v 14.6 ns against T50 scalar 29.4 ns, about 2x) are comparable. The figure that
  applies to the hub's per-event cost is G3.
FIELD PREDICTS: RNS arithmetic is carry-free between moduli, so per-event cost grows with lane count only when the lanes exceed the vector width
(Szabo and Tanaka 1967); 50 eight-bit lanes fit one 512-bit register, so G1 and G3 flat-ish and G2 not flat (per-ring scalar work) is the expected
shape. A residue code with r redundant moduli detects up to r residue errors (Mandelbaum 1972; Szabo and Tanaka 1967), so single-ring slips are
all detectable, as G4 measured. Lemire, Kaser and Kurz (2019) publish the direct-remainder method the vector fold is named after.

## The resident session (`harness/part7/ch2-wiring/src/session.rs`, `omni-gpu session PROGRAM`)
**Description.** Buffers are device-local and persist across steps; pipelines and descriptor sets are built once; the whole step is recorded once as
a chain of compute passes into one command buffer, with a barrier after every pass (it also orders the next submission), and that command buffer is
re-submitted S times. The host crosses to the device only on explicit `write` / `read` lines or per-step `stepwrite` (host-fed batch, before every
step) and `stepread` (after every step). A program is lines: `buf zero BYTES`, `buf file PATH`, `buf view PARENT OFFSET BYTES` (an exact sub-range of
a buffer, used by the memory planner), `pass SPV X,Y,Z [spec ID=U32]... bind I J ...`, `read I`. Per-pass GPU time comes from timestamp queries.
A recorded step can also contain passes whose workgroup count the GPU itself wrote (`vkCmdDispatchIndirect`, section 9).
**Gate G1** (`harness/part7/ch2-wiring/cyclone/c2a_session.py`, result `docs/appendix/part7/ch2-wiring/results/cyclone/c2a/session.json`): buffer 0 = 2^20 random
words; each step runs P pairs of a copy-and-add kernel (0 to 1 with +1, then 1 to 0 with +1); cases (P, S) = (1, 1) and (50, 20), i.e. up to 2,000
chained passes; oracle on the host: buffer 0 = input + 2PS, buffer 1 = input + 2PS - 1 (mod 2^32). Recorded: byte-exact (0 mismatched words) on the
llvmpipe and UHD 620 devices; UHD 620 0.448 ms per resident pass against 5.997 ms per pass when each pass creates, uploads, runs, reads back and tears
down (13.4x); llvmpipe 2.73 ms against 12.47 ms (4.6x).
FIELD PREDICTS: re-submitting a recorded command buffer removes per-dispatch setup cost; NVIDIA introduced CUDA Graphs (CUDA 10, 2018) for the same
launch-overhead case, and the gain should be largest for chains of short kernels, as measured.

## Batch and replica axes in the SPIR-V emitter (the emitter's `--batch` option, template T0B; the emitter source is not shipped with this part)
**Description.** Every kernel template can run N rows and R replicas in one launch: global id x = element, y = row, z = replica (the register-blocked
GEMM template uses the workgroup z index as the replica). A list argument k is strided by specialization constants: SpecId 200+3k = row stride,
201+3k = replica stride, 202+3k = slice length; the output by 290 / 291; local size is SpecId 100. **A stride of 0 means shared**: every row or
replica reads one slice (the shared-weights case). The row axis turns 2,048 per-row dispatches into one; the replica axis serves 8 models per launch.
**Gate G1** (`harness/part7/ch2-emitter/c2c_batch.py`, result `docs/appendix/part7/ch2-emitter/results/cyclone/c2c/batch.json`): for each of the 21 wall-passed
equation specs: emit twice (byte-identical), `spirv-val`, then per device (a) the op's recorded engine rows grouped by shape, each group one dispatch
of 2 replicas x N/2 rows, every row within the engine's check tolerance; (b) the first row stored once with strides 0, run as 4 rows x 2 replicas, all 8
outputs correct. Recorded: 21 of 21 ops, 1,932 rows in 933 launches per device (llvmpipe and UHD 620), 0 bad rows, worst error 0.854 of tolerance.
Prerequisite (the un-batched emitter, same tolerance rule; harness `harness/part7/ch2-emitter/v3_parity.py`): 1,764 of 1,764 recorded engine rows pass on the UHD
620 and llvmpipe (`docs/appendix/part7/ch2-emitter/results/v3/parity.json`), ternary operations bit-exact, worst 0.854 of tolerance; the same 21 specs pass 1,764 of 1,764 on an
A40 (`docs/appendix/part7/ch2-emitter/results/v3-a40/parity.json`).
FIELD PREDICTS: batched (grouped) matrix routines keep a GPU occupied when each problem is small (Dongarra et al. 2017, batched BLAS; vendor
batched-GEMM routines), so an N-replica launch should cost less than N launches until occupancy saturates.

## The wiring kernels (hand-written SPIR-V in `harness/part7/ch2-wiring/kernels/`)
### `ring_addr`: omniring addressing, lane = ring
One invocation per (event, ring): the ring's modulus, its field and the field offset come from a small table, so the **same code serves T25 (per
harness bus) and T50 (per unit hub)**; the program is data. Outputs: residues, twists against the staged plate, a per-owner **ledger**
`[owner][64][256]` counting, for every ring, how many events fell on each residue, and a per-event 64-bit deviation mask (bit k set when ring k's twist is
non-zero). Rings beyond the tier stay zero (checked: "inert" lanes). **Gate** (`harness/part7/ch2-wiring/cyclone/w2a_ring_addr.py`, result
`docs/appendix/part7/ch2-wiring/results/cyclone/w2a/ring_addr.json`): traffic is real - one floor (5 units x 8 harnesses = 40) x one school batch (4 windows x 512
positions) = 81,920 events cut from a tier-1 curriculum build; each event is staged with its own expected event (must confirm: twist 0), staged with the
token changed (must deviate on exactly the token rings where residues differ), or not staged. Oracles: the T25 residues must equal **the runtime's own
rendered T25 core** (the generated x86 bytes, executed from a memory map; the record compares against its dumped description `docs/appendix/part7/ch2-wiring/results/cyclone/c1/run/t25_core.json`);
T50 follows the T50 layout above and its lanes on the T25 rings must equal the rendered T25 core (T25 is an exact sub-torus of T50). Checked exactly:
residues, twists, per-owner ledgers, deviation masks, inert lanes, ledger total = events x rings (2,048,000 for T25, 4,096,000 for T50). Recorded: 0
mismatches on both devices; 27,188 own-staged events all confirmed, 27,118 changed-token events all flagged. GPU cost per event of a whole-floor launch:
T25 199.7 ns (llvmpipe) / 196.5 ns (UHD 620); T50 304.4 ns (llvmpipe) / 505.5 ns (UHD 620) - a laptop-class integrated GPU, a per-launch kernel, **not a
throughput claim** (the persistent T50 ring kernel is not built, section 12; the server CPU's rendered core costs 14.6 ns per event, section 2 G3, a different
machine and measurement).
### `hub_mean`, `hub_pull`: the cyclone's coupling
`hub_mean` averages the healthy models' weight slabs of a unit in float64, in order, with one rounding to float32; `hub_pull` applies
w <- w + K (mean - w) in float32, every operation rounded separately (no fused multiply-add). A model dropped by the harmony monitor has keep = 0 and is
re-seeded with K = 1. On a floor the **ring** carries the five unit means one level up: the four outer hubs pull toward the centre hub (K2 = 0.25), the
centre pulls toward the mean of the four outer hubs (K2c = 0.10), then every model pulls toward its ring-updated unit mean (K = 0.35 in this wiring test;
the training gates of sections 10.4 and 10.5 use K = 0.1 with the same K2 and K2c). Floors do not couple weights (they couple only through routing). The
constants are the defaults of the executable (`harness/part7/ch2-wiring/src/cyclone.rs`, `km: 0.35, k2: 0.25, k2c: 0.10`) and of every harness that reads them;
they were fixed at implementation and were not tuned against learning.
**Gate** (`harness/part7/ch2-wiring/cyclone/w2b_hub.py`, result `docs/appendix/part7/ch2-wiring/results/cyclone/w2b/hub.json`): unit = the 8 live-round checkpoints at
full size (6,926,912 floats each, 55,415,296 weights), one harness dropped; floor = 40 real checkpoints, first 1,048,576 floats each, one harness
dropped; two recorded steps (the second starts from the first's result, as training does); every float compared bit for bit against numpy mirroring the
CPU coordinator's arithmetic. Recorded: 0 bit mismatches on both devices; unit 249.4 MB resident, 54.3 ms per step on the UHD 620 (240.3 ms llvmpipe);
floor 197.1 MB, 59.2 ms (332.3 ms llvmpipe).
FIELD PREDICTS: coupling workers to a centre variable by an elastic force is elastic-averaging SGD (Zhang, Choromanska and LeCun 2015); a locked
state exists only above a critical coupling and the steady spread is drift over coupling (Adler 1946; Kuramoto coupled oscillators), which is the rule
the coordinator uses to set K.
### `feed_win`, `ev_build`: the harness feed
`feed_win` cuts every harness's batch (B windows x T positions) from the curriculum held resident in VRAM (window phase and offset from the harness's own
SplitMix64 stream, seed 0x5EEDC7C1): input token, target (masked where the build masks it), plate kind, proposal, stage; equal to the runtime's batch
slicing on every position. `ev_build` turns each window into the trunk's T25 events (field row = the EOS count before the position). **Gate**
(`harness/part7/ch2-wiring/cyclone/w2d_feed.py`, result `docs/appendix/part7/ch2-wiring/results/cyclone/w2d/feed.json`): feed_win, ev_build and two ring_addr passes (T25
per harness, T50 per unit) chained in ONE recorded step, one floor (160 windows, 81,920 positions): all compared exactly. Recorded: 0 mismatches in
feed, events, T25 and T50 residues and ledgers on both devices; 120.8 MB resident; 124.3 ms per floor step on the UHD 620 (67.6 ms llvmpipe).

## Routing: toroid to toroid by address (`harness/part7/ch2-wiring/kernels/route.spvasm`)
**Description.** The layout is a direct torus network whose dimensions are rings. Layouts: one floor = 5 toroids on one ring of 5 (centre + 4 around);
three floors = 15 toroids on two dimensions, ring 3 (the floor, stride 5) then ring 5 (stride 1). A toroid's coordinates are residues on those layout
rings. Each event is addressed on the T50 (5.1) and routed from its source cyclone: for each dimension in order, c = the item's residue on that ring
mod the ring's size; the item's *home* is the sum over dimensions of c x stride; if the item's current coordinate differs from c it **jumps once** (one
CRT jump per ring; every toroid is linked to every other along a ring, so at most one jump per dimension and at most two jumps in 2-D), the link
`link[dimension][from][to]` is incremented, and the hop counted. Per step the kernel also fills each toroid's **home ledger** (per ring, per residue,
the items that reached it) and its inbox count.
**Gate** (`harness/part7/ch2-wiring/cyclone/w3_route.py`, result `docs/appendix/part7/ch2-wiring/results/cyclone/w3/route.json`, and the rung gate
`harness/part7/ch2-wiring/cyclone/rung.py`): home, hop count, every link's traffic, every inbox and every home ledger compared exactly against a Python
reference of the same rule. Recorded (`docs/appendix/part7/ch2-wiring/results/cyclone/w3/route.json`, llvmpipe and UHD 620): one floor, 81,920 items, hops 0 / 1 = 16,176 / 65,744, inbox 5,512 / 27,489 /
21,264 / 5,079 / 22,576, 0 mismatches; three floors (15 toroids), 245,760 items, 0 mismatches. The G120 rung record (3 floors, 15 toroids, 120 models,
llvmpipe, 262,144-float slabs, 2 steps; `docs/appendix/part7/ch2-wiring/results/cyclone/G120/G120-llvmpipe-w262144.json`) records 245,760 routed events per step (120
harnesses x 4 windows x 512), **all 20 mismatch counters 0** (feed, T25 ledger, T50 ledger, weights, home, hops, links, home ledgers, inbox, the four cut
checks of section 8 and the seven mailbox checks of section 9), 0.506 GB resident, 351.3 ms per step on the CPU Vulkan device. An earlier revision of the same
rung (nine counters, before the cut and mailbox passes were added; copy: `docs/appendix/part7/ch2-wiring/results/cyclone/G120-earlier-revision/G120-llvmpipe-w262144.json`) recorded 0.504 GB and 304.2 ms per step; the UHD 620
record of the rung (nine counters, 0 mismatches) is 495.6 ms per step. The same checks passed on both laptop devices for G40 (`docs/appendix/part7/ch2-wiring/results/cyclone/G40/G40-llvmpipe-w1048576.json` and `docs/appendix/part7/ch2-wiring/results/cyclone/G40/G40-intel-w1048576.json`).
- Hop histogram (G120 record): 0 jumps 16,361 (6.66 %), 1 jump 98,198 (39.96 %), 2 jumps 131,201 (53.39 %); one floor: 16,176 (19.75 %) / 65,744 (80.25 %).
  FIELD PREDICTS: a destination uniform over a product of complete graphs K3 x K5 needs 0 / 1 / 2 dimension jumps with probability 1/15, 6/15, 8/15 =
  6.67 / 40.00 / 53.33 % (elementary counting for dimension-order routing, Dally and Seitz 1987), and over K5 alone 1/5, 4/5 = 20 / 80 %; measured within
  0.25 percentage points.
- **Negative / open: the load is uneven.** Inbox per toroid per step across the 15 toroids ranges 5,118 to 27,533 items (5.4x), the same pattern on every
  floor (toroids 1, 2 and 4 hot, 0 and 3 cold: 5,649 / 27,334 / 20,917 / 5,177 / 22,523 on floor 0; 5,512 / 27,489 / 21,264 / 5,079 / 22,576 on the one-floor
  run). Cause as recorded: the home on ring 5 is the residue of the token field, so frequent token classes land on three of the five toroids. FIELD
  PREDICTS: token frequencies are heavily skewed (Zipf 1949), so residues of the token field cannot be uniform. Placing by more rings together (for
  example 5 and 7) is an open decision.

## Presets and the layout/wiring rungs (`harness/part7/ch2-wiring/src/cyclone.rs`, `omni-gpu cyclone --preset G1|G4|G8|G40|G120`)
**Description.** One executable embeds the kernels and lays out and wires a preset natively (resident session, section 3): per unit a T50 hub, 8 harness
buses, the feed, the coupling and, from G40, the ring and routing. A preset stays in the executable only while the rung gate
(`harness/part7/ch2-wiring/cyclone/rung.py`) passes it on both laptop devices. The rung gate checks, over recorded steps, the feed, both ledgers, every weight after coupling and ring (bit for bit)
and, from G40, routing, and writes a record with the defining-parts table. `--slab N` uses the first N floats of each real checkpoint (laptop);
`--slab full` uses all 6,926,912; `--full-state` also allocates every model's measured training state.
**Measured.**
- Laptop, both devices (the folders `docs/appendix/part7/ch2-wiring/results/cyclone/G1/`, `docs/appendix/part7/ch2-wiring/results/cyclone/G4/`, `docs/appendix/part7/ch2-wiring/results/cyclone/G8/`, `docs/appendix/part7/ch2-wiring/results/cyclone/G40/`, `docs/appendix/part7/ch2-wiring/results/cyclone/G120/`): all 13 surviving records pass with every counter 0 (G1 / G4 / G8 with
  full real slabs, G1 also with its full training state, G40 with 1,048,576-float slabs, G120 with 262,144-float slabs). UHD 620 ms per step in the
  surviving records: G1 26.0 (23.2 with the training state), G4 51.1, G8 85.3, G40 216.5 (with routing). **Discrepancy:** earlier runs of the same presets
  are recorded in unpublished project notes as 17 / 41 / 79 / 187 ms, but the files of those runs were overwritten by the later run with routing
  (same file names), so those numbers have no surviving record; a laptop is noisy and the later executable adds checks, so neither set is a benchmark.
- L4 24 GB, full size, real weights (`docs/appendix/part7/ch2-wiring/results/cyclone/pod-l4/`, harness `harness/part7/ch2-wiring/cyclone/pod_rungs.sh` and `harness/part7/ch2-wiring/cyclone/pod_rungs_route.sh`
  driving `harness/part7/ch2-wiring/cyclone/rung.py`): **G40 with every model's full training state: 21.834 GB resident, 25.74 ms per step (25.93 ms with routing), every stream exact,
  routing included.** *What this is and is not:* the 21.8 GB is the training *state allocated*; no training step ran in these rungs (the record's own
  `parts` field says so), and the 25.7 ms is the *wiring* step (feed, T25 and T50 addressing and ledgers, coupling of 277 M weights, routing), not a
  training step. Wiring only: 1.423 GB, 25.52 ms.
- **Failure as registered:** G120 at full size on the L4 (`docs/appendix/part7/ch2-wiring/results/cyclone/pod-l4/G120/G120-l4-full.json`: 4.263 GB resident, 55.77 ms per step, one 3.32 GB slab buffer) passes feed,
  ledgers and routing but its **weight check fails: 830,276,940 mismatched words**; G40 with a 1.1 GB slab passes. The cause was not found: the bisect of
  slab sizes around 2 GB was not run. **Observation, not a diagnosis:** 120 x 6,926,912 x 4 bytes = 3,324,917,760 bytes is above 2^31 - 1 = 2,147,483,647,
  and the training-program builder carries a guard (added 2026-10-09, `harness/part7/ch2-train/gen/train_step.py`) that records that on the A40 a storage binding of
  2^31 bytes or more ran without an error but trained nothing; the G120 weights buffer is of that size on the L4 and its weight check failed while
  everything that does not depend on that buffer was exact. This is consistent with the same effect, and untested.
FIELD PREDICTS: with model state of 0.54 GB each, 40 models need 21.5 GB, so one floor fits a 24 GB card with little headroom (arithmetic from the
footprint record above; the measured 21.8 GB is 1.5 % above it).

## Variations also disclosed (alternatives considered)
1. One process per harness with a GPU matrix-multiply offload behind one lock (built, measured as the as-built baseline: 40 harnesses 15.8 k tokens/s
   against one unit's 15.4 k; `docs/appendix/part7/ch2-baseline/results/train-5x8/table.json`).
2. Model forms: R full models with hub pull ("pull", built and gated, 10.4), and the centre-plus-delta form ("centre", built and gated). A third form
   was offered and is not recorded in the shipped files.
3. Ring coupling: the one-level-up pull used here (K2, K2c); an elastic-averaging step every step against a Nesterov outer step on the mean displacement
   every H steps (designed, not run, 12).
4. Placement of items on the layout: by the token's residue on ring 5 (built, uneven); by more rings together (open).
5. Cuts: Gomory-Hu / guide trees as the verifier and for non-product links (for example several GPUs) against the counter read for product networks (8).
6. Per-block "stations" with weights stationary in shared memory, a local-rule pipeline over micro-batches, and the five batching axes (replica,
   read-out, gradient, token, live-row) of the author's unpublished batching notes: designed only except the replica axis (4, 10.3).
7. Capacity of the hub by a transport rule (Murray, 1926: parent channel cubed = sum of child channel cubed): (8 x 25^3)^(1/3) = 50 gives the unit
   hub from eight T25 harness buses (arithmetic: (8 x 15,625)^(1/3) = 50.0); the same rule gives about 85 rings over five unit hubs ((5 x 125,000)^(1/3) =
   85.5) and about 123 over three floors. **A hypothesis to test against measured hub load, not a decision.**
8. Attention products and GEMMs: folds (kept as the default of the exact gates) against batched register-blocked GEMMs (default in the learning gates) against
   tensor-core GEMMs (10.5): measured, with the bit-identity and speed results given there.

## Designed, not measured
- **Floors as a 6-D torus**: three floors stacked = X x Y x Z, three more flipped and criss-crossed = 6-D; floors currently couple only by routing and the
  weight coupling between floors is undefined; the inter-floor link is the author's to define.
- **The rest of the ring's traffic**: the precompute streams other than coupling (pages, staged offers, live-row lists) are not on the ring.
- **Each harness as its own ring system (5-ring core) on the device**: batch slicing, exact scoring against verified answers, the canary gate, the
  ladder rule, doing decode batched; the day loop stays host control flow.
- **Training-array outer step** (elastic averaging every step against a Nesterov outer step every H steps); **small deltas** (trits plus one scale per
  matrix, an estimated 1.7 MB per harness against 27.3 MB); wiring form 3 into G8 / G40.
- **The measured run against the CPU pod per wall-clock hour** (tier-1 at 0.85 and held-out loss, dollars per round).
- **The deployable**: an executable that picks the tier from the capacity and deploys it (the Linux executable with presets exists; the Windows build
  and the "pick your settings" front end do not).
- **A persistent T50 ring kernel over a mapped ring buffer** (events per second against the CPU core): not built; `ring_addr` is a per-launch kernel.
- **PTX-rendered CUDA kernels for NVIDIA tensor cores**, and drawing the cyclones in the browser from the same video memory: designed only.
- **Docking the SuperSeed**: the cyclone layout replacing the current toroid set of the transformer trunk, each "trainer" slot becoming a core; the slot
  count (one per faculty, or 8 per hub / 40 in all) is undefined.
- **A pressure valve**: render a core (capacity) into a toroid when its saturation is read and release it after; only the dispatch sizing (9) exists.
- **Replica compaction**: dispatch over the active replicas only, so that a step costs what its active slots cost (the array server's open finding, 10.7).

## Open / unmeasured
1. All defining parts together in one run (1.3 item 1); a 40-model array as one resident session (impossible as built: refused by the binding guard; the alternative of
   splitting the logits buffer or the replica axis under 2^31 bytes per binding is untested - probe arm B did not complete); the first array step statistics of a
   40-harness run that finishes a day (launch 1b took steps but no harness finished).
2. The group of 20 misses the 2 % per-harness bar (mean 4.1 %, max 9.7 %, GPU worse on 16 of 20): whether the lag is systematic (half-precision GEMM range, ring pull
   order) or the bar is simply tighter than the engine's own 4.0 % thread-count noise floor. Gate decision (2026-10-09): the 2 % verdict stands as FAIL and the next run is judged
   against the CPU-versus-CPU noise baseline (mean 2.01 %, maximum 3.99 %, plus a one-sided-skew sign test; chapter 1, section 11, G4); that baseline for the same 20
   harnesses with the same ring and switches has not been measured yet and must be first.
3. Compounding across the ring (P6) and the array against the CPU school per wall-clock hour.
4. G120 full-size weight check failure (cause untested; consistent with the 2^31-byte effect: the weights buffer is 3.32 GB); the 80 GB and 96 GB rungs.
5. Split submissions for the laptop tier (4-model school step device loss).
6. Uneven routing load (placement by more rings).
7. Box cuts on the GPU and at 1,155 toroids; the outer-ring counters as a T50 core's own counters; a decision loop that acts on the cuts.
8. Float64 sums in softmax and head (+1.9 % held-out drift); the 2 % per-harness gate against an engine that differs from itself by 4 % (decided 2026-10-09: noise-relative gate for the next run, chapter 1, section 11, G4).
9. The ring coupling rule and constants; their effect on learning.
10. Whether the exact gates survive GPU contention (a baseline step differed under contention, idle bit-identical).
11. Why ten harnesses aborted in growth launch 1b; the cause of the 4 to 9 times longer array steps there than in the isolated group of 20.
12. The T50 CPU gates: the result logs of G1-G4 and the source of the bus probe are not among the shipped files; whether the 22.2 / 29.4 ns scalar-encode rows are the one-call-per-event
    or the batched column; the host load of each run.
13. Evidence status: the numbers labelled unsupported or partial above are recorded in unpublished notes and logs, but the harness or the result file is not among the shipped files; each is labelled in place.

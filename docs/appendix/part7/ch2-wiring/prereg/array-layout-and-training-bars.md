# OMNI-RENDER-GPU-0 — our own Vulkan renderer/compute core for Omni Web + training, built by the cores (claude seat, 2026-10-08)
J 10-08: "should we also make a new cuda/vulkan based renderer for the omnibrowser … better video/rendering capabilities while staying
lightweight and accessible" → Vulkan (cross-vendor, Android; iOS via Metal back-end later), CUDA only as the NVIDIA training fast path, CPU
raster stays as fallback. "no, were just going to build it now with the cores" · "download the documents, I installed. then we'll boot up the
system and have the cores build all they can."
Lineage: `<plan>` (batching axes, stations, R1–R6), `<plan>` + handoff, VOCAB "render", "cyclone".
Clean room: specs are no-train, read for function only; bindings GENERATED from vk.xml (Apache-2.0), no third-party bindings or shader code.

## Ground (10-08)
| Item | State |
|---|---|
| Laptop | Vulkan loader 1.3.275; Mesa ANV (UHD 620, Gen9.5) + lavapipe (CPU Vulkan: runs anywhere); SPIRV-Tools 2025.1 (spirv-val / -dis / -as); vulkaninfo |
| Specs (spec-gather, project omni-render-gpu) | khronos.vulkan-spec · khronos.vk-xml · khronos.spirv-spec · khronos.spirv-glsl-ext · w3c.webgpu · aom.av1-bitstream · ietf.rfc9559 · google.vp9-bitstream (+ existing nvidia.ptx-isa, nvidia.cuda-guide, w3c.wgsl) |
| Existing parts | doctor specs + wall + implementer; gpu.emit (A1 terms → CUDA C, T0/T1/T2); host replay; parity runner; shape station; spec-read; loop.py |
| Omni Web today | CPU raster (raster.rs / paint.rs) → softbuffer + winit; AccessKit; no video; no WebGPU |

## Build (cores do the work; each step = a core with a gate + receipts)
| # | Station / core | What it builds | Gate |
|---|---|---|---|
| V0 | spec-read on the 8 new docs | functional items (Vulkan commands / structs / valid usage; SPIR-V opcodes + operands; GLSL.std.450 ops; WebGPU interfaces; AV1/VP9 decode processes; Matroska elements) | item counts per doc, provenance (sha + licence) |
| V1 | `vk.bind` core: vk.xml → our Rust FFI (types, enums, struct layouts, function pointers loaded via vkGetInstanceProcAddr) | `projects/omni-gpu/src/vk_gen.rs` (generated, deterministic) | regenerate = byte-identical; struct sizes == C layout check (offsetof probe compiled against the loader's vulkan_core.h if present, else our own layout rules from vk.xml) |
| V2 | `vk.run` core: minimal compute runner on the generated bindings (instance → device → buffers → pipeline with specialization constants → dispatch → readback) | `projects/omni-gpu/` crate + CLI `omni-gpu run SPV --buf …` | lavapipe + ANV: a hand-checked copy kernel returns its input |
| V3 | `gpu.emit` SPIR-V back-end: A1 terms → SPIR-V binary (T0 template first; shape constants as specialization constants) | `gpu/emit/spirv.py` (or Rust in omni-render jit) | spirv-val PASS on every emitted module; parity: the 21 parity-verified ops on lavapipe + ANV vs the engine rows (check_host rows) |
| V4 | cooperative-matrix probe: ternary GEMM via VK_KHR_cooperative_matrix (trits as int8) | probe kernel + timing | parity bit-exact on ternary rows; ms vs T0 on ANV / lavapipe (and the 3090 when it runs) |
| V5 | T50 / cyclone ring as a persistent compute kernel over a mapped ring buffer (lane = ring, CRT dispatch) | events/s vs the CPU core | addresses == CPU on recorded traffic |
| V6 | renderer: swapchain present via winit handles; GPU tiles + compositing replacing softbuffer behind a switch (CPU path stays default) | omni-ui `--gpu` | frames == CPU raster (pixel diff ≤ τ) on the corpus pages |
| V7 | video: Matroska/WebM demux (from RFC 9559) + AV1 via Vulkan Video where the driver offers it | `<video>` plays a test clip | decoded frames == reference decoder frames (black-box) |
| V8 | WebGPU (`navigator.gpu`) on our device, WGSL → SPIR-V via our IR | WebGPU conformance subset | pages' compute samples run |
Order: V0 → V1 → V2 → V3 (the loop's main lever) → V4/V5 → V6 → V7 → V8. Every step: ledger entry (gpu/cleanroom), INDEX row, commit on the branch.

## V0 steps (claude seat, 2026-10-08 session 583cbc8f; FULL mode) — worktree `<projects>/ai-stack-opus-gpu` (`opus-gpu/work`, where `bin/spec-read` lives)
Ground correction: laptop Vulkan = **ANV UHD 620 (Vulkan 1.4.318, conformance 1.4) + llvmpipe**, but kernel bash (Tarsus Landlock) cannot open
`/dev/dri/renderD128` (EACCES, jc has the ACL) → inside kernel bash only llvmpipe shows. GPU runs go through `systemd-run --user` / `bin/tw`
units (outside the Landlock domain). No Vulkan headers on disk (`libvulkan-dev` absent) → V1 layout check uses our own rules from vk.xml.
Census (anchor counts, independent of the reader): SPIR-V `<a id="Op…">` 685 · GLSL instruction tables 82 · Vulkan VUID anchors 27,411 ·
Vulkan listing blocks 3,547 · WebGPU `class="algorithm"` 202 · RFC 9559 `id / type:` element records · AV1 syntax tables 131 · VP9 84.
- [x] **V0.1** (DONE 10-08: board OMNI-RENDER-GPU-0 staged; claim on the worktree) board row + claim: `bin/fleet-ratify OMNI-RENDER-GPU-0 staged --title … --brief <this plan>`; `bin/claim claim` on
  `bin/spec-read` + `projects/omni-gpu`. Verify: `sqlite3 control-center/dispatch.db "select status from tasks where id='OMNI-RENDER-GPU-0'"` = staged.
- [x] **V0.2** (DONE 10-08: 13,589 items, every anchor equal, AV1/VP9 TOC coverage 100 %, 10 older docs byte-identical) reader rules in `bin/spec-read` for the 8 formats → kinds: vk.xml {command, struct, union, enum, handle, funcpointer, bitmask,
  extension, feature} · vulkan-spec {command, struct, enum (prototype + params) + valid_usage per VUID owner} · spirv {instruction (opcode,
  word count, operands, capabilities), enumerant} · glsl-ext {ext_instruction (number, operands)} · webgpu {idl, algorithm} · rfc9559
  {element (id, type, path, occurs, range, default, definition)} · av1/vp9 {syntax (table lines + descriptors), process (decoding-process
  sections)}. Verify: `bin/spec-read <8 ids> --out <run dir>` → every doc > 0 items and each kind count == its independent anchor count
  (`projects/omni-gpu/tests/v0_counts.py`, exits 1 on any mismatch).
- [x] **V0.3** (DONE: run1 == run2 for all 8) determinism: two runs → identical `out_sha256` per doc. Verify: `v0_counts.py --twice`.
- [x] **V0.4** (DONE: gate pass 8.2 s; 8 fire receipts pass, caller claude-omni-gpu) register core `spec.read` (cores.db row like `gpu.emit`, gate `bin/core-gates/spec-read.sh` = fixture read + counts), fire it
  for the 8 docs. Verify: `bin/core-registry gate spec.read` pass + 8 fire receipts verdict pass.
- [x] **V0.5** (DONE: ledger hash 20bcce06b199, chain OK; tests/INDEX.md row; commit a3fcdcb60 on opus-gpu/work) record: `ledger.py add --step V0 …` (src = the 8 ids, consulted), `projects/omni-gpu/{README.md,tests/INDEX.md}` row, commit
  on `opus-gpu/work`. Verify: `ledger.py verify` ok; `git log -1` names V0.
## V1 steps — `vk.bind` core: vk.xml → our Rust FFI (no third-party bindings, no Vulkan headers; vk.xml is Apache-2.0 OR MIT)
Selection (`projects/omni-gpu/gen/vk_select.json`): features VK_VERSION_1_0…1_4 (+ their `depends` closure, api "vulkan" only) +
VK_KHR_surface/swapchain/xlib_surface/xcb_surface/wayland_surface (V6) · VK_KHR_cooperative_matrix (V4) · VK_EXT_debug_utils ·
VK_KHR_portability_enumeration · VK_KHR_external_memory_fd (V5). Video extensions wait for video.xml (V7, std headers live there).
Mapping: handles = repr(transparent) newtypes (dispatchable *mut c_void, non-dispatchable u64); value enums = newtype(i32) + module
consts; FlagBits = u32/u64 aliases + consts; structs/unions repr(C) with zeroed Default that presets sType; commands = PFN types +
entry/instance/device tables loaded through vkGetInstanceProcAddr / vkGetDeviceProcAddr; libvulkan.so.1 by dlopen (no link-time dep).
- [x] **V1.1** (DONE 10-08: 663 types, 357 structs/unions, 133 enum groups, 268 commands; cargo build 0 errors / 0 warnings) generator `projects/omni-gpu/gen/vk_bind.py` → `src/vk_gen.rs` + our own C declarations `gen/out/vk_check.h`. Verify:
  two runs byte-identical (sha256) and `cargo build` of the crate: 0 errors.
- [x] **V1.2** (DONE: 2,882 lines 0 mismatches; + 1,149 enum values == the spec's C listings) layout gate `tests/v1_layout.sh`: gcc probe (our C declarations + the system's X11/xcb/wayland headers) vs Rust probe
  (size_of / align_of / offset_of!) for every struct, union and member. Verify: 0 mismatches.
- [x] **V1.3** (DONE: UHD 620 ANV + llvmpipe == vulkaninfo, results/v1/props.json) driver oracle `tests/v1_props.sh`: the generated loader enumerates devices and reads VkPhysicalDeviceProperties (824 bytes,
  filled by the driver) → apiVersion / vendorID / deviceID / deviceName == `vulkaninfo --summary` on llvmpipe AND ANV (ANV through a
  systemd-run unit, outside Landlock). Verify: both devices match.
- [x] **V1.4** (DONE: gate pass 6.7 s, fire pass, output sha bee1446e… = every run) register core `vk.bind` (op gen, gate = V1.1 twice + V1.2) and fire it. Verify: gate pass + fire receipt.
- [x] **V1.5** (DONE: ledger dcc2a0e8427e chain OK; INDEX rows; commit 08c8e9977) record: ledger entry (src khronos.vk-xml consulted), INDEX rows, plan log, commit. Verify: `ledger.py verify` chain OK.

## V2 steps — `vk.run` core: minimal compute runner on the generated bindings
Runner (`src/run.rs` + `omni-gpu run`): instance → device by index / name → one compute queue → N storage buffers (set 0, bindings
0..N-1, host-visible coherent) → shader module → compute pipeline with specialization constants → dispatch → barrier → readback; GPU
time from timestamp queries. Kernel for the gate: our own SPIR-V assembly written from the SPIR-V spec (`kernels/copy_add.spvasm`:
out[i] = in[i] + SpecId 0, local_size_x = SpecId 100, bounds by OpArrayLength), assembled by `spirv-as`, checked by `spirv-val`.
- [x] **V2.1** (DONE: spirv-val vulkan1.1 clean) kernel: spirv-as → spirv-val (target vulkan1.1) PASS. Verify: `spirv-val --target-env vulkan1.1 kernels/copy_add.spv`.
- [x] **V2.2** (DONE: 0 errors / 0 warnings) runner + CLI. Verify: `cargo build --release` 0 errors.
- [x] **V2.3** (DONE: 16/16 byte-exact, both devices; UHD 620 0.72–1.10 ms per 4 MB) gate `tests/v2_copy.py` on llvmpipe AND the UHD 620 (systemd-run): 1M random u32, add = 0 → out == in; add = 7 →
  out == in + 7 (mod 2^32); local size 64 and 256 via SpecId 100. Verify: all cases byte-exact on both devices, results/v2/copy.json.
- [x] **V2.4** (DONE: gate pass, fire exact, ledger cbbac596667b, commit 27cb8392c) core `vk.run` (op run; gate = V2.3 on llvmpipe) + receipts; ledger + INDEX + commit.

## V3 steps — SPIR-V back-end for the emitter (the loop's main lever): the same wall-passed A1 equation specs → SPIR-V, no CUDA
Numbers come from the reader, not a hand table: `projects/omni-gpu/gen/spirv_tables.py` turns spec.read items (685 instructions,
1,116 enumerants, GLSL.std.450) into `gen/spirv_tables.json`. Back-end `projects/thead-trial/gpu/emit/spirv.py` reuses emit.py's
parse + types (one front end, two back ends). T0 lowering: map → one invocation per output element (OpArrayLength bound), fold →
structured loop on Function variables, sel → structured if + OpPhi (no speculative OOB reads), float ops NoContraction, NMin/NMax
(C fminf/fmaxf), OpSRem / OpFRem (C % / fmodf), float literals rounded decimal → f32 exactly; scalar args = specialization constants
(SpecId = arg index; "shape constants as spec constants"), list args = storage buffers, out = last binding, local size = SpecId 100.
- [x] **V3.1** (DONE: 685 opcodes, 1,116 enumerants, 80 GLSL from spec.read items) tables JSON from the reader. Verify: every name the emitter uses resolves; `spirv-dis` of emitted modules names them.
- [x] **V3.2** (DONE: 21 specs — engine0–5 hold 21, not 22; 21/21 spirv-val clean, deterministic) emitter over all 22 specs in gpu/specs/engine0–5. Verify: `spirv-val --target-env vulkan1.1` PASS on every module,
  two emits byte-identical.
- [x] **V3.3** (DONE: 1,764/1,764 rows pass on UHD 620 and llvmpipe; ternary ops bit-exact; worst 0.85 of tol, sgemm) `omni-gpu batch` (many dispatches, one device) + `gpu/emit/check_vk.py`: every recorded engine row (examples + validate +
  holdout) on llvmpipe AND the UHD 620, check_host tolerance. Verify: per-op pass on both devices; failures diagnosed, never hidden.
- [x] **V3.4** (DONE: gate pass 14.4 s, 6 fires pass, ledger d9ec853af58e, commit b87f31264) core `gpu.emit.spirv` (gate = V3.2 + V3.3 on llvmpipe) + receipts; ledger + INDEX + commit.

## V4b + emitter evolution (J 10-08 "continue down the list you can start up a pod")
- [x] **V4b.1** (DONE 10-08: gpu-loop-3090 could not start — host had no free GPU; 3090/4090 out of stock → created `omni-gpu-a40`
  7qp7lp6dfepfuu, NVIDIA A40 (GA102, same chip as the 3090), secure, $0.59/h, env NVIDIA_DRIVER_CAPABILITIES=all; Vulkan needed
  `apt-get install libegl1` (strace: the NVIDIA ICD dlopens libEGL.so.1 before returning vkCreateInstance)) start a pod + Vulkan.
- [x] **V4b.2** (DONE: tern_coop exact on 7 shapes, ≤ 2.97 TOP/s, 2.0–2.8× OpSDot at K ≥ 1024; A40 V1/V2/V3 pass, 1,764/1,764) kernels.
- [x] **V4b.3** (DONE: results pulled, pod stopped — EXITED, disk kept; terminate = J) stop the pod.
- [x] **E1** (DONE 10-08, commit e2dc56e9e: T2 register-blocked GEMM 1.5–3.0× T0 on UHD 620, 47.5 GFLOP/s; loop-invariant hoisting + CSE
  bit-identical, BitLinear ops 150–8,400×; V3 1,764/1,764 both devices) emitter evolution: tiled GEMM by structure + hoisting.
- [ ] **E2** shared-activation staging: compute values that do not depend on the output index (BitLinear's quantised int8 activations,
  rms_row's reduction) ONCE per workgroup into Workgroup memory, then the packed OpSDot form for int8 × trit folds. Verify: v3 parity +
  bl_fwd_row / rms_row ms on UHD 620 + A40 vs E1.

## TRAIN-5x8 — cloud-GPU training run, speed + throughput with the 5×8 layout (J 10-08 "run a training run on the cloud gpu when done")
Readback (VOCAB cyclone, GPU-BATCH-GEOMETRY status log, J-confirmed): 5 units × 8 harnesses = 40 harnesses on one cloud GPU.
What exists (agent report 10-08): a harness = `omni-render thead-learn <build> <heldout> <doing> <out>` (school switches, D 256 L 6 H 4,
B 4 × T 512 = 2,048 tokens/step, ≈1.1–1.4 s/step on 4 CPU threads ≈ 1,450 tok/s); the CUDA lib (GPU-LOOP G4) offloads only sgemm with
M·N·K ≥ 2^28 under one global mutex and was never run under thead-learn; the replica axis (40 harnesses batched in shared launches, R1–R6)
is NOT built. So the run measures the layout AS BUILT (40 processes, CPU engine + GPU sgemm offload) and pairs it with a projection for the
batched layout from measured kernel rates — each labelled.
- [x] **T1** (DONE: A40 host full → A100 SXM 80GB pod 36s5pzl5fsqa3o, 32 vCPU, $1.79/h, ~23 min, stopped) start `omni-gpu-a40` ($0.59/h; 9 vCPU) or create an equivalent; verify nvidia-smi + Vulkan. Verify: `core-host probe`.
- [x] **T2** (DONE: kit + install.sh gates, libs built from engine 272ba650, 64 s) ship: `gpuloop` bundle (engine source + gpu/) + runtime binary + libomnitrain_trial.so + build-v4 tier-1 builds + r16 core;
  build libomnitrain_{cpu,gpu}.so on the pod (`gpu/lib/build.sh`, sm_86). Verify: both .so built; 1 harness smoke (2 wake steps) OK on each.
- [x] **T3** (DONE: 13.3k CPU / 15.4k GPU-lib tok/s) unit run: 8 harnesses (1 unit), 1 thread each, 1 day (20 wake + study + sleep steps), CPU lib vs GPU lib. Verify: per-harness
  s/step from state.json days[].seconds; nvidia-smi samples.
- [x] **T4** (DONE AS-BUILT ONLY: 15.9k / 15.8k tok/s, 5.1 s/step/harness — NOT J's layout, see log) layout run: 40 harnesses (5 units × 8) concurrently, GPU lib, same day. Verify: aggregate tok/s, per-harness s/step, GPU util +
  VRAM, host RAM; `results/train-5x8/` committed.
- [ ] **T5** projection for the batched 5×8 layout: measured kernel rates on the A40 (T2 fp32 GEMM via e1_gemm, coop int8 via v4) ×
  FLOPs per harness-step (from the school shapes) → step time + tok/s for 40 harnesses in shared launches; stop the pod. Verify: report table.

## CYCLONE-ARRAY — the 5-unit training array resident on one GPU (J 10-08, readback confirmed 19:10; replaces TRAIN-5x8 T5)
J's words, verbatim (19:05): "Were making a training array, each unit will have a 50t center, with 8 harnesses around it a model tied to
each. they will be connected and feeding data into they cyclone, the arc reactor evolution. that is one unit. around the one unit, there will
be 5 of those systems spread out around it, touching on the outer ring. they will all be connected by the ring and increasing
resonance/compounding" → (19:10, on the count) "yes, but actually 1 in the center 4 around for a total of 5." · (18:57, confirming the
resident readback) model, harnesses and the T50 ring system in VRAM, training on the GPU: "that was the whole point of fucking moving it to
the gpu and making a kernel". Readbacks are checked against these words, never against a paraphrase (the 10-08 paraphrase "the model and its
8 harnesses" dropped "a model tied to each").

Defining parts — every billable run lists each one PRESENT / PARTIAL / ABSENT in what will actually run; any part not PRESENT is stated to J
and the go asked before the run:
| # | Part | Lineage today (10-08) |
|---|---|---|
| P1 | T50 centre per unit (the cyclone = the arc reactor's evolution), on the GPU | `runtime/src/jit/t50.rs` CPU AVX-512 JIT (14.6 ns/event, T25/T30 exact sub-tori); `ramkit-probes/t50_bus.c` RAM-bus probe (CRT address + RRNS checks). No GPU form |
| P2 | 8 harnesses per unit around the hub | `omni-render thead-learn` processes (school phases, feed, doing decode, T25 bus), CPU |
| P3 | a model tied to each harness (8 per unit, 40 in all), training on the GPU | `omni_train.cpp` CPU engine; GPU = sgemm offload only (GPU-LOOP G4, one mutex) |
| P4 | harnesses + models feed data into the hub; the hub processes, sorts, precomputes (VOCAB arc reactor) | SHM-BUS (`runtime/src/shmbus.rs` B2 + `cloud/bus_coord.py`): weight slabs → mean, L9 coupling K, L13 harmony, residue checks — CPU, /dev/shm; T25 event bus per harness (`t25bus.rs`) |
| P5 | 5 units: 1 centre + 4 around, touching on the outer ring | nothing |
| P6 | all units connected by the ring, resonance compounding across the array | nothing |
| P7 | all of it resident in VRAM | nothing (TRAIN-5x8 T4 had none of it) |

Route — J's standing decisions for training on the GPU (session 653ec8aa, read 10-08 19:20; a route that drops one needs J's word):
1. (10:26 CONFIRMED) the training step = compute passes rendered by OUR renderer, the model's trits, optimiser state and batches in GPU
   buffers, each step a chain of passes with no CPU copies, on any machine's GPU (laptop included); "the ring systems would render no problem";
   the harness fits as its own ring system on the same device (10:27 answer: harness = 5-ring core: batch slicing, exact scoring, canary
   gate, ladder rule; day loop = control flow on the host / page; generators' problem windows uploaded or refilled from arcd).
2. (10:18–10:22) Omniglyph translates the C++ (C++ front end → IR, interpreter correct first, hot ops rendered — the YouTube tiering);
   the GPU is one more back-end of the IR. Gemini GPU 3's nvcc-compile of the engine is the generic version of this — NOT the route.
3. (GPU-BATCH status log, CONFIRMED) ALSO CUDA kernels RENDERED by omni-render (PTX JIT from the IR, cached by program hash) for NVIDIA tensor
   cores; weights stay packed trits.
4. (this plan's header) own Vulkan stack, built by the cores (V0–V4b done: generated bindings, runner, SPIR-V back-end 1,764/1,764 engine
   rows on 3 driver families, int8 tensor cores via cooperative matrix); CUDA only as the NVIDIA training fast path. GPU rental = J's go
   with the hourly price.
| # | Stage | Parts after it | Verify | Where |
|---|---|---|---|---|
| C0 | J's words + this checklist in the plans; VOCAB cyclone row gets "a model tied to each harness" + "touching on the outer ring" | — | this section; VOCAB row | laptop |
| C1 | census: every engine function one school step executes under the school switches (`cloud/school-round.sh` env, r16 core), call counts → port list | — | gcov over a short `thead-learn` day; `projects/omni-gpu/tests/cyclone/c1_census.py` → `results/cyclone/c1/census.json` | laptop |
| C2 | resident model, 1 harness, on our Vulkan stack: `omni-gpu` session mode (device-local buffers that persist across steps; the whole step recorded ONCE as a chain of compute passes and re-submitted each step); every op the C1 census lists rendered by the cores (gpu.emit.spirv from its spec — 21 parity-passed today; the missing ops through the Omniglyph C++ front end → IR → spec → wall → emit); the host feeds token batches and reads the loss | P3 1/40, P7 model | per-op parity (V3 runner) + whole-step loss / gradient parity vs the CPU lib on the r16 checkpoint, 20 steps | laptop UHD 620 + llvmpipe (free); then A40 $0.59/h for speed (J go) |
| C2a | `omni-gpu session` (`src/session.rs`): device-local buffers that persist, passes built once, the step recorded ONCE and re-submitted N times back to back; host crossings only on explicit write / read | — | `tests/cyclone/c2a_session.py`: 2,000 chained passes byte-exact vs the host oracle, both laptop devices → `results/cyclone/c2a/session.json` | laptop |
| C2c | batch + replica axes in the emitter: every template gets grid y = row (N rows per launch) and grid z = replica (8 models per launch), list args strided by spec constants — the row axis turns 2,048 per-row dispatches into one, the replica axis is GPU-BATCH axis 1 | — | batched parity: every engine row of the 21 ops, N rows × R replicas in one dispatch == per-row CPU rows | laptop |
| C2b | NVIDIA fast path: the same IR rendered to PTX by omni-render (GPU-BATCH R1–R3), int8 tensor cores for the ternary GEMMs | — | parity == C2; ms per op | A40 (J go) |
| C3 | unit: 8 models in one process, arrays [replica][…], each kernel's grid z = replica (one launch serves 8); the runtime drives 8 harnesses in lockstep phases; the T50 hub as device kernels (lane = ring, 2 warps): events → T50 address + ledger, SHM-BUS coupling + harmony over the 8 slabs in VRAM | P1, P3 8/40, P4, P7 | 8-replica step == 8 single steps; hub addresses == t50.rs on recorded traffic; coupling == bus_coord.py on the same slabs | pod |
| C4 | array: 5 units (centre + 4), one stream per unit, the outer ring between hubs — PROPOSAL to confirm with J before building: the L9 coupling one level up (each outer hub pulls toward the centre hub, the centre toward the mean of the 4) | P5, P6 | coupling == CPU reference; one school day × 40: tok/s, s/step, VRAM, SM busy | pod |
| C5 | each harness as its own ring system (5-ring core) on the device (J 10-08 10:26–10:27): batch slicing, exact scoring vs the verified answers, canary gate, ladder rule, the T25 bus, doing decode batched (8 × 8 sequences per tick), feed sieve; the day loop stays host control flow | P2 | addresses / scores / decodes == CPU on recorded rows | laptop, then pod |
| C6 | measured run: the array vs the CPU pod per wall-clock hour (tier-1 ≥ 0.85 + held-out), $ per round | all | numbers to J | pod |
Until C5 the harnesses' control loops run on the host (one process drives all 40) with their batches and feeds in VRAM — reported as P2 PARTIAL.

### Capacity tiers + test ladder (J 10-08 ~19:50, readback confirmed; words verbatim)
J: "the readback is correct, we will have different setups based on capacity. lowest is 1 cyclone with model and harness, then it scales
up to 4 at 16 then to 8 on the 32 cpu server which makes 1 unit. . once we get to gpu, it adds more units, a total of 5. with enough
capacity, it adds a layer above, (40gb?) and then it adds a layer bellow (60gb) we will make an exe/deployable that allows you to pick
your settings and deploys." · "will the 80gb fit 4 or would that be in a 96gb?" · "let's test them out. start on a 24gb to get the layout
and wiring right, then keep scaling up marking and recording results."
Measured per model (C0, CPU engine, school settings): 0.538 GB training (0.140 GB kept between steps + 0.398 GB step activations).
| Rung | Layout | Models | VRAM all-at-once / floors in turn | Card |
|---|---|---|---|---|
| G1 | 1 cyclone + 1 model + 1 harness | 1 | 0.5 GB | laptop GPU → 24 GB |
| G4 | 1 cyclone, 4 pairs | 4 | 2.2 GB | 24 GB |
| G8 | 1 unit (cyclone + 8 pairs) | 8 | 4.3 GB | 24 GB |
| G40 | 1 floor: 5 units (centre + 4 around), outer ring | 40 | 21.5 GB | 24 GB (tight) / 48 GB |
| G80 | 2 floors (floor above) | 80 | 43 / 27 GB | 48 GB |
| G120 | 3 floors (floor below) | 120 | 64.6 / 33 GB | 80 GB |
| G160 | 4 floors | 160 | 86 / 38 GB | 96 GB (or 80 GB in turn) |
Every rung records: the defining parts PRESENT / PARTIAL / ABSENT, VRAM used, ms per step, tokens/s, exactness vs the CPU references
(t25bus.rs / t50.rs / bus_coord.py / engine rows), later learning per wall-clock hour. Results → `projects/omni-gpu/results/cyclone/<rung>/`,
INDEX rows, this plan. Deployable (exe: pick the tier, it deploys) = after the GPU rungs run.
24 GB secure stock 10-08 19:55 (RunPod read): 3090 / 4090 / A5000 NONE; L4 24 GB LOW $0.59/h; PRO 6000 MIG 24 GB LOW $0.69/h.

### Model form — the cyclone holds the model, each harness its delta (J 10-09 04:1x: "3 sounds about right. thank you")
J's question: "Do we need to load the model 40 times for my vision to work?" The seat answered no (measured, school dims, one model on the
GPU step: weights 27.3 MB · Adam m,v 54.6 · grads 27.3 · Adam temp copies 81.8 · step working buffers 1,650 MB = 90 %) and offered three
forms; J chose option 3, in the seat's words: "The cyclone holds the shared model, and each harness holds only its small difference from it.
The hub's mean is already computed on the GPU (the hub coupling kernel). Each harness's model is that mean plus its own delta, which could be
ternary or sparse … It keeps per-harness learning and puts the model itself in the cyclone."
Lineage it builds on: SHM-BUS (`cloud/bus_coord.py`, `runtime/src/shmbus.rs`): mean.w of the harness slabs, pull w ← w + K·(mean − w), K by
law L9 (steady spread s* = g / K — the deltas stay small BY the coupling), harmony L13 drops, residue checks L6; GPU form = `hub_mean` /
`hub_pull` (W2b, bit-exact). Field (learn, copy nothing): EASGD (Zhang, Choromanska, LeCun 2015, arXiv 1412.6651 — workers tied to a centre
variable by an elastic force ρ; the centre moves toward the workers); DiLoCo (Douillard et al. 2023, arXiv 2311.08105 — inner AdamW per
worker, outer Nesterov step on the mean displacement every H steps); BitDelta (Liu et al. NeurIPS 2024, arXiv 2402.10193 — a fine-tune's
delta as sign bits + one scale per matrix, one base shared by many deltas, linear = base part + delta part).
Form: W_h = C + Δ_h. C (one per unit, resident in the cyclone) = the model; Δ_h (one per harness) = its own learning. Forward of harness h
reads C + Δ_h (fused into the weight quantizer tq / wf: trits of the SUM, absmean of the sum). Each harness's gradient updates its Δ_h; the
cyclone moves C by the harnesses' mean displacement and the coupling shrinks every Δ_h (Δ_h ← (1 − K)(Δ_h − mean Δ) keeps C = the exact
mean). The floor ring couples the 5 units' C the same way one level up (centre C ↔ mean of the 4).
| # | Step | Verify | Where |
|---|---|---|---|
| M0 | buffer reuse in the step (lifetime planner: a transient buffer shares memory with any buffer whose passes it never overlaps; weights, moments, host-written and read-back buffers pinned) — needed by every form | `tests/train/s2_replica.py` A (bit-identical per replica) + B (learning) still pass; bytes per model recorded, target ≤ the CPU engine's 0.398 GB of step activations | laptop |
| M1 | centre + dense delta, exact form: C once per unit, Δ_h per harness, forward on C + Δ_h, inner AdamW on Δ_h, C ← C + mean(ΔΔ), coupling K on the deltas | learning == the option-1 run with hub pull at the same K (held-out within 0.5 %), 8 harnesses, 100 steps, real batches | laptop → L4 |
| M2 | the cyclone's outer step: EASGD every step vs DiLoCo (Nesterov on the mean displacement every H steps) | held-out per wall-clock vs M1 | L4 |
| M3 | small deltas: Δ_h as trits + one scale per matrix (BitDelta form on our ternary substrate, 1.7 MB per harness vs 27.3 MB), the residual kept for error feedback | held-out within an agreed band of M1; bytes per harness | laptop → L4 |
| M4 | the form wired into G8 / G40 (feed_win → each harness's batch; the hub slab = C) | the preset trains; parts table updated | L4 |

Checkpoint: resume at the first unchecked V0.x; outputs land in `projects/omni-gpu/results/v0/` (counts JSON, kept) and
`research/specs/<id>/read.jsonl` (regenerable, not committed).

## Status log
- 2026-10-08 plan written; specs registered + fetching; spirv-tools installed by J.
- 2026-10-08 V0 prep: 8 docs fetched (~60 MB) + verified ok; spec-read has no rules for them yet (0 items) → V0 = teach the reader these formats (Vulkan refpages / SPIR-V opcode tables / GLSL.std.450 table / WebGPU WebIDL / AV1 + VP9 syntax + decoding sections / Matroska elements).
- 2026-10-08 (claude seat, Opus 5.5, session 583cbc8f) V0 DONE: `spec.read` core reads the 8 documents → 13,589 functional items
  (vk.xml 5,191 · Vulkan spec 5,496 incl. 27,411 VUIDs in 2,245 groups · SPIR-V 685 instructions + 1,116 enumerants · GLSL.std.450 80
  (the document skips 47) · WebGPU 131 IDL + 202 algorithms · Matroska 154 elements · AV1 122 syntax / 111 semantics / 133 process ·
  VP9 83 / 42 / 43). Gate `projects/omni-gpu/tests/v0_counts.py --twice` (tw `omni-gpu-v0`): reader == anchors, deterministic.
  Parameter lists: 766/782 Vulkan commands, 1,338/1,388 structs (the rest have none in the spec, e.g. vkGetDeviceProcAddr).
  Friction: PDF table rows ("7 SCALABILITY_S2T3") read as chapter headings until headings had to follow in sequence; GLSL "1..N" rule
  was wrong (47 absent); my first `<feature>` anchor also counted feature requirements. ANV visible only outside kernel bash (Landlock).
  Commit a3fcdcb60 (opus-gpu/work). Next: V1.
- 2026-10-08 (claude seat, Opus 5.5) V1 DONE: `vk.bind` core (`projects/omni-gpu/gen/vk_bind.py`) → `src/vk_gen.rs` (391 KB) + dlopen
  loader + `omni-gpu devices`. Gate: deterministic; gcc vs rustc 2,882 layout lines identical; 1,149 enum values == spec listings
  (khronos.vulkan-spec read through spec.read items as the value oracle — ledger lists it under "cited"). Driver oracle on BOTH devices
  == vulkaninfo. Friction: the kernel write tool's grounding gate re-armed mid-step (fleet_kb_search consult needed again).
  Next: V2 (compute runner + copy kernel on llvmpipe + ANV).
- 2026-10-08 (claude seat, Opus 5.5) V2 DONE: `vk.run` core = `omni-gpu run` on the generated bindings; hand-written SPIR-V copy_add
  kernel byte-exact in 16/16 cases on UHD 620 + llvmpipe. Next: V3 (SPIR-V back-end of gpu.emit from the A1 equation specs).
- 2026-10-08 (claude seat, Opus 5.5) V3 DONE: the loop's main lever — the same 21 wall-passed engine specs now run on Vulkan through our
  own SPIR-V back-end (numbers from the reader), 1,764/1,764 recorded engine rows on BOTH laptop devices, ternary ops bit-exact.
  Measured for V4 (vulkaninfo, both devices): NO VK_KHR_cooperative_matrix on UHD 620 or llvmpipe (Mesa 25.2.8); both have
  VK_KHR_shader_integer_dot_product + shaderInt8 (packed 4×int8 dot) and subgroup size control; no Vulkan Video decode on this laptop
  (V7 decode = software path first, Vulkan Video where a driver offers it). V4 → V4a integer-dot ternary GEMM here (no cost);
  V4b cooperative matrix on the 3090 = J go + $0.50/h.
- 2026-10-08 (claude seat, Opus 5.5) V4a DONE: ternary GEMM on the integer dot-product path — `kernels/tern_dot.spvasm` (packed 4×int8
  OpSDot) exact in 16/16 cases on UHD 620 + llvmpipe, 2.1–4.2× the scalar multiply-add, UHD 620 17–22 GOP/s (naive kernels, no
  tiling); runner now enables the device's core 1.1–1.3 features. Commit aafa5ded6. Wrap-up: MANUAL `docs/systems/omni-gpu/`,
  <devlog-entry>..3, FLOOR entry `omni-gpu` (PASS, fails under mutation), handoff `OMNI-RENDER-GPU-0.handoff.md`.
  Open: V4b (cooperative matrix, 3090 = J go), V5 T50 ring kernel, V6 renderer, V7 video, V8 WebGPU; emitter evolution: tiled
  SPIR-V templates + a dot-product template recognised by structure for BitLinear rows.

- 2026-10-08 (claude seat, Opus 5.5) V4b + E1 DONE (J: "continue down the list you can start up a pod"). V4b: gpu-loop-3090 could not
  start (host full; 3090/4090 out of stock) → A40 pod omni-gpu-a40 ($0.59/h, ~12 min, stopped); NVIDIA Vulkan in the container needed
  NVIDIA_DRIVER_CAPABILITIES=all + libegl1 (strace); A40 passes V1/V2/V3; tern_coop (16×16×32 int8 tensor cores) exact, ≤ 2.97 TOP/s,
  2–2.8× OpSDot. E1: T1 shared tiles ≈1× (bit-identical), T2 register blocking 1.5–3× (Fma, within reference), hoisting/CSE: first
  version hoisted nothing (it refused a reduction's own binders) — fixed with free-binder analysis + binder-independent keys →
  150–8,400× on BitLinear ops. Friction: edited spirv.py while a parity run used it (re-ran for clean provenance); unhoisted baselines
  hit the Intel GPU watchdog (VK_ERROR_DEVICE_LOST) and are recorded as such. Open: E2 (shared staging + OpSDot form), V5–V8 order (J),
  /dev/dri in Tarsus (J).
- 2026-10-08 (claude seat, Opus 5.5) TRAIN-5x8 ran the AS-BUILT baseline (results/train-5x8/table.json, commit on opus-gpu/work): every
  harness a CPU process, GPU lib = sgemm offload under one mutex; 40 harnesses 15.8k tok/s ≈ one unit's 15.4k, GPU adds nothing at 40.
  MISS (J 10-08: "I thought the harnesses and the model were going to be in the vram … did you put the 50t ring system inside?"): J's 5×8
  layout = T50 cyclone hub + model + 8 harnesses RESIDENT IN VRAM per unit (VOCAB cyclone); the run measured something else under that
  name and the seat did not say so before spending pod time. Remedy (to brainstorm with J): before running a named layout / design,
  list its defining parts (VOCAB + plan) and check each is present in what will run; any missing part is stated and the go asked first.
  Readback of the resident design sent to J; T5 (projection) replaced by building the resident layout after J's "correct".
- 2026-10-08 (claude seat, Opus 5.5) CYCLONE-ARRAY: J's layout words recorded verbatim + defining-parts checklist (P1–P7) + J's
  standing route decisions (10:26 rendered compute passes, Omniglyph translates the C++, CUDA PTX fast path, own Vulkan stack); VOCAB cyclone
  row extended ("a model tied to each" = 40 models); PROCEDURES failure row (named-design run without its parts). C2a DONE: `omni-gpu
  session` — device-local buffers persist, the step recorded once and re-submitted; 2,000 chained passes byte-exact on llvmpipe + UHD 620,
  UHD 620 0.45 ms per resident pass vs 6.0 ms one-shot (13×). C2c DONE: emitter template T0B (`spirv.py --batch`: gid.y = row, gid.z =
  replica, strides as spec constants, stride 0 = shared weights) — 21/21 ops, 1,932 rows in 933 launches per device within tolerance
  (worst 0.85 = V3). Commit 4e6fa78a2 (opus-gpu/work); ledger CYCLONE-C2a/C2c, chain OK. C1 census: first two runs too slow under coverage
  with 4 threads (counter contention); re-run single-thread on the laptop (tw cyclone-c1c) because every pod is stopped, the seat's CPU pod
  included — PROCEDURES "pod first" exception, stated. Parts after today: none of P1–P7 present yet (C2a/C2c are the vehicle: residency + the
  replica axis in the emitter).
- 2026-10-08 (claude seat, Opus 5.5) CYCLONE W1 + W2 LOCAL DONE (J: "get the layout and wiring first … local", no pod): five kernels written
  by hand from the SPIR-V spec — ring_addr (omniring addressing, lane = ring; T25 per harness bus, T50 per unit cyclone; twist vs the staged
  plate, per-ring ledger, deviation masks), hub_mean / hub_pull (cyclone coupling, bit-exact to bus_coord.py / shmbus.rs), feed_win (harness
  batch slicing == Build::win), ev_build (the trunk's T25 events). Gates: W2a 81,920 real events 0 mismatches vs the runtime's rendered T25
  core; W2b 55.4 M real weights (8 live-r14 harnesses, full) + the floor ring over 40 real checkpoints bit-exact; W2d the chained feed →
  events → T25 + T50 exact. Rungs (`tests/cyclone/rung.py`, one recorded step each): G1 / G4 / G8 full real weights, G40 one floor with the
  ring (1 M-float slabs), G1 with its full training state — all exact on llvmpipe + UHD 620; UHD 620 ms/step G1 17 · G4 41 · G8 79 ·
  G40 187. Parts: P5 PRESENT; P1 / P2 / P4 / P6 / P7 PARTIAL; P3 (models TRAINING on the GPU) ABSENT. Commit ee8f37c9c (opus-gpu/work).
  Not built: the floor link between floors (J to define), the other precompute streams on the ring (pages, staged offers, live-row lists),
  the model training step on the GPU (C2), the harness core on the GPU (C5). No pod started (J: launch only on approval).
- 2026-10-08 (claude seat, Opus 5.5) J: "continue onto the gpu starting with the 24gb and going up as layers and wiring cements, saving each
  setting/preset to an exe the layers connect in the same way our arc connector moves up and down, any time a process/step fires, it can find
  it's way to where it needs by jumping from toroid to toroid, each ring interconnects with every other toroid" + `<home>/Downloads/Toroid array.txt`
  (Seed of Life 8-fold, 1 + 4 around, torus networks: direct network, dimension-order routing, CAN/Chord, Tofu 6-D). Readback sent (direct
  torus network; coordinates = residues, ring = dimension; a fired step jumps toroid to toroid ring by ring to its address; floors link like
  the arc's tiers; 3 stacked floors = X·Y·Z, 3 more flipped + criss-crossed = 6-D) — PENDING J's "correct". EXE: `omni-gpu cyclone --preset
  G1|G4|G8|G40` (src/cyclone.rs, kernels embedded, layout + wiring native; rung.py now checks the exe) — 10/10 local runs exact (exe
  df98b36cb7e4, commit eb9636ae0). POD: create-pod for the L4 (24 GB, $0.59/h, approved by J) was DENIED by the app's auto-mode classifier —
  not worked around; `tests/cyclone/pod_ship.sh TARGET PORT L4` + `pod_rungs.sh` ready (ship exe + gates + curriculum + T25 core + 40 real
  checkpoints, run G1→G40 full size + full training state under tritwatch on the pod, pull records).
- 2026-10-08 (claude seat, Opus 5.5) J: "build the fucking training step". C2 S1 DONE — the THEAD training step on the GPU: forward + tied
  head + backward + AdamW of one model (plain trunk, school switches off), 39 kernels rendered by our emitter from equations of OUR engine
  (gen/train_kernels.py; GEMMs = the wall-passed sgemm specs, template T2) + float64 hand kernels (BitLinear scale, clip norm: split
  reductions), one recorded step re-submitted with host-fed batches (session stepwrite / stepread). Gates vs the CPU engine on the same model +
  batches: gradients cos ≥ 0.999998 (school dims); 100 school steps on the L4: loss 9.19 → 1.94 (GPU) / 1.95 (CPU), held-out 1.559 / 1.530;
  87.2 ms per full step vs 734 ms CPU (4 threads) = 8.4× per model. Profile: attention scores 33 %, GEMMs 26 %. Commit efe4cd6d6. L4 stopped
  (~47 min). G120 full-size weight check failed (3.3 GB slab buffer, everything else exact) — bisect at the 2 GB boundary pending.
  NOT yet: the replica axis in the training kernels (40 models per launch), the school switches (T25 clock, plates, port, local rule,
  routing, harmony, P3), float64 sums in the softmax / head (the +1.9 % held-out drift), the harness core on the GPU.
- 2026-10-09 (claude seat, Opus 5.5) C2 REPLICA AXIS + M0 + M1 DONE (board OMNI-RENDER-GPU-0-C2R). Replica axis: every training kernel
  emitted batched (T0B; GEMMs T2B: replica = WorkgroupId.z), float64 reductions per replica (red_part / red_fin / adam_scal z-aware); R models
  in ONE recorded step, each bit-identical to its solo GPU run (losses + every weight word), each learning like its CPU engine (s2_replica,
  llvmpipe + UHD 620; UHD 620 1.83× vs 3 separate runs). J: "Do we need to load the model 40 times for my vision to work?" → no (weights 27 MB
  of a 1.84 GB step); J chose option 3 (§ Model form). M0: lifetime planner + one arena of offset views (`buf view`, session.rs) + head
  gradient in place + relu² / scores recomputed → school 1.84 → 0.35 GB per model (option 3: 0.38 GB at 8 harnesses), every value
  bit-identical; 40 harnesses ≈ 15 GB (estimate from the planner, not yet run at R = 40). M1: `form=pull` (R models + hub_mean / hub_pull
  every step) matches 4 CPU engines + the SHM-BUS sync (held-out ≤ 0.03 %, spread equal); `form=centre` (C once, Δ per harness) matches pull
  (held-out ≤ 0.02 %, step loss ≤ 0.02 %) on llvmpipe + UHD 620. UHD 620: one school model 4.9 s / step (CPU engine 2.8 s), a 4-model school
  step = VK_ERROR_DEVICE_LOST (driver hang timeout on one long submission → split submissions, open). Commit 57387bef8 (opus-gpu/work).
  Parts: P3 PARTIAL (R models train on the GPU in one step, option 3 form built; not yet run at school size R ≥ 8 on the L4, not wired into
  the presets, school switches absent). Next: L4 tokens/s R = 1 / 8 / 24 / 40 (J's go), M3 small deltas, M2 outer step.

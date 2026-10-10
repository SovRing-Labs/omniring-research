# GROW-RUN-0 — the self-evolving growth run on the GPU, tier by tier (claude seat, Opus 5.5, 2026-10-09)

## J's words (verbatim; readbacks confirmed 10-09)
- "yes, is the curriculum autogenerator ready? we should have a few backups of the end of elementery. we'll make a copy and use it through
  out the runs for growth testing through gpu size(24gb -96gb)"
- "growth rate: how much each run progresses the model at every tier. have it set so that it autocreates it's curriculums, only passes
  staage when it masters every skill in that tier to 100, once it finishes middle school, it can start growing it's own parameters. have it
  auto save checkpoints to backup every so often, it will grow extremely quickly during these runs. we need to set this structure so it can
  evovlve itself as it needs. it may be off intuitive but it will show something important."
- readback 1 → "correct, and once it's ready it switches to growing parameters, then back to growing skills, eventually growing new
  generators. I think this model will go very far tonight."
- "the runs will happen on gpu from our current choice and up" → readback 2 → "correct"
Confirmed design: every growth run on the GPU, from the 24 GB card (L4) up through 48 / 80 / 96 GB, each starting from the frozen round-12
copy; growth rate = how much one run moves the model at each tier; the planner writes every round's curriculum; a school stage (pre-K, K,
elementary, middle) passes only when EVERY skill in it scores 100 % on held-out (current score, not sticky); after middle school the run
alternates — grow parameters, then back to growing skills — and later grows new generators; checkpoints back up automatically on a schedule;
the loop adjusts itself with no seat stepping in.

## Grounded facts (10-09)
| Item | State | Source |
|---|---|---|
| Frozen start | `runtime/results/growth-base/r12-elem/` (read-only, MANIFEST.sha256): r12 core 5b1c9c11… + school state + T25 core | made 10-09 |
| r12 at the 100 % gate | pre-K 10 / 85 skills at 1.0 · K 4 / 61 · elementary 0 / 20 · bridge 2 / 15 (0.85 sticky gate: 52 / 47 / 13 / 14 mastered) | school-state-r12.json |
| Curriculum autogenerator | `harness/school_graph.py plan|update` + `cloud/school-compile.sh` (circular splice) — ran r1–r16; plans r13 from the r12 state (28 frontier, 126 review); GATE 0.85 global + sticky mastery; WALL = 3 rounds flat; high-school rungs A, C–J UNBUILT | probe 10-09 |
| School step switches (school-round.sh) | PLATES=31 PLATES_ATTN=1 ROUTER_SIMPLEX=1 ROUTER_CE=0.5 VOICE=1 HARM=1 POINTER=5 COPY=6 T25_CORE=1 P3=1 (+ wake / doing / study / sleep) | cloud/school-round.sh:9-12 |
| GPU step today | plain trunk + replica axis + option-3 centre/delta form (C2 S1/S2, M0, M1) — none of the school switches | omni-gpu RESULTS § 4, 4b |
| Port list (C1 census, one school day) | t25_fill / t25_at (rot), plate_on / mem_fwd / mem_bwd / mem_bucket / mem_layer / mem_init_planes / plate_fwd / plate_bwd / plate_core_fwd / plate_core_bwd / plate_flush, harm_weights, port_fwd / port_bwd, copy_fwd / copy_bwd, head_any (pointer head), local_readout, route_check (+ bootstrap exits), P3 mask, row_cos, softplus | results/cyclone/c1/census.json |
| Day time split (CPU, census) | wake 25.4 s · study 16.0 s · sleep 13.1 s · doing 3.0 s · retry 1.6 s → training 91 %, decode 9 % | census day_seconds |
| Parameter growth | om_set_active grows ACTIVE blocks inside the born allocation only (r12 born L = 6, all active → no room); thead-grow (bigger checkpoint) NOT built (SEED-SCHOOL-GROW-0 S1) | omni_train.cpp:2734 |
| Pods | L4 bulh6ewiyjy7a6 cannot start (host has no free GPU); creating a new L4 was DENIED by the app's auto-mode classifier (not worked around) | 10-09 |

## Defining parts for a GPU growth run — PRESENT / PARTIAL / ABSENT (stated to J before any billable run)
| Part | State |
|---|---|
| frozen r12 start | PRESENT |
| auto curriculum per round | PRESENT (CPU planner + compile; feeds builds the GPU step can read) |
| 100 % stage gate (current score, every skill of the stage) | ABSENT (GATE 0.85, sticky) → G1 |
| school training step ON THE GPU with every school switch | ABSENT (trunk only) → G2 |
| harness loop (wake / doing / study / sleep / retry, skill eval) with its training on the GPU | ABSENT → G3 (host drives; decode on host = 9 %) |
| auto checkpoint backups on a schedule | PARTIAL (every round's core, last 5 kept) → G1 (permanent keeps every N rounds / stage pass / growth) |
| growth rate per tier (metrics) | ABSENT → G1 |
| alternation skills ↔ parameters after middle | ABSENT → G4 (needs thead-grow) |
| growing new generators | ABSENT → G5 (hook: on a wall that growth does not lift) |

## Steps (each with its verify)
| # | Step | Verify | Where |
|---|---|---|---|
| G1 | controller: `GROW_GATE=1.0` stage rule (a stage passes when every skill's CURRENT held-out = 1.0; next stage unlocks then; slipped skills return to the frontier), growth metrics row per round (skills at 1.0 per stage, held-out, tokens, wall s, params, tier), permanent keeps (every K rounds + each stage pass + each growth) with sha256, mode decision row (skills / params / generators) | planner dry runs from growth-base: stage = pre-K until 85 / 85 at 1.0; a synthetic eval with all pre-K = 1.0 unlocks K; growth.jsonl rows | laptop |
| G2 | school switches in the GPU step, one at a time, each vs the CPU engine's om_grad with that switch on (s1_grad --switch): T25 clock → plates (+ memory planes) → port / router → pointer + copy heads → harmony → local rule + depth routing → P3 mask | per switch: loss Δ ≤ 1e-4 rel, every gradient cos ≥ 0.9999; then all switches together (= school-round.sh env) on the r12 core | laptop (llvmpipe + UHD 620) |
| G3 | training on the GPU inside the harness: a GPU engine library with the engine's C ABI (training calls run the resident step; every other call goes to the CPU engine with weights synced) so `thead-learn` runs unchanged (OMR_TRAIN_LIB); then harnesses in lockstep in one process (replica axis / option 3) | one school day on the GPU == the CPU engine's day on the same build (held-out ≤ 2 %, skills at gate equal ± 2) | laptop → L4 |
| G3b-1 | FIRST (PROCEDURES 2026-10-09 ordering row) — one UNIT training resident at school size: replica step (R = 8 models, one GPU step) then option 3 (the cyclone holds C, each harness Δ_h) | `tests/train/s2_replica.py --dims school --R 8` (each replica bit-identical to solo + learns like the CPU engine) · `s3_centre.py --dims school --R 8` (centre vs pull vs 8 CPU engines + SHM-BUS sync) | A40 |
| G3b-2 | the school switches inside the R-model centre step (`build_loop(form="centre", sw=…)`, the G2 switches) | centre + switches vs 8 CPU engines with the same switches (held-out ≤ 2 %) | A40 |
| G3b-3 | the ARRAY: per-unit groups (5 units × 8) + the floor ring inside the training step (hub_mean groups, centre unit ↔ 4 around) | 40 models resident (VRAM measured) == the cyclone W2b/W2c coupling bit-exact + each unit learns like its CPU reference | A40 |
| G3b-4 | the school drives it: a resident step server (`omni-gpu serve`, the R-model session) that every unchanged thead-learn process's GPU library submits its om_train_step to; the server steps when all R batches are in (lockstep days, as par_merge) | one 8-harness school day through the server == 8 single-harness days (held-out ≤ 2 %) | A40 |
| G3b-5 | school-round uses the server in place of per-harness training (GROW mode, from growth-base) | g3w round on the pod with SERVER=1: the stage / rows / keeps / ledger gate + VRAM measured | A40 |
| G4 | thead-grow: depth stacking (trained blocks kept, new blocks born silent: o + down zeroed), width later; the controller alternates after middle | loss identical before / after on the same batch; the run resumes | laptop |
| G5 | generator growth hook: on a wall that a growth does not lift → `reason-gen evolve` on the evolvable domains + a proposal for new generators (VOCAB "the 26": a NEW faculty needs J's admission) | decision rows + J sees proposals | laptop |
| G4c | T50 interlock probe (J 10-09 confirmed; checkpoint § 8.2): the array is a Cartesian product K3□K5 (floor ring × unit ring); field kin: Klavžar–Špacapan — a min edge cut of G□H is TRIVIAL (one vertex) or the preimage of a FACTOR's min cut. The route kernel already fills, in the same pass, a source × destination table per ring (`link[d][from][to]`, source-addressed) and the destination ledger (`hled`, destination-addressed) = the two interlocked T50 ledgers. Candidate cuts read from those counters (singletons + every ring bipartition) → all-pairs min cut, vs Gomory–Hu | `tests/grow/g5_t50_cuts.py <G120 record>`: same global bottleneck as g4 (f1u1–f1u3, 27287) and all 105 pairs equal; robustness on 200 seeded dimension-order-routed traffic fields; time per recompute vs GH at 15 / 105 / 1155 toroids | laptop |
| G6 | runs: tier 24 GB (L4) → 48 → 80 → 96 GB, each from growth-base, growth rate recorded per tier | growth.jsonl per tier, keeps, report | pods (J's go + price) |

## Status log
- 2026-10-09 plan written; growth-base frozen (MANIFEST verified).
- 2026-10-09 ~22:45 PDT (claude seat) G1 DONE: stage mode (GROW_GATE; every built skill of a stage at the gate NOW, slipped skills return, next stage
  previewed), PAC sample size (≥ ⌈ln(1/δ)/ε⌉ independent held-out rows per skill, default 300; skill_eval counts rows; held-out sized per skill —
  3.98M tokens / round from r12), grow_ctl (growth-rate rows, permanent keeps every 5 rounds / stage pass / growth, skills → params → generators,
  double-descent grace), hash-chained provenance ledger + verify, min-cut weighting of the frontier (g4: pre-K cut = pk.echo@1, gates 84).
  Gate tests/grow/g1_controller.py 14/14. KB: <notes>/THEAD/PROVENANCE-CONCEPTS-2026-10-09.md (J's Provenance.txt + prov 2.txt).
  G2 DONE: the school step on the GPU — every school switch as passes (100 kernels), each gated vs the CPU engine with that switch on; all
  together 80 real steps held-out 2.7237 GPU vs 2.7268 CPU (omni-gpu RESULTS § 4c, INDEX). The doctor's source reader found 0 functions in
  omni_train.cpp (Rust / JS only) → the port was written directly from our engine. Step 4 (g4 cuts): G120 array hottest = floor 1↔2 links,
  GH global min cut f1u1–f1u3. Commits opus-gpu/work efd1dd570 … e6a8aa1d4. NEXT: G3 (the GPU step inside thead-learn: an engine library
  with the same C ABI, training on the GPU, decode on the CPU with weights synced), G4 (growth tool), then the L4 run (pod: J creates — the
  app blocked create-pod).
- 2026-10-09 ~23:20 PDT (claude seat) G3 DONE for one harness per process: `libomnitrain_gpu.so` (engine-gpu/, the engine's C ABI with
  om_train_step on the GPU; switches recorded + forwarded; weights in / out per step; moments follow snapshot / restore; CPU fallback for
  uncarried switches) — gate g3_engine_lib 40 steps PASS; ONE thead-learn school day (unchanged harness, D 64 L 4, elementary-v1, UHD 620) vs the
  CPU engine: wake 7.697 / 7.690, study 5.304 / 5.296, sleep canary 6.296→6.185 / 6.278→6.171 (results/grow/g3/day). J confirmed the T50
  interlock readback ("interlocking two 50t omniring systems … outer rings counting" → VOCAB row) → probe = NEXT 2 in the checkpoint.
  PROCEDURES row 2026-10-09 (read + probe a named system before answering about it). Checkpoint `<notes>/worker/claude/GROW-RUN-0.CHECKPOINT.md`,
  handoff `GROW-RUN-0.handoff.md`. Commits opus-gpu/work e8395e779, 254060b70.
- 2026-10-09 ~23:20 PDT (claude seat, session resume) G4c T50 interlock probe DONE: `tests/grow/g5_t50_cuts.py` (tw g5-t50-cuts). The route
  pass's own counters (link[d][from][to] source-addressed + hled / inbox destination-addressed) → trivial + factor cuts from Σm tables
  (Klavžar–Špacapan) → every pair's min cut: G120 105/105 = Gomory–Hu, global min 27,287 = g4; 200/200 routed fields; 105 toroids 5,460/5,460
  (21× GH); 1,155 toroids 60/60 sampled + Stoer–Wagner (1.6 s vs GH ≈ 104 s). Blind spot found + closed: a HOT CLUSTER (box of toroids
  saturated outward) beats the ring family (85/100) → sub-torus box cuts from the full table (the outer rings, residue = address) → 100/100.
  Open: box search at 1,155 (enumeration Π(2^m − 1)); tables on the GPU. J's JIT doc reviewed → `<notes>/THEAD/JIT-T50-CONCEPTS-2026-10-09.md`
  (pressure valve = indirect dispatch sized by the counters; prediction = the planner's next curriculum; forge = option 3 C + Δ).
- 2026-10-09 ~23:45 PDT (claude seat) G4c-GPU DONE: route.spvasm fills rtab / vtab with its own atomics; cuts.spv (our emitter, gen/cut_kernels.py) writes every
  toroid pair's min cut each step. Gate rung.py G40 + G120: tables + cut table = CPU ref, cut = Gomory–Hu, 0 mismatches; cut pass 0.94 ms (llvmpipe), route
  atomics no measurable cost (A/B 84–118 vs 89–92 ms, step 340 / 340). omni-gpu RESULTS § 4e, MANUAL row CUT READ. Commit opus-gpu/work (this entry). NEXT: indirect dispatch.
- 2026-10-09 ~00:10 PDT 10-10 (claude seat) JIT-T50 #1 DONE: toroid mailbox (mb_count / scan / scatter) + consumer by vkCmdDispatchIndirect sized on the GPU
  (Session::pass_indirect). rung G40 + G120: every mailbox check 0, mailbox ledger = route hled; G120 3,848 workgroups by load vs 6,465 fixed worst-case.
  omni-gpu RESULTS § 4f, MANUAL row. NEXT: GROW mode wired into school-live with the GPU library.
- 2026-10-09 ~01:40 PDT (claude seat) A40 pod (J: "do l4" → L4 host had no free GPU → A40 7qp7lp6dfepfuu, $0.59/h). Step 3 wiring gate PASS on the pod
  (compile + GPU-library training + eval on the A40; stage fields, rows, growth row, keep, ledger, growth-base intact). G3b (first, PROCEDURES ordering row):
  G3b-1 PASS — school-size replica step, 8 models in one GPU step: 2.78 GB, 518 ms vs 1,238 ms per model on the CPU engine, each replica bit-identical
  to its solo run, held-out within 0.02 %; centre form (the cyclone holds C, 8 harness Δ): 3.03 GB, 521 ms per unit step vs 6,591 ms (12.6×), within 0.06 %.
  G3b-2 (unit + every school switch, school size): learns (9 → 2) but per-harness held-out off by up to 6 % (mean 0.24 %); CPU-vs-CPU noise floor with the
  switches (threads 4 vs 2): up to 4.0 % per harness, losses split at steps 4–8 → the 2 % per-harness bar is tighter than the engine reproduces itself
  (gate change put to J). G3b-3: build_loop(units, ring) — one C per unit (wsum_g / dset_g), unit means + floor ring on hub_mean / hub_pull; small:
  array == separate units bit for bit (with switches too), ring learns like the CPU reference. School 5 × 8 (40 models) first trained NOTHING: the
  transient arena was one 10.9 GiB allocation, over the A40's 0xFFE00000 maxMemoryAllocationSize → arenas capped at 3.5 GiB (programs under the cap
  byte-identical); 40-model run re-gating. G3b-4 PASS — the ARRAY SERVER (omni-gpu serve, src/array.rs; engine library client mode): h0's school day
  through the server == solo, 351 / 351 leaves; server 55 steps, 1.9 / 2 slots per step. G3b-5: school-round ARRAY_SERVER=1 wired.
| 2026-10-09 11:40 | G6 decode-in-server | fc0cf307b/fbf332caa: decode in the array server on queue 2 (one GPU context); D2 PASS (4 clients, 1,536/1,536 top-1 each, exits 95/96, 0 fallbacks). Run 2 stopped (141 tok/s). Run 3b (40 harnesses) running on fbf332caa. WIP 698bcda90: decode slots of their own so decode runs before the first training step (server half; client half next). See CHECKPOINT § 9 |

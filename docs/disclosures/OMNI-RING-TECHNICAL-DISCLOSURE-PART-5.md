# omni-ring / SRFS — Technical Disclosure, Part 5 (2026-10-03): the seed's owned ground, residue memory at scale, our own engines

> Copy notice. Licence of this text: CC BY 4.0. Software that this Part describes carries its own licence where it is released.

Dated prior art. Covers work measured 2026-10-02 (after Part 4, 11:08 PDT) through 2026-10-03, plus six results measured earlier on
10-02 that Part 4 omitted (marked *pre-window*). Laptop = i5-8365U (4 cores, AVX2, L3 6 MB, RAM ~11–12 GB/s); "pod" = one rented A100.
Every bar was written before its harness (the plan files are internal and are not published); failures are disclosed as measured. `OUT/` = run-output
directories (`gpurun-out-0930/`, `gpurun-out-1003/`). Concepts that first arrived through an external model's peer review are
marked "external review concept"; methods are described in our words. Field terms throughout (the author's own vocabulary).
Evidence status: the item-level run records behind these numbers are private and are not published, and a claim-to-evidence index for this Part has not been published yet; a figure that does not name a harness and a result file is a figure recorded by the project, not an independently reproducible one.

## 1. The seed's owned ground: data provenance and the clean room
- **Full-fleet chew (pod):** 75 shards, 186,672 segments; 1,347,157 chunks embedded (nomic 768-d + Matryoshka-256), parity vs
  reference min cosine 0.99999, top-1 0.995, ~660 chunks/s.
- **Deterministic chewer as the Head's decoder head:** extraction by named pure ops; each pipeline is a keyed program vector
  (tamper-refused on read-back, Part 4 VM); records are hypervectors in a residue-addressed store. 1,201,843 reasoning records
  (3.9M rows), attribution 0.966 (bar 0.95); two runs byte-identical; field round trip 3,988/3,988 via VM LOAD/UNBIND/SIFT;
  key sieve→CRT 1,000/1,000; 24 collisions / 9,091 keys in the 1.88M space (birthday expectation 21.9) → chained payloads.
- **Sift near-duplicate detection:** 185,665 paragraphs; recall vs exact 1.00 at τ 0.9/0.8/0.7, precision 0.98/0.94/0.80.
- **Rule labellers replace a teacher where they can:** rule ops return {label, rule_id} or ABSTAIN; coverage 0.24–0.93, hand
  precision 49–50/50; agreement vs the 70B teacher 0.888–0.9985 (bar 0.85); a ring head on rule-substituted labels 0.818 vs 0.815.
  Teacher run: 25,496 rows in 7,119 s (≈ $3.14); the teacher scored BELOW majority on one task (0.330 vs 0.530).
- **Reflex heads:** ternary BitLinear heads on embeddings, 7/8 pass majority+5 (role 0.785, verb 0.956, …); dispatch-outcome head
  fails again (0.599 vs majority 0.596). Re-trained on rule labels from permissive inputs only: 0.957 / 0.944 / 1.000, 3/3 pass.
- **Clean-room filter + default-deny guard:** only rows from permissive-weights models, own generators or permissive corpora
  (unknown → dropped): 400,232 / 1,201,843 reasoning rows kept, 35,000 / 89,129 sessions, 2,099 / 8,529 docs. Training refuses any
  path whose nearest marker is not a clean-room marker (raw chew refused; outputs of external chat models marked no-train).
- **Owned base corpus:** 600,083,983 tokens, sciences + literary arts, PD / CC0 / CC-BY / CC-BY-SA only, no Wikipedia.
- **Unattended runs judged by RATE, pods launched through a gate (from a measured failure):** a pod reported 255 CPUs on a 27.2-CPU
  quota; the trainer spawned 255 threads (1.3k tok/s, GPU ~5% for ~2.5 h); 4 threads/arm → 68–93k tok/s. Rate checker replays
  the stall as STALL; the launch gate refuses jobs without lineage quotes, catalog models, thread caps or clean data (4 refusals, 1 pass).

## 2. A deterministic reasoning generator and laws cemented only by tests
- **reason-gen:** per domain a seeded generator, an exact solver emitting typed trace steps, and an INDEPENDENT verifier (a different
  method); a row exists only if it verifies; abstain rows when information is missing. 26 domains, 200/200 per domain, byte-identical
  reruns; wrong answers rejected 200/200 per domain (causal.dag 297/300). 16-op trace ISA (GOAL FACT OBSERVE INTERVENE STEP HOP DERIVE
  GUESS CONFLICT RETRACT DIFF CHECK ASK PREDICT EMIT ABSTAIN) + 7 epistemic tags (given know assume guess stuck revise unknown).
  Examples: ranked belief revision verified by subset enumeration; JSON pushdown verified by a real parser; dimensional analysis by
  exponent vectors over primes; causal DAGs with seeing ≠ doing verified by joint enumeration + mutilated graph; a bioreactor with
  hidden confounders and exact power analysis (n 63 for d 0.5, INCONCLUSIVE when underpowered), truth agreement 0.873.
  Generator bugs that changed data are disclosed (a "no bug" claim when visible tests missed the bug; a verifier refusing valid proofs;
  RNS products wrapping exactly at capacity M ≈ 1.0e11 → slicing; an SPRT false-effect rate of 4.5% vs 1%).
- **omniglyph laws:** axioms are proposals; status is computed from an append-only ledger of executed randomized tests in four
  toolchains (Python, gcc, rustc, node); CEMENTED = ≥ 2 seeds, ≥ 2,000 cases, 0 failures, scoped to the tested domain. 54 CEMENTED /
  12 REFUTED (e.g. integer division rounding down cemented in Python, refuted in C/Rust/JS with counterexamples; float associativity
  refuted everywhere). Challenges never edit a law: INVALID / UPHELD / SUSTAINED; a sustained challenge yields a narrower law version.
  Generated-input laws back every native form; one caught a real flaw: SPRT false-effect 0.045 vs 0.01 → amended law (variance from
  design residuals) CEMENTED, the old law kept REFUTED with history.

## 3. Compress-and-slice: representation matching, measured
- Template compaction alone: 1.03–1.16× (tokens live in arguments). CS-0, four concepts first judged no/partly, probed to scoped yes
  (external review concepts): 2T Cayley-graph composition walks 2,000/2,000, 2–12-hop chains reduce to ≤ 3 (−72% hops); a Hopf
  base/fibre belief store reads location 981/981 and belief lag 981/981; torus winding = coincidence truth 3,000/3,000 incl. 804
  "never"; ring-residue primality exact below 37² = 1,369, Miller–Rabin with the ring primes exact below 10⁶, ψ₁₁ edge confirmed.
- CS-1 native forms as generator domains, each with an old-form independent verifier: RNS carry-free multiply 1.37–1.91× fewer
  tokens; mixed-radix compare with an inverse plate 5.32×; trit clauses; 2T word folding 1.40×; clock-read coincidence 1.64×;
  resolution-V 2^(5−1) design + SPRT 5.6× fewer experiments (truth 0.840 vs one-factor 0.881 at 5.6× the runs); bitmask wavefront
  search 2.63–3.65×; witness-bitmask theory of mind; ring-prime MR 1.49×. All 200/200 verified.
- Tokenizers: clean BPE V 8,192 on 208.9 MB clean text (gutenberg 0.344→0.301, peS2o 0.306→0.263 tokens/byte). Atomic glyph
  tokens made traces WORSE (BPE merges break); a generator-mixed vocabulary with an even per-file budget keeps prose unchanged and
  shortens traces 1.24× across all 26 domains (a cumulative-budget bug first cost prose +16.5% — disclosed). End to end:
  851→136 tokens (6.3×), 814→208 (3.9×), 347→188 (1.8×).
- Owned curriculum: owner-approved spec (sha256) compiled deterministically from verified rows (rows that do not fit are skipped and
  counted, never truncated); 10-beat helix (Goal, Procedure, Givens, Encode, Operate, State, Verify, Laws, Answer, Receipt), 5 passes =
  levels 1→5 with fading domain labels, inverse and terse rows; 9.5M tokens compiled.

## 4. Trace science on a 1.8M-parameter ternary trunk
- **RG-1** (pre-registered; 4 layers d128, residue clock, ctx 512, 10M tokens/arm, 13 domains): exact-answer accuracy held-out / OOD:
  answers-only 0.212 / 0.172 · full traces 0.137 / 0.121 · shuffled trace lines 0.082 / 0.100 · forward-only traces (no
  conflict/retract) 0.128 / 0.110. Primary FAIL; KILL condition (traces ≤ answers + 2) met at this size. Order carries signal
  (+5.5 over shuffled); backtracking +0.9 (within noise). Evaluation bugs that changed scores are disclosed (scoring the last answer
  line, pad leakage, a quadratic cache, per-token re-quantisation: 18.8 → 8.75 ms/token).
- **FWD-0:** teaching one new domain at equal budget: backprop learns (acc 0.70) but forgets (old loss 0.507→0.968); zeroth-order
  (MeZO) over all ternary weights diverges or stalls; mechanism measured: cosine with the true gradient 0.0007 ≈ 1/√d, and ε 1e-3
  flips 1.6% of trits.

## 5. Positions, residue memory and the core
- **RING-10:** T¹⁰ = T⁵ (3,5,7,13,17) × outer (11,19,23,29,31): N = 100,280,245,065 exactly; position = (page = x div 23,205, offset).
  Decode cost grows with Σm (45 → 158 probes) for 4.3 million × the states. Additive superposed decode exact at D ≥ 576.
- **Elastic RRNS (ours to name):** inside the T⁵ window the idle outer rings are redundant moduli: 1 and 2 corrupted residues corrected
  100%, 3 corrected 99% (T⁵ alone: 0%); past the window they become the page counter. RING-10-0a: soft RRNS exact at D 256 under heavy
  noise (κ 1) where raw decode reads 0.170 — redundancy lets the vector shrink.
- **Fundamentals-only position kernel is smooth, not sharp:** σ 0.316 → 0.224 (matches √(1/2K)); worst distractor 0.81–0.92 → sharp
  addressing = integer sieve; cosine channels = smooth locality. Exact residue phasor layout: 0 constant, 0 aliased pairs.
- **LAYER-0/0b/0c — a T⁵ prism decoder inside a 10-ring transition plate:** same answers as the pool sift, 1.5–2.0 ms vs 56–117 ms
  per read (35–70×). Keys rendered by a seeded PRNG per beat (never stored) and plates paged by the FULL outer-ring address: walks of
  16,384 transitions 1.000, the full 10¹¹ range 1.000, 0.72 ms/beat, 2,560 B/transition. Disclosed failures: `mod NP` page collisions
  (LAYER-0b FAIL), one-plate capacity leg (0.986–0.993 on 2/5 seeds) → page budget ≤ 32 transitions per D 5,120 plate.
- **MATPLATE — D×D Hebbian fast-weight lens with 10-ring coded values decoded by soft RRNS:** exact to T = 2D; at T = 4D soft RRNS
  0.972 vs hard CRT 0.043 (+93 pts): residue redundancy multiplies a matrix memory's capacity.
- **LAYER-1 — the beat loop as a self-rewriting VM program:** a single-read program abstains on its own margin and rewrites itself to
  the peel program: 363/363 superposed beats routed and read exactly, 0/1,637 false abstains, 2.9 ms/tick, forged program refused.
- **MEM-0 — processing-in-memory by layout, no new hardware:** 1,000,000 marks: residue addressing 1.02 ms with 0 bytes scanned
  (11,108× fewer bytes, 492× faster than the packed full scan); superposed slots 32× fewer bytes; mmap map 40 ms vs rebuild 55 s.
- **APP-0 store:** 1,370 notes: query 5.3 ms, exact get 22 µs, open 92 ms, recall@5 0.933; index-time leg FAIL (333 s vs 60 s); an
  address-space collision at 1,368 files moved the store to 113·127·131.
- **OS-RING-0 Phase A — a laptop's state on one ring: FAIL as registered.** Warm geomean 3.34× (bar 100×), cold 0.015×; bytes moved
  1,444× fewer; address questions clear the exponent (file location 13.7×, package 9,935×) but the store is 73× the indexed data and
  cold open 23.9 s. Signpost: the store's shape.
- **CAL-3b — residue clocks vs RoPE vs learned, 50M tokens/arm (pod):** loss rise from 1× to 4× trained length: residue +0.186,
  RoPE +0.578, learned +3.031; residue best at 4× (3.886 vs 4.253). FAIL as registered in distribution (+0.026 vs ±0.02); copy metric
  ≈ 0 in every arm (harness). *Pre-window:* CAL-3 at 4M tokens inconclusive (Δ 0.014).
- **SRC-LM-0b — program-driven source path on one head:** additive intent bias on the query +6.12 pts held-out (bar +10, floor +3);
  unitary per-intent phase rotation −12.5. **MEM-HOLO-0:** residue-bucketed fast-weight plates (LSH → CRT) train from step 0 and beat
  the plain memory on copy 3/3; MEM-HOLO-1/1b inconclusive (the full-attention baseline missed its 0.5 precondition).
- **CORE-FIELD (*pre-window* CF-0/0b/1/2/2b/2c; CF-2d/2e new):** a hex-torus continuous-attractor bump read exactly by residue rings
  2,000/2,000; a rectified saturating rule keeps it alive 10,000 noisy ticks (drift 0.27 cells) and regenerates after 30% damage.
  Steering by velocity-modulated odd weights (Zhang 1996): MOVE 1.00, HOLD 1.00, RELEASE 68 ticks (bar 20) — law L16 provisional.
- **ROUTER-0 (*pre-window*):** frozen simplex-ETF head keys match learned keys (0.9957 vs 0.9959); ECE leg FAIL.
- **24-cell core in C verified:** 0 associativity violations / 13,824 triples, 408/576 non-commuting pairs, element orders = SL(2,3);
  int8 nearest-row sift + spark margin 7–17× numpy, 2–3× f32 BLAS at ¼ the memory (after a margin-normalisation fix).
- **PIPE-2:** warm-forked autoscaled replicas of the slowest prism face 1.94× sequential (cold replicas 0.55× — declared harness defect).
- **Init-scale defect found in all toy trainers:** N(0,1) tied embeddings start at 68–79 nats vs ln V 9.01 → hypersphere / std-0.02
  init (law R15); earlier "at chance" results were largely this bug.

## 6. Our own engines: decode, training, learning rules
- **omni_infer (C++/AVX2 decode for the ternary trunk):** ternary GEMV by sign-select on int8 with exact int32 sums (no multiplies),
  residue clock as exact per-prime phase tables, preallocated K/V, per-token spark margin: same final answer as PyTorch 12/12,
  5.8–7.0× faster per core. Dev line, all token-identical 18/18: plate-drafted speculative decoding (a deterministic solver drafts,
  the trunk verifies; 549/1,102 accepted, only ~1.04× — the vocabulary step dominates); a 16-sector phase-key cache; keyed SipHash-2-4
  integrity at model load (one flipped bit refused). Negative: RNS-uint8 ternary GEMV exact but 5–9× slower (rejected).
- **omni_train (our training engine, C++/AVX2, C API):** forward + backward + optimizer for the same trunk: ternary forward by
  sign-select; attention by GEMM with log-sum-exp saved and scores recomputed in backward (no T×T storage); tied head in row chunks
  (logits never stored for all rows); packed 6×16 FMA GEMM; vector exp. Matches PyTorch: identical loss, worst gradient error 6e-7,
  150-step training curves within 0.002 per step. Speed at 1 thread small dims 0.93× PyTorch after three fixes (0.29× → 0.62× →
  0.93×); full-size not yet measured.
- **Learning methods on the engine (unit-level):** (A) trits + 4-bit residue flip counters as the whole optimizer state (no latent
  floats; Bop-kin): learns 8.95 → 5.29 in 200 steps; (F) spark skip — confident-correct tokens excluded from the head backward (θ = ∞
  bit-exact); (G) frozen seeded head; (H) coprime block rhythm (block l updates when step mod p_l = 0). Components: (C) Equilibrium
  Propagation with symmetric nudging — cosine 0.984 to the exact gradient, accuracy 96.7% vs 96.0% backprop-through-settling,
  vibration-law settle stop in 10 steps; (D) shift-equivariant mixing in the character (DFT) basis of the residue rings (Schur):
  1,040 vs 32,400 parameters, equivariance 1e-15, test error 60× lower than dense; 2T irreps 1,1,1,2,2,2,3 confirmed; (E) reversible
  coupling on an int32 fixed-point stream with Q8 (⊂ 2T) mixing: bit-exact reversal (a float stream drifts), activation memory 8×
  smaller; (I) exact residue all-reduce with RRNS correction: any summation order bit-identical (float32 differs on 635,293 / 10⁶),
  1–2 corrupted residues corrected 100%, 40.8 ns/element for 8 workers; (J) metamorphic frames as data: relabel/shift/permute,
  re-solve, re-verify — 21/21 domains 100%.
- **Packed trits:** 4 per byte with an in-register unpack feeding the same sign-select dot (exact; decode engine tokens and margins
  identical 12/12; 1.01× at 1 thread — compute-bound there); 5 per byte base-3 storage (1.6 bits/weight).
- **Trial-and-commit for weight updates:** snapshot → trial update → frozen canary battery → commit or exact rollback; every decision
  in a sha256 hash chain: rollback restores weights and loss exactly; a destructive update (lr 0.5) refused with weights unchanged;
  an edited record detected at its line.
- **Negative results (signposts):** Hadamard-designed forward-only gradients below random SPSA twice (cos 0.44 vs 0.55; nudge size
  irrelevant; low-sequency Hadamard rows sum correlated gains); prioritized replay interleaved into training worse twice (6.61 vs
  6.42; 3.43 vs 3.07).

## 7. Fleet systems (agent governance and interfaces)
- **Revert-safe attention surface:** every agent file write from three different agent runtimes becomes a mark with before/after
  hashes and content-addressed blobs, shown as a card at a computed level (severity raised for core files, deletes, guard blocks,
  failed gates); revert is compare-and-swap — refused unless the file still hashes to the mark's after-hash and no later mark exists;
  a revert is itself revertable. Selftest 13/13; edit → card 2.1 s; one shared reader serves 3 streams.
- **Universal worker progress vector:** liveness of any agent runtime as acting / busy / tool / idle / claimed from log bytes (nudge
  echoes excluded), marks, process-group CPU ticks and the runtime's own status: generating 75–80 ticks/5 s, tool wait 4–10, polling
  0–2. Before: a finished worker received 32 nudges in 2.5 h. Units 11/11.
- **Harness-as-head:** an external agent CLI driven as a Talon head over its stream-json I/O; inbox messages enter mid-run as turns,
  a claim line ends the run, the session becomes recallable from other harnesses (probe 11.7 s; gate PASS).
- **Agent tool server:** client-aware tool profiles + plain-text results (28 → 12 tools, schema 19,553 → 8,032 chars per turn, −59%;
  SQL results −53%); calls routed to a resident fork-server executor (bash 55–93 ms vs 372–634 ms cold, identical outputs).
- **Procedure-gate:** writes refused until the target system's manual was read this session, fleet verbs until their procedure was
  read, and dispatcher restarts while work is live (origin: one restart killed 2 live workers). Selftest 11/11.
- **Smaller:** subscription CLI as a paid lane (fixed session id, usage limit = cooldown, request-count guard); vein sessions +
  lineage-packed briefs whose anti-pattern list grows with every correction; app evidence marks through one token-scoped door with
  day-clock decay (visible in ring state within 3 s); done-gate path tokenising (4 failing seals verified); secret-path classifier on
  every file route; low-power render profile (a CPU-painted webview 96–100% → 1.1% of a core); fleet-true yield (rescues by interactive assistant sessions counted out: first-pass yield 46.9% vs reported 55.4%).

## 8. Provenance (borrowed / ours)
The field's: CRT / RNS / RRNS (Yang & Hanzo), Garner, Miller–Rabin and the ψ₁₁ bound, Wald SPRT, Fisher factorial designs, Hopf
fibration, binary tetrahedral group, RoPE (Su 2021), ALiBi / YaRN, linear attention and fast weights (Katharopoulos 2020; Schlag 2021;
Kohonen 1972), Reformer LSH, MQAR, continuous-attractor networks (Burak & Fiete 2009; Zhang 1996), neural collapse / fixed classifiers
(Papyan 2020; Hoffer 2018), nGPT, BitNet b1.58, bitnet.cpp / T-MAC kernels, llm.c, FlashAttention recompute, Bop, MeZO, SPSA with
Hadamard perturbations (Bhatnagar 2003), Equilibrium Propagation (Scellier & Bengio 2017), group-equivariant networks (Cohen & Welling
2016), RevNet, prioritized replay, Selective Backprop, metamorphic testing, SipHash, BPE, spiral curriculum (Bruner), STaR, MCP. Ours: the clean-room default-deny training guard; the deterministic generator with independent verifiers,
trace ISA and epistemic tags; test-cemented scoped laws with non-destructive challenges; native-form training domains; the elastic RRNS
dial; rendered keys + full-address paging of holographic plates; soft-RRNS-decoded matrix memory; the self-rewriting beat loop;
processing-in-memory by residue layout; residue-phase clock engines for decode and training; solver-drafted speculative decoding;
residue flip-counter ternary optimizer; spark-gated backward; integer reversible blocks; order-independent residue all-reduce for
decentralized training; trial-and-commit with a hash-chained learning log; the agent-governance mechanisms in §7. None claimed as
first without a wider prior-art search; all dated here.

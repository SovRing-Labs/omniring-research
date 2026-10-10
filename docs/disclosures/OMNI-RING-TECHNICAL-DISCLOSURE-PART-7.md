# omni-ring / omni-render — Technical Disclosure, Part 7 (2026-10-09): live school and growth run, cyclone array and T50 hub, Omni Web, the doctor core, the cores, provenance

> Copy notice. Licence of this text: CC BY 4.0. Software that this Part describes carries its own licence where it is released
> (renderer and omni-ui: MIT OR Apache-2.0; the doctor and the T25 core: PolyForm Small Business 1.0.0 OR PolyForm Noncommercial 1.0.0;
> omni-spec: Apache-2.0, not released).

Dated prior art. Covers work measured 2026-10-06 → 2026-10-09. Machines: one laptop (i5-8365U, 4 cores / 8 threads, AVX2, Intel UHD 620;
shared with training jobs, load 6–18, so wall times are noisy), a rented CPU server (16 then 32 vCPU, AVX-512), rented GPUs (L4 24 GB, A40
48 GB, one A100 80 GB baseline). Harnesses are in `harness/part7/`, result files and pre-registration extracts in `docs/appendix/part7/`;
the experiments behind each section are docs 24–44 of this corpus, one per document with its verdict, and essays 12–16 tell how the week went. Labels: a number with no label has its harness
and result file named in the doc that covers it; **(partial)** = the value is only in a log or an index; **(unsupported)** = harness or result not
published, quoted as recorded by the project. Failures are disclosed as measured. Bars: the published extracts show the bars, not when they
were written; the ordering evidence is the version-history table `docs/appendix/part7/ordering/first-added-table.md` (114 of 128 plan /
harness pairs entered version control plan-first; a checkpoint dates entry, not authorship, so this is evidence, not proof). Every bar
carries a FIELD PREDICTS line in its doc. Field terms (the author's vocabulary): "render" = JIT-generate executable code into memory;
"core" = a JIT-rendered program that fires constantly while active; "omniring system" = a residue number system (pairwise-coprime moduli,
CRT) with its core; "toroid" = the torus shape (each hub's inner core is a toroid core, and the rings around it are toroids); "keep" = a
saved copy of a model state (permanent keep, checksummed; rolling keep, the last five rounds); "ledger" = a tracker, named by a prefix
(clean-room ledger, growth ledger, home counters); "wall" = the growth stop (three rounds with no skill gained).

**Summary.**
1. The school became one round loop over a skill graph (392 nodes) with a guard, rollback and a forgetting watch; circular builds let one
   core hold the earlier layers while learning middle school; a growth controller with a 100 % stage gate and a hash-chained growth ledger
   was built and gated.
2. The cyclone array was built as resident GPU wiring (layout, T50 addressing, toroid-to-toroid routing, exact against CPU) and, separately,
   as resident training of 8 and 20 models in one step; a group of 20 trains 21.6× faster than 20 CPU engines but **misses the registered 2
   % parity bar**; 40 models in one session are refused by a 2^31-byte binding guard; a dual-T50 cut read finds the array's bottlenecks
   without max-flow.
3. Omni Web, a browser whose page and chrome are drawn by our own engine: broker plus confined page processes, one tree for drawing and
   reading, 2.9 % of Firefox's memory on 10 document pages; script-heavy pages fail the "lightweight" claim.
4. The doctor core: equations as a code alphabet, Chrome as a black-box oracle, geometric triage, a rendered T25 box kernel firing inside
   layout, an unattended fix loop to pristine geometry, and a two-team clean room (reader, clean-room gate, implementer) that rebuilt 27 of
   32 functions from name-free specifications.
5. The cores: a registry with receipts, pod hosting, embed / chewer / math / reservoir / route cores; the math core passes its gate, embed
   and chewer fail theirs, guard and redteam are designed only.
6. Provenance: four clean-room forms, default-deny data gates, licence gates, and hash-chained ledgers, with what each actually guarantees.

## 1. The live school and the growth run (docs 24–29, 42–44)
Model: the SuperSeed trial model, a ternary-weight transformer of 6,926,912 weights (D 256, 6 blocks, 4 heads, vocabulary 8,192, context
512) with the T25 core inside it, trained by our own CPU engine.
- **Round loop over a skill graph.** A round: the planner reads the graph and per-skill scores; a fresh build is compiled for the frontier
  plus spaced review (share 0.2) and a one-level preview; N harnesses train one core for 10 days, merging weights at each day end; a
  per-skill held-out evaluation scores the merged core. Mastery: held-out top-1 ≥ 0.85 on learnable positions. Graph: 392 nodes, 786
  prerequisite edges, 9 unbuilt rungs (never faked). Sixteen rounds: tier-1 skills at the gate 28 → 72 by round 12 (sticky mastered count 46
  → 126), no wall reached (`docs/appendix/part7/ch1-live-school/results/live-school/rounds.jsonl`; the shipped planner replays all 16 rounds
  exactly).
- **Round guard and the round-9 collapse.** Averaging 3 middle-school harnesses with 5 tier-1 harnesses in one day merge wiped tier-1:
  skills at the gate 55 → 6, held-out loss 0.717 → 2.595, while the sticky mastered count *rose* 93 → 123. The guard (FAIL if skills at the
  gate on the shared skill set fall > 10 % or held-out loss rises > 30 %) flags it and passes rounds 2–8 with 0 false alarms
  (`harness/part7/ch1-live-school/round_guard.py`). Restart from round 8 with middle locked: four PASS rounds.
- **Circular builds by splicing** (`harness/part7/ch1-live-school/splice_build.py`): review → current school → preview inside one build.
  Middle on its own core held 3 / 2 of 162 / 155 tier-1 skills; spliced cores held 91 / 103 tier-1 skills at the gate *and* 27 / 36 of 46
  middle skills on the same core (rounds 15 / 16). Not a controlled pair (different rounds).
- **Growth controller** (`harness/part7/ch1-growth-controller/grow_ctl.py`): a stage passes only when every skill scores 100 % on ≥ 300
  independent held-out rows (zero errors on n rows bound the error below ε at confidence 1 − δ when n ≥ ln(1/δ)/ε; ε 0.01, δ 0.05); frontier
  weights multiplied by how many skills a skill gates (min-cut: `pk.echo@1` gates 84); modes skills → parameters on a wall → generators;
  permanent keeps with a sha256 manifest; a hash-chained growth ledger. Gate 14 / 14 on synthetic evaluations
  (`docs/appendix/part7/ch1-growth-controller/results/g1/g1.json`); one server wiring round 6 / 6 checks. At the 100 % gate the frozen
  round-12 core holds 10 of 85 pre-K skills and 0 of 20 elementary skills.
- **The school step on the GPU.** 100 kernels written from our engine's equations and emitted as SPIR-V; `thead-learn` runs unchanged on the
  library. One school day on the laptop GPU equals the CPU day in corrections (34 / 34), generator rows (14 / 14) and answered rate (0.479 /
  0.479), 6× slower on that weak device. Full-size trunk on an L4: 87.2 ms against 734 ms per step (8.4×), held-out +1.9 %.
- **Many models in one step (A40).** 8 school-size models in one step: 64.7 ms per model against 1,238.2 ms on the CPU engine, each replica
  bit-identical to its own single-model run; "the cyclone holds the model" form (shared C plus a delta per harness): 30.6× with attention as
  batched GEMMs, held-out within 0.051 %. With every school switch the per-harness held-out gap reached 5.99 % (registered bar 2 %:
  **FAIL**); the CPU engine's own noise with the same switches is up to 3.99 % (mean 2.01 %).
- **The 2^31-byte probe** (`docs/appendix/part7/ch1-array/results/probe-2g31/`). One session of 40 models is **refused at build** by an
  explicit guard (three logits buffers of 2.5 GiB exceed one storage binding); before the guard, a 40-model session trained nothing without
  an error. A group of 20 builds and learns: 8.55 GB, 1,231.7 against 26,608.7 ms per step (21.6×); **the registered 2 % bar failed**:
  per-harness held-out gap mean 4.1 %, median 3.8 %, max 9.7 %, GPU worse on 16 of 20 harnesses. The registered verdict stays FAIL. A
  noise-relative gate (mean gap ≤ 2.01 %, no harness > 3.99 %, no one-sided skew by a two-sided sign test) is registered for the next run
  only; it was written after this result.
- **Reasoning rows and a negative.** DOING answered 0.63–0.64 on fresh verifier-checked problems (rounds 9–14); the wall predictor's stall
  score does not predict stalls (AUC 0.449 / 0.406 / 0.350, chance 0.5); in an earlier controlled run plain question–answer rows beat full
  traces (21.2 % vs 13.7 %).

## 2. The cyclone array and the T50 hub (docs 28–31)
The author's design (2026-10-08): a unit is a T50 centre with 8 harnesses around it, a model tied to each, all feeding the cyclone; 5 units
(1 centre, 4 around) touch on the outer ring; everything resident in video memory. Four parts were built and gated **separately and have not
yet run together**.
- **T50 omniring system.** T25 = the 25 odd primes 3…101; T50 adds 103…233 (50 primes, sum of moduli 5,348, product ≈ 10^93.3); each ring is
  one 8-bit lane, so the tier fits one 512-bit register. The core is rendered as AVX-512 code (`harness/part7/ch2-t50-core/t50.rs`); the
  vector encode uses the direct-remainder method of Lemire, Kaser and Kurz (2019), checked exhaustively for every y < 2^24 and every
  modulus. Per-event cost: T50 14.6 ns against 29.4 ns per-ring scalar in the same run (partial: harness present, result log not published).
- **Resident session** (`harness/part7/ch2-wiring/src/session.rs`): buffers persist, the whole step is recorded once and re-submitted;
  byte-exact over 2,000 chained passes; 13.4× less time per pass than create-run-teardown on the UHD 620.
- **Layout and wiring rungs** (records `docs/appendix/part7/ch2-wiring/results/cyclone/`): G1, G4, G8 exact on both laptop devices; G40 (one
  floor, 40 models' training state allocated, not trained) 21.834 GB resident and every stream exact on an L4; G120 (3 floors) wiring exact
  with reduced slabs, **full-size weight check FAILED** on the L4 (830,276,940 mismatched weight words; cause unexplained).
- **Routing, toroid to toroid by address** (`route.spvasm`): every item moves along one ring per hop; the routing pass fills source- and
  destination-addressed counters as it moves items. Exact against the CPU on G40 and G120.
- **The dual-T50 cut read.** The author's statement: "interlocking two 50t omniring systems would solve this computation in much less time
  by relying on the massive rapidly moving and counting outer rings". Built: a pair's minimum cut = min(trivial cut at either end, the
  per-ring residue-bipartition table of every ring where the two differ), O(rings) per pair, no search. On the recorded G120 routing (15
  toroids) the global minimum cut equals Gomory–Hu; 200 of 200 seeded traffic fields exact; 105 toroids 5,460 of 5,460 pairs in 8.1 ms
  against 151 ms; 1,155 toroids: 60 of 60 sampled pairs equal to max-flow, global minimum equal to Stoer–Wagner (1.51 s against an estimated
  101 s). **Blind spot found:** a hot cluster (a box of toroids saturated outward) breaks the ring family (85 of 100 exact) until box cuts
  are added (100 of 100). On the GPU the route pass fills the tables with atomics and a cut kernel writes every pair's cut per step: 0
  mismatches (`docs/appendix/part7/ch2-cuts/results/` and `ch1-t50-cuts/`).
- **Toroid mailbox:** per step the items routed to each toroid are counted, prefix-summed and scattered, and consumers launch with an
  indirect dispatch sized on the GPU: G120 3,848 workgroups by load against 6,465 for a fixed worst case, 0 mismatches.
- **The 40-harness growth run on an A40** (two sessions of 20): no harness finished a day and no round completed; the last launch was
  stopped in its start phase with no array step statistics. **No growth-rate number exists for any GPU tier.**

## 3. Omni Web (docs 32–33)
The author's brief, verbatim: "modern, futuristic, fluid, intuitive, highly accessible, capable, lightweight, ternary". Other browsers were
observed as black boxes (output, DOM dump, process memory), never read.
- **Architecture.** A broker owns the window, network, cookie jar, cache, history and tabs and never parses page content; one confined page
  process per live tab (no_new_privs, Landlock, seccomp-BPF allow-list) parses, styles, lays out, runs scripts and rasters, over a framed
  pipe (one tag byte, a 4-byte length, the payload). **One tree, two outputs:** the chrome is a packed widget tree (22 B per widget)
  emitting both the markup our engine draws and an AccessKit tree for assistive technology; every input ends in one `act(verb, arg, source)`
  call, so what is drawn and what is read cannot disagree.
- **Memory against Firefox** (`harness/part7/ch3-memory/ram_bench.py`; `docs/appendix/part7/ch3-memory/results/ram.json`, `ram-js.json`): 10
  pages, summed PSS of every process: **211.3 MiB vs 7,297.6 MiB = 2.9 %** (script off), 308.8 vs 7,423.6 MiB = 4.2 % (script on); 2
  processes against 13–16.
- **Connectivity** (`harness/part7/ch3-connectivity/conn.sh`): 13 of 13 routes pass in each of three runs (gzip, chunked, redirects, 404 /
  500 pages, 204 without waiting, cookies, latin-1, close-delimited body, `document.cookie`); cookie jar first-party only, in memory unless
  the person chooses "keep".
- **Census of 24 real sites** (`docs/appendix/part7/ch3-census/results/census-{1,2,3}.metrics.jsonl`): frames on 24 of 24, scripts ran /
  failed 402 / 39 in run 3; **"24 of 24" means a frame, not a usable page** (8 pages built ≤ 821 px); renderer RSS median 112 MB, three
  pages ≥ 500 MB (up to 2.23 GB): **"lightweight" holds for document pages and fails for script-heavy pages.**
- **Language conformance** (`harness/part7/ch3-test262/test262.py`): 29,203 of 53,607 executed tests pass (54.5 %); two later rounds 55.33 %
  and 56.85 %. A 106-check platform probe passes 106 / 106 on eight saved gate builds (partial for the browser gates themselves).
- **Orbit chrome.** The first design was rejected by the author ("the opposite of what we are looking for") because it was limited to what
  the renderer could already draw; remedy written as a procedure: design the target in full, turn each capability it needs into engine work.
  Orbit asked for eleven engine capabilities; nine were built in the engine's paint module (rounded boxes by signed distance, closed-form
  Gaussian box shadows, gradients, backdrop blur, SVG strokes, …), each gated so that layout does not move; transforms and keyframes
  (compositor work) were not built.
- **Contrast law** (arithmetic, not eye): dark glass at alpha 0.58 over white made the third text tone 1.02 : 1; glass alpha 0.88 and
  re-chosen tones give every text colour ≥ 4.5 : 1 against the worst backdrop.
- **Merge gate and engine pin** (`harness/part7/ch3-merge-gate/merge-gate.sh`): layout baseline unchanged (24,032 of 28,040 boxes agree with
  Chrome, 85.7 %), compiled = interpreted knob lookups (2,866,688 identical), binary gate 0 lost; then main moves to exactly the gated
  commit and the app pins it.
- **Failures:** paint error against Chrome, frame times, screen-reader sessions and the keyboard-form gate were logged but not retained
  (unsupported); the video site's music front end was not made usable.

## 4. The doctor core (docs 34–37)
The author's definition: the doctor is a core that learns and repairs our own applications one at a time, finds donor code by reverse PIFS,
tests with logic and the application's own judge, and keeps a knowledge base of verified fixes. All inside the renderer binary, CPU only, no
model.
- **Code alphabet** (`harness/part7/ch4-engine/src/doctor_abc.rs`): Rust lowered to name-free SSA terms (70 of 126 layout functions); an
  e-graph with rewrite rules as data; anti-unification recovers, with no names, the shared table / grid distribution `?0 + (?1 − ?0)·?2 /
  ?3`; search by function answers 24 / 24 hand-written needs (frame-first synthesis builds 22 from examples alone, compiler-verified).
- **Chrome as a black-box oracle** (`harness/part7/ch4-oracle/oracle_synth.py`): probe families turn a failing case's numbers into symbols,
  sweeps run through Chrome, a law is synthesised and compiler-checked: nine laws (textarea, input, meter, progress, legend, body-margin
  collapse); the same probes on our engine name the defect where the laws differ (legend: 0 of 41).
- **Geometric triage and the gate series.** The origin census misses most errors (one news page: 3,102 failing boxes, 0 origins), so a shape
  station measures each box's angles against the oracle. Fixes found this way, each behind a dormant switch and gated with 0 boxes lost,
  raised agreement from 19,008 to **24,004 of 28,010 boxes (85.7 %)**
  (`docs/appendix/part7/ch4-gate-series/results/agree-snapshot-after-*.json`); the largest steps were CSS Grid implicit named areas +1,609,
  `unset` for non-inherited properties +1,284 and `:has()` +673.
- **The T25 box kernel.** A box is one point on 25 rings (x₀, y₀, w, h and its offset inside its frame, five rings each; product ≈ 2^126.45,
  one register); the twist against the oracle's point decodes by CRT to the exact error and classes the box CARRIED / SHAPE / OWN PLACE;
  triangle keys collapse 473 roots into 103 families. The kernel is generated x86 and fires after every layout pass: **0.90 % of layout
  time** over 28,040 boxes (`docs/appendix/part7/ch4-t25/results/t25fire-e1.marks.jsonl`).
- **Pristine map and the unattended fix loop.** Target: mathematically exact geometry, not Chrome parity. Six sub-pixel relations (overflow,
  near-flush, near-align, near-touch, near-equal, uneven gap); the first corpus map found 567 defect boxes in 28,058 (97.98 % pristine).
  Each fix is a per-site CSS sheet judged by twist → 0 and 0 boxes losing pristine. **Failure found:** the judge was blind to sibling
  overlaps (242 → 340); fixed, the knowledge base archived. Disclosed trade-off: pristine fixes moved 807 boxes away from Chrome, which
  draws the same defects (unsupported).
- **Two-team clean room** (`harness/part7/ch4-engine/src/doctor_spec.rs`): readers write name-free specifications (equation, examples,
  held-out and validate rows, source hash and licence); the clean-room gate passes only function (schema whitelist, one well-formed
  equation, leak scan); one implementer sees the spec and our library and never the source. On our layout file: 32 specs, seeded leaks 256 /
  256 refused; 27 of 32 rebuilt. **Failure found:** with an examples-only gate 7 of the 27 were overfits; an equation gate (the spec run as
  an oracle on 10,000 inputs) removed them. A foreign MIT-or-Apache-2.0 crate: 7 of 9 rebuilt, `average_floor` / `average_ceil` with 0
  mismatches on 1,000,000 pairs; specs for 64 % of its clean functions (**bar of 80 % missed**). Behaviour-only reader: 1 of 9 rebuilt.
  Applied to our C++ training engine through a probe driver: 6 operations, equation = engine on 128 / 128 rows each; the source reader found
  0 functions in the C++ source (it reads Rust and JavaScript only).
- **Failed probes, as registered:** predicting a failing box from good peers 3 / 368 (bar 50 %); fault localisation by code branch 0 / 5; a
  triangle-code retrieval below exact signatures (recall@5 0.77 vs 0.97).

## 5. The cores (docs 38–40)
- **Registry and receipts** (the `core-registry` program): one SQLite registry (core, version, kind, entry, gate, status; ops with an
  argument schema) and one append-only receipt file (input hash over arguments and input file bytes, output hash, verdict, milliseconds). A
  post-condition was added after exit status alone gave a false pass. Receipts as measured: 358 lines, 318 pass / 37 fail / 3 error
  (`docs/appendix/part7/ch5-registry/results/receipts-summary.json`). **Exception, disclosed:** the `math-kb` and `gen-core` programs hash
  argument strings only and leave the output unbound (17 of 18 and 33 of 59 receipts).
- **Hosting on pods.** `core-host` (ssh, cpu caps, path rewriting, sharded `map`), `corehostd` (loopback HTTP + WebSocket, a BELT v0
  priority queue with slots refilled continuously and a digest cache; slots drop while training runs), `thead-pod` (bring-up). corehostd
  test suite 5 / 5 on re-run. The doctor's 409-spec crate run is byte-identical on laptop and pod; `map` over 8 jobs 4.2 s against 20.9 s
  serial. **Negative:** corehostd was slower than a direct registry fire on 7 of 9 ops (expected: it wraps the same fire).
- **Embed core:** a static token table distilled from a sentence encoder (SIF-weighted sums; ternary 1.86 MB variant). Hybrid search
  recall@5 0.555 / 0.640 (hold-out) / 0.600 against the bar 0.775: **FAIL** in every arm; the speed ratios rest on a weak denominator (a
  60-item short-document benchmark), so only "hundreds of times faster" is claimed.
- **Chewer core:** agent sessions as step-sized chunks (deterministic ingest, FTS5 + vectors, rank fusion). Known-item recall@5: FTS 0.150,
  hybrid 0.115: **FAIL**; search finds the right conversation (0.935 top-5 session hit), not the right step.
- **Math core:** ten concepts as name-free specs, laws with teeth checks, emitted Rust (10 / 10 verified), generators and an explainer:
  explain names all 10 from fresh rows and returns `none` on 4 / 4 negative controls (re-run byte-identical); generator mutation refuses
  7,152 / 7,152 wrong answers.
- **Reservoir probe:** a fixed sparse ternary reservoir with a ridge readout to the teacher's vectors; all ten arms fail 0.775 (best 0.765;
  the same arm scores 0.705 with a second seed, so seed spread exceeds every between-arm difference); a post-hoc fusion maximum of 0.800 is
  not a pass.
- **Route core:** the dispatcher's lane router as a core (Beta posteriors per lane × task, ternary read-out, CRT codebook, Thompson
  sampling), in shadow mode; of 1,109 settled dispatches 33.8 % were infrastructure or rate-limit failures
  (`docs/appendix/part7/ch5-route/results/route_core0.result.json`).
- **Guard and redteam cores:** designed with pre-stated bars; **nothing measured**.

## 6. Provenance concepts (doc 41)
Rule: learn from everything, copy nothing — any published idea may be studied and re-made in our own words and code, each borrowed idea is
cited, no third-party source text, specification text or data row is copied into a shipped artifact.
- **Four clean-room forms**, and a statement must say which applies: (A) standard text only, other implementations run as black boxes; (B)
  two-team, where the guarantee holds on the implementer side (readers read admitted source or only behaviour); (C) idea level, procedure
  only, always paired with licence and secret scans; and, separately, the training-data guard.
- **Clean-room ledger** for the GPU kernels: 23 entries, append-only, hash-chained; the chain recomputes without a break
  (`docs/appendix/part7/ch6-clean-room-ledger/results/cleanroom-ledger.public.jsonl`). It holds no entry for the later array work, and its
  attestations are the authoring agent's own statements, not an independent audit.
- **Data gates:** the nearest marker decides (`.clean-room.json` allows, `.no-train.json` or no marker refuses); rows are kept only from
  models whose terms were read as permissive, unknown rows are dropped (`harness/part7/ch6-data-guard/cleanguard.py`).
- **Licence gates:** one licence per repository; Apache-2.0 code never contains PolyForm code; omni-spec's seven release gates, of which
  only attribution is done.
- **Growth ledger** (`grow_ctl.py`): one row per round with checkpoint, evaluation, plan and update hashes, gate evidence, decision and
  keep; `prev` chains rows; a tampered row is detected. Limits: no signature, no outside timestamp; the only field ledger is one wiring row,
  so no model that grew has been verified by it.

## 7. What has not borne fruit yet, and what is promising
- **Not yet:** no growth round completed on real data and no growth-rate number exists for any GPU tier; the group of 20 misses the
  registered 2 % parity bar (mean 4.1 %, max 9.7 %, GPU worse on 16 of 20; cause untested); 40 models cannot be built in one session; the
  G120 full-size weight check failed (830 M mismatched words); the 40-harness A40 launches finished no day; the 100 % stage gate has never
  closed a real round; the wall predictor's stall score is below chance; plain rows beat full traces in the one controlled format run; Omni
  Web is not light on script-heavy pages and its paint, frame-time and accessibility checks were not retained; the doctor missed the 80 %
  foreign-crate bar, rebuilds 1 of 9 from behaviour alone, cannot read C++, and three localisation probes failed; embed, chewer and
  reservoir cores fail their search bars; guard and redteam are unbuilt; the receipt hash exception is open.
- **Promising:** one core holds the earlier layers while learning the next when the build is circular; batching models in one recorded GPU
  step is exact per replica and 19–31× per model against the CPU engine; per-ring counters read the array's minimum cuts exactly on product
  traffic, in milliseconds; memory 2.9 % of Firefox on document pages; the doctor's gate series added 4,996 agreeing boxes with 0 lost, its
  kernel costs under 1 % of layout, and the clean-room gate refused every seeded leak; the math core identifies concepts from values with no
  false names.

## 8. Provenance (borrowed / ours)
The field's (each from the published description, no code taken): Skill-it (Chen et al., NeurIPS 2023), learning-progress curricula (Graves
et al., ICML 2017), curriculum learning (Bengio et al., ICML 2009), the spiral curriculum (Bruner, 1960), rehearsal (McCloskey & Cohen 1989;
Robins 1995), forgetting events (Toneva et al., ICLR 2019), A-GEM / GEM (Chaudhry et al., ICLR 2019; Lopez-Paz & Ranzato, NeurIPS 2017),
federated averaging (McMahan et al. 2017), local SGD (Stich 2019), DiLoCo (Douillard et al. 2023), model soups (Wortsman et al. 2022), STaR
(Zelikman et al., NeurIPS 2022), PAC learning (Valiant 1984; Blumer et al. 1989), Gomory–Hu trees (1961), Stoer–Wagner (JACM 1997), edge
connectivity of Cartesian product graphs (Klavžar & Špacapan), dimension-order routing (Dally & Seitz 1987), residue number systems (Szabo &
Tanaka 1967; Garner 1959; Mandelbaum 1972), direct-remainder computation (Lemire, Kaser & Kurz 2019), division by invariant integers
(Granlund & Montgomery 1994), hash chains (Haber & Stornetta 1991), CUDA Graphs (launch-overhead practice), the multi-process browser (Grier
et al., IEEE S&P 2008; Reis & Gribble, EuroSys 2009), Landlock and seccomp-BPF, AccessKit and AT-SPI, RFC 9110 / 9112 / 6265 / 6455, WCAG
2.x contrast, test262 (TC39), signed-distance rounded boxes (Quilez), box-filter Gaussians (Wells 1986), lazy parsing and hash-consing (V8;
Ershov 1958; Filliâtre & Conchon 2006), differential testing (McKeeman 1998), equality saturation (egg, Willsey et al., POPL 2021), babble
and Stitch (POPL 2023), DreamCoder (PLDI 2021), anti-unification (Plotkin 1970; Reynolds 1970), TRANSIT (PLDI 2013), CEGIS (Solar-Lezama et
al. 2006), λ², Myth, FlashMeta (2015), oracle-guided synthesis (Jha et al., ICSE 2010), overfitting in test-based repair (Smith et al., FSE
2015), XFix (Mahajan et al. 2017), Ochiai and Tarantula fault localisation, partitioned IFS (Jacquin 1992), Cassius (Panchekha & Torlak,
OOPSLA 2016), parallel layout (Meyerovich & Bodík 2010), two-team clean-room design ("Chinese wall"), Higham's summation bounds, RMSNorm
(Zhang & Sennrich 2019), linear attention (Katharopoulos et al. 2020), Model2Vec (Minish Lab 2024), SIF (Arora et al., ICLR 2017),
reciprocal rank fusion (Cormack et al., SIGIR 2009), echo state networks and liquid state machines (Jaeger 2001; Maass et al. 2002),
Thompson sampling, replay evaluation of bandits (Li et al., WSDM 2011), mutation and property-based testing (DeMillo et al. 1978; QuickCheck
2000), vLLM's scheduler shape (Kwon et al., SOSP 2023). Ours: the round loop over a skill graph with a sticky-proof guard on shared skills;
circular builds by splicing; the 100 % stage gate with an independent-row sample size and a hash-chained growth ledger; the school step as
emitted GPU passes behind the engine's own ABI; replica and centre forms in one recorded step; the T50 omniring hub as one 512-bit register;
toroid-to-toroid routing with ring counters; the dual-T50 cut read and the toroid mailbox; a browser whose chrome and page are drawn by our
engine from one tree that also feeds accessibility; the contrast law for translucent chrome; the merge gate and engine-pin rule; the
doctor's code alphabet, black-box law synthesis, geometric triage, T25 box kernel firing inside layout and pristine fix loop; the two-team
clean room with a name-free spec, a leak-scanning gate and an equation gate; the core registry with receipts and post-conditions; BELT v0;
the math core's explain station; four named clean-room forms with stated guarantees. None claimed as first without a wider prior-art search;
all dated here.

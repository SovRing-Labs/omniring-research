# DOCTOR-INTERP-0 — plan (claude seat, 2026-10-07). Brief: `DOCTOR-INTERP-0.brief.md`. Board: DOCTOR-INTERP-0 (staged).
Worktree: `projects/omni-render-claude` (branch `claude/work`, from main 7fbd83b). Tests: `projects/doctor-core/tests/INDEX.md`.

## Grounding (read 2026-10-07)
- CODE-ABC STATUS LOG (`<plan>:35-99`): A1 lowers layout.rs 51.6 % clean; FF-SYNTH 22/24 from examples alone; next = TYPES-0 → SKETCH-0.
- `src/doctor_abc.rs` `need()` (L1436): a need = `{need, args:[int|list], examples, holdout, validate}` → library search → `--build --ff` →
  CEGIS → rustc verify. **That JSON is already the spec minus equation/effects/provenance** → the implementer exists (CLOSE).
- A1 signatures are name-free already (`v0…`, ops, numbers; strings → `str`, fields → input slots) → the reader's writing tool exists (CLOSE).
- AST-REVIEW-RESPONSE §2: SKETCH-0 = while → loop(state, cond, step), match → case; kill 0/5 of gcd, dot, ceil_div + 2 real whiles.

## Steps (first loop at the expression level, then widen)
| # | Step | Class | Verify | Bar / kill |
|---|---|---|---|---|
| S0 | Worktree + plan + INDEX search | CLOSE | `git -C projects/omni-render-claude branch --show-current` = claude/work | — |
| S1 | READER `core --abc spec --src F --out specs.jsonl`: per lowered fn output with Int/List inputs (≤ 4) and ≤ 20 % opaque: `{spec, args, equation, examples, holdout, validate, effects, provenance{src_sha256, licence}}`; examples = the reader evaluating the equation on probe + seeded inputs; no names, no lines, no spans | BUILD | run on src/layout.rs → count specs; `grep -c` of fn names in the file = 0 | ≥ 1 spec per 3 clean fns |
| S2 | WALL `core --abc wall --specs F --src F…`: schema whitelist (only spec keys); every string value checked against the source's identifiers (≥ 3 chars, non-keyword), comment words, string literals; refuses the row with the reason | BUILD | seeded-leak harness: copies with a name / comment / literal / extra key injected → refused 100 %; clean specs → passed 100 % | < 100 % refusal → fix before S3 |
| S3 | IMPLEMENTER on wall-passed specs: `need --needs specs.wall.jsonl --build --ff` with the library built WITHOUT the source file (`--src` = other files only) | CLOSE | rows: built + rustc-verified + validate agree | report rate; 0 built → stop, report |
| S4 | SKETCH-0 statement layer (I1): while/loop → loop(state, cond, step); match → case | BUILD | `core --abc lower --src src/layout.rs` share rises; 5 SKETCH needs | 0/5 → stop (AST review kill) |
| S5 | Records: tests/INDEX rows, CODE-ABC + this STATUS LOG, doctor-core MANUAL § spec/wall, DEVLOG | CLOSE | `grep -n "abc spec" docs/systems/doctor-core/MANUAL.md` | — |
Later (brief I3–I7): readers on an admitted foreign codebase; jsi + test262 as target; THEAD proposes / doctor decides; evolve builder strategies.

## Rules
Kernel tools; builds under `timeout`, logs kept; tests ≤ 20 min under tw; commit on J's word, never push; one heavy CPU job at a time.

## STATUS LOG
- 10-07 S0 done: worktree `projects/omni-render-claude` on claude/work (7fbd83b). INDEX searched: only RSS rows; no spec / wall test exists.
- 10-07 S1 PASS: `core --abc spec --src src/layout.rs` → 138 fns, 70 clean, 150 outputs → **32 specs** (bar ≥ 1 per 3 clean fns = 24);
  skips: 68 fns over the opaque ceiling, 50 leaf outputs, 33 with 0 / > 4 inputs, 25 with < 12 defined examples, 8 duplicates, 2 constant.
  Bug found + fixed: slice bound when < 16 defined examples.
- 10-07 S2 PASS: `core --abc wall … --seed-leaks` → clean 32/32 passed, seeded leaks **256/256 refused** (8 kinds × 32; leak scan alone
  253/256 behind the schema). Fixes on the way: the wall's own vocabulary (reader id "doctor-…") matched a comment word; lexer keeps
  string text in the byte span, not `Tok.s`; one-word literals matched inside keys / as alphabet ops → whole-word + op exemption.
  Results `projects/omni-render-claude/results/doctor-interp/s1-s3/` (spec.layout.json, wall.layout.json, specs*.jsonl).
- 10-07 S3 PASS (first clean-room loop closed on our own code): implementer = `need --needs specs.layout.wall.jsonl --build-all --ff`,
  library = every other src file (1,353 fns, 5,516 terms; layout.rs excluded). Run 1 (examples-only gate): 27 built + rustc-verified, but
  hand check found overfits passing all 16 validate rows (`max(a0,a1,0)+min(a0,a1,0)` → `min(a0+a1,max(a0,a1))`; `sel(a0,0,a1)` →
  `a1·(a0%15==0)`). Fix = the brief's EQUATION gate: `spec::equiv` parses the spec equation back into the e-graph and runs it as oracle on
  10k inputs (signed edges, i32 bounds, 3 random scales, lists 0..8); a disagreement is a CEGIS counterexample. Run 2 (tw interp-s3b,
  48 s): **27/32 built from the spec alone, rustc-verified, equation-gated; validate 26/26 (1 spec has no validate rows); the gate fed
  counterexamples to 7 specs** (e.g. `not a0` 6 rounds, `sel(a0,0,a1)` 5 rounds → `a1·(a0==0)`). Library also answers 27 → 31/32.
  NOT built (5): SplitMix-style xor-shift-multiply ×2 and a 128-bit packed fold (size > builder), `a0+a1+a2[1]+a2[3]` (no constant-index
  witness), tuple output (verifier prints int / list only). Results `…/s1-s3/impl-eq.layout.{jsonl,log}`.
  Next: S4 SKETCH-0 (statements → coverage: 68 of 138 layout.rs fns are over the opaque ceiling); builder gaps above as needs.
- 10-07 COMMITTED omni-render-claude claude/work 644ecc0 (J "commit"). Staged beside it (J): EMBED-CORE-0, CHEWER-CORE-0 (briefs in this dir).
## NEXT (seat proposal 10-07, in order)
| # | Step | Bar |
|---|---|---|
| N1 | S4 SKETCH-0: while / loop / match / if-let lowered (loop(state, cond, step), case) — more functions readable → more specs | layout.rs clean fns 70 → ≥ 97 (70 %); 5 SKETCH needs, kill 0/5 |
| N2 | Builder gaps from S3 as needs: constant-index witness (`a2[1]`), tuple outputs in the verifier, hash mixers composed from library words | 3 of the 5 S3 misses built |
| N3 | Merge gate → omni-render main (tool only; baseline 18,296 unchanged) | merge-gate PASS |
| N4 | I3 first FOREIGN reader run: one small permissive codebase admitted by D9 (MIT / Apache) → specs → wall → implementer | specs for ≥ 80 % of its clean fns; rebuilt pass the specs + its own tests |
| N5 | Black-box reader: spec from behaviour only (probe a binary / engine, no source) — the Chrome loop generalised | same wall, same implementer, ≥ 1 module rebuilt |
| N6 | I5 interpreter target: test262 harness for jsi; each failing case → counterexample → spec → implementer (feeds JS-COMPILE-0 / OMNIGLYPH-INTERP-0) | pass rate measured per round |
- 10-07 N1 SKETCH-0 (statement layer) — built in omni-render-claude: `match` / `matches!` → sel chains over pattern conditions (literals, `|`,
  ranges, tuples, guards, unit-variant tags = name-free hash ints, Some/None = value / NONE sentinel); `if let` / `while`-cond via the
  same patterns; `while c {…}` → while0(init, c, step) over the state tuple (st{d}.k), `loop { if c {break;} … }` → while0(¬c),
  `loop { …; if c {break;} }` → while1 (break-test, exit after step); other loops keep the opaque path. Evaluator runs while (cap 10k).
  Coverage: layout.rs clean fns **70 → 89** (50.7 → 64.5 %; bar 97 NOT met — the rest is TYPES-0: field-of-value 83, .push 79,
  call cov 74, line! 74, variant pattern 72, .s() 69); crate 700 → **1,021** (41.5 → 60.3 %).
  Correctness: 10 hand functions (gcd, digits, collatz, do-while, match, matches!, Option, tuple match) — reader examples vs rustc on
  the real functions: **10/10 specs agree, 320 rows** (`results/doctor-interp/sketch0/check.py`).
  IMPLEMENTER route 0 `need --emit` (`spec::emit`): the spec equation printed as our Rust (wrapping semantics; while → loop over a state
  tuple), rustc-verified on spec rows + 2,000 oracle rows. Sketch specs: synthesis alone 5/10 (no loops) → emit **10/10** (all 5 loops),
  6 s. layout.rs with SKETCH lowering + `--max-inputs 8`: 38 specs, wall 38/38 + 304/304 leaks refused, **27 rebuilt from spec alone**
  (25 emit + 2 synth), 34/38 answered with library. Emit gaps (→ N2): lists (idx / len / fold), tuple outputs, get on a selected tuple.
  Bug fixed on the way: FF-SYNTH `Bank::find` panicked on an empty interval (lo > hi). SKETCH kill bar (0/5) not hit: 5/5 loops built.
- 10-07 N2 PASS: emit route gains list args (`&[i64]`), len / idx / sum, fold over a list (its indexes) or a range (its values), tuple
  outputs (`[i64; n]`), list-typed oracle rows; reader refuses an input it projects as a tuple ("tuple-typed input", 18 in layout.rs —
  fixes the `(get2 a2)` int-typed spec). layout.rs: 36 specs, wall 36/36 + 288/288 seeded leaks refused, **34/36 rebuilt from the spec
  alone** (33 emit + 1 synth; 6 list-input, 2 tuple-out, 4 fold), 36/36 answered. S3 gaps: **5/5 closed** (both xor-shift mixers, the packed
  fold, constant index, tuple out; bar 3/5). Misses left: fold over a slice idx(list, range), filter over tuple elements.
  Results `projects/omni-render-claude/results/doctor-interp/n2/`. tw n2-layout.
- 10-07 N3 PASS: merge gate (parameterised copy `results/doctor-interp/n3/merge-gate.sh`, OLD = main 7fbd83b built in a throwaway worktree,
  NEW = claude/work 6963427; tw n3-merge-gate): baseline equal (replay 20,973 / holdout 3,059), check-compiled 0 different, binary gate
  0 lost / 0 gained, JS probe 106/106, conn 13/13. main fast-forwarded → 5ad1012 (6963427 + gate results). Other seats' 118 dirty files untouched.
- 10-07 N4 (first FOREIGN clean room): num-integer 0.1.46 (`MIT OR Apache-2.0`). D9 header rule refuses lib.rs (foreign copyright header) →
  readers took roots.rs + average.rs only. A1: 27 fns, 14 clean → **9 specs** (64 % of clean fns; bar 80 % NOT met — 5 outputs were leaves,
  4 duplicates); wall 9/9 passed, 72/72 seeded leaks refused; implementer with OUR library only (no crate code): **7/9 rebuilt** (emit:
  both bit-trick averages, root initial guesses, the nested Newton loop). Black-box proof: rebuilt average_floor / average_ceil vs the real
  crate on **1,000,000 i64 pairs incl. extremes: 0 mismatches** (`results/doctor-interp/n4/blackbox-check/`). Misses: 2 specs carry a unit
  value from an early-return branch (reader artifact → reader must drop specs with a unit leaf). Crate's own test suite not run: its tests
  call generic trait methods, our rebuilds are i64 equations (→ a module layer that reassembles whole functions, brief I4).
- 10-07 TYPES-0 PASS (AST-review order: coverage): two-pass lowering — pass 1 collects SUMMARIES of same-file fns (params, input slots,
  single return, clean = 0 opaque / no effects / no writes); pass 2 inlines a clean callee at its call (params → args, `self.x` → caller's
  `self.x`, loop depths shifted by the caller's depth so inlined loops never shadow the caller's state); unit-returning calls = effects
  (non-opaque); `line!()` = its line constant; a method result read by field = a STATE VIEW input slot (name-free); `.push` = push op
  (env update), `.get(i)` = bounds-checked idx / NONE, `.is_empty()` = len == 0. Reader drops specs with a unit value (early-return
  artifacts); wall alphabet gains `push`.
  Coverage: layout.rs **89 → 112 / 138 (81.2 %; bar 97 PASS)**; crate 1,021 → **1,158** (68.1 %). Correctness: types check 9/9 = rustc
  (inline across files order + inside a loop), sketch 10/10 still. Clean room: layout.rs 37 specs, wall 37/37 + 296/296, **35/36 rebuilt**
  (33 emit + 2 synth); num-integer **7/7 rebuilt** (spec share 7/14 clean fns — 80 % bar still missed: generic-trait fns over the ceiling).
  Commit 862e0b9 (claude/work). Results `results/doctor-interp/types0/`.
- 10-07 TYPES-0 + N4 merged: gate 862e0b9 vs main 5ad1012 (baseline equal 20,973/3,059, 0 different, 0 lost, JS 106/106, conn 13/13) → main fast-forwarded.
- 10-07 N5 (black-box reader): `core --abc blackbox --cmd BIN --fn F --args …` probes a program (stdin lines → numbers, `x` = undefined)
  and writes examples-only specs (no equation); the reader keeps a PRIVATE oracle map (need id → program, fn); the wall accepts specs
  without an equation (equation optional; seeded-leak harness now always injects); `need --oracle-map M` = the live oracle across the
  wall (need id + inputs in, numbers out) feeding CEGIS. `verified` now also requires every validate row (was: examples + holdout only —
  run 1 reported 7/9 "built", all overfits, validate 24–60/64). Target: num-integer lib.rs (text refused by D9) as BEHAVIOUR via a
  driver on its public API (gcd, lcm, div_floor, mod_floor, div_ceil, is_multiple_of, binomial, sqrt, cbrt). Wall 9/9 + 72/72.
  Result: **1/9 rebuilt from behaviour alone** — div_ceil = `(a0 + a1 + (a0<0 ? −max(a1,−1) : −min(a1,1))) / a1`, **0 mismatches vs the
  black box on 200,000 mixed-scale pairs**; 8 refused (never accepted wrong). A 1e6-only oracle let a range overfit through
  (`1175 + (a0 − 1175·a1)/a1`, 20/199,595 wrong) → oracle probes now ±1e12 + mixed scales. Gap = builder strength (Euclid loop, floor
  sign logic, roots) from behaviour → brief I7 (evolve the builder's strategies on held-out needs). Results `results/doctor-interp/n5/`.
- 10-07 N5 merged: gate 74b13b0 vs main 0817f3a (equal, 0 different, 0 lost, 106/106, 13/13) → main fast-forwarded.
- 10-07 N6 prep: test262 cloned (J go) → <home>/projects/test262 (c8c79889, 53,908 tests, BSD, .no-train.json, LOCATIONS row).
- 10-07 GPU-LOOP prep (J: briefs for 2 parallel Opus seats + "continue with your share"): briefs `spawn-briefs/active/FLEET-LOOP-REG-builder.md`
  (board FLEET-LOOP-REG) + `<plan>builder.md` (board <plan>); contract `<notes>/worker/claude/CORE-REGISTRY-CONTRACT.md` v1;
  sparse worktrees `<projects>/ai-stack-opus-reg`, `<projects>/ai-stack-opus-raptor`, `<projects>/opencode-launcher-opus-raptor`
  (ai-stack tracked tree = 18 GB vs 7 GB free → sparse cones; runtime files stay at main-tree paths).
- 10-07 FLOAT-0 (track A, critical path for GPU-LOOP G1): Val::F + float-aware evaluator (f32 promote like C, sqrt / exp / ln, float sums),
  `same()` tolerance (rel 1e-4 + abs 1e-5) in every row check, reader types inputs f32 / f32list from the fn signature, wall accepts float
  rows + types (+ `exp` `ln` in the alphabet, `f32` type names exempt), TYPED emit printer (int / f32 / bool / list / tuple per node; map →
  Vec output), emit check reads rows from a data file (2,000 unrolled vec! asserts had rustc -O stuck > 10 min). Float set (dot, sumsq,
  rms_scale, relu, lerp, mean, logistic, scale_row): wall 8/8 + 64/64, **emit 8/8 verified**, reader rows = rustc f32 **8/8 (247 rows)**;
  int regression unchanged (sketch 10/10, types0 33/37, n2 33/36), all four sets in 26 s. Commit c2… (claude/work).
  Next: engine ops — black-box f32 reader on a C++ driver that includes omni_train.cpp (dot8, rms_fwd row, sgemm small), equation = the
  op's published math authored on the reader side and CHECKED against every engine row before the spec is written; emit; parity.
- 10-07 ENGINE-0 (GPU-LOOP G1, first ops): probe driver `results/doctor-interp/engine0/driver.cpp` includes our engine read-only (dot8, rms_fwd
  row, sgemm). Black-box reader typed (f32 / f32list / int, `--len 0=a2*a4` shape constraints, `--int-range`, `--ret`) + `--equation`
  authored on the reader side from the op's PUBLISHED math (dot product; RMSNorm with torch f32 eps; GEMM) and CHECKED against every
  engine row before the spec is written (refuse on any disagreement). Evaluator + printer: a loop's depth = 1 + enclosing when its body
  uses it at its own level (a fold nested in a map refers to the map's index — "first / min placeholder" both failed; sgemm caught it).
  Results: equation = engine **128/128 rows** for each op; wall 3/3 + 24/24; **emit 3/3 verified** (2,084 / 2,084 / 1,281 rows);
  independent parity ours vs engine on 20,000 fresh rows per op: plain rel 1e-4 flags 2 dot8 + 88 sgemm rows (cancellation, max rel
  0.9 %), the standard sum bound 2·n·u·Σ|a·b| (Higham §3.1) → **0 / 60,000 outside**. Rerun `results/doctor-interp/engine0/rerun.sh`.
  Follow-up: the doctor's `same()` should take the condition-aware bound for sums (today rel 1e-4 + abs 1e-5).
- 10-07 FLOAT-0 + ENGINE-0 merged: gate dbc8ebe vs main 9409643 (equal, 0 different, 0 lost, 106/106, 13/13) → main fast-forwarded.
- 10-07 ENGINE-0 batch 2: rms_bwd dx + dg (RMSNorm backward) and mem_fwd_core (causal linear attention over bucket masks, phi = elu + 1,
  Katharopoulos et al. 2020) — equations authored from the published math, = engine on 128/128 rows each. Cancellation (rms_bwd_dx, D=1)
  showed the |inputs| twin is too weak (it still subtracts) → Ev::absm magnitude mode (f32 on |values|, − as +, the running-error M of
  Higham §3.1); reader check + emit check use (2n + 16)·u·M per element. TEETH: rms_bwd_dx with the r³ term doubled → refused 128/128;
  mem_fwd without the bucket mask → refused 97/128. `--list-range` for int-list probes (bucket ids 0..2). Emit: **6/6 engine ops verified**.
  Parity vs an fp64 reference (fresh seed, 5,000 rows/op): **0/15,000**; max err/M ours 2.8–3.7e-7 vs engine 2.1–3.8e-7 (same class).
  Files: `results/doctor-interp/engine0/{driver.cpp,specs2*.jsonl,impl.specs2.jsonl,parity3.py,parity3.json,ours2.rs}`.
- 10-07 ENGINE-0 batch 2 merged: gate 95210c2 vs main 5ac697e (equal, 0 different, 0 lost, 106/106, 13/13) → main fast-forwarded.
- 10-07 FLEET-LOOP seats verified + merged (claude seat): REG 17/17 tests, cores.db 5 cores, receipts incl. caller raptor-ui; RAPTOR test_cores_api 31/31, live :47811 /cores = 5; opus-raptor/work merged into ai-stack t126-lifecycle-spine (bd1a3bce9; REG already in). GPU-LOOP-0 start condition met. Handoff: <notes>/worker/claude/DOCTOR-INTERP-0.handoff.md
- 10-08 N6 BASELINE: `results/doctor-interp/n6/test262.py` (test262 c8c79889 rules: harness + includes, flags onlyStrict / module / raw / async, negative
  phase + type; one mode per test; print shim) against `omni-render js-src` (native parser → jsi). **29,203 / 53,607 pass (54.5 %)**, 8 min 17 s, 6 jobs
  (tw n6-test262-full); ≈ 62 % without Temporal (0 / 6,634, not implemented). Areas: String 81 %, Object 81 %, statements 74.5 %, expressions 70 %,
  Array 68 %, RegExp 38 %, TypedArray 39 %. Fail classes: ReferenceError 7,734 (missing globals) · Test262Error 7,674 · parse-negative accepted 3,756
  (early errors not detected) · TypeError 2,748 · async failures ~950 · 107 timeouts · 44 crashes. Results `n6/{baseline.json, full.jsonl.zst, full.summary.txt}`.
  Next (I5 loop): each failing class → spec / counterexample → implementer; rounds measured against this baseline.
- 10-08 test262 ROUND 1 (on cpu16, 142 s): strict tracking + assignment-target early errors → 29,662 / 53,614 (55.3 %), +459, **0 regressions** (compare.py). Next: round 2 = function-level early errors (duplicate params, yield/await bindings, delete #private).
- 10-08 test262 ROUND 2 (cpu16): function-level early errors → 30,475 / 53,614 (56.85 %), +813, **0 regressions** after fixing function-expression names inside generators (3 false refusals in run r2); 5 slow Array tests (~28 s) need the 60 s timeout. Commit on claude/work; merge gate pending.

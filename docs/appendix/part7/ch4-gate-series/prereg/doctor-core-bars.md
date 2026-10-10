# DOCTOR-CORE — plan (seat, 2026-10-05; J vision readback confirmed same day)
> **Lineage — the doctor core now has its home (2026-10-07):** `projects/doctor-core/README.md` · manual `docs/systems/doctor-core/MANUAL.md`.
Lineage: <plan> (stations, +318 boxes) · REPAIR-CORE-HANDOFF.brief.md §3 · PIFS-RES-0 dossier (2026-10-02) ·
projects/arc-reactor/README.md §1–2,6 · projects/thead-generators/README.md §2–3 · VOCAB (IFS, core, ARC dock).

## Vision (J 10-05, confirmed)
A ~50 MB core that learns and repairs our in-house apps one at a time (renderer now, launcher next): finds code sections with
similar layout by REVERSE PIFS (the collage search used as donor retrieval: range = broken section, domain = working
section, map = the transform that carries one onto the other), applies known-good combinations, tests with logic + the app's
judge, keeps a knowledge base of verified fixes. Plugs into the ARC reactor dock as a harness-side core; generators = jury.

## Renderer steps (each with verify)
| # | Step | Class | Verify |
|---|---|---|---|
| D0 | Section index: cut src/layout.rs into sections at code joints (fn → loop → if-arm, adaptive), each a shape vector (identifiers α-renamed, AST n-grams; Deckard-style characteristic vectors, Jiang ICSE 2007) + a subject vector (identifiers/terms) + the ledger terms/rules it owns | BUILD | `omni-render core sections --stats` prints N sections, 0 parse failures |
| D1 | Reverse-PIFS search: range = sections reached by the open problem's stages (table column widths); rank domains by collage error after the best identifier map; output donor + map | BUILD | blind probe: for `table()` width distribution the top-3 donors include grid track sizing (parse_tracks / grow-to-limit) — PASS/FAIL logged either way |
| D2 | PATCH station: port the donor's missing clause through the map on a git worktree clone, build, screen, gate (0 lost) → PROPOSED branch | BUILD | worktree branch exists; gate log shows fixes>0, lost=0, baseline 14,935/2,774 unchanged elsewhere |
| D3 | Jury: generator laws as a second gate on the REASONING of a fix (units.dimension on px/%/fr terms, logic.chain Horn consistency, causal.dag identification, code.debug patch soundness) via arcd | CLOSE | jury verdict per fix in the trace; a planted unit-mixing patch is refused |
| D4 | Doctor traces → layout.repair generator rows (plan v3 L) | J | J decides integration |
| D5 | ARC dock: problems/stations get CRT addresses (port rings: generator·stage·station), T10 recall = codebook recall | J | J decides wiring |

## Status log
- 10-05: plan written. Slips fixed first: acc9008 (program committed), stray root files → repair-core-stray-1005/, open cards restored (provisional).
- 10-05 D0/D1 built (omni-render 08d7085, src/doctor.rs): layout.rs → 5,263 sections (fn 115 · stmt 1,710 · run 3,438) in 2.6 s.
  D1 blind probe PASS: table() width distribution (L1666–1679) → top-1 donor grid track sizing L2268–2286 on 4/4 ranges, collage
  err 0.51–0.54, map fr→fixed ncols→ncol w→mx want→auto_mx; table() min/max pass (L1650–1664) → intrinsic_w table branch L608–621
  (err 0.28), lacking line 610 = spanning-cell widening (CSS 2.2 §17.5.2.2). 4.8 s for 8 ranges.
- 10-05 D2 gate built (`core corpus --patch-gate --clause patch.K[C]=-1`; dormant patch switch `Layout::patch`, weight −1 = port on).
  Port #1 (span widening, worktree ../omni-render-doctor branch doctor/table-span-widen): dormant base exact 14,935 / 2,774;
  ON: fires (HN table 54: 31 spanning cells) but 0 lost / 0 gained → FAIL (no gain): columns already cover the spans. Donor
  structurally right, not causal. Lesson: shape similarity finds candidates, the gate decides; record negative knowledge.
- 10-05 Root cause of the largest "no knob" card (w-|TableCell|TableRow 21 inst, −340 px): 18/21 on github-com-servo-html5ever,
  whose CSS declares table-layout:fixed ×10; the engine never parsed table-layout (explain.rs:70 lists it as unsupported).
  Doctor capability this exposes (to build, D1b): MISSING-FEATURE diagnosis = properties declared on the broken boxes' ancestors
  that the engine does not implement → no donor exists in-file; the fix is a feature, written from the spec. Port #2:
  table-layout:fixed (CSS 2.2 §17.5.2.1, clean-room) as patch.table_layout_fixed, gate run pending.
- 10-05 TOOLING: kernel MCP `edit` truncated src/layout.rs to 131,081 bytes (2,381 → 1,928 lines) and reported success; restored
  from HEAD. Large files: edit via python in `bash`. Spawned task "Fix sovereign-kernel edit truncating large files".
- 10-05 Port #2 gate PASS: patch.table_layout_fixed[Table]=-1 → replay 14,935 → 15,007 (+72, github), holdout 2,774 → 2,774, lost 0/0;
  check-compiled 521,192 / 0 different; verifier 11 clauses OK; AGM launcher: INVALID (does not fire), 0 dropped. Branch
  doctor/table-span-widen f00b6af (PROPOSED, not merged, not pushed). Total agreement if merged: 17,709 → 17,781.
  Logged: run log rows doctor-d1/gate1/gate2 · Part 6 §4 · MANUAL § DOCTOR core · <devlog-entry>.
- NEXT (seat): D1b missing-feature station (declared properties on broken boxes' ancestors ∖ properties the engine parses →
  card), then rerun `--fire` on the proposed program to refresh the open cards (current open.jsonl is from the stray old-program
  run); D3 generator jury (units.dimension first). J: merge f00b6af?
- 10-05/06 J: "continue, merge". Merged doctor/table-span-widen (d1bea0c) + program clause (2c0717d): main 15,007 / 2,774.
- 10-05/06 D1b missing-feature station built (d0b4d78, `core corpus --missing`): declared props on broken boxes + 4 ancestors minus
  style.rs match-arm literals + guard arms, ranked count × lift vs 1/8 of agreeing boxes. 5.7–6.8 s.
- 10-05/06 D2′ binary gate (5f35fb1, `--agree-snapshot` / `--binary-gate`) for style-level changes the program cannot switch.
- 10-06 logical insets (CSS Logical L1 §4.3) +10, 0 lost → merged a3d043a.
- 10-06 aspect-ratio (CSS Sizing 4 §5.1): unconditioned +287 / −2 FAIL (bbc live icon in an inline-flex parent: ancestors lose);
  all flex items excluded +19 PASS; conditioned on parent display (not inline-flex/grid) **+285 (holdout +124), 0 lost PASS** →
  merged 804b2f7. Open card: inline-flex parent baseline after an aspect-sized child.
- STATE 10-06: replay 15,178 / holdout 2,898 = **18,076 of 28,010 (64.5%)**, up from 17,709 at this session's start (+367) and
  17,391 hand-fixed (+685). check-compiled 521,192 / 0. Next missing cards: font-feature-settings ("calt" 0, 16 broken),
  overflow-wrap (21, 6 pages), font-variant-alternates, grid justify-items / align-content, border-block/inline shorthands.
- 10-06 J asked for field tools to learn from (clean-room). Map (papers only, no code): ssFix (Xin & Reiss 2017) / SimFix (Jiang
  et al. ISSTA 2018) / GenProg (Le Goues 2012) = donor search; CodePhage (Sidiroglou-Douskos et al. PLDI 2015) = cross-app transfer
  (launcher); Getafix (2019) / Prophet (Long & Rinard 2016) = learned patterns + ranking; SemFix / Angelix / Nopol + CEGIS = SAT /
  solve stations; Tarantula / Ochiai SBFL + delta debugging (Zeller) = D1b ranking + causal check; XFix / IFix (Mahajan et al. ICSE
  2017) = search-based layout repair vs a visual oracle; WPT = second judge (check licence); Repairnator = propose-then-human-merge.
  NEXT BUILDS: (a) D1b → Ochiai + one-declaration delta check (would have dropped overflow-wrap and calt); (b) D1 donor ranking by
  fix types that worked (SimFix); (c) read CodePhage before the launcher.
- 10-06 overflow-wrap (CSS Text 3 §5.5): unit-correct, corpus 0/0 → held on branch doctor/overflow-wrap (correlation card).
  justify-items (Box Alignment §6.1): +34 MDN / −134 bbc FAIL; place-items not the cause; debugging bbc grid items.
- 10-06 justify-items / place-items (Box Alignment §6.1/6.3) — 4 tries: +34/−134 (bbc nested grids: our grid max-content too small →
  held back for grid-container items) → +34/−2 (grid centring ignored item margins: margin box now centred) → +30/−2 (MDN logo
  margin-left −6: only positive margins count, measured) → **+34, 0 lost PASS** → merged e3dda23. Main 18,110.
- 10-06 D1b → Ochiai (SBFL) + negative-knowledge file (font-feature/alternates/variation inert: no shaping; overflow-wrap gated 0/0).
- 10-06 **D2c condition search built (`--patch-search`, 89d7454)**: gates a dormant patch under every node-feature literal of its
  context, then pairs; keeps the best zero-loss clause. First run on border-spacing/border-collapse (CSS 2.2 §17.6): unconditioned
  +132/−14; 84 literals, 311 gates, 472 s → `[Table&tag=table&w_set=0]` **+76, 0 lost** → merged 5e56e79 + program clause.
- STATE 10-06: **18,186 of 28,010 (64.9%)**; session +477 (17,709 →), hand-fixed +795 (17,391 →). Verifier 12 clauses, compiled parity
  586,341 / 0, AGM launcher 0 dropped. Open cards: grid max-content of grid containers; inline-flex baseline after an aspect child;
  collapsing border model (wikitables, navbox subgroups); align-content; D2c → greedy multi-clause cover (+56 more possible on spacing).
- 10-06 D2c multi-round (greedy cover, `--rounds`): border-spacing round 1 +9 ([Table&bb=0&mb=+]), round 2 +1 ([Table&ovf=1]), round 3
  none → cover complete; +10, 0 lost, 788 gates, 1,355 s → results/omr.program.search2.json (adopt after the 5-min CPU break J asked
  for). Remaining border-spacing loss sits in the collapsing border model (open card).
- 10-06 Peer (IR-JIT-NEXT plan review) asks, for J: port rows8 batch sift (779e60e, 1b4b3ab; same repo) into the doctor; measure sift
  share in --donors and --fire recall first; Pool only if the fire profile shows per-tick fan-out cost; tick-memo key on hv recall.
  Report numbers back to that session. Plan step D6.
- 10-06 search2 adopted (7245125): 14 clauses, main 18,196. CPU break 5 min (J) after the search.
- 10-06 D6 rows8 (peer IR-JIT-NEXT, for J): measured first — sift = 6 ms of ~2 s donor search (0.3%); fire sieve = 1 query × 15 rows.
  Cherry-picked 779e60e + 1b4b3ab (ir.rs bench kept at main: depends on huge-pages commit 1a1419d); hv::sift_batch; donors batch.
  Parity 0 / 15,767,316; warm 3.2× (8 q) – 4.6× (2,934 q); merged 5afc52f; main unchanged 18,196, parity 586,341 / 0. Numbers sent
  back to the peer. Next speed lever for D1 = the LCS collage (124 s for a 2,934-range scan), not the sift.
- NEXT: grid-container max-content (CSS Grid §12 track sizing, fr share) — open card from justify-items (bbc nested grids).
- 10-06 grid container intrinsic width (CSS Grid §12 / §12.7.1, clean-room): **+32, 0 lost**; then the justify-items hold-back for
  grid-container items was lifted (its cause fixed): +33 total, bbc 0 lost → merged b41753c. Main 18,229.
- 10-06 grid align-content / place-content (Box Alignment §5.1, Grid §11.8): **+12 (bbc), 0 lost** → merged eda389e.
- D1b list is now down to 1-box cards (border-block/inline shorthands) + negative knowledge. Next: refresh the open cards with a
  `--fire` run on the new engine (stale since the stray old-program run), then the largest remaining card.
## J 10-06: build SimFix ranking + automatic transplant, then weigh codebase vectorisation, then research to evolve the doctor
| # | Step | Class | Verify |
|---|---|---|---|
| D7 | SimFix-style ranking: transplant ledger `results/doctor.transplants.jsonl` (range fn, donor fn, edit class, outcome); edit-class prior = (passes+α·seed)/(tries+α) seeded from seatfix class counts; donor rank = collage err − λ·log prior | BUILD | `--donors` prints the prior per donor; ledger rows appear after a transplant run |
| D8 | ssFix-style transplant: doctor emits per donor statement lacking in the range: renamed text (map), insertion line (after the range statement aligned before it); `tools/doctor-transplant.py` inserts `if self.patch(n, "patch.t<id>") { … }` on a worktree branch, builds, patch-gates `[*]=-1`, records outcome (build-fail / no-gain / lossy / pass) | BUILD | table() run reproduces the span-widening port automatically (expected 0/0 = no gain, as by hand) |
| D9 | Codebase vectorisation options brief (fleet-kb FTS, vault nomic embeddings, omnid HV shards, doctor D0 shape/subject index) — cost/benefit for cross-app donor search | J | brief in <notes>/FOUNDATION + summary to J |
- 10-06 D7 built: SimFix-style class prior, seeded from the 28 mined seat fixes, updated per ledger row (guard 0.44 → 0.08 after 22
  guard build-fails). D8 built: transplant units (byte spans, rename via map entries aligned ≥ 2×, whole statements only, block-aware
  scope check: 2,526 of 2,855 dropped before any build), tools/doctor-transplant.py (dormant switch, build, gate, ledger).
  Result: **34 units built, 34 build-fail** (out of scope 15, not a statement / syntax 9, types 7, other 3), 10–20 s each.
  Cause (t7deffcb9): analogous code differs in STRUCTURE of values (grid `l.it0` field vs flex local `it0`) — token renaming cannot
  bridge it; ssFix/SimFix use static types for this. Research question for J's next step: type-aware / compiler-error-driven
  adaptation (rename a missing name to an in-scope name of the same type; field ↔ local), or move transplant up a level (port a
  whole statement group with its bindings).
- 10-06 D9 brief: `<notes>/FOUNDATION/DOCTOR-CODE-INDEX-OPTIONS-2026-10-06.md` — recommend B (doctor structural HV index across our
  apps, per-language lexers, per-app shards ~3–14 MB, vendored code refused as donor); A (text embeddings) only as a seat convenience.
- 10-06 J: "stage an exploratory research expedition on SovRaptor free lanes, 3 research lanes, then the 3 tiered 9 oracle panel".
  Cohort DRX staged (commander-cold-start + CODEX read; Law III worktrees): context `<notes>/DRX/CONTEXT.md`; research wave
  `<notes>/DRX/drx.wave.yaml` → DRX-INDEX / DRX-ADAPT / DRX-EVOLVE staged (contract `<notes>/DRX-contract.json` locked; outputs in weaver
  PRs 9/10/11); panel = oracle-route ×9 → DRXO-{TOP,STR,ROOT}-ORACLE-{REL,REIM,ADV} staged unpinned; board PLAN.md T25. BLOCKED on J:
  free lanes are disabled by J's 10-02 "Claude for everything" policy (fleet-lanes status) — enable + approve. After the dossiers:
  merge PRs 9–11, copy to <notes>/DRX/, lock DRXO-* cohort contracts (Law III), approve one cell at a time, then CONVERGE.
- 10-06 J: "yes, enable the free lanes and approve". fleet-lanes enable opencode / openrouter / openrouter-free / zen-free (cap 2,
  until 2026-10-09, reason J 10-06). Note: opencode/* free models count under provider zen-free (guard blocked until it was enabled).
  DRX-INDEX + DRX-ADAPT dispatched; DRX-EVOLVE approved, waiting for a zen-free slot (cap 2).
- 10-06 J: "ensure we are running the full 6 lanes". Live free lanes (lane-catalog lanes.status=live, cost 0): opencode big-pickle /
  space-bunny-free / big-pickle-free, zen-free nemotron-3-ultra / 3.5-lightning (guard counts these under the OPENCODE cap), openrouter
  nemotron-550B / laguna-s-2.1 / dots-3-note; ALL openrouter-alt free lanes dead → 4 free slots + claude-desktop-cli ×2 (J's enabled
  lane) = 6. Added cohort DRXB (independent second lane per question, weaver PRs 12–14, contract locked). The router fell back to a
  PAID lane twice (openrouter/qwen/qwen3.7-flash, cost 1) when a pin was not a live lane — the seat killed both runs and re-pinned
  (DRX-EVOLVE → nemotron-550B free, DRXB-INDEX → laguna-s-2.1 free). Running: DRX-INDEX, DRX-ADAPT (opencode), DRX-EVOLVE, DRXB-INDEX
  (openrouter free), DRXB-ADAPT, DRXB-EVOLVE (claude-desktop-cli). Panel briefs regenerated to read all six dossiers.
  Gotcha for the router (worth a fix task): a pin that is a catalog model but not a live lane is cleared silently and the fallback may be PAID.
- 10-06 D9 BUILT (28ff82a): cross-app code index, 17 apps / 573 files; fn+stmt 52,922 sections = 35.0 MB, 13.2 s full, 1.4 s
  incremental (all kinds 117.5 MB / 15.2 s). Cross-app probe found omni-ui's own layout.rs table() as the donor (err 0.34). Handoff §6.
- 10-06 DRX lanes: DRX-EVOLVE + DRXB-EVOLVE PASS (100 / 104 lines); DRX-INDEX + DRX-ADAPT stalled 30 min on opencode (watchdog) →
  re-run on claude-desktop-cli (dispatched 02:58); DRXB-INDEX: laguna rate-limited ×2 then router fell back to PAID qwen again (quota
  error, no output); DRXB-ADAPT (claude) thin 52 lines, no sections → needs_review. Free lanes underdelivered this sprint.
- 10-06 J: "first find published standards/specsheets … have an agent build a quick codebase from … then a cleanroom pipeline for
  when the doctor runs into a problem it can't solve". Catalog `<notes>/FOUNDATION/SPEC-LIBRARY-CATALOG-2026-10-06.md` (23 standards,
  all URLs fetched 200; evidence: ~65 % of 493 origin mismatches are text-bearing; most-used crates). New repo `projects/omni-spec`
  (3a1f2e8, no deps). Wave `<notes>/SPEC0/spec0.wave.yaml` STAGED (contract locked): SPEC0-UAX14, -UAX29, -OTSHAPE, -INFLATE on
  claude-desktop-cli, each verified by its official conformance data (`cargo test --test <module>`). Awaiting J's approve. Next after:
  wire modules behind doctor patch switches + gate (UAX14 → inline line breaking; OTSHAPE → text widths), D9 re-index, then design the
  clean-room pipeline (catalog §4).
- 10-06 J: router intelligence broken (a Claude session's dispatcherd split, a week ago) → ONE Claude session builds the library
  sequentially. SPEC0-* retired; SPECLIB (`<notes>/SPEC0/speclib.wave.yaml`, 13 modules in order uax14 → otshape → uax29 → inflate → png
  → brotli → sfnt/WOFF2 → json → gif → jpeg → webp → uax9 → html; ledger `projects/omni-spec/docs/STATUS.md`) approved + dispatched on
  claude-desktop-cli. DRX dossiers: 4 pass (INDEX, ADAPT re-run on Claude; EVOLVE; DRXB-EVOLVE), DRXB-ADAPT thin, DRXB-INDEX missing;
  canonical copies + MANIFEST in `<notes>/DRX/` (weaver PRs 9–14 left OPEN for J). DRXO cohort contract written + locked; panel runs ONE
  cell at a time on the second Claude slot via `<notes>/DRX/panel-sequencer.sh` (log `<notes>/DRX/panel-sequencer.log`, resumable).
- 10-06 J: "add another claude agent specifically for the posix library … yes prep". SPECPOSIX (`<notes>/SPEC0/specposix.wave.yaml`,
  own crate `projects/omni-spec/posix` = omni-posix: regex BRE/ERE → the 20 posix.json tools → sh tokenizer; posix-diff harness =
  <plan>'s T3 swap-in gate) dispatched on claude-desktop-cli. dispatch-guard override claude-desktop-cli (3,3) + fleet-lanes cap 3
  (ai-stack 04989816a) → 3 Claude agents: SPECLIB, SPECPOSIX, DRX panel. Release prep in omni-spec (f4e4ade): Apache-2.0 LICENSE,
  NOTICE (Unicode License v3), LICENSING.md release gates. Memory: release-and-licensing updated.
- 10-06 04:00 Rate limit on the Claude lane: dispatcherd re-routed SPECPOSIX + 5 DRXO cells to free opencode lanes → all died
  ("Session" errors). J: "bump the sessions that were almost done" via Talon :4100. Continued (POST /api/sessions/<id>/messages):
  SPECLIB (134k tok, 3 modules done → resume at inflate), SPECPOSIX (50k), DRXO-STR-ORACLE-REL (48k). Zero-token cells (STR-REIM,
  STR-ADV, ROOT×3) re-run one at a time on Claude by `<notes>/DRX/panel-rerun.sh` after STR-REL settles. Spawned task: Talon MCP tool.
- 10-06 incr/r3 (TERNARY-STACK seat handoff) MERGED to omni-render main 12d50f0 after gates: incr corpus 6 = 282 edits, 0 mismatches;
  doctor baseline 15,343 / 2,898 unchanged; compiled 0 different; binary gate 0 lost. Main does NOT build from a clean checkout
  (main.rs `mod jsi_date;`, src/jsi_date.rs untracked — JSI seat) — worktrees need a copy to build.
- 10-06 04:15 incr/r3 #2 (S4 click loops opt-in OMR_INCR + S4b sibling-sensitive style keys) GATED green on branch doctor/incr-merge2
  (df899cd: incr corpus 6 0 mismatches, baseline 15,343 / 2,898, compiled 0 different, binary 0 lost) but NOT merged: main's working
  tree holds the JSI-PERF seat's uncommitted src/svrt.rs (+ jsi.rs, jsi_lib.rs, untracked jsi_date.rs; last touched 10-05 23:50) and
  S4 changes svrt.rs. Waits for the JSI seat to commit; then 3-way merge + re-gate. Main = 12d50f0.
- 10-06 Panel: 4/9 reports; the 5 rate-limited cells are being finished in their own Talon sessions, one at a time on Claude
  (`<notes>/DRX/panel-talon-finish.sh`) — the router fell back to paid qwen again at 04:07 when they went through dispatch.
- 10-06 04:30 incr/r3 #2 LANDED on omni-render main be4b1fb (3-way onto 4c0ca77 after the JSI files were committed by the IR-JIT-NEXT
  seat — main now builds from a clean checkout). Gates: incr corpus 6 0 mismatches; launcher sv-run --click under OMR_INCR_CHECK=1 →
  2 frames 0 mismatches; baseline 15,343 / 2,898; compiled 0 different; binary 0 lost.
- 10-06 04:40 DRX panel 9/9 GO_WITH_REVISIONS → CONVERGE `<notes>/2026-10-06 — DRX Oracle CONVERGE (9-cell).md` (GO-GATED: keep D9
  35 MB/13 s/1.4 s; hygiene first; transplant v2 = lift + rustc type probes; D2c bisection; standards ports; two growth counters; patent
  US10133657 flagged). Step 1 DONE: foreign-header refusal + snapshot skip + real paths + --no-forks; clean index 31.0 MB / 46,907
  sections / 12.6 s, 0 foreign headers. Honest probe: no non-fork cross-app donor for table() (best err 0.53–0.65) — the adversarial
  swing holds for the renderer: donors = same app + omni-spec. Handoff §6 corrected.
- 10-06 J: patent US10133657B2 read (claims 1–16) → design-around rules recorded (CONVERGE card, memory, omni-spec LICENSING gate 6b):
  bind by type + value on runs, never name-text / per-position similarity; LCS on abstracted structure only; no call-argument
  replacement mode. J "as recommended": two counters · transplant v2 kill 0/~50 · launcher after step 3.
- 10-06 04:55 incr/r3 #3 (fastparse) MERGED main d6ff48d: incr corpus 6 mismatches 0 (re-verified on merged main — the first gate's
  output was cut before the count; merged only after-the-fact confirmation, noted as a slip); baseline 15,343 / 2,898; compiled 0 diff;
  binary 0 lost; launcher click loop 0; fastparse on our sv-run output 2/2 accepted 0 mismatches (2.8×), corpus 50/50 fall back 0.
- 10-06 J (readback confirmed): bind by SYMBOLIC EQUATIONS, not variables/parameters — code sections → SSA equations (each value a
  symbol defined by one equation; loops → per-element equations over an index symbol); match up to algebra (canonical form / equality
  saturation, clean-room from egg, Willsey et al. 2021); bind symbols by unification + value equality on corpus runs (engine term keys =
  shared symbol vocabulary); emit the unified equation back as code behind a dormant switch; gate decides. Replaces name rebinding in
  step 3 (transplant v2); removes name-text ranking (patent design-around) and yields name-free J-format rewrite rows for the models.
  First probe: table extra-space distribution ↔ grid grow-to-limit unify with a consistent binding (kill: analogous sections do not unify).
- 10-06 step 2 DONE (639022a): fire refresh — 0 solved (knob space exhausted on the current engine), 63 open cards (top: h-|Block|Block 25,
  h+|Block|Flex 24, h+|Block|Block 20, w+|TableCell|TableRow|txt 20); HARMONY: 5 dead clauses (replaced by real features → AGM prune
  candidate). Growth ledger `results/doctor.growth.jsonl`: doctor-authored 318 (repair-core clauses) · seat-ported 532 = 850.
- 10-06 EQUATION PROBE PASSED (tools/doctor-equations.py): table min→max (L1878) ≡ grid grow-to-limit (L2485) as one SSA equation,
  out_k = base_k + share·(cap_k − base_k)/Σ(cap − base), bound by ROLE (mn↔w, mx↔limit, extra↔give), no names; table auto-columns =
  same family (weight = base). Next (step 3): generalise the parser over doctor sections (Rust subset → SSA), role unification + value
  fingerprints from a corpus run, emit back as code behind a dormant switch, gate. Then the same on the D8 34-unit ledger.
## Step 3 — transplant v2 with symbolic-equation binding (J 10-06 "continue into step 3")
| # | Step | Class | Verify |
|---|---|---|---|
| 3a | `Layout`-free guard `crate::layout::patch_on("patch.e<id>")` (program clause `key[*]=-1` = on) — usable in free fns and hosts without `n` | CLOSE | build + `core corpus --max 0` baseline 15,343 / 2,898 unchanged |
| 3b | `tools/doctor-eqtransplant.py`: candidate pairs from `core --donors --out` with collage err < 0.45 (CONVERGE: refuse junk); statements → SSA equations (Rust subset parser → sympy; loops over k → indexed equations; unsupported = opaque) | BUILD | probe pair (table min→max ↔ grid grow-to-limit) parses to the same canonical equation |
| 3c | Role unification: match donor ↔ range equations by canonical shape (symbols as placeholders), derive ONE consistent symbol binding; donor equations with no partner = MISSING; a missing equation is a unit only if every input symbol is bound by structure (value fingerprints = later) | BUILD | units list with binding table; 0 names used in binding (assert) |
| 3d | Emit unit as code: assignment to an existing range symbol (`y = …`, `y += …`, `v[k] = …` with its loop) behind `if crate::layout::patch_on("patch.e<id>") { … }`, spliced at a statement boundary by byte offset; `cargo check` first | BUILD | ledger rows `compiled` true/false with first rustc error |
| 3e | Gate compiled units: `core corpus --patch-gate --clause patch.e<id>[*]=-1`; ledger outcome; growth ledger row `doctor-authored` on pass | CLOSE | ledger `results/doctor.transplants.jsonl` rows with method `eq`; kill: 0 of ~50 compile → stop the transplant line (J) |
- 10-06 step 3 first measurement (omni-render commit after 49acb07): 3a patch_on guard DONE (baseline unchanged); eq transplant over
  ALL of layout.rs: 3,958 pairs → 998 / 787 equations → 12 structural matches (trivial duplicates knob_at ↔ knob_fast) → 6 missing →
  0 units bindable by structure. Why: (1) most layout code is imperative control flow, not equations (opaque: let-with-calls, if, for,
  method chains); (2) my Python statement splitter still mis-aligns spans; (3) inputs of missing equations need VALUE fingerprints
  (designed, not built). The equation form PROVES analogies (probe) but does not yet GENERATE transplants. Kill criterion (0 of ~50
  compile) not reached — there are 0 candidates. Recommendation to J: run step 5 (wire SPECLIB uax14 + otshape, 65 % text share) next;
  keep eq-transplant as a research track: use the doctor's Rust sectioner for statements (not a second parser), add value fingerprints.
- 10-06 ~05:45 HANDOFF (J: "set a brief for next agent … document all work, save all harnesses and tests, update plans/projects"):
  handoff rewritten `<notes>/worker/claude/DOCTOR-HANDOFF.brief.md`; omni-render MANUAL § DOCTOR core rewritten; omni-spec MANUAL new;
  DEVLOG <devlog-entry> + <devlog-entry>; Part 6 §4 appended; harnesses/results committed (omni-render 036d7b0, 49acb07, 03f6acb);
  ratified DRX-*, DRXO-* ×9, SPECLIB (cargo test gate); DRXB-INDEX retired (no output); next to-dos staged as DOCNEXT ×8 (PLAN.md T26,
  contract `<notes>/DOCNEXT-contract.json`). SPECPOSIX still running in Talon tln_48b1a0ea0e1c45be8f8d.
- 10-06 DOCNEXT-S5-WIRE DONE (J "continue from the brief"): omni-spec uax14 + otshape wired (patch.linebreak / patch.kern, per-element
  guards) + CSS Grid §12.6 equal maximize (patch.grid_equal_grow, the enabler: PEP `fit-content(30%) auto` lost boxes under breaking).
  Evidence-led tailoring via the new OMR_GATE_SHOW display: no break after '/' (arch `/dev/swap_partition`); kerning only on the requested
  face and never on variable fonts (Inter / Mona Sans: Chrome shapes the opsz instance). D2c conditions: kern[Inline&tag!=a] +26,
  kern[Block&ws=0] +8, linebreak[Inline&pt=0] +21 → binary gate +55, 0 lost → main 537a39c / 538827f: **18,296 / 28,010**. Open: 7
  kern + 1 linebreak boxes uncovered (MDN "Tools" in Inter static?; arch `<code>` shift; MDN section compensating error); font variations
  (fvar/gvar/HVAR) = next omni-spec module candidate. Next: CODE-ABC (J 10-06 "go ahead with code abc after s5") — `<plan>`.
- 10-06 EVENING — PATIENT + CHROME ORACLE + REBUILD LOOP (J: "run it on the actual thing"; "use the blackbox itself, find the equation …
  rebuild it"; "compare the bug lib to our browser, then query chrome"; "you haven't implemented the code abc"). Patient run, Chrome black-box KB,
  both engines as oracles (CHROME vs OURS laws diffed by CODE-ABC), tools/emit_laws.py → src/oracle_laws.rs (doctor-written code). Fixes:
  +45 +22 +328 +311 +6 → **19,008 / 28,010**, 0 lost; textarea + input our law == Chrome law 120/120. Handoff: DOCTOR-HANDOFF.brief.md.

# DOCTOR-COMPOUND — stop test-after-test; rank by blast radius, reduce automatically, fix causes (2026-10-06, Claude seat)
> **Lineage — the doctor core now has its home (2026-10-07):** `projects/doctor-core/README.md` · manual `docs/systems/doctor-core/MANUAL.md`.
Lineage: `DOCTOR-HANDOFF.brief.md` (19,008 / 28,010; +767 in ~6 h), `<plan>`, `<plan>`, explainer
`<notes>/FOUNDATION/DOCTOR-CODE-ABC-EXPLAINER-2026-10-06.md`. J 10-06: "we cannot keep doing blind test after test … synthesize a new method".

## GROUND (measured this session, omni-render 9af1171, binary target-doctor)
- `omni-render mismatches corpus` = 3.7 s full corpus: 9,002 failing of 28,010; only 414 "origins" (wrong while parent agrees on ALL axes).
- Concentration: theguardian 3,102 (34 %), nytimes 1,023, MDN display 810, wiktionary 607, wikipedia 500 → top 5 pages = 67 %.
- theguardian: 3,102 failing boxes, **0 origins** → invisible to `--abc patient`, patch-search cards, repair core (all origin-driven).
  6 pages have the `html` box wrong: 3,867 failing boxes there, only 74 origins.
- Why: height errors flow UP (child too tall → every ancestor to the root wrong), and the origin rule demands a fully agreeing parent,
  so every other bug under that chain is hidden. Families are ranked by origin COUNT (patient prints n = 24 …), not by boxes recoverable.
- First candidate found by reading one dark page (theguardian section `.dcr-cavc6m`): `grid-column: decoration` / `content` with lines
  named `[decoration-start] … [decoration-end]`. CSS Grid §8.3 (implicit named areas from `<ident>-start`/`-end` lines): a bare ident
  resolves to `ident-start` on the start side, `ident-end` on the end side. `src/layout.rs:2416 parse_place.line` looks up `named.get(p)`
  for the bare name only → miss → auto placement, span 1 (ours w 110 vs Chrome 1140; 60 vs 140; 80 vs 960). Unverified until gated.

## ANALYZE — the tunnel
Every tool after the census is good (oracle, builder, emit_laws, gates). The census is the bottleneck: it picks WHAT to work on by a rule
that hides most of the error mass, then each pick is hand-traced (hours). Test-after-test = no ranking by value + no automatic reduction.

## TROUBLESHOOT (risks)
1. Blame rule wrong for a layout mode (flex/grid widths can flow UP from content; shrink-to-fit) → cross-check against the counterfactual.
2. Reduction runs too slowly with a fresh Chrome per probe → one persistent Playwright browser, `page.set_content` per probe.
3. Reduced case loses the bug (CSS from the cascade not carried) → inline computed-winning declarations (explain provenance) before cutting.

## IMAGINE — the method (synthesis of parts already built)
| Stage | Field name | What it does | Class |
|---|---|---|---|
| B1 BLAME | dependency-aware fault localisation | per axis: w/x flow from the parent's content box, h from the children, y from the previous sibling. A box is a CULPRIT on axis k when its axis-k inputs agree with Chrome and its output does not. Blast radius = failing boxes whose error traces back to it | CLOSE (diff map + DOM in `score_full`) |
| B2 ROI | counterfactual / oracle injection | force the culprit to Chrome's geometry, relayout, count boxes gained = upper bound before any fix | BUILD (later; only if B1 ranking misleads) |
| B3 REDUCE | delta debugging (Zeller & Hildebrandt 2002, ddmin), clean-room | culprit subtree + ancestor chain, winning declarations inlined; ddmin over elements then declarations while ours ≠ Chrome on that axis → a 3–10-element case in `blackbox/reduced/` | BUILD on `chrome_blackbox.py` + `mismatches` |
| B4 CLUSTER | — | group reduced cases by their surviving declaration set = the real cause families | CLOSE |
| B5 LAW | existing loop | surviving numbers → symbols (this IS open item 5a `spec_probe`) → `oracle_synth` → builder → `emit_laws` or seat patch → gate the set | CLOSE |
Compounding: blame re-runs in 4 s after every merge (unmasks the next layer); every reduced case stays as a regression test;
every law stays in `oracle_laws.rs`; reduced cases + fixes = J-format `code.debug` traces later (J decides).

## PLAN (each step verified; gate = 0 lost)
- [ ] 1 PROVE ON THE BIGGEST: implicit named areas §8.3 in `parse_place` behind dormant `patch.grid_named_area` → `cargo build`;
      `--binary-gate` / `--patch-gate` → PASS = gained > 0, lost 0; expected: a large share of theguardian's 3,102.
- [ ] 2 B1 `core corpus --abc blame [--out F]`: culprits per axis + blast radius, ranked → verify: theguardian shows culprits
      (> 0) and the sum of blast radii covers ≥ 80 % of 9,002 failing boxes.
- [ ] 3 B3 `tools/reduce_case.py <page> <node> <axis>`: persistent Chrome, ddmin → verify: the step-1 bug (pre-fix binary) reduces to
      ≤ 10 elements and still disagrees; time per case logged.
- [ ] 4 Batch B3 over the top 20 culprits by blast radius under `bin/tw`; B4 cluster → verify: `blackbox/reduced/index.jsonl` rows,
      clusters with summed boxes at stake.
- [ ] 5 B5 per cluster, largest first: oracle law or spec patch → gate the set → growth ledger row; re-run B1 after each merge.
- [ ] 6 Records: MANUAL § DOCTOR (blame + reduce), DEVLOG, handoff brief §2 method replaced, memory rule.
Kill: if step 2 blame radii cover < 50 % of failing boxes, the per-axis flow rule is wrong → build B2 counterfactual instead.

## Checkpoint contract
Resume at the first unchecked step. State: census 9,002 / 414 origins; theguardian dark (0 origins); candidate §8.3 at layout.rs:2416.

## STATUS LOG
- 10-06 GROUND done (this file). Awaiting J's go on the method before Act.
- 10-06 J: "measure the angles and see where it differs from the shape it's supposed to have — square in the square hole" (readback
  confirmed); "add aliasing / feathering, make the outline thicker". BUILT SHAPE station `core corpus --abc shape [--all --alias DEG
  --outline T --feather F --out F]` (omni-render-doctor 26dec4a, src/doctor_shape.rs): ∠W ∠X ∠Y ∠H per box ours vs Chrome, derived H
  dropped, snap + feathered outline + front-to-back alpha charging. 49 pages, 2.5–3.2 s: hairline 5,781 causes / 100 % coverage →
  alias 0.25° outline 2 feather 1: 3,699 / 99.5 % → alias 1° outline 4: 3,185 / 98.7 %. Top: nytimes article._feed-item W +34° (582),
  nytimes video W (262), wiktionary etytree Y (110+104+54), theguardian grid item dcr-7eafox W −37° (78, the §8.3 candidate).
  Equations are pure fns lowered by CODE-ABC (`--abc dump --src src/doctor_shape.rs`); atan2 is opaque → exact angles fix that.
  Results: results/doctor-runs/2026-10-06/shape/. NEXT (pending J readback): exact angles (cross-multiplication in 1/64 px ints).
- 10-06 J PIPELINE (supersedes B1–B5 above): 1 patient census → 2 measure angles → 3 alias/feather → 4 compare to oracle → 5 apply fix →
  6 reverse IFS the faulty shape, replace with the correct shape. FIRST RUN: theguardian grid item ∠W −37° → Chrome oracle
  blackbox/oracle-grid-named (bare `grid-column: decoration|content|title|hide` 0 px wide in ours; `-start/-end` form already right) →
  CSS Grid §8.3 implicit named areas `patch.grid_named_area` → patch-gate +1,609 / 0 lost (replay 16,011 → 17,620, holdout 2,997) →
  reverse IFS: D1 donors find no other faulty lookup in layout.rs; shape census after: the family is gone. Corpus 9,002 → 7,393 failing
  (agree 20,617 / 28,010). omni-render main 52413fa (ff). Next shapes: nytimes article._feed-item ∠W +34° (582), nytimes
  _container ∠Y (262), wiktionary etytree ∠Y (128+110+54), theguardian dcr-18agdrd ∠Y in grid (116+62+42), lwn ArticleText ∠X (77).
- 10-06 J DIRECTION (exact angles): Chrome displaces shapes with text / formatting (not bugs, but cost); structure our engine's
  geometry exact (integer 1/64 px, angles as cross-products, no float trig) regardless of formatting or text → faster, less RAM.
  Readback pending; J decides scope (engine-wide refactor vs the shape station first).
- 10-06 REVERSE IFS v1–v3 (tools/shape_ifs.py, 05adae9): parts-partition v2 from ONE theguardian grid item → 148/152 repaired grid
  items, 1,031/1,411 repaired boxes at 0.706 precision (flat family 0.006); floods on 2-part shapes; v3 frame gate + sign oracle →
  precise but 2/152. J: 3-tier triage = (a) sieve (b) shape match (c) 3-point TRIANGULATION (larger triangle, ◢ ▲ ◣ turns,
  superimpose, fuzzy fit) → then oracle → fix → reverse IFS. TRIANGULATION v1 (tools/shape_tri.py): ▲ at θ 0 splits failing boxes
  FIT 3,573 / DEFECT 3,807 (τ 4 px); truth 1,411/1,411 + 152/152 DEFECT, 0 FIT. Rigid turns (centroid spin / base lean, δ 1–6°)
  absorb ≤ 16 boxes: DISPLACED tier empty. Misfit corners: bottom-only 1,920 (height: text/format), all four 1,107, right side 232.
- 10-06 TRIANGULATION v2 (J: "◺ △ ⊿ and ◸ △ ◹, slight angle variations at each corner"): five triangles anchored on the frame
  rect, each exact + pivoted ±3° at each of its corners. FIT 4,845 / DEFECT 2,533 of 7,387 failing (τ 4); corner variations rescue
  ≤ 10. All five triangles always agree: any 3 points of one rectangle fix the same affine map → the triangles must anchor on
  DIFFERENT reference boxes to disagree. Full-frame anchoring leaks height-up propagation (28/1,411 truth → FIT; ▲ width-anchored had 0).
  FORMAT-FIT probe (J's 2nd experiment): only 8 failing text boxes are off in height alone (x, y, w right, Δh < 25 %); 409 bottom-only
  misfits = 309 containers (height from children) + 94 text; per-line Δ per (font, size) not consistent (sd 2–29 px) → no single
  line-height law; formatting-only drift is small on this corpus. Log: results/doctor-runs/2026-10-06/shape-ifs/format-fit-probe.log.
- 10-06 TRIANGULATION v3 (J "try this": re-anchor on separate references; omni-render-doctor 5c45121): △ width only · ◸ previous
  sibling · ◹ next sibling · ◺ Chrome's target bottom (the hole) · ⊿ the frame's own bottom. The triangles now DISAGREE: of 7,387
  failing — FIT 2,764 · DEFECT 2,178 · SPLIT 2,445 (fits only from below 917 · fits from above, carried 515 · previous-not-next 207 ·
  next-not-previous 199 · other 607). Truth: 0 of 1,411 repaired boxes → FIT (leak closed, was 28); 151/152 grid items DEFECT.
  Next: reverse IFS on the 2,178 DEFECT (range = misfit corners + split signature), then oracle → fix → gate.
- 10-06 EXPERIMENT 2, error-vector guided annealing (J translate.txt; `core corpus --abc anneal`, omni-render-doctor 1a159bd): per box the
  triangles' signed fracture [x y w h] picks the knobs (W → letter-spacing; H → line-height / font-size / padding-bottom), each knob is
  STRESSED ±h (linear answer = it controls the crack), then SEALED by Newton steps. 2,178 DEFECT (6m40s): 1,363 no knob controls the
  crack (structural) · 686 crack proven, size axis sealed (647 to ≤ 1 px), shape still off on position · 53 sealed fully · 76
  position-only. Consistent cracks = formatting laws to find: MDN 288 boxes H ← font-size 16 → 17.79 (one shared cause, the line box
  height); arstechnica 36 W ← letter-spacing +0.87 at 12 px; allrecipes p 16 px line-height 22.39 → ~23.0 (+0.61, 4/4). Work (layout
  terms) unchanged by formatting (487,039 → 487,509); agreeing boxes on those pages 17,987 → 18,423 with the sealed formatting.
- 10-06 J Translate 2 (SIMD / SoA layout): measured: 89 % of 28,010 boxes sit in wavefront batches ≥ 8 (same page, depth, display,
  frame display), 45 % in batches ≥ 64. Field kin: Meyerovich & Bodík 2010 (parallel layout as attribute-grammar tree traversals,
  SIMD/GPU), Servo parallel layout. Proposed probe LAYOUT-SOA-0 (J decides).
- 10-06 THE BROWSER AS SIMD v0 (J: "run the browser as simd"; omni-render-doctor `core corpus --abc simd`): every box a row in flat
  arrays, 33 depth waves (gather parent content width → branch-free exact-integer block-width kernel → scatter as the next wave's
  containing block). 12,249 of 31,623 boxes (39 %) run in the batch; 94.5 % bit-exact vs the recursive engine (12 off by 1/64 px,
  664 larger — program knobs / boundary content widths to classify); kernel 0.117 ms for all 12,249 widths (9.6 ns/box) vs the
  engine's whole layout 434 ms for 31,623 boxes. Next: classify the 676 misses, add the height wave (bottom-up sums) and the next
  rule batches (flex rows, grid tracks), then run a page end-to-end from the arrays.
- 10-06 EXACT GEOMETRY (J: "format our browser to be exact", Translate 3 trits; omni-render-doctor 7b568c0): the SIMD wave in a mixed-radix exact unit
  1/(2^6·3^4·5^4) = 1/3,240,000 px, i64 lanes: 0.117 ms (1/64 px wave 0.106 ms). Divisions off the grid 52 → 0. Per-box trit
  sign(1/64 px − exact): −1 48 · 0 12,189 · +1 12; block widths drift only 0.39 px in total (max 0.0125). The 664 larger misses vs the
  engine are not precision (knobs / boundary widths). Exactness pays where space is SPLIT: next batches flex / grid fr tracks and text
  advances; then the engine's unit behind a patch switch + gate.
- 10-06 STEP 1 DONE (omni-render-doctor 08270eb): the exact SIMD wave's 571 peps disagreements = CSS 2.2 §8.4 — percent padding
  resolved against the box's own width (float main 74 %, padding 3.2 % → 27.65 px) instead of the containing block (1,168 px →
  37.375 px, Chrome). patch.pad_pct_cb (block() + place_float() pass the containing block; memo bypassed when it differs): gate
  +18 / 0 lost (the rest were inside tolerance, now exact); wave vs engine 94.5 % → 99.1 % bit-exact; corpus 7,393 → 7,375 failing.
  KB mining (2 of 3 agents back): soft-RRNS triangulation (L7, RING-10: 0.969 vs hard 0.674), alias grid K=240 on the SHARE not the
  angle (L8), Hopf base/fibre shape key (L14), L17 margin gate, unquantised seed for peel (PEEL-2b/2c), learned SIEVE→PART→PEEL
  ladder (CORE-ROUTE-2) as the firing core, residue fingerprint of exact errors, check ring 17 on child sums. Refuted: paraxial,
  Chernoff-grows-with-B, int div/mod semantics in Rust (use div_euclid). J queued: render the T15 (ARC tiers) in the trit browser.
- 10-06 KB-MINING #1 SOFT-RRNS TRIANGULATION (omni-render-doctor ebbaffe, tools/shape_rrns.py): five views → max-likelihood source
  over 8 syndromes + margin gate. Now: commits 89 % of 2,445 SPLIT, 83 % of 2,160 DEFECT. VERIFIED vs Chrome: frame-height sources
  87–90 % have the frame height off (all failing 32 %); "box itself" 2,403 → 81 % own size off (54 %); "carried" 3,447 → 74 % own size
  right (46 %). Sibling-gap syndromes do not verify (n 40/75) — next: sibling anchors carry x too; split ◸/◹ into x and y views.
- 10-06 KB-MINING #2 REVERSE IFS, exact cause-ordered key (ced700f, tools/shape_key.py): domain = "box itself"; key = frame display
  + trit of the FIRST cracked axis in dataflow order (w → x → h → gap) — downstream axes are consequences. From ANY of 3 different
  grid-bug instances: 133/152 repaired grid items, 365 repeats (precision 0.36 on grid truth; 90 of the 365 agree outright after the
  fix). Own-display or all-trit keys fail (0.007–0.49): the same bug lands with different heights. Next: Omnitri stage 2 inside the
  bucket to lift precision; run KC on today's top "box itself" defects to list the families by size.
- 10-06 (remote session) ROUND 2 (tools/doctor_round.sh): +124 patch.track_math (grid min() track with %, codinghorror; 64a8087)
  → 20,759 / 28,010. MDN family (Flex, w, −1): two true causes found, both DORMANT (f9dd696): `:root{scrollbar-gutter:stable}` → Chrome
  root 1,265 px (patch.sb_gutter) and @font-face `size-adjust: 95 %` on JetBrains Mono (measured width ratio 1.0527, sd 0.0001 over
  206 boxes; patch.size_adjust). The set gates +13 / −8: once width is exact, Inter text (variable font, ~1 % wide) re-wraps — the
  compensating error is variable-font advances at the used opsz (fvar/HVAR, omni-spec candidate). Gate the three together.
- 10-06 (remote) MERGED omni-render main f2a0459 (ff from doctor/abc): CSS Cascade 4 §7.3 `unset` = initial for non-inherited
  properties (it took the parent's value) + CSS-wide keyword arms (flex-basis/grow/shrink/direction/wrap, order, align/justify,
  insets) — family (Flex, h, +1) → theguardian card media `flex-basis: unset` → binary gate +1,284 / 0 lost → **22,043 / 28,010**
  (morning 19,008: +3,035 today). Dormant, waiting on their compensating errors: patch.sb_gutter + patch.size_adjust (Inter variable
  font ~1 % wide), patch.font_shorthand (+25 / −2: Font Awesome inline-block baseline at line-height 1; weather.gov li wrap).
- 10-06 (remote) MERGED main 311a339: -webkit-box vertical + -webkit-line-clamp (patch.line_clamp) +56 / 0 lost → **22,099 / 28,010**.
  PROCESS SLIP (recorded in the growth ledger): the family came from ebay, a HOLDOUT page — doctor_round.sh ran `shape --all`; now
  replay-only. The fix is a spec feature (also +12 on replay allrecipes), but ebay's +44 is no longer an independent canary result.
- 10-06 (remote) MERGED main 2b0e3fe: column-flex definite flex-basis (patch.flex_col_basis +63) · CSS 2.2 §17.2.1 anonymous cell
  for a row of non-cell content (patch.anon_cell +111, oracle blackbox/oracle-tlines) · non-<table> tables take the CSS
  border-spacing, not UA 2 px (patch.nontable_spacing[Table&bt=0&tag=span] +242; general rule −2 to a wikipedia portalbox
  row-height compensating error) → **22,515 / 28,010** (+3,507 today).
- 10-06 (remote) MERGED main e458c24: media range queries with calc() + strict < > (+75, MDN breakpoints) → **22,590 / 28,010**
  (+3,582 today). DORMANT MDN SET (all correct by Chrome oracles; the set gates +16 / −8 on MDN): sb_gutter, size_adjust, var_font
  (fvar/HVAR weight instances + opsz = used size: Inter 1.0087 → 1.0002, JetBrains Mono 1.0527 → 1.0012), pseudo_vars (custom
  props on ::before). Remaining MDN compensating error: the sidebar header — custom element `mdn-button` lays out 163.8 px wide vs
  Chrome 33.5 px (abs-positioned over the filter input), so the input row wraps (+39 px) and shifts the whole sidebar list.
  Next MDN step: the mdn-button / filter header; then enable the 4 dormant switches together.
- 10-06 PREDICT FROM KNOWN-GOOD POINTS (J; tools/shape_predict.py, pre-registered bar): FAIL. Eligible = failing boxes in a good
  frame with ≥ 3 good peers: 368 of 4,298 (3,825 sit in failing frames — only 473 roots). Predicted within tolerance 3/368 (bar
  50 %); median corner hypotenuse 215 px predicted vs 32 px ours. Where ours is wrong on an axis, the peer prediction is right on
  x 3 % · y 4 % · w 2 % · h 15 %. Reading: a failing box differs from its good peers BECAUSE its conditions differ (the CSS the
  peers lack) — the good peers' shape is not the failing box's shape. The measurement that holds: errors cascade from 473 roots.
- 10-06 BOX TREE ↔ CODE AST (J, readback confirmed; tools/shape_ast.py): path.* branch markers in the term ledger give every box
  its code path (block_box / flow / flex / flex_column / grid / table / float / inline / shrink_to_fit / intrinsic_w + 29 terms).
  Pre-registered test (6 fixes switched off, Ochiai per error leg): the later fix's code branch in the top 5 for 0/5 (best ranks
  12–49) → FAIL at branch granularity; 517 roots span many bugs and ubiquitous branches dominate. Signal that holds: horizontal-leg
  roots concentrate in intrinsic sizing (shrink_to_fit, intrinsic_w, Block>InlineBlock) — text measurement, matching the font finds.
  To make it work: statement-level coverage (CODE-ABC spans) + rank WITHIN a geometric family, not globally.
- 10-06 STATEMENT-LEVEL AST TEST (tools/shape_ast_family.py; 163 cov(line!()) markers, CurNode stack): fix line in the family
  top 3 for 1/4 → FAIL (bar ≥ 3). HIT: flex_col_basis rank 3 (tied with path.flex_column at the top). MISSES are coverage gaps:
  anon_cell / line_clamp / track_math fixes sit in one-line match arms or style.rs (no marker), so their line cannot rank. Next if
  pursued: markers in arms with string guards + style.rs + parse_track, and families restricted to roots (cppreference family of
  353 includes its cascade).
- 10-06 EULER / LINE-COUNT SPLIT (J triangle torus; `core corpus --abc lines`): pre-registered PASS 532/585 = 90.9 % (bar 80 %),
  BUT the instrument fails its own check: on 16,231 agreeing boxes with Chrome text only 80 % line counts match and 1,762 find
  none of our runs inside the box (no constant offset → geometric containment picks up overlapping content). Verdict: result
  NOT trusted; count lines by DOM ownership (needs Item::Text node ids: Frag runs are per style, not per node) before using it.
- 10-06 SHADOW DOM (dormant patch.shadow_styles v2): scoped shadow stylesheets (<style> + <link> inside declarative shadow roots),
  :host rewrite, encapsulation. nytimes feed root (1,023 boxes) now resolves `display:flex` (its CSS is a <link> inside the
  shadow root) but the feed items size wrong next (w +536: overflow-x scroll + gap via custom props); MDN +707 / −658. Next layer:
  the feed item sizing on nytimes; MDN components (mdn-* hosts) under encapsulation.
- 10-06 nytimes feed, next layer found: feed items use `width: var(--item-width)` = calc((min(100cqw, …) − gaps) / n) —
  CONTAINER QUERY UNITS (cqw) are not supported (calc fails → auto width). Needs cq units resolved at layout time against the
  nearest `container-type: inline-size` ancestor (fallback: small viewport) — a feature, not a fix; queued.
- 10-06 T25 DOCTOR (box_t25.py, t25_ifs.py): every box = one T25 point (x0, y0, w, h, ry), 47,686/47,686 exact, errors decoded
  from ring angles 4,298/4,298 (1.6 s Python, whole corpus). Reverse IFS on absolute twists: 473 roots → 369 families (exact
  repeats only: MDN 38, bbc 11). TRIANGLES' PLACE (J): the triangle = the DIFFERENCE of torus points (box − frame, box − sibling)
  — translation invariance is free; carried 2,509 / own 1,786. As the sieve KEY (triangle twist trits + display pair): 473 roots →
  103 families; pre-fix validation: theguardian's 26 repaired roots fall in 3 families (17 in one) vs 23 with absolute keys.
  Next: oracle → fix the largest triangle families (MDN Block/Block x−1 53, arstechnica/MDN InlineBlock x+ w− 46, theguardian
  Grid/Flex h− 24, servo Flex/Block y− h+ 21).
- 10-06 FAMILY 1 FIXED (omni-render aaa9a30, main ff): MDN Block/Block x−8 (53 roots) → MDN `:is(.left-sidebar ol):not(:has(>li>details))>li`
  — `:has()` (Selectors 4 §4.5) was unparsed, so `:not(:has(…))` was always true (li padding 8 vs Chrome 16). Built `:has()`
  (relative chains, forward walk; breaks sibling style sharing + INCR memo, both disabled for :has rules). Turning it on exposed
  ebay rules gated by :has — needed CONTAINER UNITS (cq*, resolved at layout from a container-type stack, small-viewport
  fallback — also the queued nytimes feed blocker), the first implicit grid column from grid-auto-columns (§7.1), minmax(fixed,
  fixed) min-content = base (§12), definite Expr heights. GATE FIX: pseudo-elements live in the DOM arena, so a style change that
  adds/drops one shifts every later id — ebay read 32 lost / 32 gained for an unchanged page; binary gate now keys by stable ids
  (real-node index). Also `patch_on` read the switch before the lazy program load (first page of a process saw patches off).
  Oracles: has 8 cases x-exact, cq 0/32, gridmm 0/20. Gate +673 / 0 lost (MDN +599, nytimes +73, github +1) → 23,261 (stable ids;
  base 22,588 = 22,590 minus 2 pseudo boxes). Open from the oracles: closed <details> shows its body (h 36 vs 18); body/h3
  margin collapse (body y 0 vs 18.7); ebay subgrid (grid-template-rows: subgrid) — the carousel cards' height (592 vs 319).
- 10-06 QUEUE RUN (tools/t25_families.py = the fix queue; omni-render 2330185 → 8b51c17 → unicode_range → 928b743): 23,261 → 23,851.
  MDN Block>InlineBlock w+ (183, w ratio 1.0527) = dormant size_adjust, lands only as a set with sb_gutter + var_font (+200/0);
  MDN Flex>Block x−16 (102, sidebar chevron) = pseudo_vars, its losses were sidebar content +39 px from the unstyled
  mdn-sidebar-filter shadow → shadow_styles now passes alone; set +152/0. unicode_range re-gated +82/0 (arstechnica family).
  grid_span_fill: spec = span-count groups vs the same base sizes, equal shares, max per row (not water-fill) → docs.rs fixed;
  its theguardian "loss" was 2 footers agreeing only by the 5 %-of-y tolerance (161 px off) — real causes: `1fr 1fr` rows under
  indefinite height equalize (§12.7.1, grid_fr_rows) and column-flex auto margins (§8.1, flex_col_auto_margin) → +156/0,
  theguardian main height exact. Dormant: font_shorthand +25/−2 (both `line-height: normal` line-box details: docs.rs nav
  baseline 3 px; weather.gov li wraps). YARDSTICK NOTE: y tolerance max(2, 5 % of |y|) lets 100+ px y errors "agree" deep in a
  page — a gate can read a real fix as a loss; classify by rect before trusting a small loss count.
- 10-06 DIRECTION (J, readback confirmed): the goal is NOT Chrome parity — it is mathematically PRISTINE pages: every box exact
  geometry (exact units, exact angles, every triangle closing with frame + siblings, zero twist). Chrome stays an intent reference.
  The doctor's yardstick must move from "agrees with Chrome within 2 px / 5 %" to "geometrically exact by its own rules"; the T25
  core (projects/t25-render, WebGPU, arc reactor inside) is to live in the ternary browser as the system-wide processor/intelligence.

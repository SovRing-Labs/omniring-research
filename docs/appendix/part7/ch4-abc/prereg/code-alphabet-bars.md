# CODE-ABC — the doctor's code alphabet (J 10-06, readback confirmed "yes correct, go ahead with code abc after s5")
> **Lineage — the doctor core now has its home (2026-10-07):** `projects/doctor-core/README.md` · manual `docs/systems/doctor-core/MANUAL.md`.
Source: `<home>/Downloads/Code ABC.txt` (J's research thread) · lineage: `<plan>` § Step 3 (equation probe PASSED; eq-transplant v2
first run 3,958 pairs → 0 bindable units: syntactic matching cannot see `x*2` ≡ `x+x` ≡ `x<<1`) · CONVERGE `<notes>/2026-10-06 — DRX Oracle CONVERGE (9-cell).md`.

## Readback (confirmed)
Library stored as equations (name-free SSA). The core (1) recognises where the same equation is used elsewhere = equation-level pattern
matching / idiom recognition; (2) merges recurring equations into larger reusable ones per feature = library learning by anti-unification
(DreamCoder / Stitch); (3) writes new code by composing them = program synthesis over the learned library. Equations = alphabet, merged
groups = words, programs = sentences.

## Field (search first; learn from everything, copy nothing — papers only, our own code)
- E-graphs + equality saturation: Willsey et al., "egg: Fast and Extensible Equality Saturation", POPL 2021 (hashcons + union-find + rebuild).
- Library learning modulo equational theory: Cao et al., "babble", POPL 2023 (anti-unification over e-graphs) — the closest fit to J's idea.
- Stitch: Bowers et al., POPL 2023 (corpus-guided top-down abstraction search, compression objective).
- DreamCoder: Ellis et al., PLDI 2021 (wake / sleep library learning; MDL objective).
- Anti-unification: Plotkin 1970 / Reynolds 1970 (least general generalisation).
- Patent US10133657B2 design-around holds by construction: binding is by equation structure / e-class, never name text or per-position similarity.

## Steps (Rust, inside the doctor core: `src/doctor_abc.rs`, declared from `doctor.rs`; CLI `omni-render core --abc …`)
| # | Step | Class | Verify | Kill / bar |
|---|---|---|---|---|
| A1 | ALPHABET: lower Rust sections (doctor sectioner D0 tokens) to a typed term language — primitives `+ − × ÷ neg min max clamp abs`, compare / `and or not`, `if`, `sum/fold map filter` over an index, `field(x,"f")` read, `const`, opaque `call(f,…)`; types Int / Bool / List / Opaque; names erased to SSA slots | BUILD | `core --abc lower --src src/layout.rs` → share of fn sections lowered with ≤ 20 % opaque nodes; unit tests | ≥ 50 % of layout.rs fns lower, else re-scope the alphabet before A2 |
| A2 | E-GRAPH: own hashcons + union-find + rebuild (egg §3), rewrite rules as data (comm/assoc of + × min max, `x*2=x+x=x<<1`, `min(max(x,a),b)=clamp`, distribution, `a−b+b=a`, `if c x x = x`), saturation with node + iteration limits | BUILD | unit tests: the three `x*2` forms land in one e-class; probe pair (table min→max ≡ grid grow-to-limit) merges WITHOUT the hand probe | probe pair not merged after rules → stop, report |
| A3 | RECOGNISE: every indexed section (D9, 17 apps, 46,907 sections) inserted; equivalent / sub-term-shared e-classes across sections = "same use in the field"; rows `results/abc-recognise.jsonl` | BUILD | on the 3,958 D1 pairs: count pairs with ≥ 1 shared non-trivial e-class (depth ≥ 3) | < 5 non-trivial shared classes on 50 sampled pairs → stop (J's step-3 kill) |
| A4 | WORDS: anti-unification over e-classes (babble-style) → candidate abstractions (λ with holes typed), scored by compression (MDL: corpus size before − after rewriting with the abstraction); library `results/abc-library.json` with provenance (sections, apps) | BUILD | top-20 abstractions listed with compression gain + usage count; manual read of 10 | 0 abstractions with gain > 0 used in ≥ 3 sections → stop |
| A5 | SENTENCES: synthesis = compose library words, type-directed, to fill a missing equation of a range (D1b missing-feature cards / D1 donor pairs); emit behind `patch_on("patch.e<id>")`, `cargo check`, gate | BUILD | ledger `results/doctor.transplants.jsonl` method `abc`; gate rows | 0 of ~50 synthesised units compile → stop (J) |
| A6 | Records: MANUAL § DOCTOR core, DEVLOG, growth ledger counter `doctor-authored` on any pass; VOCAB row "code alphabet" | CLOSE | `grep -n "code alphabet" control-center/governance/VOCAB.md` | — |

## Rules
Every engine change gated (MANUAL recipe). Keep every harness + result (`results/doctor-runs/<date>/`). Index never takes vendored / foreign-licence
code (D9 refusal already in). One heavy CPU job at a time. Never push.

## STATUS LOG
- 10-06 plan written (J go: "after s5"). S5-WIRE first; A1 starts after S5 merges.
- 10-06 A1–A4 FIRST CUT (omni-render branch doctor/abc 334b30f; `src/doctor_abc.rs`, CLI `core --abc lower|probe|recognise|dump`; log
  `results/doctor-runs/2026-10-06/abc/abc-a1-a4.log`). A1 PASS on its bar: layout.rs 65/126 fns ≤ 20 % opaque (51.6 %); all omni-render
  383/943 (40.6 %; top opaque: field-of-value, match, .s(), .push(), if-let). A2 probe PASS 4/4 (x*2≡x+x≡x<<1, clamp≡min∘max, (a+b)−b≡a,
  a−b≢b−a) after moving distribution to opt-in (it grew 199k e-nodes). A3: 55 shared equations in 37 fns, 0.58 s (SplitMix64 written 3×,
  splitmix 2×; table/intrinsic_w span widths). A4: Plotkin LGG recovers the equation-probe pair with no names, ?0 + (?1 − ?0)·?2/?3, and on
  real layout.rs table↔grid 63 anti-unifiers in 0.34 s. HONEST: the probe pair does NOT merge in the e-graph (not equal — the table's
  share/divisor are compound) — it meets by anti-unification, which is the right tool. Pairwise LGG is O(n²): J 10-06 "use our resonance and
  sieve to find the vocab and structure faster" = next — readback sent (HV per e-class bound from op + children → sift shortlist → sieve
  buckets → exact LGG), awaiting J's yes. Then A4 corpus-wide MDL scoring over the D9 index, then A5.
- 10-06 RESONANCE + SIEVE (J readback confirmed): `core --abc words` — structural HV per e-class, LSH bands = residue buckets, exact LGG
  on the shortlist. layout.rs: 22,611 of 490,569 pairs (22×), 89 % weighted word recall, top-30 30/30. FLEET (142 Rust files, 1,658 fns):
  830 words in 1.85 s, 241 span ≥ 2 apps — calendar civil_from_days/days_from_civil written 3× (omni-render jsi_date, omni-posix date,
  omni-ui recur), SplitMix64 6× (incl. terminal-launcher tsift). Merged to omni-render main (385c9ea; tool only, baseline 18,296 unchanged).
- J 10-06 (readback confirmed): "if it needs a specific function or need, it can search by functions and build what it needs" → A5 =
  query by behaviour: (1) value fingerprints — evaluate each word / equation on fixed probe inputs (typed: ints, sequences) → fingerprint
  HV; (2) a need = a typed signature + a few input→output examples (from a D1b card, a failing box, or a seat); sift by fingerprint, exact
  check by evaluation; (3) nothing fits → type-directed enumeration over the words (bottom-up, smallest first, observational equivalence
  pruning by fingerprint), emit behind patch_on, cargo check, gate. Kill: 0 of ~50 needs answered → stop (J).
- 10-06 A5 FIRST CUT (omni-render 4c8a17f, merged; J "yes continue"): `core --abc need` — search by behaviour (evaluator over the
  alphabet; every sub-term, every argument order; names never read) + `--build` (bottom-up OE enumeration, learned words as components,
  CEGIS on held-out counterexamples, verifier = rustc on every example). Needs v3 (24): 16 FOUND in our code (days_from_civil /
  civil_from_days → jsi_date, is_leap → omni-posix, signum = clamp(x,−1,1), distance, saturating_sub, scale_list…), 4 BUILT + verified
  (clamp, count_pos, midpoint, avg_list) = 20/24 (kill bar 0/~50 not hit). Held-out caught an overfit (ceil_div = 1+(a−1)/b). MISSES:
  grow_share (the library's version sums a filtered list — no scalar 4-hole word), dot (no zip-lambda in the builder), gcd (while-loops
  opaque). Next: (1) needs from real doctor cards (a failing box's missing equation) instead of hand-written ones; (2) zip/two-list lambdas +
  while-loop lowering; (3) THEAD integration J asked about: develop the `code.debug` faculty (problem maker from our real equations,
  solver = equation localise + e-graph inverse, verifier stays independent) + an `arcd` dock engine (recognise / words / need receipts) +
  J-format traces from gate-passed acts — J decides before any faculty / dock change.
- 10-06 TRI-CODE-0 (J: "polygon triangle tech … take one whole and break it into pieces or take a few pieces/needs put them together",
  readback confirmed; omni-render 4325675, `core --abc tri`). Equations → name-free S–R–O triangles (8×1,024-bit lanes), functions →
  polygons (bipolar accumulators), behaviour face = equation fingerprints on canonical probes. RESULTS: (1) pieces→whole recall@5 0.77 vs
  exact signatures 0.98; with one wrong piece 0.52 vs 0.84; shape depth 2/3/6 no change; 43 ms/query → FAIL on its bar: when the pieces
  are exact, exact hashing of α-signatures beats superposition (polygon noise grows with √triangles; triangles are local motifs).
  (2) behaviour face: 15/24 needs in 0.75 ms total (index 15,913 fingerprints, 2.2 s once) vs A5 evaluator 16/24 in 1.2 s → PASS on
  speed (~1,600×) → becomes A5's first stage (fingerprint sieve, then the evaluator on the need's own examples decides). Caveat: probe
  table must discriminate (is_leap matched y%4==0 on small probes — add years/large values). Signpost for the geometric form: use it where
  exact fails — near-miss pieces (a different constant / operator), cross-language pieces — not as a replacement for exact signatures.
- 10-06 AST review (`<home>/Downloads/AST.txt`) answered: `<notes>/FOUNDATION/AST-REVIEW-RESPONSE-2026-10-06.md`. Adopted as next probes, in
  order (each gated, results kept): TYPES-0 (Option/Result/field types + method summaries + .push as store; bar layout.rs ≥ 70 % fns
  ≤ 20 % opaque, today 51.6 %) → SKETCH-0 (statement lowering: while → loop(state, cond, step), match → case; statement-level
  anti-unification = skeleton words; builder picks a skeleton then fills holes; kill 0/5 of gcd, dot, ceil_div + 2 real while needs) →
  TRACE-0 (loop step + invariants from execution traces; kill < 2/4) → PATH-0 (exact path-context rows → hole fillers; bar top-5 ≥ 50 %).
- 10-06 PROSE ENGINE × AST inspection (J: "the speech/prose generator in our thead would add value to the ast"):
  `<notes>/FOUNDATION/PROSE-ENGINE-X-CODE-AST-INSPECTION-2026-10-06.md`. Key finds: (1) PLM-0's frame-first (lock goal + givens,
  backward-chain; work 16 vs 960) = top-down example-propagating synthesis (λ², Myth, FlashMeta — Microsoft's framework is named PROSE)
  → the fix for A5's size-7 wall; (2) the 16-op epistemic ISA maps 1:1 onto the AST statement layer → the doctor speaks the faculties'
  trace language; (3) "What was the prompt?" = inverse synthesis → auto-generated needs + J-format rows; (4) E13 "kept only if it
  parses back" = round-trip verifier for printer / transplants / A1. Probes queued: FF-SYNTH-0 → ROUNDTRIP-0 → ISA-CODE-0 → INVERSE-0 →
  RECEIPT-CODE-0 / FRAME-AST-0 (code.debug integration needs J's go).
- 10-06 FF-SYNTH-0 DONE (J: "quit your negativity and build"; "use our math concepts"; omni-render 42053cf → 7d4d169, merged).
  Frame-first builder (`core --abc need --build --ff`): goal + givens locked, witnesses Add/Sub/Mul/Div/Max/Min/Sel give interval
  sub-goals answered from a behaviour-indexed bank; loop sketch (two-slot while); Occam over witness orders; CEGIS ≤ 16 rounds;
  residue math from the KB — period mining (#10 gcd of differences per output class, nested) + mixed-radix refinement (#7).
  RESULT (24 needs × 24 held-out, rustc-verified): bottom-up 18/24 → frame-first 22/24; + library search = 24/24 answered.
  Built from examples alone: grow_share, dot (1.9k work vs bottom-up fail at 153k), gcd (Euclid loop), ceil_div ((a+b−1)/b after
  CEGIS moved off an overfit), is_leap = if y%100==0 { y%400==0 } else { y%4==0 }. Bugs found + fixed: Div witness interval for
  negative divisors; assembled terms re-checked vs goal. Next: SKETCH-0 / ISA-CODE-0 statement layer, then real needs from renderer
  cards; the same frame-first + residue methods to the transformer (J: "then we will apply the same to the transformer in return").
- 10-06 BROWSER-BODY-0 brief for a second seat (J): `spawn-briefs/active/BROWSER-BODY-0-builder.md` (omni-ui Web app; own worktree).
- 10-06 EVENING — CODE-ABC closes the loop on the patient: builder + constant / floor-rational mining synthesizes Chrome's law AND our
  engine's law from the same probes; the equation diff names the defect (textarea advance 8.031 vs 8.025 px; input constant 8 vs 25 px;
  legend constant vs shrink-to-fit); emit_laws writes the Chrome law as Rust at the site (patch.oracle_laws) → OURS == CHROME 120/120.
  Next: scale to every oracle target + spec_probe (auto-symbolize failing cases) + parse gatherer formulas as candidate laws.

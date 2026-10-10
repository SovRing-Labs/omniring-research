# The doctor core, part 1: equations as a code alphabet, and search by function

| | |
|---|---|
| **Date** | 2026-10-06 → 2026-10-07 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). The author reviews each document before publication. |
| **Type** | measured result (one laptop CPU, no model) |
| **Verdict** | Lowering bar (≥ 50 % of layout functions) PASS; search by function 24 / 24 PASS; triangle-code retrieval FAIL as registered |
| **Code** | the renderer's `src/doctor_abc.rs` (`harness/part7/ch4-engine/src/doctor_abc.rs`); results `docs/appendix/part7/ch4-abc/results/` |

## What the doctor is
The author's definition (readback confirmed): the doctor is a **core** — a core that learns and repairs our own applications one at a time
(the renderer first, the launcher next), finds donor code by reverse PIFS, applies known-good combinations, tests with logic and the
application's own judge, and keeps a knowledge base of verified fixes. It lives inside the renderer binary, CPU only, no model. The
direction came on 10-06: *"let's first find published standards/specsheets that we can have an agent build a quick codebase from for our
most used/needed items. then we'll set up a cleanroom pipeline for when the doctor runs into a problem it can't solve"* (doc 37).

*The record below is the full measured account from the technical disclosure's working chapters: every gate, every failure, with the
harness and result paths in this repository. "Section n" and "§n" inside it refer to the sections of that chapter; the matching documents here
are listed in the README. "Recorded; no saved result" marks a figure the project recorded whose output file is not published.*

### What the doctor is, today
- **Owner's definition (readback confirmed):** the doctor is a core — a core that learns and repairs our own applications one at a
  time (the renderer first, the launcher next), finds donor code by reverse PIFS, applies known-good combinations, tests with logic
  and the application's own judge, and keeps a knowledge base of verified fixes. "Evolving the doctor" means the doctor itself
  becoming a different kind of core; a core never has a core under it.
- **What exists (all inside the renderer binary, Rust, CPU only, no model):** the Part 6 stations; the code alphabet (§4.3); the
  Chrome black-box oracle and rebuild loop (§4.4); the geometric triage instruments (§4.5); one station that already is rendered
  code, the T25 box kernel (§4.7); the pristine map and unattended fix loop (§4.8); the two-team clean room (§4.9). **What is still
  batch:** everything except the T25 box kernel; the intended design that would make the other motions rendered ones is "designed, not
  measured" (§4.14).
- **Gate hardening found in this window (each a failure disclosed as measured):**
  - The binary gate compared agreement by box index. Pseudo-elements live in the same arena as DOM nodes, so a style change that adds
    or drops one shifts every later index: on one held-out page that did not change in geometry, the candidate that added `:has()` read **32 lost / 32 gained** by index and **0 / 0** with
    the stable key (the box's index among real, non-generated nodes). (harness: harness/part7/ch4-engine/src/doctor.rs `binary_gate`, harness/part7/ch4-engine/src/repair.rs `score_stable`; result: docs/appendix/part7/ch4-gate-series/results/round7/bgate-all2.log, docs/appendix/part7/ch4-gate-series/results/round7/bgate-all2-stable.log)
  - A patch switch was read before the program file had been loaded, so the first page of a process saw every patch off. Fixed by
    loading before the first read. (harness: harness/part7/ch4-engine/src/layout.rs `patch_on` (guard and its comment))
  - The yardstick tolerance (x, y, w, h each within max(2 px, 5 % of the value)) lets a y error of 100 px or more "agree" deep in a
    page: one pair of footers agreed at 161 px off. Rule adopted: classify a small loss by rectangle before trusting it. (harness: harness/part7/ch4-engine/src/repair.rs (the `agree` closure); result: docs/appendix/part7/ch4-gate-series/results/doctor.growth.jsonl (grid-span-fill row; "growth" in this chapter means the doctor's own count of agreement boxes gained per merged fix, not the school's growth of chapter 1))
  - A round script ran its shape census over all pages including a held-out page; one fix family then came from that page
    (+44 boxes on it, 0 lost; the same fix gained +12 on a replay page). The fix is a specification feature, but that +44 is no longer an
    independent check. Rounds now use replay pages only. (harness: harness/part7/ch4-gate-series/doctor_round.sh; result: docs/appendix/part7/ch4-gate-series/results/round3/gate-line-clamp.log, docs/appendix/part7/ch4-gate-series/results/doctor.growth.jsonl)
  - Several fixes only pass together because their errors compensate: the image chain (replaced-element `aspect-ratio`, a replaced
    element's automatic height from its used width, empty explicit grid rows kept) gained +328 as a set; the single-fix losses are recorded only in a development note. The gate is applied to the set.
    (result: docs/appendix/part7/ch4-gate-series/results/doctor.growth.jsonl)

### The code alphabet (equations as letters, e-graph, words, search by function)
- **A1 alphabet (`src/doctor_abc.rs`, CLI `core --abc lower|dump`):** a Rust function is lowered to name-free SSA terms over a typed
  primitive set (`+ − × ÷ neg min max clamp abs`, comparisons, `and or not`, `if`, `sum / fold / map / filter` over an index, field
  read, constant); inputs become numbered slots, strings become `str`, every unknown call becomes a unique opaque node. Types: Int,
  Bool, List, Opaque. A function counts as lowered when at most 20 % of its nodes are opaque.
  **G1 (bar: ≥ 50 % of the layout file's functions):** saved log: 70 of 126 functions (55.6 %); across the whole renderer 382 of 943 (40.5 %); the
  opaque reasons by frequency on the layout file: field-of-value reads 67, `match` 52, method calls 51, `.push` 50, `if let` 48, `call new` 45, `matches!` 44. The development note records the first cut as 65 of 126 (51.6 %) and
  383 of 943 (40.6 %); the saved log is a later re-run of the same command and is the only result file. The bar is met either way. (harness: harness/part7/ch4-engine/src/doctor_abc.rs; result: docs/appendix/part7/ch4-abc/results/abc-a1-a4.log)
- **A2 e-graph:** hash-consing + union-find + rebuild, rewrite rules kept as data (commutativity / associativity of `+ × min max`,
  `x·2 = x+x = x<<1`, `min(max(x,a),b) = clamp`, `a−b+b = a`, `if c x x = x`), saturation with node and iteration limits; distribution is
  opt-in. **G2 (probe):** 4/4 — the three `x·2` forms land in one class, clamp ≡ min∘max, (a+b)−b ≡ a, a−b ≢ b−a. **Negative:** with distribution available, `(a+b)−b` still reaches 18,130 e-nodes without
  saturating in 10 iterations; the development note records 199,000 e-nodes when distribution was on by default (recorded; no saved result). **Negative:** the table min→max distribution
  and the grid grow-to-limit distribution do NOT merge in the e-graph (0 shared signatures; their share and divisor are compound terms), so the pair meets
  by anti-unification, not equality (2 anti-unifiers on the isolated pair, 63 on the real layout code). (harness: harness/part7/ch4-engine/src/doctor_abc.rs; result: docs/appendix/part7/ch4-abc/results/abc-a1-a4.log)
- **A3 recognise:** α-normalised signatures with commutative operands sorted by shape; **G3:** across the renderer's source files, 55 shared equations in 37 functions (the layout file alone: 24 shared in 10 functions, 0.23 s). The development note records a
  time of 0.58 s for the 55 (recorded; no saved result). (harness: harness/part7/ch4-engine/src/doctor_abc.rs; result: docs/appendix/part7/ch4-abc/results/omr-recognise.jsonl, docs/appendix/part7/ch4-abc/results/abc-a1-a4.log)
- **A4 words:** Plotkin/Reynolds anti-unification (least general generalisation) over e-classes; pairs shortlisted by "resonance +
  sieve": each e-class gets a structural hypervector (operator bound with position-rotated children), a Hamming/inner-product sift
  shortlists, LSH bands act as residue buckets, the exact generalisation decides. The generalisation of the table and grid pair
  recovers, with no names, `?0 + (?1 − ?0)·?2 / ?3`. **G4:** the layout file (exhaustive reference: 490,569 pairs, 286 words): 22,611 pairs examined (21.7× fewer) at 89 %
  weighted recall of the words, top-30 words 30/30; the sweep of the other settings: 5,173 pairs / recall 0.60 up to 28,609 pairs / recall 0.93. Whole Rust fleet of the owner's workspace (142 files, 1,658 functions): 830 words, 241 of them
  spanning ≥ 2 applications (recomputed from the word file) — a civil-calendar pair of functions written 3 times and a SplitMix64 mixer written 6 times; the saved log reads 2.42 s for the whole fleet pass (the development note says 1.85 s).
  **Negative:** the sieve dropped the pair whose real grid form has a Σ, so the exhaustive pass (17.4 s) is the reference. (harness: harness/part7/ch4-engine/src/doctor_abc.rs `words`; result: docs/appendix/part7/ch4-abc/results/abc-words-sift.log,
  docs/appendix/part7/ch4-abc/results/fleet-words.jsonl, docs/appendix/part7/ch4-abc/results/abc-a1-a4.log)
- **A5 search by function, build what is missing (`core --abc need`):** a need is a typed signature plus input→output examples, held-out
  rows and validate rows. Stage 1 sifts by value fingerprints (each word evaluated on fixed probe inputs); stage 2 evaluates the need's
  own examples on every sub-term and argument order (names are never read); stage 3, when nothing fits, builds: bottom-up enumeration
  with observational-equivalence pruning, learned words as components, counterexample-guided repair on held-out rows (CEGIS), and
  `rustc` as an independent verifier on every example. **G5 (24 hand-written needs, 24 held-out each; kill bar 0 of ~50 answered):**
  16 found in the owner's code, 4 built and verified = 20/24; the four misses are a share over a filtered list, a dot product (no zip lambda), a gcd (while-loops opaque) and `ceil_div`, whose
  first build, `1 + (a−1)/b`, was an overfit that the held-out rows rejected (the rejected candidate is kept). (harness: harness/part7/ch4-engine/src/doctor_abc.rs `need`; result: docs/appendix/part7/ch4-abc/results/needs-v3.out.jsonl, docs/appendix/part7/ch4-abc/results/build/ceil_div.rs)
- **Frame-first synthesis (frame-first; results in `ff-synth/`):** lock the goal and givens, let arithmetic witnesses (Add/Sub/Mul/Div/Max/Min/Sel) turn the goal into
  interval sub-goals answered from a behaviour-indexed bank; a two-slot loop sketch; Occam order over witnesses; CEGIS ≤ 16 rounds;
  residue arithmetic mined from the examples (period of differences per output class, mixed-radix refinement; floor-rational by simplest
  fraction). **G6:** bottom-up 18/24, frame-first **22/24** built from examples alone (a library of two functions); library search answers the other two (the calendar functions): 24/24 answered. Built: share (a depth-3 witness, size 12),
  dot (1,935 work units; the bottom-up run gave up with no answer after 152,893), gcd (a Euclid loop; 67–121 million work units across the three saved runs), `ceil_div` (`(a0 + (a1−1)) / a1`, size 7, 2 CEGIS rounds), `is_leap`
  (`if y%100==0 { y%400==0 } else { y%4==0 }`, size 16, 4 CEGIS rounds). The first run answered 0 of 24 because the independent compiler was not on the path (nothing was accepted). **Bug found and fixed:**
  the Div witness interval for negative divisors (the fix is in `div_range`). (harness: harness/part7/ch4-engine/src/doctor_abc.rs `ff_synth`; result: docs/appendix/part7/ch4-abc/results/ff-synth/ffsynth1.log, docs/appendix/part7/ch4-abc/results/ff-synth/ffsynth4.log, docs/appendix/part7/ch4-abc/results/ff-synth/ff5.jsonl, docs/appendix/part7/ch4-abc/results/ff-synth/ff5--ff.jsonl, docs/appendix/part7/ch4-abc/results/ff-synth/ff8--ff.jsonl)
  (the bug itself has no failing-run record) [P gap]
- **Triangle code (polygon face):** an equation as a name-free subject–relation–object triangle (8 lanes × 1,024 bits), a function as a polygon
  (bipolar accumulator), a behaviour face = equation fingerprints. **G7a (pieces → whole, bar: beat exact signatures):** recall@5 0.77
  against 0.97–0.98 for exact α-signatures; with one wrong piece 0.52 against 0.84; depth 2 / 3 / 6 made no change; 42–57 ms per query → **FAIL as registered**. **G7b (behaviour face as a sieve):**
  15/24 needs in 0.751 ms (index of 15,913 fingerprints built once in 2.19 s) against 16/24 for the evaluator in a recorded 1.2 s (~1,600× faster) → PASS on speed; caveat measured: the probe table must discriminate (`is_leap` was matched by the
  `y%4==0` of a date library). (harness: harness/part7/ch4-engine/src/doctor_abc.rs `tri`; result: docs/appendix/part7/ch4-abc/results/tri0.log, docs/appendix/part7/ch4-abc/results/tri-sweep.log)
- FIELD PREDICTS: equality saturation (egg) yields one class for algebraically equal terms and blows up under distribution plus
  associativity/commutativity; library learning by anti-unification over e-graphs (babble) and by top-down abstraction search (Stitch)
  finds shared abstractions with holes; bottom-up enumeration with observational equivalence stalls at small term sizes (TRANSIT),
  which frame-first / example-propagating synthesis (λ², Myth, FlashMeta) pushes past; superposed hypervectors lose capacity as bound
  items grow (Kanerva 2009), so exact hashing beats superposition when pieces are exact. All consistent with G2, G5/G6 and G7a.

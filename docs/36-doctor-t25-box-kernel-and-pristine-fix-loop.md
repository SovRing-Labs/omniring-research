# The doctor core, part 3: the T25 box kernel inside layout, and the unattended fix loop toward pristine geometry

| | |
|---|---|
| **Date** | 2026-10-07 → 2026-10-08 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). The author reviews each document before publication. |
| **Type** | measured result (one laptop CPU) |
| **Verdict** | Kernel exact and under 1 % of layout PASS; fix loop 565 → 220 defects with 0 pristine boxes lost; an overlap-blind judge found and fixed |
| **Code** | `harness/part7/ch4-t25/box_t25.py`, `t25_ifs.py`, `t25_families.py`; the renderer's `src/jit/t25.rs`, `doctor_shape.rs`, `doctor_fix.rs` (`harness/part7/ch4-engine/src/`) |

*The record below is the full measured account from the technical disclosure's working chapters: every gate, every failure, with the
harness and result paths in this repository. "Section n" and "§n" inside it refer to the sections of that chapter; the matching documents here
are listed in the README. "Recorded; no saved result" marks a figure the project recorded whose output file is not published.*

### The doctor's T25 box kernel (a box is one point on 25 rings; the kernel is rendered x86; it fires inside layout)
- **Encoding (`tools/box_t25.py` golden, `src/jit/t25.rs`):** a box is the point (x₀, y₀, w, h, r) with each coordinate in 1/64 px, one
  residue number system of 25 pairwise-coprime moduli (the 25 odd primes 3…101) in five groups of five rings: x₀ {3, 29, 41, 59, 101}, y₀ {5, 31, 37, 67, 89}, w {7, 23, 43, 61, 97},
  h {11, 19, 47, 71, 83}, **r {13, 17, 53, 73, 79}**. The product of all 25 is 116,431,182,179,248,680,450,031,658,440,253,681,535 ≈ 2^126.45 (recomputed; it fits one unsigned 128-bit integer); every residue < 128, so a box's whole point is
  25 bytes, one 32-byte AVX2 register (lanes 0–24 = the groups in the order x₀, y₀, w, h, r; lanes 25–31 inert zero). **The fifth coordinate r is the box's vertical offset inside its frame:** r = y₀ − (y₀ of the frame), where the frame is the box's parent rectangle in the same engine
  (ours uses ours' parent, Chrome's uses Chrome's; the root's frame offset is 0). Its group product is 13·17·53·73·79 = 67,548,871 units (≈ 1.055 million px), stored centred (offset ⌊67,548,871 / 2⌋ = 33,774,435 units, so r spans ±527,725 px); x₀ and y₀ carry an offset of 16,384 px so negative
  positions stay representable (group products 21,255,753 and 34,197,805 units); w and h are unsigned (products 40,963,391 and 57,886,939 units, up to 640,052 and 904,483 px). A coordinate c is stored per ring as (c + offset) mod m. The group exists because absolute y₀ alone cannot tell a box that is wrong
  from a box that was merely moved by its ancestor: the pair (y₀, r) separates them. Each failing box is then classed (tolerance max(2 px, 5 %) on w, h, 2 px on the rest): SHAPE if a w or h twist exceeds it, else OWN PLACE if the r twist exceeds 2 px, else CARRIED if only x₀ / y₀ twist.
  A box's TWIST is the per-ring difference (ours − plate) mod m; the plate is the oracle's point (or, §4.8, the page's own exact geometry);
  a group with any non-zero twist is decoded by the Chinese remainder theorem (the direct sum of residues times precomputed basis coefficients modulo the group product, centred; not Garner's mixed-radix form, which is the alternative) to the exact signed error. A TRIANGLE is the
  difference of two torus points (box − frame, box − a sibling), so translation invariance is free; a CARRIED box (triangle twist 0) is
  displaced only because its frame moved, an OWN box is not. The family KEY = the twist trits of the triangle + the (frame display, box display)
  pair; the SIEVE bucket is the residue address. (harness: harness/part7/ch4-t25/box_t25.py, harness/part7/ch4-engine/src/jit/t25.rs `coords`, `Program`, `decode`; result: docs/appendix/part7/ch4-t25/results/t15/box_t25.log; the group product and the round trip recomputed from the script's moduli (20,000 random points decoded exactly))
- **G1 golden (Python, whole corpus):** all 47,686 rectangles (23,843 boxes) encode and decode exactly; errors decoded from ring angles equal the direct errors on 4,298 / 4,298 failing boxes (the whole-corpus run time of 1.6 s is in the development note only (recorded; no saved result)); the five-group class split of those failing boxes: CARRIED 2,079 (48 %; the frame also
  failing for 96 % of them), SHAPE 1,972 (46 %; 82 %), OWN PLACE 247 (6 %; 81 %). Reverse IFS on absolute twists: 473 roots → 369 exact twist families (364 after a sift at θ 0.98); with the triangle key 473 → **103** families; on the pre-fix dump 517 roots → 403 absolute families against 108 triangle-key families, and the 26 repaired
  roots of one site fell in 3 triangle-key families (largest 17) against 23 absolute families (largest 2). (harness: harness/part7/ch4-t25/box_t25.py, harness/part7/ch4-t25/t25_ifs.py, harness/part7/ch4-t25/t25_families.py; result: docs/appendix/part7/ch4-t25/results/t15/box_t25.log, docs/appendix/part7/ch4-t25/results/t15/t25_ifs.log, docs/appendix/part7/ch4-t25/results/t15/t25_ifs_tri.log) 
- **G2 kernel in the engine (`core corpus --abc t25`):** the development note records it bit-exact against the golden on all 49 pages: twists 28,040/28,040, roots 372 = 372, triangle keys 372/372, families 109 = 109; AVX2 twist = scalar, 0 mismatches; kernel 54 µs per corpus (1.9 ns/box); residues 8.1 ms (scalar `rem_euclid`,
  77 % of the core); whole core ≈ 10.5 ms against ≈ 1.7 s in Python. Only the box count (28,040) and the root count (372) of this run are in a saved file (the fire marks of G5); the rest is working-note prose. (recorded; no saved result) (harness harness/part7/ch4-t25/t25_check.py, harness/part7/ch4-engine/src/jit/t25.rs present; no saved output)
- **G3 rendered (`t25::render`):** the kernel is GENERATED x86: the development note records **1,209 bytes, 269 instructions, rendered in 19 µs** — 25 nine-instruction ring blocks
  (offset, reciprocal magic ⌈2⁴⁰/m⌉, modulus as immediates: `q = x·M >> 40`, `x − q·m`, no divide) plus 7 AVX2 instructions twisting all 25 rings against
  the plate; 11 new encodings equal `objdump`'s; residues 0 / twists 0 mismatches over 28,040 boxes; residues + twist 598 µs per corpus (21.3 ns/box;
  scalar residues were 7,562 µs). The program (moduli of the tier, plus the plate) is hashed, and a changed tier re-renders the kernel by hash (the source of this step ships; the kernel bytes and the timing do not). (recorded; no saved result)
- **G4 live view:** the plate is built once per page; every frame the generated kernel fires over all of one news page's 3,256 boxes (that page's box count is in the first census, §4.5) in ~80 µs
  (24 ns/box); the engine lays out and rasterises the frame from the kernel's output (25 rings around the kernel, each ring's byte block lit where it twists). The frame manifests do not ship; the timing is working-note prose. (recorded; no saved result)
- **G5 fires inside every layout pass (`--abc t25fire`):** the hook runs after each `Layout::run` when a plate is armed (one thread-local check otherwise).
  Kernel agreement over the 49 pages: **24,032 of 28,040** boxes = the station's 24,032 (the baseline of the merge gates); roots 372; toggling `body_collapse` the kernel reads **49 lost / 3 gained** (23,986). The development note adds 0 mismatches per box, that the toggle equals the station and the patch gate, and 109 families (recorded; no saved result).
  Firing cost, recomputed from the marks: **0.90 %** of layout time (17.8 ms of 1,979.7 ms) for the base program and 0.97 % with the toggle; the recorded range 0.74–1.05 % covers both; per page the share runs 0.04–7.4 %, median 1.1 %. The 0.54 % in a later procedure note is not in the marks file; the first pristine map run, which fires the same kernel,
  saved 0.558 % (docs/appendix/part7/ch4-pristine/results/doctor-map/*). Both instruments are reported. (harness: harness/part7/ch4-engine/src/doctor_shape.rs `t25fire`, harness/part7/ch4-engine/src/jit/t25.rs; result: docs/appendix/part7/ch4-t25/results/t25fire-e1.marks.jsonl, docs/appendix/part7/ch4-pristine/results/doctor-map/corpus-2026-10-07.map.json)
- **Event-bus use of the same rendered kernel:** the development note records 1,000,000 events × 2 runs, load 8.7: batched 24–25 ns/event, one call per event 27–28 ns, encode + confirm + dispatch 39–42 ns, scalar reference 171–186 ns; residues 0 / twist 0 mismatches; 10,000 damaged plate rows flagged exactly. (recorded; no saved result) (harness `bus_bench` in harness/part7/ch4-engine/src/jit/t25.rs; no saved output)
- FIELD PREDICTS: the Chinese remainder theorem reconstructs a value exactly when it is below the product of the moduli, and residue arithmetic
  works channel by channel without carries (Garner 1959; Szabo & Tanaka 1967), so a kernel over 25 byte-wide channels should equal a big-integer
  reference bit for bit and vectorise; replacing division by a multiply-and-shift with a precomputed reciprocal is exact for a bounded dividend
  (Granlund & Montgomery 1994). Consistent with the recomputed round trip and the golden's exact decode.

### The pristine map and the unattended fix loop (the doctor repairs a page's own code)
- **Direction (owner, readback confirmed):** the goal is not agreement with Chrome but mathematically pristine geometry — every box an exact point,
  every relation to its frame and siblings exact; Chrome stays a reference for intent. The pristine plate is derived INSIDE the kernel from the page's
  own boxes, so any page bundle can be mapped without an oracle snapshot.
- **Six relations in 1/64 px (a defect = a sub-pixel near-miss; a whole pixel or more is deliberate):** *overflow* (a box leaves its non-scrolling
  frame by > 0.5 px at left, right or top; not absolute/fixed) → place inside; *near_flush* (left/right edge 1–63 units off the frame's content box) → flush; *near_align*
  (left edge 1–63 off the previous sibling's) → aligned; *near_touch* (gap to the previous sibling 1–63) → touching; *near_equal* (width 2–64 off
  the previous sibling's) → equal; *uneven_gap* (three siblings on one line, gaps differing by 2–64) → even. (harness: harness/part7/ch4-engine/src/doctor_shape.rs `pristine`; result: docs/appendix/part7/ch4-pristine/results/pristine/defects-exact.jsonl)
- **Life cycle:** FIRST LOAD (one map on a page's first layout) → DORMANT (nothing runs; one thread-local check per layout) → WAKE (a re-map after a
  DOM or script change, a viewport resize, or a failed check; the browser-process hooks for the first two are not wired) → REPAIR (the kernel fires
  every layout pass while a candidate is judged).
- **Map (`--abc t25map`; any bundle):** per box the twist against the pristine plate, CRT-decoded to the exact per-axis error, the rule that set the
  target = the defect kind, a family key. **G1:** the first corpus map (49 pages): 28,058 boxes, **27,491 pristine (97.98 %), 567 defect boxes** carrying 570 kind hits (two boxes carry two and three kinds): overflow 476,
  near_flush 57, near_align 5, near_touch 5, near_equal 27, uneven 0 (570); 53 families. The older pristine station reads the same 570 hits on the same 567 boxes by kind 475 · 58 · 5 · 5 · 27 · 0 (one box differs between overflow and near_flush); the development note's "equal on the Chrome-comparable
  set, 27,963 boxes / 27,396 pristine" is not in a saved file (recorded; no saved result). (harness: harness/part7/ch4-engine/src/doctor_shape.rs `pristine`, harness/part7/ch4-engine/src/jit/t25.rs; result: docs/appendix/part7/ch4-pristine/results/doctor-map/corpus-2026-10-07.map.json, docs/appendix/part7/ch4-pristine/results/doctor-map/corpus-2026-10-07.defects.jsonl, docs/appendix/part7/ch4-pristine/results/pristine/defects-exact.jsonl)
- **Solve loop (`--abc t25solve`), per defect box, roots first:** read the box (rule, axis, exact error, frame) → candidates cheapest first: a knowledge-base
  hit for the family key; a formatting knob; a rounding fix (precedent: cumulative-rounding exact split, near-flush 136 → 58); a page-code rewrite written
  as a per-site CSS fix sheet loaded last in the cascade (selectors by `:nth-child` path); an engine patch → judge in repair mode: accept only if the box's
  twist → 0, **0 boxes lose pristine**, and the defect count drops → store the outcome (family key × template, with failures as negative knowledge).
  Templates: margin-left shift, margin-top shift, exact width, width = frame, max-width = frame, min-width 0, letter-spacing fit, frame scroll (an item wholly
  past its frame's edge is a row item, so the frame becomes a horizontal scroller), vertical-align top, position shift. (harness: harness/part7/ch4-engine/src/doctor_fix.rs, harness/part7/ch4-engine/src/doctor_shape.rs; result: docs/appendix/part7/ch4-pristine/results/doctor-kb.jsonl (template and class fields))
- **Route 2 (starts once a site is ≥ 97 % pristine):** the geometry is written INTO layout (a box laid out at the doctor's exact offset and width; its children
  and paint follow, text re-wraps), stored per site beside the CSS sheet; rounds repeat until no defect is left or no round passes, because siblings are
  not carried by each other (median 2 rounds). A post-layout translation is not possible cleanly (paint items carry no node and later splices shift indices).
- **G2 first unattended corpus run (49 sites, judge = pristine only):** defects 565 → 220, 331 fixed, pristine 97.99 → 99.22 % (arithmetic on 28,058 boxes), 0 pristine boxes lost; an independent reload with the sheets reads 222 (220 + 2 in a shadow tree no selector reaches); knowledge-base reuse: 105/105 on one site's family and 62/62
  on another fixed first try; candidate classes: structure 298/493 fixed, rounding 30/56, format 3/3; templates that passed: margin-left shift 145, margin-top
  shift 94, exact width 36, width = frame 26, max-width = frame 23, min-width 0 6, letter-spacing fit 1. The archived first knowledge base reproduces the fixed-box counts exactly if each of its rows is read as stored twice: 1,970 rows, 662 passing = 2 × 331; templates 290 / 188 / 72 / 52 / 46 / 12 / 2 = 2 × the counts above; classes 596 / 60 / 6 = 2 × 298 / 30 / 3
  (596 of its rows occur exactly twice). **Failures as measured:** the development note counts 640 failed trials, 618 "box still defective" (the declaration did not move the box): the candidate library is the limit; the file read the same way gives 654 failed trials and 622 with the defect count unchanged. The run completed in 374 s (job history).
  (harness: harness/part7/ch4-engine/src/doctor_shape.rs `t25solve`; result: docs/appendix/part7/ch4-pristine/results/doctor-kb.v1-overlap-blind.jsonl, docs/appendix/part7/ch4-jobs/results/job-history-excerpt.tsv)
- **G3 route 2:** 565 → 145 defects, 99.48 % pristine; the reload reads 147 (145 + 2) and the saved list has **147 defect boxes on 15 sites** (three sites hold 108 of them: 37, 36, 35); route 2 on 16 sites (79 boxes) and five sites at 93.9–96.7 % (below the 97 % threshold, route 2 did not start) are working-note prose (recorded; no saved result). The run took 256 s. (result: docs/appendix/part7/ch4-pristine/results/doctor-map/after-r2.defects.jsonl,
  docs/appendix/part7/ch4-jobs/results/job-history-excerpt.tsv)
- **Failure found by inspection — an overlap-blind judge:** the six relations never compare siblings with each other; the judge's runs raised in-flow sibling
  overlaps from 242 to 340 (boxes pulled inside the frame onto neighbours) and still reported 99.48 %. Fix: the map counts sibling overlaps (floats and absolute boxes
  excluded); both judges reject a fix that raises them; the first knowledge base was archived (file above). **G4 (fresh run, original corpus):** 565 → **24**, **99.91 %** (arithmetic), overlaps 242 = baseline; reload 26 (24 + 2). (recorded; no saved result) (no saved overlap counts or run output; job history: a run of 288 s)
- **G5 top-100 set** (a compiled list of 100 widely used public sites, adult sites left out, captured with scripts off, kept outside the frozen yardstick; knowledge base carried over): the saved before-map lists **1,464 defect boxes on 68 of the 100 sites** (the development note counts 1,460; the difference of 4 is not explained) → development note: **106**, 97.28 → **99.80 %** (arithmetic on 53,764 boxes), 67 of 100 sites at 0, overlaps 328 = baseline, reload 110 (106 + 4 unreachable);
  frame-scroll used 414 times, margin-top shift 241, margin-left shift 65, exact width 56. Eleven per-site geometry files are saved. The run took 454 s. (harness: harness/part7/ch4-pristine/fetch_corpus.py, harness/part7/ch4-pristine/urls-top100.txt (list); result: docs/appendix/part7/ch4-pristine/results/doctor-map/top100-before.defects.jsonl, docs/appendix/part7/ch4-pristine/results/doctor-fixes-top100/*.geo.json, docs/appendix/part7/ch4-jobs/results/job-history-excerpt.tsv)
- **Intent trade-off, disclosed:** with the fix sheets loaded, agreement with Chrome fell 24,032 → 23,225 (−807): the defects are in the published design (Chrome draws them
  too), so pristine fixes move boxes away from Chrome by construction; part of the 807 may be collateral (descendants that moved with a fixed box). The owner kept the judge
  pristine-only. (recorded; no saved result)
- **Caveat measured by the development note:** with scripts off, app-shell sites are near-empty to the doctor (one music site 2 boxes from 166 KB of HTML; six more sites 0 boxes); the map of
  such sites needs the browser's script path (§4.11). Lowest sites left: one at 95.6 % (18 defects), one at 98.2 % (26). (recorded; no saved result)
- FIELD PREDICTS: search-based repair against a visual oracle (XFix, Mahajan et al. 2017) predicts that candidate edits fix many boxes and introduce collateral
  change, so the oracle must also test for non-regression; test-based repair overfits when the oracle is weak (Smith et al. 2015) — an overlap-blind judge is such an
  oracle. Consistent with the 242 → 340 overlaps and the 618 / 640 no-effect trials.

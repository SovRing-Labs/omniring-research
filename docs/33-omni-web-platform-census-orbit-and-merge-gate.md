# Omni Web: the page platform, a 24-site census, the Orbit chrome and the merge gate

| | |
|---|---|
| **Date** | 2026-10-07 → 2026-10-08 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). The author reviews each document before publication. |
| **Type** | measured result + design record |
| **Verdict** | Census: frames on 24 / 24, but **"lightweight" fails on script-heavy pages**; test262 54.5 % → 56.85 %; merge gate 0 boxes lost in three runs; the video site's music front end **not made usable** |
| **Code** | `harness/part7/ch3-census/census.sh`, `harness/part7/ch3-test262/test262.py`, `harness/part7/ch3-js-platform/`, `harness/part7/ch3-merge-gate/merge-gate.sh` |

*The record below is the full measured account from the technical disclosure's working chapters: every gate, every failure, with the
harness and result paths in this repository. "Section n" and "§n" inside it refer to the sections of that chapter; the matching documents here
are listed in the README. "Recorded; no saved result" marks a figure the project recorded whose output file is not published.*

## The first design was rejected, and the remedy is a rule

Variation considered and rejected (2026-10-07): three chrome layouts (A one-row, B compact, C keyboard-and-palette) × light / dark /
high-contrast × seven states, delivered as a clickable mock-up. The owner rejected it: "the opposite of what we are looking for".
Cause, as recorded: the author first measured what the renderer could draw (no rounded corners, shadows, gradients, motion or blur)
and made that the ceiling, so the design was flat and boxy. **Remedy written as a procedure:** start from the vision and the best
current work in the field; design the target in full (look, feel, motion, accessibility); turn each capability the design needs into
engine work; show the owner the target with that engine work listed beside it. Result: the second design ("Orbit") was approved the same
day; its design document lists eleven engine capabilities (`docs/appendix/part7/ch3-design/results/WEB-DESIGN.summary.md`, table "Engine work the design creates"; section 8), each of which was then gated by the layout gate. The approved vision page (`orbit.html`, shipped once its sample text is replaced by the neutral text) (29,189 bytes as authored, before its sample text was replaced: one document of markup, style and script), its eight target shots (1280 × 800, rendered by Chrome as the look to reach) exist in the author's tree and are not shipped, because they embed article text of a third-party site (the original page reproduced them). **The text on the shipped Orbit pages (`orbit.html`, `mockup.html`) is original sample text written for this study, and the eight Orbit screenshots are not shipped;** the rejected first draft is `mockup.html` (same condition) (11,526 bytes as authored). Design: the page owns the window; a glass bar
floats over it; nothing is shown that the page in front of the person does not need. *Designed:* WebExtensions-style plug-in surface and
developer tools (inspector with a box-exactness view, console, network log) were specified as later steps and are not built (section 13).

FIELD PREDICTS (design method): compact / auto-hiding chrome and keyboard-first command surfaces are established in published products
(design references observed, no code read: Zen Browser compact mode, Arc, Safari compact tab bar, qutebrowser, Nyxt, the Chromium
project's URL display guidelines). Nothing is predicted about our numbers from them; they only fix the target experience.

## The page platform: a 106-check probe, a 24-site census, and what still fails

**Probe.** Harness `harness/part7/ch3-js-platform/index.html` (served by `harness/part7/ch3-connectivity/server.py`): 106 checks = 88 synchronous + 15 asynchronous + 3 load-order checks
(counted from the page source by name prefix, 106 distinct names; by area: language 39, DOM 31, network 9, BOM 8, async 7, web APIs 5, events 3, load order 4), each recorded in a
result map and summarised in the page title.
Chrome's run of the same page printed the title "FINAL pass 106/106" (`docs/appendix/part7/ch3-js-platform/results/jsprobe-chrome.summary.txt`, one line read from Chrome's document dump; the dump is not shipped): the probe itself is valid.
Engine progression from the author's working log: 66 / 106 (first measurement) → 79 → 83 → **106 / 106** (recorded; no saved result). What is saved: eight later gate folders of a second engine worktree, run with a parameterised copy of the same script that does write the line, each hold `jsprobe.txt` = "FINAL pass 106/106"
(`docs/appendix/part7/ch3-later-gates/results/gate-01/` … `gate-08/`, file `jsprobe.txt`, with `binaries.txt` giving the sha256 of the old and new binaries). So the probe is passed 106 / 106 by those eight builds, none of which is a browser gate. The gaps closed, in
order: language items (class `super`, class fields, generators, tagged templates, labelled `continue`, the iterator protocol, BigInt,
WeakMap, Proxy, Reflect, typed arrays, `eval`, regex named groups), then the page platform (`atob`, `TextEncoder`, `URL`, `FormData`,
`XMLHttpRequest`, `getComputedStyle`, layout boxes readable by scripts, `MutationObserver`, `customElements`, `attachShadow`,
`template.content`, `history.pushState`, dynamically inserted scripts) and ES modules with import maps. The language half was driven by a
law-per-gap method (Omniglyph `js` laws, node as oracle; 60 / 60 on our IR (recorded; no saved result)). **Limit, stated plainly:** a 106-check probe is a smoke test, not conformance. A separate run of the language test suite (test262, suite commit c8c79889, harness `harness/part7/ch3-test262/test262.py`, one run per test, strict only when flagged) found
29,203 of 53,607 executed tests passing (54.5 %) on 2026-10-08 00:30; 53,614 tests were collected and 7 skipped, which settles the two denominators in the records; 24,404 failed. Result:
`docs/appendix/part7/ch3-test262/results/baseline.json` and `full.summary.txt`. Without the two Temporal directories that the summary lists (4 of 6,634 passing) it is 62.2 % (29,199 of 46,973). Engine: a second engine worktree; the run's
reproduction summary (`docs/appendix/part7/ch3-test262/results/repro.summary.json`) records the short revision f6e6705 and no uncommitted files; the result carries the binary's
sha256 prefix b4aedcda77368db2. That is not the browser worktree's pinned engine. Failure classes are in the file (most frequent: uncaught ReferenceError 7,734; Test262Error 7,674; a missing early syntax error 3,756; TypeError 2,748; timeout 107).
Two later rounds are summarised in `docs/appendix/part7/ch3-test262/results/r1.summary.txt`, `r2.summary.txt`, `r2b.summary.txt` (55.33 %, 56.83 %, 56.85 %; no binary named in them).

**Script parse path (step 8, 2026-10-06/07).** A Rust JavaScript parser produces the same intermediate form as the build-time reference
parser (acorn): 29 laws × 2 seeds, parser path = node = reference path in 58 of 58 runs (`docs/appendix/part7/ch3-js-parse/results/omniglyph-jsparse.json`: 29 distinct laws, 17,002 generated cases in all, every row true; harness
`harness/part7/ch3-js-parse/omniglyph_jsparse_parity.py`, which reads the Omniglyph runner and needs node and acorn); the
author's working log gives a further figure "345 of 345 programs, 6 of 6 injected mutations caught, 5.3 MB/s" (recorded; no saved result).

**Real pages, early** (`docs/appendix/part7/ch3-js-platform/results/js-pages.metrics.jsonl`, per-page counters only, 10 pages, script on, before the language work; the driving script is not shipped, but each row records its command): 0 parse errors; 28 scripts ran and 12
failed; failures on 4 pages (scripts ran / failed: a documentation book 7 / 7, a Python-enhancement page 4 / 2, a developer-docs page 4 / 2, a news-archive page 0 / 1). The working log says "scripts run on 6 of 10 pages"; the file, recounted,
shows 7 of 10 pages ran at least one script (4 with no failure). The per-page file is the measurement and is used; why the log's summary says 6 is not recorded. The js0 page and its
cases (script load, onclick toggle, a listener that cancels a link, `fetch` through the broker, a timer) are `harness/part7/ch3-js-platform/js0/{index,other}.html`, `app.js`, `data.json`; `harness/part7/ch3-js-platform/session8.txt`, `docs/appendix/part7/ch3-js-platform/results/session8.out.jsonl` and the two screenshots (`results/js0-load.png`, `results/js0-clicks.png`, captures of our own test page) show: after load "After: 2,4,6", after the clicks the heading
"Link intercepted by a listener", the hidden paragraph revealed, the fetched and timer paragraphs present, and the plain link navigating to the second page.

**Census (24 real sites, three runs).** Harness `harness/part7/ch3-census/census.sh` (`omni-render page`, script on, one page at a time,
120 s cap; the script names the browser worktree binary, revision not printed). Results, metrics only (page titles and script error texts of the sites are not shipped): `docs/appendix/part7/ch3-census/results/census-1.metrics.jsonl` (run 1), `census-2.metrics.jsonl`, `census-3.metrics.jsonl`.

| Run | Pages that produced a frame | Scripts ran / failed | Parse errors | Sites with ≥1 failed script |
|---|---|---|---|---|
| 1 (morning 10-07) | 20 of 24 (4 produced nothing) | 148 / 69 | 9 | 13 |
| 2 | 24 of 24 | 243 / 111 | 11 | 16 |
| 3 (after the language merge) | 24 of 24 | **402 / 39** | **1** | 12 |

Run 3 details (n = 24, recounted from the rows): HTTP 200 on 22, 403 on 2 (page shown); median wall time 2.6 s; four pages over 20 s (a code-hosting site 36.0 s, a
newspaper 23.3 s, a social site 39.6 s, and gnu.org **101.0 s** with 0 scripts — it was 0.92 s in run 2 and 1.56 s in run 1; the run-3 row shows 24,220 ms of layout against 90 ms in run 2 and one refused fetch against none, 0.3 ms of script; the remaining
~77 s are attributed to nothing in any file, so the cause is open; the code-hosting site's 36.0 s is 33,889 ms of script time with 102 refused fetches); 8 pages have page
height ≤ 821 px (the window is 800), i.e. app-shell or blocked pages that built little (two forum front pages, the 403 pair, an auction site,
a mail app, a search page, a maps app) — **"24 of 24 load" means a frame was produced, not that 24 pages are usable**. Renderer RSS (kB as printed, ×1000 here): median 112 MB (112,270 kB);
12 of 24 above 100 MB; three at or above 500 MB (an auction site 711 MB, a maps app 665 MB, a video site 2.23 GB). **So "lightweight" holds for
document pages (section 4) and fails for script-heavy pages.** The classifieds site's page height changed from 9,121 px (run 2) to 909 px (run 3); in run 3 it ran 8 scripts (2,522 kB, 2,450 ms) against 3 (24 kB) and its renderer held 380 MB against 23 MB; the files show the correlation, not the cause. Runs 1 and 2 are the "before" for the connectivity and script work; run 3 was taken before the module-referrer and attribute fixes
described in the working log, so claims after it (a code-hosting site 34 s → 8.5 s with 0 chunk 404s and 8 of 9 scripts; a weather site's jQuery 1.12
running) are (recorded; no saved result).

FIELD PREDICTS (probe and census): a from-scratch engine will pass what it implements and fail on the long tail of the platform; published
conformance suites for the language (test262, TC39) and the web platform (web-platform-tests) are the broad instruments, and a small probe
cannot predict a pass rate on them. The census predicts only that script-heavy sites cost far more memory than document pages.

## Orbit: a chrome drawn by the engine, and the engine work the design created

**The design as built** (design summary and vision page: `docs/appendix/part7/ch3-design/results/`; code `omni-ui/src/orbit.rs`, `omni-ui/src/web_app.rs`): the page fills the window; a floating glass bar holds the
core (three small rings, each turning at its own rhythm of 3 / 5 / 7 s on its own axis, moving only while a page loads or the bar moves), back,
forward, the site trit with the address, reload and reader view; a settings orb sits top-right. Settings: *Hide bar* (the bar folds left into
the core icon after 5 s unused; touching the icon springs it back), theme (dark / light / contrast), surfaces (glass / solid), motion
(fluid / still), page scripts; saved to a small tab-separated file. A tab rail appears with more than one tab; typing in the address lists
matching open tabs, bookmarks and pages seen (history persists as one row per address, ≤ 2,000 rows, atomic write). Failed loads are a designed
page (class from the network layer's message: bad address, no such host, not answering, certificate / TLS, invalid answer, other; plain title,
one sentence, what to try, the address, "Try again", the raw detail) and are not added to history. Motion is a spring integrated per tick
(no resident animation loop); panels fade on their own spring; the reader view is a column drawn once at full height and scrolled as pixels.

**Engine work the design asked for (the design drives the renderer).** The design document's eleven items: (1) `border-radius`; (2) `box-shadow` incl. inset and glow; (3) gradients; (4) `backdrop-filter`; (5) 2-D / 3-D transforms and `perspective`;
(6) transitions, `@keyframes` and cubic-bezier springs on a frame clock; (7) inline SVG stroke / `currentColor` / linecap; (8) the system UI face; (9) `inset`, `place-items`, `0fr → 1fr` grid rows, `color-mix()`, `text-overflow`, `::after`, `:focus-visible`;
(10) root background to the canvas; (11) a local-file view. Items 5 and 6 (compositor work) were not built (below). In the engine's paint module (`omni-render/src/paint.rs`): rounded boxes by signed-distance
coverage with analytic anti-aliasing (plain boxes keep the old zero-cost path); `box-shadow` outer and inset by a closed form (Gaussian
convolved with a rounded box, erf along one axis integrated along the other, with erfc from Abramowitz and Stegun 7.1.26, `paint.rs:125-135`); linear / radial / conic gradients with stops, smooth tiles kept
24-bit instead of 16-bit; `backdrop-filter: blur() saturate()` by drawing a tile with an apron, blurring what lies below (separable box
filter three times ≈ Gaussian, `paint.rs:616`) and clipping to the box; inline SVG strokes with `currentColor`; the system UI face, root background to the
canvas, `inset`, `place-items`, `color-mix()`, `text-overflow: ellipsis`. Performance passes after the owner's report that it was "quite
laggy": an overlay raster that re-draws only what the chrome covers, a cross-frame tile memo, a cached half- or quarter-resolution blur per glass
box, cached shadow masks, integer inner loops; and a bug where the page process read its viewport after the preload exchange, so every remote
page was laid out (and its scripts run) once at 64 px wide before the real size.

**Gate G8 (paint against Chrome).** Harness: a comparison script with five probe pages (radius, shadow, gradient, glass, icons; script and pages are not shipped, because no result was retained): per probe, our render (`omni-render page --png`) against headless Chrome's screenshot, mean absolute
channel difference (0–255) over an 800 × 450 frame. Registered bar: radius probe ≤ 2 % mean error (0.39 of 255 is 0.15 %), others "within tolerance"; a later hand-over note states a target "≤ 1 on every probe", which the glass probe misses (logged as font differences only). **Result: logged
as radius 0.39, gradient 0.08, shadow 0.59 / 0.75 / 0.76 (three logs), icons 0.12 / 0.13, glass 5.07 / 5.11 (the log attributes the glass error to
font differences only) (recorded; no saved result).** Binary and revision per log: the three logs name three successive engine revisions, which no shipped result file records. The author's development log names the second log's engine as `a51be17` (beside shadow 0.75, icons 0.13) and the third as `c87630d` (the revision of the third merge gate, section 12); the first log's revision is withheld. First log: shadow 0.59, icons 0.12, glass 5.07; second (`a51be17`): shadow 0.75, icons 0.13; third (`c87630d`): shadow 0.76, icons 0.13, glass 5.11. The shadow error rises with each later engine revision, which the logs do not comment on.

**Gate G9 (layout must not move).** Each paint step was gated by the layout merge gate (section 12): box agreement with Chrome unchanged,
0 lost. This is the part of the result that is retained (three gate runs).

**Gate G10 (responsiveness) (recorded; no saved result).** Logged: chrome click 160–700 ms before the passes (the cost was the overlay raster,
glass blur per tile, and a whole-window raster), 22–26 ms steady after; panel first open 75–85 ms; steady frame median 32 ms; page scroll
54–90 ms; reader scroll ≈ 50 ms; all at box load 9–13 on 8 threads. Measurement command named in the author's manual: `OMNI_UI_TRACE=1 OMR_PAINT_TRACE=1
omni-ui script web --script <file>`; its output was not kept. *Failure recorded:* the first live drive of the new chrome was reported as
laggy by its owner; the numbers above are the diagnosis, not a retained result.

**Open defects found by measuring, not fixed in this window** (the program-before-lockdown change is visible in `omni-render/src/pageproc.rs:165-166`): (a) on a near-black page background (#05070d) a few tile-shaped squares draw
darker than the rest — suspected 16-bit smooth-tile quantisation of dark colours; (b) pages that use the CSS `font:` shorthand draw in a serif face
because the engine switch that would fix them (`patch.font_family`) loses one box on one page in the layout gate (+11 / −1) and so stays off — the gate
refused it; (c) SVG `stroke-linecap: round` is not implemented; (d) the confined page process ran **without** the layout-repair program, so every
gated repair was off in the browser — the program file is now read before the file-system lockdown and honoured on request, but off by default
(on / off on 5 live pages changed mean pixel error by ±0.4 (recorded; no saved result)).
Motion variation: the pre-registration specified CSS transforms, transitions and `@keyframes` on a compositor; what was built instead is app-side
spring motion that re-renders the small chrome markup per tick. The compositor as specified is **not** built.

FIELD PREDICTS (G8): analytic coverage from a signed-distance field should match a reference rasteriser except at anti-aliasing and font
differences (signed-distance rounded boxes: Inigo Quilez, "Distance functions"; closed-form Gaussian-blurred rounded box shadows are published
as GPU techniques, e.g. Evan Wallace, "Fast Rounded Rectangle Shadows" — field kin, not claimed as the source used); three box passes approximate a
Gaussian (Wells, IEEE TPAMI 1986). Text is predicted to dominate the glass-probe error because it depends on font rendering, not on the
filter. FIELD PREDICTS (G10): frame time of a CPU raster of translucent layers scales with blurred area; caching per box should cut it by
the ratio of redrawn to total area.

## Ternary elements in the browser

- **Site trit (built).** Beside the address, a ring and a three-part panel: *connection* (+1 https with certificate checked, 0 plain http or an internal
  page, −1 the server answered HTTP ≥ 400), *cookies* (+1 kept for this site or none stored, 0 stored for this session only, −1 blocked), *third
  parties* (**constant +1 by construction**: the jar never stores or sends a cookie for another site — it is a statement of the policy, not a measurement).
- **Ternary cookie switch (built).** Block · Session · Keep per site: blocked = nothing stored and nothing sent; session = memory only; keep = persistent
  cookies survive a restart. Verified by script against the local route server (session → cookie present; blocked → absent; kept → present)
  (recorded; no saved result).
- **Designed, not built, not measured:** a tracker head (allow / ask / block as a trit per request, with agreement against a filter list as the
  gate), ternary selector matching in the browser (its probe on the engine is in Part 6), the 25-ring core's view inside the browser,
  and the whole-machine role of that core.

FIELD PREDICTS (designed items): learned or list-based request blockers are published practice (filter-list engines in content blockers); a
three-valued verdict adds an "ask" state without a published precedent we know of — treat as untested.

## Heavy script pages: a compact function store and a parse feed (YouTube as the test), and a negative result

Problem measured (census, run 3, `docs/appendix/part7/ch3-census/results/census-3.metrics.jsonl`): the video site's renderer holds 2.23 GB (RSS 2,226,784 kB; 41 scripts ran, 2 failed; 498 DOM
nodes — the page stayed a skeleton). The author's working log's probes attribute 1.9 GB to the parse tree of one 10.8 MB script, 4.1 % of 47,430 functions ever called,
and 67.3 % of tree nodes repeating an earlier identical subtree (recorded; no saved result).

Mechanism (enabling description; the compiler modules that implement it are not in the reviewed source tree, so only the description and the working log's numbers exist here): (1) the parser emits **hash-consed stored nodes** — each finished function becomes a content-addressed node
(content hash = its address; u32 ids) behind a 5-field placeholder {type, id, flags, parameter counts}; (2) the interpreter lowers a function **on its
first call**, not at parse time; (3) the broker, outside the sandbox, parses scripts ≥ 24 KB on a background thread (large stack) and writes a blob to
a disk cache keyed by the fast hash of the script bytes; the page process asks over frame `c` and receives *blob*, *wait* (still parsing) or
*parse it yourself*; (4) the cache file carries a **format version** (magic `OMJ2`, also in the file name); a reader refuses an unknown version. Parity
gates named in the working log: parser output identical to the old JSON form (`js-parse --parity`, 345 / 345), exact feed round trip (`--feedcheck`, 345 / 345), probe
106 / 106, connectivity 13 / 13 (recorded; no saved result). Logged effect: parse-time RSS 1.93 → 0.86 GB, page renderer 2.2 → 0.92 GB, 30.9 k functions made,
2.6 k lowered, 2.2 k called (recorded; no saved result).
**Failure registered:** a cache blob written by a newer build was read by an older pinned build and two scripts failed with no error naming the cache —
the cause of the version rule above.

**Negative result at the end of the window (2026-10-08 ~02:00).** The video site's music front end could not be made usable: the page's component
framework's boot was repaired step by step (template contents, accessor inheritance in a shadow-DOM polyfill, interface prototype chains,
custom-element reactions, attribute-change callbacks, `hasOwnProperty` on nodes), the shell, masthead and guide drew, and the page manager created its
browse component — but the grid never stamped, a replay then ran over 4 minutes and once crashed the renderer, and the owner stopped the work.
Not usable at the end of the window. An early finding: sending a product token after a Chrome-compatible user-agent string gets the
site's "browser deprecated" page while the bare Chrome-compatible string gets the real application, so the engine was changed to send a plain Chrome-compatible string (logged; no result file shows whether the final pinned build carries it, and the author's manual's network paragraph still lists the earlier product string).

FIELD PREDICTS: engines parse lazily and pre-parse inner functions (V8, "Blazingly fast parsing, part 2: lazy parsing", v8.dev 2019); hash-consing
shares equal subtrees (Ershov 1958; Filliâtre and Conchon 2006); most functions in a large bundle are never called, so lowering on first call
should skip most of the work and most of the memory.

## The layout-repair core fired inside the browser's layout pass (cross-reference)

The engine's 25-ring layout-repair core (the doctor's processor; its own section of this Part) was rendered as machine code (1,209 bytes, 269
instructions, 25 nine-instruction ring blocks with the moduli as immediates) and hooked after every layout run so that each layout carries its own
fix queue; the browser's engine build mounts it (`omni-render/src/jit/t25.rs`, `omni-render/src/jit/ir.rs`). Logged, step by step, in the author's working log: bit-exact against the Python golden
on 49 pages (28,040 of 28,040 twists), 1.9 ns per box for the kernel, 0.74–1.05 % of a layout pass when fired live (partial). Finding in
this section's scope: in the browser the core was off until the layout-repair program was read before the lockdown (section 8, item d).
*Designed, not measured:* the owner's direction that the browser aims at mathematically exact page geometry rather than Chrome parity (the
doctor's gate today still measures agreement with Chrome), and that this core be the machine-wide processor.

## The merge gate and the engine-pin rule

Procedure (written 2026-10-07 after failures recorded in the author's procedure log (not shipped): a build script's error filter hid a failed build twice so an old binary was
measured and installed; cargo kept the old binary after a re-pin because archived files keep old modification times; and a branch merge that was
not re-gated, section 4):
gate the exact commit with `harness/part7/ch3-merge-gate/merge-gate.sh`: (1) the layout baseline is unchanged: `core corpus --program <program> --max 0`
→ agreement count on 37 replay + 12 holdout pages (49 pages), compared old binary vs new; (2) `--check-compiled`: interpreter = compiled = bitmask =
stencil-JIT knob lookups, 0 different; (3) `--binary-gate`: against a snapshot taken from the old binary, 0 boxes lost and gained > 0 (`omni-render/src/doctor.rs`, `binary_gate`); (4) the JS probe 106 / 106;
(5) connectivity 13 / 13. A gate whose run exits 0 is not a pass: the script does not propagate the binary gate's exit status (the engine exits 1 when gained is 0). Then fast-forward main to exactly the gated commit and release the pin: pin the app's engine to that commit, rebuild, and
confirm `omni-ui --engine-rev` equals the pinned revision (the build re-runs on every new pin).

**Gate G11 (three runs).** Harness `harness/part7/ch3-merge-gate/merge-gate.sh` (run under the tritwatch runner; the runner's history records three runs, each exit 0, 306 / 238 / 72 s; exit 0
is the script's own exit, not a pass verdict). Results: `docs/appendix/part7/ch3-merge-gate/results/run-1/`, `run-2/`, `run-3/` (each: `base-old.txt`,
`base-new.txt`, `check-compiled.txt`, `binary-gate.json`, `binary-gate.err`, `conn.txt`, `agree-old.json`).

| Run (local time, 2026-10-07) | Baseline old = new | check-compiled | binary-gate | conn.sh | Engine revision gated (named in the author's development log; in no shipped result file) |
|---|---|---|---|---|---|
| 10:31 | replay 20,973 / holdout 3,059 of 28,040 = unchanged | 2,866,688 identical, 0 different (44 keys, 49 pages) | lost 0 / 0, gained 0 / 0 → prints FAIL | 13 / 13 | revision withheld (merge of main into the browser branch; the working log names this gate folder; the old binary is the main build named in the script's own comment) |
| 12:37 | same | same | same | 13 / 13 | `a51be17` (the development log names it with this gate's counts, 20,973 / 3,059, JS 106 / 106, conn 13 / 13; folder matched by runner start time 12:37:54; recorded in no result file) |
| 13:59 | same | same | same | 13 / 13 | `c87630d` (the development log names it as "merge gate" with these counts; folder matched by runner start time 13:59:45; recorded in no result file) |

Reading the table honestly: (a) the three runs are identical because the gate tests *layout* (a refactor or paint feature must not move a box), not
paint, scripts or network; (b) the binary gate prints **FAIL** in all three because its rule requires gained > 0, which a pure merge cannot satisfy; the
working log calls this expected, and the same line was printed on main; (c) the binary gate's own replay count (20,945) differs from the baseline's (20,973) by
28 because the two count different things: the snapshot is written with "stable" node ids (real-node index, pseudo-elements excluded; `omni-render/src/doctor.rs`, `binary_gate`), the baseline counts arena ids; the snapshot holds 24,004 agreeing ids (recomputed from `run-1/agree-old.json`; 20,945 + 3,059), the baseline 24,032. The same 20,945 appears in the engine's
earlier gate logs (`docs/appendix/part7/ch3-merge-gate/results/earlier-gate/bgate-exact.log`), so it is a standing counting difference, not a regression; that the 28 are pseudo-element boxes is the source's rule, not shown box by box. The three `agree-old.json` files are byte-identical (same sha256), i.e. the old binary was the same main build each time; (d) the JS probe line (106 / 106) is printed to the terminal by the script and is **not** stored in these folders
(recorded; no saved result); (e) no result file names the binary or its revision — the script names the two binary
paths, and the revisions `a51be17` (run 2) and `c87630d` (run 3) come from the author's development log; which run each belongs to is matched with the runner's start times (`docs/appendix/part7/ch3-merge-gate/results/runs.summary.json`: start time, 306 / 238 / 72 s, exit 0 each); the runner's job logs and reproduction snapshots are not shipped; (f) the baseline compares against Chrome (box x, y, width, height each within max(2 px, 5 %)) on 49 frozen pages —
85.7 % of 28,040 boxes (24,032) agree (24,032 also sums from the per-page `agree` column of the base rows in `docs/appendix/part7/ch3-layout-core/results/t25fire-e1.marks.jsonl`).

FIELD PREDICTS: differential testing of a new build against the old one on a fixed corpus catches regressions that unit tests miss
(McKeeman, "Differential Testing for Software", Digital Technical Journal 1998); a gate that cannot show a gain on a pure merge is expected to
read as "no change", not as pass.

## Open / unmeasured (designed only)

- **Designed, not built:** plug-in surface (manifest, content scripts in the page process, request rules, per-site enable, sandboxed); developer
  tools (inspector with box + exactness view, console, network log; F12); tracker head; ternary selector matching and the 25-ring core view inside the
  browser; text selection and copy of page text (copy today = link or page address); file inputs; iframes (drawn as a 300 × 150 box); video, audio,
  encrypted media; AVIF; a search-engine choice and "find that page" ranking by our retrieval daemon (address suggestions today use open tabs, bookmarks
  and history only); install polish (default-browser entry, first run, update path).
- **Designed as a target position, not measured:** Android port (cross-compile of the engine, aarch64 emitter beside the x86 one, touch and IME, a
  platform accessibility adapter, system fonts, isolated-process sandbox). Its comparison table (size "est. 20–40 MB", independent engine, own interpreter,
  "JS probe 106/106; YouTube does not draw yet") is an estimate (recorded; no saved result). Field fact: iOS requires the system web engine for browsers outside the EU
  (Apple App Store Review Guideline 2.5.6; alternative engines allowed in the EU since iOS 17.4).
- **GPU compositor:** a hand-over note names a GPU path (WebGPU / Vulkan lineage) for remaining chrome paint cost (box SDF ≈ 10–30 ms); not built here.
- **Unrun human checks:** the owner using it as the daily browser for a day; a screen-reader session; any usability test.
- **Unmeasured claims in the logs:** every figure tagged unsupported above; the page-process lockdown 5/5; fold timing (touch → 640 px bar; 3 s open;
  6 s folded); error-page classes by script (unknown host, refused port, `ftp://`); history persistence across two runs; WebSocket echo (`ws_echo.py`:
  open, message, echo, close 1000); binary WebSocket send (open); GC for script object cycles (renderer RSS 230–270 MB on two large sites, no collector);
  the code-hosting site's chunk-loader path resolution before the module fix; one site's jQuery 1.12 (reported working later).
- **Source not available:** the engine's closure compiler and function-store modules (section 10) are not in the reviewed source tree; omni-ui has no component PROVENANCE file.
- **Not in this section:** the NeuralOS applications on the same widget toolkit (Find, Reader, Calendar, Mail, Notes, Library; 2026-10-04) — their
  result files hold personal data paths and belong to a separate disclosure; the engine's JavaScript compiler and the test suites
  (own sections).

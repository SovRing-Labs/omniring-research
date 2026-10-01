# The triangle memory: triangulation, triage, truncation

| | |
|---|---|
| **Date** | 2026-10-01 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Written with AI assistance (Claude) from the author's conversations of 30 September – 1 October 2026 (unpublished). The author reviews it before publication. |
| **Type** | essay — every number is cited to the omni-ring Technical Disclosure Part 2 (`P2 §n`); anything not measured is marked **Speculative** |

## In one paragraph

The ring memory made one relationship — "how similar are these two?" — cheap enough to do millions of times. The
author's next step was to ask for a primitive one rung higher: not a point but a closed relationship among three
things, a fact. Three words came to the author for what it should do — **triangulation, triage, truncation** — and three for
how it should live — **movement, resonance, harmony**. Each word became a mechanism and a test. Most held. Some did
not, and the ones that did not told us where the triangle belongs in the larger system.

## The idea, in the author's words and ours

*Inference closes two triangles.* If A relates to B and B relates to C, the third side follows. *Information on
vectors is orthogonal*, so triangles from different memories can share space without colliding. Could one triangle
connect any three points across many rings and make inference instant? The answer we built: a fact (subject,
relation, object) is one bound vector; it is filed under each of its three edges; any two corners recover the third
with one clean-up (P2 §6.1).

## How we got here

The triangle arrived out of a review. Asked to look back over a day of geometry, the author answered with a creation
story — point, line, triangle, square, cube, four dimensions — and asked where we stood. The answer was "at the door
of four dimensions, with the cube not yet solid." The author's reply set the direction: *once we step into the
fourth dimension we need an entirely new kind of substrate … another omniring-class tool, though it may be a triangle
or a square, following that lineage until our primitives can stand on their own.*

The first proposal from our side overreached. It said chained inference on the torus is just addition — if relations
are phase shifts, A + r1 + r2 lands exactly on C. That is only true for relations that behave like translations. It
was corrected in writing before any test ran, and both versions were measured: hop-by-hop with clean-up was exact;
pure addition failed 0–5% of the time, every failure a pair of paths that commute. A search of the field showed the
same limit in published work on torus knowledge-graph embeddings, which also told us what was and was not new here.

The three words came next, unprompted: *triangulation, triage, truncation.* Each was turned into a mechanism with a
bar written before the code: three edge indexes and a second-path check; a trit with thresholds fitted on one half of
the data and reported on the other; decay with a window set from measured capacity. The capacity test found the
ceiling at 256 facts per bucket. The chaining test found a bug of our own along the way — the logic engine re-derived
everything from scratch on each new fact, so loading 3,000 facts took far too long; the harness was changed to load
in bulk (recorded as a harness change) — and it also produced a speed comparison that later had to be retracted
(essay 11).

## Three words, three mechanisms

**Triangulation — finding and confirming.** Surveyors locate a point from two known ones, and trust it when a second
sighting agrees. The memory does both: two known corners give the third; then a second path (the other edge) must
return the corner we started from. Measured: up to 256 facts per bucket recovered at 99% or better; 100,000 facts
recovered almost perfectly (P2 §8).

**Triage — deciding what to trust.** Every answer gets a trit: +1 commit, 0 escalate to an exact system, −1
contradiction. With moderately full buckets: committed answers 100% correct, facts never stored never committed,
contradictions all caught; with full buckets (256): committed answers 99.3% correct, still none invented (P2 §8).
This is the same "I don't know" that runs through the whole corpus (essay 06).

**Truncation — staying under capacity.** A superposition holds only so much. Decay lets old, unreinforced facts fade:
the most recent facts were recovered 100% with decay and 14% without (P2 §8).

## Three ways to live

**Movement.** A polygon of facts can be moved in time — every fact in it — by one operation, because binding
distributes over bundling. On real agent sessions, re-timing and re-roling lost nothing (P2 §6.4, §8).

**Resonance.** Chains of inference proceed hop by hop, each hop cleaned up against the codebook so noise never
accumulates: identical to an exact logic engine over 2–10 hops (P2 §6.3). Pure "phase arithmetic" chaining failed
exactly where two paths commute — a limit known from earlier work on the torus (TorusE), now seen first-hand.

**Harmony.** Several observations of one fact either agree or don't; one number (how cleanly the best answer stands
above the next) separated agreement from dissent perfectly (P2 §8).

## Polygons and nesting

The author's next image: *every triangle becomes a building triangle for a polygon of information or ideas, one solid,
manageable, transformable polygon.* We built polygons from 300 of the fleet's own agent sessions (each step a triangle:
position, tool, argument). They held up to 256 steps; a polygon could itself become one corner of a higher triangle
and be found and opened again; two levels of nesting reached 262,144 facts in three lookups at 99.95% (P2 §8).

The compression the author expected turned out to be a different kind: not fewer bytes (a ternary polygon costs about
as much as the raw text) but **three items handled as one** — one object to query, verify, move and nest (P2 §9).

### The twists in the middle

Two results surprised us. The pyramid, which had given 4.9 times on single marks, failed completely on full buckets:
320 dimensions cannot see one fact through 255 others superposed on it. Shapes do not transfer automatically between
levels of the ladder. And the polygon test on real sessions was taking far longer than it should; the author noticed
one processor core pinned while the others idled. The harness was rebuilding a 3,000-row table for every question.
Fixed, it ran 19 times faster with identical results.

Then the author asked for a "sifter core" in each bucket — *a torus geometric code that constantly fires, sifting
naturally.* The version that does real work is error-driven: reinforce members whose margin is thin, push away what
confuses them. It did raise capacity. Its safety bar failed, and part of that failure was ours (the bar came from
smaller buckets). The diagnostic that followed was more important than the bar: even without the core, a full bucket
cannot tell a stored fact from an absent one. A second test confirmed it from the other side — triage stayed safe at
256 facts per bucket and collapsed at 384 with or without the core. A third tried to make the ternary form better by
putting it inside the refinement loop; it gained half a point. Three failures in a row, all pointing the same way:
truth has to live somewhere exact.

## Where it did not hold

* **The sifter core.** The author asked whether each bucket could have its own continuously firing core. It raised
  capacity 1.5–2x, but full buckets then could no longer tell a stored fact from an absent one (P2 §9). Truth has to
  live somewhere exact.
* **"Three as one" on the processor.** Superposing three queries into one pass was up to 2.5x faster but changed too
  many answers (P2 §9).
* **Speed on exact chains.** An indexed database answers exact multi-hop questions about 250 times faster. That
  result redirected the design: the triangle is not a faster table; it is what a table cannot be (essay 10).

## What the triangle is for

Verification by a second path, a trit on every answer, coherence as a number, transforms in one step, and nesting —
on top of exact rows. That is a primitive (essay 07): small, specified, portable, and built from the ring below it.

# Square, line, circle, triangle: a substrate

| | |
|---|---|
| **Date** | 2026-10-01 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Written with AI assistance (Claude) from the author's conversations of 1 October 2026 (unpublished). The author reviews it before publication. |
| **Type** | essay — numbers cited to the omni-ring Technical Disclosure Part 2 (`P2 §n`); designs not yet measured are marked **Speculative** |

## In one paragraph

The author's planned next development was a full-text index, an embedding model and an SQL "matrix" around the ring
memory. The author's observation: *an SQL table is essentially a square in this 2-D.* Tested, it completed the picture the
triangle experiments had pointed to. Exact truth belongs in rows; bulk inference belongs in matrix products; words
enter through a full-text index; meaning enters through a ring; and the triangle supplies verification, coherence,
transforms and nesting. No single tool covered every kind of question; the combination did.

## How we got here

The road to the table ran through three failed attempts at the author's next idea: *manage and transform three items
as though it were one — on the conveyor belt, so each lane per clock cycle takes one thing but processes it as though
it were three.* The physics allows that in only three ways: fewer bytes per item, fewer passes, or more items per
register. One test was written for each.

* **More items per register.** Phases are four bits; the triangle code stored each in eight bytes. Packing sixteen
  phases into one 64-bit word and adding them without carries was correct but *slower* in the array language (each
  step made a temporary array). In C, the packed version was 109 times faster than the original — a real gain, just
  not the one predicted.
* **Fewer bytes.** Running the triangle clean-up through the ring's packed integer kernel gave the same answers and was
  slower than a plain floating-point matrix multiply.
* **Fewer passes.** Superposing three questions into one search pass was up to 2.5 times faster and changed up to 15%
  of answers. Killed.

The calibration that followed was the turning point. Asked for a fair speed comparison, an indexed SQLite database
answered exact multi-hop questions about 250 times faster than the vector memory, and a plain hash table faster
still. The author's response turned the result into a design: *we can make a matrix out of an SQL table, right? My
next omniring development was going to be the full-text, embedding and SQL matrix. An SQL table is essentially a
square in this 2-D.* The fleet already had a design for joining full-text search and vector search in one database
query, written weeks earlier; this gave it a place in the geometry.

Three laptop tests closed the loop: matrix closure (23–102 times faster than bulk SQL joins, exact), the perception
cache (99.9% of live texts were repeats), and the routed substrate below.

## Each shape, its job

| Shape | Tool | Job | Measured |
|---|---|---|---|
| Square | Relational table (SQLite) | Exact truth; exact lookups | ~250x faster than vector memory on exact chains (P2 §8) |
| Cube | Sparse matrix products | Every chain for every entity at once | Exact; 23–102x faster than bulk SQL joins (P2 §8) |
| Line | Full-text index (FTS5, BM25) | Words to rows | 90% on reordered-word questions (P2 §8.1) |
| Circle | Ring pen (trigram or embedding) | Noisy or partial surfaces to atoms | 58% on misspelled questions where table and full-text scored 0% (P2 §8.1) |
| Triangle | Omnitri | Verify, cohere, transform, nest | P2 §6, essay 09 |

## The routed test

On 300 real agent sessions (20,761 rows), questions came in three kinds: exact, reworded and misspelled. Each tool
alone failed one kind badly. Routed through all of them — table first, then full-text, then ring with table
confirmation — the system answered 84% overall against 61% for the best single tool, and was never worse than the
best tool on any kind. It missed its latency target (the full-text query was untuned), and that is recorded as a
failure (P2 §8.1).

## Perception, cached

The most practical finding was the simplest. The fleet's live event stream: 97,385 texts, 86 distinct. An exact
cache in front of the embedding model removes 99.9% of perception work; near-duplicates are not safe to reuse
(P2 §8). The author's notebook had said it: *determinism offloads reasoning* (essay 07).

## A ternary pen of our own (Speculative)

The memory already reads through a ternary embedding model released openly by Microsoft (BitNet-embedding-270M). On
the project's own retrieval test it trailed the larger full-precision model it would replace (recall 0.90 vs 0.95).
Three designs are disclosed and not yet run (P2 §10): train the ternary model's own weights on local text with the
larger model as teacher (days, a few GPU hours); add a "triangle head" so text maps straight to triangles; and a
memory-attention layer, frozen per version so stored marks stay comparable. The constraint behind all three: the pen
must stay stable, or every stored mark goes stale.

### How the ternary pen question went

The author asked how long it would take to port the full-precision embedding model to ternary weights — not an adapter
on top, but the model itself. Grounding the question turned up something we already had: the ring classifiers had
been reading through an openly released ternary embedding model all along, and a patch made earlier that week (the
model was computing a 262,000-word output layer on every token and throwing it away) had made it 2.35 times faster.
So the question became narrower: close a 5-point recall gap on our own data. Training its own ternary weights on
local text pairs, with the larger model as teacher, is days of work and a few GPU hours; porting the larger model's
architecture to ternary is two weeks, most of it in the inference code. The first is planned; the second waits on
its result. The author then asked whether the ring and the triangle could be spliced into the transformer itself.
Of five places to splice, two were rejected (replacing attention, quantising activations to phases), one deferred
(memory attention, only if frozen per version), and two kept (a cache in front, a triangle head on top) — all under
one rule: the pen must not drift.

## What the substrate is

Primitives that share a representation compose without glue (essay 07). Here the shared representation is the
SuperSeed phase vector plus the relational row: every triangle has a row; every row can have a triangle. That is the
ground the next round of tools will be built on.

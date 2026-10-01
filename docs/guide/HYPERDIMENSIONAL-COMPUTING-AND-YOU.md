# Hyperdimensional Computing and You

*A guide to where the SovRing tools sit in hyperdimensional computing, what they borrow, what they add, and how to start
using them well.*

| | |
|---|---|
| **Date** | 2026-10-01 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 |
| **Covers** | vsa-core 0.1.0, omni-ring 0.1.1 (Technical Disclosures Part 1 and Part 2), omnitool 0.1.0 |
| **Status of claims** | Measured results are cited to the disclosures (`P1 §n`, `P2 §n`) or a repo's `DOSSIER.md`. Anything else is marked **Design** (specified, not yet measured) or **Speculative**. |

---

## 1. Hyperdimensional computing in plain words

Ordinary programs store a fact in one place: a row, a field, a variable. **Hyperdimensional computing** (HDC), also
called **vector-symbolic architectures** (VSA), stores everything — symbols, records, sequences, even programs — as
very long vectors, typically thousands of dimensions. Three properties make that useful:

* **Random long vectors are almost always unrelated.** Two random 5,000-dimension vectors are nearly perpendicular,
  so you can hand out millions of distinct "symbols" without collisions.
* **A handful of operations build structure.**
  * **Bind** (⊗) combines two vectors into a third that resembles neither — "role = filler", "key → value".
    It can be undone exactly (unbind).
  * **Bundle** (+) superposes several vectors into one that resembles each of them — a set, a bag, a memory slot.
  * **Permute** (ρ) shuffles dimensions to mark order or position.
* **Clean-up recovers the exact symbol.** A noisy result (after unbinding from a crowded bundle) is compared against a
  codebook of known symbols; the nearest one is the answer. If nothing is near enough, the honest answer is "I don't
  know".

That is the whole toolkit. A record such as *(colour: red, shape: ball)* becomes `colour⊗red + shape⊗ball`; asking
"what colour?" is `unbind(record, colour)` followed by clean-up, which returns `red`.

### Where the field came from

| Idea | Who | What it gave everyone |
|---|---|---|
| Hyperdimensional computing; sparse distributed memory | Pentti Kanerva | The case that high-dimensional random vectors are a natural substrate for cognition; the "dollar of Mexico" analogy |
| Holographic reduced representations; fractional power encoding | Tony Plate | Binding by circular convolution, bundling, clean-up, and continuous values as fractional powers |
| Resonator networks | Frady, Kent, Olshausen, Sommer | Iterative factorisation of a bound vector into its unknown factors |
| Residue hyperdimensional computing | Kymn and colleagues | Coprime modular codes in vectors, combined by the Chinese Remainder Theorem |
| Grid-cell modular codes | Fiete, Burak, Brookings | The biological picture of several periodic codes at once |
| Knowledge-graph embeddings on the torus / as rotations | Ebisu & Ichise (TorusE); Sun et al. (RotatE) | Relations as translations or rotations in phase space (trained by gradient) |
| Retraining HDC prototypes | Imani and colleagues | Error-driven refinement of bundles |
| Ternary networks (BitNet b1.58 and successors) | Microsoft Research and others | Weights in {−1, 0, +1} that run on ordinary CPUs |

Full citations: `PROVENANCE.md` in each repo; thanks: `TECHNICAL-DISCLOSURE-PART-2.md` §13.

## 2. Where our work sits

We did not invent hyperdimensional computing. Our contribution is engineering and measurement: making these ideas
**exact, portable, verifiable and useful on computers people already own** — a 2019 laptop CPU, an integrated GPU,
second-hand office desktops. Each item below is marked **new** (we found no prior description), **adapted** (known
idea, our variant), or **borrowed** (used as published).

| Our component | Status | What it is |
|---|---|---|
| Two-faced 2,560-byte slot (10,240 ternary dims ↔ 5,120 sixteen-level phases) with a total transcode | adapted | One memory block readable as ternary bitplanes or as phases (P1 §2) |
| Shared-memory blackboard: seqlock single-writer bus, slot registry, prefix summaries | adapted | Many agents read one memory without locks (vsa-core) |
| Sealed trust result (convergence class + barycenter flag + scores) | new | Every retrieval says how much to trust it (vsa-core §3) |
| Coprime rings + a redundant **17 check ring**; cue-driven soft resonator that abstains | adapted (residue HDC + redundant residue codes) | Detects 100% of single-ring slips (P1 §3–4) |
| Peeling, diamond facets with checksum centre, decaying mark store | adapted | Reading crowded slots; structured records; recency (P1 §6–9) |
| **SuperSeed**: integer-only spec for codewords, projections, encoding, scores; golden-hash conformance | new | The same bytes on every language and chip (P2 §2) |
| Tie-inclusive top-k rule | new (as a spec rule) | Removes a hidden bias from duplicate marks (P2 §2) |
| Geometry of the sift: cubes, pyramids, cluster spheres, lattice packings, golden-ratio frequencies | adapted (tiling, image pyramids, IVF, Conway–Sloane, Weyl) | The same exact answers ~12x faster (P2 §4) |
| Programs as vectors (position-bound instructions, integer unbind) | adapted | 1,024 steps exact in 20 KB (P2 §4.7) |
| Resident integrated-GPU sift engine + measured routing table | adapted | GPU helps only beside a busy CPU (P2 §5) |
| **Triangle memory (omnitri)**: three edge indexes, second-path confirmation, triage trit, decay, harmony, polygons, one-operation transforms, nesting | new as a combination (relatives: TorusE/RotatE, which are trained) | Untrained, integer, online fact memory with verification (P2 §6) |
| Substrate: table for truth, matrix closure, full-text, ring pen, triangle layer | new as a combination | Each tool doing the job it measured best at (P2 §7) |
| Deterministic agent-tool guard with honest classifier fallback | new (omnitool) | Batched agent tool calls repaired, validated and guarded (omnitool §3–7) |

What we deliberately do **not** claim: that HDC beats indexes on exact lookup (it does not — P2 §8), that superposition
is free (capacity is finite and measured), or that geometry makes arithmetic faster (gains come from reusing bytes
and skipping work — P2 §4.8).

## 3. Concepts we used, and where

| Concept | Source | Our component | Measured result |
|---|---|---|---|
| Binding / unbinding on phases | Plate; Kanerva | every repo | Torus binding recovery 1.000 vs 0.018 for a paraboloid (P2 §4.4) |
| Bundling with clean-up | Plate | omni-ring slots, triangle buckets | ≤ 256 triangles per bucket at ≥ 99% (P2 §8) |
| Residue codes + CRT | Kymn et al. | coprime rings | 1,365 addresses; 100% single-slip detection (P1 §12) |
| Resonator settling | Frady et al. | cued resonator | Cue is mandatory; ≈ 12 marks/slot by resonance; ≤ 192 by exhaustive sift (P1 §12) |
| Explaining away | classical | peeling | 16.65 true marks per crowded slot, 0 fakes (P1 §12) |
| Fractional power encoding | Plate; Frady | dials, positions | Golden-ratio frequencies: 0% aliasing failures at range 100 (P2 §4.6) |
| Ternary projection | BitNet; random projections | SuperSeed encode | Portable to Python / C / C++ / GLSL bit-for-bit (P2 §2) |
| Cache tiling; coarse-to-fine | HPC; Burt & Adelson | sift kernels | 2.1–2.6x; 4.9x (P2 §4.1–4.2) |
| Inverted-file indexes | Jégou et al. | spheres | Killed at < 9k marks per head (P2 §4.3) |
| Lattice quantisers | Conway & Sloane | lattice ladder | E8 > D4 > A2 > Z for reconstruction; retrieval ~flat (P2 §4.5) |
| Knowledge on the torus | TorusE, RotatE | triangle memory | Chaining exact by hop + clean-up; commutative limit seen (P2 §6.3) |
| Prototype retraining | Imani et al. | sifter core | 1.5–2x capacity; unsafe at full fill (P2 §9) |
| Truth maintenance; soft unification | Doyle; Rocktäschel & Riedel | logic spine | (engine; in the research log) |
| BM25 / FTS5; SimHash | Robertson & Spärck Jones; Charikar | substrate; perception cache | Routed 0.844 vs 0.612 best single tool (P2 §8.1) |

## 4. The tools and how they fit

```
          agents, apps, scripts
                  │  (batched JSON tool calls)
            ┌─────▼─────┐
            │ omnitool  │  repair → validate → guard → execute        "the hands"
            └─────┬─────┘
                  │  marks, cues, telemetry
            ┌─────▼─────┐
            │ omni-ring │  rings, check ring, resonator, sift,        "the memory"
            │           │  heads, triangles, polygons
            └─────┬─────┘
                  │  2,560-byte slots
            ┌─────▼─────┐
            │ vsa-core  │  shared-memory bus, trust result,           "the nervous bus"
            └───────────┘  bundling, phase kernel
```

* **vsa-core** is the bus: a block of shared memory where many processes read and write fixed-size vectors safely.
  Start here if you want several programs to share one memory.
* **omni-ring** is the memory: it writes marks into slots and reads them back by cue, resonance or exact sift, with a
  check ring and abstention. Part 2 adds the portable spec, fast kernels and the triangle memory (code arriving in
  weekly updates).
* **omnitool** is the hands: it lets language-model agents send batches of tool calls that are repaired, validated
  and guarded before anything runs. It does not require the other two.

## 5. Getting started

Each repo's README has install and test commands; the shortest path through all three:

1. **Clone and test.** `vsa-core`: `make test`. `omni-ring`: `./build_kernel.sh && python3 -m pytest -q`.
   `omnitool`: `make test`. A green suite on your machine is the first proof the kernels match your CPU.
2. **Write your first mark** (omni-ring): encode a coordinate on the coprime rings, store it in a slot, read it back
   with one ring clamped as a cue. Then corrupt one ring and watch the check ring refuse the answer.
3. **Read a crowded slot**: store a dozen marks, read with a cue, then with peeling, then with the exhaustive sift —
   and compare against the capacity table in P1 §12.
4. **Build a classifier that can abstain** (**Design** in the public code until the Part 2 modules ship): embed your
   labelled texts with one embedding model, encode them as marks, read new texts by top-k vote, and use the margin to
   abstain. P2 §3 specifies it fully.
5. **Store facts as triangles** (**Design** in the public code): bind (subject, relation, object), file each triangle
   under its three edges, and keep the rows themselves in SQLite. P2 §6–7.
6. **Give your agents hands** (omnitool): point an MCP-capable agent at the omnitool server, send a batch with
   `--validate-only` first, and read the guard's verdicts before running for real.

## 6. Best uses

| Use | Why HDC fits | Practice |
|---|---|---|
| Classifiers that can say "I don't know" | Votes over marks give a margin; abstain below it | Calibrate the margin on held-out data (P2 §3) |
| Verifiable recall | Check ring and second-path confirmation catch corrupted or unsupported answers | Treat abstention as a feature, not a failure |
| Agent memory and coordination | A shared bus of fixed-size vectors; marks as evidence between agents | One writer per slot; readers retry on a changed counter (vsa-core §2) |
| Noisy or partial lookups | A misspelled or reworded cue still lands near the right atom | Pair with exact rows for confirmation (P2 §8.1) |
| Structured facts and their coherence | Triangles, harmony, contradictions as a trit | Keep buckets at or below the measured capacity |
| Moving or re-labelling whole groups | Binding distributes over bundling: one operation moves every member | Re-time and re-role measured lossless (P2 §8) |
| Deduplication and perception caching | Repeated inputs are common in machine-generated streams | Exact-hash cache first; near-duplicate reuse only if measured safe (P2 §8) |
| Small hardware | Integer kernels, 4-bit packing, no GPU needed | Run the tests; an SSE kernel for pre-AVX2 CPUs ships with the Part 2 code |

## 7. Integrations

* **SQLite (+ FTS5).** Keep truth in rows; let the ring index meaning and the triangle verify. Exact multi-hop
  questions go to indexed joins; bulk closure to sparse matrix products (P2 §7–8).
* **Embedding models.** Any embedder can be the "pen" that turns text into vectors before SuperSeed encoding. Use
  **one pen per ring**: marks from different models are not comparable. Ternary embedders (BitNet family) run well on
  CPUs.
* **Language-model agents.** omnitool exposes an MCP server; the ring heads can sit in front of a model as a cheap
  first answer with abstention, escalating only what they cannot answer.
* **Multiple machines.** Each machine holds a shard; a cue is broadcast; only answers that pass the check ring may win
  (P1 §11). **Speculative** at scale until measured.
* **Integrated GPUs.** Use them for bulk sifting beside a CPU that is busy with embedding; keep them out of the
  request path on shared-power laptops (P2 §5).

## 8. Practices that kept us honest

1. **Pre-register.** Write the pass and kill bars before running. Publish the kills.
2. **Search the field first.** Most good ideas have relatives; cite them and say what differs.
3. **Truth in rows, meaning in rings, verification in triangles.**
4. **One pen per ring; never let the pen drift.** Re-embedding with a changed model silently invalidates every mark.
5. **Measure capacity on your data.** Every superposition has a ceiling; stay below it.
6. **Cache perception.** Machine-generated text repeats; do not embed it twice.
7. **Prefer exact integer specs.** If two machines disagree on a score, you have a bug, not noise.
8. **Abstain.** A trit with a zero is worth more than a confident guess.

## 9. When not to use HDC

* **Exact lookups by key**: use an index or hash table — hundreds of times faster (P2 §8).
* **Dense matrix arithmetic**: use BLAS on the CPU (or a real GPU).
* **Unbounded superposition**: past the measured capacity, recall and safety fall off a cliff.
* **No cue at all**: unguided decoding of a crowded slot is seed-dependent; give the memory something to start from
  (P1 §12).

## 10. Where to go next

* Technical disclosures: `omni-ring/TECHNICAL-DISCLOSURE.md` (Part 1), `TECHNICAL-DISCLOSURE-PART-2.md`;
  `vsa-core/TECHNICAL-DISCLOSURE.md`; `omnitool/TECHNICAL-DISCLOSURE.md`.
* Each repo's `DOSSIER.md`: history, specification, metrics, tests and limits.
* This corpus: measured documents `docs/01–23`, essays `docs/essays/01–11`.

# From a point to a tesseract: the geometry ladder

| | |
|---|---|
| **Date** | 2026-10-01 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Written with AI assistance (Claude) from the author's conversations of 30 September – 1 October 2026 (unpublished). The author reviews it before publication. |
| **Type** | essay — every number is cited to the omni-ring Technical Disclosure Part 2 (`P2 §n`); anything not measured is marked **Speculative** |

## In one paragraph

Over two days the author asked one question in many forms: if this memory is geometry, which shapes make it faster,
denser or smarter? Each shape became a pre-registered experiment on a 2019 laptop. Some shapes paid (cubes, pyramids,
the torus itself, golden-ratio frequencies); some did not at this scale (spheres, dense lattices for retrieval); and
the honest summary is that every gain came from reusing fetched bytes or skipping work, never from faster arithmetic.
The same answers now arrive about 12 times faster than they did on the morning of 30 September.

## The ladder

The author described it as a creation story: *everything starts with a point; it connects to another point and makes
a line; a third point makes the first triangle; then a square; then it uses everything it already has to become the
same in three dimensions, then in four.* That is also how mathematicians build two families of shapes: the
**cube family** (copy what you have and join each point to its copy: point, line, square, cube, tesseract) and the
**triangle family** (add one point joined to everything: triangle, tetrahedron, 4-simplex). The memory climbed both.

| Rung | In the memory | What it does | Result |
|---|---|---|---|
| Point on a circle | One dimension of a mark: a phase on a 16-position ring; a mark is a point on a torus | Stores compactly; binds exactly | Binding recovery 1.000 on the torus vs 0.018 on a flat paraboloid (P2 §4.4) |
| Line | One comparison (the sift) | Similarity between two marks | Bit-identical across Python, C, C++, GPU (P2 §2) |
| Triangle | Query, nearest marks, label — and later a stored fact | Votes; facts | Tie fix: d4 0.745 → 0.806 (P2 §2) |
| Square | A tile: 4 queries share each fetched chunk | Reuses bytes | 2.1–2.6x (P2 §4.1) |
| Cube / pyramid | Tiles stacked into coarse-to-fine levels | Skips work | 4.9x; ~12x vs the morning (P2 §4.2) |
| 4D | Time as the fourth axis; the 24-cell (D4) lattice | Memory that knows when; denser packing | Programs as vectors exact over 1,024 steps (P2 §4.7) |

## How we got here

The geometry did not start as geometry. It started with a document about squeezing more out of the laptop's
processor, and a question from the author: could the machine's own power and temperature readings be turned into a
torus — a ring-shaped lookup table — that the processor's governor consults? That was built first. A governor that
read the machine's state as a point on a torus cut the slowest 1% of requests from 118 to 99 ms and the time spent at
or above 95 °C from 11% to 3%. A side finding stuck: asking the processor for its power-saving preference cost about
40% less energy per text, while the performance preference bought 16–20% speed. A new Linux scheduler, tried on the
way, made things neutral to slightly worse and was dropped.

Then the author asked the question that set the method for the next two days: *swap the torus for a paraboloid and
measure the difference.* Two experiments followed. The first (on the classifiers) gave the binding result above. The
second (on the governor's own data) was badly designed — our error: the time split put brand-new workloads only in the
test period, so neither geometry could be scored fairly. It was reported as a design flaw rather than quietly redone.

*"But you're running it on the model — can we apply this to the CPU itself?"* That turned the question from the
governor to the search kernel. A study of the processor's memory system said the bottleneck was bytes, not
arithmetic, so the first shape was the cube: four queries sharing each fetched chunk. It was bit-identical and 2.1–2.6
times faster. A Hilbert-curve ordering of the tiles, expected to help the cache, did nothing at this scale — the
query grid was too small for the curve to matter.

*"We have spheres, cubes and stars, yet no pyramids or triangles. I don't think I'm wrong."* The author was right: the pyramid
gave 4.9 times on top of the cubes with one changed answer in 5,711. Spheres (clusters) came next and were killed by
their own pre-registered bar. Then the author listed shapes to try — E8, the cuboctahedron, the dodecahedron, the
hypercube, four-dimensional solids. The lattice experiment that tested them was killed by the operating system the
first time (it ran out of memory copying 8,738 vectors of 10,240 numbers in double precision) and finished on a
second run in single precision, in chunks.

*"Find the limit of performance — break past current limits."* The roofline measurement answered honestly: the
hardware sets the limit for brute force, and the only way past it is to do less work. The pyramid's effective rate
already sat above the machine's brute-force ceiling. The same batch put programs into vectors. The first decoder was
slow — 976 microseconds per instruction, 94% of it spent computing angles; a follow-up, labelled post-hoc, unbound
with integer subtraction instead and reached 33 microseconds with the same exact output.

## What each shape taught

**The torus earns its place by composition, not lookup.** Swapping the ring for a paraboloid (exact Euclidean
geometry) barely changed classification accuracy, but the paraboloid could not undo a binding (0.018). The circle
matters because going around it can be reversed exactly; that is what later made triangles possible (P2 §4.4).

**Cubes and pyramids are about bytes, not maths.** The laptop's memory delivers about 12 GB/s; the exact search can
consume more. Letting four queries share each fetched chunk (the cube) beat the memory wall by about 4x in bytes per
second, and the pyramid — a cheap coarse pass, a narrower medium pass, an exact apex — went past the brute-force
ceiling by not doing most of the work (P2 §4.1–4.2, §4.8).

**Spheres wait for scale.** Clustering marks first (an inverted-file index) flipped labels at the boundaries of
clusters on heads of under 9,000 marks; at that size the pyramid is already cheap (P2 §4.3).

**Denser packings keep more information but the reader barely notices.** The lattice ladder E8 > D4 > hexagon > square
held for reconstruction, but retrieval accuracy moved by about 1.5 points (P2 §4.5).

**The golden ratio has a legitimate job.** A separate conversation explored the golden ratio in language and poetry.
In the memory, its precise use turned out to be frequencies: clocks built on rational frequencies repeat and confuse
distant values (91% failures at range 100), clocks built on golden-ratio steps never line up (0%) (P2 §4.6).

**Programs can live in vectors.** A 1,024-step program stored as position-bound instructions decoded exactly from
20 KB, at 33 microseconds per instruction once unbinding was done with integers (P2 §4.7).

## The second screen: the integrated GPU

The author's instinct was that the laptop's small integrated GPU could hold a "geometric script" that runs
continuously. Measured: the GPU sift is exact and reaches 14.1 billion dimensions per second when its marks stay
resident; it helps when the CPU is busy embedding text (+51%); it hurts when placed in the request path (p99 +18%);
and it loses every dense matrix job (P2 §5). The routing table that came out of it is itself a small primitive: send
each job to the engine that measured best for it.

### How the GPU work went

The first GPU shader gave the right answers four times slower than the processor. On the largest classifier it then
"finished" in a tenth of a millisecond with wrong output: the graphics driver's hang check had silently cancelled a
long dispatch. Splitting the work into chunks fixed it. Rewriting the shader so 64 threads walk one mark together and
eight queries share every word, with the score table in fast on-chip memory, brought it to parity with one processor
core. Keeping the marks resident and feeding queries through a pipe made it a usable engine — and, used beside the
processor rather than instead of it, it let the processor embed text 51% faster. The author then asked whether the
GPU could "serve in trit", running the ternary model's matrices as table lookups. It did, exactly, and 18 times
slower than the processor. Placing the GPU in the live request path raised the slowest-1% latency by 18%; it was
switched off by default. None of this was wasted: it produced the routing table, and the idea of a continuously
running background engine that essay 09 picks up.

## Where the ladder leads

Four dimensions here means time: a memory that moves, keeps learning and remembers when. One experiment showed why
that is needed: a frozen memory of fleet behaviour raised false alarms on 75% of later windows, because the fleet
itself had changed. The next rung is a memory that updates as it goes (**Speculative** until measured). The triangle
family took over the climb from here (essay 09).

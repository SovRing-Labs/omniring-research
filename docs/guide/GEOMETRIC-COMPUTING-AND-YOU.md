# Geometric Computing and You

*A booklet of the axioms, laws and rules we found while building the rings, written down so we could find our way.
It covers what we measured, what we assumed, and who discovered each idea first.*

| | |
|---|---|
| **Date** | 2026-10-10 (laws first written 2026-10-01; corrections of 2026-10-03 applied) |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Compiled with AI assistance (Claude) and the Sovereign Raptor Fleet System from the author's research conversations (unpublished), the experiment record and the math core's knowledge base. The author reviews it before publication. |
| **Type** | guide booklet. Every law cites the pre-registered experiments it rests on; their results are in `docs/appendix/geometric-laws/` (the **Evidence** table at the end). Anything that is not measured is marked **Postulate**, **Provisional** or **Speculative**. |
| **Companion** | `docs/guide/HYPERDIMENSIONAL-COMPUTING-AND-YOU.md` (the field and the tools); `docs/guide/MATH-CONCEPTS-AND-THANKS.md` (every concept we used, with credits) |

## The And You series

Three companion guides, written to be used together. Each one is for doing something, not only for reading.

| Guide | Read it when you want to… | What you walk away with |
|---|---|---|
| **Hyperdimensional Computing and You** | understand the idea and start building with the tools | five recipes you can run in under an hour, the patterns that pay off, and where each tool fits |
| **Geometric Computing and You** | design your own system and know in advance whether it will hold | a sizing formula, a ring-picking rule, a decision checklist and a pre-registration template, each tied to a measured law |
| **Math Concepts and Thanks** | find where an idea came from, check it yourself, or cite it | every concept with its plain meaning, its original author, where it lives in our code, and a script that tests the laws on your machine |

A path through all three:

1. **First hour.** Run the recipes in section 8 of the HDC guide.
2. **First design.** Size your memory and pick your rings with the Geometric guide's "Using the laws in your own work".
3. **Whenever a term is new.** Look it up in Math Concepts. When you build on it, cite the original author.

---

## In one paragraph

Geometric computing is the author's name for a way of working that grew out of hyperdimensional computing. Everything is
a point in a very large space, and every relation is a movement through it. You pick the shape of that space on purpose:
a torus for clocks, a simplex for choices, a four-dimensional group for order. Then you let the shape do the work that
code usually does by searching. Most of the ground under it was discovered by other people, and this booklet credits
them. Some of it is ours, measured on a 2019 laptop. Ours are the fitted capacity law, the separation of what from when,
the vibration warning, harmony read from phase, and the rule that shape pays only where things are compared. The
booklet lists twenty axioms, seventeen laws, seventeen rules and the structure that ties them together. Each says what
would break it.

## Why this booklet exists

The list began as notes for ourselves. On 2 October, after reading the first draft, the author wrote: *"these are for
myself and the fleet to navigate this creation process and help me make sense of it."* The author was frank about where things
stood: *"I've been moving ahead with trial and error and piecing together what I can, with the help of the fleet. TBH,
i'm quite out of my depth."* The author also asked the question this booklet tries to answer: *"Would Geometric computation
count as a field, and what/where can I pull from to keep devloping this, is it just HDC? 3/4d rendered code as a
program/loop/core."*

On 3 October, when a review pointed out that most of the laws come from hyperdimensional computing, the author replied:
*"thats fine i'm jsut trying to wrap the fleets' mind around the concept of geometric computing."* The same day the author said
why it matters beyond us: *"how can our geometric computing bring back legacy hardware and move people away from
overpriced tech, saving landfills from thousands of old devices. I'm not looking for a 1-10%increase, I believe this
field we are developing is key to this and many more feats."*

So this booklet has two jobs. It is a map for anyone joining the work, people and agents alike. It is also an honest
account of which parts are borrowed, which parts are ours, and which parts are still only a hope.

## What we mean by geometric computing

Hyperdimensional computing (HDC) stores everything as a long vector and builds structure with three moves: **bind**,
**bundle** and **permute** (Kanerva; Plate; Gayler). The companion guide explains it in plain words. Geometric
computing adds one habit on top: **choose the shape on purpose, then measure what it buys.**

- **A clock is a circle.** A counter that wraps is a ring. Several rings whose sizes share no factor name every number
  up to their product, which is the Chinese Remainder Theorem. Reading a time back is a jump, not a search.
- **A choice is a simplex.** K options that must be told apart sit best at the corners of a regular simplex, where
  every pair is equally far apart.
- **Order needs four dimensions.** On a circle, "a then b" lands where "b then a" lands. In a four-dimensional group of
  unit quaternions the two land in different places, so order is kept.
- **Code can be a shape too.** The author's phrase is *"3/4d rendered code as a program/loop/core"*: a program written
  as positions that the machine steps through, rather than as text it parses. Later this became the JIT-rendered cores
  of Parts 4 to 7.

The author's shortest statement of the goal came later, about web pages, but it holds for everything here: *"if we structure our
code to be geometric and exact regardless of formatting or text, we would optimze to another level."*

## The words you need

- **Vector, dimension (D).** A long list of numbers. Here, typically 2,560 to 10,240 entries.
- **Phase, torus.** Each entry is a dial position on a circle; a whole vector is a point on a many-dimensional torus.
- **Bind (⊗).** Combine two vectors into a third that looks like neither, and can be undone with the same key.
- **Bundle (+).** Add vectors into one that resembles each of them. A memory slot holds a bundle.
- **Sift.** Compare a cue with every candidate and keep the best match. **Clean-up** snaps a noisy result to the
  nearest known item.
- **Capacity (n, C).** n items bundled in one vector; C candidates the sift must choose between.
- **Ring, coprime, residue.** A counter that wraps; sizes that share no factor; the remainder that a ring shows.
- **2T.** The 24 unit quaternions of the binary tetrahedral group, the corners of the 24-cell. It is our 4-D core:
  one byte per coordinate.
- **Pre-registered, PASS / KILL.** The bars for an experiment are written before it runs. A result that misses them
  stays a failure.
- **LAW / RULE / STRUCTURE.** A **law** is quantitative, fitted or replicated across at least two families of
  experiment. A **rule** is a design consequence of measured results. **Structure** is how the parts fit.

---

## Part I. The axioms

The axioms are the smallest set of starting points that the laws follow from. Each one carries:

- the **plain reading**, in the author's words where the author wrote one;
- its **status**: **Postulate** (our starting choice), **Measured** (supported by the laws below) or **Field** (known
  before us);
- **who found it first**;
- **what would break it**.

They fall into five families: Space, Join, Read, Govern and Run. Their numbers are kept stable, so A0, A18 and A19
were added later without renumbering the rest.

### I. Space

**A0. Random is almost always unrelated.** In high dimension, vectors drawn at random are nearly perpendicular. Their
similarity sits near zero with a spread of about 1/√D, so new symbols never need to be coordinated.
*Plain reading:* Strangers are almost always unrelated.
Status: **Field**, reproduced implicitly by every capacity run here. First found: Kanerva (2009); concentration of
measure. Breaks if random atoms at our D collide more than the capacity law predicts.

**A1. Meaning is position.** Every thing is a point in a large product of circles and groups (a torus, a 4-D group, a
lattice), and a relation is a motion of that space.
*Plain reading (J):* Where you are is what you mean; moving is relating.
Status: **Postulate**, our representation choice. First found: Plate's FHRR, where phase vectors are points on a torus;
Snaider and Franklin (2014), modular composite representations. Breaks if a task needs information that no
position-and-motion encoding can carry at bounded dimension.

**A2. Dimension is the budget.** What a space can hold grows with its dimension, not its precision. When a space fills,
nest a new one inside it and clean up between levels.
*Plain reading (J):* When constrained, add a bigger room, not smaller handwriting; when the room fills, build a room
inside it.
Status: **Measured** (L1, L2, L5). First found: capacity grows with dimension (Kanerva 2009; Frady, Kleyko and Sommer
2018). Our fitted constant a = 1.046 is ours. Breaks if more precision ever beats an equal-byte increase in dimension
in the operating range.

**A19. Meaning is spread, so damage degrades gracefully.** Information lives across all dimensions equally. Losing or
corrupting some of them lowers similarity smoothly instead of breaking the item.
*Plain reading:* A hologram cut in half still shows the whole picture, just dimmer.
Status: **Field**. First found: holographic and distributed representation (Plate; Kanerva 2009). Ours is that the
clock read stayed exact under phase noise of σ 0.6 (TF-5). Breaks if a small fraction of dimensions carries a large
share of an item's recoverability.

### II. Join

**A3. Binding is a group action.** Combining two things is a product in a group, so it can be undone: what is bound
with a key is unbound exactly with that key.
*Plain reading (J):* What a key joins, the same key can undo.
Status: **Postulate and Measured**. Unbinding is exact in every family we built; TF-2 showed that roles unbind
exactly. First found: invertible binding in Plate's HRR, group VSAs, and GHRR (2024).

**A4. Superposition is shared presence, paid in crosstalk.** Many things can live in one vector by addition. Each one
adds noise in proportion to n/D, and the gain is what you can do with them, not how small they become.
*Plain reading (J):* There are many truths, but with more truths come more half lies. An individual can become part of
a whole, yet it is still an individual: each voice stays itself inside the chorus.
Status: **Measured** (L1, L3). First found: crosstalk in proportion to n/D (Kanerva 2009; Thomas, Dasgupta and Rosing
2021). Breaks if a superposed store beats raw storage per bit at equal reliability.

**A5. Order requires non-commutation.** If "a then b" must differ from "b then a", the algebra must not commute. Four
dimensions is the first place an exact finite one lives (the groups 2T and 2I).
*Plain reading (J):* Socks then shoes isn't shoes then socks; to keep order you need math where swapping changes the
answer.
Status: **Measured** (L4, L11). First found: non-commutative binding (GHRR 2024; group VSAs). Using 2T and 2I as exact
byte tables is ours.

**A18. Binding distributes over bundling.** A key applied to a mixture equals the mixture of each part bound with that
key: k ⊗ (a + b) = k⊗a + k⊗b. One operation acts on a whole store at once.
*Plain reading:* Turn the whole crowd at once, and every person in it turns.
Status: **Field**. First found: the algebra of MAP, HRR and FHRR (survey: Kleyko and colleagues, 2022). It is why one
query can search a whole bundle in one step. Breaks if a binding we adopt, such as one with a non-linear clean-up
inside it, stops distributing.

### III. Read

**A17. What and when are separable.** Every stored thing carries its content and its time as two layers of one
vector. Time can be shifted without touching content, and content read without knowing the time.
*Plain reading (J):* There is a time and a place to everything: a thing and its time travel together but can be read
apart.
Status: **Measured** (L14, TF-1), **Provisional** until a second run. First found: not found in the sources we
searched; this one is ours. Its geometry is the Hopf fibration (H. Hopf, 1931).

**A6. Similarity is the only read.** A memory is read by comparing a cue with candidates. In mathematical terms that is
a projection onto characters, a Fourier read. Nothing answers without a cue.
*Plain reading (J):* Resonance drives recall, and only a question can ring the bell.
Status: **Measured** (RING-1, R3). First found: clean-up memory (Kanerva 2009); similarity as a kernel (Frady and
colleagues, 2021, on fractional power encoding). Breaks if a store returns the right item with no cue at all.

**A7. Exact from structure, approximate from sums.** Group products, residues and rows are exact. Sums are approximate
and need clean-up. Each job goes to the form that fits it.
*Plain reading (J):* Structure is exact; mixtures distort and need cleaning.
Status: **Measured** (R4, R5). First found: in parts, clean-up memory and residue HDC (Kymn and colleagues). The split
of jobs between the forms is our rule.

**A8. Shape pays where things are compared.** Designed geometry earns its place in what is sifted and routed. Where
things are only bound and unbound, randomness is enough.
*Plain reading (J):* Shape matters when you compare, not when you pack.
Status: **Measured** (R1: TF-2 against TF-3 and SIMPLEX-0). First found: not found in the sources we searched. Its kin
is the simplex frame of neural collapse (Papyan, Han and Donoho, 2020).

### IV. Govern

**A9. Control sits one level above memory.** Memory is passive. A source one level up supplies the cues, releases old
intents, and governs by acting on the scores below, not by competing with them. This is the author's "+1" rule.
*Plain reading (J):* A mind without a governor has no control, and the governor doesn't shout over the voices; it
decides which to listen to.
Status: **Measured** (R2, R3, TF-3b, SOURCE-0 → SOURCE-2); untested inside a trained model. First found: not found in
the sources we searched. Its kin is biased competition in attention (Desimone and Duncan, 1995).

**A10. Truth beats intent.** An exact proof or check overrides any intent, vote or fluent output.
*Plain reading (J):* Proof outranks what anyone wants.
Status: **Postulate and Measured** (R4, R10, PLM-2). Our design choice; its kin is neuro-symbolic verification.

**A11. Redundancy detects; only a key authenticates.** Check residues expose errors exactly. Resisting forgery needs a
secret.
*Plain reading:* An echo catches mistakes; only a secret stops forgers.
Status: **Measured** (L6, TF-4b). Authentication itself is not built yet. First found: redundant residue codes in
coding theory; message authentication codes in cryptography.

**A12. Everything leaves a mark.** Every read and every decision carries where it came from: the marks that voted, the
proof that held.
*Plain reading (J):* Every action leaves a trail back to why.
Status: **Postulate**, the auditability choice; provenance on every sift is built. Its kin is provenance in databases
and citation in retrieval systems.

**A16. Agreement is phase.** Parts can tell each other how they are doing (harmony, dissonance, urgency) by a shared
rhythm alone, with no content and no shared vocabulary. Dissonance shows as a phase offset; a break shows as a beat.
*Plain reading:* You can hear who's out of tune without knowing the song.
Status: **Measured** (L13, HARM-0), but the graded offset reading was found after the fact. **Provisional**; reruns
are owed. First found: not found in the sources we searched. Breaks if phase-only signalling fails to find the
dissonant part under realistic noise.

### V. Run

**A13. The machine is part of the math.** Bandwidth, cache and heat set the real cost of each dimension. Capacity per
second equals items per dimension times the dimensions per second the hardware can stream.
*Plain reading:* The road is part of the trip: speed = how much fits × how fast it streams.
Status: **Measured** (L10, L1). First found: its kin is the roofline model (Williams, Waterman and Patterson, 2009).
Breaks if a design's measured throughput departs from that product without a new mechanism.

**A14. Time is a coordinate, and it breathes.** Every computation has an exact (token, layer) address on coprime clocks.
Coupling between clocks changes the tempo, never the address.
*Plain reading:* Every moment has an address; breathing changes the tempo, never the address.
Status: **Measured** for the address (TF-5 exact) and the coupling (L9). Breathing inside a model is untested. The
address is kin to rotary position encoding (Su and colleagues, 2021) and to residue HDC; the dual clock with coupling is
ours.

**A15. A loop that still moves is not done.** A settling system signals its own failure by moving before the outcome.
The system can listen to itself and escalate early.
*Plain reading:* If it's still shaking, it isn't settled.
Status: **Measured** (L12, VIB-0), **Provisional**. First found: not found in the sources we searched. Its kin is
critical slowing down near a tipping point. Breaks if residual vibration stops separating right from wrong settles in a
new loop design.

**What the axioms predict that we have not tested yet.** Each of these is a future pre-registration:

- A2: nesting across three or more levels inside a model.
- A5 with 2I: does capacity keep rising with group size?
- A9 inside a trained transformer, top-down and bottom-up.
- A11: the forgery rate of a keyed check slot.
- A14: breathing depth inside a language model.

---

## Part II. The laws

Each law has a plain sentence first, then the measurement. Experiment names in capitals (TF-0, QUAT-1 …) point to the
**Evidence** table.

**L1. Superposition capacity law.** *The more you put in one vector, and the more candidates you must tell apart, the
sooner recall fails, and you can say exactly when.* For n items bundled in D dimensions and recovered by sift among C
candidates, accuracy ≈ Φ(a·√(D/n))^(C−1). The fit gives a = 1.046 (rmse 0.0019) over 14 operating points (accuracy at
least 0.9). The points came from SIMPLEX-0, TF-0 (both arms), TF-1 (random and orbit), TF-2 and TF-6, and span:

- D 2,560 to 5,120;
- C 16 to 6,194;
- int8 and float storage;
- K 16 and K 240.

Items held at 99 % per 1,000 dimensions: 106 (C 16), 60 (C 1,000), 51 (C 6,194). It predicts the 256 per bucket that
TRI-0 found: the law gives about 308 per corner, and TRI-0 needed all three corners at once. It breaks only under deep
overload (fill of 1,024 or more at D 5,120), where the Gaussian approximation fails.
*Correction (CAL-2, applied 2026-10-03).* One form holds near the knee, but a is fitted per family (1.02–1.33), and the
overload tail needs its own law. In that tail the Gaussian form misses with rmse 0.097, because real crowded holograms
keep recovering a slow fraction. CAL-2 failed as registered.
Credit: the capacity analysis of distributed memory (Kanerva; Plate; Frady, Kleyko and Sommer 2018). The fitted form
and constant are ours.

**L2. Dimensions, not precision.** *More dial positions do not buy room; more dials do.* Capacity follows D, not phase
resolution. K 240 at half the dimensions has the same efficiency a (1.08 against 1.02), and therefore half the capacity
(TF-0). Precision adds only quantisation noise.

**L3. Superposition is not compression.** *Bundling costs more bits than writing the names down; it is worth it for
what you can do with the bundle.* At 99 % reliability, 4-bit dimensions cost about 38 / 67 / 79 bits per item for
C = 16 / 1,000 / 6,194, against log₂C = 4 / 10 / 12.6 bits of identity. That is 6–9 times the overhead (L1). POLY-0
saw the same: 32 bytes per fact as trits, against 26.9 bytes raw. The value of geometry is **operability**: bind,
shift, nest, sift and check in one object. It is not size.

**L4. Commutativity collides order; a 4-D group removes it.** *On a circle, "a then b" equals "b then a"; with
quaternions it does not.* Phase addition on the torus commutes, so every multi-hop failure in TRI-1's phase-addition
arm was a commutative collision. Unit quaternions (QUAT-0) and the finite group 2T (QUAT-1) are exact with 0
collisions at 1–10 hops. 2T buckets hold 384 against the torus's 256 (QUAT-2).
Credit: quaternions (W. R. Hamilton); the group 2T and the 24-cell (Conway and Smith, 2003).

**L5. Nesting multiplies capacity at one clean-up per level.** *Put rooms inside rooms; each level costs one clean-up.*
Polygons of polygons held 262,144 facts at 0.9995 in three lookups (REC-2). A 10 KB polygon holds 64 real embeddings at
0.9996 (NOMIC-POLY-1).

**L6. Residue checks detect; they do not authenticate.** *An extra ring catches every honest slip but cannot stop a
forger.* Every single-ring slip is caught: with the 17-ring, 100 % of 54,600 (RING-1 check); in TF-5, 2,000 of 2,000
with 0 false flags. A random vector passes with probability 1/|check space|: 0.04 % measured in TF-4b, against 0.043 %
from the formula.
Credit: redundant residue number systems (Szabo and Tanaka, 1967; Yang and Hanzo, 2001).

**L7. Evidence combines in the log domain.** *Add up how sure each view is, then normalise; do not count votes.*
Summed view scores with softmax reach 0.969 with calibration error 0.009, against 0.674 for a hard vote (SOFT-1). A
plain soft score beat voting only slightly (SOFT-0: 0.710 against 0.674, below its +0.05 bar, calibration error 0.284).
Credit: log-domain evidence and softmax (Bridle, 1990, for the name); calibration error as in the forecasting
literature.

**L8. Exact solids need the grid to divide the shape.** *A triangle fits a 16-tooth gear only if 16 divides by 3,
which it does not.* On K = 16 only shapes with n dividing 16 are exact: the tetrahedron, the 8-simplex. Triangles and
pentagons need K divisible by 3 and 5, and balanced harmonics. In TF-6, random harmonics gave error 0.0035; balanced
harmonics gave 1e-16. TF-6 did not pass as a whole, because the blocks were not all exact.

**L9. Coupled clocks lock above critical coupling; lock time grows near it.** *Two clocks pulled together will march in
step if the pull is strong enough; just above the threshold they take longest.*

- In TF-7, coupling at 3·Kc locked in 2 ticks and 1.5·Kc in 7; 0.5·Kc never locked.
- Locked rings meet at the mean frequency, so both of them move. Release is immediate.
- TF-7 failed as registered, because the bar should have been the textbook curve. This is why the field-prediction
  line exists (Part V).

Closed form, from the Adler equation, which matched the author's instinct toward a Taylor (small-angle) expansion:

- dΔ/dt = Δω − 2K·sin Δ, and a lock exists if and only if K ≥ Δω/2.
- The linearised relaxation rate is √(4K² − Δω²). That gives a time constant of 2.98 ticks at 1.5·Kc and 1.18 at
  3·Kc, against measured locks of 7 and 2 ticks (about two time constants).
- The locked frequency is (ω_t + ω_l)/2 = 1.15; measured, 1.150.
- Lock time diverges as K approaches Kc. That is the law, not the harness.

The snap is a saddle-node bifurcation on the circle (SNIC), not a Hopf bifurcation:

- Below lock, the rings beat at √(Δω² − 4K²). Simulated: 0.2892 / 0.2571 / 0.1761 / 0.0928 rad/tick at 0.25 / 0.5 /
  0.8 / 0.95·Kc. Predicted: 0.2905 / 0.2598 / 0.1800 / 0.0937.
- Above lock, they settle at √(4K² − Δω²).
- One tipping point, with mirror-image laws on each side.

Credit: Adler (1946); Kuramoto (1975).

**L10. On this laptop, sift is limited by memory unless it fits in cache.** *The road is slower than the engine.*

- RAM streams 11–12 GB/s, against sift compute of 12.6 and 43.6 G dims/s on 1 and 4 threads (LIMIT-0).
- Cache-fitted tiles gain 1.18–1.33 times (TILE-1).
- The integrated GPU lost every head-to-head: GEMM-0, PYR-GPU-0 P2, PROG-GPU-0, TERN-GPU-0 T2, HOLO-4.
- Sustained load reaches the CPU's thermal limit (GEAR-0). The answer was a rhythm and a thermal gearbox: BELT, GEAR-1,
  TORUS-TEL-1.

Credit: the roofline model (Williams, Waterman and Patterson, 2009).

**L11. Core efficiency under L1: 2T carries about 1.6 times the torus's effective dimensions per coordinate.** *A
4-D dial holds more than a 2-D one, though not as much as theory allows.*

- Same task (1,000 entities, 50 relations, D 5,120, int8): torus a = 1.074 (rmse 0.0029, 11 points); 2T a = 1.354
  (rmse 0.0024, 10 points). So (a_2T / a_torus)² = 1.59.
- For comparison, information per coordinate is log₂24 / log₂16 = 1.15, and real components are 4 against 2.
- Per byte: 2T stored at 1 byte per coordinate, against the torus at 4 bits, holds about 0.8 times the torus. Packed
  at 5 bits per coordinate (24 states; QUAT-1) it holds about 1.27 times, and keeps order (L4).
- Moderate confidence: both fits rest on points near the ceiling (`xlaw_cores.result.json`).

*Group-theory prediction.* The 24 elements of 2T have the same second moments as the whole 3-sphere:
E[(q·q′)²] = 1/4, against the torus's E[cos²] = 1/2. So the ideal gain is exactly 2.0 per coordinate. We measured
1.59, so about 20 % is lost somewhere: perhaps in storing four int8 components, perhaps in bundling saturation. That is
an open, testable gap, and representation theory gives the target.

**L12. A settling loop that still moves is about to settle wrong.** *If it's still shaking at tick 30, the answer
will be wrong.*

- In the source and resonator loop, residual vibration predicts a wrong final settle with AUC 0.98–0.999 within every
  load. That is the variance of movement energy at ticks 10–30.
- The medians differ by about 1,000 times (VIB-0).
- The loop is overdamped, with a red-noise spectrum and no resonant peak, so the signal is a failure to settle, not
  ringing.
- Critical slowing (lag-1 autocorrelation) rises with load to M 20, then plateaus. That second leg was registered as
  rising throughout, so VIB-0 failed as registered on it.

**L13. Harmony is measurable without content.** *You can hear which voice is off without knowing the words.*

- Heads were modelled as light Stuart–Landau oscillators (the Hopf normal form) that write only their phase to a
  shared bus.
- A head whose state shifts its hum is found 100 % of the time within 1–4 ticks, with 0 false alarms (HARM-0).
- How dissonant it is reads as its phase offset while still locked: 0.47 / 1.23 / 1.34 rad at 0.5 / 2 / 4·K, toward
  the π/2 limit. Once it breaks lock, it reads as a beat: 0.10 rad/tick at 8·K. That is the same Adler law as the
  clocks (L9).
- The graded readout was not the registered one, so HARM-0 failed as registered. The offset law is a diagnostic
  finding that awaits its own run.

**L14. What and when separate in one vector (Hopf fibration).** *The same vector tells you what a thing is and when it
happened, on two different layers.*

- The Hopf base (relative phases of dimension pairs) reads content at any time phase: 100 %, against 52 % raw.
- The fibre (global phase) reads time once content is known: 100 % within one step (HOPF-0).
- The base is non-linear. It separates kinds of information, not crowds: in a bundle of 32, 43 % against 100 % for the
  modulus.

Credit: the Hopf fibration (H. Hopf, 1931). Applying it to read content and time apart is ours.

**L15. Rhythms share one bus at the price of time resolution.** *Many radio stations fit on one wire if each has room
to breathe.*

- Bands multiplexed on a shared bus decode as well as alone (kick F1 0.661 against 0.666) when each band's gap Δω
  gives a listening window 2π/Δω well below the fastest change it carries.
- When the window approaches the spacing of events, events merge. This is the time–frequency uncertainty (Gabor).
- It is a diagnostic found after the fact in HARM-2. The registered run failed on its decoder, and a fresh
  pre-registered run is owed.

**L16. Moving a bump on a continuous attractor needs lopsided wiring.** *To roll the ball, tilt the bowl one way.*
**Provisional**: supported by the CF-2e probe (MOVE 1.00, HOLD 1.00), but CF-2e failed its third leg (release in 68
ticks against a bar of 20). A pre-registered rerun is pending.

- A symmetric recurrent footprint W_sym(|i−j|) makes a well that pins the bump.
- Moving it at velocity v(t) without changing its shape needs asymmetric connectivity:
  W(x, v) = W_sym(x) + γ·v(t)·(−∂W_sym/∂x).
- Symmetric noise only makes the bump quiver inside its well. That explains why CF-2d stalled; CF-2d failed as
  registered.

Credit: Zhang (1996); Burak and Fiete (2009).

**L17. Exact abstention follows the extreme-value spacing of inner products.** *When the best match is not far enough
ahead of the second, say "I don't know".* **Provisional and pre-registered**: it awaits a cheap probe on ring-head data.

- In an equiangular simplex codebook of size C in D dimensions, the gap between the top similarity and the runner-up
  follows a Gumbel extreme-value distribution.
- The answer can be trusted when Δs = s(1) − s(2) ≥ (√(2 ln C) / √D) · θ, with θ calibrated.
- Below this margin, the signal is lost in the noise. The circuit should then emit an exact null (0), abstaining
  instead of guessing.

Credit: extreme-value statistics (Gumbel).

---

## Part III. The rules

Rules are what the laws tell us to do when we build.

- **R1.** Geometry matters where items are **compared**: routing and sifted codebooks gained 5.8 points in TF-3 and
  1.6–2.5 in SIMPLEX-0. It does not matter where roles are bound and unbound: 0 in TF-2.
- **R2.** The level above governs by acting **on** the level below's scores, through a margin or spark, not as one more
  candidate: 0.634 against 0.459 in TF-3b. This is the tested form of the author's "+1 dimension" rule. TF-3b's
  registered question, whether a learned key earns its place, came out no; the margin arm is the one that won.
- **R3.** Memory answers only when cued (RING-1). A source supplies the cue every tick, and must **release** an old
  intent to switch: 25 % in SOURCE-0, 98.5 % in SOURCE-2. SOURCE-0 failed as registered, and SOURCE-2 passed two of
  its four legs.
- **R4.** Logic lives on an exact spine. Superposed logic falls to chance at depth 5–6 (LOGIC-0 failed that leg),
  while consistency scoring is perfect (HARMONY-0, AUC 1.000; TRI-2). Frame-first proof beats greedy steps: 1.00
  against 0.24 with about 60 times less work (PLM-0).
- **R5.** Exact lookups go to rows: SQL is about 250 times faster (Part 2's fair comparison; SQ-0 router). The ring is
  for association, chains and sift.
- **R6.** Real data must be whitened before it obeys L1: NOMIC-POLY-0 failed, NOMIC-POLY-1 passed.
- **R7.** Superposed queries do not hold the mismatch bar (SUPER-Q-0 KILL). Prefix clean-up needs single items, not
  full buckets (TRI-3).
- **R8.** Positions on real orbits cost nothing and turn a time shift into a rotation (TF-1). Long ranges use a
  winding orbit; clocks use a residue orbit (TF-5 exact).
- **R9.** Head keys form a regular simplex (TF-3). Exact odd shapes go only in dedicated, balanced blocks (TF-0, TF-6).
- **R10.** A community mouth must not carry the verdict (PLM-2 showed a yes-bias and failed as registered). The spine
  decides; the mouth words it.
- **R11.** Live streams repeat: 99.9 % of live notes were exact repeats (EMB-CACHE-0). Cache before computing.
- **R12.** Pre-registration catches our own errors. Harness and sample-size problems in TF-1, TF-3 and TF-4 were found
  because a bar existed.
- **R13.** Give every shared rhythm its own band, with a gap Δω of several times 2π / (the fastest change it must
  carry). Keep rhythms off the memory vectors (A4). Prefer coprime ratios between coupled rhythms so they neither lock
  nor alias (L9, the torus-knot note).
- **R14.** Never scan memory that residue algebra can address (MEM-0, BUS-PEEL-0). Context history belongs in
  residue-indexed bundled slots: BUS-PEEL measured 24–64 marks per 10 KB slot with 0 fakes, and MEM-0 holds 128 items
  per read. Key retrieval is a CRT jump on an exact key: 0 bytes scanned, 1.0 ms per lookup.
- **R15.** Start representation spaces on the unit hypersphere or a simplex frame, never on unnormalised Gaussian
  draws. Unnormalised embeddings inflate the starting dot-product variance to D^(1/2), which gave starting losses of
  68–79 nats against 9.01 for uniform. Normalisation starts the loss at ln(V) with no gradient shock. Kin: nGPT
  (Loshchilov and colleagues, 2024) and cosine-softmax heads.
- **R16 (Provisional, 2026-10-03).** Positions live on the commuting torus; the **order** of content goes through
  non-commutative binding (2T). Relative-position attention needs commuting rotations, which is necessary and
  sufficient (ComRoPE, 2025). Ordered structure needs non-commutative binding (GHRR 2024; our L4 and QUAT-2). Use each
  where it is native.
- **R17 (Provisional, 2026-10-03).** A continuous-attractor surface that can be steered must have Euler characteristic
  0, which means a torus. By the Poincaré–Hopf theorem, every smooth steering field on a sphere stalls somewhere.
  Grid-cell activity lives on a torus (Gardner and colleagues, 2022), and our hex-torus field steers (CF-2e MOVE and
  HOLD 1.00).

---

## Part IV. How the parts fit

**The dimensionality ladder.** This came out of a three-way conversation on 2 October (the author, Gemini and Claude).
Each rung adds one structure.

| Rung | Space | What it carries | Learned weights |
|---|---|---|---|
| 1-D | the ring, U(1) | time, sequence position, periodic clocks, CRT addresses | none |
| 2-D | the simplex | decision boundaries, margin routing, heads kept apart (⟨eᵢ, eⱼ⟩ = −1/(K−1)) | none |
| 3-D | the cube, SO(3), R³ | a continuous attractor that "breathes" and steers focus | the controller only |
| 4-D | polytopes, SU(2), S³, the 24-cell | non-commutative order: syntax, logic, proof trees (A then B ≠ B then A) | none |

Unit quaternions are the double cover of 3-D rotation. They remove gimbal lock and the reversal of causal order. Each
rung is measured on its own; the ladder as a whole is structure, not a measured claim.

**Representation.** Unit phases on a D-torus; the torus sits inside the sphere (T^D ⊂ S^(2D−1)). Codebooks are built
from their Gram matrix as designed solids (Part 3 §1). Finite groups carry order (2T, 2I), and lattices carry packing
(E8: LAT-0).

**Operations.** Bind (a group product or a phase add), bundle (a sum), permute or rotate (an orbit step), sift (a
similarity scan), clean-up (the nearest codebook item), check (redundant residues).

**Memory.** Marks go into triangle buckets, buckets into polygons, polygons into nested polygons, and those into
shards that can be mounted.

**Control.** The source (a program vector read every tick); the dual clock (token and layer residues); coupling, which
the author calls breath.

**Integrity.** Residue check rings detect. Authentication is still open (L6).

**The spectral view.** This came from the author's mathematics threads of 1 October.

- Torus phases are the **characters** of cyclic groups, so reading a residue is a Fourier projection onto one
  character. This is the Kaluza–Klein picture of a hidden circular dimension with whole-number charge.
- The 2T core uses the group's two-dimensional complex representation (four real components). Representation theory
  predicts its ideal gain: 2.0 per coordinate, against the 1.59 measured.
- Continuous values encoded by fractional powers are random Fourier features (Rahimi and Recht, 2007), so their
  similarity is a kernel. FPE-0 measured a sinc kernel with error 0.013. Gaussian-process reasoning is therefore
  available in the same vectors.
- A choice among N faces is a point in the (N−1)-simplex, which is the probability simplex and the same shape as the
  head keys (TF-3).

**Knots and links.** This is from the author's note "Hopf link and vectors", 1 October.

- Two clock rings with periods p and q trace a curve on the torus of their two phases.
- If gcd(p, q) = 1, it is one closed curve that visits all p·q coordinates: a (p, q) torus knot. That is the geometric
  face of CRT uniqueness.
- If gcd = d, it is a link of d components; (2, 2) is the Hopf link.
- Unit quaternions (the 2T core) live on S³, which the Hopf fibration splits into circles over a sphere. A vector is
  then WHAT (a point on the sphere) plus WHEN (a phase along its circle). Shifting phase, as in TF-1's rotation, moves
  along a fibre without changing content, and any two fibres are linked once.
- The torus woven from crossing helices in the author's photograph is a torus in S³ made of such fibres: the
  Villarceau circles (Yvon Villarceau, 1848).

**Two read modes.** Phase interference (the sift, "real time") and log-domain evidence (SOFT-1, "imaginary time") are
two sides of one mathematics, linked by Wick rotation. Memory read is linear and wave-like; control dynamics are
non-linear and dissipative.

**Substrate.** AVX2 and SSE kernels, cache tiles, belt-and-gearbox scheduling, and omnid as the one server.

## Part V. Connections the numbers made

When every experiment was put in one registry and the laws were fitted across them, several results we had read as
separate turned out to be one:

1. TF-0's result is L1 plus L2, not a failure of geometry: K 240 halved D, so capacity halved at the same efficiency.
2. TRI-0's 256 per bucket is what L1 predicts for C = 1,000 entities. The "cap" was the law, not the code.
3. L3 explains why POLY-0's trit solid is not compression. Its value is operability, so designs should be measured by
   operations enabled per byte, not bytes per fact.
4. L6 unifies four results (17-ring, SOURCE-3, TF-4b, TF-5): our checks are an error-detecting code. Safety against an
   adversary needs a keyed check, which is still open.
5. R3, the cue requirement and SOURCE-2 say the same thing: memory is passive, and control is the source.
6. L10 times L1: the law fixes dimensions per item; the hardware fixes cost per dimension. Throughput per fact equals
   bandwidth over bytes per dimension, times items per dimension. That is the budget the seed's attention must live
   inside.
7. Pack 2T at 5 bits and the 4-D core beats the torus per byte (about 1.27 times) and keeps order (L11). QUAT-2's
   "about even per byte" was the unpacked one-byte form.

## Using the laws in your own work

The axioms say what to assume and the laws say what to expect. This section turns them into steps you can take on
your own system. Every number in it comes from the laws above or was computed from them. The two small scripts are
in `docs/guide/examples/design_helpers.py`.

### 1. Size the memory before you write code (L1, L2, L5, A2)

Ask three questions: how many items go in one vector (n), how many candidates must the read tell apart (C), and what
accuracy you need. L1 then gives the dimension.

```python
import math
def accuracy(D, n, C, a=1.046):                    # L1
    phi = 0.5 * (1 + math.erf(a * math.sqrt(D / n) / math.sqrt(2)))
    return phi ** (C - 1)

def max_items(D, C, target=0.99, a=1.046):
    n = 1
    while accuracy(D, n + 1, C, a) >= target:
        n += 1
    return n

print(max_items(5120, 1000))                         # 308 items per 5,120-dim vector at 99 %
```

**Worked example.** You need 500 items among 1,000 candidates at 99 %.

- At D 5,120, the law allows about 308, so one vector is not enough.
- **Bigger room:** D 10,240 holds all 500 at 0.9989. D 8,192 falls short at 0.9886.
- **Room inside the room:** two vectors of 5,120 with 250 items each also give 0.9989, and nesting costs one clean-up
  per level (L5).
- **Not smaller handwriting:** more dial positions at the same dimension buy nothing (L2).

**Fit a on your own data.** The constant a was 1.02 to 1.33 across our families (the CAL-2 correction), and that range
moves the 99 % limit at D 5,120, C 1,000 from 293 to 498 items. Run three fill levels near your target, fit a, and plan
with your own number. Do not plan past the knee: in deep overload the formula stops holding.

### 2. Pick the rings for a range you need to address (CRT, L6, A11, R13)

Choose ring sizes that share no factor, whose product covers your range. Then add one check ring larger than every ring
it guards.

```python
def pick_rings(span, start=3):
    isprime = lambda p: p > 1 and all(p % q for q in range(2, int(p ** 0.5) + 1))
    rings, prod, p = [], 1, start
    while prod < span:
        if isprime(p):
            rings.append(p); prod *= p
        p += 1
    check = p
    while not isprime(check):
        check += 1
    return rings, prod, check
```

| What you need to address | Rings | Exact range | Check ring | A random vector passes the check |
|---|---|---|---|---|
| 1,000 items | 3, 5, 7, 11 | 1,155 | 13 | about 1 in 13 |
| every second of a day (86,400) | 3, 5, 7, 11, 13, 17 | 255,255 | 19 | about 1 in 19 |
| a million records | 3 … 19 | 4,849,845 | 23 | about 1 in 23 |
| every 32-bit value | 3 … 31 (ten rings) | 100,280,245,065 | 37 | about 1 in 37 |

Omni-ring itself uses 3, 5, 7, 13 with the check ring 17, for 1,365 addresses. The check catches every single slip,
but a forger gets through as often as the last column says (L6). If someone might attack it, use a keyed check
instead (A11). If two rings must also run as clocks side by side, keep their sizes coprime so they neither lock nor
alias (R13).

### 3. Decide where shape is worth the effort (A8, R1, R9)

- **If items are compared** (routed, sifted, classified), design the codebook: put the keys at the corners of a
  regular simplex. That gave 5.8 points in TF-3.
- **If items are only bound and unbound** (roles, fields), random vectors are enough. Designed shape gained 0 in TF-2.
- **If you need a triangle or a pentagon exactly**, the dial count must divide by 3 or 5 (L8). Keep such shapes in
  their own balanced block.

### 4. Decide whether order matters (A5, L4, L11, R16)

If "a then b" must differ from "b then a", as in paths, syntax, proofs and recipes, bind with the 4-D group 2T instead
of adding phases. It is exact at 1–10 hops and holds 384 per bucket against 256. Pack it at 5 bits per coordinate and
it also beats the torus per byte, about 1.27 times. Keep plain positions and times on the torus, where turning
commutes. Use each where it is native.

### 5. Send each job to the form that is exact for it (A7, R4, R5)

| The question is… | Send it to | Why |
|---|---|---|
| "the row with this key" | a table or an index | about 250 times faster (R5) |
| "something like this" | the ring sift | that is what similarity is for (A6) |
| "is this chain of facts consistent?" | an exact logic spine, with the ring only scoring | bundled logic falls to chance by depth 5–6 (R4) |
| "when did it happen?" | a residue clock | a jump, 0 bytes scanned (R14) |

### 6. Put a governor one level up (A9, R2, R3)

The memory answers only when asked. Whatever drives it should supply a cue every tick, act on the scores (a margin or
threshold) rather than add itself as one more candidate, and release an old intent before switching. In our runs,
releasing took switching from 25 % to 98.5 % (SOURCE-0 to SOURCE-2).

### 7. Let it say "I don't know" (L7, L17, A10)

Add evidence as log-scores and normalise; do not count votes. That gave 0.969 with calibration error 0.009, against
0.674 for a vote (L7). Then abstain when the top match is not far enough ahead of the second. L17 predicts the margin
as √(2 ln C)/√D times a constant you calibrate on held-out data. L17 is still **Provisional**, so calibrate the
constant on your own data.

### 8. Listen to your loop (A15, L12)

If your system settles, as a resonator, a solver or a search does, record how much it is still moving between ticks
10 and 30. In our loop that predicted a wrong answer with AUC 0.98–0.999. Escalate those cases early instead of
waiting. This is **Provisional**: check it on your loop before you rely on it.

### 9. Count the machine in (A13, L10)

Throughput per fact is bandwidth over bytes per dimension, times items per dimension. Measure your memory bandwidth
first. If your sift is slower than that predicts, tile it to the cache; that gained 1.18–1.33 times on our laptop.
Do not assume an integrated GPU helps: on ours it lost every head-to-head.

### 10. Prepare real data (R6, R15, R11)

- **Whiten real embeddings before bundling them.** They sit in a narrow cone and break L1 otherwise (R6).
- **Start learned vectors on the unit sphere**, so training starts at ln V instead of 68–79 nats (R15).
- **Cache exact repeats before computing anything** (R11).

### The design checklist

| Question | Law | What to do | How to check it held |
|---|---|---|---|
| How big must each vector be? | L1, L2 | Solve for D from n, C and the target; grow D, not precision | Measure accuracy at three fill levels and fit a |
| It is full. Now what? | L5, A2 | Nest a second level with one clean-up | Accuracy per level stays above target |
| How do I address a range? | CRT, L6 | Coprime rings covering the range, plus a larger check ring | Every single-ring slip is refused |
| Does shape matter here? | A8, R1 | Simplex keys where things are compared; random elsewhere | Compare against a random codebook |
| Does order matter? | A5, L4 | 2T binding for ordered content | No collisions at your hop depth |
| Exact or similar? | A7, R5 | Rows for keys, rings for likeness | Route by question type; time both |
| Who decides? | A9, R2 | A governor acting on scores, one level up | Switching rate with and without release |
| When to abstain? | L7, L17 | Log-domain evidence plus a calibrated margin | Calibration error on held-out data |
| Is the loop done? | A15, L12 | Watch residual motion | AUC of motion against wrong settles |
| Will the machine keep up? | A13, L10 | Bandwidth × items per dimension | Measured throughput against the product |

### A pre-registration template

Copy this above any experiment before you write the harness (see "How we keep sifting"):

```
EXPERIMENT:      <name>
QUESTION:        <one sentence>
FIELD PREDICTS:  <what established theory or a cited paper says will happen> [source]
                 (or: nothing found (searched: <terms>))
PASS if:         <measurable bar>
KILL if:         <measurable bar>
DATA:            <D, C, n, storage, seeds> written into the result file
```

A result that matches the field's prediction is a calibration. One that departs from it is a finding. Either way,
publish it as it came out.

## How we keep sifting

**The field-prediction line (a rule from the author, 2 October).** Every pre-registration carries one line above its
PASS and KILL bars:

`FIELD PREDICTS: <what established theory or a cited paper says will happen> [source]`

or, if nothing was found, `FIELD PREDICTS: nothing found (searched: <terms>)`. It is written before the harness exists,
like the bar. The reason is TF-7, which re-measured textbook Adler and Kuramoto locking as if it were news; the bar
should have been the textbook curve. A result that matches the field's prediction is a calibration, not a finding. A
result that departs from it is the finding.

**Open defects in our own record.**

- 28 experiments in the registry have no machine-readable verdict.
- Some verdicts in result files disagree with the plan's wording; the plan wins.
- Most result files do not yet record their own D, C, n and storage, so refitting L1 still needs reading the code.

**Tools for the tails** (from the author's mathematics threads):

- Chernoff and large-deviation bounds, for guaranteed false-match rates (spark thresholds).
- Extreme-value statistics or exact simulation for L1's overload curve, not a Laplace approximation.
- Exact multinomial (16-phase) and trinomial (ternary) score distributions for the extreme tails.
- The Adler equation for clock coupling (L9).

**Next fits.**

- Resonator and factorisation capacity: about 12 marks per slot at one cue, a different regime from L1.
- 2T against the torus under L1, with information per coordinate (log₂24 against log₂16).
- Latency laws from BELT, GEAR and TILE.

## Where it did not hold

- **L1 is not one universal law.** Its form holds near the knee with a per-family constant, and fails in the overload
  tail (CAL-2, FAIL as registered).
- **Several laws rest on runs that failed as registered**, and are kept as diagnostics until a fresh run:
  - L13 (HARM-0);
  - L15 (HARM-2);
  - L16 (CF-2e failed its release leg; CF-2d failed);
  - L12's second leg (VIB-0);
  - L9's run (TF-7).
- **L11's gap.** 1.59 measured against 2.0 ideal is unexplained.
- **L17 is a prediction**, pre-registered and not yet run.
- **Some evidence is not published with this corpus.** The harness code for most of these experiments is not included; only
  four harnesses are (see Evidence). The results for FPE-0, GEMM-0, PYR-GPU-0, PROG-GPU-0, TERN-GPU-0 and TF-4 are not
  included either. Claims resting only on them are **unsupported** until their records are published.

## What this booklet does not claim

- That geometric computing is a new field separate from HDC. It is a way of working inside that field, with a few
  measured additions.
- That any axiom is proven in general. Each is supported, or not, by the experiments named.
- That the dimensionality ladder runs as one machine. Its rungs are measured one at a time.
- That geometry makes arithmetic faster. Measured gains come from reusing bytes and skipping work (Part 2 §4.8).
- That this brings old hardware back into daily use. That is the author's aim (**Speculative**). What is measured is
  that these kernels run, exactly, on a 2019 laptop CPU.

## Evidence

The result files are in `docs/appendix/geometric-laws/` of this corpus, copied unchanged except where noted. "Verdict"
is the registered verdict in the file; "—" means the file carries no verdict block.

| Experiment | Supports | Result file | Verdict |
|---|---|---|---|
| fits L1, L11 | L1, L2, L11 | `xlaw.result.json`, `xlaw_operating.result.json`, `xlaw_cores.result.json` | — (fits) |
| TF-0 | L1, L2, R9 | `tf0.result.json` | KILL (exact shapes at K 240: yes) |
| TF-1 | L1, R8, A17 | `tf1.result.json` | PASS |
| TF-2 | L1, R1, A3 | `tf2.result.json` | KILL |
| TF-3 | R1, R9 | `tf3.result.json` | PASS |
| TF-3b | R2, A9 | `tf3b.result.json` | learned key did not earn its place; margin arm 0.634 against 0.459 |
| TF-4b | L6, A11 | `tf4b.result.json`; harness `tf4b.py` | PASS |
| TF-5 | L6, R8, A14, A19 | `tf5.result.json` | PASS |
| TF-6 | L1, L8, R9 | `tf6.result.json` | not PASS, not KILL (blocks not all exact) |
| TF-7 | L9 | `tf7.result.json` | FAIL |
| SIMPLEX-0 | L1, R1 | `simplex0.result.json` | PASS |
| QUAT-0 / 1 / 2 | L4, L11, A5 | `quat0.result.json`, `quat1.result.json`, `quat2.result.json` | PASS / PASS / PASS |
| POLY-0 | L3 | `poly0.result.json` | PASS (a, b, c) |
| NOMIC-POLY-0 / 1 | L5, R6 | `nomic_poly0.result.json`, `nomic_poly0_diag.result.json`, `nomic_poly1.result.json` | — (FAIL / PASS per the plan) |
| SOFT-0 / 1 | L7 | `soft0.result.json`, `soft1.result.json` | — |
| LIMIT-0 | L10 | `limit0.result.json` | — |
| TILE-1 | L10 | `tile1.result.json` | PASS (bit-identical) |
| GEAR-0 / 1 | L10 | `gear0.result.json`, `gear1.result.json` | — / T1, T2, T4 pass; T3 fail |
| BELT | L10 | `belt0.result.json` | — |
| TORUS-TEL-1 | L10 | `tortel1.result.json` | P1, P2, P3 pass |
| HOLO-4 | L10 | `holo4_cpu.log`, `holo4_gpu.log` | log |
| LAT-0 | Part IV | `lat0.log` | log |
| VIB-0 | L12, A15 | `vib0.result.json` | FAIL (V1 pass, V3 fail) |
| HARM-0 | L13, A16 | `harm0.result.json` | FAIL |
| HARM-2 | L15 | `harm2.result.json` | FAIL |
| HOPF-0 | L14, A17 | `hopf0.result.json` | PASS |
| CF-2d / CF-2e | L16, R17 | `cf2d.result.json`, `cf2e.result.json`; harnesses `cf2d.py`, `cf2e.py` (paths scrubbed) | FAIL / FAIL (move and hold pass, release fails) |
| CAL-2 | L1 correction | `cal2.result.json` | FAIL |
| SOURCE-0 / 2 / 3 | R3, A9, L6 | `source0.result.json`, `source2.result.json`, `source3.result.json` | FAIL / T1, T2 pass, T3, T4 fail / PASS |
| LOGIC-0 | R4 | `logic0.result.json`, `logic0b.result.json` | L1, L3, L4 pass; L5 fail |
| PLM-0 / PLM-2 | R4, R10, A10 | `plm0.result.json`, `plm2.lfm2.5-1.2b-instruct.result.json` | PASS / FAIL |
| SQ-0 | R5 | `sq0.result.json` | FAIL (the router; the 250× is Part 2 §8) |
| SUPER-Q-0 | R7 | `superq0.result.json` | KILL |
| EMB-CACHE-0 | R11 | `embcache0.result.json` | PASS |
| MEM-0, BUS-PEEL-0 | R14 | `mem0.result.json`, `bus_peel0.result.json`, `bus_peel0b.result.json`; harness `mem0.py` (paths scrubbed) | PASS (MEM-0) |
| RING-1, TRI-0 to TRI-3, REC-2, HARMONY-0 | L1, L4, L5, L6, R4, R7 | published: omni-ring Technical Disclosures Part 1 and Part 2, and the omni-ring `DOSSIER.md` | as published |
| FPE-0, GEMM-0, PYR-GPU-0, PROG-GPU-0, TERN-GPU-0, TF-4 | Part IV, L10, R12 | **not published with this corpus** | unsupported |

## Credits

The ground under this booklet was laid by others. Full references are in each repository's `PROVENANCE.md`, and the
running list with thanks is `docs/guide/MATH-CONCEPTS-AND-THANKS.md`.

- **Hyperdimensional computing and vector-symbolic architectures:** Pentti Kanerva; Tony Plate; Ross Gayler; Denis
  Kleyko and colleagues (survey, 2022); Snaider and Franklin (MCR).
- **Capacity:** Frady, Kleyko and Sommer (2018); Thomas, Dasgupta and Rosing (2021).
- **Residue codes and resonators:** Kymn and colleagues (residue HDC); Frady, Kent, Olshausen and Sommer (resonator
  networks); Szabo and Tanaka; Yang and Hanzo.
- **Groups and geometry:** W. R. Hamilton (quaternions); Conway and Smith; Conway and Sloane; H. Hopf; Yvon
  Villarceau; Poincaré and Hopf.
- **Oscillators and attractors:** Adler; Kuramoto; Stuart and Landau; Zhang; Burak and Fiete; Gardner and colleagues.
- **Statistics and learning:** Gumbel; Papyan, Han and Donoho; Loshchilov and colleagues; Rahimi and Recht; Bridle;
  Desimone and Duncan.
- **Hardware:** Williams, Waterman and Patterson (roofline).
- **Positions and binding:** Su and colleagues (RoPE); the ComRoPE and GHRR authors.
- **AI assistance:** Compiled with AI assistance (Claude) and the Sovereign Raptor Fleet System from the author's research conversations (unpublished), the experiment record and the math core's knowledge base. The author reviews it before publication.

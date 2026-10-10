# Math Concepts and Thanks

*A running list of every mathematical and scientific idea this work has used, tried or leaned on. It says where each
one comes from and thanks the people who gave it to everyone.*

| | |
|---|---|
| **Date** | 2026-10-10 (first index 2026-10-03; this edition adds the work of 3–9 October) |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Compiled with AI assistance (Claude) and the Sovereign Raptor Fleet System from the author's research conversations (unpublished), the experiment record and the math core's knowledge base. The author reviews it before publication. |
| **Type** | running list (living document). It grows with every release: a concept is added the first time it enters a plan, a harness or a disclosure. |
| **Companion** | `docs/guide/HYPERDIMENSIONAL-COMPUTING-AND-YOU.md`; `docs/guide/GEOMETRIC-COMPUTING-AND-YOU.md` (the axioms and laws, A0–A19, L1–L17, R1–R17) |

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

## Thank you

Nothing in this corpus starts from nothing. The rings are the Chinese Remainder Theorem, first written down in a
Chinese arithmetic book, the *Sunzi Suanjing*, more than fifteen hundred years ago. The memory is the vector memory that
Pentti Kanerva and Tony Plate described decades before we began. The training engine stands on Shannon's information,
Bridle's softmax and the ternary networks of the BitNet team. The doctor's search stands on Plotkin's and Reynolds's
anti-unification. The array's cut read stands on Gomory and Hu. Every test we pre-register follows Fisher's and Wald's
discipline.

So, to every mathematician, scientist and engineer named in this list: thank you. Many of them we know only by a
paper, some only by a theorem's name. Thanks also to the many whose work reached us without a name attached. Where an
idea has no single author, we say "field-known" rather than guess one.

Thanks also to the AI systems that studied this with the author, Claude and Gemini. They found many of these sources
and helped check them. Every number in the corpus was measured on our own machines, and every borrowed idea is cited,
not copied.

The author put the reason for keeping this list plainly: *"Ty for letting me know about the HDC known axioms, I have
honestly not learned much of the field/subject other than what i've learned to get to this point."* This list is how
we keep track of what we learned, and from whom.

## How to read the list

Each row gives:

- **Concept**, by its field name;
- **In plain words**, what it means;
- **How we use it**, where it sits in our work;
- **Status**, in one of these words:
  - **Measured**: a number in this corpus. The reference says where: `P1`–`P7` are the omni-ring Technical Disclosure
    parts (P6 is the omni-render disclosure); `L`, `R` and `A` numbers are the laws, rules and axioms in the geometric
    booklet; `doc NN` is a numbered research document.
  - **Measured†**: measured, but the record is not yet published. Treat it as unsupported until it is.
  - **Built**: code exists, with no headline number.
  - **Proposed**: designed or discussed, not built.
  - **Picture**: a teaching image, not a mechanism.
  - **Field fact**: known before us; we rely on it.
  - **Dropped**: tried or proposed, then set aside for the reason given.
- **Credit**, under one rule: the person named in our files, or the person who created the concept. Dates are first
  publication where we are sure of them.

## Put this list to work

**Learn an idea from the source.** Each row gives the plain meaning, where it lives in our work, and who first gave it
to everyone. To learn a concept properly, read the original author's work. Then open the document in the Status
column to see it running and measured.

**Judge how far to trust it.** The status word tells you how much weight a row can bear:

- **Measured:** build on it. The number and its result file are published.
- **Measured†:** test it yourself first.
- **Proposed:** an idea worth a probe, not a result.
- **Picture:** a way to teach, not a mechanism.
- **Dropped:** we tried it, and the row says why it failed. Save yourself the trip.

**Check the math core's laws on your own machine.** The ten laws in the table below ship as data in
`docs/appendix/math-kb/mathkb.json`, together with a short checker, `check_laws.py`. Every law carries its own
generator of random cases, so the checker needs nothing but Python:

```bash
cd docs/appendix/math-kb
python3 check_laws.py mathkb.json 200
```

```
mathkb.crt.bijection                       200/200
mathkb.mixed_radix.roundtrip               200/200
mathkb.barrett.equals_mod                  200/200
...
mathkb.clock.roundtrip                     200/200
```

**See a law bite.** A law is only useful if it fails when the thing it describes is wrong. Change the `prelude` of
`mathkb.hamming.triangle` to count `x | y` instead of `x ^ y` and run it again: it drops to **0/200**. That is the
"teeth check" every law in the knowledge base had to pass. Two first drafts failed it and were strengthened.

**Add a law of your own.** Each entry is a short JSON object:

- `id` and a plain `statement`;
- `vars`, the names of the variables;
- `forms.python`, the law as one Python expression;
- `prelude`, any helper the expression calls;
- `gen`, a function `gen(R, scope)` that returns one random case.

Write a **property** of the concept, never its definition restated. Then break the subject on purpose and confirm that
the law fails. If it still passes, the law is too weak.

**Cite the people.** When you build on a row, credit the name in its Credit column, not this list. When you use our
measurements, cite this corpus through its `CITATION.cff`.

**Help the list grow.** If you know an earlier source for an idea we marked as ours, or a better credit for a row
marked "field-known", tell us. We will add it and keep the old wording in the history.

---

## 1. Numbers, remainders and clocks

| # | Concept | In plain words | How we use it | Status | Credit |
|---|---|---|---|---|---|
| 1 | Chinese Remainder Theorem (CRT) | A number is fixed exactly by its remainders on sizes that share no factor | The rings: 3, 5, 7, 13 (+17 check) in omni-ring; T25 and T50 in the cores; reading a time is a jump, not a search (R14) | **Measured** (P1; P5 §5; docs 30, 36) | *Sunzi Suanjing* (3rd–5th c.); general method Qin Jiushao (1247); modern form C. F. Gauss (1801) |
| 2 | Residue number system (RNS) | Do arithmetic on the remainders instead of the number | Carry-free multiply; residue memory; residue all-reduce for training | **Measured** (P5 §2, §6) | Szabo and Tanaka (1967) |
| 3 | Coprime moduli | Periods with no common factor line up again only after their product | Choosing ring sizes; coupled rhythms that neither lock nor alias (R13) | **Measured** (TF-5; A14) | Field-known (Euclid's gcd) |
| 4 | Redundant RNS (RRNS) | Extra remainders let you catch, and sometimes fix, a corrupted one | The 17 check ring; the elastic 10-ring core; corrected all-reduce | **Measured** (P1; P5 §5–6; L6) | Yang and Hanzo (2001); redundant residue codes in coding theory |
| 5 | Soft (maximum-likelihood) residue decoding | Add each ring's score per candidate instead of trusting each ring's best guess | Plate and prism read paths | **Measured** (P5 §5) | Field-known (maximum-likelihood decoding) |
| 6 | Check residues detect, do not authenticate | An echo catches honest slips; a forger passes as often as a random guess does | The check ring and source checksum slots | **Measured** (L6; P3 §4) | Coding theory; the distinction is standard in cryptography |
| 7 | Keyed check (SipHash-2-4 message authentication) | A secret-keyed hash makes a check unforgeable | Integrity of model files at load; a keyed program syndrome | **Measured** (P5 §6) / **Proposed** for the source | Aumasson and Bernstein (2012) |
| 8 | Garner's mixed-radix conversion | Rebuild a number from its remainders digit by digit; compare from the top digit | The precomputed inverse plate; one of the math core's ten concepts | **Measured** (P5 §2; doc 40) | H. L. Garner (1959); presented in Knuth, *TAOCP* vol. 2 |
| 9 | Bézout's identity, modular inverses | For coprime p and q, p has an inverse modulo q | The constants of the inverse plate | **Built** | Étienne Bézout (18th c.); Euclid's algorithm |
| 10 | When two cycles meet | x ≡ a (mod p) and x ≡ b (mod q) have a solution only if gcd(p, q) divides a − b | The calendar clock native form; torus orbit membership | **Measured** (P5 §3) | Field-known (Euclid; CRT) |
| 11 | Barrett reduction | Replace division by multiply-and-shift for a fixed modulus | A math-core concept (laws cemented); earlier proposed as a kernel and dropped because compilers already do it | **Measured** (doc 40) / **Dropped** as a kernel | Paul Barrett (1986) |
| 12 | Montgomery reduction | Modular multiplication without division, in a shifted form | Considered with Barrett | **Dropped** (same reason) | Peter Montgomery (1985) |
| 13 | Miller–Rabin primality test | Modular powers prove a number composite | `numth.prime`, using the ring primes as witnesses; exact below 10⁶ | **Measured** (P5 §3) | Gary Miller (1976); Michael Rabin (1980) |
| 14 | Residue sieve and strong pseudoprimes (ψ₁₁) | Small-prime remainders can only refute; exact below 37² | A first-look filter that abstains past its guarantee | **Measured** (P5 §3) | Field-known; the ψ bounds are from the strong-pseudoprime literature |
| 15 | Finite (Galois) fields | Arithmetic modulo a prime is a field | Proposed for exact algebra plates in the seed library | **Proposed** | Évariste Galois |
| 16 | Fast multiplication: convolution and Fourier (NTT, Karatsuba) | Multiplying digit strings is a convolution; in the frequency domain it becomes pointwise | Explains why residue and phase multiplication are cheap | **Proposed** (explained) | Karatsuba (1960); number-theoretic transform, field-known |
| 17 | Balanced ternary; log₂3 ≈ 1.58 bits | One trit (−1, 0, +1) holds about 1.58 bits | Ternary weights, trit logic rows, ternary deltas | **Measured** (P5 §4, §6) | The Setun computer (Moscow State University, 1958) |
| 18 | Integer square root by Newton's method | Halve the gap each step and stop when r² ≤ n < (r+1)² | A math-core concept | **Measured** (doc 40) | Heron of Alexandria; Isaac Newton and Joseph Raphson |
| 19 | Smallest period of a sequence | The shortest block that repeats to make the whole | A math-core concept ("period mining") | **Measured** (doc 40) | Field-known (string periodicity) |
| 20 | Fibonacci recurrence; Cassini's identity | Each term is the sum of the two before; F(n−1)F(n+1) − F(n)² = (−1)ⁿ | A math-core concept; Cassini's identity is its law | **Measured** (doc 40) | Leonardo of Pisa (1202); Giovanni Domenico Cassini (1680) |
| 21 | Direct remainder computation | Compute x mod m with one multiplication by a precomputed constant | The T50 hub's vector encoding, checked for every value below 2²⁴ and every modulus | **Measured** (doc 30) | Lemire, Kaser and Kurz (2019) |
| 22 | Hamming distance | Count the positions where two words differ | A math-core concept; its law is the metric axioms (with a teeth check) | **Measured** (doc 40) | Richard Hamming (1950) |

## 2. Algebra, groups and logic

| # | Concept | In plain words | How we use it | Status | Credit |
|---|---|---|---|---|---|
| 23 | Cyclic groups and their characters | A phase e^(2πik/p) is a character; reading a residue is a Fourier projection | The spectral view of the clocks (booklet Part IV) | **Field fact** | Field-known (Gauss; Frobenius for characters) |
| 24 | Non-commutativity; abelian collisions | On a commutative group "a then b" equals "b then a" | Why phase-addition chains fail; the reason for the 4-D core | **Measured** (L4) | Field-known |
| 25 | Quaternions; SU(2) as the double cover of SO(3) | Four-number rotations with no gimbal lock | The 4-D rung of the ladder | **Measured** (L4; P3 §3) | W. R. Hamilton (1843) |
| 26 | Binary tetrahedral group 2T; the 24-cell | The 24 unit quaternions of the tetrahedral double cover | The order-keeping core, one byte or 5 bits per coordinate | **Measured** (L4, L11; P3 §3) | Conway and Smith (2003); the 24-cell, Ludwig Schläfli |
| 27 | Cayley graph and normal forms of 2T | Every route through the group reduces to at most 3 generator moves | The `graph.group` native form | **Measured** (P5 §3) | Arthur Cayley |
| 28 | Binary icosahedral group 2I; the 600-cell | The 120-element quaternion group | The next core to try (does capacity grow with group size?) | **Proposed** | Field-known; Conway and Smith (2003) |
| 29 | Representation theory; irreducible representations of 2T | A group's functions split into small blocks (dimensions 1, 1, 1, 2, 2, 2, 3) | Predicts the ideal 2.0 gain per coordinate (L11); character-basis layers | **Measured** (P5 §6; L11 gap open) | Frobenius; Schur |
| 30 | Schur's lemma; equivariant layers | A map that commutes with the group is block-diagonal in the character basis | Shift-equivariant mixing: 1,040 parameters against 32,400 | **Measured** (P5 §6) | Issai Schur (1905) |
| 31 | Characters for exact crosstalk | Count exact overlaps of bound triples with characters | Proposed to replace the "n/D" estimate for triangle buckets | **Proposed** | Field-known |
| 32 | Group-equivariant networks; geometric algebra transformers | Symmetry built into the network | Seed multimodal shelf: exact transforms, untrained | **Proposed** | Cohen and Welling (2016); Brehmer and colleagues (2023) |
| 33 | Clifford (geometric) algebra | An algebra of oriented areas and volumes | Proposed 3-D channels | **Proposed** | W. K. Clifford (1878) |
| 34 | Circulant matrices | Convolution is a circulant matrix whose eigenvalues are the Fourier transform | The theory under HRR binding | **Field fact** | Field-known; Plate (1995) for HRR |
| 35 | Tensor-product binding | Bind by outer product; the dimension grows | Contrasted with fixed-width binding | **Field fact** | Paul Smolensky (1990) |
| 36 | Category theory | The mathematics of structure-preserving maps | A seed shelf: the language of the IR, not a solver | **Proposed** | Eilenberg and Mac Lane (1945) |
| 37 | Formal concept analysis | A concept lattice from an object-by-attribute table | A candidate reasoning generator | **Proposed** | Ganter and Wille |
| 38 | Propositional SAT on trits; unit propagation | Clauses as rows of −1, 0, +1 | The `sat.trit` native form; its law "sound and complete against brute force" | **Measured** (P5 §3) | Davis, Putnam, Logemann and Loveland (1960s) |
| 39 | Sequent calculus; modal and intuitionistic logic; Peano's axioms | Formal proof systems | A seed logic shelf | **Proposed** | Gentzen; Peano |
| 40 | Gödel machine; self-improvement behind a gate | A program that rewrites itself only behind a proof or test | The gate design was adopted; the "Gödel sentinel" was replaced by a budget and abstention | **Proposed** (gate adopted) | Kurt Gödel; Jürgen Schmidhuber (2003) |
| 41 | Euclid's *Elements* as a graph of proofs | Each proposition proved from earlier ones | The law dependency graph as curriculum order | **Proposed** | Euclid |
| 42 | Belief revision (AGM) | What to drop when a new fact contradicts | A belief-revision generator | **Proposed** | Alchourrón, Gärdenfors and Makinson (1985) |
| 43 | Anti-unification | Find the most specific pattern with holes that two expressions both fit | The doctor finds shared shapes in code (`?0 + (?1 − ?0)·?2 / ?3`) | **Measured** (doc 34) | Gordon Plotkin (1970); John Reynolds (1970) |
| 44 | E-graphs and equality saturation | Store many equal forms of an expression at once | The doctor merges equal forms of lowered functions | **Measured** (doc 34) | Nelson and Oppen (congruence closure, 1980); Willsey and colleagues (*egg*, 2021) |

## 3. Geometry and topology

| # | Concept | In plain words | How we use it | Status | Credit |
|---|---|---|---|---|---|
| 45 | Phase torus T^D | Every item is D unit phases | The omni-ring state space (A1) | **Measured** (L1, L11) | Tony Plate (FHRR); Snaider and Franklin (2014) |
| 46 | Toroid (torus) | The doughnut shape. In our vocabulary each hub's inner core is a toroid core, and the rings around it are toroids too | The T50 hub, routing "toroid to toroid", the mailboxes | **Measured** (docs 30–31) | The shape is field-known; the toroid-core picture is the author's |
| 47 | Hopf fibration S³ → S² | The 3-sphere as circles over a sphere: the base is what, the fibre is when | Reading content and time apart | **Measured** (L14) | Heinz Hopf (1931) |
| 48 | Torus knots and links; the Hopf link | gcd(p, q) = 1 gives one curve through all p·q points | The geometric face of CRT uniqueness | **Measured** via the clock read (P5 §3) | Field-known (knot theory) |
| 49 | Villarceau circles | Circles hidden inside a torus, crossing as helices | The author's woven-torus photograph read as Hopf fibres | **Picture** with real geometry | Yvon Villarceau (1848) |
| 50 | Kronecker and Weyl orbits; equidistribution | A 1-D orbit winding evenly through a k-torus | Positions as a winding orbit (R8) | **Measured** (P5 §5) | Leopold Kronecker; Hermann Weyl (1916) |
| 51 | Regular simplex; simplex equiangular tight frame (neural collapse) | Maximally separated unit vectors, ⟨eᵢ, eⱼ⟩ = −1/(K−1) | Head keys (R9); fixed output head | **Measured** (R1, R9; P5 §6) | Papyan, Han and Donoho (2020) |
| 52 | Hypersphere initialisation | Unit-norm embeddings start the loss at ln V | R15 | **Measured** (R15) | Loshchilov and colleagues (nGPT, 2024) |
| 53 | Exact regular solids on a phase grid | An n-gon is exact only if n divides the grid size K | L8; designed codebooks | **Measured** (L8; P3 §2) | Field-known |
| 54 | E8 lattice | The densest packing in eight dimensions | Vector quantisation of head vectors | **Measured** (P2 §4.5) | Conway and Sloane, *Sphere Packings*; Viazovska (2016, optimality) |
| 55 | Hexagonal lattice (A₂) | The best packing in two dimensions | The hex-torus attractor field (R17) | **Measured** (R17, provisional) | Field-known |
| 56 | Euler characteristic; Poincaré–Hopf theorem | Every smooth field on a sphere has a stall; a torus need not | Why a steerable surface must be a torus (R17) | **Field fact** | Henri Poincaré; Heinz Hopf |
| 57 | Dimensionality ladder | Each rung adds a structure: time, choice, focus, order | The structure of the booklet | **Proposed** (rungs measured one at a time) | The author, with Gemini and Claude (2026-10-02) |
| 58 | Manifolds; intrinsic dimension | Data lives on a lower-dimensional surface | A framing for initialisation shock | **Proposed** (explanatory) | Field-known (Riemann) |
| 59 | Polyhedral model; loop tiling | Loops as integer polyhedra; tiling as a geometric transform | Cache tiles for the sift | **Measured** for tiling (L10; P3 §5) | Field-known (compiler theory) |
| 60 | Iterated function systems; partitioned IFS | Contractive maps whose fixed point is the image | The partitioned resonator | **Measured** (P4 §6) | John Hutchinson (1981); Michael Barnsley; Arnaud Jacquin (1992) |
| 61 | Collage theorem; Banach fixed point | A contraction has one attractor; the collage error bounds the decode error | The collage as the resonator's first guess | **Built** | Stefan Banach (1922); Barnsley |
| 62 | Space-filling curves | A 1-D order that keeps 2-D neighbours close | Mentioned for memory layout | **Proposed** | David Hilbert (1891); G. M. Morton (1966) |
| 63 | Signed distance functions | Store the distance to an edge, not a pixel | Rounded boxes with exact anti-aliasing in the Orbit paint module | **Built** (doc 33) | Field-known; popularised for text rendering by Chris Green (2007) |
| 64 | Box geometry as five residues | A box's corner, size and offset held on the 25 primes of T25, with its twist decoded by CRT | The doctor's T25 box kernel | **Measured** (doc 36) | CRT (row 1); the application is ours |
| 65 | Exact geometric relations ("pristine") | A box is pristine when its relations to its frame and siblings are exact to 1/64 px | The pristine fix loop | **Measured** (doc 36) | The author's goal; the relations are field-known geometry |
| 66 | Spiral (helix) curriculum | Revisit topics at rising depth | The circular build that keeps every earlier layer in the same core | **Measured** (doc 26) | Jerome Bruner (1960) |
| 67 | Golden ratio | φ ≈ 1.618 | Proposed for pacing prose; warned against as numerology | **Dropped** | Field-known (Euclid's extreme and mean ratio) |

## 4. Signals, waves and harmony

| # | Concept | In plain words | How we use it | Status | Credit |
|---|---|---|---|---|---|
| 68 | Fourier transform; convolution theorem | Convolution becomes pointwise multiplication in frequency | Phase binding is already in the Fourier domain | **Field fact** | Joseph Fourier; Cooley and Tukey (FFT, 1965) |
| 69 | Holographic reduced representations (HRR) | Fixed-width binding by circular convolution, unbinding by correlation | A baseline family for L1 | **Measured** (L1 correction, CAL-2) | Tony Plate (1995) |
| 70 | FHRR, phasor binding at K = 16 | Bind by adding phases; inverse by conjugate | The omni-ring encoding | **Measured** (L2; P1) | Tony Plate |
| 71 | Fractional power encoding = random Fourier features | Continuous values as powers of a phase vector; similarity is a kernel | Durations, positions, sensors | **Measured†** (sinc kernel); positions **Measured** (P2 §4.6) | Plate; Frady and colleagues (2021–22); Rahimi and Recht (2007) |
| 72 | Gaussian processes; kernel regression | Regression through a kernel | Possible in the same vectors (booklet Part IV) | **Proposed** | Field-known |
| 73 | Hadamard matrices; fractional factorial design | Orthogonal ±1 runs estimate many effects at once | `science.factorial` (5.6× fewer runs); deterministic perturbation directions | **Measured** (P5 §3) / directions **Measured**, worse than random (P5 §6) | Jacques Hadamard; R. A. Fisher; Box and Hunter; Bhatnagar (2003) |
| 74 | Harmonics; balanced harmonic sets | Integer multiples of a fundamental | Phasor layouts; exact solids (L8) | **Measured** (L8) | Field-known |
| 75 | Beat frequency √(Δω² − 4K²) | Two detuned oscillators drift at their difference | The dissonance reading (L13) | **Measured** (L9); the calendar-by-beat idea **Dropped** (P5 §3) | Field-known (Adler) |
| 76 | Time–frequency uncertainty; Nyquist and aliasing | Narrow bands need long windows; undersampling folds frequencies | The shared rhythm bus (L15); band spacing (R13) | **Measured** (L15, diagnostic) | Dennis Gabor; Harry Nyquist; Claude Shannon |
| 77 | Frequency-division multiplexing | Many bands on one channel | Rhythms on one bus (L15) | **Measured** (L15); bundle "OFDM normalisation" **Dropped** | Field-known |
| 78 | Spread spectrum; Gold codes | Near-orthogonal codes share one channel | An analogue of bundling | **Dropped** (separation was already 28× at D 5,120) | Robert Gold (1967) |
| 79 | Huygens wavefront as breadth-first search | Each frontier point makes the next frontier | The `search.wave` bitmask wavefront for A* | **Measured** (P5 §3) | Christiaan Huygens; Moore (BFS, 1959) |
| 80 | Wavelets; mel spectrograms | Multi-scale time–frequency transforms | A proposed audio shelf | **Proposed** | Field-known |
| 81 | Signed-distance blur and closed-form soft shadows | A Gaussian-blurred box has an exact formula | Orbit's shadows and glass | **Built** (doc 33) | Field-known |
| 82 | Contrast ratio for legibility | Text must clear 4.5 : 1 against its background | The law that fixed Orbit's grey-out | **Measured** (doc 33) | W3C, *Web Content Accessibility Guidelines* 2.0 (2008) |

## 5. Probability and statistics

| # | Concept | In plain words | How we use it | Status | Credit |
|---|---|---|---|---|---|
| 83 | Superposition capacity law Φ(a√(D/n))^(C−1) | How many items fit before recall fails | Capacity planning everywhere | **Measured** (L1) | Form and constant are ours; built on Kanerva, Plate, and Frady, Kleyko and Sommer |
| 84 | Central limit theorem | Sums of many small noises are Gaussian | The basis of L1 | **Field fact** | de Moivre; Laplace |
| 85 | Large deviations; Chernoff–Hoeffding bounds | Exact exponential tails for rare events | Proposed for guaranteed false-match rates | **Proposed** (one use **Dropped**: block votes are not independent) | Herman Chernoff (1952); Wassily Hoeffding (1963) |
| 86 | Extreme-value (Gumbel) margin | The gap between the best and second-best match follows a Gumbel law | Exact abstention (L17) | **Proposed** (pre-registered) | Emil Gumbel |
| 87 | Laplace approximation; Taylor expansion | Fit a Gaussian at the peak by its curvature | The Laplace tail fit was retracted; the Taylor step gave L9's closed form | **Dropped** (Laplace) / **Measured** (Taylor in L9) | Pierre-Simon Laplace; Brook Taylor |
| 88 | Binomial, multinomial and trinomial distributions | Counts over 2, K or 3 outcomes | Exact score tails | **Proposed** | Field-known (Bernoulli) |
| 89 | Sequential probability ratio test (SPRT) | Stop sampling as soon as evidence crosses a bound | `science.factorial`; a flawed law caught and amended | **Measured** (P5 §2) | Abraham Wald (1945) |
| 90 | Log-domain evidence; softmax; log-sum-exp; calibration | Add log-odds, then normalise | L7; stable softmax is a math-core concept | **Measured** (L7; doc 40) | John Bridle (1990, "softmax"); Ludwig Boltzmann |
| 91 | ROC and AUC | How well a score separates two groups | The vibration warning (L12); harmony scoring | **Measured** (L12; P2) | Field-known (signal detection theory) |
| 92 | Pre-registration; PASS and KILL bars | Fix the bar before the run | Every probe in this corpus (R12) | **Built** (method; R12) | Field practice; R. A. Fisher's experimental design |
| 93 | Zero-failure bound ("rule of three") | With zero errors in n independent rows, error < ε with confidence 1 − δ once n ≥ ln(1/δ)/ε | The growth gate's 300 rows per skill | **Built** (doc 27) | Hanley and Lippman-Hand (1983) |
| 94 | Von Mises noise | Gaussian noise on a circle | The phase-noise model in calibration runs | **Built** | Richard von Mises |
| 95 | Causal graphs; do-calculus | Separate seeing from doing | A proposed causal shelf and generator | **Proposed** | Judea Pearl |
| 96 | Metamorphic testing | Answers must transform with the frame | Free extra rows and a consistency check: 21 of 21 domains | **Measured** (P5 §6) | Chen, Cheung and Yiu (1998) |
| 97 | Statistical power; proper scoring rules | Enough samples to see an effect; honest probability scores | Planned for the ethics generator | **Proposed** | Field-known (Brier, 1950) |
| 98 | Entropy, cross-entropy, KL divergence | Bits of surprise; distance between distributions | Every language-model evaluation; distillation | **Measured** (P5 §4; docs 24–29) | Claude Shannon (1948); Kullback and Leibler (1951) |
| 99 | Expectation–maximisation; hidden Markov models | Fitting hidden variables | Background only | **Proposed** (mention) | Dempster, Laird and Rubin (1977); Baum |

## 6. Dynamics and physics, used literally

| # | Concept | In plain words | How we use it | Status | Credit |
|---|---|---|---|---|---|
| 100 | Kuramoto model; Adler equation | Coupled oscillators lock above Kc = Δω/2 | Dual clocks and coupling, the author's "breath" (L9) | **Measured** (L9) | Robert Adler (1946); Yoshiki Kuramoto (1975) |
| 101 | Saddle-node on invariant circle (SNIC) | The lock "snap" is one tipping point | L9's closed form | **Measured** (L9) | Field-known (bifurcation theory) |
| 102 | Hopf bifurcation; Stuart–Landau oscillator | The birth of a steady rhythm; its normal form | Heads hum their phase onto a bus (L13) | **Measured** (L13, diagnostic) | Eberhard Hopf (1942); Stuart; Landau |
| 103 | Arnold tongues; circle map | Lock regions in detuning and coupling | Proposed for the calendar | **Dropped** (integer coincidence is CRT, not phase drift) | Vladimir Arnold |
| 104 | Attractor networks; Hopfield clean-up | The state rolls downhill to a stored pattern | Clean-up memory; resonator settling (R3) | **Measured** (R3; P3 §4) | John Hopfield (1982) |
| 105 | Modern Hopfield networks = attention | Softmax attention is one step of a dense associative memory | The sift as attention | **Proposed** | Ramsauer and colleagues (2020) |
| 106 | Resonator networks | Iterative unbinding of a product of codewords | Factor decode; moved to the partitioned resonator after it fell short | **Measured** (P1; P4 §6) | Frady, Kent, Olshausen and Sommer (2020) |
| 107 | Limit cycles in iterated maps | The state repeats instead of settling | Found in an IFS perturbation test | **Measured†** (KILL) | Field-known |
| 108 | Continuous (bump) attractor | A ring of units holds a movable bump | Focus steering (L16) | **Measured** (L16, provisional) | Kechen Zhang (1996); Burak and Fiete (2009) |
| 109 | Critical slowing; residual vibration | Systems near failure relax slowly | Escalate a settle that is still moving (L12, A15) | **Measured** (L12) | Field-known (critical transitions) |
| 110 | Energy minimisation; Lyapunov functions | Dynamics that descend an energy | The resonator; equilibrium propagation | **Built** | Aleksandr Lyapunov |
| 111 | Chaos; Lyapunov exponents | Sensitive dependence on starting state | An asynchronous resonator arm | **Measured†** (no better than soft) | Field-known |
| 112 | Ising model; simulated annealing | Energy landscapes of ±1 spins; cool slowly | Explored for factorisation | **Proposed** | Ernst Ising; Kirkpatrick, Gelatt and Vecchi (1983) |
| 113 | Reversible computing; Landauer's principle | Invertible steps need not erase information | Integer reversible 2T blocks: activations 8× smaller | **Measured** (P5 §6) | Rolf Landauer (1961); Charles Bennett |
| 114 | Symplectic integrators | Physics stepping that keeps energy | A proposed micro-world generator | **Proposed** | Field-known |
| 115 | Kaluza–Klein circle; Wick rotation | A hidden circular dimension with whole-number charge; real ↔ imaginary time | The spectral view; "two read modes" | **Proposed** (structure) | Theodor Kaluza; Oskar Klein; Gian-Carlo Wick |
| 116 | Holography | Every part holds the whole; many patterns read by reference beams | Holographic plates; rotation codebooks | **Measured** (P5 §5) | Dennis Gabor (1948) |
| 117 | Paraxial and thin-lens approximation | Small-angle linearisation of optics | Suggested for the clocks; retracted (flattening deletes the snap) | **Dropped** | Field-known (Gauss's optics) |
| 118 | Grid and place cells | The brain's hexagonal, periodic spatial code | Kin of the attractor field; the torus of R17 | **Proposed** | O'Keefe; Moser and Moser; Fiete, Burak and Brookings (2008); Gardner and colleagues (2022) |
| 119 | Zoom-lens attention | The beam's area trades against resolution | The spark margin drives the sift threshold | **Proposed** | Eriksen and St. James (1986) |
| 120 | Spiking networks; Hebbian learning | Local "fire together, wire together" updates | Explored for training | **Proposed** | Donald Hebb (1949) |
| 121 | Cellular automata | Local rules on a lattice, running continuously | The "fires constantly" substrate idea | **Proposed** | von Neumann; Ulam |

## 7. Learning and optimisation

| # | Concept | In plain words | How we use it | Status | Credit |
|---|---|---|---|---|---|
| 122 | Ternary quantisation (BitNet b1.58, absmean) | Weights in {−1, 0, +1} trained through float latents | The trunk, heads and core model; absmean is a math-core concept | **Measured** (P5 §4, §6; doc 40) | Ma and colleagues, Microsoft Research (2024) |
| 123 | Latent-free binary optimisation (Bop) | Flip a weight when a momentum counter crosses a threshold | Residue flip counters as the whole optimiser state | **Measured** (P5 §6) | Helwegen and colleagues (2019) |
| 124 | Zeroth-order gradients (SPSA, MeZO) | Estimate gradients from forward passes only | Forward-only dial training; it did not hold | **Measured** (P5 §6, negative) | James Spall (1992); Malladi and colleagues (2023) |
| 125 | Equilibrium propagation | Learn from a free settle and a nudged settle, without a backward pass | Resonator heads: cosine 0.984 to the exact gradient | **Measured** (P5 §6) | Scellier and Bengio (2017) |
| 126 | Selective backprop | Skip the backward pass on tokens already learned | The spark skip | **Measured** (P5 §6) | Jiang and colleagues (2019) |
| 127 | Fixed classifier | Never train the output head | The frozen seeded head | **Measured** (P5 §6) | Hoffer and colleagues (2018) |
| 128 | Block-coordinate descent on coprime schedules | Update one block at a time, on a rhythm | The coprime block rhythm | **Measured** (P5 §6) | Field-known (FreezeOut kin) |
| 129 | Exact decentralised training (residue all-reduce) | Integer sums give the same answer in any order | Bit-identical multi-machine training | **Measured** (P5 §6) | Douillard and colleagues (DiLoCo, 2023), for the setting |
| 130 | Plasticity loss; recycling dormant units | Networks stop learning; reset the idle units | Proposed sleep cycles | **Proposed** | Dohare and colleagues (2024) |
| 131 | Knowledge distillation | A student copies a teacher's outputs | Reflex heads; rule labellers | **Measured†** | Hinton, Vinyals and Dean (2015) |
| 132 | Rotary position encoding against residue clocks | Positions as rotations | Position arms in the ternary trunk | **Measured** (P5 §5) | Su and colleagues (2021) |
| 133 | Linear attention; fast weights | Attention as a running sum | The holographic plate memory | **Measured** (P5 §5) | Katharopoulos and colleagues (2020); Schlag and colleagues (2021); Teuvo Kohonen (1972) |
| 134 | Locality-sensitive hashing | Hash keys to buckets instead of scanning | A field baseline for residue-addressed memory | **Proposed** | Indyk and Motwani (1998) |
| 135 | Random projection and random indexing | Encode without training | Encoder-free embeddings | **Measured†** | Johnson and Lindenstrauss (1984); Kanerva (random indexing) |
| 136 | Whitening | Remove the mean and correlation before bundling | R6 | **Measured** (R6; P3 §6) | Field-known |
| 137 | Clustering; inverted-file indexes | Cluster first, then search within | The sphere sift; killed below 9,000 marks per head | **Measured** (P2 §4.3, KILL) | Jégou, Douze and Schmid |
| 138 | Mixture of experts; routing | Send each input to a few experts | Heads as shards; simplex routing | **Measured** (P5 §5, routing) | Jacobs, Jordan, Nowlan and Hinton (1991) |
| 139 | Low-rank adaptation; SVD | Cheap updates in a low-rank subspace | Explored | **Proposed** | Hu and colleagues (LoRA, 2021) |
| 140 | Model merging | Combine fine-tuned weights | The daily merge of harnesses into one core | **Measured** (docs 24–26) | Field-known (weight averaging; task arithmetic) |
| 141 | State-space models; speculative decoding | Linear-time sequence models; draft, then verify | Solver-drafted speculative decoding | **Measured** (P5 §6) | Gu and Dao (Mamba, 2023); Leviathan and colleagues (2023) |
| 142 | Frame-first generation | Write the proof frame, then fill it in | R4: 1.00 against 0.24 | **Measured** (R4) | Field-known (proof planning) |
| 143 | Rehearsal against forgetting | Keep reviewing old material while learning new | The round guard and the 20 % review share | **Measured** (docs 25–26) | Field-known (continual learning; Robins, 1995) |
| 144 | Reservoir computing | A fixed random recurrent network with a trained readout | The ternary reservoir probe: all ten arms missed | **Measured** (doc 39, FAIL) | Jaeger (echo state networks, 2001); Maass (liquid state machines, 2002) |
| 145 | Rank fusion | Merge ranked lists by their ranks | Hybrid search; a weak list drags it down | **Measured** (doc 39) | Cormack, Clarke and Büttcher (reciprocal rank fusion, 2009) |
| 146 | BM25 and full-text search; SimHash | Ranked keyword search; a fingerprint for near-duplicates | The substrate; the perception cache | **Measured** (P2 §8.1) | Robertson and Spärck Jones; Moses Charikar (2002) |

## 8. Information and coding

| # | Concept | In plain words | How we use it | Status | Credit |
|---|---|---|---|---|---|
| 147 | Superposition is not compression | Geometry costs 6–9× the identity bits | L3: the value is operability | **Measured** (L3) | Ours (the measurement) |
| 148 | Signal-to-noise; channel capacity | Signal against crosstalk | The basis of L1 and sift margins | **Measured** (L1) | Claude Shannon (1948) |
| 149 | Error-correcting codes; parity | Redundancy that detects or fixes errors | Check rings; RRNS | **Measured** (L6) | Richard Hamming (1950) |
| 150 | Equiangular tight frames; the Welch bound | The best packing of more vectors than dimensions | ETF codebooks; L17 | **Proposed** | Lloyd Welch (1974) |
| 151 | Native-form compression | A shorter notation for the same reasoning trace | Native forms: 1.3–5.3× fewer tokens | **Measured** (P5 §3) | Ours (the measurement) |
| 152 | Hash chains; Merkle trees; receipts | Linked hashes that show any edit | The clean-room and growth ledgers; receipts; trial-and-commit | **Measured** (P5 §6; docs 27, 38, 41) | Ralph Merkle (1979); Haber and Stornetta (1991) |
| 153 | Minimum description length; Kolmogorov complexity | The shortest description is the best model | Proposed as a gate for self-rewrites | **Proposed** | Jorma Rissanen; Andrey Kolmogorov |

## 9. Computation and compilers

| # | Concept | In plain words | How we use it | Status | Credit |
|---|---|---|---|---|---|
| 154 | JIT code generation | Emit machine code while running. In our vocabulary, to "render" | The rendered sift, the T25 and T50 cores, the doctor kernel | **Measured** (P4 §1; docs 30, 36) | Field-known (LLVM ORC and MCJIT, cited in P4) |
| 155 | Programs as vectors | A program stored as a hypervector and rewritten while it runs | The source; the self-rewriting sifter | **Measured** (P3 §4; P4 §1) | Field-known; Hanley (VSA-Lisp, 2025) as kin |
| 156 | Finite-state machines as plates | State × input → next state in one plate | Holographic and layer cores | **Measured** (P5 §5) | Field-known (Mealy; Moore) |
| 157 | Lookup tables; SWAR and AVX2; byte shuffles | Precompute, then index | The inverse plate; the 16-phase tables; the tiled sift | **Measured** (L10; P5 §3) | Field-known |
| 158 | Roofline; memory-bound against compute-bound | Speed is capped by bandwidth unless data stays in cache | L10, A13 | **Measured** (L10) | Williams, Waterman and Patterson (2009) |
| 159 | Exact lookups through SQL and Datalog | Relational engines beat similarity for exact keys | R5 | **Measured** (R5; P2 §8) | Edgar Codd (1970) |
| 160 | Grammar-constrained decoding | A stack machine emits only balanced code | Seed code shelf | **Proposed** | Field-known (pushdown automata) |
| 161 | A* and breadth-first search | Shortest paths | The tiled A* domain | **Measured** (P5 §3) | Hart, Nilsson and Raphael (1968) |
| 162 | One IR, many back-ends | Compile one specification to several languages | SuperSeed: kernels proven bit-identical across languages | **Measured** (P2 §2) | Field-known |
| 163 | Array languages (APL, J, K) | Programs over whole arrays | A head instruction set | **Proposed** | Kenneth Iverson |
| 164 | Lambda calculus and combinators in vectors | Functions as bound vectors | Explored for the ring instruction set | **Proposed** | Alonzo Church; Moses Schönfinkel; Haskell Curry |
| 165 | GPU compute for "3-D code" | Geometry in addressing, run as a shader | The cyclone array and the GPU school step | **Measured** (docs 28–31); on the laptop's integrated GPU **Dropped** (L10) | Field-known |
| 166 | Undecidability; step budgets | Non-termination cannot be detected in general | A step budget plus abstention replaces the "Gödel sentinel" | **Built** (rule adopted) | Alan Turing (1936) |
| 167 | Stigmergy | Coordination through marks left in the environment | The fleet's field marks and board | **Built** | Pierre-Paul Grassé (1959) |
| 168 | Maximum flow and minimum cut | The narrowest point between two places in a network | The exact reference for the array's bottlenecks | **Measured** (doc 31) | Ford and Fulkerson (1956) |
| 169 | Gomory–Hu tree | All pairwise minimum cuts from n − 1 max-flow runs | The field answer the dual T50 cut read was checked against | **Measured** (doc 31) | Ralph Gomory and T. C. Hu (1961) |
| 170 | Stoer–Wagner global minimum cut | The smallest cut of a whole graph | The check on the 1,155-toroid layout | **Measured** (doc 31) | Mechthild Stoer and Frank Wagner (1997) |
| 171 | Cut read from two interlocked ring counters | The minimum cut between any two toroids, read from two traffic tables in a few lookups | The dual T50 bottleneck finder | **Measured** (doc 31) | The author's idea (2026-10-09); ours |
| 172 | Name-free specifications (clean room) | Describe what a function does with no names from its source | The two-team clean room made of doctor cores | **Measured** (doc 37) | Clean-room practice is field-known; the all-core form is the author's |

## 10. Teaching pictures

These are maps, not mechanisms. They are kept because they helped, and each says where the map stops.

| # | Picture | What it maps to | Status | Credit |
|---|---|---|---|---|
| 173 | Jump ropes turning at 3, 5 and 7 beats | CRT: the ropes line up again only at the product | **Picture**, mapping to row 1 (measured) | The author |
| 174 | The arc reactor | The ring system with a core at its centre and tiers turning in opposite directions | **Picture**; the hub is measured (doc 30) | The author, after the fictional reactor |
| 175 | "Toroids all the way up" | Ring systems within ring systems | **Picture**; three floors failed their check (doc 30) | The author |
| 176 | The conveyor belt that changes speed (BELT) | A batching scheduler | **Picture**, mapping to a built scheduler (L10; doc 38) | The author |
| 177 | Square peg, square hole | A box is wrong when its shape departs from the one it should have | **Picture**, mapping to the shape station (doc 35) | The author |
| 178 | Tesla coil | Two tuned coils trading energy, as the sift "resonates" with a query | **Picture** | Nikola Tesla (the device) |
| 179 | Faraday cage | An orthogonal "zero" space | **Picture** | Michael Faraday |
| 180 | Bohr atom, orbitals, Pauli exclusion | Shells with fixed capacity | **Picture**; "quantum numbers work like an RNS" was **Dropped** | Niels Bohr; Wolfgang Pauli |
| 181 | Wave function, interference | Superposition = bundling, interference = inner product, measurement = clean-up | **Picture**; the inner-product part is real (rows 69–70) | Erwin Schrödinger |
| 182 | Chladni plates; "reading the zeros" | Novelty from zero-amplitude nodes | **Dropped** (faint recall, not novelty) | Ernst Chladni |
| 183 | Crystal or hologram fleet | Shared state as one interference pattern | **Picture** | Field-known |
| 184 | Relativity (frames) | Laws the same in every frame | **Picture**, which became metamorphic testing (row 96) | Albert Einstein |
| 185 | Breathing, heartbeat, synapses, brain waves | Coupling (L9), ticks, sparks | **Picture**; breathing inside a model is untested (A14) | Field-known |
| 186 | Schumann resonance; impedance matching | Fleet tuning | **Picture** | Winfried Otto Schumann |
| 187 | Orbits and Kepler | Rings and lanes | **Picture** | Johannes Kepler |
| 188 | Polyphase AC; the Columbus egg | Staggered execution | **Dropped** as engineering | Nikola Tesla |
| 189 | "Free energy" | A settle that costs nothing | **Dropped** (every settle costs compute) | — |
| 190 | Dunbar's number; Gall's law; evolution | Group size limits; complex systems grow from simple ones; mutation with selection | **Picture** (heuristics) | Robin Dunbar; John Gall; Charles Darwin |

---

## The ten concepts the math core holds, and the laws it checks

The math core (doc 40) keeps ten of these concepts as live programs. Each has a name-free specification, a law that is
a property (never the definition restated), verified Rust code and a generator with an independent check. Every law
has "teeth": break the subject on purpose and the law must fail. The laws, in plain words:

| Concept | Law the core checks | Credit |
|---|---|---|
| CRT (row 1) | For coprime m₁ and m₂, x → (x mod m₁, x mod m₂) hits every pair of residues exactly once on [0, m₁m₂) | *Sunzi Suanjing*; Gauss |
| Mixed radix (row 8) | A mixed-radix value split back by divmod returns its digits | Garner |
| Barrett reduction (row 11) | With k = 16, μ = ⌊2³²/m⌋ and at most two corrections, it equals a mod m for 2 ≤ m < 2¹⁶ and 0 ≤ a < m² | Barrett |
| Hamming distance (row 22) | It is a metric: zero on itself, symmetric, triangle inequality. Teeth: popcount(a OR b) passes the triangle and symmetry but fails identity | Hamming |
| Integer square root (row 18) | Integer Newton from x₀ = n stops at r with r² ≤ n < (r+1)² | Heron; Newton |
| Period (row 19) | The smallest period p reproduces the sequence: v[i] = v[i mod p] | Field-known |
| Absmean ternary quantisation (row 122) | Values land in {−1, 0, 1} and never flip a weight's sign | Ma and colleagues (BitNet b1.58) |
| Stable softmax (row 90) | Sums to 1, is shift-invariant, and pᵢ/pⱼ = exp(xᵢ − xⱼ). Teeth: exp(x/10) passes the first two and fails the ratio | Bridle |
| Fibonacci (row 20) | Cassini's identity: F(n−1)F(n+1) − F(n)² = (−1)ⁿ | Leonardo of Pisa; Cassini |
| Clock read (row 1) | Reading a time back from its residues on rings 3, 5 and 7 returns the time (period 105) | CRT; the rings are ours |

Two first-draft laws were too weak (Hamming and softmax). When the teeth check broke their subject they still passed,
so they were strengthened. The knowledge base ships as `docs/appendix/math-kb/mathkb.json` (data, CC BY 4.0), with
`check_laws.py` to test it (see "Put this list to work").

## Concepts that are ours

These we did not find described elsewhere in the sources we searched. They are dated here as prior art, and none is
claimed as first without a wider search. Each was the author's idea, built and measured with the fleet:

- **The check ring** inside a coprime ring memory, with a cue-driven resonator that abstains (P1).
- **SuperSeed**, an integer-only portable specification with golden-hash conformance (P2).
- **The triangle memory** (P2).
- **Designed codebooks** from their Gram matrix, and **4-D cores** as byte tables (P3).
- **The source**, a program vector read every tick (P3).
- **The fitted capacity law** and the measured laws L12–L15 (booklet).
- **The circular curriculum** applied to a ternary model, with a round guard and a growth gate at 100 % (docs 24–27).
- **The T50 hub and the cyclone array**, and **the dual T50 cut read** (docs 30–31).
- **The doctor**, which repairs our own code geometrically, and **a clean room made entirely of doctor cores** (docs
  34–37).

## Ideas that did not hold

We keep these because a list that shows only successes cannot be trusted.

1. **A Barrett kernel for the coprime moduli** was not needed: the compiler already turns `x % const` into
   multiply-and-shift.
2. **"Quantum numbers work like a residue system"**, "atoms bond through zero nodes" and "Pauli slot spillage" were
   rejected. Quantum numbers are nested, while coprime rings are independent.
3. **"Twelve pentagons are twelve edge channels"** was numerology. The code it described never existed.
4. **"Flat 180–250σ across superposition depth"** was wrong. The measured contrast fell 102 → 32 → 11 → 5.5σ;
   crosstalk is statistical, and crowded slots read 66 %, not 100 %.
5. **Normalising bundles "for unitarity"**, "reading the zeros" for novelty, and "free energy" were all rejected.
6. **L1 as one universal law** failed in the overload tail (CAL-2).
7. **"Chernoff gain grows with block size"** for block votes was refuted: the votes are not independent under noise.
8. **Two claims about a positions experiment** did not hold. "It fed raw integers" was false: the fix was what ran.
   "100 % copy to 8k" was never tested, and the copy metric was broken in every arm.
9. **"The resonator failed because of ReLU"** was refuted. Phase-only and asynchronous variants were no better than
   soft decoding.
10. **"The attractor bump is proven"** overstated the result: move and hold passed, release failed (L16 stays
    provisional).
11. **"Zero aliasing" on the shared rhythm bus** was wrong: events merge when the window nears their spacing (L15).
12. **"Near-infinite signal-to-noise" on the ten-ring torus** was wrong: the worst distractor, at 0.81–0.92, sets the
    margin.
13. **Figures quoted in reviews out of their context** (0.71 ms over 10¹¹; 128 marks in 0.46 ms; "11,108× faster")
    were conflated. The 11,108 in MEM-0 is a ratio of bytes moved; the time ratio was about 492
    (`docs/appendix/geometric-laws/mem0.result.json`).
14. **Positions to 23,205 with rings 3·5·7·13·17** were wrong for our design: 17 is the check ring, so the address
    range is 1,365.
15. **A "Gödel sentinel" that detects undecidable cases** cannot exist in general. It was replaced by a step budget and
    abstention.
16. **"Belief revision = group inversion"** and **"science = wave cancellation"** were dropped.
17. **A misnumbered law ("Law 17")** was corrected. L17 is the extreme-value margin.
18. **The calendar by Arnold tongues or beats**, and **primality by residue contradiction**, did not hold as stated.
    They became scoped successes through the CRT orbit and Miller–Rabin.
19. **"IFS perturbation breaks resonator limit cycles"** was wrong. A genuine IFS drives the resonator into them; the
    earlier result came from a harness that cancelled itself.
20. **The Laplace approximation, a paraxial model for the clocks, and a "trinomial theorem" for triangles** were all
    retracted.
21. **"Hadamard directions beat random for SPSA"** failed twice (P5 §6).
22. **Claims of exact non-commutative composition and of head separation** went beyond the evidence: only bucket
    capacity was measured.
23. **A GPU shader torus on the laptop** lost: the integrated GPU lost every head-to-head (L10).
24. **A cited paper said to show "memory retrofits give marginal gains"** was miscited: that work fine-tunes, while
    ours froze the model.

## Ideas still waiting for a probe

| Idea | Why it could matter | Cheapest probe |
|---|---|---|
| A large-deviation or exact multinomial law for L1's overload tail | Capacity past the knee has no law | Fit the existing overload points; no new runs |
| Characters for exact crosstalk on 2T and the torus | Could explain L11's 1.59 against 2.0 | Compute the character inner products for the triangle triple |
| Gaussian-process reasoning in fractional-power vectors | Regression with uncertainty, with no trained encoder | Kernel ridge regression on encoded durations against a plain GP |
| Modern Hopfield energy as the sift (β = spark margin) | Gives the sift a temperature and a convergence guarantee, linked to L17 | One dense-Hopfield step against top-k sift on ring-head data |
| Causal and concept-lattice generators | Cheap new verifiable reasoning domains | Add both, with independent verifiers, and run 200/200 self-tests |
| Space-filling layout for plates | The sift is memory-bound (L10) | Reorder plate rows by Morton key and time it |
| Grassmannian codebooks when C > D + 1 | The simplex frame stops existing past D + 1 items | Random against packed codebooks under L1 |
| Annealed noise in the resonator | Might close the resonator gap | One annealed arm in the existing harness |
| Merging ternary heads | Combine shards without retraining | Merge two heads and check both tasks |
| Description length as the rewrite gate | A principled "is this worth keeping" score | Score induced plates by length against replay pass rate |
| A symplectic physics generator | Verifiable physics reasoning | A spring-mass generator with an energy-drift check |
| Combinators on the 2T core | A tested form of programs as vectors | Encode S and K on 2T and reduce five terms |

## How this list grows

A concept enters this list the first time it appears in a plan, a harness or a disclosure. When it is measured, its
status changes and its reference is added. When the math core cements a law for it, the law joins the table above.
Rows are never deleted. An idea that fails stays, marked **Dropped** with the reason, and the thanks stay too.

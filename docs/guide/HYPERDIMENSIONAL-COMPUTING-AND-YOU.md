# Hyperdimensional Computing and You

*A plain-language guide to what we are building, why, and how: the field we stand in, the ideas we borrowed, the parts
we added, and how to start using them.*

> *"We are resonators; everything we build then becomes another resonator to build off from. Develop us well."*

| | |
|---|---|
| **Date** | 2026-10-10 (second edition; first edition 2026-10-01) |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 |
| **AI assistance** | Compiled with AI assistance (Claude) and the Sovereign Raptor Fleet System from the author's research conversations (unpublished), the experiment record and the math core's knowledge base. The author reviews it before publication. |
| **Covers** | vsa-core 0.1.0; omni-ring (Technical Disclosures Parts 1–7); omnitool 0.1.0; the cores (T25, T50, the doctor, the math core) |
| **Status of claims** | Measured results are cited to the disclosures (`P1`–`P7`, plus `P6`, the omni-render disclosure), a repository's `DOSSIER.md`, a numbered research document (`doc NN`), or a law in the geometric booklet (`L1`–`L17`). Anything else is marked **Design** (specified, not yet measured) or **Speculative**. |

**What changed in this edition.** The first edition covered the memory (Parts 1 and 2). This one adds:

- the four-dimensional cores and the program that runs as a vector (P3–P4);
- our own training engine and the school that teaches the model (P5, P7);
- the ring cores T25 and T50 (P7);
- the doctor (P6–P7).

It is also rewritten in simpler words, with the author's own explanations kept in place. The axioms and laws now have a
booklet of their own: `GEOMETRIC-COMPUTING-AND-YOU.md`. Every concept we used, with thanks to the people behind it, is
in `MATH-CONCEPTS-AND-THANKS.md`.

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

## 1. Start here: the idea in one page

A normal program keeps each fact in one place: a row in a table, a field, a variable. To find it, you need its address.

**Hyperdimensional computing** (HDC), also called **vector-symbolic architectures** (VSA), works differently. Every
symbol, record, sequence and even program becomes one very long list of numbers, thousands of entries long. Three facts
make that useful.

**1. Random long lists almost never look alike.** Pick two lists of 5,000 random entries and they will be nearly
unrelated, every time. So you can hand out millions of distinct symbols without ever checking for clashes. The booklet's
short version: *strangers are almost always unrelated.*

**2. Three moves build any structure.**

- **Bind** (⊗) joins two lists into a third that looks like neither, such as "colour = red". The same key undoes it
  exactly. The author's reading: *what a key joins, the same key can undo.*
- **Bundle** (+) adds lists together into one that still resembles each part: a set, a bag, a memory slot. The
  author's reading: *an individual can become part of a whole, yet it is still an individual: each voice stays itself
  inside the chorus.*
- **Permute** (ρ) shuffles the entries to mark order or position.

**3. Clean-up gives back the exact symbol.** After you unbind something from a crowded bundle, the result is noisy.
Compare it with the list of symbols you know, and the nearest one is your answer. If nothing is close enough, the
honest answer is "I don't know".

That is the whole toolkit. A record like *(colour: red, shape: ball)* becomes `colour⊗red + shape⊗ball`. To ask "what
colour?", unbind with `colour` and clean up. The answer is `red`.

There is a price. Every item you add to a bundle adds a little noise. The author put it this way: *"There are many
truths, but with more truths come more half lies."* How many items fit before the answers go wrong is something we
measured; it is law L1 in the booklet.

## 2. Why we are doing this

The mission is to put capable, verifiable AI on the computers people already own, and to publish every piece as dated
prior art, with no patents.

The author's reasons are practical. On 3 October: *"how can our geometric computing bring back legacy hardware and move
people away from overpriced tech, saving landfills from thousands of old devices. I'm not looking for a 1-10%increase,
I believe this field we are developing is key to this and many more feats."* A day earlier, from a laptop running hot:
*"can we apply this to regular apps/computing to make legacy hardware viable for daily use again? I don't think these
are the limits of what we can do yet."*

The work is also personal problem-solving, done in the open. In the author's words, it means *"developing geometric
computing and HDC fields through my research and applying them to real life challenges I face to solve my own
problems, then release the code for it."*

And the author has been honest about learning on the way: *"I have honestly not learned much of the field/subject other
than what i've learned to get to this point."* That is why this guide exists. It is a map for people who, like the
author, came to this field by building rather than by study.

**How we work.** Everything here runs on a 2019 laptop CPU first, then an integrated GPU, then second-hand desktops,
and only then a rented server. Every experiment writes its pass and fail bars down before it runs, and failures are
published as measured. In the author's words: *failures reported as registered.*

## 3. The words you need

- **Vector.** A long list of numbers. In omni-ring each list has 5,120 entries (10,240 in the ternary view), and every
  entry is a small dial.
- **Dial, phase.** One entry, a position on a circle: one of 16 positions, or −1 / 0 / +1 in the ternary view.
- **Mark.** One small stored record, such as "task 412 finished at beat 57".
- **Slot.** One vector that holds several marks bundled together.
- **Ring.** A counter that wraps around, like the hours on a clock. A ring of size 7 counts 0 to 6 and starts again.
- **Coprime.** Sizes that share no factor, like 3, 5 and 7.
- **Residue.** The remainder a ring shows: 23 on a 7-ring shows 2.
- **Check ring.** An extra ring that carries no new information. It exists so that a wrong answer shows up as
  disagreement.
- **Cue.** Something you already know, pinned in place before reading, such as "it was the 5-ring at position 3".
- **Resonator.** A procedure that looks at a slot and works out which position of each ring produced it.
- **Sift.** Compare a cue with every candidate and keep the best match.
- **Core.** In our vocabulary, a processor: a program generated as machine code while the system runs (we say
  "rendered") that fires constantly while active. In the author's words: *"the cores are jit rendered programs that fire
  constantly when active."*
- **T25, T50.** Ring systems of 25 and 50 rings. T25 uses the 25 odd primes from 3 to 101; T50 adds the next 25, up to
  233.
- **Trit, ternary.** A value that is −1, 0 or +1. Our model's weights are trits.
- **Abstain.** Answer "I don't know" when the evidence is not strong enough.

## 4. The rings, the way the author pictures them

The rings started as a picture, not an equation. The author imagines jump ropes, each turning at its own rhythm: one
every 3 beats, one every 5, one every 7. A jumper standing among them is touched by each rope at a different moment.
After 3 × 5 × 7 = 105 beats the pattern repeats, and not before. So the moment each rope touches the jumper names the
beat exactly. Mathematicians call this the **Chinese Remainder Theorem**; it was first written down in a Chinese
arithmetic book, the *Sunzi Suanjing*, more than fifteen hundred years ago.

In the author's words, from 7 October: *"it travels one notch every tick spinning on it's axis like a jumprope. the
core sets the system overal directin."* And: *"the speed should be accurate to the moduli ring system, if it;s 3,5,7,13
it should move in step, each system has it's own rythm but moves every tick."*

Here is what that picture became, step by step.

**A clock you can read without searching.** Store a mark by binding its position on each ring. Reading it back is a
jump, not a search: the rings' positions name the number directly. Omni-ring's four rings (3, 5, 7, 13) give 1,365
exact addresses (P1).

**A check ring that catches mistakes.** Add a fifth ring, 17, whose position is fully set by the other four. If any one
ring slips, the five no longer agree, and the memory refuses the answer. It caught 100 % of single-ring slips (P1;
L6). It catches honest mistakes, not forgers: a random vector still passes about 4 times in 10,000 (L6). In the
booklet's words: *an echo catches mistakes; only a secret stops forgers.*

**Peeling, which is the jump rope's own trick.** On 2 October the author asked about the picture: *"my jumprope
eliminates jumpers each time it hits the ground"*. Does the resonator not *"pull them all out at once?"* For one mark
it does: all the dials settle together. For many marks in one slot it does not, because a resonator settles on one
answer at a time. So you do the rope's move. Find one mark, check it, subtract its exact rhythm from the slot, and read
again. This is called **peeling** (explaining away). It read 16.65 true marks per crowded slot with no fakes (P1).

**Only a question rings the bell.** The memory never answers on its own. Give it a cue (one ring pinned) and it settles
reliably. Give it nothing and the result depends on luck (P1). The author's note: *resonance drives recall, and only a
question can ring the bell.*

**Toroids all the way up.** By October the picture had grown. A ring of rings is a torus, the doughnut shape, and the
author kept stacking them. On 6 October: *"I've a feeling it's toroids all the way up."* T25 became a core: one box on
a web page held as five numbers on 25 rings, one CPU register (P7; doc 36). T50 became the hub of a training array,
where 50 rings below 256 fit one byte each and one 512-bit register in all (doc 30). Then came the author's arc reactor
picture: *"the core is what spins left or right, causing resonance and amplification, like my arc reactor vision."* In
the array, each ring moves one notch per tick at its own rhythm, exactly as the jump ropes do.

**Two rings that count.** The latest step, from 9 October: two interlocked T50 systems that count traffic as it moves.
The author's statement: *"interlocking two 50t omniring systems would solve this computation in much less time by
relying on the massive rapidly moving and counting outer rings."* It worked the first time it was measured. The
narrowest point between every pair of 105 toroids was read from two counting tables in 8.1 ms, against 151 ms for the
textbook method, with every pair equal (doc 31).

## 5. Where the field came from

We did not invent hyperdimensional computing. These people did the work we build on:

| Idea | Who | What it gave everyone |
|---|---|---|
| Hyperdimensional computing; sparse distributed memory | Pentti Kanerva | The case that long random vectors are a natural material for memory and thought; the "dollar of Mexico" analogy |
| Holographic reduced representations; fractional power encoding | Tony Plate | Binding by circular convolution, bundling, clean-up, and continuous values as fractional powers |
| The name "vector symbolic architectures" | Ross Gayler | A shared name and frame for the family |
| Resonator networks | Frady, Kent, Olshausen, Sommer | Iterative factoring of a bound vector into its unknown parts |
| Residue hyperdimensional computing | Kymn and colleagues | Coprime modular codes in vectors, combined by the Chinese Remainder Theorem |
| Grid-cell modular codes | Fiete, Burak, Brookings | The brain's picture of several periodic codes at once |
| Knowledge graphs on the torus and as rotations | Ebisu and Ichise (TorusE); Sun and colleagues (RotatE) | Relations as turns in phase space (trained by gradient) |
| Retraining HDC prototypes | Imani and colleagues | Error-driven refinement of bundles |
| Ternary networks (BitNet b1.58 and successors) | Microsoft Research and others | Weights in {−1, 0, +1} that run on ordinary CPUs |
| Quaternions; the 24-cell group 2T | W. R. Hamilton; Conway and Smith | Four-number rotations where order matters, as an exact 24-element table |
| The Hopf fibration | Heinz Hopf | The geometry that lets one vector hold *what* and *when* apart |

The full list, about 190 concepts with a thank-you to each, is `MATH-CONCEPTS-AND-THANKS.md`. Citations are in
`PROVENANCE.md` in each repository.

## 6. What is ours

Our part is engineering and measurement. We made these ideas exact, portable, checkable and useful on ordinary
computers. Each item is marked **new** (we found no earlier description in the sources we searched), **adapted** (a
known idea, our variant) or **borrowed** (used as published).

| Our component | Status | What it does, in plain words |
|---|---|---|
| Two-faced 2,560-byte slot (10,240 ternary dims ↔ 5,120 sixteen-level phases) | adapted | One block of memory you can read two ways (P1 §2) |
| Shared-memory blackboard | adapted | Many programs read one memory without locking each other out (vsa-core) |
| Sealed trust result | new | Every answer says how much to trust it (vsa-core §3) |
| Coprime rings + 17 check ring + a resonator that abstains | adapted | Catches 100 % of single-ring slips and says "I don't know" when unsure (P1 §3–4) |
| Peeling, diamond facets, decaying mark store | adapted | Reads crowded slots; structured records; recent things weigh more (P1 §6–9) |
| SuperSeed | new | Integer-only rules so every language and chip gives the same bytes (P2 §2) |
| Geometry of the sift (cubes, pyramids, lattices, golden-ratio frequencies) | adapted | The same exact answers about 12 times faster (P2 §4) |
| Triangle memory (omnitri) | new as a combination | Facts as triangles, checked by a second path, untrained (P2 §6) |
| Designed codebooks and 4-D cores (2T as a byte table) | new as byte tables | Shapes built on purpose; order kept exactly at 1–10 hops (P3 §2–3) |
| The source: a program stored as a vector | adapted | A loop that reads its own instructions every tick and refuses tampered ones (P3 §4) |
| The self-rewriting sifter | adapted | A program in the memory that rewrites itself while it runs (P4 §1) |
| Our own training engine and the ternary model | adapted | Training on a laptop CPU, matching PyTorch to 6e-7 (P5 §6) |
| The school: circular curriculum, round guard, growth gate | adapted | The model learns the next thing only when it has the last (docs 24–27) |
| T25 box core; T50 hub; cyclone array | new | Ring systems as cores, exact on CPU and GPU (docs 30, 36) |
| Dual T50 cut read | new | Finds an array's bottlenecks by reading two counting tables (doc 31) |
| The doctor and a clean room made of doctor cores | new as a combination | A small program that repairs our own code by its geometry (docs 34–37) |
| Deterministic agent-tool guard | new (omnitool) | Batches of agent tool calls repaired, checked and guarded before anything runs (omnitool §3–7) |

What we deliberately do **not** claim:

- That HDC beats an index at exact lookup. It does not (P2 §8).
- That bundling is free. Capacity is finite and measured (L1).
- That geometry makes arithmetic faster. The gains come from reusing bytes and skipping work (P2 §4.8).

## 7. How the pieces fit

```
          people, agents, apps
                  │  (batched tool calls)
            ┌─────▼─────┐
            │ omnitool  │  repair → validate → guard → execute          "the hands"
            └─────┬─────┘
                  │  marks, cues, telemetry
            ┌─────▼─────┐
            │ omni-ring │  rings, check ring, resonator, sift,          "the memory"
            │           │  triangles, 4-D cores, the source
            └─────┬─────┘
                  │  2,560-byte slots
            ┌─────▼─────┐
            │ vsa-core  │  shared-memory bus, trust result             "the nervous bus"
            └─────┬─────┘
                  │
      ┌───────────▼───────────┐
      │ the cores (rendered)  │  T25 box core, T50 hub, doctor,      "the reflexes"
      │                       │  math core, embed core
      └───────────────────────┘
```

- **vsa-core** is the bus: a block of shared memory where many programs read and write fixed-size vectors safely.
  Start here if you want several programs to share one memory.
- **omni-ring** is the memory: it writes marks into slots and reads them back by cue, resonance or exact sift, with a
  check ring and abstention. Parts 3–7 add the 4-D cores, the source, the training engine and the ring cores.
- **omnitool** is the hands: it lets language-model agents send batches of tool calls that are repaired, checked and
  guarded first. It does not need the other two.
- **The cores** are the reflexes: small deterministic programs, generated as machine code, that do one job every time
  they fire and leave a receipt. The author's view, from 4 October: *"we can make a new core for anything. we can put a
  new core into the harness that fit's its purpose and design."*

## 8. Put it to work

### Who gets what

| If you are… | What this gives you | Start with |
|---|---|---|
| **a developer on an ordinary computer** | exact addresses and timestamps without a search, memory that catches its own errors, and kernels that run on a CPU from 2019 | recipes 1–4 below, then `omni-ring` |
| **someone building AI agents** | a memory several agents can share without locks, answers that say how sure they are, and tool calls checked before anything runs | recipe 4, then `vsa-core` and `omnitool` |
| **a researcher or student** | every law with its pre-registered result and data, so you can rerun it, break it or extend it | the Geometric booklet, its Evidence table, and `docs/appendix/` |
| **someone with old hardware** | integer kernels, small memory, and no GPU needed. The reasons to keep that machine are measured, not promised | the test suites; L10 and A13 in the Geometric booklet |
| **a teacher** | the jump-rope picture, three moves, and a law you can check by hand | sections 1 and 4, and the laws table in Math Concepts |

### Your first hour: five recipes

Every recipe below was run against the public `omni-ring` code, on the NumPy path with no compiled kernel. The output
shown is what we got. The same code is in `docs/guide/examples/ring_recipes.py`.

**Setup.**

```bash
git clone https://github.com/SovRing-Labs/omni-ring && cd omni-ring
./build_kernel.sh        # optional: the AVX2 kernel; without it the NumPy fallbacks run
pip install -e .
pytest tests/ -v         # a green suite is the first proof that the kernels match your CPU
```

**Recipe 1. A clock you read without searching.** Store a number on the five rings (3, 5, 7, 13 and the 17 check
ring), then read it straight back. There is no loop over candidates: one probe per ring, then the Chinese Remainder
Theorem.

```python
from omni_ring.types import DEFAULT_SPEC
from omni_ring.codebook import generate_direct_codebooks
from omni_ring.crt import direct_probe
from omni_ring.check import check_anomaly

mods = DEFAULT_SPEC.all_moduli                  # (3, 5, 7, 13, 17)
CB = generate_direct_codebooks(seed=5)
x = 1234
slot = sum(cb[x % m] for cb, m in zip(CB, mods))
residues, got = direct_probe(slot, CB, mods)
print(residues, got, check_anomaly(residues))   # [1, 4, 2, 12, 10] 1234 1234
```

*What you get:* any number below 1,365 is stored and read back exactly, and the read is checked. Use it for IDs,
timestamps, positions, or any coordinate you would otherwise look up.

**Recipe 2. A memory that refuses a wrong answer.** Corrupt one ring and ask again.

```python
from omni_ring.check import ResidueDesyncError
bad = list(residues); bad[2] = (bad[2] + 1) % 7
try:
    check_anomaly(bad)
except ResidueDesyncError as e:
    print(e)    # Phase slip / corrupt residue detected: CRT resolved to 7864, exceeding ... 1365
```

*What you get:* every single-ring slip is caught; the public test checks all 54,600 of them. Remember what it is for:
it catches mistakes, not forgers (L6).

**Recipe 3. Time as a turn.** Moving a stored time forward is one multiplication, not a rewrite.

```python
import numpy as np
from omni_ring.codebook import generate_rotations
from omni_ring.chain import bind, encode, get_tick, advance

R = generate_rotations(seed=0)
v, tick = encode(41, R), get_tick(R)
print(np.allclose(bind(v, tick), encode(42, R)))         # True
print(np.allclose(advance(v, tick, 10), encode(51, R)))  # True
```

*What you get:* a whole bundle of timestamped marks can be shifted in time at once, because binding spreads over
bundling (A18). This is the jump rope moving one notch per tick.

**Recipe 4. A crowded slot, a cue, and peeling.** Put eight marks into one vector. Read one with a cue, then read
them all with peeling.

```python
from omni_ring.peel import read_one, read_all
rng = np.random.default_rng(7)
xs = [int(a) for a in rng.choice(1365, 8, replace=False)]   # [1057, 1137, 307, 1221, 787, 849, 930, 1283]
crowd = sum(encode(a, R) for a in xs)
print(read_one(crowd, R, cue=xs[0] % 13))   # 1057: the mark the cue points to
print(sorted(read_all(crowd, R)))           # all 8 marks, 0 fakes
```

*What you get:* one vector holds several records, and you read them back by asking. `read_one` returns `None` rather
than guess when the settle is not confident. Push the count up and watch where it stops working: that limit is L1,
and recipe 5 predicts it.

**Recipe 5. Size your memory before you build it.** Law L1 says how many items fit at a given accuracy.

```python
import math
def accuracy(D, n, C, a=1.046):            # L1: Φ(a·√(D/n))^(C−1)
    phi = 0.5 * (1 + math.erf(a * math.sqrt(D / n) / math.sqrt(2)))
    return phi ** (C - 1)
for n in (100, 200, 300, 400):
    print(n, round(accuracy(5120, n, 1000), 4))   # 1.0, 0.9999, 0.9923, 0.9129
```

*What you get:* at D 5,120 with 1,000 candidates, about 300 items per vector keep 99 %; at 400 you are already down to
91 %. Plan the number of slots before you write code. The Geometric booklet shows how to use this for a real design,
and when the formula stops holding.

### Your first week

1. **Build a classifier that can abstain** (**Design** in the public code until the Part 2 modules ship). Embed your
   labelled texts with one embedding model, encode them as marks, read new texts by top-k vote, and use the margin to
   abstain. P2 §3 specifies it fully.
2. **Store facts as triangles** (**Design** in the public code). Bind (subject, relation, object), file each triangle
   under its three edges, and keep the rows themselves in SQLite (P2 §6–7).
3. **Share one memory between programs** (vsa-core). `make` builds the kernel, allocator and self-tests. `make
   xlang-check` checks the Python and C layouts on a private segment and is safe at any time. `make check` clears the
   live bus first, and refuses if the bus holds data.
4. **Give your agents hands** (omnitool). `bin/fleet-exec --validate-only '{"operations": [...]}'` checks a batch
   without running anything. Read the guard's verdicts, then run for real, or point an MCP-capable agent at the server
   in `mcp/`.

### Patterns that pay off in your own project

- **Replace a lookup with a residue read** wherever the key is a number you compute, such as a time, a position or a
  shard. It is 0 bytes scanned (R14). Pick the rings with the rule in the Geometric booklet.
- **Add a check ring to anything that stores coordinates.** It costs one ring and catches every single slip.
- **Keep the truth in rows and the meaning in rings.** Exact questions go to SQL; "something like this" questions go
  to the ring. This is the routing that beat each tool alone, 0.844 against 0.612 (P2 §8.1).
- **Let the memory say "I don't know".** Use the margin between the best and second-best match, and route the rest to
  a slower, exact path.
- **Cache before you compute.** Machine-written streams repeat. In ours, 99.9 % of live notes were exact repeats
  (R11).
- **Make small things into cores.** A deterministic job that runs often becomes a small rendered program that leaves
  a receipt every time it fires (docs 38–40).

## 9. What it is good for

| Use | Why HDC fits | Practice |
|---|---|---|
| Classifiers that can say "I don't know" | Votes over marks give a margin; abstain below it | Calibrate the margin on held-out data (P2 §3) |
| Answers you can check | The check ring and second-path confirmation catch corrupted or unsupported answers | Treat abstention as a feature, not a failure |
| Agent memory and coordination | A shared bus of fixed-size vectors; marks as evidence between agents | One writer per slot; readers retry if a counter changed (vsa-core §2) |
| Noisy or partial lookups | A misspelled or reworded cue still lands near the right symbol | Pair it with exact rows for confirmation (P2 §8.1) |
| Structured facts and whether they agree | Triangles, harmony, contradictions as a trit | Keep buckets at or below the measured capacity |
| Moving or relabelling whole groups | Binding spreads over bundling, so one operation moves every member | Measured lossless for re-timing and re-roling (P2 §8) |
| Clocks and addresses | A residue read is a jump, not a search: 0 bytes scanned (R14) | Pick coprime ring sizes; add a check ring |
| Small hardware | Integer kernels, 4-bit packing, no GPU needed | Run the tests; an SSE kernel for pre-AVX2 CPUs ships with the Part 2 code |

## 10. When not to use it

- **Exact lookups by key.** Use an index or a hash table: hundreds of times faster (P2 §8).
- **Dense matrix arithmetic.** Use BLAS on the CPU, or a real GPU.
- **Bundling without limit.** Past the measured capacity, recall and safety fall off a cliff (L1).
- **No cue at all.** Reading a crowded slot with nothing to start from depends on luck. Give the memory something
  (P1 §12).
- **Heavy work on a laptop's integrated GPU.** On our machine it lost every head-to-head; use it beside a busy CPU,
  not instead of it (L10; P2 §5).

## 11. Integrations

- **SQLite (+ FTS5).** Keep the truth in rows. Let the ring index meaning and the triangle verify. Exact multi-hop
  questions go to indexed joins (P2 §7–8).
- **Embedding models.** Any embedder can be the "pen" that turns text into vectors. Use **one pen per ring**: marks
  from different models cannot be compared.
- **Language-model agents.** omnitool exposes an MCP server. The ring heads can sit in front of a model as a cheap
  first answer that abstains, passing on only what they cannot answer.
- **Several machines.** Each machine holds a shard and a cue is broadcast; only answers that pass the check ring may
  win (P1 §11). **Speculative** at scale until measured.
- **Rented GPUs.** One school day on the GPU matched the CPU day, and eight models in one step were each
  bit-identical to their own solo run (doc 28). At a group of twenty it missed its registered 2 % bar (doc 29).

## 12. Practices that kept us honest

1. **Pre-register.** Write the pass and kill bars before running, and publish the kills.
2. **Write what the field predicts first.** Every plan carries a line saying what known theory expects. A result that
   matches it is a calibration; one that departs from it is the finding (booklet, "How we keep sifting").
3. **Search the field first.** Most good ideas have relatives. Cite them and say what differs.
4. **Truth in rows, meaning in rings, verification in triangles.**
5. **One pen per ring; never let the pen drift.** Re-embedding with a changed model silently ruins every mark.
6. **Measure capacity on your own data.** Every bundle has a ceiling; stay below it.
7. **Cache what repeats.** Machine-written text repeats: 99.9 % of live notes were exact repeats (R11).
8. **Prefer exact integer rules.** If two machines disagree on a score, you have a bug, not noise.
9. **Abstain.** A trit with a zero is worth more than a confident guess.
10. **Judge a round by what the model knows now, not by what it once knew.** This rule came from the round-9 collapse
    (doc 25; essay 12).

## 13. Geometric computing

Geometric computing is the author's name for the habit underneath all of this: **choose the shape on purpose, then
measure what it buys.** Clocks are circles, choices sit at the corners of a simplex, and order needs four dimensions.
Code can be a shape too: the author spoke of *"3/4d rendered code as a program/loop/core."*

On 2 October the author asked whether it counts as a field of its own: *"Would Geometric computation count as a field,
and what/where can I pull from to keep devloping this, is it just HDC?"* Our honest answer is that it is a way of
working inside HDC, with a few measured additions:

- the fitted capacity law;
- the separation of *what* from *when*;
- the vibration warning;
- harmony read from phase;
- the rule that shape pays only where things are compared.

The author's notes and the full set of twenty axioms, seventeen laws and seventeen rules, each with its evidence and
the person who found it first, are in the companion booklet `GEOMETRIC-COMPUTING-AND-YOU.md`. Five of the author's
plain readings give the flavour:

- *When constrained, add a bigger room, not smaller handwriting; when the room fills, build a room inside it.*
- *Socks then shoes isn't shoes then socks; to keep order you need math where swapping changes the answer.*
- *Structure is exact; mixtures distort and need cleaning.*
- *There is a time and a place to everything: a thing and its time travel together but can be read apart.*
- *A mind without a governor has no control, and the governor doesn't shout over the voices; it decides which to
  listen to.*

## 14. Where it did not hold

We got things wrong, and we keep the record.

- **Our resonator fell far short of the field's best** on the hardest factoring test, so the decode path moved to a
  partitioned design (P4).
- **The capacity law is not universal.** It fails in the overload tail (L1, CAL-2).
- **Several laws rest on runs that failed as registered** and stay diagnostic until rerun (L12, L13, L15, L16).
- **Some ideas from AI study sessions did not survive measurement:**
  - quantum numbers as residue codes;
  - "twelve pentagons as twelve channels";
  - "free energy" in a settle.

  All are listed in `MATH-CONCEPTS-AND-THANKS.md`, "Ideas that did not hold".
- **The whole cyclone array has never run at once**, and no growth round has finished on real data (docs 27, 30).
- **Bringing old hardware back into daily use** is the aim, and still **Speculative**. What is measured is that these
  kernels run exactly on a 2019 laptop CPU.

## 15. Where to go next

- **Technical disclosures:**
  - `omni-ring/TECHNICAL-DISCLOSURE.md` (Part 1) and `TECHNICAL-DISCLOSURE-PART-2.md`;
  - Parts 3–7 in this corpus under `docs/disclosures/`;
  - `vsa-core/TECHNICAL-DISCLOSURE.md`;
  - `omnitool/TECHNICAL-DISCLOSURE.md`.
- **Each repository's `DOSSIER.md`:** history, specification, metrics, tests and limits.
- **This corpus:**
  - measured documents `docs/01–44`;
  - essays `docs/essays/01–16`;
  - the booklet `docs/guide/GEOMETRIC-COMPUTING-AND-YOU.md`;
  - the running list `docs/guide/MATH-CONCEPTS-AND-THANKS.md`.

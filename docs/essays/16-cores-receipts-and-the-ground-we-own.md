# Cores, receipts, and the ground we own

| | |
|---|---|
| **Date** | 2026-10-09 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Written with AI assistance (Claude) from the author's conversations of 3–9 October 2026 (unpublished). The author reviews it before publication. |
| **Type** | essay — every number is cited to docs 38–41 or `P7 §5–6`; anything not measured is marked **Speculative** |

## In one paragraph

By the end of the week the fleet worked differently. An agent plans, dispatches and checks; small deterministic programs — cores — do the
repeated work, on the laptop or on rented machines, and leave a receipt every time they fire. Some cores earned their place and some were killed
by their own pre-registered bars; both are on the record. Under all of it sits a rule about ground: what we build from, what we train on, and how
anyone can check that later — four kinds of clean room, a marker on every data folder, and ledgers whose rows are chained so an edit shows.

## The words you need

- **Core** — in the author's vocabulary, a JIT-rendered program that fires constantly while it is active. In the registry, a core is a row:
  how to fire it and what proves it healthy.
- **Registry** — the list of cores and their operations, each with a **gate**: a command whose exit code 0 means the core is healthy.
- **Receipt** — one line per fire: what went in (a hash of the arguments and of every input file), what came out (a hash), the verdict, the time.
- **Pod** — a rented machine (CPU or GPU) that runs cores and training.
- **BELT** — the author's name for a batching scheduler, after a conveyor belt that changes speed.
- **Clean room** — building from a published description, never from another project's code. It comes in forms with different guarantees.
- **Ledger** — a tracker, named by what it tracks. The clean-room and growth ledgers are append-only and chained by hashes.

## The idea, in the author's words and ours

On cores, 4 October: *"we can make a new core for anything. we can put a new core into the harness that fit's its purpose and design. a core that
adds processing/sifting/firing."* On how the fleet should run, 7 October: *"what's your view of the agent in the loop model? where an agent as
commnad just dispatches and reviews, sometimes steps in"* — and *"the fleet loop would also serve to grow the fleet and cores."* On what the
doctor's kind of core might become: *"what other determenistic roles can this doctor fill? debugging? encoding, decoding, what could these cores
really evolve into? Fleet swarm helpers that don't rely on llm? Accurate, fast, lightweight, evolvable, growable through database and experience
instead of training."* And on 8 October, the scale: *"would we be able to do the same for all of the 26 generators in thead? … so we can have a
decentralized full capable fleet that makes training data for the commander, and then iintegrates all the data into thead at certain checkpoints,
so the seed is constantly improving for future users?"*

On ground, 3 October, after a review found training rows produced by models whose terms restrict their use: *"Approved. Run both clean-room jobs
now: filter the Claude/Gemini rows out of reasoning-mine and retrain the three heads on our deterministic rule labels. … Let's make our ground
completely sovereign."* And on records, 8 October: *"talon keeps records of each sessoion … it would not be too hard to add a ledger would it."*

## How we got here

**A registry and its receipts (8 October).** Every core became a row with a gate, and every fire writes one line. We learned in the first day why
an exit code is not proof: a doctor run on a pod without a compiler returned success while every row it built was empty. A post-condition now
checks the output itself and records that run as a failure. Of 358 receipts, 318 passed, 37 failed and 3 errored; nine of the failures are the
doctor's black-box station refusing an equation whose rows disagreed — a refusal is a failure in the contract, as it should be. Two of our own
programs write their receipts with a hash of the argument strings only, so the output is not bound; that is disclosed, not hidden (doc 38).

**Cores on rented machines.** The author asked for the pods to be used, not watched: *"have them process the database or our knowledge database
collected for our various cores. ensuring our pod gets maximum use"* — and, more than once, *"pod is idle"*. The laptop side runs cores over ssh
with a CPU cap, rewrites paths and shards work across jobs; a pod that runs the training school is refused for anything else (added after a batch
ran on the wrong pod for an hour). The pod side keeps a small server with a BELT queue — three priorities, slots refilled continuously, a cache for
repeated deterministic work — that drops from eight slots to four while training runs. The same doctor run gave **byte-identical** results on the
laptop and on a pod; eight pod jobs did in 4.2 s what took 20.9 s serially. We had hoped the pod server would also be faster per call; it was not,
on 7 of 9 operations, because it wraps the same fire (doc 38).

**The embed core.** An embedding server is slow; a core that turns text into a vector by summing a table of per-token vectors is fast. We
distilled the table from the encoder itself and gave it a bar before any result: hybrid search recall@5 at least 0.775 and at least 100 times the
encoder's speed. It was hundreds of times faster and not good enough — 0.555 for the plain table, 0.640 for a table fitted to the encoder on
held-out documents, 0.600 with three times more text — and in every arm the hybrid fell *below* plain full-text search, because a weak list drags
a rank fusion down. Search stays on the encoder (doc 39).

**The chewer core.** The author asked for it on 7 October: *"I want to make a transcipt chewer"* — the fleet's own sessions, cut into searchable
steps, with credentials and personal paths scrubbed before storage, and later perhaps a transcriber. Measured against a pre-stated bar, it finds
the right conversation 94 % of the time and the right step far too rarely (0.115 against full text's 0.150). Neighbouring steps of one task look
alike — the same weakness this corpus notes for semantic search over its own session archive (doc 39).

**The reservoir probe** tested a different road to a fine-tunable ternary model: a fixed, sparse ternary recurrent network with a closed-form
readout and no gradient. All ten arms missed the bar; two seeds of the same arm disagreed more than any two arms did. A search over 100 fusion
weights on the same queries reached 0.800 — a maximum chosen after the fact, **not a pass** (doc 39).

**The math core** passed. Ten concepts — CRT, mixed radix, Barrett reduction, Hamming distance, integer square root, period mining, ternary
quantisation, stable softmax, the Fibonacci recurrence, the residue clock read — each as a name-free specification, laws with teeth (break the
subject on purpose and the law must fail), code emitted and verified, generators with independent verifiers, and an explainer. Given fresh values,
the explainer names all ten concepts exactly and says "none" to each of four impostors; re-run here, byte for byte the same (doc 40). Two of the
first-draft laws were too weak when the teeth check broke their subject, and were strengthened.

**Ground.** Four ways to keep a clean room, with different guarantees, and a statement must say which it uses (doc 41):

| form | who writes the code | what stops a breach |
|---|---|---|
| standard text only | one builder, from the published standard; other implementations only run as black boxes | the standard's own conformance data |
| two-team (essay 15) | an implementer who sees only a name-free specification | a gate that passes only function, and a ledger of every step |
| idea level | the author, from published ideas and our measurements | procedure, plus licence and secret scans |
| training data | — | a marker on every data folder: `.clean-room.json` allows, anything else refuses |

The standards library the doctor draws on (omni-spec) was built from specification text only, as the author asked on 6 October — *"we're building
a clean room library from this catalog, starting by building from spec then an actual reader then builder cleanroom"* — and is meant to be shared:
*"i'm thinking it will be a permissive resource that ships/pairs with the doctor core."* Its licence is decided (Apache-2.0); it is not released
yet, and only one of its seven release gates, attribution, is done. The GPU kernels have a clean-room ledger: 23 entries, every source consulted or
cited with its licence and hash, the chain intact. The growth controller writes one ledger row per round (essay 12).

## Where it did not hold

- **Guard and redteam** — a core to watch our own machine and a core to attack our own system, each with written bars — are designed, not built.
- The clean-room ledger stops before the array work; its attestations are the authoring agent's own statements, not an independent audit.
- A chained ledger without a signature shows accidental edits, not a determined rewrite of the whole file.
- The receipts of two of our own programs do not bind their outputs (doc 38).

## What this essay does not claim

That the fleet already promotes repeated agent work into new cores by itself (designed, not built); that a decentralised fleet of generator cores
feeds the seed at checkpoints (**Speculative**: the math core is the first such core measured); that the reservoir layer can be fine-tuned by
superposition or grown under a verifier — the registered tests for those have not run.

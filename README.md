# OMNIRING research corpus

<!-- status-badges (REPO-ACCESS-C) -->
[![status: pre-alpha (under development)](https://img.shields.io/badge/status-pre--alpha%20%28under%20development%29-orange)](STATUS.md) **Status: pre-alpha, under development** — what works today, what is untested and what failed: [`STATUS.md`](STATUS.md)

[![defensive publication: DOI 10.5281/zenodo.23354784](https://img.shields.io/badge/defensive%20publication-DOI%2010.5281%2Fzenodo.23354784-blue)](https://doi.org/10.5281/zenodo.23354784) **Defensive publication:** [`docs/disclosures/`](docs/disclosures/) · DOI [10.5281/zenodo.23354784](https://doi.org/10.5281/zenodo.23354784)
<!-- /status-badges -->

**Authors:** Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted)
**Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0), see `LICENSE.md`
**Copyright:** 2026 Juan Carlos De Santiago
**Version:** 0.3.0 (see `CITATION.cff`)

## What this is

The research record behind **OMNIRING**, a memory that stores small structured records ("marks") in fixed-size
high-dimensional vectors and reads them back by resonance. Its parts:

- coprime residue rings (moduli 3, 5, 7, 13) combined by the Chinese Remainder Theorem, plus a redundant
  **17 check ring** that detects any single-ring slip;
- a **cue-driven soft resonator** that settles all free rings together, and abstains when the check ring fails;
- **peeling** (explaining away) to read crowded slots one mark at a time;
- **diamond facets**: several small categorical codebooks with a checksum centre ring;
- a **mark store** with a rehearsal counter and decay.

These documents are the experiments and reviews that shaped the design. Most are pre-registered experiments: the
pass/fail rule was written before any trial ran, and each document reports it word for word next to the result.
Negative results (KILL) are published alongside positive ones.

## Read this first: what the measurements corrected

The measured account of the system is the omni-ring technical disclosure series (below). Where an older document here says
something those measurements later overturned, a `> Correction:` note cites the document that measured it. The corrections
that matter most:

1. **A cue is mandatory.** Without one, decoding depends on the random codebook draw: a clean single mark decodes
   15/15 at some seeds and 1/15 at others. With any one ring clamped it succeeded at every draw tested. Unguided
   failures abstain rather than answer wrongly.
2. **Capacity is about 12 marks per slot at one cue.** 1,365 is the address space, not the number of marks a slot
   can hold. (Later parts measure a cued peel that recovers many more marks per slot on a larger bus format; see Part 4.)
3. **The fleet's first SOFTSWEEP harness was invalid** and was rewritten. No number from it appears here.
4. **TABU knockout was not adopted.** It rescued 11% of stuck settles and turned 18% into silent errors. A stuck
   settle should abstain.
5. **The two small check slots of a program vector are an error-detecting code, not a security boundary** (Part 3,
   correction of 2026-10-01): random program vectors were accepted at about 0.04% over 20,000 trials per arm, which matches
   the analytic (1/48)^2 = 0.043%. Single-instruction tampering is always caught.
6. **omni-spec is not released.** Part 6 §4 said it was "released free to the community under Apache-2.0"; the licence is decided, the
   release is not, and only its attribution gate is done (corrected copy of Part 6; doc 41).
7. **"Mastered" is not "known".** The live school's sticky mastered count rose 93 → 123 in the round that wiped tier-1 skills at the gate from
   55 to 6; rounds are judged by skills at the gate on shared skills (doc 25).
8. **The 2 % GPU parity bar failed and stays failed.** A group of 20 models trains 21.6× faster than the CPU engines but its per-harness gap
   averaged 4.1 % (max 9.7 %), worse on 16 of 20 harnesses, not 17 as first recorded; a noise-relative gate is registered for the next run only (doc 29).
9. **40 models in one GPU session are refused, not mis-trained.** An explicit guard now stops the build (doc 29).

## Technical disclosures (dated prior art)

Parts 1 and 2 of the omni-ring series are in the omni-ring repository
([Part 1](https://github.com/SovRing-Labs/omni-ring/blob/main/TECHNICAL-DISCLOSURE.md),
[Part 2](https://github.com/SovRing-Labs/omni-ring/blob/main/TECHNICAL-DISCLOSURE-PART-2.md)). Parts 3 to 7 and the omnid and dock
disclosures are kept here, in `docs/disclosures/`; Part 7's experiments are docs 24 to 44 and essays 12 to 16 tell the week, its harnesses are in `harness/part7/` and its result files in `docs/appendix/part7/`. Failures are reported as registered. Evidence status differs by file: Parts 3 and 4 name
harnesses and result files in the omni-ring repository; Parts 5 and 6 do not yet have a published claim-to-evidence index, and say so
in their opening lines; the omnid disclosure labels some numbers *unsupported*; the dock draft labels its numbers *unverified*. Treat a number that names no result file as recorded by
the project, not independently reproduced.

| File | Date | What |
|---|---|---|
| `docs/disclosures/OMNI-RING-TECHNICAL-DISCLOSURE-PART-3.md` | 2026-10-01 | Designed solids, 4-D cores, the source (program-vector resonator loop), seams, the hypervector wire; includes the check-slot correction above |
| `docs/disclosures/OMNI-RING-TECHNICAL-DISCLOSURE-PART-4.md` | 2026-10-02 | The sifter as code (vector VM), the decode ladder, the learning core |
| `docs/disclosures/OMNI-RING-TECHNICAL-DISCLOSURE-PART-5.md` | 2026-10-03 | The seed's owned ground, residue memory at scale, our own engines, fleet systems |
| `docs/disclosures/OMNI-RENDER-TECHNICAL-DISCLOSURE-PART-6.md` | 2026-10-04 | omni-render: engine, program runtime, JS on our IR, a self-repair core |
| `docs/disclosures/OMNID-TECHNICAL-DISCLOSURE.md` | 2026-10-01 | omnid: one front door for local AI, hardened web face, hypervector wire |
| `docs/disclosures/DOCK-TECHNICAL-DISCLOSURE.md` | 2026-10-09, **draft** | dock: a constant-surface MCP front with abstaining tool search (an MCP server, unrelated to the "dock" of the ARC-reactor vocabulary) |
| `docs/disclosures/OMNI-RING-TECHNICAL-DISCLOSURE-PART-7.md` | 2026-10-09 | Live school and growth run, cyclone array and T50 hub, Omni Web, the doctor core, the cores, provenance; numbers without a published result file are labelled (partial) / (unsupported) in place |
| `docs/disclosures/CYCLONE-TRAINER-TECHNICAL-DISCLOSURE.md` | 2026-10-14 | Cyclone Trainer: a systolic toroid array that trains ternary register machines (THEAD-ISA) without large matrix multiplies or unbounded KV caches |
| `docs/disclosures/THEAD-SUPERSEED-TECHNICAL-DISCLOSURE.md` | 2026-10-14 | THEAD SuperSeed: a self-contained ternary model architecture (trunk, built-in generators, shards, inducer) aimed at forgetting, hallucination and energy cost |

**Licence of the disclosures.** Here they are CC BY 4.0 like everything else in this repository. The same words also ship in the
code repositories, under those repositories' licences: omni-ring under PolyForm Small Business 1.0.0 OR PolyForm Noncommercial
1.0.0, omnid and dock under Apache-2.0. Two licences for one text is intended: copy and cite under whichever applies to the copy you hold.

## Part 2 (2026-10-01): geometry, the triangle memory, the substrate

The omni-ring `TECHNICAL-DISCLOSURE-PART-2.md` (release v0.1.1) is the measured account of the second phase: the
SuperSeed portable spec, the geometry of the sift, integrated-GPU execution, the triangle memory ("omnitri") and the
table / full-text / ring / matrix substrate. Essays 07-11 in `docs/essays/` tell how it was reached: the questions,
the steps, the twists and what was retracted.

## Parts 3 to 7 (2026-10-01 to 10-09): programs as vectors, owned ground, our own engine, and the week of 10-06

Parts 3 to 6 (in `docs/disclosures/`) carry the sifter as code, the decode ladder, the seed's owned ground and our rendering engine. Part 7
covers the week of 6–9 October: the live school and the growth controller, the cyclone array and its T50 hub, a browser drawn by our own
engine, the doctor core and its clean room, the cores and their receipts, and how provenance is kept. Its experiments are docs 24–44, one per
document, each with its verdict; essays 12–16 tell how the week went, in the author's words.

## Contents

| File | What |
|---|---|
| `docs/01-ring1-core-cued-recall-and-capacity.md` | Cued recall, 16-level quantisation, confidence gap, slot capacity (about 12 at one cue) |
| `docs/02-ring1-check-ring.md` | The 17 check ring flags 81.8% of wrong settles with 0 false alarms |
| `docs/03-ring1-direct-keyed-storage.md` | Keyed direct read of single-mark slots (1000/1000, about 11x faster); 1-bit tag for two marks |
| `docs/04-ring1-disperse.md` | Spreading marks over many slots does not beat one crowded slot (KILL): choosing the slot is the bottleneck |
| `docs/05-ring1-softsweep-decode-soft.md` | Soft resonator vs sequential probe: at k = 5, 300/300 vs 10/300 members recovered; cued decodes at most 1/300 silent-wrong per cell |
| `docs/06-ring3-peel-diamond-correl-tabu-fret.md` | Peeling (PASS), diamond facets, correlated codebooks, tabu, coarse-to-fine dials |
| `docs/07-peel-read-all-module.md` | Peeling moved into the engine: 16.65 of 24 marks per slot, 0/333 fakes |
| `docs/08-peer-review-retrieval-and-consolidation.md` | Peer review of the prototype, with its claim ledger |
| `docs/09-ring1-halo-two-stage-chain.md` | A two-stage halo chain ties the one-resonator and costs 2.5x the iterations (KILL) |
| `docs/10-ring1-smooth-fractional-phase.md` | A soft resonator cannot *discover* a smooth factor; it *works* as a cue (KILL on discovery) |
| `docs/11-markstore-accumulation-and-decay.md` | The mark store: count-weighted accumulation, rehearsal counter, decay |
| `docs/12-seam-defining-ternary-zero.md` | Defining ternary (0,0): a 4,800/5,120 fabricated-phase defect and its fix |
| `docs/13-seam-full-slot-down-projection.md` | Down-projection replaces truncation, fixing a 97.5% discard at the model seam |
| `docs/14-seam-retracting-three-accuracy-claims.md` | Retracting three accuracy claims and replacing them with a checkable one |
| `docs/15-modulus-set-and-check-ring-decision.md` | Choosing the modulus set {3,5,7,13}+17 (three-lens panel decision) |
| `docs/16-resonator-vsa-spike-decision.md` | Should the resonator/VSA spike be built? (panel decision, superseded by measurement) |
| `docs/17-cross-field-which-ideas-change-the-design.md` | Which cross-field ideas change the design, and which stay metaphor |
| `docs/18-appendix-xp1-citation-check.md` | XP1 citation check: 17/17 arXiv ids resolve |
| `docs/19-dossier-resonator-networks.md` | Literature dossier: resonator networks, factorisation in superposition |
| `docs/20-dossier-vsa-encodings-and-capacity.md` | Literature dossier: VSA encodings, capacity, cleanup |
| `docs/21-dossier-dynamics-and-codes.md` | Literature dossier: dynamics, fractals, projections, codes |
| `docs/22-exploration-where-verified-properties-could-apply.md` | Exploration: where the verified ring properties could apply (labelled) |
| `docs/23-vision-a-resonator-cortex-labelled-speculation.md` | Vision: a resonator cortex (labelled speculation; unmeasured claims marked) |
| `docs/24-live-school-round-loop.md` | The live school as one round loop over a 392-node skill graph: tier-1 skills at the gate 28 → 72; no wall in 16 rounds |
| `docs/25-round-nine-collapse-and-round-guard.md` | Round 9 wiped tier-1 (55 → 6 at the gate) while the sticky count rose; the guard that catches it (0 false alarms) |
| `docs/26-circular-builds-by-splicing.md` | Middle on its own core wipes tier-1 (KILL); circular spliced builds keep it and learn middle (PASS) |
| `docs/27-growth-controller-and-ledger.md` | A 100 % stage gate on 300 independent rows, growth modes, permanent keeps, a hash-chained growth ledger (gate 14/14; no real round yet) |
| `docs/28-school-step-on-the-gpu.md` | The school step as emitted GPU passes; 8 models per step bit-identical per replica; the 2 % bar with every switch FAILED |
| `docs/29-the-two-gigabyte-binding-probe.md` | 40 models in one session refused at build; a group of 20 at 21.6× misses the registered 2 % bar (FAIL as registered) |
| `docs/30-cyclone-array-t50-hub-and-wiring.md` | The cyclone array as the author drew it: T50 hub in one register, resident wiring rungs G1–G40 exact, G120 FAIL |
| `docs/31-dual-t50-cut-read-and-toroid-mailbox.md` | Minimum cuts between toroids read from the rings' own counters, exact against Gomory–Hu; a hot-cluster blind spot; the mailbox |
| `docs/32-omni-web-architecture-and-memory.md` | A browser drawn by our own engine: broker, confined page processes, one tree for drawing and reading; 2.9 % of Firefox's memory |
| `docs/33-omni-web-platform-census-orbit-and-merge-gate.md` | 24-site census ("lightweight" fails on script-heavy pages), test262 54.5 → 56.85 %, the Orbit chrome, the merge gate |
| `docs/34-doctor-code-alphabet-and-search-by-function.md` | Code lowered to name-free equations; anti-unification finds shared shapes; search by function answers 24/24 |
| `docs/35-doctor-black-box-laws-and-the-gate-series.md` | Chrome as a black-box oracle (nine laws); geometric triage; agreement 19,008 → 24,004 with 0 lost; three probes FAIL |
| `docs/36-doctor-t25-box-kernel-and-pristine-fix-loop.md` | A box as one point on 25 rings, firing inside layout at 0.90 %; the unattended fix loop to pristine geometry; an overlap-blind judge |
| `docs/37-two-team-clean-room.md` | Readers, a clean-room gate, an implementer: 27 of 32 rebuilt from the spec alone, 256/256 leaks refused; foreign-crate bar missed |
| `docs/38-cores-registry-receipts-and-pod-hosting.md` | A core registry with receipts and post-conditions; cores hosted on rented pods; BELT v0 |
| `docs/39-embed-chewer-and-reservoir-cores.md` | Three cores killed by their own bars: embed (0.555–0.640 vs 0.775), chewer, reservoir (KILL) |
| `docs/40-math-core.md` | Ten concepts as specs, laws, emitted code and generators; explain names 10/10 and refuses 4/4 impostors (PASS) |
| `docs/41-provenance-clean-room-forms-gates-and-ledgers.md` | Four clean-room forms, data and licence gates, and the hash-chained ledgers, with what each guarantees |
| `docs/42-pre-k-arms-on-the-t25-core-model.md` | Pre-K arms on the T25-core model: plates attention kept; ring head, event fields, integer backward, T25 pages off; the pre-K ladder |
| `docs/43-training-on-a-rented-cpu-server.md` | Parallel day merge on a rented server, throughput by model size, a native build with no gain, a shared-RAM bus |
| `docs/44-ramkit-switches-on-the-school.md` | Memory switches that are bit-identical when off; ring memory, episodic gate and A-GEM measured, kept off |
| `docs/45-status-disclosure-2026-10-14.md` | Disclosure and status 2026-10-11 to 10-14: exact ring softmax head, ring core in attention, cyclone MLP (negative), liquid doctor ranker, open-web curriculum, BitNet decode, stop-not-failover dispatch, speech core (design only) |
| `docs/disclosures/` | The technical disclosures listed above (Parts 3 to 7, omnid, dock, Cyclone Trainer, THEAD SuperSeed) |
| `docs/appendix/part7/` | Result files and pre-registration extracts cited by Part 7 and docs 24-44 (`docs/appendix/part7/ordering/first-added-table.md`: the version-history ordering evidence) |
| `docs/guide/HYPERDIMENSIONAL-COMPUTING-AND-YOU.md` | A plain-language guide to hyperdimensional computing: what we are building, why, and how (second edition) |
| `docs/guide/GEOMETRIC-COMPUTING-AND-YOU.md` | The axioms (A0–A19), laws (L1–L17) and rules (R1–R17) of geometric computing, in plain words with the author's notes, each with its evidence and who found it first |
| `docs/guide/MATH-CONCEPTS-AND-THANKS.md` | Running list of every mathematical and scientific concept used (190 rows), with credits and a thank-you; ideas that did not hold |
| `docs/appendix/geometric-laws/` | Result files (and four harnesses) behind the laws in the geometric booklet |
| `docs/appendix/math-kb/` | The math core's knowledge base (`mathkb.json`: ten laws with generators) and `check_laws.py` to test them |
| `docs/guide/examples/` | Runnable examples for the guides: `ring_recipes.py` (five omni-ring recipes) and `design_helpers.py` (memory sizing by L1, ring picking) |
| `docs/essays/` | Readable editions of the research conversations (16 essays, plain language, speculation labelled); start with `docs/essays/INDEX.md` |
| `docs/appendix/*.run.txt` | Raw run output cited by the documents above |
| `harness/` | The numpy research scripts that produced the numbers in docs 01-06, with relative paths; see `harness/README.md`. `harness/part7/` holds the harnesses cited by Part 7 and docs 24-44 (their licence per file is listed in the release's ship list) |
| `MANIFEST.md` | What is published, what was left out, and why |
| `CITATION.cff` | How to cite this corpus |

The documents keep their experiment names (RING-1, RING-3, ...) so they can be cross-referenced. `harness/...` paths
name the numpy research scripts that produced the numbers; they ship here with every absolute path replaced by a
relative one, so you can re-run them.

## Code

- **omni-ring**: the ring memory engine (coprime rings, check ring, soft resonator, peeling, facets, mark store, and the
  later parts' modules), with its technical disclosures and the experiment harnesses and results that Parts 3 and 4 cite.
- **vsa-core**: the shared-memory vector bus, ternary and phase kernels the engine runs on.

Both are released separately as source-available software, published as prior art. omnid and dock are described by
disclosures here; their code is released in its own repositories.

## Why there is no code-licence set here

The code repositories each carry `LICENSE.md`, `LICENSE-NONCOMMERCIAL.md`, `LICENSING.md`, `DATA-AND-SHARDS.md`,
`SHARD-FORMAT.md`, `PROVENANCE.md` and `TECHNICAL-DISCLOSURE.md`. This repository is documents (CC BY 4.0) and research scripts
(their own licence file, `harness/LICENSE.md`): it ships no product code, so it has no shard format, no dual-licence
explainer and no per-product provenance file. The provenance of each technique is given in the "Provenance (borrowed / ours)"
section at the end of each disclosure.

## How it was made (AI-assistance disclosure)

This corpus was prepared with AI assistance: Claude (Anthropic), Gemini (Google) and the fleet's open-weight models
designed experiments, wrote harness code, ran reviews and drafted text. The author directed the work, chose what to
build and what to publish, and reviews every document before publication. AI systems are not authors in the legal
sense; the byline names the human author and discloses the assistance.

Where a number comes from, it says so. The numbers in docs 01-23 were measured on a 2019 laptop CPU (Intel i5-8365U, AVX2,
no GPU). The later disclosures also use rented cloud machines (CPU servers and data-centre GPUs); each disclosure names the machine
for each result. Raw AI chat transcripts are not published; where a document quotes one, it says so.

## Licence

Text and figures: CC BY 4.0. You may share and adapt them for any purpose, including commercially, if you give
credit: "Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted)", link the licence, and say if you
changed anything. The code releases carry their own licences.

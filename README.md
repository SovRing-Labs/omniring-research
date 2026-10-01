# OMNIRING research corpus

**Authors:** Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted)
**Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0), see `LICENSE.md`
**Copyright:** 2026 Juan Carlos De Santiago

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

The measured account of the system is the omni-ring `TECHNICAL-DISCLOSURE.md`. Where an older document here says
something those measurements later overturned, a `> Correction:` note cites the document that measured it. The four
corrections that matter most:

1. **A cue is mandatory.** Without one, decoding depends on the random codebook draw: a clean single mark decodes
   15/15 at some seeds and 1/15 at others. With any one ring clamped it succeeded at every draw tested. Unguided
   failures abstain rather than answer wrongly.
2. **Capacity is about 12 marks per slot at one cue.** 1,365 is the address space, not the number of marks a slot
   can hold.
3. **The fleet's first SOFTSWEEP harness was invalid** and was rewritten. No number from it appears here.
4. **TABU knockout was not adopted.** It rescued 11% of stuck settles and turned 18% into silent errors. A stuck
   settle should abstain.

## Part 2 (2026-10-01): geometry, the triangle memory, the substrate

The omni-ring `TECHNICAL-DISCLOSURE-PART-2.md` (release v0.1.1) is the measured account of the second phase: the
SuperSeed portable spec, the geometry of the sift, integrated-GPU execution, the triangle memory ("omnitri") and the
table / full-text / ring / matrix substrate. Essays 07–11 in `docs/essays/` tell how it was reached — the questions,
the steps, the twists and what was retracted. Research harnesses for Part 2 follow in weekly code updates.

## Contents

| File | What |
|---|---|
| `docs/01-ring1-core-cued-recall-and-capacity.md` | Cued recall, 16-level quantisation, confidence gap, slot capacity (≈12 at one cue) |
| `docs/02-ring1-check-ring.md` | The 17 check ring flags 81.8% of wrong settles with 0 false alarms |
| `docs/03-ring1-direct-keyed-storage.md` | Keyed direct read of single-mark slots (1000/1000, ≈11× faster); 1-bit tag for two marks |
| `docs/04-ring1-disperse.md` | Spreading marks over many slots does not beat one crowded slot (KILL): choosing the slot is the bottleneck |
| `docs/05-ring1-softsweep-decode-soft.md` | Soft resonator vs sequential probe: at k = 5, 300/300 vs 10/300 members recovered; cued decodes ≤ 1/300 silent-wrong per cell |
| `docs/06-ring3-peel-diamond-correl-tabu-fret.md` | Peeling (PASS), diamond facets, correlated codebooks, tabu, coarse-to-fine dials |
| `docs/07-peel-read-all-module.md` | Peeling moved into the engine: 16.65 of 24 marks per slot, 0/333 fakes |
| `docs/08-peer-review-retrieval-and-consolidation.md` | Peer review of the prototype, with its claim ledger |
| `docs/09-ring1-halo-two-stage-chain.md` | A two-stage halo chain ties the one-resonator and costs 2.5× the iterations (KILL) |
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
| `docs/essays/` | Readable editions of the research conversations (6 essays, plain language, speculation labelled) — start with `docs/essays/INDEX.md` |
| `docs/appendix/*.run.txt` | Raw run output cited by the documents above |
| `harness/` | The numpy research scripts that produced the numbers in docs 01–06, with relative paths; see `harness/README.md` |
| `MANIFEST.md` | Every candidate source document and the include/exclude decision for each |
| `PREP-REPORT.md` | The prep pass: what was processed, the verification output, and open questions for the author |

The documents keep their experiment names (RING-1, RING-3, …) so they can be cross-referenced. `harness/…` paths
name the numpy research scripts that produced the numbers; they ship here with every absolute path replaced by a
relative one, so you can re-run them.

## Code

- **omni-ring**: the ring memory engine (coprime rings, check ring, soft resonator, peeling, facets, mark store),
  with its `TECHNICAL-DISCLOSURE.md`.
- **vsa-core**: the shared-memory vector bus, ternary and phase kernels the engine runs on.

Both are released separately as source-available software, published as prior art.

## How it was made (AI-assistance disclosure)

This corpus was prepared with AI assistance: Claude (Anthropic), Gemini (Google) and the fleet's open-weight models
designed experiments, wrote harness code, ran reviews and drafted text. The author directed the work, chose what to
build and what to publish, and reviews every document before publication. AI systems are not authors in the legal
sense; the byline names the human author and discloses the assistance.

Every number in this corpus was measured on commodity hardware: a 2019 laptop CPU (Intel i5-8365U, AVX2, no GPU).
Raw AI chat transcripts are not published; where a document quotes one, it says so.

## Licence

Text and figures: CC BY 4.0. You may share and adapt them for any purpose, including commercially, if you give
credit: "Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted)", link the licence, and say if you
changed anything. The code releases carry their own licences.

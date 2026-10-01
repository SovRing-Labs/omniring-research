# Metaphor or mechanism: how review panels decided what to build

| | |
|---|---|
| **Date** | 2026-09-29 (panels held 2026-09-27 and 2026-09-28) |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Written with AI assistance (Claude) from the decision records of three review panels whose members were AI models, and a citation check. The panel inputs are not published. The author reviews this essay before publication. |
| **Type** | essay (readable edition of design decisions) |

## In one paragraph

Before the ring memory was built, three review panels were asked hard questions: should we build a resonator at
all, which ideas from other fields (optics, radio, physics, contemplative traditions) should change the design,
and is the choice of ring sizes right? The panels were made of AI reviewers, each told to look from a different
angle. Their most durable outputs were not mechanisms but rules: build the part that says "I am not sure" before
the part that answers; a claim from a study guide may not move a design parameter; thresholds are derived or
measured, never tuned to the test. The first panel's advice not to build the resonator yet was later overtaken by
measurements. The rules held.

## The words you need

- **Panel.** Nine independent reviews of the same question, then one written decision that reconciles them.
- **Lens.** The attitude of a reviewer: *reliability* (will it work?), *reimagine* (is there a simpler way?),
  *adversarial* (how would it fail?).
- **Altitude.** How far back the reviewer stands: the strategy, the structure, or the root arithmetic. Three
  lenses times three altitudes gives nine cells.
- **Kill criterion.** A pass/fail rule written before an experiment runs. If the result misses the bar, the idea
  is dropped ("KILL"), whatever anyone hoped.
- **Barycenter.** The average of all stored patterns. A resonator can settle there, which looks like an answer
  but is really a blend of everything.

## Panel 1: should we build a resonator now?

The first panel reviewed a proposal to add a resonator (the procedure that factors a blended vector into its
parts) to the fleet's shared memory. It had six literature dossiers and a plan.

**What it decided:** not yet. Build the reader's *trust layer* and the memory bus first, and put the resonator
behind measured kill criteria. The reasons, in plain terms:

- **Confidence before accuracy.** The most dangerous failure is a resonator that settles on the barycenter, a
  fixed point that averages everything. An accuracy number does not see it. So every read should report *how* it
  converged (one pattern, stuck between patterns, the global average, or not at all), not just what it found.
- **The data could not test it yet.** The real activity records at the time were too thin and unlabelled to
  support the experiment as written.
- **Cheap fixes first.** Small, independent improvements (centring the encoder's vectors, a faster bundling
  routine, many random seeds per claim, and a plain statistical baseline that any clever method must beat) were
  worth doing whatever happened to the resonator.
- **Fit the existing slot.** A vector of 5,120 dials with 16 positions each packs into exactly the 2,560 bytes of
  an existing bus slot. The panel chose that design point over larger ones that would have broken the slot format.

**What happened next.** The resonator was built and measured within two days, on synthetic data with
pre-registered kill criteria. The measurement supported the 16-position choice (quantising to 16 levels cost
nothing measurable) and the emphasis on confidence (the confidence gap sorts reads from 20% to 96% correct). The
"don't build yet" advice was overtaken; its reasoning about trust was not.

## Panel 2: which ideas from other fields change the design?

The author had studied a wide range of fields through AI-generated study guides: holography, cymatics, radio
codes (CDMA, Gold codes, OFDM), dynamical systems, dual-process psychology, and contemplative traditions. The
second panel asked which of these should move a design parameter, and which stay as metaphor.

**What it decided:** nearly all of it stays as metaphor. The design keeps its build order and gains three rules:

1. **Evidence tier.** No unverified or study-guide claim may move a parameter. A decision must cite a published
   source or our own measurement.
2. **No fitted thresholds.** Every threshold is derived, or measured on data held out from the test.
3. **One trust layer.** Confidence reporting lives in one place; no second, competing trust system.

It also corrected the record on several study-guide claims. For example, the asymmetric-codebook method in the
literature (ACF) freezes a one-sided change to one copy of a codebook; the study guide had described it as noise
injection. And a set of fidelity figures attributed to a quantised-phase paper were not in that paper. A separate
check confirmed that all 17 arXiv identifiers cited by the panel exist and match their topics. That check covers
existence only, not whether each claim matches its paper.

One engineering idea survived on its own merits: keep memory partitioned into many small slots rather than one
global superposition. The panel adopted it because our own design already needed it, not because of the optics
analogy that suggested it.

## Panel 3: are 3, 5, 7, 13 and 17 the right ring sizes?

The third panel checked the modulus choice for the ring memory: information rings of 3, 5, 7 and 13 (1,365
coordinates) and a check ring of 17.

**What it decided:** keep them. All three lenses agreed the arithmetic is correct. The exhaustive test of every
single-ring corruption (54,600 cases) found no missed error. A check ring of 16 is also valid (it shares no factor
with the others and is larger than 13) and would save one comparison per read, but it shrinks the combined space
from 23,205 to 21,840 combinations. The panel kept 17. It named two guardrails: never skip the check after
decoding, and keep codebook entries well separated, because a wrong answer that happens to be a legal coordinate
passes the check.

## What we measured

| Question the panels raised | Result | Source |
|---|---|---|
| Does the 17 check ring catch every single-ring slip? | Yes: 100% of 54,600 cases | technical disclosure §3, §12 |
| Does quantising dials to 16 positions cost recall? | No measurable cost | `../01-ring1-core-cued-recall-and-capacity.md`; disclosure §12 |
| Does confidence predict correctness? | Gap quartiles: 20% to 96% correct | `../01-…` |
| Does the check ring catch wrong settles in crowded slots? | 81.8% flagged, 0 false alarms; the rest pass silently | `../02-ring1-check-ring.md` |
| Does a stuck settle carry information? | Yes: forcing an answer turned 18% of stuck settles into silent errors | `../06-ring3-peel-diamond-correl-tabu-fret.md` |

## What did not hold up

- **"Don't build the resonator now."** Overtaken within two days by pre-registered measurements
  (`../01-…` to `../07-…`). The trust-first reasoning behind it stayed.
- **Study-guide claims presented as established.** Several were misattributed or were not established terms.
  The evidence-tier rule exists because of them.
- **Cross-field laws as design justification.** An optics scaling law was the clearest case of a metaphor driving
  a design argument. It was dropped; the design choice it supported was kept on other grounds.
- **Panels are not measurements.** One cell in each of the first two panels argued against adopting anything;
  in the second panel that cell also proposed a replacement no other cell supported. The decision records say so.
  A panel narrows the options; only an experiment settles them.

## Open questions

- **Speculative:** whether a different noise method the author proposed (inspired by iterated function systems)
  beats the published asymmetric-codebook method at breaking stuck settles. The panels asked for a direct A/B test
  with a written falsifier; its result is not part of this corpus.
- Should every deployment run a short behavioural smoke test that confirms the check is actually being applied?

## Sources

- Measured results: `../01-ring1-core-cued-recall-and-capacity.md`, `../02-ring1-check-ring.md`,
  `../06-ring3-peel-diamond-correl-tabu-fret.md`; the omni-ring `TECHNICAL-DISCLOSURE.md` (sections 2, 3, 12).
- Decision records: the resonator panel (2026-09-27), the cross-field panel and its citation check (2026-09-27),
  and the modulus panel (2026-09-28), all unpublished.
- Published work cited by the panels: S. J. Kent et al., arXiv 1906.11684; E. P. Frady et al., arXiv 2007.03748;
  *On the Role of Noise in Factorizers for Disentangling Distributed Representations*, arXiv 2412.00354;
  *qFHRR: Rethinking Fourier Holographic Reduced Representations through Quantized Phase and Integer Arithmetic*,
  arXiv 2604.25939; *A Grid Cell-Inspired Structured Vector Algebra for Cognitive Maps*, arXiv 2503.08608;
  *Capacity Analysis of Vector Symbolic Architectures*, arXiv 2301.10352.

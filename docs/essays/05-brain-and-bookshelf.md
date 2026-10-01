# The brain and the bookshelf: knowledge in the rings, a small model on top

| | |
|---|---|
| **Date** | 2026-09-29 (ideas from 2026-09-28 to 2026-09-29) |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Written with AI assistance (Claude) from the author's conversations with AI systems (Gemini, Claude) and an AI-drafted vision document. The conversations and the vision draft are not published; this essay paraphrases them and reports only numbers measured in this corpus. The author reviews it before publication. |
| **Type** | essay (readable edition; contains labelled speculation) |

## In one paragraph

Large language models keep their knowledge inside billions of trained weights. The idea explored here turns that
around: keep the knowledge in a verifiable ring memory (the bookshelf), and keep a small model on top whose only
job is to read it and reason (the brain). The idea has good precedent and a real design constraint behind it: a
small, low-power model cannot also be a library. But most of what was said about it in early drafts was vision,
not result. The memory side is built and measured. The model side is not trained. This essay separates the two.

## The words you need

- **Bus.** A block of shared memory holding many slots, each 2,560 bytes, that programs on one machine can read.
- **Slot.** One vector (5,120 dials of 16 positions, or equivalently 10,240 ternary values of −1, 0, +1). The two
  readings of the same bytes are called the **phase face** and the **ternary face**.
- **Head.** A small neural network (here, a transformer) that reads the bus and produces text or actions.
- **Seam.** The boundary where the large bus vector meets the much smaller model.
- **Shard.** The part of the memory held by one machine.
- **Hallucination.** A fluent answer that is wrong.

## The idea

In a conversation about building a knowledge base, the author asked whether it is better to bake knowledge into a
model or keep it in a searchable collection (a "dossier"). The answer, well established in the literature on
retrieval-augmented models, was the second: facts change and should be swappable; a model should hold skills.
The author then pushed further. Could keyword search, embedding search and the ring memory be one local engine?
Could the ring vectors themselves serve as a model's "weights"? And could a tiny model, well under 100 million
parameters, still learn to reason step by step if it never has to memorise facts?

The shape that came out of it:

- The **ring memory** holds verified marks: coordinates with a check ring, readable with a cue, able to abstain.
- A **small head** reads the bus through a bank of named slots (goal, time, entities, system state and so on)
  and does the reasoning and the wording.
- The **seam** between them must carry the whole vector, not a piece of it.

This design is written down in the omni-ring technical disclosure, section 10. Only the memory side and the seam
are built.

**Where the analogy stops.** A bookshelf holds whole books; a slot holds about a dozen small records before
reading degrades. The "bookshelf" is many small shelves, and choosing the right shelf is its own problem (below).

## Two defects at the seam, found and fixed

A peer review of the prototype (`../08-peer-review-retrieval-and-consolidation.md`, section 4) found two defects
exactly where memory meets model:

- **An undefined case in the ternary-to-phase conversion.** The neutral ternary pair (0, 0) had no mapping, so an
  all-zero vector converted to 93.75% made-up non-zero phases. Fixed by defining (0, 0) as phase 0: a null block
  stays null (technical disclosure, section 2).
- **Truncation instead of projection.** The model read only the first part of each slot and discarded 97.5% of
  it. For a design whose premise is that the bus holds the knowledge, that threw most of the knowledge away. Fixed
  with a fixed, seeded ±1 projection of the full slot (technical disclosure, section 10).

Both had survived behind a passing test suite, because the tests did not cover them.

## Many machines, one memory

The same conversation extended the idea to machines: each device holds its own lightly loaded shard, a cue is
broadcast, every shard answers only with results that pass its check ring, and the strongest verified answer
wins. Devices can exchange marks (a few bytes) rather than vectors, because every machine can rebuild a vector
from a shared codebook seed (technical disclosure, section 11).

**Measured at small scale, within one machine** (`../04-ring1-disperse.md`): spreading marks over many lightly
loaded slots keeps recall inside the right slot high (about 94%), but picking *which* slot holds the answer is
the bottleneck when every slot looks alike, and spreading did not beat one crowded slot. Cross-machine sharding has
not been measured.

## Speculative: a "resonator cortex"

An AI-drafted vision document went much further. **Everything in this section is speculation.** It proposed:

- knowledge compiled by an agent into new memory shards in seconds, with no retraining;
- a resonator that scans thousands of shards and mounts the relevant ones into a small working bank;
- a compact transformer that turns the verified result into fluent language;
- continuous learning of the small projection layers with forward-only (zeroth-order) optimisation, which needs
  no stored activations;
- a larger ring set (seven coprime moduli, 7, 11, 13, 17, 19, 23 and 29) to give every token its own
  coordinate (the draft put the space at about 8.6 million coordinates; the product of those moduli is in fact
  about 216 million, so its arithmetic needs redoing);
- hierarchical rings (root, domain, leaf) so no single slot is overfilled.

Some of these are reasonable directions. The hierarchy follows directly from the measured capacity of about 12
marks per slot and the dispersal result above. Zeroth-order optimisation is published work (MeZO, arXiv
2305.17333). None of them is built or measured here, and the performance table in that draft (retrieval times,
ingestion times, "zero" forgetting, "zero" hallucination) should not be read as results.

## What we measured

| Question | Result | Source |
|---|---|---|
| Clean single mark round trip | 1,365 / 1,365 | disclosure §12; `../08-…` |
| Bind / dot at 10,240 ternary dimensions (AVX2) | about 35 ns / 93 ns | disclosure §12 |
| Full scan of 1,000 slots | 145 µs | disclosure §12 |
| All-zero vector before the transcode fix | 93.75% fabricated phases | `../08-…` §4 (D1) |
| Share of each slot the model saw before the projection fix | 2.5% (97.5% discarded) | `../08-…` §4 (D2) |
| Capacity per slot at one cue | about 12 marks | `../01-ring1-core-cued-recall-and-capacity.md` |
| Recall given the right slot, dispersed layout | about 94% (slot choice is the bottleneck) | `../04-ring1-disperse.md` |
| Cued decode, silent-wrong rate | 1 in 1,200 at up to 10 marks | disclosure §12; `../05-ring1-softsweep-decode-soft.md` |

## What did not hold up

These are the prototype-era claims that the peer review's claim ledger marked false or unbuilt
(`../08-…`, section 6):

- **"Zero factual hallucination."** False. The check ring proves a decoded address is internally consistent
  (integrity), not that it is the right answer (accuracy). In one measured case, two marks (7 and 300) stored
  together decoded to 1197, which is neither, and passed the check.
- **"A 500M–1.5B resonant transformer engine."** Not built. The prototype's model weights were seeded random
  values, never trained.
- **"57 of 57 tests passing."** True, but it certified that the code agrees with itself, not that anything learns.
- **"Over a million combinations."** False for the verifiable coordinates: there are 1,365.
- **"Hundreds to a thousand facts per slot."** The measured figure is about 12 marks per slot at one cue.
- **"Nothing can forget."** This was a real gap at review time. A mark store with a rehearsal counter and decay was
  built afterwards (disclosure, section 9).

The claim the project now makes instead, because every clause can be checked: addresses and contents are
integrity-checked by the 17 ring; retrieval accuracy on crowded slots is measured, not assumed; the system can
abstain at every gate; the working memory is a fixed size on an ordinary CPU.

## Open questions

- **The head.** Can a small model be trained to read the bus and reason over what it reads? This is the largest
  open question in the project, and nothing here answers it.
- **Which face holds knowledge?** The phase face gives exact, verifiable coordinates; the ternary face gives fast,
  fuzzy similarity. Applications need different mixes, and the choice is not settled.
- **Speculative:** whether seven-ring coordinate spaces remain readable. Larger rings and more of them add free
  factors, and the facet measurements show that free factors make reading harder
  (`../06-ring3-peel-diamond-correl-tabu-fret.md`, DIAMOND-2).

## Sources

- Measured results: `../08-peer-review-retrieval-and-consolidation.md`, `../01-ring1-core-cued-recall-and-capacity.md`,
  `../04-ring1-disperse.md`, `../05-ring1-softsweep-decode-soft.md`, `../06-ring3-peel-diamond-correl-tabu-fret.md`;
  the omni-ring `TECHNICAL-DISCLOSURE.md` (sections 2, 9, 10, 11, 12).
- Idea lineage: the author's knowledge-base conversation (Gemini, with an embedded Claude analysis) and an
  AI-drafted "resonator cortex" vision (both unpublished).
- Published work: S. Malladi et al., *Fine-Tuning Language Models with Just Forward Passes* (MeZO), arXiv
  2305.17333. Retrieval-augmented and memory-augmented models: S. Borgeaud et al., *Improving language models by
  retrieving from trillions of tokens* (RETRO), arXiv 2112.04426; U. Khandelwal et al., *Generalization through
  Memorization: Nearest Neighbor Language Models*, arXiv 1911.00172; Y. Wu et al., *Memorizing Transformers*, arXiv
  2203.08913.

# Rings around a resonator: where OMNIRING came from

| | |
|---|---|
| **Date** | 2026-09-29 (ideas from 2026-09-27 to 2026-09-28) |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Written with AI assistance (Claude) from the author's study conversations with AI systems (Gemini, Claude). The conversations are not published; this essay paraphrases the ideas and reports only numbers measured in this corpus. The author reviews it before publication. |
| **Type** | essay (readable edition of an idea lineage) |

## In one paragraph

OMNIRING began as a picture, not a plan: one resonator in the middle, with a few rings of different sizes
turning around it, and the answer sitting wherever the rings line up. The picture turned out to describe a real
mechanism. Rings whose sizes share no common factor (3, 5, 7 and 13) can name 1,365 distinct positions while
each ring stays tiny, and a fifth, redundant ring of size 17 can catch any single ring that slips. This essay
follows how that picture formed, which parts of it survived measurement, and which parts did not.

## The words you need

- **Vector.** A long list of numbers. Here each list has 5,120 entries, and every entry is a small dial with 16
  positions (a "phase").
- **Mark.** One small stored record, such as "task 412 finished at beat 57".
- **Slot.** One vector that holds one or more marks added together.
- **Binding.** Combining two vectors into one by turning each dial of the first by the matching dial of the
  second. It can be undone exactly.
- **Ring.** A small set of vectors that stand for the positions 0, 1, 2 … of a counter that wraps around, like a
  clock face. A ring of size 7 has seven positions.
- **Codebook.** The list of vectors a ring (or any category) can take.
- **Resonator.** A procedure that looks at a slot and works out which position of each ring produced it. It
  starts every ring as a blur of all its positions and lets them settle together.
- **CRT (Chinese Remainder Theorem).** An ancient rule (first recorded in a Chinese arithmetic text, *Sunzi Suanjing*): if you know a number's remainders after dividing by
  3, 5, 7 and 13, and those divisors share no factors, you know the number itself, up to 3 × 5 × 7 × 13 = 1,365.
- **Check ring.** An extra ring that carries no new information. It exists so that disagreement between rings
  can be noticed.
- **Cue.** A position you already know and pin in place before the resonator runs (for example, "it was the
  13-ring's position 4").

## The picture

The author was working through a set of study conversations about the vocabulary of vector-symbolic computing:
residue arithmetic, grid cells in the brain, radio codes, holography. While reading about the Chinese Remainder
Theorem, he imagined a single resonator with three, five or seven rings banded around it, each turning on its own
axis, and asked whether the overlap of the rings would multiply what the system could hold.

That picture joins three things that already existed in the project's material:

1. **Dials.** Every entry of a vector is a 16-position dial, and binding is dial-turning. So "rotation" is
   literally the arithmetic the system already does.
2. **The resonator.** A known method (the resonator network) factors a bound vector by keeping one codebook per
   factor and letting all the guesses improve together.
3. **Grid cells and CRT.** The brain appears to track position with several modules of different sizes. Each
   module alone is ambiguous; together they pin a location down. That is the Chinese Remainder Theorem at work.

Put together: rings of coprime sizes, turning around a resonator, with the answer in the overlap. The author
arrived at this independently. The same idea had already been published by the group that invented resonator
networks (Kymn et al., *Computing with Residue Numbers in High-Dimensional Representation*, arXiv 2311.04872).
Finding that paper was good news: it meant the intuition pointed at a real research direction.

## Why the sizes must share no factors

Picture gears with 3, 5 and 7 teeth all advancing one tick at a time. Each gear repeats quickly, but the three
together do not return to their starting arrangement until tick 3 × 5 × 7 = 105. Gears of 4 and 6 teeth, which
share a factor of 2, line up again after only 12 ticks. That is plain arithmetic (the least common multiple), and
it is the whole reason the rings are 3, 5, 7 and 13: every coordinate below 1,365 gets its own unique
arrangement.

People have built this interlock before. The Maya ritual calendar meshes a 13-number cycle with a 20-name cycle
into 260 days; the Chinese sexagenary cycle meshes 10 and 12; the Balinese Pawukon runs ten weeks of different
lengths at once and defines a day by where they all land. The Antikythera mechanism chose its gear sizes for the
same reason. These were useful confirmations of the shape of the idea, not evidence that it works in vectors.

**Where the analogy stops.** A calendar shows that coprime cycles give unique names. It says nothing about reading
several names back out of one blended vector. That is the hard part, and the rest of the corpus is about it.

## The timing chain

The 13-ring was first imagined as a "timing chain" that drives the others. In vector form this became exact: one
extra binding step (a "tick") moves every ring forward one position at once, so the encoding of 41, ticked once,
is the encoding of 42. The rings together are a clock, and the clock can stamp *when* a mark was written. The
omni-ring technical disclosure (section 3) describes this; it treats the clock as a cue, not as the payload.

## The fifth ring: more room, or a way to catch mistakes?

With four rings holding 1,365 positions, the obvious next move was a fifth ring for more room. The choice made
instead was a **check ring**: a redundant ring of size 17 whose position is fully determined by the other four.
If the rings disagree, something went wrong, either a ring slipped or the resonator settled on a wrong answer.

Two rules came out of this:

- The check ring must be **larger than every ring it guards**. An early exploratory demo with a smaller check
  ring (11) let a few 13-ring errors through; with 17 none got through.
- Because most combinations of the five rings are illegal, a wrong settle usually lands on an illegal one and is
  caught. A later three-lens review confirmed the choice of 17 over 16 (16 is also coprime and larger than 13, and
  would save one probe, but it shrinks the combined five-ring space from 23,205 to 21,840).

## "Just go to the coordinates"

The author asked whether the system could skip calculation entirely and go straight to the coordinates. For a
slot that holds a single mark, the answer is yes. Store each ring side by side with its own random key, read
each ring by picking its best match (3 + 5 + 7 + 13 + 17 = 45 comparisons), and apply the CRT formula. No
resonator is needed. For a slot holding several marks, every ring shows the right positions but nobody knows
which position belongs to which mark. That "whose is whose" problem is exactly what binding and the resonator
exist to solve.

## Why the rings must spin together

One more piece of the picture turned out to matter. Decoding one ring at a time, committing each before moving to
the next, gets stuck: a small early experiment settled on (0, 2, 1) instead of the true (1, 3, 2) and never
recovered. Letting every ring start as a blur of all its positions and settle *together* decoded all 105
combinations of 3, 5 and 7 correctly (reported in `../08-peer-review-retrieval-and-consolidation.md`, section 2).
The motion in the picture was not decoration. A ring forced to commit while the others are still wrong cannot find
its place.

A related lesson came from a conversation about atoms. Binding is reversible, like the smooth evolution of a
quantum state; picking the best match (argmax) is like a measurement, irreversible and lossy. So: keep the state
blurred as long as possible and "measure" once, at the end. This is a design rule, and the analogy ends there.

## What we measured

All numbers below were measured on a 2019 laptop CPU (Intel i5-8365U, no GPU).

| Claim | Result | Source |
|---|---|---|
| The 17 check ring catches any single-ring slip | 100%, exhaustive over 54,600 cases | technical disclosure §3, §12 |
| A clean single mark round-trips | 1,365 / 1,365 | technical disclosure §12; `../08-peer-review-retrieval-and-consolidation.md` |
| Keyed direct read of single-mark slots | 1,000 / 1,000, about 11× faster than resonating | `../03-ring1-direct-keyed-storage.md` |
| Two marks share a slot with a 1-bit tag | 300 / 300 (267 / 300 untagged) | `../03-ring1-direct-keyed-storage.md` |
| Cued recall, 12 marks in a slot, one ring pinned | 67% (chance 8%); two rings pinned: 93% | `../01-ring1-core-cued-recall-and-capacity.md` |
| Capacity: largest load with at least 50% recall at one cue | about 12 marks per slot | `../01-ring1-core-cued-recall-and-capacity.md` |
| Check ring on wrong settles in crowded slots | flags 81.8%, 0 false alarms | `../02-ring1-check-ring.md` |
| Confidence gap (best minus runner-up) predicts correctness | lowest quartile 20% correct, highest 96% | `../01-ring1-core-cued-recall-and-capacity.md` |

## What did not hold up

- **"Instant, no calculation, unlimited scale."** Every settle costs compute, and a slot has a ceiling of about a
  dozen marks at one cue. At 12 marks, cued recall is 67%, not 100% (`../01-…`).
- **"1,365 is the capacity."** 1,365 is the address space, the number of names. What one slot can actually hold
  and read back is about 12 marks (`../01-…`, and the correction in `../08-…`).
- **"The rings can be read without a cue."** Without a pinned ring, whether decoding works depends on the random
  draw of the codebooks: a clean single mark decoded 15/15 at some draws and 1/15 at others. With any one ring
  pinned it worked at every draw tested (`../06-ring3-peel-diamond-correl-tabu-fret.md`, "Harness disclosure").
  Every query now carries a cue.
- **"The check ring means zero wrong answers."** It catches a slipped ring, and it flags most wrong settles
  (81.8%), but a wrong answer that happens to be a legal coordinate passes (`../02-…`, `../08-…` section 6).
- **Letters as positions on the 13-ring.** A and N collide on a 13-ring, and alphabet order carries no meaning.
  Words are better treated as category vectors bound onto a counter position.
- **"Four rings per 512-bit register."** The measurement host has no AVX-512; it has AVX2. The arithmetic did not
  apply.
- **Physics analogies taken literally.** Atoms do not bond through the zero between them (that node marks the
  antibonding orbital), and quantum numbers are nested (each depends on the one before), unlike independent
  coprime rings. There is no free energy: every settle costs work.

## Open questions

- **A 15-position dial.** A dial of 15 positions (3 × 5) still fits in 4 bits and would build two coprime rings
  into the main phase layer. Untested.
- **Smooth time.** Residue rings give exact names: beat 57 and beat 58 look unrelated. "Around when" needs a
  smoothly turning dial. See essay `03-tuning-the-string.md`.
- **Speculative:** whether the same coprime-ring and checksum pattern can organise larger structures (systems of
  rings inside a record, shards across machines). The disclosure describes the design (sections 7 and 11); it
  has not been measured at machine scale.

## Sources

- Measured results: `../01-ring1-core-cued-recall-and-capacity.md`, `../02-ring1-check-ring.md`,
  `../03-ring1-direct-keyed-storage.md`, `../06-ring3-peel-diamond-correl-tabu-fret.md`,
  `../08-peer-review-retrieval-and-consolidation.md`; the omni-ring `TECHNICAL-DISCLOSURE.md` (sections 3–5, 12).
- Idea lineage: the author's study conversations with Gemini and Claude and the review that sorted them into
  kept, tested and dropped (unpublished working notes); a three-lens review of the modulus choice (unpublished).
- Published work: C. J. Kymn, D. Kleyko, E. P. Frady, C. Bybee, P. Kanerva, F. T. Sommer, B. A. Olshausen,
  *Computing with Residue Numbers in High-Dimensional Representation*, arXiv 2311.04872. E. P. Frady, S. J. Kent,
  B. A. Olshausen, F. T. Sommer, *Resonator networks for factoring distributed representations of data
  structures*, arXiv 2007.03748. S. J. Kent et al., *Resonator Networks outperform optimization methods at
  solving high-dimensional vector factorization*, arXiv 1906.11684.

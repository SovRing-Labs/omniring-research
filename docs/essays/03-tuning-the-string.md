# Tuning the string: similar items, continuous dials and diamond facets

| | |
|---|---|
| **Date** | 2026-09-29 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Written with AI assistance (Claude) from the author's conversations with AI systems (Gemini, Claude). The conversations are not published; this essay paraphrases the ideas and reports only numbers measured in this corpus. The author reviews it before publication. |
| **Type** | essay (readable edition of an idea lineage) |

## In one paragraph

A guitar's D string can play many notes, and a player retunes it while playing. The author used that picture to
ask three questions of the resonator. What actually makes it resonate? What happens when a thousand stored items
are nearly identical, like one symbol rotated slightly each time? And can the resonator be tuned while it is
answering? The measurements answered the first two in useful ways: similar items can be tolerated up to a point
and "tuning the listener" recovers much of the loss, and a continuous dial reads nearly identical items well. The
third question, tuning mid-query, remains open.

## The words you need

- **Resonator.** The procedure that reads a slot by letting every ring's guess settle together (see essay
  `01-rings-around-a-resonator.md`).
- **Codebook.** The set of vectors a ring or category can take. Each entry is like one note the string can play.
- **Neighbour similarity.** How much two neighbouring codebook entries look alike, from 0 (unrelated) to 1
  (identical).
- **Whitening.** A read-time correction that removes the part all codebook entries share, so their differences
  stand out.
- **Dial (fractional power encoding).** A way to store a continuous quantity, such as time or angle, so that
  nearby values produce similar vectors. Instead of a ring with a fixed number of positions, the vector turns by a
  fraction for each unit.
- **Facet ("diamond").** A record built from several small categorical codebooks (the corners), with a checksum
  ring in the centre.

## What makes it resonate

The author's first point: the resonance is already in the string; the string holds all the notes, and it is the
pluck that makes one of them ring. A tuning fork does not test every sound in the room; its shape amplifies the
one frequency that fits and cancels the rest.

That is a fair description of how the resonator differs from a database lookup. It does not try the 1,365
coordinates one by one. It compares the slot against every entry of each small ring at once (3 + 5 + 7 + 13 + 17
comparisons per pass), and the matching entry stands out because non-matching entries tend to cancel. The cost
grows with the *sum* of the ring sizes, not their product (technical disclosure, section 4).

**Where the analogy stops.** A tuning fork rings instantly and for free. The resonator runs several passes and
each pass costs arithmetic. And it only rings for notes already in its codebooks: it recognises, it does not
compose.

In the conversation, "tuning" was split into three parts, which map onto the system like this:

| In the picture | In the system | Status |
|---|---|---|
| Shaping the fork | Choosing codebooks whose entries are distinct | Measured: see below |
| Learning the pluck | A trained model forming the query | Not built |
| A palm muting the other strings | Suppressing runner-up answers | Partly present (negative scores are zeroed; see essay `02-the-jump-rope.md`) |

## Many nearly identical notes

Suppose many stored items differ only slightly. Their codebook vectors are then similar, and striking one makes
the others ring in sympathy. The conversation's advice was to force every concept to be perfectly distinct.
The measurement was more forgiving, and gave a better tool.

**Measured** (`../06-ring3-peel-diamond-correl-tabu-fret.md`, CORREL; 4 marks per slot, 13 ring cued):

| Neighbour similarity | Plain read | Whitened read |
|---|---|---|
| 0.00 | 86.7% | 86.7% |
| 0.35 | 89.3% | 90.0% |
| 0.80 | 52.0% | 75.3% |
| 0.93 | 8.7% | 18.0% |

A moderate similarity (0.35) cost nothing. High similarity (0.80) halved recall, and read-time whitening ("tune
the listener, not the instrument") brought much of it back. At 0.93 nothing works. The pre-registered test was
formally a KILL, because it predicted that 0.35 would already hurt, and it did not.

## The same symbol, rotated slightly each time

The author's sharper case: a thousand items that are the same symbol at slightly different rotations, like a
fractal drawn with a small twist each time. A resonator that treats them as a thousand separate notes has nothing
to choose between them.

The conversation's answer was to store the symbol once and the rotation separately, as a continuous dial, and ask
the resonator for the angle rather than for one of a thousand items. That is the dial (fractional power encoding,
technical disclosure section 8), and it is what the FRET test measured.

**Measured** (`../06-…`, FRET; 1,000-tick dial, 20 symbols):

| Items in the slot | Angles | Flat search over 1,000 dial positions | Coarse-to-fine |
|---|---|---|---|
| 1 | spread out | 100% | 100% |
| 6 | clustered within 60 ticks | 92.0% | 98.0% |
| 12 | clustered within 60 ticks | 93.3% | 90.0% |

Even with 12 near-identical items packed within 60 ticks, a plain search over the dial found symbol and angle
93% of the time. A cheaper coarse-to-fine search (low-frequency dimensions on a 20-tick grid, then a local scan)
was not better, so the test was a KILL for coarse-to-fine; it remains a valid cheaper variant. The practical rule
the disclosure keeps: **use a dial as a cue** ("around when"), not as a factor to be discovered inside a crowded
slot.

This also explained an earlier failure. A first attempt at a smooth "around when" ring (RING-1 T2) had failed;
FRET showed the dial itself was not the problem. The failure came from crowding and the surrounding rings.

## Many small strings: diamond facets

A record often has several parts: what, who, where, when. The "diamond" idea gives each part its own small
codebook (a corner) and adds a centre ring whose position is a checksum of the corners, so known corners act as
cues and the centre flags inconsistent answers.

**Measured** (`../06-…`, DIAMOND and DIAMOND-2; 12 marks per slot, 2 corners known):

| Design | Both unknown corners recovered |
|---|---|
| Corners of 105 values each | 35.3% |
| Corners of 35 values each | 70.0% |
| Corners of 15 values each | 90.7% |
| 105-value corners split into 3 × 5 × 7 sub-rings | 4.7% |
| Flat residue rings with 2 cues (baseline) | 96.0% |

The centre checksum flagged 93% of wrong settles. The rule: **corner size is the lever.** Few free facets, each
small, with the checksum kept. Splitting a corner into more sub-rings adds free factors and collapses recall.

**Where the analogy stops.** A diamond's facets are fixed by its crystal. Here the number and size of the facets
is a design choice, and the measurement is what decides it.

## Tuning while playing

The last question was whether the resonator could retune itself mid-query, the way a player bends a note into
tune, perhaps with a small learning step inside each read (the conversation connected this to fast weights,
test-time training and active inference).

**Speculative:** nothing of this kind has been built or measured. Two measured results bear on it. Read-time
whitening is a fixed, non-learned form of "tuning the listener", and it helped (above). And the confidence gap
(best minus runner-up score) already tells a read whether it is in tune: the lowest quartile of gaps was 20%
correct and the highest 96% (`../01-ring1-core-cued-recall-and-capacity.md`). A mid-query learning step would have
to beat both, and would need a pre-registered test.

## What we measured

| Question | Result | Source |
|---|---|---|
| Cost of moderately similar codebooks (0.35) | none measurable | `../06-…` CORREL |
| Recovery from high similarity (0.80) by whitening | 52% → 75% | `../06-…` CORREL; disclosure §12 |
| Dial with 12 near-identical items | 93.3% flat; coarse-to-fine 90.0% | `../06-…` FRET |
| Facets with 15-value corners, 2 known, 12 marks | 90.7% | `../06-…` DIAMOND-2; disclosure §12 |
| Centre checksum on wrong settles | flags 93% | `../06-…` DIAMOND; disclosure §12 |
| Confidence gap vs correctness | 20% (lowest quartile) to 96% (highest) | `../01-…` |

## What did not hold up

- **"Force every concept to be perfectly orthogonal."** Not necessary: moderate similarity was free, and random
  codebooks at this size have headroom.
- **"Coarse-to-fine is the answer for continuous items."** It was not better than a flat dial search.
- **"Large facet corners read like small ones."** 105-value corners recovered 35%, against 91% for 15-value
  corners.
- **"The resonator locks with 100% clarity by the third or fourth cycle."** Not measured, and inconsistent with a
  measured capacity of about 12 marks per slot at one cue.

## Open questions

- Can a read tune itself in a way that beats fixed whitening, without adding silent errors?
- Which periods should a dial use? The plan is to choose them from the spectrum of real activity data, not by
  hand. Not yet done.

## Sources

- Measured results: `../06-ring3-peel-diamond-correl-tabu-fret.md` (with `../appendix/RING3-RESULTS.run.txt`,
  `../appendix/RING3b-DIAMOND2.run.txt`), `../01-ring1-core-cued-recall-and-capacity.md`; the omni-ring
  `TECHNICAL-DISCLOSURE.md` (sections 4, 7, 8, 12).
- Idea lineage: the author's D-string conversation with Gemini (unpublished).
- Published work: E. P. Frady, D. Kleyko, C. J. Kymn, B. A. Olshausen, F. T. Sommer, *Computing on Functions Using
  Randomized Vector Representations*, arXiv 2109.03429 (fractional power encoding).

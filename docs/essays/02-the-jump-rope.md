# The jump rope: telling crowded marks apart

| | |
|---|---|
| **Date** | 2026-09-29 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Written with AI assistance (Claude) from the author's conversations with AI systems (Gemini, Claude) and from a machine-written review of the RING-3 experiments. The conversations are not published; this essay paraphrases the ideas and reports only numbers measured in this corpus. The author reviews it before publication. |
| **Type** | essay (readable edition of an idea lineage) |

## In one paragraph

A slot that holds one mark is easy to read. A slot that holds a dozen is like a jump-rope game with a dozen
invisible jumpers in the same ropes: you feel all their ropes at once. The author's jump-rope picture asked two
questions. How do you find the one real jumper? And can the rhythm of the other ropes help clear away the wrong
ones? The first question led to **peeling**, now part of the engine. The second led to three concrete suggestions
from an AI reviewer; two were measured and did not help, and one describes something the resonator already does.

## The picture

Imagine ropes turning at 3, 5 and 7 beats. Rope A passes under your feet every 3rd jump, rope B every 5th, rope C
every 7th. Where you are in the pattern tells you exactly which jump you are on, up to 105. One jumper is one
stored mark.

Now put several jumpers into the same ropes, each on a different jump count, and blindfold yourself. You feel all
their ropes blended together. With up to about a dozen jumpers you can still lock onto one, especially if someone
whispers one rope's position to you. Beyond that the blend gets too thick.

In the system's terms:

| In the picture | In the system |
|---|---|
| A rope turning at 3, 5, 7 … beats | A **ring**: a set of vectors standing for the positions of a counter of that size |
| One jumper | One **mark**, a stored coordinate |
| Several jumpers in the same ropes | Several marks added into one **slot** |
| The whisper | A **cue**: one ring's position pinned before reading |
| Locking onto one jumper | The **resonator** settling on one mark |
| "The blend gets too thick" | The slot's **capacity**: about 12 marks at one cue |

**Where the analogy stops.** Real ropes do not blur into each other; the vectors do, because adding marks into
one vector mixes them. And the whisper does more than help: without it, reading fails at some random codebook
draws. The cue is mandatory, not a courtesy.

## Idea 1: every time my rope lands, clear a ghost

The author proposed that each time "his" rope hits the ground, another ghost jumper could be cleared away, so that
after a handful of jumps only the real one is left, with no need to work out each jumper's speed.

That is **peeling**, also called explaining away. Read one mark with a cue. If the check ring (the redundant 17
ring that flags inconsistent answers) says the result is legal, accept it and subtract that mark from the slot.
The loudest jumper is gone, so the quieter ones become easier to hear. Sweep through every value of the cue ring,
then sweep again over what is left.

**Measured.** In the research harness, two cued sweeps with peeling read 14.8 of 24 marks per slot, against 8.45
for one plain sweep (+75%), with 3.6% accepted fakes (`../06-ring3-peel-diamond-correl-tabu-fret.md`, PEEL).
Built into the engine with a confidence floor, it read 16.65 of 24 marks per slot with 0 fakes in 333 accepted
reads (`../07-peel-read-all-module.md`). Peeling passed its pre-registered test and ships in omni-ring.

## Idea 2: use the other ropes' rhythm to clear similar ghosts

The author then asked whether the rhythms of the other jumpers could be used to clear similar wrong answers
*proactively*, rather than waiting for them to fade. An AI conversation offered three mechanisms. Each is taken in
turn.

### Lateral inhibition: the stronger guess suppresses its neighbours

The idea: as one guess gains strength, it pushes down the competing guesses near it.

The resonator already has a mild form of this. At each step, any codebook entry whose match score is negative is
set to zero before the ring's new estimate is formed, so negative evidence cannot spread from one ring to the others
(technical disclosure section 4; `../08-peer-review-retrieval-and-consolidation.md` section 3). No stronger
version was measured. The conversation's claim that inhibition makes reading "10× faster" was never tested and
should not be repeated as a result.

### Orthogonal deflation: mute the found rope entirely

The idea: once a rope is found, do not merely subtract it; project the rest of the slot so it becomes "deaf" to
that rope, so noise cannot leak back in. An AI review of RING-3 recommended exactly this for peeling, on the grounds
that subtracting a slightly noisy estimate injects error that accumulates.

**Measured:** no difference. At 24 marks per slot, projection read 15.18 true marks per slot with 3.1% fakes;
plain subtraction read 15.14 with 3.2% (`../06-…`, "Exploratory arms"). The reason is simple: peeling subtracts the
*exact* codeword of a verified mark, not a noisy estimate, so there is no residual error for deflation to remove.

### Group testing: sieve out whole families at once

The idea: ask the blended slot broad questions ("is any jumper on an even rhythm?") and discard large parts of
the codebook in one step before the careful search begins.

Not measured. **Speculative:** this may be useful when codebooks are very large. OMNIRING's rings are small (3 to 17
positions) and the resonator already costs the sum of the ring sizes, not their product, so the gain here is
unclear.

## Idea 3: when the resonator gets stuck, knock out its favourite and vote

A related proposal, **tabu knockout**: when a settle is stuck (illegal under the check ring, or never converging),
forbid the positions it keeps choosing, settle again several ways, and take a majority vote. The AI review suggested
weighting that vote by each settle's confidence gap instead of a flat count.

**Measured:** tabu rescued 11.4% of stuck settles and turned 18.2% of them into silent errors, wrong answers
that pass the check. The confidence-weighted vote rescued slightly more (13.6%) but raised silent errors to 45.5%,
because it always picks something (`../06-…`, TABU and "Exploratory arms"). Tabu was not adopted.

The lesson is the most important one in this essay: **a stuck settle is information.** Detecting that the system
does not know is the value. The right response is to abstain, not to force an answer.

## What we measured

| Question | Result | Source |
|---|---|---|
| Can a crowded slot be read one mark at a time? | Yes: 14.8 of 24 per slot with peeling vs 8.45 without; 3.6% fakes | `../06-…` PEEL |
| Peeling in the engine, with a confidence floor | 16.65 of 24 per slot, 0 / 333 fakes | `../07-peel-read-all-module.md` |
| Does projection (deflation) beat exact subtraction? | No: 15.18 vs 15.14 true per slot | `../06-…` exploratory arms |
| Does knockout rescue stuck settles? | 11.4% rescued, 18.2% silent-wrong: not adopted | `../06-…` TABU |
| Does a confidence-weighted vote help? | Worse: 45.5% silent-wrong | `../06-…` exploratory arms |
| Capacity at one cue | about 12 marks per slot | `../01-ring1-core-cued-recall-and-capacity.md` |

## What did not hold up

- **"The resonator isolates the single correct fact with 100% certainty and lets you bundle thousands of concepts
  in one vector."** Measured capacity is about 12 marks per slot at one cue, and even cued decodes have a small
  silent-wrong rate (1 in 1,200 at up to 10 marks; technical disclosure section 12, `../05-ring1-softsweep-decode-soft.md`).
- **"Deflation and inhibition settle in 2–3 cycles instead of 12."** Not measured. Deflation made no difference
  where it was tested.
- **"Forcing an answer out of a stuck settle."** Measured as harmful. Abstain instead.

## Open questions

- **Chained resonators.** The author also pictured one resonator whose settled output becomes the cue for the next
  ("the wave it calls becomes a second"). A two-stage chain was tested as RING-1 T4 and did not beat a single
  resonator; that report is still being cleaned for this corpus. Peeling is the form of the idea that worked.
- **Speculative:** whether group testing earns its place with much larger category codebooks.

## Sources

- Measured results: `../06-ring3-peel-diamond-correl-tabu-fret.md` (with `../appendix/RING3-RESULTS.run.txt`,
  `../appendix/RING3-RECS.run.txt`), `../07-peel-read-all-module.md`, `../05-ring1-softsweep-decode-soft.md`,
  `../01-ring1-core-cued-recall-and-capacity.md`, `../08-peer-review-retrieval-and-consolidation.md`; the omni-ring
  `TECHNICAL-DISCLOSURE.md` (sections 4, 6, 12).
- Idea lineage: the author's jump-rope conversation with Gemini, and an AI-written review of RING-3 with
  recommendations (both unpublished).
- Published work: E. P. Frady et al., *Resonator networks for factoring distributed representations of data
  structures*, arXiv 2007.03748.

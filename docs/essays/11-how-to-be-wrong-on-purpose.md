# How to be wrong on purpose: the method behind the results

| | |
|---|---|
| **Date** | 2026-10-01 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Written with AI assistance (Claude) from the research log of 30 September – 1 October 2026 (unpublished). The author reviews it before publication. |
| **Type** | essay — method; numbers cited to the omni-ring Technical Disclosure Part 2 (`P2 §n`) |

## In one paragraph

Ideas in this project arrive fast and often as images — rings, ropes, triangles, polygons. Images are how the author
thinks, and they are good at finding what to try. They are bad at saying whether it worked. So every idea that became
an experiment went through the same gate: write down, before running anything, what result would count as a pass and
what would kill the idea. Over two days that produced passes, kills and a few retractions, all published together.

## The rules

1. **Search the field first.** Before calling an idea new, look for it. The triangle memory has close relatives
   (TorusE, RotatE); the ternary embedder already existed (BitNet). Lead with what exists, then say what differs.
2. **Pre-register.** Data, operationalisation, pass bar and kill bar are written into the research log before the
   harness runs. Harness changes made before results are seen are recorded as such.
3. **Report failures with the same weight as passes.** Part 2 has a section of limits and negative results (P2 §9).
4. **Never re-score after the fact.** If a bar turns out to be badly chosen, the result stays a failure and a separate,
   labelled diagnostic explains why.
5. **Physical proof.** Every number has a result file; every claim in the disclosure maps to one.

## Four times the method changed the story

**The speed claim that was retracted.** Early in the triangle work, chaining through the vector memory looked 130 to
2,100 times faster than the project's own logic engine. A fair comparison against an indexed database reversed it:
the database was about 250 times faster on exact chains (P2 §8). The claim was withdrawn in writing, and the design
changed: exact truth went to tables.

**The safety bar that was set wrong.** The sifter-core test borrowed a threshold from an experiment with buckets four
times smaller. It failed. Rather than move the bar, a diagnostic was added and labelled as one: even without the core,
full buckets could not separate absent facts from present ones (P2 §9). The conclusion got stronger, not weaker.

**The code that wasted the machine.** The author noticed one processor core pinned while seven idled. The harness was
rebuilding a large table for every query; fixing it made the same computation 19 times faster with identical results.
Since then every harness is checked for that pattern before it runs.

**The watcher that stopped.** A 72-hour live test of the classifier was meant to run unattended. A review found that
the server and its watcher had silently stopped hours earlier. The clock was restarted rather than the gap papered
over, and a supervisor was added (essay 07).

## More of the record

**Where the rules came from.** The pre-registration habit has a history. On 28 September a working shift reasoned
about the fleet's own laws from memory instead of reading them, and the fleet added a hard gate: no movement until the
grounding documents are read and recorded. Pre-registering experiments is that gate applied to research.

**A tie that hid a bias.** The ring classifiers broke ties at the k-th place by index. Heads with exact duplicate
marks were quietly biased toward whichever duplicate came first. Including every tied mark in the vote raised two
heads' accuracy from 0.745 to 0.806 and from 0.595 to 0.668 — the best results of the series came from fixing a rule,
not adding a model.

**A design flaw admitted.** The first paraboloid-versus-torus test on the governor's data split time so that new
workloads only appeared in the test period; neither geometry could be judged. It was reported as a flaw in our design.

**A run killed by the machine.** The lattice experiment ran out of memory on its first run. The partial results were
kept and labelled; the rerun used single precision and chunks, and its estimator's ceiling was reported as a caveat
on the headline (E8's lead is overstated).

**Searching before claiming.** Twice a "new" idea had close published relatives (torus knowledge-graph embeddings;
ternary embedding models). Both are cited in the disclosure and thanked by name; the claim was narrowed to what
differs.

**The outcome.** Of the experiments run over the two days, roughly half passed their bars. The ones that failed
shaped the design as much as the passes: tables for truth, rings for meaning, triangles for verification and
structure, the GPU only beside a busy processor.

## Why it matters for an open project

A disclosure published as prior art is only useful if a reader can trust which parts were measured. Publishing the
kills alongside the passes is what makes the passes believable — and it tells the next person which roads are
already walked.

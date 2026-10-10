# Toroids all the way up: the arc reactor, the cyclone array, and two rings that count

| | |
|---|---|
| **Date** | 2026-10-09 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Written with AI assistance (Claude) from the author's conversations of 4–9 October 2026 (unpublished). The author reviews it before publication. |
| **Type** | essay — every number is cited to docs 28–31 or `P7 §2`; anything not measured is marked **Speculative** |

## In one paragraph

The rings in this project began as a memory (essay 01): a resonator in the middle, rings of different sizes turning around it. During the
first week of October the author kept pushing the same picture outward — a ring system with a core at its centre, ring systems around that
system, an "arc reactor" built from them — until on 8 October it became a building plan for training many models at once: a hub of fifty rings
at the centre of every unit, eight models around it, five units touching on an outer ring, three floors, all of it on one graphics card. Most of
that plan now exists in pieces that are exact. The pieces have not yet run together. And one idea from the last day — that two fifty-ring
systems counting traffic could find the array's bottlenecks without any search — worked the first time it was measured.

## The words you need

- **Ring, ring system, T-number** — a ring is one modulus (a counter that wraps). A ring system is a set of rings whose sizes share no factor;
  together they name every number up to the product of their sizes (the Chinese Remainder Theorem, essay 01). **T25** is the system of the 25
  odd primes 3 to 101; **T50** adds the next 25, up to 233.
- **Core** — in the author's vocabulary, the processor at the centre of a ring system: a JIT-rendered program that fires while it is active.
- **Toroid** — the shape, a torus. Each hub's inner core is a toroid; the rings around it are toroids too.
- **Arc reactor** — the author's name for the three-tier ring system with cores at different dimensionality, named after the fictional and
  real reactors whose fields circulate in opposite directions.
- **Cyclone** — the same thing seen from the training side: the hub that the harnesses and models feed.
- **Harness** — one training process with its model. **Unit** — a hub with eight harness-model pairs. **Floor** — five units, one in the centre
  and four around it.
- **Resident** — living in the graphics card's memory, so the host only feeds batches and reads results.

## The idea, in the author's words and ours

The picture grew in stages. On 4 October: *"The model is sending all its outputs to the center ring, the center's middle 10 ring system, the 10t
system processes it with its core as it can and sends it down to the 5 ring system, where it gets further processed by the 3d core. The output is
then fed to the harness 5t where it processes it sorts it and routs all output back into the center for the same process in reverse to the
model."* On 6 October, asked whether a larger system could be drawn: *"Have you tried rendering the 15t? Let's try that first. I've a feeling it's
toroids all the way up."* And what the larger one might be: *"core is the inner processor at the center, the 3d code core, the holographic code
core … The "arc reactor" awas the 15t. I've no idea what the 25t is. A universe, or a reverse black hole. One in the same."*

On 7 October the author asked for motion that is real, not drawn: *"I want each tier in the t25 to alternate direction … is there a way to
mathematically express each system's rings cycling/turning like in my jumprope vision? not just visually express, actually mathematically set it
to do this so that this is how our system runs?"* And: *"the speed should be accurate to the moduli ring system, if it;s 3,5,7,13 it should move in
step, each system has it's own rythm but moves every tick"*; *"the core is what spins left or right, causing resonance and amplification, like my
arc reactor vision."* The arc reactor would sit at the centre *"with the 10 other systems around it. the precompute will happen on the outer edges
of the t25, at nanosecond speed."* And a wild one, offered as such: *"can we have a 35-50t as the memory buss with a 50t as the core for an
experiment? would that even be possible? throwing wild ideas out."*

On 8 October the picture became an array. *"Were making a training array, each unit will have a 50t center, with 8 harnesses around it a model
tied to each. they will be connected and feeding data into they cyclone, the arc reactor evolution. that is one unit. around the one unit, there
will be 5 of those systems spread out around it, touching on the outer ring. they will all be connected by the ring and increasing
resonance/compounding."* Then: *"1 in the center 4 around for a total of 5"*; on the GPU *"3 floors with the 5 unit layout"*; and the deployment:
*"lowest is 1 cyclone with model and harness, then it scales up to 4 at 16 then to 8 on the 32 cpu server which makes 1 unit … once we get to gpu,
it adds more units, a total of 5. with enough capacity, it adds a layer above … and then it adds a layer bellow … we will make an exe/deployable
that allows you to pick your settings and deploys."* How a step travels: *"any time a process/step fires, it can find it's way to where it needs
by jumping from toroid to toroid, each ring interconnects with every other toroid."* And how to begin: *"start on a 24gb to get the layout and
wiring right, then keep scaling up marking and recording results."*

## How we got here

**The hub first.** Fifty primes all below 256 means each ring fits in one byte, and the whole T50 fits one 512-bit register. An event — its
position, token, plate, level and row — becomes one residue on each ring; a **twist** against a predicted event is zero on every ring when the
prediction holds and non-zero on exactly the rings that differ; one tick moves every ring one notch at its own rhythm, which is the author's
"each system has it's own rythm but moves every tick" in arithmetic. The core is rendered as machine code; its vector encoding uses a published
direct-remainder method (Lemire, Kaser and Kurz, 2019), checked for every value below 2^24 and every modulus (doc 30).

**Wiring, rung by rung, as the author ordered.** A resident session records the whole step once and re-submits it: byte-exact over 2,000 chained
passes and 13 times cheaper per pass than setting each one up. The rungs climbed exactly as drawn — one cyclone with one pair, four pairs, a full
unit, a floor — and every stream was exact against the CPU. One floor of forty models' training state sat in 21.8 GB on the 24 GB card. Routing,
toroid to toroid by address, moved every item along one ring per hop and counted traffic as it went. Three floors failed: at full size the weight
check found 830 million mismatched words on that card, and the cause is still unexplained (doc 30).

**Training, separately.** The author's push was direct: *"approved continue, run a training run on the cloud gpu when done to get an etimate of
speed and throughput with our 5x8harnes layout."* Eight models in one recorded step were each bit-identical to their own solo run, about 19 times
faster per model than the CPU engine. Offered three ways to hold the models — each harness its own full model, a pull toward a shared mean, or
the cyclone holding the shared model with each harness keeping only its difference — the author chose the third: *"3 sounds about right. thank
you."* With attention computed as batched matrix products, a unit of eight ran 30.6 times faster than eight CPU engines and stayed within
0.051 % of them (doc 28).

**The limit the hardware drew.** Forty models in one session trained nothing — the loss stayed near 9 while the CPU engines reached 3 — and gave
no error. A guard now refuses that build outright: three buffers of 2.5 GiB each cross a 2^31-byte storage limit. A group of twenty builds and
trains, 21.6 times faster than twenty CPU engines, but its per-harness gap to the CPU averaged 4.1 % against a registered 2 %, worse on 16 of 20
harnesses. The failure stays as registered; a fairer gate, measured against the CPU engine's own noise, is written down for the next run (doc 29).

## Two rings that count

On 9 October the author brought a document about the JIT T50 and pointed at the question that had been open all week — how an array this size
knows where it is congested: *"the previous dual 50t as the resolution to the On\* equation"*, and the statement behind it: *"interlocking two 50t
omniring systems would solve this computation in much less time by relying on the massive rapidly moving and counting outer rings."*

The field's answer to "where are the bottlenecks between every pair of nodes" is a Gomory–Hu tree: n − 1 maximum-flow computations, every step.
The author's answer is that the counters already exist. The routing pass, while it moves items, fills one table addressed by source and one
addressed by destination — two interlocked sets of outer rings, turning one notch per item. Because the array is a product of rings, the minimum
cut between any two toroids is either the cut around one of them or a cut that splits one ring's residues; both are read straight from the tables,
in a handful of lookups per pair (doc 31):

| layout | ring read | exact reference |
|---|---|---|
| 15 toroids (recorded G120 traffic) | global minimum 27,287 at one toroid; 105 / 105 pairs equal | Gomory–Hu, 4.3 ms against 0.27 ms |
| 105 toroids (rings 3·5·7) | 5,460 / 5,460 pairs equal, 8.1 ms | 151 ms |
| 1,155 toroids (3·5·7·11) | 60 / 60 sampled pairs equal to max-flow; global minimum equal to Stoer–Wagner; 1.51 s | about 101 s estimated |

It has a blind spot, and we found it on purpose: a **hot cluster** — a box of toroids all saturated toward the rest — is not a cut the ring family
can see; exact on 85 of 100 such fields until box cuts were added (100 of 100). On the GPU the routing pass fills the tables with its own atomic
counters and a cut kernel writes every pair's cut each step, with 0 mismatches. The same counters size each toroid's **mailbox**, so the card
launches work where the load is: 3,848 workgroups by load instead of 6,465 for a fixed worst case (doc 31).

## Where it did not hold

- **The whole design has never run at once.** The hub, forty training models, the ring between units and full residency are exact in separate
  programs: wiring without training, training without the routing (doc 30).
- **"Compounding"** across the ring — the author's resonance between units — was not measured.
- **The growth runs on the A40** (two sessions of twenty) finished no day and no round; the last launch was stopped in its start phase. There is
  no growth-rate number for any GPU tier yet (doc 29).
- **Three floors failed** their weight check; the deployable that picks a layout by capacity is designed, not built.

## What this essay does not claim

That the T50 precomputes the model's work "at nanosecond speed" on its outer rings (**Speculative**: the measured per-event cost of the rendered
hub is about 15 ns on one server core, partial evidence); that a 35–50T memory bus around a 50T core has been tried (not yet); that the array
learns faster than the CPU school per unit of compute (the comparison the pre-registration ends with has not run).

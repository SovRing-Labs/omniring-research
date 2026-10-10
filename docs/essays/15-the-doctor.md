# The doctor: a core that repairs our own code, and a clean room made of doctors

| | |
|---|---|
| **Date** | 2026-10-09 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Written with AI assistance (Claude) from the author's conversations of 6–9 October 2026 (unpublished). The author reviews it before publication. |
| **Type** | essay — every number is cited to docs 34–37 or `P7 §4`; anything not measured is marked **Speculative** |

## In one paragraph

Part 6 described a repair core for the layout engine: a program, not a model, that takes layout problems one at a time and tries combination
after combination until they are fixed. This week it got a name and a job description — the doctor, a core that learns and repairs our own
applications — and four new senses. It learned to read code as equations, to ask Chrome questions without reading Chrome, to see every box on a
page as one point on twenty-five rings, and to fix a page until its geometry is exact rather than merely Chrome-like. Then the author asked
whether a clean room could be built entirely out of doctors, with no large model anywhere in it. It can, within limits we measured, and one head
of it ran in 95 MiB.

## The words you need

- **The doctor** — a core inside the renderer that finds, diagnoses and fixes defects in our own code, keeping a knowledge base of what worked.
- **Agreement** — a box agrees with Chrome when its x, y, width and height are each within max(2 px, 5 %) of Chrome's; 49 frozen pages give
  28,010 comparable boxes.
- **Origin box** — a failing box whose parent agrees; the place an error starts.
- **Gate** — the test every fix must pass: no box that agreed may stop agreeing, on the training pages or on the held-out pages.
- **Oracle** — the reference whose answers we trust. Chrome is an oracle observed as a black box: we keep its output, never read its code.
- **Equation (of a function)** — what a function computes, written without names: inputs become numbered slots, so `width - padding` is
  `?0 − ?1`.
- **Anti-unification** — finding the most specific equation with holes that two equations both fit.
- **Pristine** — a box whose relations to its frame and siblings are exact to 1/64 px.
- **Clean room (two-team)** — readers see a source and write a specification of what it does; a gate passes only function; an implementer
  builds from the specification and never sees the source.

## The idea, in the author's words and ours

The vision, on 6 October: *"vision for the doctor core: able to learn and fix any system app the user needs, by similar method finding other
places in the code that have similar layout, applying previously known good combinations, using logic, reasoning, and system to test and learn.
it will be essentially our doctor role, but in a 50mb core that learns the users apps and builds it's own knowledge base. I think a reverse version
of our IFS resonator mechanics would help it identify other parts in the codebook that have similar layout."* Where to start: *"well have it work
on our in house apps, learn one at a time. have it do the launcher next. but this is the vision. for now work on the renderer with this end goal in
mind."*

The same day, two turns that shaped everything after. Toward equations: *"can we use symbols and equations instead of variables paramters/etc? may
work better for our trained models anyway."* And toward a clean room: *"let's first find published standards/specsheets that we can have an agent
build a quick codebase from for our most used/needed items. then we'll set up a cleanroom pipeline for when the doctor runs into a problem it can't
solve"* — with the hope that it could be shared: *"Once we've built a clean room library, can we also share it for free to our community?"*

## How we got here

**From blind tests to a method (6 October).** The session opened with a complaint about the last one: *"last session took 6 housrs getting uner 1k
boxes. we cannot keep doing blind test after test after test. you must synthesize and find a new method. we have all the knowledge we need in our
system."* Our first attempt was to model error propagation as linear algebra over the box network. The author rejected it: the job is to measure
the angles of each box against the shape it should have — *"its as … simple as putting the square in the square hole. if the square hole turns
into a circle, its … wrong."* And then the order, in six steps: *"1. patient census. 2. measure angle. 3. add alasing/feathering. 3. compare to
oracle. 4. apply fix. 5. reverse IFS the original faulty shape and replace with correct shape."* With a reason beyond bug fixing: *"if we structure
our code to be geometric and exact regardless of formatting or text, we would optimze to another level."*

The census showed why the old method stalled. Of 10,619 failing boxes only 560 were origins; one news page had 3,102 failing boxes and **no
origin at all**, because heights flow upward — a child too tall makes every ancestor wrong. The shape station measured each box's angles in its
frame, ours against Chrome's; its first catch was a grid item off by −37°, which led to a rule we did not implement — CSS Grid's implicit named
areas — and **1,609 boxes agreed at once, none lost** (doc 35).

**Code as an alphabet.** The doctor lowers a Rust function to an equation with numbered slots and opaque nodes for what it cannot read; 70 of the
126 layout functions lower cleanly. An e-graph merges equal forms; anti-unification finds shared shapes. The space-sharing code of tables and the
grow-to-limit code of grids, written weeks apart, turn out to be one equation with holes: `?0 + (?1 − ?0)·?2 / ?3`. Across the author's whole Rust
workspace the same search found a calendar function written three times and a random-number mixer written six times. Asked for a function by
examples only — the author's *"if it needs a specific function or need, it can search by functions and build what it needs"* — the doctor found or
built all 24 test needs, and rejected its own first `ceil_div` when held-out rows showed it was an overfit (doc 34).

**Chrome as a witness, not a source.** Feed Chrome a family of probe pages, keep only its boxes and computed styles, turn every number into a
symbol, sweep it, and let the doctor synthesise the law, checked by the compiler on every answer. Then run the same probes through our engine and
synthesise our law. Where they differ, the defect is named: our legend element was a constant where Chrome's grows with its padding (doc 35).

**The gate series.** Each fix became a specification feature behind a switch, merged only with zero boxes lost: grid named areas, `unset` for
non-inherited properties (+1,284), `:has()` with container-query units (+673), the image chain (+328), grid `order` (+311) and fifteen more.
Agreement climbed from 19,008 to **24,004 of 28,010 boxes (85.7 %)**, never losing one. Some fixes only pass together, because their errors
compensate; the gate is applied to the set (doc 35).

**Boxes as points on rings.** The author asked on 6 October whether the doctor could work on the larger ring systems, and on 7 October where it
should live: *"it will run the first time a page is loaded into the browser and will be dormant unless an error arrises or it notices problems.
hence doctor."* A box is five numbers — its corner, width, height, and its offset inside its frame — held as residues on the 25 primes of T25: one
register. Its twist against the target decodes exactly by the Chinese Remainder Theorem and says whether the box is wrong in shape, wrong in its
own place, or only carried by its parent; keyed that way, 473 failing roots collapse into 103 families. The kernel is generated machine code and
fires after every layout pass for **0.90 % of the layout time** (doc 36).

**Exact, not merely Chrome-like.** The author moved the goal: *"chrome drift is irrelevant once our geometry is set isnt it? chrome is just a
reference for how our structure should look, our actual geometry is our own. is there a way to get the number to 100% pristine geometr[y]"* — and
the job: *"we are building this so that it can do it on its own, you are not doing the work for it you are designing the system and procedures it
will use to do this for any new website added that needs it."* Six exact relations define a defect (a box leaving its frame, edges a sub-pixel
from flush or aligned, near-equal widths, uneven gaps). The first map found 567 defect boxes in 28,058 (97.98 % pristine). The fix loop takes the
cheapest candidate first — a known fix, a formatting knob, a rounding fix, a per-site CSS sheet — and accepts it only if the box becomes exact and
no other box loses exactness. Unattended, it fixed 331 of 565 defects. Then we found our own mistake: the judge never compared siblings with each
other, and the fixes had pushed boxes onto their neighbours — overlaps rose from 242 to 340 while the report said 99.48 %. The judge now counts
overlaps and rejects any fix that raises them; the first knowledge base was archived (doc 36). The author's next instruction — *"add youtube,
spotify, facebook, and the top 100 most used/popular sites to the corpus. have the doctor clean them up"* — found 1,464 defect boxes on 68 of 100
sites before the loop ran.

## A clean room made of doctors

On 7 October the author asked the question that turned the doctor into a method: *"so we can't have a group of "doctors"/coder look at a codebase,
output the equations/symbols for the funcitons, and give those to the implementor doctor? with chrome it was looking at the blackbox with the same
process, is that not still applicable? it's not copying code"* — and then the whole picture: *"so essentially we can have an entire cleanroom setup
fully made up of "doctor cores" where a system scrapes or downloads specs or code, indexes them, 1-3 doctors interpret into equations, another 2-3
doctors builds them into our own database, and another 1-3 doctors are just building whatever app is on the que, with no giant llm overhead, pure
determenistic logic and reason under 100mb per head??"* And the reaction: *"this is insanity, isnt this what huge corporations are paying thousands
for??"*

What was built (doc 37). **Readers** write, for each function, a specification with no names in it: typed arguments, the equation, examples,
held-out and validation rows, and the source's hash and licence. A **gate** passes only function — a strict schema, exactly one well-formed
equation, and a scan that refuses any string that matches the source's identifiers, comment words or literals. One **implementer** sees only the
specification and our own library (built without the source file) and never the source.

- On our own layout file: 32 specifications; **256 of 256 planted leaks refused**.
- With an examples-only check, 27 of 32 functions were rebuilt — **and 7 of the 27 were wrong**, overfits that happened to satisfy the examples
  (`not a0` rebuilt as `a0 % 15 == 0`). Running each specification's own equation as an oracle on 10,000 inputs removed every one; 27 of 32 are
  rebuilt from the specification alone and correct.
- A foreign crate (MIT or Apache-2.0): 7 of 9 rebuilt with our library only, two of them checked against the real crate on a million pairs with
  no mismatch — but specifications for only 64 % of its functions, against a bar of 80 %.
- Six operations of our own C++ training engine, read through a probe driver: the equation matches the engine on 128 of 128 rows each.
- One head synthesising a function peaked at **95 MiB** resident — inside the author's *"under 100mb per head"*.

The author also asked the clean room to serve the GPU work: *"would we download a cuda kernel for the clean room or have our scraper tools find
code and specs?"* The answer became a ledger: every step of the GPU kernel work records the sources consulted or cited, with licence and hash,
chained so a changed step is detected — 23 entries, the chain intact (doc 41).

## Where it did not hold

- Three ways of pointing at the faulty code failed their bars: predicting a box from its good neighbours (3 of 368), ranking code branches
  (0 of 5), ranking statements (1 of 4) (doc 35).
- The reader found **zero functions** in our C++ engine source; it reads Rust and JavaScript only. From behaviour alone the builder rebuilt one
  function of nine (doc 37).
- Pristine fixes move boxes away from Chrome where Chrome draws the same defect (24,032 → 23,225 agreeing, logged) (doc 36).
- Repairing our JavaScript runtime with the doctor's method was attempted and **not achieved**.

## What this essay does not claim

That the doctor repairs any application but the renderer yet — the launcher is next; that rebuilt code is textually unlike its source — the
clone check has never been run; that a fleet of doctor cores runs as the author pictured it (**Speculative**: one head and one pipeline are
measured, not the fleet).

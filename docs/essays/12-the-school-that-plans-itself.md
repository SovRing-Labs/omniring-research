# The school that plans itself: a body to learn, a loop, a collapse, a circle, and a gate at one hundred

| | |
|---|---|
| **Date** | 2026-10-09 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Written with AI assistance (Claude) from the author's conversations of 3–9 October 2026 (unpublished). The author reviews it before publication. |
| **Type** | essay — every number is cited to docs 24–29 or the omni-ring Technical Disclosure Part 7 (`P7 §n`); anything not measured is marked **Speculative** |

## In one paragraph

In the first week of October the small model with the rings inside it went to school, and the author did not like the school. It was a
fixed ladder — pre-K, kindergarten, elementary, middle — that pushed the model upward whether it had learned or not. Over six days the
school was rebuilt around one idea the author kept returning to: the model should learn the next thing only when it has the last one, and
it should keep the old things while it learns the new. The result is a loop that plans every round itself, a guard that will not let a round
through if the model forgot what it knew, a circular build that keeps every earlier layer in the same core, and a growth controller that
passes a stage only at one hundred percent. On the way the model collapsed once, and the collapse gave the week its most important rule.

## The words you need

- **The model** — the SuperSeed trial model: a small transformer whose weights are ternary (−1, 0, +1), about 6.9 million of them, with the
  T25 core inside it. It is trained by our own CPU engine.
- **The body** — what the author calls the model's own faculties: the generators it can call, the rings it can read, the "pocket" (a 4-slot
  holding buffer), the arc reactor it is docked to. Tier 1 teaches the model to use its body.
- **Generator** — one of 26 deterministic problem makers. Each makes a problem, solves it step by step, and checks the answer with an
  independent method. Every training row comes from them, so every answer is verifiable.
- **Skill** — a lesson at a level, written `lesson@level`; `pk.echo@1` is the first pre-K lesson at level 1.
- **At the gate** — a skill whose held-out accuracy is at least 0.85 (in the growth controller: 1.0). Held-out means problems the model never
  trained on.
- **Harness** — one training process. Several harnesses can train one core and merge their weights at the end of each day.
- **Round** — one cycle of plan, compile, train for ten days, evaluate.
- **Wall** — the author's word for the point where more rounds stop raising the model: here, three rounds with no skill gained.
- **Keep** — a saved copy of the model: a **rolling keep** holds the last five rounds; a **permanent keep** is checksummed and never deleted.

## The idea, in the author's words and ours

The thread began on 3 October, when the author asked how the model should be taught at all: *"Yes, train on structure instead of filler,
concise then pretty and loaded. How can we create our own training curriculum that our forward pass trains on? Not having control of the
curriculums is like giving the keys to your car to a drunk."* The first rule followed a day later: *"I think the model should go 1 layer higher
than it was able to solve, as it would show a higher layer of reasoning it can learn from studying. so it gets 1 block forward and a few
blocks back."*

Then the author saw what the ladder was doing: *"We are currently sending the model to middle school witout completing elementary. It may
need a super simple symbol based tier 1 that allows it to get awuai ted with its own system and faculties before moving on to my
curriculum."* And on 5 October, the shape it should take: *"let's do a for prek b for k and grow it throughout in the same spiral circular
curriculum method … ensure all your work is able to compound and resonate with every school epoch."*

The author was also clear about what is being graded. Not answers: *"were not grading it on answering were grading it on how well it's
adjusting to it's body. completely different results at every level. a memorization machine would deffinetly get more answers correct, but it
would never be able to reason."*

Our translation of all of this is a loop. A graph of 392 skills with their prerequisites. Each round, a planner picks the **frontier** — skills
whose prerequisites are learned but which are not learned themselves — weights each by how fast it is improving, adds 20 % review of what is
already known and a one-level preview of what comes next, compiles a fresh build for exactly that, and lets the harnesses train one core for
ten days. A per-skill evaluation scores the result. The loop stops at a wall, or when nothing buildable is left (doc 24).

## How we got here

**The loop worked from the first round.** Compiling on the rented 32-core server in memory took two seconds for ten builds, where the laptop
had taken minutes between days. Over twelve rounds the model's tier-1 skills at the gate rose from 28 to 72, with small dips in rounds 2, 6
and 11, and the planner, given the saved files, replays every round's numbers exactly (doc 24). Two practical failures shaped the runner on
the way: the first multi-round launch sat idle for sixteen minutes because an ssh session hung after the server had finished — so every
harness now prints a heartbeat and the server kills a stalled one — and one harness once trained an eleventh day alone while the other seven
waited; every harness is now capped at the round's days.

**Then round 9 went to middle school.** The author was careful: *"once 12 is done goahead and run 1-2 middle school runs(ensuring a backup is
secure) we'll see what results come of it."* What ran was not what was meant. Three of the eight harnesses trained middle-school builds and
five trained tier-1, and at the end of every day all eight were averaged into one model. The model's tier-1 skills at the gate fell from 55
to **6**. Its held-out loss went from 0.717 to 2.595. The transport lesson, which it had held at 0.92, fell to 0.29. And the number we had been
watching — skills mastered — went *up*, from 93 to 123, because mastery was sticky and thirty middle-school skills had just been counted (doc 25).

The author saw it before the numbers were in: *"are we not doing the circular curriculum??"* — and then: *"i'm pretty sure ou ruined the training
by letting it run without the circular curriculum. ensure we still have the last elemetry run backup."* Both were right. The middle-school
builds carried no review of tier 1, so the merge pulled the model away from everything it knew. Elementary was not even finished: the model
later held 13 of its 20 elementary skills at the gate and none at 100 %.

**The rule we wrote down:** *judge a round by what the model knows now, not by what it once knew.* A guard now runs after every round and
compares only the skills both rounds scored — so a changed test set cannot fake a pass — and fails the round if skills at the gate drop by more
than 10 % or held-out loss rises by more than 30 %. Run back over the saved rounds it flags round 9 and raised no false alarm on rounds 2 to 8.
On a failure the round is set aside and redone with more review, and after two failed redos the loop stops for the author. The author's own
instruction became the backup rule: *"can we make backups of the core after every run, fall back and redo curriculum anytie it fails"* and
*"we keep the last 5 cores on disk."* Restarted from round 8 with middle school locked, the school passed four rounds in a row, ending at 72
tier-1 skills at the gate (doc 25).

**The circle.** The next design spliced review, the current school and a preview of the next school into one build, so one harness walks all
three in order. The splicer refuses builds that do not share the same token ids, generators and procedure plate, and pads every phase so no
training row can run off its end — a crash on exactly that edge stopped one launch at step 60 before the pad existed (doc 26). Two designs ran
in sequence:

| design | tier-1 skills at the gate | middle skills at the gate (of 46) |
|---|---|---|
| middle on its own core (rounds 13 / 14) | **3 / 2** on the middle core | 32 / 37 |
| circular, one core (rounds 15 / 16) | **91 / 103** | 27 / 36 |
| elementary only (round 12, for reference) | 72 | — |

Middle school trained alone wiped tier 1. Spliced into one circular build, the same core held more tier-1 skills than ever and learned most
of middle school beside them (doc 26). It is not a controlled pair — the rounds and lesson mixes differ — but it is the direction the field
predicts for rehearsal, and the one the author asked for.

## A gate at one hundred

On 8 October the author set the rule for growth: *"growth rate: how much each run progresses the model at every tier. have it set so that it
autocreates it's curriculums, only passes staage when it masters every skill in that tier to 100, once it finishes middle school, it can start
growing it's own parameters. have it auto save checkpoints to backup every so often, it will grow extremely quickly during these runs. we need
to set this structure so it can evovlve itself as it needs. it may be off intuitive but it will show something important."* And a moment later:
*"once it's ready it switches to growing parameters, then back to growing skills, eventually growing new generators. I think this model will go
very far tonight."*

What was built (doc 27):

- **A stage passes only when every skill in it is at 100 %** on its current score, on at least 300 independent held-out rows. Three hundred is
  not a round number: if a skill makes zero errors on n independent rows, its true error is below ε with confidence 1 − δ once n ≥ ln(1/δ)/ε;
  at ε = 1 % and δ = 5 % that is 300. Rows, not tokens, because the tokens of one row are not independent.
- **A skill that slips goes back to the frontier.** The next stage's first level is previewed at 10 %.
- **Skills that unlock many others weigh more** — `pk.echo@1` unlocks all 84 other pre-K skills.
- **Modes:** skills until middle school passes; then, at a wall, grow the parameters; after a growth, back to skills; a second wall soon after,
  grow the generators.
- **Permanent keeps** every five rounds, at every stage pass and after every growth, each with a checksum manifest.
- **A growth ledger**: one row per round with the hashes of the checkpoint, the evaluation, the plan and the update, the gate evidence and the
  decision, each row chained to the one before it so a changed row is detected.

Against that gate the frozen elementary model holds 10 of 85 pre-K skills, 4 of 61 kindergarten skills and none of the 20 elementary ones — the
gate is exactly as hard as the author meant. The controller passed all 14 of its checks on synthetic rounds, and one small wiring round on a
rented 48 GB GPU produced every field, a keep and a ledger that verifies (doc 27).

## The school on the GPU

The author wanted the runs on a graphics card from the start of the growth work: *"the runs will happen on gpu from our current choice and up."*
The training step, with every school switch, became 100 GPU passes written from our own engine's equations, and the unchanged training program
runs on them. One school day on the laptop's own GPU matched the CPU day in corrections (34 / 34), generator rows (14 / 14) and answered rate
(0.479 / 0.479). Eight school-size models in one step on a rented A40 were each bit-identical to their own solo run and about 19 times faster
per model than the CPU engine (doc 28).

Then the honest part. With every school switch on, the GPU's held-out loss for some harnesses drifted up to 5.99 % from the CPU's, against a
registered bar of 2 %. A group of twenty trained 21.6 times faster than twenty CPU engines but its per-harness gap averaged 4.1 %, with the GPU
worse on 16 of 20. Forty models in one session cannot be built at all — an explicit guard refuses three 2.5 GiB buffers that cross a 2^31-byte
limit. The author kept the failure as registered and wrote a fairer gate for the next run, measured against the CPU engine's own noise, before
that run starts (doc 29).

## Where it did not hold

- **No growth round on real data has completed.** The 40-harness launches finished no day; the one completed round is a one-harness wiring
  test. There is no growth-rate number yet for any GPU tier (docs 27, 29).
- **No wall was reached** in sixteen rounds; the high-school rungs beyond the 26 generators have no generator yet (doc 24).
- **A stall predictor failed:** its per-skill score was below chance (AUC 0.35–0.45); only the plain gap to the gate carried signal (doc 24).
- **An older result we keep in view:** in a controlled run of 3 October, plain question-and-answer rows beat full reasoning traces on held-out
  answers, 21.2 % against 13.7 %. The current ten-beat format has not been compared head to head on this school (doc 24).

## What this essay does not claim

That the model *"would do middle school well up to half of highschool before capping out"* — the author's expectation, still **Speculative**:
no wall has been reached and no growth round has run. That circular builds beat split ones in general. That the model reasons — the reasoning
rows (closed-loop answered rate 0.63–0.64 on fresh problems) are measured; what they mean is the author's question, and the next rounds'.

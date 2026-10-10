# The live school: one round loop over a skill graph (LIVE-SCHOOL rounds 1–16)

| | |
|---|---|
| **Date** | 2026-10-08 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). The author reviews each document before publication. |
| **Type** | measured result (curriculum loop on a rented 32-vCPU server) |
| **Verdict** | PASS in trend (tier-1 skills at the gate 28 → 72 by round 12); no wall reached in 16 rounds |
| **Code** | `harness/part7/ch1-live-school/` (`school_graph.py`, `skill_eval.py`, `school-live.sh`, `school-round.sh`, `school-compile.sh`, `par_merge.py`) |

The model is the SuperSeed trial model: a ternary-weight transformer of 6,926,912 weights (D 256, 6 blocks, 4 heads, vocabulary 8,192,
context 512) with the T25 core inside it, trained by our own CPU engine. Until 10-07 it went through fixed school passes (pre-K,
kindergarten, elementary, middle). The author's worry, two days earlier: *"We are currently sending the model to middle school witout
completing elementary."* This document replaces the fixed passes with one loop that only moves on when a skill is learned.

*The record below is the full measured account from the technical disclosure's working chapters: every gate, every failure, with the
harness and result paths in this repository. "Section n" and "§n" inside it refer to the sections of that chapter; the matching documents here
are listed in the README. "Recorded; no saved result" marks a figure the project recorded whose output file is not published.*

## The live school: a round loop over a skill graph (harness `harness/part7/ch1-live-school/{school_graph.py, skill_eval.py, school-live.sh, school-round.sh, school-compile.sh}`)

Description. The fixed school passes (pre-K, kindergarten, elementary, middle) were replaced by one loop. A **round** is: (1) the planner
reads the skill graph and the per-skill scores; (2) a fresh build is compiled for exactly the frontier skills plus spaced review, with a new
row seed (no fixed 5x or 25x build); (3) N harnesses train ONE core for ROUND_DAYS = 10 days each, merging their weights at every day end;
(4) a per-skill held-out evaluation scores the merged core; (5) the gates update and the next round is planned. The loop stops at a WALL
(mastered count flat for 3 rounds with no skill gaining more than 0.01) or when nothing buildable is left.

- **Skill graph (R1).** A node is `lesson@level`. Edges are prerequisites seeded from the lesson design and school order; a node's first
  level requires the first level of each prerequisite lesson, every higher level requires the level below. Groups: pre-K (17 lessons x 5
  levels), kindergarten (7 lessons x 5 + 26 per-generator units `env.<g>` x 1), elementary (4 x 5), bridge (5 x 3), middle (one lesson per
  generator, 26 x 5, prerequisites = the 5 bridge lessons + that generator's unit), high school (rung B = the 26 generators at levels 6-8
  where the generator can produce them, plus rungs A, C, D, E, F, G, H, I, J as nodes marked UNBUILT: skipped, never faked).
- **Gate (R3).** A skill is mastered when its held-out top-1 on the LEARNABLE positions is >= 0.85. Learnable = every tier-1 symbol except the
  prompt stages and except the first occurrence of random goal operands (mask, R4); for middle school, the answer span. Mastery is sticky in
  the planner state.
- **Sampler.** Frontier = unlocked and not mastered. Weight of a frontier skill = max(0.25, 10 x |last score - previous score|), 1.0 before it
  has two scores (learning-progress sampling). Review: mastered skills share a fraction r = 0.2 of the total weight, i.e. each gets
  r/(1-r) x (frontier weight total) / (number mastered). Passes are one per level; a pass under 8 % share merges into its neighbour (a merge
  never puts a generator at a level it cannot produce). The held-out of a round carries level+1 of each frontier lesson (out-of-distribution
  in operation count, R5).
- **Lessons added for the loop.** R4 selective loss: the compiler writes a per-token mask file; the runtime sets the target to "ignore" there.
  R6 bridge school: the same episode as symbol program and as constrained English from our own child-level templates. R7 mistake rows: a
  wrong draft, the check shows it, `[revise]`, the fix. R8 frame variants: operand relabelling by a ring rotation carried through goal,
  program and state (the tier-1 compiler module `tier1_school.py`: `_draft_fix`, `BRIDGE`, mask writer; source not shipped in this tree).
- **Per-skill evaluation (`harness/part7/ch1-live-school/skill_eval.py`).** Forward each held-out row through the checkpoint, count top-1 hits per `lesson@level` on the
  learnable positions; skills with fewer than 24 scored positions are dropped. A parallel wrapper script (not shipped) splits the held-out phases over processes
  (4 threads each) and merges by summing hits and counts.
- **Compile (R2) on the server, in RAM.** Per harness i of round r, seed s = 1000 r + 10 i: tier-1 build (4e5 tokens x 0.9), middle build
  (4e5 x 0.7), review build (seed s+1), preview build (seed s+2); shared held-out (seed 9000 + r) and doing bank (seed 7000 + r). All builds
  compile in parallel into `/dev/shm`, then one spliced build per harness (section 3).
- **Round (`harness/part7/ch1-live-school/school-round.sh`).** Harness i runs `thead-learn` (wake, doing, study, sleep with canary gate, retry per day) under the server's
  tritwatch with a stall kill and a 2-minute heartbeat line per harness; a straggler cut stops harnesses 180 s after the first one finishes.
  Day merge: `harness/part7/ch1-live-school/par_merge.py` waits for all N day-end weight files, averages them in float64, writes the float32 mean atomically, logs the
  RMS spread between harnesses. Switches set by the round: PLATES 31, ROUTER_SIMPLEX 1, ROUTER_CE 0.5, VOICE 1, HARM 1 (lambda 0.05, kappa
  0.9), POINTER 5, COPY 6, T25_CORE 1, PLATES_ATTN 1, P3 1, WAKE_STEPS 10, DO_N 32, DO_REVIEW 8, STUDY_STEPS 20.

Measured gates.
- G1: graph size = 392 nodes (pre-K 85, K 61, elementary 20, bridge 15, middle 130, high school 81), 786 prerequisite edges, 181 nodes built
  by the tier-1 compiler, 202 by the middle compiler, 9 unbuilt rungs; initial frontier = {`pk.echo@1`}; after it is mastered, 4 skills
  unlock (`pk.echo@2`, `pk.ping@1`, `pk.hold@1`, `pk.meet@1`); `pk.echo@1` is an ancestor of the other 84 pre-K skills and of 391 of 392
  nodes. (harness `harness/part7/ch1-live-school/school_graph.py show`; no stored result file, the output is deterministic; recomputed from the
  shipped copy, which is the stage-mode version of the file with the stage switch off)
- G2: rounds. The planner state replays exactly (recomputed): seeded with the placement record (`docs/appendix/part7/ch1-live-school/results/live-school/placement.json`: 181 skills scored,
  41 at or above 0.85, which is the "41" start value of the project's hand-off note, not shipped) and fed each round's stored `docs/appendix/part7/ch1-live-school/results/live-school/r<N>/skill.json` through the shipped
  `harness/part7/ch1-live-school/school_graph.py update`, it reproduces the recorded cumulative mastered count and gain of all 16 rounds; it reproduces the recorded frontier
  for rounds 1-7 and 9-12, and records a smaller one for rounds 8 and 13-16 (38, 28, 22, 22 against 54, 53, 49, 48) because the middle lock
  (`harness/part7/ch1-live-school/school_graph.py:113-121`, added after the round-9 collapse, and its explicit override in the runs that unlocked middle) was not in force when those
  rounds ran. Mastered is cumulative and sticky; round 9 as first run was rejected (section 4: sticky 123, tier-1 at the gate 6).

  | round | cumulative mastered | gained | tier-1 skills at the gate / scored | middle skills at the gate / scored | held-out loss (round log) | canary |
  |---|---|---|---|---|---|---|
  | r1 | 46 | +5 | 28 / 136 | - | 1.204 | 1.293 |
  | r2 | 52 | +6 | 27 / 116 | - | 0.770 | 1.302 |
  | r3 | 57 | +5 | 29 / 130 | - | (no line) | (no line) |
  | r4 | 66 | +9 | 35 / 132 | - | 0.796 | 0.568 |
  | r5 | 69 | +3 | 39 / 139 | - | 0.782 | 0.660 |
  | r6 | 76 | +7 | 38 / 144 | - | 0.773 | 0.425 |
  | r7 | 85 | +9 | 51 / 140 | - | 0.701 | 0.598 |
  | r8 | 93 | +8 | 55 / 148 | - | 0.717 | 0.474 |
  | r9 (restart from r8) | 98 | +5 | 58 / 146 | - | 0.609 | 0.442 |
  | r10 | 111 | +13 | 64 / 140 | - | 0.617 | 0.519 |
  | r11 | 117 | +6 | 60 / 141 | - | 0.592 | 0.461 |
  | r12 | 126 | +9 | 72 / 145 | - | 0.616 | 0.523 |
  | r13 (two cores) | 161 | +35 | 99 / 162 | 32 / 46 | 0.549 | 0.545 |
  | r14 (two cores) | 176 | +15 | 92 / 155 | 37 / 46 | 0.518 | 0.404 |
  | r15 (one spliced core) | 179 | +3 | 91 / 161 | 27 / 46 | 2.230 | 0.893 |
  | r16 (one spliced core) | 179 | +0 | 103 / 165 | 36 / 46 | 1.856 | 0.747 |

  Reading the table: ROUND_DAYS is 10 for every row. Cumulative mastered is NOT the number of skills currently at the gate (r16: tier-1 at the gate 103
  plus middle 36 = 139 on the same core against 179 mastered) because mastery is sticky. In r13 and r14 the tier-1 and middle columns come from two
  different cores (section 3) and the held-out is the first tier-1 harness's; in r15 and r16 the logged held-out is harness h0's, a middle-set
  held-out that is not comparable with the earlier rows (the tier-1-type harnesses of those rounds logged 0.537 and 0.561, section 3). The round log of r3
  has no held-out line. (`docs/appendix/part7/ch1-live-school/results/live-school/{rounds.jsonl, placement.json, r<N>/skill.json, r<N>/round.log}`;
  harness `harness/part7/ch1-live-school/{school-live.sh, school_graph.py, skill_eval.py}`.) Machine records of the launches (scrubbed summary,
  `docs/appendix/part7/ch1-live-school/results/launch-records-summary.json`): eight launches; three ended exit 0 (launch 5 2,057 s, launch 6 2,394 s, launch 8 920 s) and five did not (launch 1
  terminated after 1,716 s, launch 2 exit 1 after 7,238 s, launch 3 terminated after 51 s, launch 4 terminated after 793 s, launch 7 terminated after 1,297 s; the
  history also holds an earlier 140 s record of the first launch with exit 0; launch 6 was the middle-school launch, launches 7 and 8 the circular ones). How many rounds a launch completed is in the round logs, not in its exit code.
- G3: compile on the server in RAM: in the live launches 10 builds took 2 s (r9 restart: 10 builds, 41 MB in RAM; r10, r11, r12: 10 builds, 44 MB; the
  terminated first r10 launch: 9 builds, 20 MB, 2 s); later rounds: 6 builds in 9 s (r13, the split round), 18 builds + 8 circular splices in 6 s (r16)
  (`docs/appendix/part7/ch1-live-school/results/live-school/r<N>/compile.log`, N = 9 to 16, and the "pod compile" lines of three launch logs in `docs/appendix/part7/ch1-live-school/results/compile-lines-extract.txt`;
  harness `harness/part7/ch1-live-school/school-compile.sh`). The earlier
  statements - 10 builds in 6 s against 2-10 minutes of laptop gaps, 24 of 24 data files byte-identical to a laptop compile (only the manifest's relative
  spec path differs), plan to server 39 s - are recorded only in the project's test index (not shipped); the probe output was not saved (partial).
- G4: a hung-job guard: `tw run --stall 20s --on stall=kill -- sleep 600` stalls at 20 s and is killed (exit 143) (recorded only in the project's test index, not shipped; the output was not saved) (partial).
- G5: the verifier substrate. Rows come from the 26 deterministic reasoning generators (each: seeded problem maker, exact solver emitting typed trace
  steps, an INDEPENDENT verifier of a different method; a row exists only if both agree). Only two of the 26 can evolve their solver strategy
  (`sat.dpll`, `sat.trit`); the evolve gate keeps a strategy only if every frozen replay row still verifies with the same verdict, on replay AND holdout,
  and logs failures to a quarantine ledger. Mean solver trace steps: `sat.dpll` replay 16.115 -> 11.873, holdout 16.195 -> 12.043; `sat.trit` replay
  16.468 -> 11.877, holdout 15.52 -> 12.005; 46 candidates each; the first `sat.dpll` run was a dry run, the second applied it (2026-10-04, before
  this fragment's window, recorded here because the school's verifiers depend on it). (`docs/appendix/part7/ch1-live-school/results/evolve/*.json`,
  `docs/appendix/part7/ch1-live-school/results/strategies.json`; the generator source is not shipped in this tree)

Failures and negative results, as measured.
- The first multi-round launch sat idle 16 minutes after round 3: the round's ssh session hung after the server had finished, and the
  orchestrator watched only for exit. Remedy: server-side stall kill + heartbeat, keepalive + wall cap on the ssh, output streamed so that
  a laptop-side silence is real. (The 16 minutes and the cause are the status-log statement of the live-school pre-registration, `docs/appendix/part7/ch1-live-school/prereg/live-school.md`; the first launch's own log ends in an rsync
  error (code 255) after the round-2 plan, reduced to that line in the launch-records summary above; run records above.) (partial)
- Round 15: one spliced harness (h2) trained into an eleventh day alone and was terminated at 17 min 40 s while the other seven had stopped after day 10
  (`docs/appendix/part7/ch1-live-school/results/live-school/r15/round.log`); the round loop now caps every harness at ROUND_DAYS (`harness/part7/ch1-live-school/school-round.sh`).
- A phase merge put `numth.prime` level 5 into a level-6 phase and the generator raised KeyError 6: no merge across a generator's top level
  (`harness/part7/ch1-live-school/school_graph.py` `HS_DEPTH_FAIL`, lines 26 and 240; the code comment dates it to the first r10 launch).
- "Mastered" hid a collapse (section 4). Judge rounds by skills at gate and held-out loss, never by the sticky count.
- No WALL stop in 16 rounds (`WALL` false and `wall_rounds` 0 in every row of `docs/appendix/part7/ch1-live-school/results/live-school/rounds.jsonl`); the high-school rungs A, C-J have no generator, so a
  run would climb rung B and stop there (graph code, G1).

FIELD PREDICTS: Skill-it (Chen et al., NeurIPS 2023) - a skills graph with an online sampler driven by per-skill progress trains faster than
uniform or hand-ordered sampling; learning-progress task selection (Graves et al., ICML 2017); easy-to-hard ordering helps when it matches the
learner (Bengio et al., ICML 2009). The bar "frontier-plus-review rounds raise skills-at-gate until a wall" was met in trend up to r12 (tier-1 skills at the gate 28 -> 72, with dips at r2, r6 and r11; 126
mastered by the sticky count) and no wall was reached (`WALL` false in all 16 rounds).

## Reasoning rows, a negative wall predictor, and a comparison with published small models

Description. `harness/part7/ch1-live-school/reason_report.py` appends to each round's record: `doing_answered` (mean closed-loop DOING answered rate on fresh problems,
verifier-checked), `retry_fixed` (fixed on retry after study / retried), `novel_answers` (1 - share of answers found whole in the training
corpus, by a suffix-array memorisation detector), `level_up` (held-out score on skills one level above each lesson's highest mastered level),
`tier1_at_gate`. `harness/part7/ch1-live-school/wall_predict.py` fits, per skill, the least-squares trend of the last K scores and the residual RMS ("vibration");
stall score = vibration / (|slope| + eps), eta = rounds to the gate; `--backtest H` hides the last H scores and scores the stall prediction by AUC.

Measured gates.
- G1: reasoning rows, rounds r9 / r10 / r11 (the restarted r9): DOING answered 0.626 / 0.636 / 0.641; retry-fixed 0.483 / 0.489 / 0.463; novel
  answers - / 0.704 / 0.695; level+1 held-out 0.779 / 0.774 / 0.797; continuing, r12 / r13 / r14: DOING 0.643 / 0.623 / 0.644, retry-fixed 0.495 / 0.472 /
  0.394, novel 0.784 / 0.987 / 0.986, level+1 0.794 / 0.815 / 0.807 (`docs/appendix/part7/ch1-live-school/results/live-school/rounds.jsonl`, the `reasoning` field). From r13 the record mixes
  sources: the novel share is read from harness h0's memorisation report (a middle-type harness), while DOING, retry-fixed and level+1 come from the backed-up
  core, which is the tier-1 core in the split rounds r13 / r14 and harness h0's spliced core in r15 / r16 (`harness/part7/ch1-live-school/school-live.sh` lines 65-72,
  `harness/part7/ch1-live-school/reason_report.py`). For r15 / r16: DOING 0.395 / 0.392, retry-fixed 0.074 / 0.184, novel 0.927 / 0.992, level+1 0.769 / 0.811. These later rows are not
  comparable with the earlier ones (a different row mix), and the high "novel" share is a share of 10-beat-format reasoning rows, not of the earlier tier-1 symbol
  rows. The quoted "novel answers 0.70-0.99" is the range of this column.
- G2 (negative): the wall predictor's per-skill stall score does NOT predict stalls. Recomputed by replaying rounds 0-7 through the shipped planner and running
  `harness/part7/ch1-live-school/wall_predict.py --backtest H` (101 / 96 / 99 skills with the last 1 / 2 / 3 rounds hidden): stall-score AUC 0.449 / 0.406 / 0.350 (chance is 0.5);
  the simple gap-to-gate signal 0.674 / 0.673 / 0.631; school-level gain trend +0.4 skills per round (gains 5, 6, 5, 9, 3, 7, 9), no wall in sight. The tool is kept
  for the school-level forecast and the next-to-master list; the stall score is unvalidated. Discrepancy: the project's test index (not shipped) records the stall AUCs as 0.43 /
  0.44 / 0.55 and the header of `wall_predict.py` says 0.35-0.55; the recomputation reproduces the gap-to-gate figures and the trend exactly, and the stall
  figures only inside the header's range (replaying other rounds gives 0.27-0.50); the indexed values come from the project's test index, not shipped.
- G3: published comparison (explicitly NOT a controlled test: different tasks, tokenisers, evals; the comparison note is a private review, not shipped).
  Ours at the round-9 restart (2026-10-08): 98 skills mastered by the sticky rule, of which 58 of the 146 skills scored that round were at or above 0.85 on
  verifier-checked held-out problems; held-out loss 0.609; no GPU. Tokens: every harness trains about 0.40 M tokens per round (399,360 to 415,744 in the 48
  harness-round states in the shipped tree), so 8 harnesses x 10 rounds (rounds 1-8, the discarded round 9, the restarted round 9) is about 32 M plus the pre-K
  ladder (the comparison note says "35-40 M", its own estimate). Server time: the launch records through the restart add to 9,939 s (2.8 h, including idle
  waiting and the discarded round), about $3 at the quoted price. The comparison note reads "98 skills >= 85 % exact"; the results give 58 at the gate and 98
  sticky (section 1). Published rows, transcribed by the comparison's author and not re-read here (partial): Lee et al. (ICLR 2024) 10.6 M float parameters,
  plain-format 3-digit addition plateaus a little above 85 % with 10,000 examples; Eldan and Li (2023) 1-33 M parameter models give fluent English; grokking
  studies (Power et al. 2022) need 30-60 % of all pairs of one modular operation. Our depth is shallower (mastered skills mostly level 1-3, levels >= 3 at
  0.6-0.85) and we do not yet speak English at the TinyStories level.
- G4 (a negative, from our own earlier controlled run `rg1`, 2026-10-03, an older 4-layer d128 trunk, 10 M tokens per arm, same problems and seed, context
  512 by the pre-registered amendment (not shipped); the harness header still says 256): exact-answer accuracy on held-out problems at levels 1-3 (out-of-distribution
  levels 4-5 in brackets; every value is a multiple of 1/780): plain question-answer 21.2 % (17.2 %), full traces 13.7 % (12.1 %), shuffled traces 8.2 % (10.0 %),
  forward-only traces 12.8 % (11.0 %), our engine's format 12.1 % (11.5 %). The conventional format WON at that scale; the pre-registered kill rule (full traces
  at most 2 points above plain) is met, full traces being 7.4 points below. The plain arm was scored twice: 15.1 % (7.9 % out of distribution) in the
  first run (`docs/appendix/part7/ch1-live-school/results/rg1/rg1.result.armA-oldeval.json`) and 21.2 % (17.2 %) by the serial evaluator that produced the table, where the arm is marked as resumed from its
  checkpoint (greedy decode identical on 12 of 12 probes), so the evaluator moves a number by about six points; the ordering holds under either. Our 10-beat format has not been compared head-to-head with plain rows on the current school.
  (harness `harness/part7/ch1-live-school/rg1.py`; results `docs/appendix/part7/ch1-live-school/results/rg1/{rg1.result.json, rg1.result.armA-oldeval.json,
  rg1.result.serial-eval.json}`)

FIELD PREDICTS: training on the model's own verified answers (STaR, Zelikman et al., NeurIPS 2022) improves reasoning where a verifier exists;
data format dominates small-model arithmetic learning (Lee et al., ICLR 2024); exact-substring matches against the training set measure
memorisation (Lee et al., ACL 2022 deduplication work, using suffix arrays, Manber and Myers 1993); compute-optimal token counts are about 20
per parameter (Hoffmann et al., 2022) - we are at about a quarter of that, so the comparison favours breadth, not depth.

## Reading
Frontier-plus-review rounds raised skills at the gate steadily, with dips at r2, r6 and r11, and the loop did what it was built for:
it planned every round itself. The compute was modest — about 0.40 M tokens per harness per round, roughly 32 M tokens and 2.8 server
hours through the round-9 restart. FIELD PREDICTS: a skills graph with an online sampler driven by per-skill progress trains faster than
uniform or hand-ordered sampling (Skill-it, Chen et al., NeurIPS 2023; Graves et al., ICML 2017); easy-to-hard ordering helps when it
matches the learner (Bengio et al., ICML 2009). Matched in trend; no controlled comparison against uniform sampling was run.

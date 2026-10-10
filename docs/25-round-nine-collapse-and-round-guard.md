# The round-9 collapse, the round guard and keep-5 rollback

| | |
|---|---|
| **Date** | 2026-10-08 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). The author reviews each document before publication. |
| **Type** | measured failure and the guard built from it |
| **Verdict** | Collapse disclosed as measured; guard PASS (flags round 9, 0 false alarms on rounds 2–8); recovery PASS (four rounds) |
| **Code** | `harness/part7/ch1-live-school/round_guard.py`, `forget_watch.py` |

*The record below is the full measured account from the technical disclosure's working chapters: every gate, every failure, with the
harness and result paths in this repository. "Section n" and "§n" inside it refer to the sections of that chapter; the matching documents here
are listed in the README. "Recorded; no saved result" marks a figure the project recorded whose output file is not published.*

## The round guard, keep-5 rollback, forgetting watch, and the round-9 collapse (`harness/part7/ch1-live-school/{round_guard.py, forget_watch.py}`)

Description. After each round the orchestrator (a) fetches `skill.json`, (b) runs the guard against the LAST GOOD round G, (c) on PASS updates
the state, backs the core up (`cores/rN`, last 5 kept on the laptop, last 5 round directories kept on the server), (d) on FAIL moves the
round aside (`rN.failK`), keeps the good core and redoes the round with a larger review share (0.4, then 0.6: min(0.6, 0.2 + 0.2 x attempt));
after 2 failed redos it stops for the author. **Guard rule**, evaluated on the tier-1 skills scored in BOTH rounds (so a changed eval set cannot
fake it): FAIL if the count of skills at the gate falls by more than 10 %, or if the logged held-out loss rises by more than 30 %; a held-out
jump above 3x is treated as a different set (the first harness changed school) and skipped, noted in the verdict. The sticky mastered count is
never used. **Forgetting watch:** a slip is a mastered skill whose latest score is under the gate; each slip gets replay weight in the next
plan proportional to how far it fell (share 0.15 of the plan).

Measured gates and failures.
- Round 9 as first run (8 harnesses, 3 on middle builds averaged in the same day merge as 5 tier-1 harnesses; `docs/appendix/part7/ch1-live-school/results/live-school/r9.collapsed/`): tier-1 skills at
  gate 55 (of 148) -> 6 (of 167); mean tier-1 score 0.811 -> 0.492; held-out loss 0.717 -> 2.595; canary 0.474 -> 1.109; `k.transport` levels 1-5
  0.954 / 0.955 / 0.937 / 0.888 / 0.864 -> 0.360 / 0.329 / 0.308 / 0.224 / 0.247 (mean 0.919 -> 0.293); the 46 middle skills scored 30 at the gate; the
  sticky mastered count ROSE 93 -> 123 (+30 middle skills). The forgetting watch flagged 80 of the 123 mastered skills as under the gate (their current
  score in `state.r9-collapsed.json`, recomputed). (`docs/appendix/part7/ch1-live-school/results/live-school/{r8/skill.json, r9.collapsed/skill.json, r9.collapsed/round.log, rounds.r9.jsonl,
  state.r9-collapsed.json}`)
- Guard backtest, re-run from the shipped files (each round against the one before; the collapsed round 9 supplied as `r9`): rounds 2-8 PASS (0 false
  alarms in seven comparisons; round 3 has no held-out line); round 9 FAIL on the gate-count rule: tier-1 at the gate 53 -> 3 on the 141 shared skills (mean on
  the shared set 0.811 -> 0.473). The held-out rule did not decide it: 2.595 against 0.717 is a 3.6x jump and the shipped guard reads a rise above 3x as a
  different held-out set and skips it ("held-out sets differ - not compared"); the project's test index (not shipped) records the verdict as FAIL on both rules, the shipped code
  reproduces only the first. (`harness/part7/ch1-live-school/round_guard.py` run over `docs/appendix/part7/ch1-live-school/results/live-school/r<N>/{skill.json, round.log}`.) That
  the pod prune keeps exactly the last 5 round directories (a local fixture) is recorded only in the project's test index (not shipped) (partial).
- Recovery: restart from the r8 core with middle locked (`docs/appendix/part7/ch1-live-school/results/live-school/r{9,10,11,12}/{guard.json, round.log}`): r9 tier-1 at the gate 58 of 146 (r8: 55 of
  148), held-out 0.609, canary 0.442, guard PASS (shared at the gate 44 -> 53 on 134 skills); r10 PASS (42 -> 55 on 128; held-out 0.617; 64 of 140 at the
  gate); r11 PASS (52 -> 52 on 127; mean 0.827 -> 0.842; held-out 0.592; 60 of 141); r12 PASS (49 -> 60 on 128; held-out 0.616; 72 of 145).
- Forgetting-watch fixture PASS (a skill forced below the gate takes replay weight 0.05 -> 0.215 in the next plan); on the live r8 state 20 of 93 mastered
  skills were under the gate, replay share 0.15 (`docs/appendix/part7/ch1-live-school/results/forget_watch.json`, `docs/appendix/part7/ch1-live-school/results/live-school/r9/replay.json`; tool
  `harness/part7/ch1-live-school/forget_watch.py`).
- The guard code is shipped and matches its description (`harness/part7/ch1-live-school/round_guard.py`); its printed verdict for rounds 9-16 is
  stored as `docs/appendix/part7/ch1-live-school/results/live-school/r<N>/guard.json`.

FIELD PREDICTS: averaging weights from a shared initialisation works while the models stay in one basin (Frankle et al., ICML 2020, linear mode
connectivity; Wortsman et al., ICML 2022, model soups; DiLoCo, Douillard et al., 2023, merges after local steps on one task distribution) and
degrades when the merged models were trained on different objectives (Matena and Raffel, NeurIPS 2022, Fisher merging; Yadav et al., NeurIPS 2023,
interference between merged task vectors). The merge of two formats (symbol rows and reasoning rows) collapsed tier-1 as predicted. Forgetting
events are a measurable property of training (Toneva et al., ICLR 2019); the watch uses that.

## The standing curriculum decisions, and which measured runs honoured or dropped each

The author's rule, recorded in the plan after one run dropped a decision: before any restructure, list the standing decisions for the system
and tick each against the new design. The list as written in the live-school pre-registration (its standing-decisions table, `docs/appendix/part7/ch1-live-school/prereg/live-school.md`), with what each measured run did.
Runs: A = r1-r8 (tier-1 only, review share, no preview); B = r9 first attempt (3 middle + 5 tier-1 harnesses in one merge); C = r9-r12 after
restart (middle locked); D = r13-r14 (middle on its own core); E = r15-r16 (spliced circular builds, one core); F = the GPU growth runs.

| # | Decision (verbatim where quoted) | A | B | C | D | E | F |
|---|---|---|---|---|---|---|---|
| 1 | "every curriculum should be circular and build on all previous layers": pass 1 of a school reviews the schools before it, the last pass previews the next (the author's tier-1 school specification, section 8, 2026-10-04, not shipped; restated 2026-10-08) | partial: review share only, no preview | DROPPED (middle build had no tier-1 review) | partial (no preview) | DROPPED | HONOURED | designed (preview 0.1), no round completed |
| 2 | The 10-beat format on every row, never terse question-answer rows mixed in; pre-K is format (a) bare episodes by the author's own 2026-10-04 amendment ("a for prek b for k") | honoured | honoured | honoured | honoured | honoured | n/a |
| 3 | Ladder: one level above mastery plus review of a few below | honoured (frontier + 20 % review) | honoured | honoured (+ forgetting-watch replay) | honoured | honoured | n/a |
| 4 | Study = review own reasoning, `[revise]`, retry; sleep integrates the skill, never copies answers | honoured (every day: doing, study, sleep with canary gate, retry) | honoured | honoured | honoured | honoured | n/a |
| 5 | Middle locked until elementary is done, except author-approved middle experiments | honoured (no middle) | DROPPED (before the lock existed) | honoured | experiment, approved | experiment, approved | n/a |
| 6 | Back up every round's core, keep the last 5 (a rolling rollback copy), fall back and redo on failure | not yet built | not yet built | honoured | honoured | honoured | DEVIATES: the A40 launch script sets KEEP_CORES=2 (permanent keeps by the growth controller instead) |
| 7 | Develop the 26 generators already in the model, add no faculty without the author | honoured | honoured | honoured | honoured | honoured | honoured (generator growth only designed) |
| 8 | (2026-10-09) a stage passes only when EVERY skill in it scores 100 % on held-out | gate 0.85, sticky | same | same | same | same | built in the planner (section 9) but never exercised on a completed round |

(`harness/part7/ch1-live-school/school-live.sh:15-19`; `harness/part7/ch1-live-school/school-compile.sh`; `harness/part7/ch1-live-school/school_graph.py:113-121`; the project's test index (not shipped);
`harness/part7/ch1-growth-controller/run_a40.sh`; the round logs of section 1) [P: the per-run columns are this chapter's reading of the
logs and plans, and decision 2 is asserted by the plan table, not tested; the counts they rest on are recomputed in section 1]

Reading: the one run that dropped decision 1 and the run that dropped it again as an experiment (D) are the two runs that wiped tier-1; the
run that honoured it (E) is the one that kept tier-1 while learning middle (section 3). Elementary was NOT complete when middle started:
the frozen r12 core held 13 of 20 elementary skills at the 0.85 gate (sticky and by current score) and none at 1.0
(`docs/appendix/part7/ch1-growth-controller/results/growth-base/r12-elem/school-state-r12.json`, recomputed; section 9 G1).

FIELD PREDICTS: the spiral curriculum (Bruner, 1960); training a new task without rehearsal of the old interferes with it, rehearsal
reduces that (McCloskey and Cohen, 1989; Robins, 1995). The measured sequence matches the prediction in both directions (sections 3, 4).

## Reading
Averaging weights works while the merged models stay in one basin, and fails when they are trained on different objectives. Two formats
(symbol rows and reasoning rows) in one merge collapsed tier-1, as predicted. FIELD PREDICTS: linear mode connectivity and model soups
(Frankle et al., ICML 2020; Wortsman et al., ICML 2022) hold for one task distribution; merging across tasks interferes (Matena and
Raffel, NeurIPS 2022; Yadav et al., NeurIPS 2023); forgetting events are measurable (Toneva et al., ICLR 2019). The lasting rule: a
sticky count is a record of what was once learned, not of what the model knows now.

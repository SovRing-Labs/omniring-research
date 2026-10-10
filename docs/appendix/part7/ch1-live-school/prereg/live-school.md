# LIVE-SCHOOL-0 — the restructured curriculum (R1–R8) + high school A→J stacked on it, then a full run (claude seat, 2026-10-08)
J 10-08: "do r1-8 all at once and do a full run. can high school be all of those options in order with the model just working up the list
until its competent and moving up the rung?" → readback confirmed: "correct, 2 stacks on 1". Brainstorm: `<notes>/THEAD/CURRICULUM-
BRAINSTORM-2026-10-08.md`. Parent project: SEED-SCHOOL-GROW-0. Constraint: every row in J's format (VOCAB). Tests → `tests/INDEX.md`.

## Architecture (zero runtime rewrite: live at ROUND granularity)
One loop on the pod: **round** = (1) the sampler reads the skill graph + per-skill gates → (2) compiles a fresh build for exactly the
frontier skills + spaced review, new row seed (R2: live; every round new rows) → (3) thead-learn trains one pass of it (parallel day merge,
4–8 harnesses) → (4) per-skill eval (held-out) → gates update → (5) next round. A rung (skill) is mastered at its gate; a WALL = the frontier
stops moving for K rounds → pause for growth (SEED-SCHOOL-GROW-0 S1/S2).

| Step | What | Verify |
|---|---|---|
| L1 Skill graph (R1) | `harness/school_graph.py`: nodes = tier-1 lesson × level, bridge lessons, middle generator × level, high-school rungs A→J; prerequisite edges seeded from the lesson design + school order, re-weighted online from per-skill learning progress | `school_graph.py show` lists nodes + edges; unit test: a node unlocks only when its prereqs pass |
| L2 Sampler + per-skill gates (R3) | frontier = unlocked ∧ not mastered; weights ∝ learning progress + floor; 20 % spaced review of mastered; gate = held-out top-1 on the learnable classes (operand · state · transport · operator; tier-1) / answer span (middle) ≥ 0.85 | `school_graph.py plan --round N` writes a round spec; replay of the 4 saved evals gives the expected frontier |
| L3 Round compiler (R2) | round spec → tier-1 build (tier1_school) and / or middle build (curriculum.py) with a fresh row seed; held-out = reserved seed range | a round build compiles; t1-replay PASS |
| L4 Selective loss (R4) | compiler writes `mask_k.u8` (1 = do not train on the token this position predicts) on the FIRST occurrence of random goal operands; runtime sets y = −1 there when the file exists | gate: with an all-zero mask, loss == no mask (bit-identical); masked positions excluded from loss |
| L5 Operation-count axis (R5) | level = op count per lesson (tier-1: actions / term depth; middle: generator level); eval adds OOD at level+1, +2 | eval json carries `ood` per skill |
| L6 Bridge school (R6) | lessons `br.*`: the same tier-1 episode as symbol program AND as constrained English (our own child-level templates, our tokenizer), in J's 10 beats | replay PASS; English vocabulary ⊂ the template lexicon |
| L7 Mistake rows (R7) | tier-1 lessons gain a mistake variant: wrong step → MEET / TAPE shows it → `[revise]` → fix (middle already has recovery rows, RECOVERY_SHARE 0.5) | every gold mistake episode still solves; `[revise]` positions present |
| L8 Metamorphic variants (R8) | per episode a frame change (operand relabel by a ring permutation, commuted terms) carried consistently through goal, program and state | gold variants solve; variant pairs differ only by the frame |
| L9 High school rungs A→J (stack 2 on 1) | rungs in order: B depth (reason-gen levels 6–8) · A composition (2–3 generators chained) · C study at full strength · D code alphabet · E dock engines · F projects · G shards · H authoring · I macros · J abstention; each rung = lesson generator + gate; the run climbs until a rung has no generator yet (honest stop) | per rung: compile + gate defined; unbuilt rungs listed as such |
| L10 Full run | pod (J's go; cpu5c 32 vCPU $1.12/h), start core = `results/pod-20261008/par-v5/h0`; rounds until a wall or the last built rung; results fetched + indexed | gates per round in `results/live-school/rounds.jsonl` |

## Status log
- 10-08 plan written after J's go. Order: L4 (runtime, small) → L1–L3 (framework) → L6–L8 (lessons) → L5 → L9 → L10.
- 10-08 05:25Z r3: mastered 57 (+5), frontier 47. The round ssh hung after the pod finished (idle 16 min; seat watched exit only). Killed → r4 ran.
  Fixes (J "yes to all"): pod harnesses under `tw run --on stall=kill` + 2-min pod-tw heartbeat + nudge summary (`school-round.sh`, backup `.pre-tw`);
  `school-live.sh` keepalive + `timeout ROUND_WALL` + tee (swapped by atomic mv — the running bash keeps the old inode); tw in make-kit;
  stopgap watchdog for the current run; watcher = `tw wait`. PROCEDURES remedy row + memory feedback-verify-run-live. Pod copy of school-round.sh
  NOT yet updated (next launch).
- 10-08 06:00Z r4 66 (+9), r5 69 (+3). Pod compile (J "do 1"): `cloud/school-compile.sh` + `school-live.sh` POD_COMPILE=1 (ships harness, reason-gen,
  thead-generators, round specs, cloud scripts each round; middle builds compile on the laptop in parallel) · `tier1_school.py --out-root`. Test: 10 builds
  in 6 s on the pod, data byte-identical to the laptop. Swapped in by atomic mv (backup `.pre-podcompile`) → next launch.
- 10-08 07:00Z r6 76, r7 85, r8 93, r9 "123". r10 plan crashed: a MIN_SHARE merge put numth.prime@5 into a level-6 phase (KeyError 6) → fixed in
  school_graph (no merge across a generator's top level). Forgetting watch on the resume showed 80 of 123 mastered skills below the gate: round 9
  COLLAPSED tier-1 (≥0.85: 55 → 6; mean 0.81 → 0.49; held-out 0.72 → 2.60) — first round with 3 middle harnesses averaged into the same day merge
  as 5 tier-1 harnesses. Mastery is sticky, so "mastered" hid it. Resume stopped before training (pod idle). Decision for J: restart from the r8 core
  with middle kept out of the tier-1 merge. Pod compile verified live (9 builds 2 s). Idle pod: native engine build = no gain (2.02 vs 2.00 s/step).
- 10-08 07:30Z restart from the r8 core, middle locked until elementary (J): r9' 98 (+5, tier-1 at gate 58, held-out 0.609, guard PASS) → round guard +
  last-5 core backups wired (J: "fall back and redo curriculum anytime it fails … keep the last 5 cores"); r10 111 (+13, PASS), r11 117 (+6, PASS).
  Reasoning rows (DOING ~0.63, retry-fixed ~0.48, novel answers ~0.70, level+1 ~0.78). Field comparison `<notes>/THEAD/FIELD-COMPARISON-2026-10-08.md`.
  MANUAL `docs/systems/thead-cloud/` (new). DEVLOG <devlog-entry>…6.

## J's standing curriculum decisions (tick each against every redesign — PROCEDURES remedy 10-08)
| # | Decision (source) | Live school now |
|---|---|---|
| 1 | Every curriculum is CIRCULAR and builds on ALL previous layers: pass 1 reviews the schools before, last pass previews the next (TIER1-SYMBOL-SCHOOL-SPEC §8, 10-04; J 10-08) | ✔ from r15: every harness build spliced review → school → preview (`school-compile.sh`, `harness/splice_build.py`) |
| 2 | J's 10-beat format on every row; never terse Q→A mixed in (VOCAB "J's training format") | ✔ tier-1 format b / middle beats_inverse |
| 3 | Ladder: one level above mastery + review of a few below (VOCAB "ladder") | ✔ frontier + REVIEW share + forgetting-watch replay |
| 4 | Study = review own reasoning → [revise] → retry; sleep integrates the skill, never copies answers (VOCAB "study", "sleep") | ✔ thead-learn DOING / study / sleep; R7 [revise] lessons |
| 5 | Middle locked until elementary is done — EXCEPT J-approved middle experiments (J 10-08) | ✔ SCHOOL_MIDDLE=1 only on J's word |
| 6 | Back up every round's core, keep the last 5, fall back + redo on failure (J 10-08) | ✔ round guard + cores/ |
| 7 | Develop the 26 generators in the model, never add faculties without J (VOCAB "the 26") | ✔ no new domains |
- 10-08 09:35Z (wind-down) r13–r14 split middle (tier-1 core 99/92 at gate, held-out 0.518; middle core 37 middle but 2/155 tier-1 → non-circular wipes),
  r15–r16 CIRCULAR on one core (tier-1 91 → 103 at gate, middle 27 → 36 on the same core, tier-1 held-out 0.537 / 0.561 vs r12 0.616). Fixed on the way:
  clean-room marker for the tokenizer on the pod, equal days + straggler cut, phase padding (r16 DOING crash), guard held-out set-change note,
  memo off the critical path. Pod `pee8b7xhas2fkf` STOPPED 09:33Z after a full fetch (`runtime/results/pod-cpu32b/`, 3.9 GB). Backups: r12 elementary
  core ×5 (+ school-state-r12.json), r14 tier-1 + middle cores, r16 in cores/. Next launch: `thead-pod school cpu32b --on-pod` from live-r16/h0.

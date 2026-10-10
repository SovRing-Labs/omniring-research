# The growth controller: a 100 % stage gate, an independent-row sample size, and a hash-chained growth ledger (GROW-RUN gate G1)

| | |
|---|---|
| **Date** | 2026-10-09 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). The author reviews each document before publication. |
| **Type** | design + measured gates (synthetic evaluations and one wiring round) |
| **Verdict** | Controller gate PASS 14 / 14; wiring round PASS 6 / 6; **no growth round on real data has completed** |
| **Code** | `harness/part7/ch1-growth-controller/grow_ctl.py`, `g1_controller.py`, `g4_cuts.py`; stage mode in `harness/part7/ch1-live-school/school_graph.py` |

## The author's design, verbatim (2026-10-08, readback confirmed)
*"growth rate: how much each run progresses the model at every tier. have it set so that it autocreates it's curriculums, only passes
staage when it masters every skill in that tier to 100, once it finishes middle school, it can start growing it's own parameters. have
it auto save checkpoints to backup every so often, it will grow extremely quickly during these runs. we need to set this structure so it
can evovlve itself as it needs. it may be off intuitive but it will show something important."*

Earlier the same week: *"i'd want to have them go until they hit a wall, with a monitor watching when that is. i've a feeling my model
would do middle school well up to half of highschool before capping out"*, and *"prek-high school will be foundational. college will be
continuous and whatever users decide the model needs to learn next/parameters to grow."*

*The record below is the full measured account from the technical disclosure's working chapters: every gate, every failure, with the
harness and result paths in this repository. "Section n" and "§n" inside it refer to the sections of that chapter; the matching documents here
are listed in the README. "Recorded; no saved result" marks a figure the project recorded whose output file is not published.*

## The growth-run controller: stage gate at 100 %, independent-row sample size, min-cut frontier weights, hash-chained ledger (growth-run gate G1; pre-registration `docs/appendix/part7/ch1-growth-controller/prereg/growth-run.md`)

The author's design statement, verbatim (2026-10-09, readback confirmed): "growth rate: how much each run progresses the model at every tier. have
it set so that it autocreates it's curriculums, only passes staage when it masters every skill in that tier to 100, once it finishes middle school,
it can start growing it's own parameters. have it auto save checkpoints to backup every so often, it will grow extremely quickly during these runs.
we need to set this structure so it can evovlve itself as it needs. it may be off intuitive but it will show something important." Confirmed
design: every growth run on the GPU from the 24 GB tier up (48 / 80 / 96 GB), each from the frozen round-12 copy; the planner writes every round's
curriculum; a stage (pre-K, K, elementary, middle) passes only when every skill scores 100 % on held-out (current score, not sticky); after middle
the run alternates growing parameters and growing skills, later new generators; checkpoints back up on a schedule.

Description (the controller as built: `harness/part7/ch1-live-school/school_graph.py` stage mode,
`harness/part7/ch1-live-school/skill_eval.py` rows, `harness/part7/ch1-growth-controller/grow_ctl.py`).
- **Stage rule** (`GROW_GATE=1.0`): a stage passes when every built skill holds a CURRENT held-out score at the gate on at least n independent rows;
  a slipped skill returns to the frontier; the next stage's level 1 is previewed (share 0.1, `GROW_PREVIEW`). Stages: pre-K, kindergarten, elementary
  (with the bridge), middle, high school. Unset = the live school's code path (section 1 G2: the shipped update reproduces all 16 recorded rounds with
  the switch off).
- **Sample size**: zero errors on n independent samples bound the true error below epsilon with confidence 1 - delta when n >= ln(1/delta)/epsilon;
  epsilon 0.01, delta 0.05 gives n = 300 rows per skill (rows, not token positions: positions of one row are correlated). Held-out is sized per skill: the
  growth round's held-out spec asks for 4,224,000 tokens at 300 rows per skill (`docs/appendix/part7/ch1-growth-controller/results/grow-a40-run3/r13/grow-a40-r13-ho.json`; 422,400 tokens at
  30 rows in the wiring round, `docs/appendix/part7/ch1-growth-controller/results/grow-wire-pod/r13/grow-wpod-r13-ho.json`).
- **Frontier weights** multiplied by how many skills a skill gates (min-cut idea, `GROW_GATES_W`): in the pre-K graph `pk.echo@1` gates the other 84 skills.
- **grow_ctl**: one growth-rate row per round (skills at the gate per stage, held-out, tokens, wall seconds, parameters, tier, gain and gain per hour); next
  mode: skills until middle is passed, then on a WALL parameters; after a growth a grace of at least 3 rounds (up to 10 while the held-out has not come back
  below its value at the growth); a WALL again within 6 rounds of a growth with no gain in skills at the gate: generators; permanent keeps (every 5 rounds,
  each stage pass, the round after each growth) with a sha256 manifest, never pruned; a hash-chained ledger row per round (core checkpoint hash, hashes of the
  round's eval, plan and update records, gate evidence, decision, keep, the previous row's hash) and `verify`.

Measured gates.
- G1: frozen start (the last elementary-only core, hash-manifested, read-only; `docs/appendix/part7/ch1-growth-controller/results/growth-base/r12-elem/`) at the
  100 % gate: pre-K 10 of 85 skills at 1.0, K 4 of 61, elementary 0 of 20, bridge 2 of 15; at the 0.85 gate 52 / 47 / 13 / 14 are mastered by the sticky rule
  and 44 / 37 / 13 / 14 by current score (recomputed from `school-state-r12.json`, whose sha256 matches the manifest; the weight file is not shipped, so the
  core's own hash is not re-checked). The counts ignore the n >= 300 independent-rows condition, which the stored state does not carry, so a strict count could
  only be lower.
- G2: controller gate 14 of 14 (`harness/part7/ch1-growth-controller/g1_controller.py`, result `docs/appendix/part7/ch1-growth-controller/results/g1/g1.json`): the frontier is pre-K only and
  K level 1 is the preview; above-stage skills carry review weight only; 24 rows at 1.0 do not pass the stage and 300 do (pre-K -> K, a keep is written); a pre-K
  skill slipping to 0.9 returns the stage to pre-K; after a synthetic middle pass a WALL moves the mode to parameters, a recorded growth moves it back to skills,
  a second WALL within 6 rounds without gain moves it to generators, and a keep follows the growth; with the switch unset the plan is identical to the live
  planner's; the ledger chain verifies and a tampered row is detected. Every evaluation in this gate is synthetic: its report (9 rounds in 0.0006 h, "150.67
  skills per hour") is not a growth rate.
- G3: n = ceil(ln(20) / 0.01) = 300 (299.6; arithmetic; `GROW_MIN_ROWS` in `harness/part7/ch1-live-school/school_graph.py`); `pk.echo@1` gates 84 skills: re-derived from the graph code
  (section 1 G1) and recorded by the min-cut tool (`harness/part7/ch1-growth-controller/g4_cuts.py`, `docs/appendix/part7/ch1-growth-controller/results/g4/g4-cuts.json`: minimum vertex cut of the pre-K stage = {`pk.echo@1`};
  downstream counts `pk.echo@1` 84, `pk.ping@1` 39, `pk.hold@1` 34, `pk.commit@1` 24, `pk.babble@1` 24).
- G4 (wiring, one server round): a small round from the frozen core (1 harness, 1 day, epsilon 0.1 -> 30 rows; compile, GPU-library training and evaluation on the
  48 GB GPU) produced the stage fields, rows in the evaluation, a growth row, a keep with manifest and a ledger that verifies - 6 of 6 checks (`docs/appendix/part7/ch1-growth-controller/results/g3w/g3w-pod-a40.json`, with `docs/appendix/part7/ch1-growth-controller/results/g3w/growth.jsonl` and `docs/appendix/part7/ch1-growth-controller/results/g3w/update-r13.json`; harness `harness/part7/ch1-growth-controller/{run_a40.sh, g3w_local_round.sh}`): stage pre-K, 0 of 85 at the gate (one day), the round's guard PASS (42 -> 54 on 99 shared skills; held-out 0.616 ->
  0.526), growth row held-out 0.526, 1,200 s; the keep's weight hash differs from the frozen core's (it trained one day) and the frozen core's manifest entry that is shipped
  (`school-state-r12.json`) verifies. Failures: the launcher's own post-round step failed (a JSON decode error on a read-only state file, `docs/appendix/part7/ch1-growth-controller/results/grow-wire-pod/live.log`) and the update, growth
  row, keep and ledger were re-run by hand afterwards (the note in `docs/appendix/part7/ch1-growth-controller/results/g3w/g3w-pod-a40.json`); the ledger holds one row, so its chain check is trivial. No wiring round on the laptop
  completed: the machine history records eight attempts of the wiring launcher (four local, four on the server; exit codes in time order 1, -15, 1, 255, 1, 1, 124, 1; none 0; `docs/appendix/part7/ch1-growth-controller/results/launch-records-summary.json`), and the local round failed its own guard on the first attempt (tier-1 at the gate 42 -> 21 on 99 shared skills; `docs/appendix/part7/ch1-growth-controller/results/grow-wire-local/r13.fail1/guard.json`) and
  did not finish the redo. An 8-harness wiring round on the array server failed the guard the same way (42 -> 23; `docs/appendix/part7/ch1-growth-controller/results/grow-wire-pod8c/r13.fail1/guard.json`); the two other
  8-harness server rounds have no round result.

Failures: no growth round completed on real data (section 11): the stage rule, growth-rate rows and keeps were exercised only by the synthetic gate
and the small wiring rounds; no growth-rate number exists for any GPU tier.

FIELD PREDICTS: a bound of the form n >= ln(1/delta)/epsilon follows from the PAC model (Valiant, CACM 1984; Blumer et al., JACM 1989) and is the
"rule of three" at epsilon = 3/n for 95 % (Hanley and Lippman-Hand, JAMA 1983); all-pairs minimum cuts are a Gomory-Hu tree (Gomory and Hu, 1961);
a hash chain makes a record tamper-evident (Haber and Stornetta, J. Cryptology 1991); test error can rise at the interpolation threshold and fall
beyond it, so a wall may be grown past (Belkin et al., PNAS 2019; Nakkiran et al., ICLR 2020) - designed, see section 13.

## Designed, not measured

- **Parameter growth tool** (`om_set_active` exists in the engine source (not shipped), line 2734: grows active blocks inside the born allocation; new blocks
  born silent, output and down projections zeroed together with their optimiser state; a harness check recorded loss 8.711393 -> 8.711393 (`ladder_check.py`, not shipped; the value is in plan
texts only, no result file) (partial)). A tool that builds a larger checkpoint (depth stacking, width later) with a gate "loss identical before / after" and the controller's alternation after
  middle: NOT BUILT. Field kin: Net2Net (Chen, Goodfellow and Shlens, ICLR 2016); stacking for LLM pre-training (Du et al., NeurIPS 2024); learning to grow (Wang et al., ICLR 2023); masked
  structural growth (Yao et al., 2023).
- **Wall monitor with automatic growth** (designed in a pre-registration that is not shipped): not built; the live school's WALL rule only stops.
- **Generator growth hook**: on a wall growth does not lift, evolve the evolvable domains and put a proposal for new generators to the author. Only two of
  the 26 domains can evolve (`sat.dpll`, `sat.trit`; measured in section 1 G5); the hook that triggers evolution from the controller, and proposals
  for new generators, are NOT built (the controller only sets the mode); a new faculty needs the author's admission.
- **High-school rungs A, C-J** have no generator; rung B (the 26 at levels 6-8) is built for 72 nodes; levels 6-8 fail for `numth.prime` (6, 7, 8),
  `mind.revise` (7, 8), `logic.chain` (8) (`harness/part7/ch1-live-school/school_graph.py:26`).
- **Pressure valve, prediction by the planner, skill-growth forge** (capacity rendered on demand from the cut read; the planner's next curriculum
  as the predictor; a spare replica slot trains a delta merged back only if the held-out gate passes): designed, only the indirect-dispatch part
  built (section 12 G5).
- **Saturation as a growth signal** (a saturated cut -> grow capacity; headroom -> grow skills; per-block local read-out losses to find which block
  saturates): designed.
- **Tiers 24 / 80 / 96 GB**: not run.

## Reading
The structure the author asked for exists and is tested on synthetic rounds; it has not yet grown a model. FIELD PREDICTS: the bound
n ≥ ln(1/δ)/ε is the PAC sample bound (Valiant, 1984; Blumer et al., 1989) and the "rule of three" (Hanley and Lippman-Hand, 1983);
all-pairs minimum cuts are a Gomory–Hu tree (1961); a hash chain makes a record tamper-evident (Haber and Stornetta, 1991); test error can
fall again past the interpolation threshold (Belkin et al., 2019; Nakkiran et al., 2020), the field's reason a wall may be grown past.

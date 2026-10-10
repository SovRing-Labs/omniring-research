# Circular builds by splicing: one core holds the earlier layers while learning the next

| | |
|---|---|
| **Date** | 2026-10-08 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). The author reviews each document before publication. |
| **Type** | measured result (two designs in sequential rounds; not a controlled pair) |
| **Verdict** | Middle on its own core: KILL (wipes tier-1). Circular, one core: PASS (holds tier-1 and learns middle) |
| **Code** | `harness/part7/ch1-live-school/splice_build.py`, `school-compile.sh` |

The author's rule since 2026-10-04, restated when a run dropped it: *"every curriculum should be circular and build on all previous
layers"*, and on 10-05: *"grow it throughout in the same spiral circular curriculum method … ensure all your work is able to compound
and resonate with every school epoch."* After the round-9 collapse (doc 25) the question was put again: *"are we not doing the circular
curriculum??"*

*The record below is the full measured account from the technical disclosure's working chapters: every gate, every failure, with the
harness and result paths in this repository. "Section n" and "§n" inside it refer to the sections of that chapter; the matching documents here
are listed in the README. "Recorded; no saved result" marks a figure the project recorded whose output file is not published.*

## Circular builds by splicing (`harness/part7/ch1-live-school/{splice_build.py, school-compile.sh}`)

Description. One harness walks review -> current school -> preview inside ONE build, so one core holds all layers. `splice_build.py OUT
SRC1[:w] SRC2[:w] ...` joins the phases of several builds in order. It REFUSES unless: identical token ids; generator plates 0..25 in the same
order; the same procedure plate (26). The tier-1 port (31 router vertices = 26 generators + procedure + 4 body plates) is a superset of the
middle port (27), so the first build carrying a `tier1` block supplies the output port and the others get an empty tier-1 block. Phase files
(tokens, kinds, stages, rows, masks) are renumbered; each source's phases keep their relative share scaled by its weight; the clean-room
marker is copied. Every phase is padded with one trailing token (kind 255, stage 0, mask 0) so no row ends on the phase's last index (the
runtime reads token j+1 up to a row's end). Weights: a middle harness = tier-1 review of every mastered tier-1 skill (REV_W 0.3) then middle
(0.7); a tier-1 harness = tier-1 frontier and review (0.9) then middle level-1 preview over all 26 generators (PRE_W 0.1). Harness split:
NM of NH harnesses train middle builds, NM = round(NH x middle share of frontier weight), at least 1 when middle skills are present.

Measured gates.
- G1: a spliced build loads and trains: the relaunched round 16 ran all eight harnesses for 10 days with 10 merges each, exit 0
  (`docs/appendix/part7/ch1-live-school/results/live-school/r16/round.log`); the first smoke (2 days, 3,691 windows across tier-1 and middle phases) is recorded only in the project's test index (not shipped) (partial).
- G2 (negative): middle on its own core, r13 / r14 (four middle-type harnesses merged only with each other, four tier-1 harnesses merged on the tier-1 core):
  the tier-1 core scored 99 of 162 / 92 of 155 tier-1 skills at the gate, first tier-1 harness's held-out 0.549 / 0.518, and 11 / 14 of the 46 middle skills at
  the gate without ever training on them; the middle core scored 32 / 37 of the 46 middle skills at the gate but only 3 of 162 / 2 of 155 tier-1 skills
  (the "MID-CORE tier-1 retention" lines of `docs/appendix/part7/ch1-live-school/results/live-school/r13/round.log` and `docs/appendix/part7/ch1-live-school/results/live-school/r14/round.log`). Middle-only training wipes tier-1.
- G3: circular, one core, r15 / r16 (five middle-type harnesses spliced review -> middle, three tier-1-type harnesses spliced tier-1 -> middle preview, one
  merge): tier-1 skills at the gate 91 of 161 / 103 of 165 and middle skills at the gate 27 / 36 of 46 on the same core; the round guard passed both
  (shared tier-1 skills at the gate 79 -> 79 on 141 in r15, 81 -> 91 on 148 in r16); the r12 elementary-only reference is 72 of 145
  (`docs/appendix/part7/ch1-live-school/results/live-school/{r15,r16}/{round.log, guard.json, skill.json}`). One core holds tier-1 and learns middle.
- Comparability caveats. (a) The held-out loss the round log carries is harness h0's. In r15 / r16 h0 is a middle-type harness whose held-out set is the
  middle set (2.230 / 1.856); the guard prints "held-out sets differ (0.518 vs 2.230) - not compared" for r15 and skips its held-out rule (a rise above 3x is
  read as a different set), so r15's verdict rests on the gate count alone. The tier-1-type harnesses' own held-out on their round's tier-1 set was 0.537 /
  0.531 / 0.534 (r15) and 0.561 / 0.555 / 0.548 (r16), against 0.616 for the first harness at r12 (the eight r12 harnesses: 0.597-0.625); every round's set
  is a new draw with a different lesson mix, so these are not strictly comparable across rounds (`docs/appendix/part7/ch1-live-school/results/pod-cpu32b/live-r{12,13,14,15,16}/h<k>/state.json`, k = 0 to 7). (b) The
  comparable measure is skills at the gate on skills two rounds share (the guard's rule). Split cores gave 99 / 92 tier-1 skills at the gate (r13 / r14),
  circular cores 91 / 103 (r15 / r16): neither design is ahead on this count (r13 above r15, r14 below r16); what the circular design adds is that the
  middle skills (27 / 36 of 46) sit on the same core as the tier-1 skills instead of on a second core that holds 3 / 2. The two designs ran in different
  rounds and are not a controlled pair.

Failure. Round 16's first launch crashed: two harnesses (h5, h6) exited 101 at step 60 of 195 with a panic at the runtime's `Seq::from_build`
(`src/thead.rs:537`), and the other six were terminated about three minutes later (6 min 54 s; `docs/appendix/part7/ch1-live-school/results/live-school/r16/round.log`). The plan's diagnosis: an index
equal to the length at a DOING build row that ends exactly at a phase end, with the other harnesses idle waiting for merge partners. Fixed data-side by
padding every phase with one trailing token; the runtime bounds fix is not yet made (Open). After the fix the relaunch completed 10 days with 0 crashes
(all eight harnesses exit 0, 10 merges each; launch 8 of the launch-records summary, exit 0 after 920 s).

FIELD PREDICTS: rehearsal / pseudo-rehearsal retains old tasks while learning new ones (Robins, 1995); weights of independently drifting
models cannot be averaged safely across incompatible tasks (section 4). Measured: the middle core scored 3 and 2 of 162 and 155 tier-1 skills at the gate;
the spliced cores scored 91 and 103 of 161 and 165 (round 12: 72 of 145).

## Reading
Middle-only training wipes tier-1; rehearsal inside one build keeps it. FIELD PREDICTS: training a new task without rehearsal of the old
interferes with it, and rehearsal reduces that (McCloskey and Cohen, 1989; Robins, 1995); the spiral curriculum (Bruner, 1960). Matched
in both directions.

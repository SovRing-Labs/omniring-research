# ramkit: memory switches on the school, all off by default

| | |
|---|---|
| **Date** | 2026-10-08 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). The author reviews each document before publication. |
| **Type** | measured result (switches gated for bit-identity when off) |
| **Verdict** | Off = bit-identical PASS; LUT5 backward not bit-identical (kept off); ring memory, episodic gate, A-GEM: nothing beyond noise on the school (kept off) |
| **Code** | `harness/part7/ch1-ramkit/` |

Built from the author's question about memory on the training server (doc 43): switches for the engine and runtime that must be bit-identical to the shipped engine when off, and tools the live school uses.

*The record below is the full measured account from the technical disclosure's working chapters: every gate, every failure, with the
harness and result paths in this repository. "Section n" and "§n" inside it refer to the sections of that chapter; the matching documents here
are listed in the README. "Recorded; no saved result" marks a figure the project recorded whose output file is not published.*

## ramkit switches on the school (all OFF by default; results in `docs/appendix/part7/ch1-ramkit/results/`)

Description. Engine / runtime switches built to be bit-identical when off (five are gated by result files here): LUT5 backward (dx through the
5-trit lookup tables), ring-addressed memory (rows with a learned gate), episodic gate memory, A-GEM (project the new gradient when it would raise
the old task's loss), shared-memory snapshot / reload, plus CPU-side tools used by the live school (`harness/part7/ch1-ramkit/` and `harness/part7/ch1-live-school/forget_watch.py`: forgetting watch, checkpoint soup + time
machine, memorisation detector, memo of verified problems, branch chooser, reactor tables, exact generator enumeration, snapshot search).

Measured gates (result files shipped; the engine source and the built engine library are not shipped, so they are not re-run here).
- G1: switches off equal the shipped engine and runtime bit-identically (losses, forward loss, parameter hash, logs, checkpoint) on the learning
  A/B and on one full school day; PASS (`docs/appendix/part7/ch1-ramkit/results/off_gate/verdict.json`, `docs/appendix/part7/ch1-ramkit/results/learn_off/verdict_final.json`; harness `harness/part7/ch1-ramkit/{off_gate.sh, learn_off_gate.sh, learn_off_final.sh}`).
- G2 (negative): LUT5 backward is NOT bit-identical (max relative gradient difference 9.68e-7, cosine 0.999999999999822); dx kernel 1.146x
  faster (3.406 -> 2.973 s) but whole step 0.963x (wall 21.39 -> 22.22 s): default-on not allowed (`docs/appendix/part7/ch1-ramkit/results/lut5bwd/verdict.json`; harness `harness/part7/ch1-ramkit/lut5bwd_gate.sh`).
- G3: ring-memory and episodic-gate gradients vs finite differences: worst relative error 4.09e-4, PASS (`docs/appendix/part7/ch1-ramkit/results/gradcheck/gradcheck.json`; harness `harness/part7/ch1-ramkit/ramkit_gradcheck.py`);
  snapshot reload reproduces the next step exactly, plain (92,154,654 bytes) and with memories (143,080,564 bytes) (`docs/appendix/part7/ch1-ramkit/results/snap/verdict.json`; harness `harness/part7/ch1-ramkit/snap_gate.sh`)
 .
- G4: A-GEM fixture (task A next = 3t+1 mod 256 mastered, then conflicting task B; rise of task-A loss over 60 B steps, GEM off / 1 / 2): conflict
  6.43 / 5.61 / 4.29, disjoint tokens 1.64 / 0.97 / 0.35: reduced, NOT held (`docs/appendix/part7/ch1-ramkit/results/gem/fixture_*.json`; harness `harness/part7/ch1-ramkit/ramkit_gem_fixture.py`).
- G5: A/B on pre-K v4 (seed 6400), warm from the ladder, one seed each, matched steps: ring memory held-out -0.043 (step 20) / -0.009 (step 40),
  canary +0.464 / -0.697; episodic held-out +0.005, canary +0.092; A-GEM held-out +0.008, canary +0.079 (episodic and A-GEM cut by the 20-minute
  cap in day 2, only day 1 matched). The off arm's own canary moves 1.367 -> 2.113 -> 2.529 across the same steps, so the ring's canary swings
  are inside the run-to-run range. All kept OFF pending the author's call (`docs/appendix/part7/ch1-ramkit/results/ab/{verdict.json, compare.json}`; harness `harness/part7/ch1-ramkit/{ab.sh, learn_arm.sh}`).
- G6: tool self-tests (results `docs/appendix/part7/ch1-ramkit/results/tool-selftests/*.json`; tools `harness/part7/ch1-ramkit/{memo.py, soup.py, reactor_tables.py, memdetect.py, branches.py, gen_enum.py, shard_search.py, common.py}`): the memo of verified
  problems: 9,984 problems, 0 verdict mismatches, 0 wrong answers trusted, round-2 hit rate 1.96 % on generated rows (a 21.2 % hit rate on real builds is recorded only in the project's test index (not shipped) (partial)); checkpoint soup bitwise equal to the day merge (synthetic and 4 real cores), identical cores byte-equal; reactor tables 0 of 100,000 term
  mismatches and 0 of 16,232 clock mismatches against the twin, 188,146,396 bytes; the suffix-array detector equals brute force and found 275 of 870 pod answers whole in
  its 2.0 M-token corpus (31.6 %); branch chooser checks all true; exact enumeration: 47 of the generator-level pairs of levels 1-5 of 11 generators are enumerable
  up to 10^9 slots, 23 of them exhaustively and 24 by 200,016 sampled round trips, and 1,500 of 1,500 generator outputs fall inside the enumeration for each (17
  entries are infeasible, with reasons); snapshot search: the same top-10 as the reference search on 5 of 5 queries (the queries are not reproduced here) and a
  registry fire that passes.

FIELD PREDICTS: A-GEM (Chaudhry et al., ICLR 2019) and GEM (Lopez-Paz and Ranzato, NeurIPS 2017) reduce forgetting with episodic-memory gradient
projection - reproduced on the fixture, not shown on the school; large product-key memory layers help at scale (Lample et al., NeurIPS 2019),
not predicted to move a 7 M model in two days - the single-seed A/B shows nothing beyond noise.

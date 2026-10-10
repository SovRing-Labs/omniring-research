# RELEASE-REVIEW-PKG-0 — private lineage + release package for cloud agents (claude seat, 2026-10-09)
Origin: J 10-09 — use Claude cloud credit to finalize the GitHub release; "package everything we've been working on this week";
machine-generated files ARE the lineage; include the session transcripts (timeline source); "whatever the agents will need".
Class: CLOSE (existing bundles, tchew, release-cut) + BUILD (the export script, INDEX, TIMELINE — each has its reader: the cloud agents).
Window: 2026-10-02 → 2026-10-09 (last published train 10-01).

## Ground (verified 10-09)
- Published: 7 SovRing-Labs repos == local <home>/release/* (0 ahead/behind). Prerelease bundles stop at 10-06 (tarsus); omnid/talon stale.
- Disclosure parts: 1-2 published; 3-4 in omni-ring-0.2.0; 5 in research-0.2.0; 6 only in <notes>/FOUNDATION; 7 unwritten.
- Transcripts: 104 session jsonl since 10-02 (531 MB); tchew store data/shards/transcripts.db (13,470 chunks, built 10-08, nomic vectors,
  C4 recall FAIL 0.150/0.115 — step chunks alike). Timeline is built from timestamps, not semantic search.
- ai-stack origin = example/repo placeholder; never pushed; history 5.4 GB — export is a fresh single commit.

## Rules
Only J pushes (ROADMAP). Export lands in <notes>/RELEASE/review-export/ (local). Scrub + gitleaks before any push; private session text
leaves the machine only on J's word at push time. No claim without a result file.

## Steps (verify command each)
| # | Step | Verify |
|---|---|---|
| 1 | Incremental `tchew ingest-sessions` (picks up 10-08..10-09 + scratch workspaces) | `tchew list` counts > 13,470 chunks / 242 sessions |
| 2 | Export scrubbed chunks, one file per session → lineage/sessions/ | file count == sessions; gitleaks 0 |
| 3 | TIMELINE.md: day → sessions → plans/DEVLOG entries → commits → results | every row cites a source path that exists |
| 4 | Stage release layer: bundles + Part 6 + manifests + release-cut + disclosure format guide | `bin/release-cut <n> --dry-run` per bundle |
| 5 | Stage lineage layer: DEVLOG/MANUAL, plans, _Reviews, results indexes, tests/INDEX.md, TW repro, governance | size report; no file > 90 MB |
| 6 | AGENTS.md (agent brief) + INDEX.md (claim → harness → result) + task cards per agent | each card names inputs, outputs, done-when |
| 7 | Scan: gitleaks, /home paths, vault/airtable/pod-snap/.key exclusions | 0 findings; exclusion list printed |
| 8 | Show J file list + size; J says go → create private repo, one commit, push | `gh repo view` private; HEAD sha == local |

## STATUS LOG
- 10-09 plan written; J approved the package (transcripts + all lineage).
- 10-09 steps 1-7 done: tchew refresh (249 sessions, +509 chunks); builder <notes>/RELEASE/review-pkg/{build,timeline}.py + run-all.sh; export <notes>/RELEASE/review-export (3,316 files, 76 MB, 104 sessions, TIMELINE 8 days); gitleaks 5 hits all false positives; RunPod key literal 0. Step 8 (private repo + push) waits for J's go. export dir in .git/info/exclude so checkpoints don't sweep it.
- 10-09 step 8 DONE (J: 'repo can be Pre-release. private. go ahead and push'): https://github.com/SovRing-Labs/Pre-release PRIVATE, main = c172777, 3,282 tracked files (34 build-output files skipped by the projects' own .gitignore: omnid binaries, embed-core e1/vocab parts). Verified: gh repo view visibility PRIVATE; remote sha == local. Commit identity = public noreply. Next: cloud session T1+T2 (J starts it).
- 10-09 coordinate (local side): Part 6 §4 'Released free' -> 'Licensed Apache-2.0 ... once published (not yet released)' (omni-spec LICENSE is Apache-2.0, repo unreleased); item 9 table <notes>/RELEASE/review-pull/BARS-BEFORE-HARNESS.md: 128 plan->harness pairs, 114 plan-first, 14 harness-first (mostly umbrella plans citing older code). Waiting on cloud push of claude/amazing-johnson-busfba for MISSING-ALL.md.

## PROBE-2G31 (J 10-09 "4. approved") — does a >2^31-byte arena silently mis-train the 5x8 school array? (pre-registered 10-09 ~21:40 UTC, BEFORE the run)
Origin: cloud agent T4 REVIEW-NOTES: "a 2^31-byte binding cap silently mis-trains on the A40, which may also explain the first 40-model run not learning".
Searched first: <plan>:103 (arena capped 3.5 GiB "40-model run re-gating") + tests/INDEX.md GROW-RUN-0 rows — no saved result answers it (run 3b stopped at start phase).
Pod: omni-gpu-a40 (7qp7lp6dfepfuu) $0.59/h, started 21:24:09Z; container disk was wiped by the stop (nothing to pull from ANY stopped pod) -> kit re-shipped (omni-gpu exe, gen, kernels, tests, CPU engine lib, build-v4 manifest, r12-elem T25 core).
Arms (same code, same seeds): A = default OMNI_TRAIN_ARENA_MAX (3.5 GiB); B = OMNI_TRAIN_ARENA_MAX=2147483392 (2^31 - 256).
Command: tests/train/s5_array.py --dims school --units 5 --per 8 --ring --steps 6 --device A40 --sw <SCHOOL_SW>  (its own learning gate: every harness's held-out within 2 % of the CPU reference, loss falling)
Bar: PASS = s5's gate passes AND loss(last) < loss(first) for all 40 harnesses. FIELD PREDICTS: a Vulkan storage-buffer binding range above 2^31 is legal on NVIDIA (maxStorageBufferRange 4 GiB) so A should also pass;
a failure of A only would mean a 32-bit signed offset overflow in the generated kernels.
Reading: B pass + A fail = bug confirmed; both pass = hypothesis not supported (cap already fixed it); both fail = other cause (gate noise / switches), report numbers.
Time box: <= 20 min per arm, pod stopped by 22:30Z at the latest. Cost <= ~$0.70.
- PROBE-2G31 arm A RESULT (10-09 21:35Z, pod A40, s5_array.py school 5x8 ring, default arena cap): REFUSED TO BUILD, not mis-trained — gen/train_step.py:73 raises "buffer(s) over one storage binding (2147483647 bytes): L_rtlg_0/1/2 = 2,684,354,560 B — fewer models per session (array server --group)". The guard (train_step.py:21 BIND_MAX, comment "NVIDIA A40: a storage binding of >= 2^31 bytes trains NOTHING, silently") was added by the GROW-RUN seat 10-09 01:48 (commit 53e318ed3), i.e. the finding was already known and is a loud error now; the package copy the cloud agent read predates it. Arm B (OMNI_TRAIN_ARENA_MAX=2^31-256) SKIPPED: the offending buffers are named L_rtlg_* (not arena members) and the guard is independent of ARENA_MAX, so B fails identically (deterministic; not run to save 7 min of pod time).
- PROBE-2G31 arm C (pre-registered 21:36Z, before run): the real array shape = ONE GROUP of 20 (5 units x 4 harnesses, what the 2-server x 20 run 3b uses): s5_array.py --dims school --units 5 --per 4 --ring --steps 6 --device A40 --sw <SCHOOL_SW>. Bar: no storage-binding error (largest buffer < 2^31) AND s5's gate passes (each harness held-out within 2 % of the CPU reference) AND loss(last) < loss(first) for all 20. VRAM + ms/step recorded. FIELD PREDICTS: R=20 halves L_rtlg to ~1.25 GiB, legal on the A40, so it should build and train; the 2 % per-harness bar may fail on noise alone (G3b-2: CPU-vs-CPU noise floor up to 4 %), report the numbers either way.
- PROBE-2G31 arm C RESULT (10-09 21:42Z, A40, R=20 = 5 units x 4, ring, school switches, 6 steps): no binding error; 8.549 GB resident; GPU 1,231.7 ms/array step vs CPU 26,608.7 ms (21.6x); all 20 harnesses learn (loss 8.46-8.90 -> 3.77-5.19); held-out gap vs the CPU reference mean 4.13 %, median 3.83 %, max 9.72 %, >2 %: 16/20, >4 %: 10/20, GPU higher (worse) than CPU on 17/20 (mean +0.129) -> pre-registered bar (each harness <= 2 %) FAIL. Reading: the 2 % bar is tighter than the engine reproduces itself (G3b-2 CPU-vs-CPU floor up to 4 %), but the sign skew (17/20) points to a small systematic GPU lag (candidates: GEMM v2 fp16 range, ring pull order) — NOT proven noise. Gate-change question already with J (<plan>:99). Files: projects/thead-trial/runtime/results/probe-2g31/. Pod 7qp7lp6dfepfuu stopped 21:43Z (uptime 1,103 s ~ $0.18). A stop wipes the container disk -> no pod holds data that the laptop lacks.

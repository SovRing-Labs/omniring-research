# growth-base/r12-elem — THE FROZEN START for every growth run (J 10-09: "we should have a few backups of the end of elementary. we'll make a
copy and use it through out the runs for growth testing through gpu size (24gb -96gb)" → readback confirmed)
Round 12 core of the live school = the last core trained on pre-K → elementary only (before any middle school). Source copies (same sha256
5b1c9c115aa73ac6…): live-school/cores-keep/r12-pre-middle, pod-cpu32b/keep/r12-pre-middle, pod-cpu32b/live-r12/h0 (+2 on the cpu32b pod disk).
Contents: ckpt.bin (6,926,912 float32 weights, D 256 · L 6 · H 4 · V 8,192) + ckpt.json · state.json (engine run state) · t25_core.{bin,json}
(the rendered T25 core) · school-state-r12.json (planner state: per-skill held-out scores, history, mastered) · rounds-to-r12.jsonl ·
r12.plan.log · MANIFEST.sha256. READ-ONLY: a growth run copies from here and never writes here (`sha256sum -c MANIFEST.sha256`).
At J's 100 % stage gate this core holds: pre-K 10 / 85 skills at 1.0 · K 4 / 61 · elementary 0 / 20 · bridge 2 / 15 (0.85 gate: 44 / 37 / 13 / 14).

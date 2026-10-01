# MANIFEST — OMNIRING research corpus (CC BY 4.0)

Working copy for export #3 (research corpus). Source docs are never edited: each included doc is copied, then the copy is
cleaned. Ground truth for what was measured: the omni-ring `TECHNICAL-DISCLOSURE.md`. Source paths use `~/` =
the author's home directory. `AS` = `~/ai-stack`, `OL` = `~/projects/omniring-llm`.

Decision key: **include** = publish as is after cleaning · **include-with-corrections** = publish only with
`> Correction:` notes against measured results · **exclude** = not published. Status: **done** = cleaned copy in
`docs/`; **todo** = left for the staged chew task RSX-CHEW; **n/a** = excluded.

Duplicates: the 18 `OMNIRING-*` files dated 2026-09-28 exist byte-identical in `AS/_Reviews/` and `OL/reviews/`
(checked with `cmp`). Each is listed once below under its `AS/_Reviews/` path.

## A. Measured results (RING series and engine builds)

| # | Source path | Proposed title | Category | Decision | Reason | Status |
|---|---|---|---|---|---|---|
| 1 | `AS/_Reviews/RING/RING1-CORE.md` | RING-1 core: cued recall, quantisation, eigengap and slot capacity | measured-result | include-with-corrections | Source of capacity ≈12 marks/slot; c = 0 rows need the seed-lottery correction | done → `docs/01-ring1-core-cued-recall-and-capacity.md` |
| 2 | `AS/_Reviews/RING/RING1-CORE.run.txt` | Appendix: RING1-CORE raw run | measured-result (log) | include | Evidence cited by #1 | done → `docs/appendix/` |
| 3 | `AS/_Reviews/RING/RING1-CHECK.md` | RING-1 T3: the 17 check ring flags wrong settles | measured-result | include-with-corrections | 81.8% flag / 0 false alarms; c = 0 collapse explained as seed lottery | done → `docs/02-ring1-check-ring.md` |
| 4 | `AS/_Reviews/RING/RING1-CHECK.run.txt` | Appendix: RING1-CHECK raw run | measured-result (log) | include | Evidence cited by #3 | done → `docs/appendix/` |
| 5 | `AS/_Reviews/RING/RING1-DIRECT.md` | RING-1: direct keyed vs bound storage, 1-bit tag | measured-result | include | 1000/1000 keyed direct read, 300/300 tagged | done → `docs/03-ring1-direct-keyed-storage.md` |
| 6 | `AS/_Reviews/RING/RING1-DIRECT-SEAT-NOTE.md` | (merged as appendix of #5) | measured-result | include | Explains the first KILL as a brief defect (156/300 vs 300/300) | done (merged into doc 03) |
| 7 | `AS/_Reviews/RING/RING1-DIRECT.run.txt` | Appendix: RING1-DIRECT raw run | measured-result (log) | include | Evidence cited by #5 | done → `docs/appendix/` |
| 8 | `AS/_Reviews/RING/RING1-DISPERSE.md` | RING-1: dispersal vs one crowded slot | measured-result | include | Clean negative result; ≈94% recall given right slot | done → `docs/04-ring1-disperse.md` |
| 9 | `AS/_Reviews/RING/RING1-DISPERSE.run.txt` | Appendix: RING1-DISPERSE raw run | measured-result (log) | include | Evidence for #8 | done → `docs/appendix/` |
| 10 | `OL/reviews/2026-09-29 — RING1-SOFTSWEEP.md` | RING-1 SOFTSWEEP: decode_soft vs direct_probe | measured-result | include-with-corrections | Fleet v1 harness invalid, rewritten; unguided rows are seed 0 only (seed lottery) | done → `docs/05-ring1-softsweep-decode-soft.md` |
| 11 | `AS/_Reviews/RING/RING3-RESULTS.md` | RING-3: PEEL, DIAMOND, CORREL, TABU, FRET (+ DIAMOND-2) | measured-result | include | PEEL PASS; TABU not adopted; seed-lottery harness disclosure; 15-value corners 91% | done → `docs/06-ring3-peel-diamond-correl-tabu-fret.md` |
| 12 | `AS/_Reviews/RING/RING3-RESULTS.run.txt` | Appendix: RING-3 raw run | measured-result (log) | include | Evidence for #11 | done → `docs/appendix/` |
| 13 | `AS/_Reviews/RING/RING3-RECS.run.txt` | Appendix: RING-3 exploratory arms | measured-result (log) | include | Evidence for #11 "Exploratory arms" | done → `docs/appendix/` |
| 14 | `AS/_Reviews/RING/RING3b-DIAMOND2.run.txt` | Appendix: DIAMOND-2 raw run | measured-result (log) | include | Evidence for #11 DIAMOND-2 | done → `docs/appendix/` |
| 15 | `AS/_Reviews/RING/OPEEL-READ.md` | Peeling in the engine: `omni_ring.peel.read_all` | measured-result | include | 16.65/24 true, 0/333 fakes; confidence-floor sweep | done → `docs/07-peel-read-all-module.md` |
| 16 | `AS/_Reviews/RING/RING1-HALO.md` | RING-1 T4: two-stage halo chain vs one resonator | measured-result | include | Clean pre-registered KILL; harness ships in `harness/ring1/run_halo.py` and re-runs to the same verdict | done → `docs/09-ring1-halo-two-stage-chain.md` |
| 17 | `AS/_Reviews/RING/RING1-HALO.run.txt` | Appendix: RING1-HALO raw run | measured-result (log) | include | Evidence for #16; verbatim run log, paths made relative | done → `docs/appendix/RING1-HALO.run.txt` |
| 18 | `AS/_Reviews/RING/RING1-SMOOTH.md` | RING-1 T2: smooth (fractional-phase) ring for "around when" | measured-result | include-with-corrections | KILL on discovery; the cue form works. Correction added: crowding, not dial resolution, was the original failure (`06-ring3-peel-diamond-correl-tabu-fret.md`) | done → `docs/10-ring1-smooth-fractional-phase.md` |
| 19 | `AS/_Reviews/RING/RING1-SMOOTH.run.txt` | Appendix: RING1-SMOOTH raw run | measured-result (log) | include | Evidence for #18; verbatim run log, paths made relative | done → `docs/appendix/RING1-SMOOTH.run.txt` |
| 20 | `OL/reviews/2026-09-29 — ODECAY-MARKSTORE.md` | Mark store: count-weighted accumulation, rehearsal counter, decay | measured-result | include | Engine build with tests; basis of disclosure §9; contract/lane metadata stripped | done → `docs/11-markstore-accumulation-and-decay.md` |
| 21 | `OL/reviews/2026-09-28 — OSEAM-D1-TRANSCODE.md` | Defining ternary (0,0) → phase 0 | measured-result | include | Measured defect (4,800/5,120 fabricated phases) and fix; home paths stripped | done → `docs/12-seam-defining-ternary-zero.md` |
| 22 | `OL/reviews/2026-09-28 — OSEAM-D2-PROJECTION.md` | Full-slot down-projection replaces truncation | measured-result | include | Fix for the 97.5% discard at the model seam; paths stripped | done → `docs/13-seam-full-slot-down-projection.md` |
| 23 | `OL/reviews/2026-09-28 — OSEAM-CLAIMS.md` | Replacing three false accuracy claims with a checkable claim | review | include | Public record of the retracted "zero hallucination" claims; commit/lane metadata stripped | done → `docs/14-seam-retracting-three-accuracy-claims.md` |
| 24 | `AS/_Reviews/2026-09-28 — MINIRING-ORA-ROOT Oracle CONVERGE (Decision).md` | Modulus set {3,5,7,13}+17: correctness and choice | review | include-with-corrections | 54,600-case exhaustive check, modulus rationale; labelled as a three-lens panel decision with corrections on the seed-draw and detection-count readings | done → `docs/15-modulus-set-and-check-ring-decision.md` |

## B. Reviews, syntheses, vision

| # | Source path | Proposed title | Category | Decision | Reason | Status |
|---|---|---|---|---|---|---|
| 25 | `OL/reviews/2026-09-28 — OMNIRING-PEER-REVIEW-RETRIEVAL-AND-CONSOLIDATION.md` | Peer review: retrieval, consolidation, claim ledger | review | include-with-corrections | Strongest review; "retrieval unmeasured", "capacity 1,365" and D1/D2/D4 corrected | done → `docs/08-peer-review-retrieval-and-consolidation.md` |
| 26 | `AS/_Reviews/2026-09-27 — OMNIRING chew (Gemini study threads → resonator rings).md` | Origin: from study threads to coprime resonator rings | review | exclude | J 2026-09-29 decision (4): source is J's Gemini study-thread exports, which are chat/session-derived; skipped here, kept for a separate readable edition. Ideas are kept in #27 and #28. | n/a |
| 27 | `AS/_Reviews/2026-09-27 — RSPK Resonator-VSA Oracle CONVERGE (9-cell).md` | RSPK: resonator/VSA spike decision (9-cell panel) | review | include-with-corrections | Decision + kill criteria; correction added: "don't build now" was superseded by RING measurements, and the K=32 patent argument is a design conclusion, not a legal finding | done → `docs/16-resonator-vsa-spike-decision.md` |
| 28 | `AS/_Reviews/2026-09-27 — XP1 Cross-field Oracle CONVERGE (9-cell).md` | XP1: which cross-field ideas change the design | review | include-with-corrections | Rules adopted vs metaphor; lane names stripped; corrections on the ACF mask claim, the K=32 qFHRR figure and the 7.7× speedup | done → `docs/17-cross-field-which-ideas-change-the-design.md` |
| 29 | `AS/_Reviews/XP1/citation-check.md` | XP1 citation check (17/17 arXiv ids resolve) | review | include | Appendix to #28; 17/17 arXiv ids resolve, titles match topic | done → `docs/18-appendix-xp1-citation-check.md` |
| 30 | `AS/_Reviews/RSPK/2026-09-27-RSPK-RES.md` | Dossier: resonator networks, factorisation in superposition | review (literature) | include-with-corrections | Literature review; citation check run at publication: 67/69 URLs resolve, 2 mis-pointed URLs fixed, no paper missing | done → `docs/19-dossier-resonator-networks.md` |
| 31 | `AS/_Reviews/RSPK/2026-09-27-RSPK-VSA1.md` | Dossier: VSA encodings, capacity, cleanup | review (literature) | include-with-corrections | As #30; contains first-party measurements; citation check run at publication | done → `docs/20-dossier-vsa-encodings-and-capacity.md` |
| 32 | `AS/_Reviews/RSPK/2026-09-27-RSPK-MATH.md` | Dossier: dynamics, fractals, projections, codes | review (literature) | include-with-corrections | As #30; citation check run at publication | done → `docs/21-dossier-dynamics-and-codes.md` |
| 33 | `AS/_Reviews/RSPK/2026-09-27-RSPK-VSA2.md` | Dossier: VSA in agent systems | review (literature) | exclude | Mostly fleet-routing context; J to confirm | n/a |
| 34 | `AS/_Reviews/RSPK/2026-09-27-RSPK-PHYS.md` | Dossier: noise, oscillators, energy landscapes | review (literature) | exclude | Cross-field breadth judged mostly metaphor by XP1/OUTLOOK; J to confirm | n/a |
| 35 | `AS/_Reviews/RSPK/2026-09-27-RSPK-MIND.md` | Dossier: neuroscience, psychology, learning | review (literature) | exclude | As #34; J to confirm | n/a |
| 36 | `AS/_Reviews/RSPK/2026-09-27-RSPKO-*.md` (9 files) | RSPK oracle panel cells | review | exclude | Internal panel inputs; #27 summarises them; field-data and lane details | n/a |
| 37 | `AS/_Reviews/RSPK/2026-09-27 — RSPK process retrospective.md` | — | governance/ops | exclude | Dispatch process metrics | n/a |
| 38 | `AS/_Reviews/XP1/branches/*.md` (7 files incl. MANIFEST) | XP1 branch dossiers | review (literature) | exclude | #28 summarises; cross-field material mostly metaphor; J may promote B2-CAPACITY | n/a |
| 39 | `AS/_Reviews/XP1/panel/XP1O-*.md` (9 files) | XP1 oracle panel cells | review | exclude | Internal panel inputs; #28 summarises | n/a |
| 40 | `AS/_Reviews/XP1/2026-09-27-GENERATION-NOTES-triage.md` | — | review | exclude | Superseded by #26 (per its own header); reads raw chat exports | n/a |
| 41 | `AS/_Reviews/XP1/B0-coverage.md` | — | governance/ops | exclude | Internal corpus coverage map | n/a |
| 42 | `AS/_Reviews/XP1/sources/` (SG1.txt, SG2.txt, GEMINI-SYNTHESIS-2026-09-27.txt) | — | raw AI export | exclude | Raw AI chat / study-guide exports | n/a |
| 43 | `OL/reviews/2026-09-28 — OMNIRING-LINEAGE-POSSIBILITIES-APPLICATION-SURFACE.md` | Where verified ring properties could apply (exploration) | vision | include-with-corrections | Self-labelled exploration; corrections added: market mapping is a hypothesis, only measured properties carry, and any cascade assumption is superseded by #16 | done → `docs/22-exploration-where-verified-properties-could-apply.md` |
| 44 | `AS/_Reviews/2026-09-28 — OMNIRING-RESONATOR-CORTEX-VISION IMAGINE.md` | Vision: a resonator cortex (speculation) | vision | include-with-corrections | Published as labelled speculation with corrections on every unmeasured claim: O(1) framing, MeZO, forward-shot adaptation, and any capacity beyond ≈12 marks/slot | done → `docs/23-vision-a-resonator-cortex-labelled-speculation.md` |
| 45 | `AS/_Reviews/2026-09-28 — OMNIRING-DECENTRALIZED-ARCHITECTURE-DEEP-DIVE.md` | — | vision | exclude | Gemini vision; overlaps #44; unmeasured claims throughout | n/a |
| 46 | `AS/_Reviews/2026-09-28 — OMNIRING-CORTEX-PATENT-HEADS-MOUTH.md` | — | vision | exclude | Gemini vision (14B-equivalence claims unmeasured); patent framing conflicts with prior-art intent — J decides | n/a |
| 47 | `AS/_Reviews/2026-09-28 — OMNIRING-GENERATOR-HEAD-BUILD-PLAN.md` | — | design | exclude | Unbuilt plan; overlaps #44 | n/a |
| 48 | `AS/_Reviews/2026-09-28 — OMNIRING-TRANSFORMER-REPLACEMENT-FEASIBILITY.md` | — | vision | exclude | "~70% milestone" etc. flagged unverified by #25; nothing measured | n/a |
| 49 | `AS/_Reviews/2026-09-28 — OMNIRING-CORE-GEMINI-01 Deliverable.md` | — | design | exclude | Original engine build log; claims superseded by the technical disclosure | n/a |
| 50 | `AS/_Reviews/2026-09-28 — OMNIRING-TIER-1-TERNARY-ENGINE.md` | — | design | exclude | Build log (test counts); kernel facts live in vsa-core/omni-ring disclosures | n/a |
| 51 | `AS/_Reviews/2026-09-28 — OMNIRING-TIER-2-RING-BANK-AND-CLAMP.md` | — | design | exclude | Build log | n/a |
| 52 | `AS/_Reviews/2026-09-28 — OMNIRING-TIER-3-RING-ATTENTIVE-TRANSFORMER.md` | — | design | exclude | Build log; "O(1) attention" and hallucination claims measured false/unbuilt (#25, #23) | n/a |
| 53 | `AS/_Reviews/2026-09-28 — OMNIRING-BIDIR-QUERY-01 Deliverable.md` | — | design | exclude | Build log, test counts only | n/a |

## C. Excluded: governance, operations, app integration

| # | Source path | Proposed title | Category | Decision | Reason | Status |
|---|---|---|---|---|---|---|
| 54 | `AS/_Reviews/2026-09-28 — OMNIRING-PORTAL-BRIDGE Deliverable.md` | — | governance/ops | exclude | Launcher/portal integration log, PIDs, local ports | n/a |
| 55 | `AS/_Reviews/2026-09-28 — OMNIRING-PORTAL-CLIENT Deliverable.md` | — | governance/ops | exclude | App integration log | n/a |
| 56 | `AS/_Reviews/2026-09-28 — OMNIRING-PORTAL-UI Deliverable.md` | — | governance/ops | exclude | App integration log | n/a |
| 57 | `AS/_Reviews/2026-09-28 — OMNIRING-SOAK-E2E Deliverable.md` | — | governance/ops | exclude | App soak test log | n/a |
| 58 | `AS/_Reviews/2026-09-29 — OMNIRING-PORTALS integration review (analyze · troubleshoot · imagine).md` | — | governance/ops | exclude | App integration review | n/a |
| 59 | `AS/_Reviews/2026-09-28 — OMNIRING-SHADOW-PROD Oracle CONVERGE (Decision).md` | — | governance/ops | exclude | Repo-process decision | n/a |
| 60 | `AS/_Reviews/2026-09-28 — OMNIRING-SHADOW-PROD-ORACLE-ADV.md` | — | governance/ops | exclude | Repo-process panel cell | n/a |
| 61 | `AS/_Reviews/2026-09-28 — OMNIRING-SHADOW-PROD Oracle REIMAGINE.md` | — | governance/ops | exclude | Repo-process panel cell | n/a |
| 62 | `AS/_Reviews/2026-09-28 — OMNIRING-SHADOW-PROD Oracle RELIABILITY.md` | — | governance/ops | exclude | Repo-process panel cell | n/a |
| 63 | `AS/_Reviews/2026-09-29 — MINIRING-ORA-STR Oracle Pass.md` | — | governance/ops | exclude | Portal bundler/build audit | n/a |
| 64 | `AS/_Reviews/2026-09-29 — MINIRING-ORA-TOP Oracle Pass.md` | — | governance/ops | exclude | Portal architecture + TURN-0 attestations | n/a |
| 65 | `AS/_Reviews/2026-09-27 — OUTLOOK after RSPK + XP1 (what the sprints changed).md` | — | governance/ops | exclude | Fleet throughput/dispatch metrics | n/a |
| 66 | `AS/_Reviews/OMNI-SAE/2026-09-28-OMNI-SAE-RESEARCH.md` | — | governance/ops | exclude | Out of scope (tool executor, not OMNIRING) | n/a |

Totals: 66 rows covering 90 unique files (+18 byte-identical duplicates). Include / include-with-corrections rows: 33;
exclude rows: 33. Done: 33 rows (23 documents, 1 note merged into doc 03, 9 appendix logs). Todo: 0 rows.

RSX-CHEW (2026-09-29): 17 rows processed to `done` (docs 09-23, 2 appendix run logs). Row 26 skipped as chat/session-derived per J decision (4); its ideas are carried by #27 and #28. The research harness (`harness/`) ships the scripts docs 01-06 cite, with home paths made relative, and re-runs to the same verdicts. Citation check on the RSPK dossiers: 67/69 URLs resolve, 2 mis-pointed URLs fixed in the copies, no cited paper missing.

## E. Essays 07–11 (written 2026-10-01 for the Part 2 disclosure; pending J review)

| # | File | Sources | Decision | Status |
|---|---|---|---|---|
| E7 | `docs/essays/07-tool-protocol-system-primitive-substrate.md` | author's notebook (own words quoted), genr ledger counts, `_Reviews/` dates, session archive counts, disclosures | include (J review) | written |
| E8 | `docs/essays/08-from-a-point-to-a-tesseract.md` | Part 2 §2–5, §8 | include (J review) | written |
| E9 | `docs/essays/09-the-triangle-memory.md` | Part 2 §6, §8, §9 | include (J review) | written |
| E10 | `docs/essays/10-square-line-circle-triangle.md` | Part 2 §7, §8.1, §10 | include (J review) | written |
| E11 | `docs/essays/11-how-to-be-wrong-on-purpose.md` | Part 2 §9, §11; research log | include (J review) | written |
Checks: gitleaks clean on docs/essays; no home paths or emails; no third-party text reproduced (the notebook lines quoted
are the author's own); pronoun-neutral references to the author.

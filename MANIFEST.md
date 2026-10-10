# MANIFEST: OMNIRING research corpus (CC BY 4.0)

What is in this repository, what was left out, and why. Version 0.2.0. Decision key: **include** = published after cleaning;
**include-with-corrections** = published with `> Correction:` notes against later measurements; **exclude** = not published.
Every document is a cleaned copy: private paths, internal task names and raw AI chat are removed, and numbers are not changed.
The ground truth for what was measured is the omni-ring technical disclosure series (see the disclosures table below).

## A. Measured results (RING series and engine builds)

| # | Published as | What | Category | Decision | Why, and the corrections applied |
|---|---|---|---|---|---|
| 1 | `docs/01-ring1-core-cued-recall-and-capacity.md` | RING-1 core: cued recall, quantisation, eigengap and slot capacity | measured-result | include-with-corrections | Source of capacity ≈12 marks/slot; c = 0 rows need the seed-lottery correction |
| 2 | `docs/appendix/` | Appendix: RING1-CORE raw run | measured-result (log) | include | Evidence cited by #1 |
| 3 | `docs/02-ring1-check-ring.md` | RING-1 T3: the 17 check ring flags wrong settles | measured-result | include-with-corrections | 81.8% flag / 0 false alarms; c = 0 collapse explained as seed lottery |
| 4 | `docs/appendix/` | Appendix: RING1-CHECK raw run | measured-result (log) | include | Evidence cited by #3 |
| 5 | `docs/03-ring1-direct-keyed-storage.md` | RING-1: direct keyed vs bound storage, 1-bit tag | measured-result | include | 1000/1000 keyed direct read, 300/300 tagged |
| 6 | merged into `docs/03-ring1-direct-keyed-storage.md` | (merged as appendix of #5) | measured-result | include | Explains the first KILL as a brief defect (156/300 vs 300/300) |
| 7 | `docs/appendix/` | Appendix: RING1-DIRECT raw run | measured-result (log) | include | Evidence cited by #5 |
| 8 | `docs/04-ring1-disperse.md` | RING-1: dispersal vs one crowded slot | measured-result | include | Clean negative result; ≈94% recall given right slot |
| 9 | `docs/appendix/` | Appendix: RING1-DISPERSE raw run | measured-result (log) | include | Evidence for #8 |
| 10 | `docs/05-ring1-softsweep-decode-soft.md` | RING-1 SOFTSWEEP: decode_soft vs direct_probe | measured-result | include-with-corrections | Fleet v1 harness invalid, rewritten; unguided rows are seed 0 only (seed lottery) |
| 11 | `docs/06-ring3-peel-diamond-correl-tabu-fret.md` | RING-3: PEEL, DIAMOND, CORREL, TABU, FRET (+ DIAMOND-2) | measured-result | include | PEEL PASS; TABU not adopted; seed-lottery harness disclosure; 15-value corners 91% |
| 12 | `docs/appendix/` | Appendix: RING-3 raw run | measured-result (log) | include | Evidence for #11 |
| 13 | `docs/appendix/` | Appendix: RING-3 exploratory arms | measured-result (log) | include | Evidence for #11 "Exploratory arms" |
| 14 | `docs/appendix/` | Appendix: DIAMOND-2 raw run | measured-result (log) | include | Evidence for #11 DIAMOND-2 |
| 15 | `docs/07-peel-read-all-module.md` | Peeling in the engine: `omni_ring.peel.read_all` | measured-result | include | 16.65/24 true, 0/333 fakes; confidence-floor sweep |
| 16 | `docs/09-ring1-halo-two-stage-chain.md` | RING-1 T4: two-stage halo chain vs one resonator | measured-result | include | Clean pre-registered KILL; harness ships in `harness/ring1/run_halo.py` and re-runs to the same verdict |
| 17 | `docs/appendix/RING1-HALO.run.txt` | Appendix: RING1-HALO raw run | measured-result (log) | include | Evidence for #16; verbatim run log, paths made relative |
| 18 | `docs/10-ring1-smooth-fractional-phase.md` | RING-1 T2: smooth (fractional-phase) ring for "around when" | measured-result | include-with-corrections | KILL on discovery; the cue form works. Correction added: crowding, not dial resolution, was the original failure (`06-ring3-peel-diamond-correl-tabu-fret.md`) |
| 19 | `docs/appendix/RING1-SMOOTH.run.txt` | Appendix: RING1-SMOOTH raw run | measured-result (log) | include | Evidence for #18; verbatim run log, paths made relative |
| 20 | `docs/11-markstore-accumulation-and-decay.md` | Mark store: count-weighted accumulation, rehearsal counter, decay | measured-result | include | Engine build with tests; basis of disclosure §9; internal metadata stripped |
| 21 | `docs/12-seam-defining-ternary-zero.md` | Defining ternary (0,0) → phase 0 | measured-result | include | Measured defect (4,800/5,120 fabricated phases) and fix; private paths stripped |
| 22 | `docs/13-seam-full-slot-down-projection.md` | Full-slot down-projection replaces truncation | measured-result | include | Fix for the 97.5% discard at the model seam; paths stripped |
| 23 | `docs/14-seam-retracting-three-accuracy-claims.md` | Replacing three false accuracy claims with a checkable claim | review | include | Public record of the retracted "zero hallucination" claims; internal metadata stripped |
| 24 | `docs/15-modulus-set-and-check-ring-decision.md` | Modulus set {3,5,7,13}+17: correctness and choice | review | include-with-corrections | 54,600-case exhaustive check, modulus rationale; labelled as a three-lens panel decision with corrections on the seed-draw and detection-count readings |

## B. Reviews, syntheses, vision (published)

| # | Published as | What | Category | Decision | Why, and the corrections applied |
|---|---|---|---|---|---|
| 25 | `docs/08-peer-review-retrieval-and-consolidation.md` | Peer review: retrieval, consolidation, claim ledger | review | include-with-corrections | Strongest review; "retrieval unmeasured", "capacity 1,365" and D1/D2/D4 corrected |
| 27 | `docs/16-resonator-vsa-spike-decision.md` | RSPK: resonator/VSA spike decision (9-cell panel) | review | include-with-corrections | Decision + kill criteria; correction added: "don't build now" was superseded by RING measurements, and the K=32 patent argument is a design conclusion, not a legal finding |
| 28 | `docs/17-cross-field-which-ideas-change-the-design.md` | XP1: which cross-field ideas change the design | review | include-with-corrections | Rules adopted vs metaphor; internal names stripped; corrections on the ACF mask claim, the K=32 qFHRR figure and the 7.7× speedup |
| 29 | `docs/18-appendix-xp1-citation-check.md` | XP1 citation check (17/17 arXiv ids resolve) | review | include | Appendix to #28; 17/17 arXiv ids resolve, titles match topic |
| 30 | `docs/19-dossier-resonator-networks.md` | Dossier: resonator networks, factorisation in superposition | review (literature) | include-with-corrections | Literature review; citation check run at publication: 67/69 URLs resolve, 2 mis-pointed URLs fixed, no paper missing |
| 31 | `docs/20-dossier-vsa-encodings-and-capacity.md` | Dossier: VSA encodings, capacity, cleanup | review (literature) | include-with-corrections | As #30; contains first-party measurements; citation check run at publication |
| 32 | `docs/21-dossier-dynamics-and-codes.md` | Dossier: dynamics, fractals, projections, codes | review (literature) | include-with-corrections | As #30; citation check run at publication |
| 43 | `docs/22-exploration-where-verified-properties-could-apply.md` | Where verified ring properties could apply (exploration) | vision | include-with-corrections | Self-labelled exploration; corrections added: market mapping is a hypothesis, only measured properties carry, and any cascade assumption is superseded by #16 |
| 44 | `docs/23-vision-a-resonator-cortex-labelled-speculation.md` | Vision: a resonator cortex (speculation) | vision | include-with-corrections | Published as labelled speculation with corrections on every unmeasured claim: O(1) framing, MeZO, forward-shot adaptation, and any capacity beyond ≈12 marks/slot |

## C. Not published

| Kind | Candidate rows | Why not published |
|---|---|---|
| Raw AI chat or study-thread exports, and notes derived from them | 3 | Chat transcripts are not published. The ideas they carried are kept in the included reviews. |
| Literature dossiers judged out of scope or mostly metaphor | 3 | Fleet-routing context or cross-field breadth with no measured effect on the design. |
| Panel inputs and branch dossiers | 3 | Each is summarised by an included decision document; the inputs hold internal field data. |
| Process retrospectives, coverage maps, throughput metrics | 3 | Operational records, not research. |
| Vision and build-log documents | 9 | Unmeasured claims, unbuilt plans, or build logs superseded by the technical disclosures. |
| Application-integration logs, soak tests, repository-process decisions, portal audits | 12 | Out of scope for the research record. |

The 66 candidate documents (90 files, plus 18 byte-identical duplicates) split into 33 published rows and 33 rows not published.

## D. Essays (`docs/essays/`, 11 essays plus `INDEX.md`)

| Essay |
|---|
| 01 Rings around a resonator |
| 02 The jump rope |
| 03 Tuning the string |
| 04 Metaphor or mechanism |
| 05 The brain and the bookshelf |
| 06 A memory that can say "I don't know" |
| 07 Tool, protocol, system, primitive, substrate (companion of Part 2) |
| 08 From a point to a tesseract (companion of Part 2) |
| 09 The triangle memory (companion of Part 2) |
| 10 Square, line, circle, triangle (companion of Part 2) |
| 11 How to be wrong on purpose (companion of Part 2) |

Essays retell conversations in plain language; they are not transcripts. Anything not measured is marked as speculation.

## E. Guide

| File | What |
|---|---|
| `docs/guide/HYPERDIMENSIONAL-COMPUTING-AND-YOU.md` | a guide to the field; second edition 2026-10-10 (Parts 1–7, the author's words, simpler language); cites the disclosures |
| `docs/guide/GEOMETRIC-COMPUTING-AND-YOU.md` | new in 0.2.0: the axiom and law list (first written 2026-10-01, corrections of 10-03 applied), private paths removed, evidence table, credits |
| `docs/guide/MATH-CONCEPTS-AND-THANKS.md` | new in 0.2.0: the concepts index of 2026-10-03, extended to 10-09, with credits; source file names and unpublished experiment numbers removed |

## F. Technical disclosures (`docs/disclosures/`, new in 0.2.0)

Licence of these copies: CC BY 4.0. The same words ship in the code repositories under those repositories' licences.

| File | Date | What | Evidence status |
|---|---|---|---|
| `OMNI-RING-TECHNICAL-DISCLOSURE-PART-3.md` | 2026-10-01 | designed solids, 4-D cores, the source, seams, the hypervector wire; carries the 2026-10-01 correction (random-vector acceptance about 0.04 percent: the two check slots detect errors, they are not a security boundary) | harnesses and results in the omni-ring repository, `experiments/` |
| `OMNI-RING-TECHNICAL-DISCLOSURE-PART-4.md` | 2026-10-02 | the sifter as code, the decode ladder, the learning core | harnesses and results in the omni-ring repository, `experiments/part4/` |
| `OMNI-RING-TECHNICAL-DISCLOSURE-PART-5.md` | 2026-10-03 | the seed's owned ground, residue memory at scale, our own engines, fleet systems | claim-to-evidence index not yet published |
| `OMNI-RENDER-TECHNICAL-DISCLOSURE-PART-6.md` | 2026-10-04 | omni-render engine, program runtime, JS on our IR, a self-repair core | claim-to-evidence index not yet published |
| `OMNID-TECHNICAL-DISCLOSURE.md` | 2026-10-01 | omnid: front door, hardened web face, hypervector wire | some numbers labelled unsupported in the text |
| `DOCK-TECHNICAL-DISCLOSURE.md` | 2026-10-09 (DRAFT) | dock: constant-surface MCP front, abstaining tool search | every number labelled unverified in the text |
| `OMNI-RING-TECHNICAL-DISCLOSURE-PART-7.md` | 2026-10-09 | live school and growth run, cyclone array and T50 hub, Omni Web, the doctor core, the cores, provenance | numbers without a published result file are labelled (partial) / (unsupported); experiments in docs 24-44, essays 12-16 |

Parts 1 and 2 of the omni-ring series are in the omni-ring repository (`TECHNICAL-DISCLOSURE.md`, `TECHNICAL-DISCLOSURE-PART-2.md`).

## F2. Part 7 experiments and essays (new in 0.2.0)

| Path | What |
|---|---|
| `docs/24-*.md` … `docs/44-*.md` | twenty-one documents, one experiment or decision each, header table with verdict (see the README Contents) |
| `docs/essays/12-*.md` … `16-*.md` | five essays on the week of 6–9 October, in the author's words; `docs/essays/INDEX.md` lists them |
| `docs/essays/07-…` | history table extended to 2026-10-09 |
| `harness/part7/` | harnesses cited by Part 7 and docs 24–44 (287 files) |
| `docs/appendix/part7/` | result files, pre-registration extracts and summaries cited by Part 7 (832 files) |

## G. Appendix and harness

`docs/appendix/*.run.txt` are the raw run logs cited by the documents. `harness/` holds the numpy scripts behind docs 01-06 (own
licence file `harness/LICENSE.md`).
`docs/appendix/geometric-laws/` holds the 51 result files and 4 harnesses cited by the geometric booklet (home paths in two harnesses replaced by an
`OMNI_RING_PATH` variable). `docs/appendix/math-kb/mathkb.json` is the math core's knowledge base (data, CC BY 4.0), with `check_laws.py`. `docs/guide/examples/` holds the
guides' runnable examples (`ring_recipes.py` needs the public omni-ring package; `design_helpers.py` needs only Python).

## H. Not in this repository, on purpose

Review checklists and preparation logs of the corpus are working documents and are not published. The code-licence set
(`LICENSE-NONCOMMERCIAL.md`, `LICENSING.md`, `DATA-AND-SHARDS.md`, `SHARD-FORMAT.md`) and the per-repository `PROVENANCE.md` and
`TECHNICAL-DISCLOSURE.md` belong to the code repositories: this repository is documents under CC BY 4.0 plus research scripts.
A draft design disclosure for a launcher that is not released is held back until it is reviewed.

# A memory that can say "I don't know": where it might matter

| | |
|---|---|
| **Date** | 2026-09-29 (exploration written 2026-09-28) |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Written with AI assistance (Claude) from an exploration drafted by a fleet research agent during a review session (unpublished). The author reviews it before publication. |
| **Type** | essay — **speculation throughout**; the measured properties it builds on are cited |

## In one paragraph

Most AI systems answer every question. The ring memory can do something rarer: it can decline to answer, and when
it does answer, it can show that the stored record it used was not corrupted. This essay asks where that
combination might matter more than raw capability. **It is an exploration, not a plan or a product claim.**
Nothing here has been built for any of these settings, and every idea depends on questions that are still open.

## The words you need

- **Integrity.** Proof that a record read back is the one that was stored. The 17 check ring gives this for any
  single-ring slip.
- **Accuracy.** Whether the answer is the right one for the question. Integrity does not imply accuracy.
- **Abstain.** Return "no answer" instead of a guess. The engine reports a read as verified, rejected (failed the
  check) or abstained (did not converge).
- **Silent-wrong.** A wrong answer that passes every check. This is the number that matters most for any
  safety-related use.

## What is actually established

These are the properties the exploration builds on, each measured:

| Property | Result | Source |
|---|---|---|
| Single-ring slip detection | 100%, exhaustive over 54,600 cases | technical disclosure §3, §12 |
| Wrong settles flagged in crowded slots | 81.8%, 0 false alarms | `../02-ring1-check-ring.md` |
| Silent-wrong rate, cued decode, up to 10 marks | 1 in 1,200 | disclosure §12; `../05-ring1-softsweep-decode-soft.md` |
| Unguided failures | abstain rather than answer | `../05-…`; disclosure §4 |
| Peeling a crowded slot, engine build | 16.65 of 24 marks, 0 / 333 fakes | `../07-peel-read-all-module.md` |
| Forgetting | mark store with rehearsal counter and decay (built, not a benchmark) | disclosure §9 |
| Hardware | a 2019 laptop CPU, no GPU | all measured documents |

Two of these were open when the exploration was written: the silent-wrong rate had not been measured, and nothing
could decay. Both have since been addressed. The other open questions below remain.

## Speculative: settings where "I don't know" is the feature

The exploration's central argument is that the valuable thing is the combination: a local, low-power system that
refuses when it lacks a record and can prove the record it used is intact. It grouped possible uses by how much
they depend on parts not yet built.

**Useful with the memory alone (no trained model needed):**

- **Clinical and dosing checks.** Settings where a wrong answer is worse than no answer. The exploration itself
  notes a limit: a fixed interaction table does not need this system. The stronger case is a locally supplied
  formulary plus device-specific history, where no central table exists.
- **Equipment and laboratory compliance.** Interlocks, recipes and calibration records, where stored rules must
  not drift silently and stale ones must expire (which is why decay matters).
- **Audit and provenance.** Reconstructing what a system knew, when, and whether the record was intact. Marks
  can carry a time stamp through the ring clock.
- **Air-gapped environments.** No cloud, no GPU, no network egress. This is the closest fit, and the least
  dependent on unbuilt parts.

**Needing a trained model on top (not built):** edge robotics (fixed memory means no growing context and no
latency surprises), offline field service, and private clinical or legal intake.

**Plausible but weaker:** accessibility devices, energy management, tutoring.

The common thread the exploration identified: in each strong case, **a person is accountable for the output and
must be able to say what the machine based it on.** In that conversation, the ability to abstain and to prove
integrity matters more than model size.

**Where the argument stops.** None of this has been tested with users, in a regulated setting, or against the
requirements of any certification. Integrity is proven for single-ring slips; wrong settles that land on a legal
coordinate still pass (`../02-…`, `../08-peer-review-retrieval-and-consolidation.md` section 6). Whether 1 in
1,200 is acceptable depends entirely on the setting, and for many safety uses it would not be.

## What did not hold up

- **"The integrity gate means the answer is right."** It does not. Integrity and accuracy are different claims,
  and the project now states them separately (`../08-…`, claim ledger).
- **"Ready for safety-critical use."** Never claimed in the exploration, and not true. It lists what must be true
  first for every entry.

## Open questions

- **A trained model on top.** Every use beyond direct lookup needs one, and none exists.
- **Which face holds the knowledge.** Exact, verifiable coordinates (phase face) and fast, fuzzy similarity
  (ternary face) suit different uses. Nothing has decided the mix.
- **Time stamps.** Carrying *when* through the ring clock is designed (disclosure, section 3) but not measured in
  an application.
- **What abstention should do.** A refusal needs a documented fallback behaviour, not just an exit code,
  especially in control systems.

## Sources

- Measured results: `../02-ring1-check-ring.md`, `../05-ring1-softsweep-decode-soft.md`,
  `../07-peel-read-all-module.md`, `../08-peer-review-retrieval-and-consolidation.md`; the omni-ring
  `TECHNICAL-DISCLOSURE.md` (sections 3, 4, 9, 12).
- Idea lineage: an application-surface exploration written alongside the peer review (unpublished).

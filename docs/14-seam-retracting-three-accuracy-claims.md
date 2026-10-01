# Retracting three accuracy claims, and replacing them with a checkable one

| | |
|---|---|
| **Date** | 2026-09-28 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). Every number was measured on a 2019 laptop CPU (Intel i5-8365U, AVX2, no GPU); the author reviews each document before publication. |
| **Type** | review / public record of a retraction |
| **Verdict** | Three accuracy claims are retracted as measured-false; one checkable claim replaces them. |
| **Code** | the `omni-ring` engine and its test suite |

PASS


> **Read this first — the suite is currently RED and it is not this task's doing.**
> At the moment this task finished, `python3 -m pytest -q` reported **2 failed, 61 passed**. Both failures are
> `OSEAM-D2-PROJECTION`'s brand-new `test_down_projection_*` tests, written and not yet satisfied in this same
> shared tree. This task is documentation-only: it changed no executable line, and deselecting those two tests
> gives `61 passed`. Its own discriminator — the removal of the struck claims — passes outright, verified in
> *Test output* below. Nothing here was re-run until it happened to look green.

**Pillar:** Nervous System · **Lane:** opencode/big-pickle · **Seat:** dev

**Commits:** `2c4517c` (4 text files + this deliverable) and `bcff896` (2 tracked `.pyc` regenerated to match their sources — see *What changed* §6 for why that was unavoidable).

**Authority:** `reviews/2026-09-28 — OMNIRING-PEER-REVIEW-RETRIEVAL-AND-CONSOLIDATION.md` §6 "Claim ledger", which records all three claims as **FALSE** and supplies the replacement wording verbatim.

---

## What changed (file:line)

The three FALSE claims from review §6, all removed:

| # | Claim (FALSE) | Old location | Replaced with |
|---|---|---|---|
| 1 | "Zero factual hallucination" | `PROJECT_PLAN[REDACTED]:20` | Integrity-not-accuracy statement + pointer to the §6 ledger |
| 2 | "Guarantees 0% hallucination on verified discrete attractors" | `src/ring_transformer.py:219` | Docstring: clamps to a verified attractor *when one exists*; cannot distinguish a correct answer from a confidently wrong one; abstain when no attractor verifies |
| 3 | "17-check ring zero-hallucination verification gate" | `src/retrieval.py:38` | Docstring: 17-ring CRT **integrity** gate (100% single-ring slip detection, 54,600 exhaustive cases); proves the decoded address matches its codeword, not that the answer is right |

### 1. `README.md:7` + `README.md:11-16` (new section)

- Line 7 relabelled: `A Custom-Grafted 500M–1.5B Resonant Transformer Engine` →
  `A Resonant Transformer Engine … 500M–1.5B parameters is the target size, not built`. Review §6 marks this claim **NOT BUILT**; the old bullet stated it in the present tense as a shipped capability.
- **New section `## What we claim (and what we do not)`** carries the replacement claim **verbatim** from review §6:

  > Addresses and content are integrity-checked by a provable 17-ring CRT gate (100% single-ring slip detection, 54,600 exhaustive cases). Retrieval accuracy on superposition is measured, not assumed. Abstention is available at every gate. The working store is O(1) constant RAM on a 15 W CPU.

- Plus the three honest qualifiers the old README omitted: the struck claims were false / not built, and `57/57 tests passing` certifies internal self-consistency, **not learning**.

### 2. `PROJECT_PLAN[REDACTED]:18` — "500M–1.5B engine" relabelled as a target

`4. **The Resonant Transformer Engine (TARGET — NOT BUILT):**` — the size is now stated as the *target* per §3, and the shipped Tier-3 weights are named honestly: seeded pseudo-random ternary draws, reproducible but never trained. **Verified before writing:** `src/ring_transformer.py:46,113,155` use `np.random.default_rng(seed).choice([-1,0,1], …)`, i.e. the weights *are* seeded (reproducible) — an earlier draft of this line wrongly said "unseeded" and was corrected against the source.

### 3. `PROJECT_PLAN[REDACTED]:20` — accuracy claim removed

`Zero factual hallucination.` → the CRT gate is provable, retrieval accuracy on superposition is measured rather than assumed, abstention is available at every gate, and the §6 ledger is cited.

### 4. `src/retrieval.py:38-43` — docstring only

`5. 17-ring CRT integrity gate (100% single-ring slip detection, 54,600 exhaustive cases).` plus the integrity-vs-accuracy distinction and the §6 citation. Docstring lines only; no statement touched.

### 5. `src/ring_transformer.py:219-223` — docstring only

`clamp_action()` now documents what it actually does and explicitly disclaims an accuracy guarantee. **Seam care:** the cohort task OSEAM-D2-PROJECTION owns this same file (its edit is at line ~95, the `slot_dense[:d_model]` truncation). The edit here is a single exact-string replacement inside a docstring at line 219, touching no code, no imports and no formatting outside that docstring, so the two tasks do not collide.

### 6. Generated bytecode — regenerated and committed, in a separate commit

**Required for the gate to pass, and the reason the first gate run failed.** `src/__pycache__/*.pyc` are **tracked in git** in this repo, and their stale copies still contained the struck strings, so `grep -r … src` matched *binary* files even with every source string removed. Confirmed directly: `strings src/__pycache__/retrieval.cpython-312.pyc` still returned `5. 17-check ring zero-hallucination verification gate` after the source was fixed.

Regenerated with `python3 -m compileall -q src/retrieval.py src/ring_transformer.py` — **only the two modules whose docstrings this task changed**, and only in a dedicated second commit (`bcff896`), so the bytecode fix is not hidden inside the prose commit. No file was deleted (Law II).

**Why it had to be committed rather than ignored:** `src/__pycache__` was being removed and restored by something outside this task during the run (observed three times — absent at 23:58; restored from HEAD and clean; gone again within a minute, together with all of `tests/__pycache__`). The gate consequently failed *nondeterministically*: green once, then red on the next identical run, because the tracked stale blobs had been resurrected. Committing bytecode that matches its source is the only way to make this gate deterministic here. The other 16 `.pyc` were left exactly as found: recompiling them produced byte-different output, proving the committed bytecode predates this tree's current sources — pre-existing debt, not this task's to bury in a docs commit.

**Behaviour change: none.** The commits are 4 text files (2 markdown, 2 Python docstrings), this deliverable, and 2 binary `.pyc` regenerated from those sources. No executable line was added, removed or altered, and no file was deleted.

**Still owed (needs J):** a `.gitignore` (`__pycache__/`, `*.pyc`) plus `git rm -r --cached src/__pycache__ tests/__pycache__` is the real fix — untracking build output entirely. That is a **tracked-file deletion**, so it needs J's confirmation (Law II) and is deliberately not done in this docs-only task. Until then the gate is deterministic but the repo still carries bytecode it should not. Staged as open issue 2.

---

## Test output (pasted verbatim)

**Final state of the wave spec's `test_cmd` when this task finished — currently RED, and not because of this task. Stated plainly rather than re-run until it looked good:**

```
$ python3 -m pytest -q
FAILED tests/test_ring_transformer.py::test_down_projection_matrix_uses_full_slot
FAILED tests/test_ring_transformer.py::test_down_projection_distinguishes_full_slot
2 failed, 61 passed in 5.87s
[pytest exit: 1]
```

**Both failures belong to `OSEAM-D2-PROJECTION`, which is mid-TDD in this same tree.** `tests/test_ring_transformer.py` is uncommitted (its last commit is the repo's initial `049e00e`), so those two `test_down_projection_*` tests are newly written and not yet satisfied by an implementation. This task never touched that file, never touched `test_ring_transformer.py`, and changed no executable line anywhere. The same two tests were **absent** from the run at 23:58, when the suite was green — they appeared with D2's in-flight work.

Proof that the rest of the tree is green and that the two reds are D2's alone:

```
$ python3 -m pytest -q --deselect tests/test_ring_transformer.py::test_down_projection_matrix_uses_full_slot \
                             --deselect tests/test_ring_transformer.py::test_down_projection_distinguishes_full_slot
61 passed, 2 deselected in 5.46s
```

**The half of the gate that actually discriminates this task passes on its own** — and it is the half that failed at the start, when the tracked `.pyc` still held the struck strings:

```
$ grep -rniE 'zero[- ]hallucination|0% hallucination' README.md PROJECT_PLAN.md src
(no matches)
[grep exit: 1  →  no occurrences  →  PASS]
```

**On the count:** baseline at task start was `57 passed`. At the moment this task's commits were made the suite was `60 passed` (the +3 was `OSEAM-D1-TRANSCODE` adding tests to `tests/test_polymorphic[REDACTED]`). It is now 61 passed / 2 failed, the +1 and the 2 failures both from `OSEAM-D2-PROJECTION`. **This task added, removed, skipped and weakened no test** — it is documentation-only, so it cannot change the count.

---

## Open issues

1. **The test suite does not import this repo's `src/` — and sibling cohort tasks edit `src/`.** `tests/*.py` import `omni_ring.*`, which resolves through an editable install (`site-packages/omni_ring-0.1.0.pth` + `__editable___omni_ring_0_1_0_finder.py`) to `the omni-ring engine repo/omni_ring` — a **different copy of the code** from `src/` (confirmed: that copy's `retrieval.py` is 7,223 B / 17:26; this repo's is 7,636 B / 19:04). Consequence: **OSEAM-D1-TRANSCODE and OSEAM-D2-PROJECTION both edit `omniring-llm/src/*`, and a green "57 passed" will not exercise those edits.** This is the same defect class the cohort exists to fix, one layer up: the repo's own verification gate does not verify the repo's own source. Out of scope for a docs-only task, **not** fixed here. Recommend a follow-up cohort task: point the tests at `src/` (or install this repo as the package), assert the resolution in a test, then re-run D1/D2 against a gate that imports what it changes.
2. **`__pycache__` is tracked, is stale, and is being deleted mid-flight** (see "What changed" §6). A `.gitignore` + `git rm -r --cached` needs **J's confirmation** (tracked-file deletion, Law II) and is the only fix that makes the grep gate reproducible from a clean clone. Until then, the gate is green in this working tree but would fail on a fresh clone.
3. **The cohort is running three tasks in one working tree with no isolation — this already caused two real failures.** Observed live: `OSEAM-D1-TRANSCODE` editing `src/polymorphic.py`, `tests/test_polymorphic.py` and rebuilding `src/libomniring_avx2.so`; then `OSEAM-D2-PROJECTION` editing `src/ring_transformer.py` and `tests/test_ring_transformer.py`. Consequences actually hit, not hypothesised:
   - **`git add -A` swept D1's half-finished work into this task's commit.** Caught before it shipped, undone with `git reset`, and every file since staged by explicit path. **A seat in a shared cohort must never use `git add -A`.**
   - **`git commit --amend` amended *D1's* commit, not this one.** Between two commands D1 committed, so `--amend` hit their HEAD and folded 2 `.pyc` into their commit. Recovered from the reflog (`58a7c4a` restored byte-for-byte, verified by `git diff 58a7c4a 7dd2729` showing only my 2 blobs) and the bytecode shipped as its own commit on top. D1's commit is intact and their content unchanged — but this is the second time in this task that "check HEAD before you touch history" would have prevented damage.
   - **The shared tree also makes the cohort gate unrunnable while any sibling is mid-edit** (see Test output). Recommend a contract-level rule — explicit-path staging, no `--amend` in a shared tree — and per-task `git worktree` isolation as the systemic fix.
4. **`bin/done-gate` cannot verify any deliverable whose filename contains a space** — i.e. every deliverable using the fleet's own `YYYY-MM-DD — NAME.md` convention. `extract_paths` (`rust-done-gate/src/main.rs:183`) tokenises the claim with `clean.split_whitespace()`, so `/…/reviews/2026-09-28 — OSEAM-CLAIMS.md` is read as two separate paths, `…/2026-09-28` and `OSEAM-CLAIMS.md`, and both are reported missing. The file exists and is non-empty; the gate cannot see it. This affects the whole `the research corpus ` naming convention, not this task. **Workaround used here (and the one the wave spec already prescribes):** the wave's `verify` wrapper `cd the research prototype repo && {test_cmd}` passed as `--gate-cmd`, which `evaluate` treats as an executable proof that carries the claim (main.rs:755). Note `run_gate_cmd` executes with `current_dir(REPO)` = `ai-stack`, so an un-prefixed command silently runs the **whole fleet** test suite instead — that is what made the first attempt hang past 120s. A parser fix (split the claim on whitespace, then re-join filename tokens, or recognise the `—` separator) belongs to whoever owns `rust-done-gate`; recommend staging it.
5. **Review §6 rows left open, for the ledger owner:** `"1M+ combinations"` (FALSE for CRT — 1,365 verifiable) and `"~70 % milestone"` / `20 % noise → 95.7 % @ 1.75 ms` (`[?]` — re-measure). Those live in the feasibility and Tier-2 documents, not in this task's `files:` list, so they were not touched.
6. **A phrase trap worth recording:** the obvious way to document a *removed* false claim is to name it ("we no longer claim zero hallucination"). That immediately re-fails this cohort's own gate grep — it bit this task on the first draft of `README.md`. The shipped text describes the current verifiable position and cites §6 for history instead of restating the struck wording. Any future edit to these files must keep the struck phrasing out of the repo entirely (note this deliverable quotes it, which is safe only because the gate does not scan `reviews/`).

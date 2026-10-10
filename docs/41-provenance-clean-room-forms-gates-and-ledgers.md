# Provenance: four clean-room forms, data and licence gates, and hash-chained ledgers

| | |
|---|---|
| **Date** | 2026-10-09 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). The author reviews each document before publication. |
| **Type** | concepts and procedures, with the checks that exist |
| **Verdict** | Clean-room ledger chain verifies (23 entries); growth-ledger gate PASS; data guard read, not exercised; omni-spec: 1 of 7 release gates done |
| **Code** | `harness/part7/ch6-clean-room-ledger/ledger.py`, `harness/part7/ch6-data-guard/cleanguard.py`, `harness/part7/ch6-growth-controller/grow_ctl.py` |

The rule is the project's creed: **learn from everything, copy nothing** — any published idea may be studied and re-made in our own words and
code; every borrowed idea carries a citation; no third-party source text, specification text or data row is copied into a shipped artifact.
The author, 10-03: *"Let's make our ground completely sovereign."* And for the week's builds: *"follow our clean room policy as much as possible."*

*The record below is the full measured account from the technical disclosure's working chapters: every gate, every failure, with the
harness and result paths in this repository. "Section n" and "§n" inside it refer to the sections of that chapter; the matching documents here
are listed in the README. "Recorded; no saved result" marks a figure the project recorded whose output file is not published.*

## What provenance means here

Four layers, each with its own record and its own gate.

| Layer | What is recorded | Gate that uses the record |
|---|---|---|
| Code | per-component statement of what is ours, what is linked, what idea is cited; licence scan result | release checklist: licence and secret scans clean, no third-party file copied, one licence per repository |
| Specifications and ideas | the published standard or method a module is built from; the section it cites | clean-room design (section 2) |
| Data | source and licence of every training row; a marker per data directory | default-deny data guard (section 3) |
| Trained state | seeds, content hashes of checkpoints, the gate evidence and the controller decision for each growth round | hash-chained ledger and its verifier (section 5) |

The governing rule is *learn from everything, copy nothing*: any published idea may be studied and re-made in our own words and code, each borrowed idea carries
a citation (author, year, venue or the method's name), and no third-party source text, specification text or data row is copied into a shipped artifact. FIELD
PREDICTS: a clean-room process with a verifier between the two sides should let an implementer reproduce function without reproducing text; it should fail on
functions whose behaviour cannot be captured as an equation plus examples.

## Clean room by construction

The system uses four forms. They differ in what the person or program that writes the code may read; a clean-room statement for a component must say which one applies.

| Form | Who writes the code | What that writer may read | What stops a breach |
|---|---|---|---|
| A. Standard text only (2.1) | one builder | the published standard only; other implementations are run as black boxes | procedure, plus the standard's own conformance data as the test |
| B. Two-team (2.2 equations; 2.3 our own engine; and, for CSS behaviour, the gatherer / reproducer pair) | the implementer (the kernel emitter; the reproducer) | a name-free specification (equation and examples, or functional notes) and our own library; published papers as ideas. The reader reads source the code index admitted, or only behaviour | the clean-room gate (schema and leak scan) between reader and implementer; the library is built without the source file; for the kernels, a hash-chained ledger of every step |
| C. Idea level (2.4) | the author | published ideas and our own measurements | procedure only; paired with licence and secret scans |
| D. Data guard (section 3) | not a code form: it decides which data may train a model | marker files and a provider rule | default-deny guard |

In form B the *reader* does read source code (own code, or code from a permissive-licence crate), or only behaviour; the implementer never does. The clean-room
guarantee therefore lives on the implementer side and in the clean-room gate; the reader side is bound by an admission procedure (2.2, "Admission"). The gatherer / reproducer pair has the same shape: the gatherers read specifications, issues and tests, and the reproducer reads only their file.

### Build from a published standard (specification text only)

- Description: a module implements one standard from its text, cites the specification section beside the code, has no third-party dependencies, and ships the
  standard's official conformance data as its test. Other implementations may be *run* as black-box oracles in a separate process to compare outputs (the oracle
  data files used by the tests name Pillow, HarfBuzz and fontTools as the oracles); their source is never read. Third-party test suites are treated as data and are
  licence-checked before release. Where a standard has an extension that is not part of it, the extension is tagged and kept apart from the standard's scope.
- Catalogue: the catalogue of candidate standards holds 24 numbered rows (the project's manual says 23) and one row of items deliberately not built (TLS and cryptography,
  a WebAssembly runtime), with the evidence for choosing them (counts of renderer mismatches by text-bearing box, counts of crates pulled by our applications) and
  the licence terms of each specification document, to be confirmed per item before build. Catalogue:
  `docs/appendix/part7/ch6-omni-spec/results/spec-library-catalog.md`. **PARTIAL**: the mismatch and crate counts it cites come from result files that do not ship.
- Modules and their status ledger: `docs/appendix/part7/ch6-omni-spec/results/STATUS.md` (19 rows), one document per module with a "Spec:" line naming the standard and
  its sections (17 of 17 module documents have one; the lines are tabulated in `docs/appendix/part7/ch6-omni-spec/results/omni-spec-spec-lines.tsv`). The library source and the module documents are not shipped
  with this Part (omni-spec is not released); the tests ship as harness copies, and the official test data are third-party files that do not. The status ledger lags the code in one place: it lists the HTML tokenizer as not started while a
  tokenizer source file and its test exist in the project.
- Conformance, re-run. A scratch crate was assembled from the project's sources, tests and official data (the Brotli dictionary, a binary, was not available and a zero-filled
  placeholder of its size stood in, which affects only the Brotli tests) and built with rustc 1.97.0. Several oracle tests skip
  inputs that are absent and still report "ok", so the table reports the counts the tests print, not the "ok". The printed lines are kept in `docs/appendix/part7/ch6-omni-spec/results/omni-spec-rerun-summary.txt`.

| Module (standard) | Count claimed in the status ledger | Re-run | Status |
|---|---|---|---|
| Grapheme clusters (UAX #29) | 853 / 853 | 853 / 853 pass; the data file holds 853 test lines | **SUPPORTED** |
| JSON (RFC 8259) | 95 / 95 accept, 188 / 188 reject | 95 accepted, 188 rejected (35 implementation-defined cases: 11 accepted, 24 rejected); the suite directory holds 95 / 188 / 35 files | **SUPPORTED** |
| OpenType kerning + ligatures | 275 / 275 pairs, 20 / 20 strings | 275 pairs and 20 strings checked, 0 skipped (two serif fonts installed on the sandbox) | **SUPPORTED** |
| XML 1.0 | 11 / 11 tests | 11 / 11 | **SUPPORTED** |
| SHA-256 | official examples + one million "a" | 2 / 2 tests pass | **SUPPORTED** |
| Font tables | 14,094 / 14,094 rows | 12,199 rows checked and pass, 1,895 skipped (font absent) | **PARTIAL** |
| GIF | 117 / 117 | 73 checked, 44 skipped | **PARTIAL** |
| PNG | 94 / 94 | 1 checked, 93 skipped | **PARTIAL** (1 of 94) |
| DEFLATE | 49 / 49 corpus streams | 0 of 49 (streams absent); the RFC and no-panic tests pass | **unsupported** |
| Line breaking (UAX #14) | 19,346 / 19,346 | cannot run: the official test file was not available | **unsupported** |
| Bidi (UAX #9) | 770,241 + 91,707 | cannot run: the two official test files were not available | **unsupported** |
| Brotli, JPEG, lossless WebP, ZIP, OPC, XLSX, DOCX | counts in the ledger | test inputs not available; the tests stop with "not found" | **unsupported** |

  Harnesses: `harness/part7/ch6-omni-spec/{uax29,json,otshape,xml,sha256,sfnt,gif,png,inflate}.rs`; no per-run result file of the status ledger ships (the re-run lines above are the result).
  Failures: none recorded in the status ledger; the counts that could not be reproduced are listed in section 8, O9.
- Variation disclosed: where no standard exists, the fallback is the two-team design of 2.2; where a standard exists but its conformance suite is under a
  restrictive licence, the oracle is a differential run against an installed implementation.

### Two-team clean room on equations (reader, clean-room gate, implementer)

Method name: two-team clean-room design. FIELD PREDICTS: if the clean-room gate passes only function, the implementer cannot copy expression, so the output is independent
expression of the same function; the weak points are overfitting to examples, which published program-synthesis practice addresses with a counterexample loop,
and functions so small that they have one natural expression (an equal expression then proves nothing about copying).

Roles (design: `docs/appendix/part7/ch6-doctor-clean-room/prereg/doctor-bars-prereg.md`; code `harness/part7/ch6-doctor-clean-room/doctor_spec.rs`, `doctor_abc.rs`, `doctor.rs`):

| Role | Sees | Writes | Never sees |
|---|---|---|---|
| Reader (`spec`, or `blackbox` for behaviour only) | an admitted source file, or only the behaviour of a program | one specification per function output | — |
| Clean-room gate (`wall` subcommand) | the specification and the source's token set | pass or refusal with a reason | — |
| Implementer (`need`) | the specification and our own library | our code, composed from our library | the source |

- **Specification record.** One JSON row per function output with exactly these keys: `need` (a name-free identifier, `s` plus 16 hexadecimal digits), `args` (each
  `int`, `list`, `f32` or `f32list`), `equation` (one term over a fixed alphabet; arguments are `a0`, `a1`, ...), `role` (`ret`, `out` or `field`), `effects` and
  `opaque_inputs` (counts), `examples`, `holdout` and `validate` (input and output numbers only), and `provenance` with exactly `src_sha256`, `licence` and
  `reader` (`doctor-reader-<digits>`). No names, no line numbers, no spans, no comments. A behaviour-only row has no equation.
- **Admission.** Files are chosen through the code index, which refuses a file whose first 3,000 characters contain "copyright", "spdx-license-identifier" or
  "licensed under" unless they also name the authors' organisation, never indexes vendored trees by directory name, and skips any directory holding a pin file (a
  snapshot of another repository) so that forks cannot pose as donors (`harness/part7/ch6-doctor-clean-room/doctor.rs`, function `index`). In the foreign run the index
  refused the crate's main file for its header, so the readers took two other files. Two limits, read from the code: the reader command itself does not re-check
  headers (it reads whatever source list it is given), and the licence class in the record is a flag the operator passes (`--licence`, default `own`); the clean-room gate
  only checks that the declared class is one of: own, MIT, Apache-2.0, MIT OR Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, Zlib, Unlicense, CC0-1.0, black-box.
- **Clean-room gate algorithm.** (1) strict positive schema: only the keys above, exact value types, the equation tokens must be in the alphabet and form exactly one
  well-formed term (operator heads only in head position, leaves only as leaves, nothing after the root); (2) a leak scan over every string in the row, keys
  included, against the source: identifiers of three or more characters that are not alphabet symbols, comment words of four or more characters (not all digits),
  and string literals of three or more characters; single words are matched as whole words, multi-word literals as substrings; the 64-digit source hash is
  skipped, and the gate's own fixed vocabulary (keys, enumeration values, licence names, the reader identifier, alphabet tokens) is exempt because layer 1 pins it
  exactly. A row is refused with the reason. Self-test (`--seed-leaks`): every passed row is copied eight ways with one leak injected, and the gate must refuse all
  of them. The eight kinds: a source name as the identifier, as a new key, a comment word in the reader field, a literal appended to the equation, a source name as
  an equation argument, a literal as an example value, a source name as an extra provenance key, and code text in the equation.
- **Implementer.** Builds from the specification and our library only (the library is built from the other files, without the source file: 1,353 functions and 5,516
  terms in the equation-gate run), by frame-first synthesis with a counterexample loop; for equations it can instead print the equation as our own Rust (the emit
  route). The equation is also run as an oracle on 10,000 generated inputs (edge values, three random scales, lists of length 0 to 8; `spec::equiv`, called with
  10,000 in `doctor_abc.rs`); any disagreement is a counterexample fed back to the synthesiser. This equation gate was added because the example rows alone let
  overfits through (a measured failure, below).
- **Reported results** (harness: the three source files above; the program cannot be rebuilt from the files that ship, which hold no build manifest for it, so the counts
  below were recomputed from the result rows, not re-executed). Results under `docs/appendix/part7/ch6-doctor-clean-room/results/`:
  - **SUPPORTED.** Reader, own code: 32 specifications from 138 functions, of which 70 clean, from one source file (bar, from the pre-registration: at least one per three clean functions,
    that is 24); `s1-s3/spec.layout.json`.
  - **SUPPORTED.** Clean-room gate: 32 / 32 clean rows passed, 0 refused, 256 / 256 seeded leaks refused (8 kinds x 32; each kind 32 / 32); the leak scan alone, without the
    schema, caught 253 / 256; `s1-s3/wall.layout.json`. Independent check made for this section (`harness/part7/ch6-concepts/chapter6_checks.py leakwords`, output `docs/appendix/part7/ch6-doctor-clean-room/results/doctor-wall-leakword-check.txt`): the only words shared between the 32 specification rows (`s1-s3/specs.layout.wall.jsonl`) and the
    identifiers of the source file (`harness/part7/ch6-doctor-clean-room/layout.rs`) are the gate's own vocabulary (`need`, `own`, `doctor`, `ret`, `list`, `out`) and alphabet operator names (`len`, `not`, `max`,
    `min`, `range`, `and`, `filter`); no source-specific identifier appears.
  - **SUPPORTED.** Implementer, first run (examples only, no equation gate): 27 of 32 reported verified, validation 412 of 416 rows; `s1-s3/impl.layout.jsonl`.
    Second run with the equation gate: 27 / 32 built from the specification alone, validation 416 / 416 rows over 26 specifications (the 27th, the identity on its
    second argument, has no validation rows), the gate supplied counterexamples to 7 specifications; `s1-s3/impl-eq.layout.jsonl`. Of those 7, five had passed all
    16 validation rows in the first run (the overfits) and two had failed 2 of 16; the other 20 built expressions are identical in both runs. Not built (5): two
    xor-shift-multiply mixers and a 128-bit packed fold (larger than the builder reaches), one constant-index sum, one tuple-output function.
  - **SUPPORTED.** Foreign permissive crate (num-integer 0.1.46, MIT OR Apache-2.0): the two files the index admitted hold 27 functions, 14 clean; 9 specifications
    (9 / 14 = 64 %, bar 80 % **not met**); clean-room gate 9 / 9 and 72 / 72 seeded leaks refused; implementer from our library only: 7 of 9 rebuilt; `n4/wall.numint.json`,
    `n4/impl.numint.jsonl`; the denominator 14 is in `types0/spec.numint.json` (same files, a later reader run, which dropped specifications with a unit value and
    reached 7 specifications, 7 / 14 = 50 %). Black-box comparison of the two rebuilt average functions (`average_floor`, `average_ceil`) with the crate itself on
    1,000,000 integer pairs (81 edge-value pairs, the rest pseudo-random 64-bit): 0 mismatches; `n4/blackbox-check/result.txt` and its source (`harness/part7/ch4-cleanroom/n4/blackbox-check/src/main.rs`). The crate's own test
    suite was not run (its tests call generic trait methods, ours are 64-bit integer equations). The other five rebuilt functions were not compared with the crate.
  - **SUPPORTED.** Behaviour only (no source, no equation written by the reader): the driver (`harness/part7/ch6-doctor-clean-room/behaviour-driver/main.rs`) probes the crate's public interface; 9 specifications, clean-room gate 9 / 9 and
    72 / 72; implementer 1 of 9 rebuilt (`div_ceil`; 0 mismatches on 200,000 pairs including wide values); 8 not rebuilt (no candidate passed; the clean-room gate refused none,
    `refused.bb.jsonl` is empty); `n5/impl.bb3.jsonl`, `n5/div_ceil.v3.widecheck.txt`. A pipeline pass, a builder-strength failure, recorded as such. A first
    attempt had 7 candidates accepted on the examples; a wide-range oracle then found 20 mismatches in 199,595 pairs for one of them (`n5/div_ceil.widecheck.txt`)
    and the acceptance rule was tightened.
- Failures disclosed as measured: the gate's own vocabulary first matched a comment word and was refused; one-word literals matched inside keys and operator
  names until matching became whole-word with an operator exemption (the crate-wide run had 210 and 136 false refusals before it); an oracle with probes at one
  scale let a range overfit through, so probes now span several scales. These are logged in the status lines of the pre-registration (`docs/appendix/part7/ch6-doctor-clean-room/prereg/doctor-bars-prereg.md`) and in source comments (`harness/part7/ch6-doctor-clean-room/doctor_spec.rs` holds the counts 210 and 136); no result file holds
  them (**PARTIAL**).

### Two-team clean room on our own engine (GPU kernels)

The same clean-room gate and a stricter record. The reader sees only the black-box answers of our own training engine (a driver calls the engine read-only), the clean-room gate passes
function only, the implementer is a kernel emitter that works from gate-passed specifications and a template, and a parity runner compares the CPU engine (the
oracle) with the emitted kernel. Every step is appended to a hash-chained ledger carrying, per step: the author role, our licence, the engine file hash, each
source consulted (opened and read that step) or cited (idea only, document not opened) with its licence and document hash, the tool hash, the
artifact hashes, the verification result and four fixed attestations (no third-party kernel source was an input; consulted sources are no-train references;
vendor libraries are black-box oracles or linked runtimes, never code donors; reader and implementer are joined only by the clean-room gate). The attestations are the authoring agent's own statements, recorded at each step; they are not an independent audit (section 8, O7). Sources:
the ledger tool `harness/part7/ch6-clean-room-ledger/ledger.py` and the public copy of the ledger `docs/appendix/part7/ch6-clean-room-ledger/results/cleanroom-ledger.public.jsonl`. In the public copy the paths, step names, host names, repository revisions and rented-machine identifiers that the ledger's own text carried are removed and the artifact records are reduced to hashes; because those fields are hashed, the chain of the public copy was recomputed over the cleaned rows, and the original row hashes are listed beside the new ones in `docs/appendix/part7/ch6-clean-room-ledger/results/cleanroom-ledger-chain-map.tsv`.

- **SUPPORTED.** The ledger holds 23 entries (2026-10-08, two authoring agents); recomputing the chain with the ledger tool gives "23 entries, chain OK" on the original, and the recomputed chain of the public copy verifies with the same rule;
  an incident entry (third-party code seen by accident) appears 0 times. The ledger stops at 2026-10-08 19:57 UTC (last entry: the first cyclone wiring step); it holds no entry for the
  later work (routing, the training step, the replica axis, the cut and mailbox kernels, the array server), so the record is complete for the kernel loop and incomplete for the
  array (section 8, O11). **PARTIAL**: the tool's second check, that every recorded artifact still hashes as recorded, was run against the review set's files at the recorded paths: the ledger holds 213 artifact records (165 distinct paths); 65 records resolve (47 with the recorded hash, 18 edited since the record was written) and 148 do not resolve (111 paths); the 213 records are listed by hash only, with these outcomes, in `docs/appendix/part7/ch6-clean-room-ledger/results/cleanroom-artifact-hashes.tsv`.
- **Measured failure, recorded in the ledger.** For the attention backward ops, the black-box answers agreed on 8 of 136 rows for the query gradient and on 5 to 8 of 136
  for the key gradient, and the reader refused both ops; the ledger states the cause as the reader's running-error bound having no term for exponential or logarithm, and that these two ops are NOT
  certified by the clean-room gate, an open item for the doctor. An independent harness compared the engine with float64 exact arithmetic on 1,600 op-checks with 0 beyond
  1e-5 absolute (worst 1.5e-7). The entry records the harness and its result by hash; neither ships (**unsupported** here, recorded as a failure).
- The ledger also records the specification-reading station over the gatherer store (10 documents, 4,877 items extracted: 3,592 from the ECMAScript specification,
  706 from the C23 draft, 207 instruction rows, 203 builtin tables, 150 execution rules, 11 equations and 8 algorithms from papers), "never code".

### Idea-level clean room (published description only)

For ordinary components the statement is: written from published ideas and our own measurements, no third-party source file copied or adapted, runtime
dependencies listed with their licences. This is the weakest form (nothing mechanical stops reading), so it is always
paired with a licence and secret scan (section 4). The wording of the statement matters: "not from anyone's source code" (omni-ring) is a stronger claim than "no
proprietary code was referenced" (which says nothing about permissive or copyleft code). The current component provenance statements use the stronger wording only where the files support it: omni-ring (written from published ideas and measurements) and the renderer's specification ports; talon states instead exactly what it uses (the opencode configuration files, hosted model interfaces, and the Claude Code command-line interface as a subprocess).

## Data gates: only owned or permissive data may train

This extends the clean-room filter and default-deny guard already disclosed in Part 5, section 1.

- **Marker and default deny.** Walking up from a training input, the nearest marker file decides: `.clean-room.json` with `"train": true` allows; `.no-train.json`
  or no marker refuses, and a no-train marker at the same directory level wins over a clean marker. A no-train source is allowed only when the caller filters every
  row by provenance with a named row filter (one exists: the strict provider rule below), and the use is printed. A research override (an environment variable)
  reads unmarked data with a loud warning; the system manual (not shipped) states that the pod launcher refuses it and that pre-training must never set it. Token caches carry the
  provenance of the files they were built from, and training refuses a cache built from other files. Guard code `harness/part7/ch6-data-guard/cleanguard.py`
  (the training harness keeps an identical copy); the system manual (not shipped) states the launcher behaviour. **PARTIAL**: the guard is read, not exercised by a
  result; the launcher that is said to refuse the override, and the cache check, do not ship.
- **Provider rule** (`harness/part7/ch6-data-guard/clean-room`). A row is kept only if its producing model is classed *permissive*; the class is decided by first match: no model
  recorded, unknown; a name matching the restricted pattern (names of the closed-model services and of the open-weight families whose terms attach naming or
  derivative obligations), restricted; a name matching the permissive list (nemotron, glm, minimax, qwen, gpt-oss, mimo), permissive; anything else, unknown. Only
  permissive rows are kept, unknown rows are dropped, not guessed. The basis recorded for one permissive entry is a vendor's own open-model licence, not an
  OSI-approved licence, so "permissive" here means "permitted by the terms as read by the authors", checked per model card. Models under licences that attach naming
  or derivative obligations to anything trained on their outputs were found in use for three small heads; Part 5 reports those heads re-trained on rule labels from
  permissive inputs only (accuracy 0.957, 0.944 and 1.000 against majority baselines 0.389, 0.387 and 0.874) and the agreement of the rule labels with the teacher
  labels as 0.888 to 0.9985 (rule labeller per label: 0.907, 0.990, 0.888, 0.9985). **unsupported** here: the report file that holds these figures does not ship;
  they are carried in the text of the published Part 5 only. This is a licensing analysis by the authors, not legal advice, and it concerns training
  data only.
- **Generator-first corpus.** Ideas, procedures and facts are free (US copyright excludes them, 17 U.S.C. 102(b)); text of specifications and documentation is
  copyrighted, so it is read and re-expressed. Purely machine-generated output is not copyrightable in the US (Copyright Office, *Copyright and Artificial
  Intelligence, Part 2: Copyrightability*, January 2025), which is acceptable here because the data is released and no licence is enforced on generated rows;
  licences bind the generators, templates, specifications and human curation. The corpus is made by our own deterministic generators, with every example executed in
  the real toolchain (execution is the verifier, no teacher), correct by construction or by execution. Design: the author's internal licensing analysis, which does not ship.
  Designed, not measured in this section.
- **Spec gatherer** (`harness/part7/ch6-spec-gatherer/spec-gather`). A command fetches published specifications, standards and papers (never code donors) over https from a manifest the
  author approves per list, one request per document, stores each with a provenance record (SHA-256, licence, source) and a no-train marker, and `verify`
  re-checks every stored file against its record (it skips ids that have no record, i.e. not yet fetched). **PARTIAL**: the manifest ships
  (`docs/appendix/part7/ch6-spec-gatherer/results/spec-manifest.jsonl`, 18 rows: the 10 documents the system manual lists as verified, plus 8 added for the graphics work); the stored documents and
  their provenance records do not, so the "10 of 10 verified" statement of the system manual is carried by the clean-room ledger, which copies each document's licence and
  SHA-256 into the entry that consulted it (10 documents, section 2.3). The "licence" field of a gathered specification records the terms under which it may be read
  ("free to read", a vendor's documentation terms), not a right to redistribute; that is why the store is no-train and not shipped.

## Licence and release gates for code

- One licence per repository, stated in that repository's licence file. Apache-2.0 code never contains PolyForm code; PolyForm products may call Apache-2.0
  programs, not the reverse (process boundary, no shared code). Template licence files shared by the PolyForm repositories are PolyForm-only, so an Apache bundle
  must not include them. Source: the author's licence table (a proposal of 2026-10-09, awaiting approval; not shipped). Under it the daemon `omnid` is proposed as
  Apache-2.0 (decided 2026-10-09, not yet released; its proposed bundle states so in its licence boundary paragraph) and omni-spec as Apache-2.0 (not released).
- Standards-based modules carry release gates, stated in the module family's licensing note (not shipped; omni-spec is not released). State found, gate by gate:

| Gate | State found |
|---|---|
| 1 Clean-room provenance: every module cites spec sections | 17 of 17 module documents name the standard and its sections (`docs/appendix/part7/ch6-omni-spec/results/omni-spec-spec-lines.tsv`); in the source files a crude count of section citations per file ranges from 0 to 33, and three files have none (a generated table file and the OpenType and JPEG modules, whose documents carry the references); that count was made by a text search during review and no result file ships (**unsupported** as a number) |
| 2 Clone check against the best-known open implementation, with the doctor's code index | no outcome recorded anywhere (listed "to run per module") |
| 3 | not reported in this Part |
| 4 Attribution: `NOTICE` | done for the Unicode data (`docs/appendix/part7/ch6-omni-spec/results/NOTICE`); the notice does not name the MIT-licensed JSON test suite whose files and licence file sit in the test data, nor the licence file of the HTML tokenizer test directory |
| 5 Third-party test data only if redistributable | the JSON suite is MIT and its licence file is present; the HTML tokenizer test directory holds a licence and a readme only (statements about test-data directories that do not ship) |
| 6 Trademarks in crate names | names `omni-spec` / `omni-posix`; descriptive use of standard names in documents only |
| 7 Export as a fresh single-commit export | at release; not applicable yet |

  Of the seven gates, the attribution gate (4) is the only one recorded as done; omni-spec is not released.

- Component provenance statements (`PROVENANCE.md`) list what is ours, what is used and not copied, the ideas cited and, where present, the scan results. The
  release checklist requires a statement and clean scans (per-release checklist, items 3 and 5; not shipped). Scan evidence:
  ScanCode 32.5.0 (`-clpi`) over four components on 2026-09-29, with gitleaks 8.24.0 (`--no-git`, redacted): talon 65 files, cost-savers 27, agent-reliability-kit 28,
  sov-raptor 142, with no licence or copyright detection in any source file of talon, cost-savers and agent-reliability-kit, third-party licences only in the notices file of sov-raptor, and no leaks in the three that report the secret scan (summaries in `docs/appendix/part7/ch6-release-scans/results/{talon,cost-savers,agent-reliability-kit,sov-raptor}-release-scan.txt`).
  For the first public component the statement itself reports a scan over 47 files that found no third-party licence text or notices, a secret scan with none, and
  85 passing tests (2026-09-29; the published provenance statement of the omni-ring repository): **unsupported** as an independent result (no scan output for it ships), and
  stale for the 0.2.0 bundle (the current tree holds 106 files and a dry run of the release tool reports 165 tests and a clean secret scan; no new licence scan is recorded; these counts are **unsupported** here for the same reason).
  The statement says a licence scan detects licences and notices, not copied snippets. The 2026-09-29 scan results are stale for every 0.2.0 bundle: they must be re-run on the exact export tree, and a snippet-level match (ScanCode.io / matchcode or equivalent) added; until then no bundle may state that its scan is clean.

## Ledgers: how the growth of a model is made verifiable

Design (concept source: section 6, rows 5 and 7). FIELD PREDICTS: one-way hashes make a chain tamper-evident (any edit to a past row changes every later hash); fixed
seeds make a run reproducible; revealing the validity of a result without the secret behind it is the zero-knowledge idea, which the clean room mirrors (the clean-room gate
shows function, hides source). A hash chain without a signature or an outside anchor shows accidental edits, not a rewrite of the whole file by someone who
recomputes every hash.

- **Growth ledger, row format** (`harness/part7/ch6-growth-controller/grow_ctl.py`, functions `ledger_add`, `verify`, `step`, `grown`). One JSON object per line, keys
  sorted. A round row holds: `round`, `ts`, `tier`, `core_ckpt_sha256`, `eval_sha256`, `plan_sha256`, `update_sha256`, `gate` (stage, skills at the gate, the gate,
  the minimum rows per skill, the passed count per stage), `decision` (the mode used, the next mode and the `WALL` flag) and `keep` (the path of a permanent copy, or
  null). A growth row (`event: grown`) holds the round, the parameter counts before and after, how, and the core hash. Chain rule: `prev` is the previous row's
  `hash` (null for the first row); `hash` is the SHA-256 of the row serialised with keys sorted (default separators) **including `prev` and excluding `hash`**. The
  verifier re-reads every row, checks `prev` and recomputes `hash`, and re-hashes every file listed in a keep's `MANIFEST.sha256`. The clean-room ledger of 2.3 has the
  same hash rule with a genesis `prev` of 64 zeros instead of null.
- **Controller rules** (same file; parameters are environment variables with these defaults): a keep is made every 5th round, at every stage pass and after every
  growth, never pruned; the mode for the next round is *skills* until the middle stage is passed at the gate; after it, a wall gives *parameters* (grow the model,
  then back to skills); a wall again within 6 rounds of a growth with no gain since gives *generators*; after a growth the controller waits at least 3 rounds
  and up to 10 while held-out stays above its value at the growth before it counts a wall (the grace rule, row 3 of section 6). A wall is the planner's count of three consecutive rounds
  with no skill gained and the best gain under 0.01 (`harness/part7/ch6-growth-controller/school_graph.py`, `WALL_ROUNDS`, `WALL_EPS`). A stage passes only when every
  built skill of the stage holds a current held-out score at the gate (1.0 when set) on at least ceil(ln(1/delta)/epsilon) held-out rows, 300 at epsilon 0.01 and
  delta 0.05 (`GROW_MIN_ROWS`, same file; row 2 of section 6); a skill that slips falls back to the frontier. Checkpoint sets are frozen by convention: the starting
  set keeps a manifest of SHA-256 sums (`docs/appendix/part7/ch6-growth-controller/results/growth-base-MANIFEST.sha256`); 6 of its 8 listed files verify (the two weight files were not available).
- **Gate G1 (14 checks, harness `harness/part7/ch6-growth-controller/g1_controller.py`, result `docs/appendix/part7/ch6-growth-controller/results/g1.json`, bars in `docs/appendix/part7/ch6-growth-controller/prereg/growth-controller-prereg.md`).** **SUPPORTED**: 14 of 14
  true, from the frozen start state, no training. The checks: 3 on the plan (frontier is pre-K skills only; the next stage's first level is previewed; above the
  stage only review of skills already at the gate), 3 on the stage pass (24 rows at 1.0 do not pass; 300 rows at 1.0 pass and the stage advances; a keep is made),
  1 slip (a skill falling to 0.9 puts the stage back and the skill on the frontier), 4 on modes (middle passed; a wall gives parameters; after a growth,
  skills and then generators on a second wall; a keep after the growth), 1 default (with the gate unset the plan is byte-identical to the planner without this
  change) and 2 on the ledger (the chain verifies over at least 9 rows; a tampered row is detected). The saved report shows 9 rounds, skills at the gate 85 to 311, and 3
  keeps. **Re-run for this section** in a scratch tree built from the shipped harness files and the project's sources: 13 of 13 checks that can run reproduced; the default-identical check
  compares against the planner as it was before the change, which is not available, so it could not be re-run (13 of 14 reproduced, 1 not re-runnable).
- **Chain in the field.** One recorded run ledger ships: a single-row ledger from the first wiring run on a rented GPU (tier `a40-wire`,
  2026-10-09; `docs/appendix/part7/ch6-growth-controller/results/wiring-run-ledger.public.jsonl`, in which the absolute keep path of the original row was made relative and the row hash recomputed; the original and the new hash are in `docs/appendix/part7/ch6-growth-controller/results/wiring-run-ledger-chain-map.tsv`); the verifier returns `rows 1, ok` on the original. That row records 30 minimum rows,
  not 300: the wiring run did not use the default. **No growth run at the planned scale (8 or 40 harnesses) completed a round** (see Part 7, section 1; a one-harness GPU-library round did complete); the recorded ledger is a one-row wiring record, so the chain has verified a test
  state machine and one wiring row, not a model that grew.
- Limits found by reading the code, all unmeasured as problems: the `keep` path is stored as an absolute path of the machine that wrote it, so a chain verifies the
  keep manifests only where that path exists (otherwise the keep check is skipped silently); there is no signature and no outside timestamp; the first row's
  `prev` is null here and 64 zeros in the clean-room ledger.
- **Clean-room ledger:** section 2.3.

## Concepts studied and where each lands

Five texts of outside origin were supplied by the author between 2026-10-06 and 2026-10-09 (the code-grammar text first, the cut and growth texts last) as research input, with the remark that some details in them are wrong and
that the concepts and their connections to our network, not the text, were to be used. They are kept privately as reference only (not training data); none is reproduced here and none ships. The drafters audited their origin for this section (an audit by the drafters, not an independent one): what each contains, which concepts it supplied, and what in
it was set aside.

| Text (bytes) | What it contains | Concepts taken | Set aside or wrong as stated |
|---|---|---|---|
| A (4,951 bytes) | four topics at three depths each: graph theory (all-pairs max-flow, Gomory-Hu trees, guide trees, a near-quadratic bound), computability (Turing machines, halting, P versus NP), machine learning (PAC, VC dimension, gradient descent, neural tangent kernel, implicit bias, double descent), randomness and cryptography (one-way functions, interactive and probabilistically checkable proofs, zero knowledge) | rows 1, 2, 3, 4, 5 below | the rule of three, function-preserving growth and the hash chain are not in the text; they were added by the reading agent as field kin |
| B (8,505 bytes) | a toroidal network of 18 nodes in 3 levels with 8 harnesses at over 100,000 tokens per second; Gomory-Hu trees and guide trees for routing; a dual-mode controller (saturated cut: grow parameters; headroom: grow skills); Murray's law, constructal theory, max-cut and Ising analogies | rows 4, 6, 7, 8, 9, 10 | the node count (our array has 15 toroids), the token rate, the parameter budget, "guide tree" and the bound attributed to a named author (no reference given), and the statement that a minimum cut equals the ground state of the Ising model of max-cut (min cut is polynomial, max cut is NP-hard; the Ising correspondence holds for ferromagnetic couplings with fixed terminals), and "constant physical time" on annealers |
| C (8,301 bytes) | its first part is the reading agent's own checkpoint message (not outside text); its second part is an outside text on rendering a "50t" core into each toroid on demand | rows 11, 12, 13 (the concepts only) | "50t" read as thread or tera-operation (ours is the 50-ring system); the figures (100,000 tokens per second, 100 million parameters); the claim that the guide trees can be rebuilt faster than the flow |
| D (7,611 bytes) | an outside reply on abstract syntax trees for the code-equation pipeline (templates with holes, types as punctuation, execution traces, syntax-tree n-grams, data-flow chains, a billion-vector index); the text is repeated once with residue of source-link markers and ends mid-sentence | the doctor's statement layer and coverage probes (Part 7, section 4); not used in this section | the billion-vector sizing (a 1B x 1,024-bit store is 128 GB, and an exact-address index is the right tool at that size, as the response recorded) |
| E (2,475 bytes) | the reading agent's reply (a readback and a critique of an outside answer) about running a parser in the outer-ring tier of the 25-ring system | the parse-dock idea (Part 7, section 3); not used in this section | the outside answer's claim that a ring residue cannot hold a 1.9 GB tree is right but answers a question nobody asked (rings are addresses here, not storage) |

The model that produced each outside text is not identified anywhere in the records, so none is credited by name. Text-overlap check, made for this section (`harness/part7/ch6-concepts/chapter6_checks.py ngram`, counts in `docs/appendix/part7/ch6-concepts/results/outside-text-overlap-summary.txt`): no
sequence of eight consecutive words is shared between any of the five texts and (a) this section, (b) the two concept notes of the review (internal notes, not shipped); the only six-word overlaps are with the reading agent's own text (the opening
message of text C and the reply in text E). This is a lexical check, not a semantic one (section 8, O8).

Status column: M = measured here (harness and result ship), P = partial, D = designed, not measured. Origin column: A, B and C = the first three texts of the table above, S = added by
the reading agent from the field.

| # | Concept (field source) | Origin | Applied to | Status |
|---|---|---|---|---|
| 1 | Verifying is easier than solving; interactive proofs; probabilistically checkable proofs (spot checks) | A | stage gates pass on verified answers, never on loss; generators are verifiers, the model is the prover; parity checks may sample random rows | P: the stage gate reads top-1 on verified targets and is covered by G1 (section 5); sampling for parity is not built |
| 2 | PAC sample bound; the rule of three: zero errors on n independent samples bounds the true error near 3/n at 95 % | A (PAC), S (rule of three) | the gate counts independent held-out rows per skill (not positions within a row) and needs n at least ln(1/delta)/epsilon; with epsilon 0.01 and delta 0.05, ln(20)/0.01 = 299.57, so 300 rows (3/300 = 1 %) | P: constant `GROW_MIN_ROWS` = 300 in `school_graph.py`, and G1 checks that 24 rows do not pass and 300 do; effect on real stage decisions unmeasured (O2) |
| 3 | Double descent; implicit bias; neural tangent kernel; function-preserving growth | A, S (Net2Net) | a wall may be the interpolation threshold, so grow past it; new blocks are created silent (output and down projections zero) so the function is unchanged at growth; the controller's grace period after a growth ends on held-out recovery | P: the grace and mode rules are built and covered by G1; the growth tool is **not built**; a small-model check that a silent block leaves the loss identical exists as a script (not shipped) with no result file (**unsupported**) |
| 4 | All-pairs max-flow; Gomory-Hu tree (n-1 edges give every pair's min cut); min cuts of Cartesian products | A, B | (a) cuts between toroids of the array network; (b) min cuts on the skill graph weight the planner's frontier | M for (a) (below); for (b): on the pre-K stage, 85 skills, one entry skill, the minimum vertex cut is that single skill, which gates 84 others (`harness/part7/ch6-cuts/g4_cuts.py`, result `docs/appendix/part7/ch6-cuts/results/g4-cuts.json`); the planner uses the count of skills a frontier skill gates as a weight, no flow computation (`GROW_GATES_W`), effect unmeasured |
| 5 | Randomness as a resource; one-way hashes; provenance; zero knowledge | A, S (hash chain) | seeds fixed; hash-chained ledger; the clean room as the same shape | M: ledger chain verifies and a tampered row is detected (G1 checks 6; clean-room ledger 23 entries) |
| 6 | Guide trees for dynamic all-pairs max-flow | A, B | recompute cuts each round from the routing counters | P: on the product network the read replaces the tree (row 4); the GPU emits its cut table each step, 0 mismatches against Gomory-Hu at 40 and 120 harnesses on a software Vulkan device (`docs/appendix/part7/ch6-gpu-cut-tables/results/G40-llvmpipe-w262144.json`, `G120-llvmpipe-w262144.json`, fields `check.cut_*`; kernels `harness/part7/ch6-gpu-cut-tables/route.spvasm`, generator `harness/part7/ch6-gpu-cut-tables/cut_kernels.py`); not run on a hardware GPU; no per-round wiring into the controller |
| 7 | Dual-mode controller: saturated cut means grow capacity, headroom means grow skills | B | saturation as a growth input in three places (array, block, router) | P: the mode machine (skills, parameters, generators) is built and tested (G1); saturation as an input is **not built** (no saturation term in `grow_ctl.py`) |
| 8 | Murray's law: parent channel cubed equals the sum of child channels cubed (Murray 1926; constructal transport, Bejan) | B | hub sizing: (8 x 25^3)^(1/3) = 50 (the 25-ring to 50-ring choice); the next tiers give about 85.5 and 123.3 as a hypothesis to test against measured hub load | D: arithmetic only. For eight equal children the cube root of eight is 2, so the result 2 x 25 = 50 holds for any child size and cannot confirm the choice; the tiers above are a hypothesis |
| 9 | Max-cut and the Ising spin glass; annealing | B | min cut of the coupling graph as a drift monitor | D; the outside statement is corrected above; no probe run |
| 10 | Ternary arithmetic frees compute for flow work | B | the integer path rides in the same recorded step | D |
| 11 | Pressure valve: render capacity where a cut saturates, release after | C | per-toroid work sized on the GPU from the routing counters (indirect dispatch) | P: on the 15-toroid record the elastic dispatch totals 3,848 workgroups against 6,465 for a fixed worst case, all 20 checks in the record at 0 mismatches (7 of them mailbox checks) (`docs/appendix/part7/ch6-gpu-cut-tables/results/G120-llvmpipe-w262144.json`, fields `mailbox`, `check`); software Vulkan device only |
| 12 | Learning-augmented algorithms (online algorithms with predictions) | C | the planner writes the next round's curriculum, so the next round's routing can be predicted before it runs | D: the replay probe (predicted against measured counters) was not run |
| 13 | A side core trains diverted parameters and merges them back without stalling the stream | C | a delta trained in a spare replica slot, merged only if the held-out gate passes | D |

Measured part of row 4: the product-network read. Because the array network is a Cartesian product of rings, a minimum edge cut of a product graph is trivial (one
vertex) or comes from a factor's min cut (Klavzar and Spacapan, for the unweighted case; agreement on weighted loads is empirical). The routing pass already counts
items per link and per destination, so every pair's min cut is read from those counters, with sub-torus box cuts added for a saturated cluster. Harness
`harness/part7/ch6-cuts/g5_t50_cuts.py`, input recording `docs/appendix/part7/ch6-cuts/results/g4-G120-llvmpipe-w262144.json` (a recorded routing on a software Vulkan
device, 15 toroids, 45 links), result `docs/appendix/part7/ch6-cuts/results/g5-t50-cuts.json`. All of the following are **SUPPORTED** by the saved result and were reproduced by
re-running the harness on the input (every count identical; only timings differ; the re-run needs the graph library networkx):

| Case | Result (saved) |
|---|---|
| 15 toroids, recorded routing | 105 / 105 pairs equal Gomory-Hu; global minimum 27,287, the cut isolating one toroid, equal to the Gomory-Hu tree's smallest edge (`g4-cuts.json`) |
| 200 seeded dimension-order-routed fields | 200 / 200 fields with all 105 pairs exact (194 trivial-cut global minima, 6 factor-cut) |
| 105 toroids (rings 3, 5, 7) | 5,460 / 5,460 pairs exact |
| 1,155 toroids (rings 3, 5, 7, 11) | 60 / 60 sampled pairs equal exact max-flow; global minimum 2,922 equals the Stoer-Wagner value |
| hot cluster, rings 3 and 5 (a box of toroids saturated outward) | ring cuts alone exact on 85 / 100 fields (worst gap 0.556 of the capacity); with box cuts 100 / 100 |
| hot cluster, rings 3, 5, 7 | 3 / 3 with box cuts (3 / 3 with ring cuts as well) |

Timings are Python and are machine-dependent. The saved result records, at 15 toroids, 0.18 ms for the counter read and 0.09 ms for all pairs against 4.3 ms for
Gomory-Hu, with a recorded speed-up of 17.2x (the ratio field is not the quotient of those rounded figures); at 105 toroids 18.9x; at 1,155 toroids 0.71 s for the read
and 0.81 s for all pairs against an estimated 101 s for Gomory-Hu (an estimate from 60 sampled max-flows). A re-run in a different sandbox gave 11.7x, 15.2x and an
estimate of 79 s. The speed-up is therefore of the order of ten to twenty at 15 to 105 toroids and is not a constant. The box-cut enumeration grows as the product of (2^m - 1) over the
rings and was run only to 105 toroids (3 rings) and, for the hot-cluster case, to 3 rings.

FIELD PREDICTS for the designed rows: (3) test error can rise at the interpolation threshold and fall beyond it, so growing past a wall may help (Belkin et al.
2019), and a block created with zero output and down projections leaves the function unchanged by construction (Chen et al. 2016); (7), (9), (10): no published prediction
is cited, treated as exploration; (8) Murray's law predicts the branching of fluid transport networks, and no published result is cited for sizing compute hubs
by it; (12) learning-augmented algorithms are consistent when the prediction is right and robust when it is wrong (Lykouris and Vassilvitskii 2018); (13) averaging or merging
weights that start from one initialisation works while the models stay in one basin (Frankle et al. 2020, as cited in Part 7, section 1).

## Designed, not measured

Rows 3 (the growth tool), 7 (saturation input), 8 to 10, 12 and 13 of section 6; saturation as a growth signal; staggered-phase exchange through the hub; the
generator-first corpus plan of section 3 (execution-verified emitters for every language); the signature or outside anchor for the ledger; a simultaneous PAC bound
over all skills of a stage (see O2). Methods the plans borrow are cited in section 9.

## Open / unmeasured

- O1. The ledger rows hold a machine-specific path, have no signature and no outside anchor (section 5; the public copy of the wiring-run ledger carries a relative path and a recomputed hash). Needs: a decision on path-independent keeps and an
  anchoring step.
- O2. Whether the 300-row PAC rule changes any stage decision on real data (no run recorded). Also, the rule is a bound for one skill: a stage waits on all its
  skills, and a bound that holds for all 85 pre-K skills at once needs ln(85/0.05)/0.01 = 743.8, so 744 rows (derived by arithmetic here, not in the harness).
- O3. The report file behind the head-retraining and rule-agreement figures (section 3) does not ship.
- O4. The reader reaches 64 % of clean functions on the foreign crate against an 80 % bar (50 % after the later reader change); generic-trait functions are over the
  opaque ceiling. Behaviour-only builder strength: 1 of 9.
- O5. Box-cut search at 1,155 toroids; the GPU cut tables on a hardware GPU and above 15 toroids.
- O6. Closed in form, open in fact. The clean-room statement of section 9.1 now says that readers read admitted permissive source, that admission is a step of the code index and not
  a check inside the reader, and that the licence class is declared by the operator. Still open: the admission check is not made by the reader, and the operator declares the licence class; none of this is the "never read another implementation" invariant of 2.1.
- O7. No independent clean-room audit (snippet-level matching, for example a code-matching service) has been run; the licence scans reported detect licences and
  notices only; the clone check (gate 2) has no outcome; no licence scan is recorded for the omni-ring 0.2.0 bundle, omnid, dock or omni-spec.
- O8. Whether an outside text's meaning (not wording) leaked into any shipped text is unchecked beyond the lexical check of section 6.
- O9. The omni-spec counts that could not be reproduced (section 2.1): line breaking, bidi, Brotli, JPEG, lossless WebP, ZIP, OPC, XLSX, DOCX, the DEFLATE corpus,
  and the greater part of the PNG, GIF and font-table oracles, because test inputs were not available.
- O10. Independence of small rebuilt functions: the two rebuilt average functions are the well-known bit identities, so equal behaviour (compared on 1,000,000 pairs)
  says nothing about copying; the rebuilt text was not compared with the crate's text.
- O11. The clean-room ledger covers the kernel loop to 2026-10-08 19:57 UTC only (section 2.3); later array steps have no entries.
- O12. Whether the two-team form held at every step of the kernel ledger is not shown by any shipped file: the attestations are the authoring agent's own statements, no independent audit exists, and chapters 1 and 2 make no two-team claim for the kernels.

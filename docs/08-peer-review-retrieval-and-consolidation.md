# Peer review of the omniring prototype: retrieval, consolidation, claim ledger and week plan

| | |
|---|---|
| **Date** | 2026-09-28 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). Every number was measured on a 2019 laptop CPU (Intel i5-8365U, AVX2, no GPU); the author reviews each document before publication. |
| **Type** | review |
| **Verdict** | Review: architecture sound; three accuracy claims false; retrieval on superposition unmeasured at the time (since measured, see corrections) |
| **Code** | the omniring-llm research prototype (predecessor of omni-ring) and vsa-core |

**Scope.** A peer review of `the omniring-llm research prototype` (+ `vsa-core` substrate), requested by the project owner. Written by a fleet research agent.

**Method.** Direct source reads of 18 Python modules + C kernel headers; live `pytest` run; live measurement of
bind/unbind round-trip, superposition depth sweep, and transcode edge cases; review of design documents in
two unpublished AI chat exports (Claude, Gemini) containing the original design notes.

**Standard applied.** A claim without physical proof is treated as unproven. Every verdict below is tagged
`[VERIFIED]`, `[READ]` (read from source, not exercised), `[MEASURED]` (run this session), or `[?]`.

> **Note on bias-testing.** Four errors were made across earlier rounds by asserting from partial reads
> ("no unbind", "rings are just slots", "100% is only integrity", "sequential probe was the retrieval path").
> Each is corrected below. The corrections are retained as evidence of method, not hidden.

---

## 1. What is verified (do not re-litigate)

These are sound. Any future claim that contradicts them is wrong.

| Property | Evidence | Tag |
|---|---|---|
| Phase face `unbind(bind(a,b),b) == a` | measured this session, exact, 5,120-D | `[MEASURED]` |
| CRT integrity gate | coprimality ⇒ any single-ring error reconstructs outside `[0,1365)`. **54,600 cases exhaustively enumerated**, 100% detection. A *proof*, not a sample. | `[READ]` `check`, `README:54` |
| Clean-signal round-trip | **1,365 / 1,365** exact | `[MEASURED]` |
| Ternary popcount dot | 0.44 ms / 4.19 M weights, 0 float math | `[READ]` `PROJECT_PLAN` |
| Full bus scan | 145 µs SIMD | `[READ]` `README` |
| Bind / dot latency | ~35 ns / ~93 ns at 10,240-D | `[READ]` `README` |
| Majority bundling | 100% member recall at k=100, noise floor ~133 | `[READ]` `README:54` |
| Torn reads | 0 in 200,000 under concurrency | `[READ]` `README` |
| Test suite | **57 passed in 7.89 s** | `[MEASURED]` |
| Phase/ternary split | correct division: phase for composition, ternary for popcount retrieval | `[READ]` |

> **Note (added at publication).** Rows tagged `[READ]` were read from the prototype's README or source and are not re-measured in this corpus; the measured figures that the omni-ring release stands behind are listed in its technical disclosure, section 12.

**The UNVERIFIED convention in `README` should be preserved at all costs.** Four defects survived weeks behind
green tests. That scar is the most valuable artifact in the repo.

---

## 2. The most important correction: the retrieval path is the *sequential* one

**`direct_probe` (`crt`) commits each ring independently via `argmax`.** That is the
*sequential decoder* — the failure mode the design documents name explicitly.

From `design notes (Claude chat export, unpublished)`:

> **Stopping one ring at a time:** set a ring to its best guess, then move to the next. It got stuck on the wrong
> answer (0,2,1 instead of 1,3,2) and never recovered. A ring that's forced to commit while the others are
> still wrong can't find its place.
> **All rings "spinning" at once** … This decoded **all 105 values correctly**.

From `design notes (Gemini chat export, unpublished)`:

> Sequential Decoding … gets trapped in a **limit cycle** (0,2,1 instead of 1,3,2).

**Measured consequence this session.** Two-member superposition, 5 trials:

```
REJECTED (detectably ambiguous) : 4/5
returned a true member          : 0/5
VALID-BUT-WRONG                 : 1/5     bundled 7 + 300  ->  CRT returned 1197 (neither)
```

Depth sweep, 30 trials per row:

| members | rejected | **valid-but-wrong** |
|---|---|---|
| 2 | 26/30 | 2/30 |
| 5 | 29/30 | 0/30 |
| 10 | 28/30 | 2/30 |
| 20 | 27/30 | 2/30 |
| 50 | 26/30 | **4/30** |
| 100 | 29/30 | 0/30 |

**Reading.** (a) The 1,365/1,365 clean result is real but is the *clean-signal* case, where sequential
happens to work because there is nothing to disambiguate. (b) The silent-wrong rate is **0–13% and does not
decrease monotonically with data volume** (k=50 is the worst row). (c) The resonant path —
`resonator decode_soft` — exists and is the intended decoder, but **has not been measured.**

**Status: retrieval on superposition is UNMEASURED.** This is the single most load-bearing unmeasured claim
in the project.

> **Correction (added at publication).** Retrieval through `decode_soft` was measured the next day (`05-ring1-softsweep-decode-soft.md`, 300 trials per cell). With the 13 ring clamped (cued), recall of the cued target was 86–100% up to k = 100 with at most 1/300 silent-wrong decodes per cell (1 in 1,200 at k ≤ 10). At k = 5, `decode_soft` recovered a true member 300/300 vs 10/300 for `direct_probe`, which also returned 10/300 silent-wrong. Unguided decoding depends on the codebook draw (a seed lottery), so every query must carry a cue. The sequential-path figures in this section still stand as the contrast.

---

## 3. `decode_soft` — the resonant path, explained

The CRT gate answers *"is this coordinate in range?"* — integrity. It cannot answer *"which member did you
mean?"* because it commits rings independently. `decode_soft` reformulates unbinding as **iterative
estimation**:

1. **Initialize every ring to a blur** — `est[i] = cb.mean(axis=0)`, the codebook average. A superposition of
   all possibilities, not a guess. This is the "all rings spinning" state. `[READ] resonator:42`
2. **Each pass, every ring unbinds the others' current guesses** — `u = v ⊙ ∏_{j≠i} conj(e_j)`. Ring *i* asks
   "if the other factors are roughly what I now think, what does that leave for me?" `[READ] :61-64`
3. **ReLU-then-project — the load-bearing line.** `relu_a = np.maximum(a, 0); e = relu_a @ CB_i`. Only positive
   projections survive: the components consistent with the current hypothesis. **A wrong estimate produces
   negative projections, ReLU zeroes them, and that ring cannot propagate its error into the others.**
   `[READ] :70-72`
4. **Unit-modulus normalize**, repeat to `tolerance=1e-5`, early stop. `[READ] :74-87`
5. **Per-ring confidence from the eigengap** `(top1 − top2)/top1`. `[READ] :100-103`

**Why step 3 is the mechanism.** Sequential argmax has no such filter — a ring that commits early forces the
others into a bad state and the system parks in a limit cycle. ReLU is what lets a ring reject a bad estimate
and recover on the next iteration. `clamp` locks a known ring (used for the 17-check); **ACF** is the frozen
bit-flip mask that breaks residual symmetry.

**Bug found this session.** `resonator:102` computes `(top1 - top2) / top1` **unguarded**,
while `resonator_clamp:118` correctly uses `abs(top1) + 1e-9`. On a near-zero `top1` the
`decode_soft` confidence is garbage or non-finite. **Fix before measuring** — otherwise the confidence
signal being measured is broken.

---

## 4. Defects (measured, reproducible)

### D1 — `(0,0)` is undefined in the ternary→phase transcode

> **Correction (added at publication).** Fixed: `(0,0)` now maps to phase 0 (the additive identity) in both the C and Python paths; see the omni-ring technical disclosure, section 2.


`polymorphic:139-151`. The fallback LUT has **8** keys; the nine possible ternary pairs include
`(0,0)`, which is **missing**. Unmapped pairs fall through to a *position-dependent pseudorandom* value:

```python
phases[k] = lut.get(pair, (k * 5 + 7) & 0x0F)   # fabricated, not an error
```

- Reproduced: an all-zero ternary vector transcodes to **93.75 % fabricated non-zero phases.** `[MEASURED]`
- On realistic vectors (README: Nomic slot 102 = 38.5 % zero): **766 / 5,120 = 15.0 % of blocks are
  `(0,0)`** → undefined. `[MEASURED]`
- **The test excludes it by construction.** `tests/test_polymorphic` — *"Test that **active**
  ternary pairs (t0,t1) != (0,0)"* — then fills only the 8 active combinations. **57/57 never touches
  this path.** `[READ]`

**Fix.** Define `(0,0) → 0` explicitly; make the Python fallback match the C path; extend
`test_transcode_reversibility` to include `(0,0)` blocks.

### D2 — 97.5 % of bus content is discarded at the model seam

> **Correction (added at publication).** Fixed: the truncation was replaced by a fixed, seeded ±1 down-projection of the full slot; see the omni-ring technical disclosure, section 10.


`ring_transformer:95`:

```python
context += w * slot_dense[:self.d_model]    # d_model=256 of 10,240 dims
```

A **truncation**, not a projection. For a system whose premise is that the bus holds the knowledge, this
discards 97.5 % of every ring. `ActivationProjector` already exists in `bridge` and is
used for the up-direction. **Fix:** real down-projection.

### D3 — `decode_soft` eigengap unguarded (see §3)

### D4 — no weight-update path exists

> **Correction (added at publication).** A count-weighted mark store with a rehearsal-counter sidecar and decay was built after this review (omni-ring technical disclosure, section 9). It is reinforcement and forgetting, not gradient learning; the rest of this defect stands.


Grep across `src/` finds **zero** weight-update, training, Hebbian, decay, prune, or consolidation functions.
The write ABI is `bind`, `dot`, `bundle` — `vsa_kernel:38-52`. `bundle` is sum-then-threshold:
**every write to the bus is superposition, not learning.**

---

## 5. Consolidation: episodic → learned knowledge

### 5.1 Current state

**The fast store learns by frequency. There is no slow store.** A mark is reinforced by being written more
often, and because `bundle` is majority-threshold, repeatedly written marks survive — but **nothing on the
bus ever becomes stronger than a count, and nothing is ever promoted, consolidated, or solidified.**

`WORKING_0/WORKING_1` are scratchpads. `TEMPORAL` carries FPE phase rotation. `IMMUNE_FILTER` rejects.
**No slot has a learning role.** CLS's slow system is entirely absent.

### 5.2 The quantisation trap that must be designed in

Phase indices are quantised to **K=16 (4 bits) on write**. `bundle` is sum-then-threshold. Therefore
**repeated writes do not accumulate magnitude — they re-threshold.** A rehearsal count therefore **cannot
be recovered from the vector**; it requires an explicit per-slot counter.

This is the hardware form of the metadata finding: architectural state must ride *alongside* the payload,
not inside it. A sidecar counter is cheap. It does not exist today. **Any reinforcement design that assumes
"touch it enough times and it hardens" is broken at the bit level and must be specified with a counter.**

### 5.3 Proposed three-stage consolidation

Not gradient descent — counts and thresholds against the verified gate.

```
BUS SLOT          fast, count-weighted, O(1) constant RAM
  │  rehearsal count crosses threshold  AND  decodes stably across repeated probes
  ▼
SPINE             the 1,365 CRT coordinates (phase face, 17-ring verified)
  │  periodic: attest, decay, prune
  ▼
CODEBOOK          the 22-per-factor dictionaries the resonator decodes against
  │  offline, human-governed, smallest model only
  ▼
WEIGHTS           the only true gradient step
```

**Why this is safe where backprop is not.** Promotion requires two deterministic conditions: a
**rehearsal counter** and **stable decode under the 17-ring gate**. Neither is a learned judgement. If the
CRT slips, the mark does not promote. **The integrity gate becomes the promotion criterion** — which is the
one thing that makes autonomous knowledge acquisition possible without an external loss function.

**Why not backprop for geometry.** Changing the codebook invalidates every vector and address already on the
bus, and voids the CRT guarantee for the existing population. Geometry is frozen (`nomic_vsa_bridge`
uses a fixed deterministic ±1 projection, seed 42 — by design). Gradient descent over geometry trades a
verified property for an unverified one. **Counts and thresholds do not have that failure mode.**

### 5.4 Decay is the highest-value single addition

Bundling means **old marks never fade.** In a store meant to learn, that is the defect that matters most —
the bus fills monotonically with whatever arrived first and can never let go. Selective decay (per ARM,
per the design docs' "selective remembrance and decay") is a **two-line mask on the active plane** and needs
no learning machinery. **If only one thing is built from this document, build decay.**

---

## 6. Claim ledger

| Claim | Location | Verdict | Tag |
|---|---|---|---|
| "Zero factual hallucination" | `PROJECT_PLAN:6` | **FALSE** — integrity ≠ accuracy | `[MEASURED]` §2 |
| "Guarantees 0% hallucination" | `ring_transformer:219` | **FALSE** | `[READ]` |
| "17-check ring zero-hallucination verification gate" | `retrieval` | **FALSE** | `[READ]` |
| 100 % single-ring slip detection, 54,600 cases | `README:54` | **TRUE, provable** — keep, sharpen wording | `[READ]` |
| 100 % member recall at k=100 | `README:54` | **TRUE, measured** | `[READ]` |
| 57/57 tests | `README` | **TRUE** — but certifies self-consistency, **not learning** | `[MEASURED]` |
| "500M–1.5B engine" | `PROJECT_PLAN:24` | **NOT BUILT** — all weights are `rng.choice`; relabel as target | `[READ]` |
| "~70 % milestone" | feasibility doc | **`[?]`** — re-verify before citing | `[?]` |
| 20 % noise → 95.7 % @ 1.75 ms | `PROJECT_PLAN:28` | Re-measure; depends on unmeasured `decode_soft` | `[?]` |
| "1M+ combinations" | circulating | **FALSE for CRT** (1,365 verifiable). Loose state-space talk otherwise. Strike. | `[MEASURED]` |
| "< 150 µs cross-ring attention" | `README` | TRUE — but D2 truncates 97.5 % of what it reads | `[READ]` |
| 15-position dial (3×5 in one 4-bit slot) | `Claude Omni ring.txt` | **`[?]`** — doc correctly marks it untested | `[?]` |

**Replacement claim — every clause independently checkable:**

> Addresses and content are integrity-checked by a provable 17-ring CRT gate (100 % single-ring slip
> detection, 54,600 exhaustive cases). Retrieval accuracy on superposition is **measured, not assumed**.
> Abstention is available at every gate. The working store is O(1) constant RAM on a 15 W CPU.

**This is a stronger claim than "zero hallucination"** because every clause can be checked by a sceptic.
Aim for the sky; land the claim where you can stand on it.

---

## 7. Scope correction: what the head actually is

`ring_transformer` — **every weight is random**: `w_q`, `w_o`, `w_ffn1`, `w_ffn2`, `w_head` are
`rng.choice([-1,0,1], p=[.25,.5,.25])`; embeddings are `rng.standard_normal`. Defaults `d_model=256,
vocab=1000, n_layers=2, d_ffn=512`. The Week-1 graft onto SmolLM-360M has not happened. `[READ]`

**Honest one-line status: a verified associative-memory kernel with an untrained scaffold on top.** That is a
good thing to be. It is not a model, and the docs should say so in the same register they use for UNVERIFIED.

---

## 8. The eight named rings

`ring_bank:25-34` — `TEMPORAL, GOAL, ENTITY_CONTEXT, SYSTEM_STATE, ACTION_ATTRACTOR,
IMMUNE_FILTER, WORKING_0, WORKING_1`.

**They are not 8 memories of a kind. They are 8 different update laws on one 2,560-byte substrate:**

| Slot | Update law | State kind |
|---|---|---|
| `TEMPORAL` | FPE phase rotation `v_0^⊙t` | continuous, ever-advancing |
| `GOAL` | overwrite | slow |
| `ENTITY_CONTEXT` | additive bind `E₁⊗V₁ ⊕ E₂⊗V₂` | bundled structure |
| `SYSTEM_STATE` | overwrite | slow |
| `ACTION_ATTRACTOR` | quantise to verified attractor | discrete, gated |
| `IMMUNE_FILTER` | **rejection only** | negative |
| `WORKING_0/1` | scratchpad ping-pong | transient |

**Two distinct ring systems exist and must not be conflated:**

- **Named working rings (8):** a fixed control surface — 20.48 KB, L1/L2-resident. This is a *control-surface*
  size, not a memory-capacity figure.
- **CRT coprime rings (5):** `{3,5,7,13}` data + `{17}` check. **Capacity is `prod(data moduli)` = 1,365.**

> **Correction (added at publication).** 1,365 is the *address space* (the number of distinct coordinates). The measured *capacity* of one slot is about 12 marks at one cue (largest load with Wilson-99% lower bound of recall ≥ 50%; `01-ring1-core-cued-recall-and-capacity.md`).


More named rings = more *kinds* of state (new operators), not more capacity. Volume lives in the 1,000-slot
bus. Per the design docs, the named rings encode **category** factors (no natural order) while the coprime
rings are **counting** rings — best fit **time / beats / mark age**, i.e. marks that carry *when*.

---

## 9. Week plan

**Not capacity. Not rings. Not the model. Measure retrieval.** Everything else is downstream of it.

| Day | Task | Gate |
|---|---|---|
| 1 | Fix **D1** `(0,0)` transcode; extend `test_transcode_reversibility` to include `(0,0)` | round-trips; suite green |
| 1 | Fix **D3** `decode_soft` eigengap guard | no non-finite confidence |
| 1 | Fix **D2** `slot_dense[:d_model]` → real down-projection | no truncation; bus content survives |
| 2 | **Retrieval sweep through `decode_soft`** — k ∈ {2,5,10,20,50,100,200}, 30 trials; record rejected / correct / **silent-wrong** | table published |
| 3 | Sweep `min_confidence` vs silent-wrong cases | threshold chosen + justified |
| 3 | Same sweep on the **sequential** path, for contrast | quantifies what the resonator buys |
| 4 | Per-slot rehearsal counter sidecar (survives 4-bit quantise-on-write) | counter round-trips |
| 5 | **Spec only** — bus→spine promotion rule: count threshold + stable decode across probes | spec in `docs/`, no code |
| 6 | Strike the three zero-hallucination claims; publish this ledger | ledger in `reviews/` |

**Ordering rationale.** Days 1–2 unblock measurement. Day 2 decides whether the ring design delivers.
Day 4 is the cheapest real learning primitive and must precede any promotion rule. Day 5 is **spec-only
this week** — promoting unverified marks into the spine is an irreversible write, and the fleet's laws
exist to prevent exactly that. Day 6 is the honesty work that costs nothing and makes everything credible.

---

## 10. Open questions — explicitly `[?]`

1. **Does the resonant path deliver?** `decode_soft` has never been measured. `[?]` *(Answered since: yes, when cued; see `05-ring1-softsweep-decode-soft.md`.)*
2. **Does a selective scan (Mamba-style) survive bitplane packing?** RES-2 has not landed. Gates any
   recurrence proposal. `[?]`
3. **15-position dial (3×5 coprime rings in one 4-bit slot).** Cheap candidate, untested per its own doc. `[?]`
4. **Does anything learn?** No weight-update path exists. `[?]`
5. **Can 1,365 CRT coordinates scale?** Bounded by K=16; raising K is a packing change, not a ring change. `[?]`
6. **1-bit embedding accuracy loss** — the figure I have is unverified. `[?]`

---

## 11. Verdict

**The architecture is right, and right for reasons usually gotten wrong.** Most VSA work treats binding as
the primitive and retrieval as a side effect; this inverted it — phase for composition, ternary for popcount
retrieval, in the same 2,560 bytes, transcodeable. The verification discipline is genuinely unusual and
should be protected.

**Two things must change before any capability is added.** (1) The most quotable claim in the repo is the
least supportable one; replacing it with the checkable claim in §6 is strictly stronger. (2) The one claim
the whole design rests on — retrieval on superposition — is measured on the *wrong decoder* and has not
been measured on the right one.

**Both defects cluster at the same boundary: the 10,240-D bus ↔ 256-dim model seam.** That is a pattern, not
bad luck, and it is where the next review should concentrate. When the real model arrives, that is where it
breaks.

**Attempt, fail, learn is the right method** — with one requirement: every failure is measured and written
down, so the next attempt starts from knowledge rather than optimism. The `UNVERIFIED` convention is that
method. Preserve it.

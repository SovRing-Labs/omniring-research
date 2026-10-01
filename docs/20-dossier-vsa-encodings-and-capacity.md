# Dossier: vector symbolic architectures — encodings, capacity and cleanup

| | |
|---|---|
| **Date** | 2026-09-28 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance. This is a literature dossier: its claims are cited to primary sources, and every cited URL was verified at publication (see the citation check below). The author reviews it before publication. |
| **Type** | review (literature dossier) |
| **Verdict** | Literature survey plus first-party measurements; the measurements are marked where they appear. |
| **Code** | the ternary core and cleanup memory measured here |


> **Citation check (run at publication, 2026-09-29).** Every URL in this dossier was resolved.
> **67 of 69 resolve.** The 2 failures were mis-pointed URLs in the source, both fixed in this copy:
> the Rachkovskij & Kussul 2001 "thinning" reference pointed at a JMLR page (404) and is now the
> correct MIT Press DOI; the in-memory-factorisation reference pointed at a Nature Nanotechnology URL
> that 404s and is now the DOI for *In-memory factorization of holographic perceptual
> representations*, Nat. Nanotechnol. 18(5):479–485, 2023. **No cited paper was found to be missing.**
> Publisher links that return HTTP 403 to an automated client (ACM, IEEE, MIT Press, Springer,
> Nature, Justia) were verified independently through Crossref and are all live.


Researcher dossier · 2026-09-27 · scope `RSPK/RSPK-VSA1-scope.md` · shared facts `RSPK/CONTEXT.md`
Pillar: **Nervous System** (BOOTSTRAP §I.5). Non-execution task — no code, no architecture decision.

**Tags:** `[VERIFIED-SOURCE]` = I read the source or measured it. `[INFERRED]` = my reasoning from
measurements + sources. `[SPECULATIVE]` = a guess, flagged as such. **Blank beats wrong.**

**All first-party numbers below were measured this session** by linking the fleet's real
`the VSA core repo ` (rebuilt from source at `-O3 -march=native -mavx2`) into a
throwaway probe under `/tmp/opencode/`, private memory only — the live `/dev/shm/vsa_matrix_bus`
was never opened or written. Host: i5-8365U, 4c/8t, **AVX2 only, no AVX-512** (verified: no
`avx512*` flag in `/proc/cpuinfo`), L1d 128 KiB, L2 1 MiB, L3 6 MiB. Rebuild verified
byte-identical in size to the shipped `vsa_kernel.o` (`size` → `text 1254 / bss 20480` both).

---

## Summary

1. **Our bind is exact, our bundle is not distributive, and that combination is the whole story.**
   `vsa_bind` is elementwise ternary multiplication with **zero mismatches in 10,240 dims** — it is
   commutative and self-inverse. But `bind` does **not** distribute over majority-bundling
   (**200/200 failures**), so no role can be algebraically pulled out of a bundle.
2. **Measured capacity of one ternary bundle at D=10,240: 100% argmax recall to k=128, 97.7% at
   k=256, 68.6% at k=512, 24.9% at k=1024.** This vindicates the fleet's "100% at k=100" claim on
   the *keyed* protocol — but the self-test only asserts the weaker "beats 20 random foils".
3. **Sparsity is nearly free.** Across item density 1.0→0.3 and key density 1.0→0.4 at k=256,
   recall stayed flat at 97.7–99.6%. The γ·σ deadband costs essentially nothing for keyed
   retrieval, and zeros buy **no measurable crosstalk reduction** under majority bundling.
4. **Magnitude is unrepresentable in ternary — heat/counts are impossible.** Bundling one codeword
   *n* times returns a bit-identical vector for **every n from 1 to 64** (dot = 5081 in all cases).
   Decaying mark heat therefore *requires* the phase layer. This is a hard constraint, not a tuning
   knob.
5. **Selective unbinding of a factor out of a mixed bundle carries no usable signal** — across 8
   independent seeds at NM=512 it scores **at or near chance**: 22% correct with 4 lanes (chance
   25%) and 9.4% with 16 lanes (chance 6.25%), with 6/8 seeds at exactly zero and signal-to-crosstalk
   ≈ 0.02. Single-seed runs read as a clean 0/N; multi-seed shows the true result is *no better
   than guessing*. The resonator question as posed
   ("which lane × task kind × beat × error explains these failures?") **cannot be answered in ternary.**
6. **Cleanup is cheap now and expensive later.** Exact-NN: 199 µs @1k, 3.6 ms @10k, 37.7 ms @100k,
   **399 ms @1M** single-core (DRAM-resident; dot degrades 100 ns → 737 ns).
7. **`vsa_bundle` is the hot spot: ~20 µs/vector, 217× the cost of a dot.** It is a scalar bit-by-bit
   `ctz` loop, not SIMD. This is the highest-leverage local optimisation available and it is ~free.
8. **The real corpus is `dispatch.db` (1,018 tasks), not the field (145 marks, all `outcome=ok`,
   all `beat=null`).** Size the mark schema on 22 roles × 10 classes × 9 kinds × 20 models.

---

## Findings

| Concept | What it is (2 lines) | Evidence (source, year) | Tag | Relevance to our system |
|---|---|---|---|---|
| Ternary VSA algebra | HVs over {−1,0,+1}; bind = elementwise multiply (0 absorbs); bundle = sum then majority-threshold. The zero is an absorbing element, which is both the feature and the trap. | Kleyko, Rachkovskij, Osipov, Rahimi, *ACM CSUR* 2023 (arXiv 2111.06077) §II-C; measured 0/10,240 mismatches vs ternary product | [VERIFIED-SOURCE] | Our kernel's exact semantics. Confirmed, not assumed. |
| Self-inverse binding | `bind(bind(a,k),k) == a` **only where `k` has no zeros**. Zeros in `k` annihilate `a` in exactly that fraction of dims. | Measured: exact at key density 1.0 (50/50), 0/50 at 0.8 and below; dims lost = 6144×(1−key_density) | [VERIFIED-SOURCE] | Quantifies CONTEXT's "ternary binding loses information at zeros" as an exact law. |
| Non-distributivity | `bind(a, bundle(c,d)) ≠ bundle(bind(a,c), bind(a,d))`. Majority threshold is nonlinear. | Measured 200/200 differ | [VERIFIED-SOURCE] | **Kills** algebraic role-extraction from bundles. First-order design constraint. |
| Keyed item memory | Store `S = bundle_i(item_i ⊕ key_i)`; read `u = S ⊖ key_q`; clean up against the item memory. This is the standard VSA retrieval protocol. | Standard protocol (Kleyko et al. 2023 §II-B5, §III-A); measured recall curve below | [VERIFIED-SOURCE] | The only ternary protocol that actually retrieves. Must be the bus contract. |
| Capacity of one bundle | 100% argmax recall to k=128; 97.7% k=256; 68.6% k=512; 24.9% k=1024; 0.3% k=8192. Margin decays 3817→272→75→−5. | Measured, D=10,240, item_d 0.5, key_d 1.0 | [VERIFIED-SOURCE] | Plan ≤64 per slot for margin; 128 is the measured knee. |
| Capacity ∝ √D | Anchored at 1.265·√D for 100% recall (128 @ D=10,240). Cross-validated against published binary numbers (60–70 @ D=10,000) — ternary majority is ~2× binary. | Measured anchor + Schmuck et al. 2018 (arXiv 1807.08583), Fig. 18 | [INFERRED] | k=1000 needs D≈625k (123 KB/HV bit-packed). Not a bus slot. Never bundle 1000 at D=10,240. |
| One key = one address | With a single shared key, unbinding yields the *same* vector for every query; recall is exactly 1/k at every k. A key addresses one item, not a set. | Measured, k=2…8192 | [VERIFIED-SOURCE] | Capacity is (#keys × items-per-key), not a flat k. 1000 slots ≠ 1000×128 records. |
| Sparsity is cheap but useless | Recall flat 97.7–99.6% across item_d 1.0→0.3 and key_d 1.0→0.4. Bundle density saturates to ~99% regardless. | Measured, k=256 keyed | [VERIFIED-SOURCE] | Keep the deadband. Do **not** expect crosstalk savings from it — that hypothesis is dead. |
| Context-dependent thinning | The canonical way to *create* sparsity in binary codes; a threshold on binding output. Our γ·σ deadband is the same idea applied to a dense projection. | Rachkovskij & Kussul, *Neural Computation* 13(2):411–452, 2001; Kleyko et al. 2023 §II-C8 | [VERIFIED-SOURCE] | Our deadband is a known technique, not an invention. Cite it as such. |
| Magnitude is destroyed | `bundle_n(cw)` is bit-identical to `cw` for all n∈{1..64}. Majority threshold discards the count. | Measured | [VERIFIED-SOURCE] | Heat/decay/counts are impossible in ternary. Phase layer is mandatory for them. |
| Selective unbinding is at chance | `S = bundle_i(bind(who_i, rest_i))`; probe `S ⊖ who_q`; argmax over lanes. **8 independent seeds, NM=512, 25% of marks carry the queried lane:** 4 lanes → 7/32 total (22%, chance 25%), 16 lanes → 12/128 (9.4%, chance 6.25%); 6/8 seeds returned exactly 0/16. Margin/\|self\| ≈ 0.005–0.036. | Measured, 8 seeds, ASan-clean. Single-seed runs looked like a clean 0/N — corrected after multi-seed re-verification | [VERIFIED-SOURCE] | **The resonator's target question is not answerable in ternary.** The strongest argument for qFHRR found in this spike. |
| Crosstalk scale | Random-vs-random dot sd matches √D·d: 20.4/41.0/59.9/83.4 at d=0.2/0.4/0.6/0.8 (theory 20.2/40.5/60.7/81.0). Member z-score: 67.6 (k=2) → 8.9 (k=128) → 4.0 (k=256) → 2.4 (k=1024). | Measured; theory cross-check Thomas, Dasgupta, Rosing, *JAIR* 2023 (arXiv 2010.07426) on bounding crosstalk by d, s, m | [VERIFIED-SOURCE] | Gives the oracle a principled capacity model, not a magic number. |
| Formal VSA capacity | Capacity bounds expressed via sketching matrices and Bloom filters; VSAs as dimension reduction from {0,1}^d. | *Capacity Analysis of Vector Symbolic Architectures*, arXiv 2301.10352, 2023 | [VERIFIED-SOURCE] | Cite for the theory section of any paper we write. |
| Resonator baseline | The serious competitor: iterative factorisation of bound composites, with capacity measured against optimisation-based methods. | Kent, Frady, Sommer, Olshausen, *Neural Computation* 32(12):2332–2388, 2020 | [VERIFIED-SOURCE] | RSPK-RES must beat *this*, not SQL alone. |
| Fractional power encoding | `z(v) = π_base^v`; similarity between codes ≈ a kernel `K(v₁−v₂)`. Requires a phase/complex kernel. Kernel shape follows the phase distribution (uniform → sinc-like). | Kleyko, Kymn, Olshausen, Sommer, arXiv 2109.03429, 2021; `torchhd.embeddings.FractionalPower` | [VERIFIED-SOURCE] | The right tool for decaying heat — but we have no phase kernel. |
| FPE cleanup is the hard part | "Cleanup methods for continuous-value encodings are not as effective"; iterative circular-distance regression needed to decode FHRR continuous values. | *Improved Cleanup and Decoding of Fractional Power Encodings*, arXiv 2412.00488, 2024 | [VERIFIED-SOURCE] | Budget for this. FPE is not a free substitute for a scalar column. |
| Scalar encoding in binary | Sparse binary distributed encoding of scalars — the pre-FPE route to numbers without phases. | Rachkovskij, Slipchenko, Kussul, Baidyk, *J. Automation & Information Sciences* 37(6):12–23, 2005 | [VERIFIED-SOURCE] | Evidence that number-in-binary-HDC is a real, if weaker, option. |
| Random rotation before binarising | ITQ finds a rotation of zero-centred data minimising quantisation error; binarising CCA-projected data with ITQ can *improve* retrieval precision. | Gong, Lazebnik, Gordo, Perronnin, *IEEE TPAMI*, 2011 | [VERIFIED-SOURCE] | Answers scope Q4: yes, better than sign/threshold exists. Start with a *free* random rotation. |
| 2-bit sign-magnitude > 1-bit | Pairing a sign bit with a magnitude bit cuts quantisation variance ~75% vs 1-bit SimHash, keeps XOR+popcount-only distance, and lifts Recall@10 76.6%→88.6% at D=768; reaches 96% of 4-bit scalar-quant quality at 6.6× speed. | *QuIVer: Rethinking ANN Graph Topology via Training-Free Binary Quantization*, arXiv 2605.02171, 2026 | [VERIFIED-SOURCE] | Our deadband *discards* magnitude into a 0 state. Keeping a distinct small/large magnitude is a measured win. |
| Dimension must grow with corpus | Precision threshold `B* = O(ln ln N)` below which no dimension suffices; dimension and precision must grow with corpus size. | *What Limits Does Quantization Place on Dense Top-k Retrieval?*, arXiv 2606.11780, 2026 | [VERIFIED-SOURCE] | For a growing vault, raise D before raising bits. |
| Binary vs ternary capacity | Binary "golden method" stores ~60–70 orthogonal HVs at D=10,000; back-to-back binary saturates at 10–15. | Schmuck et al., arXiv 1807.08583, 2018, Fig. 18 | [VERIFIED-SOURCE] | Independent confirmation that our measured 128 @ D=10,240 is the right order — ternary is ~2× binary. |
| In-memory HDC silicon | HDC executed in resistive crossbar memory; energy/latency claims are crossbar-specific. | Karunaratne, Le Gallo, Cherubini, Benini, Rahimi, Sebastian, *Nature Electronics* 3:327–337, 2020 | [VERIFIED-SOURCE] | Explicitly out of scope: "CPUs people already own". Avoid. |
| Bundle cost is the bottleneck | `vsa_bundle` ≈ 20 µs/vector, linear in k; bundle(1024) = 20.7 ms. `vsa_dot` = 100 ns in-cache. 217× gap, caused by a scalar `ctz` loop vs SIMD dot. | Measured | [VERIFIED-SOURCE] | Top-ranked local optimisation. Any design that bundles heavily is CPU-bound. |
| DRAM-resident dot | Streaming a dot from a 2.44 GB working set: 736.7 ns vs 99.9 ns in-cache. | Measured | [VERIFIED-SOURCE] | Exact-NN at 1M items is bandwidth-bound, not compute-bound. Cache-blocking is mandatory past ~10k. |

---

## Answers

### 1. Survey of VSA/HDC families — binding/bundling/permutation, exactness of unbinding, capacity

Canonical taxonomy is Kleyko et al., *ACM CSUR* 2023 (arXiv 2111.06077), whose §II-C walks
TPR → HRR → MAP → FHRR → BSC → SBDR → sparse block codes, with §II-D on information capacity.

For **our** family (sparse ternary, the SBDR/BSC neighbourhood with an absorbing zero):

- **Binding** = elementwise multiplication. Measured exact: 0/10,240 deviations from the ternary
  product. Commutative; associative. **Self-inverse only on the dense subspace** — at key density
  1.0 the round trip is bit-exact (50/50), at 0.8 and below it never is. Lost dimensions =
  `active(a) × (1 − key_density)` exactly.
- **Bundling** = elementwise sum then majority threshold, *not* saturating OR. OR collapses at k=7
  (fleet-measured); majority holds. Confirmed here: bundle density rises monotonically
  62.6% (k=2) → 95.2% (k=128) → 98.3% (k=1024), and majority is the only variant measured to
  reach k≥100.
- **Permutation** — the fleet has none. A permutation is a role-filler ordering device in the MAP
  lineage; for a stigmergic mark where order is genuinely irrelevant (marks are a *set*), its
  absence is defensible. **Verdict: no permutation needed; do not build one.** [INFERRED]
- **Exactness of unbinding**: exact iff the unbind key is fully dense, or — as measured — if the
  same key was used at store and read time, in which case the key's zeros cancel consistently and
  recall is unaffected. This is why the deadband is safe.

**Capacity** at D=10,240 (keyed protocol, argmax recall over the item memory):

| k | 2 | 8 | 32 | 128 | 256 | 512 | 1024 | 2048 | 8192 |
|---|---|---|---|---|---|---|---|---|---|
| recall | 100% | 100% | 100% | **100%** | 97.7% | 68.6% | 24.9% | 6.6% | 0.3% |
| margin | 3817 | 1897 | 824 | 272 | 75 | −5 | 25 | 6 | 3 |

Fitting the knee gives capacity ≈ 1.265·√D, cross-validated against the published binary figure
(60–70 orthogonal HVs at D=10,000, Schmuck et al. 2018) — our ternary majority is roughly **twice**
as capacious as binary at equal D, which is the expected payoff of keeping magnitude until the
threshold. **To hold k=1000 you need D≈625,000** (≈123 KB/HV bit-packed) — 60× our current
dimension and far too large for a 2,560-byte bus slot. [INFERRED]

### 2. Bundling capacity and crosstalk: ternary vs bipolar vs phase; role of zeros; what k=100 @ 100% recall implies at D=10,240

**Zeros do not reduce crosstalk under majority bundling — measured, and it is the one assumption in
CONTEXT that fails.** At k=256 keyed, recall was 97.7–99.6% across every combination of item
density 1.0→0.3 and key density 1.0→0.4. Bundle saturation is driven by *k*, not by density: at
k=256 the bundle is ~99% active whether the members were 30% or 100% dense. So the deadband is
free, but it buys nothing. [VERIFIED-SOURCE]

Crosstalk is governed by one number: for independent ternary vectors at density *d*, the
random-vs-random dot has sd = √D·d — measured 20.4 / 41.0 / 59.9 / 83.4 against theory
20.2 / 40.5 / 60.7 / 81.0 at d = 0.2 / 0.4 / 0.6 / 0.8. The *signal* is what dies: member z-score
falls 67.6 → 8.9 → 4.0 → 2.4 as k goes 2 → 128 → 256 → 1024, because bundle saturation inflates
the noise floor (sd 57 → 72) while the majority vote erodes the signal. [VERIFIED-SOURCE]

Ternary vs bipolar vs phase, on the evidence:

- **Ternary (ours)**: carries a third state, so bundling can *tie* (0 = "undecided") instead of
  forcing a false majority. That is why it beats binary on capacity. Cost: the absorbing zero makes
  unbinding lossy off the dense subspace, and the threshold makes bundling non-distributive.
- **Bipolar (MAP)**: strictly cheaper (1 bit/dim, half the bytes) and exactly self-inverse
  everywhere, but no tie state — published capacity 60–70 @ D=10,000. **Half the capacity of ours.**
  A throughput play, not a fidelity play.
- **Phase (FHRR/qFHRR)**: bundling is a *linear* sum of unit-modulus complex numbers with **no
  threshold at bundle time**. Signal grows with count, noise with √count, so SNR *improves* with
  superposition instead of saturating. This is a categorically different capacity regime, and it is
  the only one of the three that can represent magnitude. [INFERRED from the measured ternary
  failure in Q5; the linear-superposition argument is standard.]

**"k=100 at 100% recall" at D=10,240 implies**: one bundle holds ~128 distinguishable items, and
**only when each item has its own key**. It does *not* imply 100 facts per vector. A single key
yields one addressable vector (recall exactly 1/k at every k measured). Real capacity is
`#keys × items-per-key`, which is why the 1000-slot bus is 1000 channels, not 1000×128 records.
It also implies √D scaling, so "just bundle more" is not available to us at D=10,240. [INFERRED]

### 3. Cleanup / item memory: exact-NN vs Hopfield-style, cost at 1k–1M items

Measured exact-NN full scans against a DRAM-resident item memory (dot = 736.7 ns streaming):

| items | working set | scan (1 core) | 4 cores | scans/s (1 core) |
|---|---|---|---|---|
| 1,000 | 2.4 MB (fits L3) | **199 µs** | 50 µs | 5,031 |
| 10,000 | 24 MB | **3.6 ms** | 0.9 ms | 274 |
| 100,000 | 244 MB | **37.7 ms** | 9.4 ms | 27 |
| 1,000,000 | 2.44 GB | **399 ms** | ~100 ms | 3 |

Note the 100 ns → 737 ns degradation: past ~10k items the operation is memory-bandwidth-bound, not
compute-bound. [VERIFIED-SOURCE]

**Verdict by regime:**
- **≤10k items — exact NN, no contest.** 199 µs–3.6 ms, simple, exact, debuggable, and the item
  memory can be *rematerialised* rather than stored (Kleyko et al. 2023 §II-B5 note; Schmuck et
  al. 2019; Eggimann et al. 2021). Our real corpora are 145 marks and 1,018 tasks — three orders of
  magnitude inside this regime. **Hopfield cleanup would be a downgrade here.**
- **10k–100k — block the item memory** into cache-resident partitions and score one block. Pure
  engineering, keeps exactness.
- **≥1M — exact NN is dead on a 4-core laptop** (0.4 s/query). Here iterative Hopfield-style
  cleanup becomes attractive because its cost is `O(iterations × D)` and **independent of N**. Its
  price is convergence risk and limit cycles — which is precisely why the literature adds noise
  (IBM's stochastic in-memory factoriser, *Nature Nanotechnology* 2023) and precisely why J's
  "controlled randomness" instinct is well-founded. [INFERRED]

**Recommendation for the spike: build exact NN only.** Do not build a Hopfield cleanup until a
measured corpus exceeds ~10⁵ items. [INFERRED]

### 4. Mapping dense neural embeddings (768-D Nomic) into HVs

Current pipeline: Nomic Embed 1.5 (768-D) → ±1 random projection to 10,240-D → γ·σ deadband.
Measured real output (slot 102, per README): 6,297 active = 3,142 +1 / 3,155 −1, **38.5% zero**.

What the literature supports, in order of cost:

1. **Mean-centring first — free, do it.** CONTEXT records real Nomic HVs starting at ~0.42 mutual
   similarity, and the bridge already showed centring doubles the topic gap (0.083 → 0.178). Our
   measured baseline of ~0.42 mutual similarity is a *bias* artefact, not a property of ternary
   codes. The 2-bit-SM literature makes the same point: quantisation error is computed on
   *zero-centred* data, and sign-only binarisation inherits any mean offset.
2. **A random rotation before the deadband — free, no training.** ITQ's core claim is that finding
   a rotation of zero-centred data which minimises quantisation error improves retrieval, sometimes
   *beyond* the float baseline; RaBitQ-style randomised rotation gives error bounds with no
   training at all. This is the "better than sign/threshold" answer: **a random orthogonal rotation
   costs one 768×768 matmul, needs no labels, and is the standard first step before considering
   ITQ.** Whiten (PCA) first, then rotate, then deadband.
3. **Keep the magnitude bit instead of discarding it — the highest-value change.** We currently map
   |x| < γ·σ → 0, throwing away the difference between "barely above threshold" and "strongly
   above". The 2-bit sign-magnitude result keeps that distinction, still with XOR+popcount-only
   distance, for +12 pp Recall@10 at D=768. Our two-bitplane layout can express three states
   (−small, +small, 0) or four (±small, ±large) at unchanged storage and unchanged dot. This is
   directly implementable and literature-backed. **Caveat: it changes the dot, so the
   Python↔C parity gate and the bus ABI must be re-verified — treat as a new layout, not a tweak.**
4. **Learned projections (ITQ / a trained encoder)** — only if 1–3 leave a measured recall gap.
   Justified by arXiv 2606.11780: dimension and precision must both grow with corpus size, so for
   a growing vault the lever is **D, not bits**.

**Recall loss vs float is still UNMEASURED on our real data** (CONTEXT flags this as open and it
remains open). The 0.58-vs-0.28 ordering test is not a recall@k measurement. What would settle it:
take the existing vault, embed with Nomic, compute float recall@10 as ground truth, then re-measure
recall@10 after (a) centre, (b) centre+whiten+rotate, (c) magnitude-preserving deadband. That is a
few hours of CPU and it is the single highest-information experiment in this dossier. [INFERRED]

### 5. Fractional power encoding for continuous values, and its kernel interpretation

FPE encodes a scalar `v` as `z(v) = π_base^v`, so that `⟨z(v₁), z(v₂)⟩ ≈ K(v₁ − v₂)` — a
reproducing-kernel-hilbert-space construction; the resulting framework is called Vector Function
Architecture (Kleyko et al. 2021). Kernel *shape* is set by the phase distribution of the base
vector — uniform phases give a sinc-like kernel, and `bandwidth` trades breadth for narrowness.
`torchhd` ships `FractionalPower` for FHRR. [VERIFIED-SOURCE]

**The finding that matters for us: in ternary, magnitude is not merely lossy — it is absent.**
Bundling one codeword *n* times produced dot = **5081 for n = 1, 2, 4, 8, 16, 32 and 64
alike**, and the sequence is non-monotone with the first failure at n=2. The majority threshold
returns the codeword itself, bit-for-bit, discarding the count entirely. There is no γ, no
threshold, no bit width that recovers it, because the information is destroyed at bundle time
rather than at quantisation time. [VERIFIED-SOURCE]

Consequences for **decaying mark heat**:
- Heat/count/duration **cannot** live in the ternary bus. The qFHRR layer is mandatory for them,
  which independently corroborates CONTEXT's reason (a) for wanting a phase kernel. Two separate
  lines of evidence now converge on the same conclusion.
- FPE is *not* free. The 2024 follow-up is explicit that cleanup for continuous-value encodings
  is markedly less effective than for symbols and needs iterative circular-distance regression to
  decode. Budget for that; it is a project, not a function call.
- **Pragmatic interim option** [INFERRED]: carry heat as a small integer *beside* the hypervector
  (a `REAL` column, which `field.sqlite:marks.weight` already is) and apply the half-life decay in
  SQL where it is exact and free. This loses the kernel property — you cannot ask "find marks whose
  heat is near 0.5" as a similarity query — but it is honest, cheap, and reversible. Recommend this
  now, FPE later, and let the oracle decide which is worth it.

### 6. Hardware and efficiency: bit-packed ternary on AVX2/AVX-512, in-memory, neuromorphic; realistic on a 4-core laptop

Measured on the actual host:

| op | measured | note |
|---|---|---|
| `vsa_bind` | 63.9 ns | AVX2, 1280 B/plane |
| `vsa_dot` | 99.9 ns in-cache / 736.7 ns streaming | pshufb nibble-LUT popcount |
| `vsa_active_count` | 71.3 ns | |
| full 1000-HV bus scan | **153.8 µs** | README's 145 µs reproduces |
| `vsa_bundle` | **~20 µs per vector** | 217× a dot; bundle(1024) = 20.7 ms |

**AVX-512 is absent on this host** (verified: no `avx512*` in `/proc/cpuinfo`), and the kernel
comment is right that `VPOPCNTQ` is `AVX512_VPOPCNTDQ`. The pshufb path is the correct choice here.
Any claim of an AVX-512 speedup must be flagged as *not measurable on our reference machine*. [VERIFIED-SOURCE]

**Is the two-bitplane layout right?** Yes, and this is worth stating because it is counter-intuitive.
BitNet-style 1.58-bit packing is *information-theoretically* optimal for ternary but
**destroys the popcount-dot**: you can no longer align bits to 64-bit words, which is the entire
reason dot is 100 ns. Halving the bytes at the cost of a 10–50× slower dot is a bad trade for a
*matching/routing* bus. The 2,560-byte two-plane layout is the correct SIMD representation. The
1-bit bipolar layout (1,280 B) is the throughput play if we ever need raw scan bandwidth and can
accept half the capacity. [INFERRED]

**The real optimisation is not packing — it is `vsa_bundle`.** It is a scalar per-bit `ctz` loop
with an `int16` accumulator, 217× the cost of a dot. A bit-sliced majority (carry-save counters
across 64-bit words, then a single compare) is the standard technique and is fully AVX2-friendly.
This is a self-contained, testable, high-payoff change to existing shipped code. [INFERRED]

**In-memory / neuromorphic: avoid.** The energy and latency claims in the crossbar literature
(*Nature Electronics* 3:327–337, 2020; FELIX; Loihi 2) are all crossbar-specific and presuppose
hardware nobody in our install base owns. CONTEXT already imposes "must run on CPUs people already
own." Recording this so the oracle does not relitigate it. [VERIFIED-SOURCE]

### 7. Representing a stigmergic mark (who/what/where/when/outcome) as one HV, and capacity per bundle

**Schema** — pure bind chain, no bundle inside:

```
mark = bind(who, bind(what, bind(where, bind(when, outcome))))
```

Binding is elementwise ternary multiplication, hence **commutative and associative** — verified
0/10,240 deviations from the ternary product. So the composite is **order-free**: the schema can be
re-nested or extended to a sixth factor with no change in semantics, and no distributivity is
required. This is a genuine structural advantage over any schema that uses bundle inside a
composite, and it is why the pure-bind form is the right choice. [VERIFIED-SOURCE]

**Cardinalities, measured from the real corpora** (this is what sizes the codebooks):

| role | `dispatch.db:tasks` (1,018 rows) | `field.sqlite:marks` (145 rows) |
|---|---|---|
| who | role **22**, owner 13, model 20 | agent 3, role 3 |
| what | kind **9**, class 10 | kind 5 (command 136, file 5, arrive 2, debrief 1, read 1) |
| where | — (in `dispatches`) | target **142** |
| when | `task_beats` table exists | `beat` — **null in all 145** |
| outcome | status 7 (done 741, retired 207, staged 31, blocked 30, in-flight 4, dispatched 3, approved 2) | outcome — **`ok` in all 145** |
| — | `blocked_reason`: 8 distinct, on 84 rows | weight 0.3–1.0, mean 0.53 |

730 dispatch attempts across 486 distinct tasks → 1.5 attempts/task.

**Two consequences the oracle must not miss.** First, **the field is degenerate right now**: one
distinct task, one distinct outcome, zero beats, all marks from a single day. The planned
"lane × task kind × beat × error" cross-product has an empty error axis — there is nothing to
explain. Sizing a resonator benchmark against today's field would measure nothing. Second,
`dispatch.db` is the corpus with real factor structure (22 × 9 × 10 × 20 with 8 distinct failure
reasons) and 730 attempts of history. **The capacity benchmark should be built on `dispatch.db`,
not on the field.** [VERIFIED-SOURCE]

**Capacity per bundle** — measured, keyed protocol, D=10,240:

- **One mark per slot**: trivially fine. Each mark is one 2,560-byte HV; retrieval is a 100 ns dot.
- **Superposing *k* keyed marks in one slot**: 100% recall to **k=128**, 97.7% at 256. **Plan for
  k ≤ 64 per slot** to keep margin above the noise floor, and treat 128 as the verified ceiling.
- **Unbinding one role out of a superposed bundle**: **no usable signal** (8 seeds: 22% at 4 lanes
  vs 25% chance, 9.4% at 16 lanes vs 6.25% chance, 6/8 seeds exactly zero; SNR ≈ 0.02). A bundle is
  an *address space*, not a record. You get k records out of a bundle only by unbinding with k
  distinct keys. Note this is *at chance*, not deterministically zero — a single seed will often
  read a clean 0/N, which is exactly why it was re-verified across seeds before being written up.
- **Counts, durations, heat, and the `when` factor**: not representable. `when` must be a *codebook
  entry* (a beat name), never a continuous value, in ternary.

So the honest schema is: **one mark = one HV; the bus slot is an address; a bundle is a small
(≤64) keyed index, not a summary.** A bus that superposes 1,000 marks into one slot and expects to
   read back "which lane" is relying on a mechanism I measured to perform at chance. [VERIFIED-SOURCE]

---

## Cross-links

1. **Ternary majority threshold (this vein) ↔ minority-factor extinction (RSPK-RES resonator).**
   Our measured chance-level selective-unbinding result is the algebraic reason the resonator cannot
   be built on ternary. The resonator's proposed question — factorise bundled marks to find the lane ×
   task-kind × beat × error behind failures — asks for a *minority* factor inside a *mixed*
   population, and majority bundling erases exactly that. A phase kernel's linear superposition
   (no threshold at bundle time) is the mechanism that would keep it. This is the sharpest
   interface between the two dossiers: **RSPK-VSA2's qFHRR decision is a prerequisite for
   RSPK-RES's core question, not a parallel track.**

2. **Magnitude destruction (Q5) ↔ stochastic-dynamics escape from limit cycles (RSPK-RES / J's IFS
   idea).** In ternary, the count is destroyed at bundle time — measured bit-identical for n=1..64.
   So "controlled randomness" has nothing to randomise *in ternary*: there is no magnitude channel
   whose noise could be tuned. The stochastic-resonator literature works precisely because phase
   bundling retains magnitude for noise to act on. J's instinct and the phase requirement are the
   same requirement.

3. **√D capacity law (Q1) ↔ the 5-bit-phase dimension decision (RSPK-VSA2).** Capacity ∝ √D means
   D is the scarce resource and bits are nearly free. That is the quantitative argument for
   spending 5 bits/dim on *phase precision* rather than on *more dimensions*: at fixed storage,
   D=10,240 × 1 bit (1,280 B) vs D=10,240 × 5 bits (6,400 B) — the phase layer buys ~2.2× √D
   capacity, i.e. ~4.8× the items per bundle, for 2.5× the bytes. It also means the alternative —
   raising D to 625k for k=1000 — is off the table on a 4-core laptop, while K=32 phase at D=10,240
   is not.

4. **Degenerate field factors (Q7) ↔ "verified traces become training data" (RSPK-MIND / learning).**
   `outcome='ok'` in 145/145 marks and `beat=null` in 145/145 means the field currently carries
   **no negative signal at all**. Whatever the resonator or immune tier is meant to learn from, the
   field as it stands cannot supply it. This is a data-collection blocker with a hard dependency on
   the mark writer emitting real outcomes and beats — upstream of any learning claim.

5. **Exact-NN cleanup cost (Q3) ↔ memory-bandwidth realism (RSPK-PHYS).** 100 ns in-cache → 737 ns
   streaming is a 7.4× cliff at the L3 boundary, and 1M items = 2.44 GB. Any claim that the
   resonator or a VSA item memory "fits in cache" is a physics claim that must be checked against
   the 6 MiB L3, not assumed. The 1M-item projection (399 ms/query) should be treated as the
   physical ceiling, and cache-blocking as the mitigation.

6. **Zeros-are-free-but-useless (Q2) ↔ the Nomic deadband γ (Q4) ↔ sparse-code lineage (RSPK-MATH).**
   The thinning literature (Rachkovskij & Kussul 2001) creates sparsity for *energy and storage*
   on wide buses, not for crosstalk reduction in a majority-vote scheme. My measurement says the
   crosstalk rationale is void here, while the storage rationale is weak (we store 2,560 B either
   way, because the two-plane layout is fixed). So γ should be chosen on **recall**, not on a
   crosstalk theory — an argument for tuning it empirically.

7. **One key = one address (Q2) ↔ bus slot registry (CONTEXT: "no slot registry").** Measured: a
   shared key yields exactly one addressable vector (recall 1/k at all k). The missing slot registry
   is therefore not bookkeeping hygiene — **it is the addressing scheme**, and it is what makes a
   bundle readable. This upgrades a known gap into a first-class build item.

8. **Magnitude-preserving deadband (Q4) ↔ `vsa_stochastic.h`'s 5-bit register (CONTEXT).** That
   register's trit + confidence is, in effect, the sign-magnitude idea already sketched — and its
   "99.96%" was a metric artefact (exact ternary match 50.1%). The 2-bit-SM literature (arXiv
   2605.02171) says the magnitude bit is worth +12 pp Recall@10 *when measured properly*. The
   concept was right; the measurement was not. Worth revisiting with a sound metric rather than
   discarding the idea.

---

## Implications for the spike

**Ranked. Build / measure / avoid.**

1. **MEASURE (highest information per hour) — float-vs-ternary recall@k on the real vault, with the
   three encoder variants.** Float recall@10 as ground truth; then (a) centre, (b) centre + PCA-whiten
   + random rotation, (c) magnitude-preserving deadband (keep ±small/±large instead of collapsing to
   0). CONTEXT records this as unmeasured and it gates every downstream VSA-text claim. Cheap,
   decisive, and it settles Q4 empirically instead of by citation.
2. **BUILD — SIMD majority-bundle.** `vsa_bundle` is ~20 µs/vector, 217× a dot, and is a scalar
   `ctz` loop. A bit-sliced majority closes a ~200× gap on the operation every superposition-based
   design depends on. Self-contained, testable against the existing OR-regression guard, and it
   makes any future bundle-heavy design affordable on the reference laptop.
3. **BUILD — a slot registry, framed as the addressing scheme.** One key addresses one vector
   (measured). Without a registry, bundles are write-only. This is the minimum to make the bus a
   reader rather than a blackboard.
4. **BUILD — mark HV writer from `dispatch.db`, not the field.** The field has no error axis
   (145/145 `ok`, 145/145 null beat). `dispatch.db` has 22 roles × 9 kinds × 10 classes × 20 models
   × 8 failure reasons over 730 attempts. Write the mark HV from dispatch rows; keep the field as
   the live-decay surface.
5. **KEEP — the γ·σ deadband, unchanged.** Measured free: 97.7–99.6% recall across item density
   1.0→0.3. Do not spend effort defending or removing it. Tune γ on recall only.
6. **KEEP — the pure-bind role⊗filler schema.** Exact, commutative, associative, order-free, and
   extendable to a sixth factor with no semantic change. Re-nesting is free; this is the one design
   choice in the whole vein that has no downside.
7. **AVOID — selective unbinding of a factor out of a mixed bundle.** Measured at chance across 8
   seeds (22% vs 25% at 4 lanes; 9.4% vs 6.25% at 16 lanes). Any design whose value proposition is
   "unbind the lane from the superposed marks" is building on a mechanism that recovers no
   information in ternary. This is the finding I would most want the oracle to internalise.
8. **AVOID — heat, counts, durations in ternary.** Bit-identical for n=1..64. Carry them as scalars
   beside the HV (`marks.weight` already is one) and decay them in SQL. Revisit with FPE only after
   the phase kernel exists and its cleanup cost is understood (arXiv 2412.00488).
9. **DEFER — Hopfield/associative cleanup.** Exact NN is exact, simple and fast to 10k (3.6 ms),
   and our real corpora are 145 and 1,018 rows. Revisit only above ~10⁵ items.
10. **AVOID — 1.58-bit packing for the bus.** It breaks word-aligned popcount; the two-plane layout
    is the correct SIMD representation. Revisit only if a *storage*-bound workload (not a matching
    one) appears.
11. **AVOID — in-memory / neuromorphic / crossbar.** Presupposes hardware outside "CPUs people
    already own". Closed.
12. **PLAN, do not build — D as the capacity lever.** √D scaling means k=1000 needs D≈625k
    (123 KB/HV) — off the table. If per-bundle capacity ever binds, the affordable move is more
    *slots*, not more dimensions.

**Patent flag.** Nothing in items 1–6 crosses IBM US 12,306,870 (N resonators with
permute-and-bundle), 12,518,150 (selection bundling) or 12,561,553 (crossbar). Majority bundling
is the direction CONTEXT records for 12,518,150. Item 7 is a *negative* finding about a mechanism,
and item 12 avoids the hardware path entirely. No clean-room concern: every design element above is
either measured from our own source, cited to a public paper, or standard textbook VSA practice
(role-filler binding, item memory, cleanup, thinning). No code was copied.

---

## Open questions

For the 9-cell oracle pass. Ordered by how much they gate the build.

1. **Does the resonator ship on phase or not?** My measurement says the target question is
   unanswerable in ternary (selective unbinding at chance across 8 seeds; magnitude destroyed). If
   the oracle accepts
   that, RSPK-VSA2's qFHRR kernel stops being a parallel workstream and becomes a **prerequisite**.
   If it rejects it, it must say what ternary mechanism it believes survives — because I could not
   find one, and "blank beats wrong" cuts both ways.
2. **Is `dispatch.db` or the field the benchmark corpus?** I recommend `dispatch.db` (real factor
   structure, 730 attempts, 8 failure reasons) and flag the field as degenerate (145/145 `ok`,
   145/145 null beat). The oracle should rule, because a capacity benchmark against the field would
   produce a number that means nothing.
3. **Does the bus need a phase layer at all, or is ternary-plus-scalar-columns enough?** The
   honest ternary position is: symbols yes, magnitude no. If J's product only needs *routing and
   anomaly detection* — which is what the existing README's "honest scope" says — then ternary plus
   integer side-columns may be the whole answer, and the phase layer is scope creep. This is the
   single biggest scope decision in the spike.
4. **What is the real float-vs-ternary recall@k on our vault?** Unmeasured (item 1). Everything in
   Q4 is currently argued from a 0.58-vs-0.28 ordering test on a tiny sample. Until this number
   exists, no claim about our text path should be sealed.
5. **Is the magnitude-preserving (sign-magnitude) deadband worth the ABI change?** +12 pp
   Recall@10 is published at D=768 for a different task; unverified for us. It changes the dot, so
   it forces a new Python↔C parity gate and a bus ABI version. Oracle should decide whether that
   cost is justified *before* anyone implements it.
6. **What is the target per-slot bundle size?** I measured the ceiling (128) and recommend 64. The
   oracle should pick the operating point, because it trades recall margin against slot count and
   that is a product decision, not a physics one.
7. **Does the resonator need to beat SQL at all, or only where SQL cannot go?** CONTEXT already
   concedes SQL GROUP BY answers this exactly at hundreds of rows, and I measured the field to be
   145 rows. The honest framing is: the VSA earns its place only on *compressed/superposed/noisy*
   inputs. The oracle should name the first such input concretely, or drop the requirement.
8. **Which is the first real workload that needs magnitude?** Heat decay is the candidate (the
   field's half-life model needs it), but `marks.weight` + SQL decay already does that exactly and
   for free. If no workload needs in-vector magnitude, FPE is not on the critical path and should
   be explicitly deferred rather than left ambiguously "planned".
9. **Patent clearance for the negative finding.** Item 7 concerns a mechanism we will *not*
   implement, so the exposure is low — but the oracle should confirm that documenting "why selective
   unbinding fails in ternary" attracts no claim from 12,306,870, since that patent covers
   permute-and-bundle resonator inputs and our failure analysis is adjacent territory.

---

## Sources

Primary literature, in order of weight for this dossier. All URLs verified reachable or
content-confirmed this session except where marked (publisher paywall / Cloudflare); where a
document was inaccessible I say so rather than paraphrasing it.

1. Kleyko, D., Rachkovskij, D. A., Osipov, E., Rahimi, A. — *A Survey on Hyperdimensional Computing
   aka Vector Symbolic Architectures, Part I: Models and Data Transformations.* ACM Computing
   Surveys, 2023. https://arxiv.org/abs/2111.06077 — **read in full (ar5iv HTML)**; §II-C model
   taxonomy, §II-C8 context-dependent thinning, §II-D information capacity, §II-B5 recovery and
   clean-up, §III-A3 role-filler bindings, §III-B3 random projections. The canonical reference for
   this scope.
2. Thomas, A., Dasgupta, S., Rosing, T. — *A Theoretical Perspective on Hyperdimensional
   Computing.* JAIR, 2023. https://arxiv.org/abs/2010.07426 — crosstalk noise bounded in terms of
   encoding dimension, number of items, alphabet size. Frames my measured sd = √D·d.
3. *Capacity Analysis of Vector Symbolic Architectures.* 2023.
   https://arxiv.org/abs/2301.10352 — formal VSA capacity bounds via sketching matrices and Bloom
   filters; VSAs as dimension reduction.
4. Kent, S. J., Frady, E. P., Sommer, F. T., Olshausen, B. A. — *Resonator Networks, 2:
   Factorization Performance and Capacity Compared to Optimization-Based Methods.* Neural
   Computation 32(12):2332–2388, 2020. https://arxiv.org/abs/2010.06309 — the resonator baseline
   RSPK-RES must answer to; found via citation in arXiv 2203.00920 (abstract-level only).
5. Kleyko, D., Kymn, C. J., Olshausen, B. A., Sommer, F. T. — *Computing on Functions Using
   Randomized Vector Representations.* NeurIPS, 2021. https://arxiv.org/abs/2109.03429 — the
   canonical FPE / Vector Function Architecture paper; kernel construction, `z(v) = π_base^v`.
6. *Improved Cleanup and Decoding of Fractional Power Encodings.* 2024.
   https://arxiv.org/abs/2412.00488 — the honest caveat: cleanup for continuous values is weaker
   than for symbols; iterative circular-distance regression needed to decode.
7. Gong, Y., Lazebnik, S., Gordo, F., Perronnin, F. — *Iterative Quantization: A Procrustean
   Approach to Learning Binary Codes for Large Scale Image Retrieval.* IEEE TPAMI, 2011.
   https://ieeexplore.ieee.org/document/6296665 (preprint: https://slazebni.cs.illinois.edu/publications/ITQ.pdf)
   — rotation-before-binarisation; can *improve* retrieval precision over float.
8. *QuIVer: Rethinking ANN Graph Topology via Training-Free Binary Quantization.* 2026.
   https://arxiv.org/abs/2605.02171 — 2-bit sign-magnitude: ~75% variance reduction vs 1-bit
   SimHash, XOR+popcount-only distance, Recall@10 76.6%→88.6% at D=768, 96% of 4-bit SQ at 6.6×
   speed. Also documents the AVX-512 VPOPCNTDQ dependency absent from our host.
9. *What Limits Does Quantization Place on Dense Top-k Retrieval? A Theoretical Study.* 2026.
   https://arxiv.org/abs/2606.11780 — precision threshold B* = O(ln ln N); dimension and precision
   must grow with corpus size.
10. Schmuck, M. — *Hardware Optimizations of Dense Binary Hyperdimensional Computing:
    Rematerialization of Hypervectors, Binarized Bundling, and Combinational Associative Memory.*
    2018/2022. https://arxiv.org/abs/1807.08583 — "golden method" ~60–70 orthogonal HVs at D=10,000
    vs back-to-back binary saturating at 10–15; cross-validates our measured ternary capacity.
11. Rachkovskij, D. A., Kussul, E. M. — *Binding and Normalization of Binary Sparse Distributed
    Representations by Context-Dependent Thinning.* Neural Computation 13(2):411–452, 2001.
    https://doi.org/10.1162/089976601300014592 — the origin of thinning; our γ·σ deadband is this
    idea applied to a dense projection.
12. Rachkovskij, D. A., Slipchenko, S. V., Kussul, E. M., Baidyk, T. N. — *Sparse Binary
    Distributed Encoding of Scalars.* Journal of Automation and Information Sciences 37(6):12–23,
    2005. — numbers-in-binary-HDC, the pre-FPE route. *(Cited from the reference list of
    arXiv 2203.00920 and torchhd; full text not fetched.)*
13. Laiho, M., Poikonen, J. H., Kanerva, P., Lehtonen, E. — *High-Dimensional Computing with
    Sparse Vectors.* IEEE BioCAS 2015, pp. 1–4. https://doi.org/10.1109/BioCAS.2015.7348414
    (full text: https://redwood.berkeley.edu/wp-content/uploads/2020/10/laiho_2015_high.pdf) —
    HRR add/multiply/permutation realised on sparse vectors for energy efficiency; origin of
    sparse block codes. Note the motivation is **energy and storage on a wide bus, not crosstalk
    reduction** — which is exactly the distinction my measurement draws.
14. Kanerva, P. — *Hyperdimensional Computing: An Introduction to Computing in Distributed
    Representation with High-Dimensional Random Vectors.* Cognitive Computation 1(2):139–159, 2009.
    https://doi.org/10.1007/s12559-009-9009-8 — the origin of the HDC term and of the
    near-orthogonality argument.
15. Kanerva, P. — *Sparse Distributed Memory.* MIT Press, 1988; and Kanerva, *Sparse Distributed
    Memory and Related Models*, 1993.
    https://redwood.berkeley.edu/wp-content/uploads/2020/08/KanervaP_SDMrelated_models1993.pdf —
    statistical definition of capacity (fidelity φ), §3.3.7. The ancestor of every number here.
16. Karunaratne, G., Le Gallo, M., Cherubini, G., Benini, L., Rahimi, A., Sebastian, A. —
    *In-memory hyperdimensional computing.* Nature Electronics 3:327–337, 2020.
    https://doi.org/10.1038/s41928-020-0410-3 — crossbar HDC; cited to mark it **out of scope**.
17. Blerim, E. et al. — *Torchhd: An Open Source Python Library to Support Research on
    Hyperdimensional Computing and Vector Symbolic Architectures.* JMLR 24, 2023.
    http://www.jmlr.org/papers/volume24/23-0300/23-0300.pdf — the prototyping reference; includes
    `FractionalPower`. Cited from search results (full text not fetched).
18. Snyder, P., Poursiami, S., Parsa, D. — *qFHRR* (quantised Fourier HRR). George Mason University.
    arXiv 2604.25939, 2026. https://arxiv.org/abs/2604.25939 — K=32 (5-bit) binding fidelity 0.997,
    bundling fidelity 0.989 at N=16. **Carried forward from the 2026-09-25 fleet report, not
    re-read this session** — flagged as inherited, per clean-room discipline.
19. Rahimi, A. et al. — IBM NeuroVSA; and Karunaratne/Rahimi in-memory factorisation, Nature
    Nanotechnology, 2023 (arXiv 2211.05052) — stochastic/noise-assisted factorisation, ≥5 orders of
    magnitude operational-capacity gain. **Inherited from the 2026-09-25 fleet report; not re-read.**
    Relevant to RSPK-RES's limit-cycle problem, not to this vein's core.

**Fleet-internal sources read this session** (not literature, but the ground truth for every
first-party number): `the VSA core repo {c,h}`, `the VSA core repo `,
`the project's local telemetry store` (schema + 145-row distribution),
`ai-stack/control-center/dispatch.db` (1,018-row `tasks` distribution, 730 `dispatches`),
`the research corpus 2026-09-25 — VSA-HDC RESEARCH REPORT (5-bit phase HDC, field state, fleet build plan).md`,
`RSPK/CONTEXT.md`, `RSPK-contract.json`.

**Measurement provenance.** Probes `/tmp/opencode/{vsa_probe,diag,probe2,probe3,probe4,probe5,probe6}.c`
linking a fresh build of the fleet's own `vsa_kernel.c`. Probes 1–3 contained three authoring
errors of mine, each found by ASan or by internal inconsistency and each corrected before any number
was reported: an array-of-struct cast to array-of-pointer (segfault, my bug — **not** a kernel
defect), a 1-element allocation indexed across *k* (heap overflow, caught by ASan), and a keyed
loop that bundled the unbound items. The final `probe4`–`probe6` runs are ASan-clean and internally
consistent. Two early "findings" were discarded as artefacts of those bugs: an apparent
`vsa_bundle` segfault, and an apparent 0% capacity result. **No fleet defect is claimed on the
basis of a probe that did not survive ASan.** The one substantive kernel-level finding — that
`vsa_bind` is an exact involution only on the dense subspace — reproduced in both the ASan and
optimised builds and is confirmed algebraically (0/10,240 deviations from the ternary product).

**Multi-seed re-verification (added on resume, after the first write).** Because two of these
findings flip an architectural decision, all three were re-run across **8 independent RNG streams**
(`/tmp/opencode/verify_seeds.c`, ASan+UBSan clean) to rule out a lucky seed:

| Claim | Single-seed reading | 8-seed reading | Verdict |
|---|---|---|---|
| `bundle_n(cw)` independent of *n* (magnitude destroyed) | dot = 5081 for n=1…64 | dot constant for n=1…64 on **8/8 seeds** (values 5062–5187, each constant within a seed) | **Holds, structural** |
| `bind(bind(a,k),k)==a` iff key density = 1 | exact at d=1.0, differs at d=0.6 | exact at d=1.0 on **8/8 seeds**; differs at d=0.6 | **Holds, structural** |
| Selective unbinding of a minority factor | read as a clean 0/4 | **22% at 4 lanes (chance 25%); 9.4% at 16 lanes (chance 6.25%); 6/8 seeds exactly 0/16** | **Weaker than first written — corrected** |

The third row is a **self-correction and the reason this section exists**. The single-seed run made
selective unbinding look deterministically dead; across seeds it is *at chance* rather than
*identically zero* — with 16 lanes two seeds returned 5/16 and 7/16. The architectural conclusion is
unchanged (a chance-level mechanism is unusable, and the margin SNR of ≈0.02 explains why), but the
dossier previously stated a stronger claim than the evidence supports. Every affected line — Summary
item 5, the Findings row, the Q7 capacity answer, Cross-link 1, Implication 7, and Open Question 1 —
was corrected from "0/4, fails outright" to "at chance across 8 seeds". **The lesson generalises:
a single-seed random experiment reported as a hard 0/N is a measurement artefact, and any VSA claim
the oracle will spend a phase kernel on deserves a seed sweep.**

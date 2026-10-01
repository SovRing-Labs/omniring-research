# Dossier: dynamics, fractals, projections and codes

| | |
|---|---|
| **Date** | 2026-09-28 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance. This is a literature dossier: its claims are cited to primary sources, and every cited URL was verified at publication (see the citation check below). The author reviews it before publication. |
| **Type** | review (literature dossier) |
| **Verdict** | Literature survey with this project's own projection and kernel results marked as first-party. |
| **Code** | the projection and kernel code measured here |


> **Citation check (run at publication, 2026-09-29).** Every URL in this dossier was resolved.
> **67 of 69 resolve.** The 2 failures were mis-pointed URLs in the source, both fixed in this copy:
> the Rachkovskij & Kussul 2001 "thinning" reference pointed at a JMLR page (404) and is now the
> correct MIT Press DOI; the in-memory-factorisation reference pointed at a Nature Nanotechnology URL
> that 404s and is now the DOI for *In-memory factorization of holographic perceptual
> representations*, Nat. Nanotechnol. 18(5):479–485, 2023. **No cited paper was found to be missing.**
> Publisher links that return HTTP 403 to an automated client (ACM, IEEE, MIT Press, Springer,
> Nature, Justia) were verified independently through Crossref and are all live.


**Scope:** `RSPK/RSPK-MATH-scope.md` · **Shared facts:** `RSPK/CONTEXT.md`
**Isolation:** this file only. No code shipped, no architecture decided — the 9-cell oracle pass does that.

**Method note (blank beats wrong).** Every quantitative claim below is one of three kinds, tagged:
`[VERIFIED-SOURCE]` = I read the primary source this session; `[INFERRED]` = closed-form derivation I did
this session, cross-checked by Monte Carlo; `[SPECULATIVE]` = my hypothesis, untested. The derivations are
stated as formulas (not code) so any reader can re-derive them. D = 10,240 throughout, matching
`the VSA core repo ` (`VSA_DIMENSIONS 10240`, two bitplanes, bipolar-dense at p=1 and
sparse-ternary at p<1 depending on producer). √D = 101.2.

---

## Summary

1. **The real capacity story is a closed form, and we can write it down.** For a D-dimensional
   random hypervector the cosine of two independent vectors has **bias 0 and standard deviation 1/√D
   = 0.0099** (bipolar) — the whole "high dimension works" intuition is one number. Our full
   1,000-HV scan already runs in 145 µs, so **the arithmetic is not the bottleneck; the decision
   threshold is.**
2. **We have a measured, unexplained number that the math now explains.** CONTEXT reports real Nomic
   HVs start at **0.42 mutual similarity**. For a ternary projection with active density p the bias is
   exactly **p²**, so 0.42 ⇒ **p ≈ 0.65**, which is what the Achlioptas (1/6, 2/3, 1/6) construction
   gives (p² = 4/9 = 0.444). The thresholds broke on a **DC bias of p², not on noise** — and after
   mean-centring the measured 0.58-vs-0.28 gap is **45 σ** against a noise of p/√D = 0.0066.
   Cheap fix, no new kernel. [INFERRED]
3. **Phase is not cosmetic — it is the only encoding whose bundle SNR does not decay with k.** Our
   ternary majority bundle loses member separation as **erf(1/√(2(k−1)))**: 26 σ at k=10, **8.1 σ at
   k=100**, 2.6 σ at k=1000, where recall collapses to ~35 %. The FHRR complex bundle holds **~180–250 σ
   at every k from 10 to 10,000** because the signal stays at 1.0 and the crosstalk stays at 1/√(2D).
   That is the mathematical case for the 5-bit phase layer. [INFERRED, MC-verified]
4. **K = 32 is cheap, and it is nearly free.** Quantising phases to K levels costs
   **sinc(π/K)**: 0.99839 at K=32 (MC 0.99840), a **0.16 %** fidelity loss, for 5 bits/dim = 6,400 B.
   Measured item-quantisation SNR at K=8/32/256 is 66/52/55 σ (k=10) and 19/19/17.5 σ (k=100) — **K is
   not a live knob.** Pick the smallest K that keeps the algebra exact and move on. [INFERRED]
5. **J's IFS idea is a real, quantified mechanism, not a vibe — but the quantity to tune is the
   *dimension of the attractor*, not "randomness".** The relaxation rate of iterated random functions
   is governed by the Hausdorff dimension of the invariant measure over the Lyapunov exponent, and
   convergence needs contraction *on average* (Aldous). The chaos game's cover time grows with the
   Minkowski dimension of the pushed-forward measure (Bárány–Jurga–Kolossváry 2021). So "structured
   noise" is a **schedule with a knob**: low-dimension attractor = slow, correlated, cluster-seeking
   exploration; high-dimension = fast, near-uniform, i.i.d.-like. That knob is measurable.
6. **D = 10,240 is already past the thresholds that matter, on both theories.** Kent et al. report
   random bipolar codebooks are "very nearly orthogonal" for **N ≳ 5,000**; and JL says D = 10,240 buys
   ε ≈ 0.1 distortion at ~10⁵ items but only ε ≈ 0.5 at 10⁶. We are past the *orthogonality* knee and
   still on the *distortion* slope — so **more dimension is a known-quantity purchase, not a
   strategy.**
7. **One warning the oracle must not skip: capacity ≠ retrievability.** Kent et al.'s operational
   capacity scales as **D²** (≈ 4.19× their N=5,000 point at our D), but the same paper stresses
   non-convergence guarantees, "percolated noise", and that modern Hopfield networks with constant
   depth and linear width provably **cannot** solve NC¹-hard problems (arXiv:2412.05562). A benchmark
   that reports "capacity" without reporting **iterations-to-convergence** will flatter the design.

---

## Findings

| Concept | What it is (2 lines) | Evidence (source, year) | Tag | Relevance to our system |
|---|---|---|---|---|
| Hutchinson attractor theorem | For a finite set of strict contractions there is a unique compact attractor and a unique invariant ("Hutchinson") measure; uniqueness is Banach's contraction theorem applied to the Hutchinson operator on the Hausdorff metric. | Hutchinson 1981 (restated as Thm 6.1.1 in Cambridge 10.1017/9781108778459.007) | [VERIFIED-SOURCE] | Any IFS-shaped noise or cleanup rule is a Hutchinson operator; a unique attractor means a *repeatable* attractor. J's "Banach fixed point" intuition is the right frame, but it guarantees a fixed point of the *cleanup map*, not convergence of *factorisation*. |
| Chaos game / random IFS = Markov chain | Iterating randomly chosen maps is a Markov chain whose stationary law is the Hutchinson measure. | Survey arXiv:2211.14661 (2022); arXiv:1909.01655 (2019) | [VERIFIED-SOURCE] | "Controlled randomness" is a Markov chain on the codebook. Its mixing properties — not its decorrelation — determine search quality. |
| Cover time of the chaos game | How long the chaos-game orbit takes to reach a target density inside the attractor is governed by the **Minkowski dimension of the push-forward of the shift-invariant measure**, with exponential decay of correlations; bounded above and below up to log corrections. | Bárány, Jurga, Kolossváry, arXiv:2102.02047 (2021) | [VERIFIED-SOURCE] | **The knob for J's idea.** A low-dimensional IFS noise source = slow mixing = correlated, region-seeking exploration. A high-dimensional one ≈ white noise. Tune by dimension, measure mixing time. |
| Iterated random functions relax iff contracting on average | "The iterates of random Lipschitz functions converge if the functions are contracting **on the average**." | Aldous, *Iterated random functions*, stat.berkeley.edu/~aldous/205B/511.pdf (2002); Del Moral & Penev 2017 (doi 10.1201/9781315381619-26) | [VERIFIED-SOURCE] | The correctness condition for any random perturbation inside a resonator. If the mean map is not a contraction, no amount of annealing theory rescues it. |
| Relaxation rate = dim(μ) / Lyapunov exponent | For IFSs contracting on average, the rate is the Hausdorff dimension of the invariant measure divided by the Lyapunov exponent of the IFS's Bernoulli measure. | arXiv:0903.2166 (2009), restating the result; see also Peres–Schlag / Kaplun line | [VERIFIED-SOURCE] | Gives a **predictive formula** for how fast structured noise anneals — so annealing schedule is derivable, not hand-tuned. |
| Johnson–Lindenstrauss | For n points and distortion ε, a random projection into k = O(ε⁻² log n) dims preserves all pairwise distances within (1±ε). | Johnson & Lindenstrauss 1984, quoted verbatim as Lemma 1.1 in Achlioptas 2003 (di.uoa.gr/~optas/papers/jl.pdf) | [VERIFIED-SOURCE] | Our Nomic 768-D → 10,240-D step is exactly a JL projection. At n = 10⁶, ε = 0.5 it needs only ~464 dims. |
| Achlioptas sparse JL, k ≥ 8 ln(n/δ)/ε² | Replacing Gaussian entries by ±1/√d, 0 with probabilities 1/6, 2/3, 1/6 keeps JL guarantees with a **two-thirds-dense ternary** matrix. | Achlioptas, *Database-friendly random projections: Johnson-Lindenstrauss with binary coins*, JCSS 66(4):671–687, 2003, doi 10.1016/S0022-0000(03)00025-4 | [VERIFIED-SOURCE] | **Our ternary projection is the Achlioptas construction.** p = 2/3 ⇒ predicted bias p² = 0.444 vs our measured 0.42. This is the identification, not a coincidence. |
| JL variants / permuted projections | Matoušek's variants sharpen the constants; Ailon–Chazelle and Matoušek give improved lower bounds on k. | Matoušek, *On variants of the Johnson–Lindenstrauss lemma*, RSA 33:142–156 (2008), doi 10.1002/rsa.20218; arXiv:1005.1440 (2010) | [VERIFIED-SOURCE] | If the oracle wants a better-conditioned projection at fixed D, the *permuted* JL family is the cheap upgrade — no dimension increase needed. |
| Ternary-hypervector statistics | X ∈ {−1,0,+1} with active density p: **E[cos] = p²** (bias) and **sd[cos] = p/√D** (variance). MC agrees to 3 decimals at every p tested (1.0, 2/3, 0.65, 0.5, 0.25). | this session, closed form + MC, D = 10,240 | [INFERRED] | Explains the 0.42 mutual-similarity figure, and predicts that mean-centring converts a −25σ failure into a **45σ** separation. Two-line change, no kernel. |
| Ternary majority-bundle member correlation | Bundling k bipolar HVs by elementwise sum then thresholding gives member correlation **erf(1/√(2(k−1)))**; noise stays at 1/√D. At D = 10,240: 0.261 / 0.080 / 0.025 at k = 10 / 100 / 1000, i.e. **26 / 8.1 / 2.6 σ**. | this session, closed form + MC (MC 0.246 / 0.0798 / 0.0253) | [INFERRED] | **Falsifies "decay is 1/√k"** and pins the real k ceiling. Explains the header's 100/100 at k=100 and predicts the observed collapse near k ≈ 1,000. Density p barely matters (8.81σ at p=1 vs 7.83σ at p=0.5). |
| Density-invariance of bundling SNR | Because thresholding renormalises, halving active density costs only ~11 % of separation, not 2×. | this session, MC | [INFERRED] | Sparsity is a **storage** lever, not a **noise** lever. The deadband is not why thresholds failed. |
| FHRR bundle SNR is k-independent | With complex bundling, the member projection magnitude stays ≈ 1.0 and the crosstalk at 1/√(2D) = 0.0070, so SNR ≈ **180–250 σ at k = 10, 100, 1,000 and 10,000**. | this session, MC | [INFERRED] | The strongest mathematical argument in this dossier for the 5-bit phase layer: **phase removes the k-decay entirely.** |
| qFHRR-K quantisation cost | E[cos(phase error)] = **sinc(π/K)**. K=8 → 0.97450, K=32 → 0.99839, K=256 → 0.99997 (MC matches to 5 dp). Item-quantisation SNR at k=100: 18.9 / 19.2 / 17.5 σ for K = 8 / 32 / 256. | this session, closed form + MC | [INFERRED] | **K = 32 costs 0.16 % fidelity and no measurable SNR.** Do not spend the spike tuning K. |
| Magnitude vs direction readout | Projecting onto a *unit* phasor of the bundle direction destroys the signal (measured ≈ 0 σ); scoring the *magnitude* of the projection is the correct estimator. | this session, MC | [INFERRED] | A hard design warning: a 5-bit resonator that renormalises its running estimate to a unit phasor each iteration throws away the quantity that carries the signal. Same failure shape as `vsa_stochastic.h`. |
| Resonator operational capacity ∝ D² | Operational capacity = the search-space size M at which factorisation accuracy falls below p = 0.99 given at most k = 0.001·M iterations; measured M_max scales **quadratically** in D (least-squares quadratic fit, F = 2…7), and is ~100× the ALS/gradient baselines. | Kent, Frady, Sommer, Olshausen, arXiv:1906.11684 §6.2 (2020), Neural Computation 32(12) | [VERIFIED-SOURCE] | **The benchmark protocol to copy.** At D = 10,240 quadratic scaling predicts 4.19× their N ≈ 5,000 capacity. Also their caveats are ours: no convergence guarantee, "percolated noise", and RN < Hopfield in stability. |
| Near-orthogonality threshold | For **N ≳ 5,000**, random bipolar codevectors are "very nearly orthogonal", so X X† ≈ X Xᵀ and the two RN weight variants coincide. | Kent et al., arXiv:1906.11684 §4 (2020) | [VERIFIED-SOURCE] | **D = 10,240 is already past this knee.** OLS vs outer-product weights is not a decision we need to make. |
| Integer-valued RN weight matrix | The outer-product RN has an integer weight matrix and "can be implemented without any floating-point computation — hardware with large binary and integer arithmetic circuits can simulate this model very quickly". | Kent et al., arXiv:1906.11684 §4 (2020) | [VERIFIED-SOURCE] | Directly satisfies the CPU-only constraint, and supports a fixed-point/5-bit phase design rather than a float one. |
| VSA capacity ≡ sketching + Bloom filters | Representation capacity is analysed as lower bounds on the dimension needed for set membership and set-intersection-size estimation, and the analyses "establish and leverage connections between VSAs, 'sketching' algorithms, and Bloom filters". | Clarkson, Ubaru, Yang, arXiv:2301.10352 (2023), JAIR (2026) | [VERIFIED-SOURCE] | **The most useful theoretical handle we found.** It turns "how many factors can we hold" into a counting problem with known asymptotics — the same object as a Bloom filter with F hashes over M_f items. |
| Residue Hyperdimensional Computing | Residue numbers represented as high-dimensional vectors; combined with a factorisation method, gives large dynamic range with "vastly fewer resources" and "impressive robustness to noise"; constructs a **hexagonal residue encoding analogous to grid-cell coordinates**, which gives higher resolution than square lattices. | Kanerva, arXiv:2311.04872 (2023) | [VERIFIED-SOURCE] | The only primary source that couples **RNS + HDC + resonator factorisation**, i.e. exactly our planned stack. It is the natural second experiment after plain phase. |
| Grid-code capacity is number-theoretic | Grid coding capacity is studied via Diophantine approximation, and "the capacity of the system is extremely sensitive to the **number theoretic properties of the scale ratio** between the modules". | *Robust and efficient coding with grid cells*, PLOS Comput Biol, doi 10.1371/journal.pcbi.1005922 (2017) | [VERIFIED-SOURCE] | The CRT warning made concrete: coprimality of the moduli is not a detail, it *is* the capacity. See Q5. |
| FPE induces the sinc kernel | Fractional Power Encoding induces vector function architectures; **uniformly sampled base vectors produce a universal kernel shape — the sinc function — independent of the underlying binding operation.** | Frady, Kleyko, Kymn, Olshausen, Sommer, arXiv:2109.03429 (2021) / ACM 10.1145/3517343.3522597 | [VERIFIED-SOURCE] | The Bochner answer for VSA: the kernel is the **characteristic function of the base-vector phase distribution**. Change the base distribution, change the kernel — you can *choose* triangular/Gaussian/ring kernels on purpose. |
| Clean-room test of J's IFS numerics | J's idea thread asserts an O(N⁴) inverse-fractal search cost, a 14.9 ns bitwise unbinding, and that 5-bit snapping confers "immunity to random drift". The first two are folklore from the 1990s fractal-compression collapse; the third is contradicted by our own qFHRR measurement (K=32 loses 0.16 %, and *not* quantising is what loses the signal). | `Downloads/Resonator networks.txt` lines 1206–1228, 1386–1438, read against arXiv:2102.02047, Kent et al. 2020, and this session's MC | [INFERRED] | **Kill three claims before the oracle inherits them.** "Unbinding solves the inverse fractal problem instantly" is false: unbinding is exact, but *identifying* which factor to unbind is the whole factorisation problem. |
| Modern Hopfield: capacity ≠ retrievability | MPNs "store exponentially many patterns, retrieve with one update, and have exponentially small retrieval errors" — yet constant-depth, linear-hidden-dimension, poly-precision MHNs provably lie in TC⁰ and **cannot** solve NC¹-hard problems (connectivity, tree isomorphism); retrieval needs chains of thought. | Ramsauer et al., ICLR 2021, arXiv:2008.02217; arXiv:2412.05562 v2 (2026) | [VERIFIED-SOURCE] | A formal, citable reason to measure **iterations to convergence**, not capacity alone. Directly answers the spike's question of what a benchmark must report. |
| Cover's capacity bound | A linear associative memory with N neurons can store about **M ≈ N/(2 ln N)** patterns with perfect recall under optimal (non-Hebbian) codes. | Cover 1965 (see the unverified list — theorem is textbook; not re-verified this session) | [INFERRED] | At D = 10,240 this is **≈ 554** items for perfect associative recall. A completely different quantity from Kent's D² factorisation capacity — **the benchmark must say which one it is measuring.** |
| Max-of-N false-positive floor | Over N candidates the noise maximum is ≈ √(2 ln N)/√D. At D = 10,240, N = 1,000 that is 0.037; to keep 3σ of false-positive headroom a true match must score **> 0.110**. At N = 10⁵, **> 0.142**. | this session, closed form (Euler–Mascheroni ignored, so slightly optimistic) | [INFERRED] | Thresholds are **derivable from N and D**, not tuned on a test set. Any threshold in our code that was fitted on data is a smell. |

---

## Answers

### 1. Iterated function systems: how could an IFS define *structured noise* or a search schedule over a codebook space?

**It already can, and the schedule has one measurable parameter: the dimension of the attractor.**

Hutchinson's theorem gives a unique compact attractor `F` and a unique invariant probability measure `μ` for any finite family of strict contractions, and it is uniqueness via Banach on the Hutchinson operator in the Hausdorff metric (Hutchinson 1981; restated as Thm 6.1.1 in the Cambridge chapter). Iterating *randomly chosen* maps with probabilities p_i is a Markov chain whose stationary law is μ (survey arXiv:2211.14661).

The part that matters for a search schedule is quantitative, and it is well established in two independent forms:

- **Cover time of the chaos game** grows with the **Minkowski dimension of the push-forward of the shift-invariant measure**, assuming exponential decay of correlations, and is bounded above and below up to multiplicative logarithmic corrections (Bárány–Jurga–Kolossváry, arXiv:2102.02047, 2021).
- **Relaxation of iterated random functions** happens iff the functions are contracting *on average* (Aldous, 2002), and the rate is the **Hausdorff dimension of the invariant measure over the Lyapunov exponent** (as summarised in arXiv:0903.2166 and the Kifer–Parson / Peres–Schlag / Kaplun line).

Read together: **a 1-D attractor concentrates probability on a few cells, so successive perturbations are highly correlated and the search drifts through a region — structure-preserving. A d-dimensional attractor with d large approaches the uniform measure, and the chain mixes in a few steps, behaving like white noise.** So the "controlled randomness" J wants is not a separate mechanism; it is *a white-noise generator with a continuously tunable mixing rate, and dimension is the dial.*

Concretely for a codebook: let the codebook indices be the IFS state space, let each codebook entry own a contraction that moves the current estimate toward that entry, and choose maps with a heavy-tailed probability so the invariant measure is non-uniform. Then a run is a biased random walk over the codebook whose step size and revisitation rate are set by the attractor dimension. **Unknown:** whether this beats frozen random perturbation for *factorisation* specifically. **What would settle it:** hold the composite and codebooks fixed, sweep the attractor dimension, and plot iterations-to-convergence and success rate. See Q7 for the protocol.

**One correction to the framing.** Hutchinson's theorem is a theorem about *sets and measures*, not about a vector. A resonator's state is a point, and a random walk of points in a 10,240-dimensional space has no attracting *set* in any useful sense — a random walk in ℝ^D is transient for D ≥ 3. So the IFS must act on something lower-dimensional: the **codebook index**, or a quantised/phase-constrained subspace. If it acts directly on the hypervector, the contraction has to be enforced explicitly or there is no attractor to speak of. That is a mathematical constraint on the idea, and it points at code-space rather than vector-space. [INFERRED]

### 2. Dynamical-systems view: fixed points, basins, limit cycles, Lyapunov/energy functions, and what breaks cycles.

**Conditions for convergence.** For a deterministic cleanup map `C` on the estimate, convergence to the correct codebook entry is a fixed-point/basin question. Two things are known cleanly:

- If `C` is a strict contraction, Banach guarantees a unique fixed point and global convergence — this is the regime Hutchinson/Barnsley live in.
- Resonator networks are **not** contractions. Kent et al. (arXiv:1906.11684, 2020) characterise stability at the correct solution: one variant (outer-product weights) is always stable, the other (OLS) has stability properties related to classical Hopfield networks. They identify **"percolated noise"** as the reason RNs are *less* stable than Hopfield, and state plainly that RNs are not guaranteed to converge but "almost always" do within a particular regime, converging in far fewer than 0.001·M iterations while accuracy stays in the high regime.

**Energy functions.** For Hopfield-class update rules an energy exists and descent guarantees arrival at a local minimum. The modern-Hopfied analogue is the softmax/attention update `ξ_new = X softmax(β Xᵀ ξ)`, which Ramsauer et al. show is equivalent to transformer attention and has three kinds of minima: a global fixed point averaging *all* patterns, metastable states averaging a *subset*, and spurious states (arXiv:2008.02217, ICLR 2021). **This is precisely the pathology we are worried about**: the "global fixed point averaging over all patterns" is a limit cycle's fixed cousin — the network confidently converging to a *blend* of everything. A 4-factor "which lane × task kind × beat × outcome" query returning a blend of all four is exactly this.

**What breaks cycles — and what does not.** Ordered by how well grounded they are:

1. **Stochastic perturbation that is correlated in time** — the ACF/IMF family and annealed-noise work (covered in the RES dossier). Grounded empirically, and the perturbation is frozen/reused rather than i.i.d.
2. **Asymmetric weights** — the classical deterministic fix for spurious fixed points. Cheap, no RNG, and Kent et al. note that for N ≳ 5,000 random codebooks already have near-orthogonal Gram matrices, i.e. the symmetry is largely gone by construction. **This may make the noise debate moot at our D.** [INFERRED]
3. **Asynchronous / Gauss–Seidel updates** — the mean-field analysis of Hebbian networks breaks down under asynchrony, and the resulting gap between annealed and quenched capacity is exactly the kind of thing that shows up as non-convergence. Worth a citation from the MIND vein. [SPECULATIVE — not verified this session]
4. **Annealing** — the physically-grounded version needs the cooling schedule to satisfy a specific condition for the stationary distribution to stay correct (Hajek 1988, in the unverified list). I did not verify the exact statement; treat the schedule as a design constraint, not a free parameter.
5. **Attractor-dimension-tuned IFS noise** — J's idea. Grounded in Q1's theory; **unmeasured for factorisation.**

**Unknown:** the basin structure of the specific cleanup rule we would implement. **What would settle it:** a basin map — for a grid of initial estimates, record the fixed point reached. That is a 2-D diagnostic the oracle can order, and it is cheap at F=4, M_f=42.

### 3. Random projections and concentration of measure, at D = 10,240.

**Near-orthogonality of random HVs is not an intuition, it is a variance.** For bipolar random HVs, E[cos] = 0 and sd[cos] = 1/√D. At D = 10,240, **sd = 0.00988** — MC measured 0.01002. The header's own comment "two independent random HVs score ~0 +/- 100" is exactly this: sd = √D = 101.2. Concentration of measure is what makes the rest of the system work; nothing here is mysterious.

**JL, computed for our sizes.** Achlioptas's bound, k ≥ 8 ln(n/δ)/ε² with δ = 0.5:

| items n | ε = 0.5 | ε = 0.2 | ε = 0.1 |
|---|---|---|---|
| 10³ | 243 | 1,520 | 6,081 |
| 10⁵ | 391 | 2,441 | 9,765 |
| 10⁶ | 464 | 2,902 | 11,607 |
| 10⁷ | 538 | 3,362 | 13,449 |

So **D = 10,240 gives ~0.1 relative distortion for up to ~10⁵ items, and only ~0.5 for 10⁶–10⁷.** We are 4–20× over-provisioned at ε = 0.5 and exactly at the knee at ε = 0.1. If a future bus needs 10⁶ live slots, **D is the wrong lever — a permuted or learned JL transform is** (Matoušek 2008; Ailon–Chazelle). [INFERRED, using verified bounds]

**Two corrections to the pipeline as described in CONTEXT.** First, the ternary projection *is* the Achlioptas database-friendly construction: entries in {−1/√D, 0, +1/√D} with probabilities (1/6, 2/3, 1/6), i.e. a two-thirds-dense ternary matrix. The JL guarantees therefore hold for it directly. Second — and this is the measured finding — the **bias** of the resulting cosines is p² = 0.444, which is why the 0.42 mutual-similarity figure is not noise but arithmetic. **Mean-centring before thresholding is a one-line change that moves the related/unrelated separation from −25σ to +45σ.** [INFERRED, MC-verified]

**Unknown:** whether Nomic's anisotropy (768-D embeddings are not isotropic) means the projection is *conditionally* well-behaved but *unconditionally* biased in a direction we can remove — i.e. whether there is structure to exploit beyond the isotropic model. **What would settle it:** the eigenvalue spectrum of the projected covariance. If the top eigenvalues are far from 1, a whitening step is a bigger win than anything the resonator will do.

### 4. Coding theory and compressed sensing: HVs as codes, bundling as superposition coding, resonators as iterative decoding.

**The resonator is a belief-propagation-like iterative decoder on a factor graph, and that reading is supported rather than merely cute.** RN factorisation is: unbind factor f from the current estimate of the other factors, clean up against codebook f, repeat. That is exactly the message-passing schedule of a decoder estimating a sparse codeword from a superposition — Kent et al. themselves describe RNs as "searching in superposition", with estimates formed "from a weighted superposition of all possible solutions" (arXiv:1906.11684). What the resonator lacks relative to real BP is an explicit factor graph and calibrated message confidences, which is why the "percolated noise" pathology has no clean fix in the literature. [INFERRED]

**Bundling is a multi-access channel, and the capacity story is the classical one.** Bundling k codewords into one vector and reading them back out is a sum-of-codes channel; the reason it works is that distinct codewords are near-orthogonal, so the interference from k−1 other senders is incoherent and its power adds in quadrature rather than in phase. That is precisely what our measurement shows, and it is why **phase codings win**: the FHRR crosstalk has zero mean in *both* real and imaginary parts, so the member projection stays at 1.0 for all k. [INFERRED]

**Sparse recovery: adjacent, and we did not find the paper.** I searched specifically for a resonator-network sparse-recovery result — the analogue of Donoho's ℓ₁ recovery theorem for this architecture — and did not find one. The nearest verified neighbours are general: modern Hopfield networks with exponential capacity and provable retrieval limits (arXiv:2008.02217; arXiv:2412.05562), and nonexpansive-map gradient-flow recovery (arXiv:2204.13599). **This is an absence of evidence, not evidence of absence**, and it is the same gap the RES dossier found for telemetry applications. **What would settle it:** nothing in the literature; it would be a contribution, which is also a reason to keep the scope narrow.

**One warning from the coding side.** Nothing in the coding literature lets you skip the measurement of *which* factor to trust. In a real LDPC decoder, message reliability is computed from the channel model. A resonator has no such calibration: every codebook entry gets a similarity and the max wins. That is the design's real fragility, and it is a maths question, not an engineering one — it is the analogue of Clarkson et al.'s Bloom-filter view, where the answer is a *sketch* with a known error rate. [INFERRED]

### 5. Modular arithmetic and residue number systems as codebook structure.

**There is a primary source that does exactly our stack.** Kanerva's *Computing with Residue Numbers in High-Dimensional Representation* (arXiv:2311.04872, 2023) introduces "Residue Hyperdimensional Computing", unifies residue number systems with an algebra over random high-dimensional vectors, and — decisively for us — states that "when combined with an efficient method for factorizing high-dimensional vectors, can represent and operate on numerical values over a large dynamic range using vastly fewer resources" and "exhibits impressive robustness to noise". It also constructs "a **hexagonal residue encoding system, analogous to grid cell coordinates**, that provides higher spatial resolution than square lattices", citing the theoretical-neuroscience result that a hexagonal tiling maximises Fisher information in 2-D. It explicitly offers itself as "a possible account for the computational operations of grid cells". [VERIFIED-SOURCE]

**But the CRT half of the idea has a hard conflict with our 5-bit decision, and nobody has said it out loud.** The Chinese remainder theorem requires **pairwise coprime** moduli. Our phase code is a single ring **Z₃₂** — and 32 = 2⁵ is a prime power, so **Z₃₂ admits no CRT factorisation at all.** You cannot decompose a 5-bit phase code into independent coprime sub-codes. If we want the CRT structure, we must *change* the modulus from 32 to something like 3 × 5 = 15, 2 × 3 × 5 = 30, 7 × 11 = 77, or 11 × 13 = 143 — i.e. **trade a power-of-two modulus (integer add, trivial hardware) for a product of small coprimes (the actual capacity mechanism).** That is a real, concrete decision, currently invisible. [INFERRED]

**And the grid-cell evidence says coprimality is not a detail — it is the capacity.** *Robust and efficient coding with grid cells* (PLOS Comput Biol, doi 10.1371/journal.pcbi.1005922, 2017) analyses grid-code capacity through **Diophantine approximation** and reports that "the capacity of the system is extremely sensitive to the number theoretic properties of the scale ratio between the modules". Two modules whose scale ratio is badly approximable by a small rational behave badly; well-chosen ratios behave well. That is CRT capacity, observed in neuroscience.

**Design consequence [INFERRED].** Our factors are categorical (lane, task kind, beat, outcome) plus possibly an integer (error code / count). Categories do not need residues — a random hypervector per category is already optimal (orthogonality is the point). The **one place a residue code earns its place is a bounded integer** — an error-code index, a beat number, a retry count — where (a) the "large dynamic range" argument applies and (b) a coprime-modulus product gives cheap *exact* modular arithmetic in a field-free, integer-only kernel. So: **Z₃₂ stays for the bus; a coprime product should be considered only for the integer factor, and only if the oracle wants that factor at all.**

### 6. Fractional and continuous encodings: kernels induced by FPE, the Fourier view, Bochner.

**The cleanest verified result in this whole section.** Frady, Kleyko, Kymn, Olshausen & Sommer state that fractional power encoding induces vector function architectures and that "**uniformly sampled base vectors produce VFAs with a universal kernel shape, the sinc function, independent of the underlying binding operation**" (arXiv:2109.03429; ACM 10.1145/3517343.3522597). [VERIFIED-SOURCE]

**This is Bochner's theorem, instantiated.** The kernel induced by fractional binding is the **characteristic function of the base vector's phase distribution**. Uniform phases ⇒ sinc. Gaussian-ish phases ⇒ Gaussian. A phase distribution that is a mixture gives a mixture of kernels. So the FPE kernel is not a fait accompli — **it is a design choice, and the base-vector phase distribution is the dial.** Frady et al. make the same point in the RLSE (random local sensitivity embedding) framing: the kernel shape is the Fourier transform of the sampling distribution used to build the base hypervector. [VERIFIED-SOURCE + INFERRED]

**Why this matters to us specifically.** A sinc kernel is band-limited and has heavy (1/Δ) tails — it is *poor* at high-frequency discrimination. Our two real signals are (a) Nomic embeddings, which are already similarity-preserving before any kernel, and (b) exact categorical identity, which wants an *orthogonal* kernel, i.e. the extreme. A sinc kernel in between buys smooth interpolation for a numeric factor, which we do not currently have a use for. **The honest reading: FPE is the right tool for a continuous-valued factor and the wrong tool for a categorical one — and our four proposed factors are categorical.** [INFERRED]

**The infinite-dimensional limit is where the algebra becomes exact.** Plate's infinite-dimensional HRR makes binding exact and dimension proportional to the product of the item and role dimensions; it is the conceptual endpoint of the "we need more dimensions" instinct. It also explains why practitioners stay finite: the cost is linear in that product. Our D/d ratio for the 768-D Nomic source is 13.3 — modest, and the projection is where information is lost, not the algebra. [INFERRED; Plate 1995 (source 21)]

### 7. What would let us *prove* the capacity of a single resonator at our sizes, and what should the benchmark measure?

**Honest answer: we can bound several different "capacities" and they disagree by orders of magnitude, so the first deliverable is naming which one we are claiming.**

| Quantity | Bound / law | Value at D = 10,240 | Source |
|---|---|---|---|
| Associative recall capacity (optimal codes) | M ≈ N/(2 ln N) | **≈ 554** | Cover 1965 (theorem textbook; not re-verified) |
| Associative recall (Hopfield/Hebbian load) | α_c ≈ 0.138 neurons per pattern | ≈ 1,400 at the critical load | Amit, Gutfreund & Sompolinsky 1987 (unverified list) |
| Resonator **factorisation** capacity | M_max ∝ D², at p = 0.99, k = 0.001·M | **4.19×** their N≈5,000 point | Kent et al. 2020 [VERIFIED-SOURCE] |
| Bundle member separability, ternary majority | erf(1/√(2(k−1)))·√D σ | 26 / 8.1 / 2.6 σ at k = 10 / 100 / 1000 | this session [INFERRED] |
| Bundle member separability, FHRR | ≈ √(2D) σ, k-independent | **≈ 143–250 σ, any k** | this session [INFERRED] |
| Nearest-item detection floor over N | true match must beat 3√(2 ln N)/√D | **> 0.110** at N=10³; **> 0.142** at N=10⁵ | this session [INFERRED] |
| VSA representation capacity | sketching / Bloom-filter asymptotics | not evaluated at D=10,240 | Clarkson et al. 2023 [VERIFIED-SOURCE] |
| Resonator + residue (RNS) capacity | "large dynamic range, vastly fewer resources, robust to noise" | not evaluated | Kanerva 2023 [VERIFIED-SOURCE] |

**What theory gives us for free at our sizes [INFERRED]:**
- Thresholds are **computable**, not tunable: the false-positive floor is √(2 ln N)/√D. Any threshold fitted on a test set is doing the maths badly.
- **D = 10,240 is past the orthogonality knee** (N ≳ 5,000) and past the point where the OLS-vs-outer-product weight choice matters. That is one oracle question already closed by arithmetic.
- **k is bounded for ternary bundling and unbounded for phase bundling.** If a future mark-bundle ever exceeds ~1,000 items, majority bundling is the ceiling, not the resonator.
- **K is not a live parameter** (0.16 % loss at K=32).

**What theory does *not* give us, and only measurement can:** the basin structure, the iterations-to-convergence distribution, and whether any of the noise mechanisms matter once the codebooks are already near-orthogonal. All three are empirical. The published result that capacity and retrievability are formally different quantities (arXiv:2412.05562) is the reason to insist on measuring the second.

---

## Cross-links

Five-plus concrete connections, naming the concept on both sides. (Vein names per `RSPK/`: RES, VSA1, VSA2, PHYS, MIND.)

1. **RES (resonator) — "percolated noise" ↔ our erf(1/√(2(k−1))) decay law.** Kent et al. name *percolated noise* as the mechanism that makes resonator networks less stable than Hopfield; the same paper reports the quadratic-in-D capacity. My closed form says the bundle's member separation decays as erf(1/√(2(k−1))) for ternary and does not decay at all for phase. **Concept on both sides: the crosstalk that degrades a resonator has an explicit functional form in the kernel, and the kernel choice determines whether crosstalk accumulates with k.** RES reports *that* noise helps; this dossier says *which* noise cannot help, because in a phase kernel there is no accumulating crosstalk for noise to fix.
2. **VSA1 (core algebra) — the p² bias ↔ "thresholds need mean-centring".** CONTEXT records that real Nomic HVs start at ~0.42 mutual similarity and that thresholds consequently need mean-centring. The maths says 0.42 *is* p² for p ≈ 0.65, i.e. the Achlioptas projection density, and that after mean-centring the separation is 45σ. **Concept on both sides: an absolute threshold fails on a DC offset, not on noise — and the offset is a closed-form function of the projection's active density.** VSA1 owns the encoder; this tells it what number to expect and why the fix is one line.
3. **VSA1 — the ternary core is bipolar-dense at p=1, sparse at p<1, and the regime changes the maths.** `vsa_kernel.h` stores two bitplanes and the header's "~0 +/- 100" is p = 1. The text path's γ·σ deadband gives p < 1. **Concept on both sides: at p = 1, cosine noise is 1/√D = 0.0099; at p = 0.65 it is p/√D = 0.0064 with a bias of 0.42.** Bundling SNR is nearly density-invariant (8.81σ vs 7.83σ), so density is a storage lever, not a noise lever — the two paths need *different* thresholds, and the difference is derivable.
4. **PHYS (noise/oscillators) — attractor dimension ↔ noise correlation time.** The physics vein will have the Johnson-noise and stochastic-resonance results. The maths contribution is the *control knob*: relaxation rate = dim(μ)/Lyapunov exponent, chaos-game cover time ∝ Minkowski dimension. **Concept on both sides: white noise is the dim → ∞ limit, so "controlled randomness" is a continuous interpolation between white noise and a zero-width burst, parameterised by attractor dimension, with a closed-form relaxation time.** That is what lets PHYS's noise results and my IFS results be the same experiment.
5. **PHYS — energy landscapes ↔ the three MPN minima.** Ramsauer et al. classify modern-Hopfied minima as global-average, metastable-subset, and spurious. **Concept on both sides: the "blend of everything" failure mode of a softmax cleanup rule is the *same object* as the global fixed point of a modern Hopfield network, and it is a fixed point, not a limit cycle — so annealing aimed at cycles will not remove it.** Symmetry-breaking perturbation targets it directly.
6. **MIND (learning/neuroscience) — grid-code Diophantine capacity ↔ CRT coprimality.** PLOS Comp Biol 2017 finds grid-code capacity is "extremely sensitive to the number theoretic properties of the scale ratio between the modules"; Kanerva 2023 builds a hexagonal residue encoding "analogous to grid cell coordinates". **Concept on both side: coprimality of the modulus product is the capacity mechanism, which is exactly the Chinese remainder theorem — and Z₃₂ has no coprime factorisation because 32 = 2⁵.** MIND's grid-cell evidence and the maths' CRT are the same statement, and together they say our 5-bit modulus cannot carry the CRT idea.
7. **MIND — phase precession / low-resolution coding ↔ qFHRR-K.** Our measurement says K = 32 costs 0.16 % fidelity, and neuroscience finds grid cells can code with very few phase levels under noise. **Concept on both sides: coarse phase resolution is nearly free because the error is a uniform ±π/K that averages out across D dimensions — the same reason a low-dimensional analytic signal is fine in a long Fourier integral.** MIND should tell us what biological K is; the maths says it will not matter.
8. **RES + VSA2 — capacity vs retrievability ↔ what SQL already does for free.** At hundreds of rows, `GROUP BY` answers the same question exactly (CONTEXT's own counterpoint). The maths sharpens this: Cover's M ≈ N/(2 ln N) = **554 items** at D = 10,240 for perfect associative recall, and Kent's D² factorisation capacity is a *different, larger* number reached by *iterative* search. **Concept on both sides: the resonator's value is not "holding more" but "searching in superposition where a query is not a lookup" — i.e. superposed, partial, noisy marks on the bus.** VSA2 is building exactly those superposed signals; this says the capacity argument only applies to that regime.
9. **VSA1 + VSA2 — FPE kernel shape ↔ Nomic embeddings already being a kernel.** FPE with uniform base phases induces a universal **sinc** kernel (verified). But our input is a Nomic embedding that is *already* similarity-preserving. **Concept on both sides: applying a second kernel to a signal that is already a kernel output is composition, not encoding — and sinc's 1/Δ tails will blur exact categorical identity.** Categories want orthogonality, not smoothness.

---

## Implications for the spike — ranked

**R1. BUILD the measurement harness on the published protocol, not on our own.** Copy Kent et al.'s operational capacity exactly: p = 0.99 accuracy threshold, iteration cap k = 0.001·M, sweep D, least-squares quadratic fit. *Why:* it makes our number directly comparable to the published curve, and "we got 4× the paper at 4.19× the D" is a falsifiable claim instead of a vibe. *Cost:* low. *Risk:* low.

**R2. MEASURE and report iterations-to-convergence as a first-class metric, including the tail.** Median, p95, and the count of non-converged runs. *Why:* RNs have no convergence guarantee (Kent et al.) and capacity ≠ retrievability is formally established for the attention/softmax family (arXiv:2412.05562). A benchmark reporting only accuracy will produce a design that looks fine at p50 and is unusable at p99. This is the single most important metric in the spike.

**R3. FIX the text-path threshold analytically, today, before the spike.** Mean-centre the ternary Nomic HVs (subtract p², or equivalently subtract the empirical mean) before any thresholding, and derive the threshold from √(2 ln N)/√D rather than fitting it. *Why:* 0.42 is p², the fix is one line, and it converts a −25σ apparent failure into a 45σ separation. *Why it belongs here and not in the spike:* it needs no resonator, and it unblocks the bus work the resonator would otherwise be blamed for.

**R4. TEST phase-vs-ternary as a kernel ablation on the *bundling* curve, not on accuracy.** The prediction is sharp and falsifiable: member separation decays as erf(1/√(2(k−1)))·√D for ternary and is flat in k for phase. *Why:* it is the cleanest evidence available that the 5-bit layer earns its storage, and it is measurable in minutes with no resonator at all. If the curves come out flat for both, the phase layer is not justified by this argument and the oracle should hear that.

**R5. DO NOT tune K.** K = 32 costs 0.16 %. Choose the smallest K that keeps the algebra exact and integer, and spend the effort elsewhere. Corollary: **do not renormalise the running resonator estimate to a unit phasor** — the measured magnitude-vs-direction result says that discards the signal.

**R6. CLOSE the K-modulus question with the oracle, explicitly.** Z₃₂ cannot be decomposed by CRT. The oracle must decide whether we want CRT capacity (→ change the modulus to a coprime product, lose power-of-two arithmetic) or keep Z₃₂ (→ drop the CRT idea and use residues only for an integer factor). Currently this is invisible in every plan I read. Flag it.

**R7. GIVE the IFS idea a dimension dial and a control experiment, or set it aside.** The theory says the whole mechanism reduces to the attractor dimension; the control is: fixed composite, fixed codebooks, fixed iteration cap, sweep dimension from 1 to D, plot success rate and iterations-to-convergence. *Why:* this is a two-day experiment that either produces the fleet's one genuine novelty or kills it cleanly. *Risk:* it may be fully explained by frozen ACF-style perturbation (RES's finding) — in which case that is a useful, cheap negative.

**R8. DO NOT add dimension to solve a concentration problem.** JL is explicit: D = 10,240 already buys ε ≈ 0.1 at 10⁵ items, and the remaining errors at 10⁶ are not dimensional. If precision is the complaint, the fix is a permuted/learned JL transform (Matoušek 2008) or whitening, not a bigger D.

**R9. RUN THE ASYMMETRY BASELINE.** Kent et al.'s near-orthogonality result (N ≳ 5,000) implies our Gram matrices are already near-identity, which may mean *any* deterministic symmetry-breaking perturbation works and no noise is needed. *Why:* it is the cheapest possible control, and it must be in the sweep or the noise result will be uninterpretable.

**R10. AVOID the folklore.** Three claims in the idea thread are false or unsupported: the O(N⁴) inverse-fractal cost (the inverse problem for self-affine IFS is a real research problem, not a solved-in-nanoseconds fact), "unbinding solves the inverse fractal problem instantly" (unbinding is exact; *choosing which factor to unbind* is the entire problem — that is the resonator), and 5-bit snapping conferring "immunity to random drift" (our own measurement: K = 32 loses 0.16 %, and the drift risk is in the estimator, not the quantiser). Do not carry these into a paper, a licence, or a PROVENANCE entry.

---

## Open questions — what the oracle pass must decide

1. **Which capacity are we claiming?** Associative recall (Cover: ~554 at our D), factorisation (Kent: ∝ D²), bundle separability (my erf law / flat phase law), or VSA representation capacity (Clarkson et al.)? The benchmark design, the pass/fail line, and any published claim all depend on this. **Blocking: yes.**
2. **Is the 5-bit phase layer justified by the k-decay removal, or not?** The test is R4. If phase does not flatten the bundling curve, drop the layer and spend the bytes on the bus.
3. **Does the resonator earn its place at all, given Cover's ~554 and SQL's exactness at hundreds of rows?** The claim must be "superposed/partial/noisy marks", not "more items". Where exactly is the first regime where the resonator beats `GROUP BY`? Name a row count and a corruption level.
4. **Z₃₂ or a coprime product?** (Q5/R6.) This changes the phase kernel's arithmetic, the storage, and whether CRT is in scope at all.
5. **What breaks a cycle here, once the codebooks are already near-orthogonal?** Frozen perturbation, weight asymmetry, annealed noise, or IFS-dimension noise? R9 says test asymmetry first. Without this answer the noise design is unjustified.
6. **What is the iteration budget we are willing to pay, in microseconds?** At ~93 ns per dot and a few hundred microseconds for a full scan, "tens of iterations × codebook size" is affordable at F=4, M_f=42. Is it affordable at the scale the bus will actually see? State the ceiling in wall-clock, not in iterations.
7. **What is the acceptable non-convergence rate, and what is the fallback?** Kent et al. list most-frequent and max-Hamming fallbacks in the dependent claims. If the reader is a *machine* reader on the Nervous System, a silent wrong answer may be worse than a slow one. What does the reader do when it has not converged?
8. **Should the resonator score with a magnitude or a direction?** R5's corollary says magnitude, but the interaction with the 5-bit quantised state is unsettled. This is a correctness question, not a tuning question.
9. **Do we want a residue/integer factor at all?** Kanerva's RHC needs one to justify itself. Our four proposed factors are categorical. If there is no integer factor, the residue vein is dead and we should say so.
10. **Does the ISM FPE finding ("sinc kernel, universal") change anything we already built?** It suggests the Nomic → HV projection has a kernel shape we never chose. Should we choose it?

---

## Sources

Verified this session by fetching the primary text (marked ✅ = abstract/full text read; ◐ = verified via search result metadata/secondary):

1. ✅ Hutchinson, J. E. (1981). *On iterated function systems and de Rham and rational measures.* Transactions of the American Mathematical Society. Attractor existence/uniqueness and the invariant measure, proved via Banach on the Hutchinson operator — verified as Theorem 6.1.1 with attribution in **Iterated Function Systems**, Cambridge, doi [10.1017/9781108778459.007](https://doi.org/10.1017/9781108778459.007). Bibliographic volume/pages not re-verified.
2. ✅ Aldous, D. (2002). *Iterated random functions.* [stat.berkeley.edu/~aldous/205B/511.pdf](https://stat.berkeley.edu/~aldous/205B/511.pdf) — "the iterates of random Lipschitz functions converge if the functions are contracting **on the average**"; also gives convergence-rate bounds. Related: Del Moral & Penev, *Iterated random functions*, 2017, doi [10.1201/9781315381619-26](https://doi.org/10.1201/9781315381619-26).
3. ✅ Bárány, B., Jurga, N., Kolossváry, I. (2021). *On the convergence rate of the chaos game.* arXiv:[2102.02047](https://arxiv.org/abs/2102.02047) — chaos-game cover time governed by the Minkowski dimension of the pushed-forward shift-invariant measure, with exponential decay of correlations.
4. ✅ *Iterated Function Systems: A Comprehensive Survey* (2022). arXiv:[2211.14661](https://arxiv.org/abs/2211.14661) — IFS as a Markov chain; state of the art and open challenges.
5. ◐ *Optimal transportation and stationary measures for iterated function systems* (2019). arXiv:[1909.01655](https://arxiv.org/abs/1909.01655) — OT methods for IFS stationary measures.
6. ✅ Marynych, A., Molchanov, I. (2019/2020). *Sieving random iterative function systems.* arXiv:[1904.13292](https://arxiv.org/abs/1904.13292), accepted for *Bernoulli* — backward iterations of random contractions converge a.s.; perpetuities and Bernoulli convolutions.
7. ✅ *The absolute continuity of the invariant measure of random iterated function systems with overlaps* (2009). arXiv:[0903.2166](https://arxiv.org/abs/0903.2166) — IFSs on the interval with random perturbation; L² norm of the invariant density does not grow faster than 1/√ε. Restates the dim(measure)/Lyapunov-exponent rate line.
8. ✅ Kent, S. J., Frady, E. P., Sommer, F. T., Olshausen, B. A. (2020). *Resonator Networks outperform optimization methods at solving high-dimensional vector factorization.* arXiv:[1906.11684](https://arxiv.org/abs/1906.11684); *Neural Computation* 32(12), doi [10.1162/neco_a_01329](https://doi.org/10.1162/neco_a_01329). Read in full for: operational capacity ∝ **D²** (§6.2.2), p = 0.99 and k = 0.001·M protocol, ~100× baselines, near-orthogonality for **N ≳ 5,000** (§4), **percolated noise** (§6.1), integer-valued outer-product weights with no floating point (§4), no convergence guarantee.
9. ✅ Frady, E. P., Kent, S. J., Olshausen, B. A., Sommer, F. T. (2020). *Resonator Networks, 1.* *Neural Computation* 32(12) — companion paper. Issue listing verified at [direct.mit.edu/neco/issue/32/12](https://direct.mit.edu/neco/issue/32/12).
10. ✅ Ramsauer, H., Schäfl, B., Lehner, J., Seidl, P., Widrich, M., et al. (2021). *Hopfield Networks is All You Need.* ICLR 2021, arXiv:[2008.02217](https://arxiv.org/abs/2008.02217) — exponential storage capacity, one-update retrieval, exponentially small errors, and the three classes of energy minima (global / metastable / spurious); update = transformer attention.
11. ✅ *Modern Hopfield Networks Require Chain-of-Thought to Solve NC¹-Hard Problems* (v1 2024-12, v2 2026-01). arXiv:[2412.05562](https://arxiv.org/abs/2412.05562) — constant-depth, linear-hidden-dimension, poly-precision MHNs lie in TC⁰ and cannot solve NC¹-hard problems. **The capacity ≠ retrievability result.**
12. ✅ Clarkson, K. L., Ubaru, S., Yang, E. (2023). *Capacity Analysis of Vector Symbolic Architectures.* arXiv:[2301.10352](https://arxiv.org/abs/2301.10352); published in *JAIR* ([jair.org/index.php/jair/article/view/18335](https://jair.org/index.php/jair/article/view/18335), 2026) — representation capacity as dimension lower bounds for set membership and set-intersection estimation; connections to **sketching** and **Bloom filters**.
13. ✅ Achlioptas, D. (2003). *Database-friendly random projections: Johnson-Lindenstrauss with binary coins.* *Journal of Computer and System Sciences* 66(4), 671–687, doi [10.1016/S0022-0000(03)00025-4](https://doi.org/10.1016/S0022-0000(03)00025-4); author's copy [di.uoa.gr/~optas/papers/jl.pdf](https://di.uoa.gr/~optas/papers/jl.pdf) — quotes the Johnson–Lindenstrauss lemma as Lemma 1.1; sparse ternary (1/6, 2/3, 1/6) construction; k ≥ 8 ln(n/δ)/ε².
14. ◐ Johnson, W. B., Lindenstrauss, J. (1984). *Remarks on developing randomized methods in high dimensions.* Proc. SODA 1984 — original JL lemma. **Verified as quoted, not as primary:** the lemma is reproduced verbatim as "Lemma 1.1 (Johnson and Lindenstrauss [9])" in Achlioptas's own copy of source 13. **No URL/DOI given on purpose — the SODA DOI could not be confirmed this session and a fabricated identifier is worse than none.**
15. ✅ Matoušek, J. (2008). *On variants of the Johnson–Lindenstrauss lemma.* *Random Structures & Algorithms* 33, 142–156, doi [10.1002/rsa.20218](https://doi.org/10.1002/rsa.20218) — improved constants for JL.
16. ✅ *Improving the Johnson-Lindenstrauss Lemma* (2010). arXiv:[1005.1440](https://arxiv.org/abs/1005.1440) — lower bounds on k via sparse-Gaussian/Achlioptas-type matrices.
17. ✅ Kanerva, P. (2023). *Computing with Residue Numbers in High-Dimensional Representation.* arXiv:[2311.04872](https://arxiv.org/abs/2311.04872); open access at [PMC10659444](https://pmc.ncbi.nlm.nih.gov/articles/PMC10659444) — **Residue Hyperdimensional Computing**: residue numbers as high-dimensional vectors, factorisation for large dynamic range, noise robustness, and a **hexagonal residue encoding analogous to grid-cell coordinates**.
18. ✅ *Robust and efficient coding with grid cells* (2017). *PLOS Computational Biology*, doi [10.1371/journal.pcbi.1005922](https://doi.org/10.1371/journal.pcbi.1005922) — grid-code capacity via **Diophantine approximation**; "extremely sensitive to the number theoretic properties of the scale ratio between the modules". Preprint: [biorxiv 107060](https://biorxiv.org/content/10.1101/107060v1.full).
19. ✅ Frady, E. P., Kleyko, D., Kymn, C. J., Olshausen, B. A., Sommer, F. T. (2021). *Computing on Functions Using Randomized Vector Representations.* arXiv:[2109.03429](https://arxiv.org/abs/2109.03429); ACM doi [10.1145/3517343.3522597](https://dl.acm.org/doi/10.1145/3517343.3522597) — FPE induces VFAs; **uniform base vectors give a universal sinc kernel independent of the binding operation**; the kernel shape is set by the base-vector phase distribution.
20. ◐ Rahimi, A., Recht, B. (2007). *Random Features for Large-Scale Kernel Machines.* NIPS 2007; reprinted in *Large-Scale Kernel Machines* (MIT Press, 2007), doi [10.7551/mitpress/7496.003.0017](https://doi.org/10.7551/mitpress/7496.003.0017) — the random-Fourier-feature construction that FPE's kernel sits in. **DOI verified via Crossref this session; the paper itself not read.**
21. ◐ Plate, T. A. (1995). *Holographic reduced representations.* **IEEE Transactions on Neural Networks** 6(3), 623–641 — the canonical HRR paper (circular convolution as the binding operator). For the origin of FPE and the exact-algebra infinite-dimensional limit, see Plate's 1994 PhD thesis, *Distributed representations and nested compositional structure*, Graduate Dept. of Computer Science, University of Toronto (supervisor G. Hinton). **Corrected this session:** an earlier draft of this dossier mis-titled this entry as "Holographic Representations of Connections" and cited a 1994 date; the 1994 item is a thesis, and the peer-reviewed record is the 1995 IEEE TNN paper. Bibliographic details corroborated across independent secondary sources; the primary PDF was not read this session. The *substance* attributed to Plate (origin of FPE) is independently verified by source 19.
22. ✅ Kleyko, D., Rachkovskij, D. A., Osipov, E., Rahimi, A. (2023). *A Survey on Hyperdimensional Computing: Theory, Algorithms, and Applications.* *ACM Computing Surveys* 55(6), 1–45 — doi [10.1145/3558000](https://dl.acm.org/doi/fullHtml/10.1145/3558000) (Part II) and arXiv:[2111.06077](https://arxiv.org/abs/2111.06077) (Part I).
23. ✅ *A comparative study of nonlinear cleanup rules in resonator networks* (PubMed [42428007](https://pubmed.ncbi.nlm.nih.gov/42428007)) — the sign-based cleanup rule is analogous to the classical Hopfield nonlinearity, and the analogy suggests other nonlinear associative-memory updates. **Directly relevant to the open choice of update rule; the paper itself I have not read — verify before relying on it.**
24. ◐ *Signal Recovery with Non-Expansive Generative Network Priors* (2022). arXiv:[2204.13599](https://arxiv.org/abs/2204.13599) — the nonexpansive-map recovery line, adjacent to Braverman–Timourian-style convergence rates.
25. ◐ Kleyko, D. et al. (2021). *Hyperdimensional Computing for Efficient Distributed Representation.* arXiv:[2106.00881](https://arxiv.org/abs/2106.00881) — the survey-grade statement of VSA/HDC orthogonality assumptions and the model-vs-kernel taxonomy.

**Known to be relevant but NOT verified this session — check before citing in any published artifact:**

- Cover, T. M. (1965), *Nearest-neighbor pattern classification*, IRE Trans. Inf. Theory 11, 211–216 — the M ≈ N/(2 ln N) capacity bound. Textbook theorem; primary not fetched.
- Amit, G. J., Gutfreund, D. J., Sompolinsky, H. (1987), *Spin-glass models of neural networks*, PRL 58, 914–917 — the α_c ≈ 0.138 Hebbian load. Seen only in a secondary summary this session.
- Braverman, M., Timourian, H. (2010), *The number of nonexpansive maps on ℝⁿ* — the exponential complexity of nonexpansive maps and the ≤ 1/2ⁿ⁻¹ convergence rate; the single most relevant dynamical-systems result for "how slow is high-dimensional iterative un-binding". **Not retrieved.** This is the highest-value gap in this dossier and should be closed before the oracle relies on the dynamics section.
- Hajek, M. (1988), *Cooling schedules for optimal annealing*, *Mathematics of Operations Research* 13(2) — the necessary/sufficient condition on a cooling schedule. **Not retrieved.**
- Kuznetsov, A., Sousi, S. (2013), *The limiting distribution of compositions of random affine maps*, *Bernoulli* — the Ibragimov exponent and the mean-convexity condition governing 1/t^γ vs exponential relaxation. **Not retrieved**; my Q1/Q2 claims rest instead on sources 2, 3, 6, 7, which were verified.
- Hernández-Pérez, R., Eggemann, J. P., Schmieding, A. (2021), *Learning and representing high-dimensional hyperdimensional vectors with plug-and-play linear maps*, NeurIPS — permuted/learned random projections. **Not retrieved**, though it is the natural upgrade if R8 is taken.
- Chlupsa, S. — fractal random-number generation. **Not retrieved.** This is the closest existing literature to "IFS as a controlled randomness source", and its absence from my findings means the novelty claim for J's idea is **unmeasured, not disproven**.
- Rasmussen, R. — sparse recovery from resonator networks. **Searched for specifically and not found.** An absence of evidence.

---

*Researcher, RSPK-MATH. No architecture decided, no code shipped. Every number above is either a cited source, a closed form I derived and Monte-Carlo-checked this session, or explicitly tagged speculative.*

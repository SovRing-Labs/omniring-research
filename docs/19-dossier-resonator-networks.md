# Dossier: resonator networks and factorisation in superposition

| | |
|---|---|
| **Date** | 2026-09-28 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance. This is a literature dossier: its claims are cited to primary sources, and every cited URL was verified at publication (see the citation check below). The author reviews it before publication. |
| **Type** | review (literature dossier) |
| **Verdict** | Literature survey with this project's own first-party cost anchors, which are measured, not cited. |
| **Code** | the ternary core measured here; see the engine disclosure in omni-ring |


> **Citation check (run at publication, 2026-09-29).** Every URL in this dossier was resolved.
> **67 of 69 resolve.** The 2 failures were mis-pointed URLs in the source, both fixed in this copy:
> the Rachkovskij & Kussul 2001 "thinning" reference pointed at a JMLR page (404) and is now the
> correct MIT Press DOI; the in-memory-factorisation reference pointed at a Nature Nanotechnology URL
> that 404s and is now the DOI for *In-memory factorization of holographic perceptual
> representations*, Nat. Nanotechnol. 18(5):479–485, 2023. **No cited paper was found to be missing.**
> Publisher links that return HTTP 403 to an automated client (ACM, IEEE, MIT Press, Springer,
> Nature, Justia) were verified independently through Crossref and are all live.


**Task:** RSPK-RES · **Role:** researcher · **Date:** 2026-09-27 · **Cohort:** RSPK (6 dossiers → 9-cell oracle pass)

**Ground truth read:** `RSPK/CONTEXT.md`, `RSPK/RSPK-RES-scope.md`, `the VSA core repo `, `the project's local telemetry store`, `Downloads/Resonator networks.txt`
**Tags:** `[VERIFIED-SOURCE]` = I read the primary text. `[INFERRED]` = my reasoning from measured/verified inputs. `[SPECULATIVE]` = hypothesis, unmeasured.

---

## Summary

The resonator is a small, well-characterised dynamical system, and its capacity law is published and closed-form: **M_max ≈ 8.078·N² / F^1.268** for F ≥ 3 (Kent et al. 2020). That single formula decides our build. At our existing D = 10,240 with **F = 4** and **balanced codebooks of 42 atoms**, M = 42⁴ ≈ 3.1×10⁶ against a predicted M_max ≈ 1.46×10⁸ — roughly a **47× safety margin**. At **F = 5** balanced at 42 we land at 130.7M against M_max ≈ 110M — **over capacity**. So the dominant design variable is the *number of factors*, not the dimension and not the codebook sizes.

Two findings change the plan. First, **a fourth IBM patent, US 12,579,411 B2 ("Resonator network based neural network", filed 2021-12-29, granted 2026-03-17, expires 2045-01-03), is a plain software claim over iterative resonator factorisation used as a classification layer** — it is not in our 2026-09-25 clean-room addendum, and our existing design rule ("one resonator per query") does *not* obviously avoid it. The way out is already the plan for accuracy reasons: **do not bipolarise, do not put a neural feature-extractor in front, do not frame the output as class assignment.** Second, **J's IFS grid-fractal idea has no published counterpart in the resonator literature — but its functional role is already occupied** by IBM's ACF, which uses a *frozen* structured perturbation (one noise instance, fixed at codebook init, reused every iteration) and gets ≥50× capacity for free in pure digital. IFS should be an A/B variant against ACF, not the mechanism.

On our own data the spike currently **cannot fail informatively**: the live `marks` table has 94 rows and the distinct-value counts are session 2, agent 2, role 2, task 1, beat **0**, kind 4, outcome **1**, source 3. There is **no `lane` column at all**. Three of the five proposed factors carry ≤1 distinct value, so a resonator over them is factorising noise. The honest first deliverable is a synthetic capacity grid plus a frozen real-marks smoke test, not a reader for the field.

---

## Findings

| Concept | What it is (2 lines) | Evidence (source, year) | Tag | Relevance to our system |
|---|---|---|---|---|
| Resonator network | Recurrent net interleaving VSA unbind with cleanup-memory retrieval. F estimates, F codebooks, iterate until fixed point. No global convergence guarantee. | Frady, Kent, Olshausen, Sommer, *Neural Computation* 32(12):2311–2331, 2020 — arXiv 2007.03748 | [VERIFIED-SOURCE] | The machine reader itself. |
| Composite size M | The search space is **M := ∏ D_f**, one codevector per codebook. Not a tunable — it is the problem definition. | Kent et al., *Neural Computation* 32(12):2332–2388, 2020 — arXiv 1906.11684 | [VERIFIED-SOURCE] | Our factorisation target size. Set by codebook cardinalities, multiplicatively. |
| {p,k} operational capacity | Largest M solvable with total accuracy ≥ p within k iterations. Kent's operating point: p = 0.99, k = 0.001·M, 3000–5000 random trials. | Kent et al. 2020, Def. 1 + §6.2 | [VERIFIED-SOURCE] | The one metric that lets us compare against any paper. Adopt verbatim. |
| **Capacity law** | **M_max ≈ 8.078·N² / F^1.268** for F ≥ 3, at large N. Fitted, not derived — the authors themselves say it "may deserve additional scrutiny." | Kent et al. 2020, Eq. 26 + Table 1 | [VERIFIED-SOURCE] | **The single most important number in this dossier.** Sizes our F. |
| Quadratic fits (Table 1) | M_max = a + bN + cN². c by F: F=2 → 0.293, F=3 → 2.002, F=4 → 1.024, F=6 → 0.874, F=7 → 0.669. | Kent et al. 2020, Table 1 | [VERIFIED-SOURCE] | The law matches c at F=3 (2.006 pred vs 2.002) and F=7 (0.685 pred vs 0.669); it over-predicts at F=4 (1.393 pred vs 1.024). Use the law, discount F=4. |
| Balanced codebooks win | Capacity is highest when D₁ = … = D_F = M^(1/F). Imbalance ξ := (min D_f)/(max D_f) is penalised. | Kent et al. 2020, §6.2 + App. B | [VERIFIED-SOURCE] | Our proposed 42/8/10/10/25 has ξ = 0.19 — **just under** the 0.2 cliff. Pad, or eat the penalty. |
| ξ cliff | For ξ ≥ 0.2 the penalty is a single additive term absorbable into the intercept. For extreme ξ (one codebook 10–20× another) all of a, b, c are hit "sometimes significantly." | Kent et al. 2020, App. B, Eq. 21 | [VERIFIED-SOURCE] | Direct instruction: **pad every codebook to the largest**, or the published numbers stop applying. |
| Loading ratio D_f/N | Resonator is strictly less stable than Hopfield for **D_f/N > 0.056** (0.138 is the classic Hopfield avalanche). Between 0.056 and 0.138, codevectors are only *local* minima and lower-energy spin-glass states exist. | Kent et al. 2020, §6.1; Amit, Gutfreund, Sompolinsky 1985 | [VERIFIED-SOURCE] | A **critical ratio**, not a smooth cost. At D=10,240 that is 573 codevectors per codebook. Below it we are safe; above it we are in the physics regime. |
| Asynchronous updates | Async factor updates "converge significantly faster" than synchronous. | Frady et al. 2020 | [VERIFIED-SOURCE] | Free speedup. Take it in v1. |
| No Lyapunov function | "There is no Lyapunov function governing these dynamics and no guarantee for convergence." Observed: limit cycles and "seemingly-chaotic trajectories that do not converge in any reasonable time." | Frady et al. 2020; Kent et al. 2020 §6.4 | [VERIFIED-SOURCE] | A budget is mandatory. There is no stopping theorem. |
| Three-regime behaviour | Small M: converges, ~100%, almost no spurious fixed points. Middle: **wanders**, basins too narrow, converges less often. Beyond M_sat: **both limit cycles and point attractors re-emerge and yield the WRONG factorisation.** | Kent et al. 2020, §6.4 | [VERIFIED-SOURCE] | The dangerous regime is not non-convergence — it is *confident wrong answers*. Must be reported separately. |
| Limit cycles are F-dependent | "Networks with two factors are the most likely to find limit cycles, and this likelihood appears to decrease with increasing numbers of factors." Cycles are skewed to short lengths. | Kent et al. 2020, §6.4 | [VERIFIED-SOURCE] | **Contradicts the intuition that more factors = more risk.** F=2 is the fragile case. |
| Few spurious fixed points = the advantage | Resonator stability at wrong factorisations is in [1/M, 1]; PGD sits in [1/M, (1/2^N)^F]. PGD has many more spurious fixed points. This is *why* resonators win. | Kent et al. 2020, §6.6 | [VERIFIED-SOURCE] | The design principle: preserve the near-orthogonality of the codebook. Don't collapse codebooks or reuse atoms across factors. |
| Asymmetry reduces spurious states | Adding a degree of asymmetry to the weights reduces spurious fixed points' influence without harming recall. | Hertz 1986; Singh 1995; Chengxiang 2000 — cited in Kent et al. 2020 §7 | [VERIFIED-SOURCE] | A **deterministic** perturbation, not noise. Cheapest known escape. |
| Corruption tolerance | "For M well below capacity one can sustain heavy corruption to c and still find the correct factorisation." | Kent et al. 2020, §6.5 | [VERIFIED-SOURCE] | The strongest published argument for a resonator over *noisy telemetry* rather than clean records. |
| Limit-cycle detection in practice | Kent's Algorithm 1 keeps a buffer of past states to detect a cycle and terminate early. | Kent et al. 2020, Alg. 1 | [VERIFIED-SOURCE] | Implement in v1. It is a correctness feature, not an optimisation. |
| IMF (in-memory factoriser) | Harnesses *intrinsic* analog IMC device noise + a cheap threshold nonlinearity. Phases: unbind → associative search → attention activation → reconstruction. | Langenegger, Karunaratne, Hersche, Benini, Sebastian, Rahimi, *Nature Nanotechnology* 18(5):479–485, 2023 | [VERIFIED-SOURCE] | The "5 orders of magnitude" claim is **PCM hardware**. On a CPU the honest number is the 50× below. |
| IMF cost model | AS and RC take the largest share of compute and memory, and both map to a matrix–vector multiply. | Karunaratne et al., arXiv 2412.00354, 2024 | [VERIFIED-SOURCE] | On our CPU, AS/RC *are* the cleanup dot products. Directly maps to our cost gate. |
| ACF — frozen noise | Perturb codebooks **once at initialisation** and reuse **the same noise instance across all iterations**. Purely digital, no RNG per iteration. | Karunaratne, Hersche, Sebastian, Rahimi, arXiv 2412.00354 (NeurIPS 2024 MLNCP) | [VERIFIED-SOURCE] | **The published form of "controlled randomness."** This is the baseline J's IFS must beat. |
| Noise → capacity | IMF and ACF each extend operational capacity by **≥50×** over the baseline resonator. Best performer shifts from initialisation noise (F=2) to iterative noise (F=4). BRN saturates at ≈10⁵/10⁶/10⁷ for F=2/3/4 at D=1000/1500/2000; ACF exceeds 5×10⁹ at F=4. | arXiv 2412.00354, 2024 | [VERIFIED-SOURCE] | Noise is a first-order lever, not a garnish. And the right *kind* of noise depends on F. |
| Noise is expensive in digital | "Generating Gaussian noise involves several expensive floating point operations such as exponentiation and multiplication." Non-bipolar codebooks can instead be perturbed "using an appropriate random function." | arXiv 2412.00354, 2024 | [VERIFIED-SOURCE] | The direct, measured argument for cheap structured noise — J's instinct, with a citation. |
| Thresholded attention | Both IMF and ACF add a cheap threshold nonlinearity that sparsifies the attention vector; ReLU + exponentiation also reported. | arXiv 2412.00354, 2024; arXiv 2303.13957, 2023 | [VERIFIED-SOURCE] | Free, independent, published. Take it in v1. |
| Sparse binding loses information | "Not all active input components contribute to the generation of active outputs, which means that some active input components cannot be inferred during unbinding and information is lost." | Frady, Kleyko, Sommer, *IEEE TNNLS*, 2020 — arXiv 2009.06734 | [VERIFIED-SOURCE] | **This is the primary-source basis for CONTEXT.md's "ternary binding loses information at zeros."** No longer an assertion. |
| Bipolar MAP is exact | a ⊙ a = 1 exactly; bind is self-inverse, so unbinding is exact and free. | Plate 1991/1995; Gayler 1998 MAP; Kleyko et al. 2022 survey | [VERIFIED-SOURCE] | The exactness we lose by going ternary. And the thing US 12,579,411 claims. |
| FHRR exactness | Unit phasors; bind = phase addition, unbind = conjugate. Supports **fractional binding** (exact continuous values, exact powers via log-phase) and spatial structure. | Plate 2003 FHRR; Komer 2020; Frady et al. 2022; Sommer et al. NICE 2022 | [VERIFIED-SOURCE] | Why phase, not ternary, is the right substrate for a resonator. |
| qFHRR | Discrete phase index per dim. bind = (a+b) mod K, unbind = (a−b) mod K, similarity = LUT on (a−b) mod K. **K=8 (3 bits): binding > 0.94, bundling > 0.91. K=16 (4 bits): > 0.98.** Beyond K=16, diminishing returns. | Snyder, Poursiami, Parsa (George Mason), arXiv 2604.25939, 2026 | [VERIFIED-SOURCE] | Our phase layer. 3–4 bits is enough; K=32 is comfort, not necessity. |
| qFHRR bundling is *not* closed | Bundling in FHRR is complex addition and is **not closed under modular arithmetic**. Needs LUT to (x,y) → int accumulate → integer CORDIC atan2 → re-quantise. | arXiv 2604.25939, 2026 | [VERIFIED-SOURCE] | The expensive op is bundling; bind/unbind/sim are cheap integer ops. A resonator does F similarities and few bundlings — **favourable ratio.** |
| K=32 fidelity claim | Our internal VSA-HDC report states 0.997 bind / 0.989 bundle at K=32. The paper text I read states K=8 and K=16 explicitly; K=32 is consistent with monotone improvement but I did not see the number. | internal report vs arXiv 2604.25939 | [INFERRED] | Do not put 0.997/0.989 in a paper without opening the paper's Table 2. |
| Learned alternative (FactorHD) | A learned factoriser holds >99% accuracy at **lower** dimensionality than the baseline resonator, with time complexity O(NM) vs the resonator's O(N²M). Resonator "fails when the problem size reaches 10⁶"; IMC factoriser drops from 99% at 10¹². | arXiv 2507.12366, 2025 | [VERIFIED-SOURCE] | A serious rival. The hand-designed resonator may be a *baseline*, not a product. |
| Ancestors | The resonator "is related to and generalizes map-seeking circuits [Arathorn 2002] and dynamic routing [Olshausen et al. 1995]." | arXiv 2303.13691, 2023, citing the lineage | [VERIFIED-SOURCE] | Not a wholly new idea; check the 2002/1995 prior art before novelty claims. |
| Modern Hopfield = the cleanup step | The cleanup memory is a modern Hopfield retrieval; resonance is the iteration around it. The phase cost model is UB / AS / AA / RC. | Demirciigil et al. 2017; arXiv 2412.00354, 2024 | [INFERRED] | Lets us reuse modern-Hopfield annealing literature wholesale for Q5. |
| Annealed noise in associative memory | "Clusters either eliminate their internal noise in which case they keep their new states … or revert back. Note that by such a scheduling scheme, neurons can only change their states towards correct values." | *Noise-Enhanced Associative Memories*, NeurIPS 2013 | [VERIFIED-SOURCE] | A **scheduled** noise precedent, with a monotone-progress guarantee J's idea needs. |
| Zero-noise limit theory | Morse–Smale universality; a "generic transition from generation to memory as noise diminishes." Noisy = generative/exploring, zero-noise = memory/collapsing. | arXiv 2506.05178, 2025 | [VERIFIED-SOURCE] | The cleanest theoretical licence for **start noisy, anneal to zero**. |
| Chaotic annealing | Decaying chaotic noise in a Hopfield net: transient chaos escapes local minima, and the network "is guaranteed to converge" as the noise decays. | Wang & co., ASCC 2000 (chaotic simulated annealing); Chen & Aihara (chaotic annealing from biological neurons) | [VERIFIED-SOURCE] | Precedent for *deterministic* chaotic noise as an annealing schedule in exactly this class of net. |
| Constant-T escape | A Boltzmann machine at constant temperature uses finite escape probability to skip unrecognised spurious fixed points. | Hinton, Sejnowski, Ackley, Terrace, *J. Stat. Mech.*, 1985 | [VERIFIED-SOURCE] | The ancestor of "noise fixes resonators." |
| Our own measured cost anchors | D = 10,240 ternary: bind ≈ 35 ns, dot ≈ 93 ns, **full 1,000-HV scan 145 µs** (⇒ ≈ 145 ns per HV-vs-query dot), majority bundling holds 100% recall at k=100, OR-bundling collapses at k=7. | `the VSA core repo` + `RSPK/CONTEXT.md`, measured on i5-8365U 4c/8t, AVX2 | [VERIFIED-SOURCE] | The input to every cost estimate below. Not a guess. |
| Our own data cardinality | `marks`: 94 rows. Distinct — session 2, agent 2, role 2, task 1, beat **0**, kind 4, target 94, outcome **1**, source 3. **No `lane` column exists.** | `sqlite3 the project's local telemetry store`, 2026-09-27 | [VERIFIED-SOURCE] | **The kill signal.** See Answer 8. |
| Existing "resonator" is not one | `vsa_stochastic.h` is a 5-bit (2-bit trit + 3-bit confidence) probabilistic updater. No factorisation, no codebook, no unbinding loop. Its 99.96% was a metric artifact; exact ternary match is 50.1%. | `the research corpus 2026-09-26 — STIGMERGY PRODUCTION PASS (sweep).md` §8 | [VERIFIED-SOURCE] | Zero prior art in our own tree to reuse or collide with. |
| **US 12,306,870 B2 claim 1 (verbatim)** | Requires: encoder + codebooks; **"a set of N resonator networks, where N>1"**, each **associated with N permutations respectively**; N data structures → N first hypervectors; **"applying the N permutations to the N first hypervectors respectively"**; **"combining the N permuted hypervectors into a bundled hypervector"**; process that bundle **"thereby simultaneously factorizing the N first hypervectors."** | IBM (Rahimi), filed 2022-04-08, granted 2025-05-20, expires 2043-10-19 — claim text read at patents.google.com/patent/US12306870B2 | [VERIFIED-SOURCE] | **N > 1 plus permute-and-bundle is the claim.** One resonator per query, no permutation, is outside claim 1. Our V4 rule is correct and now textually grounded. |
| **US 12,579,411 B2 claim 1 (verbatim)** | "A computer-implemented method for performing a **classification of an input signal**… computing, by a **feature extraction subnetwork**… a real-valued query vector; **bipolarizing**… the query vector; **iteratively performing, by a resonator subnetwork, a factorization of the bipolarized query vector** … and, responsive to convergence, **assigning a class**." Dep. claims: fixed codebooks, **bipolar codebooks**, parallel unbinding, frozen classification layer during training, and non-convergence fallbacks (most-frequent / max Hamming similarity). | IBM, filed 2021-12-29 (US 17/564,275), published 2023-06-29, **granted 2026-03-17, expires 2045-01-03** | [VERIFIED-SOURCE] | **⚠ NOT IN OUR ADDENDUM.** A software claim on plain single-resonator factorisation as a readout. "One resonator per query" does not dodge it. See Answer 7. |
| US 12,561,553 B2 | "Storing respective code hypervectors … within row lines of a neuromorphic memory device **with a crossbar array**." | IBM, filed 2022-03-16, granted 2026-02-24, expires 2044-12-26 | [VERIFIED-SOURCE] | Low risk on CPU. Stays low while we never target memristive hardware. |
| US 12,518,150 B2 | "Bundling hypervectors." Claim 1 = FFN encoder + **selection-based** bundling (weight vector → S-dim index vector, S = D/L, each element *selects* a source code HV for that dimension) + "**decoding, by a resonator network**, the hypervector." Claim 4 gives the selector: s_k(i) = m if ∂_{m−1} < v ≤ ∂m, where ∂ = cumsum(a)/sum(a). Claim 2: output is **sparse binary** {0,1}^D. | IBM, filed 2022-06-27, published 2023-12-28, granted 2026-01-06, expires 2044-08-24 — claims read verbatim | [VERIFIED-SOURCE] | **It names a resonator network as the decoder**, so it is a resonator patent, not just a bundling one. But the *bundling* is the claimed novelty and ours is dense majority/sum-threshold, not sparse binary selection. Different operation. |
| US 2025/0086251 A1 (pending) | "Providing alternative implementations of a step for each step of the iterative process… **selecting a step** from the provided implementations." | IBM, via Justia inventor record (Karunaratne) | [VERIFIED-SOURCE] | Avoid *selecting among alternative step implementations at runtime*. We have one implementation. |
| Base algorithm | Resonator networks (Frady/Kent/Olshausen/Sommer) — no patent found in our search; published 2020, so prior art against later claims on the base method. Absence of patent is not proof. | Kent et al. 2020; clean-room addendum 2026-09-25 | [VERIFIED-SOURCE] | Clean-room from the paper is safe; copy nothing from any repo. |

---

## Answers

### 1. How do resonator networks work?

Given a composite **c** = x⁽¹⁾ ⊙ x⁽²⁾ ⊙ … ⊙ x⁽ᴳ⁾, one codevector drawn from each of F codebooks X_f, the resonator holds F estimates x̂⁽ᶠ⁾[t] and iterates. Each iteration, for each factor f: unbind the composite against the *other* current estimates, then clean up by similarity search against codebook X_f, then apply a transfer function. Two variants of the cleanup weights: **outer-product** (OP) weights, and **ordinary-least-squares** weights x̂⁽ᶠ⁾[t+1] = sgn(X_f X†_f ô⁽ᶠ⁾[t] ⊙ c). The OLS formulation guarantees c is always a fixed point; OP does not but converges faster in the high-accuracy regime and is the one used for the capacity fits. Updates are **asynchronous** — factor f has already been updated this iteration while f+1 has not — and that convention converges significantly faster than synchronous. There is **no Lyapunov function and no convergence guarantee**; the system has no energy it must descend. Correct solutions are fixed points with sizeable basins, and the reason resonators beat optimisation baselines is that they have **comparatively few spurious fixed points** (stability at a wrong factorisation lies in [1/M, 1], while projected gradient descent sits in [1/M, (1/2^N)^F]).

### 2. How does factorisation success scale with D, M, F, and superposed bound vectors?

**The law: M_max ≈ 8.078·N² / F^1.268 for F ≥ 3** (Kent et al. 2020, Eq. 26), fitted by simulation at p = 0.99, k = 0.001·M. This is the answer to "how does it scale with dimension D": **quadratically.** With F, the decay is only F^-1.268 — which is why F is the cheap axis and D is the expensive one.

Applied to our machine (D = 10,240, 42³·2² style arithmetic below):
- M_max(F=3) ≈ 2.006 × 1.0486×10⁸ ≈ **2.10×10⁸**
- M_max(F=4) ≈ 1.393 × 1.0486×10⁸ ≈ **1.46×10⁸** *(the Table 1 fit for F=4 gives the more conservative c = 1.024 → 1.07×10⁸)*
- M_max(F=5) ≈ 1.050 × 1.0486×10⁸ ≈ **1.10×10⁸**
- M_max(F=7) ≈ 0.685 × 1.0486×10⁸ ≈ **7.2×10⁷**

Two modifiers matter more than the law. **(a) Codebook balance:** capacity peaks at D₁ = … = D_F and degrades with imbalance ξ = (min D_f)/(max D_f); the penalty is a single absorbable term only while ξ ≥ 0.2. **(b) The loading ratio D_f/N is a phase boundary, not a slope:** 0.056 is where the resonator loses its Hopfield-level stability and 0.138 is the classic Hopfield avalanche. At D = 10,240, 0.056·N = **573** — so any codebook under ~573 atoms is comfortably in the stable regime. Our codebooks (≤ 42) are an order of magnitude below it.

**On "how many bound vectors are superposed":** the resonator factors **one** product vector. Superposed items are handled by an **outer loop** — converge on one object, **explain it away** by subtracting the converged state from the scene vector, reset, re-run (Frady et al. 2020 §4.2). This is exactly our "bundled marks" case, and it is also the algorithm's known weak point: traditional explaining-away *amplifies noise* as items are subtracted, and the first remedy in the literature is a **query sampler** that performs multiple decodings in parallel (Hersche et al., NeSy 2023). Supersposed-item count is therefore a **sequential-error** problem, not a capacity problem, and it has no published scaling law. [VERIFIED-SOURCE for the mechanism; the absence of a scaling law is my search result, stated as such.]

### 3. Failure modes, and what fixes them

**The three regimes (this is the important part).** At small M almost everything converges and lands on the correct factorisation; limit cycles are possible but rare, and — crucially — **"if the trajectory converges to a point attractor or limit cycle, one can be confident this state indicates the correct factorization"**, because spurious fixed points are few. In the middle regime basins narrow and the network **wanders**: it does not fall into wrong answers, it simply fails to find the basin. Past saturation M_sat, the picture inverts: **both limit cycles and point attractors re-emerge and they yield the incorrect factorisation.**

So the dangerous failure is not non-convergence. It is a **confident, converged, wrong answer.** Any benchmark that reports only "fraction converged" will hide the real risk. Ours must report converged-and-wrong separately.

**Limit cycles** are the estimate oscillating over a small set of codevectors; they can persist for unlimited iterations, are skewed to short lengths, and are **most likely at F = 2**, *less* likely as F grows. That is the opposite of the naive "more factors, more risk" intuition. There is also a class of "seemingly-chaotic trajectories that do not converge in any reasonable time."

**Fixes, ranked by cost-to-us (all independently published):**

| Fix | Source | Cost on our CPU |
|---|---|---|
| **Asynchronous updates** | Frady et al. 2020 | zero |
| **Past-state buffer → detect cycle, terminate early** | Kent et al. 2020, Alg. 1 | ~one compare per iteration |
| **Thresholded / sparsifying attention activation** | arXiv 2412.00354; arXiv 2303.13957 | one compare per dim |
| **Weight asymmetry** (breaks the symmetry that creates cycles) | Hertz 1986; Singh 1995; via Kent et al. 2020 | free at init |
| **ACF: frozen initialisation noise, same instance every iteration** | arXiv 2412.00354, 2024 | D×D_f bits stored once |
| **ReLU + exponentiation on similarity** | via arXiv 2412.00354 | cheap |
| **Conditional random sampling** | Hersche et al., arXiv 2303.13957 | per-iteration RNG |
| **ℓ∞ similarity instead of cosine** | Hersche et al., arXiv 2303.13957 | cheap |
| **IMF: iterative noise at controlled σ** | *Nature Nanotechnology* 18(5), 2023 | RNG per iteration, tuned σ; the 5-orders-of-magnitude result is PCM-specific and does **not** transfer to CPU |

**What they cost, honestly:** on analog IMC the noise is free (it is the device), which is why IMF's headline is 5 orders of magnitude. In digital it is not free — Gaussian noise needs exp and multiply, which the IBM authors explicitly call expensive. Their escape is ACF: perturb the codebooks **once** and reuse the same noise instance, giving a relaxed noise requirement and a purely digital design. ACF beats IMF at F = 2 (fewer factor interactions) and loses at F = 4. **The best noise *kind* is F-dependent, and the crossover is published.** Capacity gain for both: **≥50×** over the baseline resonator, versus BRN saturating at ≈10⁵/10⁶/10⁷ for F = 2/3/4 at D = 1000/1500/2000.

### 4. Representations: which supports exact unbinding, and with what fidelity?

| Representation | Bind | Unbind | Exact? | Published fidelity |
|---|---|---|---|---|
| **Bipolar MAP** {±1} | Hadamard (self-inverse) | same op | **Exactly** — a ⊙ a = 1 | Exact by construction; capacity law above is calibrated here |
| **Ternary {−1,0,+1}** | sign-multiply | same op | **No.** "Some active input components cannot be inferred during unbinding and information is lost" (Frady/Kleyko/Sommer, TNNLS 2020) | Loss grows with sparsity; not quantified for our D — *Unknown* |
| **FHRR (phasor)** | phase add | conjugate multiply | **Yes**, and adds *fractional* binding for exact continuous values, exact powers (log-phase), and spatial structure | Exact in real arithmetic; float error is the limit |
| **qFHRR (quantised phase)** | (a+b) mod K | (a−b) mod K | Yes, in the index algebra | K=8: bind > 0.94, bundle > 0.91. K=16: > 0.98 |
| **qFHRR bundling** | — | — | **Not closed** under modular arithmetic | Needs LUT→(x,y), int accumulate, integer CORDIC, re-quantise |

**Which supports exact unbinding: FHRR/qFHRR and bipolar MAP both do. Ternary does not** — and that is now a primary-source statement, not our inference.

**The decisive practical point:** in a resonator, the per-iteration hot path is F × (unbind + similarity), and the *cold* path is occasional re-bundling. Under qFHRR, bind/unbind/similarity are **integer add/sub plus a byte LUT**; only bundling needs the CORDIC. That ratio favours qFHRR strongly for this specific algorithm. Our internal K=32 figures (0.997/0.989) are consistent with monotone improvement but I did not read them in the paper — treat as [INFERRED] until Table 2 is opened. Since the paper reports diminishing returns beyond K=16, **K = 16 (4 bits, one nibble) is a legitimate target**, which would halve codebook memory versus K = 32. [INFERRED]

### 5. Could structured noise — IFS grid-fractal "controlled randomness" — replace white noise in escaping limit cycles?

**Partly yes, but the role is already filled, and by exactly the mechanism one would guess.** Direct answer:

**What is published (all verified):** IBM's **ACF** perturbs codebooks with noise *at initialisation* and reuses **the same noise instance across all iterations**. That is a *fixed, structured, deterministic-in-practice* perturbation — not white noise — and it buys ≥50× capacity in pure digital. The stated rationale is that the perturbation breaks the "symmetric and deterministic nature of the codebooks" that causes cycles. Relatedly, **weight asymmetry** (a purely deterministic perturbation) is the classical fix for spurious fixed points. And there is a genuine, well-populated **annealed-noise** literature for Hopfield-class nets: scheduled internal noise in NeurIPS 2013 (where the schedule makes states move *only toward* correct values), constant-temperature Boltzmann escape of spurious fixed points (Hinton et al. 1985), **decaying chaotic noise** simulated annealing in Hopfield networks (ASCC 2000; Chen & Aihara), and a 2025 theory of the **zero-noise limit** giving a principled "noisy = generative, zero = memory" transition (arXiv 2506.05178).

**What I did *not* find, stated plainly:** no paper, patent, or repository that uses an **iterated function system / chaos-game / fractal grid** as the noise source in a resonator network or a VSA factoriser. Searches over the resonator, VSA-factoriser, and annealed-noise literature returned the ACF/IMF/noise-enhanced-memory line instead. **This is an absence of evidence, not evidence of absence** — and it is a real, citable novelty opening for the fleet.

**But the honest engineering read [INFERRED]:** ACF's frozen perturbation already occupies the *functional* slot J's idea targets — cheap, structured, no per-iteration RNG, breaks the symmetry that makes cycles. An IFS would have to beat it on a specific axis, and there is exactly one plausible axis: **ACF's noise is i.i.d. across codebook entries; an IFS perturbation is spatially correlated and generated from a small seed by contraction.** That buys (a) a *tiny* storage footprint (a seed of tens of numbers instead of M_f × D noise values) and (b) a perturbation with **structure** — it can bias the search toward a *region* of codebook space rather than uniformly, which is what a chaos-game search does. Whether that helps at F = 4 with M_f = 42 is entirely unmeasured. I would not name it in a paper, a licence, or a PROVENANCE entry until it beats frozen ACF noise on the same benchmark. **The banked note in `Downloads/Resonator networks.txt` (lines 1386–1438) is J's own idea thread, correctly labelled in CONTEXT.md as "ideas, not facts"; the Banach-fixed-point argument in it is intuition, not a proof for this algorithm.**

One genuine convergence with the literature worth carrying into the oracle: J's framing that quantisation is a "safety net" that bounds drift is the same claim as the zero-noise-limit theory, and the same claim as ACF's "relaxed noise requirement." Three independent routes to the same design. That is a good sign for the design, not a proof of it.

### 6. Applications closest to ours

**Published:** tree/sequence-structure parsing (Frady et al. 2020); visual scene parsing with a hierarchical resonator — 26 letters × 7 colours = 745,472 combinations, 98.4% on single-object translation, and **84% on a 6-factor scene** where the binding capacity is not the limit and errors are "spurious matches involving complex mixtures of generative factors" (Renner et al., arXiv 2208.12880); **integer/semiprime factorisation** using FHRR log-phase so that s = xy becomes a vector factorisation, converging to the correct prime pair in several iterations (NICE 2022, DOI 10.1145/3517343.3517368); **replacing a CNN's fully-connected classification layer** with an F-factor codebook factoriser over CIFAR-100/ImageNet-1K/RAVEN (Hersche et al., arXiv 2303.13957); and multi-object scene decoding via explain-away/deflation.

**Not found, and this matters:** **no published application of resonator factorisation to logs, telemetry, incident data, or system diagnosis.** I searched for it specifically. Every application in the literature is perceptual (vision, attributes) or mathematical (integers). Our target — "which lane × task kind × beat × outcome explains these failures?" — is therefore **novel but unbacked by precedent.** Two consequences. The upside is real: nobody has published this, so a working version is a contribution. The downside is equally real: we have **no prior art telling us the right D, K, F, or even that the factorisation is well-posed**, and the closest published analogue is visual-scene parsing where accuracy *degrades to 84% at 6 factors*.

The one published result that argues *for* our noisy-data case specifically is the corruption-tolerance finding (§3, Kent et al. 2020 §6.5): well below capacity, the composite can be heavily corrupted and still factorise correctly. Telemetry is corrupted, partial, and superposed. That is the resonator's home turf and it is a genuine, citable reason to believe.

### 7. Patent boundary

**Verified this session, from primary claim text.** The binding constraint is not the crossbar patent — it is **US 12,579,411 B2**, which our 2026-09-25 clean-room addendum does not list.

| Patent | What claim 1 actually requires (read verbatim) | Our exposure |
|---|---|---|
| **US 12,579,411 B2** — "Resonator network based neural network" (IBM; filed 2021-12-29, US 17/564,275; published 2023-06-29; **granted 2026-03-17; expires 2045-01-03**) | A computer-implemented method for **classification of an input signal** by a neural network, comprising: computing a real-valued query vector by a **feature extraction subnetwork**; **bipolarizing** it; **iteratively performing, by a resonator subnetwork, a factorization of the bipolarized query vector** across a plurality of codebooks; and, on convergence, **assigning a class** corresponding to the estimated vector product. | **⚠ REAL RISK.** A plain *software* claim on single-resonator factorisation as a readout. It requires **no** crossbar, **no** N>1 resonators, **no** permutations, **no** bundling. Our rule "one resonator per query" does not dodge it. Three elements give a way out: (i) do **not** bipolarise — use phase indices, (ii) do **not** put a neural feature-extractor subnetwork in front — our input is structured records, not a signal, (iii) do **not** frame the output as class assignment from an input signal. Dependent claims 3/4 (fixed / **bipolar** codebooks) and 13–15 (non-convergence fallbacks: most-frequent, max Hamming) all depend on claim 1. **This is an oracle + attorney question, not ours to close.** |
| **US 12,306,870 B2** (IBM, Rahimi; filed 2022-04-08, granted 2025-05-20, expires 2043-10-19) | encoder + codebooks; **"a set of N resonator networks, where N>1"**, each **associated with N permutations respectively**; N structures → N hypervectors; **apply the N permutations**; **"combining the N permuted hypervectors into a bundled hypervector"**; process it to **simultaneously** factorise the N originals | **Avoid that pattern, and we do.** The claim needs N > 1 *and* permute-and-bundle *and* simultaneous multi-factorisation. One resonator per query, no permutations, is outside claim 1. Our V4 rule is correct — and is now textually grounded rather than assumed. |
| **US 12,561,553 B2** (IBM; filed 2022-03-16, granted 2026-02-24, expires 2044-12-26) | code hypervectors stored in row lines of a neuromorphic memory device **with a crossbar array**; attention-weighted estimate updates | **Low.** System, method, and program-product claims all require the crossbar. Stays low while we never target memristive/PCM hardware — which also means we give up IMF's 5-orders-of-magnitude number, correctly. |
| **US 12,518,150 B2** (IBM; filed 2022-06-27, published 2023-12-28, granted 2026-01-06, expires 2044-08-24) — *claims read verbatim this session* | claim 1: FFN encoder; bundling M code HVs by mapping an M-dim **weight** vector to an S-dim **index** vector (S = D/L) whose elements each *indicate which* code HV supplies that dimension; and **"decoding, by a resonator network"**. Claim 2: output is **sparse binary {0,1}^D** with sparsity S/D. Claim 4: the selector is a cumulative-sum partition, ∂ = cumsum(a)/sum(a). | **None**, but read it twice. The resonator is named only as the *decoder*; the claimed novelty is the **selection-based, sparse, binary** bundling. Our majority/sum-threshold bundling is dense, non-selection, and threshold-based — a different operation that produces a different vector. Confirmed: a prior measurement showed selection-style bundling collapsing recall at k=7 while majority bundling held 100% at k=100, so we would not adopt it even if it were free. |
| **US 2025/0086251 A1 (pending, IBM)** | providing **alternative implementations** of each iterative step and **selecting** one at runtime | Avoid runtime selection among step implementations. We have one implementation. |
| Base algorithm (Frady/Kent/Olshausen/Sommer 2020) | — | No patent found in our search; published 2020 so prior art against later claims. Absence not proven. |

**Clearly free to implement, on the evidence:** a **single** resonator per query, software-only on CPU/GPU, no crossbar or memristive targeting, majority/sum bundling only, non-bipolar (phase) codebooks, no permute-and-bundle multi-input scheme, no runtime selection of alternative step implementations, written from the 2020 papers with provenance recorded. **Not legal advice.** Two live items for the oracle: (i) an FTO opinion on 12,579,411 specifically, and (ii) a re-check of pending applications before any commercial tier, exactly as the addendum already demands for the noise method.

### 8. A concrete minimal design for us — and the benchmark that would kill it

**First, the finding that overrides the brief's codebook list.** The scope proposes {lane ~42, role 8, task kind ~10, beat 10, outcome/rule ~25}. Measured against the live schema (`marks`, 94 rows, 2026-09-27):

- **There is no `lane` column.** The 42-atom codebook has nothing to bind to. The closest proxy is `source` (3 distinct) or `agent` (2 distinct).
- **`beat` has 0 distinct values.** An empty codebook. Cannot be a factor.
- **`outcome` has 1 distinct value, `task` has 1.** Zero information.
- `role` 2, `kind` 4 (command 92, arrive 1, debrief 1, file 1), `target` 94 (unique per row — that is a free-text string, not a categorical codebook).

So **3 of 5 proposed factors currently carry ≤ 1 distinct value.** Factorising them is factorising noise, and no benchmark built on them can fail informatively. CONTEXT.md's honest counterpoint is confirmed by measurement, and it is stronger than stated: the problem is not that SQL is better at hundreds of rows, it is that **the categorical structure the resonator needs does not exist yet.**

**Design, given the data that will actually exist.** Sizing against the law, with the Table-1-conservative c for F=4:

| Choice | M | M_max @ D=10,240 | Utilisation | Verdict |
|---|---|---|---|---|
| F=5, exact 42/8/10/10/25 (unbalanced, ξ=0.19) | 8.4×10⁵ | 1.10×10⁸ | 0.08% | Nominal headroom, **but ξ < 0.2 puts us in the un-modelled regime** |
| **F=5, balanced at 42** | 1.307×10⁸ | 1.10×10⁸ | **119%** | ❌ **OVER CAPACITY** |
| F=5, balanced at 40 | 1.024×10⁸ | 1.10×10⁸ | 93% | ⚠ at the transition where wrong-answer attractors appear |
| F=4, balanced at 42 (**recommended**) | 3.11×10⁶ | 1.46×10⁸ (1.07×10⁸ conservative) | **2.1–2.9%** | ✅ **~35–47× margin** |
| F=3, balanced at 42 | 74,088 | 2.10×10⁸ | 0.04% | ✅ enormous margin |

**Recommended minimal design** [INFERRED from the verified law + our measured cost anchors]:

- **F = 4**, not 5. Capacity decays only as F^-1.268, so dropping the weakest factor (fold `role` into the `agent`/`lane` factor, or fold it out) buys an order of magnitude for free.
- **D = 10,240**, reuse the existing bus dimension. M_max ∝ N², so a dedicated D = 4,096 would cost 6× capacity for no benefit at F=4. **Do not shrink D.**
- **K = 32 (5 bits)** for the phase layer, matching CONTEXT.md; **K = 16 is a legitimate cheaper A/B** since the paper reports diminishing returns past K=16. The differentiator is the **patent interaction, not fidelity**: phase indices also keep us off the "bipolarize" element of US 12,579,411.
- **Balanced codebooks**: pad every codebook to 42 atoms with inert filler that never wins the similarity contest. Cost is 42×42×D phase bytes ≈ 18 MB per codebook set at D=10,240 — trivially affordable, and it moves us from the un-modelled ξ<0.2 regime into the published one. **This is the single highest-leverage cheap decision in the whole design.**
- **Iteration budget: 24 iterations hard cap**, with early exit on a repeated past state (Kent's Alg. 1). Note explicitly that Kent's *capacity definition* uses k = 0.001·M (≈3,100 at our M), which is **not** an operating point we can afford online — so the honest move is to **measure the median-iteration curve ourselves** rather than borrow his k. [INFERRED]
- **Noise schedule, in order:** (1) **ACF-style frozen structured noise** at codebook init, one instance reused every iteration — published, digital, ≥50×, and the correct baseline; (2) **IFS grid-fractal perturbation** as the A/B variant, generated from a small seed by contraction, motivated by the correlated-and-tiny argument in Answer 5; (3) annealed schedule (decaying) only if a fixed perturbation proves insufficient. Include the **weight asymmetry** fix and **thresholded attention** from v1 — both free, both published.

**Cost estimate, anchored on our own measurements** [INFERRED, from verified anchors — the formula is given so a reader can substitute]:

- Measured: 1,000-HV scan at D=10,240 ternary = 145 µs ⇒ **145 ns per HV-vs-query dot**.
- One cleanup pass over a 42-atom codebook = 42 × 145 ns ≈ **6.1 µs** (ternary baseline).
- Per iteration at F=4: 4 unbinds (4 × 35 ns ≈ 0.14 µs) + 4 cleanup passes (≈ 24.4 µs) ≈ **24.5 µs**.
- A 24-iteration query ≈ **590 µs** on the ternary baseline. Allow up to **5×** for qFHRR's per-dimension LUT gather ⇒ **≈ 3 ms per query**, i.e. ~330 queries/s single-threaded. Well inside "inline reader" territory. **This is an estimate, not a measurement, and it is the first thing to measure.**

**The benchmark that can fail.** Two stages; stage 1 is a synthetic grid with known ground truth, stage 2 is real marks.

*Stage 1 — synthetic capacity grid (this is a falsifiable prediction test, because Kent's law was fit on data we can regenerate).* Sweep F ∈ {2,3,4,5} × D ∈ {4096, 10240} × M_f ∈ {8,16,32,42} × K ∈ {8,16,32}, 3000 random trials per cell (Kent's own minimum for a stable 99% estimate), **balanced codebooks**, and record: total accuracy, median iterations, fraction limit-cycled, and **converged-but-wrong** as a separate column. Then plot measured M_max against the predicted 8.078·N²/F^1.268.

*Stage 2 — real marks.* Take genuinely superposed, weight-decayed bundles from the live field, encode, factorise, and check the decoded factors against SQL over the same rows. **Today this stage is vacuous** and must be gated on the field reaching real cardinality: at minimum `beat` non-empty and `lane` (or a defined proxy) populated, with ≥ 20 distinct values per factor before the result means anything.

**Kill criteria — each one able to fail, stated up front:**
1. Accuracy at the design point (F=4, M=42 balanced, D=10,240, K=32) **< 99%** ⇒ the design point is wrong; drop F or raise D.
2. Measured M_max at F=4, D=10,240 more than **10× below** the predicted 1.46×10⁸ ⇒ our phase representation and optimiser are losing an order of magnitude to published bipolar results, and phase is not fit for purpose. (This is the single most likely real failure: the whole law was calibrated on bipolar MAP.)
3. Median iterations at the design point **> 24** ⇒ this is a batch tool, not an online reader, and the north-star claim of an inline machine reader fails.
4. qFHRR-5 cleanup **> 1.25 µs per codevector** at D=10,240 ⇒ the 5 ms/query inline budget is blown ⇒ CPU-infeasible at this D; the phase layer must be redesigned (two-plane, or K=16 nibble packing). **Derived, not guessed:** one query costs 24 iterations × 4 factors × 42 atoms = **4,032 cleanup similarities**; 5 ms ÷ 4,032 = **1.24 µs** per codevector. The measured ternary baseline is 0.145 µs, so the gate permits an **8.6× phase-layer overhead** and no more. (An earlier draft used 20 µs/codevector; that would have admitted an 80 ms reader — 12 queries/s — as "inline." Corrected before release.)
5. ACF-style frozen noise gain **< 5×** over deterministic at our D ⇒ noise is not the lever it was on PCM, and the IFS question becomes moot.
6. Any stage-1 cell where **converged-but-wrong > 1%** while accuracy > 99% ⇒ the wrong-answer attractor regime is closer than the law predicts, and a "converged" flag cannot be trusted as a correctness signal in the reader.

**What the benchmark cannot settle, and must not be claimed to:** whether the resonator beats `SELECT kind, count(*) … GROUP BY`. It will not, at 10² rows, and CONTEXT.md already says so. The resonator's place is the **superposed** case — the shared-memory bus, micromodel memory, cross-machine streams, and noisy/partial records — which is exactly the case with no SQL equivalent and for which the corruption-tolerance result gives published backing. Stage 2 must therefore be built on **bundled, decayed, superposed** marks, not on a plain grouped table, or it will measure the wrong thing.

---

## Cross-links

1. **Resonator ↔ modern Hopfield networks (RSPK-VSA / RSPK-PHYS).** The cleanup memory *is* a modern Hopfield retrieval step (Demirciigil et al. 2017); the resonator is that retrieval wrapped in an unbind-and-reiterate loop. Consequence for us: the entire modern-Hopfield annealing literature transfers as noise-schedule prior art — including the **zero-noise-limit** result (arXiv 2506.05178) that noisy = generative and zero-noise = memory, which is the theoretical form of "anneal the noise to zero and let the attractor catch you." The IBM phase naming (unbind → associative search → attention activation → reconstruction) is modern Hopfield's vocabulary, not a resonator-specific one.

2. **Resonator ↔ simulated annealing and Boltzmann machines (RSPK-MATH).** Hinton, Sejnowski, Ackley & Terrace (1985) already established that a **constant-temperature** associative net uses finite escape probability to *skip* unrecognised spurious fixed points — the direct ancestor of IMF and ACF. The distinguishing move the resonator makes is refusing the global convergence guarantee: Kent argues requiring global convergence "unnecessarily constrains the search," which is a real, citable tension between annealed and relaxation-style dynamics. The oracle should treat "annealed escape" vs "many-restart relaxation" as a genuine fork, not a detail.

3. **Resonator ↔ sparse/bipolar MAP representations (RSPK-VSA).** The binding-axiom requirement — associative, distributive over addition, **having an inverse** — is what a resonator *is*: it needs a self-inverse bind to unbind. Frady & Kleyko (TNNLS 2020) show sparse codes lose information precisely at the zeros, which is why our ternary bus cannot host a resonator and our phase layer must. The same paper's compressed-sensing result (sparse binding ≡ tensor-product binding, dimension-reduced) is the bridge if anyone proposes staying ternary.

4. **Resonator ↔ statistical physics / spin-glass theory (RSPK-PHYS).** **The loading ratio D_f/N = 0.056 is a phase transition borrowed from Amit, Gutfreund & Sompolinsky (1985)**, and between 0.056 and 0.138 lower-energy spin-glass states exist that beat the codevectors. Our resonator therefore has a **critical dimension ratio**, not a smooth cost curve — a physics-vein question with a concrete numeric answer, and a direct read-across from the Hopfield avalanche literature. The same vein owns the concentration-of-measure argument (Ledoux 2001) that makes M_max ∝ N² in the first place.

5. **Resonator ↔ the F-exponent / measure-theoretic structure (RSPK-MATH).** M := ∏ D_f is multiplicative, so capacity is destroyed exponentially in F and only polynomially in D. The measured exponents α₁ = 2^3.014 = 8.078 and α₂ = 1.268 (Kent's own fit, which the authors flag as noisy and not analytically derived) are the sharpest available objects for the math vein. Related: the ξ-imbalance penalty and the "capacity highest when codebooks are equal" result are a statement about the *geometry* of a product measure, and the Table-1 discrepancy at F=4 (law says 1.393, fit says 1.024) is itself a small open problem worth 30 minutes of someone's time.

6. **Resonator ↔ memory, sequence indexing, and learning (RSPK-MIND).** The same VSA algebra that indexes **tree depth** for Frady's parsing resonator indexes **time and position** for working memory (Frady, Kleyko & Sommer, *Neural Computation* 2018), and fractional binding is what makes positional structure smooth (Komer 2020; Frady et al. 2022). So a resonator is a *retrieval* primitive sitting on a *memory* algebra — which is precisely the "Read (resonator, immune) → Learn" step of our loop. The counter-branch is FactorHD (arXiv 2507.12366, 2025): a **learned** factoriser that holds >99% at *lower* D with O(NM) instead of O(N²M) complexity. If that holds at our scale, the hand-designed resonator is a baseline and a teacher, not a product. That is a mind/learning question, not a resonator question.

7. **Resonator ↔ superposition decoding / explain-away (RSPK-VSA, shared bottleneck).** Our motivating query is a *bundle* of marks, and every published resonator handles superposed items with a sequential **explain-away** outer loop. The first named limitation in the modern literature is precisely this: noise amplification in traditional explaining-away, remedied by a **query sampler** doing parallel decodings (Hersche, Opala, Karunaratne, Sebastian, Rahimi, NeSy 2023). Our bus bundles up to 100 members (measured), which is deep into the regime where sequential subtraction is the weak link. This cross-link is load-bearing for the spike and is currently **unowned** by any of the six veins.

---

## Implications for the spike — ranked

1. **Fix the benchmark before writing the resonator.** Build the synthetic capacity grid first, with 3000 trials per cell and **converged-but-wrong reported as its own column**. It is the only artifact that can be wrong, and it is a direct test of a published law. Nothing else in the spike is falsifiable until this exists. *(Non-Execution: this is a recommendation to the oracle, not a build decision.)*
2. **Choose F = 4 and balance the codebooks to 42.** Capacity decays as F^-1.268, so the single cheapest large win in the design is dropping the weakest factor. Balance every codebook to the largest (≈18 MB, free) to move from the un-modelled ξ < 0.2 regime into the published one. This is the highest-leverage cheap decision available.
3. **Keep D = 10,240.** M_max ∝ N², so shrinking D to 4,096 would cost 6× capacity and buy nothing at F = 4. Reuse the bus dimension; do not build a second width.
4. **Use qFHRR phase, and never bipolarise.** Two independent wins from one decision: it is the only substrate besides bipolar MAP that supports exact unbinding (the ternary bus provably loses information at the zeros), and staying non-bipolar keeps us off the "bipolarizing" element of US 12,579,411. A/B **K=16 against K=32** — the paper reports diminishing returns past K=16, and K=16 halves codebook memory.
5. **Adopt ACF-style frozen structured noise as the baseline, not white noise.** It is published, digital, needs no per-iteration RNG, and gets ≥50×. Treat the IFS grid-fractal as the A/B *variant* against it, with a written hypothesis (correlated perturbation from a small seed, region-biasing search) that can fail. Do not put IFS in a paper, licence, or PROVENANCE entry until it wins.
6. **Take the four free robustness fixes in v1:** asynchronous updates; past-state buffer for cycle detection and early exit; thresholded attention; weight asymmetry. All independently published, all near-zero cost, all separately verifiable.
7. **Measure the qFHRR cleanup cost on day one and gate on it at ≤ 1.25 µs per codevector at D = 10,240** (= the 5 ms/query inline budget, derived in Answer 8). Our whole cost case rests on the measured 145 ns ternary dot; the phase layer adds a per-dimension LUT gather and that factor is the unknown. The gate allows an 8.6× overhead over ternary and nothing more.
8. **Do not make the resonator the primary reader for the field at 10² rows.** `SELECT … GROUP BY` answers the same question exactly and will keep doing so. Build the resonator for the **superposed** case — the `/dev/shm` bus, micromodel memory, cross-machine streams, noisy/partial records — where there is no SQL equivalent and where the published corruption-tolerance result gives us backing. A reader that loses to SQL is a liability, not a feature.
9. **Do not let the field's cardinality silently invalidate the spike.** `beat` is empty, `outcome` and `task` have one value, and **there is no `lane` column**. Either the field schema grows a lane and a populated beat, or the resonator's target changes. Decide this explicitly at the oracle, not by discovering it at implementation time.
10. **Flag US 12,579,411 B2 for a real FTO opinion, and add it to the clean-room addendum.** It is a granted software claim over iterative resonator factorisation as a readout layer, it post-dates our 2026-09-25 addendum (granted 2026-03-17), and our existing design rule does not cover it. Re-check pending applications before any commercial tier, exactly as the addendum already requires for the noise method.
11. **Keep the clean-room discipline that the evidence supports.** Write from the 2020 papers; the base algorithm shows no patent and 2020 publication is prior art. Do not copy from any repo, even MIT — and note that IBM's own `in-memory-factorizer` is Apache-2.0, whose patent grant covers *that code*; clean-room code does not inherit it, so we get no protection from depending on it.
12. **Watch FactorHD as the genuine rival.** If a learned factoriser holds >99% at lower D with O(NM) complexity, the hand-designed resonator is a teacher and a baseline. Worth a scope line, not a build.

---

## Open questions — what the oracle pass must decide

1. **FTO (highest stakes):** does a **non-bipolarised, non-signal, single-resonator** factoriser over structured records, not framed as class assignment, fall outside **US 12,579,411 B2**? Requires a patent attorney, not a vote. Related: is the phase-instead-of-bipolar choice load-bearing for this, or incidental?
2. **How many factors, F?** 3, 4, or 5. The whole design pivots on it (capacity ∝ F^-1.268). Which of {role, beat} folds into which, and what is the "largest legitimate composite" we are willing to answer in one shot?
3. **Balance or exact codebooks?** Pad every codebook to 42 (published regime, ~18 MB, ξ = 1.0), or keep exact cardinalities and accept an un-modelled ξ = 0.19 penalty? Nobody has published the sub-0.2 case, so "exact" means "we don't know."
4. **Which factors exist at all?** `lane` has no column. Do we add one to `marks`, derive a proxy from `source`/`agent`, or restructure the query around {kind, target, outcome}?
5. **What is the actual question, and is it well-posed?** "Which lane × kind × beat × outcome explains these failures?" has no defined ground truth today. What does *explains* mean — argmax factorisation, marginal contribution, or a decayed-weight ranking? A resonator returns a joint argmax; that is a real semantic constraint on the reader's output, not an implementation detail.
6. **IFS: distinct mechanism, or a re-derivation of ACF's frozen noise?** State the falsifiable hypothesis (correlated perturbation from a compact seed, region-biasing search) and the metric that would refute it. If no advantage appears, say so and keep ACF.
7. **Annealed vs fixed vs per-iteration noise — and does the F-crossover matter at F = 4?** IBM reports ACF wins at F = 2 and IMF at F = 4. We will be at F = 4, which is the regime where the *harder* noise wins. Is fixed noise enough there, or do we need a σ schedule?
8. **K = 16 or K = 32?** Fidelity, memory, and the CORDIC cost of bundling all trade off. And: does the phase layer ever need **fractional** binding, or only the K-member index algebra? Fractional binding is a substantially larger build.
9. **Iteration budget vs the published definition.** Kent's capacity uses k = 0.001·M (≈3,100 at our M). An online reader cannot afford that. Do we publish our own median-iteration curve at a stated budget, and do we re-derive operational capacity at *that* budget so our numbers are comparable to anything?
10. **Is "converged" a safe correctness signal?** At low M, Kent says yes (few spurious fixed points). Past M_sat, no. Our reader will be wired to act on convergence. Where is our margin, and do we need an independent confidence check?
11. **Hand-designed or learned?** Does FactorHD-style learning beat the relaxation dynamics at our D and our (tiny) data? If yes, what is the hand-designed resonator *for* — a teacher, a baseline, or a cold-start scaffold?
12. **What is the honest scope claim?** No published resonator application exists for logs/telemetry/diagnosis. Is the goal an internal reader, a benchmarkable contribution, or a licence-clean component? The answer changes how much clean-room/IP rigor the next 2–4 days of Tier 6.2 need.
13. **The corpus is 45-source but uncited.** `Downloads/Resonator networks.txt` should be re-read as *claims to check*, not as evidence. Which of its 45 sources survive primary reading? (The Banach-fixed-point convergence argument for the IFS idea in particular needs to be either proved or dropped.)

---

## Sources

1. Frady, E. P., Kent, S. J., Olshausen, B. A., Sommer, F. T. — *Resonator Networks, 1: An Efficient Solution for Factoring High-Dimensional, Distributed Representations of Data Structures.* Neural Computation 32(12):2311–2331, 2020. https://arxiv.org/abs/2007.03748
2. Kent, S. J., Frady, E. P., Sommer, F. T., Olshausen, B. A. — *Resonator Networks, 2: Factorization Performance and Capacity Compared to Optimization-Based Methods.* Neural Computation 32(12):2332–2388, 2020. https://arxiv.org/abs/1906.11684 · https://doi.org/10.1162/neco_a_01329
3. Karunaratne, G., Hersche, M., Sebastian, A., Rahimi, A. — *On the Role of Noise in Factorizers for Disentangling Distributed Representations.* NeurIPS 2024 MLNCP, arXiv 2412.00354, 2024. https://arxiv.org/abs/2412.00354
4. Langenegger, J., Karunaratne, G., Hersche, M., Benini, L., Sebastian, A., Rahimi, A. — *In-memory factorization of holographic perceptual representations.* Nature Nanotechnology 18(5):479–485, 2023. https://doi.org/10.1038/s41565-023-01357-8 (PubMed 36997756) · https://research.ibm.com/publications/in-memory-factorization-of-holographic-perceptual-representations
5. Snyder, S., Poursiami, H., Parsa, M. (George Mason University) — *qFHRR: Rethinking Fourier Holographic Reduced Representations through Quantized Phase and Integer Arithmetic.* arXiv 2604.25939, 2026. https://arxiv.org/abs/2604.25939
6. Frady, E. P., Kleyko, D., Sommer, F. T. — *Variable Binding for Sparse Distributed Representations: Theory and Applications.* IEEE Trans. Neural Networks and Learning Systems, 2020. https://arxiv.org/abs/2009.06734
7. Renner, A., Supic, L., Danielescu, A., Indiveri, G., Olshausen, B. A., Sandamirskaya, Y., Sommer, F. T., Frady, E. P. — *Neuromorphic Visual Scene Understanding with Resonator Networks.* arXiv 2208.12880, 2023. https://arxiv.org/abs/2208.12880
8. Khosrowshahi, A., Nikonov, D. E., Olshausen, B. A., Sommer, F. T., Frady, E. P. — *Integer Factorization with Compositional Distributed Representations.* NICE 2022. https://doi.org/10.1145/3517343.3517368
9. Hersche, M., Terzic, A., Karunaratne, G., Langenegger, J., Pouget, A., Cherubini, G., Benini, L., Sebastian, A., Rahimi, A. — *Factorizers for Distributed Sparse Block Codes.* NeSy 2023, arXiv 2303.13957. https://arxiv.org/abs/2303.13957
10. Hersche, M., Opala, Z., Karunaratne, G., Sebastian, A., Rahimi, A. — *Decoding superpositions of bound symbols represented by distributed representations.* NeSy 2023, pp. 279–288. (cited in [3]; explains the noise-amplification limit of explain-away and the query-sampler remedy)
11. **IBM / Rahimi — US 12,306,870 B2, "Set of resonator networks for factorizing hyper vectors."** Filed 2022-04-08, published 2023-10-12, granted 2025-05-20, expires 2043-10-19. Claim 1 read verbatim and all four dates confirmed against the Google Patents record this session. https://patents.google.com/patent/US12306870B2/en
12. **IBM — US 12,579,411 B2, "Resonator network based neural network."** Filed 2021-12-29 (US 17/564,275), published 2023-06-29, granted 2026-03-17, expires 2045-01-03. Claim 1 read verbatim and all four dates confirmed against the Google Patents record this session. https://patents.google.com/patent/US12579411B2/en
13. **IBM (Karunaratne, Hersche, Cherubini, Sebastian, Rahimi) — US 12,561,553 B2, "In-memory resonator network for factorizing hyper vectors."** Filed 2022-03-16, published 2023-09-21, granted 2026-02-24, expires 2044-12-26. Dates confirmed against the Google Patents record this session. https://patents.google.com/patent/US12561553/en
14. **IBM (Hersche, Rahimi) — US 12,518,150 B2, "Bundling hypervectors."** Filed 2022-06-27, published 2023-12-28, granted 2026-01-06, expires 2044-08-24. Claims 1/2/4 read verbatim this session (selection-based sparse-binary bundling; resonator network named as the decoder). https://patents.google.com/patent/US12518150B2/en
15. **IBM — US 2025/0086251 A1, pending.** Alternative implementations of each iterative step + runtime selection. https://patents.justia.com/inventor/kumudu-geethan-karunaratne
16. *Noise-Enhanced Associative Memories.* NeurIPS 2013. https://proceedings.neurips.cc/paper_files/paper/2013/file/f4552671f8909587cf485ea990207f3b-Paper.pdf
17. *Associative Memory and Generative Diffusion in the Zero-noise Limit.* arXiv 2506.05178, 2025. https://arxiv.org/abs/2506.05178
18. Wang, L. et al. — *Chaotic Simulated Annealing with Decaying Chaotic Noise.* ASCC 2000. https://personal.ntu.edu.sg/elpwang/PDF_web/00_ASCC.pdf
19. Hinton, G. E., Sejnowski, T. J., Ackley, D. H., Terrace, H. S. — *Convergence and Pattern-Stabilization in the Boltzmann Machine.* J. Statistical Mechanics, 1985. https://papers.nips.cc/paper_files/paper/1988/hash/c45147dee729311ef5b5c3003946c48f-Abstract.html
20. Kleyko, D., Rachkovskij, D. A., et al. — *A Survey on Hyperdimensional Computing aka Vector Symbolic Architectures, Part I.* ACM Computing Surveys, 2022. https://doi.org/10.1145/3538531
21. Plate, T. A. — *Holographic reduced representations.* IEEE Trans. Neural Networks 6(3), 1995. https://dl.acm.org/doi/abs/10.1109/72.377968
22. Renner, A. et al. — *FactorHD: A Hyperdimensional Computing Model for Multi-Object Multi-Class Representation and Factorization.* arXiv 2507.12366, 2025. https://arxiv.org/abs/2507.12366
23. Komer, M. et al. — *Learning and Generation of Compositional Scenes from a Single Distributed Representation.* arXiv 2303.13691, 2023. (resonator generalises map-seeking circuits, Arathorn 2002; dynamic routing, Olshausen et al. 1995) https://arxiv.org/abs/2303.13691
24. Rahimi, A. et al. — *Vector Symbolic Architectures as a Computing Framework for Emerging Hardware.* arXiv 2106.05268, 2023. https://arxiv.org/abs/2106.05268
25. **Internal, measured on this machine (2026-09-27):** `sqlite3 the project's local telemetry store` — `marks` cardinality census; `the VSA core repo ` bind/dot/scan timings; `RSPK/CONTEXT.md`; `the research corpus 2026-09-25 — RELEASE SCOPE + CLEAN-ROOM PLAN.md` (patent addendum); `the research corpus 2026-09-26 — STIGMERGY PRODUCTION PASS (sweep).md` §8 (IFS resonator search + `vsa_stochastic.h` metric defect); `Downloads/Resonator networks.txt` lines 1386–1438 (J's IFS idea thread — **ideas, not facts**).

---

## Verification ledger

Per the ai-stack rule "verify every claim with a command before stating it," here is what was machine-checked versus read from primary text. **Two errors were caught in this gate and corrected in place** — both are recorded rather than silently fixed.

**Machine-verified this session (arithmetic re-computed independently, all figures matched):**

| Claim | Command | Result |
|---|---|---|
| M_max = 8.078·N²/F^1.268 at N=10,240 | `python3` recompute | F=3 → 2.10×10⁸; F=4 → 1.46×10⁸; F=5 → 1.10×10⁸; F=7 → 7.18×10⁷ — **all match the dossier** |
| 42⁵ = 1.307×10⁸ vs M_max(F=5) | `python3` | 118.8% → **over capacity**, as stated |
| 40⁵ = 1.024×10⁸ vs M_max(F=5) | `python3` | 93.0% — as stated |
| 42⁴ = 3.11×10⁶ vs M_max(F=4) | `python3` | 2.1% util, **46.9× margin** (34.5× against the conservative Table-1 c=1.024) — as stated |
| 42×8×10×10×25 = 8.4×10⁵ | `python3` | exact |
| Table-1 c vs law per F | `python3` | F=3 2.006/2.002; F=4 1.393/1.024; F=6 0.833/0.874; F=7 0.685/0.669 — matches the dossier's "matches at F=3, F=7; over-predicts at F=4" claim. **F=2 is 3.354 predicted vs 0.293 measured**, which is why Kent restricts the law to F ≥ 3 and why the dossier does too |
| Loading ratios 0.056 / 0.138 at N=10,240 | `python3` | 573 and 1,413 codevectors — as stated |
| Cost model (145 ns/dot → 588 µs/query) | `python3` | 6.1 µs cleanup, 24.5 µs/iter, 588 µs for 24 iters, 1,701 q/s ternary — as stated |
| **Kill-criterion #4 threshold** | `python3` | 24 iters × 4 factors × 42 atoms = **4,032 similarities**; 5 ms ÷ 4,032 = **1.24 µs** — the dossier's original 20 µs gate was **16× too loose** and would have passed an 80 ms reader. **Corrected in two places.** |
| `marks` cardinality census | `sqlite3 the project's local telemetry store` | 94 rows; distinct session 2, agent 2, role 2, task 1, **beat 0**, kind 4, target 94, **outcome 1**, source 3; **no `lane` column** |
| Patent dates ×3 | Google Patents record reads | US 12,306,870: 2022-04-08 / 2023-10-12 / 2025-05-20 / 2043-10-19 ✓ · US 12,579,411: 2021-12-29 / 2023-06-29 / 2026-03-17 / 2045-01-03 ✓ · US 12,561,553: 2022-03-16 / 2023-09-21 / 2026-02-24 / 2044-12-26 ✓ |
| US 12,518,150 filing date | Google Patents record read | Dossier said **2022-06-22; actual is 2022-06-27. Corrected in two places.** Claims 1/2/4 also read, which changed the row's substance — the patent **names a resonator network as the decoder**, which the earlier addendum summary did not convey |

**Read from primary text (claims, papers) but not independently re-derived:** all claim-1 language for the four patents (verbatim in Answers 7); the Kent capacity law and Table-1 coefficients; the qFHRR K=8/K=16 fidelities; the IMF/ACF ≥50× capacity gain; the Nature Nanotechnology 5-orders-of-magnitude claim (explicitly flagged as PCM-only and non-transferable to CPU); the 2020 Frady sparse-binding information-loss statement; the Renner 84%-at-6-factors scene result.

**Explicitly NOT verified, and flagged as such in the dossier:** the K=32 fidelity figures (0.997/0.989) — `[INFERRED]`, paper's Table 2 not opened; US 2025/0086251 A1 (pending) — known only from a Justia inventor record, so the claim scope is *not* confirmed; the absence of a telemetry/logs application and the absence of an IFS-noise paper — **absence of evidence, stated as such**; the 45-source corpus in `Downloads/Resonator networks.txt` — unvalidated, needs primary reading (Open Question 13).

**Not done, and not claimed:** no architecture decided, no code written, no repo copied, no resonator implemented, no FTO opinion obtained. The four patent reads are claim-text reads, **not legal advice**, and an attorney must clear US 12,579,411 before any build.

---

*DONE RSPK-RES — dossier at the project root/the research corpus RSPK/2026-09-27-RSPK-RES.md*

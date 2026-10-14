# 45 — Technical disclosure and status, 2026-10-11 → 2026-10-14
Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted). CC BY 4.0. Published as prior art; no patent is claimed.

This chapter discloses every design the project built or tested after research corpus v0.2.0 (2026-10-10) and records its status as of
2026-10-14. "Measured" means a saved run with its numbers; "NOT YET TESTED" means designed but not run. Negative results are reported as
results. The standalone design disclosures for the Cyclone Trainer and the THEAD SuperSeed are in `disclosures/`.
**Evidence status:** every number here comes from a saved run (command, binary revision and result file) kept in the project's
working records; those harnesses and result files are not published in this release, so the numbers stand as reported, not yet
independently reproducible from this repository.

## 45.1 Exact residue-ring softmax, log-sum-exp and loss inside a ternary transformer trainer ("digital abacus")
**Design.** The output head's softmax, log-sum-exp and cross-entropy are computed in a residue number system over the 20 large outer moduli
of a 50-ring omniring system: logits are quantised once at scale S (S = a product of five ring moduli), the exponential term, row sum,
Newton reciprocal, atanh-series logarithm and LSE are ring algorithms; scaling by S is exact RNS scaling with base extension; the row
maximum stays an exact float maximum (quantisation is monotone). The same source emits host and device code. A "sub-base" form runs the
Horner scalings on 11 rings with a written range proof and extends the mantissa back to all 20 rings. Heads with an avoid token
(−ln(1−p_avoid)) and routing masks use the same ring path (Σ' = Σ − e_avoid exactly; the 1e-5 clamp is a ring comparison).
**Measured.** CPU and GPU kernels bit-identical (0 mismatches, three runs, two shapes); versus a float64 reference the ring LSE error is
1.5e-11 against 3.1e-6 for float32. In the CUDA trainer at school size (6.8M parameters): device == host on 40/40 training buffers;
training loss matches the CPU engine (9.158415 vs 9.158470). The ring term was cut from 66.4 ms to 13.1 ms per step and then to 1.98×
the float kernel (dp4a dot products, sub-base, 256-element chunks) with identical bytes (bench 2048×8192: 69.6 → 6.1 ms). An in-place
write race that made avoid programs differ between device and host was found and fixed (40/40 identical after).
**Not yet tested.** Vulkan back end; R > 1; vocabularies below the chunked threshold.

## 45.2 The ring core inside attention, replaced by a Cyclone or an Armilla 3×3 structure
**Design.** THEAD's attention turns each head's queries and keys by phases on prime clock rings; each token's phase comes from its
25-residue (T25) event address rendered by a JIT core, with per-head octave voicing and 37–53 harmony rings. Explored replacements:
(a) T50 addressing — T25 is a sub-torus of T50, so shared rings keep their lanes and residues and added rings start at phase 0 (identity);
(b) an Armilla 3×3 layout — 27 lanes as 9 ring systems × 3 rings, two compute groups as the bases of the reversible trunk's two streams,
one guard group; residue-redundant fields give an RRNS guard on every token address; (c) Cyclone routing — the address selects one of
8 slot head-groups, attention only within a slot plus one dense hub head.
**Measured (frozen 6.8M checkpoint, 7,364 held-out tokens).** (a) logits byte-identical with the added zero-phase lanes; a trained
variant with head width 100 (18 new T50 lane pairs per head, new weights initialised so step 0 is identical, gradient-checked) reached
the dense model's held-out loss within seed noise at 650 steps but did not beat it. (b) Guard observe-only: byte-identical, 0 false
alarms in 18,223 tokens, 53–259 ns per token; single-residue faults 7,354 corrected / 0 wrong; with "abstain → recompute the address
from the event's fields" every fault class (1 residue, 2 rings, a whole field, 4 rings anywhere) costs ≤ 0.0067 nats (an earlier
"abstain → position clock" fallback cost up to +1.4 nats — the trained model does not tolerate one token on a different clock). The
recompute guard is now the engine default for the T25 address (clean runs byte-identical). (c) Routing by address at fixed weights
costs +1.4…+1.9 nats, the same as random slots; a hub head recovers ~0.4; trained with the mask for 650 steps the gap closes from +1.44
to +0.26 at 39 % of dense attention work. Longer and annealed training arms (two seeds, CPU and GPU) were running at the time of writing.

## 45.3 Cyclone shape as the model's MLP core (SuperSeed-EVO) — negative result
**Design.** Each block's MLP split into a hub (half the hidden units, every token) plus 8 slot-cores of D/4; a token fires the hub and
the slot its T25 address names (CRT integer mod 8 by Garner's mixed radix, exact); optional hub_pull coupling.
**Measured (RTX A6000, 18 min per arm, same data, same total ternary parameters, device == host bit-identical in all arms).** Held-out
loss: dense 0.4034; hub + 8 slots +4.2 % (answer span +12.7 %); with hub_pull +9.6 % (answer +35.3 %, canary +29.1 %). The MLP-slot
form does not beat the dense trunk at this size. **Guard in the step (Armilla 3×3):** 32,768 hub values carried as 9 residue units in
3 groups restore a bit-exact training step after a faulty unit, a faulty group, or two units in two groups; four faulty units abstain
(keep the last good state) and write nothing wrong; without the guard the step goes to NaN.

## 45.4 A liquid ternary ranker for a self-repairing browser engine ("the doctor")
**Design.** The doctor repairs layout defects by trying fix templates; a frozen ternary reservoir (N = 512) with a ternary readout ranks
which template to try first; online, the readout learns from each verdict of a frozen gate (the gate never learns), and the live model
is served only while it strictly beats the frozen shadow over the trailing 40 episodes. The reservoir runs as a resident GPU kernel;
a daemon serves scores over TCP.
**Measured.** GPU kernel == CPU integer scores on 57,160 × 14 requests (0 mismatches, 175k requests/s); daemon replay 2,858 × 14, 0
mismatches; served-model floor: 0 of 2,621 episodes worse than frozen (5 folds); A/B on 23 sites: the same 205 defects fixed with 289
tries (learning) vs 350 (frozen ternary) vs 361 (rule base). Growth blocks (adding reservoir units) showed no headroom on this metric.

## 45.5 The open web as the doctor's curriculum, judged by page-own geometry
**Design.** Pages are sampled from Common Crawl's columnar index by category (AI, video, developer, user, commercial, long tail), fetched
by WARC byte range into offline bundles with full provenance (no network at render time), laid out by the engine, and scored by a
"pristine" yardstick that judges every box by its own page's geometry (overflow, near-flush, near-align, near-touch, near-equal, uneven
gap) — no reference browser needed. A capture mode for reference pages runs the page's JavaScript, then saves the post-script DOM with
scripts removed and a Chrome snapshot of that same DOM.
**Measured.** 10,312 pages from 2,851 sites, mapped at 330 pages/s on 8 CPU cores, 99.22 % of boxes pristine; doctor fix loop on 100
held-out pages: defects 1,200 → 65 with the learning ranker vs 70 frozen, 2.9 % fewer tries; the feed's first harvest was 45 pages that
crashed the engine — 43 traced to one grid-placement bug (fixed), 2 open. Top-100 sites with JavaScript run: 99 pages, 90,371 boxes,
96.63 % pristine, 0 pages without boxes. Cost ≈ $0.12 per 1,000 pages (fetch-dominated; per-IP throttling).

## 45.6 Whole public ternary model decoded on the Armilla pull engine
**Measured.** BitNet b1.58 2B4T decoded layer by layer with every ternary matrix product exact (0 mismatches against a direct integer
dot, 210 matrices × 17 positions); logits hash identical on an Intel i5-8365U and an AMD EPYC; 1.37× bitnet.cpp tokens/s on a quiet
pod with identical tokens and logits (decode is now memory-bandwidth bound). The released weights expect ReLU² (perplexity 14.45 on a
public-domain text) while a SiLU graph scores 81.4.

## 45.7 Dispatch that stops instead of failing over
**Design.** In an agent fleet, a failed task may move to another lane only if that lane has produced an accepted result for the task's
class within 14 days; otherwise the task stops with its reason (held, not re-dispatched); paid-subscription pins never fall to free
lanes. **Measured** on a 7-day replay: 0 productive dispatches lost; the replay also showed lane choice explains only 6 of 145 wasted
dispatches (the rest: rate-limit retry loops, first-dispatch failures, re-dispatch after a productive result).

## 45.8 A speech core in the same exact forms (design only)
**Design.** A whisper-like speech recogniser built from published descriptions only: an exact number-theoretic-transform front end
over the ring primes (bit-identical log-mel), a ternary encoder on the trunk forms with prime clock rings over time frames, and a CTC
head whose softmax is the ring softmax of 45.1, running as a resident core that fires per audio frame. **Status:** NOT YET TESTED;
voice search in the browser currently runs on a separate local recogniser (whisper.cpp, 1.1 s speech-end to results).

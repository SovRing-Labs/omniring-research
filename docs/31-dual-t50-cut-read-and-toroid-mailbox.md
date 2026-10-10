# The dual-T50 cut read: the array's bottlenecks from the rings' own counters, and the toroid mailbox

| | |
|---|---|
| **Date** | 2026-10-09 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). The author reviews each document before publication. |
| **Type** | measured result (CPU reference and GPU kernels on the software driver) |
| **Verdict** | PASS on product-structured traffic (exact against Gomory–Hu and max-flow); a blind spot found and closed with box cuts |
| **Code** | `harness/part7/ch1-t50-cuts/g5_t50_cuts.py`, `rung.py`, `cut_kernels.py`, `route.spvasm`, `mb_count.spvasm`, `mb_scan.spvasm`, `mb_scatter.spvasm`, `mb_ledger.spvasm`; `harness/part7/ch1-growth-controller/g4_cuts.py` |

## The author's statement, verbatim (2026-10-09, readback confirmed)
*"interlocking two 50t omniring systems would solve this computation in much less time by relying on the massive rapidly moving and
counting outer rings."* The computation: where is the array congested — the minimum cuts between toroids — without an all-pairs
max-flow every step.

*The record below is the full measured account from the technical disclosure's working chapters: every gate, every failure, with the
harness and result paths in this repository. "Section n" and "§n" inside it refer to the sections of that chapter; the matching documents here
are listed in the README. "Recorded; no saved result" marks a figure the project recorded whose output file is not published.*

## The dual-T50 cut read: bottlenecks from the rings' own counters
**Description.** The array is the Cartesian product of two rings (floor ring of 3 x unit ring of 5, 15 toroids). The route pass already fills, in the
same pass that moves the items, two ledgers: a **source-addressed** table `link[d][from][to]` (traffic along each ring dimension) and the
**destination-addressed** home ledger / inbox (per toroid, per ring, per residue). These are the two interlocked ledgers. The read: per toroid a
"trivial" cut (the load on all its links) and, per ring, an m x m table of traffic between residue classes whose bipartitions give the cuts that follow
that ring; the min cut between any two toroids s, t is the minimum of the two trivial cuts and of every ring bipartition that separates s from t. With
capacity C = 1.25 x the busiest link, the integer value is 5 x (cut size) x busiest - 4 x (crossing traffic), i.e. four times the headroom. No search,
no max-flow: O(rings) per pair. A **box cut** (a sub-torus S = product of residue subsets, one per ring) reads the full source x destination table; the
20 outer rings 131...233 each exceed the toroid count, so residue = address there and they hold that full table.
**Gate G1, CPU probe** (`harness/part7/ch2-cuts/g5_t50_cuts.py`, input = the G120 rung record, result
`docs/appendix/part7/ch2-cuts/results/g5/g5-t50-cuts.json`; Gomory-Hu baseline `harness/part7/ch2-cuts/g4_cuts.py`, result
`docs/appendix/part7/ch2-cuts/results/g4/g4-cuts.json`; needs networkx): G120 recorded routing, 15 toroids: capacity C = 13,680 (busiest link 10,944, all hot links at 0.8 of C); the
ring read equals the Gomory-Hu tree on **105 of 105 pairs**, global bottleneck 27,287 (headroom units; the cut isolating floor-1 unit 1, shared by the
Gomory-Hu tree), the read costing 0.27 ms (0.182 ms for the ring tables, 0.091 ms for all pairs) against 4.3 ms for Gomory-Hu (17.2x as recorded); 200
seeded dimension-order routed fields: 200 of 200 exact; 105 toroids (3 x 5 x 7): 5,460 of 5,460 pairs exact, 8.1 ms against 151 ms (18.9x); 1,155 toroids (3
x 5 x 7 x 11): 60 of 60 sampled pairs equal exact max-flow, global minimum 2,922 equal to Stoer-Wagner's, 1.5 s against about 101 s for Gomory-Hu (an
estimate of 1,154 max-flows at 0.0878 s each, not a run; Stoer-Wagner took 12.2 s). Timings are Python on the laptop. **Corrections to the earlier
draft** (unpublished project notes and a review quoted 4.2 ms, 8.8 ms against 184 ms, 1.6 s against about 104 s): the result file is the figure above. Two further
statements of the earlier draft have no entry in the result file and stay recorded-only: i.i.d. and lognormal link loads at headroom 25 % to 0.01 % (100 of
100 on 3 x 5, 20 of 20 on 3 x 5 x 7) (recorded; no saved result), and a crafted two-toroid hot cluster (79 of 105 pairs exact) (recorded; no saved result).
- **Negative result, then fix.** A **hot cluster** (a box of toroids saturated toward the rest) defeats the ring family: exact on only 85 of 100 cases
  (3 x 5; worst gap 0.556 C). Adding the box cuts from the full table makes it 100 of 100 (3 x 5; box read 2.1 ms) and 3 of 3 (3 x 5 x 7; box read 2.08 s,
  the ring family alone also 3 of 3 there). Box enumeration is the product of (2^m - 1) over rings: fine at 15 and 105 toroids, **not at 1,155** (open: search
  driven by the hot vertices, or certify the reported bottleneck with one max-flow, since every ring answer is an upper bound, a real cut).
**Gate G2, GPU form** (`harness/part7/ch2-wiring/kernels/route.spvasm` bindings 8 and 9, the cut-kernel module generated by `harness/part7/ch2-wiring/gen/cut_kernels.py` (the compiled module is not shipped), rung gate
`harness/part7/ch2-wiring/cyclone/rung.py`, results `docs/appendix/part7/ch2-wiring/results/cyclone/G40/G40-llvmpipe-w262144.json` and `docs/appendix/part7/ch2-wiring/results/cyclone/G120/G120-llvmpipe-w262144.json`): the route pass fills `rtab` (per ring, residue x
residue) and `vtab` (per toroid) with its own atomics; the cut pass writes `cut[s x T + t]` for every toroid pair each step. Recorded: on G40 and G120 the
tables and the cut table equal the CPU reference with 0 mismatches (`cut_rtab`, `cut_vtab`, `cut_table`) and the cut table equals Gomory-Hu on every pair
(`cut_vs_gomory_hu` 0). The cut-pass time (0.94 ms, llvmpipe) and the route-atomics A/B (84-118 ms with against 89-92 ms without, step 340 ms both) are in
unpublished notes only - the surviving records are of the later run with the mailbox (step 351.3 ms) and carry no cut-pass timing
(partial). Limits: ring size <= 16; **box (hot-cluster) cuts are not on the GPU**, and the *outer-ring counting for box cuts exists only in
the Python probe*.
**What the dual-T50 claim does and does not rest on.** What ran: two interlocked ledgers filled by the routing pass, read by formula (trivial + ring +
box cuts), compared with Gomory-Hu. What did not run: two coupled T50 omniring cores whose outer-ring counters are the ledgers; a decision loop that
re-routes or re-sizes the array from the cuts; a test on a non-product network.
FIELD PREDICTS: a minimum edge cut of a Cartesian product G x H is either trivial (one vertex) or the preimage of a factor's minimum cut (Klavzar and
Spacapan 2008) - an *unweighted* theorem, so exact agreement under weights is empirical and a failure under a saturated cluster is expected (measured:
85 of 100). All-pairs min cuts are conventionally computed with a Gomory-Hu tree (Gomory and Hu 1961; Gusfield 1990) at n - 1 max-flows; Stoer and
Wagner (1997) give the global minimum cut.

## The toroid mailbox and GPU-sized dispatch (`harness/part7/ch2-wiring/kernels/mb_count.spvasm`, `harness/part7/ch2-wiring/kernels/mb_scan.spvasm`, `harness/part7/ch2-wiring/kernels/mb_scatter.spvasm`, `harness/part7/ch2-wiring/kernels/mb_ledger.spvasm`; `Session::pass_indirect` in `harness/part7/ch2-wiring/src/session.rs`)
**Description.** Per step: `mb_count` counts items per home toroid; `mb_scan` takes the exclusive prefix of the counts (item offsets), the prefix of
ceil(items / 64) (workgroup offsets) and writes the indirect-dispatch arguments, then resets the counters; `mb_scatter` gives every item a slot in its
home toroid's contiguous mailbox; consumers are launched by `vkCmdDispatchIndirect` with the group count the GPU itself computed, workgroup w mapped to
a toroid through the workgroup offsets. Today's consumer, `mb_ledger`, rebuilds each toroid's T50 ledger. New per-toroid work plugs in as another
indirect pass reading the mailbox. No host round trip sizes the work.
**Gate** (`harness/part7/ch2-wiring/cyclone/rung.py`, G40 and G120, results `docs/appendix/part7/ch2-wiring/results/cyclone/G40/G40-llvmpipe-w262144.json` and `docs/appendix/part7/ch2-wiring/results/cyclone/G120/G120-llvmpipe-w262144.json`): every mailbox
check 0 (counts, offsets, workgroup offsets, indirect arguments, workgroups per toroid, per-toroid item sets, mailbox ledger equal to the routing home
ledger). Recorded: G40 **1,283 workgroups sized by load against 2,175 for a fixed worst-case launch**; G120 **3,848 against 6,465** (80 to 431 per
toroid; both figures also recomputed from the inbox counts of the record: sum of ceil(inbox / 64) = 3,848; 15 x 431 = 6,465). Mailbox pass times on
llvmpipe at G120: 3.8 + 0.09 + 4.5 + 21.2 ms (count, scan, scatter, ledger).
Not measured: wall-time gain from the elastic launch (the fixed-size variant was not timed); any consumer heavier than the ledger rebuild.
FIELD PREDICTS: count, exclusive scan, scatter is a counting sort (Blelloch 1990, prefix sums; Harris, Sengupta and Owens 2007 for the GPU scan), and
issuing indirect dispatches from device-written counters is the GPU-driven pipeline pattern (Haar and Aaltonen 2015).

## The dual-T50 cut read and its GPU form (growth-run gate G4c; harness `harness/part7/ch1-t50-cuts/g5_t50_cuts.py`; GPU kernels `harness/part7/ch1-t50-cuts/{route.spvasm, mb_count.spvasm, mb_ledger.spvasm, mb_scan.spvasm, mb_scatter.spvasm}`; the compiled cut kernel is a binary and is not shipped)

The author's statement, verbatim (2026-10-09, readback confirmed): "interlocking two 50t omniring systems would solve this computation in much less time
by relying on the massive rapidly moving and counting outer rings". In field terms: two residue-number systems coupled ring to ring; the outer rings
(the T50's 20 large moduli 131..233, odd primes 3..233 in all, sum of moduli 5,348) are counters turning one notch per tick; their per-ring counts
of the traffic give the network's bottlenecks (minimum cuts between toroids) without a Gomory-Hu / all-pairs max-flow computation.

Description. The array is a Cartesian product of rings (15 toroids = floor ring 3 x unit ring 5; every toroid linked to every other along a ring).
The routing pass already fills, while it moves items: `link[d][from][to]` (source-addressed) and `hled` / `inbox` (destination-addressed): the two ledgers.
Cut read: trivial cuts from per-vertex ring sums; factor cuts from an m x m table per ring (every residue bipartition); a pair's min cut = min(trivial s,
trivial t, the table of every ring where s and t differ) - O(rings) per pair, tables of sum m^2 + n entries, no search. Capacity model: residual =
C - load, C = 1.25 x the busiest link. Where a box of toroids saturates toward the rest, sub-torus box cuts from the full source x destination table.

Measured gates (harnesses `harness/part7/ch1-t50-cuts/g5_t50_cuts.py` and `harness/part7/ch1-growth-controller/g4_cuts.py` (Python), GPU form `harness/part7/ch1-t50-cuts/{rung.py, cut_kernels.py}` with the kernels above; results `docs/appendix/part7/ch1-t50-cuts/results/{g4,g5}/`, `docs/appendix/part7/ch1-growth-controller/results/g4/` and `docs/appendix/part7/ch1-t50-cuts/results/cyclone/{G40,G120}/`).
- G1: the recorded G120 routing record (15 toroids, two steps): per-toroid inbox 5,118 ... 27,533 items per step (u0/u3 cold, u1/u2/u4 hot, the same on every floor); the ring read of
  that record gives the global minimum cut 27,287, at the vertex f1u1, equal to the Gomory-Hu global minimum; the closure of the table equals the plain enumeration; 105 of 105 toroid
  pairs equal; read 0.18 ms + 0.09 ms for all pairs against 4.3 ms for Gomory-Hu (`docs/appendix/part7/ch1-t50-cuts/results/g5/g5-t50-cuts.json`, input `docs/appendix/part7/ch1-t50-cuts/results/g4/G120-llvmpipe-w262144.json`, `docs/appendix/part7/ch1-growth-controller/results/g4/g4-cuts.json`). The ring side was also
  re-run here from the shipped source with a stub for the graph library (rings 3 and 5, 15 toroids, 45 links, 33 candidates, the same minimum, 0.29 ms); the Gomory-Hu side is taken from
  the record and was not re-run (the graph library is not installed here).
- G2: against Gomory-Hu (`docs/appendix/part7/ch1-t50-cuts/results/g5/g5-t50-cuts.json`): 200 seeded dimension-order-routed traffic fields: 200 of 200 exact (194 trivial, 6 factor-cut global minima); 105 toroids (3.5.7): 5,460 of
  5,460 pairs equal, 8.1 ms (3.69 ms read + 4.43 ms all pairs) against 151 ms; 1,155 toroids (3.5.7.11): 60 of 60 sampled pairs equal to exact max-flow (0.088 s per pair), global minimum 2,922
  equal to Stoer-Wagner (12.2 s), ring read + all pairs 1.51 s against about 101 s for all pairs by max-flow (an estimate: 0.088 s x 1,154). Recorded only in a private review note
  (not shipped), not in the result file: i.i.d. and lognormal link loads at 25 % headroom exact on 100 of 100 (K3 x K5) and 20 of 20 (K3 x K5 x K7), and a
  crafted two-toroid cluster where 79 of 105 pairs were exact (recorded; no saved result).
- G3 (a blind spot found): a HOT CLUSTER (a box of toroids saturated outward) breaks the ring family: exact on 85 of 100 fields at 15 toroids (worst gap 0.556 of C); adding box cuts: 100 of 100
  (K3 x K5), and 3 of 3 at 105 toroids (K3 x K5 x K7, where the ring family alone was already exact on those 3). Box enumeration is prod(2^m - 1): 2.1 ms mean at 15 toroids, 2.08 s mean at
  105, not tried at 1,155 (`docs/appendix/part7/ch1-t50-cuts/results/g5/g5-t50-cuts.json`, `hot_cluster`). The edge-connectivity theorem used is for unweighted graphs; the weighted agreement is empirical.
- G4: on the GPU the route pass fills the tables with its own atomics and a cut kernel writes every toroid pair's min cut per step: on G40 (5 toroids) and G120 (15 toroids), two steps each on the
  software driver, the tables and the cut table equal the CPU reference and the cut equals Gomory-Hu - 0 mismatches in every check (feed, ledgers, weights, routing, cut tables)
  (`docs/appendix/part7/ch1-t50-cuts/results/cyclone/G40/G40-llvmpipe-w262144.json`, `docs/appendix/part7/ch1-t50-cuts/results/cyclone/G120/G120-llvmpipe-w262144.json`); G120 step 351 ms. The cut-pass time (0.94 ms) and the comparison of the route pass with and without the new
  atomics (84-118 vs 89-92 ms) are in the omni-gpu results summary (not shipped) only: the stored record lists seventeen unnamed pass times (partial).
- G5: toroid mailbox with an indirect dispatch sized on the GPU from the counters (same two records): every mailbox check 0 mismatches, the mailbox ledger equals the routing ledger; G120: 3,848
  workgroups by load against 6,465 for a fixed worst-case dispatch (80-431 per toroid; G40: 1,283 against 2,175); mailbox passes 3.8 + 0.09 + 4.5 + 21.2 ms on the software driver.

FIELD PREDICTS: a minimum edge cut of a Cartesian product graph is trivial or the preimage of a factor's minimum cut (Klavzar and Spacapan, on the
edge-connectivity of Cartesian product graphs; unweighted); all-pairs min cuts = Gomory-Hu (1961); a global min cut = Stoer-Wagner (JACM 1997);
dimension-order routing (Dally and Seitz, IEEE Trans. Computers 1987) keeps traffic on one ring per hop so per-ring counters are exact; predictions-
augmented capacity (Lykouris and Vassilvitskii, ICML 2018) is the field's frame for pre-rendering capacity from the planner's next curriculum - designed only.
The measured weighted agreement and the hot-cluster miss are consistent with a theorem that holds without weights and fails for non-product structure.

## Reading
On product-structured traffic the outer rings' counters are the cut structure, read in milliseconds; non-product structure (a hot box) needs
the box cuts. FIELD PREDICTS: a minimum edge cut of a Cartesian product graph is trivial or the preimage of a factor's minimum cut (Klavžar
and Špacapan, unweighted graphs; our weighted agreement is empirical); all-pairs cuts = Gomory–Hu (1961); global minimum = Stoer–Wagner (1997);
counting sort by exclusive prefix scan for the mailbox. Matched, including the predicted failure outside product structure.

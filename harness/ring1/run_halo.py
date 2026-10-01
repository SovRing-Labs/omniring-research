#!/usr/bin/env python3
"""RING-1 T4: two-stage halo chain (Arm B) vs one big resonator (Arm A) on crowded slots.

Task: RING1-HALO (_Pads/RING/ring1-w2.wave.yaml, cohort contract _Pads/RING1B-contract.json).
Pillar: Nervous System, Loop step "Read".  Pure synthetic study, Python 3 + numpy only.

Arm A -- ONE RESONATOR (exactly RING1-CORE's T1 cell, 13-ring clamped to the target):
    resonate(slot, rings, clamp={13-ring: target % 13}, 50, 0)
    All three remaining rings (3, 5, 7) start at their codebook means and iterate
    together, mutually unbinding each other, until the argmax tuple is stable.

Arm B -- TWO-STAGE HALO CHAIN (a cascade, same physics, fewer free rings per stage):
    stage 1: resonate ONLY the 7-ring, with the 13-ring clamped to the target and the
             3- and 5-rings HELD at their codebook means (they enter the unbind
             product but are never updated).
    stage 2: the settled 7-residue becomes a clamp, together with the 13-residue;
             stage 2 resonates the 3- and 5-rings.
    "total iterations" = stage 1 iterations + stage 2 iterations.

Note on what stage 1 physically is: in Arm A every free ring also starts at its
codebook mean, so the state Arm A is in at the end of its first iteration is exactly
the state Arm B's stage 1 starts from.  The halo is therefore not a different
operator -- it is Arm A with the 3- and 5-rings frozen after one sweep, then two
settled residues used as cues for the rest.  That is the whole claim under test.

The runner refuses to report a number it cannot stand behind: before any grid runs it
proves two things on disk-exact terms.
  1. EQUIVALENCE -- the local resonate_free() (needed because ring1_core exposes no
     free-ring subset and the brief forbids editing it) reproduces
     ring1_core.resonate() field for field when the free set is "everything not
     clamped".  If it does not, Arm A and Arm B would not be the same harness.
  2. HARNESS CROSS-CHECK -- Arm A is re-run on RING1-CORE's own T1 cell seeds
     (c=1, quant=float, 200 trials) and must reproduce RING1-CORE's published counts
     and median iterations exactly.  Source: _Reviews/RING/RING1-CORE.run.txt.

Pre-registration, the decision, the seeds and the stats rules are printed verbatim at
the top of the output.  No threshold is fitted to any number produced here.

Usage:
    python3 _Pads/RING/ring1/run_halo.py            # full: 300 trials/cell
    python3 _Pads/RING/ring1/run_halo.py --quick    # 30 trials/cell
    python3 _Pads/RING/ring1/run_halo.py --quick --trials 40
    python3 _Pads/RING/ring1/run_halo.py --verify-only
"""
from __future__ import annotations

import argparse
import os
import sys
import time

# Keep the BLAS thread pool small and fixed so timings are comparable between runs.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "4")

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ring1_core  # noqa: E402
from ring1_core import make_rings, make_slot, resonate, wilson  # noqa: E402

# --------------------------------------------------------------------------- config
D = 5120
MODS = (3, 5, 7, 13)
R3, R5, R7, R13 = 0, 1, 2, 3                       # ring indices
STATES = 1
for _m in MODS:
    STATES *= _m                                   # 1,365
MAX_MARK = STATES - 1
MAX_ITER = 50
BASE_SEED = 20260928                              # same base seed as RING1-CORE
QUANT = "float"                                   # T4 fixes the quantisation
LOADS = (12, 32)                                  # crowded slots
DECISION_LOAD = 32                                 # the cell the criterion names
FULL_TRIALS = 300
QUICK_TRIALS = 30

Z99 = 2.5758293035489004                          # two-sided normal quantile, 99%

# These two mirror ring1_core's private constants of the same name.  They are not
# imported (the brief forbids reaching into the library); the EQUIVALENCE check below
# is what proves the mirror is faithful.
_NORM_FLOOR = 1e-12
_TIE_SLACK = 1e-12

# RING1-CORE's own T1 cells (stream 1, clamp_n 1, quant float -> index 0), 200 trials.
# Published values, _Reviews/RING/RING1-CORE.run.txt.  Arm A must reproduce these.
CORE_CROSSCHECK = {
    12: {"n": 200, "correct": 134, "any": 200, "median_iters": 2.0},
    32: {"n": 200, "correct": 69, "any": 196, "median_iters": 2.0},
}
CORE_CELL_SEED_STREAM = 1                          # run_core.py cell_seed(stream=1, ...)
CORE_CELL_CLAMP_N = 1
CORE_CELL_QUANT_INDEX = 0                          # run_core.T1_QUANTS.index("float")

PRE_REGISTERED = """\
PRE-REGISTERED DECISION (verbatim from _Pads/RING/ring1-w2.wave.yaml, task RING1-HALO, step 6):
  PASS if Arm B's target recall Wilson-99% lower bound exceeds Arm A's point recall at
  M = 32, OR Arm B matches Arm A (intervals overlap) with <= 0.5x the median total
  iterations. Otherwise KILL (the halo buys nothing).
PRE-REGISTERED SCOPE (verbatim, step 2):
  Same problems for both arms: mods (3,5,7,13), float, M in (12, 32), 300 trials, the
  13-ring clamped to the target. Arm A: one resonator over all free rings (as RING1-CORE).
  Arm B (halo): stage 1 resonates only the 7-ring against the slot with the 13-ring clamped
  and the 3- and 5-rings held at their codebook means; its settled 7-residue then clamps
  stage 2, which resonates the 3- and 5-rings. Report target recall, median total
  iterations and wall time for both arms.
REPORTING RULES (verbatim, step 4):
  fixed seeds; the decision criterion below is pre-registered; every number from a
  command you ran; chance rate beside every recall; Wilson 99% intervals on every rate.
  chance = 1/M.

READING OF THE CRITERION (stated before the run, not after it):
  Clause 1 names M = 32 explicitly.  Clause 2 ("matches Arm A with <= 0.5x the median
  total iterations") names no M.  This runner evaluates the criterion at M = 32 -- the
  crowded cell the task is named for and the cell clause 1 names -- and prints the same
  test at M = 12 beside it for transparency.  A PASS declared at M = 32 that would NOT
  have held at M = 12 is flagged explicitly in the output, so a stricter reading can be
  applied by the reader without re-running anything."""


# ------------------------------------------------------------------ small utilities
def pct(x):
    return 100.0 * float(x)


def _positions(cbs, ests, rng):
    """argmax over each ring's positions against that ring's current estimate.

    The 'don't measure early' rule from ring1_core: this is the single measurement,
    taken once the rings have settled.  `rng` breaks exact ties only.
    """
    positions = []
    for cb, e in zip(cbs, ests):
        scores = (cb.conj() @ e).real
        top = scores.max()
        tied = np.flatnonzero(scores >= top - _TIE_SLACK)
        if tied.size == 1:
            positions.append(int(tied[0]))
        else:
            positions.append(int(tied[rng.integers(0, tied.size)]))
    return positions


def resonate_free(v, rings, clamp=None, free=None, frozen=None, max_iter=MAX_ITER, seed=0):
    """ring1_core.resonate() generalised to an explicit set of free rings.

    This exists because ring1_core exposes no free-ring subset and the brief forbids
    editing it.  Given free=None (the default) it is ring1_core.resonate() verbatim --
    the EQUIVALENCE check below proves that field for field rather than asserting it.

    free     ring indices that are updated each iteration.  None means "every ring that
             is neither clamped nor explicitly held".
    frozen   optional assertion: the set of rings expected to be held at their codebook
             mean (used by the call site as a guard, never trusted to define the set).

    Held rings initialise to their codebook mean exactly like a free ring does, enter the
    unbind product through that mean, and are never updated.  Clamped rings initialise to
    their fixed position and are never updated.  Returns the same dict as
    ring1_core.resonate(), plus "free" and "held" for the caller's bookkeeping.
    """
    v = np.asarray(v, dtype=np.complex128).ravel()
    Dv = v.shape[0]
    cbs = [np.asarray(cb) for cb in rings]
    cbs_c = [cb.conj() for cb in cbs]
    n_rings = len(cbs)

    pinned = {} if clamp is None else {int(k): int(p) for k, p in dict(clamp).items()}
    for idx in pinned:
        if not 0 <= idx < n_rings:
            raise IndexError("clamp ring index %r out of range" % (idx,))

    free_set = (set(range(n_rings)) - set(pinned)) if free is None \
        else {int(i) for i in free}
    held = set(range(n_rings)) - free_set - set(pinned)
    if frozen is not None and {int(i) for i in frozen} != held:
        raise ValueError("frozen %r does not match the rings left held %r"
                         % (sorted(int(i) for i in frozen), sorted(held)))

    # Free ring -> codebook mean; clamped ring -> its fixed position; held ring stays
    # at its mean and is never assigned again.
    ests = [
        (cbs[i][pinned[i]] if i in pinned else cbs[i].mean(0)).astype(np.complex128)
        for i in range(n_rings)
    ]

    rng = np.random.default_rng(int(seed))
    prev = None
    stable = 0
    seen = set()
    iters = 0
    converged = False
    cycled = False
    gap_first = float("nan")
    gap_min = float("nan")
    positions = _positions(cbs, ests, rng)

    for it in range(1, int(max_iter) + 1):
        gap_iter = float("inf")
        for i in sorted(free_set):
            u = v.copy()
            for j in range(n_rings):
                if j != i:
                    u = u * ests[j].conj()
            s = (cbs_c[i] @ u).real / Dv
            if s.size >= 2:
                pair = np.partition(s, -2)[-2:]
                gap = float(pair.max() - pair.min())
            else:
                gap = 0.0
            if gap < gap_iter:
                gap_iter = gap
            w = np.maximum(s, 0.0)
            e = w @ cbs[i]
            mag = np.abs(e)
            ests[i] = e / np.where(mag > _NORM_FLOOR, mag, 1.0)
        iters = it
        gap_min = gap_iter if np.isfinite(gap_iter) else float("nan")
        if it == 1:
            gap_first = gap_min

        positions = _positions(cbs, ests, rng)
        key = tuple(positions)
        stable = stable + 1 if (prev is not None and key == prev) else 0
        prev = key
        if stable >= 1:              # argmax identical for 2 consecutive iterations
            converged = True
            break
        if key in seen:              # a state revisited without convergence -> cycle
            cycled = True
            break
        seen.add(key)

    return {
        "positions": positions,
        "iters": iters,
        "converged": converged,
        "cycled": cycled,
        "gap_min": gap_min,
        "gap_first": gap_first,
        "free": sorted(free_set),
        "held": sorted(held),
    }


# ------------------------------------------------------------- integrity: equivalence
def check_equivalence(rings, n_problems=40, seed=BASE_SEED + 4242):
    """resonate_free(free=None) must equal ring1_core.resonate() exactly.

    Random loads 1..8, random clamp counts 0..2 in the RING1-CORE clamp order.  Every
    field of the returned dict is compared; gaps with a 1e-12 tolerance.
    """
    rng = np.random.default_rng(np.random.SeedSequence([int(seed), 4]))
    mismatches = []
    for n in range(int(n_problems)):
        load = int(rng.integers(1, 9))
        clamp_n = int(rng.integers(0, 3))
        marks = [int(x) for x in rng.integers(0, STATES, load)]
        target = marks[0]
        clamp = {i: target % MODS[i] for i in (3, 2, 1)[:clamp_n]}
        v = make_slot(marks, rings, MODS)
        lib = resonate(v, rings, clamp, MAX_ITER, 0)
        mine = resonate_free(v, rings, clamp=clamp, max_iter=MAX_ITER, seed=0)
        same = (lib["positions"] == mine["positions"]
                and lib["iters"] == mine["iters"]
                and bool(lib["converged"]) == bool(mine["converged"])
                and bool(lib["cycled"]) == bool(mine["cycled"])
                and np.isclose(lib["gap_first"], mine["gap_first"], rtol=0, atol=1e-12,
                               equal_nan=True)
                and np.isclose(lib["gap_min"], mine["gap_min"], rtol=0, atol=1e-12,
                               equal_nan=True))
        if not same:
            mismatches.append((n, load, clamp_n, lib, mine))
    return mismatches


# ------------------------------------------------- integrity: Arm A == RING1-CORE
def core_cell_seed(load):
    """RING1-CORE's T1 cell seed for clamp=1, quant=float -- the same SeedSequence."""
    return np.random.SeedSequence([BASE_SEED, CORE_CELL_SEED_STREAM, int(load),
                                   CORE_CELL_CLAMP_N, CORE_CELL_QUANT_INDEX])


def check_against_core(rings, loads=(12, 32)):
    """Re-run Arm A on RING1-CORE's own seeds; the counts must match its published run."""
    out = {}
    for load in loads:
        exp = CORE_CROSSCHECK[load]
        rng = np.random.default_rng(core_cell_seed(load))
        correct = any_k = 0
        iters = []
        for _ in range(exp["n"]):
            marks = [int(x) for x in rng.integers(0, STATES, load)]
            target = marks[0]
            v = make_slot(marks, rings, MODS)
            res = resonate(v, rings, {R13: target % MODS[R13]}, MAX_ITER, 0)
            pos = res["positions"]
            correct += int(pos == [target % m for m in MODS])
            any_k += int(any(pos == [x % m for m in MODS] for x in marks))
            iters.append(int(res["iters"]))
        med = float(np.median(np.array(iters, dtype=float)))
        out[load] = {"n": exp["n"], "correct": correct, "any": any_k, "median_iters": med,
                     "exp": exp,
                     "ok": (correct == exp["correct"] and any_k == exp["any"]
                            and med == exp["median_iters"])}
    return out


# ------------------------------------------------------------------------------ arms
def arm_one_resonator(v, target, rings):
    """Arm A: one resonator over all free rings, 13-ring clamped (RING1-CORE's cell)."""
    res = resonate(v, rings, {R13: int(target) % MODS[R13]}, MAX_ITER, 0)
    return {"positions": list(res["positions"]), "iters": int(res["iters"]),
            "converged": int(bool(res["converged"])), "cycled": int(bool(res["cycled"]))}


def arm_halo_chain(v, target, rings):
    """Arm B: stage 1 settles the 7-ring alone; its residue clamps stage 2 (3 and 5).

    Stage 1: free = {7-ring}, clamped = {13-ring -> target}, held = {3-ring, 5-ring} at
    their codebook means.  Stage 2: free = {3-ring, 5-ring}, clamped = {13-ring, 7-ring}.
    """
    c13 = {R13: int(target) % MODS[R13]}
    s1 = resonate_free(v, rings, clamp=c13, free=(R7,), frozen=(R3, R5),
                       max_iter=MAX_ITER, seed=0)
    r7 = int(s1["positions"][R7])
    s2 = resonate_free(v, rings, clamp={R13: c13[R13], R7: r7}, free=(R3, R5),
                       max_iter=MAX_ITER, seed=0)
    return {
        "positions": [s2["positions"][R3], s2["positions"][R5], r7, c13[R13]],
        "iters": int(s1["iters"]) + int(s2["iters"]),
        "iters_s1": int(s1["iters"]), "iters_s2": int(s2["iters"]),
        "converged": int(bool(s1["converged"]) and bool(s2["converged"])),
        "cycled": int(bool(s1["cycled"]) or bool(s2["cycled"])),
    }


def run_cell(trials, load, rings):
    """One cell: both arms on the SAME problems, so the comparison is paired."""
    rng = np.random.default_rng(np.random.SeedSequence([BASE_SEED, 4, int(load)]))
    recs = []
    secs = {"A": 0.0, "B": 0.0}
    for _ in range(trials):
        marks = [int(x) for x in rng.integers(0, STATES, load)]
        target = marks[0]
        v = make_slot(marks, rings, MODS)
        truth = [target % m for m in MODS]
        truths = [[x % m for m in MODS] for x in marks]

        t0 = time.perf_counter()
        a = arm_one_resonator(v, target, rings)
        t1 = time.perf_counter()
        b = arm_halo_chain(v, target, rings)
        t2 = time.perf_counter()
        secs["A"] += t1 - t0
        secs["B"] += t2 - t1

        recs.append({
            "A_correct": int(a["positions"] == truth),
            "B_correct": int(b["positions"] == truth),
            "A_any": int(any(a["positions"] == t for t in truths)),
            "B_any": int(any(b["positions"] == t for t in truths)),
            "A_iters": a["iters"], "B_iters": b["iters"],
            "B_iters_s1": b["iters_s1"], "B_iters_s2": b["iters_s2"],
            "A_converged": a["converged"], "B_converged": b["converged"],
            "A_cycled": a["cycled"], "B_cycled": b["cycled"],
            # Per-ring residue agreement.  The 13-ring is clamped to the target in both
            # arms, so it is 1 by construction and is not recorded as evidence.
            "A_ring3": int(a["positions"][R3] == truth[R3]),
            "A_ring5": int(a["positions"][R5] == truth[R5]),
            "A_ring7": int(a["positions"][R7] == truth[R7]),
            "B_ring7": int(b["positions"][R7] == truth[R7]),
            "B_ring3": int(b["positions"][R3] == truth[R3]),
            "B_ring5": int(b["positions"][R5] == truth[R5]),
        })
    return {"load": load, "n": trials, "recs": recs,
            "A_secs": secs["A"], "B_secs": secs["B"]}


def summarise(cell):
    r = cell["recs"]
    n = len(r)
    out = {"load": cell["load"], "n": n,
           "A_secs": cell["A_secs"], "B_secs": cell["B_secs"]}
    for arm in ("A", "B"):
        it = np.array([x[arm + "_iters"] for x in r], dtype=float)
        out[arm + "_correct"] = sum(x[arm + "_correct"] for x in r)
        out[arm + "_any"] = sum(x[arm + "_any"] for x in r)
        out[arm + "_converged"] = sum(x[arm + "_converged"] for x in r)
        out[arm + "_cycled"] = sum(x[arm + "_cycled"] for x in r)
        out[arm + "_median_iters"] = float(np.median(it))
        out[arm + "_mean_iters"] = float(it.mean())
        out[arm + "_ms"] = 1000.0 * cell[arm + "_secs"] / n
    out["B_median_s1"] = float(np.median(np.array([x["B_iters_s1"] for x in r], float)))
    out["B_median_s2"] = float(np.median(np.array([x["B_iters_s2"] for x in r], float)))
    # Where each arm's answer goes wrong, ring by ring (report-only; no threshold).
    for key in ("A_ring3", "A_ring5", "A_ring7", "B_ring3", "B_ring5", "B_ring7"):
        out[key] = sum(x[key] for x in r)
    # Stage-2 (3 and 5 rings) accuracy conditional on stage 1 having settled the right
    # 7-residue -- the halo's second stage, isolated.
    s1_ok = [x for x in r if x["B_ring7"]]
    out["B_s1_ok_n"] = len(s1_ok)
    out["B_s2_given_s1_ok"] = (sum(1 for x in s1_ok if x["B_ring3"] and x["B_ring5"])
                               if s1_ok else 0)
    # Oracle: is the answer reachable at all, i.e. would running BOTH arms help?
    out["oracle_either"] = sum(1 for x in r if x["A_correct"] or x["B_correct"])
    # Paired discordance (supplementary, no threshold is fitted to it).
    out["discord_B_only"] = sum(1 for x in r if x["B_correct"] and not x["A_correct"])
    out["discord_A_only"] = sum(1 for x in r if x["A_correct"] and not x["B_correct"])
    return out


def print_decomposition(cells):
    """Report-only.  Per-ring accuracy and where the halo's error actually lives.

    Nothing here feeds the pre-registered decision; it exists so the KILL names a cause
    instead of only a number.
    """
    print("\n--- WHERE THE ERROR LIVES (report-only, feeds no decision) ---")
    print("The 13-ring is clamped to the target in both arms, so it is right by")
    print("construction and is omitted.  Every row is a Wilson-99% interval.")
    for c in cells:
        n = c["n"]
        print("\n  M = %d  (n = %d, chance 1/M = %.1f%%)" % (c["load"], n, pct(1.0 / c["load"])))
        rows = [
            ("A one-resonator  7-ring", c["A_ring7"]),
            ("A one-resonator  5-ring", c["A_ring5"]),
            ("A one-resonator  3-ring", c["A_ring3"]),
            ("B halo stage 1   7-ring", c["B_ring7"]),
            ("B halo stage 2   5+3 both", c["B_s2_given_s1_ok"]),
        ]
        for label, k in rows:
            denom = c["B_s1_ok_n"] if label.endswith("5+3 both") else n
            if denom == 0:
                print("    %-26s n/a (no stage-1 successes)" % label)
                continue
            _, lo, hi = wilson(k, denom, Z99)
            print("    %-26s %3d/%-3d %4d%% [%5.1f,%5.1f]%s"
                  % (label, k, denom, pct(k / denom), pct(lo), pct(hi),
                     "   (of stage-1 hits)" if label.endswith("5+3 both") else ""))
        _, lo_o, hi_o = wilson(c["oracle_either"], n, Z99)
        print("    %-26s %3d/%-3d %4d%% [%5.1f,%5.1f]"
              % ("either arm correct", c["oracle_either"], n, pct(c["oracle_either"] / n),
                 pct(lo_o), pct(hi_o)))
        print("    paired: A-only %d, B-only %d -> the two arms fail on different trials"
              % (c["discord_A_only"], c["discord_B_only"]))


def print_table(cells):
    print("\n=== T4: two-stage halo chain (B) vs one resonator (A), 13-ring clamped ===")
    print("D=%d mods=%s states=%d max_iter=%d quant=%s  chance = 1/M"
          % (D, MODS, STATES, MAX_ITER, QUANT))
    print("target recall  = all 4 rings equal the TARGET's residues")
    print("any-mark recall= all 4 rings equal SOME mark in the slot")
    print()
    hdr = ("%4s %5s %4s | %8s %-16s %7s | %6s %6s | %8s %-16s %6s %6s %6s"
           % ("M", "n", "arm", "target", "wilson99", "chance", "medIt", "ms",
              "any-mark", "wilson99", "conv", "cycle", "medIt"))
    print(hdr)
    print("-" * len(hdr))
    for c in cells:
        for arm, name in (("A", "one"), ("B", "halo")):
            _, lo_t, hi_t = wilson(c[arm + "_correct"], c["n"], Z99)
            _, lo_a, hi_a = wilson(c[arm + "_any"], c["n"], Z99)
            print("%4d %5d %4s | %3d/%-3d %4d%% [%5.1f,%5.1f] %6.1f%% | %6.1f %6.2f |"
                  " %3d/%-3d %4d%% [%5.1f,%5.1f] %5.1f%% %5.1f%% %6.1f"
                  % (c["load"], c["n"], name, c[arm + "_correct"], c["n"],
                     pct(c[arm + "_correct"] / c["n"]), pct(lo_t), pct(hi_t),
                     pct(1.0 / c["load"]), c[arm + "_median_iters"], c[arm + "_ms"],
                     c[arm + "_any"], c["n"], pct(c[arm + "_any"] / c["n"]),
                     pct(lo_a), pct(hi_a),
                     pct(c[arm + "_converged"] / c["n"]),
                     pct(c[arm + "_cycled"] / c["n"]),
                     c[arm + "_median_iters"]))
        print("     stage split (halo): stage 1 median %.1f it, stage 2 median %.1f it; "
              "paired discards: A-only %d, B-only %d"
              % (c["B_median_s1"], c["B_median_s2"], c["discord_A_only"],
                 c["discord_B_only"]))
    print()
    print("%4s %14s %14s %10s %12s %12s"
          % ("M", "A wall (s)", "B wall (s)", "iters ratio", "A ms/trial", "B ms/trial"))
    for c in cells:
        ratio = c["B_median_iters"] / c["A_median_iters"] if c["A_median_iters"] else float("nan")
        print("%4d %14.2f %14.2f %10.2f %12.2f %12.2f"
              % (c["load"], c["A_secs"], c["B_secs"], ratio, c["A_ms"], c["B_ms"]))


# -------------------------------------------------------------------------- decision
def evaluate_criterion(c):
    """The pre-registered test at one load.  Returns (clause1, clause2, detail lines)."""
    pa, lo_a, hi_a = wilson(c["A_correct"], c["n"], Z99)
    pb, lo_b, hi_b = wilson(c["B_correct"], c["n"], Z99)
    clause1 = lo_b > pa
    overlap = not (hi_b < lo_a or hi_a < lo_b)
    iter_ok = c["B_median_iters"] <= 0.5 * c["A_median_iters"]
    clause2 = overlap and iter_ok
    lines = [
        "  Arm A target recall %d/%d = %.1f%%  wilson99 = [%.1f%%, %.1f%%]  median iters %.1f"
        % (c["A_correct"], c["n"], pct(pa), pct(lo_a), pct(hi_a), c["A_median_iters"]),
        "  Arm B target recall %d/%d = %.1f%%  wilson99 = [%.1f%%, %.1f%%]  median iters %.1f"
        % (c["B_correct"], c["n"], pct(pb), pct(lo_b), pct(hi_b), c["B_median_iters"]),
        "  chance at M=%d = %.1f%%   uniform 1/%d = %.2f%%"
        % (c["load"], pct(1.0 / c["load"]), STATES, pct(1.0 / STATES)),
        "  clause 1  lo_B (%.1f%%) > point_A (%.1f%%)  ->  %s"
        % (pct(lo_b), pct(pa), "TRUE" if clause1 else "false"),
        "  clause 2  intervals overlap = %s  AND  medIt_B (%.1f) <= 0.5 x medIt_A (%.1f = %.1f)"
        "  ->  %s"
        % (overlap, c["B_median_iters"], c["A_median_iters"], 0.5 * c["A_median_iters"],
           "TRUE" if clause2 else "false"),
        "  criterion at M=%d: %s" % (c["load"], "PASS" if (clause1 or clause2) else "KILL"),
    ]
    return clause1, clause2, lines


def decide(cells):
    by_load = {c["load"]: c for c in cells}
    print("\n=== PRE-REGISTERED DECISION ===")
    results = {}
    for load in sorted(by_load):
        c1, c2, lines = evaluate_criterion(by_load[load])
        results[load] = (c1, c2)
        if load == DECISION_LOAD:
            print("decision cell (the one the criterion names): M = %d" % load)
        else:
            print("reported for transparency: M = %d" % load)
        for ln in lines:
            print(ln)
        print()

    c1, c2 = results[DECISION_LOAD]
    passed = c1 or c2
    c12 = results.get(12)
    if passed and c12 is not None and not (c12[0] or c12[1]):
        print("NOTE: the criterion holds at M=%d but NOT at M=12.  A stricter reading that"
              % DECISION_LOAD)
        print("      requires the criterion at both loads would call this KILL.  The"
              " verdict")
        print("      below follows the reading stated at the top of this output (M=32).")
        print()
    if passed:
        why = ("Arm B's Wilson-99%% lower bound (%.1f%%) exceeds Arm A's point recall"
               " (%.1f%%) at M=%d -- clause 1"
               % (pct(wilson(by_load[DECISION_LOAD]["B_correct"],
                             by_load[DECISION_LOAD]["n"], Z99)[1]),
                  pct(by_load[DECISION_LOAD]["A_correct"] / by_load[DECISION_LOAD]["n"]),
                  DECISION_LOAD)) if c1 else \
               ("Arm B matches Arm A (overlapping Wilson-99%% intervals) with median total "
               "iterations %.1f <= 0.5 x %.1f at M=%d -- clause 2"
               % (by_load[DECISION_LOAD]["B_median_iters"],
                  by_load[DECISION_LOAD]["A_median_iters"], DECISION_LOAD))
        return True, "PASS: the two-stage halo chain buys something on a crowded slot (%s)." % why
    return False, ("KILL: the halo buys nothing. At M=%d Arm B's Wilson-99%% lower bound "
                   "(%.1f%%) does not exceed Arm A's point recall (%.1f%%), and Arm B does "
                   "not match Arm A at half the iterations (medIt_B %.1f vs medIt_A %.1f)."
                   % (DECISION_LOAD,
                      pct(wilson(by_load[DECISION_LOAD]["B_correct"],
                                 by_load[DECISION_LOAD]["n"], Z99)[1]),
                      pct(by_load[DECISION_LOAD]["A_correct"] / by_load[DECISION_LOAD]["n"]),
                      by_load[DECISION_LOAD]["B_median_iters"],
                      by_load[DECISION_LOAD]["A_median_iters"]))


# ----------------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--quick", action="store_true",
                    help="%d trials per cell instead of %d" % (QUICK_TRIALS, FULL_TRIALS))
    ap.add_argument("--trials", type=int, default=None, help="override trials per cell")
    ap.add_argument("--loads", default=",".join(str(x) for x in LOADS),
                    help="comma-separated slot loads")
    ap.add_argument("--verify-only", action="store_true",
                    help="run the two integrity checks and exit")
    args = ap.parse_args(argv)

    trials = args.trials if args.trials else (QUICK_TRIALS if args.quick else FULL_TRIALS)
    loads = tuple(int(x) for x in args.loads.split(",") if x.strip())

    print("RING-1 T4 -- two-stage halo chain vs one resonator on crowded slots")
    print("D=%d mods=%s states=%d max_iter=%d quant=%s trials/cell=%d loads=%s"
          % (D, MODS, STATES, MAX_ITER, QUANT, trials, list(loads)))
    print("python %s  numpy %s" % (".".join(map(str, sys.version_info[:3])), np.__version__))
    print("threads: OMP=%s OPENBLAS=%s MKL=%s"
          % (os.environ["OMP_NUM_THREADS"], os.environ["OPENBLAS_NUM_THREADS"],
             os.environ["MKL_NUM_THREADS"]))
    print()
    print(PRE_REGISTERED)
    print()

    t_build = time.time()
    rings = make_rings(MODS, D=D, seed=BASE_SEED, quant=QUANT)
    print("built %d float codebooks in %.2fs (same base seed as RING1-CORE)"
          % (len(rings), time.time() - t_build))

    # ---- integrity 1: the local free-ring resonator IS the library resonator
    print("\n--- INTEGRITY 1: resonate_free() == ring1_core.resonate() ---")
    t0 = time.time()
    mism = check_equivalence(rings)
    print("  40 random problems (load 1..8, clamp 0..2): %d mismatches (%.2fs)"
          % (len(mism), time.time() - t0))
    for n, load, cn, lib, mine in mism[:5]:
        print("    problem %d (load=%d clamp=%d): lib=%s mine=%s"
              % (n, load, cn,
                 {k: lib[k] for k in ("positions", "iters", "converged", "cycled")},
                 {k: mine[k] for k in ("positions", "iters", "converged", "cycled")}))
    equiv_ok = not mism
    print("  EQUIVALENCE %s" % ("PASS" if equiv_ok else "FAIL"))

    # ---- integrity 2: Arm A IS RING1-CORE's published cell
    print("\n--- INTEGRITY 2: Arm A reproduces RING1-CORE (T1, c=1, float, 200 trials) ---")
    xc = check_against_core(rings)
    core_ok = True
    for load in sorted(xc):
        e = xc[load]
        print("  M=%2d  this run %3d/%-3d target, %3d/%-3d any-mark, medIt %.1f   "
              "RING1-CORE %3d/%-3d target, %3d/%-3d any-mark, medIt %.1f   %s"
              % (load, e["correct"], e["n"], e["any"], e["n"], e["median_iters"],
                 e["exp"]["correct"], e["exp"]["n"], e["exp"]["any"], e["exp"]["n"],
                 e["exp"]["median_iters"], "MATCH" if e["ok"] else "MISMATCH"))
        core_ok = core_ok and e["ok"]
    print("  HARNESS CROSS-CHECK %s" % ("PASS" if core_ok else "FAIL"))
    if not (equiv_ok and core_ok):
        print("\nINTEGRITY FAILURE -- the two arms would not be the same harness, so no")
        print("number below would be meaningful.  Stopping without reporting results.")
        return 1

    if args.verify_only:
        print("\nverify-only: both integrity checks passed, no grid run.")
        return 0

    # ------------------------------------------------------------------------ grid
    t_start = time.time()
    cells = []
    for load in loads:
        t0 = time.time()
        c = summarise(run_cell(trials, load, rings))
        cells.append(c)
        _, lo_b, _ = wilson(c["B_correct"], c["n"], Z99)
        print("  cell M=%2d -> A %d/%d, B %d/%d (wilson99 lower %.1f%%), "
              "medIt A %.1f / B %.1f  (%.1fs)"
              % (load, c["A_correct"], c["n"], c["B_correct"], c["n"], pct(lo_b),
                 c["A_median_iters"], c["B_median_iters"], time.time() - t0))

    print_table(cells)
    print_decomposition(cells)
    passed, verdict = decide(cells)
    print("\n" + "=" * 78)
    print("VERDICT: %s" % verdict)
    print("total wall clock: %.1fs" % (time.time() - t_start))
    print("=" * 78)
    return 0 if passed else 0      # exit 0 on a clean run; the verdict is the gate


if __name__ == "__main__":
    sys.exit(main())

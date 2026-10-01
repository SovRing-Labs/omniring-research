#!/usr/bin/env python3
"""RING-1 core grid runner: T1 (exact counter rings: clamp x load x quantisation),
T5 (eigengap as a confidence signal) and T6 (slot capacity -> overflow rule).

Task: RING1-CORE (_Pads/RING/ring1-w1.wave.yaml).  Pillar: Nervous System, Loop step "Read".
Synthetic only, Python 3 + numpy, no dependency on the C phase kernel.

Every threshold used to decide PASS/KILL is pre-registered in the brief and is
printed verbatim at the top of the output (see PRE-REGISTERED below).  No threshold
is fitted to these results.

Usage:
    python3 _Pads/RING/ring1/run_core.py            # full: 200 trials/cell
    python3 _Pads/RING/ring1/run_core.py --quick    # 30 trials/cell
    python3 _Pads/RING/ring1/run_core.py --cells T1 --quick
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
from ring1_core import make_rings, make_slot, resonate, crt, wilson  # noqa: E402

# --------------------------------------------------------------------------- config
D = 5120
MODS = (3, 5, 7, 13)
STATES = 1
for _m in MODS:
    STATES *= _m                                   # 1,365
MAX_MARK = STATES - 1                             # marks drawn uniformly 0..1364
MAX_ITER = 50
BASE_SEED = 20260928

# Clamp order is fixed by the brief: 13-ring, then 7, then 5.
# MODS = (3,5,7,13) -> ring indices 3, 2, 1.  The 3-ring is never clamped.
CLAMP_ORDER = (3, 2, 1)

T1_LOADS = (4, 12, 32)
T1_CLAMPS = (0, 1, 2, 3)
T1_QUANTS = ("float", "k16")
T6_LOADS = (1, 2, 4, 8, 12, 16, 24, 32, 48)
T6_CLAMP = 1
T6_QUANT = "float"

Z99 = 2.5758293035489004                          # two-sided normal quantile, 99%

PRE_REGISTERED = """\
PRE-REGISTERED DECISION (verbatim from _Pads/RING/ring1-w1.wave.yaml, task RING1-CORE, step 6):
  PASS if, at M = 12 and c = 1 (float), the Wilson-99% lower bound of target recall is > 2/M
  (twice chance). Otherwise KILL: clamping does not select a mark out of a crowded slot.
  The k16 cells are reported, never used to decide PASS/KILL.
PRE-REGISTERED T6 (verbatim, step 6 scope B):
  capacity_50 = largest M whose Wilson-99% LOWER bound of target recall is >= 0.5.
PRE-REGISTERED T5 (verbatim, scope B):
  Report only, no threshold.  Spearman rank correlation of gap_first and gap_min with
  correctness and with iterations; plus correctness rate by gap_min quartile.
REPORTING RULES (verbatim, step 4):
  report the chance rate beside every recall figure; Wilson 99% intervals on every rate.
  chance = 1/M  (the pre-registered chance baseline; the uniform 1/1365 target chance is
  reported alongside it as a second column and is NOT used in any decision)."""

# ------------------------------------------------------------------ small utilities
def spearman(x, y):
    """Spearman rho via average ranks + Pearson (numpy only, no scipy dependency)."""
    rx, ry = _rankdata(x), _rankdata(y)
    if rx.size < 3:
        return float("nan")
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    den = float(np.sqrt((rx * rx).sum() * (ry * ry).sum()))
    return float((rx * ry).sum() / den) if den > 0 else float("nan")


def _rankdata(a):
    a = np.asarray(a, dtype=float)
    n = a.size
    order = np.argsort(a, kind="mergesort")
    sa = a[order]
    ranks = np.empty(n, dtype=float)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and sa[j + 1] == sa[i]:
            j += 1
        ranks[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return ranks


def pct(x):
    return 100.0 * float(x)


def pct_str(x):
    return "%5.1f%%" % pct(x)


def cell_seed(stream, load, clamp, quant):
    return np.random.SeedSequence([BASE_SEED, stream, int(load), int(clamp),
                                   T1_QUANTS.index(quant)])


def make_clamp(clamp_n, target):
    """clamp_n rings pinned to the target's true residues, in the brief's order."""
    out = {}
    for i in CLAMP_ORDER[:clamp_n]:
        out[i] = int(target) % MODS[i]
    return out


# ----------------------------------------------------------------------------- T1
def run_t1_cell(trials, load, clamp_n, quant, rings):
    """Return the per-trial records plus the cell summary for one grid point."""
    rng = np.random.default_rng(cell_seed(1, load, clamp_n, quant))
    t0 = time.time()
    recs = []
    for _ in range(trials):
        marks = rng.integers(0, STATES, load)
        target = int(marks[0])
        clamp = make_clamp(clamp_n, target)
        v = make_slot([int(x) for x in marks], rings, MODS)
        res = resonate(v, rings, clamp, MAX_ITER, 0)
        pos = res["positions"]
        truth = [target % m for m in MODS]
        any_mark = any(pos == [int(x) % m for m in MODS] for x in marks)
        recs.append({
            "correct": int(pos == truth),
            "any": int(any_mark),
            "converged": int(bool(res["converged"])),
            "cycled": int(bool(res["cycled"])),
            "iters": int(res["iters"]),
            "gap_first": float(res["gap_first"]),
            "gap_min": float(res["gap_min"]),
        })
    elapsed = time.time() - t0
    n = len(recs)
    c_k = sum(r["correct"] for r in recs)
    a_k = sum(r["any"] for r in recs)
    cv_k = sum(r["converged"] for r in recs)
    cy_k = sum(r["cycled"] for r in recs)
    iters = np.array([r["iters"] for r in recs], dtype=float)
    return {
        "load": load, "clamp": clamp_n, "quant": quant, "n": n,
        "correct": c_k, "any": a_k, "converged": cv_k, "cycled": cy_k,
        "median_iters": float(np.median(iters)),
        "mean_iters": float(iters.mean()),
        "secs": elapsed, "recs": recs,
    }


def print_t1(cells):
    print("\n=== T1: exact counter rings -- clamp x load x quantisation ===")
    print("D=%d mods=%s states=%d max_iter=%d  (each ring is a count ring; chance = 1/M)"
          % (D, MODS, STATES, MAX_ITER))
    print("target recall  = all 4 rings equal the TARGET's residues")
    print("any-mark recall= all 4 rings equal SOME mark in the slot")
    print()
    hdr = ("%3s %5s %6s %5s | %8s %-16s %7s | %8s %-16s %7s | %6s %6s %6s %6s"
           % ("M", "clamp", "quant", "n", "target", "wilson99", "chance",
              "any-mark", "wilson99", "1/1365", "conv", "cycle", "medIt", "secs"))
    print(hdr)
    print("-" * len(hdr))
    for c in cells:
        _, lo_t, hi_t = wilson(c["correct"], c["n"], Z99)
        _, lo_a, hi_a = wilson(c["any"], c["n"], Z99)
        print("%3d %5d %6s %5d | %3d/%-3d %4d%% [%5.1f,%5.1f] %6.1f%% | %3d/%-3d %4d%% [%5.1f,%5.1f] %6.2f%% | %5.1f%% %5.1f%% %6.1f %6.1f"
              % (c["load"], c["clamp"], c["quant"], c["n"],
                 c["correct"], c["n"], pct(c["correct"] / c["n"]), pct(lo_t), pct(hi_t),
                 pct(1.0 / c["load"]),
                 c["any"], c["n"], pct(c["any"] / c["n"]), pct(lo_a), pct(hi_a),
                 pct(1.0 / STATES),
                 pct(c["converged"] / c["n"]), pct(c["cycled"] / c["n"]),
                 c["median_iters"], c["secs"]))


# ----------------------------------------------------------------------------- T5
def print_t5(cells):
    pooled = [r for c in cells for r in c["recs"]]
    correct = np.array([r["correct"] for r in pooled], dtype=float)
    iters = np.array([r["iters"] for r in pooled], dtype=float)
    gf = np.array([r["gap_first"] for r in pooled], dtype=float)
    gm = np.array([r["gap_min"] for r in pooled], dtype=float)
    n = len(pooled)

    print("\n=== T5: eigengap as a confidence signal (pooled over all T1 trials) ===")
    print("pooled n = %d trials (both quantisations, all loads, all clamp counts)" % n)
    print("Spearman rho, report-only -- no threshold is fitted:")
    print("%-12s %-12s %s" % ("gap", "vs", "rho"))
    for name, arr in (("gap_first", gf), ("gap_min", gm)):
        print("%-12s %-12s %+.4f" % (name, "correct", spearman(arr, correct)))
        print("%-12s %-12s %+.4f" % (name, "iters", spearman(arr, iters)))

    print("\ncorrectness by gap_min quartile (equal-count bins):")
    order = np.argsort(gm, kind="mergesort")
    bins = np.array_split(order, 4)
    print("%-8s %-22s %6s %-16s %9s" % ("quartile", "gap_min range", "n",
                                       "correct wilson99", "medIt"))
    for qi, b in enumerate(bins, 1):
        lo_b, hi_b = float(gm[b].min()), float(gm[b].max())
        k, nb = int(correct[b].sum()), int(b.size)
        _, lo, hi = wilson(k, nb, Z99)
        print("Q%d       [%.4f, %.4f]%s %6d %4d/%-4d %4d%% [%5.1f,%5.1f] %8.1f"
              % (qi, lo_b, hi_b, " " * max(1, 8 - len("%.4f, %.4f" % (lo_b, hi_b))),
                 nb, k, nb, pct(k / nb), pct(lo), pct(hi),
                 float(np.median(iters[b]))))


# ----------------------------------------------------------------------------- T6
def run_t6_cell(trials, load, rings):
    rng = np.random.default_rng(np.random.SeedSequence(
        [BASE_SEED, 6, int(load), T6_CLAMP, T1_QUANTS.index(T6_QUANT)]))
    t0 = time.time()
    recs = []
    for _ in range(trials):
        marks = rng.integers(0, STATES, load)
        target = int(marks[0])
        v = make_slot([int(x) for x in marks], rings, MODS)
        res = resonate(v, rings, make_clamp(T6_CLAMP, target), MAX_ITER, 0)
        pos = res["positions"]
        truth = [target % m for m in MODS]
        recs.append({
            "correct": int(pos == truth),
            "any": int(any(pos == [int(x) % m for m in MODS] for x in marks)),
            "converged": int(bool(res["converged"])),
            "cycled": int(bool(res["cycled"])),
            "iters": int(res["iters"]),
        })
    elapsed = time.time() - t0
    n = len(recs)
    return {"load": load, "n": n, "correct": sum(r["correct"] for r in recs),
            "any": sum(r["any"] for r in recs),
            "converged": sum(r["converged"] for r in recs),
            "cycled": sum(r["cycled"] for r in recs),
            "median_iters": float(np.median([r["iters"] for r in recs])),
            "secs": elapsed}


def print_t6(cells):
    print("\n=== T6: slot capacity (c=%d, quant=%s) -> overflow rule ===" % (T6_CLAMP, T6_QUANT))
    print("capacity_50 = largest M whose Wilson-99% LOWER bound of target recall >= 0.5")
    hdr = ("%4s %5s | %8s %-16s %7s | %8s %-16s %6s | %6s %6s %6s %6s"
           % ("M", "n", "target", "wilson99", "chance", "any-mark", "wilson99",
              "1/1365", "conv", "cycle", "medIt", "secs"))
    print(hdr)
    print("-" * len(hdr))
    cap = None
    for c in cells:
        _, lo_t, hi_t = wilson(c["correct"], c["n"], Z99)
        _, lo_a, hi_a = wilson(c["any"], c["n"], Z99)
        flag = ""
        if lo_t >= 0.5:
            cap = c["load"]
            flag = "  <- >= 0.5 lower bound"
        print("%4d %5d | %3d/%-3d %4d%% [%5.1f,%5.1f] %6.1f%% | %3d/%-3d %4d%% [%5.1f,%5.1f] %6.2f%% | %5.1f%% %5.1f%% %6.1f %6.1f%s"
              % (c["load"], c["n"], c["correct"], c["n"], pct(c["correct"] / c["n"]),
                 pct(lo_t), pct(hi_t), pct(1.0 / c["load"]),
                 c["any"], c["n"], pct(c["any"] / c["n"]), pct(lo_a), pct(hi_a),
                 pct(1.0 / STATES), pct(c["converged"] / c["n"]), pct(c["cycled"] / c["n"]),
                 c["median_iters"], c["secs"], flag))
    print("capacity_50 = %s" % (cap if cap is not None else "none (no M reached 0.5 lower bound)"))
    return cap


# ------------------------------------------------------------------------ decision
def decide(t1_cells):
    """The pre-registered PASS/KILL test: M=12, c=1, float, Wilson-99% LOWER > 2/M."""
    for c in t1_cells:
        if c["load"] == 12 and c["clamp"] == 1 and c["quant"] == "float":
            _, lo, _ = wilson(c["correct"], c["n"], Z99)
            bar = 2.0 / 12.0
            print("\n=== PRE-REGISTERED DECISION ===")
            print("cell: M=12 clamp=1 quant=float   n=%d" % c["n"])
            print("target recall %d/%d = %.1f%%  wilson99 = [%.1f%%, %.1f%%]"
                  % (c["correct"], c["n"], pct(c["correct"] / c["n"]), pct(lo),
                     pct(wilson(c["correct"], c["n"], Z99)[2])))
            print("bar 2/M = %.4f  (%.1f%%)   lower bound = %.4f (%.1f%%)"
                  % (bar, pct(bar), lo, pct(lo)))
            if lo > bar:
                return True, ("PASS: clamping selects the cued mark out of a crowded slot "
                              "(M=12, c=1, float, wilson-99 lower %.1f%% > 2/M %.1f%%)"
                              % (pct(lo), pct(bar)))
            return False, ("KILL: clamping does not select a mark out of a crowded slot "
                           "(M=12, c=1, float, wilson-99 lower %.1f%% <= 2/M %.1f%%)"
                           % (pct(lo), pct(bar)))
    return False, "KILL: decision cell (M=12, c=1, float) missing from the grid"


# ---------------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--quick", action="store_true",
                    help="30 trials per cell instead of 200")
    ap.add_argument("--trials", type=int, default=None,
                    help="override trials per cell")
    ap.add_argument("--cells", default="T1,T5,T6",
                    help="comma-separated subset of T1,T5,T6")
    args = ap.parse_args(argv)
    trials = args.trials if args.trials else (30 if args.quick else 200)
    want = {s.strip().upper() for s in args.cells.split(",") if s.strip()}

    print("RING-1 core grid -- D=%d mods=%s states=%d max_iter=%d trials/cell=%d"
          % (D, MODS, STATES, MAX_ITER, trials))
    print("base seed = %d (all cell seeds are SeedSequence children of it, so every"
          % BASE_SEED)
    print("number below is reproducible from the command line alone)")
    print("python %s  numpy %s" % (sys.executable.split("/")[-1], np.__version__))
    print("threads: OMP=%s OPENBLAS=%s MKL=%s"
          % (os.environ["OMP_NUM_THREADS"], os.environ["OPENBLAS_NUM_THREADS"],
             os.environ["MKL_NUM_THREADS"]))
    print()
    print(PRE_REGISTERED)

    rings_cache = {}
    for q in T1_QUANTS:
        if "T1" in want or "T5" in want or "T6" in want:
            t0 = time.time()
            rings_cache[q] = make_rings(MODS, D=D, seed=BASE_SEED, quant=q)
            print("  built %-5s codebooks in %.2fs" % (q, time.time() - t0))
    print("  both codebooks come from the same j_d stream (same seed), so the")
    print("  float vs k16 comparison is paired rather than confounded by the draw.")

    t_start = time.time()
    t1_cells = []
    if "T1" in want or "T5" in want:
        for q in T1_QUANTS:
            rings = rings_cache[q]
            for load in T1_LOADS:
                for clamp_n in T1_CLAMPS:
                    t0 = time.time()
                    c = run_t1_cell(trials, load, clamp_n, q, rings)
                    t1_cells.append(c)
                    print("  cell M=%2d clamp=%d quant=%-5s -> %d/%d target, "
                          "%.1f%% chance  (%.1fs)"
                          % (load, clamp_n, q, c["correct"], c["n"],
                             pct(1.0 / load), c["secs"]))
        print("\nT1 grid complete: %d cells x %d trials = %d trials in %.1fs"
              % (len(t1_cells), trials, len(t1_cells) * trials, time.time() - t_start))
        print_t1(t1_cells)

    if "T5" in want and t1_cells:
        print_t5(t1_cells)

    t6_cells = []
    if "T6" in want:
        rings = rings_cache[T6_QUANT]
        for load in T6_LOADS:
            c = run_t6_cell(trials, load, rings)
            t6_cells.append(c)
            print("  T6 M=%2d -> %d/%d target, wilson99 lower %.1f%% (%.1fs)"
                  % (load, c["correct"], c["n"],
                     pct(wilson(c["correct"], c["n"], Z99)[1]), c["secs"]))
        print_t6(t6_cells)

    passed, verdict = decide(t1_cells) if t1_cells else (False, "KILL: T1 not run")
    print("\n" + "=" * 78)
    print("VERDICT: %s" % verdict)
    print("total wall clock: %.1fs" % (time.time() - t_start))
    print("=" * 78)
    return 0 if passed else 0      # exit 0 either way; the verdict is the gate


if __name__ == "__main__":
    sys.exit(main())

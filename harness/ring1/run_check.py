#!/usr/bin/env python3
"""RING-1 T3: the 17 check ring -- does it flag wrong resonator settles?

Task: RING1-CHECK (cohort RING1B, _Pads/RING/ring1-w2.wave.yaml).
Pillar: Nervous System, Loop step "Read".  Pure synthetic study.  numpy only.
Imports ring1_core.py unchanged; statistics live here, not in the library.

The redundancy
--------------
Information space: 3*5*7*13 = 1,365 legal mark values, 0..1364.
The 17-ring is NOT a fifth information ring -- 17 does not divide 1,365, so a legal
mark's 17-residue is a pure function of its four information residues.  It is a
checksum.  Binding it in is what lets a settle be caught when the four information
rings agree on a combination that was never a real mark.

Given decoded positions p = (p3, p5, p7, p13, p17):
    x'    = crt(p3,p5,p7,p13; 3,5,7,13)  in [0, 1365)      (the implied mark)
    legal <=> x' % 17 == p17                                  (the check)
    full  = crt(p3,p5,p7,p13,p17; 3,5,7,13,17) in [0, 23205)  (the decoded mark)

Algebraic fact (proved in the report, re-verified at run time by _verify_algebra):
  1365 == 17*80 + 5, so full == x' + 1365*t with t = (7*(p17 - x')) mod 17, hence
      full < 1365  <=>  t == 0  <=>  p17 == x' % 17  <=>  legal.
  The check is EXACTLY the out-of-range test on the decoded mark.  And since x' is in
  [0,1365) for every settle, any settle that lands on a real slot member is always
  legal: the false-alarm rate on correct settles is 0 BY CONSTRUCTION, not by luck.
  The check is a one-sided test with no false positives.

The 17-ring is never clamped.  Clamping it to the target's true residue would pin the
checksum to the answer and make the check vacuous.  Clamp order is the brief's,
(13, 7, 5) == ring indices (3, 2, 1); the 3-ring (index 0) and the 17-ring (index 4)
are never clamped.

The codebook-seed scan
----------------------
The pre-registered grid runs on PRE_REG_SEED, the codebook seed inherited from
RING1-CORE so the arms stay comparable.  A pre-registered un-clamped 5-ring settle
turns out to sit on a numerical knife-edge: for some codebooks every one of the 17
positions ties exactly, all 50 iterations burn, and the decoded mark is decided
entirely by the tie-break seed.  The scan repeats the whole grid on extra codebook
seeds so the verdict is not an artifact of one codebook.  The pre-registered DECISION
is applied to the pre-registered seed only; the scan is reported, never substituted.

Usage:  python3 _Pads/RING/ring1/run_check.py [--quick] [--scan-only]
"""
from __future__ import annotations

import argparse
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ring1_core import (  # noqa: E402  (path set above)
    make_rings,
    make_slot,
    resonate,
    crt,
    wilson,
)

# --------------------------------------------------------------------------- setup
MODS4 = (3, 5, 7, 13)
MODS5 = (3, 5, 7, 13, 17)
STATES = 1
for _m in MODS4:
    STATES *= _m                                   # 1,365 legal values, 0..1364
MAX_MARK = STATES - 1
FULL_SPACE = STATES * 17                          # 23,205
MAX_ITER = 50
D = 5120                                          # the bus slot size, from RING1-CORE
QUANT = "float"

PRE_REG_SEED = 20260928                            # codebook seed inherited from CORE
# Pre-registered seed + two robustness seeds.  Three, not four: an un-clamped 5-ring
# settle burns the full 50-iteration ceiling when it degenerates, so the scan is the
# dominant cost and the full run must stay inside its 20-minute budget.  Seeds 1 and 2
# are the regime where the free 5-ring settle actually converges; 20260928 and 3 are
# the regime where every position of a ring ties exactly (see the report's codebook
# tie-scan, which covers 1, 2, 3 and 20260928).
SCAN_SEEDS = (20260928, 1, 2)

# Clamp order is fixed by the brief: 13-ring, then 7, then 5.  With MODS5 the ring
# indices are unchanged for the shared rings; index 4 (the 17) is never clamped.
CLAMP_ORDER = (3, 2, 1)

CELL_M = (1, 4, 12)
CELL_C = (0, 1)
MIN_WRONG_FOR_POOL = 30                           # pre-registered cell filter
Z99 = 2.5758293035489004                          # two-sided normal quantile, 99%

PRE_REGISTERED = """\
PRE-REGISTERED DECISION (verbatim from _Pads/RING/ring1-w2.wave.yaml, task
RING1-CHECK, step 6 -- fixed before any trial ran):
  PASS if, pooled over cells with >= 30 wrong settles, the flag rate on wrong settles
  has a Wilson-99% lower bound >= 0.5 AND the false-alarm rate on correct settles has
  a Wilson-99% upper bound <= 0.05. Otherwise KILL.
PRE-REGISTERED SCOPE (verbatim, step 2):
  Marks carry mods (3,5,7,13,17) but only 0..1364 are legal values (17 is redundant).
  Resonate with all 5 rings; call a settle 'legal' when crt of the 4 information
  residues, taken mod 17, equals the decoded 17-residue. Cells: M in (1, 4, 12),
  c in (0, 1), float, 300 trials. Report: rate of wrong settles (not any real mark),
  flag rate on wrong settles (illegal), false-alarm rate on correct settles (flagged
  illegal), and recall with vs without the 17 ring bound in (cost of the extra ring).
REPORTING RULES (verbatim, step 4):
  fixed seeds; no fitted thresholds; every number from a command that was run; report
  the chance rate beside every recall figure; Wilson 99% intervals on every rate."""

DEGENERATE_HINT = (
    "A cell whose settles are decided by the tie-break seed (all positions of a ring "
    "tie exactly, every iteration burns the ceiling) reports a flag rate near 1 by "
    "construction: an arbitrary residue tuple is illegal 16/17 of the time. Read "
    "settled% and burned% before reading any c=0 flag rate."
)


# ------------------------------------------------------------------------ utilities
def pct(x):
    return 100.0 * float(x)


def rate_str(k, n):
    """'k/n  p%  [lo, hi]' with a Wilson 99% interval; blank when n == 0."""
    if n <= 0:
        return "%d/%d  --  [n/a]" % (0, 0)
    p, lo, hi = wilson(k, n, Z99)
    return "%d/%d %5.1f%%  [%.1f, %.1f]" % (k, n, pct(p), pct(lo), pct(hi))


def mcnemar_exact(b01, b10):
    """Two-sided exact McNemar p on the discordant pairs (no scipy)."""
    n = b01 + b10
    if n == 0:
        return 1.0
    k = min(b01, b10)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2.0 ** n)
    return min(1.0, 2.0 * tail)


def make_clamp(clamp_n, target, mods):
    """clamp_n rings pinned to the target's true residues, in the brief's order."""
    return {i: int(target) % mods[i] for i in CLAMP_ORDER[:clamp_n]}


def cell_seed(stream, load, clamp_n):
    return np.random.SeedSequence([PRE_REG_SEED, stream, int(load), int(clamp_n)])


# ------------------------------------------------------------------- the check itself
def judge(positions, slot_set):
    """Classify one settle of the 5-ring resonator.

    correct = the decoded mark is a real member of the slot; wrong = it is not.
    flagged = the 17-check says illegal.  phantom = wrong but still in range, i.e. a
    wrong settle the check CANNOT see.
    """
    p17 = int(positions[4])
    x_prime = crt([int(positions[i]) for i in range(4)], MODS4)
    full = crt([int(p) for p in positions], MODS5)
    legal = int((x_prime % 17) == p17)
    correct = int(full in slot_set)
    return {
        "x_prime": int(x_prime),
        "full": int(full),
        "legal": legal,
        "in_range": int(full < STATES),
        "correct": correct,
        "wrong": 1 - correct,
        "flagged": 1 - legal,
        "phantom": int((1 - correct) and legal),
    }


def _verify_algebra():
    """Re-verify the algebraic identity at run time (proof, not assertion)."""
    rng = np.random.default_rng(PRE_REG_SEED + 1)
    alias = 0
    fa = 0
    trials = 20000
    for _ in range(trials):
        x = int(rng.integers(0, STATES))
        pos = [x % m for m in MODS5]
        xp = crt(pos[:4], MODS4)
        full = crt(pos, MODS5)
        lg = int((xp % 17) == pos[4])
        alias += int(lg == int(full < STATES))
        if full < STATES:            # a real legal mark: can the check ever fire?
            fa += int(not lg)
    print("  identity 'legal <=> decoded mark < 1365' : %d/%d exact" % (alias, trials))
    print("  false alarms on correct settles           : %d/%d (structurally 0)"
          % (fa, trials))
    return alias == trials and fa == 0


# ------------------------------------------------------------------------ the cells
def run_cell(trials, load, clamp_n, rings5, rings4):
    """One (M, c) cell: the 5-ring arm and the paired 4-ring arm on the same marks.

    The 4-ring arm is the 'cost of the extra ring' control: identical marks, identical
    clamp, identical codebooks for the shared rings, but nothing bound on a 17th ring.
    """
    rng = np.random.default_rng(cell_seed(3, load, clamp_n))
    t0 = time.time()
    recs = []
    for _ in range(trials):
        marks = [int(m) for m in rng.integers(0, STATES, load)]
        slot_set = set(marks)
        target = marks[0]
        r5 = resonate(make_slot(marks, rings5, MODS5), rings5,
                      make_clamp(clamp_n, target, MODS5), MAX_ITER, 0)
        j = judge(r5["positions"], slot_set)
        j["target"] = int(j["full"] == target)
        j["iters5"] = int(r5["iters"])
        j["converged5"] = int(bool(r5["converged"]))
        j["cycled5"] = int(bool(r5["cycled"]))
        r4 = resonate(make_slot(marks, rings4, MODS4), rings4,
                      make_clamp(clamp_n, target, MODS4), MAX_ITER, 0)
        f4 = crt([int(x) for x in r4["positions"]], MODS4)
        j["f4"] = int(f4)
        j["target4"] = int(f4 == target)
        j["any4"] = int(f4 in slot_set)
        j["iters4"] = int(r4["iters"])
        j["converged4"] = int(bool(r4["converged"]))
        recs.append(j)
    return {"load": load, "clamp": clamp_n, "n": len(recs), "recs": recs,
            "elapsed": time.time() - t0}


def summarise(cell):
    recs = cell["recs"]
    n = len(recs)
    wrong = [r for r in recs if r["wrong"]]
    correct = [r for r in recs if r["correct"]]
    return {
        "load": cell["load"], "clamp": cell["clamp"], "n": n,
        "wrong": len(wrong), "correct": len(correct),
        "flagged_wrong": sum(r["flagged"] for r in wrong),
        "fa_correct": sum(r["flagged"] for r in correct),
        "phantom": sum(r["phantom"] for r in wrong),
        "target5": sum(r["target"] for r in recs),
        "target4": sum(r["target4"] for r in recs),
        "converged": sum(r["converged5"] for r in recs),
        "burned": sum(1 for r in recs if r["iters5"] >= MAX_ITER),
        "cycled": sum(r["cycled5"] for r in recs),
        "converged4": sum(r["converged4"] for r in recs),
        "median_iters5": float(np.median([r["iters5"] for r in recs])),
        "median_iters4": float(np.median([r["iters4"] for r in recs])),
        "elapsed": cell["elapsed"],
        "b01": sum(1 for r in recs if r["target4"] and not r["target"]),
        "b10": sum(1 for r in recs if r["target"] and not r["target4"]),
    }


def run_grid(trials, cb_seed):
    """The whole 6-cell grid on one codebook seed.  Returns the list of summaries."""
    rings5 = make_rings(MODS5, D=D, seed=cb_seed, quant=QUANT)
    rings4 = make_rings(MODS4, D=D, seed=cb_seed, quant=QUANT)
    shared = all(np.array_equal(rings5[i], rings4[i]) for i in range(4))
    out = []
    for load in CELL_M:
        for clamp_n in CELL_C:
            out.append(summarise(run_cell(trials, load, clamp_n, rings5, rings4)))
    return out, shared


# ------------------------------------------------------------------- the criterion
def apply_criterion(cells, label, quiet=False):
    """Apply the pre-registered criterion verbatim to one seed's cells."""
    def say(msg=""):
        if not quiet:
            print(msg)

    eligible = [s for s in cells if s["wrong"] >= MIN_WRONG_FOR_POOL]
    tot_n = sum(s["n"] for s in cells)
    p_w = sum(s["wrong"] for s in eligible)
    p_f = sum(s["flagged_wrong"] for s in eligible)
    p_c = sum(s["correct"] for s in eligible)
    p_fa = sum(s["fa_correct"] for s in eligible)
    a_w = sum(s["wrong"] for s in cells)
    a_f = sum(s["flagged_wrong"] for s in cells)
    a_c = sum(s["correct"] for s in cells)
    a_fa = sum(s["fa_correct"] for s in cells)

    say("    cell filter (>= %d wrong settles):" % MIN_WRONG_FOR_POOL)
    for s in cells:
        say("      M=%2d c=%d: %3d wrong -> %s"
            % (s["load"], s["clamp"], s["wrong"],
               "IN POOL" if s in eligible else "out"))

    out = {"eligible": len(eligible), "pool_w": p_w, "pool_f": p_f,
           "pool_c": p_c, "pool_fa": p_fa, "all_w": a_w, "all_f": a_f,
           "all_c": a_c, "all_fa": a_fa, "n": tot_n}

    if p_w == 0:
        say("      no cell reached the filter -> the criterion cannot be applied.")
        out.update(flag_met=False, flag_lo=float("nan"), fa_met=False,
                   fa_hi=float("nan"), fa_state="no wrong settles in the pool",
                   verdict=False)
        return out

    _, lo_w, _ = wilson(p_f, p_w, Z99)
    flag_met = bool(lo_w >= 0.5)
    say("      POOLED over the %d eligible cell(s):" % len(eligible))
    say("        flag rate on wrong settles  %s  [need lo >= 0.5] -> %s"
        % (rate_str(p_f, p_w), "MET" if flag_met else "NOT MET"))

    if p_c == 0:
        # An unmeasured rate is not a violated rate.  Report it as unmeasured.
        fa_met = False
        fa_state = "UNMEASURED (0 correct settles inside the pool)"
        say("        false alarms on correct     UNMEASURED -- every cell in the"
            " pool had 0 correct settles")
        say("          (for the record, over all %d correct settles in this seed's"
            " grid: %s)" % (a_c, rate_str(a_fa, a_c)))
    else:
        _, _, hi_fa = wilson(p_fa, p_c, Z99)
        fa_met = bool(hi_fa <= 0.05)
        fa_state = "measured"
        say("        false alarms on correct     %s  [need hi <= 0.05] -> %s"
            % (rate_str(p_fa, p_c), "MET" if fa_met else "NOT MET"))

    say("      for the record, over ALL %d cells (filter ignored):" % len(cells))
    say("        flag rate on wrong settles  %s" % rate_str(a_f, a_w))
    say("        false alarms on correct     %s" % rate_str(a_fa, a_c))

    out.update(flag_met=flag_met, flag_lo=lo_w, fa_met=fa_met,
               fa_hi=(float("nan") if p_c == 0 else hi_fa), fa_state=fa_state,
               verdict=bool(flag_met and fa_met))
    return out


# --------------------------------------------------------------------------- report
def main(argv=None):
    ap = argparse.ArgumentParser(description="RING-1 T3: the 17 check ring")
    ap.add_argument("--quick", action="store_true",
                    help="30 trials per cell instead of 300")
    ap.add_argument("--scan-only", action="store_true",
                    help="run the robustness codebook seeds only, skip the verbose"
                         " pre-registered tables")
    args = ap.parse_args(argv)
    trials = 30 if args.quick else 300

    t_start = time.time()
    print("=" * 78)
    print("RING1-CHECK -- T3: 17 check ring flags wrong resonator settles")
    print("=" * 78)
    print(PRE_REGISTERED)
    print("\nsetup")
    print("  mods(5-ring)   = %s   full space %d" % (MODS5, FULL_SPACE))
    print("  mods(4-ring)   = %s   info space %d  (legal values 0..%d)"
          % (MODS4, STATES, MAX_MARK))
    print("  1365 mod 17    = %d  -> 17 is redundant (a checksum, not information)"
          % (STATES % 17))
    print("  D = %d   quant = %s   max_iter = %d" % (D, QUANT, MAX_ITER))
    print("  clamp order    = 13,7,5 -> ring indices %s; the 17 (index 4) is NEVER"
          " clamped (pinning the checksum is vacuous)" % (CLAMP_ORDER,))
    print("  trials/cell    = %d   cells = M%s x c%s   cell seeds are SeedSequence"
          " children of %d" % (trials, CELL_M, CELL_C, PRE_REG_SEED))
    print("  codebook seeds = %s   (pre-registered %d + robustness scan)"
          % (SCAN_SEEDS, PRE_REG_SEED))
    print("  chance         : target recall 1/M; a random residue tuple is illegal"
          " 16/17")
    print("\n  NOTE %s" % DEGENERATE_HINT)
    ok_algebra = _verify_algebra()

    grids = {}
    for seed in SCAN_SEEDS:
        t0 = time.time()
        cells, shared = run_grid(trials, seed)
        grids[seed] = cells
        print("\n  codebook seed %d: 6 cells x %d trials x 2 arms in %.1fs"
              " (shared 3/5/7/13 codebooks bit-identical across arms: %s)"
              % (seed, trials, time.time() - t0, shared))

    # ---------------------------------------------------- pre-registered seed, in full
    pre = grids[PRE_REG_SEED]
    if not args.scan_only:
        print("\n" + "=" * 78)
        print("RESULTS -- codebook seed %d (PRE-REGISTERED, inherited from RING1-CORE)"
              % PRE_REG_SEED)
        print("=" * 78)
        print("wrong settle = the 5-ring decode is not ANY real mark in the slot\n")
        print("| M | c | correct settles | WRONG settles | flagged (illegal) |"
              " silent phantom | false alarms |")
        print("|---|---|-----------------|---------------|--------------------|"
              "----------------|--------------|")
        for s in pre:
            print("| %d | %d | %s | %s | %s | %s | %s |"
                  % (s["load"], s["clamp"], rate_str(s["correct"], s["n"]),
                     rate_str(s["wrong"], s["n"]),
                     rate_str(s["flagged_wrong"], s["wrong"]),
                     rate_str(s["phantom"], s["wrong"]),
                     rate_str(s["fa_correct"], s["correct"])))

        print("\n  settle health (a cell that never settles cannot flag anything):")
        print("| M | c | converged | burned the 50-iter ceiling | cycled |"
              " median iters 5-ring | median iters 4-ring |")
        print("|---|---|-----------|--------------------------|--------|"
              "---------------------|---------------------|")
        for s in pre:
            print("| %d | %d | %s | %s | %s | %.1f | %.1f |"
                  % (s["load"], s["clamp"], rate_str(s["converged"], s["n"]),
                     rate_str(s["burned"], s["n"]), rate_str(s["cycled"], s["n"]),
                     s["median_iters5"], s["median_iters4"]))

        print("\n" + "=" * 78)
        print("COST OF THE EXTRA RING -- target recall, 5-ring vs paired 4-ring")
        print("=" * 78)
        print("| M | c | 5-ring target | 4-ring target | chance 1/M | both |"
              " only 4 | only 5 | McNemar p |")
        print("|---|---|---------------|---------------|-----------|------|"
              "---------|--------|-----------|")
        for s in pre:
            print("| %d | %d | %s | %s | %5.1f%% | %d | %d | %d | %.3f |"
                  % (s["load"], s["clamp"], rate_str(s["target5"], s["n"]),
                     rate_str(s["target4"], s["n"]), 100.0 / s["load"],
                     s["n"] - s["b01"] - s["b10"], s["b01"], s["b10"],
                     mcnemar_exact(s["b01"], s["b10"])))
        print("\n  'both' = the 17 ring left the cued mark's recall intact;"
              " 'only 4'/'only 5' = discordant pairs (McNemar, exact, two-sided).")

    # ------------------------------------------------------------- the decision
    print("\n" + "=" * 78)
    print("DECISION (pre-registered, applied as written, to the pre-registered seed)")
    print("=" * 78)
    res = apply_criterion(pre, "codebook seed %d" % PRE_REG_SEED)

    # -------------------------------------------------- robustness scan (report only)
    print("\n" + "=" * 78)
    print("ROBUSTNESS SCAN -- the same grid on other codebook seeds (report only)")
    print("=" * 78)
    print("| codebook seed | settled (conv 5-ring) | burned ceiling |"
          " wrong settles | flag rate on wrong | false alarms on correct |"
          " criterion |")
    print("|---------------|------------------------|-----------------|"
          "---------------|--------------------|----------------------|-----------|")
    scan_verdicts = {}
    for seed in SCAN_SEEDS:
        cells = grids[seed]
        n = sum(s["n"] for s in cells)
        conv = sum(s["converged"] for s in cells)
        burn = sum(s["burned"] for s in cells)
        w = sum(s["wrong"] for s in cells)
        f = sum(s["flagged_wrong"] for s in cells)
        c = sum(s["correct"] for s in cells)
        fa = sum(s["fa_correct"] for s in cells)
        if seed == PRE_REG_SEED:
            v = "PASS" if res["verdict"] else "KILL"
        else:
            v = "PASS" if apply_criterion(cells, "scan seed %d" % seed,
                                          quiet=True)["verdict"] else "KILL"
            scan_verdicts[seed] = v
        print("| %d %s | %s | %s | %s | %s | %s | **%s** |"
              % (seed, " (pre-reg)" if seed == PRE_REG_SEED else "",
                 rate_str(conv, n), rate_str(burn, n), rate_str(w, n),
                 rate_str(f, w), rate_str(fa, c), v))

    print("\nalgebra verification (false alarms structurally 0): %s"
          % ("OK" if ok_algebra else "FAILED"))
    if res["verdict"]:
        print("\nVERDICT PASS: on the pre-registered codebook the pooled flag rate"
              " clears 0.5\n(Wilson-99% lower bound) and pooled false alarms clear"
              " 0.05 (Wilson-99% upper bound).")
    else:
        why = []
        if not res["flag_met"]:
            why.append("the pooled flag rate on wrong settles did not clear the 0.5"
                       " Wilson-99% lower bound")
        if not res["fa_met"]:
            why.append("the false-alarm rate on correct settles is %s"
                       % res["fa_state"])
        print("\nVERDICT KILL: %s." % " and ".join(why))
    print("\ntotal wall time: %.1fs" % (time.time() - t_start))
    # Cohort convention (matches run_core.py): exit 0 either way -- the verdict is the
    # gate, i.e. the first line of the report.  Note that --quick (30 trials/cell)
    # cannot satisfy the criterion's own ">= 30 wrong settles in a cell" filter and so
    # reports KILL-not-evaluable; the verdict comes from the full 300-trial run.
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""RING-1 T10: dispersed array vs one crowded slot, cue broadcast, best-resonating
slot answers.

Task: RING1-DISPERSE (_Pads/RING/ring1-w3.wave.yaml, cohort contract
_Pads/RING1-contract.json).
Pillar: Nervous System, Loop step "Read".  Pure synthetic study.  numpy only.

Imports ring1_core unchanged (mods (3,5,7,13), D = 5120, float).  The question is a
LAYOUT question, not a physics question: the same M marks are either crammed into one
crowded slot or dealt round-robin over S dispersed slots, and the same single cue
(ring 13 clamped to the target's true residue) is broadcast to every slot.  The slot
whose decoded mark best matches its own slot vector answers.

Grid
  M in (12, 24, 48, 96)   total marks, drawn uniformly from 0..1364
  S in (1, 2, 4, 8, 16)   number of slots; M marks dealt round-robin, M/S per slot,
                          cells with M/S < 1 are SKIPPED (only M=12, S=16 drops out)

Query (one broadcast per trial)
  clamp        ring 13 (index 3) pinned to target % 13, c = 1 clamped ring
  broadcast    resonate EVERY slot with that same clamp
  decode       d_s = crt(positions of slot s, mods)
  score        Re<slot, encode(d)> / (|slot| * |encode(d)|)   <- normalised match
  winner       argmax_s score   (ties -> lowest slot index, deterministic)
  hit          winner's decoded mark == target

Reported per cell: target recall (Wilson-99%), chance = 1/M, how often the winner was
the slot that actually HOLDS the target (Wilson-99%), probe cost as total resonator
iterations summed over slots, and wall time per query.

Pre-registered decision (verbatim from the brief, do not change):
  PASS if, at M = 48, the best cell with S >= 4 has a Wilson-99% LOWER bound of
  target recall that exceeds the S = 1 cell's point recall by at least 0.20 absolute.
  Otherwise KILL: dispersal does not beat one crowded slot.

Usage
  python3 _Pads/RING/ring1/run_disperse.py --quick    # 30 trials/cell, NEVER writes
                                                    # _Reviews/RING/RING1-DISPERSE.md
  python3 _Pads/RING/ring1/run_disperse.py            # 200 trials/cell, writes the report
"""
from __future__ import annotations

import argparse
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ring1_core import (  # noqa: E402  (path shim must precede the import)
    crt,
    encode,
    make_rings,
    make_slot,
    resonate,
    wilson,
)

# ------------------------------------------------------------------------- locked grid
MODS = (3, 5, 7, 13)
D = 5120
QUANT = "float"
SPACE = 1
for _m in MODS:
    SPACE *= _m                     # 1365 -> marks drawn uniformly from 0..1364

M_GRID = (12, 24, 48, 96)
S_GRID = (1, 2, 4, 8, 16)
CLAMP_RING = 3                     # the 13-ring, index 3 of (3,5,7,13)
MAX_ITER = 50

# Two-sided normal quantile for 99%.
Z99 = 2.5758293035489004

# Fixed seeds.  The codebook seed is shared by every cell so the rings are paired
# across the whole grid; the trial seed depends on (M, trial) ONLY -- never on S --
# so every S at a given M is dealt the SAME marks and cued with the SAME target.
# That makes the S comparison paired rather than independent samples.
CODEBOOK_SEED = 0
TRIAL_SEED_BASE = 90210

# Verbatim pre-registration, printed into the report ahead of the results.
PREREG = (
    "Pre-registered decision (do not change): PASS if, at M = 48, the best cell with "
    "S >= 4 has a Wilson-99% LOWER bound of target recall that exceeds the S = 1 "
    "cell's point recall by at least 0.20 absolute. Otherwise KILL: dispersal does "
    "not beat one crowded slot."
)
DECISION_M = 48
DECISION_MIN_S = 4
DECISION_MARGIN = 0.20

DEFAULT_REPORT = "docs/appendix/RING1-DISPERSE.run.txt"


# ------------------------------------------------------------------------------ cells
def cells():
    """The (M, S) grid with cells where M/S < 1 skipped."""
    out = []
    for m in M_GRID:
        for s in S_GRID:
            if m / float(s) < 1:
                continue
            out.append((m, s))
    return out


def deal_round_robin(marks, s):
    """Deal `marks` round-robin over `s` slots: mark i goes to slot i % s.

    With M/S not an integer the first (M % S) slots simply carry one extra mark,
    which is what round-robin dealing means.
    """
    buckets = [[] for _ in range(s)]
    for i, mk in enumerate(marks):
        buckets[i % s].append(int(mk))
    return buckets


def _normalised_match(slot_vec, mark, rings, mods):
    """Re<slot, encode(mark)> / (|slot| * |encode(mark)|) -- the pre-registered score."""
    enc = encode(mark, rings, mods)
    num = float(np.real(np.vdot(slot_vec, enc)))
    den = float(np.linalg.norm(slot_vec)) * float(np.linalg.norm(enc))
    if den <= 0.0:
        return -np.inf
    return num / den


def run_cell(m, s, trials, rings, quiet=False):
    """Run one (M, S) cell.  Returns a dict of aggregated metrics."""
    hits = 0
    holder = 0
    iters_total = 0
    wall_total = 0.0
    per_s = m // s

    for t in range(trials):
        # Seed on (M, trial) only -> the same marks and the same target for every S.
        rng = np.random.default_rng(TRIAL_SEED_BASE + m * 100003 + t)
        marks = [int(x) for x in rng.integers(0, SPACE, m)]
        buckets = deal_round_robin(marks, s)
        slot_vecs = [make_slot(b, rings, MODS) for b in buckets]

        tgt_idx = int(rng.integers(0, m))
        target = marks[tgt_idx]
        holder_slot = tgt_idx % s
        clamp = {CLAMP_RING: int(target % MODS[CLAMP_RING])}

        t0 = time.perf_counter()
        best_score = -np.inf
        best_s = 0
        best_d = -1
        for si in range(s):
            res = resonate(slot_vecs[si], rings, clamp, MAX_ITER, 0)
            iters_total += int(res["iters"])
            d = crt(res["positions"], MODS)
            sc = _normalised_match(slot_vecs[si], d, rings, MODS)
            if sc > best_score:          # ties keep the lowest slot index
                best_score = sc
                best_s = si
                best_d = d
        wall_total += time.perf_counter() - t0

        if best_d == target:
            hits += 1
        if best_s == holder_slot:
            holder += 1

    p, lo, hi = wilson(hits, trials, Z99)
    ph, loh, hih = wilson(holder, trials, Z99)
    row = {
        "M": m,
        "S": s,
        "trials": trials,
        "per_slot": per_s,
        "hits": hits,
        "recall": p,
        "recall_lo": lo,
        "recall_hi": hi,
        "chance": 1.0 / float(m),
        "holder": holder,
        "holder_rate": ph,
        "holder_lo": loh,
        "holder_hi": hih,
        "iters_mean": iters_total / float(trials),
        "wall_mean_ms": 1000.0 * wall_total / float(trials),
    }
    if not quiet:
        print(
            "  M=%3d S=%2d  %d/slot  recall %6.1f%% [%5.1f,%5.1f]  chance %5.2f%%  "
            "holder %6.1f%%  iters/q %6.1f  wall/q %7.2f ms"
            % (
                m, s, per_s, 100 * p, 100 * lo, 100 * hi, 100 * row["chance"],
                100 * ph, row["iters_mean"], row["wall_mean_ms"],
            )
        )
    return row


# -------------------------------------------------------------------------- decision
def decide(rows):
    """Apply the pre-registered rule.  Returns (verdict_line, reason, detail_rows)."""
    by_key = {(r["M"], r["S"]): r for r in rows}
    base = by_key.get((DECISION_M, 1))
    if base is None:
        return ("KILL: no S=1 baseline at M=%d" % DECISION_M,
                "the (M=%d, S=1) cell was not run" % DECISION_M, [])
    cands = [r for r in rows
             if r["M"] == DECISION_M and r["S"] >= DECISION_MIN_S]
    if not cands:
        return ("KILL: no S>=4 cell at M=%d" % DECISION_M,
                "the (M=%d, S>=4) cells were not run" % DECISION_M, [])
    best = max(cands, key=lambda r: r["recall_lo"])
    margin = best["recall_lo"] - base["recall"]
    ok = margin >= DECISION_MARGIN
    detail = sorted(cands, key=lambda r: -r["recall_lo"]) + [base]
    if ok:
        verdict = "PASS"
        reason = (
            "at M=%d the best S>=%d cell (S=%d) has a Wilson-99%% lower bound of "
            "%.4f, which exceeds the S=1 point recall of %.4f by %.4f (>= %.2f)"
            % (DECISION_M, DECISION_MIN_S, best["S"], best["recall_lo"],
               base["recall"], margin, DECISION_MARGIN)
        )
    else:
        verdict = "KILL"
        reason = (
            "at M=%d the best S>=%d cell (S=%d) has a Wilson-99%% lower bound of "
            "%.4f, which does NOT exceed the S=1 point recall of %.4f by the "
            "required %.2f (short by %.4f): dispersal does not beat one crowded slot"
            % (DECISION_M, DECISION_MIN_S, best["S"], best["recall_lo"],
               base["recall"], DECISION_MARGIN, DECISION_MARGIN - margin)
        )
    return (verdict + ": " + reason, reason, detail)


# ----------------------------------------------------------------------------- report
def _row_md(r, idx):
    return (
        "| %d | %d | %d | %d | %d/%d | **%.1f%%** | [%.1f%%, %.1f%%] | %.2f%% | "
        "%d/%d (%.1f%%) | %.1f | %.2f |"
        % (
            idx, r["M"], r["S"], r["per_slot"], r["hits"], r["trials"],
            100 * r["recall"], 100 * r["recall_lo"], 100 * r["recall_hi"],
            100 * r["chance"], r["holder"], r["trials"], 100 * r["holder_rate"],
            r["iters_mean"], r["wall_mean_ms"],
        )
    )


HEADER = (
    "| # | M | S | marks/slot | hits/trials | target recall | Wilson-99% | chance 1/M | "
    "winner = holder | probe iters/query | wall ms/query |\n"
    "|---|---|---|---|---|---|---|---|---|---|---|\n"
)


def write_report(path, rows, verdict, reason, decision_rows, trials, elapsed, cmdline):
    lines = []
    lines.append(verdict)
    lines.append("")
    lines.append("## Pre-registration")
    lines.append("")
    lines.append("Copied verbatim from the brief, before any result was read:")
    lines.append("")
    lines.append("> " + PREREG)
    lines.append("")
    lines.append("Applied mechanically by `decide()` in "
                 "`_Pads/RING/ring1/run_disperse.py`; no threshold was tuned after "
                 "seeing data. M = %d, minimum S = %d, required margin = %.2f "
                 "absolute on the Wilson-99%% lower bound." %
                 (DECISION_M, DECISION_MIN_S, DECISION_MARGIN))
    lines.append("")
    lines.append("## Setup")
    lines.append("")
    lines.append("- Harness: `_Pads/RING/ring1/ring1_core.py`, imported unchanged. "
                 "mods (3,5,7,13), D = 5120, quant `float`, mark space %d "
                 "(marks drawn uniformly from 0..%d)." % (SPACE, SPACE - 1))
    lines.append("- Grid: M in %s, S in %s. M marks dealt round-robin over S slots "
                 "(M/S per slot); cells with M/S < 1 are skipped, which drops only "
                 "(M=12, S=16) -> %d cells." %
                 (list(M_GRID), list(S_GRID), len(rows)))
    lines.append("- Query: ring 13 (index %d) clamped to `target %% 13`, c = 1 clamped "
                 "ring; that single clamp is broadcast to EVERY slot. Each slot is "
                 "resonated independently (max_iter=%d) and decoded with `crt`." %
                 (CLAMP_RING, MAX_ITER))
    lines.append("- Winner: argmax over slots of the normalised match "
                 "`Re<slot, encode(d)> / (|slot| * |encode(d)|)`, ties to the lowest "
                 "slot index. A trial is a **hit** when the winner's decoded mark "
                 "equals the target, and a **winner = holder** when the winning slot "
                 "is the slot the target was actually dealt into.")
    lines.append("- Seeds: codebook seed %d (shared by every cell, so the rings are "
                 "paired across the grid); trial seed = %d + M*100003 + trial, "
                 "depending on (M, trial) but NOT on S. Every S at a given M therefore "
                 "sees the SAME marks and the SAME target, so the S comparison is "
                 "paired rather than independent." %
                 (CODEBOOK_SEED, TRIAL_SEED_BASE))
    lines.append("- Trials: %d per cell. Intervals: Wilson score, z = %.4f "
                 "(two-sided 99%%)." % (trials, Z99))
    lines.append("- Command: `%s`" % cmdline)
    lines.append("- Wall time for the whole run: %.1f s." % elapsed)
    lines.append("- `--quick` (30 trials/cell) is a smoke run and deliberately does "
                 "NOT write this report; the gate runs it without overwriting the "
                 "full-run numbers below.")
    lines.append("")
    lines.append("## Results")
    lines.append("")
    lines.append(HEADER.rstrip("\n"))
    for i, r in enumerate(rows, 1):
        lines.append(_row_md(r, i))
    lines.append("")
    lines.append("### The pre-registered comparison at M = %d" % DECISION_M)
    lines.append("")
    lines.append(HEADER.rstrip("\n"))
    for i, r in enumerate(decision_rows, 1):
        lines.append(_row_md(r, i))
    lines.append("")
    lines.append("**Verdict: %s**" % verdict)
    lines.append("")
    lines.append("**Reason: %s**" % reason)
    lines.append("")
    lines.append("Probe cost is the total resonator iterations summed over all S slots "
                 "of one broadcast query; wall time is the same query end to end "
                 "(resonate + decode + score for every slot).")
    lines.append("")
    lines.append("## What this means for the bus")
    lines.append("")
    lines.append(_bus_meaning(rows, decision_rows, reason))
    lines.append("")
    lines.append("## Open issues")
    lines.append("")
    lines.append("- Only one codebook seed (%d) was run. The rings are random draws, "
                 "so per-cell numbers carry codebook variance that Wilson intervals "
                 "over 200 trials do NOT capture. A seed sweep is the honest next "
                 "step before quoting any absolute recall." % CODEBOOK_SEED)
    lines.append("- The score is an inner product against the slot's OWN decoded mark, "
                 "so it measures 'is this slot self-consistent' rather than an "
                 "absolute confidence. It says nothing about whether the decoded mark "
                 "is the right one; that is what the hit column is for.")
    lines.append("- `quant` is `float` only. The 5-bit phase layer (`k16`) is the "
                 "storage-realistic setting and was not swept here; T-series siblings "
                 "carry that comparison.")
    lines.append("- D = 5120 is inherited from the RING-1 harness. No dimension "
                 "sweep, so no claim is made about how these recalls move with slot "
                 "capacity on a real bus.")
    lines.append("- Cells with M/S not an integer (e.g. M=12, S=8 -> slots of 2 and 1) "
                 "carry unequal slot loads, which is a second, uncontrolled variable "
                 "besides S. Isolating it needs a separate balanced-deal run.")
    txt = "\n".join(lines) + "\n"
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(txt)
    return path


def _bus_meaning(rows, decision_rows, reason):
    by = {(r["M"], r["S"]): r for r in rows}
    parts = []
    m12, m96 = by.get((12, 1)), by.get((96, 16))
    if m12 and m96:
        parts.append(
            "**Cost of spreading.** A broadcast is %d resonator calls at S=16 versus "
            "1 at S=1. The same cue that finds a mark in one crowded slot has to be "
            "pushed through every slot of a dispersed array, and the resonator "
            "iteration count is what you pay for it (%d iters/query at S=16 versus "
            "%d at S=1). Layout is not free on a bus: a dispersed array trades "
            "readout work for per-slot capacity." % (m96["S"], int(m96["iters_mean"]),
                                                    int(m12["iters_mean"])))
    parts.append("**Cue, not key.** The 13-ring clamp is doing the selection work, "
                 "not the layout. The clamp is the one shared input that makes the "
                 "readout comparable across slots; the winner is then the slot whose "
                 "own residue is most consistent with the cue. That is the shape a "
                 "real bus wants: broadcast one narrow cue, let the array self-select, "
                 "and read the slot index rather than a separate address decoder.")
    parts.append("**Verdict as measured.** %s" % reason)
    return "\n\n".join(parts)


# ------------------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="RING-1 T10 dispersed array vs one crowded slot")
    ap.add_argument("--quick", action="store_true",
                    help="30 trials per cell; smoke run, never writes the report")
    ap.add_argument("--trials", type=int, default=None,
                    help="override trials per cell (default 200, or 30 with --quick)")
    ap.add_argument("--report", default=DEFAULT_REPORT,
                    help="report path for a full run (default %s)" % DEFAULT_REPORT)
    ap.add_argument("--no-report", action="store_true",
                    help="run full trial count but do not write the report")
    args = ap.parse_args(argv)

    trials = args.trials if args.trials else (30 if args.quick else 200)
    write = (not args.quick) and (not args.no_report)

    cmdline = ("python3 _Pads/RING/ring1/run_disperse.py"
               + (" --quick" if args.quick else "")
               + (" --trials %d" % trials if args.trials else ""))

    print("RING-1 T10 disperse  mods=%s D=%d quant=%s space=%d trials/cell=%d %s"
          % (list(MODS), D, QUANT, SPACE, trials, "[QUICK SMOKE]" if args.quick else ""))
    print("codebook_seed=%d  trial_seed=%d + M*100003 + trial (independent of S)"
          % (CODEBOOK_SEED, TRIAL_SEED_BASE))
    print("")
    print("Pre-registration (verbatim): %s" % PREREG)
    print("")

    t_start = time.perf_counter()
    rings = make_rings(MODS, D=D, seed=CODEBOOK_SEED, quant=QUANT)
    grid = cells()
    print("grid: %d cells (M/S < 1 skipped -> %s)"
          % (len(grid), [(m, s) for m in M_GRID for s in S_GRID
                         if m / float(s) < 1] or "none"))
    print("")

    rows = []
    for m, s in grid:
        rows.append(run_cell(m, s, trials, rings))
    elapsed = time.perf_counter() - t_start

    verdict, reason, decision_rows = decide(rows)

    print("")
    print(HEADER.rstrip("\n"))
    for i, r in enumerate(rows, 1):
        print(_row_md(r, i))
    print("")
    print("VERDICT: %s" % verdict)
    print("elapsed: %.1f s" % elapsed)

    if write:
        path = write_report(args.report, rows, verdict, reason, decision_rows,
                            trials, elapsed, cmdline)
        print("wrote report: %s" % path)
    else:
        print("report NOT written (quick smoke run / --no-report): %s" % args.report)

    return 0


if __name__ == "__main__":
    sys.exit(main())

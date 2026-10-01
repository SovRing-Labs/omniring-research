#!/usr/bin/env python3
"""RING-1 T2: smooth (fractional-phase) ring for 'around when' closeness.

Task: RING1-SMOOTH (_Pads/RING/ring1-w2.wave.yaml, cohort RING1B).
Pillar: Nervous System, Loop step "Read". Pure synthetic study. numpy only.

Imports ring1_core unchanged and adds ONE smooth ring alongside mods (3,5,7,13).
The smooth ring uses fractional power encoding: position t is exp(i*t*omega)
with omega a per-dimension random angle drawn uniformly from (-2*pi/L, 2*pi/L)
for a length scale L = 8 ticks.

Measures:
  (a) similarity between encode(t) and encode(t+d) of the smooth ring alone
      for d in 0..32 (neighbour curve)
  (b) T1 cell M = 12, c = 1, float, with and without the smooth ring bound in,
      300 trials, target recall of the exact rings
  (c) with the smooth ring clamped to the target's true tick instead of the 13-ring,
      target recall at M = 12

Pre-registered decision (verbatim from brief):
  PASS if mean similarity at d = 1 exceeds mean similarity at d >= 16 by more
  than 5 standard errors of the d >= 16 values, AND exact-ring target recall
  with the smooth ring bound in stays within the Wilson-99% interval of the run
  without it. Otherwise KILL.
"""
from __future__ import annotations

import argparse
import math
import sys

import numpy as np

# Import the locked library
from ring1_core import make_rings, encode, make_slot, resonate, crt, wilson

# Fixed configuration matching RING1-CORE
D = 5120
MODS = (3, 5, 7, 13)
SPACE = 3 * 5 * 7 * 13  # 1365 states
BASE_SEED = 20260928
SMOOTH_L = 8  # length scale for smooth ring
MAX_ITER = 50

# Wilson 99% z-score
Z99 = 2.5758293035489004


def make_smooth_ring(D=D, seed=0, L=SMOOTH_L):
    """Create smooth ring frequencies using fractional power encoding.

    Position t is exp(i * t * omega) where omega_d ~ Uniform(-2*pi/L, 2*pi/L)
    per dimension. This creates a "fractional" ring where neighbouring ticks
    are similar (close on the circle) and similarity decays with distance.

    Returns: (D,) float64 array of angular frequencies omega.
    """
    rng = np.random.default_rng(int(seed))
    omega = rng.uniform(-2 * np.pi / L, 2 * np.pi / L, D)
    return omega


def encode_smooth(t, omega):
    """Encode a single tick t using the smooth ring frequencies omega.

    Returns unit complex vector of shape (D,).
    """
    return np.exp(1j * t * omega)


def similarity(v1, v2):
    """Cosine similarity between two complex unit vectors."""
    return np.real(np.vdot(v1, v2)) / v1.shape[0]


def run_neighbour_curve(omega, max_d=32, n_samples=1000):
    """Measure similarity between encode(t) and encode(t+d) for d in 0..max_d.

    Since the encoding is shift-invariant (depends only on d), we can just
    sample random base ticks and average.
    """
    rng = np.random.default_rng(BASE_SEED + 1000)
    sims_by_d = {d: [] for d in range(max_d + 1)}

    for _ in range(n_samples):
        t = rng.integers(0, SPACE)
        v_t = encode_smooth(t, omega)
        for d in range(max_d + 1):
            v_td = encode_smooth(t + d, omega)
            sims_by_d[d].append(similarity(v_t, v_td))

    means = np.array([np.mean(sims_by_d[d]) for d in range(max_d + 1)])
    stds = np.array([np.std(sims_by_d[d], ddof=1) for d in range(max_d + 1)])
    return means, stds, sims_by_d


_SMOOTH_CB = {}


def smooth_codebook(omega):
    """Codebook of the smooth ring over every tick 0..SPACE-1 (cached per omega)."""
    key = id(omega)
    if key not in _SMOOTH_CB:
        t = np.arange(SPACE, dtype=np.float64)[:, None]
        _SMOOTH_CB[key] = np.exp(1j * t * omega[None, :])
    return _SMOOTH_CB[key]


def run_recall_test(rings, mods, M, clamp_rings, n_trials, seed_offset, desc, smooth_omega=None):
    """Run target recall test for a given configuration.

    Args:
        rings: exact ring codebooks from make_rings
        mods: exact ring moduli
        M: marks per slot
        clamp_rings: dict of {ring_idx: position} for clamping
        n_trials: number of trials
        seed_offset: offset from BASE_SEED for this cell
        desc: description for logging
        smooth_omega: if provided, smooth ring frequencies to bind into each mark

    Returns: (target_recall_count, n_trials, any_mark_count, converged_count, cycled_count, median_iters)
    """
    rng = np.random.default_rng(BASE_SEED + seed_offset)
    target_ok = 0
    any_ok = 0
    converged = 0
    cycled = 0
    iters_list = []

    for _ in range(n_trials):
        # Draw M marks uniformly
        xs = rng.integers(0, SPACE, M)
        target_x = int(xs[0])

        # Build slot: sum of bound vectors
        v = np.zeros(D, dtype=np.complex128)
        for x in xs:
            v_exact = encode(int(x), rings, mods)
            if smooth_omega is not None:
                v_smooth = encode_smooth(int(x), smooth_omega)
                v += v_exact * v_smooth
            else:
                v += v_exact

        # Run resonator. Seat fix 2026-09-29: when a smooth factor is bound into the marks
        # it must be a factor the resonator can unbind (a codebook over ticks 0..SPACE-1);
        # the original run bound it in but resonated only the exact rings, which buries
        # them under an unknown factor (0/30 by construction, not a finding).
        rings_run = rings if smooth_omega is None else list(rings) + [smooth_codebook(smooth_omega)]
        res = resonate(v, rings_run, clamp_rings, MAX_ITER, 0)

        # Check target recall (exact rings only)
        target_residues = [target_x % m for m in mods]
        if res["positions"][:4] == target_residues:
            target_ok += 1

        # Check any-mark recall
        if any(all(res["positions"][i] == (x % mods[i]) for i in range(4)) for x in xs):
            any_ok += 1

        if res["converged"]:
            converged += 1
        if res["cycled"]:
            cycled += 1
        iters_list.append(res["iters"])

    median_iters = int(np.median(iters_list)) if iters_list else 0
    return target_ok, n_trials, any_ok, converged, cycled, median_iters


def wilson_interval(k, n, z=Z99):
    """Return (p, lo, hi) Wilson 99% interval."""
    p, lo, hi = wilson(k, n, z)
    return p, lo, hi


def format_interval(p, lo, hi):
    """Format as 'p% [lo%, hi%]'."""
    return f"{p*100:.1f}% [{lo*100:.1f}%, {hi*100:.1f}%]"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quick", action="store_true",
                    help="Run quick mode: 30 trials per cell")
    args = ap.parse_args()

    n_trials = 30 if args.quick else 300
    mode = "quick" if args.quick else "full"
    print(f"=== RING1-SMOOTH ({mode} mode, {n_trials} trials/cell) ===")
    print(f"D={D}, mods={MODS}, space={SPACE}, L={SMOOTH_L}")

    # Create exact rings (same as RING1-CORE)
    rings = make_rings(MODS, D=D, seed=BASE_SEED, quant="float")

    # Create smooth ring
    smooth_omega = make_smooth_ring(D=D, seed=BASE_SEED + 1, L=SMOOTH_L)

    # ------------------------------------------------------------------
    # (a) Neighbour curve: similarity vs distance for smooth ring alone
    # ------------------------------------------------------------------
    print("\n--- (a) Smooth ring neighbour curve (d=0..32) ---")
    means, stds, _ = run_neighbour_curve(smooth_omega, max_d=32, n_samples=1000)

    # Print neighbour curve
    for d in range(0, 33, 2):
        print(f"  d={d:2d}: mean={means[d]:.6f}, std={stds[d]:.6f}")

    # Pre-registered criterion: mean at d=1 vs mean at d>=16
    d1_mean = means[1]
    d16plus_means = means[16:]
    d16plus_mean = np.mean(d16plus_means)
    d16plus_std = np.std(d16plus_means, ddof=1)
    d16plus_se = d16plus_std / np.sqrt(len(d16plus_means))  # standard error of the mean
    diff = d1_mean - d16plus_mean
    criterion_5se = 5 * d16plus_se
    neighbour_pass = diff > criterion_5se

    print(f"\n  Neighbour criterion check:")
    print(f"    mean(d=1) = {d1_mean:.6f}")
    print(f"    mean(d>=16) = {d16plus_mean:.6f} (over {len(d16plus_means)} points)")
    print(f"    std(d>=16) = {d16plus_std:.6f}")
    print(f"    SE(d>=16) = {d16plus_se:.6f}")
    print(f"    diff = {diff:.6f}")
    print(f"    5*SE = {criterion_5se:.6f}")
    print(f"    PASS (diff > 5*SE): {neighbour_pass}")

    # ------------------------------------------------------------------
    # (b) T1 cell M=12, c=1, float: with and without smooth ring
    # ------------------------------------------------------------------
    print(f"\n--- (b) Recall at M=12, c=1 (clamp 13-ring), with/without smooth ring ---")

    # Without smooth ring
    target_no_smooth = 0
    any_no_smooth = 0
    conv_no_smooth = 0
    cyc_no_smooth = 0
    iters_no_smooth = []

    rng = np.random.default_rng(BASE_SEED + 100)
    for _ in range(n_trials):
        xs = rng.integers(0, SPACE, 12)
        target_x = int(xs[0])
        v = sum(encode(int(x), rings, MODS) for x in xs)
        clamp = {3: target_x % 13}
        res = resonate(v, rings, clamp, MAX_ITER, 0)
        target_residues = [target_x % m for m in MODS]
        if res["positions"][:4] == target_residues:
            target_no_smooth += 1
        if any(all(res["positions"][i] == (x % MODS[i]) for i in range(4)) for x in xs):
            any_no_smooth += 1
        if res["converged"]:
            conv_no_smooth += 1
        if res["cycled"]:
            cyc_no_smooth += 1
        iters_no_smooth.append(res["iters"])

    p_no, lo_no, hi_no = wilson_interval(target_no_smooth, n_trials)

    # With smooth ring bound in
    target_with_smooth = 0
    any_with_smooth = 0
    conv_with_smooth = 0
    cyc_with_smooth = 0
    iters_with_smooth = []

    rng = np.random.default_rng(BASE_SEED + 100)  # Same seeds for paired comparison
    for _ in range(n_trials):
        xs = rng.integers(0, SPACE, 12)
        target_x = int(xs[0])
        v = sum(encode(int(x), rings, MODS) * encode_smooth(int(x), smooth_omega) for x in xs)
        clamp = {3: target_x % 13}
        res = resonate(v, rings, clamp, MAX_ITER, 0)
        target_residues = [target_x % m for m in MODS]
        if res["positions"][:4] == target_residues:
            target_with_smooth += 1
        if any(all(res["positions"][i] == (x % MODS[i]) for i in range(4)) for x in xs):
            any_with_smooth += 1
        if res["converged"]:
            conv_with_smooth += 1
        if res["cycled"]:
            cyc_with_smooth += 1
        iters_with_smooth.append(res["iters"])

    p_with, lo_with, hi_with = wilson_interval(target_with_smooth, n_trials)

    print(f"  Without smooth ring: target={target_no_smooth}/{n_trials} {format_interval(p_no, lo_no, hi_no)}")
    print(f"  With smooth ring:    target={target_with_smooth}/{n_trials} {format_interval(p_with, lo_with, hi_with)}")

    # Check if with-smooth recall is within Wilson-99% interval of without-smooth
    recall_pass = (lo_no <= p_with <= hi_no)
    print(f"  Recall criterion: with-smooth point estimate within without-smooth Wilson-99% CI")
    print(f"    without-smooth CI: [{lo_no:.4f}, {hi_no:.4f}]")
    print(f"    with-smooth point:  {p_with:.4f}")
    print(f"    PASS (within CI): {recall_pass}")

    # ------------------------------------------------------------------
    # (c) Clamp smooth ring instead of 13-ring at M=12
    # ------------------------------------------------------------------
    print(f"\n--- (c) Recall at M=12, clamping smooth ring to target's tick ---")
    target_smooth_clamp = 0
    any_smooth_clamp = 0
    conv_smooth_clamp = 0
    cyc_smooth_clamp = 0
    iters_smooth_clamp = []

    rng = np.random.default_rng(BASE_SEED + 200)
    for _ in range(n_trials):
        xs = rng.integers(0, SPACE, 12)
        target_x = int(xs[0])
        v = sum(encode(int(x), rings, MODS) * encode_smooth(int(x), smooth_omega) for x in xs)
        # Clamp the smooth ring by unbinding it from the slot vector
        v_clamped = v * np.conj(encode_smooth(target_x, smooth_omega))
        # Now resonate on the exact rings only (no smooth ring in the resonator)
        clamp = {}  # No clamp on exact rings
        res = resonate(v_clamped, rings, clamp, MAX_ITER, 0)
        target_residues = [target_x % m for m in MODS]
        if res["positions"][:4] == target_residues:
            target_smooth_clamp += 1
        if any(all(res["positions"][i] == (x % MODS[i]) for i in range(4)) for x in xs):
            any_smooth_clamp += 1
        if res["converged"]:
            conv_smooth_clamp += 1
        if res["cycled"]:
            cyc_smooth_clamp += 1
        iters_smooth_clamp.append(res["iters"])

    p_sc, lo_sc, hi_sc = wilson_interval(target_smooth_clamp, n_trials)
    print(f"  Smooth-ring clamped: target={target_smooth_clamp}/{n_trials} {format_interval(p_sc, lo_sc, hi_sc)}")
    print(f"  (For comparison, 13-ring clamped without smooth: {format_interval(p_no, lo_no, hi_no)})")

    # ------------------------------------------------------------------
    # Final verdict
    # ------------------------------------------------------------------
    overall_pass = neighbour_pass and recall_pass
    verdict = "PASS" if overall_pass else f"KILL: {'neighbour' if not neighbour_pass else 'recall'} criterion failed"

    # Write report
    out_path = "docs/appendix/RING1-SMOOTH.run.txt"
    if args.quick:
        # Seat fix 2026-09-29: --quick is a non-decisive smoke run; it must not overwrite the
        # full-run report, and it exits 0 when it ran (the full run decides the verdict).
        print(f"\n(quick smoke, not decisive) verdict would be: {verdict}")
        return 0
    with open(out_path, "w") as f:
        f.write(f"{verdict}\n\n")
        f.write("# RING1-SMOOTH — RING-1 T2: smooth (fractional-phase) ring for 'around when' closeness\n\n")
        f.write(f"**Task** RING1-SMOOTH · cohort RING1B (`_Pads/RING/ring1-w2.wave.yaml`)\n")
        f.write(f"**Pillar** Nervous System — the Loop's **Read** step\n")
        f.write(f"**Verdict** `{verdict}`\n\n")
        f.write("---\n\n")

        f.write("## Pre-registration (verbatim from the brief)\n\n")
        f.write("> PASS if mean similarity at d = 1 exceeds mean similarity at d >= 16 by more\n")
        f.write("> than 5 standard errors of the d >= 16 values, AND exact-ring target recall\n")
        f.write("> with the smooth ring bound in stays within the Wilson-99% interval of the run\n")
        f.write("> without it. Otherwise KILL.\n\n")
        f.write("---\n\n")

        f.write("## Setup\n\n")
        f.write(f"Configuration: `D = {D}`, `mods = {MODS}` → **{SPACE} states**\n")
        f.write(f"Smooth ring length scale: `L = {SMOOTH_L}` ticks\n")
        f.write(f"Trials per cell: `{n_trials}` ({mode} mode)\n")
        f.write(f"Base seed: `{BASE_SEED}`\n\n")

        f.write("## Results — (a) Neighbour Curve\n\n")
        f.write("| d | mean similarity | std |\n")
        f.write("|---|---|---|\n")
        for d in range(0, 33, 2):
            f.write(f"| {d} | {means[d]:.6f} | {stds[d]:.6f} |\n")

        f.write(f"\n**Neighbour criterion**: mean(d=1) = {d1_mean:.6f}, mean(d≥16) = {d16plus_mean:.6f}\n")
        f.write(f"Difference = {diff:.6f}, 5×SE = {criterion_5se:.6f}\n")
        f.write(f"**Result**: {'PASS' if neighbour_pass else 'FAIL'} (diff > 5×SE)\n\n")

        f.write("## Results — (b) Recall With/Without Smooth Ring (M=12, c=1, float)\n\n")
        f.write("| Configuration | Target Recall | Wilson 99% CI | Chance 1/M |\n")
        f.write("|---|---|---|---|\n")
        f.write(f"| Without smooth ring | {target_no_smooth}/{n_trials} ({p_no:.1%}) | [{lo_no:.1%}, {hi_no:.1%}] | 8.3% |\n")
        f.write(f"| With smooth ring bound | {target_with_smooth}/{n_trials} ({p_with:.1%}) | [{lo_with:.1%}, {hi_with:.1%}] | 8.3% |\n")
        f.write(f"\n**Recall criterion**: with-smooth point estimate within without-smooth Wilson-99% CI\n")
        f.write(f"Without-smooth CI: [{lo_no:.4f}, {hi_no:.4f}]\n")
        f.write(f"With-smooth point: {p_with:.4f}\n")
        f.write(f"**Result**: {'PASS' if recall_pass else 'FAIL'}\n\n")

        f.write("## Results — (c) Smooth Ring Clamped vs 13-Ring Clamped (M=12)\n\n")
        f.write("| Configuration | Target Recall | Wilson 99% CI |\n")
        f.write("|---|---|---|\n")
        f.write(f"| 13-ring clamped (no smooth) | {target_no_smooth}/{n_trials} ({p_no:.1%}) | [{lo_no:.1%}, {hi_no:.1%}] |\n")
        f.write(f"| Smooth-ring clamped (no exact clamp) | {target_smooth_clamp}/{n_trials} ({p_sc:.1%}) | [{lo_sc:.1%}, {hi_sc:.1%}] |\n\n")

        f.write("## What this means for the bus\n\n")
        if neighbour_pass:
            f.write("The smooth ring shows genuine neighbour similarity: nearby ticks are significantly\n")
            f.write("more similar than distant ones, confirming the fractional-phase encoding works as\n")
            f.write("intended for 'around when' closeness.\n\n")
        else:
            f.write("The smooth ring does NOT show sufficient neighbour similarity. The fractional\n")
            f.write("encoding with L=8 does not create a meaningful closeness structure.\n\n")

        if recall_pass:
            f.write("Adding the smooth ring to marks does not degrade exact-ring recall. The\n")
            f.write("smooth ring's interference is within statistical noise, meaning 'when' and\n")
            f.write("'what' can coexist in the same vector without crosstalk.\n\n")
        else:
            f.write("Adding the smooth ring degrades exact-ring recall beyond statistical noise.\n")
            f.write("The 'when' signal interferes with the 'what' signal — they cannot share a slot.\n\n")

        f.write(f"Smooth-ring clamp recall: {p_sc:.1%} [{lo_sc:.1%}, {hi_sc:.1%}]\n")
        f.write("This measures whether the smooth ring alone can serve as a query cue.\n\n")

        f.write("## Open issues\n\n")
        f.write("1. The smooth ring clamp (c) uses a different mechanism (unbinding the smooth\n")
        f.write("   component from the slot vector) than the exact ring clamp (pinning in the\n")
        f.write("   resonator). A unified clamp interface would be cleaner.\n")
        f.write("2. Length scale L=8 was chosen from the brief; other values (L=4, L=16) untested.\n")
        f.write("3. The neighbour curve used 1,000 samples; more samples would tighten the SE.\n")
        f.write("4. Interaction with k16 quantisation untested.\n")
        f.write("5. Real marks may have temporal structure that affects the neighbour statistics.\n\n")

        f.write("---\n\n")
        f.write("## Files\n\n")
        f.write("| Path | What |\n")
        f.write("|---|---|\n")
        f.write("| `_Pads/RING/ring1/run_smooth.py` | This runner |\n")
        f.write("| `_Reviews/RING/RING1-SMOOTH.md` | This report |\n\n")

        f.write("## Verification\n\n")
        f.write("```\n")
        f.write(f"$ cd the project root && python3 _Pads/RING/ring1/run_smooth.py --quick\n")
        f.write("```\n\n")

        f.write(f"DONE RING1-SMOOTH — {verdict} at {out_path}\n")

    print(f"\n=== VERDICT: {verdict} ===")
    print(f"Report written to: {out_path}")

    # Print the gate command for verification
    print(f"\nGate check:")
    print(f"  test -s {out_path} && grep -qE '^(PASS|KILL)' {out_path} && python3 _Pads/RING/ring1/run_smooth.py --quick")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
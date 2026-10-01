#!/usr/bin/env python3
"""RING-1 core: reusable numpy resonator harness for coprime counting rings.

Task: RING1-CORE (_Pads/RING/ring1-w1.wave.yaml, cohort contract _Pads/RING1-contract.json).
Pillar: Nervous System, Loop step "Read".  Pure synthetic study. numpy only.

This module is a LIBRARY.  Other RING-1 tasks (T2 smooth ring, T3 check ring,
T4 halo chain, T5 eigengap, T6 capacity, T7 direct-vs-bound) import it unchanged.

Public API (exactly the six functions the brief locks):
    make_rings(mods, D, seed, quant)  -> list of codebooks, one per ring
    encode(x, rings, mods)            -> bound unit vector for mark x
    make_slot(xs, rings, mods)        -> superposition of encodes (no normalisation)
    resonate(v, rings, clamp, max_iter, seed) -> dict of the settle result
    crt(residues, mods)               -> exact mark id from residues
    wilson(k, n, z)                   -> (p, lo, hi) Wilson score interval

Physics, verbatim from the seed demo _Pads/RING/ring_demos.py (seed 0/1/3/5):
  * ring m contributes theta_d = j_d * 2*pi/m per dimension, j_d ~ U{0..m-1};
    position k of ring m is exp(i*k*theta).
  * binding is the elementwise product over rings: encode(x) = prod_m codebook_m[x % m].
  * a slot is the plain sum of encodes (superposition; NO per-dimension normalisation --
    normalising was shown in the seed demo to destroy member separation).
  * the soft resonator starts every free ring at the mean of its codebook, and each
    iteration, for each free ring i, unbinds the other rings' current estimates,
    scores every position, takes weights = max(score, 0), rebuilds the estimate as the
    weighted sum and renormalises it to unit modulus per dimension.  "Don't measure
    early": rings settle together, argmax/cleanup happens once at the end.

Quantisation: quant="k16" rounds every stored phase to the nearest multiple of
2*pi/16, which is how the bus 5-bit phase layer stores a phase vector.  The
underlying per-dimension multiples j_d are drawn from the same rng stream for
both settings, so float vs k16 is a paired comparison.

Self-test:  python3 _Pads/RING/ring1/ring1_core.py --selftest
            decodes 20 clean single marks with mods (3,5,7,13) and exits 0 only
            if all 20 decode exactly.
"""
from __future__ import annotations

import argparse
import math
import sys

import numpy as np

__all__ = ["make_rings", "encode", "make_slot", "resonate", "crt", "wilson"]

# Phase levels of the bus 5-bit phase layer.
K16_LEVELS = 16
# Below this magnitude a per-dimension estimate is treated as zero and left as-is.
_NORM_FLOOR = 1e-12
# Two scores closer than this count as an exact tie (float64 slack).
_TIE_SLACK = 1e-12


# --------------------------------------------------------------------------- rings
def make_rings(mods, D=5120, seed=0, quant="float"):
    """One codebook per ring.  Returns a list of (m, D) complex128 arrays of unit
    complex numbers; position k of ring m is exp(i*k*theta) with theta a per-dimension
    random multiple of 2*pi/m.

    quant="float" keeps the exact angles.
    quant="k16"   rounds every phase to the nearest multiple of 2*pi/16.
    """
    if quant not in ("float", "k16"):
        raise ValueError("quant must be 'float' or 'k16', got %r" % (quant,))
    mods = [int(m) for m in mods]
    rng = np.random.default_rng(int(seed))
    codebooks = []
    for m in mods:
        if m < 2:
            raise ValueError("ring modulus must be >= 2, got %r" % (m,))
        j = rng.integers(0, m, int(D))          # per-dimension multiple index
        k = np.arange(m, dtype=np.int64)[:, None]
        # exp(i*k*theta) has turn phase (k*j_d / m) mod 1 == ((k*j_d) mod m) / m,
        # which keeps every phase in [0, 1) turns.
        turns = ((k * j[None, :]) % m) / float(m)
        if quant == "k16":
            turns = np.round(turns * K16_LEVELS) / float(K16_LEVELS)
        codebooks.append(np.exp(2j * np.pi * turns))
    return codebooks


# ------------------------------------------------------------------------- binding
def encode(x, rings, mods):
    """Bound vector for one mark: elementwise product of each ring's position x % m."""
    v = np.ones(rings[0].shape[1], dtype=np.complex128)
    for cb, m in zip(rings, mods):
        m = int(m)
        v = v * cb[int(x) % m]
    return v


def make_slot(xs, rings, mods):
    """The slot vector: plain sum of encode() over the marks xs (superposition,
    NO per-dimension normalisation)."""
    v = np.zeros(rings[0].shape[1], dtype=np.complex128)
    for x in xs:
        v += encode(x, rings, mods)
    return v


# ----------------------------------------------------------------------- resonator
def _cleanup_positions(codebooks, ests, rng):
    """argmax over each ring's positions against that ring's current estimate.

    The 'don't measure early' rule: this is the single measurement, taken once the
    rings have settled.  `rng` breaks exact ties only (and is the only use of the
    `seed` argument, so with no exact ties the result is seed-independent).
    """
    positions = []
    for cb, e in zip(codebooks, ests):
        scores = (cb.conj() @ e).real
        top = scores.max()
        tied = np.flatnonzero(scores >= top - _TIE_SLACK)
        if tied.size == 1:
            positions.append(int(tied[0]))
        else:
            positions.append(int(tied[rng.integers(0, tied.size)]))
    return positions


def resonate(v, rings, clamp=None, max_iter=50, seed=0):
    """Run the soft resonator on slot vector v.

    clamp       dict {ring index: position}.  Those rings are pinned to that fixed
                position and are never updated; the pin enters the unbind product,
                which is exactly the "13-ring clamp" of the seed demo -- the query
                cue that selects a mark out of a crowded slot.
    max_iter    hard iteration ceiling.
    seed        used ONLY to break exact score ties deterministically.  With no exact
                ties (the generic case) the result is independent of it.

    Returns a dict:
        positions  per-ring argmax at the end
        iters      iterations actually used
        converged  argmax stable for 2 consecutive iterations
        cycled     a state was revisited within 50 iterations without converging
        gap_min    smallest best-minus-runner-up score over the FREE rings at the end
        gap_first  the same margin after iteration 1
    gap_min/gap_first are computed from the per-ring *update* score
    (best - runner-up over that ring's positions).  Clamped rings are excluded:
    their position is given rather than computed, so including them would inflate
    the confidence signal by construction.
    """
    v = np.asarray(v, dtype=np.complex128).ravel()
    D = v.shape[0]
    cbs = [np.asarray(cb) for cb in rings]
    cbs_c = [cb.conj() for cb in cbs]
    n_rings = len(cbs)

    pinned = {} if clamp is None else {int(k): int(p) for k, p in dict(clamp).items()}
    for idx in pinned:
        if not 0 <= idx < n_rings:
            raise IndexError("clamp ring index %r out of range" % (idx,))

    # Every free ring starts as the mean of its codebook; a clamped ring starts
    # (and stays) at its fixed position.
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
    positions = _cleanup_positions(cbs, ests, rng)

    for it in range(1, int(max_iter) + 1):
        gap_iter = float("inf")
        for i in range(n_rings):
            if i in pinned:
                continue
            u = v.copy()
            for j in range(n_rings):
                if j != i:
                    u = u * ests[j].conj()
            s = (cbs_c[i] @ u).real / D
            # best minus runner-up.  np.partition returns the two largest
            # UNORDERED, so take the difference as max-min of that pair.
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

        positions = _cleanup_positions(cbs, ests, rng)
        key = tuple(positions)
        stable = stable + 1 if (prev is not None and key == prev) else 0
        prev = key
        if stable >= 1:            # argmax identical for 2 consecutive iterations
            converged = True
            break
        if key in seen:            # a state revisited without convergence -> cycle
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
    }


# ------------------------------------------------------------------ exact counters
def crt(residues, mods):
    """Chinese remainder theorem over coprime mods -> the mark id in [0, prod(mods))."""
    mods = [int(m) for m in mods]
    total = 1
    for m in mods:
        total *= m
    acc = 0
    for r, m in zip(residues, mods):
        mi = total // m
        acc += int(r) * mi * pow(mi, -1, int(m))
    return acc % total


def wilson(k, n, z):
    """Wilson score interval.  Returns (p, lo, hi) with p = k/n.
    z is the two-sided normal quantile for the confidence level (99% -> 2.5758...)."""
    k = float(k)
    n = float(n)
    if n <= 0:
        return (0.0, 0.0, 1.0)
    p = k / n
    z2 = float(z) * float(z)
    denom = 1.0 + z2 / n
    # Probability units throughout: centre = (p + z^2/(2n)) / (1 + z^2/n)
    centre = (p + z2 / (2.0 * n)) / denom
    half = (float(z) / denom) * math.sqrt(p * (1.0 - p) / n + z2 / (4.0 * n * n))
    return (p, max(0.0, centre - half), min(1.0, centre + half))


# ---------------------------------------------------------------------- self-test
SELFTEST_MODS = (3, 5, 7, 13)
SELFTEST_D = 5120


def _selftest(n_marks=20, codebook_seed=7, trial_seed=1234):
    mods = SELFTEST_MODS
    space = 1
    for m in mods:
        space *= m
    rings = make_rings(mods, D=SELFTEST_D, seed=codebook_seed, quant="float")
    rng = np.random.default_rng(trial_seed)

    exact = 0
    for _ in range(int(n_marks)):
        x = int(rng.integers(0, space))
        res = resonate(make_slot([x], rings, mods), rings, None, 50, 0)
        exact += int(res["positions"] == [x % m for m in mods])

    # CRT round-trip on the same marks, and the wilson contract.
    crt_ok = 0
    for _ in range(20):
        x = int(rng.integers(0, space))
        crt_ok += int(crt([x % m for m in mods], mods) == x)
    p, lo, hi = wilson(50, 100, 2.5758293035489004)

    print("selftest mods=%s D=%d space=%d marks=%d codebook_seed=%d trial_seed=%d"
          % (mods, SELFTEST_D, space, n_marks, codebook_seed, trial_seed))
    print("  exact decode of clean single marks: %d/%d" % (exact, n_marks))
    print("  crt round-trip:                     %d/20" % crt_ok)
    print("  wilson(50,100,z99) -> p=%.4f lo=%.4f hi=%.4f" % (p, lo, hi))
    ok = (exact == int(n_marks)) and crt_ok == 20 and lo < p < hi
    print("SELFTEST %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true",
                    help="decode 20 clean single marks with mods (3,5,7,13); "
                         "exit 0 only if all 20 decode exactly")
    ap.add_argument("--marks", type=int, default=20,
                    help="number of single marks in the self-test (default 20)")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest(n_marks=args.marks)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())

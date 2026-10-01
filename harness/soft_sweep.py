#!/usr/bin/env python3
"""RING1-SOFTSWEEP — decode_soft retrieval on superposed slots vs direct_probe (seat rewrite 2026-09-29).

Fleet v1 (kept as soft_sweep.py.fleet-v1) was invalid: marks were stored as an unkeyed SUM of ring vectors (residue codebooks share
position 0), the 17 check ring was never written, decode_soft (a factoriser for BOUND encodings) was fed that sum, and trials were
split round-robin across loads (8-10 per cell). Even k=1 failed (ds 50%, dp 0%), contradicting the verified 1,365/1,365.

This version uses the repo's own paths (omni_ring = the imported module):
  bound slot  = sum over k marks of chain.encode(x, rotations) (all 5 rings incl. 17), as tests/test_gates.py gate 4
  (A) decode_soft over the 5 ring codebooks (unguided = pre-registered arm; clamped at the 13 ring reported as an extra arm)
  (B) direct slot = sum over k marks of GatedMemoryEngine direct codebook rows (independent random codebooks), direct_probe
  gate: check.check_anomaly (17-ring CRT) -> REJECTED; decode_soft also abstains when min(confidences) < min_confidence.
  CORRECT = a true member; SILENT-WRONG = passes every gate and is not a member.
Usage: bench/soft_sweep.py [--quick] [--trials N] [--out PATH]
"""
from __future__ import annotations
import argparse, math, sys, time
import numpy as np
from omni_ring.codebook import generate_rotations, generate_direct_codebooks
from omni_ring.chain import encode
from omni_ring.resonator import decode_soft
from omni_ring.crt import direct_probe
from omni_ring.check import check_anomaly
from omni_ring.types import DEFAULT_SPEC as SPEC

PRE_REG = ("PASS if decode_soft's silent-wrong rate has a Wilson-99% UPPER bound <= 0.02 at every k <= 10 with min_confidence = 0.1, "
           "AND its correct rate at k = 5 exceeds direct_probe's correct rate at k = 5 by >= 0.20 absolute. Otherwise KILL (state which half failed).")
LOADS = (1, 2, 5, 10, 20, 50, 100)
MCS = (0.0, 0.05, 0.1, 0.2, 0.3)
MODS = SPEC.all_moduli  # (3,5,7,13,17)
N = SPEC.data_capacity  # 1365


def wilson(k, n, z=2.576):
    if n == 0:
        return (0.0, 1.0)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def classify(residues, conf, mc, members):
    if mc > 0 and conf is not None and min(conf) < mc:
        return "REJ"
    try:
        x = check_anomaly(list(residues), SPEC)
    except Exception:
        return "REJ"
    return "OK" if x in members else "SWR"


def run(trials, seed=0):
    rot = generate_rotations(SPEC, seed=seed)
    cb = [np.exp(1j * np.outer(np.arange(m), r)) for m, r in zip(MODS, rot)]
    dcb = generate_direct_codebooks(SPEC, seed=seed + 1)
    dconj = [np.conj(c) for c in dcb]
    rng = np.random.default_rng(seed + 7)
    arms = {f"ds@{mc}": {k: {"OK": 0, "REJ": 0, "SWR": 0} for k in LOADS} for mc in MCS}
    arms["ds_clamp13@0.1"] = {k: {"OK": 0, "REJ": 0, "SWR": 0} for k in LOADS}
    arms["dp"] = {k: {"OK": 0, "REJ": 0, "SWR": 0} for k in LOADS}
    t0 = time.time()
    for k in LOADS:
        for _ in range(trials):
            xs = [int(x) for x in rng.choice(N, size=k, replace=False)]
            members = set(xs)
            v = sum(encode(x, rot) for x in xs)
            r = decode_soft(v, cb, iterations=30)
            for mc in MCS:
                arms[f"ds@{mc}"][k][classify(r.residues, r.confidences, mc, members)] += 1
            t = xs[0]
            rc = decode_soft(v, cb, iterations=30, clamp=t % 13, clamp_idx=3)
            arms["ds_clamp13@0.1"][k][classify(rc.residues, rc.confidences, 0.1, members)] += 1
            vd = sum(sum(c[x % m] for c, m in zip(dcb, MODS)) for x in xs)
            res, _ = direct_probe(vd, dcb, MODS, codebooks_conj=dconj)
            arms["dp"][k][classify(res, None, 0.0, members)] += 1
    return arms, time.time() - t0


def verdict(arms, trials):
    c1 = []
    for k in (1, 2, 5, 10):
        s = arms["ds@0.1"][k]["SWR"]; ub = wilson(s, trials)[1]
        if ub > 0.02:
            c1.append(f"k={k} silent-wrong {s}/{trials} upper {ub:.3f} > 0.02")
    ds5 = arms["ds@0.1"][5]["OK"] / trials; dp5 = arms["dp"][5]["OK"] / trials
    c2 = ds5 - dp5 >= 0.20
    if not c1 and c2:
        return "PASS", f"silent-wrong upper bound <= 0.02 at k<=10; correct@k=5 ds {ds5:.2f} vs dp {dp5:.2f}"
    why = []
    if c1:
        why.append("half 1 (silent-wrong): " + "; ".join(c1))
    if not c2:
        why.append(f"half 2 (correct@k=5): ds {ds5:.2f} - dp {dp5:.2f} = {ds5 - dp5:+.2f} < 0.20")
    return "KILL", " | ".join(why)


def table(arms, trials):
    out = ["| arm | k | correct [99% CI] | rejected | silent-wrong [99% CI] | chance-of-member |", "|---|---|---|---|---|---|"]
    for a, cells in arms.items():
        for k, c in cells.items():
            lo, hi = wilson(c["OK"], trials); slo, shi = wilson(c["SWR"], trials)
            out.append(f"| {a} | {k} | {c['OK']}/{trials} [{lo:.2f},{hi:.2f}] | {c['REJ']}/{trials} | {c['SWR']}/{trials} [{slo:.2f},{shi:.2f}] | {k / N:.4f} |")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true"); ap.add_argument("--trials", type=int)
    ap.add_argument("--out"); a = ap.parse_args()
    trials = a.trials or (30 if a.quick else 100)
    arms, secs = run(trials)
    v, why = verdict(arms, trials)
    print(table(arms, trials)); print(f"\n{trials} trials/cell, {secs:.0f}s"); print(("VERDICT (quick smoke, not decisive): " if a.quick else "VERDICT: ") + v + " -- " + why)
    if a.out and not a.quick:
        with open(a.out, "w") as f:
            f.write(f"{v}{': ' + why if v == 'KILL' else ''}\n\n# RING1-SOFTSWEEP — decode_soft vs direct_probe on superposed slots (seat rewrite)\n\n"
                    f"## Pre-registration (verbatim)\n{PRE_REG}\n\n## Setup\nomni_ring (imported module), D={SPEC.dimension}, rings {MODS}, "
                    f"{trials} trials per cell, decode_soft 30 iterations, gate = check_anomaly (17-ring CRT). Bound slots for decode_soft; "
                    f"direct (independent codebooks) slots for direct_probe. Fleet v1 harness defects: see module docstring.\n\n"
                    f"## Results\n{table(arms, trials)}\n\nRuntime {secs:.0f}s.\n\n## Verdict\n{v}: {why}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""RING-3b DIAMOND-2 (seat, 2026-09-29): can the diamond be made readable?
  (a) small category corners K in {15, 35} (+ centre checksum 17), 2 corners known.
  (b) residue corners (3,5,7)+check 11 each, 2 corners known AND a one-ring cue (the 7 ring) inside each unknown corner.
Baseline from RING3-RESULTS: K=105 category corners, 2 known -> 35.3% (M=12); flat (3,5,7,13)+17 with 2 clamps -> 96%."""
import sys, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); sys.path.insert(0, str(Path(__file__).parents[1] / "ring1"))
import run_ring3 as R, ring1_core as rc
D = R.D
def cat(trials, K, C=17, seed=11):
    rng = np.random.default_rng(seed); cbs = [R.rand_cb(K, rng) for _ in range(4)] + [R.rand_cb(C, rng)]
    for M in (12, 24):
        ok = w = f = 0
        for _ in range(trials):
            marks = [tuple(int(x) for x in rng.integers(0, K, 4)) for _ in range(M)]
            v = sum(R.bind_rows(cbs, list(mk) + [sum(mk) % C]) for mk in marks); t = marks[0]
            p = R.res_general(v, cbs, clamp={0: t[0], 1: t[1]})["positions"]
            if (p[2], p[3]) == (t[2], t[3]): ok += 1
            else: w += 1; f += p[4] != (t[0] + t[1] + p[2] + p[3]) % C
        print(f"| (a) category corners K={K} + checksum | {M} | {R.fmt(ok, trials)} | {f}/{w} |")
def resid(trials, seed=11):
    cm = (3, 5, 7, 11); cap = 105; rings = []
    for c in range(4): rings += rc.make_rings(cm, D, seed=seed * 100 + c, quant="float")
    rng = np.random.default_rng(seed + 1)
    for M in (12, 24):
        ok = w = f = 0
        for _ in range(trials):
            marks = [tuple(int(x) for x in rng.integers(0, cap, 4)) for _ in range(M)]
            v = sum(R.bind_rows(rings, [val % m for val in mk for m in cm]) for mk in marks); t = marks[0]
            clamp = {c * 4 + r: t[c] % m for c in (0, 1) for r, m in enumerate(cm)}
            clamp.update({c * 4 + 2: t[c] % 7 for c in (2, 3)})
            p = R.res_general(v, rings, clamp=clamp)["positions"]
            dec, ill = [], False
            for c in (2, 3):
                x = rc.crt([p[c * 4 + r] for r in range(4)], cm); ill |= x >= cap; dec.append(x)
            if dec == [t[2], t[3]]: ok += 1
            else: w += 1; f += ill
        print(f"| (b) residue corners (3,5,7)+11, 7-ring cue per unknown corner | {M} | {R.fmt(ok, trials)} | {f}/{w} |")
if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    print("| design | M | recall of both unknown corners (2 known) | wrong settles flagged |\n|---|---|---|---|")
    cat(n, 15); cat(n, 35); resid(n)

#!/usr/bin/env python3
"""CF-2e (CORE-FIELD plan, pre-registered before this file): Zhang-1996 velocity-modulated odd weights; gamma calibrated on a
held-out walk set (seed 99), then scored once on cf2d.measure (seed 0). Result -> ~/gpurun-out-0930/cf2e.result.json"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cf2d as c


def zstep(a, v=(0.0, 0.0), extra=0.0, noise=0.0, gam=16.0, w_ex=2.0, w_in=2.5, b0=0.05, tau=0.1):
    tot = np.zeros_like(a)
    for d in range(4):
        al = v[0] * c.DIRS[d][0] + v[1] * c.DIRS[d][1]
        a_d = a * c.MASK[d]; ex, ey = c.L_OFFSET * c.DIRS[d][0], c.L_OFFSET * c.DIRS[d][1]
        for dy, dx, w in c.BASE_TAPS:
            tot += (1 + gam * al) * w * np.roll(a_d, (ey + dy, ex + dx), (0, 1))
    drive = w_ex * tot - w_in * 6 * a.mean() + b0 + extra
    if noise: drive = drive + noise * c.rng.normal(size=a.shape)
    return np.clip(a + tau * (-a + drive), 0, 1)


def heldout_move(gam, walks=10):
    r = np.random.default_rng(99); hits = 0
    for _ in range(walks):
        a = c.bump_at(24, 24); t = np.array([24.0, 24.0])
        for _ in range(30): a = zstep(a, gam=gam)
        for _ in range(100):
            v = r.normal(0, 0.3, 2); t += v; a = zstep(a, tuple(v), gam=gam)
        hits += int(c.wrap_dist(c.centre(a), t % c.N) <= 2.0)
    return hits / walks


cal = {g: heldout_move(g) for g in (8, 12, 16, 20, 24, 32)}
gbest = max(cal, key=lambda g: (cal[g], -abs(g - 16)))
c.rng = np.random.default_rng(0)
mv, hd, rl = c.measure(zstep, dict(gam=float(gbest)), False)
res = {"calibration_heldout_move": cal, "gamma": gbest, "move": mv, "hold": hd, "release": rl,
       "verdict": {"MOVE_ge_0.95": mv >= 0.95, "HOLD_ge_0.99": hd >= 0.99, "RELEASE_le_20": rl is not None and rl <= 20,
                   "KILL_move_lt_0.5": mv < 0.5}}
res["verdict"]["PASS"] = all(res["verdict"][k] for k in ("MOVE_ge_0.95", "HOLD_ge_0.99", "RELEASE_le_20"))
json.dump(res, open(os.path.expanduser("~/gpurun-out-0930/cf2e.result.json"), "w"), indent=1)
print(json.dumps(res, indent=1))

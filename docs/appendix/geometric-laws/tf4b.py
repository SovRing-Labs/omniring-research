#!/usr/bin/env python3
"""TF-4b (TRUEFORM plan, pre-registered after TF-4 FAIL): random-program acceptance rate, RANDOM vs WIND slot positions,
20,000 uniform random program vectors per arm, same decoder as SOURCE-3."""
import importlib, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

N = 20000
res = {"analytic_base_rate": (1 / 48) * (1 / 48)}
for arm in ("random", "wind"):
    if arm == "wind":
        os.environ["SOURCE_POS"] = "wind"
    else:
        os.environ.pop("SOURCE_POS", None)
    import source3 as S3
    S3 = importlib.reload(S3)
    g = np.random.default_rng(4242)
    acc = 0
    for _ in range(N):
        v = (S3.PH[g.integers(0, 16, S3.D)] * 3).astype(np.complex64)
        acc += S3.read_program(v) is not None
    p = acc / N; se = np.sqrt(max(p * (1 - p), 1e-12) / N)
    res[arm] = {"accepted": int(acc), "of": N, "rate": p, "ci95": [max(0.0, p - 1.96 * se), p + 1.96 * se], "se": se}
    print(f"TF-4b {arm}: accepted {acc}/{N} = {p:.5f} (95% CI {res[arm]['ci95'][0]:.5f}-{res[arm]['ci95'][1]:.5f})", flush=True)
res["verdict"] = {"PASS": bool(res["wind"]["rate"] <= res["random"]["rate"] + 2 * res["random"]["se"])}
print("TF-4b analytic base rate", round(res["analytic_base_rate"], 5), "verdict", res["verdict"], flush=True)
json.dump(res, open(os.path.expanduser("~/gpurun-out-0930/tf4b.result.json"), "w"), indent=1)

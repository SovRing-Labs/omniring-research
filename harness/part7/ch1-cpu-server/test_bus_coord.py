# SHM-BUS-0 B1 tests: synthetic slabs → exact mean, harmony drops (NaN, loss outlier, drift outlier, torn write), K follows the drift (L9 rule).
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "cloud"))
import bus_coord as bc

P = 10_000


def put(d, i, w, loss=1.0, step=1, chk=True, torn=False):
    w = w.astype(np.float32); w.tofile(os.path.join(d, f"h{i}.w"))
    if chk:
        res = bc.residues(w)
        if torn: res[0] = (res[0] + 1) % bc.PRIMES[0]
        json.dump({"step": step, "res": res}, open(os.path.join(d, f"h{i}.chk"), "w"))
    json.dump({"step": step, "loss_ema": loss}, open(os.path.join(d, f"h{i}.json"), "w"))


def test_mean_exact(tmp_path):
    r = np.random.default_rng(0); Ws = [r.normal(size=P) for _ in range(4)]
    for i, w in enumerate(Ws): put(tmp_path, i, w)
    st = bc.Coord(str(tmp_path), 4).tick()
    M = np.fromfile(tmp_path / "mean.w", dtype=np.float32)
    assert np.allclose(M, np.mean([w.astype(np.float32) for w in Ws], axis=0, dtype=np.float64).astype(np.float32))
    assert not any(h["drop"] for h in st["h"].values())


def test_harmony_drops(tmp_path):
    r = np.random.default_rng(1); base = r.normal(size=P)
    for i in range(5): put(tmp_path, i, base + 0.01 * r.normal(size=P), loss=1.0 + 0.001 * i)
    bad = base.copy(); bad[7] = np.nan; put(tmp_path, 1, bad)                        # NaN
    put(tmp_path, 2, base + 0.01 * r.normal(size=P), loss=9.0)                       # loss outlier
    put(tmp_path, 3, base + 0.5 * r.normal(size=P))                                  # drift outlier
    put(tmp_path, 4, base + 0.01 * r.normal(size=P), torn=True)                      # torn write
    put(tmp_path, 5, base + 0.01 * r.normal(size=P), loss=1.002)
    put(tmp_path, 6, base + 0.01 * r.normal(size=P), loss=0.999)
    st = bc.Coord(str(tmp_path), 7).tick()
    why = {k: v["why"] for k, v in st["h"].items()}
    assert st["h"]["1"]["drop"] and "NaN" in why["1"]
    assert st["h"]["2"]["drop"] and "loss_ema" in why["2"]
    assert st["h"]["3"]["drop"] and "drift" in why["3"]
    assert st["h"]["4"]["drop"] and "residue" in why["4"]
    assert not any(st["h"][k]["drop"] for k in ("0", "5", "6"))
    M = np.fromfile(tmp_path / "mean.w", dtype=np.float32)
    assert np.isfinite(M).all() and float(np.sqrt(np.mean((M - base) ** 2))) < 0.02   # the mean ignores the dropped harnesses


def test_k_follows_drift(tmp_path):
    r = np.random.default_rng(2); base = r.normal(size=P); co = bc.Coord(str(tmp_path), 4, c=2.0, s_tol=0.05)   # accepted spread = a day-merge spread (> per-sync drift)
    for i in range(4): put(tmp_path, i, base + 0.01 * r.normal(size=P))
    co.tick()                                                                        # sets s_tol from the first spread
    for i in range(4): put(tmp_path, i, base + 0.011 * r.normal(size=P), step=2)     # small drift
    k_small = co.tick()["K"]
    for i in range(4): put(tmp_path, i, base + 0.05 * r.normal(size=P), step=3)      # big drift
    k_big = co.tick()["K"]
    assert 0 < k_small < k_big <= 1.0, (k_small, k_big)


def test_fixed_k(tmp_path):
    r = np.random.default_rng(3)
    for i in range(3): put(tmp_path, i, r.normal(size=P))
    co = bc.Coord(str(tmp_path), 3, k_fixed=1.0); co.tick(); assert co.tick()["K"] == 1.0

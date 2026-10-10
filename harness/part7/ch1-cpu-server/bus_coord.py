#!/usr/bin/env python3
"""SHM-BUS-0 B1 — the shared-RAM bus coordinator (J 10-08 approved; design <notes>/worker/claude/SHM-BUS-0.design.md). Grown from par_merge.py.

N harnesses on ONE box write their weights to mmap'd slabs in BUS_DIR (/dev/shm/thead-bus): h<i>.w (raw float32, ckpt.bin weight layout),
then h<i>.chk (residue check, below). This coordinator keeps mean.w = the mean of the healthy slabs, and bus.json:
  {"K": float, "step": int, "spread": float, "drift": float, "h": {"<i>": {"step": int, "loss_ema": float, "drop": bool, "why": str}}}
Harnesses pull w ← w + K·(mean − w) every BUS_EVERY steps (thead.rs B2) and write their own "step" / "loss_ema" into bus.json's h.<i> via
h<i>.json (the coordinator merges those files; harnesses never write bus.json).

Coupling (law L9, Adler: lock exists iff K ≥ Δω/2). Between syncs the harnesses drift apart by g (rms per sync, measured as the spread growth
since the last pull); a pull with K shrinks the spread by (1 − K); steady spread s* = g / K. K_auto = clamp(C · g / (2 · S_TOL), K_MIN, 1):
C = 1.5–3 × critical (L9: 3·Kc locks in 2 ticks, 1.5·Kc in 7), S_TOL = the spread we accept (default: the last measured day-merge spread).
Harmony (law L13): a harness is dropped (weight 0 in the mean, flagged for re-seed from mean.w) when its loss_ema leaves the others' band
(> MAD_K robust deviations from the median), when its slab holds NaN/Inf, when its drift from the mean is > DRIFT_X × the median drift, or when
its residue check fails (torn write — law L6: detects, does not authenticate).
Residue check: h<i>.chk = JSON {"step": s, "res": [sum of the slab's uint32 words mod p for p in PRIMES]}.

python3 bus_coord.py <BUS_DIR> <N> [--c 2.0] [--s-tol auto|<float>] [--k fixed] [--every 0.5] [--idle 900]
"""
import argparse, json, math, os, time
import numpy as np

PRIMES = (65521, 65519, 65497)


def residues(arr):
    u = arr.view(np.uint32).astype(np.uint64)
    return [int(u.sum() % p) for p in PRIMES]


def robust_out(vals, k):
    v = np.array(vals, dtype=np.float64); med = np.median(v); mad = np.median(np.abs(v - med)) or 1e-12
    return [abs(x - med) / (1.4826 * mad) > k for x in v]


class Coord:
    def __init__(self, d, n, c=2.0, s_tol=None, k_fixed=None, mad_k=6.0, drift_x=4.0, k_min=0.02):
        self.d, self.n, self.c, self.s_tol, self.k_fixed, self.mad_k, self.drift_x, self.k_min = d, n, c, s_tol, k_fixed, mad_k, drift_x, k_min
        self.prev_spread = None; self.K = 1.0 if k_fixed is None else k_fixed; self.state = {"K": self.K, "step": 0, "h": {}}

    def slab(self, i):
        p = os.path.join(self.d, f"h{i}.w")
        return np.memmap(p, dtype=np.float32, mode="r") if os.path.exists(p) else None

    def check_ok(self, i, w):
        p = os.path.join(self.d, f"h{i}.chk")
        if not os.path.exists(p): return True, ""
        try: chk = json.load(open(p))
        except ValueError: return False, "check unreadable"
        return (chk.get("res") == residues(np.asarray(w)), "residue check failed (torn write)")

    def tick(self):
        W, ids = [], []
        for i in range(self.n):
            w = self.slab(i)
            if w is not None: W.append(np.asarray(w)); ids.append(i)
        if len(W) < 2 or len({w.size for w in W}) != 1: return None
        hs = {}
        for i in ids:
            p = os.path.join(self.d, f"h{i}.json")
            try: hs[i] = json.load(open(p))
            except (OSError, ValueError): hs[i] = {}
        drop = {i: "" for i in ids}
        for k, i in enumerate(ids):
            if not np.isfinite(W[k]).all(): drop[i] = "NaN/Inf in slab"
            ok, why = self.check_ok(i, W[k])
            if not ok: drop[i] = why
        live = [k for k, i in enumerate(ids) if not drop[i]]
        if len(live) >= 3:
            losses = [hs[ids[k]].get("loss_ema", math.nan) for k in live]
            if all(math.isfinite(x) for x in losses):
                for k, out in zip(live, robust_out(losses, self.mad_k)):
                    if out: drop[ids[k]] = f"loss_ema {hs[ids[k]]['loss_ema']:.4f} outside the band"
        live = [k for k, i in enumerate(ids) if not drop[i]]
        # drift is measured against the coordinate-wise MEDIAN of the live slabs: one outlier cannot move it (a mean, even leave-one-out,
        # is pulled toward the outlier when only a few harnesses are healthy)
        MED = np.median(np.stack([W[k] for k in live]), axis=0)
        dist = [float(np.sqrt(np.mean((W[k] - MED) ** 2))) for k in live]
        med = float(np.median(dist)) or 1e-12
        for k, dd in zip(live, dist):
            if dd > self.drift_x * med and len(live) >= 3: drop[ids[k]] = f"drift {dd:.2e} > {self.drift_x}× median {med:.2e}"
        live = [k for k, i in enumerate(ids) if not drop[i]]
        M = np.mean([W[k] for k in live], axis=0, dtype=np.float64).astype(np.float32)
        spread = float(np.mean([np.sqrt(np.mean((W[k] - M) ** 2)) for k in live]))
        g = 0.0 if self.prev_spread is None else max(0.0, spread - self.prev_spread * (1.0 - self.K))
        if self.s_tol is None: self.s_tol = spread or 1e-6           # first measurement sets the accepted spread
        if self.k_fixed is None and self.prev_spread is not None:
            self.K = float(min(1.0, max(self.k_min, self.c * g / (2.0 * self.s_tol))))
        self.prev_spread = spread
        tmp = os.path.join(self.d, "mean.w.tmp"); M.tofile(tmp); os.replace(tmp, os.path.join(self.d, "mean.w"))
        self.state = {"K": self.K, "step": max((hs[i].get("step", 0) for i in ids), default=0), "spread": spread, "drift": g, "s_tol": self.s_tol,
                      "h": {str(i): {"step": hs[i].get("step", 0), "loss_ema": hs[i].get("loss_ema"), "drop": bool(drop[i]), "why": drop[i]} for i in ids},
                      "at": time.strftime("%H:%M:%S")}
        tmp = os.path.join(self.d, "bus.json.tmp"); json.dump(self.state, open(tmp, "w")); os.replace(tmp, os.path.join(self.d, "bus.json"))
        return self.state


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("dir"); ap.add_argument("n", type=int); ap.add_argument("--c", type=float, default=2.0)
    ap.add_argument("--s-tol", default="auto"); ap.add_argument("--k", type=float); ap.add_argument("--every", type=float, default=0.5)
    ap.add_argument("--idle", type=float, default=900)
    a = ap.parse_args(); os.makedirs(a.dir, exist_ok=True)
    co = Coord(a.dir, a.n, a.c, None if a.s_tol == "auto" else float(a.s_tol), a.k)
    log = open(os.path.join(a.dir, "bus.log"), "a"); last_step, last_t = -1, time.time()
    while not os.path.exists(os.path.join(a.dir, "STOP")):
        st = co.tick()
        if st and st["step"] != last_step:
            last_step, last_t = st["step"], time.time(); print(json.dumps(st), file=log, flush=True)
        if time.time() - last_t > a.idle: print(f"idle {a.idle}s — stopping", file=log, flush=True); break
        time.sleep(a.every)


if __name__ == "__main__":
    main()

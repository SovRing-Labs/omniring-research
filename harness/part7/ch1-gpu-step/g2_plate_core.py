#!/usr/bin/env python3
"""GROW-RUN-0 G2 — the plate core alone: the GPU plate kernels (pphi, pscore, pden, pv, pnorm; pc, pg, pp, pv / ptv, pdphi) vs the engine's
own exported plate core om_plate_test (plate_core_fwd + plate_core_bwd: one sequence, one head) on the same q, k, v, row starts, pages, dy.
Compared: y, den, dq, dk, dv.   g2_plate_core.py [--T 64] [--DH 32] [--pages 4] [--device llvmpipe] [--seed 1]"""
import ctypes, json, os, subprocess, sys, tempfile
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, f"{P}/gen"); sys.path.insert(0, HERE)
import train_step
from s1_grad import LIB, BIN

def main():
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    T, DH, NP, dev, seed = int(opt("--T", "64")), int(opt("--DH", "32")), int(opt("--pages", "4")), opt("--device", "llvmpipe"), int(opt("--seed", "1"))
    rng = np.random.default_rng(seed); f32 = np.float32
    q, k, v, dy = (rng.standard_normal((T, DH)).astype(f32) * f32(0.7) for _ in range(4))
    ends = sorted(rng.choice(np.arange(3, T - 1), size=max(2, T // 10), replace=False)); rs = np.zeros(T, np.int32); st = 0
    for t in range(T):
        rs[t] = st
        if t in ends: st = t + 1
    bq = rng.integers(0, NP, T).astype(np.int32); bk = rng.integers(0, NP, T).astype(np.int32)
    Lb = ctypes.CDLL(LIB); fp = np.ctypeslib.ndpointer(np.float32, flags="C_CONTIGUOUS"); ip = np.ctypeslib.ndpointer(np.int32, flags="C_CONTIGUOUS")
    Lb.om_plate_test.argtypes = [fp, fp, fp, ip, ip, ip, fp, fp, fp, fp, fp, fp, ctypes.c_int, ctypes.c_int]
    y, den, dq, dk, dv = np.zeros((T, DH), f32), np.zeros(T, f32), np.zeros((T, DH), f32), np.zeros((T, DH), f32), np.zeros((T, DH), f32)
    Lb.om_plate_test(q, k, v, rs, bq, bk, dy, y, den, dq, dk, dv, T, DH)
    with tempfile.TemporaryDirectory(prefix="g2-plate-") as Tm:
        pr = train_step.Prog(Tm); B = lambda n, d: pr.buf(n, data=d)
        Q, K, V, dY = B("Q", q), B("K", k), B("V", v), B("dY", dy)
        BQ, BK, RS = B("bq", bq.astype(f32)), B("bk", bk.astype(f32)), B("rs", rs); Z = pr.buf("zero", T * DH * 4)
        fb = lambda n, s: pr.buf(n, s * 4)
        phQ, phK, A, den_, AV, Yp = fb("phQ", T * DH), fb("phK", T * DH), fb("A", T * T), fb("den", T), fb("AV", T * DH), fb("Yp", T * DH)
        pr.k("pphi", [Q, phQ], n_out=T * DH); pr.k("pphi", [K, phK], n_out=T * DH)
        pr.k("pscore", [phQ, phK, BQ, BK, RS, A], (T, DH), n_out=T * T, rows=1, row_strides=[T * DH, T * DH, T, T, T], out_stride=T * T)
        pr.k("pden", [A, den_], (T,), n_out=T, rows=1, row_strides=[T * T], out_stride=T)
        pr.k("pv", [A, V, AV], (T, DH), n_out=T * DH, rows=1, row_strides=[T * T, T * DH], out_stride=T * DH)
        pr.k("pnorm", [AV, den_, Yp], (DH,), n_out=T * DH, rows=1, row_strides=[T * DH, T], out_stride=T * DH)
        dP, c, G, Pp = fb("dP", T * T), fb("c", T), fb("G", T * T), fb("Pp", T * T)
        pr.k("qkT", [dY, V, dP], (T, DH), n_out=T * T, rows=1, row_strides=[T * DH, T * DH], out_stride=T * T)
        pr.k("pc", [dY, Yp, den_, c], (DH,), n_out=T, rows=1, row_strides=[T * DH, T * DH, T], out_stride=T)
        pr.k("pg", [A, dP, den_, c, G], (T,), n_out=T * T, rows=1, row_strides=[T * T, T * T, T, T], out_stride=T * T)
        pr.k("pp", [A, den_, Pp], (T,), n_out=T * T, rows=1, row_strides=[T * T, T], out_stride=T * T)
        dpq, dpk, dpv, oq, ok_ = fb("dpq", T * DH), fb("dpk", T * DH), fb("dpv", T * DH), fb("oq", T * DH), fb("ok", T * DH)
        pr.k("pv", [G, phK, dpq], (T, DH), n_out=T * DH, rows=1, row_strides=[T * T, T * DH], out_stride=T * DH)
        pr.k("ptv", [G, phQ, dpk], (T, DH), n_out=T * DH, rows=1, row_strides=[T * T, T * DH], out_stride=T * DH)
        pr.k("ptv", [Pp, dY, dpv], (T, DH), n_out=T * DH, rows=1, row_strides=[T * T, T * DH], out_stride=T * DH)
        pr.k("pdphi", [Z, dpq, Q, oq], n_out=T * DH); pr.k("pdphi", [Z, dpk, K, ok_], n_out=T * DH)
        outs = {"y": Yp, "den": den_, "dq": oq, "dk": ok_, "dv": dpv}
        lines, idx = pr.program(pinned=set(outs.values()))
        open(f"{Tm}/prog.txt", "w").write("\n".join(lines + [f"read {idx[b]}" for b in outs.values()]) + "\n")
        r = subprocess.run([BIN, "session", f"{Tm}/prog.txt", "--device", dev, "--steps", "1", "--out", f"{Tm}/o"], capture_output=True, text=True)
        if r.returncode: sys.exit(r.stderr[-1500:])
        got = {n: np.fromfile(f"{Tm}/o/buf{idx[b]}.bin", np.float32) for n, b in outs.items()}
    want = {"y": y.ravel(), "den": den, "dq": dq.ravel(), "dk": dk.ravel(), "dv": dv.ravel()}; rec = {"T": T, "DH": DH, "pages": NP, "device": dev}
    ok = True
    for n in want:
        w, g = want[n].astype(np.float64), got[n][:want[n].size].astype(np.float64); m = max(np.abs(w).max(), 1e-30)
        rel = float(np.abs(w - g).max() / m); rec[n] = {"max_rel": rel, "worst_at": int(np.abs(w - g).argmax())}; ok &= rel <= 1e-4
    rec["pass"] = bool(ok); print(json.dumps(rec)); sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()

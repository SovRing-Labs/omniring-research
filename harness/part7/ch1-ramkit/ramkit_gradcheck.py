"""RAM-KIT-0 gradcheck (#4 ring memory gate + rows, #5 episodic gate). Central finite differences of f = Σ dy·y on the memory op alone
(engine hooks om_rmem_test / om_epi_test on a tiny real model, as om_plate_test does for plates), float64 accumulation in Python.
  #4 quant 0 (float rows): x, gate w/b, touched rows all FD-checked.  quant 1 (ternary read, STE): gate w/b + x FD-checked; the row grads
     must equal the float-row formula (STE passes the read's gradient straight to the latent row).
  #5: the store is not differentiable by design (selection + mix are constants); the gate w/b are FD-checked.
Usage: python3 ramkit_gradcheck.py <lib.so>  → one JSON line, pass = worst rel err ≤ 1e-2 everywhere (the engine's gradcheck bar)."""
import ctypes
import json
import sys

import numpy as np

lib = ctypes.CDLL(sys.argv[1]); P, I, F = ctypes.c_void_p, ctypes.c_int, ctypes.c_float
fp = np.ctypeslib.ndpointer(np.float32, flags="C_CONTIGUOUS"); ipn = np.ctypeslib.ndpointer(np.int32, flags="C_CONTIGUOUS")
def fn(n, a, r=None): f = getattr(lib, n); f.argtypes = a; f.restype = r; return f
create = fn("om_create", [I, I, I, I, I, ipn, I, ctypes.c_uint64], P); fn("om_threads", [I])(1)
nparams, pname = fn("om_nparams", [P], I), fn("om_param_name", [P, I], ctypes.c_char_p)
psize, pptr, gptr = fn("om_param_size", [P, I], ctypes.c_long), fn("om_param_ptr", [P, I], ctypes.POINTER(F)), fn("om_param_grad", [P, I], ctypes.POINTER(F))
set_rm = fn("om_set_ring_mem", [P, I, I, I, I, F], I); rm_ptr = fn("om_rmem_ptr", [P, ctypes.POINTER(ctypes.c_long)], ctypes.POINTER(F))
rm_test = fn("om_rmem_test", [P, fp, ipn, I, I, fp, fp, fp, ctypes.c_void_p])
set_epi = fn("om_set_epi", [P, I, I, F], I); epi_write = fn("om_epi_write", [P, ipn, I], I); epi_test = fn("om_epi_test", [P, fp, I, fp, fp, fp])
fwd = fn("om_forward_loss", [P, ipn, ipn, I, I], F)
V, D, L, H, T, B = 64, 32, 2, 2, 16, 2; N = B * T
PR = np.array([3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137], np.int32)
rng = np.random.default_rng(5)


def view(h, name):
    for i in range(nparams(h)):
        if pname(h, i).decode() == name:
            n = psize(h, i); return np.ctypeslib.as_array(pptr(h, i), (n,)), np.ctypeslib.as_array(gptr(h, i), (n,))
    raise KeyError(name)


def rel(a, b): return float(np.max(np.abs(a - b)) / max(np.max(np.abs(b)), 1e-8))


def ring(quant):
    h = create(V, D, L, H, T, PR, (D // H) // 2, 3); S = set_rm(h, 64, 2, 0, quant, 1.0)
    n = ctypes.c_long(); W = np.ctypeslib.as_array(rm_ptr(h, ctypes.byref(n)), (n.value,)); W[:] = rng.normal(0, 0.5, n.value).astype(np.float32)
    gw, ggw = view(h, "rmem.gw"); gb, ggb = view(h, "rmem.gb"); gw[:] = rng.normal(0, 0.3, D).astype(np.float32); gb[:] = 0.2
    x = rng.normal(0, 1, (N, D)).astype(np.float32); tok = rng.integers(0, V, (B, T)).astype(np.int32); tok[1, 5:8] = tok[0, 5:8]   # shared n-grams
    dy = rng.normal(0, 1, (N, D)).astype(np.float32)
    y, dx, dW = np.zeros_like(x), np.zeros_like(x), np.zeros(n.value, np.float32)
    def f(xx):
        yy = np.zeros_like(x); rm_test(h, np.ascontiguousarray(xx), tok, B, T, dy, yy, np.zeros_like(x), None); return float(np.sum(yy.astype(np.float64) * dy))
    rm_test(h, x, tok, B, T, dy, y, dx, dW.ctypes.data); agw, agb = ggw.copy(), ggb.copy()
    e = 1e-3; out = {"rows": S}
    idx = [(i, j) for i in range(0, N, 5) for j in (0, 7, 31)]
    num = []
    for (i, j) in idx:
        xp = x.copy(); xp[i, j] += e; xm = x.copy(); xm[i, j] -= e; num.append((f(xp) - f(xm)) / (2 * e))
    out["x"] = rel(np.array([dx[i, j] for i, j in idx]), np.array(num))
    nw = []
    for j in range(D):
        o = gw[j]; gw[j] = o + e; a = f(x); gw[j] = o - e; c = f(x); gw[j] = o; nw.append((a - c) / (2 * e))
    out["gate_w"] = rel(agw, np.array(nw))
    o = gb[0]; gb[0] = o + e; a = f(x); gb[0] = o - e; c = f(x); gb[0] = o; out["gate_b"] = rel(agb, np.array([(a - c) / (2 * e)]))
    touched = np.nonzero(np.abs(dW) > 0)[0]
    if quant == 0:
        pick = touched[:: max(1, len(touched) // 40)]; nr = []
        for k in pick:
            o = W[k]; W[k] = o + e; a = f(x); W[k] = o - e; c = f(x); W[k] = o; nr.append((a - c) / (2 * e))
        out["rows_fd"] = rel(dW[pick], np.array(nr)); out["rows_checked"] = int(len(pick))
    out["touched_entries"] = int(len(touched))
    return out, dW, h


def epi():
    h = create(V, D, L, H, T, PR, (D // H) // 2, 4); set_epi(h, 32, 4, 0.1)
    gw, ggw = view(h, "epi.gw"); gb, ggb = view(h, "epi.gb"); gw[:] = rng.normal(0, 0.3, D).astype(np.float32); gb[:] = -0.5
    xs = rng.integers(0, V, (B, T)).astype(np.int32).ravel(); ys = rng.integers(0, V, (B, T)).astype(np.int32).ravel()
    fwd(h, xs, ys, B, T); held = epi_write(h, np.arange(0, N, 1, dtype=np.int32), 24)
    x = rng.normal(0, 1, (N, D)).astype(np.float32); dy = rng.normal(0, 1, (N, D)).astype(np.float32)
    def f():
        yy = np.zeros_like(x); epi_test(h, x, N, dy, yy, np.zeros_like(x)); return float(np.sum(yy.astype(np.float64) * dy))
    y, dx = np.zeros_like(x), np.zeros_like(x); epi_test(h, x, N, dy, y, dx); agw, agb = ggw.copy(), ggb.copy()
    e = 1e-3; nw = []
    for j in range(D):
        o = gw[j]; gw[j] = o + e; a = f(); gw[j] = o - e; c = f(); gw[j] = o; nw.append((a - c) / (2 * e))
    o = gb[0]; gb[0] = o + e; a = f(); gb[0] = o - e; c = f(); gb[0] = o
    return {"entries": held, "gate_w": rel(agw, np.array(nw)), "gate_b": rel(agb, np.array([(a - c) / (2 * e)])), "read_moved_y": float(np.max(np.abs(y - x)))}


r0, dW0, _ = ring(0)
rng = np.random.default_rng(5); r1, dW1, _ = ring(1)          # same draws → same gates, rows, x, dy; quant changes only the read
r1["rows_ste_eq_float"] = rel(dW1, dW0) if np.any(dW0) else None
re = epi()
worst = max(v for d in (r0, r1, re) for k, v in d.items() if k in ("x", "gate_w", "gate_b", "rows_fd", "rows_ste_eq_float") and v is not None)
print(json.dumps({"ring_quant0": r0, "ring_quant1": r1, "epi": re, "worst_rel": worst, "pass": worst <= 1e-2}))

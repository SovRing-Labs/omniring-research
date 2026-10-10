"""T25-REACTOR plates fast kernel gate: plates=1 (one attention block per row) vs plates=2 (masked T×T reference) on a real pre-K batch,
harmony + HOLO on: same loss, gradient cosine, step and attention time.   python3 segfast_check.py [lib]"""
import ctypes, json, sys, time
import numpy as np
L = ctypes.CDLL(sys.argv[1] if len(sys.argv) > 1 else "<workspace>/projects/thead-trial/engine/omni_train/libomnitrain_trial_rx4.so")
P, I, F = ctypes.c_void_p, ctypes.c_int, ctypes.c_float; ip = ctypes.POINTER(ctypes.c_int)
for n, a, r in [("om_create", [I] * 5 + [ip, I, ctypes.c_ulonglong], P), ("om_threads", [I], None), ("om_set_p2", [P, I], None), ("om_set_lut5", [P, I], None),
                ("om_set_plates", [P, I, I], I), ("om_grad", [P, P, P, I, I], F), ("om_nparams", [P], I), ("om_param_size", [P, I], ctypes.c_long),
                ("om_param_grad", [P, I], ctypes.POINTER(F)), ("om_set_harmony", [P, I, F, F], None), ("om_set_mem", [P, I], None), ("om_prof", [P], None)]:
    f = getattr(L, n); f.argtypes = a; f.restype = r
L.om_threads(4); PR = (I * 32)(*[3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137])
h = L.om_create(8192, 256, 6, 4, 512, PR, 32, 1); L.om_set_p2(h, 1); L.om_set_lut5(h, 1); L.om_set_mem(h, 1); L.om_set_harmony(h, 1, 0.05, 0.9)
d = np.fromfile("<workspace>/projects/thead-trial/build-v4/tier1-prek-v3-s6100/phase_0.u16", dtype=np.uint16).astype(np.int32)
B, T = 4, 512; st = [0, 9000, 18000, 27000]
x = np.ascontiguousarray(np.concatenate([d[s:s + T] for s in st])); y = np.ascontiguousarray(np.concatenate([d[s + 1:s + T + 1] for s in st]))
def run(mode):
    L.om_set_plates(h, mode, 0); l = L.om_grad(h, x.ctypes.data, y.ctypes.data, B, T)
    g = np.concatenate([np.ctypeslib.as_array(L.om_param_grad(h, i), shape=(L.om_param_size(h, i),)).copy() for i in range(L.om_nparams(h))])
    pr = np.zeros(10); L.om_prof(pr.ctypes.data); ts = []
    for _ in range(3): t0 = time.time(); L.om_grad(h, x.ctypes.data, y.ctypes.data, B, T); ts.append(time.time() - t0)
    L.om_prof(pr.ctypes.data); return l, g, min(ts), (pr[1] + pr[5]) / 3
l2, g2, t2, a2 = run(2); l1, g1, t1, a1 = run(1)
cos = float(g1 @ g2 / (np.linalg.norm(g1) * np.linalg.norm(g2)))
print(json.dumps({"loss_masked": l2, "loss_fast": l1, "grad_cos": round(cos, 7), "step_s_masked": round(t2, 2), "step_s_fast": round(t1, 2),
                  "attn_s_masked": round(a2, 3), "attn_s_fast": round(a1, 3), "PASS": abs(l1 - l2) < 1e-4 and cos > 0.99999}))

"""P3 gate (T25-PRECOMPUTE P3, J 10-07 "5 approved"; plan <notes>/worker/claude/<plan> E5).
On a trained T25 school checkpoint, held-out windows with the plate channel:
  (1) P3 off: gradients dumped (run again with OMNI_TRAIN_LIB=<old lib> and compare → off == old lib, bit-identical);
  (2) P3 on, compacted == P3 on, mask-only (the same masked backward without compaction) within float tolerance;
  (3) dropped-row share and om_grad ms, off vs compacted.
python3 p3_check.py <run_dir> <out.npz> [p=0.95] [windows=4]"""
import ctypes, json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.expanduser("<home>/ai-stack/projects/thead-trial/harness"))
import route_decode_check as rc

L = rc.L; vp = ctypes.c_void_p; ip = np.ctypeslib.ndpointer(np.int32, flags="C_CONTIGUOUS")
L.om_grad.restype = ctypes.c_float; L.om_grad.argtypes = [vp, ip, ip, ctypes.c_int, ctypes.c_int]
L.om_param_grad.restype = ctypes.POINTER(ctypes.c_float); L.om_param_grad.argtypes = [vp, ctypes.c_int]
has_p3 = hasattr(L, "om_set_p3")
if has_p3:
    L.om_set_p3.argtypes = [vp, ctypes.c_float, ctypes.c_int, ctypes.c_int]; L.om_p3_stats.argtypes = [vp, np.ctypeslib.ndpointer(np.int64)]
R, OUT = sys.argv[1], sys.argv[2]; PTH = float(sys.argv[3]) if len(sys.argv) > 3 else 0.95; NW = int(sys.argv[4]) if len(sys.argv) > 4 else 4
L.om_threads(4); h, cfg = rc.load(R)
hb = os.path.normpath(os.path.join(rc.T0, "runtime", cfg["heldout"])); T, B = 512, 4
d = np.fromfile(f"{hb}/phase_2.u16", dtype=np.uint16).astype(np.int32); kd = np.fromfile(f"{hb}/kind_2.u8", dtype=np.uint8)
def batch(w):
    s0 = w * B * T; x = np.ascontiguousarray(d[s0:s0 + B * T]); y = np.ascontiguousarray(d[s0 + 1:s0 + B * T + 1])
    k = np.array([int(v) if v != 255 else -1 for v in kd[s0:s0 + B * T]], np.int32); pr = np.where(k >= 0, y, -1).astype(np.int32)
    return x, y, k, pr
def grads():
    return [np.ctypeslib.as_array(L.om_param_grad(h, i), shape=(L.om_param_size(h, i),)).copy() for i in range(L.om_nparams(h))]
def run(p, compact):
    if has_p3: L.om_set_p3(h, p, 1, compact)
    G, ms, loss = None, 0.0, 0.0
    for w in range(NW):
        x, y, k, pr = batch(w); L.om_set_port_data(h, k, pr, B * T)
        t = time.perf_counter(); loss += L.om_grad(h, x, y, B, T); ms += (time.perf_counter() - t) * 1e3
        g = grads(); G = g if G is None else [a + b for a, b in zip(G, g)]
    st = np.zeros(2, np.int64)
    if has_p3: L.om_p3_stats(h, st)
    return G, ms / NW, loss / NW, st
G0, ms0, l0, _ = run(0.0, 1)
np.savez(OUT, *G0)
rep = {"run": R, "lib": os.environ.get("OMNI_TRAIN_LIB", "default"), "has_p3": has_p3, "off_ms": round(ms0, 1), "loss": round(l0, 4)}
if has_p3:
    G1, ms1, l1, st = run(PTH, 1); G2, ms2, l2, _ = run(PTH, 0)
    md = max(float(np.max(np.abs(a - b))) for a, b in zip(G1, G2)); mx = max(float(np.max(np.abs(b))) for b in G2)
    rep.update({"p": PTH, "dropped_share": round(st[1] / max(st[0], 1), 3), "compact_ms": round(ms1, 1), "mask_only_ms": round(ms2, 1),
                "compact_vs_mask_max_abs": md, "grad_max_abs": mx, "compact_eq_mask": md <= 1e-4 * max(mx, 1e-12), "loss_equal": abs(l1 - l0) < 1e-6})
print(json.dumps(rep))

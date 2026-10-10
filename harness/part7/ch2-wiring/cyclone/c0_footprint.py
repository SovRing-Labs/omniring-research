#!/usr/bin/env python3
"""CYCLONE-ARRAY capacity probe — the memory ONE model's training state takes (what must live in VRAM per harness), measured on OUR CPU
engine: peak RSS of a fresh process before / after om_create + school switches + om_train_step at the school batch (B 4 × T 512,
D 256, L 6, H 4, V 8,192, port 31 plates, plates attention, local rule, depth routing, pointer, copy, harmony, P3). Each configuration runs
in its own process (VmHWM is per process). Run with one thread.   c0_footprint.py LIB [--out DIR]"""
import json, os, subprocess, sys
LIB = sys.argv[1]; OUT = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
CODE = r"""
import ctypes, json, sys, numpy as np
def hwm():
    for l in open('/proc/self/status'):
        if l.startswith('VmHWM'): return int(l.split()[1]) * 1024
def rss():
    for l in open('/proc/self/status'):
        if l.startswith('VmRSS'): return int(l.split()[1]) * 1024
L = ctypes.CDLL(sys.argv[1]); vp = ctypes.c_void_p; sw = sys.argv[2] == "school"
L.om_create.restype = vp; L.om_create.argtypes = [ctypes.c_int]*5 + [vp, ctypes.c_int, ctypes.c_ulonglong]
ip = np.ctypeslib.ndpointer(np.int32, flags='C_CONTIGUOUS')
L.om_train_step.restype = ctypes.c_float; L.om_train_step.argtypes = [vp, ip, ip, ctypes.c_int, ctypes.c_int, ctypes.c_float]
L.om_nparams.argtypes = [vp]; L.om_param_size.restype = ctypes.c_long; L.om_param_size.argtypes = [vp, ctypes.c_int]
L.om_threads(1)
V, D, NL, H, T, B = 8192, 256, 6, 4, 512, 4
PR = (ctypes.c_int * 32)(3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137)
r0 = rss()
h = L.om_create(V, D, NL, H, T, PR, (D // H) // 2, 1234)
if sw:
    L.om_set_port.argtypes = [vp, ctypes.c_int, ctypes.c_float]; L.om_set_port(h, 31, 1.0)
    L.om_set_plates.argtypes = [vp, ctypes.c_int, ctypes.c_int]; L.om_set_plates(h, 1, 0)
    L.om_set_local.argtypes = [vp, ctypes.c_int, ctypes.c_int]; L.om_set_local(h, 2, 4)
    L.om_set_route.argtypes = [vp, ctypes.c_float]; L.om_set_route(h, 0.9)
    L.om_set_pointer.argtypes = [vp, ctypes.c_int, ctypes.c_float]; L.om_set_pointer(h, 1, 5.0)
    L.om_set_copy.argtypes = [vp, ctypes.c_int, ctypes.c_float]; L.om_set_copy(h, 1, 6.0)
    L.om_set_harmony.argtypes = [vp, ctypes.c_int, ctypes.c_float, ctypes.c_float]; L.om_set_harmony(h, 1, 0.05, 0.9)
    L.om_set_p3.argtypes = [vp, ctypes.c_float, ctypes.c_int, ctypes.c_int]; L.om_set_p3(h, 0.95, 4, 1)
r1 = rss()
params = sum(L.om_param_size(h, i) for i in range(L.om_nparams(h)))
rg = np.random.default_rng(7); x = rg.integers(0, V, B * T).astype(np.int32); y = rg.integers(0, V, B * T).astype(np.int32)
for _ in range(2): loss = L.om_train_step(h, x, y, B, T, 1e-3)
print(json.dumps({"config": sys.argv[2], "params": params, "rss_lib_bytes": r0, "after_create_bytes": r1 - r0, "after_steps_rss_bytes": rss() - r0,
                  "peak_hwm_minus_start_bytes": hwm() - r0, "loss": float(loss)}))
"""
res = []
for cfg in ("base", "school"):
    p = subprocess.run([sys.executable, "-c", CODE, LIB, cfg], capture_output=True, text=True, timeout=900, env=dict(os.environ, OMP_NUM_THREADS="1"))
    if p.returncode: sys.exit(f"{cfg}: {p.stderr[-1200:]}")
    res.append(json.loads(p.stdout.strip().splitlines()[-1])); print(json.dumps(res[-1]), flush=True)
s = res[-1]; per = s["peak_hwm_minus_start_bytes"]
fit = {g: {"vram_gb": vram, "models_fit": int(vram * 0.9e9 // per)} for g, vram in (("RTX 3090 / 4090", 24), ("A40", 48), ("A100 80GB", 80), ("H100 80GB", 80))}
rep = {"probe": "CYCLONE-ARRAY per-model training footprint (CPU engine, school shapes)", "lib": LIB, "runs": res, "per_model_bytes": per,
       "per_model_gb": round(per / 1e9, 3), "layouts": {"1 floor (5 units x 8)": 40, "3 floors (15 units x 8)": 120},
       "need_gb": {"40": round(40 * per / 1e9, 1), "120": round(120 * per / 1e9, 1)}, "fit_at_90pct": fit}
print(json.dumps(rep))
if OUT: os.makedirs(OUT, exist_ok=True); json.dump(rep, open(f"{OUT}/footprint.json", "w"), indent=1)

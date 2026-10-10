"""Training throughput of OUR ternary trainer by model size (J 10-07: "see how long it would take to train a ~100m").
Fresh model through the same engine lib thead-learn uses, with the school's switches (P2 packing, memory, port 31 plates, local rule
stride 4, plates attention, P3), random tokens, B=4 × T=512 windows. Reports params, tok/s, and the time for a token budget.
python3 ternary_size_bench.py <D> <L> <H> [steps=8] [threads=8]     (run on the pod; numbers = this host only)"""
import ctypes, json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.expanduser("<home>/ai-stack/projects/thead-trial/harness"))
import route_decode_check as rc

L = rc.L; vp = ctypes.c_void_p
D, NL, H = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]); STEPS = int(sys.argv[4]) if len(sys.argv) > 4 else 8
TH = int(sys.argv[5]) if len(sys.argv) > 5 else 8
L.om_threads(TH)
h = L.om_create(rc.V, D, NL, H, 512, (ctypes.c_int * 32)(*rc.P), (D // H) // 2, 7)
L.om_set_p2(h, 1); L.om_set_mem(h, 1); assert L.om_set_port(h, 31, 1.0) > 0; L.om_set_port_tau(h, 0.05, 1)
assert L.om_set_local(h, 2, 4) == 0
L.om_set_plates.restype = ctypes.c_int; L.om_set_plates.argtypes = [vp, ctypes.c_int, ctypes.c_int]; L.om_set_plates(h, 1, 0)
if hasattr(L, "om_set_p3"):
    L.om_set_p3.argtypes = [vp, ctypes.c_float, ctypes.c_int, ctypes.c_int]; L.om_set_p3(h, 0.95, 4, 1)
n = sum(L.om_param_size(h, i) for i in range(L.om_nparams(h)))
B, T = 4, 512; R = np.random.default_rng(1)
kinds = np.full(B * T, -1, np.int32); props = np.full(B * T, -1, np.int32)
times = []
for s in range(STEPS):
    x = R.integers(0, rc.V, B * T).astype(np.int32); y = np.roll(x, -1).astype(np.int32)
    L.om_set_port_data(h, kinds, props, B * T)
    t = time.perf_counter(); L.om_train_step(h, x, y, B, T, 1e-3); times.append(time.perf_counter() - t)
st = float(np.median(times[2:] if len(times) > 3 else times)); tps = B * T / st
out = {"model": "ternary-decoder (ours)", "D": D, "L": NL, "H": H, "vocab": rc.V, "params": int(n), "threads": TH, "step_s": round(st, 3),
       "tok_per_s": round(tps), "hours_per_1B_tokens": round(1e9 / tps / 3600, 1), "hours_chinchilla_20x": round(20 * n / tps / 3600, 1),
       "host": open("/proc/cpuinfo").read().split("model name")[1].split("\n")[0].strip(": ")}
print(json.dumps(out))

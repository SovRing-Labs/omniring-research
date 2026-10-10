"""RAM-KIT-0 #9 A-GEM fixture: a small trunk (V 256, D 64, L 2, H 2, T 64, B 8) masters task A (next = 3t+1 mod 256), then trains task B
(next = 5t+7 mod 256 on the same tokens: a direct conflict). Arm GEM=0|1 (one per process, same seed): with GEM on, every B step first
takes the reference gradient on a fresh A batch (om_gem_ref) and the engine projects B's gradient when it would raise A's loss.
Reports task-A held-out loss before B, its max and its end over the B phase, and B's end loss. Usage: python3 ramkit_gem_fixture.py <lib> <0|1> [conflict|disjoint]"""
import ctypes
import json
import sys

import numpy as np

lib = ctypes.CDLL(sys.argv[1]); GEM = int(sys.argv[2]); MODE = sys.argv[3] if len(sys.argv) > 3 else "conflict"; P, I, F = ctypes.c_void_p, ctypes.c_int, ctypes.c_float
ipn = np.ctypeslib.ndpointer(np.int32, flags="C_CONTIGUOUS")
def fn(n, a, r=None): f = getattr(lib, n); f.argtypes = a; f.restype = r; return f
PR = np.array([3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137], np.int32)
V, D, L, H, T, B = 256, 64, 2, 2, 64, 8
fn("om_threads", [I])(4); h = fn("om_create", [I, I, I, I, I, ipn, I, ctypes.c_uint64], P)(V, D, L, H, T, PR, (D // H) // 2, 9)
fn("om_set_opt", [P, I, F, F, F, F, F, I, I])(h, 0, 0.0, 0.9, 0.95, 1.0, 1.0, 4, 0); fn("om_set_p2", [P, I])(h, 1)
step, fwd = fn("om_train_step", [P, ipn, ipn, I, I, F], F), fn("om_forward_loss", [P, ipn, ipn, I, I], F)
rng = np.random.default_rng(1)
def task(a, c, n=B, base=0, M=V):
    s = np.zeros((n, T + 1), np.int64); s[:, 0] = rng.integers(0, M, n)
    for t in range(T): s[:, t + 1] = (a * s[:, t] + c) % M
    s = (s + base).astype(np.int32); return np.ascontiguousarray(s[:, :-1].ravel()), np.ascontiguousarray(s[:, 1:].ravel())
if MODE == "disjoint":   # A on tokens 0..127, B on 128..255: forgetting only through the shared weights
    A = lambda n=B: task(3, 1, n, 0, 128); Bt = lambda n=B: task(5, 7, n, 128, 128)
else:                    # the same tokens, conflicting successors
    A = lambda n=B: task(3, 1, n); Bt = lambda n=B: task(5, 7, n)
held = A(32); heldB = Bt(32)
evalA = lambda: fwd(h, held[0], held[1], 32, T)
for i in range(150): x, y = A(); step(h, x, y, B, T, 3e-3)
a0 = evalA()
if GEM:
    fn("om_set_gem", [P, I])(h, GEM); gref = fn("om_gem_ref", [P, ipn, ipn, I, I], F)
traj = []
for i in range(60):
    if GEM: mx, my = A(); gref(h, mx, my, B, T)
    x, y = Bt(); step(h, x, y, B, T, 3e-3)
    if i % 5 == 4: traj.append(round(evalA(), 4))
st = np.zeros(9); fn("om_ramkit_stats", [P, np.ctypeslib.ndpointer(np.float64)])(h, st)
print(json.dumps({"gem": GEM, "mode": MODE, "taskA_before_B": round(a0, 4), "taskA_traj": traj, "taskA_max": max(traj), "taskA_end": traj[-1],
                  "taskA_rise": round(traj[-1] - a0, 4), "taskB_end": round(fwd(h, heldB[0], heldB[1], 32, T), 4), "gem_steps": st[7], "gem_projections": st[8]}))

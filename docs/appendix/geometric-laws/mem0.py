#!/usr/bin/env python3
"""MEM-0 (INTEGRATE-3D plan): processing-in-memory by layout, no new hardware. 1M marks, D 5120."""
import json, os, sys, time, mmap
import numpy as np
sys.path.insert(0, os.environ.get("OMNI_RING_PATH", "../omni-ring"))
from omni_ring import seed, DEFAULT_SPEC, generate_rotations  # noqa: E402
from omni_ring.chain import encode  # noqa: E402
from omni_ring.crt import direct_probe, solve_crt  # noqa: E402
from omni_ring.peel import read_all_kernel  # noqa: E402

OUT = os.path.expanduser("~/gpurun-out-0930/mem0.result.json"); D = seed.D; NMARK = int(os.environ.get("NMARK", 1_000_000))
TMP = "/tmp/mem0-lattice.npy"
res = {}
g = np.random.default_rng(0)
gold = np.stack([seed.codeword(f"golden-{i}", 0) for i in range(16)])

# ---- baseline: packed full scan (SCALE-1 form) ----
t = time.time()
pk = np.empty((NMARK, D // 2), dtype=np.uint8)
for a in range(0, NMARK, 50_000):
    pk[a:a + 50_000] = seed.pack4(g.integers(0, 16, (min(50_000, NMARK - a), D), dtype=np.uint8))
pk[:16] = seed.pack4(gold)
res["build_s"] = time.time() - t
seed.sift_batch_p4(gold[:1], pk)
ts = []
for i in range(8):
    t1 = time.time(); sc = seed.sift_batch_p4(gold[i][None, :], pk)[0]; ts.append(time.time() - t1); assert int(sc.argmax()) == i
res["SCAN_packed"] = {"ms": 1000 * float(np.median(ts)), "bytes": int(pk.nbytes), "bytes_per_mark": D // 2}
print("SCAN packed 1M:", res["SCAN_packed"], flush=True)

# ---- (C) prefix cascade: score first D/4 dims, rescore top-64 ----
ts = []; ok = 0
for i in range(8):
    t1 = time.time(); coarse = seed.sift_batch_p4(gold[i][None, :], pk, d_used=D // 4)[0]
    top = np.argsort(-coarse)[:64]; fine = seed.sift_rows_p4(gold[i], pk, top); ts.append(time.time() - t1); ok += int(int(top[int(fine.argmax())]) == i)
res["CASCADE_prefix"] = {"ms": 1000 * float(np.median(ts)), "bytes": int(NMARK * D // 8 + 64 * D // 2), "recall": ok / 8}
print("CASCADE prefix D/4:", res["CASCADE_prefix"], flush=True)

# ---- (D) mmap zero-copy load of a prebuilt lattice vs rebuild ----
np.save(TMP, pk); del pk
t1 = time.time(); m = np.load(TMP, mmap_mode="r"); first = int(m[0, 0]); t_map = time.time() - t1
t1 = time.time(); sc = seed.sift_batch_p4(gold[0][None, :], np.ascontiguousarray(m[:200_000]))[0]; t_cold = time.time() - t1
t1 = time.time(); sc = seed.sift_batch_p4(gold[0][None, :], np.ascontiguousarray(m[:200_000]))[0]; t_warm = time.time() - t1
res["MMAP"] = {"map_ms": 1000 * t_map, "rebuild_s": res["build_s"], "scan200k_cold_ms": 1000 * t_cold, "scan200k_warm_ms": 1000 * t_warm}
print("MMAP:", res["MMAP"], flush=True)
del m

# ---- (A) residue addressing: marks stored AT their CRT address; lookup = address arithmetic ----
spec = DEFAULT_SPEC; rot = generate_rotations(spec, seed=0); N = spec.data_capacity
from omni_ring.codebook import generate_direct_codebooks
dcb = generate_direct_codebooks(spec, seed=0); dcbc = [np.conj(c) for c in dcb]
store = np.zeros((N, 64), dtype=np.int8)                    # payload at address x (64 bytes each): the "mark" lives at its address
payload = g.integers(-127, 127, (N, 64), dtype=np.int8); store[:] = payload
def addr_lookup(x):                                        # encode (additive, bus form) -> 45 probes -> CRT -> address -> payload
    v = sum(cb[x % m] for cb, m in zip(dcb, spec.all_moduli)); ph = np.round(np.angle(v) * 16 / (2 * np.pi)).astype(int) % 16
    _, xd = direct_probe(np.exp(1j * ph * 2 * np.pi / 16), dcb, spec.all_moduli, dcbc); return xd, store[xd]
ts = []; ok = 0
for _ in range(200):
    x = int(g.integers(0, N)); t1 = time.time(); xd, p = addr_lookup(x); ts.append(time.time() - t1); ok += int(xd == x and np.array_equal(p, payload[x]))
res["ADDRESS_residue"] = {"us": 1e6 * float(np.median(ts)), "bytes_scanned": 0, "bytes_touched": 45 * D * 8 // 8 + 64, "recall": ok / 200, "note": "45 probes of 5,120 dims + one 64-B payload read; no scan"}
print("ADDRESS residue:", res["ADDRESS_residue"], flush=True)

# ---- (B) superposition: 1M marks as 7,813 slots x 128; which-slot (80 MB scan) + read the slot (128 marks per read) ----
K = 128; NS = NMARK // K; keys = np.exp(1j * g.uniform(0, 2 * np.pi, (NS, D))).astype(np.complex64)
code = np.stack([encode(x, rot) for x in range(N)]).astype(np.complex64)
members = np.stack([g.choice(N, K, replace=False) for _ in range(NS)])
slots = np.zeros((NS, 2, D), dtype=np.int8)
t = time.time()
for a in range(0, NS, 256):
    v = code[members[a:a + 256]].sum(1) * keys[a:a + 256]; s = np.maximum(np.abs(v.real).max(1), np.abs(v.imag).max(1))[:, None] / 127
    slots[a:a + 256, 0] = np.rint(v.real / s); slots[a:a + 256, 1] = np.rint(v.imag / s)
res["SUPER_build_s"] = time.time() - t
re_ = slots[:, 0].astype(np.float32); im_ = slots[:, 1].astype(np.float32)
ts = []; ok = 0
for _ in range(20):
    si = int(g.integers(0, NS)); x = int(members[si][g.integers(0, K)]); q = code[x] * keys[si]
    t1 = time.time(); sc = re_ @ q.real + im_ @ q.imag; ts.append(time.time() - t1); ok += int(int(sc.argmax()) == si)
which_ms = 1000 * float(np.median(ts))
si = 0; v = (slots[si, 0].astype(np.float32) + 1j * slots[si, 1].astype(np.float32)) * np.conj(keys[si])
t1 = time.time(); got = set(read_all_kernel(v, rot, max_marks=160)); t_read = time.time() - t1
res["SUPER_slots"] = {"which_slot_ms": which_ms, "which_recall": ok / 20, "slot_read_ms": 1000 * t_read, "marks_recovered": len(got & set(int(m) for m in members[si])),
                      "bytes_which_slot": int(slots.nbytes), "bytes_per_mark_equiv": int(slots.nbytes / NMARK), "ms_per_recovered_mark": 1000 * t_read / max(1, len(got))}
print("SUPER slots:", res["SUPER_slots"], flush=True)
base_b = res["SCAN_packed"]["bytes"]; base_ms = res["SCAN_packed"]["ms"]
res["verdict"] = {"A_bytes_div": base_b / max(1, res["ADDRESS_residue"]["bytes_touched"]), "A_ms_div": base_ms / (res["ADDRESS_residue"]["us"] / 1000),
                  "B_bytes_div": base_b / res["SUPER_slots"]["bytes_which_slot"], "B_ms_div": base_ms / res["SUPER_slots"]["which_slot_ms"],
                  "C_bytes_div": base_b / res["CASCADE_prefix"]["bytes"], "C_ms_div": base_ms / res["CASCADE_prefix"]["ms"]}
res["verdict"]["PASS"] = bool((res["verdict"]["A_bytes_div"] >= 100 and res["verdict"]["A_ms_div"] >= 10 and res["ADDRESS_residue"]["recall"] >= 0.999) or
                              (res["verdict"]["B_bytes_div"] >= 100 and res["verdict"]["B_ms_div"] >= 10 and res["SUPER_slots"]["which_recall"] >= 0.95))
json.dump(res, open(OUT, "w"), indent=1); print("MEM-0", res["verdict"])

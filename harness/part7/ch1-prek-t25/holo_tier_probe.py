"""HOLO transition plates decoded by ring systems of growing tier (J 10-07: "can we evolve our t5/t10 decode ring systems to our higher
dimension powered cores for better decoding?"). LAYER-0's mechanism unchanged (code = Σ ring codebook rows; key = snapped code ⊙ input;
plate = Σ key ⊙ code(next); read = plate ⊙ conj(key); decode = per-ring sift + soft RRNS vote over the 23,205 inner states), only the ring
system changes: T5 (3·5·7·13·17) · T10 (3…31) · T25 (3…101 — the T25 core's rings, residues exactly as the core emits them), codebooks
flat (random) vs simplex (the stack's bottom shape). Accuracy of recalling the next state, by transitions per plate T, D 1,024."""
import json, sys, time
import numpy as np
K = 16
T5 = (3, 5, 7, 13, 17); T10 = (3, 5, 7, 11, 13, 17, 19, 23, 29, 31)
T25 = (3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101)
INNER = 3 * 5 * 7 * 13 * 17; X = np.arange(INNER)
def phases(D, g, mods, shape):
    out = []
    for m in mods:
        if shape == "simplex":
            base = g.integers(0, K, D); rot = 1 + (np.arange(D) % (m - 1))
            out.append((base[None, :] + np.round(K * np.arange(m)[:, None] * rot[None, :] / m).astype(np.int64)) % K)
        else: out.append(g.integers(0, K, (m, D)))
    return [np.exp(1j * p * (2 * np.pi / K)).astype(np.complex64) for p in out]
def run(mods, shape, D, Ts, nread=150, seed=7):
    g = np.random.default_rng(seed); cb = phases(D, g, mods, shape); inp = np.exp(1j * g.integers(0, K, (16, D)) * (2 * np.pi / K)).astype(np.complex64)
    R = np.stack([X % m for m in mods], 1)
    code = lambda x: sum(c[x % m] for c, m in zip(cb, mods))
    def key(x, i): a = np.angle(code(x)); return (np.exp(1j * np.round(a * K / (2 * np.pi)) * (2 * np.pi / K)) * inp[i]).astype(np.complex64)
    res = {}
    for T in Ts:
        rng = np.random.default_rng(1000 + T); src = rng.integers(0, INNER, T); ii = rng.integers(0, 16, T); dst = rng.integers(0, INNER, T)
        plate = np.zeros(D, np.complex64)
        for s, i, d in zip(src, ii, dst): plate += key(int(s), int(i)) * code(int(d))
        ok = 0; sel = rng.choice(T, min(nread, T), replace=False)
        for j in sel:
            v = plate * np.conj(key(int(src[j]), int(ii[j])))
            sc = [(np.conj(c) @ v).real for c in cb]
            ok += int(np.argmax(sum(s[R[:, k]] for k, s in enumerate(sc)))) == dst[j]
        res[T] = round(ok / len(sel), 3)
    return res
D = int(sys.argv[1]) if len(sys.argv) > 1 else 1024; Ts = tuple(int(t) for t in sys.argv[2].split(",")) if len(sys.argv) > 2 else (144, 256, 512, 1024, 2048)
out = {}; t0 = time.time()
for name, mods in (("T5", T5), ("T10", T10), ("T25", T25)):
    for shape in ("flat", "simplex"):
        out[f"{name}_{shape}"] = run(mods, shape, D, Ts); print(name, shape, out[f"{name}_{shape}"], flush=True)
print(json.dumps({"D": D, "acc_by_T": out, "s": round(time.time() - t0)}))

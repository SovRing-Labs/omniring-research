# ENGINE-0 parity, condition-aware: for a sum of products the f32 error bound scales with Σ|a·b| (not |result|) — the standard
# float-GEMM check (Higham, "Accuracy and Stability of Numerical Algorithms", §3.1: |fl(x·y) − x·y| ≤ γ_n Σ|x_i y_i|, γ_n ≈ n·u).
# Same inputs as parity.py (seed 11); a row fails if any element's |engine − ours| > 2·n·u·Σ|a_k b_k| + 1e-6.
import random, subprocess, json
random.seed(11); U = 2.0**-24
def lst(n, s): return [round(random.uniform(-s, s), 6) for _ in range(n)]
def enc(v): return f"{len(v)} " + " ".join(map(str, v))
lines, meta = [], []
for i in range(20000):
    n = random.randint(1, 64); s = random.choice([1, 10, 100]); a, b = lst(n,s), lst(n,s); lines.append(f"dot8 {enc(a)} {enc(b)}"); meta.append(("dot8", a, b, None))
    n = random.randint(1, 64); x, g = lst(n,s), lst(n,2); lines.append(f"rms_row {enc(x)} {enc(g)}"); meta.append(("rms_row", x, g, None))
    M, N, K = random.randint(1, 12), random.randint(1, 12), random.randint(1, 24); A, B = lst(M*K,s), lst(K*N,s); lines.append(f"sgemm {enc(A)} {enc(B)} {M} {N} {K}"); meta.append(("sgemm", A, B, (M, N, K)))
inp = "\n".join(lines) + "\n"
eng = subprocess.run(["./driver"], input=inp, capture_output=True, text=True).stdout.splitlines()
our = subprocess.run(["./ours"], input=inp, capture_output=True, text=True).stdout.splitlines()
stat = {}
for (op, a, b, shp), e, o in zip(meta, eng, our):
    st = stat.setdefault(op, {"rows": 0, "bad": 0}); st["rows"] += 1
    ev = [float(x) for x in e.split()]; ov = [float(x) for x in o.split()]
    if op == "dot8": bounds = [2 * len(a) * U * sum(abs(p*q) for p, q in zip(a, b)) + 1e-6]
    elif op == "sgemm": M, N, K = shp; bounds = [2 * K * U * sum(abs(a[i*K+k] * b[k*N+j]) for k in range(K)) + 1e-6 for i in range(M) for j in range(N)]
    else: bounds = [1e-5 + 1e-4 * max(abs(p), abs(q)) for p, q in zip(ev, ov)]
    if len(ev) != len(ov) or any(abs(p - q) > bd for p, q, bd in zip(ev, ov, bounds)): st["bad"] += 1
print(json.dumps(stat)); open("parity2.json", "w").write(json.dumps(stat) + "\n")

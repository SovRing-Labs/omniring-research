# ENGINE-0 batch 2 parity vs an fp64 REFERENCE of the published math (RMSNorm backward; linear attention, Katharopoulos et al. 2020):
# per element, err_ours = |ours − ref64|, err_eng = |engine − ref64|; a row fails when err_ours > max(4·err_eng, 64·u·M) + 1e-6,
# M = magnitude (Σ|terms|) — "ours is at least as accurate as the engine". Fresh seed, 5,000 rows per op.
import random, subprocess, json, math
random.seed(23); U = 2.0**-24; EPS = 1.1920928955078125e-07
def lst(n, s): return [round(random.uniform(-s, s), 6) for _ in range(n)]
def enc(v): return f"{len(v)} " + " ".join(map(str, v))
def phi(x): return x + 1 if x > 0 else math.exp(x)
lines, refs = [], []
for i in range(5000):
    D = random.randint(1, 48); s = random.choice([1, 10, 100]); x, g, dy = lst(D, s), lst(D, 2), lst(D, s)
    ss = sum(v*v for v in x); r = 1 / math.sqrt(ss / D + EPS); sdot = sum(dy[j]*g[j]*x[j] for j in range(D)) / D
    dx = [r*dy[j]*g[j] - r**3 * x[j] * sdot for j in range(D)]; M = [abs(r*dy[j]*g[j]) + abs(r**3 * x[j]) * sum(abs(dy[k]*g[k]*x[k]) for k in range(D)) / D for j in range(D)]
    lines.append(f"rms_bwd_dx {enc(x)} {enc(g)} {enc(dy)}"); refs.append((dx, M))
    dg = [dy[j]*x[j]*r for j in range(D)]; lines.append(f"rms_bwd_dg {enc(x)} {enc(g)} {enc(dy)}"); refs.append((dg, [abs(v) for v in dg]))
    T, DH = random.randint(1, 8), random.randint(1, 8); q, k, v = lst(T*DH, 2), lst(T*DH, 2), lst(T*DH, s); bq = [random.randint(0, 2) for _ in range(T)]; bk = [random.randint(0, 2) for _ in range(T)]
    y, My = [], []
    for ii in range(T):
        a = [sum(phi(q[ii*DH+e]) * phi(k[j*DH+e]) for e in range(DH)) if bk[j] == bq[ii] else None for j in range(ii)]
        z = sum(x_ for x_ in a if x_ is not None); cnt = sum(1 for x_ in a if x_ is not None)
        for d in range(DH):
            num = sum(a[j] * v[j*DH+d] for j in range(ii) if a[j] is not None); mag = sum(a[j] * abs(v[j*DH+d]) for j in range(ii) if a[j] is not None)
            y.append(num / (z + 1e-6) if cnt else 0.0); My.append(mag / (z + 1e-6) if cnt else 0.0)
    lines.append(f"mem_fwd {enc(q)} {enc(k)} {enc(v)} {enc(bq)} {enc(bk)} {T} {DH}"); refs.append((y, My))
inp = "\n".join(lines) + "\n"
eng = subprocess.run(["./driver"], input=inp, capture_output=True, text=True).stdout.splitlines()
our = subprocess.run(["./ours2"], input=inp, capture_output=True, text=True).stdout.splitlines()
stat = {}
for l, (ref, M), e, o in zip(lines, refs, eng, our):
    op = l.split()[0]; st = stat.setdefault(op, {"rows": 0, "bad": 0, "ours_max_err": 0.0, "engine_max_err": 0.0}); st["rows"] += 1
    ev = [float(x) for x in e.split()]; ov = [float(x) for x in o.split()]
    if len(ev) != len(ref) or len(ov) != len(ref): st["bad"] += 1; continue
    for rr, m, a, b in zip(ref, M, ev, ov):
        ee, eo = abs(a - rr), abs(b - rr); st["ours_max_err"] = max(st["ours_max_err"], eo / (m + 1e-12)); st["engine_max_err"] = max(st["engine_max_err"], ee / (m + 1e-12))
        if eo > max(4 * ee, 64 * U * m) + 1e-6: st["bad"] += 1; break
print(json.dumps(stat)); open("parity3.json", "w").write(json.dumps(stat) + "\n")

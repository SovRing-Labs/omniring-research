# ENGINE-0 parity: the engine (driver, our C++ engine read-only) vs OUR clean-room Rust (emitted from name-free specs), same inputs.
import random, subprocess, math, sys, json
random.seed(11)
def lst(n, s): return [round(random.uniform(-s, s), 6) for _ in range(n)]
def enc(v): return f"{len(v)} " + " ".join(map(str, v))
lines = []
for i in range(20000):
    n = random.randint(1, 64); s = random.choice([1, 10, 100]); lines.append(f"dot8 {enc(lst(n,s))} {enc(lst(n,s))}")
    n = random.randint(1, 64); lines.append(f"rms_row {enc(lst(n,s))} {enc(lst(n,2))}")
    M, N, K = random.randint(1, 12), random.randint(1, 12), random.randint(1, 24); lines.append(f"sgemm {enc(lst(M*K,s))} {enc(lst(K*N,s))} {M} {N} {K}")
inp = "\n".join(lines) + "\n"
eng = subprocess.run(["./driver"], input=inp, capture_output=True, text=True).stdout.splitlines()
our = subprocess.run(["./ours"], input=inp, capture_output=True, text=True).stdout.splitlines()
def close(a, b): return abs(a - b) <= 1e-5 + 1e-4 * max(abs(a), abs(b))
stat = {}
for l, e, o in zip(lines, eng, our):
    op = l.split()[0]; st = stat.setdefault(op, {"rows": 0, "bad": 0, "max_rel": 0.0})
    ev = [float(x) for x in e.split()]; ov = [float(x) for x in o.split()]; st["rows"] += 1
    if len(ev) != len(ov) or not all(close(a, b) for a, b in zip(ev, ov)): st["bad"] += 1
    for a, b in zip(ev, ov):
        if max(abs(a), abs(b)) > 1e-3: st["max_rel"] = max(st["max_rel"], abs(a - b) / max(abs(a), abs(b)))
print(json.dumps(stat)); open("parity.json", "w").write(json.dumps(stat) + "\n")

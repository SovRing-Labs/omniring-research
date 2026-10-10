#!/usr/bin/env python3
"""math core M4 — dock generators for the math KB concepts (maker / solver with trace / INDEPENDENT verifier), levels 1–5.
DOCK engines, not THEAD faculties (VOCAB "the 26": the model's faculty list is the author's decision). Each verifier uses a different method from its
solver, so a row exists only when two methods agree (the reason-gen rule).

  mathgen.py gen CONCEPT --n N [--level L] [--seed S]     → JSON lines {concept, level, problem, answer, trace, verified}
  mathgen.py mutate [--n 200]                             → per concept: wrong answers made from right ones, every one must be refused
  mathgen.py list
"""
import argparse, json, math, random, sys

def _crt_solve(p):
    tr, x = [], 0
    for x in range(p["m1"] * p["m2"]):
        if x % p["m1"] == p["r1"] and x % p["m2"] == p["r2"]: tr.append(f"x={x}: {x}%{p['m1']}={p['r1']}, {x}%{p['m2']}={p['r2']}"); return x, tr
    return None, tr
def _crt_verify(p, a):  # by the definition + range (no search)
    return isinstance(a, int) and 0 <= a < p["m1"] * p["m2"] and a % p["m1"] == p["r1"] and a % p["m2"] == p["r2"]
def _crt_gen(R, L):
    hi = [6, 12, 30, 60, 120][L - 1]
    while True:
        m1, m2 = R.randint(2, hi), R.randint(2, hi)
        if math.gcd(m1, m2) == 1: return {"r1": R.randrange(m1), "m1": m1, "r2": R.randrange(m2), "m2": m2}

def _mr_solve(p): v = p["d0"] + p["m0"] * (p["d1"] + p["m1"] * p["d2"]); return v, [f"{p['d0']} + {p['m0']}·({p['d1']} + {p['m1']}·{p['d2']}) = {v}"]
def _mr_verify(p, a):   # divmod back to the digits
    return isinstance(a, int) and a >= 0 and (a % p["m0"], a // p["m0"] % p["m1"], a // p["m0"] // p["m1"]) == (p["d0"], p["d1"], p["d2"])
def _mr_gen(R, L):
    hi = [5, 10, 30, 100, 1000][L - 1]; m0, m1 = R.randint(2, hi), R.randint(2, hi)
    return {"d0": R.randrange(m0), "d1": R.randrange(m1), "d2": R.randint(0, hi * 10), "m0": m0, "m1": m1}

def _br_solve(p):
    a, m = p["a"], p["m"]; mu = 2 ** 32 // m; q = (a * mu) >> 32; r = a - q * m; tr = [f"mu={mu}", f"q={q}", f"r={r}"]
    while r >= m: r -= m; tr.append(f"r-=m → {r}")
    return r, tr
def _br_verify(p, a):   # Python's % (a different method)
    return isinstance(a, int) and a == p["a"] % p["m"]
def _br_gen(R, L): m = R.randint(2, [50, 500, 5000, 30000, 65535][L - 1]); return {"a": R.randrange(m * m), "m": m}

def _hm_solve(p): x = p["a"] ^ p["b"]; c = bin(x).count("1"); return c, [f"a^b={x:b}", f"popcount={c}"]
def _hm_verify(p, a):   # position by position over the binary strings
    n = max(p["a"].bit_length(), p["b"].bit_length(), 1); sa, sb = format(p["a"], f"0{n}b"), format(p["b"], f"0{n}b")
    return isinstance(a, int) and a == sum(1 for u, v in zip(sa, sb) if u != v)
def _hm_gen(R, L): b = [4, 8, 16, 31, 62][L - 1]; return {"a": R.getrandbits(b), "b": R.getrandbits(b)}

def _is_solve(p):
    n, x, tr = p["n"], p["n"], []
    while x * x > n: x = (x + n // x) // 2; tr.append(f"x={x}")
    return x, tr
def _is_verify(p, a): return isinstance(a, int) and a >= 0 and a * a <= p["n"] < (a + 1) * (a + 1)   # the bracket
def _is_gen(R, L): return {"n": R.randint(0, [100, 10 ** 4, 10 ** 6, 10 ** 12, 2 ** 62][L - 1])}

def _pe_solve(p):
    v = p["v"]
    for q in range(1, len(v) + 1):
        if all(v[i] == v[i + q] for i in range(len(v) - q)): return q, [f"p={q} reproduces"]
def _pe_verify(p, a):   # reproduces AND no smaller q does (checked with v[i] == v[i mod q])
    v = p["v"]; ok = lambda q: all(v[i] == v[i % q] for i in range(len(v)))
    return isinstance(a, int) and 1 <= a <= len(v) and ok(a) and not any(ok(q) for q in range(1, a))
def _pe_gen(R, L):
    base = [R.randint(0, [1, 2, 3, 4, 9][L - 1]) for _ in range(R.randint(1, L + 2))]; n = R.randint(1, 6 * L + 4)
    return {"v": [base[i % len(base)] for i in range(n)]}

def _q_solve(p):
    w = p["w"]; s = max(sum(abs(x) for x in w) / len(w), 1e-5); q = [min(1, max(-1, round(x / s))) for x in w]; return q, [f"s={s:.6g}"]
def _q_verify(p, a):    # element-wise: the thresholds |x| ≥ s/2 (round half even at exactly s/2 accepted either way)
    w = p["w"]; s = max(sum(map(abs, w)) / len(w), 1e-5)
    if not (isinstance(a, list) and len(a) == len(w)): return False
    for q, x in zip(a, w):
        t = abs(x) / s
        if t > 0.5 + 1e-12 and q != (1 if x > 0 else -1): return False
        if t < 0.5 - 1e-12 and q != 0: return False
    return True
def _q_gen(R, L): n = R.randint(1, [4, 8, 16, 64, 256][L - 1]); return {"w": [round(R.uniform(-3, 3), 6) for _ in range(n)]}

def _sm_solve(p):
    x = p["x"]; m = max(x); e = [math.exp(v - m) for v in x]; z = sum(e); return [v / z for v in e], [f"max={m}", f"z={z:.6g}"]
def _sm_verify(p, a):   # sums to 1 and the defining ratios p_i / p_0 = exp(x_i − x_0) (no max-shift used)
    x = p["x"]
    if not (isinstance(a, list) and len(a) == len(x) and all(isinstance(v, float) and v >= 0 for v in a)): return False
    if abs(sum(a) - 1) > 1e-9: return False
    j = max(range(len(x)), key=lambda i: a[i])
    return all(abs(a[i] - a[j] * math.exp(x[i] - x[j])) <= 1e-9 for i in range(len(x)))
def _sm_gen(R, L): return {"x": [round(R.uniform(-[2, 10, 50, 200, 700][L - 1], [2, 10, 50, 200, 700][L - 1]), 4) for _ in range(R.randint(1, 4 * L))]}

def _fb_solve(p):
    a, b = 0, 1
    for _ in range(p["n"]): a, b = b, a + b
    return a, [f"F({p['n']})={a}"]
def _fb_verify(p, a):   # fast doubling (a different algorithm)
    def fd(n):
        if n == 0: return 0, 1
        u, v = fd(n // 2); c = u * (2 * v - u); d = u * u + v * v
        return (d, c + d) if n % 2 else (c, d)
    return isinstance(a, int) and a == fd(p["n"])[0]
def _fb_gen(R, L): return {"n": R.randint(0, [10, 30, 90, 300, 1000][L - 1])}

def _ck_solve(p):
    for t in range(105):
        if t % 3 == p["r3"] and t % 5 == p["r5"] and t % 7 == p["r7"]: return t, [f"t={t}"]
def _ck_verify(p, a): return isinstance(a, int) and 0 <= a < 105 and (a % 3, a % 5, a % 7) == (p["r3"], p["r5"], p["r7"])
def _ck_gen(R, L): t = R.randrange(105); return {"r3": t % 3, "r5": t % 5, "r7": t % 7}

GENS = {"crt2": (_crt_gen, _crt_solve, _crt_verify), "mixed_radix": (_mr_gen, _mr_solve, _mr_verify), "mod_barrett": (_br_gen, _br_solve, _br_verify),
        "hamming": (_hm_gen, _hm_solve, _hm_verify), "isqrt": (_is_gen, _is_solve, _is_verify), "period": (_pe_gen, _pe_solve, _pe_verify),
        "absmean_quant": (_q_gen, _q_solve, _q_verify), "softmax": (_sm_gen, _sm_solve, _sm_verify), "fib": (_fb_gen, _fb_solve, _fb_verify),
        "clock_read": (_ck_gen, _ck_solve, _ck_verify)}

def wrongs(ans, R):
    """wrong answers made from a right one: off by one, doubled, negated, an element changed / dropped"""
    if isinstance(ans, list):
        out = []
        if ans: b = list(ans); i = R.randrange(len(b)); b[i] = (b[i] + 1) if isinstance(b[i], int) else b[i] * 1.5 + 0.01; out.append(b)
        if len(ans) > 1: out.append(ans[:-1])
        return out
    return [ans + 1, ans - 1, ans * 2 + 1, -ans - 1]

def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    g = sp.add_parser("gen"); g.add_argument("concept"); g.add_argument("--n", type=int, default=10); g.add_argument("--level", type=int, default=3); g.add_argument("--seed", type=int, default=0)
    m = sp.add_parser("mutate"); m.add_argument("--n", type=int, default=200)
    sp.add_parser("list")
    a = ap.parse_args()
    if a.cmd == "list": print("\n".join(GENS)); return
    if a.cmd == "gen":
        mk, sv, vf = GENS[a.concept]; R = random.Random(a.seed)
        for _ in range(a.n):
            p = mk(R, a.level); ans, tr = sv(p); print(json.dumps({"concept": a.concept, "level": a.level, "problem": p, "answer": ans, "trace": tr, "verified": vf(p, ans)}))
        return
    bad = 0
    for c, (mk, sv, vf) in GENS.items():
        R = random.Random(7); ok_right = tried = refused = 0
        for i in range(a.n):
            p = mk(R, 1 + i % 5); ans, _ = sv(p); ok_right += vf(p, ans)
            for w in wrongs(ans, R):
                if w == ans: continue
                tried += 1; refused += not vf(p, w)
        print(json.dumps({"concept": c, "right_accepted": f"{ok_right}/{a.n}", "wrong_refused": f"{refused}/{tried}"}))
        bad += ok_right != a.n or refused != tried
    sys.exit(1 if bad else 0)

if __name__ == "__main__": main()

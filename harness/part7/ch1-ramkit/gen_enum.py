#!/usr/bin/env python3
"""ramkit #15 — generator state-space enumeration + coverage (RAM-KIT-0, J 10-08; VOCAB "the 26").
For each reason-gen domain whose problem space at a level is a product of small ranges, an exact bijection rank ↔ problem over the WHOLE
space (unrank(i) for i in range(size) = the enumeration; slots a generator can never produce, e.g. a smudged digit on a 2-digit number,
unrank to None and are not counted). Coverage = distinct problems the given builds' rows contain / valid problems at that level. Rows are regenerated exactly from the build sidecar (gen_row, gen_seed, gen_level,
base_domain) through the generator only (no solver). Seen problems are held as a set of ranks (RAM ∝ rows, not space);
a dense bitmap (1 bit per slot, CAP = 10^9 slots = 125 MB) is the option when rows approach the space size.

  gen_enum.py space                         → per domain × level: size or the reason it is not enumerable
  gen_enum.py coverage <build …> [--out F]  → per domain × level: rows, distinct, valid space, coverage
  gen_enum.py selftest"""
import argparse, json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

CAP = 1_000_000_000
RINGS = (3, 5, 7, 13, 17); MR = 3 * 5 * 7 * 13 * 17
DIRS = "ULDR"


def _mixed(res, ms):
    i, b = 0, 1
    for r, m in zip(res, ms): i += r * b; b *= m
    return i


def _unmixed(i, ms):
    out = []
    for m in ms: out.append(i % m); i //= m
    return out


class Mul:                                       # gen_mul: nd = 1 + level digits each; plain or one smudged digit k < nd-1
    def __init__(s, L): s.nd = 1 + L; s.lo = 10 ** (s.nd - 1); s.D = 9 * s.lo; s.size = s.D * s.D * s.nd; s.valid = s.size
    def rank(s, p): return ((p["a"] - s.lo) * s.D + (p["b"] - s.lo)) * s.nd + (p["smudged"] + 1 if "smudged" in p else 0)
    def unrank(s, i):
        t, j = divmod(i, s.nd); a, b = divmod(t, s.D); p = {"a": a + s.lo, "b": b + s.lo}
        if j: p["smudged"] = j - 1
        return p


class Mrc:                                       # gen_mrc: x (maybe one residue unreadable) × y, residues on 3·5·7·13·17
    def __init__(s, L):
        s.xoff = [MR]
        for i, m in enumerate(RINGS): s.xoff.append(s.xoff[-1] + MR // m)
        s.nx = s.xoff[-1]; s.size = s.nx * MR; s.valid = s.size
    def _rx(s, x):
        if None not in x: return _mixed(x, RINGS)
        i = x.index(None); ms = [m for j, m in enumerate(RINGS) if j != i]
        return s.xoff[i] + _mixed([r for j, r in enumerate(x) if j != i], ms)
    def rank(s, p): return s._rx(p["x"]) * MR + _mixed(p["y"], RINGS)
    def unrank(s, i):
        ix, iy = divmod(i, MR); y = _unmixed(iy, RINGS)
        if ix < MR: return {"x": _unmixed(ix, RINGS), "y": y}
        k = max(j for j in range(5) if s.xoff[j] <= ix); ms = [m for j, m in enumerate(RINGS) if j != k]
        x = _unmixed(ix - s.xoff[k], ms); x.insert(k, None)
        return {"x": x, "y": y}


class Cal:                                       # gen_calendar: p, q ∈ [2, 4+3L], a, b ∈ [0,14), b may be unrecorded (None)
    def __init__(s, L): s.P = 3 + 3 * L; s.size = s.P * s.P * 14 * 15; s.valid = s.size
    def rank(s, p): return (((p["p"] - 2) * s.P + p["q"] - 2) * 14 + p["a"]) * 15 + (14 if p["b"] is None else p["b"])
    def unrank(s, i):
        i, b = divmod(i, 15); i, a = divmod(i, 14); pp, q = divmod(i, s.P)
        return {"p": pp + 2, "a": a, "q": q + 2, "b": None if b == 14 else b}


class CalRing:                                   # gen_calendar_ring: (p, q) = an ordered pair of distinct clock rings, a, b ∈ [0,14), b may be None
    def __init__(s, L):
        s.CL = list(C.rg().CLOCK); s.pairs = [(p, q) for p in s.CL for q in s.CL if p != q]; s.pi = {pq: i for i, pq in enumerate(s.pairs)}
        s.size = len(s.pairs) * 14 * 15; s.valid = s.size
    def rank(s, p): return (s.pi[(p["p"], p["q"])] * 14 + p["a"]) * 15 + (14 if p["b"] is None else p["b"])
    def unrank(s, i):
        i, b = divmod(i, 15); k, a = divmod(i, 14); pp, q = s.pairs[k]
        return {"p": pp, "a": a, "q": q, "b": None if b == 14 else b}


class Prime:                                     # gen_prime: n in the level's range (prime search may step past hi), maybe one smudged digit (n ≥ 100)
    R = {1: (40, 1369), 2: (1369, 10 ** 5), 3: (10 ** 5, 10 ** 7)}
    def __init__(s, L, small=False):
        L = min(L, 3) if small else L
        if L not in s.R: raise ValueError("range too large")
        s.lo, hi = s.R[L]; s.hi = hi + 2000; s.dm = len(str(s.hi - 1)); s.size = (s.hi - s.lo) * s.dm
        s.valid = 0
        for d in range(len(str(s.lo)), s.dm + 1):                       # 1 plain + (d-1) smudged per n with d digits (n ≥ 100)
            a, b = max(s.lo, 10 ** (d - 1)), min(s.hi, 10 ** d)
            if a < b: s.valid += (b - a) * (1 + ((d - 1) if d >= 3 else 0))
    def rank(s, p): return (p["n"] - s.lo) * s.dm + (p["smudged"] + 1 if p.get("smudged") is not None else 0)
    def unrank(s, i):
        t, j = divmod(i, s.dm); n = t + s.lo
        if j == 0: return {"n": n}
        if n < 100 or j - 1 >= len(str(n)) - 1: return None
        return {"n": n, "smudged": j - 1}


class Group:                                     # gen_group: start ∈ 24 stations × route ∈ ULDR^(2+2L), maybe one move unreadable ('?')
    def __init__(s, L):
        s.S = sorted(C.rg().G2T_BY_NAME); s.si = {x: i for i, x in enumerate(s.S)}; s.n = 2 + 2 * L
        s.per = 4 ** s.n + s.n * 4 ** (s.n - 1); s.size = len(s.S) * s.per; s.valid = s.size
    def rank(s, p):
        w = p["word"]; base = s.si[p["start"]] * s.per
        if "?" not in w: return base + _mixed([DIRS.index(c) for c in w], [4] * s.n)
        k = w.index("?"); rest = [DIRS.index(c) for c in w if c != "?"]
        return base + 4 ** s.n + k * 4 ** (s.n - 1) + _mixed(rest, [4] * (s.n - 1))
    def unrank(s, i):
        st, r = divmod(i, s.per)
        if r < 4 ** s.n: return {"start": s.S[st], "word": "".join(DIRS[d] for d in _unmixed(r, [4] * s.n))}
        k, r = divmod(r - 4 ** s.n, 4 ** (s.n - 1)); w = [DIRS[d] for d in _unmixed(r, [4] * (s.n - 1))]; w.insert(k, "?")
        return {"start": s.S[st], "word": "".join(w)}


SPACES = {"arith.mul": Mul, "arith.mul_rns": Mul, "arith.mrc_compare": Mrc, "arith.mrc_plate": Mrc, "calendar.crt": Cal,
          "calendar.ring_euclid": CalRing, "calendar.clock": CalRing, "numth.prime": Prime,
          "numth.prime_trial": lambda L: Prime(L, small=True), "graph.group": Group, "graph.group_walk": Group}
INFEASIBLE = {
    "logic.chain": "rules over 6+2L atoms sampled from ATOMS with random distractor rules + shuffle: permutations of the atom list alone exceed 10^12",
    "graph.path": "a random relation graph: hops+4+L people × 3 random relations each pointing at any person → > 10^15 graphs at L1",
    "sat.dpll": "3+L vars, round(4.2n) random 3-literal clauses (ordered list): ~10^30 formulas at L1",
    "sat.trit": "same formulas as sat.dpll (trit rendering): ~10^30 at L1",
    "mind.revise": "random formula sets + evidence sequences over atoms: unbounded nesting, no small product space",
    "struct.pushdown": "random nested JSON-like documents (j_value recursion) — tree count explodes with depth",
    "units.dimension": "1–2 terms of 1–3 quantities from QTY + level-scaled numbers: real-valued magnitudes, not a finite small space",
    "code.debug": "programs with injected bugs + random test cases from a code catalogue: space is the bug × case product, not enumerable cheaply",
    "science.bioreactor": "real-valued simulated world (noise, factors, temperature) — continuous parameters",
    "science.factorial": "same continuous bioreactor world as science.bioreactor",
    "mind.tom": "agents × objects × move sequences of random length — > 10^9 stories at L1",
    "mind.tom_mask": "same stories as mind.tom",
    "search.astar": "random grids with walls (2^cells layouts) — > 10^20 at L1",
    "search.wave": "same grids as search.astar",
    "causal.dag": "random DAGs + coefficient draws (real-valued) — continuous",
    "numth.prime@4-5": "n up to 10^10 / 10^12 — 10^10+ slots, past the 10^9-bit cap",
    "graph.group@5": "24 · (4^12 + 12·4^11) = 1.6·10^9 slots, past the 10^9-bit cap"}


def space(domain, L):
    f = SPACES.get(domain)
    if f is None: return None, INFEASIBLE.get(domain, "no enumerator")
    try: S = f(L)
    except ValueError as e: return None, INFEASIBLE.get(f"{domain}@4-5", str(e))
    if S.size > CAP: return None, f"{S.size:.3g} slots > cap {CAP:.0e}"
    return S, None


def coverage(builds):
    RG = C.rg(); bits, rows, seen, skipped = {}, {}, {}, []
    spaces = {}
    for b in builds:
        man = json.load(open(os.path.join(b, "manifest.json")))
        if not C.build_is_generator(man): skipped.append(os.path.basename(b)); continue
        doms = man["port"]["domains"]
        for k, R, _ in C.build_rows(b):
            for r in R:
                d, i, sd, lv = doms[int(r[11])], int(r[8]), int(r[9]), int(r[10])
                key = (d, lv); rows[key] = rows.get(key, 0) + 1
                if key not in spaces: spaces[key] = space(d, lv)
                S, why = spaces[key]
                if S is None: continue
                _, p, _ = C.regen_problem(d, i, sd, lv)
                bits.setdefault(key, set()).add(S.rank(p)); seen[key] = seen.get(key, 0) + 1
    out = {}
    for (d, lv), n in sorted(rows.items()):
        S, why = spaces[(d, lv)]
        if S is None: out[f"{d}@{lv}"] = {"rows": n, "enumerable": False, "why": why}; continue
        dist = len(bits.get((d, lv), ()))
        out[f"{d}@{lv}"] = {"rows": n, "distinct": dist, "valid_space": S.valid, "coverage": dist / S.valid, "repeat_rows": n - dist}
    return {"builds": [os.path.basename(b) for b in builds], "skipped_tier1": skipped, "by_domain_level": out}


def selftest(out=None):
    RG = C.rg(); res = {"bijection": {}, "generator_support": {}, "infeasible": sorted(INFEASIBLE)}; ok = True; t0 = time.time()
    for d in sorted(SPACES):
        for L in range(1, 6):
            S, why = space(d, L)
            if S is None: res["bijection"][f"{d}@{L}"] = f"not enumerable: {why}"; continue
            n_check = min(S.size, 200_000); step = max(1, S.size // n_check); good = valid = 0
            for i in range(0, S.size, step):                                    # enumeration: unrank every (sampled) slot, rank it back
                p = S.unrank(i)
                if p is None: continue
                valid += 1; good += S.rank(p) == i
            if S.size <= 200_000 and valid != S.valid: ok = False
            sup = 0; R = 1500
            for i in range(R):                                                  # every generator output lies in the space, rank ↔ unrank exact
                gen = RG.fns_of(d)[0]; p, _ = gen(RG.rng_for(d, i, 77), L); x = S.rank(p)
                sup += 0 <= x < S.size and C.canon(S.unrank(x)) == C.canon(p)
            ok &= good == valid and sup == R
            res["bijection"][f"{d}@{L}"] = {"size": S.size, "valid": S.valid, "checked": valid, "round_trip": good, "exhaustive": step == 1}
            res["generator_support"][f"{d}@{L}"] = f"{sup}/{R}"
    bd = os.path.join(C.TRIAL, "build-v4")
    bs = [os.path.join(bd, b) for b in ("seed-v4-short", "seed-v4-short-heldout", "seed-v4-doing-bank", "live-r1-s1000") if os.path.isdir(os.path.join(bd, b))]
    if bs:
        cv = coverage(bs)
        res["coverage_real"] = {"builds": cv["builds"], "skipped_tier1": cv["skipped_tier1"],
                                "enumerable": {k: {kk: (round(vv, 6) if isinstance(vv, float) else vv) for kk, vv in v.items()}
                                               for k, v in cv["by_domain_level"].items() if v.get("enumerable", True)},
                                "not_enumerable_rows": sum(v["rows"] for v in cv["by_domain_level"].values() if not v.get("enumerable", True))}
    res["s"] = round(time.time() - t0, 1); res["rss_mb"] = C.rss_mb()
    if out: C.json_out(res, out)
    return ok, res


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="c", required=True)
    sp.add_parser("space")
    c = sp.add_parser("coverage"); c.add_argument("builds", nargs="+"); c.add_argument("--out")
    s = sp.add_parser("selftest"); s.add_argument("--out")
    a = ap.parse_args()
    if a.c == "space":
        r = {}
        for d in C.GENS26:
            for L in range(1, 6):
                S, why = space(d, L); r[f"{d}@{L}"] = {"size": S.size, "valid": S.valid} if S else why
        print(json.dumps(r, indent=1))
    elif a.c == "coverage":
        r = coverage(a.builds); print(C.json_out(r, a.out) if a.out else json.dumps(r))
    else:
        ok, res = selftest(a.out); print(json.dumps(res)); print("PASS" if ok else "FAIL", "gen_enum"); sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

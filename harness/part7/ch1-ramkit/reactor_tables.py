#!/usr/bin/env python3
"""ramkit #10 — reactor precompute tables (RAM-KIT-0, J 10-08; VOCAB "center ring": the reactor PRE-CALCULATES what the other side needs).
EVAL (harness/reactor_twin.py eval_term): a prefix term over the 32-operand ring, ADD SUB MUL MIN MAX (Int,Int→Int) · NEG (Int→Int) ·
EQ LT (Int,Int→Bool), arithmetic mod 32. Tables (file RTAB1, mmap-able):
  OP   [8][32][32] u8      every operator on every operand pair (NEG uses row b=0) — EVAL of ANY depth = O(len) table reads, no arithmetic
  V1   [5184] u8           value of every depth-≤1 Int term: index v (operand) · 32+v (NEG v) · 64 + j·1024 + a·32 + b (ADD..MAX)
  T2   [7][5184][5184] u8  every depth-2 term with a binary top (ADD SUB MUL MIN MAX EQ LT) over depth-≤1 Int children = 188,116,992 B
  N2   [5184] u8           NEG over depth-≤1 children
Result byte: 0..31 Int · 32 True · 33 False (malformed is decided by the parser: None). Depth is capped at 2 by RAM: depth-3 terms number
~10^17. Deeper terms resolve through OP (exact). Residue-clock schedule (runtime/src/arc.rs ResidueClock, M = 3…53, κ = ±1): per clock value c
in one phase period lcm(3,17,53) = 2703 — phase flags (token c%3, beat c%17, epoch c%53), ticks to the next token / beat / epoch phase. Ring
residues are (κ·c) mod m from c itself — the 15 rings' joint period (Π M ≈ 6·10^17) cannot be tabled; clock() returns them alongside.

  reactor_tables.py build <out.rtab>              (~190 MB file; build RAM ~250 MB)
  reactor_tables.py eval  <tab> <tok tok …>        → ("int", v) | ("bool", b) | None, same as reactor_twin.eval_term
  reactor_tables.py selftest [--n 100000] [--tab FILE]
API: T = Tables(path); T.eval(term_tokens, A) ; T.clock(c, kappa) → dict"""
import argparse, json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
sys.path.insert(0, os.path.join(C.TRIAL, "harness"))

MAGIC = b"RTAB1\0\0\0"
N = 32; OPS = ("ADD", "SUB", "MUL", "MIN", "MAX", "NEG", "EQ", "LT"); BIN7 = ("ADD", "SUB", "MUL", "MIN", "MAX", "EQ", "LT")
TRUE, FALSE = 32, 33; N1 = 64 + 5 * 1024
M15 = (3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53); PERIOD = 3 * 17 * 53


def _f(name, a, b):
    if name == "ADD": return (a + b) % N
    if name == "SUB": return (a - b) % N
    if name == "MUL": return (a * b) % N
    if name == "MIN": return np.minimum(a, b)
    if name == "MAX": return np.maximum(a, b)
    if name == "NEG": return (-a) % N
    if name == "EQ": return np.where(a == b, TRUE, FALSE)
    if name == "LT": return np.where(a < b, TRUE, FALSE)


def schedule():
    c = np.arange(PERIOD)
    flags = ((c % 3 == 0) * 1 + (c % 17 == 0) * 2 + (c % 53 == 0) * 4).astype(np.uint8)
    nxt = np.stack([(-c) % 3, (-c) % 17, (-c) % 53], 1).astype(np.uint8)        # ticks until the clock is next on that phase
    return flags, nxt


def build(out):
    a = np.arange(N, dtype=np.int32)
    OP = np.zeros((8, N, N), np.uint8)
    for j, nm in enumerate(OPS): OP[j] = _f(nm, a[:, None], np.zeros((1, N), np.int32) if nm == "NEG" else a[None, :])
    V1 = np.zeros(N1, np.uint8); V1[:N] = a; V1[N:2 * N] = (-a) % N
    for j in range(5): V1[64 + j * 1024:64 + (j + 1) * 1024] = OP[j].reshape(-1)
    N2 = ((-V1.astype(np.int32)) % N).astype(np.uint8)
    flags, nxt = schedule()
    v = V1.astype(np.int16)
    with open(out + ".tmp", "wb") as f:
        f.write(MAGIC); f.write(np.array([N, N1, PERIOD], np.uint64).tobytes())
        f.write(OP.tobytes()); f.write(V1.tobytes()); f.write(N2.tobytes())
        f.write(flags.tobytes()); f.write(nxt.tobytes())
        for nm in BIN7:
            for i0 in range(0, N1, 1296):                                         # 1296 rows at a time: ~13 MB per slab
                f.write(_f(nm, v[i0:i0 + 1296, None], v[None, :]).astype(np.uint8).tobytes())
    os.replace(out + ".tmp", out)
    return os.path.getsize(out)


class Tables:
    def __init__(self, path):
        mm = np.memmap(path, dtype=np.uint8, mode="r")
        assert bytes(mm[:8]) == MAGIC, f"{path}: not RTAB1"
        n, n1, per = (int(x) for x in np.frombuffer(bytes(mm[8:32]), np.uint64)); o = 32
        def take(shape):
            nonlocal o
            k = int(np.prod(shape)); a = mm[o:o + k].reshape(shape); o += k; return a
        self.OP = np.array(take((8, n, n))); self.V1 = np.array(take((n1,))); self.N2 = np.array(take((n1,)))
        self.flags = np.array(take((per,))); self.nxt = np.array(take((per, 3)))
        self.T2 = take((7, n1, n1))                                               # stays memory-mapped (188 MB)
        self.n1 = n1

    def _parse(self, A, term):
        """prefix term → tree: int leaf v | (opname, [children]) ; None if malformed (reactor_twin.eval_term's rules)"""
        def go(i):
            if i >= len(term): return None, i
            t = term[i]
            if t in A.op_index: return A.op_index[t], i + 1
            if t not in A.oper: return None, i + 1
            name, ar = A.oper[t]; kids = []; j = i + 1
            for _ in range(ar):
                k, j = go(j)
                if k is None or (isinstance(k, tuple) and k[0] in ("EQ", "LT")): return None, j   # a Bool where an Int goes
                kids.append(k)
            return (name, kids), j
        if not term: return None
        tr, i = go(0)
        return tr if tr is not None and i == len(term) else None

    def _idx1(self, t):
        """index of a depth-≤1 Int tree in V1, else None"""
        if isinstance(t, int): return t
        nm, k = t
        if not all(isinstance(x, int) for x in k): return None
        if nm == "NEG": return N + k[0]
        return 64 + OPS.index(nm) * 1024 + k[0] * N + k[1]

    def _val(self, t):
        if isinstance(t, int): return t
        nm, k = t
        i = [self._idx1(x) for x in k]
        if all(x is not None for x in i):                                           # depth ≤ 2: one read of the enumerated table
            return int(self.N2[i[0]]) if nm == "NEG" else int(self.T2[BIN7.index(nm), i[0], i[1]])
        v = [self._val(x) for x in k]                                               # deeper: compose through OP
        return int(self.OP[OPS.index(nm), v[0], v[1] if len(v) > 1 else 0])

    def eval(self, term, A):
        t = self._parse(A, term)
        if t is None: return None
        r = self._val(t)
        return ("bool", r == TRUE) if r >= TRUE else ("int", r)

    def clock(self, c, kappa=1):
        p = c % PERIOD
        return {"token": bool(self.flags[p] & 1), "beat": bool(self.flags[p] & 2), "epoch": bool(self.flags[p] & 4),
                "next": self.nxt[p].tolist(), "rings": [(kappa * c) % m for m in M15]}          # a ring's residue needs c itself (the 15 rings' joint period is ~6e17)


def _clock_twin(steps, kappa):
    """ResidueClock (arc.rs:205-222) re-expressed: tick → clock += 1, ring[i] = (ring[i] + κ) mod M[i]"""
    ring = [0] * 15; out = []
    for c in range(1, steps + 1):
        ring = [(r + kappa) % m for r, m in zip(ring, M15)]
        out.append((c, c % 3 == 0, c % 17 == 0, c % 53 == 0, list(ring)))
    return out


def random_term(R, A, depth):
    ops = list(A.oper)
    if depth == 0 or R.random() < 0.15: return [R.choice(A.ops)]
    t = R.choice(ops); name, ar = A.oper[t]
    out = [t]
    for _ in range(ar): out += random_term(R, A, depth - 1)
    return out


def selftest(n=100000, tab=None, out=None):
    import random, tempfile, reactor_twin as rt, tier1_symbols
    A = rt.Alphabet(tier1_symbols.load())
    tmp = None
    if not tab:
        tmp = tempfile.mkdtemp(prefix="ramkit-rtab-"); tab = os.path.join(tmp, "reactor.rtab")
    t0 = time.time(); size = build(tab) if not os.path.exists(tab) else os.path.getsize(tab); tb = time.time() - t0
    T = Tables(tab); R = random.Random(10); bad = 0; kinds = {"depth<=2": 0, "deep": 0, "noise": 0, "malformed": 0}
    t0 = time.time()
    for i in range(n):
        u = R.random()
        if u < 0.6: term = random_term(R, A, 2); kinds["depth<=2"] += 1
        elif u < 0.85: term = random_term(R, A, R.randint(3, 6)); kinds["deep"] += 1
        else:
            term = [R.choice(A.ops + list(A.oper)) for _ in range(R.randint(0, 7))]; kinds["noise"] += 1
        want = rt.eval_term(A, term); got = T.eval(term, A)
        kinds["malformed"] += want is None
        if want != got: bad += 1
    te = time.time() - t0
    cbad = 0
    for kappa in (1, -1):
        for c, tok, beat, ep, ring in _clock_twin(3 * PERIOD + 7, kappa):
            g = T.clock(c, kappa)
            if (g["token"], g["beat"], g["epoch"], g["rings"]) != (tok, beat, ep, ring): cbad += 1
            if g["next"][1] != (-c) % 17: cbad += 1
    t2 = 7 * T.n1 * T.n1
    res = {"lookups": n, "mismatch_vs_twin": bad, "mix": kinds, "clock_ticks_checked": 2 * (3 * PERIOD + 7), "clock_mismatch": cbad,
           "file_bytes": size, "t2_entries": t2, "build_s": round(tb, 1), "lookup_s": round(te, 1), "rss_mb": C.rss_mb()}
    del T
    if tmp: import shutil; shutil.rmtree(tmp, ignore_errors=True)
    if out: C.json_out(res, out)
    return bad == 0 and cbad == 0, res


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="c", required=True)
    b = sp.add_parser("build"); b.add_argument("out")
    e = sp.add_parser("eval"); e.add_argument("tab"); e.add_argument("toks", nargs="*", type=int)
    s = sp.add_parser("selftest"); s.add_argument("--n", type=int, default=100000); s.add_argument("--tab"); s.add_argument("--out")
    a = ap.parse_args()
    if a.c == "build": t = time.time(); print(json.dumps({"out": a.out, "bytes": build(a.out), "s": round(time.time() - t, 1), "rss_mb": C.rss_mb()}))
    elif a.c == "eval":
        import reactor_twin as rt, tier1_symbols
        print(Tables(a.tab).eval(a.toks, rt.Alphabet(tier1_symbols.load())))
    else:
        ok, res = selftest(a.n, a.tab, a.out); print(json.dumps(res)); print("PASS" if ok else "FAIL", "reactor_tables"); sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

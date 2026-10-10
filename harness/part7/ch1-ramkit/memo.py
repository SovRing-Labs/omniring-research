#!/usr/bin/env python3
"""ramkit #2 — verified-answer memo (RAM-KIT-0, J 10-08). hash(domain | canonical problem) → (verified answer, verifier verdict).
DOING checks become one lookup; generator rows already made in an earlier round are reused instead of re-solved.

File RMEMO1 (mmap-able, little-endian): magic 8B · n u64 · keys u64[n] (sorted) · offs u64[n+1] · verdict u8[n] · blob (answers, canonical
JSON utf-8). Load = np.memmap views (no parse); Memo.ram() also builds a Python dict for O(1) hits in a hot loop.

  memo.py build  OUT.rmemo [--rg DIR ...] [--builds B ...] [--gen DOMAINS --n N --seed S [--level L]]
  memo.py lookup MEMO --domain D --problem JSON              → answer + verdict (exit 3 = miss)
  memo.py replay MEMO --builds B ... | --gen …               → hit-rate of those problems in MEMO
  memo.py selftest [--n 10000]
API: m = Memo(path); m.get(domain, problem) → (answer, verdict) | None; m.check(domain, problem, answer) → verdict (lookup when the answer is
the stored one, else the verifier — never trusted blind)."""
import argparse, glob, json, os, subprocess, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

MAGIC = b"RMEMO1\0\0"


def entries_from_rg_dir(d):
    """reason-gen `gen --out DIR` output: DIR/<domain>.jsonl.zst (or .jsonl) rows with problem / answer / verified"""
    for p in sorted(glob.glob(os.path.join(d, "*.jsonl.zst")) + glob.glob(os.path.join(d, "*.jsonl"))):
        if p.endswith(".zst"):
            data = subprocess.run(["zstd", "-dc", p], capture_output=True, check=True).stdout.decode()
        else:
            data = open(p).read()
        for line in data.split("\n"):
            if line:
                r = json.loads(line); yield r["domain"], r["problem"], r["answer"], bool(r["verified"])


def entries_from_gen(domains, n, seed, level=None):
    RG = C.rg()
    for d in domains:
        for i in range(n):
            r = RG.make(d, i, seed, level)
            yield d, r["problem"], r["answer"], bool(r["verified"])


def problems_from_builds(builds):
    """(domain, i, seed, level) of every generator row in middle builds (tier-1 builds are skipped: not regenerable — see README)"""
    for b in builds:
        man = json.load(open(os.path.join(b, "manifest.json")))
        if not C.build_is_generator(man):
            print(f"memo: skip {b} (tier-1 build: rows are not regenerable from the sidecar)", file=sys.stderr); continue
        doms = man["port"]["domains"]
        for k, rows, _ in C.build_rows(b):
            for r in rows:
                yield doms[int(r[11])], int(r[8]), int(r[9]), int(r[10])


def entries_from_builds(builds):
    RG = C.rg(); seen = set()
    for d, i, s, lv in problems_from_builds(builds):
        if (d, i, s, lv) in seen: continue
        seen.add((d, i, s, lv)); r = RG.make(d, i, s, lv)
        yield d, r["problem"], r["answer"], bool(r["verified"])


def write(path, entries):
    """entries: iterable of (domain, problem, answer, verdict); duplicate keys keep the first"""
    rec = {}
    for d, p, a, v in entries:
        k = C.problem_key(d, p)
        if k not in rec: rec[k] = (C.canon(a).encode(), 1 if v else 0)
    keys = np.array(sorted(rec), dtype=np.uint64); n = len(keys)
    blobs = [rec[int(k)][0] for k in keys]; offs = np.zeros(n + 1, np.uint64)
    if n: offs[1:] = np.cumsum([len(b) for b in blobs], dtype=np.uint64)
    verd = np.array([rec[int(k)][1] for k in keys], np.uint8)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path + ".tmp", "wb") as f:
        f.write(MAGIC); f.write(np.uint64(n).tobytes()); f.write(keys.tobytes()); f.write(offs.tobytes()); f.write(verd.tobytes())
        f.write(b"".join(blobs))
    os.replace(path + ".tmp", path)
    return n


class Memo:
    def __init__(self, path):
        mm = np.memmap(path, dtype=np.uint8, mode="r")
        if bytes(mm[:8]) != MAGIC: raise ValueError(f"{path}: not an RMEMO1 file")
        n = int(np.frombuffer(bytes(mm[8:16]), np.uint64)[0]); o = 16
        self.keys = np.frombuffer(mm, np.uint64, n, o); o += 8 * n
        self.offs = np.frombuffer(mm, np.uint64, n + 1, o); o += 8 * (n + 1)
        self.verd = np.frombuffer(mm, np.uint8, n, o); o += n
        self.blob0, self.mm, self.n, self.d = o, mm, n, None
        self.hits = self.misses = self.recomputed = 0

    def ram(self):
        self.d = {int(k): i for i, k in enumerate(self.keys)}; return self

    def _idx(self, key):
        if self.d is not None: return self.d.get(key)
        i = int(np.searchsorted(self.keys, np.uint64(key)))
        return i if i < self.n and int(self.keys[i]) == key else None

    def get(self, domain, problem):
        i = self._idx(C.problem_key(domain, problem))
        if i is None: self.misses += 1; return None
        self.hits += 1
        a = bytes(self.mm[self.blob0 + int(self.offs[i]):self.blob0 + int(self.offs[i + 1])])
        return json.loads(a), bool(self.verd[i])

    def check(self, domain, problem, answer):
        g = self.get(domain, problem)
        if g is not None and C.canon(g[0]) == C.canon(answer): return g[1]
        self.recomputed += 1
        try:
            return bool(C.rg().fns_of(domain)[2](problem, answer))
        except Exception:                                   # a malformed answer is a wrong answer
            return False


def _src(a):
    it = []
    for d in a.rg or []: it.append(entries_from_rg_dir(d))
    if a.builds: it.append(entries_from_builds(a.builds))
    if a.gen: it.append(entries_from_gen(a.gen.split(","), a.n, a.seed, a.level))
    for x in it: yield from x


def cmd_build(a):
    t = time.time(); n = write(a.out, _src(a))
    print(json.dumps({"memo": a.out, "entries": n, "bytes": os.path.getsize(a.out), "s": round(time.time() - t, 2), "rss_mb": C.rss_mb()}))


def cmd_lookup(a):
    g = Memo(a.memo).get(a.domain, json.loads(a.problem))
    if g is None: print("MISS"); sys.exit(3)
    print(json.dumps({"answer": g[0], "verdict": g[1]}))


def cmd_replay(a):
    m = Memo(a.memo).ram()
    if a.builds: probs = [(d, C.regen_problem(d, i, s, lv)[1]) for d, i, s, lv in problems_from_builds(a.builds)]
    else: probs = [(d, p) for d, p, _, _ in entries_from_gen(a.gen.split(","), a.n, a.seed, a.level)]
    for d, p in probs: m.get(d, p)
    tot = m.hits + m.misses
    print(json.dumps({"memo": a.memo, "problems": tot, "hits": m.hits, "hit_rate": round(m.hits / max(1, tot), 4)}))


def selftest(n=10000, out_dir=None):
    """10k problems over the 26: memo verdict == recompute verdict; a wrong answer is re-verified, never trusted; two rounds' hit-rate"""
    import tempfile
    RG = C.rg(); out_dir = out_dir or tempfile.mkdtemp(prefix="ramkit-memo-")
    per = max(1, n // len(C.GENS26)); t0 = time.time()
    A = list(entries_from_gen(C.GENS26, per, 1001))
    p1 = os.path.join(out_dir, "r1.rmemo"); write(p1, A); t_build = time.time() - t0
    m = Memo(p1); bad = 0; t = time.time()
    for d, p, a_, v in A:
        g = m.get(d, p)
        if g is None or bool(RG.fns_of(d)[2](p, g[0])) != g[1] or g[1] != v: bad += 1
    t_check = time.time() - t
    wrong = 0                                               # a perturbed answer must go to the verifier and fail
    for d, p, a_, v in A[:: max(1, len(A) // 200)]:
        if not v: continue
        if m.check(d, p, {"__not_the_answer__": 1}) is not False: wrong += 1
    # two rounds: round 2 = another row seed + the same levels → hit-rate when round 2 replays against round 1's memo
    m2 = Memo(p1).ram(); B = [(d, RG.make(d, i, 1002, None)["problem"]) for d in C.GENS26 for i in range(per)]
    for d, p in B: m2.get(d, p)
    hit_dom = {}
    for d, p in B: hit_dom.setdefault(d, [0, 0]); hit_dom[d][1] += 1; hit_dom[d][0] += m2._idx(C.problem_key(d, p)) is not None
    res = {"problems": len(A), "memo_entries": m.n, "verdict_mismatch": bad, "wrong_answer_trusted": wrong,
           "build_s": round(t_build, 1), "lookup_plus_verify_s": round(t_check, 1), "file_bytes": os.path.getsize(p1),
           "round2_hit_rate": round(m2.hits / max(1, m2.hits + m2.misses), 4),
           "round2_hit_by_domain": {d: round(h / n_, 3) for d, (h, n_) in sorted(hit_dom.items()) if h}, "rss_mb": C.rss_mb()}
    ok = bad == 0 and wrong == 0 and m.n > 0.9 * len(A)
    return ok, res


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="c", required=True)
    def src(p):
        p.add_argument("--rg", nargs="*"); p.add_argument("--builds", nargs="*"); p.add_argument("--gen")
        p.add_argument("--n", type=int, default=1000); p.add_argument("--seed", type=int, default=0); p.add_argument("--level", type=int)
    b = sp.add_parser("build"); b.add_argument("out"); src(b)
    l = sp.add_parser("lookup"); l.add_argument("memo"); l.add_argument("--domain", required=True); l.add_argument("--problem", required=True)
    r = sp.add_parser("replay"); r.add_argument("memo"); src(r)
    s = sp.add_parser("selftest"); s.add_argument("--n", type=int, default=10000); s.add_argument("--out")
    a = ap.parse_args()
    if a.c == "build": cmd_build(a)
    elif a.c == "lookup": cmd_lookup(a)
    elif a.c == "replay": cmd_replay(a)
    else:
        ok, res = selftest(a.n)
        C.json_out(res, a.out); print(json.dumps(res)); print(("PASS" if ok else "FAIL"), "memo"); sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""ramkit #11 — memorisation detector (RAM-KIT-0, J 10-08; infini-gram idea, Liu et al. 2024 — clean-room, numpy only).
A suffix array over the token rows of the given build dirs (phase_k.u16; one 65535 separator between phases / documents) and, optionally,
the model's own written tokens from run journals (journal.jsonl `own_tokens`). Query: the longest stretch of a token sequence that occurs in
the corpus (matching statistics over every start) and how often it occurs. "Memorised the answer" = the model's answer is one long corpus
match; "ran the procedure" = short matches stitched together.
SA build: prefix doubling (argsort of (rank_i, rank_{i+k}) packed in int64), O(n log n · log L). RAM ≈ 40 B/token while building (2 M
tokens ≈ 80 MB); the index on disk = corpus u16 + SA u32 (6 B/token).

  memdetect.py index  <out_dir> <build …> [--journal FILE …]
  memdetect.py query  <index_dir> <tok tok …>
  memdetect.py report <index_dir> <journal.jsonl> [--out FILE] [--min-len 4]    → per answer: length, longest match, count; summary
  memdetect.py selftest"""
import argparse, json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

SEP = 65535


def corpus_from(builds, journals=()):
    parts, docs = [], []
    for b in builds:
        man = json.load(open(os.path.join(b, "manifest.json")))
        for k in range(len(man["phases"])):
            p = os.path.join(b, f"phase_{k}.u16")
            if os.path.exists(p):
                parts.append(np.fromfile(p, np.uint16)); parts.append(np.array([SEP], np.uint16)); docs.append(f"{os.path.basename(b)}/{k}")
    for j in journals:
        for line in open(j):
            try: t = json.loads(line).get("own_tokens")
            except ValueError: continue
            if t: parts.append(np.array(t, np.uint16)); parts.append(np.array([SEP], np.uint16))
        docs.append(os.path.basename(os.path.dirname(j)) + "/journal")
    return (np.concatenate(parts) if parts else np.zeros(0, np.uint16)), docs


def suffix_array(x):
    n = len(x)
    rank = x.astype(np.int64); k = 1
    sa = np.argsort(rank, kind="stable")
    while True:
        r2 = np.full(n, -1, np.int64); r2[:n - k] = rank[k:] if k < n else r2[:0]
        key = (rank << 32) | (r2 + 1)
        sa = np.argsort(key, kind="stable"); ks = key[sa]
        new = np.empty(n, np.int64); new[sa] = np.concatenate([[0], np.cumsum(ks[1:] != ks[:-1])])
        rank = new
        if rank.max() == n - 1 or k >= n: break
        k *= 2
    return sa.astype(np.uint32)


class Index:
    def __init__(self, d):
        self.x = np.fromfile(os.path.join(d, "corpus.u16"), np.uint16)
        self.sa = np.load(os.path.join(d, "sa.npy"), mmap_mode="r")
        self.n = len(self.x)

    @classmethod
    def build(cls, d, x, meta):
        os.makedirs(d, exist_ok=True); t = time.time(); sa = suffix_array(x)
        x.tofile(os.path.join(d, "corpus.u16")); np.save(os.path.join(d, "sa.npy"), sa)
        meta = dict(meta, tokens=int(len(x)), sa_s=round(time.time() - t, 1), rss_mb=C.rss_mb()); C.json_out(meta, os.path.join(d, "meta.json"))
        return cls(d), meta

    def _tok(self, i):
        return int(self.x[i]) if i < self.n else -1

    def _narrow(self, lo, hi, off, t):
        """within sa[lo:hi] (suffixes sharing their first `off` tokens) the sub-range whose token at off == t"""
        a, b = lo, hi
        while a < b:
            m = (a + b) // 2
            if self._tok(int(self.sa[m]) + off) < t: a = m + 1
            else: b = m
        s = a; b = hi
        while a < b:
            m = (a + b) // 2
            if self._tok(int(self.sa[m]) + off) <= t: a = m + 1
            else: b = m
        return s, a

    def longest_prefix(self, q):
        """(length of q's longest prefix in the corpus, its occurrence count)"""
        lo, hi, L = 0, self.n, 0
        for off, t in enumerate(q):
            a, b = self._narrow(lo, hi, off, int(t))
            if a >= b: break
            lo, hi, L = a, b, off + 1
        return L, (hi - lo if L else 0)

    def count(self, q):
        L, c = self.longest_prefix(q)
        return c if L == len(q) else 0

    def longest_match(self, q):
        """longest substring of q found in the corpus: (length, count, start in q)"""
        best = (0, 0, 0)
        for s in range(len(q)):
            if len(q) - s <= best[0]: break
            L, c = self.longest_prefix(q[s:])
            if L > best[0]: best = (L, c, s)
        return best


def report(idx, journal, min_len=4):
    rows = []
    for line in open(journal):
        try: e = json.loads(line)
        except ValueError: continue
        t = e.get("own_tokens")
        if not t or len(t) < min_len: continue
        L, c, s = idx.longest_match(t)
        rows.append({"domain": e.get("domain"), "stage": e.get("stage"), "solved": e.get("solved"), "len": len(t), "longest": L, "count": c,
                     "full": L == len(t)})
    n = len(rows)
    summ = {"answers": n, "full_match": sum(r["full"] for r in rows), "full_match_rate": round(sum(r["full"] for r in rows) / max(1, n), 4),
            "mean_longest_over_len": round(float(np.mean([r["longest"] / r["len"] for r in rows])) if rows else 0.0, 4)}
    by = {}
    for r in rows: by.setdefault(r["stage"], [0, 0]); by[r["stage"]][0] += r["full"]; by[r["stage"]][1] += 1
    summ["full_by_stage"] = {k: f"{a}/{b}" for k, (a, b) in by.items()}
    return summ, rows


def selftest(out=None):
    import tempfile, random
    d = tempfile.mkdtemp(prefix="ramkit-memdet-"); res = {}
    R = np.random.default_rng(3); x = R.integers(0, 6, 3000).astype(np.uint16)          # SA == brute-force sort on a small corpus
    sa = suffix_array(x); brute = sorted(range(len(x)), key=lambda i: tuple(x[i:].tolist()))
    res["sa_equals_bruteforce"] = bool(np.array_equal(sa, np.array(brute, np.uint32)))
    bdir = os.path.join(C.TRIAL, "build-v4")
    builds = [os.path.join(bdir, b) for b in ("live-r1-s1000", "seed-v4-short") if os.path.isdir(os.path.join(bdir, b))]
    if builds:
        x, docs = corpus_from(builds)
    else:                                                                               # pod without builds: synthetic corpus
        x = R.integers(0, 2000, 400_000).astype(np.uint16); docs = ["synthetic"]
    idx, meta = Index.build(os.path.join(d, "ix"), x, {"builds": builds, "docs": docs})
    res["corpus_tokens"] = meta["tokens"]; res["sa_s"] = meta["sa_s"]
    # a known row: 60 consecutive corpus tokens (no separator) → full-length match; a random sequence → short
    rr = random.Random(5)
    while True:
        s = rr.randrange(0, len(x) - 61)
        if SEP not in x[s:s + 60]: break
    known = x[s:s + 60].tolist(); Lk, ck, _ = idx.longest_match(known)
    rnd = [rr.randrange(0, 4000) for _ in range(60)]; Lr, cr, _ = idx.longest_match(rnd)
    t = time.time(); _ = [idx.longest_match(x[rr.randrange(0, len(x) - 40):][:40].tolist()) for _ in range(50)]; qs = (time.time() - t) / 50
    res.update({"known_row_len": 60, "known_longest": Lk, "known_count": ck, "random_longest": Lr, "random_count": cr,
                "query_ms_40tok": round(qs * 1000, 1), "rss_mb": C.rss_mb()})
    J = os.path.join(C.TRIAL, "runtime/results/pod-live-r1/live-r1/h0/journal.jsonl")      # read-only report on a real round's answers
    if builds and os.path.exists(J):
        summ, _ = report(idx, J); res["report_pod_live_r1_h0_vs_r1s1000_seedv4"] = summ
    import shutil; shutil.rmtree(d, ignore_errors=True)
    ok = res["sa_equals_bruteforce"] and Lk == 60 and ck >= 1 and Lr <= 8
    if out: C.json_out(res, out)
    return ok, res


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="c", required=True)
    i = sp.add_parser("index"); i.add_argument("out"); i.add_argument("builds", nargs="*"); i.add_argument("--journal", nargs="*", default=[])
    q = sp.add_parser("query"); q.add_argument("index"); q.add_argument("toks", nargs="+", type=int)
    r = sp.add_parser("report"); r.add_argument("index"); r.add_argument("journal"); r.add_argument("--out"); r.add_argument("--min-len", type=int, default=4)
    s = sp.add_parser("selftest"); s.add_argument("--out")
    a = ap.parse_args()
    if a.c == "index":
        x, docs = corpus_from(a.builds, a.journal); _, meta = Index.build(a.out, x, {"builds": a.builds, "journals": a.journal, "docs": docs})
        print(json.dumps({k: meta[k] for k in ("tokens", "sa_s", "rss_mb")}))
    elif a.c == "query":
        L, c, s = Index(a.index).longest_match(a.toks); print(json.dumps({"len": len(a.toks), "longest": L, "count": c, "start": s}))
    elif a.c == "report":
        summ, rows = report(Index(a.index), a.journal, a.min_len)
        if a.out: C.json_out({"summary": summ, "rows": rows}, a.out)
        print(json.dumps(summ))
    else:
        ok, res = selftest(a.out); print(json.dumps(res)); print("PASS" if ok else "FAIL", "memdetect"); sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

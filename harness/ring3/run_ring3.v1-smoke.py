#!/usr/bin/env python3
"""RING-3 — five tests from J's 2026-09-29 thought threads (seat-run, pre-registered).

  DIAMOND  facet systems: 4 corner systems (each its own coprime rings + a per-corner check ring), marks bind one value per
           corner; the query knows 2 corners; recover the other 2. Compared with the flat (3,5,7,13)+17 system with 2 clamps.
  PEEL     explaining away: settle, accept if the 17 ring says legal, SUBTRACT the found mark, settle again; stop at the first
           illegal settle. Plain soft weights vs annealed inhibition (weight power ramps 1 -> 4).
  CORREL   codebooks whose entries are similar (mean pairwise similarity rho); plain vs a no-training decorrelation
           (centre each ring's codebook, re-project to unit modulus) used for both storage and read.
  TABU     J's knockout: on trials that did not converge / cycled, knock out the stuck positions, re-settle several ways,
           keep only 17-legal answers, accept the answer that survives >= 2 knockouts (consensus).
  FRET     "store the fret, not the note": 20 symbols x a continuous rotation dial (FPE, 1,000 ticks). Flat resonator over
           1,000 dial positions vs coarse-to-fine (low-frequency dims first on a 20-tick grid, then full dims locally).

Library: _Pads/RING/ring1/ring1_core.py (make_rings / encode / make_slot / resonate / crt / wilson), unchanged.
Usage: run_ring3.py [--quick] [--only NAME[,NAME]] [--out PATH]
"""
from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ring1"))
import ring1_core as rc  # noqa: E402

D = 5120
Z99 = 2.5758293035489004
MODS = (3, 5, 7, 13)
MODS_C = (3, 5, 7, 13, 17)
N = 1365

PREREG = {
    "DIAMOND": "PASS if, at M = 12 marks per slot with 2 corners known, the diamond's recall of BOTH unknown corners has a "
               "Wilson-99% lower bound >= the flat (3,5,7,13)+17 system's point recall with 2 clamps (13 and 7), AND the "
               "per-corner check rings flag >= 50% of wrong settles (pooled over M in {12, 24}). Otherwise KILL.",
    "PEEL": "PASS if, at M = 24, peeling (best of plain / annealed) recovers on average >= 2.0 true marks per slot (a single "
            "settle recovers at most 1) with accepted fakes <= 2% of all accepted answers (Wilson-99% upper bound <= 0.05). "
            "Otherwise KILL.",
    "CORREL": "PASS if plain recall at rho = 0.3 falls >= 0.20 below plain recall at rho = 0 (similar codebooks hurt), AND "
              "decorrelated recall at rho = 0.3 is within 0.10 of plain recall at rho = 0 (the fix recovers it). Otherwise "
              "KILL (state which half failed).",
    "TABU": "PASS if, over stuck trials (not converged or cycled) pooled over M in {12, 24}, knockout+consensus rescues "
            "(accepts the correct target) >= 50% of them, with silent-wrong accepts <= 2% of stuck trials (Wilson-99% upper "
            "bound <= 0.05). Otherwise KILL.",
    "FRET": "PASS if coarse-to-fine recovers symbol AND angle (|error| <= 1 tick) for >= 90% of queries (Wilson-99% lower "
            "bound >= 0.80) at M = 1, while the flat resonator scores < 50% there. Otherwise KILL.",
}


def wil(k, n):
    p, lo, hi = rc.wilson(k, n, Z99)
    return p, lo, hi


def fmt(k, n):
    p, lo, hi = wil(k, n)
    return f"{k}/{n} = {p:.1%} [{lo:.1%}, {hi:.1%}]"


# ------------------------------------------------------------------ generic resonator (masks + annealing)
def res_general(v, cbs, clamp=None, max_iter=50, power=lambda it: 1.0, masks=None):
    """Soft resonator as ring1_core.resonate, plus (a) a per-ring position mask (excluded positions get weight 0) and
    (b) a weight power schedule (lateral inhibition strength). Returns positions, iters, converged, cycled."""
    v = np.asarray(v, dtype=np.complex128)
    n = len(cbs)
    pinned = {} if clamp is None else dict(clamp)
    masks = masks or {}
    ests = [(cbs[i][pinned[i]] if i in pinned else cbs[i].mean(0)).astype(np.complex128) for i in range(n)]
    prev, stable, seen = None, 0, set()
    converged = cycled = False
    it = 0
    pos = None
    for it in range(1, max_iter + 1):
        p = power(it)
        pos = []
        for i in range(n):
            if i in pinned:
                pos.append(pinned[i]); continue
            u = v.copy()
            for j in range(n):
                if j != i:
                    u = u * ests[j].conj()
            s = (cbs[i].conj() @ u).real / len(v)
            w = np.maximum(s, 0.0)
            if i in masks:
                w = w * masks[i]
            if p != 1.0:
                w = w ** p
            e = w @ cbs[i]
            mag = np.abs(e)
            ests[i] = e / np.where(mag > 1e-12, mag, 1.0)
            sc = s.copy()
            if i in masks:
                sc = np.where(masks[i] > 0, sc, -np.inf)
            pos.append(int(np.argmax(sc)))
        key = tuple(pos)
        if key == prev:
            stable += 1
            if stable >= 1:
                converged = True; break
        else:
            stable = 0
        if key in seen and key != prev:
            cycled = True
        seen.add(key)
        prev = key
    return {"positions": pos, "iters": it, "converged": converged, "cycled": cycled and not converged}


def legal5(res):
    return rc.crt(list(res), MODS_C) < N


def val4(res):
    return rc.crt(list(res[:4]), MODS)


# ------------------------------------------------------------------ DIAMOND
def diamond(trials, seed=11):
    out = {}
    for tag, cmods, chk in (("A (3,5,7)+11", (3, 5, 7), 11), ("B (5,7,11)+13", (5, 7, 11), 13)):
        cap = math.prod(cmods)
        corner_mods = cmods + (chk,)
        rings = []
        for c in range(4):
            rings += rc.make_rings(corner_mods, D, seed=seed * 100 + c, quant="float")
        rng = np.random.default_rng(seed + 1)
        for M in (12, 24):
            ok = wrong = flagged = 0
            iters = []
            for _ in range(trials):
                marks = [tuple(int(x) for x in rng.integers(0, cap, 4)) for _ in range(M)]
                v = np.zeros(D, complex)
                for mk in marks:
                    e = np.ones(D, complex)
                    for c, val in enumerate(mk):
                        for r, m in enumerate(corner_mods):
                            e = e * rings[c * 4 + r][val % m]
                    v += e
                tgt = marks[0]
                clamp = {}
                for c in (0, 1):  # corners 0 and 1 known
                    for r, m in enumerate(corner_mods):
                        clamp[c * 4 + r] = tgt[c] % m
                res = rc.resonate(v, rings, clamp=clamp, max_iter=50, seed=0)
                iters.append(res["iters"])
                pos = res["positions"]
                dec = []
                illegal = False
                for c in (2, 3):
                    rr = [pos[c * 4 + r] for r in range(4)]
                    x = rc.crt(rr, corner_mods)
                    if x >= cap:
                        illegal = True
                    dec.append(x)
                if dec == [tgt[2], tgt[3]]:
                    ok += 1
                else:
                    wrong += 1
                    flagged += illegal
            out[(tag, M)] = (ok, trials, wrong, flagged, float(np.median(iters)))
    # flat reference: (3,5,7,13)+17, 2 clamps (13, 7)
    rings = rc.make_rings(MODS_C, D, seed=seed * 7, quant="float")
    rng = np.random.default_rng(seed + 2)
    flat = {}
    for M in (12, 24):
        ok = 0
        for _ in range(trials):
            xs = [int(x) for x in rng.integers(0, N, M)]
            v = rc.make_slot(xs, rings, MODS_C)
            t = xs[0]
            res = rc.resonate(v, rings, clamp={3: t % 13, 2: t % 7}, max_iter=50, seed=0)
            ok += val4(res["positions"]) == t and legal5(res["positions"])
        flat[M] = (ok, trials)
    fa = out[("A (3,5,7)+11", 12)]
    _, lo, _ = wil(fa[0], fa[1])
    flat_p = flat[12][0] / flat[12][1]
    wr = sum(out[("A (3,5,7)+11", M)][2] for M in (12, 24))
    fl = sum(out[("A (3,5,7)+11", M)][3] for M in (12, 24))
    c1, c2 = lo >= flat_p, (fl / wr if wr else 1.0) >= 0.5
    verdict = "PASS" if c1 and c2 else "KILL"
    why = f"diamond A lower {lo:.3f} vs flat {flat_p:.3f} ({'ok' if c1 else 'fail'}); check flags {fl}/{wr} wrong settles ({'ok' if c2 else 'fail'})"
    lines = ["| system | M | recall of both unknown corners | wrong settles flagged by corner check | median iters |", "|---|---|---|---|---|"]
    for (tag, M), (ok, n, w, f, mi) in out.items():
        lines.append(f"| diamond {tag} | {M} | {fmt(ok, n)} | {f}/{w} | {mi:.0f} |")
    for M, (ok, n) in flat.items():
        lines.append(f"| flat (3,5,7,13)+17, 2 clamps | {M} | {fmt(ok, n)} | n/a | n/a |")
    return verdict, why, "\n".join(lines)


# ------------------------------------------------------------------ PEEL
def peel_once(v, rings, members, power):
    acc_true, acc_fake = set(), 0
    v = v.copy()
    for _ in range(len(members) + 3):
        r = res_general(v, rings, max_iter=50, power=power)
        pos = r["positions"]
        if not legal5(pos):
            break
        x = val4(pos)
        if x in members:
            acc_true.add(x)
        else:
            acc_fake += 1
        v = v - rc.encode(x, rings, MODS_C)
    return len(acc_true), acc_fake


def peel(trials, seed=21):
    rings = rc.make_rings(MODS_C, D, seed=seed, quant="float")
    rng = np.random.default_rng(seed + 1)
    arms = {"plain": lambda it: 1.0, "annealed": lambda it: min(4.0, 1.0 + 0.5 * (it - 1))}
    res = {}
    sweep = {}
    for M in (12, 24):
        tot = {a: [0, 0, 0] for a in arms}  # true, fake, accepted
        sw_true = sw_fake = 0
        for t in range(trials):
            xs = [int(x) for x in rng.choice(N, M, replace=False)]
            members = set(xs)
            v = rc.make_slot(xs, rings, MODS_C)
            for a, pw in arms.items():
                tr, fk = peel_once(v, rings, members, pw)
                tot[a][0] += tr; tot[a][1] += fk; tot[a][2] += tr + fk
            if t < max(10, trials // 5):  # context baseline: clamp sweep over the 13 ring
                found, fk = set(), 0
                for r13 in range(13):
                    rr = rc.resonate(v, rings, clamp={3: r13}, max_iter=50, seed=0)["positions"]
                    if legal5(rr):
                        x = val4(rr)
                        if x in members:
                            found.add(x)
                        else:
                            fk += 1
                sw_true += len(found); sw_fake += fk
        res[M] = tot
        n_sw = max(10, trials // 5)
        sweep[M] = (sw_true / n_sw, sw_fake / n_sw)
    best = max(arms, key=lambda a: res[24][a][0])
    tr, fk, ac = res[24][best]
    mean_true = tr / trials
    _, _, hi = wil(fk, ac) if ac else (0, 0, 1)
    c1, c2 = mean_true >= 2.0, (ac > 0 and hi <= 0.05)
    verdict = "PASS" if c1 and c2 else "KILL"
    why = f"M=24 best arm '{best}': {mean_true:.2f} true marks/slot ({'ok' if c1 else 'fail'}); fakes {fk}/{ac} accepted, upper {hi:.3f} ({'ok' if c2 else 'fail'})"
    lines = ["| M | arm | true marks recovered / slot | accepted fakes / accepted | clamp-sweep context (13 settles): true / fake per slot |", "|---|---|---|---|---|"]
    for M in (12, 24):
        for a in arms:
            tr, fk, ac = res[M][a]
            lines.append(f"| {M} | {a} | {tr / trials:.2f} | {fk}/{ac} | {sweep[M][0]:.2f} / {sweep[M][1]:.2f} |")
    return verdict, why, "\n".join(lines)


# ------------------------------------------------------------------ CORREL
def corr_rings(mods, rho, seed):
    rng = np.random.default_rng(seed)
    out = []
    for m in mods:
        proto = np.exp(1j * rng.uniform(-np.pi, np.pi, D))
        own = np.exp(1j * rng.uniform(-np.pi, np.pi, (m, D)))
        mix = math.sqrt(rho) * proto + math.sqrt(1 - rho) * own
        out.append(mix / np.abs(mix))
    return out


def decorrelate(rings):
    out = []
    for cb in rings:
        c = cb - cb.mean(0)
        out.append(c / np.where(np.abs(c) > 1e-12, np.abs(c), 1.0))
    return out


def mean_sim(cb):
    g = (cb @ cb.conj().T).real / D
    m = cb.shape[0]
    return float((g.sum() - np.trace(g)) / (m * (m - 1)))


def correl(trials, seed=31):
    rows, rec = [], {}
    for rho in (0.0, 0.1, 0.3, 0.5):
        base = corr_rings(MODS_C, rho, seed + int(rho * 100))
        for arm, rings in (("plain", base), ("decorrelated", decorrelate(base))):
            rng = np.random.default_rng(seed + 5)
            ok = 0
            for _ in range(trials):
                xs = [int(x) for x in rng.integers(0, N, 4)]
                v = rc.make_slot(xs, rings, MODS_C)
                t = xs[0]
                r = rc.resonate(v, rings, clamp={3: t % 13}, max_iter=50, seed=0)["positions"]
                ok += val4(r) == t and legal5(r)
            rec[(rho, arm)] = ok / trials
            rows.append(f"| {rho} | {arm} | {np.mean([mean_sim(c) for c in rings]):.3f} | {fmt(ok, trials)} |")
    drop = rec[(0.0, "plain")] - rec[(0.3, "plain")]
    gap = rec[(0.0, "plain")] - rec[(0.3, "decorrelated")]
    c1, c2 = drop >= 0.20, gap <= 0.10
    verdict = "PASS" if c1 and c2 else "KILL"
    why = f"plain drop rho 0->0.3 = {drop:+.2f} ({'ok' if c1 else 'fail'}); decorrelated@0.3 vs plain@0 = {-gap:+.2f} ({'ok' if c2 else 'fail'})"
    return verdict, why, "| rho (target) | codebook | measured mean similarity | target recall, M=4, 13-ring clamped |\n|---|---|---|---|\n" + "\n".join(rows)


# ------------------------------------------------------------------ TABU
def tabu(trials, seed=41):
    rings = rc.make_rings(MODS_C, D, seed=seed, quant="float")
    rng = np.random.default_rng(seed + 1)
    stuck = rescued = silent = baseline_ok = 0
    per = {}
    for M in (12, 24):
        s_M = r_M = w_M = 0
        for _ in range(trials):
            xs = [int(x) for x in rng.integers(0, N, M)]
            v = rc.make_slot(xs, rings, MODS_C)
            t = xs[0]
            clamp = {3: t % 13}
            r0 = res_general(v, rings, clamp=clamp, max_iter=50)
            if r0["converged"] and not r0["cycled"]:
                continue
            s_M += 1
            baseline_ok += val4(r0["positions"]) == t and legal5(r0["positions"])
            free = [0, 1, 2, 4]
            answers = []
            knock_sets = [[i] for i in free] + [[0, 1], [2, 4]]
            for ks in knock_sets:
                masks = {}
                for i in ks:
                    mk = np.ones(MODS_C[i]); mk[r0["positions"][i]] = 0.0
                    masks[i] = mk
                rr = res_general(v, rings, clamp=clamp, max_iter=50, masks=masks)["positions"]
                if legal5(rr):
                    answers.append(val4(rr))
            if r0["positions"] and legal5(r0["positions"]):
                answers.append(val4(r0["positions"]))
            if answers:
                vals, cnt = np.unique(answers, return_counts=True)
                k = int(np.argmax(cnt))
                if cnt[k] >= 2:
                    if int(vals[k]) == t:
                        r_M += 1
                    else:
                        w_M += 1
        per[M] = (s_M, r_M, w_M)
        stuck += s_M; rescued += r_M; silent += w_M
    _, _, hi = wil(silent, stuck) if stuck else (0, 0, 1)
    c1 = stuck > 0 and rescued / stuck >= 0.5
    c2 = stuck > 0 and hi <= 0.05
    verdict = "PASS" if c1 and c2 else "KILL"
    why = (f"stuck {stuck}; rescued {rescued} ({(rescued / stuck if stuck else 0):.1%}, {'ok' if c1 else 'fail'}); "
           f"silent-wrong {silent} (upper {hi:.3f}, {'ok' if c2 else 'fail'}); stuck trials' own answer correct {baseline_ok}")
    lines = ["| M | stuck trials (of %d) | rescued (correct target accepted) | silent-wrong accepted |" % trials, "|---|---|---|---|"]
    for M, (s, r, w) in per.items():
        lines.append(f"| {M} | {s} | {fmt(r, s) if s else '0/0'} | {fmt(w, s) if s else '0/0'} |")
    return verdict, why, "\n".join(lines)


# ------------------------------------------------------------------ FRET
def fret(trials, seed=51, L=8.0, T=1000, S=20):
    rng = np.random.default_rng(seed)
    sym = np.exp(1j * rng.uniform(-np.pi, np.pi, (S, D)))
    omega = rng.uniform(-2 * np.pi / L, 2 * np.pi / L, D)
    dial = lambda th: np.exp(1j * np.outer(np.atleast_1d(th), omega))  # noqa: E731
    P_full = dial(np.arange(T))
    low = np.abs(omega) < (2 * np.pi / (L * 8))            # wide-kernel dims (~1/8 of D)
    grid = np.arange(0, T, 20)
    out = {}
    trng = np.random.default_rng(seed + 1)
    for M in (1, 3):
        flat_ok = ctf_ok = 0
        for _ in range(trials):
            items = [(int(trng.integers(0, S)), int(trng.integers(0, T))) for _ in range(M)]
            v = sum(sym[s] * dial(th)[0] for s, th in items)
            members = set(items)
            # A: flat resonator over [symbols, 1,000 dial positions]
            r = rc.resonate(v, [sym, P_full], max_iter=50, seed=0)["positions"]
            flat_ok += any(r[0] == s and abs(r[1] - th) <= 1 for s, th in members)
            # B: coarse (low-frequency dims, 20-tick grid) -> fine (all dims, +-30 ticks)
            rcs = rc.resonate(v[low], [sym[:, low], dial(grid)[:, low]], max_iter=50, seed=0)["positions"]
            s_hat, th_c = rcs[0], int(grid[rcs[1]])
            u = v * sym[s_hat].conj()
            cand = np.arange(max(0, th_c - 30), min(T, th_c + 31))
            sc = (dial(cand).conj() @ u).real
            th_hat = int(cand[int(np.argmax(sc))])
            ctf_ok += any(s_hat == s and abs(th_hat - th) <= 1 for s, th in members)
        out[M] = (flat_ok, ctf_ok)
    f1, c1n = out[1]
    _, lo, _ = wil(c1n, trials)
    ok1, ok2 = lo >= 0.80, f1 / trials < 0.5
    verdict = "PASS" if ok1 and ok2 else "KILL"
    why = f"M=1 coarse-to-fine {fmt(c1n, trials)} ({'ok' if ok1 else 'fail'}); flat {fmt(f1, trials)} ({'ok' if ok2 else 'fail'})"
    lines = ["| M items in slot | flat resonator (1,000 dial positions) | coarse-to-fine |", "|---|---|---|"]
    for M, (f, c) in out.items():
        lines.append(f"| {M} | {fmt(f, trials)} | {fmt(c, trials)} |")
    lines.append(f"\nlow-frequency dims used for the coarse pass: {int(low.sum())} of {D}; kernel width L = {L} ticks; dial {T} ticks; {S} symbols.")
    return verdict, why, "\n".join(lines)


TESTS = {"DIAMOND": diamond, "PEEL": peel, "CORREL": correl, "TABU": tabu, "FRET": fret}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--only")
    ap.add_argument("--trials", type=int)
    ap.add_argument("--out")
    a = ap.parse_args()
    trials = a.trials or (20 if a.quick else 150)
    names = a.only.split(",") if a.only else list(TESTS)
    report = [f"# RING-3 results (seat-run, {time.strftime('%Y-%m-%d %H:%M')}, {trials} trials per cell, D = {D})\n"]
    summary = []
    for nm in names:
        t0 = time.time()
        v, why, table = TESTS[nm](trials)
        dt = time.time() - t0
        print(f"== {nm}: {v} -- {why} ({dt:.0f}s)\n{table}\n", flush=True)
        summary.append(f"| {nm} | {v} | {why} |")
        report.append(f"## {nm}: {v}\n**Pre-registered:** {PREREG[nm]}\n\n**Result:** {why} ({dt:.0f} s)\n\n{table}\n")
    if a.out and not a.quick:
        Path(a.out).write_text(report[0] + "\n| test | verdict | reason |\n|---|---|---|\n" + "\n".join(summary) + "\n\n" + "\n".join(report[1:]))
        print("wrote", a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

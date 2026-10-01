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
               "centre checksum ring flags >= 50% of wrong settles (pooled over M in {12, 24}). Otherwise KILL.",
    "PEEL": "[revised after smoke: cued readout] PASS if, at M = 24, two 13-ring clamp sweeps WITH explaining-away (subtract "
            "each accepted mark) recover >= 1.25x the true marks of one plain sweep, with accepted fakes Wilson-99% upper "
            "bound <= 0.05. Otherwise KILL.",
    "CORREL": "PASS if plain recall at rho = 0.3 falls >= 0.20 below plain recall at rho = 0 (similar codebooks hurt), AND "
              "the listener fix (whitened scores) at rho = 0.3 is within 0.10 of plain recall at rho = 0. Otherwise KILL "
              "(state which half failed).",
    "TABU": "[revised: stuck = settle illegal under the 17 ring OR not converged] PASS if, over stuck trials pooled over "
            "M in {12, 24, 48}, knockout+consensus rescues (accepts the correct target) >= 50% of them, with silent-wrong "
            "accepts <= 2% of stuck trials (Wilson-99% upper bound <= 0.05). Otherwise KILL.",
    "FRET": "[revised: crowded near-identical cell decides] PASS if, at M = 12 items with angles clustered within 60 ticks, "
            "coarse-to-fine's any-member symbol+angle (|err| <= 1) Wilson-99% lower bound exceeds the flat resonator's point "
            "rate by >= 0.20. Otherwise KILL.",
}


def wil(k, n):
    p, lo, hi = rc.wilson(k, n, Z99)
    return p, lo, hi


def fmt(k, n):
    p, lo, hi = wil(k, n)
    return f"{k}/{n} = {p:.1%} [{lo:.1%}, {hi:.1%}]"


# ------------------------------------------------------------------ generic resonator (masks + annealing)
def res_general(v, cbs, clamp=None, max_iter=50, power=lambda it: 1.0, masks=None, whiten=None):
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
            if whiten is not None:
                s = whiten[i] @ s
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


# ------------------------------------------------------------------ helpers
def rand_cb(m, rng):
    return np.exp(1j * rng.uniform(-np.pi, np.pi, (m, D)))


def bind_rows(cbs, idx):
    e = np.ones(D, complex)
    for cb, k in zip(cbs, idx):
        e = e * cb[k]
    return e


# ------------------------------------------------------------------ DIAMOND (category corners + centre checksum)
def diamond(trials, seed=11, K=105, C=17):
    rng = np.random.default_rng(seed)
    corners = [rand_cb(K, rng) for _ in range(4)]
    centre = rand_cb(C, rng)
    cbs = corners + [centre]
    out = {}
    for M in (12, 24):
        ok = wrong = flagged = 0
        its = []
        for _ in range(trials):
            marks = [tuple(int(x) for x in rng.integers(0, K, 4)) for _ in range(M)]
            v = sum(bind_rows(cbs, list(mk) + [sum(mk) % C]) for mk in marks)
            t = marks[0]
            r = res_general(v, cbs, clamp={0: t[0], 1: t[1]}, max_iter=50)
            its.append(r["iters"])
            p = r["positions"]
            if (p[2], p[3]) == (t[2], t[3]):
                ok += 1
            else:
                wrong += 1
                flagged += p[4] != (t[0] + t[1] + p[2] + p[3]) % C
        out[M] = (ok, wrong, flagged, float(np.median(its)))
    rings = rc.make_rings(MODS_C, D, seed=21, quant="float")
    frng = np.random.default_rng(seed + 2)
    flat = {}
    for M in (12, 24):
        ok = 0
        for _ in range(trials):
            xs = [int(x) for x in frng.integers(0, N, M)]
            v = rc.make_slot(xs, rings, MODS_C)
            t = xs[0]
            r = rc.resonate(v, rings, clamp={3: t % 13, 2: t % 7}, max_iter=50, seed=0)["positions"]
            ok += val4(r) == t and legal5(r)
        flat[M] = ok
    _, lo, _ = wil(out[12][0], trials)
    flat_p = flat[12] / trials
    wr = sum(out[M][1] for M in out); fl = sum(out[M][2] for M in out)
    c1, c2 = lo >= flat_p, (fl / wr if wr else 1.0) >= 0.5
    verdict = "PASS" if c1 and c2 else "KILL"
    why = (f"diamond lower {lo:.3f} vs flat {flat_p:.3f} ({'ok' if c1 else 'fail'}); centre checksum flags {fl}/{wr} "
           f"wrong settles ({'ok' if c2 else 'fail'})")
    lines = ["| system | M | recall of both unknown corners (2 known) | wrong settles flagged by centre | median iters |",
             "|---|---|---|---|---|"]
    for M, (ok, w, f, mi) in out.items():
        lines.append(f"| diamond: 4 category corners x {K} + centre checksum {C} | {M} | {fmt(ok, trials)} | {f}/{w} | {mi:.0f} |")
    for M, ok in flat.items():
        lines.append(f"| flat (3,5,7,13)+17 rotation rings, 2 clamps | {M} | {fmt(ok, trials)} | n/a | n/a |")
    return verdict, why, "\n".join(lines)


# ------------------------------------------------------------------ PEEL (cued sweeps, explaining away)
def sweep(v, rings, members, peel_on, power=lambda it: 1.0):
    found, fakes, acc = set(), 0, 0
    for r13 in range(13):
        r = res_general(v, rings, clamp={3: r13}, max_iter=50, power=power)["positions"]
        if not legal5(r):
            continue
        x = val4(r)
        acc += 1
        if x in members:
            found.add(x)
        else:
            fakes += 1
        if peel_on:
            v = v - rc.encode(x, rings, MODS_C)
    return found, fakes, acc, v


def peel(trials, seed=21):
    rings = rc.make_rings(MODS_C, D, seed=seed, quant="float")
    rng = np.random.default_rng(seed + 1)
    arms = ("plain 1 sweep", "peel 2 sweeps", "peel 2 sweeps annealed")
    anneal = lambda it: min(4.0, 1.0 + 0.5 * (it - 1))  # noqa: E731
    res = {}
    for M in (12, 24):
        tot = {a: [0, 0, 0] for a in arms}
        for _ in range(trials):
            xs = [int(x) for x in rng.choice(N, M, replace=False)]
            mem = set(xs)
            v = rc.make_slot(xs, rings, MODS_C)
            f, fk, ac, _ = sweep(v, rings, mem, False)
            tot[arms[0]] = [tot[arms[0]][0] + len(f), tot[arms[0]][1] + fk, tot[arms[0]][2] + ac]
            for a, pw in ((arms[1], lambda it: 1.0), (arms[2], anneal)):
                f1, fk1, ac1, vr = sweep(v, rings, mem, True, pw)
                f2, fk2, ac2, _ = sweep(vr, rings, mem, True, pw)
                tot[a] = [tot[a][0] + len(f1 | f2), tot[a][1] + fk1 + fk2, tot[a][2] + ac1 + ac2]
        res[M] = tot
    base = res[24][arms[0]][0]
    best = max(arms[1:], key=lambda a: res[24][a][0])
    tr, fk, ac = res[24][best]
    _, _, hi = wil(fk, ac)
    c1, c2 = tr >= 1.25 * base, hi <= 0.05
    verdict = "PASS" if c1 and c2 else "KILL"
    why = (f"M=24: '{best}' {tr / trials:.2f} vs plain {base / trials:.2f} true marks/slot ({'ok' if c1 else 'fail'}); "
           f"fakes {fk}/{ac} upper {hi:.3f} ({'ok' if c2 else 'fail'})")
    lines = ["| M | arm | true marks recovered / slot | accepted fakes / accepted |", "|---|---|---|---|"]
    for M in res:
        for a in arms:
            tr, fk, ac = res[M][a]
            lines.append(f"| {M} | {a} | {tr / trials:.2f} (of {M}) | {fk}/{ac} |")
    return verdict, why, "\n".join(lines)


# ------------------------------------------------------------------ CORREL (neighbour-chained similarity; tune the listener)
def chain_cb(m, rho, rng):
    cb = np.empty((m, D), complex)
    cb[0] = np.exp(1j * rng.uniform(-np.pi, np.pi, D))
    for k in range(1, m):
        mix = math.sqrt(rho) * cb[k - 1] + math.sqrt(1 - rho) * np.exp(1j * rng.uniform(-np.pi, np.pi, D))
        cb[k] = mix / np.abs(mix)
    return cb


def correl(trials, seed=31):
    rows, rec = [], {}
    for rho in (0.0, 0.3, 0.6, 0.8):
        rng = np.random.default_rng(seed)
        cbs = [chain_cb(m, rho, rng) for m in MODS_C]
        W = []
        for cb in cbs:
            G = (cb.conj() @ cb.T).real / D
            W.append(np.linalg.pinv(G))
        nb = float(np.mean([((cb[1:].conj() * cb[:-1]).sum(1).real / D).mean() for cb in cbs]))
        for arm, wh in (("plain", None), ("listener-whitened", W)):
            trng = np.random.default_rng(seed + 5)
            ok = 0
            for _ in range(trials):
                xs = [int(x) for x in trng.integers(0, N, 4)]
                v = sum(bind_rows(cbs, [x % m for m in MODS_C]) for x in xs)
                t = xs[0]
                r = res_general(v, cbs, clamp={3: t % 13}, max_iter=50, whiten=wh)["positions"]
                ok += val4(r) == t and legal5(r)
            rec[(rho, arm)] = ok / trials
            rows.append(f"| {rho} | {nb:.2f} | {arm} | {fmt(ok, trials)} |")
    r_hi = 0.6 if (0.6, "plain") in rec else 0.3
    drop = rec[(0.0, "plain")] - rec[(0.3, "plain")]
    gap = rec[(0.0, "plain")] - rec[(0.3, "listener-whitened")]
    c1, c2 = drop >= 0.20, gap <= 0.10
    verdict = "PASS" if c1 and c2 else "KILL"
    why = (f"plain drop rho 0->0.3 = {drop:+.2f} ({'ok' if c1 else 'fail'}); whitened@0.3 vs plain@0 = {-gap:+.2f} "
           f"({'ok' if c2 else 'fail'}); plain@0.6 {rec[(0.6, 'plain')]:.2f}, whitened@0.6 {rec[(0.6, 'listener-whitened')]:.2f}")
    return verdict, why, ("| rho | measured neighbour similarity | read | target recall, M=4, 13 ring clamped |\n|---|---|---|---|\n"
                          + "\n".join(rows))


# ------------------------------------------------------------------ TABU (knockout + consensus on stuck settles)
def tabu(trials, seed=41):
    rings = rc.make_rings(MODS_C, D, seed=seed, quant="float")
    rng = np.random.default_rng(seed + 1)
    stuck = rescued = silent = own_ok = 0
    per = {}
    for M in (12, 24, 48):
        s_M = r_M = w_M = 0
        for _ in range(trials):
            xs = [int(x) for x in rng.integers(0, N, M)]
            v = rc.make_slot(xs, rings, MODS_C)
            t = xs[0]
            clamp = {3: t % 13}
            r0 = res_general(v, rings, clamp=clamp, max_iter=50)
            p0 = r0["positions"]
            if r0["converged"] and legal5(p0):
                continue
            s_M += 1
            answers = []
            for ks in ([0], [1], [2], [4], [0, 1], [2, 4], [1, 2]):
                masks = {}
                for i in ks:
                    mk = np.ones(MODS_C[i]); mk[p0[i]] = 0.0
                    masks[i] = mk
                rr = res_general(v, rings, clamp=clamp, max_iter=50, masks=masks)["positions"]
                if legal5(rr):
                    answers.append(val4(rr))
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
           f"silent-wrong {silent} (upper {hi:.3f}, {'ok' if c2 else 'fail'})")
    lines = [f"| M | stuck (illegal or not converged, of {trials}) | rescued (correct target accepted) | silent-wrong accepted |",
             "|---|---|---|---|"]
    for M, (s_, r_, w_) in per.items():
        lines.append(f"| {M} | {s_} | {fmt(r_, s_) if s_ else '0/0'} | {fmt(w_, s_) if s_ else '0/0'} |")
    return verdict, why, "\n".join(lines)


# ------------------------------------------------------------------ FRET (symbol x continuous dial)
def fret(trials, seed=51, L=8.0, T=1000, S=20):
    rng = np.random.default_rng(seed)
    sym = rand_cb(S, rng)
    omega = rng.uniform(-2 * np.pi / L, 2 * np.pi / L, D)
    dial = lambda th: np.exp(1j * np.outer(np.atleast_1d(th), omega))  # noqa: E731
    P_full = dial(np.arange(T))
    low = np.abs(omega) < (2 * np.pi / (L * 8))
    grid = np.arange(0, T, 20)
    out = {}
    trng = np.random.default_rng(seed + 1)
    for M, clustered in ((1, False), (3, False), (6, True), (12, True)):
        flat_ok = ctf_ok = 0
        for _ in range(trials):
            if clustered:
                c0 = int(trng.integers(0, T - 60))
                items = [(int(trng.integers(0, S)), c0 + int(trng.integers(0, 60))) for _ in range(M)]
            else:
                items = [(int(trng.integers(0, S)), int(trng.integers(0, T))) for _ in range(M)]
            v = sum(sym[s] * dial(th)[0] for s, th in items)
            r = res_general(v, [sym, P_full], max_iter=50)["positions"]
            flat_ok += any(r[0] == s and abs(r[1] - th) <= 1 for s, th in items)
            rcs = res_general(v[low], [sym[:, low], dial(grid)[:, low]], max_iter=50)["positions"]
            s_hat, th_c = rcs[0], int(grid[rcs[1]])
            u = v * sym[s_hat].conj()
            cand = np.arange(max(0, th_c - 30), min(T, th_c + 31))
            th_hat = int(cand[int(np.argmax((dial(cand).conj() @ u).real))])
            ctf_ok += any(s_hat == s and abs(th_hat - th) <= 1 for s, th in items)
        out[(M, clustered)] = (flat_ok, ctf_ok)
    f12, c12 = out[(12, True)]
    _, lo, _ = wil(c12, trials)
    ok = lo >= f12 / trials + 0.20
    verdict = "PASS" if ok else "KILL"
    why = f"M=12 clustered: coarse-to-fine {fmt(c12, trials)} vs flat {fmt(f12, trials)} ({'ok' if ok else 'fail'})"
    lines = ["| M items | angles | flat resonator (1,000 dial positions) | coarse-to-fine |", "|---|---|---|---|"]
    for (M, cl), (f, c) in out.items():
        lines.append(f"| {M} | {'clustered within 60 ticks' if cl else 'uniform'} | {fmt(f, trials)} | {fmt(c, trials)} |")
    lines.append(f"\ncoarse pass: {int(low.sum())} of {D} low-frequency dims on a 20-tick grid; kernel width L = {L}; dial {T} ticks; {S} symbols.")
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

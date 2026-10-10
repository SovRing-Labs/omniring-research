#!/usr/bin/env python3
"""ramkit #7 — checkpoint soup + time machine (RAM-KIT-0, J 10-08).
Soup: average k round cores (ckpt.bin = every parameter as float32 LE, back to back, in ckpt.json's order — runtime/src/thead.rs save()).
Uniform = par_merge.py's math exactly (float64 accumulate, divide by k, cast to float32); EMA = s ← (1−α)s + α·w_i in float64, oldest first.
Streams one core at a time: RAM = one float64 accumulator (2× a core) + one core (27 MB core → ~85 MB).
The soup dir gets ckpt.bin + the last core's ckpt.json / state.json (so `thead-learn` / skill_eval load it like any core) + soup.json.
Time machine: per skill across rounds (skill.json files) — first round at gate, rounds it slipped after that, best, last.

  soup.py make <out_dir> <core_dir …(oldest first)> [--ema ALPHA]
  soup.py history <skill.json …(round order)> [--out FILE] [--gate 0.85]
  soup.py selftest"""
import argparse, json, os, shutil, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C


def soup(out, cores, ema=None):
    idx0 = json.load(open(os.path.join(cores[0], "ckpt.json")))
    acc = None
    for i, c in enumerate(cores):
        if json.load(open(os.path.join(c, "ckpt.json"))) != idx0: raise ValueError(f"{c}: ckpt.json layout differs from {cores[0]}")
        w = np.fromfile(os.path.join(c, "ckpt.bin"), dtype=np.float32)
        if acc is None:
            acc = w.astype(np.float64)
        elif ema is None:
            acc += w                                                   # = np.add.reduce over axis 0, row after row (par_merge's np.mean)
        else:
            acc *= (1.0 - ema); acc += ema * w.astype(np.float64)
        del w
    if ema is None: acc /= len(cores)
    M = acc.astype(np.float32); del acc
    os.makedirs(out, exist_ok=True)
    M.tofile(os.path.join(out, "ckpt.bin.tmp")); os.replace(os.path.join(out, "ckpt.bin.tmp"), os.path.join(out, "ckpt.bin"))
    for f in ("ckpt.json", "state.json"):
        if os.path.exists(os.path.join(cores[-1], f)): shutil.copy(os.path.join(cores[-1], f), os.path.join(out, f))
    meta = {"cores": [os.path.abspath(c) for c in cores], "mode": "uniform" if ema is None else f"ema {ema}", "params": int(M.size),
            "sha256": C.sha_file(os.path.join(out, "ckpt.bin")), "inputs_sha256": [C.sha_file(os.path.join(c, "ckpt.bin")) for c in cores]}
    C.json_out(meta, os.path.join(out, "soup.json"))
    return meta


def history(skill_files, gate=0.85):
    h = {}
    for r, f in enumerate(skill_files, 1):
        for k, v in json.load(open(f))["skill"].items(): h.setdefault(k, []).append((r, float(v)))
    out = {}
    for k, seq in sorted(h.items()):
        first = next((r for r, v in seq if v >= gate), None)
        slips = [r for r, v in seq if first is not None and r > first and v < gate]
        out[k] = {"first_at_gate": first, "slipped_rounds": slips, "best": max(v for _, v in seq), "last": seq[-1][1],
                  "last_round": seq[-1][0], "scores": [[r, v] for r, v in seq]}
    return {"rounds": len(skill_files), "skills": len(out), "gained": sum(1 for v in out.values() if v["first_at_gate"]),
            "ever_slipped": sum(1 for v in out.values() if v["slipped_rounds"]), "by_skill": out}


def selftest(out=None):
    import tempfile
    d = tempfile.mkdtemp(prefix="ramkit-soup-"); R = np.random.default_rng(7); n = 50_000
    idx = [{"name": "a", "offset": 0, "len": 30_000}, {"name": "b", "offset": 120_000, "len": 20_000}]
    W = [R.standard_normal(n).astype(np.float32) for _ in range(3)]
    for i, w in enumerate(W):
        os.makedirs(f"{d}/c{i}"); w.tofile(f"{d}/c{i}/ckpt.bin"); json.dump(idx, open(f"{d}/c{i}/ckpt.json", "w"))
    os.makedirs(f"{d}/same1"); shutil.copy(f"{d}/c0/ckpt.bin", f"{d}/same1/ckpt.bin"); shutil.copy(f"{d}/c0/ckpt.json", f"{d}/same1/")
    soup(f"{d}/s_same", [f"{d}/c0", f"{d}/same1", f"{d}/c0"])
    same = open(f"{d}/s_same/ckpt.bin", "rb").read() == open(f"{d}/c0/ckpt.bin", "rb").read()
    soup(f"{d}/s_uni", [f"{d}/c{i}" for i in range(3)])
    ref = np.mean(W, axis=0, dtype=np.float64).astype(np.float32)            # par_merge.py line 16, verbatim math
    uni = np.array_equal(np.fromfile(f"{d}/s_uni/ckpt.bin", np.float32).view(np.uint32), ref.view(np.uint32))
    soup(f"{d}/s_ema", [f"{d}/c{i}" for i in range(3)], ema=0.5)
    e = W[0].astype(np.float64); e = 0.5 * e + 0.5 * W[1]; e = 0.5 * e + 0.5 * W[2]
    ema_ok = np.array_equal(np.fromfile(f"{d}/s_ema/ckpt.bin", np.float32), e.astype(np.float32))
    res = {"identical_cores_byte_equal": same, "uniform_equals_par_merge_bitwise": bool(uni), "ema_equals_reference": bool(ema_ok)}
    # real cores (read-only): round-1 harness cores of the live school copy, if on disk — soup vs par_merge math on 27 MB cores
    real = sorted(os.path.join(C.TRIAL, "runtime/results/pod-live-r1/live-r1", h) for h in os.listdir(os.path.join(C.TRIAL, "runtime/results/pod-live-r1/live-r1"))
                  if h.startswith("h") and os.path.exists(os.path.join(C.TRIAL, "runtime/results/pod-live-r1/live-r1", h, "ckpt.bin"))) \
        if os.path.isdir(os.path.join(C.TRIAL, "runtime/results/pod-live-r1/live-r1")) else []
    if len(real) >= 2:
        cs = real[:4]; m = soup(f"{d}/s_real", cs)
        Wr = [np.fromfile(f"{c}/ckpt.bin", np.float32) for c in cs]
        refr = np.mean(Wr, axis=0, dtype=np.float64).astype(np.float32)
        res["real"] = {"cores": [os.path.relpath(c, C.TRIAL) for c in cs], "params": m["params"],
                       "equals_par_merge_bitwise": bool(np.array_equal(np.fromfile(f"{d}/s_real/ckpt.bin", np.float32).view(np.uint32), refr.view(np.uint32))),
                       "rms_core_to_soup": round(float(np.mean([np.sqrt(np.mean((w - refr) ** 2)) for w in Wr])), 6)}
        del Wr, refr
        uni = uni and res["real"]["equals_par_merge_bitwise"]
    live = os.path.join(C.TRIAL, "runtime/results/live-school")
    sk = [f"{live}/r{i}/skill.json" for i in range(1, 50) if os.path.exists(f"{live}/r{i}/skill.json")]
    if sk:
        H = history(sk); res["time_machine_live"] = {k: H[k] for k in ("rounds", "skills", "gained", "ever_slipped")}
    res["rss_mb"] = C.rss_mb()
    shutil.rmtree(d, ignore_errors=True)
    if out: C.json_out(res, out)
    return bool(same and uni and ema_ok), res


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="c", required=True)
    m = sp.add_parser("make"); m.add_argument("out"); m.add_argument("cores", nargs="+"); m.add_argument("--ema", type=float)
    h = sp.add_parser("history"); h.add_argument("skills", nargs="+"); h.add_argument("--out"); h.add_argument("--gate", type=float, default=0.85)
    s = sp.add_parser("selftest"); s.add_argument("--out")
    a = ap.parse_args()
    if a.c == "make": print(json.dumps(soup(a.out, a.cores, a.ema)))
    elif a.c == "history":
        r = history(a.skills, a.gate); print(C.json_out(r, a.out) if a.out else json.dumps({k: r[k] for k in ("rounds", "skills", "gained", "ever_slipped")}))
    else:
        ok, res = selftest(a.out); print(json.dumps(res)); print("PASS" if ok else "FAIL", "soup"); sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

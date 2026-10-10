#!/usr/bin/env python3
"""CYCLONE-ARRAY W2d gate — the harness → model feed and the model → cyclone event stream, chained on the GPU in ONE recorded step:
  feed_win  every harness cuts its batch (B windows × T positions) from the curriculum resident in VRAM: x · y · plate kind · proposal · stage
            (== runtime/src/thead.rs Build::win + win_stage, compared on every position)
  ev_build  every window's trunk T25 events [position · token · plate · level · row] (row = EOS count before the position)
  ring_addr ×2  each harness's events on its T25 bus (ledger per harness) and on its unit's T50 cyclone (ledger per unit)
            (== the runtime's rendered T25 core / the Program64::t50 layout, as W2a)
Curriculum: the tier-1 build tier1-prek-v4-s6400 (every phase uploaded once); one floor = 5 units × 8 harnesses × 4 windows × 512.
Run OUTSIDE kernel-bash Landlock (systemd-run / tw unit) for the Intel device.   w2d_feed.py [--devices llvmpipe,Intel] [--out DIR]"""
import hashlib, json, os, subprocess, sys, tempfile
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from w2a_ring_addr import T25, program, t50_groups, rendered_t25, scalar, BIN, BUILD, P
K = {k: f"{P}/kernels/{k}.spv" for k in ("feed_win", "ev_build", "ring_addr")}
UNITS, PER, B, CTX, EOS = 5, 8, 4, 512, 0

def curriculum():
    man = json.load(open(f"{BUILD}/manifest.json")); d, kd, st, mk, base = [], [], [], [], []
    o = 0
    for k, p in enumerate(man["phases"]):
        x = np.fromfile(f"{BUILD}/{p['file']}", dtype="<u2").astype(np.uint32); n = len(x)
        kind = np.fromfile(f"{BUILD}/kind_{k}.u8", dtype=np.uint8).astype(np.uint32)
        sp = f"{BUILD}/stage_{k}.u8"; mp = f"{BUILD}/mask_{k}.u8"
        s = np.full(n, -1, np.int32); m = np.zeros(n, np.uint32)
        if os.path.exists(sp): v = np.fromfile(sp, np.uint8); s[:len(v)] = v[:n]
        if os.path.exists(mp): v = np.fromfile(mp, np.uint8); m[:len(v)] = v[:n]
        d.append(x); kd.append(kind[:n]); st.append(s); mk.append(m); base.append(o); o += n
    return [np.concatenate(a) for a in (d, kd, st, mk)] + [base, [len(x) for x in d]]

def main():
    a = sys.argv[1:]; opt = lambda k, v: a[a.index(k) + 1] if k in a else v
    devices = opt("--devices", "llvmpipe,Intel").split(","); out = opt("--out", f"{P}/results/cyclone/w2d"); os.makedirs(out, exist_ok=True)
    d, kd, st, mk, base, lens = curriculum(); rng = np.random.default_rng(20261008)
    nwin = UNITS * PER * B; phs = rng.integers(len(lens), size=nwin); offs = np.array([rng.integers(lens[p] - CTX - 1) for p in phs])
    start = np.array([base[p] + o for p, o in zip(phs, offs)], np.uint32); level = phs.astype(np.uint32)
    # reference feed: Build::win + win_stage, position by position
    s = start[:, None].astype(np.int64) + np.arange(CTX)[None]
    x = d[s].astype(np.int64); nxt = d[s + 1].astype(np.int64)
    y = np.where(mk[s] == 1, -1, nxt); none = kd[s] == 255; k = np.where(none, -1, kd[s].astype(np.int64)); p = np.where(none, -1, nxt); sg = st[s].astype(np.int64)
    feed_ref = np.stack([x, y, k, p, sg], -1).reshape(-1, 5)
    row = np.concatenate([np.zeros((nwin, 1), np.int64), np.cumsum(x[:, :-1] == EOS, axis=1)], 1)
    h = np.repeat(np.arange(nwin) // B, CTX); u = h // PER
    ev_ref = np.stack([np.tile(np.arange(CTX), nwin), x.ravel(), np.where(k.ravel() >= 0, k.ravel(), 36), np.repeat(level, CTX), row.ravel(), u, h, np.zeros(nwin * CTX, np.int64)], -1)
    n = len(ev_ref); coords = ev_ref[:, :5]
    r25, _ = rendered_t25(coords)
    fails, cases = [], []
    with tempfile.TemporaryDirectory(prefix="omni-gpu-w2d-") as Tm:
        d.tofile(f"{Tm}/d.bin"); kd.tofile(f"{Tm}/k.bin"); st.tofile(f"{Tm}/s.bin"); mk.tofile(f"{Tm}/m.bin"); start.tofile(f"{Tm}/w.bin"); level.tofile(f"{Tm}/l.bin")
        tabs = {}
        for name, groups in (("T25", T25), ("T50", t50_groups())):
            mods, field, off = program(groups); tab = np.zeros(133, np.uint32); tab[:len(mods)] = mods; tab[64:64 + len(mods)] = field
            tab[128:133] = np.array(off, np.int64).astype(np.int32).view(np.uint32); tab.tofile(f"{Tm}/tab{name}.bin"); tabs[name] = (mods, field, off)
        gx = 4096; gy = -(-n // gx); fg = -(-n // 64)
        prog = [f"buf file {Tm}/d.bin", f"buf file {Tm}/k.bin", f"buf file {Tm}/s.bin", f"buf file {Tm}/m.bin", f"buf file {Tm}/w.bin", f"buf file {Tm}/l.bin",   # 0–5
                f"buf zero {n * 20}", f"buf zero {n * 32}",                                                                                             # 6 feed · 7 events
                f"buf file {Tm}/tabT25.bin", f"buf file {Tm}/tabT50.bin", f"buf zero {n * 256}",                                                          # 8, 9 tables · 10 zero plates
                f"buf zero {n * 256}", f"buf zero {n * 256}", f"buf zero {UNITS * PER * 64 * 256 * 4}", f"buf zero {n * 8}",                            # 11–14 T25 res tw ledger dev
                f"buf zero {n * 256}", f"buf zero {n * 256}", f"buf zero {UNITS * 64 * 256 * 4}", f"buf zero {n * 8}",                                  # 15–18 T50 res tw ledger dev
                f"buf zero {n * 32}",                                                                                                                   # 19 events keyed by harness
                f"pass {K['feed_win']} {min(fg, 65535)},{-(-fg // 65535)},1 spec 1={CTX} bind 0 1 2 3 4 6",
                f"pass {K['ev_build']} {-(-nwin // 64)},1,1 spec 1={CTX} 2={B} 3=1 4={EOS} bind 6 5 19",                                                # unit field = harness (T25 bus per harness)
                f"pass {K['ev_build']} {-(-nwin // 64)},1,1 spec 1={CTX} 2={B} 3={PER} 4={EOS} bind 6 5 7",                                              # unit field = unit (T50 cyclone per unit)
                f"pass {K['ring_addr']} {gx},{gy},1 spec 1=25 bind 19 8 10 11 12 13 14",
                f"pass {K['ring_addr']} {gx},{gy},1 spec 1=50 bind 7 9 10 15 16 17 18",
                "read 6", "read 7", "read 11", "read 13", "read 15", "read 17"]
        open(f"{Tm}/prog.txt", "w").write("\n".join(prog) + "\n")
        m25, f25, o25 = tabs["T25"]; m50, f50, o50 = tabs["T50"]
        ref50 = scalar(coords, m50, f50, o50)
        led25 = np.zeros((UNITS * PER, 64, 256), np.int64); led50 = np.zeros((UNITS, 64, 256), np.int64)
        for kk in range(25): np.add.at(led25, (h, kk, r25[:, kk].astype(np.int64)), 1)
        for kk in range(50): np.add.at(led50, (u, kk, ref50[:, kk]), 1)
        for dev in devices:
            od = f"{Tm}/o-{dev}"; case = {"device": dev, "harnesses": UNITS * PER, "units": UNITS, "windows": nwin, "events": n, "passes": 5}
            r = subprocess.run([BIN, "session", f"{Tm}/prog.txt", "--device", dev, "--steps", "1", "--out", od], capture_output=True, text=True, timeout=900)
            if r.returncode: case["error"] = r.stderr[-400:]; fails.append(f"{dev}: {case['error']}"); cases.append(case); continue
            info = json.loads(r.stdout.strip().splitlines()[-1])
            feed = np.fromfile(f"{od}/buf6.bin", np.int32).reshape(-1, 5); ev = np.fromfile(f"{od}/buf7.bin", np.int32).reshape(-1, 8)
            g25 = np.fromfile(f"{od}/buf11.bin", np.uint32).reshape(n, 64); gl25 = np.fromfile(f"{od}/buf13.bin", np.uint32).reshape(UNITS * PER, 64, 256)
            g50 = np.fromfile(f"{od}/buf15.bin", np.uint32).reshape(n, 64); gl50 = np.fromfile(f"{od}/buf17.bin", np.uint32).reshape(UNITS, 64, 256)
            case.update({"device_name": info["device"], "gpu_ms": info["gpu_ms_last"], "bytes_resident": info["bytes"],
                         "feed_mismatches": int((feed != feed_ref).sum()), "event_mismatches": int((ev != ev_ref).sum()),
                         "t25_residue_mismatches": int((g25[:, :25] != r25[:, :25]).sum()), "t25_ledger_mismatches": int((gl25 != led25).sum()),
                         "t50_residue_mismatches": int((g50[:, :50] != ref50).sum()), "t50_ledger_mismatches": int((gl50 != led50).sum())})
            bad = {kk: v for kk, v in case.items() if kk.endswith("mismatches") and v}
            if bad: fails.append(f"{dev}: {bad}")
            cases.append(case); print(json.dumps(case), flush=True)
    rep = {"gate": "CYCLONE-ARRAY W2d feed + events + T25/T50 addressing chained on the GPU", "build": BUILD,
           "kernels": {k: hashlib.sha256(open(v, "rb").read()).hexdigest()[:12] for k, v in K.items()}, "cases": cases, "fails": fails, "pass": not fails}
    json.dump(rep, open(f"{out}/feed.json", "w"), indent=1)
    print("PASS" if not fails else "FAIL: " + "; ".join(fails)); sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()

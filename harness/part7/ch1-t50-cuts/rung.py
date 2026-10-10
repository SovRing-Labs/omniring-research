#!/usr/bin/env python3
"""CYCLONE-ARRAY rung gate (W1 layout + W2 wiring) — runs a PRESET of the deployable (`omni-gpu cyclone --preset …`, kernels embedded) and
checks every stream it produces against the CPU references; writes the rung's record with the defining parts. A preset stays in the exe
only while its rung passes here.
  G1  1 cyclone + 1 harness/model   · G4  1 cyclone + 4 pairs   · G8  1 unit (cyclone + 8 pairs)   · G40  1 floor (centre unit + 4 around, ring)
Checked per run: the feed (== runtime/src/thead.rs Build::win + win_stage, windows drawn by the harness's own splitmix), the T25 ledger of
every harness bus (== the runtime's rendered T25 core), the T50 ledger of every unit cyclone (== Program64::t50), every weight after the
coupling + ring (== bus_coord.py / shmbus.rs arithmetic, bit for bit), over --steps recorded steps.
Weights: real school checkpoints (pod-cpu32b/live-r14/h0..h7 first, then the other school-shape ckpt.bin files, sorted); --slab N = the first N
floats of each (laptop), --slab full = all 6,926,912; --full-state also allocates every model's measured training state (C0).
  rung.py G8 [--device D] [--steps 2] [--slab 1048576|full] [--full-state] [--out DIR]      (data roots: CYCLONE_THEAD / _RESULTS / _CORE)"""
import glob, hashlib, json, os, subprocess, sys, tempfile, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from w2a_ring_addr import T25, program, t50_groups, rendered_t25, scalar, BIN, BUILD, P
from w2b_hub import mean_ref, pull_ref, R as RESULTS, NW
from w2d_feed import curriculum
RUNGS = {"G1": (1, 1, 1), "G4": (1, 1, 4), "G8": (1, 1, 8), "G40": (1, 5, 8), "G120": (3, 5, 8)}   # (floors, units per floor, pairs per unit)
B, CTX, EOS, KM, K2, K2C, SEED, M64 = 4, 512, 0, 0.35, 0.25, 0.10, 0x5EEDC7C1, (1 << 64) - 1

def splitmix(s):                                                   # runtime/src/thead.rs splitmix == omni-gpu cyclone::splitmix
    s = (s + 0x9E3779B97F4A7C15) & M64; z = s
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64; z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
    return s, z ^ (z >> 31)

def parts(units):
    return {"P1 T50 centre per unit": "PARTIAL — addressing + ledger + weight coupling on the GPU; the other precompute streams not yet",
            "P2 8 harnesses per unit": "PARTIAL — batch slicing + T25 bus on the GPU; HarnessCore / doing / judging still CPU",
            "P3 a model per harness, training on the GPU": "ABSENT — weights resident and coupled; no training step on the GPU yet",
            "P4 harnesses + models feed the cyclone": "PARTIAL — token events + weights flow into the hub",
            "P5 1 centre + 4 around": "PRESENT" if units % 5 == 0 else "n/a at this rung",
            "P6 units connected by the ring": "PARTIAL — the coupling stream crosses the ring; every item routes toroid → toroid by address" if units % 5 == 0 else "n/a at this rung",
            "P7 all resident in VRAM": "PARTIAL — everything that runs is resident; the training state only with --full-state",
            "routing (toroid → toroid by address)": ("PRESENT — every token event jumps ring by ring (CRT jump) to its home toroid" if units % 5 == 0 else "n/a at this rung")}

def cut_ref(rtab, vtab, dims, link, U):
    """G4c reference of cuts.spv (integer, same formula): 4 · min-cut headroom with C = 1.25 · busiest link = min over the separating
    trivial / ring cuts of 5·cnt·busiest − 4·crossing (tests/grow/g5_t50_cuts.py, Klavžar–Špacapan)"""
    D = len(dims); mx = max(int((link[q] + link[q].T).max()) for q in range(D)); deg = sum(S - 1 for _, S, _ in dims)
    triv = [5 * deg * mx - 4 * int(vtab[:D, v].sum()) for v in range(U)]
    out = np.zeros((U, U), np.float32)
    for s_ in range(U):
        for t_ in range(U):
            if s_ == t_: continue
            best = min(triv[s_], triv[t_])
            for q, (_, S, st) in enumerate(dims):
                cs, ct = (s_ // st) % S, (t_ // st) % S
                if cs == ct: continue
                for m in range(1, 2 ** S - 1):
                    A = [i for i in range(S) if m >> i & 1]
                    if cs not in A or ct in A: continue
                    cross = sum(int(rtab[q, i, j] + rtab[q, j, i]) for i in A for j in range(S) if j not in A)
                    best = min(best, 5 * len(A) * (S - len(A)) * (U // S) * mx - 4 * cross)
            out[s_, t_] = best
    return out

def gh_check(cut, link, dims, U):
    """the GPU's cut table vs Gomory–Hu on the same link ledger (networkx; −1 when networkx is absent)"""
    try: import networkx as nx
    except ImportError: return -1
    D = len(dims); mx = max(int((link[q] + link[q].T).max()) for q in range(D))
    G = nx.Graph()
    for q, (_, S, st) in enumerate(dims):
        for a_ in range(U):
            for b_ in range(a_ + 1, U):
                if all((a_ // o) % z == (b_ // o) % z for e, (_, z, o) in enumerate(dims) if e != q) and (a_ // st) % S != (b_ // st) % S:
                    G.add_edge(a_, b_, capacity=5 * mx - 4 * int(link[q][a_, b_] + link[q][b_, a_]))
    T_ = nx.gomory_hu_tree(G); bad = 0
    for s_ in range(U):
        for t_ in range(s_ + 1, U):
            path = nx.shortest_path(T_, s_, t_); w = min(T_[x][y]["weight"] for x, y in zip(path, path[1:]))
            bad += int(w != cut[s_, t_]) + int(w != cut[t_, s_])
    return bad

def main():
    a = sys.argv[1:]; rung = a[0]; opt = lambda k, v: a[a.index(k) + 1] if k in a else v
    F, UPF, PER = RUNGS[rung]; U = F * UPF; H = U * PER; dev = opt("--device", "llvmpipe"); steps = int(opt("--steps", "2")); slab = opt("--slab", "1048576")
    full_state = "--full-state" in a; out = opt("--out", f"{P}/results/cyclone/{rung}"); os.makedirs(out, exist_ok=True)
    W = NW if slab == "full" else int(slab)
    unit_files = [f"{RESULTS}/pod-cpu32b/live-r14/h{i}/ckpt.bin" for i in range(8)]
    pool = sorted(f for f in glob.glob(f"{RESULTS}/**/ckpt.bin", recursive=True) if os.path.getsize(f) == NW * 4)
    distinct = unit_files + [f for f in pool if f not in unit_files]
    files = [distinct[i % len(distinct)] for i in range(H)]                    # > len(distinct) models (G120): real checkpoints reused in rotation
    d, kd, st, mk, base, lens = curriculum(); nwin = H * B; n = nwin * CTX
    s = SEED; phs, offs = [], []
    for _ in range(nwin):
        s, z = splitmix(s); ph = z % len(lens); s, z = splitmix(s); phs.append(ph); offs.append(z % (lens[ph] - CTX - 1))
    phs = np.array(phs); start = np.array([base[p] + o for p, o in zip(phs, offs)], np.int64); level = phs
    # ── references ────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    sx = start[:, None] + np.arange(CTX)[None]; x = d[sx].astype(np.int64); nxt = d[sx + 1].astype(np.int64)
    none = kd[sx] == 255; k = np.where(none, -1, kd[sx].astype(np.int64))
    feed_ref = np.stack([x, np.where(mk[sx] == 1, -1, nxt), k, np.where(none, -1, nxt), st[sx].astype(np.int64)], -1).reshape(-1, 5)
    row = np.concatenate([np.zeros((nwin, 1), np.int64), np.cumsum(x[:, :-1] == EOS, axis=1)], 1)
    hh = np.repeat(np.arange(nwin) // B, CTX); uu = hh // PER
    coords = np.stack([np.tile(np.arange(CTX), nwin), x.ravel(), np.where(k.ravel() >= 0, k.ravel(), 36), np.repeat(level, CTX), row.ravel()], -1)
    r25, _ = rendered_t25(coords); m50, f50, o50 = program(t50_groups()); ref50 = scalar(coords, m50, f50, o50)
    led25 = np.zeros((H, 64, 256), np.int64); led50 = np.zeros((U, 64, 256), np.int64)
    for q in range(25): np.add.at(led25, (hh, q, r25[:, q].astype(np.int64)), steps)
    for q in range(50): np.add.at(led50, (uu, q, ref50[:, q]), steps)
    w0 = np.stack([np.fromfile(f, np.float32, count=W) for f in files]).reshape(U, PER, W)
    keep = np.ones((U, PER), np.uint32); kf = np.full((U, PER), KM, np.float32)
    if PER > 1: keep[U - 1, PER - 1] = 0; kf[U - 1, PER - 1] = 1.0
    kout = np.array([[0, 1, 1, 1, 1]], np.uint32); kcen = np.array([[1, 0, 0, 0, 0]], np.uint32)
    rko = np.array([[0, K2, K2, K2, K2]], np.float32); rkc = np.array([[K2C, 0, 0, 0, 0]], np.float32)
    wref = w0.copy()
    for _ in range(steps):
        means = mean_ref(wref, keep)
        if UPF == 5:                                                               # every floor's ring (floors do not couple weights)
            for fl in range(F):
                mf = means[fl * 5:(fl + 1) * 5]; tc = mean_ref(mf[None], kout); cc = mean_ref(mf[None], kcen)
                means[fl * 5:(fl + 1) * 5] = pull_ref(pull_ref(mf[None], cc, rko), tc, rkc)[0]
        wref = pull_ref(wref, means, kf)
    route = None
    if UPF == 5:                                                                   # W3: every item jumps toroid → toroid to its address
        lane_of = {m: q for q, m in enumerate(m50)}; dims = [(3, F, 5), (5, 5, 1)] if F > 1 else [(5, 5, 1)]
        home = np.zeros(n, np.int64); cur = uu.copy(); hops = np.zeros(n, np.int64); link = np.zeros((4, U, U), np.int64)
        for q, (ring, S, stride) in enumerate(dims):
            ch = ref50[:, lane_of[ring]] % S; home += ch * stride; cc_ = (cur // stride) % S; jump = cc_ != ch; nxt = cur - cc_ * stride + ch * stride
            np.add.at(link, (q, cur[jump], nxt[jump]), 1); cur = np.where(jump, nxt, cur); hops += jump
        rtab = np.zeros((4, 16, 16), np.int64); vtab = np.zeros((4, U), np.int64)          # G4c cut tables (route's own atomics)
        for q, (ring, S, stride) in enumerate(dims):
            fr, to = np.nonzero(link[q])
            np.add.at(rtab, (q, (fr // stride) % S, (to // stride) % S), link[q][fr, to] * steps)
            vtab[q] += (link[q].sum(1) + link[q].sum(0)) * steps
        cut = cut_ref(rtab, vtab, dims, link * steps, U)
        hled = np.zeros((U, 64, 256), np.int64)
        for q in range(50): np.add.at(hled, (home, q, ref50[:, q]), 1)
        route = {"home": home, "hops": hops, "link": link * steps, "hled": hled * steps, "inbox": np.bincount(home, minlength=U) * steps, "dims": dims,
                 "rtab": rtab, "vtab": vtab, "cut": cut}
    # ── the deployable's preset ───────────────────────────────────────────────────────────────────────────────────────────────────
    with tempfile.TemporaryDirectory(prefix=f"omni-gpu-{rung}-") as Tm:
        open(f"{Tm}/ckpts.txt", "w").write("\n".join(files) + "\n"); od = f"{Tm}/dump"; t0 = time.time()
        cmd = [BIN, "cyclone", "--preset", rung, "--build", BUILD, "--ckpts", f"{Tm}/ckpts.txt", "--device", dev, "--steps", str(steps),
               "--slab", "full" if slab == "full" else str(W), "--dump", od] + (["--full-state"] if full_state else [])
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        rec = {"rung": rung, "floors": F, "units": U, "pairs_per_unit": PER, "harnesses": H, "models": H, "device": dev, "steps": steps, "slab_floats": W,
               "full_state": full_state, "events_per_step": n, "windows_per_step": nwin, "exe": BIN, "exe_sha256": hashlib.sha256(open(BIN, "rb").read()).hexdigest()[:12],
               "command": " ".join(cmd[1:]), "parts": parts(U), "weights_files": files, "distinct_checkpoints": len(set(files))}
        fails = []
        if r.returncode: rec["error"] = r.stderr[-600:]; fails.append(rec["error"])
        else:
            info = json.loads(r.stdout.strip().splitlines()[-1])
            feed = np.fromfile(f"{od}/feed.bin", np.int32).reshape(-1, 5)
            g25 = np.fromfile(f"{od}/led25.bin", np.uint32).reshape(H, 64, 256); g50 = np.fromfile(f"{od}/led50.bin", np.uint32).reshape(U, 64, 256)
            wt = np.fromfile(f"{od}/wt.bin", np.float32).reshape(U, PER, W)
            rec.update({"device_name": info["device"], "passes": info["passes"], "buffers": info["buffers"], "bytes_resident": info["bytes_resident"],
                        "gb_resident": round(info["bytes_resident"] / 1e9, 3), "setup_ms": info["setup_ms"], "first_step_ms": info["first_step_ms"],
                        "ms_per_step": info["ms_per_step"], "gpu_ms_last": info["gpu_ms_last"], "pass_ms": info.get("pass_ms", []),
                        "check": {"feed_mismatches": int((feed != feed_ref).sum()), "t25_ledger_mismatches": int((g25 != led25).sum()),
                                  "t50_ledger_mismatches": int((g50 != led50).sum()), "weight_bit_mismatches": int((wt.view(np.uint32) != wref.view(np.uint32)).sum())}})
            if route:
                g = lambda nm, sh=None: (lambda a: a.reshape(sh) if sh else a)(np.fromfile(f"{od}/{nm}.bin", np.uint32))
                rec["check"].update({"route_home_mismatches": int((g("home") != route["home"]).sum()), "route_hop_mismatches": int((g("hops") != route["hops"]).sum()),
                                     "route_link_mismatches": int((g("link", (4, U, U)) != route["link"]).sum()), "route_home_ledger_mismatches": int((g("hled", (U, 64, 256)) != route["hled"]).sum()),
                                     "route_inbox_mismatches": int((g("inbox") != route["inbox"]).sum()),
                                     "cut_rtab_mismatches": int((g("rtab", (4, 16, 16)) != route["rtab"]).sum()),
                                     "cut_vtab_mismatches": int((g("vtab", (4, U)) != route["vtab"]).sum()),
                                     "cut_table_mismatches": int((np.fromfile(f"{od}/cut.bin", np.float32).reshape(U, U) != route["cut"]).sum()),
                                     "cut_vs_gomory_hu_mismatches": gh_check(np.fromfile(f"{od}/cut.bin", np.float32).reshape(U, U), route["link"], dims, U)})
                c = np.bincount(route["home"], minlength=U); wg = (c + 63) // 64                   # JIT-T50 #1 mailbox, per step (the last step's)
                off = np.concatenate([[0], np.cumsum(c)[:-1]]); wgo = np.concatenate([[0], np.cumsum(wg)])
                mail = g("mb_mail"); goff = g("mb_off")
                rec["check"].update({"mb_count_mismatches": int((g("mb_tcnt") != c).sum()), "mb_offset_mismatches": int((goff != off).sum()),
                                     "mb_wg_offset_mismatches": int((g("mb_wgo") != wgo).sum()), "mb_args_mismatches": int((g("mb_args") != [wgo[-1], 1, 1]).sum()),
                                     "mb_workgroups_per_toroid_mismatches": int((g("mb_wgt") != wg * steps).sum()),
                                     "mb_mailbox_set_mismatches": sum(int(not np.array_equal(np.sort(mail[off[t]:off[t] + c[t]]), np.nonzero(route["home"] == t)[0])) for t in range(U)),
                                     "mb_ledger_vs_route_hled_mismatches": int((g("mb_led", (U, 64, 256)) != route["hled"]).sum())})
                rec["mailbox"] = {"items_per_toroid": c.tolist(), "workgroups_per_toroid": wg.tolist(), "workgroups_elastic": int(wg.sum()),
                                  "workgroups_fixed_worst_case": int(U * wg.max())}
                rec["route"] = {"dims": [{"ring": r, "size": S, "stride": st} for r, S, st in route["dims"]], "inbox_per_step": (route["inbox"] // steps).tolist(),
                                "hops_histogram": {str(k): int((route["hops"] == k).sum()) for k in range(len(route["dims"]) + 1)},
                                "link_per_step": (route["link"][:len(route["dims"])] // steps).tolist()}   # [dim][from][to] items per step (GROW-RUN-0 g4 cuts)
            bad = {kk: v for kk, v in rec["check"].items() if v}
            if bad: fails.append(str(bad))
        rec["fails"] = fails; rec["pass"] = not fails; rec["wall_s"] = round(time.time() - t0, 1)
        tag = f"{rung}-{dev.split()[0].lower()}-{'full' if slab == 'full' else 'w' + str(W)}{'-state' if full_state else ''}"
        json.dump(rec, open(f"{out}/{tag}.json", "w"), indent=1)
        print(json.dumps({kk: v for kk, v in rec.items() if kk not in ("parts", "weights_files", "command")}))
        print("PASS" if not fails else "FAIL: " + "; ".join(fails)); sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()

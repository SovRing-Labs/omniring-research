#!/usr/bin/env python3
"""CYCLONE-ARRAY W3 gate — toroid → toroid routing by address on the GPU (kernels/route.spvasm; J 10-08 readback confirmed: a direct torus
network, a toroid's coordinates = residues on the layout rings, a fired item jumps ring by ring — one CRT jump per ring — to the toroid its
own address names). Every token event of every harness is addressed on the T50 (ring_addr) and routed from its source cyclone:
  1 floor   5 toroids (centre + 4 around) on ring 5                         (G40 layout: 40 harnesses, 81,920 events)
  3 floors  15 toroids: ring 3 = the floor (up / down), then ring 5        (G120 layout: 120 harnesses, 245,760 events)
Checked exactly vs the reference (Python, the same rule): each item's home toroid, its hop count, every link's traffic per ring, every
toroid's inbox, every toroid's home ledger (per ring, per residue). Also recorded: the hop histogram and the link traffic map.
Run OUTSIDE kernel-bash Landlock (systemd-run / tw unit) for the Intel device.   w3_route.py [--devices llvmpipe,Intel] [--out DIR]"""
import hashlib, json, os, subprocess, sys, tempfile
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from w2a_ring_addr import program, t50_groups, scalar, BIN, BUILD, P
K = {k: f"{P}/kernels/{k}.spv" for k in ("ring_addr", "route")}
PER, B, CTX, EOS, NO_PLATE = 8, 4, 512, 0, 36
LAYOUTS = {"1 floor (5 toroids)": (1, [(5, 5, 1)]), "3 floors (15 toroids)": (3, [(3, 3, 5), (5, 5, 1)])}   # (floors, [(ring, S, stride)])

def events(units, seed):
    man = json.load(open(f"{BUILD}/manifest.json")); rng = np.random.default_rng(seed); ev = []
    phases = [np.fromfile(f"{BUILD}/{p['file']}", dtype="<u2") for p in man["phases"]]
    kinds = [np.fromfile(f"{BUILD}/kind_{k}.u8", dtype=np.uint8) for k in range(len(phases))]
    for h in range(units * PER):
        for _ in range(B):
            ph = int(rng.integers(len(phases))); d, kd = phases[ph], kinds[ph]; i = int(rng.integers(len(d) - CTX - 1))
            x = d[i:i + CTX].astype(np.int64); row = np.concatenate([[0], np.cumsum(x[:-1] == EOS)])
            plate = np.where(kd[i:i + CTX] == 255, NO_PLATE, kd[i:i + CTX]).astype(np.int64)
            for j in range(CTX): ev.append([j, int(x[j]), int(plate[j]), ph, int(row[j]), h // PER, h, 0])
    return np.array(ev, dtype=np.int64)

def main():
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    devices = opt("--devices", "llvmpipe,Intel").split(","); out = opt("--out", f"{P}/results/cyclone/w3"); os.makedirs(out, exist_ok=True)
    mods, field, off = program(t50_groups()); L = len(mods); lane_of = {m: k for k, m in enumerate(mods)}
    fails, cases = [], []
    for name, (floors, dims) in LAYOUTS.items():
        T = floors * 5; units = T; ev = events(units, 20261008 + floors); n = len(ev); res = scalar(ev[:, :5], mods, field, off)
        lay = np.zeros(13, np.uint32); lay[0] = len(dims)
        for i, (ring, S, stride) in enumerate(dims): lay[1 + 3 * i:4 + 3 * i] = [lane_of[ring], S, stride]
        # reference: home, hops, links, inbox, home ledger
        home = np.zeros(n, np.int64); cur = ev[:, 5].copy(); hops = np.zeros(n, np.int64); link = np.zeros((4, T, T), np.int64)
        for i, (ring, S, stride) in enumerate(dims):
            ch = res[:, lane_of[ring]] % S; home += ch * stride
            cc = (cur // stride) % S; jump = cc != ch; nxt = cur - cc * stride + ch * stride
            np.add.at(link, (i, cur[jump], nxt[jump]), 1); cur = np.where(jump, nxt, cur); hops += jump
        assert (cur == home).all()
        inbox = np.bincount(home, minlength=T); hled = np.zeros((T, 64, 256), np.int64)
        for q in range(L): np.add.at(hled, (home, q, res[:, q]), 1)
        with tempfile.TemporaryDirectory(prefix="omni-gpu-w3-") as Tm:
            tab = np.zeros(133, np.uint32); tab[:L] = mods; tab[64:64 + L] = field; tab[128:133] = np.array(off, np.int64).astype(np.int32).view(np.uint32)
            ev.astype(np.int32).tofile(f"{Tm}/ev.bin"); tab.tofile(f"{Tm}/tab.bin"); lay.tofile(f"{Tm}/lay.bin")
            gy = -(-n // 4096)
            prog = [f"buf file {Tm}/ev.bin", f"buf file {Tm}/tab.bin", f"buf zero {n * 256}", f"buf zero {n * 256}", f"buf zero {n * 256}",       # 0 ev · 1 tab · 2 plate · 3 res · 4 tw
                    f"buf zero {T * 64 * 256 * 4}", f"buf zero {n * 8}", f"buf file {Tm}/lay.bin", f"buf zero {n * 4}", f"buf zero {n * 4}",    # 5 led · 6 dev · 7 lay · 8 home · 9 hops
                    f"buf zero {4 * T * T * 4}", f"buf zero {T * 64 * 256 * 4}", f"buf zero {T * 4}",                                          # 10 link · 11 hled · 12 inbox
                    f"pass {K['ring_addr']} 4096,{gy},1 spec 1={L} bind 0 1 2 3 4 5 6",
                    f"pass {K['route']} 4096,{gy},1 spec 1={L} 2={T} bind 0 3 7 8 9 10 11 12", "read 8", "read 9", "read 10", "read 11", "read 12"]
            open(f"{Tm}/prog.txt", "w").write("\n".join(prog) + "\n")
            for dev in devices:
                od = f"{Tm}/o-{dev}"; case = {"layout": name, "toroids": T, "dims": [{"ring": r, "size": S, "stride": st} for r, S, st in dims], "device": dev, "items": n}
                r = subprocess.run([BIN, "session", f"{Tm}/prog.txt", "--device", dev, "--steps", "1", "--out", od], capture_output=True, text=True, timeout=900)
                if r.returncode: case["error"] = r.stderr[-400:]; fails.append(f"{name} {dev}: {case['error']}"); cases.append(case); continue
                info = json.loads(r.stdout.strip().splitlines()[-1])
                g = lambda i, dt=np.uint32: np.fromfile(f"{od}/buf{i}.bin", dt)
                gh, gp, gl, ghl, gin = g(8), g(9), g(10).reshape(4, T, T), g(11).reshape(T, 64, 256), g(12)
                case.update({"device_name": info["device"], "gpu_ms": info["gpu_ms_last"],
                             "home_mismatches": int((gh != home).sum()), "hop_mismatches": int((gp != hops).sum()), "link_mismatches": int((gl != link).sum()),
                             "inbox_mismatches": int((gin != inbox).sum()), "home_ledger_mismatches": int((ghl != hled).sum()),
                             "hops_histogram": {str(k): int((hops == k).sum()) for k in range(len(dims) + 1)}, "inbox": inbox.tolist(),
                             "link_traffic": {f"ring {r}": link[i, :T, :T].tolist() for i, (r, _, _) in enumerate(dims)}})
                bad = {kk: v for kk, v in case.items() if kk.endswith("mismatches") and v}
                if bad: fails.append(f"{name} {dev}: {bad}")
                cases.append(case); print(json.dumps({kk: v for kk, v in case.items() if kk != "link_traffic"}), flush=True)
    rep = {"gate": "CYCLONE-ARRAY W3 toroid → toroid routing by address", "kernels": {k: hashlib.sha256(open(v, "rb").read()).hexdigest()[:12] for k, v in K.items()},
           "cases": cases, "fails": fails, "pass": not fails}
    json.dump(rep, open(f"{out}/route.json", "w"), indent=1)
    print("PASS" if not fails else "FAIL: " + "; ".join(fails)); sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()

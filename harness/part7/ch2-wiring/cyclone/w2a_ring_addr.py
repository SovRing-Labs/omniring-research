#!/usr/bin/env python3
"""CYCLONE-ARRAY W2a gate — omniring addressing on the GPU (kernels/ring_addr.spvasm, lane = ring) for every harness of a floor at once.
Traffic: REAL — one floor (5 units × 8 harnesses = 40) × one school batch (4 windows × 512 positions) cut from a tier-1 build; each position
is the trunk's T25 event [position, token, plate (kind, 36 = none), level (phase), row (EOS count before it)] = 81,920 events per launch.
Plates (the precompute): per event either staged with its OWN expected event (must confirm: twist 0), staged with the token field changed
(must deviate on exactly the token rings where the residues differ), or not staged (zeros: twist = residue).
Oracles: T25 = the runtime's OWN rendered T25 core (<run>/t25_core.bin, x86 mapped executable — the bytes the model fires); T50 = the
Program64::t50 layout of runtime/src/jit/t50.rs (T25 groups + T30_ADD + the 20 primes 131…233 dealt round-robin, T25 offsets), whose lanes
on the T25 rings must ALSO equal the rendered T25 core (T25 is an exact sub-torus of T50). Checked: residues, twists, the per-unit ledger
(per ring, per residue counts), the per-event deviation masks — all exact.
Run OUTSIDE kernel-bash Landlock (systemd-run / tw unit) for the Intel device.   w2a_ring_addr.py [--devices llvmpipe,Intel] [--out DIR]"""
import ctypes, hashlib, json, mmap, os, subprocess, sys, tempfile, time
import numpy as np
P = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BIN = f"{P}/target/release/omni-gpu"; SPV = f"{P}/kernels/ring_addr.spv"
T = os.environ.get("CYCLONE_THEAD", "<workspace>/projects/thead-trial"); BUILD = f"{T}/build-v4/tier1-prek-v4-s6400"
CORE = os.environ.get("CYCLONE_CORE", f"{P}/results/cyclone/c1/run")                      # a school run's rendered T25 core (t25_core.bin + .json), written by the runtime
T25 = [[3, 29, 41, 59, 101], [5, 31, 37, 67, 89], [7, 23, 43, 61, 97], [11, 19, 47, 71, 83], [13, 17, 53, 73, 79]]
T30_ADD = [103, 107, 109, 113, 127]
UNITS, PER, B, CTX, EOS, NO_PLATE = 5, 8, 4, 512, 0, 36

def program(groups):
    prod4 = int(np.prod(groups[4][:5], dtype=np.int64))      # t25.rs: off = [16384·64, 16384·64, 0, 0, prod(group 4)/2] (T25 group 4)
    off = [16384 * 64, 16384 * 64, 0, 0, prod4 // 2]
    mods = [m for g in groups for m in g]; field = [gi for gi, g in enumerate(groups) for _ in g]
    return mods, field, off

def t50_groups():
    primes = [p for p in range(3, 234, 2) if all(p % d for d in range(3, int(p ** 0.5) + 1, 2))]
    more = [p for p in primes if p > 127]; assert len(more) == 20
    gs = [list(T25[i]) + [T30_ADD[i]] for i in range(5)]
    for i, p in enumerate(more): gs[i % 5].append(p)
    return gs

def events():
    man = json.load(open(f"{BUILD}/manifest.json")); rng = np.random.default_rng(20261008); ev = []
    phases = [np.fromfile(f"{BUILD}/{p['file']}", dtype="<u2") for p in man["phases"]]
    kinds = [np.fromfile(f"{BUILD}/kind_{k}.u8", dtype=np.uint8) for k in range(len(phases))]
    for h in range(UNITS * PER):
        for b in range(B):
            ph = int(rng.integers(len(phases))); d, kd = phases[ph], kinds[ph]; i = int(rng.integers(len(d) - CTX - 1))
            x = d[i:i + CTX].astype(np.int64); row = np.concatenate([[0], np.cumsum(x[:-1] == EOS)])
            plate = np.where(kd[i:i + CTX] == 255, NO_PLATE, kd[i:i + CTX]).astype(np.int64)
            for j in range(CTX): ev.append([j, int(x[j]), int(plate[j]), ph, int(row[j]), h // PER, h])
    return np.array(ev, dtype=np.int64)

def rendered_t25(coords):
    meta = json.load(open(f"{CORE}/t25_core.json")); code = open(f"{CORE}/t25_core.bin", "rb").read()
    mm = mmap.mmap(-1, len(code), prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC); mm.write(code)
    fn = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)(ctypes.addressof(ctypes.c_char.from_buffer(mm)))
    n = len(coords); c = np.ascontiguousarray(coords, dtype=np.int64); res = np.zeros((n, 32), np.uint8); pl = np.zeros((n, 32), np.uint8); tw = np.zeros((n, 32), np.uint8)
    mods = np.array(meta["mods"], dtype=np.uint8)
    fn(c.ctypes.data, n, res.ctypes.data, pl.ctypes.data, tw.ctypes.data, mods.ctypes.data)
    return res, meta["mods"]

def scalar(coords, mods, field, off):
    x = coords[:, field] + np.array(off, dtype=np.int64)[field]; assert (x >= 0).all() and (x < 2 ** 31).all(), "event outside the kernel's domain"
    return (x % np.array(mods, dtype=np.int64)).astype(np.int64)

def main():
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    devices = opt("--devices", "llvmpipe,Intel").split(","); out = opt("--out", f"{P}/results/cyclone/w2a"); os.makedirs(out, exist_ok=True)
    ev = events(); n = len(ev); coords = ev[:, :5]; rng = np.random.default_rng(7)
    kind = rng.integers(0, 3, n)                                  # 0 staged own · 1 staged with the token changed · 2 not staged
    alt = coords.copy(); alt[:, 1] = (alt[:, 1] + 1 + rng.integers(0, 8000, n)) % 8192
    r25, mods25 = rendered_t25(coords)
    fails, cases = [], []
    for name, groups in (("T25", T25), ("T50", t50_groups())):
        mods, field, off = program(groups); L = len(mods)
        ref = scalar(coords, mods, field, off); ref_alt = scalar(alt, mods, field, off)
        if name == "T25":
            bad = int((ref != r25[:, :25]).any(axis=1).sum()); cases.append({"check": "T25 scalar mirror == rendered T25 core", "events": n, "mismatched_events": bad})
            if bad: fails.append(f"T25 scalar mirror != rendered core on {bad} events")
        else:                                                    # T25 is an exact sub-torus of T50: shared rings carry the same residue
            pos = {m: k for k, m in enumerate(mods25[:25])}; lanes = [(k, pos[m]) for k, m in enumerate(mods) if m in pos]
            bad = int(sum((ref[:, k] != r25[:, l]).sum() for k, l in lanes)); cases.append({"check": "T50 on the T25 rings == rendered T25 core", "lanes": len(lanes), "mismatches": bad})
            if bad: fails.append(f"T50 sub-torus mismatch {bad}")
        plate = np.zeros((n, 64), np.int64); plate[kind == 0, :L] = ref[kind == 0]; plate[kind == 1, :L] = ref_alt[kind == 1]
        mm = np.array(mods, dtype=np.int64)
        tw_ref = (ref - plate[:, :L]) % mm
        dev_ref = np.zeros((n, 2), np.uint64)
        for k in range(L): dev_ref[:, k // 32] |= (tw_ref[:, k] != 0).astype(np.uint64) << np.uint64(k % 32)
        led_ref = np.zeros((UNITS, 64, 256), np.int64)
        for k in range(L): np.add.at(led_ref, (ev[:, 5], k, ref[:, k]), 1)
        with tempfile.TemporaryDirectory(prefix="omni-gpu-w2a-") as Tm:
            evb = np.zeros((n, 8), np.int32); evb[:, :5] = coords; evb[:, 5] = ev[:, 5]; evb[:, 6] = ev[:, 6]; evb[:, 7] = (kind < 2)
            tab = np.zeros(133, np.uint32); tab[:L] = mods; tab[64:64 + L] = field; tab[128:133] = np.array(off, dtype=np.int64).astype(np.int32).view(np.uint32)
            evb.tofile(f"{Tm}/ev.bin"); tab.tofile(f"{Tm}/tab.bin"); plate.astype(np.uint32).tofile(f"{Tm}/plate.bin")
            gx = 4096; gy = -(-n // gx)
            prog = "\n".join([f"buf file {Tm}/ev.bin", f"buf file {Tm}/tab.bin", f"buf file {Tm}/plate.bin", f"buf zero {n * 256}", f"buf zero {n * 256}",
                              f"buf zero {UNITS * 64 * 256 * 4}", f"buf zero {n * 8}", f"pass {SPV} {gx},{gy},1 spec 1={L} bind 0 1 2 3 4 5 6",
                              "read 3", "read 4", "read 5", "read 6"]) + "\n"
            open(f"{Tm}/prog.txt", "w").write(prog)
            for dev in devices:
                od = f"{Tm}/o-{dev}-{name}"
                r = subprocess.run([BIN, "session", f"{Tm}/prog.txt", "--device", dev, "--steps", "1", "--out", od], capture_output=True, text=True, timeout=600)
                case = {"tier": name, "rings": L, "device": dev, "events": n, "harnesses": UNITS * PER, "units": UNITS}
                if r.returncode: case["error"] = r.stderr[-400:]; fails.append(f"{name} {dev}: {case['error']}"); cases.append(case); continue
                info = json.loads(r.stdout.strip().splitlines()[-1])
                res = np.fromfile(f"{od}/buf3.bin", np.uint32).reshape(n, 64); tw = np.fromfile(f"{od}/buf4.bin", np.uint32).reshape(n, 64)
                led = np.fromfile(f"{od}/buf5.bin", np.uint32).reshape(UNITS, 64, 256); dv = np.fromfile(f"{od}/buf6.bin", np.uint32).reshape(n, 2)
                case.update({"device_name": info["device"], "gpu_ms": info["gpu_ms_last"], "ns_per_event": round(info["gpu_ms_last"] * 1e6 / n, 2) if info["gpu_ms_last"] else None,
                             "residue_mismatches": int((res[:, :L] != ref).sum()), "inert_nonzero": int(res[:, L:].sum() + tw[:, L:].sum()),
                             "twist_mismatches": int((tw[:, :L] != tw_ref).sum()), "ledger_mismatches": int((led != led_ref).sum()),
                             "ledger_total": int(led.sum()), "dev_mask_mismatches": int((dv.astype(np.uint64) != dev_ref).sum()),
                             "confirmed": int(((kind == 0) & (dv == 0).all(axis=1)).sum()), "staged_own": int((kind == 0).sum()),
                             "flagged_changed": int(((kind == 1) & (dv != 0).any(axis=1)).sum()), "staged_changed": int((kind == 1).sum())})
                bad = {k: case[k] for k in ("residue_mismatches", "inert_nonzero", "twist_mismatches", "ledger_mismatches", "dev_mask_mismatches") if case[k]}
                if bad: fails.append(f"{name} {dev}: {bad}")
                if case["ledger_total"] != n * L: fails.append(f"{name} {dev}: ledger total {case['ledger_total']} != {n * L}")
                cases.append(case); print(json.dumps(case), flush=True)
    rep = {"gate": "CYCLONE-ARRAY W2a omniring addressing on the GPU", "spv_sha256": hashlib.sha256(open(SPV, "rb").read()).hexdigest()[:12],
           "core": CORE, "build": BUILD, "cases": cases, "fails": fails, "pass": not fails}
    json.dump(rep, open(f"{out}/ring_addr.json", "w"), indent=1)
    print("PASS" if not fails else "FAIL: " + "; ".join(fails)); sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()

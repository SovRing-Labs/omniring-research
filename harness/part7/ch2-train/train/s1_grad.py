#!/usr/bin/env python3
"""CYCLONE-ARRAY C2 S1 gate — THE TRAINING STEP ON THE GPU vs OUR CPU ENGINE. One THEAD model (plain trunk, every school switch off) is
created by the CPU engine (om_create, seeded); its parameters (om_param_ptr, P order) and one batch of REAL curriculum tokens go to the GPU
step (gen/train_step.py, one recorded resident step on `omni-gpu session`); the CPU engine runs om_grad on the same model + batch.
Compared: the loss, and every parameter's gradient (cosine, max |Δ| / max |g|) — the GPU-LOOP G4 bar: cosine ≥ 0.9999 and max rel ≤ 1e-3
per parameter (float order differs: the engine's AVX dot8 / blocked sgemm / exp8 vs the GPU's sums).
  s1_grad.py [--dims small|school] [--device llvmpipe] [--out DIR]"""
import ctypes, json, os, subprocess, sys, tempfile, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, f"{P}/gen")
import train_step
LIB = os.environ.get("CYCLONE_LIB", "<workspace>/projects/thead-trial/engine/omni_train/libomnitrain_trial.so")
BUILD = os.environ.get("CYCLONE_BUILD", "<workspace>/projects/thead-trial/build-v4/tier1-prek-v4-s6400")
BIN = f"{P}/target/release/omni-gpu"
T25_DIR = os.environ.get("CYCLONE_T25", "<workspace>/projects/thead-trial/runtime/results/growth-base/r12-elem")   # a round's rendered T25 core

def t25_core(d=T25_DIR):
    """the runtime's rendered T25 core (x86 bytes the model fires) mapped executable → (entry, mods [32] uint8, eos, keep-alive)"""
    import mmap
    meta = json.load(open(f"{d}/t25_core.json")); code = open(f"{d}/t25_core.bin", "rb").read()
    mm = mmap.mmap(-1, max(4096, len(code)), prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC); mm.write(code)
    ent = ctypes.addressof(ctypes.c_char.from_buffer(mm)); mods = (ctypes.c_ubyte * 32)(*meta["mods"][:32])
    return ent, mods, int(meta.get("eos", 0)), (mm, mods)

def switches_on(Lb, h, sw, D, H, L_=2):
    """the school switches on the CPU engine (the oracle) → aux tables for the GPU step"""
    aux, keep = {}, []
    if "t25" in sw:
        ent, mods, eos, k = t25_core(); keep.append(k)
        Lb.om_set_t25.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]; Lb.om_set_t25.restype = ctypes.c_int
        pairs = Lb.om_set_t25(h, ent, mods, eos)
        aux["t25lane"] = [next((k_ for k_ in range(32) if mods[k_] and mods[k_] == train_step.PRIMES[i]), -1) for i in range((D // H) // 2)]
        aux["t25_pairs"] = pairs
    if "voice" in sw: Lb.om_set_voicing.argtypes = [ctypes.c_void_p, ctypes.c_int]; Lb.om_set_voicing(h, 1)
    if any(w.startswith("spark") for w in sw):                       # spark skip (LEARN_SPARK, default 4 in the school)
        th = float(next(w for w in sw if w.startswith("spark")).split("=")[1]) if any("=" in w for w in sw if w.startswith("spark")) else 4.0
        per = (ctypes.c_int * 64)(*([1] * 64)); Lb.om_set_flags.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_float, ctypes.c_void_p]
        Lb.om_set_flags(h, 0, th, per); aux["spark"] = th
    if any(w.split("=")[0] == "p3" for w in sw):                      # P3 (school: P3=1 → p 0.95, full every 4, compact); p3=P for a gate that fires
        w = next(w for w in sw if w.split("=")[0] == "p3"); pp = float(w.split("=")[1]) if "=" in w else 0.95
        Lb.om_set_p3.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_int, ctypes.c_int]; Lb.om_set_p3(h, pp, 4, 1); aux["p3"] = (pp, 4)
    if "port" in sw:                                                  # the library port as the school sets it (Eng::load + thead-learn):
        vpp = ctypes.c_void_p                                         # K = PLATES 31, θ 1.0, τ 0.05 soft, simplex router, router CE 0.5, pointer β₀ 5
        Lb.om_set_port.argtypes = [vpp, ctypes.c_int, ctypes.c_float]; Lb.om_set_port.restype = ctypes.c_int; Lb.om_set_port(h, 31, 1.0)
        Lb.om_set_port_tau.argtypes = [vpp, ctypes.c_float, ctypes.c_int]; Lb.om_set_port_tau(h, 0.05, 0)
        Lb.om_set_pointer.argtypes = [vpp, ctypes.c_int, ctypes.c_float]; Lb.om_set_pointer.restype = ctypes.c_int; Lb.om_set_pointer(h, 1, 5.0)
        Lb.om_set_router_simplex.argtypes = [vpp, ctypes.c_float, ctypes.c_ulonglong]; Lb.om_set_router_simplex.restype = ctypes.c_float; Lb.om_set_router_simplex(h, 0.0, 7)
        Lb.om_set_router_ce.argtypes = [vpp, ctypes.c_float]; Lb.om_set_router_ce(h, 0.5)
        Lb.om_set_port_data.argtypes = [vpp, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
        aux["port"] = {"K": 31, "theta": 1.0, "tau": 0.05, "rce": 0.5}
    rtw = next((w for w in sw if w.split("=")[0] == "route"), None)            # route[=θ[:sat]] (school: θ 3, sat 0.9)
    rt = (float(rtw.split("=")[1].split(":")[0]) if "=" in rtw else 3.0) if rtw else 0.0
    rsat = (float(rtw.split(":")[1]) if rtw and ":" in rtw else 0.9) if rt > 0 else 0.0
    if "local" in sw or rt > 0:                                       # the local rule (school: LEARN_LOCAL 2, LOCAL_STRIDE 4) + routing (EXIT_THETA 3, ROUTE_SAT 0.9)
        vpp = ctypes.c_void_p; Lb.om_set_local.argtypes = [vpp, ctypes.c_int, ctypes.c_int]; Lb.om_set_local.restype = ctypes.c_int; Lb.om_set_local(h, 2, 4)
        Lb.om_set_route.argtypes = [vpp, ctypes.c_float]; Lb.om_set_route.restype = ctypes.c_int; Lb.om_set_route(h, rt)
        Lb.om_set_route_sat.argtypes = [vpp, ctypes.c_float]; Lb.om_set_route_sat(h, rsat)
        roles = None
        if "roles" in sw:
            roles = role_masks(L_, L_); Lb.om_set_roles.argtypes = [vpp, ctypes.c_void_p, ctypes.c_int]; Lb.om_set_roles(h, (ctypes.c_uint * L_)(*roles), L_)
        Lb.om_set_stage_data.argtypes = [vpp, ctypes.c_void_p, ctypes.c_int]
        aux["local"] = {"S": 4, "roles": roles, "route": rt, "sat": rsat}
    if "avoid" in sw: Lb.om_set_avoid.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]; Lb.om_set_avoid.restype = ctypes.c_int; aux["avoid"] = 1.0
    if "copy" in sw:                                                  # context copy pointer (school: COPY=6 → β₀ 6)
        Lb.om_set_copy.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_float]; Lb.om_set_copy.restype = ctypes.c_int; Lb.om_set_copy(h, 1, 6.0)
    if "harm" in sw:                                                  # harmony (school: HARM=1, HARM_LAMBDA 0.05, HARM_KAPPA 0.9)
        Lb.om_set_harmony.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_float, ctypes.c_float]; Lb.om_set_harmony(h, 1, 0.05, 0.9); aux["harm"] = (0.05, 0.9)
    if "plates" in sw:                                                # attention plates (PLATES_ATTN=1): rows end at the build's eos
        aux["eos"] = int(json.load(open(f"{BUILD}/manifest.json")).get("token_ids", {}).get("eos", 0))
        Lb.om_set_plates.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]; Lb.om_set_plates(h, 1, aux["eos"])
    return aux, keep

def sw_dict(sw, aux):
    """the switch list → the step builder's dict (values where a switch carries one)"""
    d = {w.split("=")[0]: True for w in sw}
    for k in ("spark", "p3", "harm", "port", "local", "avoid"):
        if k in aux: d[k] = aux[k]
    return d

def t25_res(Lb, h, N):
    Lb.om_t25_addr.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]; Lb.om_t25_addr.restype = ctypes.c_int
    out = np.zeros((N, 32), np.uint8)
    for n in range(N):
        if Lb.om_t25_addr(h, n, out[n].ctypes.data) != 0: raise SystemExit(f"no T25 address for position {n}")
    return out

DIMS = {"small": dict(V=512, D=64, L=2, H=2, T=64, B=2), "small4": dict(V=512, D=64, L=4, H=2, T=64, B=2), "school": dict(V=8192, D=256, L=6, H=4, T=512, B=4)}

def batch(V, T, B, seed=20261008, port=False):
    """B windows of T real curriculum tokens (mod V for small dims). port=True: + Build::win's kinds (255 → −1) and proposals (the next token
    where a kind is set), and y = −1 on masked positions — exactly the harness's window"""
    man = json.load(open(f"{BUILD}/manifest.json")); rng = np.random.default_rng(seed)
    ph = [np.fromfile(f"{BUILD}/{p['file']}", dtype="<u2").astype(np.int64) for p in man["phases"]]; xs, ys, ks, ps, ss = [], [], [], [], []
    for _ in range(B):
        pi = int(rng.integers(len(ph))); d = ph[pi]; i = int(rng.integers(len(d) - T - 1)); xs.append(d[i:i + T] % V); yy = d[i + 1:i + T + 1] % V
        if port:
            sf = f"{BUILD}/stage_{pi}.u8"; ss.append(np.fromfile(sf, np.uint8)[i:i + T].astype(np.int32) if os.path.exists(sf) else np.full(T, -1, np.int32))
            kd = np.fromfile(f"{BUILD}/kind_{pi}.u8", np.uint8)[i:i + T].astype(np.int32); mf = f"{BUILD}/mask_{pi}.u8"
            mk = np.fromfile(mf, np.uint8)[i:i + T] if os.path.exists(mf) else np.zeros(T, np.uint8)
            yy = np.where(mk == 1, -1, yy); k_ = np.where(kd == 255, -1, kd); ks.append(k_); ps.append(np.where(k_ >= 0, d[i + 1:i + T + 1] % V, -1))
        ys.append(yy)
    out = (np.concatenate(xs).astype(np.int32), np.concatenate(ys).astype(np.int32))
    return out + ((np.concatenate(ks).astype(np.int32), np.concatenate(ps).astype(np.int32), np.concatenate(ss).astype(np.int32)) if port else ())

def avoid_rows(y, V, seed):
    """a study-like avoid push: about a quarter of the rows get a wrong token to push down (−1 = none)"""
    r = np.random.default_rng(seed); av = np.where(r.random(len(y)) < 0.25, r.integers(0, V, len(y)), -1).astype(np.int32)
    return np.where(av == np.asarray(y), -1, av).astype(np.int32)

def role_masks(al, l):
    """thead.rs:1498 role_masks — the grown non-top blocks share the procedure's stages bottom-up (top = all)"""
    g = [1 | 2 | 4, 8, 16, 32 | 64 | 128]; k = max(al - 1, 0); m = [0] * l
    plan = {0: [], 1: [0], 2: [g[0] | g[1], g[2] | g[3]], 3: [g[0], g[1], g[2] | g[3]], 4: list(g)}.get(k, [g[0]] + [g[1]] * (k - 3 if k > 3 else 0) + [g[2], g[3]])
    for b, v in enumerate(plan):
        if b < l: m[b] = v
    return m

def main():
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    dn = opt("--dims", "small"); dims = DIMS[dn]; dev = opt("--device", "llvmpipe"); sw = [w for w in opt("--sw", "").split(",") if w]; out = opt("--out", f"{P}/results/cyclone/c2-s1"); os.makedirs(out, exist_ok=True)
    V, D, L, H, T, B = (dims[k] for k in ("V", "D", "L", "H", "T", "B"))
    Lb = ctypes.CDLL(LIB); vp = ctypes.c_void_p
    Lb.om_create.restype = vp; Lb.om_create.argtypes = [ctypes.c_int] * 5 + [vp, ctypes.c_int, ctypes.c_ulonglong]
    ip = np.ctypeslib.ndpointer(np.int32, flags="C_CONTIGUOUS")
    Lb.om_grad.restype = ctypes.c_float; Lb.om_grad.argtypes = [vp, ip, ip, ctypes.c_int, ctypes.c_int]
    for fn, rt in (("om_param_ptr", ctypes.POINTER(ctypes.c_float)), ("om_param_grad", ctypes.POINTER(ctypes.c_float)), ("om_param_size", ctypes.c_long), ("om_param_name", ctypes.c_char_p)):
        getattr(Lb, fn).restype = rt; getattr(Lb, fn).argtypes = [vp, ctypes.c_int]
    Lb.om_nparams.argtypes = [vp]; Lb.om_threads(4)
    PR = (ctypes.c_int * 32)(*train_step.PRIMES)
    h = Lb.om_create(V, D, L, H, T, PR, (D // H) // 2, 1234)
    aux, keep = switches_on(Lb, h, sw, D, H, L)                       # first: switches may add parameters (copy, port, local norms)
    names = [Lb.om_param_name(h, i).decode() for i in range(Lb.om_nparams(h))]
    params = [(n, np.ctypeslib.as_array(Lb.om_param_ptr(h, i), shape=(Lb.om_param_size(h, i),)).copy()) for i, n in enumerate(names)]
    PORT = "port" in sw; LOCAL = "local" in aux
    if PORT or LOCAL:                                                # the harness's window: kinds, proposals, stages, masked targets
        x, y, pk, pp, st = batch(V, T, B, port=True); aux["pstage"] = st
        if PORT: aux["pkind"], aux["pprop"] = pk, pp; Lb.om_set_port_data(h, pk.ctypes.data, pp.ctypes.data, B * T)
        if LOCAL: Lb.om_set_stage_data(h, st.ctypes.data, B * T)
    else: x, y = batch(V, T, B)
    if "avoid" in aux: aux["pavoid"] = avoid_rows(y, V, 7); Lb.om_set_avoid(h, aux["pavoid"].ctypes.data, B * T)
    Lb.om_tok_loss.restype = ctypes.POINTER(ctypes.c_float); Lb.om_tok_loss.argtypes = [vp]
    t0 = time.time(); loss_cpu = float(Lb.om_grad(h, x, y, B, T)); t_cpu = time.time() - t0
    tok_cpu = np.ctypeslib.as_array(Lb.om_tok_loss(h), shape=(B * T,)).copy()
    g_cpu = {n: np.ctypeslib.as_array(Lb.om_param_grad(h, i), shape=(Lb.om_param_size(h, i),)).copy() for i, n in enumerate(names)}
    if "t25" in sw: aux["t25res"] = t25_res(Lb, h, B * T)
    with tempfile.TemporaryDirectory(prefix="omni-gpu-s1-") as Tm:
        text, outs, npass, nbuf = train_step.build(dims, params, x, y, Tm, sw=sw_dict(sw, aux), aux=aux)
        open(f"{Tm}/prog.txt", "w").write(text); od = f"{Tm}/o"
        r = subprocess.run([BIN, "session", f"{Tm}/prog.txt", "--device", dev, "--steps", "1", "--out", od], capture_output=True, text=True, timeout=7200)
        rec = {"gate": "CYCLONE-ARRAY C2 S1: the training step on the GPU vs the CPU engine (om_grad)", "dims": dims, "device": dev, "switches": sw,
               "t25_pairs": aux.get("t25_pairs"), "passes": npass,
               "buffers": nbuf, "loss_cpu": loss_cpu, "cpu_s": round(t_cpu, 3), "lib": LIB}
        if r.returncode:
            rec.update({"pass": False, "error": r.stderr[-1500:]}); print(json.dumps(rec)); json.dump(rec, open(f"{out}/s1-{dn}-{dev.split()[0].lower()}{'-' + '-'.join(sw) if sw else ''}.json", "w"), indent=1); sys.exit(1)
        info = json.loads(r.stdout.strip().splitlines()[-1])
        rd = lambda k: np.fromfile(f"{od}/buf{outs[k][0]}.bin", np.float32)
        loss_gpu = float(rd("loss")[0]); per = {}; worst_cos, worst_rel = 1.0, 0.0
        dtok = np.abs(rd("hst").reshape(-1, 3)[:, 2] - tok_cpu)                     # per-token loss: GPU vs CPU
        tokd = {"median": float(np.median(dtok)), "p99": float(np.quantile(dtok, 0.99)), "max": float(dtok.max()),
                "tokens_over_1e-4": int((dtok > 1e-4).sum()), "tokens": int(dtok.size)}
        frozen = train_step.FROZEN(sw_dict(sw, aux))                      # the simplex router: its gradient is computed by the engine, never used
        for n in names:
            if n in frozen: continue
            gg, gc = rd(f"g:{n}")[:g_cpu[n].size], g_cpu[n]
            den = float(np.linalg.norm(gg) * np.linalg.norm(gc)); cos = float(np.dot(gg.astype(np.float64), gc) / den) if den > 0 else (1.0 if not gg.any() and not gc.any() else 0.0)
            rel = float(np.max(np.abs(gg - gc)) / max(np.max(np.abs(gc)), 1e-30))
            per[n] = {"cos": round(cos, 7), "max_rel": float(f"{rel:.3e}"), "norm_cpu": float(np.linalg.norm(gc)), "norm_gpu": float(np.linalg.norm(gg))}
            worst_cos, worst_rel = min(worst_cos, cos), max(worst_rel, rel)
        ok = abs(loss_gpu - loss_cpu) <= 1e-4 * max(1.0, abs(loss_cpu)) and worst_cos >= 0.9999 and worst_rel <= 1e-3
        rec.update({"device_name": info["device"], "loss_gpu": loss_gpu, "loss_abs_diff": abs(loss_gpu - loss_cpu), "worst_cos": worst_cos, "worst_max_rel": worst_rel,
                    "gpu_ms_step": info["gpu_ms_last"], "token_loss_diff": tokd, "bytes_resident": info["bytes"], "per_param": per, "pass": bool(ok)})
        json.dump(rec, open(f"{out}/s1-{dn}-{dev.split()[0].lower()}{'-' + '-'.join(sw) if sw else ''}.json", "w"), indent=1)
        print(json.dumps({k: v for k, v in rec.items() if k != "per_param"}))
        for n in per: print(f"  {n:28} cos {per[n]['cos']:.7f}  max_rel {per[n]['max_rel']:.2e}")
        print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""GROW-RUN-0 D1 gate — the harness decode on the GPU (engine library OMR_GPU_DECODE=1, gen/decode_step.py) vs the CPU engine's
om_decx_step, on a real core + real held-out rows, teacher-forced (both sides see the same tokens, kinds, offers — thead.rs:1420's way):
per step top-1 and margin, per row the exit counts, and om_decx_logit of the top-1. Each side runs in its own process (OMNI_TRAIN_LIB).
  d1_decode.py CORE_DIR HELDOUT_BUILD OUT_DIR [rows=24] [tokens=64]            (child: d1_decode.py --side cpu|gpu …)
D2 (D1_SERVER=N, OMNI_GPU_BIN = the omni-gpu binary): the GPU side through the ARRAY SERVER's decode service — `omni-gpu serve` with N slots and
N harness clients at once, client i on its own rows (rows i·n … i·n+n−1: different stations, same step), each connected by one lr-0 training
step (weights unchanged; lazy fetch exercised); every client's decode vs the CPU engine on its rows."""
import ctypes, json, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))


def side(core, hb, out, nrows, ntok):
    sys.path.insert(0, os.environ["THEAD_HARNESS"]); import route_decode_check as rc
    L = rc.L; vp = ctypes.c_void_p; h, cfg = rc.load(core)
    L.om_set_exit.argtypes = [vp, ctypes.c_float]; L.om_set_route_sat.argtypes = [vp, ctypes.c_float]; L.om_set_sieve.argtypes = [vp, ctypes.c_int]
    L.om_dec_prepare.argtypes = [vp]; L.om_decx_new.restype = vp; L.om_decx_new.argtypes = [vp]; L.om_decx_reset.argtypes = [vp, vp]
    L.om_decx_step.argtypes = [vp, vp, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_float)]
    L.om_decx_logit.restype = ctypes.c_float; L.om_decx_logit.argtypes = [vp, vp, ctypes.c_int]
    L.om_decx_exits.argtypes = [vp, vp, ctypes.POINTER(ctypes.c_long)]
    L.om_set_route(h, 0.0); L.om_set_exit(h, float(cfg.get("exit_theta", 0.0))); L.om_set_route_sat(h, float(cfg.get("route_sat", 0.0)))
    L.om_set_sieve(h, int(cfg.get("sieve", 64)))
    man = json.load(open(f"{hb}/manifest.json")); nf = len(man["rows_sidecar"]["fields"])
    d = np.fromfile(f"{hb}/phase_0.u16", dtype=np.uint16).astype(np.int32); kd = np.fromfile(f"{hb}/kind_0.u8", dtype=np.uint8)
    r0 = int(os.environ.get("D1_ROW0", 0)); rows = np.fromfile(f"{hb}/rows_0.u32", dtype=np.uint32).reshape(-1, nf)[r0:r0 + nrows]
    if os.environ.get("D1_TRAIN1"):                                            # D2: connect to the array server with one lr-0 step
        ip = ctypes.POINTER(ctypes.c_int); L.om_train_step.argtypes = [vp, ip, ip, ctypes.c_int, ctypes.c_int, ctypes.c_float]; L.om_train_step.restype = ctypes.c_float
        s0 = int(rows[0][0]); x = np.ascontiguousarray(d[s0:s0 + 64], np.int32); y = np.ascontiguousarray(d[s0 + 1:s0 + 65], np.int32)
        L.om_train_step(h, x.ctypes.data_as(ip), y.ctypes.data_as(ip), 1, 64, 0.0)
    L.om_dec_prepare(h)
    dec = L.om_decx_new(h); nl = int(cfg.get("L", 6)) if "L" in cfg else 6
    rec = []; top = ctypes.c_int(); mg = ctypes.c_float()
    for r in rows:
        s0 = int(r[0]); L.om_decx_reset(h, dec); steps = []
        for j in range(min(ntok, len(d) - s0 - 1)):
            k = int(kd[s0 + j]); k = -1 if k == 255 else k; p = int(d[s0 + j + 1]) if k >= 0 else -1
            L.om_decx_step(h, dec, int(d[s0 + j]), k, p, ctypes.byref(top), ctypes.byref(mg))
            steps.append([top.value, round(float(mg.value), 5), round(float(L.om_decx_logit(h, dec, top.value)), 5)])
        ex = (ctypes.c_long * 16)(); L.om_decx_exits(h, dec, ex)
        rec.append({"steps": steps, "exits": [int(ex[i]) for i in range(nl)]})
    json.dump(rec, open(out, "w"))


def main():
    a = sys.argv[1:]
    if a[0] == "--side": return side(a[2], a[3], a[4], int(a[5]), int(a[6]))
    core, hb, out = a[0], a[1], a[2]; nrows = int(a[3]) if len(a) > 3 else 24; ntok = int(a[4]) if len(a) > 4 else 64
    os.makedirs(out, exist_ok=True); res = {}
    if os.environ.get("D1_SERVER"): return server_gate(core, hb, out, nrows, ntok, int(os.environ["D1_SERVER"]))
    for nm, env in (("cpu", {"OMNI_TRAIN_LIB": os.environ["CPU_LIB"]}), ("gpu", {"OMNI_TRAIN_LIB": os.environ["GPU_LIB"], "OMR_GPU_DECODE": "1"})):
        r = subprocess.run([sys.executable, __file__, "--side", nm, core, hb, f"{out}/{nm}.json", str(nrows), str(ntok)],
                           env=dict(os.environ, **env), capture_output=True, text=True, timeout=3600)
        open(f"{out}/{nm}.log", "w").write(r.stdout + r.stderr)
        if r.returncode: print(nm, "FAILED", r.stderr[-1500:]); sys.exit(2)
        res[nm] = json.load(open(f"{out}/{nm}.json"))
    n = agree = 0; mdiff = []; ldiff = []; ex_eq = 0
    for c, g in zip(res["cpu"], res["gpu"]):
        ex_eq += int(c["exits"] == g["exits"])
        for (tc, mc, lc), (tg, mg_, lg) in zip(c["steps"], g["steps"]):
            n += 1; agree += int(tc == tg)
            if tc == tg: mdiff.append(abs(mc - mg_)); ldiff.append(abs(lc - lg))
    r = {"gate": "D1: the harness decode on the GPU vs the CPU engine (teacher-forced, real core + held-out rows)", "rows": len(res["cpu"]), "steps": n,
         "top1_agree": agree, "top1_agree_rate": round(agree / max(1, n), 5), "margin_absdiff_max": max(mdiff or [0]), "margin_absdiff_median": float(np.median(mdiff or [0])),
         "logit_absdiff_max": max(ldiff or [0]), "rows_with_identical_exits": ex_eq, "pass": agree / max(1, n) >= 0.995}
    json.dump(r, open(f"{out}/d1.json", "w"), indent=1); print(json.dumps(r, indent=1)); print("PASS" if r["pass"] else "FAIL")


def compare(cpu, gpu):
    n = agree = 0; mdiff = []; ldiff = []; ex_eq = 0
    inc = lambda rs: [[b - a for a, b in zip(p["exits"], q["exits"])] for p, q in zip([{"exits": [0] * len(rs[0]["exits"])}] + rs[:-1], rs)]
    for c, g, ce, ge in zip(cpu, gpu, inc(cpu), inc(gpu)):                 # exit counts are cumulative per decoder: compare each row's increment
        ex_eq += int(ce == ge)
        for (tc, mc, lc), (tg, mg_, lg) in zip(c["steps"], g["steps"]):
            n += 1; agree += int(tc == tg)
            if tc == tg: mdiff.append(abs(mc - mg_)); ldiff.append(abs(lc - lg))
    return {"rows": len(gpu), "steps": n, "top1_agree": agree, "top1_agree_rate": round(agree / max(1, n), 5), "margin_absdiff_max": max(mdiff or [0]),
            "logit_absdiff_max": max(ldiff or [0]), "rows_with_identical_exits": ex_eq, "pass": n > 0 and agree / n >= 0.995}


def server_gate(core, hb, out, nrows, ntok, N):
    import time
    cp = subprocess.run([sys.executable, __file__, "--side", "cpu", core, hb, f"{out}/cpu.json", str(nrows * N), str(ntok)],
                        env=dict(os.environ, OMNI_TRAIN_LIB=os.environ["CPU_LIB"]), capture_output=True, text=True, timeout=3600)
    open(f"{out}/cpu.log", "w").write(cp.stdout + cp.stderr)
    if cp.returncode: print("cpu FAILED", cp.stderr[-1500:]); sys.exit(2)
    cpu = json.load(open(f"{out}/cpu.json"))
    sd = f"{out}/srv"; os.makedirs(sd, exist_ok=True)
    for f_ in os.listdir(sd): os.remove(os.path.join(sd, f_)) if os.path.isfile(os.path.join(sd, f_)) else None
    srv = subprocess.Popen([os.environ["OMNI_GPU_BIN"], "serve", sd, "--slots", str(N), "--device", os.environ.get("OMNI_GPU_DEVICE", "")],
                           stdout=open(f"{out}/server.log", "w"), stderr=subprocess.STDOUT)
    t0 = time.time()
    cl = [subprocess.Popen([sys.executable, __file__, "--side", "gpu", core, hb, f"{out}/gpu{i}.json", str(nrows), str(ntok)],
                           env=dict(os.environ, OMNI_TRAIN_LIB=os.environ["GPU_LIB"], OMR_GPU_DECODE="1", OMR_GPU_SERVER=sd, OMR_GPU_SLOT=str(i),
                                    D1_TRAIN1="1", D1_ROW0=str(i * nrows)), stdout=open(f"{out}/gpu{i}.log", "w"), stderr=subprocess.STDOUT) for i in range(N)]
    rcs = [c.wait(timeout=3600) for c in cl]; wall = time.time() - t0
    open(f"{sd}/stop", "w").write("stop\n"); srv.wait(timeout=120)
    per = []
    for i in range(N):
        if rcs[i]: per.append({"client": i, "pass": False, "exit": rcs[i]}); continue
        g = json.load(open(f"{out}/gpu{i}.json")); per.append(dict(compare(cpu[i * nrows:(i + 1) * nrows], g), client=i))
    st = json.load(open(f"{sd}/stats.json")) if os.path.exists(f"{sd}/stats.json") else {}
    logs = "".join(open(f"{out}/gpu{i}.log").read() for i in range(N))
    r = {"gate": f"D2: the harness decode through the array server's decode service ({N} clients, one GPU context) vs the CPU engine", "clients": per,
         "server": st, "wall_s": round(wall, 1), "cpu_fallbacks": logs.count("continues on the CPU"), "server_decode_off": logs.count("server decode off"),
         "pass": all(p["pass"] for p in per) and logs.count("continues on the CPU") == 0 and st.get("decode_steps", 0) > 0}
    json.dump(r, open(f"{out}/d2.json", "w"), indent=1); print(json.dumps(r, indent=1)); print("PASS" if r["pass"] else "FAIL")


if __name__ == "__main__":
    main()

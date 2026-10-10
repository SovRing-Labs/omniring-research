#!/usr/bin/env python3
"""GROW-RUN-0 speed — the attention products as GEMMs (OMNI_TRAIN_ATTN_GEMM=1: qkT / pv / ptv → sgemm gnt / gnn / gtn over z = R·rows,
Prog.bgemm). The A40 profile of the 8-model school step: qkT 40 %, ptv + pv 14 % — one thread per output folding the dot product. Gate: the
same R-model program (centre form, units, the school switches) run with the switch OFF and ON → every per-step loss and every final C / Δ word
bit-identical (the GEMM template sums in the fold's k order), and the GPU ms per step of both.
  s6_attn_gemm.py [--dims small4|school] [--units 1] [--per 2] [--steps 4] [--sw school|none] [--device llvmpipe] [--out DIR]"""
import json, os, subprocess, sys, tempfile
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(os.path.dirname(HERE))

def main():
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    dn, U, per, S, swa, dev = opt("--dims", "small4"), opt("--units", "1"), opt("--per", "2"), opt("--steps", "4"), opt("--sw", "school"), opt("--device", "llvmpipe")
    out = opt("--out", f"{P}/results/cyclone/g3b"); os.makedirs(out, exist_ok=True); res = {}
    VAR, V0, V1 = opt("--var", "OMNI_TRAIN_ATTN_GEMM"), opt("--v0", "0"), opt("--v1", "1")   # any switch: run A = V0, run B = V1
    code = f'''
import sys, os, json, tempfile, numpy as np
sys.argv = ["s5", "--dims", "{dn}", "--units", "{U}", "--per", "{per}", "--steps", "{S}", "--sw", "{swa}", "--device", "{dev}"]
sys.path.insert(0, "{P}/tests/train"); import s5_array as m
'''
    # run s5's own GPU path in a child per mode (the switch is read at import), dumping losses + C/Δ
    runner = f"{HERE}/_s6_child.py"
    open(runner, "w").write('''import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s5_array as m
captured = {}
real = m.gpu_run
def spy(*a, **k):
    loss, W, raw, gms, info = real(*a, **k); captured.update(loss=loss, raw=raw, gms=gms, info=info); return loss, W, raw, gms, info
m.gpu_run = spy
sys.argv = ["s5"] + sys.argv[2:] + ["--out", os.environ["S6_OUT"]]   # full s5 path: its CPU reference also makes the T25 residues the switches read
try: m.main()
except SystemExit: pass
np.save(sys.argv[0] + ".npy", None) if False else None
o = os.environ["S6_DUMP"]; np.save(f"{o}/loss.npy", captured["loss"])
np.savez(f"{o}/w.npz", **{f"C:{n}": c for n, (c, d) in captured["raw"].items()}, **{f"D:{n}": d for n, (c, d) in captured["raw"].items()})
json.dump({"gpu_ms": captured["gms"], "passes": captured["info"].get("passes")}, open(f"{o}/info.json", "w"))
''')
    with tempfile.TemporaryDirectory(prefix="s6-") as Tm:
        for mode, val in (("0", V0), ("1", V1)):
            d = f"{Tm}/m{mode}"; os.makedirs(d)
            env = dict(os.environ, **{VAR: val}, S6_OUT=Tm, S6_DUMP=d)
            r = subprocess.run([sys.executable, runner, "x", "--dims", dn, "--units", U, "--per", per, "--steps", S, "--sw", swa, "--device", dev],
                               capture_output=True, text=True, env=env, timeout=7200)
            if r.returncode not in (0, 1) or not os.path.exists(f"{d}/loss.npy"): print(r.stderr[-1500:]); sys.exit(2)
            res[mode] = (np.load(f"{d}/loss.npy"), dict(np.load(f"{d}/w.npz")), json.load(open(f"{d}/info.json")))
    (l0, w0, i0), (l1, w1, i1) = res["0"], res["1"]
    bad_l = int((l0.view(np.uint32) != l1.view(np.uint32)).sum()); bad_w = sum(int((w0[k].view(np.uint32) != w1[k].view(np.uint32)).sum()) for k in w0)
    rec = {"gate": f"{VAR} {V0} vs {V1}: losses + weights compared word for word", "var": VAR, "v0": V0, "v1": V1, "dims": dn, "units": int(U), "per": int(per), "steps": int(S), "switches": swa,
           "device": dev, "loss_words_differ": bad_l, "weight_words_differ": bad_w,
           "loss_fold": l0.tolist(), "loss_gemm": l1.tolist(), "max_rel_loss_diff": float(np.max(np.abs(l0 - l1) / np.abs(l0))),
           "max_abs_weight_diff": max(float(np.max(np.abs(w0[k].astype(np.float64) - w1[k]))) for k in w0),
           "max_abs_weight": max(float(np.max(np.abs(w0[k]))) for k in w0), "gpu_ms_fold": round(i0["gpu_ms"], 2), "gpu_ms_gemm": round(i1["gpu_ms"], 2),
           "speedup": round(i0["gpu_ms"] / i1["gpu_ms"], 2) if i1["gpu_ms"] else None, "pass": bad_l == 0 and bad_w == 0}
    json.dump(rec, open(f"{out}/s6-{VAR.lower()}-{V0}-{V1}-{dn}-U{U}x{per}-{dev.split()[0].lower()}.json", "w"), indent=1); print(json.dumps(rec)); print("PASS" if rec["pass"] else "FAIL")
    sys.exit(0 if rec["pass"] else 1)

if __name__ == "__main__":
    main()

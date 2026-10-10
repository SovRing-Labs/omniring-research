#!/usr/bin/env python3
"""CYCLONE-ARRAY C2 S1 profile — where ONE training step's GPU time goes: the step (gen/train_step.build_train, 1 step: forward, backward,
AdamW) run once with per-pass GPU timestamps (OMNI_GPU_PROFILE=1); the time of every pass, summed per kernel, largest first.
  s1_profile.py [--dims school] [--device L4] [--out DIR]"""
import json, os, subprocess, sys, tempfile
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, f"{P}/gen"); sys.path.insert(0, HERE)
import train_step
from s1_grad import BIN, DIMS, batch

def main():
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    dn = opt("--dims", "school"); dims = DIMS[dn]; dev = opt("--device", "L4"); out = opt("--out", f"{P}/results/cyclone/c2-s1"); os.makedirs(out, exist_ok=True)
    V, D, L, H, T, B = (dims[k] for k in ("V", "D", "L", "H", "T", "B")); rng = np.random.default_rng(1)
    shapes = [("emb.weight", V * D)] + [(f"blocks.{l}.{n}", s) for l in range(L) for n, s in (("n1.weight", D), ("n2.weight", D), ("qkv.weight", 3 * D * D),
              ("o.weight", D * D), ("up.weight", 4 * D * D), ("down.weight", 4 * D * D))] + [("nf.weight", D)]
    params = [(n, (rng.standard_normal(s) * 0.02).astype(np.float32) if "n1" not in n and "n2" not in n and "nf" not in n else np.ones(s, np.float32)) for n, s in shapes]
    x, y = batch(V, T, B)
    with tempfile.TemporaryDirectory(prefix="omni-gpu-prof-") as Tm:
        text, outs, npass, nbuf = train_step.build_train(dims, params, [(x, y)], [3e-3], Tm)
        open(f"{Tm}/prog.txt", "w").write(text); od = f"{Tm}/o"
        r = subprocess.run([BIN, "session", f"{Tm}/prog.txt", "--device", dev, "--steps", "2", "--out", od], capture_output=True, text=True, timeout=7200,
                           env=dict(os.environ, OMNI_GPU_PROFILE="1"))
        if r.returncode: sys.exit(r.stderr[-1500:])
        info = json.loads(r.stdout.strip().splitlines()[-1]); prof = json.load(open(f"{od}/profile.json"))
    tot = {}; cnt = {}
    for n, ms in prof: tot[n] = tot.get(n, 0.0) + ms; cnt[n] = cnt.get(n, 0) + 1
    step = sum(tot.values()); rows = sorted(tot.items(), key=lambda kv: -kv[1])
    rec = {"dims": dims, "device": info["device"], "passes": npass, "step_gpu_ms": round(step, 3), "ms_per_step_wall": info["ms_per_step"],
           "by_kernel": [{"kernel": n, "ms": round(ms, 3), "share": round(ms / step, 4), "passes": cnt[n]} for n, ms in rows]}
    json.dump(rec, open(f"{out}/profile-{dn}-{dev.split()[0].lower()}.json", "w"), indent=1)
    print(f"{rec['device']}  passes {npass}  step GPU {step:.1f} ms  (wall {info['ms_per_step']:.1f} ms)")
    for row in rec["by_kernel"][:25]: print(f"  {row['kernel']:12} {row['ms']:9.3f} ms  {100 * row['share']:5.1f} %  ×{row['passes']}")

if __name__ == "__main__":
    main()

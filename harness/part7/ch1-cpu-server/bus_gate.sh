#!/usr/bin/env bash
# SHM-BUS-0 B2 gate (thead.rs harness side): one school day (learn_arm.sh), a fixed mean M = the OFF arm's day-1 weights + 0.01·noise.
#  P: today's PAR day merge (PAR_DIR with merged-d1.bin = M pre-placed)   Q: bus, BUS_EVERY=0 (PAR point), BUS_K=1, mean.w = M
#  R: bus, BUS_EVERY=0, BUS_K=0.5: ckpt must equal slab + 0.5·(M − slab) exactly (slab = h0.w, the weights written before the pull)
# Pass: ckpt(P) == ckpt(Q) bitwise; on the non-BitLinear params P == M and R == the formula bitwise (BitLinear latents are re-snapped by
# sync_latent after the merge, in both paths — first run 10-08 found this: 611,245 BL entries differ from M in P AND Q alike). (OFF == previous: learn_off_gate.sh.)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); R=$HOME/ai-stack/projects/thead-trial/runtime; E=$HOME/ai-stack/projects/thead-trial/engine/omni_train
BIN=$R/target-ramkit/release/omni-render; LIB=$E/libomnitrain_trial_ramkit.so
OUT=$HERE/results/bus; G=/dev/shm/thead-busgate; rm -rf "$G"; mkdir -p "$OUT" "$G/par" "$G/busQ" "$G/busR"
python3 -c "
import numpy as np; a=np.fromfile('$HERE/results/learn_off/A/ckpt.bin', np.float32); r=np.random.default_rng(1)
m=(a+np.float32(0.01)*r.standard_normal(a.size).astype(np.float32)).astype(np.float32); m.tofile('$G/M.bin')"
cp "$G/M.bin" "$G/par/merged-d1.bin"; cp "$G/M.bin" "$G/busQ/mean.w"; cp "$G/M.bin" "$G/busR/mean.w"
export DAYS=1
"$HERE/learn_arm.sh" "$OUT/P" "$BIN" "$LIB" PAR_DIR=$G/par PAR_ID=0 > "$OUT/P.log" 2>&1 &
"$HERE/learn_arm.sh" "$OUT/Q" "$BIN" "$LIB" BUS_DIR=$G/busQ PAR_ID=0 BUS_EVERY=0 BUS_K=1 BUS_WAIT=0 > "$OUT/Q.log" 2>&1 &
"$HERE/learn_arm.sh" "$OUT/R" "$BIN" "$LIB" BUS_DIR=$G/busR PAR_ID=0 BUS_EVERY=0 BUS_K=0.5 BUS_WAIT=0 > "$OUT/R.log" 2>&1 &
wait
python3 - "$OUT" "$G" <<'EOF'
import json, os, sys, numpy as np
o, g = sys.argv[1], sys.argv[2]; rd = lambda p: np.fromfile(p, np.float32)
M, P, Q, Rk, slab = rd(f"{g}/M.bin"), rd(f"{o}/P/ckpt.bin"), rd(f"{o}/Q/ckpt.bin"), rd(f"{o}/R/ckpt.bin"), rd(f"{g}/busR/h0.w")
want = slab + np.float32(0.5) * (M - slab); bl = np.zeros(M.size, bool)
import re
for e in json.load(open(f"{o}/R/ckpt.json")):   # BitLinear latents are re-snapped by sync_latent after every merge / pull (PAR does it too)
    if re.match(r"blocks\.\d+\.(qkv|o|up|down)\.weight", e["name"]): bl[e["offset"] // 4:e["offset"] // 4 + e["len"]] = True
eq = lambda a, b: bool(np.array_equal(a.view(np.uint32), b.view(np.uint32)))
r = {"Q_eq_P": eq(Q, P), "nonBL_P_eq_M": eq(P[~bl], M[~bl]), "nonBL_R_formula_exact": eq(Rk[~bl], want[~bl]),
     "slab_size_eq_ckpt": slab.size == P.size, "chk": json.load(open(f"{g}/busR/h0.chk")), "rec": json.load(open(f"{g}/busR/h0.json")),
     "logs": {k: [l.strip() for l in open(f"{o}/{k}.log") if "[bus]" in l or "[par]" in l] for k in "PQR"}}
r["pass"] = r["Q_eq_P"] and r["nonBL_P_eq_M"] and r["nonBL_R_formula_exact"]
json.dump(r, open(f"{o}/verdict.json", "w"), indent=1); print(json.dumps(r)); sys.exit(0 if r["pass"] else 1)
EOF

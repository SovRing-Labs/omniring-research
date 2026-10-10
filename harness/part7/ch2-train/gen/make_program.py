#!/usr/bin/env python3
"""GROW-RUN-0 G3 — the program the GPU engine library runs (libomnitrain_gpu.so): from the model the harness built (dims, the engine's
parameter list in P order, the school switches the harness turned on — recorded by the library from the om_set_* calls) → the resident
training step (gen/train_step.build_loop) + its host-I/O map.
  make_program.py CFG.json OUTDIR  → OUTDIR/prog.txt, OUTDIR/io.json ({name: session buffer index}), OUTDIR/meta.json
CFG = {"dims": {V, D, L, H, T, B}, "params": [[name, size], …], "sw": {…build_loop switches…}, "aux": {"t25lane": […], "eos": int}}
"R" with "decode": R harness decoders in one step (the array server's decode service, queue 2).
"R": n (G3b-4, the array server src/array.rs) → R independent harness models in one step (the replica form, C2 S2) + OUTDIR/array.txt (the slot
layout: n V B T H + one `param NAME SIZE` line per parameter)."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import train_step

def main():
    cfg = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    params = [(n, np.zeros(int(sz), np.float32)) for n, sz in cfg["params"]]   # weights arrive from the engine every step
    sw = cfg.get("sw", {})
    if "p3" in sw: sw["p3"] = tuple(sw["p3"])
    if "harm" in sw: sw["harm"] = tuple(sw["harm"])
    R = int(cfg.get("R", 1))
    if cfg.get("decode"):                                                      # GPU DECODE (decode_step.py): stations × one token per step
        import decode_step
        dc = cfg["decode"]
        text, ix, npass, nbuf = decode_step.build_decode(cfg["dims"], params, out, sw, cfg.get("aux", {}), int(dc["S"]), int(dc["Tmax"]),
                                                         params_R=[params] * R if R > 1 else None, exit_theta=float(dc.get("exit_theta", 0)), route_sat=float(dc.get("route_sat", 0)))
        open(f"{out}/prog.txt", "w").write(text); json.dump(ix, open(f"{out}/io.json", "w"), indent=1)
        print(json.dumps({"passes": npass, "buffers": nbuf, "io": len(ix), "decode": dc})); return
    text, ix, npass, nbuf = train_step.build_loop(cfg["dims"], params, out, sw=sw, aux=cfg.get("aux", {}), params_R=[params] * R if R > 1 else None,
                                                  fwd_only=bool(cfg.get("fwd")))   # "fwd": the forward alone (eval: loss, head stats, top-1 per token)
    d = cfg["dims"]
    open(f"{out}/array.txt", "w").write("".join(f"{k} {v}\n" for k, v in (("n", d["B"] * d["T"]), ("V", d["V"]), ("B", d["B"]), ("T", d["T"]), ("H", d["H"]), ("R", R)))
                                         + "".join(f"param {n} {sz}\n" for n, sz in cfg["params"]))
    open(f"{out}/prog.txt", "w").write(text); json.dump(ix, open(f"{out}/io.json", "w"), indent=1)
    json.dump({"passes": npass, "buffers": nbuf, "frozen": sorted(train_step.FROZEN(sw))}, open(f"{out}/meta.json", "w"))
    print(json.dumps({"passes": npass, "buffers": nbuf, "io": len(ix)}))

if __name__ == "__main__":
    main()

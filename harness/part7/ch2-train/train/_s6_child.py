import sys, os, json, numpy as np
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

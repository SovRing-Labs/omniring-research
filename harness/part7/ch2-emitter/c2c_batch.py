#!/usr/bin/env python3
"""CYCLONE-ARRAY C2c gate — the emitter's batch axes (spirv.py --batch, template T0B): one launch serves N rows × R replicas.
For every wall-passed spec in gpu/specs/engine0–5: emit T0B twice (byte-identical), spirv-val, then on each device:
  batched  — the op's recorded engine rows (examples + validate + holdout) grouped by shape (scalar values, list lengths); each group runs
             as ONE dispatch with 2 replicas × N/2 rows (rows q-major in the buffers, strides by spec constants); every row's output must
             match its recorded answer at the check_host tolerance (same as V3).
  shared   — the op's first row stored ONCE with row stride 0 and replica stride 0 (every row reads the same slice: the shared-weights
             case), dispatched as 4 rows × 2 replicas → 8 outputs, each must match that row's answer.
Run OUTSIDE kernel-bash Landlock (systemd-run / tw unit) so the Intel device is visible.
  c2c_batch.py [--devices llvmpipe,Intel] [--out DIR]   → DIR/batch.json; exit 1 on any failure"""
import glob, hashlib, json, math, os, struct, subprocess, sys, tempfile
P = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); G = os.path.normpath(f"{P}/../thead-trial/gpu")
BIN = f"{P}/target/release/omni-gpu"; DIRS = ["engine0", "engine1", "engine2", "engine3", "engine4", "engine5"]; LOCAL = 64
BS, OBS = 200, 290

def names(d):
    ids = {json.loads(l)["need"]: os.path.basename(f)[:-6] for f in glob.glob(f"{G}/specs/{d}/pod/*.jsonl") for l in open(f)}
    return [ids[json.loads(l)["need"]] for l in open(f"{G}/specs/{d}/pod-specs.wall.jsonl") if l.strip()]

def bits(v, t): return (int(v) & 0xFFFFFFFF) if t == "int" else struct.unpack("<I", struct.pack("<f", float(v)))[0]

def job(spv, at, rows, Q, Rq, nout, shared=False):
    """rows = [(ins, want)] q-major (row of replica q, index r = rows[q*Rq + r]); shared → rows[0] stored once, strides 0"""
    ins0 = rows[0][0]
    spec = [(k, bits(v, t)) for k, (v, t) in enumerate(zip(ins0, at)) if t in ("int", "f32")] + [(100, LOCAL)]
    binds = []
    for k, t in enumerate(at):
        if t not in ("f32list", "list"): continue
        ln = len(ins0[k]); src = [ins0] if shared else [r[0] for r in rows]
        spec += [(BS + 3 * k, 0 if shared else ln), (BS + 3 * k + 1, 0 if shared else Rq * ln), (BS + 3 * k + 2, ln)]
        vals = [x for ins in src for x in ins[k]]
        binds.append((f"f {len(vals)} " + " ".join(repr(float(x)) for x in vals)) if t == "f32list" else (f"i {len(vals)} " + " ".join(str(int(x)) for x in vals)))
    spec += [(OBS, nout), (OBS + 1, Rq * nout)]
    binds.append(f"z {4 * nout * Q * Rq}")
    g = f"{max(1, -(-nout // LOCAL))},{Rq},{Q}"
    return f"JOB {spv} {g} {len(spec)} " + " ".join(f"{k} {b}" for k, b in spec) + f" {len(binds)} " + " ".join(binds) + f" {len(binds) - 1}"

def row_ok(ins, at, want, got, rtol=1e-4, atol=1e-5):
    flat = [abs(float(v)) for x, t in zip(ins, at) if t in ("f32", "f32list") for v in (x if isinstance(x, list) else [x])]
    arow = max(atol, 16 * 2.0 ** -24 * max([v for v in flat if math.isfinite(v)], default=0.0)); worst = 0.0
    if len(got) != len(want): return False, worst
    for gv, wv in zip(got, want):
        wv = float(wv)
        if math.isnan(wv):
            if not math.isnan(gv): return False, worst
            continue
        if math.isinf(wv):
            if gv != wv: return False, worst
            continue
        tol = arow + rtol * abs(wv); worst = max(worst, abs(gv - wv) / tol if math.isfinite(gv) else math.inf)
        if not abs(gv - wv) <= tol: return False, worst
    return True, worst

def main():
    a = sys.argv[1:]; opt = lambda k, v: a[a.index(k) + 1] if k in a else v
    devices = opt("--devices", "llvmpipe,Intel").split(","); out = opt("--out", f"{P}/results/cyclone/c2c"); os.makedirs(out, exist_ok=True)
    fails, rec = [], {"emit": {}, "val": {}, "ops": {}}
    with tempfile.TemporaryDirectory(prefix="omni-gpu-c2c-") as T:
        for d in DIRS:
            nm = names(d); spec = f"{G}/specs/{d}/pod-specs.wall.jsonl"; srows = [json.loads(l) for l in open(spec) if l.strip()]
            for tgt in (f"{T}/a/{d}", f"{T}/b/{d}"):
                r = subprocess.run([sys.executable, f"{G}/emit/spirv.py", spec, "--names", ",".join(nm), "--out", tgt, "--batch"], capture_output=True, text=True)
                if r.returncode: fails.append(f"{d}: emit failed {r.stderr[-400:]}")
            same = json.load(open(f"{T}/a/{d}/manifest.json")) == json.load(open(f"{T}/b/{d}/manifest.json"))
            rec["emit"][d] = {"modules": len(nm), "deterministic": same}
            if not same: fails.append(f"{d}: two batch emits differ")
            for f in sorted(glob.glob(f"{T}/a/{d}/*.spv")):
                v = subprocess.run(["spirv-val", "--target-env", "vulkan1.1", f], capture_output=True, text=True)
                rec["val"][f"{d}/{os.path.basename(f)}"] = "pass" if not v.returncode else v.stderr.strip()[:300]
                if v.returncode: fails.append(f"spirv-val {d}/{os.path.basename(f)}: {v.stderr.strip()[:200]}")
            lines, index = [], []
            for row, n in zip(srows, nm):
                at = row["args"]; spv = f"{T}/a/{d}/{n}.spv"
                pairs = [(ins, w if isinstance(w, list) else [w]) for k in ("examples", "validate", "holdout") for ins, w in row.get(k, [])]
                grp = {}
                for ins, w in pairs:
                    key = json.dumps([v if t in ("int", "f32") else len(v) for v, t in zip(ins, at)] + [len(w)])
                    grp.setdefault(key, []).append((ins, w))
                for rs in grp.values():
                    Q = 2 if len(rs) >= 2 else 1; Rq = len(rs) // Q; main_rows, rest = rs[:Q * Rq], rs[Q * Rq:]
                    for chunk, q in ((main_rows, Q), (rest, 1)):
                        if not chunk: continue
                        r_ = len(chunk) // q; lines.append(job(spv, at, chunk, q, r_, len(chunk[0][1]))); index.append((d, n, at, chunk, "batched"))
                if pairs:
                    lines.append(job(spv, at, [pairs[0]] * 8, 2, 4, len(pairs[0][1]), shared=True)); index.append((d, n, at, [pairs[0]] * 8, "shared"))
            for dev in devices:
                p = subprocess.run([BIN, "batch", "--device", dev], input="\n".join(lines) + "\n", capture_output=True, text=True, timeout=3600)
                outs = p.stdout.splitlines()
                if p.returncode or len(outs) != len(lines): fails.append(f"{dev} {d}: batch exit {p.returncode}, {len(outs)}/{len(lines)} answered {p.stderr[-300:]}")
                for (dd, n, at, chunk, kind), o in zip(index, outs):
                    s = rec["ops"].setdefault(dev, {}).setdefault(f"{dd}/{n}", {"dispatches": 0, "rows": 0, "bad": 0, "errors": 0, "worst_over_tol": 0.0, "shared_ok": None})
                    f = o.split(); s["dispatches"] += 1
                    if not f or f[0] != "OK": s["errors"] += 1; s.setdefault("first_error", o[:300]); fails.append(f"{dev} {dd}/{n} {kind}: {o[:200]}"); continue
                    got = [float(x) for x in f[3:]]; nout = len(chunk[0][1]); good = True
                    for i, (ins, w) in enumerate(chunk):
                        ok, worst = row_ok(ins, at, w, got[i * nout:(i + 1) * nout]); s["worst_over_tol"] = max(s["worst_over_tol"], worst); s["rows"] += 1
                        if not ok:
                            good = False; s["bad"] += 1; s.setdefault("first_bad", f"{kind} row {i}: got {got[i * nout:(i + 1) * nout][:4]} want {w[:4]}")
                    if kind == "shared": s["shared_ok"] = good
                    if not good: fails.append(f"{dev} {dd}/{n} {kind}: {s.get('first_bad', '')}"[:300])
                print(f"{dev:10} {d}: " + " ".join(f"{k.split('/')[1]}={'pass' if not v['bad'] and not v['errors'] else 'FAIL'}({v['rows']} rows/{v['dispatches']} launches)"
                                                for k, v in rec["ops"].get(dev, {}).items() if k.startswith(d + "/")), flush=True)
    for dev in rec["ops"]:
        for s in rec["ops"][dev].values(): s["worst_over_tol"] = round(s["worst_over_tol"], 4)
    rec.update({"devices": devices, "fails": fails, "verdict": "pass" if not fails else "fail",
                "rows_checked": {dev: sum(s["rows"] for s in ops.values()) for dev, ops in rec["ops"].items()},
                "launches": {dev: sum(s["dispatches"] for s in ops.values()) for dev, ops in rec["ops"].items()}})
    json.dump(rec, open(f"{out}/batch.json", "w"), indent=1, sort_keys=True)
    print("\n".join(fails[:30]) if fails else f"C2c BATCH PASS: rows {rec['rows_checked']} in launches {rec['launches']}"); sys.exit(1 if fails else 0)

if __name__ == "__main__": main()

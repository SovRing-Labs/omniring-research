#!/usr/bin/env python3
"""OMNI-RENDER-GPU-0 V3 gate — the SPIR-V back-end (thead-trial/gpu/emit/spirv.py) over every wall-passed spec in gpu/specs/engine0–5:
  1 emit twice → byte-identical modules (determinism); the kept copy goes to gpu/emit/spv/<engine>/ (+ manifest.json)
  2 spirv-val --target-env vulkan1.1 on every module (the SPIR-V tools' own validator, a black box)
  3 parity: every recorded engine row of every spec on each device (gpu/emit/check_vk.py, check_host tolerance)
Run OUTSIDE kernel-bash Landlock (systemd-run / tw unit) so the Intel ANV device is visible.
  v3_parity.py [--devices llvmpipe,Intel] [--out DIR] [--keep-dir DIR]   → DIR/parity.json; exit 1 on any failure"""
import glob, hashlib, json, os, subprocess, sys, tempfile
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); G = os.path.normpath(f"{P}/../thead-trial/gpu")
DIRS = ["engine0", "engine1", "engine2", "engine3", "engine4", "engine5"]

def names(d):
    ids = {json.loads(l)["need"]: os.path.basename(f)[:-6] for f in glob.glob(f"{G}/specs/{d}/pod/*.jsonl") for l in open(f)}
    return [ids[json.loads(l)["need"]] for l in open(f"{G}/specs/{d}/pod-specs.wall.jsonl") if l.strip()]

def main():
    a = sys.argv[1:]; opt = lambda k, v: a[a.index(k) + 1] if k in a else v
    devices = opt("--devices", "llvmpipe,Intel").split(","); out = opt("--out", f"{P}/results/v3"); keep = opt("--keep-dir", f"{G}/emit/spv")
    os.makedirs(out, exist_ok=True); fails, rec = [], {"emit": {}, "val": {}, "parity": {}}
    with tempfile.TemporaryDirectory(prefix="omni-gpu-v3-") as T:
        for d in DIRS:
            nm = ",".join(names(d)); spec = f"{G}/specs/{d}/pod-specs.wall.jsonl"
            for tgt in (f"{T}/a/{d}", f"{keep}/{d}"):
                r = subprocess.run([sys.executable, f"{G}/emit/spirv.py", spec, "--names", nm, "--out", tgt], capture_output=True, text=True)
                if r.returncode: fails.append(f"{d}: emit failed {r.stderr[-400:]}")
            ma, mb = (json.load(open(f"{x}/manifest.json")) for x in (f"{T}/a/{d}", f"{keep}/{d}"))
            rec["emit"][d] = {"modules": len(names(d)), "deterministic": ma == mb}
            if ma != mb: fails.append(f"{d}: two emits differ")
            for f in sorted(glob.glob(f"{keep}/{d}/*.spv")):
                v = subprocess.run(["spirv-val", "--target-env", "vulkan1.1", f], capture_output=True, text=True)
                rec["val"][f"{d}/{os.path.basename(f)}"] = "pass" if not v.returncode else v.stderr.strip()[:300]
                if v.returncode: fails.append(f"spirv-val {d}/{os.path.basename(f)}: {v.stderr.strip()[:200]}")
            for dev in devices:
                r = subprocess.run([sys.executable, f"{G}/emit/check_vk.py", f"{keep}/{d}", spec, nm, "--device", dev], capture_output=True, text=True, timeout=3600)
                ls = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
                for s in ls:
                    if "op" in s:
                        rec["parity"].setdefault(dev, {})[s["op"]] = s
                        if s["verdict"] != "pass": fails.append(f"{dev} {d}/{s['op']}: bad {s['bad']} errors {s['errors']} {s.get('first_bad') or s.get('first_error', '')}"[:300])
                if r.returncode and not any("op" in s for s in ls): fails.append(f"{dev} {d}: check_vk exit {r.returncode} {r.stderr[-300:]}")
                print(f"{dev:10} {d}: " + " ".join(f"{s['op']}={s['verdict']}" for s in ls if "op" in s), flush=True)
    rec["devices"] = devices; rec["fails"] = fails; rec["verdict"] = "pass" if not fails else "fail"
    rec["modules"] = sum(x["modules"] for x in rec["emit"].values())
    rec["rows_checked"] = {dev: sum(s["rows"] for s in ops.values()) for dev, ops in rec["parity"].items()}
    json.dump(rec, open(f"{out}/parity.json", "w"), indent=1, sort_keys=True)
    print("\n".join(fails) if fails else f"V3 PARITY PASS: {rec['modules']} modules, rows {rec['rows_checked']}"); sys.exit(1 if fails else 0)

if __name__ == "__main__": main()

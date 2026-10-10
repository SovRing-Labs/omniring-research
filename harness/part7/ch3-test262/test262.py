#!/usr/bin/env python3
"""DOCTOR-INTERP-0 N6 — test262 (tc39, BSD; <home>/projects/test262, no-train: tests only) against our JS engine: `omni-render js-src FILE [--script]`
(native parser jsparse → jsi). Exit 0 = ran, 1 = uncaught (stderr "Uncaught <Type>…"), 2 = parse error.
Rules from test262's INTERPRETING.md: harness assert.js + sta.js (+ doneprintHandle.js for async) + the test's `includes`; flags onlyStrict (prefix
"use strict"), noStrict / raw (raw = no harness), module (parsed as a module), async (pass = "Test262:AsyncTestComplete" printed); `negative`
{phase: parse|early|resolution|runtime, type} → must fail that way. Baseline runs each test ONCE (strict only when onlyStrict; test262 asks for both
modes — the second mode is a later round). A print() shim is prepended (the engine has no print).

  python3 test262.py --bin B --root <home>/projects/test262 [--dirs test/built-ins/Math,…] [--jobs 6] [--timeout 10] --out results.jsonl
"""
import argparse, concurrent.futures as cf, json, os, re, subprocess, sys, tempfile, time

FM = re.compile(r"/\*---(.*?)---\*/", re.S)
SHIM = "var print = function () { var s = ''; for (var i = 0; i < arguments.length; i++) s += (i ? ' ' : '') + String(arguments[i]); if (typeof console !== 'undefined' && console.log) console.log(s); };\n"

def meta(src):
    m = FM.search(src); y = m.group(1) if m else ""
    def lst(key):
        r = re.search(rf"^{key}:\s*\[(.*?)\]", y, re.M)
        if r: return [x.strip() for x in r.group(1).split(",") if x.strip()]
        r = re.search(rf"^{key}:\s*\n((?:\s+-\s*.+\n?)+)", y, re.M)
        return [x.strip()[1:].strip() for x in r.group(1).splitlines() if x.strip().startswith("-")] if r else []
    neg = None
    r = re.search(r"^negative:\s*\n\s+phase:\s*(\w+)\s*\n\s+type:\s*(\w+)", y, re.M)
    if r: neg = (r.group(1), r.group(2))
    return {"includes": lst("includes"), "flags": lst("flags"), "features": lst("features"), "negative": neg}

def one(args):
    path, root, binp, timeout = args
    src = open(path, encoding="utf-8", errors="replace").read(); m = meta(src); fl = set(m["flags"])
    if "CanBlockIsTrue" in fl: return {"test": os.path.relpath(path, root), "verdict": "skip", "why": "CanBlockIsTrue"}
    parts = []
    if "raw" not in fl:
        parts.append(SHIM)
        for h in ["assert.js", "sta.js"] + (["doneprintHandle.js"] if "async" in fl else []) + m["includes"]:
            hp = os.path.join(root, "harness", h)
            if not os.path.exists(hp): return {"test": os.path.relpath(path, root), "verdict": "skip", "why": f"missing include {h}"}
            parts.append(open(hp, encoding="utf-8").read())
    body = "\n".join(parts) + "\n" + src
    if "onlyStrict" in fl: body = '"use strict";\n' + body
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f: f.write(body); tmp = f.name
    cmd = [binp, "js-src", tmp] + ([] if "module" in fl else ["--script"])
    t0 = time.time()
    try: p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout); rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired: rc, out, err = -9, "", "timeout"
    finally: os.unlink(tmp)
    ms = int((time.time() - t0) * 1000); neg = m["negative"]
    if rc == -9: v, why = "fail", "timeout"
    elif rc not in (0, 1, 2): v, why = "fail", f"crash rc {rc}: {err.strip().splitlines()[-1][:120] if err.strip() else ''}"
    elif neg:
        phase, typ = neg
        if phase in ("parse", "early"): ok = rc == 2 or (rc == 1 and typ in err)
        else: ok = rc == 1 and typ in err
        v, why = ("pass", "") if ok else ("fail", f"expected {phase} {typ}, got rc {rc} {err.strip()[:100]}")
    elif "async" in fl:
        ok = rc == 0 and "Test262:AsyncTestComplete" in out
        v, why = ("pass", "") if ok else ("fail", (out + err).strip().splitlines()[-1][:120] if (out + err).strip() else f"rc {rc}, no completion")
    else:
        v, why = ("pass", "") if rc == 0 else ("fail", err.strip().splitlines()[-1][:120] if err.strip() else f"rc {rc}")
    return {"test": os.path.relpath(path, root), "verdict": v, "why": why, "ms": ms, "features": m["features"]}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--bin", required=True); ap.add_argument("--root", default=os.path.expanduser("<home>/projects/test262"))
    ap.add_argument("--dirs", default="test"); ap.add_argument("--jobs", type=int, default=6); ap.add_argument("--timeout", type=float, default=10); ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    files = []
    for d in a.dirs.split(","):
        for dp, _, fs in os.walk(os.path.join(a.root, d)):
            files += [os.path.join(dp, f) for f in fs if f.endswith(".js") and "_FIXTURE" not in f]
    files.sort()
    if a.limit: files = files[:a.limit]
    t0 = time.time(); res = []
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for r in ex.map(one, [(f, a.root, a.bin, a.timeout) for f in files]): res.append(r)
    with open(a.out, "w") as f:
        for r in res: f.write(json.dumps(r) + "\n")
    tot = {"pass": 0, "fail": 0, "skip": 0}; by = {}
    for r in res:
        tot[r["verdict"]] += 1; k = "/".join(r["test"].split("/")[:3]); by.setdefault(k, {"pass": 0, "fail": 0, "skip": 0})[r["verdict"]] += 1
    run = tot["pass"] + tot["fail"]
    print(json.dumps({"tests": len(res), **tot, "pass_rate": round(tot["pass"] / max(1, run), 4), "secs": round(time.time() - t0, 1)}))
    for k, v in sorted(by.items(), key=lambda kv: -(kv[1]["pass"] + kv[1]["fail"]))[:25]:
        n = v["pass"] + v["fail"]; print(f"  {k:45} {v['pass']:>6}/{n:<6} {100 * v['pass'] / max(1, n):5.1f}%")

if __name__ == "__main__": main()

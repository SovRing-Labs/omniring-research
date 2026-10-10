#!/usr/bin/env python3
"""omnikit selftest — one PASS/FAIL line per core (omnikit). Per core: (1) its registry gate command, (2) one known-answer fire
through `bin/core-registry fire` (the exact path corehostd takes; receipt appended), (3) when corehostd answers on 127.0.0.1:47820, the
same fire over HTTP. CORES_DB / CORE_RECEIPTS env select the registry (a scratch one on the laptop). Exit 0 = every core PASS.
  python3 selftest.py [--no-http] [--only hdc.sift,ring.crt]"""
import argparse, json, os, sqlite3, subprocess, sys, tempfile, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
AI = os.environ.get("CH_AI") or os.path.abspath(os.path.join(HERE, "..", "..", ".."))
REG = os.path.join(AI, "bin", "core-registry")
DB = os.environ.get("CORES_DB", os.path.join(AI, "control-center", "cores.db"))
CH = os.environ.get("CH_URL", "http://127.0.0.1:47820")
SYMS = [f"s{i}" for i in range(50)]

# core, op, input, check(output) -> bool
CASES = [
    ("hdc.sift", "sift", {"items": [{"sym": "s3"}, {"sym": "s9"}], "codebook": {"syms": SYMS}}, lambda o: sorted(o["above"]) == ["s3", "s9"]),
    ("hdc.sift", "hamming", {"query": {"sym": "s7", "flip": 0.25}, "codebook": {"syms": SYMS}, "dims": 4096, "ternary": True, "top": 1},
     lambda o: o["hits"][0]["label"] == "s7"),
    ("hdc.bind", "bind", {"a": {"sym": "x"}, "b": {"sym": "y"}}, lambda o: o["ok"] and len(o["phases"]) == 1024),
    ("hdc.bundle", "bundle", {"items": [{"sym": "x"}, {"sym": "y"}]}, lambda o: o["ok"] and o["n_items"] == 2 and o["slot"]["scale"] > 0),
    ("hdc.resonate", "resonate", {"coord": 777}, lambda o: o["x"] == 777 and o["check_ok"]),
    ("ring.crt", "crt", {"residues": [2, 3, 2], "moduli": [3, 5, 7]}, lambda o: o["x"] == 23),
    ("ring.peel", "peel", {"coords": [10, 200, 1200]}, lambda o: o["exact"]),
    ("arcd.solve", "solve", {"domain": "arith.mul", "i": 2, "seed": 1}, lambda o: o["verified"]),
    ("arcd.verify", "verify", None, lambda o: o["verified"]),   # input = the solve case's problem + answer
]


def sh(cmd, env=None, timeout=300):
    r = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, timeout=timeout, cwd=AI, env=env)
    return r.returncode, r.stdout, r.stderr


def health():
    try:
        with urllib.request.urlopen(CH + "/health", timeout=5) as r:
            return r.status == 200
    except Exception:  # noqa: BLE001
        return False


def fire_http(core, op, args):
    body = json.dumps({"args": args, "caller": "omnikit-selftest", "priority": "interactive"}).encode()
    req = urllib.request.Request(f"{CH}/cores/{core}/{op}", data=body, method="POST", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-http", action="store_true")
    ap.add_argument("--only")
    a = ap.parse_args()
    only = set(a.only.split(",")) if a.only else None
    con = sqlite3.connect(DB)
    gates = dict(con.execute("SELECT core, gate FROM cores"))
    http = (not a.no_http) and health()
    tmp = tempfile.mkdtemp(prefix="omnikit-selftest-")
    solved, fails, gated = None, 0, set()
    for core, op, inp, check in CASES:
        if only and core not in only:
            continue
        t0 = time.time(); notes = []
        ok = core in gates
        if not ok:
            notes.append("not in registry")
        if ok and core not in gated:                       # the gate once per core
            rc, out, err = sh(gates[core]); gated.add(core)
            ok = rc == 0; notes.append("gate " + ("ok" if ok else f"rc {rc}: {(err or out).strip().splitlines()[-1:]}"))
        if ok:
            if inp is None:
                inp = {"domain": "arith.mul", "problem": solved["problem"], "answer": solved["answer"]} if solved else {}
            fin, fout = os.path.join(tmp, f"{core}.{op}.in.json"), os.path.join(tmp, f"{core}.{op}.out.json")
            json.dump(inp, open(fin, "w"))
            rc, out, err = sh([sys.executable, REG, "fire", core, op, "--arg", f"in={fin}", "--arg", f"out={fout}", "--caller", "omnikit-selftest"])
            try:
                rec = json.loads(out.strip().splitlines()[-1]); o = json.load(open(fout))
                ok = rec["verdict"] == "pass" and bool(check(o)); notes.append(f"fire {rec['verdict']} {rec['ms']}ms")
                if core == "arcd.solve" and ok:
                    solved = o
            except Exception as e:  # noqa: BLE001
                ok = False; notes.append(f"fire error {type(e).__name__}: {e} {err.strip()[-200:]}")
            if ok and http:
                fout2 = fout.replace(".out.json", ".http.json")
                try:
                    rec = fire_http(core, op, {"in": fin, "out": fout2})
                    rec = rec.get("receipt", rec)              # corehostd wraps the §2 receipt: {"ok", "receipt"}
                    ok = rec.get("verdict") == "pass" and bool(check(json.load(open(fout2))))
                    notes.append(f"corehostd {rec.get('verdict')}{' cached' if rec.get('cached') else ''} {rec.get('ms')}ms")
                except Exception as e:  # noqa: BLE001
                    ok = False; notes.append(f"corehostd error {type(e).__name__}: {e}")
        fails += not ok
        print(f"{'PASS' if ok else 'FAIL'} {core}.{op} · {' · '.join(notes)} · {time.time() - t0:.1f}s", flush=True)
    if not http and not a.no_http:
        print(f"note: corehostd not reachable at {CH} — registry fires only")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

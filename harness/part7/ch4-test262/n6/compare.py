"""test262 round vs baseline, per test: gains, REGRESSIONS (passed before, fail now — must be 0 or explained), net. Usage: compare.py BASE NEW"""
import json, subprocess, sys, collections
def load(p):
    txt = subprocess.run(["zstd", "-dc", p], capture_output=True, text=True).stdout if p.endswith(".zst") else open(p).read()
    return {r["test"]: r for r in map(json.loads, txt.splitlines()) if r}
a, b = load(sys.argv[1]), load(sys.argv[2])
gain = [t for t in b if b[t]["verdict"] == "pass" and a.get(t, {}).get("verdict") == "fail"]
reg = [t for t in b if b[t]["verdict"] == "fail" and a.get(t, {}).get("verdict") == "pass"]
pa = sum(r["verdict"] == "pass" for r in a.values()); pb = sum(r["verdict"] == "pass" for r in b.values())
print(json.dumps({"base_pass": pa, "new_pass": pb, "net": pb - pa, "gains": len(gain), "regressions": len(reg), "tests": len(b)}))
print("gains by area:", collections.Counter("/".join(t.split("/")[1:4]) for t in gain).most_common(8))
for t in reg[:25]: print("REGRESSION", t, "—", b[t]["why"][:110])

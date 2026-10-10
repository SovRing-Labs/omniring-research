# math core M5 bar: math.kb explain names the concept from FRESH rows (generator seed 99, levels 1–3) for ≥ 8/10; 4 negative controls → none.
import json, subprocess, random, sys
sys.path.insert(0, "<workspace>/projects/math-core/gen"); import mathgen
res = {}
for c, (mk, sv, vf) in mathgen.GENS.items():
    R = random.Random(99); rows = []
    for i in range(24):
        p = mk(R, 1 + i % 3); a, _ = sv(p); rows.append([list(p.values()), a])
    open(f"m5/rows.{c}.jsonl", "w").write("".join(json.dumps(r) + "\n" for r in rows))
    out = json.loads(subprocess.run(["<workspace>/bin/math-kb", "explain", "--rows", f"m5/rows.{c}.jsonl"], capture_output=True, text=True).stdout)
    res[c] = out["explained_by"]; print(c.ljust(14), "→", out["explained_by"])
R = random.Random(5); neg = {
 "a_plus_b": [[[x, y], x + y] for x, y in [(R.randint(0, 999), R.randint(1, 999)) for _ in range(24)]],
 "square_plus_one": [[[n], n * n + 1] for n in [R.randint(0, 3000) for _ in range(24)]],
 "list_len": [[[v], len(v)] for v in [[R.randint(0, 2) for _ in range(R.randint(1, 9))] for _ in range(24)]],
 "reverse_floats": [[[v], v[::-1]] for v in [[round(R.uniform(-3, 3), 4) for _ in range(R.randint(2, 9))] for _ in range(24)]]}
negok = 0
for k, rows in neg.items():
    open(f"m5/neg.{k}.jsonl", "w").write("".join(json.dumps(r) + "\n" for r in rows))
    out = json.loads(subprocess.run(["<workspace>/bin/math-kb", "explain", "--rows", f"m5/neg.{k}.jsonl"], capture_output=True, text=True).stdout)
    print("neg", k.ljust(16), "→", out["explained_by"]); negok += out["explained_by"] == ["none"]
right = sum(1 for c, h in res.items() if h == [c])
print(json.dumps({"explained_exactly": f"{right}/10", "negatives_none": f"{negok}/4"}))
open("m5/result.json", "w").write(json.dumps({"explained": res, "explained_exactly": right, "negatives_none": negok}) + "\n")

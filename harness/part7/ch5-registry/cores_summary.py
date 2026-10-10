#!/usr/bin/env python3
"""Summarise a registry SQL dump without its entry/gate command lines (which hold absolute private paths).

usage: cores_summary.py cores.db.sql OUT.json
Writes: counts by kind and status, one record per core (id, version label class, kind, status, op names),
and the gate text only for rows whose gate is a bare command with no path. Standard library only.
"""
import hashlib, json, re, sqlite3, sys

src, out = sys.argv[1], sys.argv[2]
raw = open(src, "rb").read()
db = sqlite3.connect(":memory:")
db.executescript(raw.decode())
cores = db.execute("select core, version, kind, status, gate from cores order by core").fetchall()
ops = {}
for c, o in db.execute("select core, op from ops order by core, op"):
    ops.setdefault(c, []).append(o)


def bare(g):
    g = re.sub(r"^/\S*?/(?=bin/)", "", g)           # drop an absolute prefix before bin/
    g = re.sub(r"^bin/", "", g)
    return g if "/" not in g and "home" not in g.lower() else None


rows = []
for c, v, k, s, g in cores:
    gate = None
    if c == "math.kb":
        gate = "math-kb check --n 200"
    elif c == "chew.sessions":
        gate = "pytest -q tests (timeout 120 s)"
    else:
        b = bare(g)
        gate = b if b and "probe" not in b else None
    rows.append({"core": c, "version_label": "bin:<12 hex>" if v.startswith("bin:") else ("<12 hex>" if re.fullmatch(r"[0-9a-f]{12}", v) else v),
                 "kind": k, "status": s, "ops": ops.get(c, []), "gate": gate})
S = {"source_sha256": hashlib.sha256(raw).hexdigest(), "cores": len(rows),
     "ops": sum(len(v) for v in ops.values()),
     "by_kind": {k: sum(1 for r in rows if r["kind"] == k) for k in sorted({r["kind"] for r in rows})},
     "by_status": {k: sum(1 for r in rows if r["status"] == k) for k in sorted({r["status"] for r in rows})},
     "generators": sum(1 for r in rows if r["core"].startswith("gen.")),
     "retired": [r["core"] for r in rows if r["status"] == "retired"],
     "rows": rows}
json.dump(S, open(out, "w"), indent=1); open(out, "a").write("\n")

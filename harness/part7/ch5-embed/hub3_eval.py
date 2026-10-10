"""hub-3 (pre-registered in <plan> before running): shardd vault search vs the cloud store, same 200 queries.
PASS: hybrid (FTS5 + nomic, RRF) recall@5 >= 0.745 (mistral_cloud from the EMBED-BN-1c run). Reports FTS-only, nomic-only."""
import json, random, re, sys, time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shardd

IX = Path("<workspace>/vault-indexer/index")
data = json.load(open(IX / "docstore.json"))["docstore/data"]
ids = json.load(open(IX / "nomic_local" / "ids.json"))
cand = []
for k, i in enumerate(ids):  # identical selection to eval_nomic_vs_mistral.py
    m = re.search(r"^#+\s+(.{8,120})$", data[i]["__data__"]["text"], re.M)
    if m: cand.append((k, m.group(1).strip()))
random.Random(0).shuffle(cand); cand = cand[:200]

srv = shardd.Server(); st = srv.st
assert srv.emb.c is not None, "omnid must be up for the query embedding"
hyb = fts = vec = 0; lat = []
for k, q in cand:
    target = ids[k]
    t0 = time.perf_counter()
    hits = srv.handle({"op": "shard_search", "q": q, "stores": ["vault"], "k": 5})["hits"]
    lat.append(time.perf_counter() - t0)
    hyb += target in [h["id"] for h in hits]
    fts += target in [p["id"] for _, p in st.fts_vault(q, 5)]
    vec += target in [p["id"] for _, p in st.vec_vault(srv.emb.query(q), 5)]
n = len(cand)
r = {"n": n, "hybrid_recall5": hyb / n, "fts_recall5": fts / n, "nomic_recall5": vec / n,
     "p50_ms": round(1000 * float(np.median(lat)), 1), "bar": 0.745, "PASS": hyb / n >= 0.745}
print(r)
json.dump(r, open(Path.home() / "gpurun-out-0930/hub3.result.json", "w"), indent=1)

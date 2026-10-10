#!/usr/bin/env python3
"""ramkit #12 — fleet knowledge on the pod (RAM-KIT-0, J 10-08). A snapshot of shardd's vault + notes stores that a pod searches locally
(stdlib sqlite FTS5 + numpy), behind corehostd as registry core `shard.search` (CORE-REGISTRY-CONTRACT v1 §1 row, kind cli).
Same retrieval as projects/omnid/shardd.py for stores vault + notes: vault_fts (bm25, top 50) + vault_vec (cosine, top 50) + notes_fts,
fused by reciprocal rank (k = 60). The pod has no nomic embedder: the caller sends the query vector (`qvec`, a .npy the laptop's omnid made);
without it the vector list is empty (FTS-only), exactly as shardd does when omnid is down. Sessions / talon / transcripts stay on the laptop
(private, large, live-refreshing).

  shard_search.py export <snap_dir>                       laptop: vault.db (chunks + FTS5, shardd's insert order) + vecs + ids + notes.db + MANIFEST.json
  shard_search.py search --manifest M --q TEXT [--qvec F.npy] [--k 10] [--stores vault,notes] --out OUT.json
  shard_search.py register [--db CORES_DB] [--entry PATH]   insert the `shard.search` core + op rows (idempotent; like corehostd/seed_pod.py)
  shard_search.py selftest
Snapshot ships to the pod with the kit (no network volume): <home>/ai-stack/data/shards/pod-snap/ (sizes in MANIFEST.json)."""
import argparse, datetime, hashlib, json, os, shutil, sqlite3, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

RRF_K = 60
VAULT = os.path.join(C.AI, "vault-indexer", "index")
NOTES = os.path.join(C.AI, "data", "shards", "notes.db")
DEFAULT_SNAP = os.path.join(C.AI, "data", "shards", "pod-snap")


def fts_query(q):                                                    # shardd._fts_query, verbatim rule
    terms = [t for t in "".join(c if c.isalnum() else " " for c in q).split() if len(t) > 1]
    return " OR ".join(f'"{t}"' for t in terms[:16]) or '""'


def rrf(lists, k):                                                   # shardd.rrf, same arithmetic + tie order
    score, payload, why = {}, {}, {}
    for name, hits in lists:
        for rank, (key, p) in enumerate(hits):
            score[key] = score.get(key, 0.0) + 1.0 / (RRF_K + rank + 1)
            payload.setdefault(key, {}).update(p); why.setdefault(key, {})[name] = rank + 1
    out = []
    for key in sorted(score, key=score.get, reverse=True)[:k]:
        p = payload[key]; p["key"] = key; p["score"] = round(score[key], 5); p["ranks"] = why[key]; out.append(p)
    return out


def export(snap, vault=VAULT, notes=NOTES):
    os.makedirs(snap, exist_ok=True); t = time.time()
    data = json.load(open(os.path.join(vault, "docstore.json")))["docstore/data"]
    db = os.path.join(snap, "vault.db.tmp")
    if os.path.exists(db): os.remove(db)
    c = sqlite3.connect(db)
    c.execute("create table chunks(cid text primary key, path text, text text)")
    c.execute("create virtual table vault_fts using fts5(text, path unindexed, cid unindexed)")
    rows = []
    for cid, d in data.items():                                      # dict order = shardd's insert order → same FTS rowids
        m = d["__data__"].get("metadata") or {}
        rows.append((d["__data__"]["text"], m.get("path", ""), cid))
    c.executemany("insert into vault_fts values (?,?,?)", rows)
    c.executemany("insert into chunks values (?,?,?)", [(cid, p, tx) for tx, p, cid in rows])
    c.commit(); c.close(); os.replace(db, os.path.join(snap, "vault.db")); del data, rows
    nl = os.path.join(vault, "nomic_local")
    if os.path.exists(os.path.join(nl, "vectors.f32.npy")):
        v = np.load(os.path.join(nl, "vectors.f32.npy")); v = v / np.linalg.norm(v, axis=1, keepdims=True)
        np.save(os.path.join(snap, "vecs.f32.npy"), v.astype(np.float32)); shutil.copy(os.path.join(nl, "ids.json"), os.path.join(snap, "ids.json"))
    if os.path.exists(notes):
        src = sqlite3.connect(f"file:{notes}?mode=ro", uri=True); dst = sqlite3.connect(os.path.join(snap, "notes.db"))
        src.backup(dst); src.close(); dst.close()
    files = {f: {"bytes": os.path.getsize(os.path.join(snap, f)), "sha256": C.sha_file(os.path.join(snap, f))}
             for f in sorted(os.listdir(snap)) if f != "MANIFEST.json" and not f.endswith(".tmp")}
    man = {"what": "shardd vault + notes snapshot for pod search (ramkit #12)", "made": datetime.datetime.now().isoformat(timespec="seconds"),
           "source": {"vault": vault, "notes": notes}, "files": files, "total_bytes": sum(f["bytes"] for f in files.values()),
           "export_s": round(time.time() - t, 1)}
    C.json_out(man, os.path.join(snap, "MANIFEST.json"))
    return man


class Snap:
    def __init__(self, manifest):
        self.d = os.path.dirname(os.path.abspath(manifest))
        self.v = sqlite3.connect(f"file:{os.path.join(self.d, 'vault.db')}?mode=ro", uri=True)
        self.meta = dict(self.v.execute("select cid, path from chunks"))
        self.text = None
        p = os.path.join(self.d, "vecs.f32.npy")
        self.vecs = np.load(p, mmap_mode="r") if os.path.exists(p) else None
        self.ids = json.load(open(os.path.join(self.d, "ids.json"))) if self.vecs is not None else []
        n = os.path.join(self.d, "notes.db")
        self.notes = sqlite3.connect(f"file:{n}?mode=ro", uri=True) if os.path.exists(n) else None

    def fts_vault(self, q, n):
        sql = "select cid, path, snippet(vault_fts, 0, '[', ']', '…', 24) from vault_fts where vault_fts match ? order by rank limit ?"
        return [(f"vault:{r[0]}", {"store": "vault", "id": r[0], "path": r[1], "text": r[2]}) for r in self.v.execute(sql, (fts_query(q), n))]

    def vec_vault(self, qv, n):
        if qv is None or self.vecs is None: return []
        s = self.vecs @ (qv / np.linalg.norm(qv)); top = np.argsort(-s)[:n]
        get = lambda cid: (self.v.execute("select text from chunks where cid=?", (cid,)).fetchone() or [""])[0]
        return [(f"vault:{self.ids[i]}", {"store": "vault", "id": self.ids[i], "path": self.meta.get(self.ids[i], ""),
                 "cos": round(float(s[i]), 4), "text": get(self.ids[i])[:300]}) for i in top]

    def fts_notes(self, q, n):
        if self.notes is None: return []
        sql = ("select n.id, n.source, n.tags, n.ts, snippet(notes_fts, 0, '[', ']', '…', 24) from notes_fts "
               "join notes n on n.id = notes_fts.rowid where notes_fts match ? order by rank limit ?")
        return [(f"notes:{r[0]}", {"store": "notes", "id": r[0], "source": r[1], "tags": r[2], "ts": r[3], "text": r[4]})
                for r in self.notes.execute(sql, (fts_query(q), n))]

    def search(self, q, qv=None, k=10, stores=("vault", "notes")):
        lists = []
        if "vault" in stores: lists += [("vault_fts", self.fts_vault(q, 50)), ("vault_vec", self.vec_vault(qv, 50))]
        if "notes" in stores: lists.append(("notes_fts", self.fts_notes(q, 50)))
        return rrf(lists, k)


def register(db=None, entry=None):
    db = db or os.environ.get("CORES_DB", os.path.join(C.AI, "control-center", "cores.db"))
    entry = entry or os.path.abspath(__file__)
    ver = hashlib.sha256(open(entry, "rb").read()).hexdigest()[:12]
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    con = sqlite3.connect(db)
    con.executescript("""CREATE TABLE IF NOT EXISTS cores(core TEXT PRIMARY KEY, version TEXT NOT NULL, owner TEXT NOT NULL,
      kind TEXT NOT NULL CHECK(kind IN ('cli','socket','http','mcp')), entry TEXT NOT NULL, gate TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'live' CHECK(status IN ('live','dormant','retired')), added_ts TEXT NOT NULL, last_fired_ts TEXT);
      CREATE TABLE IF NOT EXISTS ops(core TEXT NOT NULL REFERENCES cores(core), op TEXT NOT NULL, args_schema TEXT NOT NULL,
      returns TEXT NOT NULL, deterministic INTEGER NOT NULL DEFAULT 1, PRIMARY KEY(core, op));""")
    con.execute("INSERT OR REPLACE INTO cores(core,version,owner,kind,entry,gate,status,added_ts) VALUES(?,?,?,?,?,?,?,?)",
                ("shard.search", ver, "claude-seat", "cli", json.dumps([entry]), f"python3 {entry} selftest --gate-only", "live", now))
    con.execute("INSERT OR REPLACE INTO ops VALUES(?,?,?,?,?)", ("shard.search", "search", json.dumps([
        {"name": "manifest", "type": "path", "required": True}, {"name": "q", "type": "str", "required": True},
        {"name": "qvec", "type": "path", "required": False}, {"name": "k", "type": "str", "required": False},
        {"name": "stores", "type": "str", "required": False}, {"name": "out", "type": "path", "required": True}]),
        json.dumps({"arg": "out", "format": "json", "what": "top-k hits (store, id, path, score, ranks) — shardd fusion over the snapshot"}), 1))
    con.commit(); con.close()
    return {"core": "shard.search", "version": ver, "db": db}


def selftest(out=None, gate_only=False):
    """laptop: export a snapshot, then for 5 queries the snapshot's top-10 == shardd.Stores' top-10 over the same stores (FTS + vector);
    then register the core in a scratch registry and fire it through bin/core-registry (the path corehostd takes). --gate-only (pod):
    a present snapshot answers one FTS query."""
    import tempfile, subprocess
    if gate_only:
        m = os.path.join(DEFAULT_SNAP, "MANIFEST.json")
        if not os.path.exists(m): return False, {"error": f"no snapshot at {m}"}
        h = Snap(m).search("fleet plan", None, 5); return len(h) > 0, {"hits": len(h)}
    d = tempfile.mkdtemp(prefix="ramkit-shard-"); snap = os.path.join(d, "snap")
    if not os.path.exists(os.path.join(VAULT, "docstore.json")): return False, {"error": "no vault index on this machine (laptop-only test)"}
    shutil.copy(NOTES, os.path.join(d, "notes-ref.db")) if os.path.exists(NOTES) else None
    man = export(snap)
    sys.path.insert(0, os.path.join(C.AI, "projects", "omnid")); import shardd
    shardd.SESS_DB = shardd.Path("/nonexistent/s.db"); shardd.TALON_DB = shardd.Path("/nonexistent/t.db")
    shardd.TRANSCRIPTS_DB = shardd.Path("/nonexistent/tr.db"); shardd.NOTES_DB = shardd.Path(os.path.join(d, "notes-ref.db"))
    ST = shardd.Stores(); S = Snap(os.path.join(snap, "MANIFEST.json"))
    try: emb = shardd.Embedder(); emb_ok = emb.c is not None
    except Exception: emb, emb_ok = None, False
    Q = ["ternary transformer training", "eBay listing shipping", "residue number system rings", "morning routine sleep", "doctor core renderer"]
    same, detail = 0, []
    for i, q in enumerate(Q):
        qv = emb.query(q) if emb_ok else None
        if qv is None: qv = np.asarray(S.vecs[(i * 997) % len(S.ids)], np.float32) if S.vecs is not None else None
        ref = shardd.rrf([("vault_fts", ST.fts_vault(q, 50)), ("vault_vec", ST.vec_vault(qv, 50)), ("notes_fts", ST.fts_notes(q, 50))], 10)
        got = S.search(q, qv, 10)
        rk = [f"{h['store']}:{h['id']}" for h in ref]; gk = [h["key"] for h in got]
        same += rk == gk; detail.append({"q": q, "match": rk == gk, "n": len(gk), "top1": gk[:1]})
        if i == 0: np.save(os.path.join(d, "q0.npy"), np.asarray(qv, np.float32)); top0 = gk
    # registry path: scratch cores.db + receipts, fire through bin/core-registry exactly as corehostd does
    env = dict(os.environ, CORES_DB=os.path.join(d, "cores.db"), CORE_RECEIPTS=os.path.join(d, "receipts.jsonl"))
    reg = os.path.join(C.AI, "bin", "core-registry")
    os.environ["CORES_DB"] = env["CORES_DB"]; register(env["CORES_DB"]); del os.environ["CORES_DB"]
    r = subprocess.run([sys.executable, reg, "fire", "shard.search", "search", "--arg", f"manifest={snap}/MANIFEST.json",
                        "--arg", f"q={Q[0]}", "--arg", f"qvec={d}/q0.npy", "--arg", "k=10", "--arg", f"out={d}/fire.json", "--caller", "ramkit-selftest"],
                       capture_output=True, text=True, env=env, timeout=300)
    fired = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {"verdict": "no output", "err": r.stderr[-300:]}
    fire_same = os.path.exists(f"{d}/fire.json") and [h["key"] for h in json.load(open(f"{d}/fire.json"))["hits"]] == top0
    res = {"queries": len(Q), "same_top10": same, "embedder": "omnid nomic" if emb_ok else "stored vault vectors as query vectors (omnid down)",
           "detail": detail, "snapshot_bytes": man["total_bytes"], "snapshot_files": {k: v["bytes"] for k, v in man["files"].items()},
           "export_s": man["export_s"], "registry_fire": {"verdict": fired.get("verdict"), "ms": fired.get("ms"), "same_as_direct": fire_same},
           "rss_mb": C.rss_mb()}
    shutil.rmtree(d, ignore_errors=True)
    if out: C.json_out(res, out)
    return same == len(Q) and fired.get("verdict") == "pass" and fire_same, res


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="c", required=True)
    e = sp.add_parser("export"); e.add_argument("snap", nargs="?", default=DEFAULT_SNAP)
    s = sp.add_parser("search"); s.add_argument("--manifest", required=True); s.add_argument("--q", required=True); s.add_argument("--qvec")
    s.add_argument("--k", default="10"); s.add_argument("--stores", default="vault,notes"); s.add_argument("--out", required=True)
    r = sp.add_parser("register"); r.add_argument("--db"); r.add_argument("--entry")
    t = sp.add_parser("selftest"); t.add_argument("--out"); t.add_argument("--gate-only", action="store_true")
    a = ap.parse_args()
    if a.c == "export": man = export(a.snap); print(json.dumps({"snap": a.snap, "total_bytes": man["total_bytes"], "export_s": man["export_s"]}))
    elif a.c == "search":
        qv = np.load(a.qvec).astype(np.float32) if a.qvec else None
        hits = Snap(a.manifest).search(a.q, qv, int(a.k), tuple(a.stores.split(",")))
        C.json_out({"q": a.q, "k": int(a.k), "hits": hits}, a.out); print(json.dumps({"hits": len(hits)}))
    elif a.c == "register": print(json.dumps(register(a.db, a.entry)))
    else:
        ok, res = selftest(a.out, a.gate_only); print(json.dumps(res)); print("PASS" if ok else "FAIL", "shard_search"); sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

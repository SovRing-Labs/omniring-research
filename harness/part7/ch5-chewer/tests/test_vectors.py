"""C3 on a SYNTHETIC store: pod vector files load by rowid (idempotent, count-checked), hybrid RRF ranks a chunk found by both lists first."""
import json, pytest
from tchew import store, vectors

def mk(tmp_path):
    db = store.connect(str(tmp_path / "t.db"))
    for i, t in enumerate(["the merge gate passed", "pod embedding batch", "unrelated lunch note"], 1):
        db.execute("INSERT INTO chunks(rowid,id,project_id,session_date,seq,start_ms,end_ms,speakers,participants,topics,text) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                   (i, f"c{i}", "p", "2026-10-08", i, 0, 0, "user", "", "", t))
    db.commit(); return db

def vec(i): v = [0.0] * 768; v[i] = 1.0; return v

def test_load_and_hybrid(tmp_path):
    db, V = mk(tmp_path), tmp_path / "v"; V.mkdir()
    json.dump([[1, 2]], open(V / "rowids.json", "w")); json.dump([vec(0), vec(1)], open(V / "shard000.emb", "w"))
    json.dump([[3]], open(V / "rowids2.json", "w")); json.dump([vec(2)], open(V / "b2shard000.emb", "w"))
    assert vectors.load(db, str(V)) == 3 and vectors.load(db, str(V)) == 0
    top = store.hybrid(db, "merge gate", vec(0), k=3)
    assert top[0][-1] == "the merge gate passed" and top[0][0] > top[1][0]

def test_count_mismatch_refused(tmp_path):
    db, V = mk(tmp_path), tmp_path / "v"; V.mkdir()
    json.dump([[1, 2]], open(V / "rowids.json", "w")); json.dump([vec(0)], open(V / "shard000.emb", "w"))
    with pytest.raises(ValueError): vectors.load(db, str(V))

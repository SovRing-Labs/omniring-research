import pytest, struct
from pathlib import Path
from pydantic import ValidationError
from tchew.ingest import ingest, IngestError
from tchew.chunk import chunk
from tchew.models import Meta
from tchew import store

FX = Path(__file__).parent / "fixtures"
META = Meta(project_id="proj-1", session_date="2026-10-07", participant_ids=("alice", "bob"), topic_tags=("budget",))

def test_vtt_parse():
    cues = ingest(FX / "a.vtt")
    assert [(c.start_ms, c.speaker) for c in cues] == [(1000, "Alice"), (3500, "Alice"), (6200, "Bob")]

def test_srt_parse():
    assert ingest(FX / "a.srt")[0].end_ms == 3500

def test_chunk_by_turn():
    ch = chunk(ingest(FX / "a.vtt"), META)
    assert [c.text for c in ch] == ["Alice: Welcome to the review. First item is the budget.", "Bob: Budget looks fine to me."]

def test_deterministic():
    a = [c.model_dump_json() for c in chunk(ingest(FX / "a.vtt"), META)]
    b = [c.model_dump_json() for c in chunk(ingest(FX / "a.vtt"), META)]
    assert a == b

def test_missing_meta_refused():
    with pytest.raises(ValidationError):
        Meta(project_id="p", session_date="2026-10-07")
    with pytest.raises(ValidationError):
        Meta(project_id="p", session_date="2026-10-07", participant_ids=())

def test_bad_input_refused(tmp_path):
    f = tmp_path / "x.vtt"; f.write_text("WEBVTT\n\n00:00:05.000 --> 00:00:01.000\nhi\n")
    with pytest.raises(IngestError):
        ingest(f)
    g = tmp_path / "y.vtt"; g.write_text("WEBVTT\n")
    with pytest.raises(IngestError):
        ingest(g)

def test_store_roundtrip_and_idempotent(tmp_path):
    db = store.connect(str(tmp_path / "t.db"))
    ch = chunk(ingest(FX / "a.vtt"), META)
    vecs = [[1.0 if j == i else 0.0 for j in range(768)] for i in range(len(ch))]
    assert store.put(db, ch, vecs) == 2
    assert store.put(db, ch, vecs) == 0
    hit = store.search(db, vecs[1], k=1)
    assert hit[0][5] == ch[1].text and hit[0][0] < 1e-6
    assert [r[2] for r in store.listing(db, "proj-1")] == [0, 1]

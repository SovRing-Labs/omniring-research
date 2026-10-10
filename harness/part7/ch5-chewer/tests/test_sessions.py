"""chewer core C1/C2 tests on a SYNTHETIC sessions db (never real transcripts)."""
import sqlite3
import pytest
from tchew import sessions as S, store

def make_db(path, extra=False):
    c = sqlite3.connect(path)
    c.executescript("""CREATE TABLE sessions(session_id TEXT PRIMARY KEY, project_dir TEXT NOT NULL, cwd TEXT, git_branch TEXT, title TEXT, first_seen TEXT,
        last_seen TEXT, message_count INTEGER DEFAULT 0, input_tokens INTEGER DEFAULT 0, output_tokens INTEGER DEFAULT 0);
        CREATE TABLE messages(id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, line_no INTEGER, uuid TEXT, parent_uuid TEXT, role TEXT, block_type TEXT,
        tool_name TEXT, content TEXT, timestamp TEXT);""")
    c.execute("INSERT INTO sessions(session_id, project_dir, first_seen) VALUES ('s1', '-home-x-proj', '2026-10-08T01:00:00Z')")
    rows = [(1, "user", "text", None, "fix the parser please"), (2, "assistant", "thinking", None, "secret plan"), (3, "assistant", "text", None, "on it"),
            (4, "assistant", "tool_use", "Bash", "grep foo key=sk-ant-api03-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"), (5, "user", "tool_result", None, "found foo in a.rs"),
            (6, "user", "text", None, "now run the tests"), (7, "assistant", "text", None, "tests pass")]
    if extra: rows += [(8, "user", "text", None, "commit it"), (9, "assistant", "text", None, "done")]
    for ln, role, bt, tool, content in rows:
        c.execute("INSERT INTO messages(session_id, line_no, role, block_type, tool_name, content, timestamp) VALUES ('s1',?,?,?,?,?,'2026-10-08T01:00:00Z')", (ln, role, bt, tool, content))
    c.commit(); return c

def test_steps_close_only_on_next_prompt(tmp_path):
    c = make_db(tmp_path / "s.db"); ch, last = S.chunk_session(c, "s1", "-home-x-proj", "2026-10-08T01:00:00Z")
    assert len(ch) == 1 and last == 5                       # step 2 ("now run the tests") is still open → not stored
    t = ch[0].text
    assert t.startswith("USER: fix the parser please") and "secret plan" not in t   # thinking left out
    assert "TOOL Bash:" in t and "RESULT: found foo" in t
    assert "sk-ant-api03" not in t                          # scrubbed before storing

def test_deterministic_and_incremental(tmp_path):
    c = make_db(tmp_path / "s.db")
    a, _ = S.chunk_session(c, "s1", "-home-x-proj", "2026-10-08T01:00:00Z")
    b, _ = S.chunk_session(c, "s1", "-home-x-proj", "2026-10-08T01:00:00Z")
    assert [x.id for x in a] == [x.id for x in b]
    db = store.connect(str(tmp_path / "t.db")); assert store.put(db, a) == 1 and store.put(db, a) == 0
    c2 = make_db(tmp_path / "s2.db", extra=True)            # the session grew: step 2 closes, step 3 stays open
    more, last = S.chunk_session(c2, "s1", "-home-x-proj", "2026-10-08T01:00:00Z", after_line=5, seq0=1)
    assert len(more) == 1 and more[0].text.startswith("USER: now run the tests") and last == 7

def test_refuses_without_date(tmp_path):
    c = make_db(tmp_path / "s.db")
    with pytest.raises(ValueError):
        S.chunk_session(c, "s1", "-home-x-proj", "")

def test_fts_finds_step(tmp_path):
    c = make_db(tmp_path / "s.db"); ch, _ = S.chunk_session(c, "s1", "-home-x-proj", "2026-10-08T01:00:00Z")
    db = store.connect(str(tmp_path / "t.db")); store.put(db, ch)
    assert store.fts(db, "parser")[0][5].startswith("USER: fix the parser")

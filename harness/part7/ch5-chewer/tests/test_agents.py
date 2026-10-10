"""opencode + Talon readers on SYNTHETIC dbs (never real sessions): step chunks, reasoning out, scrub, closed vs open sessions."""
import json, sqlite3
from tchew import agents as A

def oc_db(p):
    c = sqlite3.connect(p); c.executescript("""CREATE TABLE message(id TEXT PRIMARY KEY, session_id TEXT, time_created INTEGER, time_updated INTEGER, data TEXT);
        CREATE TABLE part(id TEXT PRIMARY KEY, message_id TEXT, session_id TEXT, time_created INTEGER, time_updated INTEGER, data TEXT);""")
    def m(i, role, t): c.execute("INSERT INTO message VALUES (?,?,?,?,?)", (i, "s1", t, t, json.dumps({"role": role})))
    def p(i, mid, t, d): c.execute("INSERT INTO part VALUES (?,?,?,?,?,?)", (i, mid, "s1", t, t, json.dumps(d)))
    m("m1", "user", 1); p("p1", "m1", 1, {"type": "text", "text": "build the gate"})
    m("m2", "assistant", 2); p("p2", "m2", 2, {"type": "reasoning", "text": "hidden plan"}); p("p3", "m2", 3, {"type": "text", "text": "on it"})
    p("p4", "m2", 4, {"type": "tool", "tool": "bash", "state": {"input": {"command": "export KEY=sk-ant-api03-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"}, "output": "ok"}})
    c.commit(); return c

def test_opencode_closed_session_stores_its_only_step(tmp_path):
    ev = A.opencode_events(oc_db(tmp_path / "o.db"), "s1")
    open_, _ = A.chunk_events(ev, "s1", "<home>/proj", 1_760_000_000_000, closed=False)
    done, _ = A.chunk_events(ev, "s1", "<home>/proj", 1_760_000_000_000, closed=True)
    assert open_ == [] and len(done) == 1
    t = done[0].text
    assert t.startswith("USER: build the gate") and "hidden plan" not in t and "TOOL: bash" in t and "RESULT: ok" in t and "sk-ant-api03" not in t

def test_talon_events(tmp_path):
    c = sqlite3.connect(tmp_path / "t.db")
    c.execute("CREATE TABLE messages(session_id TEXT, seq INTEGER, role TEXT, content TEXT, tool_calls TEXT, name TEXT)")
    rows = [(1, "system", "sys", None, None), (2, "user", "fix it", None, None), (3, "assistant", "looking", json.dumps([{"function": {"name": "grep", "arguments": "{\"q\":\"x\"}"}}]), None),
            (4, "tool", "found x", None, "grep"), (5, "user", "thanks", None, None)]
    for seq, role, content, calls, name in rows: c.execute("INSERT INTO messages VALUES ('t1',?,?,?,?,?)", (seq, role, content, calls, name))
    ch, last = A.chunk_events(A.talon_events(c, "t1"), "t1", "<home>/proj", 1_760_000_000.0, closed=False)
    assert len(ch) == 1 and last == 4 and "sys" not in ch[0].text and "TOOL: grep" in ch[0].text and "RESULT: grep found x" in ch[0].text

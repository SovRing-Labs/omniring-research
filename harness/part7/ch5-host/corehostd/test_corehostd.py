# corehostd tests (pod hosting P1–P4): real server process, real registry CLI, a fake core that logs its start/end and nice value.
import base64, json, os, socket, sqlite3, subprocess, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(D, "..", "..", ".."))
REGISTRY = os.path.join(REPO, "bin", "core-registry")
FAKE = """#!/bin/bash
# fake core: <op> <secs>
s=$(date +%s.%N); sleep "$2"; e=$(date +%s.%N)
echo "$s $e $(awk '{print $19}' /proc/$$/stat)" >> "$FAKE_LOG"; echo "slept $2"
"""

def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p

@pytest.fixture(scope="module")
def srv(tmp_path_factory):
    t = tmp_path_factory.mktemp("ch")
    fake = t / "fake.sh"; fake.write_text(FAKE); fake.chmod(0o755)
    db, rec, log = t / "cores.db", t / "receipts.jsonl", t / "fake.log"
    env = dict(os.environ, CORES_DB=str(db), CORE_RECEIPTS=str(rec))
    subprocess.run([REGISTRY, "init"], env=env, check=True, capture_output=True)
    con = sqlite3.connect(db)
    con.execute("INSERT INTO cores VALUES('test.sleep','t1','test','cli',?,'true','live','2026-10-08T00:00:00Z',NULL)", (json.dumps([str(fake)]),))
    con.execute("INSERT INTO ops VALUES('test.sleep','run',?,?,1)",
                (json.dumps([{"name": "secs", "type": "str", "required": True, "positional": True}]), json.dumps({"what": "stdout"})))
    con.commit(); con.close()
    port = free_port()
    env.update(CH_PORT=str(port), CH_HOST="testpod", CH_SLOTS="8", CH_SLOTS_TRAINING="2", CORE_REGISTRY_BIN=REGISTRY,
               CH_TRAIN_RE="fake-train-zq7", FAKE_LOG=str(log))
    p = subprocess.Popen([sys.executable, os.path.join(D, "corehostd.py")], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for _ in range(50):
        try: urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1); break
        except Exception: time.sleep(0.1)
    yield dict(port=port, log=log, rec=rec)
    p.terminate(); p.wait(5)

def call(port, method, path, body=None, headers=None):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", method=method,
                                 data=json.dumps(body).encode() if body is not None else None, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=120) as r: return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e: return e.code, json.loads(e.read())

def overlap(lines):
    ev = []
    for l in lines:
        s, e, _ = l.split(); ev += [(float(s), 1), (float(e), -1)]
    cur = peak = 0
    for _, d in sorted(ev, key=lambda x: (x[0], x[1])): cur += d; peak = max(peak, cur)
    return peak

def test_p1_health_cores_fire_receipt(srv):
    st, h = call(srv["port"], "GET", "/health"); assert st == 200 and h["host"] == "testpod" and h["nice"] == 19
    st, c = call(srv["port"], "GET", "/cores"); assert st == 200 and any(x["core"] == "test.sleep" for x in c["cores"])
    st, r = call(srv["port"], "POST", "/cores/test.sleep/run", {"args": {"secs": "0.01"}, "caller": "pytest"})
    assert st == 200 and r["ok"], r
    rec = r["receipt"]
    for k in ("v", "ts", "core", "version", "op", "caller", "input_hash", "output_ref", "output_hash", "gate", "verdict", "ms", "tw"): assert k in rec
    assert rec["caller"] == "pytest@pod:testpod" and rec["verdict"] == "pass" and rec["input_hash"].startswith("sha256:")
    st, rs = call(srv["port"], "GET", "/cores/receipts?last=5"); assert rs["receipts"][-1]["input_hash"] == rec["input_hash"]

def test_p1_refusals(srv):
    assert call(srv["port"], "POST", "/cores/nope/run", {"args": {}})[0] == 404
    assert call(srv["port"], "POST", "/cores/test.sleep/nope", {"args": {}})[0] == 404
    assert call(srv["port"], "POST", "/cores/test.sleep/run", {"args": {"bogus": 1}})[0] == 400
    assert call(srv["port"], "POST", "/cores/test.sleep/run", {"args": {"secs": "0"}}, {"Origin": "https://evil.example"})[0] == 403

def test_p2_belt_64_ops_8_at_a_time_and_cache(srv):
    srv["log"].write_text(""); t0 = time.monotonic()
    with ThreadPoolExecutor(64) as ex:
        res = list(ex.map(lambda i: call(srv["port"], "POST", "/cores/test.sleep/run", {"args": {"secs": f"1.0{i:03d}"}}), range(64)))
    wall = time.monotonic() - t0
    assert all(st == 200 and r["ok"] for st, r in res)
    lines = srv["log"].read_text().split("\n")[:-1]
    st, h = call(srv["port"], "GET", "/health")
    # slots = 8: the server's own peak is 8, the cores' sleeps never overlap more than 8, and 64 x 1 s ran in waves (>= 8 s, far under the 64 s of a serial run; laptop load varies)
    assert len(lines) == 64 and h["peak"] == 8 and 6 <= overlap(lines) <= 8 and 8.0 <= wall < 40.0, (h["peak"], overlap(lines), wall)
    assert all(l.split()[2] == "19" for l in lines)                          # W3: every op ran at nice 19
    st, r = call(srv["port"], "POST", "/cores/test.sleep/run", {"args": {"secs": "1.0005"}})
    assert r["receipt"].get("cached") is True and r["receipt"]["ms"] == 0
    assert len(srv["log"].read_text().split("\n")[:-1]) == 64              # the cached op did not run

def test_p3_ws_stream(srv):
    s = socket.create_connection(("127.0.0.1", srv["port"]), timeout=10)
    key = base64.b64encode(os.urandom(16)).decode()
    s.sendall((f"GET /cores/stream HTTP/1.1\r\nHost: x\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
               f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
    hs = b""
    while b"\r\n\r\n" not in hs: hs += s.recv(1024)
    assert b"101" in hs.split(b"\r\n")[0]
    st, r = call(srv["port"], "POST", "/cores/test.sleep/run", {"args": {"secs": "0.02"}, "caller": "ws"})
    buf = b""; msg = None; t0 = time.monotonic()
    while msg is None and time.monotonic() - t0 < 10:              # skip lines of earlier receipts; take the one for this fire
        buf += s.recv(65536)
        while len(buf) >= 2:
            n = buf[1] & 0x7F; off = 2
            if n == 126: n = int.from_bytes(buf[2:4], "big"); off = 4
            if len(buf) < off + n: break
            m = json.loads(buf[off:off + n]); buf = buf[off + n:]
            if m.get("input_hash") == r["receipt"]["input_hash"]: msg = m; break
    s.close()
    assert msg["caller"] == "ws@pod:testpod" and msg["input_hash"] == r["receipt"]["input_hash"]

def test_p4_budget_shrinks_with_training(srv):
    tr = subprocess.Popen(["bash", "-c", "exec -a fake-train-zq7 sleep 60"])
    try:
        time.sleep(0.3)
        st, h = call(srv["port"], "GET", "/health"); assert h["training"] is True and h["slots"] == 2
        srv["log"].write_text("")
        with ThreadPoolExecutor(16) as ex:
            list(ex.map(lambda i: call(srv["port"], "POST", "/cores/test.sleep/run", {"args": {"secs": f"0.2{i:03d}"}}), range(16)))
        assert overlap(srv["log"].read_text().split("\n")[:-1]) == 2
    finally:
        tr.kill(); tr.wait()
    st, h = call(srv["port"], "GET", "/health"); assert h["training"] is False and h["slots"] == 8

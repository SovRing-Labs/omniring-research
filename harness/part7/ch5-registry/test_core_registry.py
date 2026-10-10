"""core-registry (FLEET-LOOP-REG R5): schema, seeds, fire, receipt hash stability, refusals. Contract v1:
<notes>/worker/claude/CORE-REGISTRY-CONTRACT.md. Hermetic: tmp CORES_DB / CORE_RECEIPTS and a fake cli core (no doctor binary needed),
except test_seed_gate_tw which fires the real tw gate (`bin/tw --version`)."""
import json, os, sqlite3, subprocess, sys
from pathlib import Path
import pytest

CLI = Path(__file__).resolve().parents[2] / "bin" / "core-registry"
FAKE = """#!/usr/bin/env python3
import sys, hashlib
a = sys.argv[1:]
if "--boom" in a: sys.exit(3)
src = a[a.index("--src") + 1]; out = a[a.index("--out") + 1]
open(out, "w").write(hashlib.sha256(open(src, "rb").read()).hexdigest() + "\\n")
print("fake ok")
"""


@pytest.fixture
def env(tmp_path):
    e = dict(os.environ, CORES_DB=str(tmp_path / "cores.db"), CORE_RECEIPTS=str(tmp_path / "r.jsonl"), CORE_CALLER="pytest")
    run(e, "init")
    fake = tmp_path / "fake-core"; fake.write_text(FAKE); fake.chmod(0o755)
    c = sqlite3.connect(e["CORES_DB"])
    c.execute("INSERT INTO cores(core,version,owner,kind,entry,gate,added_ts) VALUES('test.fake','t1','pytest','cli',?,?, 'now')",
              (json.dumps([str(fake), "hash"]), "true"))
    c.execute("INSERT INTO ops VALUES('test.fake','hash',?,?,1)",
              (json.dumps([{"name": "src", "type": "path", "required": True}, {"name": "out", "type": "path", "required": True},
                           {"name": "boom", "type": "str", "flag": True}, {"name": "n", "type": "int"}]),
               json.dumps({"arg": "out", "format": "txt"})))
    c.commit(); c.close()
    e["TMP"] = str(tmp_path)
    return e


def run(e, *args, ok=True):
    r = subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True, env=e, timeout=120)
    if ok is True: assert r.returncode == 0, r.stderr
    return r


def receipts(e):
    p = Path(e["CORE_RECEIPTS"])
    return [json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []


def test_schema_and_seeds(env):
    c = sqlite3.connect(env["CORES_DB"])
    assert c.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    cols = [r[1] for r in c.execute("PRAGMA table_info(cores)")]
    assert cols == ["core", "version", "owner", "kind", "entry", "gate", "status", "added_ts", "last_fired_ts"]
    assert [r[1] for r in c.execute("PRAGMA table_info(ops)")] == ["core", "op", "args_schema", "returns", "deterministic"]
    rows = json.loads(run(env, "list", "--json").stdout)
    assert {"doctor.spec", "doctor.wall", "doctor.need", "doctor.blackbox", "tw"} <= {r["core"] for r in rows}
    tw = next(r for r in rows if r["core"] == "tw")
    assert {o["op"] for o in tw["ops"]} == {"start", "wait", "kill", "status"}
    with pytest.raises(sqlite3.IntegrityError):  # contract CHECK constraints hold
        c.execute("INSERT INTO cores(core,version,owner,kind,entry,gate,added_ts) VALUES('x','v','o','ftp','[]','true','t')")


def test_init_idempotent(env):
    assert "0 new" in run(env, "init").stdout
    assert len(json.loads(run(env, "list", "--json").stdout)) == 6  # 5 seeds + test.fake


def test_fire_writes_one_receipt(env):
    src = Path(env["TMP"]) / "in.txt"; src.write_text("hello\n"); out = Path(env["TMP"]) / "out.txt"
    r = run(env, "fire", "test.fake", "hash", "--arg", f"src={src}", "--arg", f"out={out}")
    rec = json.loads(r.stdout)
    assert rec["verdict"] == "pass" and rec["v"] == 1 and rec["caller"] == "pytest" and rec["version"] == "t1"
    assert rec["output_ref"] == str(out) and rec["output_hash"].startswith("sha256:")
    assert set(rec) >= {"v", "ts", "core", "version", "op", "caller", "input_hash", "output_ref", "output_hash", "gate", "verdict", "ms", "tw"}
    assert receipts(env) == [rec]
    assert json.loads(run(env, "show", "test.fake").stdout)["last_fired_ts"] == rec["ts"]


def test_input_hash_stable_and_content_bound(env):
    src = Path(env["TMP"]) / "in.txt"; src.write_text("a\n")
    o1, o2 = Path(env["TMP"]) / "o1", Path(env["TMP"]) / "o2"
    h = lambda *extra: json.loads(run(env, "fire", "test.fake", "hash", "--dry", *extra).stdout)["input_hash"]
    base = h("--arg", f"src={src}", "--arg", f"out={o1}")
    assert base == h("--arg", f"out={o1}", "--arg", f"src={src}")          # arg order does not matter (sorted keys)
    run(env, "fire", "test.fake", "hash", "--arg", f"src={src}", "--arg", f"out={o1}")
    assert base == h("--arg", f"src={src}", "--arg", f"out={o1}")          # an existing output file is not input
    src.write_text("b\n")
    assert base != h("--arg", f"src={src}", "--arg", f"out={o1}")          # input content is bound
    a1 = json.loads(run(env, "fire", "test.fake", "hash", "--arg", f"src={src}", "--arg", f"out={o1}").stdout)
    a2 = json.loads(run(env, "fire", "test.fake", "hash", "--arg", f"src={src}", "--arg", f"out={o2}").stdout)
    assert a1["output_hash"] == a2["output_hash"]                          # deterministic core → same output hash


def test_dry_writes_nothing(env):
    r = json.loads(run(env, "fire", "test.fake", "hash", "--dry", "--arg", "src=/x", "--arg", "out=/y").stdout)
    assert r["verdict"] == "dry" and r["argv"][-4:] == ["--src", "/x", "--out", "/y"]
    assert receipts(env) == []


@pytest.mark.parametrize("args,msg", [
    (["fire", "no.such", "op"], "unknown core"),
    (["fire", "test.fake", "nope"], "has no op"),
    (["fire", "test.fake", "hash", "--arg", "src=/x"], "missing required"),
    (["fire", "test.fake", "hash", "--arg", "src=/x", "--arg", "out=/y", "--arg", "bogus=1"], "unknown arg"),
    (["fire", "test.fake", "hash", "--arg", "src=/x", "--arg", "out=/y", "--arg", "n=abc"], "not an int"),
    (["fire", "test.fake", "hash", "--arg", "src"], "bad --arg"),
    (["gate", "no.such"], "unknown core"),
])
def test_refusals(env, args, msg):
    r = run(env, *args, ok=False)
    assert r.returncode == 2 and msg in r.stderr
    assert receipts(env) == []


def test_fail_and_error_verdicts(env):
    src = Path(env["TMP"]) / "in.txt"; src.write_text("x")
    r = run(env, "fire", "test.fake", "hash", "--arg", f"src={src}", "--arg", f"out={env['TMP']}/o", "--arg", "boom=true", ok=False)
    assert r.returncode == 1 and json.loads(r.stdout)["verdict"] == "fail"
    c = sqlite3.connect(env["CORES_DB"]); c.execute("UPDATE cores SET entry='[\"/no/such/binary\"]' WHERE core='test.fake'"); c.commit()
    r = run(env, "fire", "test.fake", "hash", "--arg", f"src={src}", "--arg", f"out={env['TMP']}/o", ok=False)
    assert json.loads(r.stdout)["verdict"] == "error"                      # error = the core did not run
    assert [x["verdict"] for x in receipts(env)] == ["fail", "error"]


def test_gate_receipt_and_receipts_filter(env):
    rec = json.loads(run(env, "gate", "test.fake").stdout)
    assert rec["op"] == "gate" and rec["verdict"] == "pass"
    c = sqlite3.connect(env["CORES_DB"]); c.execute("UPDATE cores SET gate='echo nope; exit 4' WHERE core='test.fake'"); c.commit()
    bad = run(env, "gate", "test.fake", ok=False)
    assert bad.returncode == 1 and json.loads(bad.stdout)["gate"] == "nope"
    assert len(json.loads(run(env, "receipts", "--json", "--core", "test.fake").stdout)) == 2
    assert len(json.loads(run(env, "receipts", "--json", "--last", "1").stdout)) == 1


def test_seed_gate_tw(env):
    rec = json.loads(run(env, "gate", "tw").stdout)
    assert rec["verdict"] == "pass" and rec["gate"].startswith("tw ")


def test_tw_field_explicit_only(env):
    """`tw` names the tw run that wraps THIS fire: only an explicit CORE_TW sets it; an inherited TW_ID (caller under tw) does not."""
    e = dict(env, TW_ID="caller-job"); e.pop("CORE_TW", None)
    assert json.loads(run(e, "gate", "test.fake").stdout)["tw"] is None
    assert json.loads(run(dict(e, CORE_TW="gates-run"), "gate", "test.fake").stdout)["tw"] == "gates-run"


def test_tw_argv_shape(env):
    r = json.loads(run(env, "fire", "tw", "start", "--dry", "--arg", "id=j1", "--arg", 'cmd=["sleep","1"]').stdout)
    assert r["argv"][1:] == ["start", "--id", "j1", "--", "sleep", "1"]


def test_require_rows_post_condition(env, tmp_path):
    """returns.require (pod hosting 10-08): exit 0 with empty `built` rows is a fail, not a pass; unset when_any flags skip the check."""
    core = tmp_path / "need-core"
    core.write_text("#!/usr/bin/env python3\nimport sys, json\na = sys.argv[1:]; out = a[a.index('--out') + 1]\n"
                    "good = '--good' in a\nopen(out, 'w').write(''.join(json.dumps({'built': {'verified': True} if good else None}) + '\\n' for _ in range(3)))\n")
    core.chmod(0o755)
    c = sqlite3.connect(env["CORES_DB"])
    c.execute("INSERT INTO cores(core,version,owner,kind,entry,gate,added_ts) VALUES('test.need','t1','pytest','cli',?,'true','now')",
              (json.dumps([str(core), "need"]),))
    c.execute("INSERT INTO ops VALUES('test.need','need',?,?,1)",
              (json.dumps([{"name": "out", "type": "path", "required": True}, {"name": "emit", "type": "str", "flag": True},
                           {"name": "good", "type": "str", "flag": True}]),
               json.dumps({"arg": "out", "format": "jsonl", "require": {"when_any": ["emit"], "rows": "built.verified"}})))
    c.commit(); c.close()
    out = str(tmp_path / "n.jsonl")
    r = run(env, "fire", "test.need", "need", "--arg", f"out={out}", "--arg", "emit=true", ok=False)
    rec = json.loads(r.stdout.strip().splitlines()[-1])
    assert r.returncode == 1 and rec["verdict"] == "fail" and "3/3 rows missing" in rec["note"]
    rec = json.loads(run(env, "fire", "test.need", "need", "--arg", f"out={out}", "--arg", "emit=true", "--arg", "good=true").stdout.strip().splitlines()[-1])
    assert rec["verdict"] == "pass"
    rec = json.loads(run(env, "fire", "test.need", "need", "--arg", f"out={out}").stdout.strip().splitlines()[-1])
    assert rec["verdict"] == "pass"                      # no emit flag → no requirement

#!/usr/bin/env python3
"""Recount a core-receipts file and write (1) a counts summary and (2) a scrubbed sample.

usage: receipts_recount.py RECEIPTS.jsonl OUTDIR

The input file is private (some lines carry private text) and is not shipped; its sha256 is
recorded in the summary. The sample keeps hashes, verdicts and timings only: output_ref paths,
free-text notes, probe payloads, caller names and run names are replaced (see SCRUB below).
Python standard library only.
"""
import collections, hashlib, json, os, sys

# output files that ship next to the sample: basename -> destination path of the shipped copy
SHIPPED_OUT = {
    "wall.out.jsonl": "experiments/part7/ch5-host/results/h6/wall.out.jsonl",
    "spec.raptor.jsonl": "experiments/part7/ch5-host/results/h6/spec.raptor.jsonl",
}
SHIPPED_HASH_PREFIXES = ("sha256:564d8972", "sha256:bd854332")  # sha256 of the two shipped h6 output files
NOTE_CLASSES = ("require built.verified: no output file", "exit 101", "exit 3: blackbox", "exit 1", "exit 127")


def load(path):
    raw = open(path, "rb").read()
    rows = [json.loads(l) for l in raw.decode().splitlines() if l.strip()]
    return raw, rows


def base(r):
    return r["core"].split("@")[0]


def note_class(n):
    if not n:
        return None
    for c in NOTE_CLASSES:
        if n.startswith(c):
            return "equation REFUSED" if c == "exit 3: blackbox" and "REFUSED" in n else c
    return "other"


def scrub(r):
    gate = r.get("gate")
    if gate is not None and any(t in gate for t in ("/", "host", "nproc", "load")):
        gate = None  # probe payloads and paths are not shipped
    ref = r.get("output_ref")
    if ref:
        ref = SHIPPED_OUT.get(os.path.basename(ref), "<path>")
    caller = r["caller"]
    caller = "raptor-ui" if caller == "raptor-ui" else ("<caller>@" + caller.split("@", 1)[1] if "@" in caller else "<caller>")
    out = {"v": r["v"], "ts": r["ts"], "core": r["core"], "version": r["version"], "op": r["op"],
           "caller": caller, "input_hash": r["input_hash"], "output_ref": ref,
           "output_hash": r["output_hash"], "gate": gate, "verdict": r["verdict"], "ms": r["ms"],
           "tw": None if r["tw"] is None else "<run-name>"}
    if r.get("note"):
        out["note_class"] = note_class(r["note"])
    return out


def summarise(raw, rows):
    S = {"source_sha256": hashlib.sha256(raw).hexdigest(), "lines": len(rows),
         "first_ts": rows[0]["ts"], "last_ts": rows[-1]["ts"], "ts_min": min(r["ts"] for r in rows), "ts_max": max(r["ts"] for r in rows)}
    S["verdicts"] = dict(collections.Counter(r["verdict"] for r in rows))
    fails = [r for r in rows if r["verdict"] == "fail"]
    S["fail_classes"] = {
        "core_host_run_nonzero": sum(1 for r in fails if base(r) == "core-host" and r["op"] == "run"),
        "doctor_blackbox_failures": sum(1 for r in fails if r["core"].startswith("doctor.blackbox")),
        "doctor_blackbox_equation_refused": sum(1 for r in fails if r["core"].startswith("doctor.blackbox") and "REFUSED" in (r.get("note") or "")),
        "post_condition": sum(1 for r in fails if (r.get("note") or "").startswith("require built.verified")),
        "doctor_wall_exit_101": sum(1 for r in fails if r["core"].startswith("doctor.wall") and (r.get("note") or "").startswith("exit 101")),
    }
    pc = [r for r in fails if (r.get("note") or "").startswith("require built.verified")]
    S["post_condition_distinct_hosts"] = len({r["core"].split("@")[1] for r in pc})
    dr = [r for r in rows if r["core"].startswith("doctor.") and "@" in r["core"]]
    dl = [r for r in rows if r["core"].startswith("doctor.") and "@" not in r["core"]]
    S["doctor_remote"] = dict(collections.Counter(r["verdict"] for r in dr))
    S["doctor_local"] = dict(collections.Counter(r["verdict"] for r in dl))
    ch = collections.defaultdict(collections.Counter)
    for r in rows:
        if base(r) == "core-host":
            ch[r["op"]][r["verdict"]] += 1
    S["core_host"] = {"receipts": sum(sum(c.values()) for c in ch.values()), "by_op": {k: dict(v) for k, v in ch.items()}}
    gen = [r for r in rows if r["core"].startswith("gen.")]
    S["gen"] = {"receipts": len(gen), "verdicts": dict(collections.Counter(r["verdict"] for r in gen)),
                "output_hash_null": sum(1 for r in gen if r["output_hash"] is None),
                "null_by_op": dict(collections.Counter(r["op"] for r in gen if r["output_hash"] is None)),
                "hashed_by_op": dict(collections.Counter(r["op"] for r in gen if r["output_hash"] is not None))}
    mk = [r for r in rows if r["core"] == "math.kb"]
    S["math_kb"] = {"receipts": len(mk), "output_hash_null": sum(1 for r in mk if r["output_hash"] is None),
                    "null_by_op": dict(collections.Counter(r["op"] for r in mk if r["output_hash"] is None)),
                    "hashed_by_op": dict(collections.Counter(r["op"] for r in mk if r["output_hash"] is not None))}
    ui = [r for r in rows if r["caller"] == "raptor-ui"]
    S["console_caller"] = {"receipts": len(ui), "tw_null": sum(1 for r in ui if r["tw"] is None), "tw_set": sum(1 for r in ui if r["tw"] is not None)}
    S["output_hash_equals_file_sha256"] = "recomputed separately; see the note column of the ship list"
    return S


def sample_rows(rows):
    keep, seen = [], set()

    def add(r):
        k = id(r)
        if k not in seen:
            seen.add(k)
            keep.append(r)
    for r in rows[:5]:
        add(r)
    for r in rows:
        if r["core"] == "math.kb" or r["core"].startswith("gen.") or r["core"] == "chew.sessions" or r["caller"] == "raptor-ui":
            add(r)
        elif (r.get("note") or "").startswith(("require built.verified", "exit 101")):
            add(r)
        elif os.path.basename(r.get("output_ref") or "") in SHIPPED_OUT or (r["output_hash"] or "").startswith(SHIPPED_HASH_PREFIXES):
            add(r)
        elif base(r) == "core-host" and r["op"] == "map":
            add(r)
    return sorted(keep, key=lambda r: rows.index(r))


def main(src, outdir):
    raw, rows = load(src)
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "receipts-summary.json"), "w") as f:
        json.dump(summarise(raw, rows), f, indent=1, sort_keys=True); f.write("\n")
    with open(os.path.join(outdir, "receipts-sample.jsonl"), "w") as f:
        for r in sample_rows(rows):
            f.write(json.dumps(scrub(r), sort_keys=True) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

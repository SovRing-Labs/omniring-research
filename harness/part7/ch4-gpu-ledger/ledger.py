#!/usr/bin/env python3
"""GPU-LOOP clean-room ledger (J 10-08: "ensure proper documentation and tracking of each step, with source license and essential
data for cleanroom certification").  Append-only, hash-chained JSONL: gpu/cleanroom/ledger.jsonl.

  ledger.py add --step ID --stage G1b --what "text" --op a,b --artifact PATH [--artifact PATH ...]
                [--src ID,..] spec-store ids OPENED+READ this step · [--cite ID,..] ideas cited, document not opened; both copy (licence + sha256 copied from research/specs/<id>/provenance.json)
                [--basis "published math the equations were authored from (idea only)"]
                [--reader PATH] [--result "wall / parity verdict"] [--oracle "what the output was checked against"]
  ledger.py verify        chain intact · every artifact still hashes as recorded (drift is listed, not hidden) · third-party scan
  ledger.py show [--step ID]

Each entry records: who/what authored (role), our code's licence, the engine file hash (our code, read-only input), every consulted
source with its licence and document hash, reader/emitter binary hash + repo revision, artifact hashes, the verification result, and
fixed attestations.  A certification reviewer needs only this file + the artifacts it hashes.
"""
import argparse, hashlib, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
GPU = os.path.dirname(HERE)
LEDGER = os.path.join(HERE, "ledger.jsonl")
MAIN = os.environ.get("AISTACK", "<workspace>")
SPECS = os.path.join(MAIN, "research", "specs")
ENGINE = os.path.join(GPU, "..", "engine", "omni_train", "omni_train.cpp")
OUR_LICENCE = ("ai-stack own code: copyright J (jc); source-available dual PolyForm Small Business 1.0.0 OR PolyForm Noncommercial 1.0.0 "
               "for the nervous-system packages; release licence for GPU-LOOP output is J's decision at release (memory release-and-licensing)")
ATTEST = [
    "Equations/kernels were authored from OUR engine's behaviour and published mathematics only; no third-party kernel source "
    "(CUTLASS, BitBLAS, BitNet, cuBLAS, FlashAttention code) was copied, translated or read as a code donor.",
    "Consulted sources are listed with licence and document sha256; they are no-train references read for idea/function only.",
    "cuBLAS/cuDNN, if used, are black-box oracles or linked NVIDIA runtime libraries (allowed by the brief), never code donors.",
    "The reader (behaviour -> equation) and the implementer (equation -> kernel) are separate tools joined only by the wall "
    "(core --abc wall: schema + grammar + leak scan; seeded leaks refused).",
]
BANNED = ["cutlass", "bitblas", "bitnet.cpp", "permission is hereby granted", "spdx-license-identifier", "copyright (c) nvidia",
          "all rights reserved", "apache license", "mit license"]


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def sh(cmd, cwd=None):
    try:
        return subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:
        return ""


def entries():
    if not os.path.exists(LEDGER):
        return []
    return [json.loads(l) for l in open(LEDGER) if l.strip()]


def entry_hash(e):
    return hashlib.sha256(json.dumps({k: v for k, v in e.items() if k != "hash"}, sort_keys=True).encode()).hexdigest()


def cmd_add(a):
    es = entries(); prev = es[-1]["hash"] if es else "0" * 64
    srcs = []; cites = []
    for kind, ids in (("consulted", a.src), ("cited", a.cite)):
      for sid in [s for grp in (ids or []) for s in grp.split(",") if s]:
        p = os.path.join(SPECS, sid, "provenance.json")
        if not os.path.exists(p):
            sys.exit(f"unknown spec-store id {sid} (research/specs/<id>/provenance.json)")
        pv = json.load(open(p))
        (srcs if kind == "consulted" else cites).append({"id": sid, "title": pv.get("title"), "licence": pv.get("licence"), "url": pv.get("url"), "sha256": pv.get("sha256"),
            "use": "opened and read this step; idea/function only (no-train)" if kind == "consulted" else "idea cited from published work; document NOT opened this step (no-train)"})
    arts = []
    for p in a.artifact or []:
        ap = os.path.abspath(p)
        if not os.path.exists(ap):
            sys.exit(f"artifact missing: {p}")
        arts.append({"path": os.path.relpath(ap, os.path.join(GPU, "..", "..", "..")), "sha256": sha(ap), "bytes": os.path.getsize(ap)})
    e = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "step": a.step, "stage": a.stage, "what": a.what,
         "ops": [o for o in (a.op or "").split(",") if o], "author": a.author, "our_licence": OUR_LICENCE,
         "input_engine": {"path": "projects/thead-trial/engine/omni_train/omni_train.cpp", "sha256": sha(ENGINE), "use": "OUR code, read-only behavioural oracle"},
         "sources_consulted": srcs, "ideas_cited": cites, "formula_basis": a.basis, "oracle": a.oracle, "artifacts": arts, "result": a.result,
         "host": os.uname().nodename, "worktree_rev": sh("git rev-parse --short HEAD", GPU), "attestations": ATTEST, "prev": prev}
    if a.reader:
        e["tool"] = {"path": a.reader, "sha256": sha(a.reader), "repo_rev": sh("git rev-parse --short HEAD", os.path.dirname(os.path.dirname(os.path.dirname(a.reader))))}
    e["hash"] = entry_hash(e)
    with open(LEDGER, "a") as f:
        f.write(json.dumps(e, sort_keys=True) + "\n")
    print(f"ledger +1  step={a.step} stage={a.stage} artifacts={len(arts)} sources={len(srcs)} hash={e['hash'][:12]}")


def cmd_verify(_):
    es = entries(); bad = 0; prev = "0" * 64; root = os.path.join(GPU, "..", "..", "..")
    for i, e in enumerate(es):
        if e["prev"] != prev or e["hash"] != entry_hash(e):
            print(f"CHAIN BROKEN at entry {i} ({e['step']})"); bad += 1
        prev = e["hash"]
        for ar in e["artifacts"]:
            p = os.path.join(root, ar["path"])
            if not os.path.exists(p):
                print(f"MISSING  {ar['path']} (step {e['step']})")
            elif sha(p) != ar["sha256"]:
                print(f"DRIFT    {ar['path']} changed since step {e['step']} (re-ledger it if intended)")
    for d in ("specs", "emit"):
        for dp, _, fs in os.walk(os.path.join(GPU, d)):
            for fn in fs:
                if fn.endswith((".jsonl", ".json", ".log")):
                    continue
                t = open(os.path.join(dp, fn), errors="ignore").read().lower()
                for b in BANNED:
                    if b in t:
                        print(f"THIRD-PARTY MARKER '{b}' in {os.path.relpath(os.path.join(dp, fn), GPU)}"); bad += 1
    print(f"verify: {len(es)} entries, chain {'OK' if not bad else 'PROBLEMS'}")
    sys.exit(1 if bad else 0)


def cmd_show(a):
    for e in entries():
        if a.step and e["step"] != a.step:
            continue
        print(f"{e['ts']} {e['step']:<14} {e['stage']:<5} ops={','.join(e['ops']) or '-'} srcs={[s['id'] for s in e['sources_consulted']]} :: {e['result']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="c", required=True)
    p = sp.add_parser("add"); p.add_argument("--step", required=True); p.add_argument("--stage", required=True); p.add_argument("--what", required=True)
    p.add_argument("--op"); p.add_argument("--artifact", action="append"); p.add_argument("--src", action="append"); p.add_argument("--cite", action="append"); p.add_argument("--basis", default="")
    p.add_argument("--reader"); p.add_argument("--result", default=""); p.add_argument("--oracle", default="OUR engine (omni_train.cpp) rows")
    p.add_argument("--author", default="claude seat (GPU-LOOP-0 builder, Sonnet 5.5) with the doctor clean-room tools"); p.set_defaults(f=cmd_add)
    sp.add_parser("verify").set_defaults(f=cmd_verify)
    p = sp.add_parser("show"); p.add_argument("--step"); p.set_defaults(f=cmd_show)
    a = ap.parse_args(); a.f(a)

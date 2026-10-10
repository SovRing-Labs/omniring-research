#!/usr/bin/env python3
"""grow_ctl — the GROW-RUN-0 controller (J 10-09; plan <notes>/worker/claude/<plan>). One call per round, after
`GROW_GATE=1.0 school_graph.py update` — it keeps the run going with no seat:
  · growth rate: one row per round in <run>/growth.jsonl (tier, stage, skills at the gate per stage, held-out, tokens, seconds, params, mode)
    — J: "growth rate: how much each run progresses the model at every tier"
  · mode for the next round: SKILLS until middle school is passed at the gate; after it, a WALL → PARAMS (grow the model, then back to
    SKILLS — J: "once it's ready it switches to growing parameters, then back to growing skills"); a WALL again within WALL_AFTER_GROW
    rounds of a growth with no gain since → GENERATORS (J: "eventually growing new generators"; a NEW faculty needs J's admission, VOCAB "the 26")
  · keeps: a permanent, checksummed copy of the core every KEEP_EVERY rounds, at every stage pass and after every growth, in <run>/keep/
    (never pruned — J: "auto save checkpoints to backup every so often")
  grow_ctl.py step  RUN --round R --update UPD.json --core DIR --tier T [--params N] [--tokens N] [--secs S] [--heldout X]
  grow_ctl.py grown RUN --round R --params-from A --params-to B [--how TEXT]
  grow_ctl.py report RUN
  grow_ctl.py verify RUN   → the provenance chain (PROVENANCE-CONCEPTS-2026-10-09 #5): every round's ledger row (core sha256, the round's
                             eval + plan sha256, gate evidence, decision, keep) linked by sha256 to the row before; keeps' MANIFESTs re-hashed"""
import hashlib, json, os, shutil, sys, time

KEEP_EVERY = int(os.environ.get("GROW_KEEP_EVERY", "5")); WALL_AFTER_GROW = int(os.environ.get("GROW_WALL_AFTER", "6")); GROWN_ROUNDS = int(os.environ.get("GROW_GROWN_ROUNDS", "3")); GRACE_MAX = int(os.environ.get("GROW_GRACE_MAX", "10"))
ORDER = ["prek", "k", "elem", "middle", "high", "done"]
CORE_FILES = ("ckpt.bin", "ckpt.json", "state.json", "t25_core.bin", "t25_core.json")


def load_ctl(run):
    p = os.path.join(run, "grow-ctl.json")
    return json.load(open(p)) if os.path.exists(p) else {"mode": "skills", "growths": [], "keeps": [], "passed": [], "t0": time.time()}


def save_ctl(run, c):
    json.dump(c, open(os.path.join(run, "grow-ctl.json"), "w"), indent=1)


def keep(run, core, rnd, why):
    d = os.path.join(run, "keep", f"r{rnd}-{why}"); os.makedirs(d, exist_ok=True); man = []
    for f in CORE_FILES:
        s = os.path.join(core, f)
        if os.path.exists(s):
            shutil.copy2(s, os.path.join(d, f)); man.append(f"{hashlib.sha256(open(s, 'rb').read()).hexdigest()}  {f}")
    open(os.path.join(d, "MANIFEST.sha256"), "w").write("\n".join(man) + "\n")
    return d


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest() if path and os.path.exists(path) else None


def ledger_add(run, row):
    """append a hash-chained provenance row: hash = sha256(canonical JSON of the row with prev, without hash)"""
    p = os.path.join(run, "ledger.jsonl"); prev = None
    if os.path.exists(p):
        lines = [l for l in open(p) if l.strip()]
        if lines: prev = json.loads(lines[-1])["hash"]
    row = dict(row, prev=prev); row["hash"] = hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest()
    open(p, "a").write(json.dumps(row, sort_keys=True) + "\n"); return row["hash"]


def verify(run):
    p = os.path.join(run, "ledger.jsonl"); prev = None; bad = []; n = 0
    for i, l in enumerate(open(p) if os.path.exists(p) else []):
        if not l.strip(): continue
        r = json.loads(l); h = r.pop("hash"); n += 1
        if r.get("prev") != prev: bad.append(f"row {i}: prev link broken")
        if hashlib.sha256(json.dumps(r, sort_keys=True).encode()).hexdigest() != h: bad.append(f"row {i}: content hash mismatch")
        k = r.get("keep")
        if k and os.path.exists(os.path.join(k, "MANIFEST.sha256")):
            for line in open(os.path.join(k, "MANIFEST.sha256")):
                if not line.strip(): continue
                hh, f = line.split(None, 1); f = f.strip()
                if sha(os.path.join(k, f)) != hh: bad.append(f"row {i}: keep {f} changed")
        prev = h
    out = {"rows": n, "ok": not bad, "problems": bad}; print(json.dumps(out)); return out


def step(run, a):
    os.makedirs(run, exist_ok=True); c = load_ctl(run); upd = json.load(open(a["update"])); rnd = int(a["round"])
    stage = upd.get("stage", "prek"); si = ORDER.index(stage) if stage in ORDER else 0
    rows = [json.loads(l) for l in open(os.path.join(run, "growth.jsonl"))] if os.path.exists(os.path.join(run, "growth.jsonl")) else []
    prev = rows[-1] if rows else None
    if upd.get("stage_passed"): c["passed"].append({"round": rnd, "stage_before": ORDER[max(0, si - 1)], "hours": round((time.time() - c["t0"]) / 3600, 3)})
    mode = c["mode"]
    if mode == "params":                                              # a growth was requested and not yet recorded: hold the request
        nxt = "params"
    elif si <= ORDER.index("middle"):                                 # before middle is passed: skills only
        nxt = "skills"
    elif not upd.get("WALL"):
        nxt = "skills"
    else:                                                             # a wall after middle school
        g = c["growths"][-1] if c["growths"] else None
        since = rnd - g["round"] if g else None; gained_since = (upd.get("at_gate", 0) - (g["at_gate"] or 0)) if g else None
        if g is None: nxt = "params"
        elif since < GROWN_ROUNDS or (since < GRACE_MAX and g.get("heldout") is not None and a.get("heldout") and float(a["heldout"]) > g["heldout"]):
            nxt = "skills"                                            # grace (double descent): the grown model recovers its held-out first
        elif since <= WALL_AFTER_GROW and gained_since <= 0: nxt = "generators"   # growth did not lift the wall
        else: nxt = "params"
    row = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "round": rnd, "tier": a.get("tier"), "mode": mode, "next_mode": nxt,
           "stage": stage, "stage_passed": bool(upd.get("stage_passed")), "at_gate": upd.get("at_gate"), "gate": upd.get("gate"),
           "stages": upd.get("stages"), "wall_rounds": upd.get("wall_rounds"), "WALL": upd.get("WALL"),
           "params": int(a["params"]) if a.get("params") else None, "tokens": int(float(a["tokens"])) if a.get("tokens") else None,
           "secs": float(a["secs"]) if a.get("secs") else None, "heldout": float(a["heldout"]) if a.get("heldout") else None,
           "hours": round((time.time() - c["t0"]) / 3600, 4)}
    if prev and prev.get("at_gate") is not None and row["at_gate"] is not None:
        row["gain"] = row["at_gate"] - prev["at_gate"]
        dt = (row["secs"] or 0) / 3600; row["gain_per_hour"] = round(row["gain"] / dt, 3) if dt > 0 else None
    why = [w for w, on in (("stage", row["stage_passed"]), ("every", rnd % KEEP_EVERY == 0),
                           ("grown", bool(c["growths"]) and c["growths"][-1]["round"] == rnd - 1)) if on]
    if why and a.get("core"):
        row["keep"] = keep(run, a["core"], rnd, "-".join(why)); c["keeps"].append(row["keep"])
    c["mode"] = nxt; save_ctl(run, c)
    open(os.path.join(run, "growth.jsonl"), "a").write(json.dumps(row) + "\n")
    ledger_add(run, {"round": rnd, "ts": row["ts"], "tier": row["tier"], "core_ckpt_sha256": sha(os.path.join(a["core"], "ckpt.bin")) if a.get("core") else None,
                     "eval_sha256": sha(a.get("eval")), "plan_sha256": sha(a.get("plan")), "update_sha256": sha(a["update"]),
                     "gate": {"stage": stage, "at_gate": row["at_gate"], "gate": row["gate"], "min_rows": upd.get("min_rows"), "stages": row["stages"]},
                     "decision": {"mode": mode, "next_mode": nxt, "WALL": row["WALL"]}, "keep": row.get("keep")})
    print(json.dumps({"round": rnd, "mode": nxt, "stage": stage, "at_gate": row["at_gate"], "gain": row.get("gain"), "keep": row.get("keep")}))


def grown(run, a):
    c = load_ctl(run); rows = [json.loads(l) for l in open(os.path.join(run, "growth.jsonl"))]
    c["growths"].append({"round": int(a["round"]), "from": int(a["params-from"]), "to": int(a["params-to"]), "how": a.get("how", ""),
                         "at_gate": rows[-1].get("at_gate") if rows else None, "heldout": rows[-1].get("heldout") if rows else None})
    c["mode"] = "skills"; save_ctl(run, c)
    ledger_add(run, {"round": int(a["round"]), "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "event": "grown", "growth": c["growths"][-1],
                     "core_ckpt_sha256": sha(os.path.join(a["core"], "ckpt.bin")) if a.get("core") else None})
    print(json.dumps({"grown": c["growths"][-1], "mode": "skills"}))


def report(run):
    c = load_ctl(run); rows = [json.loads(l) for l in open(os.path.join(run, "growth.jsonl"))] if os.path.exists(os.path.join(run, "growth.jsonl")) else []
    if not rows: print(json.dumps({"rounds": 0})); return
    out = {"tier": rows[-1].get("tier"), "rounds": len(rows), "hours": rows[-1].get("hours"), "at_gate_first": rows[0].get("at_gate"),
           "at_gate_last": rows[-1].get("at_gate"), "stage_now": rows[-1].get("stage"), "stages_passed": c["passed"], "growths": c["growths"],
           "keeps": len(c["keeps"]), "mode_now": c["mode"]}
    h = sum(r.get("secs") or 0 for r in rows) / 3600
    if h > 0 and out["at_gate_first"] is not None: out["skills_per_hour"] = round((out["at_gate_last"] - out["at_gate_first"]) / h, 2)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    av = sys.argv[1:]; cmd, run = av[0], av[1]; a = {}
    i = 2
    while i < len(av):
        if av[i].startswith("--"): a[av[i][2:]] = av[i + 1]; i += 2
        else: i += 1
    r = {"step": lambda: step(run, a), "grown": lambda: grown(run, a), "report": lambda: report(run), "verify": lambda: verify(run)}[cmd]()
    if cmd == "verify" and not r["ok"]: sys.exit(1)

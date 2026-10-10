#!/usr/bin/env python3
"""ramkit #6 — forgetting watch (RAM-KIT-0, J 10-08). Every round's skill.json re-scores the skills in its held-out build (mastered skills are
in it through the REVIEW share). A SLIP = a skill in state.json's mastered list whose latest score is under the gate (0.85). Each slip gets a
replay weight for the next plan, proportional to how far under the gate it fell; the planner adds it on top of review.

  forget_watch.py watch <state.json> <skill.json …(round order)> [--out replay.json] [--share 0.15] [--gate 0.85]
  forget_watch.py selftest
Merge point (seat wires it; school_graph.py is not ours): in school_graph.plan(), right after the REVIEW block
    ("for k in rev: w[k] = w.get(k, 0) + rw") add
        if os.environ.get("RAMKIT_REPLAY"):
            sys.path.insert(0, os.path.expanduser("<home>/ai-stack/projects/thead-trial/ramkit")); import forget_watch
            w = forget_watch.apply(w, os.environ["RAMKIT_REPLAY"], N)
and in school-live.sh before `school_graph.py plan` (ramkit-hooks.sh `ramkit_watch`): write $L/r$r/replay.json from r1..r(r-1) skill.json."""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

GATE = 0.85


def history(skill_files):
    """per skill: [(round index, score)] in the order given"""
    h = {}
    for i, f in enumerate(skill_files):
        for k, v in json.load(open(f))["skill"].items(): h.setdefault(k, []).append((i + 1, float(v)))
    return h


def watch(state_path, skill_files, share=0.15, gate=GATE):
    st = json.load(open(state_path)); mastered = set(st["mastered"]); h = history(skill_files)
    slips, gaps = [], {}
    for k in sorted(mastered):
        if k not in h: continue
        r, v = h[k][-1]
        if v < gate:
            first = next((rr for rr, vv in h[k] if vv >= gate), None)
            slips.append({"skill": k, "round": r, "score": round(v, 4), "first_at_gate_round": first, "gap": round(gate - v, 4)})
            gaps[k] = gate - v
    tot = sum(gaps.values())
    replay = {k: round(share * g / tot, 5) for k, g in gaps.items()} if tot else {}
    rescored = sum(1 for k in mastered if k in h and h[k][-1][0] == len(skill_files))
    return {"rounds": len(skill_files), "mastered": len(mastered), "rescored_last_round": rescored, "slips": slips,
            "replay_share": share if replay else 0.0, "replay": replay, "gate": gate,
            "merge": "school_graph.plan: w = forget_watch.apply(w, RAMKIT_REPLAY, N) after the REVIEW block"}


def apply(w, replay_path, N=None):
    """add the replay weights to the plan's weights: replay share s of the current total for each slipped skill (in the graph, built)"""
    if not replay_path or not os.path.exists(replay_path): return w
    rep = json.load(open(replay_path)).get("replay", {}); tot = sum(w.values()) or 1.0; w = dict(w)
    for k, s in rep.items():
        if N is not None and (k not in N or N[k].get("builder") == "UNBUILT"): continue
        w[k] = w.get(k, 0.0) + s * tot
    return w


def selftest(out=None):
    import tempfile
    d = tempfile.mkdtemp(prefix="ramkit-watch-")
    json.dump({"mastered": ["a@1", "b@1", "c@2"], "score": {}, "hist": {}, "rounds": 2, "wall": 0}, open(f"{d}/state.json", "w"))
    json.dump({"skill": {"a@1": 0.9, "b@1": 0.95}}, open(f"{d}/r1.json", "w"))
    json.dump({"skill": {"a@1": 0.91, "b@1": 0.70, "c@2": 0.88, "x@1": 0.4}}, open(f"{d}/r2.json", "w"))
    r = watch(f"{d}/state.json", [f"{d}/r1.json", f"{d}/r2.json"])
    json.dump(r, open(f"{d}/replay.json", "w"))
    w0 = {"a@1": 0.05, "b@1": 0.05, "x@1": 1.0}; w1 = apply(w0, f"{d}/replay.json")
    ok = ([s["skill"] for s in r["slips"]] == ["b@1"] and r["slips"][0]["first_at_gate_round"] == 1 and set(r["replay"]) == {"b@1"}
          and w1["b@1"] > w0["b@1"] and w1["a@1"] == w0["a@1"] and abs(w1["b@1"] - w0["b@1"] - 0.15 * sum(w0.values())) < 1e-9)
    res = {"fixture_slips": r["slips"], "weights_before": w0, "weights_after": w1}
    live = os.path.join(C.TRIAL, "runtime/results/live-school")                       # read-only report on the live run, if present
    sk = [f"{live}/r{i}/skill.json" for i in range(1, 50) if os.path.exists(f"{live}/r{i}/skill.json")]
    if sk and os.path.exists(f"{live}/state.json"):
        L = watch(f"{live}/state.json", sk)
        res["live_school"] = {"rounds": L["rounds"], "mastered": L["mastered"], "rescored_last_round": L["rescored_last_round"],
                              "slips": len(L["slips"]), "slipped": [(s["skill"], s["score"]) for s in L["slips"]][:20]}
    if out: C.json_out(res, out)
    return ok, res


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="c", required=True)
    w = sp.add_parser("watch"); w.add_argument("state"); w.add_argument("skills", nargs="+"); w.add_argument("--out")
    w.add_argument("--share", type=float, default=0.15); w.add_argument("--gate", type=float, default=GATE)
    s = sp.add_parser("selftest"); s.add_argument("--out")
    a = ap.parse_args()
    if a.c == "watch":
        r = watch(a.state, a.skills, a.share, a.gate); print(C.json_out(r, a.out) if a.out else json.dumps(r))
    else:
        ok, res = selftest(a.out); print(json.dumps(res)); print("PASS" if ok else "FAIL", "forget_watch"); sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

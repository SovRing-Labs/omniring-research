#!/usr/bin/env python3
"""ramkit #14 — speculative curriculum branches (RAM-KIT-0, J 10-08). DEFAULT OFF (BRANCHES=0); model-changing → on only on J's go.
Given a round plan (school_graph.py plan → plan-r<N>.json + live-r<N>.json), emit k alternative tier-1 specs that weight the next lessons
differently; after the round, a chooser picks the winner from each branch's held-out skill.json (same held-out build for all branches).
Branch weightings (applied to the plan's tier-1 weights; passes rebuilt with school_graph's own MIN_SHARE merge rule):
  b0 base      the plan as made (control)
  b1 sharpen   w² — lean harder on the highest learning progress
  b2 flat      every tier-1 frontier skill equal; review keeps its share
  b3 low-first the lowest frontier level ×2 (consolidate before climbing)
  b4 review+   review share doubled (mastered skills ×2)

  branches.py emit   <plan-rN.json> <k> <out_dir>       → out_dir/live-rN-b<i>.json + branches-rN.json (spec paths, weights)
  branches.py choose <branches-rN.json> <skill-b0.json> <skill-b1.json> …  [--out choose.json]   → winner (mean top-1 over the round's
                     frontier skills present in every branch's eval; ties keep b0)
  branches.py selftest
Wiring (seat; ramkit-hooks.sh ramkit_branches): branch harnesses run WITHOUT PAR_DIR (a branch must not be averaged into the day merge),
each on its own branch build; skill-eval each on the round's held-out; choose; if a branch wins, next CORE = that branch's core."""
import argparse, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
sys.path.insert(0, os.path.join(C.TRIAL, "harness"))

NAMES = ["base", "sharpen", "flat", "low-first", "review+"]


def variants(w, N, mastered):
    t1 = {k: v for k, v in w.items() if k in N and N[k]["builder"] == "tier1"}
    fr = {k: v for k, v in t1.items() if k not in mastered}; rv = {k: v for k, v in t1.items() if k in mastered}
    out = [dict(t1)]
    out.append({**{k: v * v for k, v in fr.items()}, **rv})
    m = (sum(fr.values()) / len(fr)) if fr else 0
    out.append({**{k: m for k in fr}, **rv})
    lo = min((N[k]["level"] for k in fr), default=0)
    out.append({**{k: v * (2 if N[k]["level"] == lo else 1) for k, v in fr.items()}, **rv})
    out.append({**fr, **{k: v * 2 for k, v in rv.items()}})
    return out


def passes_of(t1, N, rnd, min_share):
    """school_graph.plan's tier-1 pass builder (by level; a pass under MIN_SHARE joins its neighbour)"""
    by_lv = {}
    for k, v in t1.items(): by_lv.setdefault(N[k]["level"], {})[N[k]["lesson"]] = round(v, 4)
    tot = sum(t1.values()) or 1.0; ps = []
    for lv in sorted(by_lv):
        les = by_lv[lv]
        ps.append({"name": f"round {rnd} · level {lv}", "share": round(sum(les.values()) / tot, 4), "levels": [lv], "format": "b",
                   "format_of": {l: ("a" if l.startswith("pk.") else "b") for l in les}, "lessons": les})
    merged = []
    for p in ps:
        if merged and (p["share"] < min_share or merged[-1]["share"] < min_share):
            m = merged[-1]; m["levels"] = sorted(set(m["levels"]) | set(p["levels"])); m["share"] = round(m["share"] + p["share"], 4)
            for l, v in p["lessons"].items(): m["lessons"][l] = round(m["lessons"].get(l, 0) + v, 4)
            m["format_of"].update(p["format_of"]); m["name"] = f"round {rnd} · levels {m['levels'][0]}–{m['levels'][-1]}"
        else: merged.append(p)
    return merged


def emit(plan_path, k, out, mastered=None):
    import school_graph as g
    P = json.load(open(plan_path)); rnd = P["round"]; N = g.nodes()
    base = json.load(open(P["specs"]["tier1"])) if P["specs"].get("tier1") else None
    if base is None: return {"round": rnd, "branches": [], "note": "no tier-1 spec this round — nothing to branch"}
    if mastered is None:                                       # mastered = weights the plan gave to non-frontier skills (review)
        mastered = {kk for kk in P["weights"] if kk not in set(P["frontier"])}
    V = variants(P["weights"], N, mastered); os.makedirs(out, exist_ok=True); br = []
    for i in range(min(k, len(V))):
        s = json.loads(json.dumps(base)); s["id"] = f"{base['id']}-b{i}"; s["passes"] = passes_of(V[i], N, rnd, g.MIN_SHARE)
        s["why"] = f"{base.get('why', '')} · ramkit branch b{i} ({NAMES[i]})"; s["branch"] = {"of": base["id"], "i": i, "name": NAMES[i]}
        p = os.path.join(out, f"{s['id']}.json"); json.dump(s, open(p, "w"), indent=1)
        br.append({"i": i, "name": NAMES[i], "spec": p, "weights": {kk: round(v, 5) for kk, v in V[i].items()}})
    meta = {"round": rnd, "plan": os.path.abspath(plan_path), "frontier": [f for f in P["frontier"] if f in N and N[f]["builder"] == "tier1"],
            "branches": br}
    json.dump(meta, open(os.path.join(out, f"branches-r{rnd}.json"), "w"), indent=1)
    return meta


def choose(meta_path, skill_files, out=None):
    M = json.load(open(meta_path)); S = [json.load(open(f))["skill"] for f in skill_files]
    common = [k for k in M["frontier"] if all(k in s for s in S)]
    score = [sum(s[k] for k in common) / len(common) if common else float("-inf") for s in S]
    best = max(range(len(S)), key=lambda i: (score[i], -i))   # tie → lowest index (b0 = control)
    r = {"round": M["round"], "frontier_scored": len(common), "mean_top1": [round(x, 4) if math.isfinite(x) else None for x in score],
         "winner": best, "winner_name": M["branches"][best]["name"] if best < len(M["branches"]) else None,
         "margin_vs_base": round(score[best] - score[0], 4) if common else None}
    if out: C.json_out(r, out)
    return r


def selftest(out=None):
    import tempfile, school_graph as g
    d = tempfile.mkdtemp(prefix="ramkit-branch-"); N = g.nodes()
    fr = ["pk.echo@3", "pk.ping@2", "pk.hold@2", "k.store@1", "pk.babble@4"]; rv = ["pk.echo@1", "pk.echo@2", "pk.ping@1"]
    w = {"pk.echo@3": 2.0, "pk.ping@2": 0.5, "pk.hold@2": 1.0, "k.store@1": 0.25, "pk.babble@4": 1.5, **{k: 0.3 for k in rv}}
    spec = {"id": "live-r9", "status": "approved", "school": "live", "role": "training", "ctx": 512, "tokens": 1000000, "passes": [], "why": "fixture"}
    json.dump(spec, open(f"{d}/live-r9.json", "w"))
    json.dump({"round": 9, "frontier": fr, "weights": w, "specs": {"tier1": f"{d}/live-r9.json"}, "unbuilt": []}, open(f"{d}/plan-r9.json", "w"))
    M = emit(f"{d}/plan-r9.json", 4, f"{d}/br")
    specs = [json.load(open(b["spec"])) for b in M["branches"]]
    shares_ok = all(abs(sum(p["share"] for p in s["passes"]) - 1) < 0.01 for s in specs)
    lessons_ok = all({l for p in s["passes"] for l in p["lessons"]} <= {N[k]["lesson"] for k in w} for s in specs)
    distinct = len({json.dumps(s["passes"], sort_keys=True) for s in specs}) == len(specs)
    flat_ok = len({round(v, 6) for kk, v in M["branches"][2]["weights"].items() if kk in fr}) == 1
    sk = []
    for i, bonus in enumerate([0.0, 0.05, -0.02, 0.01]):
        f = f"{d}/skill-b{i}.json"; json.dump({"skill": {k: 0.6 + bonus for k in fr}}, open(f, "w")); sk.append(f)
    ch = choose(os.path.join(f"{d}/br", "branches-r9.json"), sk)
    tie = choose(os.path.join(f"{d}/br", "branches-r9.json"), [sk[0], sk[0]])
    res = {"branches": [(b["i"], b["name"], len(s["passes"])) for b, s in zip(M["branches"], specs)], "shares_sum_to_1": shares_ok,
           "lessons_within_plan": lessons_ok, "distinct_specs": distinct, "flat_equal": flat_ok, "choose": ch, "tie_keeps_base": tie["winner"] == 0}
    real_ok = True                                       # read-only: on the live run's last plan, b0 must rebuild the planner's own passes
    live = os.path.join(C.TRIAL, "runtime/results/live-school")
    plans = sorted((int(x[1:]), x) for x in os.listdir(live) if x[1:].isdigit() and os.path.exists(f"{live}/{x}/plan-{x}.json")) if os.path.isdir(live) else []
    if plans:
        x = plans[-1][1]; P = json.load(open(f"{live}/{x}/plan-{x}.json"))
        if P["specs"].get("tier1") and os.path.exists(P["specs"]["tier1"]):
            Mr = emit(f"{live}/{x}/plan-{x}.json", 5, f"{d}/real")
            b0 = json.load(open(Mr["branches"][0]["spec"]))["passes"]; own = json.load(open(P["specs"]["tier1"]))["passes"]
            real_ok = b0 == own
            res["live_plan"] = {"plan": x, "b0_equals_planner_passes": real_ok, "branches": len(Mr["branches"]),
                                "passes_per_branch": [len(json.load(open(b["spec"]))["passes"]) for b in Mr["branches"]]}
    import shutil; shutil.rmtree(d, ignore_errors=True)
    if out: C.json_out(res, out)
    return shares_ok and lessons_ok and distinct and flat_ok and ch["winner"] == 1 and tie["winner"] == 0 and real_ok, res


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="c", required=True)
    e = sp.add_parser("emit"); e.add_argument("plan"); e.add_argument("k", type=int); e.add_argument("out")
    c = sp.add_parser("choose"); c.add_argument("meta"); c.add_argument("skills", nargs="+"); c.add_argument("--out")
    s = sp.add_parser("selftest"); s.add_argument("--out")
    a = ap.parse_args()
    if a.c == "emit": print(json.dumps(emit(a.plan, a.k, a.out)))
    elif a.c == "choose": print(json.dumps(choose(a.meta, a.skills, a.out)))
    else:
        ok, res = selftest(a.out); print(json.dumps(res)); print("PASS" if ok else "FAIL", "branches"); sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

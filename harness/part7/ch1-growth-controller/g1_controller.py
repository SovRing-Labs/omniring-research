#!/usr/bin/env python3
"""GROW-RUN-0 G1 gate — the controller from the frozen r12 state (runtime/results/growth-base/r12-elem), no training:
  1 GROW_GATE=1.0 plan: only stage-1 (pre-K) skills below 1.0 on the frontier + K level 1 as preview; nothing from elementary / middle
  2 a synthetic eval with every pre-K skill at 1.0 → stage passed (prek → k); grow_ctl keeps the core (r13-stage)
  3 one pre-K skill slips to 0.9 → the stage is pre-K again and that skill is back on the frontier
  4 after middle (synthetic: every skill through middle at 1.0), a WALL → mode params; `grown` → skills; a WALL within 6 rounds with no gain
    since the growth → mode generators
  5 GROW_GATE unset → the plan is byte-identical to the planner's output without this change (live-school default kept)
  g1_controller.py [--out DIR]   → results/grow/g1/g1.json"""
import json, os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); TT = os.path.dirname(os.path.dirname(HERE))
H = f"{TT}/harness"; CTL = f"{TT}/cloud/grow_ctl.py"
BASE = os.environ.get("GROW_BASE", "<workspace>/projects/thead-trial/runtime/results/growth-base/r12-elem")
sys.path.insert(0, H)


def run(args, env=None):
    e = dict(os.environ); e.pop("GROW_GATE", None); e.update(env or {})
    r = subprocess.run([sys.executable] + args, capture_output=True, text=True, env=e, cwd=H)
    if r.returncode: raise SystemExit(f"{args}: {r.stderr[-800:]}")
    return json.loads(r.stdout.strip().splitlines()[-1])


def main():
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else f"{TT}/tests/grow/results/g1"; os.makedirs(out, exist_ok=True)
    os.environ.pop("GROW_GATE", None); import school_graph as g
    N = g.nodes(); checks = {}
    with tempfile.TemporaryDirectory(prefix="grow-g1-") as T:
        st = f"{T}/state.json"; shutil.copyfile(f"{BASE}/school-state-r12.json", st); G = {"GROW_GATE": "1.0"}
        p = run(["school_graph.py", "plan", st, "13", f"{T}/p13"], G); pl = json.load(open(f"{T}/p13/plan-r13.json"))
        fr = pl["frontier"]; sch = {N[k]["school"] for k in fr}; pv = [k for k in pl["weights"] if k not in fr and N[k]["school"] == "k"]
        checks["1_frontier_prek_only"] = sch == {"prek"} and all(json.load(open(st))["score"].get(k, 0) < 1.0 for k in fr)
        checks["1_preview_k_level1"] = bool(pv) and all(N[k]["level"] == 1 for k in pv)
        s12 = json.load(open(st))["score"]                               # above stage 1 only REVIEW of skills already at 1.0 carries weight
        checks["1_above_stage_only_review"] = all(s12.get(k, 0) >= 1.0 for k in pl["weights"] if N[k]["school"] in ("elem", "bridge", "middle", "high"))
        R = g.GROW_MIN_ROWS or 300                                        # PAC rule: 1.0 on 24 rows proves nothing — must not pass
        ev = {"skill": {k: 1.0 for k, n in N.items() if n["school"] == "prek"}, "rows": {k: 24 for k, n in N.items() if n["school"] == "prek"}}
        json.dump(ev, open(f"{T}/ev12b.json", "w")); u = run(["school_graph.py", "update", st, "12", f"{T}/ev12b.json"], {**G, "GROW_EPS": "0.01"})
        checks["2a_pac_24_rows_not_enough"] = u["stage"] == "prek" and u["stages"]["prek"][0] == 0
        s0 = json.load(open(st)); ev = {"skill": {k: 1.0 for k, n in N.items() if n["school"] == "prek"}, "rows": {k: R for k, n in N.items() if n["school"] == "prek"}}
        json.dump(ev, open(f"{T}/ev13.json", "w")); u = run(["school_graph.py", "update", st, "13", f"{T}/ev13.json"], G)
        json.dump(u, open(f"{T}/u13.json", "w"))
        checks["2_stage_passed_prek_to_k"] = u["stage_passed"] and u["stage"] == "k" and u["stages"]["prek"][0] == u["stages"]["prek"][1]
        core = f"{T}/core"; shutil.copytree(BASE, core, copy_function=shutil.copyfile)
        runp = f"{T}/run"; c = run([CTL, "step", runp, "--round", "13", "--update", f"{T}/u13.json", "--core", core, "--tier", "test", "--secs", "600"])
        checks["2_keep_on_stage_pass"] = bool(c["keep"]) and os.path.exists(os.path.join(c["keep"], "MANIFEST.sha256")) and c["mode"] == "skills"
        k0 = next(k for k, n in N.items() if n["school"] == "prek"); json.dump({"skill": {k0: 0.9}, "rows": {k0: R}}, open(f"{T}/ev14.json", "w"))
        u = run(["school_graph.py", "update", st, "14", f"{T}/ev14.json"], G)
        run(["school_graph.py", "plan", st, "15", f"{T}/p15"], G); pl15 = json.load(open(f"{T}/p15/plan-r15.json"))
        checks["3_slip_returns"] = u["stage"] == "prek" and k0 in pl15["frontier"]
        ev = {"skill": {k: 1.0 for k, n in N.items() if n["school"] in ("prek", "k", "elem", "bridge", "middle")}, "rows": {k: R for k, n in N.items() if n["school"] in ("prek", "k", "elem", "bridge", "middle")}}
        json.dump(ev, open(f"{T}/ev16.json", "w")); u = run(["school_graph.py", "update", st, "16", f"{T}/ev16.json"], G)
        checks["4_middle_passed"] = u["stage"] == "high"
        modes = []
        for r in range(17, 21):                                       # flat rounds → WALL after WALL_ROUNDS
            json.dump({"skill": dict(json.load(open(st))["score"]), "rows": dict(json.load(open(st)).get("rows", {}))}, open(f"{T}/ev.json", "w")); u = run(["school_graph.py", "update", st, str(r), f"{T}/ev.json"], G)   # a flat round: every skill re-evaluated, same scores
            json.dump(u, open(f"{T}/u.json", "w")); modes.append(run([CTL, "step", runp, "--round", str(r), "--update", f"{T}/u.json", "--core", core, "--tier", "test", "--secs", "600"])["mode"])
        checks["4_wall_to_params"] = modes[-1] == "params"
        run([CTL, "grown", runp, "--round", "20", "--params-from", "6926912", "--params-to", "9000000", "--how", "test"])
        m2 = []
        for r in range(21, 25):
            json.dump({"skill": dict(json.load(open(st))["score"]), "rows": dict(json.load(open(st)).get("rows", {}))}, open(f"{T}/ev.json", "w")); u = run(["school_graph.py", "update", st, str(r), f"{T}/ev.json"], G)
            json.dump(u, open(f"{T}/u.json", "w")); m2.append(run([CTL, "step", runp, "--round", str(r), "--update", f"{T}/u.json", "--core", core, "--tier", "test", "--secs", "600"])["mode"])
        checks["4_grown_to_skills_then_generators"] = m2[0] == "skills" and m2[-1] == "generators"
        checks["4_keep_after_growth"] = any("grown" in k for k in json.load(open(f"{runp}/grow-ctl.json"))["keeps"])
        # 5 default unchanged: plan without GROW_GATE == the reference planner's output (main tree copy, same state)
        st2 = f"{T}/state2.json"; shutil.copyfile(f"{BASE}/school-state-r12.json", st2)
        run(["school_graph.py", "plan", st2, "13", f"{T}/d13"]); ref = "<workspace>/projects/thead-trial/harness/school_graph.py"
        r = subprocess.run([sys.executable, ref, "plan", st2, "13", f"{T}/r13"], capture_output=True, text=True, cwd=os.path.dirname(ref))
        rd = lambda d, f: open(f"{T}/{d}/{f}", "rb").read().replace(f"{T}/{d}/".encode(), b"OUT/")   # the plan names its own out dir
        same = all(rd("d13", f) == rd("r13", f) for f in os.listdir(f"{T}/r13"))
        checks["5_default_identical"] = r.returncode == 0 and same
        rep = json.loads(subprocess.run([sys.executable, CTL, "report", runp], capture_output=True, text=True).stdout)
        v = subprocess.run([sys.executable, CTL, "verify", runp], capture_output=True, text=True); vj = json.loads(v.stdout)
        checks["6_ledger_chain_verifies"] = v.returncode == 0 and vj["ok"] and vj["rows"] >= 9
        L_ = open(f"{runp}/ledger.jsonl").read().splitlines(); t_ = json.loads(L_[2]); t_["decision"]["next_mode"] = "tampered"; L_[2] = json.dumps(t_, sort_keys=True)
        open(f"{runp}/ledger.jsonl", "w").write("\n".join(L_) + "\n")
        v2 = subprocess.run([sys.executable, CTL, "verify", runp], capture_output=True, text=True)
        checks["6_tamper_detected"] = v2.returncode != 0
    rec = {"gate": "GROW-RUN-0 G1 controller (dry, from growth-base r12)", "checks": checks, "report": rep, "pass": all(checks.values())}
    json.dump(rec, open(f"{out}/g1.json", "w"), indent=1); print(json.dumps(rec, indent=1)); sys.exit(0 if rec["pass"] else 1)


if __name__ == "__main__":
    main()

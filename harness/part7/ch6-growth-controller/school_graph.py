#!/usr/bin/env python3
"""school_graph — the LIVE school (LIVE-SCHOOL-0, J 2026-10-08: "do r1-8 all at once and do a full run"; high school A→J stacked on it,
"2 stacks on 1"). Plan `<notes>/worker/claude/<plan>`; brainstorm `<notes>/THEAD/CURRICULUM-BRAINSTORM-2026-10-08.md`.

R1  skill graph: a node = (lesson, level); prerequisite edges seeded from the lesson design and school order (below); progress per node
    is recorded every round (rounds.jsonl) so the measured graph can be drawn from the run itself.
R2  live curriculum: every round compiles FRESH rows (new row seed) for exactly the frontier + review — no fixed 5× / 25× build.
R3  per-skill gates (held-out top-1 on the learnable classes ≥ GATE) + a sampler weighted by learning progress; mastered skills drop to
    spaced review (REVIEW share).
R5  difficulty axis = level (operation count per lesson); the held-out of each round also carries level+1 of the frontier (OOD).
High school: ordered rungs A→J (J 10-08 "in order … until its competent and moving up the rung"); a rung with no generator yet is listed
as UNBUILT and skipped, never faked.

  python3 school_graph.py plan  <state.json> <round> <out_dir>   → round specs (tier-1 and / or middle) + the round's held-out / doing specs
  python3 school_graph.py update <state.json> <round> <eval.json> → gates + progress; prints the frontier, mastered count, WALL flag
  python3 school_graph.py show  [state.json]"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = 0.85; MIN_SHARE = 0.08; REVIEW = 0.2; LP_FLOOR = 0.25; WALL_ROUNDS = 3; WALL_EPS = 0.01
GENS = ["arith.mul", "arith.mrc_compare", "logic.chain", "graph.path", "sat.dpll", "mind.revise", "struct.pushdown", "units.dimension",
        "calendar.crt", "code.debug", "science.bioreactor", "mind.tom", "search.astar", "causal.dag", "arith.mul_rns", "arith.mrc_plate",
        "sat.trit", "graph.group_walk", "graph.group", "calendar.ring_euclid", "calendar.clock", "science.factorial", "search.wave",
        "mind.tom_mask", "numth.prime_trial", "numth.prime"]
# levels 6–8 the generator can make today (checked 10-08: reason-gen gen --level 6/7/8)
HS_DEPTH_FAIL = {6: {"numth.prime"}, 7: {"mind.revise", "numth.prime"}, 8: {"logic.chain", "mind.revise", "numth.prime"}}

# ── R1: the graph (lesson → (levels, prerequisites at level 1, format)) — design-seeded edges ────────────────────────────────────────
PREK = [("pk.echo", []), ("pk.ping", ["pk.echo"]), ("pk.hold", ["pk.echo"]), ("pk.commit", ["pk.hold"]), ("pk.flush", ["pk.hold"]),
        ("pk.give", ["pk.ping"]), ("pk.tape", ["pk.commit"]), ("pk.meet", ["pk.echo"]), ("pk.meet_fix", ["pk.meet"]),
        ("pk.press", ["pk.commit"]), ("pk.mix", ["pk.flush", "pk.give", "pk.tape"]), ("pk.babble", ["pk.ping"]),
        ("pk.predict", ["pk.babble", "pk.meet"]), ("pk.predict_fix", ["pk.predict", "pk.meet_fix"]), ("pk.goal", ["pk.babble"]),
        ("pk.same", ["pk.babble"]), ("pk.rot", ["pk.echo", "pk.commit"])]
KIND = [("k.store", ["pk.commit", "pk.press"]), ("k.transport", ["pk.give"]), ("k.meet", ["pk.meet"]), ("k.meet_fix", ["k.meet", "pk.meet_fix"]),
        ("k.tape", ["pk.tape", "k.store"]), ("k.review", ["k.store"]), ("k.rot", ["pk.rot", "k.store"])]
ELEM = [("e.search", ["k.meet"]), ("e.chord", ["k.store", "k.transport", "k.meet"]), ("e.tape_act", ["k.tape"]), ("e.press", ["k.store"])]
BRIDGE = [("br.echo", ["e.chord"]), ("br.ping", ["br.echo"]), ("br.meet", ["br.echo", "k.meet"]), ("br.babble", ["br.echo", "pk.babble"]),
          ("br.goal", ["br.babble", "pk.goal"])]
HS = [("hs.A", "composition — 2–3 of the 26 chained (minted compose.* PROPOSED: admission = J / mint gate)", False),
      ("hs.B", "depth — the 26 at levels 6–8", True),
      ("hs.C", "study at full strength — find the flaw, [revise], retry (middle recovery rows + R7 lessons)", False),
      ("hs.D", "the code alphabet — equations → words → programs (CODE-ABC, doctor-verified)", False),
      ("hs.E", "dock engines as tools (arcd; J's call per VOCAB 'the 26')", False),
      ("hs.F", "projects — plan → execute → verify → report", False), ("hs.G", "shards — retrieve, cite, use", False),
      ("hs.H", "authoring — write a new problem + its verified answer", False), ("hs.I", "invent a word — reusable macro", False),
      ("hs.J", "calibrated abstention — honest unknown (reason-gen ABSTAIN rows at a higher share)", False)]


def nodes():
    """every skill: key "lesson@level" → {school, lesson, level, prereq: [keys], fmt, builder}"""
    N = {}
    def add(school, lesson, levels, pre, fmt, builder="tier1"):
        for lv in levels:
            req = [f"{p}@1" for p in pre] if lv == levels[0] else [f"{lesson}@{lv - 1}"]
            N[f"{lesson}@{lv}"] = {"school": school, "lesson": lesson, "level": lv, "prereq": req, "fmt": fmt, "builder": builder}
    for l, pre in PREK: add("prek", l, range(1, 6), pre, "a")
    for l, pre in KIND: add("k", l, range(1, 6), pre, "b")
    for g in GENS: add("k", f"env.{g}", [1], ["k.store", "k.transport"], "b")
    for l, pre in ELEM: add("elem", l, range(1, 6), pre, "b")
    for l, pre in BRIDGE: add("bridge", l, range(1, 4), pre, "b")
    for g in GENS:
        add("middle", f"mid.{g}", range(1, 6), [b[0] for b in BRIDGE] + [f"env.{g}"], "J", "middle")
    prev = [f"mid.{g}@5" for g in GENS]
    for rung, what, built in HS:
        if rung == "hs.B":
            for g in GENS:
                lv = [l for l in (6, 7, 8) if g not in HS_DEPTH_FAIL[l]]
                if lv: add("high", f"hs.B.{g}", lv, [f"mid.{g}"], "J", "middle")
                for k, n in N.items():
                    if n["lesson"] == f"hs.B.{g}" and n["level"] == lv[0]: n["prereq"] = [f"mid.{g}@5"]
        else:
            N[f"{rung}@1"] = {"school": "high", "lesson": rung, "level": 1, "prereq": list(prev), "fmt": "J",
                             "builder": "middle" if built else "UNBUILT", "what": what}
    return N


def load(state_path):
    return json.load(open(state_path)) if os.path.exists(state_path) else {"score": {}, "hist": {}, "mastered": [], "rounds": 0, "wall": 0}


# GROW-RUN-0 (J 10-09: "only passes staage when it masters every skill in that tier to 100"): GROW_GATE set → stage mode. A stage passes when
# EVERY built skill of it holds a CURRENT held-out score ≥ GROW_GATE (not sticky: a slipped skill returns to the frontier); later stages stay
# locked until then; the next stage's level 1 is previewed at GROW_PREVIEW (J 10-08 circular rule); prerequisites inside a stage keep GATE.
GROW_GATE = float(os.environ["GROW_GATE"]) if os.environ.get("GROW_GATE") else None
TAG = os.environ.get("LIVE_TAG", "live")   # build / spec name prefix: a growth run (LIVE_TAG=grow-…) never collides with the live school's builds
STAGES = [("prek", ("prek",)), ("k", ("k",)), ("elem", ("elem", "bridge")), ("middle", ("middle",)), ("high", ("high",))]
GROW_PREVIEW = float(os.environ.get("GROW_PREVIEW", "0.1"))
# PAC sample size (PROVENANCE-CONCEPTS-2026-10-09 #2): zero errors on n INDEPENDENT rows bounds the true error at ln(1/δ)/n — a skill is at the
# gate only with its score ≥ GROW_GATE on at least ⌈ln(1/δ)/ε⌉ held-out rows (default ε 1 %, δ 5 % → 300); GROW_EPS=0 turns the rule off
GROW_EPS, GROW_DELTA = float(os.environ.get("GROW_EPS", "0.01")), float(os.environ.get("GROW_DELTA", "0.05"))
GROW_MIN_ROWS = int(-(-__import__("math").log(1 / GROW_DELTA) // GROW_EPS)) if GROW_EPS > 0 else 0
GROW_HO_ROW_TOK = int(os.environ.get("GROW_HO_ROW_TOK", "64"))   # held-out sizing: tokens per row (estimate) × rows needed × 1.25


def stage_of(N, school):
    return next(i for i, (_, g) in enumerate(STAGES) if school in g)


def at_gate(N, st):
    """GROW mode: the skills whose CURRENT score is at the gate"""
    return [k for k in N if st["score"].get(k, 0.0) >= GROW_GATE and st.get("rows", {}).get(k, 0) >= GROW_MIN_ROWS]


def stage_now(N, st):
    """GROW mode: (index of the first stage not passed, per-stage [at gate, built]) — len(STAGES) = every stage passed"""
    ag = set(at_gate(N, st)); prog = []
    for i, (_, g) in enumerate(STAGES):
        ks = [k for k, n in N.items() if n["school"] in g and n["builder"] != "UNBUILT"]; prog.append([sum(k in ag for k in ks), len(ks)])
    cur = next((i for i, (a, b) in enumerate(prog) if b and a < b), len(STAGES))
    return cur, prog


MIDDLE_AFTER_ELEM = True   # J 10-08 (after the r9 collapse: middle harnesses merged with tier-1 wiped tier-1): "no middle until elementary is done"


def unlocked(N, st, k):
    if GROW_GATE is not None:                                         # stage mode: no skill above the current stage
        cur, _ = stage_now(N, st)
        if stage_of(N, N[k]["school"]) > cur: return False
        return all(p in st["mastered"] or st["score"].get(p, 0.0) >= GROW_GATE for p in N[k]["prereq"])
    if MIDDLE_AFTER_ELEM and os.environ.get("SCHOOL_MIDDLE") != "1" and N[k]["school"] in ("middle", "high") and not all(j in st["mastered"] for j, n in N.items() if n["school"] == "elem"):
        return False
    return all(p in st["mastered"] for p in N[k]["prereq"])


def frontier(N, st):
    if GROW_GATE is not None:                                         # stage mode: every unlocked skill below the gate, slipped ones included
        return [k for k, n in N.items() if st["score"].get(k, 0.0) < GROW_GATE and n["builder"] != "UNBUILT" and unlocked(N, st, k)]
    return [k for k, n in N.items() if k not in st["mastered"] and n["builder"] != "UNBUILT" and unlocked(N, st, k)]


def preview(N, st):
    """GROW mode: level 1 of the next stage's skills (circular: the last pass previews the next school)"""
    cur, _ = stage_now(N, st)
    if cur + 1 >= len(STAGES): return []
    g = STAGES[cur + 1][1]
    return [k for k, n in N.items() if n["school"] in g and n["level"] == 1 and n["builder"] != "UNBUILT"]


def tier1_spec(N, t1, rnd, sid, tokens, why):
    """a tier-1 spec from {skill: weight} (same pass rules as plan()): one pass per level, small passes merged (MIN_SHARE)"""
    by_lv = {}
    for k, v in t1.items(): by_lv.setdefault(N[k]["level"], {})[N[k]["lesson"]] = round(v, 4)
    tot = sum(t1.values()) or 1.0; passes = []
    for lv in sorted(by_lv):
        les = by_lv[lv]
        passes.append({"name": f"round {rnd} · {sid} · level {lv}", "share": round(sum(les.values()) / tot, 4), "levels": [lv], "format": "b",
                       "format_of": {l: ("a" if l.startswith("pk.") else "b") for l in les}, "lessons": les})
    merged = []
    for ps in passes:
        if merged and (ps["share"] < MIN_SHARE or merged[-1]["share"] < MIN_SHARE):
            m = merged[-1]; m["levels"] = sorted(set(m["levels"]) | set(ps["levels"])); m["share"] = round(m["share"] + ps["share"], 4)
            for l, v in ps["lessons"].items(): m["lessons"][l] = round(m["lessons"].get(l, 0) + v, 4)
            m["format_of"].update(ps["format_of"])
        else: merged.append(ps)
    return {"id": sid, "status": "approved", "owner": "J", "school": "live", "role": "training", "ctx": 512,
            "tokenizer": "~/gpurun-out-1003/tokenizer-glyph-fix/tokenizer.json", "tokens": tokens, "parent": f"live round {rnd - 1}",
            "approved_by": "J 2026-10-08: \"every curriculum should be circular and build on all previous layers\"", "why": why, "passes": merged}


def plan(state_path, rnd, out, tier1_tokens=1_000_000, mid_tokens=1_000_000):
    """R2 + R3: the round's specs — frontier weighted by learning progress, REVIEW share of mastered skills, held-out with level+1 (R5)"""
    N = nodes(); st = load(state_path); fr = frontier(N, st)
    def lp(k):
        h = st["hist"].get(k, [])
        return max(LP_FLOOR, abs(h[-1] - h[-2]) * 10) if len(h) >= 2 else 1.0
    w = {k: lp(k) for k in fr}
    rev = [k for k in (at_gate(N, st) if GROW_GATE is not None else st["mastered"]) if k in N and N[k]["builder"] != "UNBUILT"]
    if rev and w:
        rv = float(os.environ.get("SCHOOL_REVIEW", REVIEW))   # round guard retry raises the review share (J 10-08: fall back and redo)
        tot = sum(w.values()); rw = rv / (1 - rv) * tot / len(rev)
        for k in rev: w[k] = w.get(k, 0) + rw
    if os.environ.get("RAMKIT_REPLAY"):   # RAM-KIT #6 forgetting watch (ramkit-hooks.sh ramkit_watch): slipped mastered skills get replay weight
        sys.path.insert(0, os.environ.get("RAMKIT") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ramkit")); import forget_watch
        w = forget_watch.apply(w, os.environ["RAMKIT_REPLAY"], N)
    if GROW_GATE is not None and w and float(os.environ.get("GROW_GATES_W", "1.0")) > 0:   # min-cut weighting (PROVENANCE-CONCEPTS #4, g4 cuts):
        gates = {k: 0 for k in N}                                     # a frontier skill weighs 1 + gw·(skills it gates / most gated) — the
        kids = {}                                                     # stage waits on its cut skills (pre-K: pk.echo@1 gates all 84 others)
        for k_, n_ in N.items():
            for p_ in n_["prereq"]: kids.setdefault(p_, []).append(k_)
        def down(k_, seen):
            for c_ in kids.get(k_, []):
                if c_ not in seen: seen.add(c_); down(c_, seen)
            return seen
        for k_ in w: gates[k_] = len(down(k_, set()))
        mg = max([gates[k_] for k_ in w] + [1]); gw_ = float(os.environ.get("GROW_GATES_W", "1.0"))
        for k_ in list(w): w[k_] *= 1.0 + gw_ * gates[k_] / mg
    if GROW_GATE is not None and w:                                   # stage mode: the next stage's level 1 at GROW_PREVIEW of the round
        pv = [k for k in preview(N, st) if k not in w]
        if pv:
            tot = sum(w.values()); pw = GROW_PREVIEW / (1 - GROW_PREVIEW) * tot / len(pv)
            for k in pv: w[k] = pw
    os.makedirs(out, exist_ok=True); made = {}
    t1 = {k: v for k, v in w.items() if N[k]["builder"] == "tier1"}; md = {k: v for k, v in w.items() if N[k]["builder"] == "middle"}
    if t1:
        by_lv = {}
        for k, v in t1.items(): by_lv.setdefault(N[k]["level"], {})[N[k]["lesson"]] = round(v, 4)
        tot = sum(t1.values()); passes = []
        for lv in sorted(by_lv):
            les = by_lv[lv]; fmt_of = {l: ("a" if l.startswith("pk.") else "b") for l in les}
            passes.append({"name": f"round {rnd} · level {lv}", "share": round(sum(les.values()) / tot, 4), "levels": [lv], "format": "b",
                           "format_of": fmt_of, "lessons": les})
        merged = []                                                   # a pass under MIN_SHARE joins its neighbour (windows need room: 512-token rows)
        for ps in passes:
            if merged and (ps["share"] < MIN_SHARE or merged[-1]["share"] < MIN_SHARE):
                m = merged[-1]; m["levels"] = sorted(set(m["levels"]) | set(ps["levels"])); m["share"] = round(m["share"] + ps["share"], 4)
                for l, v in ps["lessons"].items(): m["lessons"][l] = round(m["lessons"].get(l, 0) + v, 4)
                m["format_of"].update(ps["format_of"]); m["name"] = f"round {rnd} · levels {m['levels'][0]}–{m['levels'][-1]}"
            else: merged.append(ps)
        passes = merged
        spec = {"id": f"{TAG}-r{rnd}", "status": "approved", "owner": "J", "school": "live", "role": "training", "ctx": 512,
                "tokenizer": "~/gpurun-out-1003/tokenizer-glyph-fix/tokenizer.json", "tokens": tier1_tokens, "parent": f"live round {rnd - 1}",
                "approved_by": "J 2026-10-08: \"do r1-8 all at once and do a full run\" (LIVE-SCHOOL-0)",
                "why": f"live round {rnd}: frontier {len(fr)} skills (learning-progress weighted) + {len(rev)} in review", "passes": passes}
        p = os.path.join(out, f"{TAG}-r{rnd}.json"); json.dump(spec, open(p, "w"), indent=1); made["tier1"] = p
        # held-out: the same skills + level+1 of each frontier lesson (R5 OOD), small
        ho = json.loads(json.dumps(spec)); ho["id"] = f"{TAG}-r{rnd}-ho"; ho["tokens"] = 120000
        if GROW_GATE is not None:                                     # stage mode: every skill an EQUAL share, enough rows for the PAC bound
            for ps in ho["passes"]:
                ps["lessons"] = {l_: 1.0 for l_ in ps["lessons"]}; ps["share"] = float(len(ps["lessons"]))
            tot_ = sum(ps["share"] for ps in ho["passes"]) or 1.0
            for ps in ho["passes"]: ps["share"] = round(ps["share"] / tot_, 4)
            n_sk = sum(len(ps["lessons"]) for ps in ho["passes"]) * 2   # each lesson at its level and level + 1
            ho["tokens"] = int(max(120000, GROW_MIN_ROWS * n_sk * GROW_HO_ROW_TOK * 1.25)); ho["why"] = ho.get("why", "") + f" · PAC: ≥ {GROW_MIN_ROWS} rows per skill"
        for ps in ho["passes"]: ps["levels"] = [ps["levels"][0]] + ([ps["levels"][0] + 1] if ps["levels"][0] < 5 else [])
        p = os.path.join(out, f"{TAG}-r{rnd}-ho.json"); json.dump(ho, open(p, "w"), indent=1); made["tier1_heldout"] = p
    if md:
        base = json.load(open(os.path.expanduser("<home>/ai-stack/<notes>/GPU-RUN/curricula/seed-v4-short.json")))
        by_lv = {}
        for k, v in md.items():
            g = N[k]["lesson"].replace("hs.B.", "").replace("mid.", ""); by_lv.setdefault(N[k]["level"], {})[g] = v
        tot = sum(md.values()); phases = []
        for lv in sorted(by_lv):
            label = 1.0 if lv <= 2 else 0.5 if lv == 3 else 0.15 if lv == 4 else 0.0
            phases.append({"name": f"round {rnd} · level {lv}", "share": round(sum(by_lv[lv].values()) / tot, 4), "levels": [lv],
                           "label": label, "modes": {"beats_inverse": 1.0}, "domains": sorted(by_lv[lv])})
        mp = []                                                       # same rule as tier-1: no phase under MIN_SHARE
        for ph in phases:
            lvs = set(mp[-1]["levels"]) | set(ph["levels"]) if mp else set(); dms = set(mp[-1]["domains"]) | set(ph["domains"]) if mp else set()
            ok = not any(d in HS_DEPTH_FAIL.get(L, ()) for L in lvs for d in dms)   # r10 10-08: a merge put numth.prime@5 in a level-6 phase → KeyError 6
            if mp and ok and (ph["share"] < MIN_SHARE or mp[-1]["share"] < MIN_SHARE):
                m = mp[-1]; m["levels"] = sorted(set(m["levels"]) | set(ph["levels"])); m["share"] = round(m["share"] + ph["share"], 4)
                m["domains"] = sorted(set(m["domains"]) | set(ph["domains"])); m["name"] = f"round {rnd} · levels {m['levels'][0]}–{m['levels'][-1]}"
            else: mp.append(ph)
        phases = mp
        spec = dict(base); spec.update({"id": f"{TAG}-mid-r{rnd}", "tokens": mid_tokens, "phases": phases,   # top-level domains stay the FULL 26 in order: plate index = generator index (K 31)
                                        "approved_by": "J 2026-10-08: \"do r1-8 all at once and do a full run\" (LIVE-SCHOOL-0)",
                                        "why": f"live round {rnd}: middle / high-school depth frontier"})
        p = os.path.join(out, f"{TAG}-mid-r{rnd}.json"); json.dump(spec, open(p, "w"), indent=1); made["middle"] = p
    # CIRCULAR (J 10-08; TIER1-SYMBOL-SCHOOL-SPEC §8): every build revisits all previous layers and previews the next.
    #   tier1_review  = every mastered tier-1 skill (spaced review) — spliced FIRST into each middle harness's build (pass 1 = the schools before)
    #   middle_preview = middle level 1 over all 26 generators — spliced LAST into each tier-1 harness's build (the next school's format)
    rv = {k: 1.0 for k in (at_gate(N, st) if GROW_GATE is not None else st["mastered"]) if k in N and N[k]["builder"] == "tier1"}
    if md and rv:
        spec = tier1_spec(N, rv, rnd, f"{TAG}-rev-r{rnd}", 300000, f"live round {rnd}: review of {len(rv)} mastered tier-1 skills (circular pass 1)")
        p = os.path.join(out, f"{TAG}-rev-r{rnd}.json"); json.dump(spec, open(p, "w"), indent=1); made["tier1_review"] = p
    base = json.load(open(os.path.expanduser("<home>/ai-stack/<notes>/GPU-RUN/curricula/seed-v4-short.json")))
    pre = dict(base); pre.update({"id": f"{TAG}-pre-r{rnd}", "tokens": 100000, "phases": [{"name": f"round {rnd} · middle preview · level 1", "share": 1.0,
          "levels": [1], "label": 1.0, "modes": {"beats_inverse": 1.0}, "domains": sorted(GENS)}],
          "approved_by": "J 2026-10-08: \"every curriculum should be circular and build on all previous layers\"", "why": f"live round {rnd}: next-school preview"})
    p = os.path.join(out, f"{TAG}-pre-r{rnd}.json"); json.dump(pre, open(p, "w"), indent=1); made["middle_preview"] = p
    unbuilt = [k for k, n in N.items() if n["builder"] == "UNBUILT"]
    json.dump({"round": rnd, "frontier": fr, "weights": w, "specs": made, "unbuilt": unbuilt}, open(os.path.join(out, f"plan-r{rnd}.json"), "w"), indent=1)
    print(json.dumps({"round": rnd, "frontier": len(fr), "review": len(rev), "specs": made, "unbuilt_rungs": unbuilt}))


def update(state_path, rnd, eval_path):
    """R3 gates: eval = {"skill": {"lesson@level": top1, …}} (skill_eval.py); history per skill; WALL = mastered count flat for K rounds"""
    N = nodes(); st = load(state_path); evf = json.load(open(eval_path)); ev = evf["skill"]; evr = evf.get("rows")
    before = len(st["mastered"]) if GROW_GATE is None else len(at_gate(N, st)); stage0 = stage_now(N, st)[0] if GROW_GATE is not None else None
    for k, v in ev.items():
        st["score"][k] = v; st["hist"].setdefault(k, []).append(v)
        if evr is not None: st.setdefault("rows", {})[k] = evr.get(k, 0)
        if v >= GATE and k in N and k not in st["mastered"]: st["mastered"].append(k)
    gained = (len(st["mastered"]) if GROW_GATE is None else len(at_gate(N, st))) - before
    best = max((st["hist"][k][-1] - st["hist"][k][-2] for k in st["hist"] if len(st["hist"][k]) >= 2), default=1.0)
    st["wall"] = st["wall"] + 1 if gained == 0 and best < WALL_EPS else 0
    st["rounds"] = rnd; json.dump(st, open(state_path, "w"), indent=1)
    fr = frontier(N, st)
    row = {"round": rnd, "mastered": len(st["mastered"]), "gained": gained, "frontier": len(fr), "wall_rounds": st["wall"],
           "WALL": st["wall"] >= WALL_ROUNDS, "top_gain": round(best, 3)}
    if GROW_GATE is not None:                                         # stage mode: where the run stands at the gate
        cur, prog = stage_now(N, st)
        row.update({"gate": GROW_GATE, "min_rows": GROW_MIN_ROWS, "at_gate": len(at_gate(N, st)), "stage": STAGES[cur][0] if cur < len(STAGES) else "done",
                    "stage_passed": cur > stage0, "stages": {STAGES[i][0]: prog[i] for i in range(len(STAGES))}})
    print(json.dumps(row))


def show(state_path=None):
    N = nodes(); st = load(state_path) if state_path else load("/nonexistent")
    by = {}
    for k, n in N.items(): by.setdefault(n["school"], []).append(k)
    for s, ks in by.items(): print(f"{s:7s} {len(ks):4d} skills · mastered {sum(k in st['mastered'] for k in ks)}")
    print("frontier now:", frontier(N, st)[:12], "…" if len(frontier(N, st)) > 12 else "")
    print("UNBUILT rungs:", [k for k, n in N.items() if n["builder"] == "UNBUILT"])


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "plan": plan(sys.argv[2], int(sys.argv[3]), sys.argv[4])
    elif c == "update": update(sys.argv[2], int(sys.argv[3]), sys.argv[4])
    else: show(sys.argv[2] if len(sys.argv) > 2 else None)

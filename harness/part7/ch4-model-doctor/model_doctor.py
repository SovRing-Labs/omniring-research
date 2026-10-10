"""model_doctor.py — READY Y5 (J 2026-10-07: the doctor core's census → blame → cluster, applied to the model). Reads a run's journal
(+ the doing build it decoded from) and blames every doing / retry attempt with ONE cause, then clusters by (generator, cause, beat) and
ranks by blast radius (attempts, written tokens). The oracle is the generator's own gold trace (the role Chrome plays for the doctor).
Causes, first match wins:
  solved_own · solved_assisted (solved with a harness consult at the answer) · runaway (loop guard stopped it) · cap (ran to the cap
  without the answer marker) · no_call (call build: reached the answer without its ◈g) · slip@<beat> (left the solver's path: the beat
  line where the first divergence sits, from the gold trace) · wrong_answer (answered, not the generator's answer) · no_answer.
Usage: python3 model_doctor.py <run_dir> [--build <doing_build>] [--top 25] → <run_dir>/model_doctor.json + printed table."""
import argparse
import collections
import json
import os

import numpy as np


def gold_lines(build, man, nf, cache, level, start):
    key = (level, start)
    if key in cache: return cache[key]
    if level not in cache.setdefault("_rows", {}):
        cache["_rows"][level] = {int(r[0]): r for r in np.fromfile(os.path.join(build, f"rows_{level}.u32"), dtype="<u4").reshape(-1, nf)}
        cache.setdefault("_tok", {})[level] = np.fromfile(os.path.join(build, man["phases"][level]["file"]), dtype="<u2")
    r = cache["_rows"][level].get(start)
    if r is None: cache[key] = None; return None
    inv = r[4] in (3, 6); pe = int(r[7] if inv else r[6]); cont = cache["_tok"][level][pe:int(r[3])].tolist()
    cache[key] = cont; return cont


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("run"); ap.add_argument("--build"); ap.add_argument("--top", type=int, default=25)
    a = ap.parse_args()
    st = json.load(open(os.path.join(a.run, "state.json"))); cfg = st["config"]
    build = a.build or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runtime", cfg["doing"]))
    man = json.load(open(os.path.join(build, "manifest.json"))); nf = len(man["rows_sidecar"]["fields"]); nl = man["token_ids"]["newline"][0]
    tok = None
    try:
        from tokenizers import Tokenizer
        tok = Tokenizer.from_file(json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tier1_symbols.json")))["tokenizer"])
    except Exception:
        pass
    cap = cfg.get("do_cap", 320); call_build = "call" in man; cache = {}
    rows = [json.loads(l) for l in open(os.path.join(a.run, "journal.jsonl"))]
    blamed = []
    for d in rows:
        if d.get("stage") not in ("doing", "retry"): continue
        own = d.get("own", d["solved"] and d.get("tool", {}).get("consulted_at_answer", 0) == 0)
        if d["solved"]: cause = "solved_own" if own else "solved_assisted"
        elif d.get("runaway"): cause = "runaway"
        elif not d["answered"] and d["written"] >= cap: cause = "cap"
        elif call_build and d["answered"] and not d.get("called"): cause = "no_call"
        elif d.get("first_divergence") is not None and not d["answered"]:
            cont = gold_lines(build, man, nf, cache, d["level"], d["start"]); beat = "?"
            if cont is not None:
                div = d["first_divergence"]; line_start = max([0] + [i + 1 for i in range(min(div, len(cont))) if cont[i] == nl])
                if tok is not None and line_start + 1 < len(cont): beat = tok.decode(cont[line_start:line_start + 2]).strip()[:6] or "?"
            cause = f"slip@{beat}"
        elif d["answered"]: cause = "wrong_answer"
        else: cause = "no_answer"
        blamed.append({"domain": d["domain"], "level": d["level"], "stage": d["stage"], "mode": d.get("mode"), "cause": cause,
                       "written": d["written"], "first_divergence": d.get("first_divergence")})
    fam = collections.defaultdict(lambda: {"attempts": 0, "tokens": 0})
    for b in blamed:
        f = fam[(b["domain"], b["cause"])]; f["attempts"] += 1; f["tokens"] += b["written"]
    by_cause = collections.Counter(b["cause"].split("@")[0] for b in blamed)
    ranked = sorted(([k[0], k[1], v["attempts"], v["tokens"]] for k, v in fam.items() if not k[1].startswith("solved")), key=lambda x: (-x[2], -x[3]))
    out = {"run": a.run, "build": build, "call_build": call_build, "attempts": len(blamed), "by_cause": dict(by_cause),
           "families": [{"domain": d, "cause": c, "attempts": n, "tokens": t} for d, c, n, t in ranked], "blamed": blamed}
    json.dump(out, open(os.path.join(a.run, "model_doctor.json"), "w"), indent=1)
    print(f"MODEL-DOCTOR {a.run}: {len(blamed)} attempts · causes {dict(by_cause)}")
    for d, c, n, t in ranked[:a.top]: print(f"  {n:4d} attempts {t:6d} tok  {d:22s} {c}")


if __name__ == "__main__":
    main()

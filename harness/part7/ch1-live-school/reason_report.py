#!/usr/bin/env python3
"""Reasoning row per round (J 10-08 approved: "we're not grading it on answering, we're grading it on how well it's adjusting to its body").
Adds a "reasoning" field to round R's line in <L>/rounds.jsonl (one line per round, as before):
  doing_answered   mean DOING answered rate over the round's days (fresh problems, closed loop, verifier-checked)  — from the core's state.json
  retry_fixed      problems fixed on retry after study / problems retried (study layer: find the flaw, retry)
  novel_answers    share of the round's answers that appear NOWHERE whole in the training corpus (ramkit memdetect; 1 − full_match_rate)
  level_up         mean held-out score on skills one level ABOVE the lesson's highest mastered level (generalisation upward)
  tier1_at_gate    tier-1 skills ≥ 0.85 this round (from skill.json)
Sources: <L>/cores/r<R>/state.json (backed up by school-live after a guard pass) or --state; <L>/r<R>/memdetect.json; <L>/r<R>/skill.json; state.
  python3 reason_report.py <L> <R> [--state path] [--print]
"""
import argparse, json, os, re, statistics as stats

GATE = 0.85


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("L"); ap.add_argument("r", type=int); ap.add_argument("--state"); ap.add_argument("--print", action="store_true")
    a = ap.parse_args(); L, r = a.L, a.r
    out = {}
    sp = a.state or os.path.join(L, "cores", f"r{r}", "state.json")
    if os.path.exists(sp):
        days = json.load(open(sp)).get("days", [])
        ans = [d["answered_rate"] for d in days if isinstance(d.get("answered_rate"), (int, float))]
        fx = [d["retry"] for d in days if isinstance(d.get("retry"), list) and len(d["retry"]) == 2]
        if ans: out["doing_answered"] = round(stats.mean(ans), 3)
        if fx and sum(t for _, t in fx): out["retry_fixed"] = round(sum(f for f, _ in fx) / sum(t for _, t in fx), 3)
    mp = os.path.join(L, f"r{r}", "memdetect.json")
    if os.path.exists(mp):
        s = json.load(open(mp)).get("summary", {})
        if "full_match_rate" in s: out["novel_answers"] = round(1 - s["full_match_rate"], 3)
    kp = os.path.join(L, f"r{r}", "skill.json")
    if os.path.exists(kp):
        sk = json.load(open(kp))["skill"]
        out["tier1_at_gate"] = sum(v >= GATE for k, v in sk.items() if not k.startswith(("mid.", "hs.")))
        st = json.load(open(os.path.join(L, "state.json")))
        top = {}
        for k in st["mastered"]:
            les, lv = k.rsplit("@", 1); top[les] = max(top.get(les, 0), int(lv))
        up = [v for k, v in sk.items() if "@" in k and k.rsplit("@", 1)[0] in top and int(k.rsplit("@", 1)[1]) == top[k.rsplit("@", 1)[0]] + 1]
        if up: out["level_up"] = round(stats.mean(up), 3); out["level_up_n"] = len(up)
    rp = os.path.join(L, "rounds.jsonl")
    rows = [json.loads(l) for l in open(rp) if l.strip()]
    for row in rows:
        if row.get("round") == r: row["reasoning"] = out
    tmp = rp + ".tmp"; open(tmp, "w").write("".join(json.dumps(x) + "\n" for x in rows)); os.replace(tmp, rp)
    print(json.dumps({"round": r, "reasoning": out}))


if __name__ == "__main__":
    main()

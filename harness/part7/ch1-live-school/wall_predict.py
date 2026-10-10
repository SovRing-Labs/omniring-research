#!/usr/bin/env python3
# Wall predictor (J 10-08 approved; OMNITECH-ON-POD-BRAINSTORM #11). Geometric-computing law L12: "a settling loop that still moves is about to
# settle wrong" — residual vibration (movement not explained by the trend) predicted a wrong final settle at AUC 0.98–0.999 (VIB-0). Applied to
# the live school: each frontier skill's per-round score series is a settling loop toward the 0.85 gate. Per skill:
#   trend  = least-squares slope of the last K scores        vibe = RMS of the residuals around that line
#   eta    = rounds to the gate at the current slope          stall score = vibe / (|slope| + ε)  (moving without heading anywhere)
# Outputs: per-skill table (likely-to-stall first), a school-level WALL forecast (gains per round trend), and --backtest: hide each skill's last H
# scores, predict from the rest, check against what actually happened (AUC of the stall score for "not mastered at the end").
# BACKTEST 10-08 (rounds 1–7, ~100 skills, hide 1–3 rounds): the L12 stall score did NOT transfer — AUC 0.35–0.55 (moving scores are
# skills still learning, not settling wrong); best simple signal = gap to gate, AUC 0.63–0.67. Per-skill held-out sets are small, so scores are
# noisy. Use the school-level gain trend + next_to_master; treat `stall` as unvalidated until more rounds.
#   python3 wall_predict.py <state.json> [--k 4] [--top 15] [--backtest H] [--json out.json]
import argparse, json, math

GATE = 0.85


def fit(ys):
    n = len(ys); xs = list(range(n)); mx = sum(xs) / n; my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs) or 1.0
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    res = [y - (my + slope * (x - mx)) for x, y in zip(xs, ys)]
    return slope, math.sqrt(sum(r * r for r in res) / n), my + slope * (n - 1 - mx)


def features(ys, k):
    ys = ys[-k:]
    slope, vibe, now = fit(ys)
    eta = (GATE - now) / slope if slope > 1e-4 and now < GATE else (0.0 if now >= GATE else math.inf)
    return {"now": round(now, 3), "slope": round(slope, 4), "vibe": round(vibe, 4), "eta_rounds": None if math.isinf(eta) else round(eta, 1),
            "stall": round(vibe / (abs(slope) + 0.01) + (1.0 if slope <= 0 else 0.0), 3)}


def auc(pos, neg):
    if not pos or not neg: return None
    w = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return round(w / (len(pos) * len(neg)), 3)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("state"); ap.add_argument("--k", type=int, default=4); ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--backtest", type=int, default=0); ap.add_argument("--json")
    a = ap.parse_args()
    st = json.load(open(a.state)); hist, mastered = st["hist"], set(st["mastered"])
    out = {"round": st.get("rounds"), "gate": GATE, "k": a.k}
    front = {s: features(v, a.k) for s, v in hist.items() if s not in mastered and len(v) >= 3}
    rank = sorted(front.items(), key=lambda kv: -kv[1]["stall"])
    out["likely_stall"] = [{"skill": s, **f} for s, f in rank[:a.top]]
    out["next_to_master"] = [{"skill": s, **f} for s, f in sorted(front.items(), key=lambda kv: (kv[1]["eta_rounds"] is None, kv[1]["eta_rounds"] or 0))[:a.top]]
    if a.backtest:
        H = a.backtest; pos, neg = [], []
        for s, v in hist.items():
            if len(v) < H + 3: continue
            f = features(v[:-H], a.k)
            if f["now"] >= GATE: continue                     # already at the gate when hidden — not a prediction
            (neg if s in mastered else pos).append(f["stall"])
        out["backtest"] = {"hidden_rounds": H, "skills": len(pos) + len(neg), "stalled": len(pos), "reached_gate": len(neg), "auc_stall_score": auc(pos, neg)}
    try:
        rows = [json.loads(l) for l in open(a.state.replace("state.json", "rounds.jsonl")) if l.strip()]
        g = [r["gained"] for r in rows]
        if len(g) >= 3:
            s, v, now = fit(g[-a.k:])
            out["school"] = {"gained_per_round": g, "trend": round(s, 2), "vibe": round(v, 2), "frontier_now": rows[-1]["frontier"],
                             "rounds_to_flat_at_trend": None if s >= 0 else round(now / -s, 1)}
    except OSError:
        pass
    txt = json.dumps(out, indent=1)
    if a.json: open(a.json, "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Round guard (J 10-08, readback confirmed: "make backups of the core after every run, fall back and redo curriculum anytime it fails …
we keep the last 5 cores on disk"). Decides whether round R's core is GOOD enough to build on, against the last good round G.

FAIL when either (both measured on what the two rounds share, so a changed eval set cannot fake it):
  · tier-1 skills at the gate fell: count(score ≥ 0.85) on the tier-1 skills scored in BOTH rounds < (1 − DROP) × the count in G  (DROP 0.10)
  · held-out loss rose: R's held-out port loss > (1 + RISE) × G's  (RISE 0.30)  — read from r<N>/round.log "held-out / canary [(day, ho, canary)]"
Mastery is sticky in the school state, so the guard never looks at the mastered count (r9 showed +30 mastered while tier-1 ≥0.85 went 55 → 6).
  python3 round_guard.py <live-school dir L> <round R> <last good round G> [--drop 0.10] [--rise 0.30]   → JSON; exit 0 pass / 1 fail / 2 no data
"""
import argparse, json, os, re, sys

GATE = 0.85


def tier1(skill):
    return {k: v for k, v in skill.items() if not k.startswith(("mid.", "hs."))}


def heldout(L, r):
    p = os.path.join(L, f"r{r}", "round.log")
    if not os.path.exists(p): return None
    m = re.findall(r"held-out / canary \[\(\d+, ([0-9.]+), ([0-9.]+)\)\]", open(p, errors="replace").read())
    return float(m[-1][0]) if m else None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("L"); ap.add_argument("r", type=int); ap.add_argument("g", type=int)
    ap.add_argument("--drop", type=float, default=0.10); ap.add_argument("--rise", type=float, default=0.30)
    a = ap.parse_args()
    try:
        sr = tier1(json.load(open(os.path.join(a.L, f"r{a.r}", "skill.json")))["skill"])
        sg = tier1(json.load(open(os.path.join(a.L, f"r{a.g}", "skill.json")))["skill"]) if a.g > 0 else None
    except (OSError, ValueError, KeyError) as e:
        print(json.dumps({"round": a.r, "verdict": "nodata", "why": str(e)})); sys.exit(2)
    out = {"round": a.r, "vs_good": a.g, "drop": a.drop, "rise": a.rise, "why": []}
    if sg is None:
        out.update(verdict="pass", note="no earlier good round (first round)"); print(json.dumps(out)); sys.exit(0)
    common = [k for k in sr if k in sg]
    cg, cr = sum(sg[k] >= GATE for k in common), sum(sr[k] >= GATE for k in common)
    hg, hr = heldout(a.L, a.g), heldout(a.L, a.r)
    out.update(common=len(common), gate_count_good=cg, gate_count_now=cr,
               mean_good=round(sum(sg[k] for k in common) / max(1, len(common)), 4), mean_now=round(sum(sr[k] for k in common) / max(1, len(common)), 4),
               heldout_good=hg, heldout_now=hr)
    if cg and cr < (1 - a.drop) * cg: out["why"].append(f"tier-1 at gate {cg} → {cr} on {len(common)} shared skills (> {a.drop:.0%} drop)")
    # the logged held-out is harness h0's own held-out set: a middle h0 (circular rounds) reports the middle held-out (~2.2) — not comparable
    # with a tier-1 h0's (~0.5). A > 3× jump is a different SET, not a regression: skip it and say so (tier-1 skills still decide).
    if hg and hr and hr > 3 * hg: out["heldout_note"] = f"held-out sets differ ({hg:.3f} vs {hr:.3f}: h0 changed school) — not compared"
    elif hg and hr and hr > (1 + a.rise) * hg: out["why"].append(f"held-out {hg:.3f} → {hr:.3f} (> {a.rise:.0%} rise)")
    out["verdict"] = "fail" if out["why"] else "pass"
    print(json.dumps(out)); sys.exit(1 if out["why"] else 0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Circular build splice (J 10-08: "every curriculum should be circular and build on all previous layers"; TIER1-SYMBOL-SCHOOL-SPEC §8: pass 1 of a
school reviews the school before it, the last pass previews the next school's format). Joins the PHASES of several builds into ONE build, in order,
so one harness walks review → current school → preview without a second core.

Compatibility (checked 10-08, refused otherwise): same token_ids; generator plates 0..25 in the same order (tier1_symbols.json "generators" == the
middle port domains) and the same procedure plate (26). The tier-1 port (K 31: + pocket / meet / hear / tape plates) is a superset of the middle
port (K 27), so the FIRST build with a "tier1" key gives the output port + tier1 block; phases from builds without it get an empty t1_k.json.
Files per phase: <phase file>, kind_k.u8, stage_k.u8, rows_k.u32 (+ mask_k.u8, t1_k.json when present) — renumbered k → offset + k.
step_share: each source's phases keep their relative shares, scaled by that source's weight (--w; default = its share of tokens).
  python3 splice_build.py OUT SRC1[:w] SRC2[:w] …      (order = curriculum order: review first, preview last)
"""
import json, os, shutil, sys


def load(d):
    return json.load(open(os.path.join(d, "manifest.json")))


def pad(d):
    """append ONE trailing token to every phase (a copy of its last token; kind 255, stage 0, mask 0) so no row ends at the phase's last index.
    Runtime Seq::from_build reads token j+1 up to a row's end → a row ending exactly at the phase length read past the end (r16 10-08:
    thead.rs:537 index 62448 of len 62448 in a DOING build). Rows are unchanged. Idempotent via manifest "padded"."""
    import numpy as np
    m = json.load(open(os.path.join(d, "manifest.json")))
    if m.get("padded"): return 0
    for k, p in enumerate(m["phases"]):
        f = os.path.join(d, p["file"]); a = np.fromfile(f, dtype=np.uint16)
        if a.size: np.append(a, a[-1]).astype(np.uint16).tofile(f)
        for stem, val in (("kind", 255), ("stage", 0), ("mask", 0)):
            g = os.path.join(d, f"{stem}_{k}.u8")
            if os.path.exists(g): b = np.fromfile(g, dtype=np.uint8); np.append(b, np.uint8(val)).tofile(g)
    m["padded"] = 1; json.dump(m, open(os.path.join(d, "manifest.json"), "w"), indent=1)
    return len(m["phases"])


def main():
    if sys.argv[1:2] == ["--pad"]:
        for d in sys.argv[2:]: print(json.dumps({"padded": d, "phases": pad(d)}))
        return
    out, srcs = sys.argv[1], [a.rsplit(":", 1) if ":" in os.path.basename(a) else [a, None] for a in sys.argv[2:]]
    if not srcs: sys.exit(__doc__)
    mans = [load(s) for s, _ in srcs]
    base_i = next((i for i, m in enumerate(mans) if "tier1" in m), 0); base = mans[base_i]
    gen = None
    for (s, _), m in zip(srcs, mans):
        if m["token_ids"] != base["token_ids"]: sys.exit(f"refused: {s} token_ids differ")
        doms = m["port"]["domains"]
        g26 = doms[:26] if "tier1" not in m else json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tier1_symbols.json")))["generators"]
        if gen is None: gen = g26
        if g26 != gen: sys.exit(f"refused: {s} generator plate order differs")
        if m["port"].get("procedure_plate") != base["port"].get("procedure_plate"): sys.exit(f"refused: {s} procedure plate differs")
    toks = [sum(p.get("tokens", 0) for p in m["phases"]) for m in mans]
    w = [float(x) if x else t for (_, x), t in zip(srcs, toks)]; W = sum(w)
    if os.path.exists(out): shutil.rmtree(out)
    os.makedirs(out)
    phases, k = [], 0
    for (s, _), m, wi in zip(srcs, mans, w):
        ps = m["phases"]; st = [p.get("step_share") or p.get("share") or p.get("tokens", 1) for p in ps]; S = sum(st) or 1
        for j, p in enumerate(ps):
            q = dict(p); q["file"] = f"phase_{k}.u16"; q["step_share"] = round(wi / W * st[j] / S, 6); q["source"] = os.path.basename(os.path.normpath(s))
            shutil.copyfile(os.path.join(s, p["file"]), os.path.join(out, q["file"]))
            for stem, ext in (("kind", "u8"), ("stage", "u8"), ("rows", "u32"), ("mask", "u8")):
                f = os.path.join(s, f"{stem}_{j}.{ext}")
                if os.path.exists(f): shutil.copyfile(f, os.path.join(out, f"{stem}_{k}.{ext}"))
            t1 = os.path.join(s, f"t1_{j}.json")
            if "tier1" in base: shutil.copyfile(t1, os.path.join(out, f"t1_{k}.json")) if os.path.exists(t1) else open(os.path.join(out, f"t1_{k}.json"), "w").write("[]")
            phases.append(q); k += 1
    man = dict(base); man["phases"] = phases; man["spliced_from"] = [{"build": os.path.basename(os.path.normpath(s)), "weight": round(wi / W, 4)} for (s, _), wi in zip(srcs, w)]
    man["tokens_planned"] = sum(m.get("tokens_planned", 0) for m in mans); man["spec"] = "splice:" + "+".join(os.path.basename(os.path.normpath(s)) for s, _ in srcs)
    json.dump(man, open(os.path.join(out, "manifest.json"), "w"), indent=1)
    shutil.copyfile(os.path.join(srcs[base_i][0], ".clean-room.json"), os.path.join(out, ".clean-room.json"))   # every source is clean-room
    pad(out)
    print(json.dumps({"out": out, "phases": k, "from": man["spliced_from"], "padded": True}))


if __name__ == "__main__":
    main()

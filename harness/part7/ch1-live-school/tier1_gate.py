"""tier1_gate — the progression gate (TIER1 spec §9; J 10-05 "yes do pointer port and the rest of your suggestions"): a school passes when
the model COPIES — held-out top-1 on the positions whose operand is determined (operands it writes + the state line), over the lessons
whose copies are fully determined, is ≥ the bar (0.85). Reads <run>/probes/tier1_eval.json. Exit 0 = pass.
python3 tier1_gate.py <run> <school> [bar]"""
import json, sys
GATE = {"prek": ["pk.hold", "pk.commit", "pk.flush", "pk.give", "pk.tape", "pk.press", "pk.mix", "pk.echo", "pk.ping"],   # J 10-07: pk.meet out
        # (v3 drafts miss 40 % by design → not a determined copy; it held 552 of 5,107 gate positions — same rule as K below)
        "k": ["k.store", "k.transport", "k.tape"]}                    # K: meet drafts are random by design → not a copy measure
run, school = sys.argv[1], sys.argv[2]; bar = float(sys.argv[3]) if len(sys.argv) > 3 else 0.85
H = json.load(open(f"{run}/probes/tier1_eval.json"))["heldout_by_lesson_and_class"]
hit = n = 0
for les in GATE[school]:
    for cls in ("operand", "state"):
        c = H.get(les, {}).get(cls)
        if c: hit += c["top1"] * c["n"]; n += c["n"]
score = hit / max(n, 1)
print(f"TIER1-GATE {school}: copy top-1 {score:.3f} over {n} positions · bar {bar} · {'PASS' if score >= bar else 'REPEAT'}")
sys.exit(0 if score >= bar else 1)

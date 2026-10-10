"""T25-REACTOR arms: per day held-out · answer · canary · wake loss · day seconds.   python3 rx_report.py <arm> …"""
import json, os, sys
R = "<workspace>/projects/thead-trial/runtime/results"
print("arm | day | held-out | answer | canary | wake loss | day s | wake s")
for arm in sys.argv[1:]:
    p = f"{R}/rx-{arm}/state.json"
    if not os.path.exists(p): print(arm, "| no state"); continue
    s = json.load(open(p))
    for e in [e for e in s["log"] if e.get("day")]:
        d = next((x for x in s["days"] if x["day"] == e["day"]), {}); sec = d.get("seconds", {})
        print(" | ".join(str(v) for v in (arm, e["day"], round(e["heldout_loss_port"], 3), round(e["answer_loss_port"], 3), round(e["canary"], 3),
                                          round(d.get("wake_loss", 0), 3), round(sum(sec.values())), round(sec.get("wake", 0)))))

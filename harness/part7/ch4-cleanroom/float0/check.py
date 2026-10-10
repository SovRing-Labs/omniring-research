# FLOAT-0 differential: every reader row vs the real f32 functions (rustc). Name-free specs → match each spec to the function whose
# signature shape fits and whose outputs agree within rel 1e-4 + abs 1e-5 (same rule as the doctor's `same`).
import json, subprocess, sys, math
SIG = {"dot":["f32list","f32list"],"sumsq":["f32list"],"rms_scale":["f32list","f32"],"relu":["f32"],"lerp":["f32","f32","f32"],"mean":["f32list"],"logistic":["f32"],"scale_row":["f32list","f32"]}
def close(a,b): return (math.isnan(a) and math.isnan(b)) or abs(a-b) <= 1e-5 + 1e-4*max(abs(a),abs(b))
specs=[json.loads(l) for l in open(sys.argv[1])]; ok=0; covered=set()
for s in specs:
    ex=s["examples"]+s["holdout"]+s["validate"]; hit=None
    for fn,sig in SIG.items():
        if sig!=s["args"]: continue
        lines="".join(fn+"|"+"|".join(" ".join(map(str,x if isinstance(x,list) else [x])) for x in e[0])+"\n" for e in ex)
        out=subprocess.run(["./drive"],input=lines,capture_output=True,text=True).stdout.splitlines()
        good=all(len(o.split())==(len(e[1]) if isinstance(e[1],list) else 1) and all(close(float(p),float(q)) for p,q in zip(o.split(), e[1] if isinstance(e[1],list) else [e[1]])) for o,e in zip(out,ex))
        if good and len(out)==len(ex): hit=fn; break
    print("MATCH" if hit else "NONE ", hit, len(ex), "rows", s["equation"][:60]); ok+=bool(hit); hit and covered.add(hit)
print(json.dumps({"specs":len(specs),"agree":ok,"functions":sorted(covered)}))

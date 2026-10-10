# TYPES-0 differential: reader examples vs the real functions (rustc). Name-free specs → try every (fn, arg order); lists go after ints.
import json, subprocess, itertools, sys
FN = {"sq":(1,0),"clamp3":(2,0),"sumsq":(2,0),"clamped_sq":(2,0),"first_or":(1,1),"nth_or":(2,1),"empty_flag":(0,1),"steps":(1,0),"half":(1,0)}
specs=[json.loads(l) for l in open(sys.argv[1])]
def run(fn, rows):
    inp="".join(f"{fn}|{' '.join(map(str,ints))}|{' '.join(map(str,lst))}\n" for ints,lst in rows)
    out=subprocess.run(["./drive"],input=inp,capture_output=True,text=True,timeout=60).stdout.split()
    return [int(x) for x in out]
ok=0; cov=set()
for s in specs:
    ex=s["examples"]+s["holdout"]+s["validate"]; types=s["args"]; ni=types.count("int"); nl=types.count("list"); hit=None
    if nl>1: print("SKIP",s["equation"][:60]); continue
    for fn,(fi,fl) in FN.items():
        if (fi,fl)!=(ni,nl): continue
        ii=[k for k,t in enumerate(types) if t=="int"]; li=[k for k,t in enumerate(types) if t=="list"]
        for perm in itertools.permutations(ii):
            rows=[([e[0][k] for k in perm],[x for k in li for x in e[0][k]]) for e in ex]
            try:
                if run(fn,rows)==[e[1] for e in ex]: hit=fn; break
            except Exception: pass
        if hit: break
    print("MATCH" if hit else "NONE ", hit, s["equation"][:90]); ok+=bool(hit); hit and cov.add(hit)
print(json.dumps({"specs":len(specs),"agree":ok,"fns":sorted(cov)}))

# SKETCH-0 differential: every reader example (examples + holdout + validate) must equal the real function compiled by rustc.
# The spec is name-free, so each spec is matched against every (function, argument order) of the same arity.
import json, subprocess, itertools, sys
ARITY = {"gcd":2,"digits":1,"collatz":1,"sum_down":1,"classify":1,"pick":1,"opt":2,"unwrap":1,"pow2_above":1,"tri":2}
specs=[json.loads(l) for l in open(sys.argv[1])]
def run(fn, rows):
    inp="".join(f"{fn} {' '.join(map(str,r))}\n" for r in rows)
    return [int(x) for x in subprocess.run(["./drive"],input=inp,capture_output=True,text=True,timeout=60).stdout.split()]
ok=0; matched=set()
for s in specs:
    ex=s["examples"]+s["holdout"]+s["validate"]; n=len(s["args"]); hit=None
    for fn,a in ARITY.items():
        if a!=n: continue
        for perm in itertools.permutations(range(n)):
            rows=[[e[0][p] for p in perm] for e in ex]
            if run(fn,rows)==[e[1] for e in ex]: hit=(fn,perm); break
        if hit: break
    print(("MATCH " if hit else "NONE  "), len(ex), "examples", hit, s["equation"][:70]); ok+=bool(hit); hit and matched.add(hit[0])
print(json.dumps({"specs":len(specs),"agree_with_rustc":ok,"functions_covered":sorted(matched),"of":len(ARITY)}))

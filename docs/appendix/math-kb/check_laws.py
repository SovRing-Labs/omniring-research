# check_laws.py (CC BY 4.0, research corpus): test every law in mathkb.json on random cases from its own generator.
# Usage: python3 check_laws.py mathkb.json [cases]
import json, math, random, sys

kb = json.load(open(sys.argv[1]))
cases = int(sys.argv[2]) if len(sys.argv) > 2 else 200
R = random.Random(0)
for law in kb["axioms"]:
    env = {"math": math}
    exec(law.get("prelude", ""), env)          # helper the law needs (e.g. barrett, h, quant)
    exec(law["gen"], env)                       # defines gen(R, scope) -> one case
    ok = 0
    for _ in range(cases):
        args = env["gen"](R, None)
        scope = dict(env, **dict(zip(law["vars"], args)))   # one namespace, so lambdas see the variables
        ok += bool(eval(law["forms"]["python"], scope))
    print("%-42s %d/%d" % (law["id"], ok, cases))

"""CYCLONE-ARRAY C1 — turn the gcov JSON of one short school day into the port list for the resident model (C2).
Per engine function: calls, lines run / lines, its OpenMP parallel loops (and how many ran), sgemm call sites, and whether a GPU-LOOP spec of
the same name exists (gpu/specs/jobs.json). Exits 1 if the day did not run (no state.json day) or no function executed.
python3 -I c1_census.py <omni_train.cpp.gcov.json.gz> <omni_train.cpp> <state.json> <out.json>"""
import gzip, json, re, sys
GZ, SRC, STATE, OUT = sys.argv[1:5]
SPECS = "<projects>/ai-stack-opus-gpu/projects/thead-trial/gpu/specs/jobs.json"
g = json.load(gzip.open(GZ))
f = next(x for x in g["files"] if x["file"].endswith("omni_train.cpp"))
src = open(SRC).read().split("\n")
hits = {l["line_number"]: l["count"] for l in f["lines"]}
spec_fns = {j["fn"] for j in json.load(open(SPECS))}
day = json.load(open(STATE))["days"][0]
pragma = [i + 1 for i, s in enumerate(src) if re.match(r"\s*#pragma omp parallel for", s)]
rows = []
for fn in f["functions"]:
    a, b = fn["start_line"], fn["end_line"]
    name = fn["demangled_name"]; short = re.sub(r"\(.*", "", name).split("::")[-1]
    body = range(a, b + 1)
    loops = [p for p in pragma if a <= p <= b]
    loops_ran = [p for p in loops if hits.get(p + 1, 0) > 0 or hits.get(p, 0) > 0]
    gemm = sum(1 for i in body if re.search(r"\bsgemm\s*\(", src[i - 1]) and not src[i - 1].lstrip().startswith("static"))
    lines = [i for i in body if i in hits]
    rows.append({"fn": short, "sig": name, "lines": [a, b], "calls": fn["execution_count"], "lines_run": sum(1 for i in lines if hits[i] > 0),
                 "lines_total": len(lines), "omp_loops": len(loops), "omp_loops_ran": len(loops_ran), "sgemm_sites": gemm,
                 "gpu_spec": short if short in spec_fns else None})
ran = [r for r in rows if r["calls"] > 0]
if not ran: print("no engine function executed"); sys.exit(1)
ran.sort(key=lambda r: r["lines"][0])
out = {"engine_lines": len(src), "functions_total": len(rows), "functions_ran": len(ran),
       "omp_loops_total": len(pragma), "omp_loops_ran": sum(r["omp_loops_ran"] for r in ran),
       "lines_run": sum(r["lines_run"] for r in ran), "lines_in_ran_functions": sum(r["lines_total"] for r in ran),
       "with_gpu_spec": sorted({r["fn"] for r in ran if r["gpu_spec"]}),
       "specs_not_matched_by_name": sorted(spec_fns - {r["fn"] for r in rows}),
       "day_seconds": day.get("seconds"), "ran": ran,
       "not_ran": sorted({r["fn"] for r in rows if r["calls"] == 0})}
json.dump(out, open(OUT, "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ("ran", "not_ran")}))
print(f"{'fn':28} {'calls':>9} {'lines':>9} {'omp':>5} {'gemm':>4} spec")
for r in sorted(ran, key=lambda r: -r["lines_run"])[:60]:
    print(f"{r['fn'][:28]:28} {r['calls']:9} {r['lines_run']:4}/{r['lines_total']:<4} {r['omp_loops_ran']:2}/{r['omp_loops']:<2} {r['sgemm_sites']:4} {r['gpu_spec'] or ''}")

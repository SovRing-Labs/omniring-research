#!/usr/bin/env python3
"""GROW-RUN-0 step 4 — the network cuts (PROVENANCE-CONCEPTS-2026-10-09 #4, #6, #8): Gomory–Hu trees on OUR two graphs.
  (a) the array: 15 toroids (G120: 3 floors × 5 units), links = the layout rings (every toroid linked to every other along a ring: floor ring
      of 3, unit ring of 5 — W3 kernels/route.spvasm), loads = the items each link carried per step in the G120 rung (exact on the GPU).
      Residual capacity = C − load with C = the busiest link × 1.25 (so the hottest link sits at 80 %) → GH tree (n − 1 = 14 edges): the
      bottleneck between every pair of toroids; the global min cut = where the array saturates first.
  (b) the school: the prerequisite graph of one stage — the minimum vertex cut between its entry skills and its top levels (the skills
      every path through the stage must cross) + each skill's downstream count (how many skills it gates).
  g4_cuts.py <G120 rung record.json> [--stage prek] [--out DIR]"""
import itertools, json, os, sys
import networkx as nx
HERE = os.path.dirname(os.path.abspath(__file__)); TT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, f"{TT}/harness")


def array_cuts(rec):
    r = rec["route"]; dims = r["dims"]; L = r["link_per_step"]; U = len(r["inbox_per_step"])
    G = nx.Graph(); load = {}
    for d, dm in enumerate(dims):
        for a, b in itertools.combinations(range(U), 2):
            same = all(((a // o["stride"]) % o["size"]) == ((b // o["stride"]) % o["size"]) for e, o in enumerate(dims) if e != d)
            if same and ((a // dm["stride"]) % dm["size"]) != ((b // dm["stride"]) % dm["size"]):
                load[(a, b)] = L[d][a][b] + L[d][b][a]
    C = max(load.values()) * 1.25
    for (a, b), l_ in load.items(): G.add_edge(a, b, capacity=C - l_, load=l_)
    T = nx.gomory_hu_tree(G)
    name = lambda t: f"f{t // 5}u{t % 5}" + ("(centre)" if t % 5 == 0 else "")
    tree = sorted(({"a": name(u), "b": name(v), "min_cut_headroom": round(w["weight"], 1)} for u, v, w in T.edges(data=True)), key=lambda e: e["min_cut_headroom"])
    hot = sorted(({"link": f"{name(a)}–{name(b)}", "load": l_, "saturation": round(l_ / C, 3)} for (a, b), l_ in load.items()), key=lambda e: -e["load"])[:6]
    return {"toroids": U, "links": len(load), "capacity_C": C, "inbox_per_step": {name(i): v for i, v in enumerate(r["inbox_per_step"])},
            "hottest_links": hot, "gh_tree_14_edges": tree, "global_min_cut": tree[0]}


def school_cuts(stage):
    import school_graph as g
    N = g.nodes(); grp = dict(g.STAGES)[stage]; ks = [k for k, n in N.items() if n["school"] in grp]
    D = nx.DiGraph(); D.add_nodes_from(ks)
    for k in ks:
        for p in N[k]["prereq"]:
            if p in N and N[p]["school"] in grp: D.add_edge(p, k)
    src = [k for k in ks if D.in_degree(k) == 0]; top = [k for k in ks if D.out_degree(k) == 0]
    H = D.copy(); H.add_edges_from(("SRC", s) for s in src); H.add_edges_from((t, "SNK") for t in top)
    cut = sorted(nx.minimum_node_cut(H, "SRC", "SNK"))
    down = sorted(((k, len(nx.descendants(D, k))) for k in ks), key=lambda kv: -kv[1])[:10]
    return {"stage": stage, "skills": len(ks), "entry": len(src), "top": len(top), "min_vertex_cut": cut, "cut_size": len(cut),
            "most_downstream": [{"skill": k, "gates": n} for k, n in down]}


def main():
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    rec = json.load(open(a[0])); out = opt("--out", f"{TT}/tests/grow/results/g4"); os.makedirs(out, exist_ok=True)
    res = {"array": array_cuts(rec), "school": school_cuts(opt("--stage", "prek")), "source_record": a[0]}
    json.dump(res, open(f"{out}/g4-cuts.json", "w"), indent=1); print(json.dumps(res, indent=1)[:4000])


if __name__ == "__main__":
    main()

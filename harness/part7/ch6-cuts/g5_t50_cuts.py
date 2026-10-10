#!/usr/bin/env python3
"""GROW-RUN-0 G4c — the T50 interlock probe (J 10-09, confirmed: "interlocking two 50t omniring systems would solve this computation in much
less time by relying on the massive rapidly moving and counting outer rings"; VOCAB row "interlocking two T50 omniring systems").
  The array is a Cartesian product of rings: 15 toroids = floor ring (3) × unit ring (5), every toroid linked to every other along a ring.
  Field kin (clean-room, idea only): Klavžar & Špacapan, "On the edge-connectivity of Cartesian product graphs" — a minimum edge cut of G□H is
  either TRIVIAL (the edges at one vertex) or the preimage of a minimum cut of a FACTOR. So the cuts split along the rings.
  The route kernel (omni-gpu kernels/route.spvasm) already counts, in the same pass that moves the items:
    link[d][from][to]  per ring d, source residue × destination residue  (the source-addressed T50 ledger)
    hled[home][ring][residue] / inbox[home]                              (the destination-addressed T50 ledger)
  RING method: candidate cuts read straight from those counters — every singleton (per-vertex ring sums) + every bipartition of every ring's
  residues (a ring-level residue × residue table, Σ over fibres) → the min cut of every pair = the min candidate separating it.
  BASELINE: Gomory–Hu (networkx, n − 1 max-flows) → the min cut of every pair = the min edge on its tree path.
  Capacity model = g4_cuts.py: residual = C − load, C = the busiest link × 1.25.
  g5_t50_cuts.py <G120 rung record.json> [--fields 200] [--out DIR]"""
import itertools, json, os, random, sys, time
import networkx as nx
CAP = 1.25                                  # C = busiest link × CAP (g4 model); the saturation sweep lowers it
HERE = os.path.dirname(os.path.abspath(__file__)); TT = os.path.dirname(os.path.dirname(HERE))


def coords(t, rings):                       # mixed-radix address; layout order = rings[0] slowest (stride = Π later sizes), as W3 dims
    c = []
    for m in reversed(rings): c.append(t % m); t //= m
    return tuple(reversed(c))


def links(rings):                           # (a, b, d): a, b differ in exactly ring d
    n = 1
    for m in rings: n *= m
    C = [coords(t, rings) for t in range(n)]
    out = []
    for a, b in itertools.combinations(range(n), 2):
        diff = [d for d in range(len(rings)) if C[a][d] != C[b][d]]
        if len(diff) == 1: out.append((a, b, diff[0]))
    return n, C, out


def route_traffic(rings, items, rng, skew):  # dimension-order routing exactly as route.spvasm: for d in layout order jump to home's residue
    n, C, _ = links(rings)
    w = [rng.random() ** skew for _ in range(n)]            # skewed homes (the G120 inbox is uneven 5.1k … 27.5k)
    link = [[[0] * n for _ in range(n)] for _ in rings]
    index = {c: t for t, c in enumerate(C)}
    homes = rng.choices(range(n), weights=w, k=items)
    for h in homes:
        cur = list(C[rng.randrange(n)])
        for d in range(len(rings)):
            if cur[d] != C[h][d]:
                a = index[tuple(cur)]; cur[d] = C[h][d]; b = index[tuple(cur)]; link[d][a][b] += 1
    return link


def loads_from(link, lk):
    return {(a, b): link[d][a][b] + link[d][b][a] for a, b, d in lk}


def gomory_hu(n, lk, load, C):
    G = nx.Graph()
    for (a, b), l_ in load.items(): G.add_edge(a, b, capacity=C - l_)
    t0 = time.perf_counter(); T = nx.gomory_hu_tree(G); dt = time.perf_counter() - t0
    allp = {}
    for s in range(n):                      # min edge on every tree path (one DFS per source)
        stack = [(s, None, float("inf"))]
        while stack:
            u, p, m = stack.pop()
            if u != s: allp[(min(s, u), max(s, u))] = m
            for v in T[u]:
                if v != p: stack.append((v, u, min(m, T[u][v]["weight"])))
    return allp, dt, T


def ring_cuts(rings, C_, link, C):
    """The interlock read: only per-ring counters. Singletons from per-vertex ring sums; factor cuts from the per-ring residue × residue
    table (Σ over fibres). Returns the candidate list [(headroom, side-test)] and the time to build it."""
    t0 = time.perf_counter()
    n = len(C_); cand = []
    for v in range(n):                      # trivial cut: all links at v; degree = Σ (m − 1)
        deg = sum(m - 1 for m in rings)
        inc = sum(sum(link[d][v]) + sum(link[d][u][v] for u in range(n)) for d in range(len(rings)))
        cand.append((deg * C - inc, ("v", v)))
    for d, m in enumerate(rings):           # factor cut on ring d: residue bipartition A | Ā, preimage over the n/m fibres
        R = [[0] * m for _ in range(m)]
        for a in range(n):
            for b in range(n):
                if link[d][a][b]: R[C_[a][d]][C_[b][d]] += link[d][a][b]
        fib = n // m
        for k in range(1, m // 2 + 1):
            for A in itertools.combinations(range(m), k):
                if k * 2 == m and 0 not in A: continue
                As = set(A); cross = sum(R[i][j] + R[j][i] for i in As for j in range(m) if j not in As)
                cand.append((k * (m - k) * fib * C - cross, ("f", d, frozenset(As))))
    cand.sort(key=lambda c: c[0])
    return cand, time.perf_counter() - t0


def box_cuts(rings, C_, link, C):
    """Sub-torus cuts S = Π A_d (a residue subset per ring) — closes the hot-cluster gap (two toroids saturated toward everything else: the
    cut around the cluster is neither trivial nor a factor cut). Needs the full source × destination link table, which the OUTER rings hold
    collision-free (every outer modulus 131…233 > the toroid count, so residue = address). Small arrays only (Π (2^m − 1) boxes)."""
    t0 = time.perf_counter(); n = len(C_); cand = []
    subsets = [[frozenset(A) for k in range(1, m + 1) for A in itertools.combinations(range(m), k)] for m in rings]
    lk = [(a, b, d, link[d][a][b] + link[d][b][a]) for a, b, d in links(rings)[2]]
    for box in itertools.product(*subsets):
        if all(len(A) == m for A, m in zip(box, rings)): continue
        inn = [all(C_[t][d] in box[d] for d in range(len(rings))) for t in range(n)]
        cnt = cross = 0
        for a, b, d, l_ in lk:
            if inn[a] != inn[b]: cnt += 1; cross += l_
        cand.append((cnt * C - cross, ("b", tuple(box))))
    return cand, time.perf_counter() - t0


def separates(side, s, t, C_):
    if side[0] == "v": return (s == side[1]) != (t == side[1])
    if side[0] == "b":
        ins = lambda x: all(C_[x][d] in A for d, A in enumerate(side[1])); return ins(s) != ins(t)
    _, d, A = side; return (C_[s][d] in A) != (C_[t][d] in A)


def hot_cluster_sweep(rings, fields, seed):
    """Adversarial fields: a random box of toroids saturated toward the rest, background routed traffic. Ring family vs ring + box family."""
    n, C_, lk = links(rings); rng = random.Random(seed); ring_ok = box_ok = 0; worst_ring = worst_box = 0.0; t_box = 0.0
    for _ in range(fields):
        link = route_traffic(rings, 4000, rng, 2)
        box = [frozenset(rng.sample(range(m), rng.randint(1, m - 1))) for m in rings]
        inn = [all(C_[t][d] in box[d] for d in range(len(rings))) for t in range(n)]
        hot = max(max(max(r) for r in L) for L in link) * 3
        for a, b, d in lk:
            if inn[a] != inn[b]: link[d][a][b] += hot
        load = loads_from(link, lk); C = max(load.values()) * CAP
        gh_all, _, _ = gomory_hu(n, lk, load, C)
        cand, _ = ring_cuts(rings, C_, link, C); r_all, _ = all_pairs_from(cand, n, C_)
        bc, tb = box_cuts(rings, C_, link, C); t_box += tb; b_all, _ = all_pairs_from(sorted(cand + bc, key=lambda c: c[0]), n, C_)
        gr = max(r_all[p] - gh_all[p] for p in gh_all) / C; gb = max(b_all[p] - gh_all[p] for p in gh_all) / C
        ring_ok += gr <= 1e-9; box_ok += gb <= 1e-9; worst_ring = max(worst_ring, gr); worst_box = max(worst_box, gb)
    return {"rings": rings, "fields": fields, "ring_family_exact": ring_ok, "ring_plus_box_exact": box_ok,
            "worst_gap_over_C_ring": round(worst_ring, 3), "worst_gap_over_C_box": round(worst_box, 3), "box_read_s_mean": round(t_box / fields, 4)}


def all_pairs_from(cand, n, C_):
    t0 = time.perf_counter(); out = {}
    for s, t in itertools.combinations(range(n), 2):
        for h, side in cand:                # sorted: first separating candidate = the pair's min
            if separates(side, s, t, C_): out[(s, t)] = h; break
    return out, time.perf_counter() - t0


def closed_form(cand, rings, n):
    """Σm form: a per-vertex trivial cut + per ring an m × m table (best factor cut separating residues i, j). A pair's min cut =
    min(trivial s, trivial t, the ring tables of every ring where s and t differ) — O(rings) per pair, no search."""
    t0 = time.perf_counter(); triv = [0.0] * n; tab = [[[float("inf")] * m for _ in range(m)] for m in rings]
    for h, side in cand:
        if side[0] == "v": triv[side[1]] = h
        else:
            _, d, A = side; m = rings[d]
            for i in A:
                for j in range(m):
                    if j not in A and h < tab[d][i][j]: tab[d][i][j] = tab[d][j][i] = h
    return triv, tab, time.perf_counter() - t0


def pair_cut(s, t, triv, tab, C_):
    return min([triv[s], triv[t]] + [tab[d][C_[s][d]][C_[t][d]] for d in range(len(tab)) if C_[s][d] != C_[t][d]])


def compare(rings, link, with_gh=True, sample=0):
    n, C_, lk = links(rings); load = loads_from(link, lk); C = max(load.values()) * CAP
    cand, t_ring = ring_cuts(rings, C_, link, C); triv, tab, t_tab = closed_form(cand, rings, n)
    t0 = time.perf_counter(); ring_all = {(s, t): pair_cut(s, t, triv, tab, C_) for s, t in itertools.combinations(range(n), 2)}
    t_pairs = time.perf_counter() - t0
    res = {"toroids": n, "links": len(lk), "candidates": len(cand), "ring_read_s": round(t_ring + t_tab, 6),
           "ring_all_pairs_s": round(t_pairs, 6), "ring_table_entries": n + sum(m * m for m in rings), "ring_global_min": round(cand[0][0], 1)}
    if n <= 105:                            # cross-check the closed form against the plain enumeration
        enum, _ = all_pairs_from(cand, n, C_); res["closed_form_equals_enumeration"] = enum == ring_all
    if sample:                              # too big for a full GH here: sampled pairs by exact max-flow + the global min by Stoer–Wagner
        G = nx.Graph()
        for (a, b), l_ in load.items(): G.add_edge(a, b, capacity=C - l_, weight=C - l_)
        rng = random.Random(11); pairs = [tuple(sorted(rng.sample(range(n), 2))) for _ in range(sample)]
        t0 = time.perf_counter(); exact = {p: nx.minimum_cut_value(G, p[0], p[1]) for p in pairs}; t_mf = (time.perf_counter() - t0) / sample
        t0 = time.perf_counter(); sw, _ = nx.stoer_wagner(G); t_sw = time.perf_counter() - t0
        res.update({"sampled_pairs": sample, "sampled_equal": sum(abs(exact[p] - ring_all[p]) <= 1e-6 * C for p in pairs),
                    "maxflow_s_per_pair": round(t_mf, 4), "gh_estimate_s": round(t_mf * (n - 1), 1),
                    "stoer_wagner_global_min": round(sw, 1), "stoer_wagner_s": round(t_sw, 2)})
    if with_gh:
        gh_all, t_gh, _ = gomory_hu(n, lk, load, C)
        bad = [(p, gh_all[p], ring_all[p]) for p in gh_all if abs(gh_all[p] - ring_all[p]) > 1e-6 * C]
        res.update({"gh_s": round(t_gh, 4), "gh_global_min": round(min(gh_all.values()), 1), "pairs": len(gh_all),
                    "pairs_equal": len(gh_all) - len(bad), "worst_gap": round(max((r - g for _, g, r in bad), default=0.0), 1),
                    "speedup": round(t_gh / max(t_ring + t_pairs, 1e-9), 1)})
    return res, cand, C_


def main():
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    rec = json.load(open(a[0])); out = opt("--out", f"{TT}/tests/grow/results/g5"); os.makedirs(out, exist_ok=True)
    r = rec["route"]; rings = [o["size"] for o in r["dims"]]; U = len(r["inbox_per_step"])
    link = [[row[:U] for row in r["link_per_step"][d][:U]] for d in range(len(rings))]
    name = lambda t: f"f{t // 5}u{t % 5}"
    g120, cand, C_ = compare(rings, link)
    g120["ring_bottleneck"] = (name(cand[0][1][1]) if cand[0][1][0] == "v" else f"ring {rings[cand[0][1][1]]} cut {sorted(cand[0][1][2])}")
    g4 = json.load(open(f"{TT}/tests/grow/results/g4/g4-cuts.json"))["array"]["global_min_cut"]
    g120["g4_global_min_cut"] = g4
    rng = random.Random(1009); fields = int(opt("--fields", 200)); agree = 0; worst = 0.0; kinds = {"v": 0, "f": 0}
    for _ in range(fields):                 # robustness: seeded dimension-order-routed traffic on the same K3□K5, varied skew
        lk_ = route_traffic(rings, 40000, rng, rng.choice([0.5, 1, 2, 4, 8]))
        res, cnd, _ = compare(rings, lk_); agree += res["pairs_equal"] == res["pairs"]; worst = max(worst, res["worst_gap"])
        kinds[cnd[0][1][0]] += 1
    scale = []
    for rs, items, gh, smp in (([3, 5], 245760, True, 0), ([3, 5, 7], 245760, True, 0), ([3, 5, 7, 11], 245760, False, 60)):
        lk_ = route_traffic(rs, items, random.Random(7), 2); res, _, _ = compare(rs, lk_, with_gh=gh, sample=smp); res["rings"] = rs
        scale.append(res)
    result = {"probe": "G4c T50 interlock", "source_record": a[0], "G120": g120,
              "robustness": {"fields": fields, "all_105_pairs_equal": agree, "worst_gap": worst, "global_min_kind": kinds},
              "scaling": scale, "hot_cluster": [hot_cluster_sweep([3, 5], 100, 21), hot_cluster_sweep([3, 5, 7], 3, 22)]}
    json.dump(result, open(f"{out}/g5-t50-cuts.json", "w"), indent=1); print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()

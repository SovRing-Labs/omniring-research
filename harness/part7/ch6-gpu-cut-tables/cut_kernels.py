#!/usr/bin/env python3
"""GROW-RUN-0 G4c-GPU — the cut read on the GPU, rendered by OUR emitter (thead-trial/gpu/emit/spirv.py, template T0) from one name-free
equation. Reads ONLY the tables the route pass fills with its own atomics (kernels/route.spvasm bindings 8, 9) + the link ledger's busiest
link, and writes every toroid pair's min cut (the T50 interlock read, probe tests/grow/g5_t50_cuts.py; field kin Klavžar–Špacapan: a min cut
of a ring product is trivial — the links at one toroid — or the preimage of one ring's cut).
  args  a0 rtab int[4·16·16]  per ring d: residue × residue items  rtab[(d·16 + from)·16 + to]
        a1 vtab int[4·T]      per ring d: items through toroid v      vtab[d·T + v]  (both ends of every jump)
        a2 lay  int[13]       [D, (lane, S, stride) × 4]             (route's layout)
        a3 link int[4·T·T]    the source-addressed link ledger (only its busiest link is read: C = 1.25 · busiest)
        a4 T    (spec)        toroids
  out   cut float[T·T]        4 · (min-cut headroom) = min over separating cuts of 5·cnt·busiest − 4·crossing  (integer, exact < 2²⁴)
  cut_kernels.py OUT_DIR     → OUT_DIR/cuts.spv (+ manifest row printed)"""
import hashlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(HERE)
sys.path.insert(0, os.path.normpath(f"{P}/../thead-trial/gpu/emit"))
import spirv
BIG = 1 << 30


def fold(p, lo, hi, init, body):          # a fold evaluated at depth p binds item{p+1} / acc{p+1}.0 in its body
    q = p + 1; return f"(fold (range {lo} {hi}) {init} {body(q, f'item{q}', f'acc{q}.0')})"


def let(p, value, body):                  # one-iteration fold = a let: body sees value as acc{p+1}.0
    return fold(p, 0, 1, value, lambda q, _i, a: body(q, a))


T = "a4"; ND = "(idx a2 0)"
S = lambda d: f"(idx a2 (+ (* 3 {d}) 2))"
ST = lambda d: f"(idx a2 (+ (* 3 {d}) 3))"
coord = lambda x, d: f"(% (/ {x} {ST(d)}) {S(d)})"
pow2 = lambda p, i: fold(p, 0, i, 1, lambda q, _i, a: f"(* {a} 2)")
bit = lambda p, m, i: f"(% (/ {m} {pow2(p, i)}) 2)"
R = lambda d, i, j: f"(idx a0 (+ (* (+ (* {d} 16) {i}) 16) {j}))"


def busiest(p):                           # max over links of both directions' items
    TT = f"(* {T} {T})"
    def body(q, it, a):
        d = f"(/ {it} {TT})"; r = f"(% {it} {TT})"; x = f"(/ {r} {T})"; y = f"(% {r} {T})"
        return f"(max {a} (+ (idx a3 {it}) (idx a3 (+ (* {d} {TT}) (+ (* {y} {T}) {x})))))"
    return fold(p, 0, f"(* {ND} {TT})", 0, body)


def equation():
    s, t = f"(/ item1 {T})", f"(% item1 {T})"
    def with_mx(p1, mx):
        def with_deg(p2, dg):
            inc = lambda p, v: fold(p, 0, ND, 0, lambda q, d, a: f"(+ {a} (idx a1 (+ (* {d} {T}) {v})))")
            triv = lambda p, v: f"(- (* 5 (* {dg} {mx})) (* 4 {inc(p, v)}))"
            def ring(q1, d, a1):                                   # ring d: best bipartition separating s's residue from t's
                cs, ct, Sd = coord(s, d), coord(t, d), S(d)
                def mask(q2, m, a2):
                    ok = f"(and (== {bit(q2, m, cs)} 1) (== {bit(q2, m, ct)} 0))"
                    k = fold(q2, 0, Sd, 0, lambda q3, i, a3: f"(+ {a3} {bit(q3, m, i)})")
                    cross = fold(q2, 0, Sd, 0, lambda q3, i, a3: f"(+ {a3} " + fold(q3, 0, Sd, 0, lambda q4, j, a4:
                        f"(+ {a4} (sel (and (== {bit(q4, m, i)} 1) (== {bit(q4, m, j)} 0)) (+ {R(d, i, j)} {R(d, j, i)}) 0))") + ")")
                    val = f"(- (* 5 (* (* {k} (- {Sd} {k})) (* (/ {T} {Sd}) {mx}))) (* 4 {cross}))"
                    return f"(sel {ok} (min {a2} {val}) {a2})"
                best = fold(q1, 1, f"(- {pow2(q1, Sd)} 1)", BIG, mask)
                return f"(sel (!= {cs} {ct}) (min {a1} {best}) {a1})"
            return f"(min (min {triv(p2, s)} {triv(p2, t)}) {fold(p2, 0, ND, BIG, ring)})"
        return let(p1, fold(p1, 0, ND, 0, lambda q, d, a: f"(+ {a} (- {S(d)} 1))"), with_deg)
    return f"(map (range 0 (* {T} {T})) (sel (== {s} {t}) 0 {let(1, busiest(1), with_mx)}))"


ARGS = ["list", "list", "list", "list", "int"]


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else f"{P}/kernels"
    b, info = spirv.emit_spv({"args": ARGS, "equation": equation()}, json.load(open(spirv.TABLES)), "T0", False)
    open(f"{out}/cuts.spv", "wb").write(b)
    import subprocess
    v = subprocess.run(["spirv-val", "--target-env", "vulkan1.1", f"{out}/cuts.spv"], capture_output=True, text=True)
    print(json.dumps({"cuts.spv": {"args": ARGS, "sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b), **info}, "spirv_val": v.returncode == 0,
                      "val_err": v.stderr[-400:]}, indent=1, default=str))
    sys.exit(v.returncode)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""OMNI-RENDER-GPU-0 § CYCLONE-ARRAY C2 — the THEAD training step's kernels, rendered by OUR emitter (thead-trial/gpu/emit/spirv.py) from
name-free A1 equations. Each equation states the arithmetic of one piece of OUR engine (engine/omni_train/omni_train.cpp; the function and
line it mirrors is named beside it) in the engine's own operation order, so the GPU step can be compared with the CPU engine row for row.
These equations are AGENT-WRITTEN from our own engine source (not reader-made); the gate is the CPU engine's own loss and gradients.
GEMMs reuse the wall-passed GPU-LOOP sgemm_{gnn,gnt,gtn} specs (template T2: register-blocked). Row operations are two passes — the row's
statistics once (one invocation per row), then the elementwise pass — never statistics recomputed per element.
  train_kernels.py OUT_DIR      → OUT_DIR/<name>.spv + OUT_DIR/manifest.json (args, template, dispatch, spec ids)"""
import hashlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(HERE)
EMIT = os.path.normpath(f"{P}/../thead-trial/gpu/emit"); sys.path.insert(0, EMIT)
import spirv                                                                                    # our SPIR-V back end (V3 + E1 + C2c)
SPECS = os.path.normpath(f"{P}/../thead-trial/gpu/specs/jobs.json")
EPS = "1.1920928955078125e-07f"                                                                 # omni_train.cpp:34 EPS
RND = "12582912.0f"                                                                             # 1.5·2²³: (v + RND) − RND = nearbyintf(v), |v| < 2²²

def rot_eq():
    """omni_train.cpp:677 rot (voicing off, no T25: k = pos mod p): pairs (2i, 2i+1) of each head of the q and k thirds turned by the residue
    clock; the v third copied. args: qkv, cos, sin (flattened per pair), off (pair → table offset), primes, N, T, D, DH, sign"""
    W3 = "(* 3 a7)"; c = f"(% item1 {W3})"; cc = f"(% {c} a7)"; j = f"(% {cc} a8)"; i = f"(/ {j} 2)"; n = f"(/ item1 {W3})"
    k = f"(% (% {n} a6) (idx a4 {i}))"; ci = f"(+ (idx a3 {i}) {k})"; co = f"(idx a1 {ci})"; si = f"(* a9 (idx a2 {ci}))"
    base = f"(- item1 {j})"; a = f"(idx a0 (+ {base} (* 2 {i})))"; b = f"(idx a0 (+ (+ {base} (* 2 {i})) 1))"
    rot = f"(sel (== (% {j} 2) 0) (- (* {a} {co}) (* {b} {si})) (+ (* {a} {si}) (* {b} {co})))"
    return f"(map (range 0 (* a5 {W3})) (sel (>= {c} (* 2 a7)) (idx a0 item1) {rot}))"

def rot25_eq():
    """omni_train.cpp:677 rot WITH the T25 core + octave voicing (school: T25_CORE=1, VOICE=1): pair i turns by k = the position's T25
    residue on its lane (lane ≥ 0) else (n mod T) mod p; voicing: k ← k·(2^h mod p) mod p for head h. args: qkv, cos, sin, off, primes,
    res (N·32 residues, the rendered core's address per position), lane (pair → lane, −1 none), N, T, D, DH, sign, voice"""
    W3 = "(* 3 a9)"; c = f"(% item1 {W3})"; cc = f"(% {c} a9)"; j = f"(% {cc} a10)"; i = f"(/ {j} 2)"; n = f"(/ item1 {W3})"; h = f"(/ {cc} a10)"
    p = f"(idx a4 {i})"; ln = f"(idx a6 {i})"
    k0 = f"(sel (>= {ln} 0) (idx a5 (+ (* {n} 32) {ln})) (% (% {n} a8) {p}))"
    pw = f"(fold (range 0 {h}) 1 (% (* acc2.0 2) {p}))"
    k = f"(sel (!= a12 0) (% (* {k0} {pw}) {p}) {k0})"
    ci = f"(+ (idx a3 {i}) {k})"; co = f"(idx a1 {ci})"; si = f"(* a11 (idx a2 {ci}))"
    base = f"(- item1 {j})"; av = f"(idx a0 (+ {base} (* 2 {i})))"; bv = f"(idx a0 (+ (+ {base} (* 2 {i})) 1))"
    rot = f"(sel (== (% {j} 2) 0) (- (* {av} {co}) (* {bv} {si})) (+ (* {av} {si}) (* {bv} {co})))"
    return f"(map (range 0 (* a7 {W3})) (sel (>= {c} (* 2 a9)) (idx a0 item1) {rot}))"

def rot25p_eq():
    """GPU DECODE (GROW-RUN-0): rot25 for one token per station at its OWN position — k0 = the T25 residue on the pair's lane, else
    pos[station] mod p (rot25 takes n mod T). args: qkv, cos, sin, off, primes, res, lane, N, D, DH, sign, voice, pos"""
    W3 = "(* 3 a8)"; c = f"(% item1 {W3})"; cc = f"(% {c} a8)"; j = f"(% {cc} a9)"; i = f"(/ {j} 2)"; n = f"(/ item1 {W3})"; h = f"(/ {cc} a9)"
    p = f"(idx a4 {i})"; ln = f"(idx a6 {i})"
    k0 = f"(sel (>= {ln} 0) (idx a5 (+ (* {n} 32) {ln})) (% (idx a12 {n}) {p}))"
    pw = f"(fold (range 0 {h}) 1 (% (* acc2.0 2) {p}))"
    k = f"(sel (!= a11 0) (% (* {k0} {pw}) {p}) {k0})"
    ci = f"(+ (idx a3 {i}) {k})"; co = f"(idx a1 {ci})"; si = f"(* a10 (idx a2 {ci}))"
    base = f"(- item1 {j})"; av = f"(idx a0 (+ {base} (* 2 {i})))"; bv = f"(idx a0 (+ (+ {base} (* 2 {i})) 1))"
    rot = f"(sel (== (% {j} 2) 0) (- (* {av} {co}) (* {bv} {si})) (+ (* {av} {si}) (* {bv} {co})))"
    return f"(map (range 0 (* a7 {W3})) (sel (>= {c} (* 2 a8)) (idx a0 item1) {rot}))"

def rcpart_eq():
    """row statistics in chunks (GROW-RUN-0 speed: hstatsA / rtcheck looped one thread over all V): per (row, chunk of V/C) its max m, how many
    entries equal m, and the largest entry below m. args: L, V, C → [N·C·3]"""
    n = "(/ item1 (* a2 3))"; c = "(% (/ item1 3) a2)"; w = "(% item1 3)"; CS = "(/ a1 a2)"; base = f"(+ (* {n} a1) (* {c} {CS}))"
    Lv = lambda i: f"(idx a0 (+ {base} {i}))"
    m2 = f"(fold (range 0 {CS}) (neg 1e30f) (max acc2.0 {Lv('item2')}))"; m3 = f"(fold (range 0 {CS}) (neg 1e30f) (max acc3.0 {Lv('item3')}))"
    cnt = f"(fold (range 0 {CS}) 0.0f (+ acc2.0 (sel (== {Lv('item2')} {m3}) 1.0f 0.0f)))"
    s2 = f"(fold (range 0 {CS}) (neg 1e30f) (max acc2.0 (sel (== {Lv('item2')} {m3}) (neg 1e30f) {Lv('item2')})))"
    return f"(map (range 0 (* (/ (len a0) a1) (* a2 3))) (sel (== {w} 0) {m2} (sel (== {w} 1) {cnt} {s2})))"

def rcz_eq():
    """per (row, chunk) Σ exp(L − row max) with the row max from the chunk partials. args: L, part, V, C → [N·C]"""
    n = "(/ item1 a2)"; c = "(% item1 a2)"; CS = "(/ a2 a2)"; CS = "(/ a2 a3)"; base = f"(+ (* {n} a2) (* {c} {CS}))"
    M3 = f"(fold (range 0 a3) (neg 1e30f) (max acc3.0 (idx a1 (* (+ (* {n} a3) item3) 3))))"
    return f"(map (range 0 (* (/ (len a0) a2) a3)) (fold (range 0 {CS}) 0.0f (+ acc2.0 (exp (- (idx a0 (+ {base} item2)) {M3})))))"

def hstats_chunk_eq():
    """hstatsA from the chunk partials (same formula: mask, y < 0, avoid). args: L, y, mask, av, part, zc, N, V, C, alpha → [mx, z, loss]"""
    n = "(/ item1 3)"; w = "(% item1 3)"; row = f"(* {n} a7)"
    mx2 = f"(fold (range 0 a8) (neg 1e30f) (max acc2.0 (idx a4 (* (+ (* {n} a8) item2) 3))))"
    z2 = f"(fold (range 0 a8) 0.0f (+ acc2.0 (idx a5 (+ (* {n} a8) item2))))"
    t = f"(idx a1 {n})"; av = f"(idx a3 {n})"
    ul = f"(and (and (>= {av} 0) (< {av} a7)) (!= {av} {t}))"
    pa = f"(/ (exp (- (idx a0 (+ {row} {av})) {mx2})) {z2})"
    u = f"(sel {ul} (* (neg a9) (ln (max (- 1.0f {pa}) 1e-5f))) 0.0f)"
    loss = f"(sel (or (< {t} 0) (<= (idx a2 {n}) 0.0f)) 0.0f (+ (- (+ {mx2} (ln {z2})) (idx a0 (+ {row} {t}))) {u}))"
    return f"(map (range 0 (* a6 3)) (sel (== {w} 0) {mx2} (sel (== {w} 1) {z2} {loss})))"

def rtcheck_chunk_eq():
    """rtcheck with the exact top-2 margin (ties → 0) from the chunk partials. args: logits, xo, xi, ex, pkind, part, V, D, l, AL, theta, sat,
    portrows, C → ex′"""
    n = "item1"; pm = lambda i: f"(idx a5 (* (+ (* {n} a13) {i}) 3))"; pc = lambda i: f"(idx a5 (+ (* (+ (* {n} a13) {i}) 3) 1))"
    ps = lambda i: f"(idx a5 (+ (* (+ (* {n} a13) {i}) 3) 2))"
    mx = f"(fold (range 0 a13) (neg 1e30f) (max acc2.0 {pm('item2')}))"; mx3 = f"(fold (range 0 a13) (neg 1e30f) (max acc3.0 {pm('item3')}))"
    ties = f"(fold (range 0 a13) 0.0f (+ acc2.0 (sel (== {pm('item2')} {mx3}) {pc('item2')} 0.0f)))"
    s2 = f"(sel (> {ties} 1.5f) {mx} (fold (range 0 a13) (neg 1e30f) (max acc2.0 (sel (== {pm('item2')} {mx3}) {ps('item2')} {pm('item2')}))))"
    dot = lambda A, B: f"(fold (range 0 a7) 0.0f (+ acc2.0 (* (idx {A} (+ (* {n} a7) item2)) (idx {B} (+ (* {n} a7) item2)))))"
    cos = f"(/ {dot('a1', 'a2')} (sqrt (max (* {dot('a1', 'a1')} {dot('a2', 'a2')}) 1e-30f)))"
    run = f"(and (and (== (idx a3 {n}) a9) (not (and (!= a12 0) (>= (idx a4 {n}) 0)))) (or (<= a11 0.0f) (>= {cos} a11)))"
    return f"(map a3 (sel (and {run} (>= (- {mx} {s2}) a10)) a8 (idx a3 {n})))"

def split_eq(width):
    """[N, width·D] rows → one head-major part [B][H][T][DH] (part w of the row's thirds when width = 3). args: src, B, T, H, DH, w"""
    HTD = "(* a3 (* a2 a4))"; TD = "(* a2 a4)"
    b = f"(/ item1 {HTD})"; r2 = f"(% item1 {HTD})"; h = f"(/ {r2} {TD})"; r3 = f"(% {r2} {TD})"; t = f"(/ {r3} a4)"; d = f"(% {r3} a4)"
    D = "(* a3 a4)"
    src = f"(+ (+ (* (+ (* {b} a2) {t}) (* {width} {D})) (* a5 {D})) (+ (* {h} a4) {d}))"
    return f"(map (range 0 (* a1 {HTD})) (idx a0 {src}))"

def merge_eq():
    """[B][H][T][DH] → [N, D] (attention output). args: O, B, T, H, DH"""
    D = "(* a3 a4)"; n = f"(/ item1 {D})"; c = f"(% item1 {D})"; b = f"(/ {n} a2)"; t = f"(% {n} a2)"; h = f"(/ {c} a4)"; d = f"(% {c} a4)"
    return f"(map (range 0 (* (* a1 a2) {D})) (idx a0 (+ (* (+ (* (+ (* {b} a3) {h}) a2) {t}) a4) {d})))"

def merge3_eq():
    """dQ, dK, dV [B][H][T][DH] → dqkv [N, 3D]. args: dQ, dK, dV, B, T, H, DH"""
    D = "(* a5 a6)"; D3 = f"(* 3 {D})"; n = f"(/ item1 {D3})"; c3 = f"(% item1 {D3})"; w = f"(/ {c3} {D})"; c = f"(% {c3} {D})"
    b = f"(/ {n} a4)"; t = f"(% {n} a4)"; h = f"(/ {c} a6)"; d = f"(% {c} a6)"
    src = f"(+ (* (+ (* (+ (* {b} a5) {h}) a4) {t}) a6) {d})"
    return f"(map (range 0 (* (* a3 a4) {D3})) (sel (== {w} 0) (idx a0 {src}) (sel (== {w} 1) (idx a1 {src}) (idx a2 {src}))))"

def attn_stats_eq():
    """omni_train.cpp:712 attn_fwd softmax row (plates off, causal): per (bh, i) three values: mx = max_{j≤i} S·sc, iz = 1/z, lse = mx + ln z,
    z = Σ_{j≤i} exp(S·sc − mx). Batched over bh (row axis). args: S, T, sc"""
    i = "(/ item1 3)"; w = "(% item1 3)"
    mx2 = f"(fold (range 0 (+ {i} 1)) (neg 1e30f) (max acc2.0 (* (idx a0 (+ (* {i} a1) item2)) a2)))"
    mx3 = f"(fold (range 0 (+ {i} 1)) (neg 1e30f) (max acc3.0 (* (idx a0 (+ (* {i} a1) item3)) a2)))"
    z = f"(fold (range 0 (+ {i} 1)) 0.0f (+ acc2.0 (exp (- (* (idx a0 (+ (* {i} a1) item2)) a2) {mx3}))))"
    return f"(map (range 0 (* a1 3)) (sel (== {w} 0) {mx2} (sel (== {w} 1) (/ 1.0f {z}) (+ {mx2} (ln {z})))))"

def attn_stats_row_eq():
    """attn_stats_eq with plates on (omni_train.cpp:735 T25-REACTOR): the softmax runs over the row's own keys j0 ≤ j ≤ i, j0 = the row start.
    args: S, rs (row start per position of this (b, h) row), T, sc"""
    i = "(/ item1 3)"; w = "(% item1 3)"; j0 = f"(idx a1 {i})"
    mx2 = f"(fold (range {j0} (+ {i} 1)) (neg 1e30f) (max acc2.0 (* (idx a0 (+ (* {i} a2) item2)) a3)))"
    mx3 = f"(fold (range {j0} (+ {i} 1)) (neg 1e30f) (max acc3.0 (* (idx a0 (+ (* {i} a2) item3)) a3)))"
    z = f"(fold (range {j0} (+ {i} 1)) 0.0f (+ acc2.0 (exp (- (* (idx a0 (+ (* {i} a2) item2)) a3) {mx3}))))"
    return f"(map (range 0 (* a2 3)) (sel (== {w} 0) {mx2} (sel (== {w} 1) (/ 1.0f {z}) (+ {mx2} (ln {z})))))"

def plate_bucket_eq():
    """omni_train.cpp:1080 mem_bucket of the UN-rotated head slice (plate_fwd): 12 LSH sign bits over planes [DH, 12] → page (code mod 13)·17 +
    code mod 17. Out head-major [B][H][T]. args: qkv0 (N·3D, before rot), planes, pw (2^b), T, D, DH, H, which (0 = q, 1 = k)"""
    b = "(/ item1 (* a6 a3))"; h = "(% (/ item1 a3) a6)"; t = "(% item1 a3)"; n = f"(+ (* {b} a3) {t})"
    base = f"(+ (+ (* {n} (* 3 a4)) (* a7 a4)) (* {h} a5))"
    s_ = f"(fold (range 0 a5) 0.0f (+ acc3.0 (* (idx a0 (+ {base} item3)) (idx a1 (+ (* item3 12) item2)))))"
    code = f"(fold (range 0 12) 0 (+ acc2.0 (sel (> {s_} 0.0f) (idx a2 item2) 0)))"
    return f"(map (range 0 (* (* (/ (len a0) (* 3 a4)) a6) 1)) (+ (* (% {code} 13) 17) (% {code} 17)))"

def harm_c_eq(i, j, hw, tc, ts, ro, rp, d):
    """c_ij = Σ_r hw[i·10 + 2r]·cos(o_r) + hw[i·10 + 2r + 1]·sin(o_r), o_r = (i − j) mod p_r — a fold at depth d over the 5 rings"""
    it = f"item{d}"; o = f"(% (- {i} {j}) (idx {rp} {it}))"; tix = f"(+ (idx {ro} {it}) {o})"
    return (f"(fold (range 0 5) 0.0f (+ acc{d}.0 (+ (* (idx {hw} (+ (* {i} 10) (* 2 {it}))) (idx {tc} {tix})) "
            f"(* (idx {hw} (+ (+ (* {i} 10) (* 2 {it})) 1)) (idx {ts} {tix})))))")

def harm_w_eq():
    """harm_weights:827 per element (b, h, i, r, c) of hz [B·H·T·10]: heads' sums on ring r at row (b, i)"""
    HT10 = "(* (* a1 a2) 10)"; b = f"(/ item1 {HT10})"; i = "(% (/ item1 10) a2)"; r = "(/ (% item1 10) 2)"; c = "(% item1 2)"
    zi = lambda hh, cc: f"(idx a0 (+ (+ (* (+ (* (+ (* {b} a1) {hh}) a2) {i}) 10) (* 2 {r})) {cc}))"
    Ar = f"(fold (range 0 a1) 0.0f (+ acc2.0 {zi('item2', 0)}))"; Ai = f"(fold (range 0 a1) 0.0f (+ acc2.0 {zi('item2', 1)}))"
    S = f"(fold (range 0 a1) 0.0f (+ acc2.0 (sqrt (+ (+ (* {zi('item2', 0)} {zi('item2', 0)}) (* {zi('item2', 1)} {zi('item2', 1)})) a6))))"
    A = f"(sqrt (+ (+ (* {Ar} {Ar}) (* {Ai} {Ai})) a6))"; R = f"(/ {A} {S})"
    g = f"(/ (* (* -2.0f a4) (- a3 {R})) a5)"
    z0, z1 = "(idx a0 (- item1 (% item1 2)))", "(idx a0 (+ (- item1 (% item1 2)) 1))"
    zn = f"(sqrt (+ (+ (* {z0} {z0}) (* {z1} {z1})) a6))"
    Ac = f"(sel (== {c} 0) {Ar} {Ai})"; zc = "(idx a0 item1)"
    w = f"(* {g} (- (/ (/ {Ac} {A}) {S}) (* (/ {A} (* {S} {S})) (/ {zc} {zn}))))"
    return f"(map a0 (sel (< {R} a3) {w} 0.0f))"

def pstat_eq():
    """port_fwd:1388 per row of r [N·K]: [a1, a2, ds, mx, z] — a1 = first max, a2 = first max among k ≠ a1, z = Σ exp(r − mx). args: r, K"""
    n = "(/ item1 5)"; w = "(% item1 5)"; R = lambda k: f"(idx a0 (+ (* {n} a1) {k}))"
    a1 = f"(fold (range 0 a1) 0 (sel (> {R('item2')} {R('acc2.0')}) item2 acc2.0))"
    a1b = f"(fold (range 0 a1) 0 (sel (> {R('item3')} {R('acc3.0')}) item3 acc3.0))"
    a2 = f"(fold (range 0 a1) -1 (sel (== item2 {a1b}) acc2.0 (sel (< acc2.0 0) item2 (sel (> {R('item2')} {R('acc2.0')}) item2 acc2.0))))"
    mx = R(a1); ds = f"(sel (> a1 1) (- {R(a1)} {R(a2)}) {R(a1)})"
    z = f"(fold (range 0 a1) 0.0f (+ acc2.0 (exp (- {R('item2')} {R(a1b)}))))"
    return f"(map (range 0 (* (/ (len a0) a1) 5)) (sel (== {w} 0) {a1} (sel (== {w} 1) {a2} (sel (== {w} 2) {ds} (sel (== {w} 3) {mx} {z})))))"

def pdgw_eq():
    n = "(/ item1 2)"; c = "(% item1 2)"; kd = f"(idx a5 {n})"; pp = f"(idx a6 {n})"
    valid = f"(and (and (>= {kd} 0) (< {kd} a9)) (>= {pp} 0))"
    dot = lambda A, B: f"(fold (range 0 a10) 0.0f (+ acc2.0 (* (idx {A} (+ (* {n} a10) item2)) {B})))"
    bk = f"(idx a7 {kd})"; dlp = f"(idx a8 {n})"; g = f"(idx a4 (* {n} 2))"; ww = f"(idx a4 (+ (* {n} 2) 1))"
    dg = f"(+ {dot('a0', f'(idx a1 (+ (* {n} a10) item2))')} (* (* {dlp} {bk}) {ww}))"
    dw = f"(+ {dot('a2', f'(idx a3 (+ (* {pp} a10) item2))')} (* (* {dlp} {bk}) {g}))"
    return f"(map (range 0 (* (len a5) 2)) (sel {valid} (sel (== {c} 0) {dg} {dw}) 0.0f))"

def pdr_eq():
    n = "(/ item1 a6)"; k = "(% item1 a6)"; kd = f"(idx a4 {n})"; pp = f"(idx a5 {n})"
    valid = f"(and (and (>= {kd} 0) (< {kd} a6)) (>= {pp} 0))"
    st = lambda j: f"(idx a1 (+ (* {n} 5) {j}))"; sk = lambda kk: f"(/ (exp (- (idx a0 (+ (* {n} a6) {kk})) {st(3)})) {st(4)})"
    g = f"(idx a2 (* {n} 2))"; dg = f"(idx a3 (* {n} 2))"; dw = f"(idx a3 (+ (* {n} 2) 1))"
    dds = f"(/ (* (* {dg} {g}) (- 1.0f {g})) a7)"
    soft = f"(* (* {dw} {sk(k)}) (- (sel (== {k} {kd}) 1.0f 0.0f) {sk(kd)}))"
    gate = f"(- (sel (== {k} {st(0)}) {dds} 0.0f) (sel (== {k} {st(1)}) {dds} 0.0f))"
    ce = f"(/ (* a8 (- {sk(k)} (sel (== {k} {kd}) 1.0f 0.0f))) a9)"
    return f"(map (range 0 (* (len a4) a6)) (sel {valid} (sel (== a10 0) (+ {soft} {gate}) {ce}) 0.0f))"

def head_stats_eq():
    """omni_train.cpp:897 head (mode 0, no pointer / copy / avoid / spark): per row mx, z = Σ_v exp(l − mx), loss = mx + ln z − l[y] (y < 0: 0).
    args: L [N·V], y, N, V → 3 per row"""
    n = "(/ item1 3)"; w = "(% item1 3)"; row = f"(* {n} a3)"
    mx2 = f"(fold (range 0 a3) (neg 1e30f) (max acc2.0 (idx a0 (+ {row} item2))))"
    mx3 = f"(fold (range 0 a3) (neg 1e30f) (max acc3.0 (idx a0 (+ {row} item3))))"
    z = f"(fold (range 0 a3) 0.0f (+ acc2.0 (exp (- (idx a0 (+ {row} item2)) {mx3}))))"
    t = f"(idx a1 {n})"
    loss = f"(sel (< {t} 0) 0.0f (- (+ {mx2} (ln {z})) (idx a0 (+ {row} {t}))))"
    return f"(map (range 0 (* a2 3)) (sel (== {w} 0) {mx2} (sel (== {w} 1) {z} {loss})))"

def head_stats_mask_eq():
    """head_stats_eq with a row mask (1 = in this head): the final head with depth routing (rows that exited are y = −1 there) and the
    blocks' local read-outs (their selected rows). args: L, y, mask, N, V → 3 per row"""
    n = "(/ item1 3)"; w = "(% item1 3)"; row = f"(* {n} a4)"
    mx2 = f"(fold (range 0 a4) (neg 1e30f) (max acc2.0 (idx a0 (+ {row} item2))))"
    mx3 = f"(fold (range 0 a4) (neg 1e30f) (max acc3.0 (idx a0 (+ {row} item3))))"
    z = f"(fold (range 0 a4) 0.0f (+ acc2.0 (exp (- (idx a0 (+ {row} item2)) {mx3}))))"
    t = f"(idx a1 {n})"
    loss = f"(sel (or (< {t} 0) (<= (idx a2 {n}) 0.0f)) 0.0f (- (+ {mx2} (ln {z})) (idx a0 (+ {row} {t}))))"
    return f"(map (range 0 (* a3 3)) (sel (== {w} 0) {mx2} (sel (== {w} 1) {z} {loss})))"

def rtcheck_eq():
    """route_check:1857 after block l: a row still running (ex = AL), with no port offer, and settled (cos(x_out, x_in) ≥ sat) reads out
    through block l's own norm + the tied codebook; exact top-2 margin (ties → 0) ≥ θ → it leaves here (ex = l).
    args: logits [N·V], xo, xi (N·D), ex, pkind, V, D, l, AL, theta, sat, portrows → ex′"""
    n = "item1"; zr = lambda v: f"(idx a0 (+ (* {n} a5) {v}))"
    mx = f"(fold (range 0 a5) (neg 1e30f) (max acc2.0 {zr('item2')}))"
    mx3 = f"(fold (range 0 a5) (neg 1e30f) (max acc3.0 {zr('item3')}))"
    ties = f"(fold (range 0 a5) 0 (+ acc2.0 (sel (== {zr('item2')} {mx3}) 1 0)))"
    s2 = f"(sel (> {ties} 1) {mx} (fold (range 0 a5) (neg 1e30f) (max acc2.0 (sel (== {zr('item2')} {mx3}) (neg 1e30f) {zr('item2')}))))"
    dot = lambda A, B: f"(fold (range 0 a6) 0.0f (+ acc2.0 (* (idx {A} (+ (* {n} a6) item2)) (idx {B} (+ (* {n} a6) item2)))))"
    cos = f"(/ {dot('a1', 'a2')} (sqrt (max (* {dot('a1', 'a1')} {dot('a2', 'a2')}) 1e-30f)))"
    run = f"(and (and (== (idx a3 {n}) a8) (not (and (!= a11 0) (>= (idx a4 {n}) 0)))) (or (<= a10 0.0f) (>= {cos} a10)))"
    return f"(map a3 (sel (and {run} (>= (- {mx} {s2}) a9)) a7 (idx a3 {n})))"

def hdl_avoid_eq():
    n = "(/ item1 a7)"; v = "(% item1 a7)"; t = f"(idx a2 {n})"; av = f"(idx a6 {n})"; nrm = "(idx a5 0)"
    mx = f"(idx a1 (* {n} 3))"; z = f"(idx a1 (+ (* {n} 3) 1))"
    ul = f"(and (and (>= {av} 0) (< {av} a7)) (!= {av} {t}))"
    pa = f"(/ (exp (- (idx a0 (+ (* {n} a7) {av})) {mx})) {z})"
    ulc = f"(sel {ul} (/ (* a8 {pa}) (max (- 1.0f {pa}) 1e-5f)) 0.0f)"
    g = (f"(+ (- (* (exp (- (idx a0 item1) {mx})) (/ (- 1.0f {ulc}) (* {z} {nrm}))) (sel (== {v} {t}) (/ 1.0f {nrm}) 0.0f)) "
         f"(sel (and {ul} (== {v} {av})) (/ {ulc} {nrm}) 0.0f))")
    return f"(map a0 (sel (or (or (< {t} 0) (> (idx a3 {n}) 0.0f)) (<= (idx a4 {n}) 0.0f)) 0.0f {g}))"

def head_stats_avoid_eq():
    """head_stats_mask_eq + avoid (study / sleep, omni_train.cpp:953): a row with av ≥ 0, av < V, av ≠ y adds −α·ln(max(1 − p_av, 1e-5)) to its
    loss. args: L, y, mask, av, N, V, alpha → [mx, z, loss] per row"""
    n = "(/ item1 3)"; w = "(% item1 3)"; row = f"(* {n} a5)"
    mx2 = f"(fold (range 0 a5) (neg 1e30f) (max acc2.0 (idx a0 (+ {row} item2))))"
    mx3 = f"(fold (range 0 a5) (neg 1e30f) (max acc3.0 (idx a0 (+ {row} item3))))"
    z = f"(fold (range 0 a5) 0.0f (+ acc2.0 (exp (- (idx a0 (+ {row} item2)) {mx3}))))"
    t = f"(idx a1 {n})"; av = f"(idx a3 {n})"
    ul = f"(and (and (>= {av} 0) (< {av} a5)) (!= {av} {t}))"
    pa = f"(/ (exp (- (idx a0 (+ {row} {av})) {mx2})) {z})"
    u = f"(sel {ul} (* (neg a6) (ln (max (- 1.0f {pa}) 1e-5f))) 0.0f)"
    loss = f"(sel (or (< {t} 0) (<= (idx a2 {n}) 0.0f)) 0.0f (+ (- (+ {mx2} (ln {z})) (idx a0 (+ {row} {t}))) {u}))"
    return f"(map (range 0 (* a4 3)) (sel (== {w} 0) {mx2} (sel (== {w} 1) {z} {loss})))"

SPV = "(sel (> (idx a{r} 0) 20.0f) (idx a{r} 0) (ln (+ 1.0f (exp (idx a{r} 0)))))"   # softplus of a raw scalar param
K = {
    # name: (args, equation, template, batch)
    "gather":   (["f32list", "list", "int", "int"], "(map (range 0 (* a2 a3)) (idx a0 (+ (* (idx a1 (/ item1 a3)) a3) (% item1 a3))))", "T0", False),
    # rms_fwd (:356) and the BitLinear's own RMSNorm (bl_fwd :456): r = 1/sqrt(Σx²/D + EPS), then y = x·r·g
    "rstat":    (["f32list", "int", "int"], f"(map (range 0 a1) (/ 1.0f (sqrt (+ (/ (fold (range 0 a2) 0.0f (+ acc2.0 (* (idx a0 (+ (* item1 a2) item2)) (idx a0 (+ (* item1 a2) item2))))) a2) {EPS}))))", "T0", False),
    "rapply":   (["f32list", "f32list", "f32list", "int", "int"], "(map (range 0 (* a3 a4)) (* (* (idx a0 item1) (idx a1 (/ item1 a4))) (idx a2 (% item1 a4))))", "T0", False),
    # bl_fwd (:456): gg = 127/max(max|x·r|, 1e-5); q = clamp(nearbyint(x·r·gg), −128, 127); y = acc·(s/gg) [+ base]
    "actg":     (["f32list", "f32list", "int", "int"], "(map (range 0 a2) (/ 127.0f (max (fold (range 0 a3) 0.0f (max acc2.0 (abs (* (idx a0 (+ (* item1 a3) item2)) (idx a1 item1))))) 1e-5f)))", "T0", False),
    "actq":     (["f32list", "f32list", "f32list", "int", "int"], f"(map (range 0 (* a3 a4)) (max (neg 128.0f) (min 127.0f (- (+ (* (* (idx a0 item1) (idx a1 (/ item1 a4))) (idx a2 (/ item1 a4))) {RND}) {RND}))))", "T0", False),
    "xq":       (["f32list", "f32list", "f32list", "int", "int"], f"(map (range 0 (* a3 a4)) (* (max (neg 128.0f) (min 127.0f (- (+ (* (* (idx a0 item1) (idx a1 (/ item1 a4))) (idx a2 (/ item1 a4))) {RND}) {RND}))) (/ 1.0f (idx a2 (/ item1 a4)))))", "T0", False),
    "blout":    (["f32list", "f32list", "f32list", "f32list", "int", "int", "int"], "(map (range 0 (* a4 a5)) (+ (sel (== a6 1) (idx a3 item1) 0.0f) (* (idx a0 item1) (/ (idx a2 0) (idx a1 (/ item1 a5))))))", "T0", False),
    # bl_quant (:438) mode 0: trits t = clamp(nearbyint(w/s), −1, 1), float view wf = t·s (s from absmean.spv, float64 sum as the engine)
    "tq":       (["f32list", "f32list"], f"(map a0 (max (neg 1.0f) (min 1.0f (- (+ (/ (idx a0 item1) (idx a1 0)) {RND}) {RND}))))", "T0", False),
    "wf":       (["f32list", "f32list"], f"(map a0 (* (max (neg 1.0f) (min 1.0f (- (+ (/ (idx a0 item1) (idx a1 0)) {RND}) {RND}))) (idx a1 0)))", "T0", False),
    "rot":      (["f32list", "f32list", "f32list", "list", "list", "int", "int", "int", "int", "int"], rot_eq(), "T0", False),
    "rot25":    (["f32list", "f32list", "f32list", "list", "list", "list", "list", "int", "int", "int", "int", "int", "int"], rot25_eq(), "T0", False),
    "split3":   (["f32list", "int", "int", "int", "int", "int"], split_eq(3), "T0", False),
    "split1":   (["f32list", "int", "int", "int", "int", "int"], split_eq(1), "T0", False),
    "merge":    (["f32list", "int", "int", "int", "int"], merge_eq(), "T0", False),
    "merge3":   (["f32list", "f32list", "f32list", "int", "int", "int", "int"], merge3_eq(), "T0", False),
    # attention per (b, h) — batched over bh (row axis): S = Q·Kᵀ, softmax stats, P, O = P·V; backward: dP = dY·Vᵀ, D_i, dS, dQ, dK, dV
    "qkT":      (["f32list", "f32list", "int", "int"], "(map (range 0 (* a2 a2)) (fold (range 0 a3) 0.0f (+ acc2.0 (* (idx a0 (+ (* (/ item1 a2) a3) item2)) (idx a1 (+ (* (% item1 a2) a3) item2))))))", "T0", True),
    "astats":   (["f32list", "int", "f32"], attn_stats_eq(), "T0", True),
    "aprob":    (["f32list", "f32list", "int", "f32"], "(map (range 0 (* a2 a2)) (sel (<= (% item1 a2) (/ item1 a2)) (* (exp (- (* (idx a0 item1) a3) (idx a1 (* (/ item1 a2) 3)))) (idx a1 (+ (* (/ item1 a2) 3) 1))) 0.0f))", "T0", True),
    "pv":       (["f32list", "f32list", "int", "int"], "(map (range 0 (* a2 a3)) (fold (range 0 a2) 0.0f (+ acc2.0 (* (idx a0 (+ (* (/ item1 a3) a2) item2)) (idx a1 (+ (* item2 a3) (% item1 a3)))))))", "T0", True),
    "ptv":      (["f32list", "f32list", "int", "int"], "(map (range 0 (* a2 a3)) (fold (range 0 a2) 0.0f (+ acc2.0 (* (idx a0 (+ (* item2 a2) (/ item1 a3))) (idx a1 (+ (* item2 a3) (% item1 a3)))))))", "T0", True),
    "apb":      (["f32list", "f32list", "int", "f32"], "(map (range 0 (* a2 a2)) (sel (<= (% item1 a2) (/ item1 a2)) (exp (- (* (idx a0 item1) a3) (idx a1 (+ (* (/ item1 a2) 3) 2)))) 0.0f))", "T0", True),
    "adi":      (["f32list", "f32list", "int", "int"], "(map (range 0 a2) (fold (range 0 a3) 0.0f (+ acc2.0 (* (idx a0 (+ (* item1 a3) item2)) (idx a1 (+ (* item1 a3) item2))))))", "T0", True),
    "ads":      (["f32list", "f32list", "f32list", "int", "f32"], "(map (range 0 (* a3 a3)) (sel (<= (% item1 a3) (/ item1 a3)) (* (* (idx a0 item1) (- (idx a1 item1) (idx a2 (/ item1 a3)))) a4) 0.0f))", "T0", True),
    "relu2":    (["f32list"], "(map a0 (sel (> (idx a0 item1) 0.0f) (* (idx a0 item1) (idx a0 item1)) 0.0f))", "T0", False),
    "relu2b":   (["f32list", "f32list"], "(map a0 (* (idx a0 item1) (sel (> (idx a1 item1) 0.0f) (* 2.0f (idx a1 item1)) 0.0f)))", "T0", False),
    "hstats":   (["f32list", "list", "int", "int"], head_stats_eq(), "T0", False),
    # head backward (:897): dl = exp(l − mx)·(1/(z·N)), dl[y] −= 1/N; rows with y < 0 carry none
    "hdl":      (["f32list", "f32list", "list", "int", "int"], "(map (range 0 (* a3 a4)) (sel (< (idx a2 (/ item1 a4)) 0) 0.0f (- (* (exp (- (idx a0 item1) (idx a1 (* (/ item1 a4) 3)))) (/ 1.0f (* (idx a1 (+ (* (/ item1 a4) 3) 1)) a3))) (sel (== (% item1 a4) (idx a2 (/ item1 a4))) (/ 1.0f a3) 0.0f))))", "T0", False),
    "lsum":     (["f32list", "int"], "(map (range 0 1) (/ (fold (range 0 a1) 0.0f (+ acc2.0 (idx a0 (+ (* item2 3) 2)))) a1))", "T0", False),
    # rms_bwd (:365): dxh = dy·g; s = (dxh·x)/D; dx = [dx +] r·dxh − r³·x·s; dg += Σ_n dy·x·r
    "rbs":      (["f32list", "f32list", "f32list", "int", "int"], "(map (range 0 a3) (/ (fold (range 0 a4) 0.0f (+ acc2.0 (* (* (idx a0 (+ (* item1 a4) item2)) (idx a1 item2)) (idx a2 (+ (* item1 a4) item2))))) a4))", "T0", False),
    "rbx":      (["f32list", "f32list", "f32list", "f32list", "f32list", "f32list", "int", "int"], "(map (range 0 (* a6 a7)) (+ (idx a0 item1) (- (* (idx a4 (/ item1 a7)) (* (idx a1 item1) (idx a2 (% item1 a7)))) (* (* (* (* (idx a4 (/ item1 a7)) (idx a4 (/ item1 a7))) (idx a4 (/ item1 a7))) (idx a3 item1)) (idx a5 (/ item1 a7))))))", "T0", False),
    "rbg":      (["f32list", "f32list", "f32list", "f32list", "int", "int"], "(map (range 0 a5) (+ (idx a0 item1) (fold (range 0 a4) 0.0f (+ acc2.0 (* (* (idx a1 (+ (* item2 a5) item1)) (idx a2 (+ (* item2 a5) item1))) (idx a3 item2))))))", "T0", False),
    # bl_bwd (:580): da = dy·wf (GEMM); s = (da·x)/in; dx = r·da − r³·x·s (no accumulate: block_bwd's fresh buffers)
    "bs":       (["f32list", "f32list", "int", "int"], "(map (range 0 a2) (/ (fold (range 0 a3) 0.0f (+ acc2.0 (* (idx a0 (+ (* item1 a3) item2)) (idx a1 (+ (* item1 a3) item2))))) a3))", "T0", False),
    "bx":       (["f32list", "f32list", "f32list", "f32list", "int", "int"], "(map (range 0 (* a4 a5)) (- (* (idx a2 (/ item1 a5)) (idx a0 item1)) (* (* (* (* (idx a2 (/ item1 a5)) (idx a2 (/ item1 a5))) (idx a2 (/ item1 a5))) (idx a1 item1)) (idx a3 (/ item1 a5)))))", "T0", False),
    # forward_backward (:2196): G[x[n]] += dx[n] in n order (tokens grouped by a stable sort: ord + per-token start), starting from G
    # opt_step (:2304) AdamW, sc = [coef, lr, wd, b1, b2, step_size, sbc2, eps]: g' = g·coef; m = b1·m + (1−b1)·g'; v = b2·v + (1−b2)·g'·g';
    # w = (w − lr·wd·w) − step_size·m / (√v / sbc2 + eps)
    "adam_m":   (["f32list", "f32list", "f32list"], "(map a0 (+ (* (idx a2 3) (idx a0 item1)) (* (- 1.0f (idx a2 3)) (* (idx a1 item1) (idx a2 0)))))", "T0", False),
    "adam_v":   (["f32list", "f32list", "f32list"], "(map a0 (+ (* (idx a2 4) (idx a0 item1)) (* (* (- 1.0f (idx a2 4)) (* (idx a1 item1) (idx a2 0))) (* (idx a1 item1) (idx a2 0)))))", "T0", False),
    "adam_w":   (["f32list", "f32list", "f32list", "f32list"], "(map a0 (- (- (idx a0 item1) (* (* (idx a3 1) (idx a3 2)) (idx a0 item1))) (/ (* (idx a3 5) (idx a1 item1)) (+ (/ (sqrt (idx a2 item1)) (idx a3 6)) (idx a3 7)))))", "T0", False),
    # OMNI-RENDER-GPU-0 § Model form (J 10-09 option 3: the cyclone holds the model C, each harness its delta Δ): W_h = C + Δ_h at the step's
    # start (C shared by every replica: stride 0); after AdamW and the cyclone's hub_mean (C = mean of the updated models W'_h), each harness
    # keeps Δ_h = (1 − K)·(W'_h − C) — so C + Δ_h = the hub pull W' + K·(mean − W'), with C stored once
    "wsum":     (["f32list", "f32list"], "(map a1 (+ (idx a0 item1) (idx a1 item1)))", "T0", False),
    "dset":     (["f32list", "f32list", "f32"], "(map a0 (* (- 1.0f a2) (- (idx a0 item1) (idx a1 item1))))", "T0", False),
    # GROW-RUN-0 G2 — T25-REACTOR attention plates (PLATES_ATTN=1, omni_train.cpp:1165–1248): dense attention inside each row (row-bounded
    # softmax) + one plate per page read in one step. The page sweep (S += φ(k)vᵀ when a row ends; y = Sᵀφ(q) / zᵀφ(q)) is masked linear
    # attention over the window: A_ij = φq_i·φk_j where j lies in an EARLIER row and in the same page, y_i = Σ_j A_ij v_j / (Σ_j A_ij + 1e-6)
    "astatsR":  (["f32list", "list", "int", "f32"], attn_stats_row_eq(), "T0", True),
    "aprobR":   (["f32list", "f32list", "list", "int", "f32"], "(map (range 0 (* a3 a3)) (sel (and (<= (% item1 a3) (/ item1 a3)) (>= (% item1 a3) (idx a2 (/ item1 a3)))) (* (exp (- (* (idx a0 item1) a4) (idx a1 (* (/ item1 a3) 3)))) (idx a1 (+ (* (/ item1 a3) 3) 1))) 0.0f))", "T0", True),
    "apbR":     (["f32list", "f32list", "list", "int", "f32"], "(map (range 0 (* a3 a3)) (sel (and (<= (% item1 a3) (/ item1 a3)) (>= (% item1 a3) (idx a2 (/ item1 a3)))) (exp (- (* (idx a0 item1) a4) (idx a1 (+ (* (/ item1 a3) 3) 2)))) 0.0f))", "T0", True),
    "pbucket":  (["f32list", "f32list", "list", "int", "int", "int", "int", "int"], plate_bucket_eq(), "T0", False),
    "pphi":     (["f32list"], "(map a0 (sel (> (idx a0 item1) 0.0f) (+ (idx a0 item1) 1.0f) (exp (idx a0 item1))))", "T0", False),
    "pscore":   (["f32list", "f32list", "f32list", "f32list", "list", "int", "int"], "(map (range 0 (* a5 a5)) (sel (and (< (% item1 a5) (idx a4 (/ item1 a5))) (== (idx a3 (% item1 a5)) (idx a2 (/ item1 a5)))) (fold (range 0 a6) 0.0f (+ acc2.0 (* (idx a0 (+ (* (/ item1 a5) a6) item2)) (idx a1 (+ (* (% item1 a5) a6) item2))))) 0.0f))", "T0", True),
    "pden":     (["f32list", "int"], "(map (range 0 a1) (sel (> (fold (range 0 a1) 0.0f (+ acc2.0 (idx a0 (+ (* item1 a1) item2)))) 0.0f) (+ (fold (range 0 a1) 0.0f (+ acc2.0 (idx a0 (+ (* item1 a1) item2)))) 1e-6f) 0.0f))", "T0", True),
    "pnorm":    (["f32list", "f32list", "int"], "(map a0 (sel (> (idx a1 (/ item1 a2)) 0.0f) (* (idx a0 item1) (/ 1.0f (idx a1 (/ item1 a2)))) 0.0f))", "T0", True),
    "pc":       (["f32list", "f32list", "f32list", "int"], "(map a2 (sel (> (idx a2 item1) 0.0f) (/ (fold (range 0 a3) 0.0f (+ acc2.0 (* (idx a0 (+ (* item1 a3) item2)) (idx a1 (+ (* item1 a3) item2))))) (idx a2 item1)) 0.0f))", "T0", True),
    "pg":       (["f32list", "f32list", "f32list", "f32list", "int"], "(map a0 (sel (> (idx a0 item1) 0.0f) (- (/ (idx a1 item1) (idx a2 (/ item1 a4))) (idx a3 (/ item1 a4))) 0.0f))", "T0", True),
    "pp":       (["f32list", "f32list", "int"], "(map a0 (sel (> (idx a0 item1) 0.0f) (/ (idx a0 item1) (idx a1 (/ item1 a2))) 0.0f))", "T0", True),
    "pdphi":    (["f32list", "f32list", "f32list"], "(map a0 (+ (idx a0 item1) (* (idx a1 item1) (sel (> (idx a2 item1) 0.0f) 1.0f (exp (idx a2 item1))))))", "T0", False),
    # GROW-RUN-0 G2 — spark skip (LEARN_SPARK, omni_train.cpp:932): a row whose target is the UNIQUE top-1 with margin > spark gets no head
    # gradient (its loss still counts). args: logits [N·V], y, hst, N, V, spark → 1.0 skip / 0.0
    "hspark":   (["f32list", "list", "f32list", "int", "int", "f32"], "(map (range 0 a3) (sel (< (idx a1 item1) 0) 0.0f (sel (and (and (== (idx a0 (+ (* item1 a4) (idx a1 item1))) (idx a2 (* item1 3))) (== (fold (range 0 a4) 0 (+ acc2.0 (sel (and (!= item2 (idx a1 item1)) (== (idx a0 (+ (* item1 a4) item2)) (idx a2 (* item1 3)))) 1 0))) 0)) (> (- (idx a2 (* item1 3)) (fold (range 0 a4) (neg 1e30f) (max acc2.0 (sel (== item2 (idx a1 item1)) (neg 1e30f) (idx a0 (+ (* item1 a4) item2)))))) a5)) 1.0f 0.0f)))", "T0", False),
    # head gradient with the skip mask: dl = 0 on masked (y < 0) or skipped rows. args: logits, hst, y, skip, N, V
    "hdlx":     (["f32list", "f32list", "list", "f32list", "int", "int"], "(map (range 0 (* a4 a5)) (sel (or (< (idx a2 (/ item1 a5)) 0) (> (idx a3 (/ item1 a5)) 0.0f)) 0.0f (- (* (exp (- (idx a0 item1) (idx a1 (* (/ item1 a5) 3)))) (/ 1.0f (* (idx a1 (+ (* (/ item1 a5) 3) 1)) a4))) (sel (== (% item1 a5) (idx a2 (/ item1 a5))) (/ 1.0f a4) 0.0f))))", "T0", False),
    # P3 (forward_backward:2155): a confirmed row (y ≥ 0, row loss < −ln p) is DEAD except on a full step (step mod full == 0).
    # args: hst, y, stepv [step], lmax, full → 1.0 live / 0.0 dead
    "p3mask":   (["f32list", "list", "list", "f32", "int"], "(map (range 0 (len a1)) (sel (or (== (% (idx a2 0) a4) 0) (or (< (idx a1 item1) 0) (>= (idx a0 (+ (* item1 3) 2)) a3))) 1.0f 0.0f))", "T0", False),
    # rows times a per-row mask: out[n·W + i] = src[n·W + i]·mask[n]. args: src, mask, W
    "rowmask":  (["f32list", "f32list", "int"], "(map a0 (* (idx a0 item1) (idx a1 (/ item1 a2))))", "T0", False),
    # GROW-RUN-0 G2 — harmony (HARM=1, omni_train.cpp:735 hz, :827 harm_weights, :785 attn_bwd hw): rings HR = 37·41·43·47·53, tables
    # tc / ts = cos / sin(2πq/p) concatenated (offsets ro, primes rp). o = (i − j) mod p.
    # harmz: per (bh row, i, ring r, c) z = Σ_{j≤i} P_ij·(cos | sin)(o). args: P, tc, ts, ro, rp, T → T·10 per row
    "harmz":    (["f32list", "f32list", "f32list", "list", "list", "int"], "(map (range 0 (* a5 10)) (fold (range 0 (+ (/ item1 10) 1)) 0.0f (+ acc2.0 (* (idx a0 (+ (* (/ item1 10) a5) item2)) (sel (== (% item1 2) 0) (idx a1 (+ (idx a3 (/ (% item1 10) 2)) (% (- (/ item1 10) item2) (idx a4 (/ (% item1 10) 2))))) (idx a2 (+ (idx a3 (/ (% item1 10) 2)) (% (- (/ item1 10) item2) (idx a4 (/ (% item1 10) 2))))))))))", "T0", True),
    # harmw: dℓ/dz for every (b, h, i, r, c) from the heads' z on that ring: R = |Σ_h z| / Σ_h |z|; below κ: g = −2λ(κ − R)/norm,
    # w = g·((A_c / A) / S − (A / S²)(z_c / |z|)). args: hz [B·H·T·10], H, T, kappa, lam, norm, eps
    "harmw":    (["f32list", "int", "int", "f32", "f32", "f32", "f32"], harm_w_eq(), "T0", False),
    # harmdh: Dh_i = Σ_{j≤i} P_ij c_ij, c_ij = Σ_r w_r,re·cos(o) + w_r,im·sin(o). args: P, hw (T·10 per row), tc, ts, ro, rp, T → T per row
    "harmdh":   (["f32list", "f32list", "f32list", "f32list", "list", "list", "int"], f"(map (range 0 a6) (fold (range 0 (+ item1 1)) 0.0f (+ acc2.0 (* (idx a0 (+ (* item1 a6) item2)) {harm_c_eq('item1', 'item2', 'a1', 'a2', 'a3', 'a4', 'a5', 3)}))))", "T0", True),
    # adsH: dS_ij = P_ij (dP_ij − D_i + c_ij − Dh_i)·sc (j ≤ i). args: P, dP, Di, hw, Dh, tc, ts, ro, rp, T, sc
    "adsH":     (["f32list", "f32list", "f32list", "f32list", "f32list", "f32list", "f32list", "list", "list", "int", "f32"], f"(map (range 0 (* a9 a9)) (sel (<= (% item1 a9) (/ item1 a9)) (* (* (idx a0 item1) (- (+ (- (idx a1 item1) (idx a2 (/ item1 a9))) {harm_c_eq('(/ item1 a9)', '(% item1 a9)', 'a3', 'a5', 'a6', 'a7', 'a8', 2)}) (idx a4 (/ item1 a9)))) a10) 0.0f))", "T0", True),
    # GROW-RUN-0 G2 — context copy pointer (COPY, omni_train.cpp:858 copy_fwd / :872 copy_bwd / :921 head): β = softplus(raw), g = σ(gw·hf + gb)
    "cpgate":   (["f32list", "f32list", "f32list", "int"], "(map (range 0 (/ (len a0) a3)) (/ 1.0f (+ 1.0f (exp (neg (+ (fold (range 0 a3) 0.0f (+ acc2.0 (* (idx a1 item2) (idx a0 (+ (* item1 a3) item2))))) (idx a2 0)))))))", "T0", False),
    # logits[n, v] += β·g_n·Σ_{u ≤ t, x_u = v} a[n, u] — the earlier positions holding v found through the batch's token grouping (eord / est)
    # args: logits, A [N·T], g, braw, eord, est, T, V
    "cpadd":    (["f32list", "f32list", "f32list", "f32list", "list", "list", "int", "int"], "(map a0 (+ (idx a0 item1) (* (* SP3 (idx a2 (/ item1 a7))) (fold (range (idx a5 (% item1 a7)) (idx a5 (+ (% item1 a7) 1))) 0.0f (+ acc2.0 (sel (and (== (/ (idx a4 item2) a6) (/ (/ item1 a7) a6)) (<= (% (idx a4 item2) a6) (% (/ item1 a7) a6))) (idx a1 (+ (* (/ item1 a7) a6) (% (idx a4 item2) a6))) 0.0f))))))".replace("SP3", SPV.format(r=3)), "T0", False),
    # da[n, u] = (u ≤ t) β·g_n·dl[n, x_u]. args: dl, g, braw, x, T, V → N·T
    "cpda":     (["f32list", "f32list", "f32list", "list", "int", "int"], "(map (range 0 (* (len a1) a4)) (sel (<= (% item1 a4) (% (/ item1 a4) a4)) (* (* SP2 (idx a1 (/ item1 a4))) (idx a0 (+ (* (/ item1 a4) a5) (idx a3 (+ (* (/ (/ item1 a4) a4) a4) (% item1 a4)))))) 0.0f))".replace("SP2", SPV.format(r=2)), "T0", False),
    # dsum[n] = Σ_{u ≤ t} a[n, u]·dl[n, x_u]. args: A, dl, x, T, V → N
    "cpdsum":   (["f32list", "f32list", "list", "int", "int"], "(map (range 0 (/ (len a0) a3)) (fold (range 0 (+ (% item1 a3) 1)) 0.0f (+ acc2.0 (* (idx a0 (+ (* item1 a3) item2)) (idx a1 (+ (* item1 a4) (idx a2 (+ (* (/ item1 a3) a3) item2))))))))", "T0", False),
    # per row of width W: Σ_j A·B. args: A, B, W
    "rdot":     (["f32list", "f32list", "int"], "(map (range 0 (/ (len a0) a2)) (fold (range 0 a2) 0.0f (+ acc2.0 (* (idx a0 (+ (* item1 a2) item2)) (idx a1 (+ (* item1 a2) item2))))))", "T0", False),
    # dz[n] = β·dsum[n]·g(1 − g). args: dsum, g, braw
    "cpdz":     (["f32list", "f32list", "f32list"], "(map a0 (* (* SP2 (idx a0 item1)) (* (idx a1 item1) (- 1.0f (idx a1 item1)))))".replace("SP2", SPV.format(r=2)), "T0", False),
    # out[d] = Σ_n s[n]·X[n·D + d]. args: s, X, D
    "colsum":   (["f32list", "f32list", "int"], "(map (range 0 a2) (fold (range 0 (len a0)) 0.0f (+ acc2.0 (* (idx a0 item2) (idx a1 (+ (* item2 a2) item1))))))", "T0", False),
    # out = dst + s[n]·w[d]. args: dst, s, w, D
    "rowaxpy":  (["f32list", "f32list", "f32list", "int"], "(map a0 (+ (idx a0 item1) (* (idx a1 (/ item1 a3)) (idx a2 (% item1 a3)))))", "T0", False),
    "vsum":     (["f32list"], "(fold (range 0 (len a0)) 0.0f (+ acc1.0 (idx a0 item1)))", "T0", False),
    # dβ_raw = Σ_n g_n·dsum_n · σ(raw). args: g, dsum, braw
    "cpdb":     (["f32list", "f32list", "f32list"], "(* (fold (range 0 (len a0)) 0.0f (+ acc1.0 (* (idx a0 item1) (idx a1 item1)))) (/ 1.0f (+ 1.0f (exp (neg (idx a2 0))))))", "T0", False),
    # GROW-RUN-0 G2 — the library port (om_set_port K plates, omni_train.cpp:1379 port_fwd / :1410 port_bwd) + pointer (POINTER) + router CE.
    # r = W·mid + b [N·K]; per row a1 / a2 = top-2 (first max), ds = r_a1 − r_a2, mx, z = Σ exp(r − mx); valid = kind ∈ [0, K) and prop ≥ 0
    "addbias":  (["f32list", "f32list", "int"], "(map a0 (+ (idx a0 item1) (idx a1 (% item1 a2))))", "T0", False),
    "pstat":    (["f32list", "int"], pstat_eq(), "T0", False),
    # [g, w] per row: g = σ((ds − θ)/τ); w = valid ? exp(r_kind − mx)/z : 0. args: r, st, kind, prop, K, theta, tau
    # hard port (decode / eval, om_set_port_tau(.., hard=1); omni_train.cpp:2392): router one-hot at a1, gate = ds ≥ θ ? 1 : 0. args as pgw (τ unused)
    "pgwH":     (["f32list", "f32list", "list", "list", "int", "f32", "f32"], "(map (range 0 (* (/ (len a0) a4) 2)) (sel (== (% item1 2) 0) (sel (>= (idx a1 (+ (* (/ item1 2) 5) 2)) a5) 1.0f 0.0f) (sel (and (and (>= (idx a2 (/ item1 2)) 0) (< (idx a2 (/ item1 2)) a4)) (>= (idx a3 (/ item1 2)) 0)) (sel (== (idx a2 (/ item1 2)) (idx a1 (* (/ item1 2) 5))) 1.0f 0.0f) 0.0f)))", "T0", False),
    # per-token top-1 (the engine's tok_hit: logit[y] == the row max; y < 0 → 0). args: logits, y, hst, N, V
    "thit":     (["f32list", "list", "f32list", "int", "int"], "(map (range 0 a3) (sel (< (idx a1 item1) 0) 0.0f (sel (== (idx a0 (+ (* item1 a4) (idx a1 item1))) (idx a2 (* item1 3))) 1.0f 0.0f)))", "T0", False),
    # ── GPU DECODE (GROW-RUN-0): one token per station, each station its own K/V cache [S][Tmax][Dc] (omni_train.cpp dec_step_d) ──
    "rot25p":   (["f32list", "f32list", "f32list", "list", "list", "list", "list", "int", "int", "int", "int", "int", "list"], rot25p_eq(), "T0", False),
    # cache slot write: cache[s][pos_s][d] = src[s·SW + OFF + d]; every other slot unchanged (out = the cache itself). args: cache, src, pos, Tmax, Dc, OFF, SW
    "kvput":    (["f32list", "f32list", "list", "int", "int", "int", "int"], "(map a0 (sel (== (% (/ item1 a4) a3) (idx a2 (/ item1 (* a3 a4)))) (idx a1 (+ (+ (* (/ item1 (* a3 a4)) a6) a5) (% item1 a4))) (idx a0 item1)))", "T0", False),
    # the same for an int source (the token ids of the copy cache, held as exact floats). args: cache, src, pos, Tmax
    "kvputi":   (["f32list", "list", "list", "int"], "(map a0 (sel (== (% item1 a3) (idx a2 (/ item1 a3))) (idx a1 (/ item1 a3)) (idx a0 item1)))", "T0", False),
    # scores over the station's cache (j ≤ pos): q·K_j·sc, else −1e30. args: q, Kc, pos, H, Tmax, Dc, DH, QS (q row stride), sc → [N·H·Tmax]
    "dscore":   (["f32list", "f32list", "list", "int", "int", "int", "int", "int", "f32"], "(map (range 0 (* (len a2) (* a3 a4))) (sel (<= (% item1 a4) (idx a2 (/ item1 (* a3 a4)))) (* (fold (range 0 a6) 0.0f (+ acc2.0 (* (idx a0 (+ (+ (* (/ item1 (* a3 a4)) a7) (* (% (/ item1 a4) a3) a6)) item2)) (idx a1 (+ (+ (* (+ (* (/ item1 (* a3 a4)) a4) (% item1 a4)) a5) (* (% (/ item1 a4) a3) a6)) item2))))) a8) (neg 1e30f)))", "T0", False),
    # per (station, head): [max, Σ exp(s − max)] over j ≤ pos. args: scores, pos, H, Tmax → [N·H·2]
    # att[s][h·DH + d] = Σ_{j ≤ pos} exp(s_j − max)·(1/z) · V_j. args: scores, stat, Vc, pos, H, Tmax, Dc, DH → [N·Dc]
    # per (station, head) max and Σ exp(s − max) over j ≤ pos (two passes, each linear). args: scores, pos, H, Tmax [, mx] → [N·H]
    "dmx":      (["f32list", "list", "int", "int"], "(map (range 0 (* (len a1) a2)) (fold (range 0 (+ (idx a1 (/ item1 a2)) 1)) (neg 1e30f) (max acc2.0 (idx a0 (+ (* item1 a3) item2)))))", "T0", False),
    "dz":       (["f32list", "f32list", "list", "int", "int"], "(map (range 0 (* (len a2) a3)) (fold (range 0 (+ (idx a2 (/ item1 a3)) 1)) 0.0f (+ acc2.0 (exp (- (idx a0 (+ (* item1 a4) item2)) (idx a1 item1))))))", "T0", False),
    # att[s][h·DH + d] = Σ_{j ≤ pos} exp(s_j − max)·(1/z) · V_j. args: scores, mx, z, Vc, pos, H, Tmax, Dc, DH → [N·Dc]
    "datt":     (["f32list", "f32list", "f32list", "f32list", "list", "int", "int", "int", "int"], "(map (range 0 (* (len a4) a7)) (fold (range 0 (+ (idx a4 (/ item1 a7)) 1)) 0.0f (+ acc2.0 (* (* (exp (- (idx a0 (+ (* (+ (* (/ item1 a7) a5) (/ (% item1 a7) a8)) a6) item2)) (idx a1 (+ (* (/ item1 a7) a5) (/ (% item1 a7) a8))))) (/ 1.0f (idx a2 (+ (* (/ item1 a7) a5) (/ (% item1 a7) a8))))) (idx a3 (+ (* (+ (* (/ item1 a7) a6) item2) a7) (% item1 a7)))))))", "T0", False),
    # exact top-2 per row in three linear passes: the max, the FIRST index holding it, the max over the others. args: logits, V [, mx [, a1]]
    "rowmax":   (["f32list", "int"], "(map (range 0 (/ (len a0) a1)) (fold (range 0 a1) (neg 1e30f) (max acc2.0 (idx a0 (+ (* item1 a1) item2)))))", "T0", False),
    "rowarg":   (["f32list", "f32list", "int"], "(map (range 0 (len a1)) (fold (range 0 a2) -1 (sel (and (< acc2.0 0) (== (idx a0 (+ (* item1 a2) item2)) (idx a1 item1))) item2 acc2.0)))", "T0", False),
    "row2nd":   (["f32list", "f32list", "int"], "(map (range 0 (len a1)) (fold (range 0 a2) (neg 1e30f) (max acc2.0 (sel (== item2 (idx a1 item1)) (neg 1e30f) (idx a0 (+ (* item1 a2) item2))))))", "T0", False),
    # rows whose exit layer is l take a, the rest b. args: a, b, ex, D, l
    "selex":    (["f32list", "f32list", "f32list", "int", "int"], "(map a0 (sel (== (idx a2 (/ item1 a3)) a4) (idx a0 item1) (idx a1 item1)))", "T0", False),
    # copy strength per station: softplus(β)·g. args: g [N], beta [1]
    "csg":      (["f32list", "f32list"], "(map a0 (* (ln (+ 1.0f (exp (idx a1 0)))) (idx a0 item1)))", "T0", False),
    # the head with this step's boosts (running rows only): logit + (Σ_{u ≤ pos, cx_u = v} cs·exp(a_u − m)/z + [v = prop]·ptr).
    # args: logits, cp (copy scores N·Tmax), cst (N·2), cs (N), cx (N·Tmax tokens), pos, ppb (N), prop, ex (N), V, Tmax, L
    # args: logits, cp (copy scores N·Tmax), cmx (N), cz (N), cs (N), cx (N·Tmax tokens), pos, ppb (N), prop, ex (N), V, Tmax, L
    "dhead":    (["f32list", "f32list", "f32list", "f32list", "f32list", "f32list", "list", "f32list", "list", "f32list", "int", "int", "int"], "(map a0 (sel (< (idx a9 (/ item1 a10)) a12) (idx a0 item1) (+ (idx a0 item1) (+ (fold (range 0 (+ (idx a6 (/ item1 a10)) 1)) 0.0f (+ acc2.0 (sel (== (idx a5 (+ (* (/ item1 a10) a11) item2)) (% item1 a10)) (* (idx a4 (/ item1 a10)) (/ (exp (- (idx a1 (+ (* (/ item1 a10) a11) item2)) (idx a2 (/ item1 a10)))) (idx a3 (/ item1 a10)))) 0.0f))) (sel (== (% item1 a10) (idx a8 (/ item1 a10))) (idx a7 (/ item1 a10)) 0.0f)))))", "T0", False),
    # exact top-2 per row: [a1 (first max), s1, s2 = max over v ≠ a1]. args: logits, V
    "rcpart":   (["f32list", "int", "int"], rcpart_eq(), "T0", False),
    "rcz":      (["f32list", "f32list", "int", "int"], rcz_eq(), "T0", False),
    "hstatsC":  (["f32list", "list", "f32list", "list", "f32list", "f32list", "int", "int", "int", "f32"], hstats_chunk_eq(), "T0", False),
    "rtcheckC": (["f32list", "f32list", "f32list", "f32list", "list", "f32list", "int", "int", "int", "int", "f32", "f32", "int", "int"], rtcheck_chunk_eq(), "T0", False),
    "pgw":      (["f32list", "f32list", "list", "list", "int", "f32", "f32"], "(map (range 0 (* (/ (len a0) a4) 2)) (sel (== (% item1 2) 0) (/ 1.0f (+ 1.0f (exp (neg (/ (- (idx a1 (+ (* (/ item1 2) 5) 2)) a5) a6))))) (sel (and (and (>= (idx a2 (/ item1 2)) 0) (< (idx a2 (/ item1 2)) a4)) (>= (idx a3 (/ item1 2)) 0)) (/ (exp (- (idx a0 (+ (* (/ item1 2) a4) (idx a2 (/ item1 2)))) (idx a1 (+ (* (/ item1 2) 5) 3)))) (idx a1 (+ (* (/ item1 2) 5) 4))) 0.0f)))", "T0", False),
    # v[n, d] = valid ? w·E[prop, d] : 0. args: E, gw, kind, prop, K, D
    "pvec":     (["f32list", "f32list", "list", "list", "int", "int"], "(map (range 0 (* (len a2) a5)) (sel (and (and (>= (idx a2 (/ item1 a5)) 0) (< (idx a2 (/ item1 a5)) a4)) (>= (idx a3 (/ item1 a5)) 0)) (* (idx a1 (+ (* (/ item1 a5) 2) 1)) (idx a0 (+ (* (idx a3 (/ item1 a5)) a5) (% item1 a5)))) 0.0f))", "T0", False),
    # out[n, d] = a[n, d] + s[n·stride + off]·b[n, d]. args: a, b, s, D, stride, off
    "raxpy2":   (["f32list", "f32list", "f32list", "int", "int", "int"], "(map a0 (+ (idx a0 item1) (* (idx a2 (+ (* (/ item1 a3) a4) a5)) (idx a1 item1))))", "T0", False),
    # pointer bias pb[n] = valid ? β[kind]·g·w : 0. args: gw, beta, kind, prop, K
    "pptrb":    (["f32list", "f32list", "list", "list", "int"], "(map (range 0 (len a2)) (sel (and (and (>= (idx a2 item1) 0) (< (idx a2 item1) a4)) (>= (idx a3 item1) 0)) (* (* (idx a1 (idx a2 item1)) (idx a0 (* item1 2))) (idx a0 (+ (* item1 2) 1))) 0.0f))", "T0", False),
    # logits[n, prop_n] += pb[n] (pb ≠ 0). args: logits, pb, prop, V
    "hptr":     (["f32list", "f32list", "list", "int"], "(map a0 (+ (idx a0 item1) (sel (and (== (% item1 a3) (idx a2 (/ item1 a3))) (!= (idx a1 (/ item1 a3)) 0.0f)) (idx a1 (/ item1 a3)) 0.0f)))", "T0", False),
    # ∂L/∂logit[prop] for the pointer rows. args: dl, pb, prop, V
    "pgather":  (["f32list", "f32list", "list", "int"], "(map a1 (sel (and (!= (idx a1 item1) 0.0f) (>= (idx a2 item1) 0)) (idx a0 (+ (* item1 a3) (idx a2 item1))) 0.0f))", "T0", False),
    # gdx[n, d] = valid ? g·dx : 0. args: dx, gw, kind, prop, K, D
    "pgdx":     (["f32list", "f32list", "list", "list", "int", "int"], "(map a0 (sel (and (and (>= (idx a2 (/ item1 a5)) 0) (< (idx a2 (/ item1 a5)) a4)) (>= (idx a3 (/ item1 a5)) 0)) (* (idx a1 (* (/ item1 a5) 2)) (idx a0 item1)) 0.0f))", "T0", False),
    # [dg, dw] per row: dg = dx·uv + dlp·β_kind·w; dw = dv·E[prop] + dlp·β_kind·g (0 off the offer rows). args: dx, uv, dv, E, gw, kind, prop, beta, pdl, K, D
    "pdgw":     (["f32list", "f32list", "f32list", "f32list", "f32list", "list", "list", "f32list", "f32list", "int", "int"], pdgw_eq(), "T0", False),
    # dr[n, k]: which 0 = the port path (softmax + gate), 1 = router CE rce·(s_k − δ)/N. args: r, st, gw, dgw, kind, prop, K, tau, rce, N, which
    "pdr":      (["f32list", "f32list", "f32list", "f32list", "list", "list", "int", "f32", "f32", "int", "int"], pdr_eq(), "T0", False),
    # out[k] = Σ_n A[n, k] + B[n, k]. args: A, B, K
    "colsum2":  (["f32list", "f32list", "int"], "(map (range 0 a2) (fold (range 0 (/ (len a0) a2)) 0.0f (+ acc2.0 (+ (idx a0 (+ (* item2 a2) item1)) (idx a1 (+ (* item2 a2) item1))))))", "T0", False),
    # dβ[k] = Σ_{n: kind = k, valid} dlp·g·w. args: gw, kind, prop, pdl, K
    "pdbeta":   (["f32list", "list", "list", "f32list", "int"], "(map (range 0 a4) (fold (range 0 (len a1)) 0.0f (+ acc2.0 (sel (and (== (idx a1 item2) item1) (>= (idx a2 item2) 0)) (* (* (idx a3 item2) (idx a0 (* item2 2))) (idx a0 (+ (* item2 2) 1))) 0.0f))))", "T0", False),
    # GROW-RUN-0 G2 — the local rule (LEARN_LOCAL=2) + depth routing (LEARN_ROUTE = EXIT_THETA 3, ROUTE_SAT 0.9) + stage roles (LEARN_ROLES)
    "fillc":    (["int", "f32"], "(map (range 0 a0) a1)", "T0", False),
    # avoid-aware head (study / sleep): stats; spark (never on a pushed row); gradient with ulc = α·p_av / max(1 − p_av, 1e-5):
    # dl = e^(l − mx)/z·(1 − ulc)/nrm − [v = y]/nrm + [v = av]·ulc/nrm
    "hstatsA":  (["f32list", "list", "f32list", "list", "int", "int", "f32"], head_stats_avoid_eq(), "T0", False),
    "hsparkA":  (["f32list", "list", "f32list", "f32list", "list", "int", "int", "f32"], "(map (range 0 a5) (sel (or (or (< (idx a1 item1) 0) (<= (idx a3 item1) 0.0f)) (and (and (>= (idx a4 item1) 0) (< (idx a4 item1) a6)) (!= (idx a4 item1) (idx a1 item1)))) 0.0f (sel (and (and (== (idx a0 (+ (* item1 a6) (idx a1 item1))) (idx a2 (* item1 3))) (== (fold (range 0 a6) 0 (+ acc2.0 (sel (and (!= item2 (idx a1 item1)) (== (idx a0 (+ (* item1 a6) item2)) (idx a2 (* item1 3)))) 1 0))) 0)) (> (- (idx a2 (* item1 3)) (fold (range 0 a6) (neg 1e30f) (max acc2.0 (sel (== item2 (idx a1 item1)) (neg 1e30f) (idx a0 (+ (* item1 a6) item2)))))) a7)) 1.0f 0.0f)))", "T0", False),
    # args: logits, hst, y, skip, mask, nsbuf, av, V, alpha
    "hdlA":     (["f32list", "f32list", "list", "f32list", "f32list", "f32list", "list", "int", "f32"], hdl_avoid_eq(), "T0", False),
    # the loss with depth routing: (Σ head row losses + Σ exited rows' read-out CE) / N (forward_backward:2145). args: hst, rce, N
    "lsumR":    (["f32list", "f32list", "int"], "(/ (+ (fold (range 0 a2) 0.0f (+ acc1.0 (idx a0 (+ (* item1 3) 2)))) (fold (range 0 a2) 0.0f (+ acc1.0 (idx a1 item1)))) a2)", "T0", False),
    "rtcheck":  (["f32list", "f32list", "f32list", "f32list", "list", "int", "int", "int", "int", "f32", "f32", "int"], rtcheck_eq(), "T0", False),
    # the exited row's CE at its read-out (rows that left at l; value only + P3's row loss). args: logits, y, ex, rce, V, l → rce′
    "rtce":     (["f32list", "list", "f32list", "f32list", "int", "int"], "(map a3 (sel (and (== (idx a2 item1) a5) (>= (idx a1 item1) 0)) (- (+ (fold (range 0 a4) (neg 1e30f) (max acc2.0 (idx a0 (+ (* item1 a4) item2)))) (ln (fold (range 0 a4) 0.0f (+ acc2.0 (exp (- (idx a0 (+ (* item1 a4) item2)) (fold (range 0 a4) (neg 1e30f) (max acc3.0 (idx a0 (+ (* item1 a4) item3)))))))))) (idx a0 (+ (* item1 a4) (idx a1 item1)))) (idx a3 item1)))", "T0", False),
    # frozen rows (left below block l) keep their state through it: out = ex < l ? A : B. args: A, B, ex, D, l
    "rowsel":   (["f32list", "f32list", "f32list", "int", "int"], "(map a0 (sel (< (idx a2 (/ item1 a3)) a4) (idx a0 item1) (idx a1 item1)))", "T0", False),
    # out[n] = ex[n] ≥ th ? 1 : 0. args: ex, th
    "exmask":   (["f32list", "int"], "(map a0 (sel (>= (idx a0 item1) a1) 1.0f 0.0f))", "T0", False),
    "hstatsM":  (["f32list", "list", "f32list", "int", "int"], head_stats_mask_eq(), "T0", False),
    "hsparkM":  (["f32list", "list", "f32list", "f32list", "int", "int", "f32"], "(map (range 0 a4) (sel (or (< (idx a1 item1) 0) (<= (idx a3 item1) 0.0f)) 0.0f (sel (and (and (== (idx a0 (+ (* item1 a5) (idx a1 item1))) (idx a2 (* item1 3))) (== (fold (range 0 a5) 0 (+ acc2.0 (sel (and (!= item2 (idx a1 item1)) (== (idx a0 (+ (* item1 a5) item2)) (idx a2 (* item1 3)))) 1 0))) 0)) (> (- (idx a2 (* item1 3)) (fold (range 0 a5) (neg 1e30f) (max acc2.0 (sel (== item2 (idx a1 item1)) (neg 1e30f) (idx a0 (+ (* item1 a5) item2)))))) a6)) 1.0f 0.0f)))", "T0", False),
    # dl = (mask, y ≥ 0, not skipped) (softmax − onehot) / nrm, nrm = N (final head) or the read-out's row count Ns from a buffer.
    # args: logits, hst, y, skip, mask, nsbuf, V  (nsbuf[0] = the normaliser)
    "hdlN":     (["f32list", "f32list", "list", "f32list", "f32list", "f32list", "int"], "(map a0 (sel (or (or (< (idx a2 (/ item1 a6)) 0) (> (idx a3 (/ item1 a6)) 0.0f)) (<= (idx a4 (/ item1 a6)) 0.0f)) 0.0f (- (* (exp (- (idx a0 item1) (idx a1 (* (/ item1 a6) 3)))) (/ 1.0f (* (idx a1 (+ (* (/ item1 a6) 3) 1)) (idx a5 0)))) (sel (== (% item1 a6) (idx a2 (/ item1 a6))) (/ 1.0f (idx a5 0)) 0.0f))))", "T0", False),
    # local_readout:1763 row selection of block l: not left below l, not P3-dead; left AT l → always; else stage roles (rm bit of the row's
    # stage, stage < 0 → yes) or the stride (n + step) mod S = 0. args: ex, p3m, pst, stepv, pw32, l, rm, S, routeon, roleson
    "lsel":     (["f32list", "f32list", "list", "list", "list", "int", "int", "int", "int", "int"], "(map a0 (sel (or (and (!= a8 0) (< (idx a0 item1) a5)) (<= (idx a1 item1) 0.0f)) 0.0f (sel (and (!= a8 0) (== (idx a0 item1) a5)) 1.0f (sel (!= a9 0) (sel (or (< (idx a2 item1) 0) (== (% (/ a6 (idx a4 (% (idx a2 item1) 32))) 2) 1)) 1.0f 0.0f) (sel (== (% (+ item1 (idx a3 0)) a7) 0) 1.0f 0.0f)))))", "T0", False),
    # P3 with routing: a row that left early has its read-out CE as its row loss. args: hst, rce, ex, y, stepv, lmax, full, AL
    "p3maskR":  (["f32list", "f32list", "f32list", "list", "list", "f32", "int", "int"], "(map a1 (sel (or (== (% (idx a4 0) a6) 0) (or (< (idx a3 item1) 0) (>= (sel (< (idx a2 item1) a7) (idx a1 item1) (idx a0 (+ (* item1 3) 2))) a5))) 1.0f 0.0f))", "T0", False),
    # harmony rows not heard at block l (left below it): hw[(b·H + h)·T + i, ·] · live[b·T + i]. args: hw, live, H, T
    "hwmask":   (["f32list", "f32list", "int", "int"], "(map a0 (* (idx a0 item1) (idx a1 (+ (* (/ item1 (* (* a2 a3) 10)) a3) (% (/ item1 10) a3)))))", "T0", False),
    "embg":     (["f32list", "f32list", "list", "list", "int", "int"], "(map (range 0 (* a4 a5)) (fold (range (idx a3 (/ item1 a5)) (idx a3 (+ (/ item1 a5) 1))) (idx a0 item1) (+ acc2.0 (idx a1 (+ (* (idx a2 item2) a5) (% item1 a5))))))", "T0", False),
}

def emit_all(out):
    os.makedirs(out, exist_ok=True); T = json.load(open(spirv.TABLES)); man = {}
    jobs = {j["fn"]: j for j in json.load(open(SPECS))}
    for name, (args, eq, tpl, batch) in sorted(K.items()):                   # C2 replica axis: every kernel batched (T0B: rows y, replicas z)
        b, info = spirv.emit_spv({"args": args, "equation": eq}, T, tpl, True)
        open(f"{out}/{name}.spv", "wb").write(b); man[name] = {"args": args, "sha256": hashlib.sha256(b).hexdigest(), **info}
    for g in ("sgemm_gnn", "sgemm_gnt", "sgemm_gtn"):                                          # wall-passed GPU-LOOP specs, template T2
        j = jobs[g]; b, info = spirv.emit_spv({"args": j["args"].split(","), "equation": j["equation"]}, T, "T2", True)   # T2B: per replica
        open(f"{out}/{g}.spv", "wb").write(b); man[g] = {"args": j["args"].split(","), "sha256": hashlib.sha256(b).hexdigest(), **info}
    json.dump(man, open(f"{out}/manifest.json", "w"), indent=1, sort_keys=True)
    return man

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else f"{P}/kernels/train"
    man = emit_all(out)
    import subprocess
    bad = [n for n in man if subprocess.run(["spirv-val", "--target-env", "vulkan1.1", f"{out}/{n}.spv"], capture_output=True).returncode]
    print(f"emitted {len(man)} kernels → {out}; spirv-val failures: {bad or 'none'}")
    sys.exit(1 if bad else 0)

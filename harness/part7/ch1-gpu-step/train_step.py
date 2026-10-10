#!/usr/bin/env python3
"""OMNI-RENDER-GPU-0 § CYCLONE-ARRAY C2 S1 — THE TRAINING STEP ON THE GPU: one THEAD model's forward + head + backward (the plain trunk:
omni_train.cpp forward_backward with every school switch off — no plates / port / local rule / routing / harmony / P3 / T25 core) as ONE
recorded resident step of compute passes on our Vulkan session (`omni-gpu session`), in the engine's own order:
  bl_quant ×4L (absmean f64 + trits + float view) → gather E[x] → per block [rms n1 → BitLinear qkv → rot → attention per (b, h) → BitLinear o
  (+ residual) → rms n2 → BitLinear up → relu² → BitLinear down (+ residual)] → rms nf → tied head (logits, softmax, loss, dl) →
  dh = dl·E, dE += dlᵀ·hf → rms_bwd nf → per block in reverse [bl_bwd down → relu² bwd → bl_bwd up → rms_bwd n2 → bl_bwd o → attention bwd →
  rot⁻¹ → bl_bwd qkv → rms_bwd n1] → dE += scatter of dx (tokens grouped, n order)
Kernels: gen/train_kernels.py (our emitter) + kernels/absmean.spv. The parameters arrive in the engine's P order (om_param_ptr); the gate is
the CPU engine's own om_grad on the same weights + batch (tests/train/s1_grad.py).
  build(dims, param_files, x, y, workdir) → (program text, outputs: {name: (buffer index, shape)})"""
import json, math, os, struct, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(HERE)
KD = f"{P}/kernels/train"; MAN = json.load(open(f"{KD}/manifest.json")) if os.path.exists(f"{KD}/manifest.json") else {}
HAND = {"absmean": ["f32list"], "sumsq": ["f32list"], "adam_scal": ["f32list"], "red_part": ["f32list"], "red_fin": ["f32list"], "copy": ["f32list"],
        "hub_mean": ["f32list"], "hub_pull": ["f32list"], "wsum_g": ["f32list"], "dset_g": ["f32list"], "copy2": ["f32list"]}   # wsum_g / dset_g: the array's per-unit cyclone (G3b-3)                     # hub_mean / hub_pull = the cyclone's W2b kernels (kernels/hub_*.spvasm)     # hand-written float64 kernels (kernels/*.spvasm)
ARENA = os.environ.get("OMNI_TRAIN_ARENA", "1") != "0"; ALIGN = 256           # M0: transients as views of one arena (0 = shared whole buffers)
PLAN = os.environ.get("OMNI_TRAIN_PLAN", "1") != "0"                          # M0 buffer reuse (0 = one buffer per logical buffer, for A/B)
ARENA_MAX = int(float(os.environ.get("OMNI_TRAIN_ARENA_MAX", 3.5 * 2 ** 30)))   # one arena ≤ one device allocation (A40 maxMemoryAllocationSize 0xFFE00000)
BIND_MAX = int(os.environ.get("OMNI_TRAIN_BIND_MAX", 2 ** 31 - 1))   # NVIDIA A40: a storage binding of ≥ 2³¹ bytes trains NOTHING, silently
                                                                                # (G3b-3 sweep: R 30 logits 2.01 GB learns, R 32 = 2³¹ B does not)
ATTN_GEMM = os.environ.get("OMNI_TRAIN_ATTN_GEMM", "1") == "1"   # ON (s3 centre school R8 learning gate PASS on the A40, 10-09); attention products (qkT / pv / ptv) as batched register-blocked GEMMs (z = R·rows)
GT = (MAN.get("sgemm_gnt", {}).get("dispatch", {}) or {}).get("tile", 64)   # the GEMM template's block tile (T2: 128 since 10-09)
CH = int(os.environ.get("OMNI_TRAIN_CHUNKS", "64"))                   # row statistics over V in CH chunks (rcpart / rcz): 0 = one thread per row
HG = os.environ.get("OMNI_TRAIN_HGEMM", "0")   # tensor-core GEMMs (gen/coop_gemm.py): "bl" = BitLinear's forward only (int8 × trits: exact), "all", "0"
for _k in ("gnt", "gnn", "gtn"):
    if f"sgemm_{_k}" in MAN: MAN[f"hgemm_{_k}"] = dict(MAN[f"sgemm_{_k}"], dispatch=dict(MAN[f"sgemm_{_k}"].get("dispatch", {}), tile=64))
LOCAL = 512                                                                     # T0 local size (SpecId 100): 65,535 × 512 elements per launch
PRIMES = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137]

def bits(v, t):
    return (int(v) & 0xFFFFFFFF) if t in ("int", "list") else struct.unpack("<I", struct.pack("<f", float(v)))[0]

class Prog:
    def __init__(self, wd, R=1, U=1): self.wd = wd; self.R = R; self.U = U; self.bufs = {}; self.meta = {}; self.decl = {}; self.glob = set(); self.plist = []; self.passes = 0; self.tag = ""
    def buf(self, name, nbytes=None, data=None, glob=False, shared=False):
        """a buffer of this step (named under the current step tag) or a global one (tables, parameters). Replica axis: nbytes / data are PER
        REPLICA (data may carry a leading R axis: one slice per replica); the buffer holds R slices unless shared (one slice read by all)"""
        full = name if glob else self.tag + name
        if full in self.bufs: raise ValueError(f"buffer {full} twice")
        self.bufs[full] = len(self.bufs); reps = 1 if shared else self.R
        if glob: self.glob.add(full)
        if data is not None:
            d = np.ascontiguousarray(data)
            if not shared and self.R > 1 and (d.ndim < 2 or d.shape[0] != self.R): d = np.stack([d] * self.R)   # the same slice for every replica
            f = f"{self.wd}/{full}.bin"; d.tofile(f); self.decl[full] = ("file", f, d.nbytes); per = d.size // reps
        else: per = max(1, int(nbytes) // 4); self.decl[full] = ("zero", None, max(4, per * 4 * reps))
        self.meta[full] = (per, shared)
        return full
    def full(self, name):
        return self.tag + name if self.tag + name in self.bufs else name
    def program(self, pinned=(), plan=True):
        """→ (buf + pass lines, {logical name: session buffer index}). M0 BUFFER REUSE (plan § Model form): a logical buffer shares one
        physical buffer with others whose pass ranges it never overlaps (a barrier follows every pass, so a range is [first pass, last
        pass]); never shared: globals (weights, moments, tables, partials), file-backed and host-written / read-back buffers (pinned), any
        buffer first READ before it is written (it keeps its zero / file start), and red_part / red_fin inputs, which size their slices by
        arrayLength (exact size only)."""
        OUT = {"red_part": 1, "red_fin": 2, "adam_scal": 1, "copy": 1, "hub_mean": 2, "hub_pull": 0, "wsum_g": 2, "dset_g": 2, "copy2": 1}; first, last, firstw, exact = {}, {}, {}, set()
        for i, (kern, _, _, names) in enumerate(self.plist):
            if kern == "__segment__": continue
            w = names[OUT.get(kern, len(names) - 1)]
            if kern in ("red_part", "red_fin"): exact.add(names[0])
            for n in names:
                first.setdefault(n, i); last[n] = i
            firstw.setdefault(w, i)
        fixed = set(self.glob) | set(pinned) | {n for n, d in self.decl.items() if d[0] == "file"}
        fixed |= {n for n in first if firstw.get(n, 10 ** 9) > first[n]}             # read before written: keeps its start contents
        phys, idx = [], {}                                                             # phys: [decl, size, free after pass, exact]
        for n in self.bufs:
            if n not in first or n in fixed or not plan: idx[n] = len(phys); phys.append([self.decl[n], self.decl[n][2], 10 ** 9, True])
        big = [(n, self.decl[n][2]) for n in self.bufs if self.decl[n][2] > BIND_MAX]
        if big: raise ValueError(f"buffer(s) over one storage binding ({BIND_MAX} bytes): {big[:3]} — fewer models per session (array server --group)")
        trans = [n for n in self.bufs if n not in idx]
        if ARENA and trans:                                                    # arenas, each transient a view at its own offset (exact range):
            placed, off, where = [[]], {}, {}                                  # greedy by size — largest first, lowest offset free over its pass range;
            for n in sorted(trans, key=lambda n: (-self.decl[n][2], first[n])):   # an arena never passes ARENA_MAX (one device allocation: the A40
                need = self.decl[n][2]                                         # allows 0xFFE00000 bytes; a 10.9 GiB arena trained nothing, G3b-3 R 40)
                for a in range(len(placed) + 1):
                    if a == len(placed): placed.append([])
                    cur = 0
                    for o, sz in sorted((off[m], self.decl[m][2]) for m in placed[a] if not (last[m] < first[n] or first[m] > last[n])):
                        if o - cur >= need: break
                        cur = max(cur, -(-(o + sz) // ALIGN) * ALIGN)
                    if cur + need <= ARENA_MAX or not placed[a]: break         # fits under the cap (or alone in a fresh arena)
                off[n] = cur; where[n] = a; placed[a].append(n)
            ais = []
            for a, ns in enumerate(placed):
                if not ns: continue
                size = max(off[n] + self.decl[n][2] for n in ns); ais.append((a, len(phys), size)); phys.append([("zero", None, size), size, 10 ** 9, True])
            lines = [(f"buf file {d[1]}" if d[0] == "file" else f"buf zero {size}") for d, size, _, _ in phys]
            ai = {a: i for a, i, _ in ais}
            for n in trans: idx[n] = len(lines); lines.append(f"buf view {ai[where[n]]} {off[n]} {self.decl[n][2]}")
            self.arena = sum(sz for _, _, sz in ais); self.arenas = [sz for _, _, sz in ais]
        else:
          for n in sorted(trans, key=lambda n: first[n]):
            need = self.decl[n][2]; ex = n in exact
            cand = [j for j, ph in enumerate(phys) if ph[2] < first[n] and (ph[1] == need if (ex or ph[3]) else ph[1] >= need)]
            if cand:
                j = min(cand, key=lambda j: phys[j][1]); phys[j][2] = last[n]; idx[n] = j
            else: idx[n] = len(phys); phys.append([self.decl[n], need, last[n], ex])
          lines = [(f"buf file {d[1]}" if d[0] == "file" else f"buf zero {size}") for d, size, _, _ in phys]
        for kern, g, spec, names in self.plist:
            if kern == "__segment__": lines.append("segment"); continue           # a new recorded segment (Session::step_seg)
            lines.append(f"pass {KD}/{kern}.spv {g} " + ("spec " + " ".join(f"{a}={b}" for a, b in spec) + " " if spec else "") + "bind " + " ".join(str(idx[b]) for b in names))
        self.nphys = len(phys); self.bytes_planned = sum(size for _, size, _, _ in phys); self.bytes_logical = sum(d[2] for d in self.decl.values())
        return lines, idx
    def segment(self): self.plist.append(("__segment__", None, None, []))
    def mt(self, name):
        return self.meta[self.tag + name] if self.tag + name in self.meta else self.meta[name]
    def ix(self, name):
        if self.tag + name in self.bufs: return self.bufs[self.tag + name]
        return self.bufs[name]
    def tot(self, name):
        per, sh = self.mt(name); return per if sh else per * self.R
    def k(self, kern, binds, scalars=(), n_out=None, rows=None, row_strides=None, out_stride=None, groups=None, per=None, width=None):
        """one pass of a train kernel: binds = buffer names for the list args then the output; scalars = values of the scalar args in
        order; T0: n_out elements (1-D, LOCAL per group); T0B (rows): row strides per list arg + out_stride; T2: groups from the shape"""
        if ATTN_GEMM and kern in ("qkT", "pv", "ptv") and rows:               # the products as GEMMs over z = R · rows (same k order as the fold)
            T_, d_ = int(scalars[0]), int(scalars[1]); sA, sB = row_strides; sO = out_stride
            if kern == "qkT": return self.bgemm("gnt", binds, T_, T_, d_, d_, d_, T_, rows, sA, sB, sO)      # S = Q·Kᵀ
            return self.bgemm("gnn" if kern == "pv" else "gtn", binds, T_, d_, T_, T_, d_, d_, rows, sA, sB, sO)   # P·V · Pᵀ·V
        m = MAN[kern] if kern not in HAND else {"args": HAND[kern], "template": "hand"}
        args = m["args"]; spec = []; si = 0; li = 0
        for k_, t in enumerate(args):
            if t in ("int", "f32"): spec.append((k_, bits(scalars[si], t))); si += 1
        assert si == len(scalars) or kern in HAND, f"{kern}: {len(scalars)} scalars for {si}"
        tpl = m.get("template"); R = self.R
        if tpl in ("T0B", "T2B"):                                              # replica axis z: each list arg at its replica's slice
            lists = [k_ for k_, t in enumerate(args) if t in ("f32list", "list")]; rs = row_strides or [0] * len(lists)
            for j, k_ in enumerate(lists):
                per, sh = self.mt(binds[j])
                spec += [(200 + 3 * k_, rs[j]), (201 + 3 * k_, 0 if sh else per), (202 + 3 * k_, rs[j] if rows else per)]
            per, sh = self.mt(binds[-1]); spec += [(290, out_stride or 0), (291, 0 if sh else per)]
            if tpl == "T0B": spec.append((100, LOCAL)); g = f"{max(1, math.ceil(n_out / LOCAL))},{rows or 1},{R}"
            else: gx, gy, _ = groups.split(","); g = f"{gx},{gy},{R}"
        elif tpl == "T0": spec.append((100, LOCAL)); g = f"{max(1, math.ceil(n_out / LOCAL))},1,1"
        elif tpl == "T2": g = groups
        elif kern in ("hub_mean", "hub_pull"):                                 # 64 per group over G·W (mean) or G·R·W (pull), y when x > 32,768
            W_ = width or self.mt(binds[0])[0]; pg = per or R // self.U          # pg = models per hub: a unit's harnesses (R / U), or a floor's units
            n_ = self.tot(binds[0]) // pg if kern == "hub_mean" else self.tot(binds[0]); ng = math.ceil(n_ / 64); gx = min(ng, 32768)
            g = f"{gx},{math.ceil(ng / gx)},1"; spec = [(1, pg), (2, W_)]
        elif kern in ("wsum_g", "dset_g"):                                     # each harness against ITS unit's C (r / per): over R·W
            W_ = self.mt(binds[-1])[0]; ng = math.ceil(R * W_ / 64); gx = min(ng, 32768)
            g = f"{gx},{math.ceil(ng / gx)},1"; spec = [(1, R // self.U), (2, W_)] + ([(3, bits(scalars[0], "f32"))] if kern == "dset_g" else [])
        else:
            if kern == "copy" and math.ceil(n_out * R / LOCAL) > 65535:      # one grid axis holds 65,535 groups: past that the 2-D copy (copy2)
                kern = "copy2"; ng = math.ceil(n_out * R / LOCAL); gx = min(ng, 32768); cg = f"{gx},{math.ceil(ng / gx)},1"
            g = f"16,1,{R}" if kern == "red_part" else f"{math.ceil(n_out * R / LOCAL)},1,1" if kern == "copy" else cg if kern == "copy2" else f"1,1,{R}"
            spec = [(0, bits(scalars[0], "f32"))] if kern == "adam_scal" else [(0, int(scalars[0]))] if kern in ("red_part", "red_fin") else \
                   [(0, 0), (100, LOCAL)] if kern in ("copy", "copy2") else []
        self.plist.append((kern, g, spec, [self.full(b) for b in binds])); self.passes += 1
    def bgemm(self, kind, binds, M, N, K, lda, ldb, ldc, rows, sA, sB, sO):
        """a GEMM per (replica, row) — batch z = R · rows, every matrix at its own slice (stride sA / sB / sO in elements): the buffers are
        [R][rows][matrix], so z · stride is exactly the T0B address (replica · rows + row) · stride"""
        A, B, out = binds; kern = f"hgemm_{kind}" if HG == "all" else f"sgemm_{kind}"; tile = 64 if HG == "all" else GT; dper, dsh = self.mt("dummy") if "dummy" in self.bufs or self.tag + "dummy" in self.bufs else (1, True)
        spec = [(3, M), (4, N), (5, K), (6, lda), (7, ldb), (8, ldc), (9, 0)]
        spec += [(200, 0), (201, sA), (202, sA), (203, 0), (204, sB), (205, sB), (206, 0), (207, 0), (208, dper), (290, 0), (291, sO)]
        g = f"{math.ceil(ldc / tile)},{math.ceil(M / tile)},{self.R * rows}"
        self.plist.append((kern, g, spec, [self.full(b) for b in (A, B, "dummy", out)])); self.passes += 1
    def gemm(self, kind, A, B, C, out, M, N, K, lda, ldb, ldc, accum, hint=None):
        hg = HG == "all" or (HG == "bl" and hint == "int")                   # tensor cores: every GEMM, or the exact integer ones
        kern, tile = (f"hgemm_{kind}", 64) if hg else (f"sgemm_{kind}", GT)
        self.k(kern, [A, B, C, out], (M, N, K, lda, ldb, ldc, 1 if accum else 0), groups=f"{math.ceil(ldc / tile)},{math.ceil(M / tile)},1")

def hstats(pr, L, y, mask, av, out, N, V, alpha, tag):
    """[mx, z, loss] per row (hstatsA's formula) — in CH chunks when V allows (max exact, z summed per chunk)"""
    if CH > 1 and V % CH == 0 and V >= 1024:
        part = pr.buf(f"rp_{tag}", 4 * N * CH * 3); zc = pr.buf(f"rz_{tag}", 4 * N * CH)
        pr.k("rcpart", [L, part], (V, CH), n_out=N * CH * 3); pr.k("rcz", [L, part, zc], (V, CH), n_out=N * CH)
        pr.k("hstatsC", [L, y, mask, av, part, zc, out], (N, V, CH, float(alpha)), n_out=N * 3)
    else: pr.k("hstatsA", [L, y, mask, av, out], (N, V, float(alpha)), n_out=N * 3)

def rtcheck(pr, lg, xo, xi, ex, kind, N, V, D, l, AL, theta, sat, portrows, tag):
    """route_check / decoding's exit rule — the top-2 margin from CH chunk partials when V allows (exact: max, ties, runner-up)"""
    if CH > 1 and V % CH == 0 and V >= 1024:
        part = pr.buf(f"rcp_{tag}", 4 * N * CH * 3); pr.k("rcpart", [lg, part], (V, CH), n_out=N * CH * 3)
        pr.k("rtcheckC", [lg, xo, xi, ex, kind, part, ex], (V, D, l, AL, float(theta), float(sat), portrows, CH), n_out=N)
    else: pr.k("rtcheck", [lg, xo, xi, ex, kind, ex], (V, D, l, AL, float(theta), float(sat), portrows), n_out=N)

def setup(pr, dims, params, params_R=None):
    """global buffers: the parameters (P order; params_R = one parameter list per replica), the rotary tables, constants"""
    V, D, L, H, T, B = (dims[k] for k in ("V", "D", "L", "H", "T", "B")); DH = D // H; N = B * T
    if params_R: W = {n: pr.buf(f"w0_{i}", data=np.stack([pr_[i][1].astype(np.float32) for pr_ in params_R]), glob=True) for i, (n, _) in enumerate(params)}
    else: W = {n: pr.buf(f"w0_{i}", data=w.astype(np.float32), glob=True) for i, (n, w) in enumerate(params)}
    off, cs, sn = [], [], []
    for i in range(DH // 2):
        p_ = PRIMES[i]; off.append(len(cs)); a = 2.0 * np.pi * np.arange(p_) / p_; cs += list(np.cos(a).astype(np.float32)); sn += list(np.sin(a).astype(np.float32))
    pr.buf("rcos", data=np.array(cs, np.float32), glob=True, shared=True); pr.buf("rsin", data=np.array(sn, np.float32), glob=True, shared=True)
    pr.buf("roff", data=np.array(off, np.int32), glob=True, shared=True); pr.buf("rpr", data=np.array(PRIMES[:DH // 2], np.int32), glob=True, shared=True)
    pr.buf("dummy", 4, glob=True, shared=True); pr.buf("zeroND", N * D * 4, glob=True, shared=True); pr.buf("zeroD", D * 4, glob=True, shared=True)
    pr.buf("part", 1024 * 8, glob=True)                                       # float64 partials of the split reductions (reused pass by pass)
    return W

def fwd_bwd(pr, dims, W, x, y, sw=None, aux=None, fwd_only=False):
    """one forward + backward under the current step tag → (gradient buffers by parameter name, loss buffer, per-row head stats buffer).
    sw = the school switches on (GROW-RUN-0 G2): {"t25": the T25 core's residues turn the rotary clock, "voice": octave voicing};
    aux = their per-batch inputs when the batch is fixed (t25res [N, 32]) and tables (t25lane [DH/2])"""
    V, D, L, H, T, B = (dims[k] for k in ("V", "D", "L", "H", "T", "B")); DH = D // H; N = B * T; F = 4
    f = lambda *s: int(np.prod(s)) * F; sw = sw or {}; aux = aux or {}
    G = {}
    if sw.get("t25"):                                                          # T25-CORE: 32 residues per position (host-fed in the loop)
        if x is None: pr.buf("t25res", N * 32 * 4)
        else: pr.buf("t25res", data=np.asarray(aux["t25res"], np.int32).reshape(-1))
        if "t25lane" not in pr.bufs: pr.buf("t25lane", data=np.asarray(aux["t25lane"], np.int32), glob=True, shared=True)
    if sw.get("plates"):                                                       # attention plates: row starts per (b, h) (host-fed in the loop) + tables
        if x is None: pr.buf("rsBH", B * H * T * 4)
        else: pr.buf("rsBH", data=row_starts(x, B, T, aux["eos"], H))
        if "planes" not in pr.bufs:
            pr.buf("planes", data=plate_planes(DH), glob=True, shared=True); pr.buf("pw", data=np.array([1 << b_ for b_ in range(12)], np.int32), glob=True, shared=True)
    PL = bool(sw.get("plates"))
    PT = sw.get("port")                                                        # library port: {"K", "theta", "tau", "rce"}; kinds / proposals host-fed
    if PT:
        if x is None: pr.buf("pkind", N * 4); pr.buf("pprop", N * 4)
        else: pr.buf("pkind", data=np.asarray(aux["pkind"], np.int32)); pr.buf("pprop", data=np.asarray(aux["pprop"], np.int32))
    HM = sw.get("harm")                                                        # harmony: (lambda, kappa) — the ring tables once
    if HM and "htc" not in pr.bufs:
        HR = [37, 41, 43, 47, 53]; tc = np.concatenate([np.cos(2 * np.pi * np.arange(p_) / p_).astype(np.float32) for p_ in HR])
        ts_ = np.concatenate([np.sin(2 * np.pi * np.arange(p_) / p_).astype(np.float32) for p_ in HR])
        pr.buf("htc", data=tc, glob=True, shared=True); pr.buf("hts", data=ts_, glob=True, shared=True)
        pr.buf("hro", data=np.array([0, 37, 78, 121, 168], np.int32), glob=True, shared=True); pr.buf("hrp", data=np.array(HR, np.int32), glob=True, shared=True)
    if sw.get("p3"):                                                           # P3: the step number decides the full step (host-fed in the loop)
        if x is None: pr.buf("stepv", 4)
        else: pr.buf("stepv", data=np.array([aux.get("step", 0)], np.int32))
    AV = sw.get("avoid")                                                       # avoid rows (study / sleep): α; the token to push down per row (host-fed)
    if AV:
        if x is None: pr.buf("pavoid", N * 4)
        else: pr.buf("pavoid", data=np.asarray(aux["pavoid"], np.int32))
        if "nN" not in pr.bufs: pr.buf("nN", data=np.array([float(N)], np.float32), glob=True, shared=True)
        if "onesH" not in pr.bufs: pr.buf("onesH", N * 4); pr.k("fillc", ["onesH"], (N, 1.0), n_out=N)
    LC = sw.get("local")                                                       # local rule (LEARN_LOCAL=2): {"S", "roles": masks per block | None, "route": θ, "sat"}
    RT = bool(LC and float(LC.get("route", 0)) > 0)                            # depth routing (needs the local rule, as in the engine)
    if LC:
        pr.buf("ex", N * 4); pr.k("fillc", ["ex"], (N, float(L)), n_out=N)    # exit_at per row: L = still running
        pr.buf("rce", N * 4); pr.k("fillc", ["rce"], (N, 0.0), n_out=N)
        if pr.full("stepv") not in pr.bufs:
            if x is None: pr.buf("stepv", 4)
            else: pr.buf("stepv", data=np.array([aux.get("step", 0)], np.int32))
        if LC.get("roles"):
            if x is None: pr.buf("pstage", N * 4)
            else: pr.buf("pstage", data=np.asarray(aux["pstage"], np.int32))
        if "pw32" not in pr.bufs: pr.buf("pw32", data=np.array([(1 << b_) & 0x7FFFFFFF for b_ in range(32)], np.int32), glob=True, shared=True)
        if not sw.get("port") and "nokind" not in pr.bufs: pr.buf("nokind", data=np.full(N, -1, np.int32), glob=True)
    def rot(src, dst, sign):
        if sw.get("t25"): pr.k("rot25", [src, "rcos", "rsin", "roff", "rpr", "t25res", "t25lane", dst], (N, T, D, DH, sign, 1 if sw.get("voice") else 0), n_out=N * 3 * D)
        else: pr.k("rot", [src, "rcos", "rsin", "roff", "rpr", dst], (N, T, D, DH, sign), n_out=N * 3 * D)
    if x is None:                                                              # step loop: the host writes the batch before every step
        pr.buf("x", N * 4); pr.buf("y", N * 4); pr.buf("eord", N * 4); pr.buf("est", (V + 1) * 4)
    else:
        pr.buf("x", data=np.asarray(x, np.int32)); pr.buf("y", data=np.asarray(y, np.int32))
        order, st = batch_index(x, V); pr.buf("eord", data=order); pr.buf("est", data=st)
    BL = {}
    for l in range(L):
        for nm, (o_, i_) in (("qkv", (3 * D, D)), ("o", (D, D)), ("up", (4 * D, D)), ("down", (D, 4 * D))):
            key = f"blocks.{l}.{nm}.weight"; w = W[key]; s = pr.buf(f"s_{l}_{nm}", 4); t = pr.buf(f"t_{l}_{nm}", f(o_, i_)); wf = pr.buf(f"wf_{l}_{nm}", f(o_, i_))
            pr.k("red_part", [w, "part"], (0,)); pr.k("red_fin", [w, "part", s], (0,)); pr.k("tq", [w, s, t], n_out=o_ * i_); pr.k("wf", [w, s, wf], n_out=o_ * i_)
            BL[(l, nm)] = (w, s, t, wf, o_, i_)
    E = W["emb.weight"]
    pr.buf("X0", f(N, D)); pr.k("gather", [E, "x", "X0"], (N, D), n_out=N * D)
    def bl_fwd(l, nm, xin, out, base=None, tag=""):
        w, s, t, wf, o_, i_ = BL[(l, nm)]; p = f"{l}_{nm}"
        r = pr.buf(f"br_{p}", f(N)); g = pr.buf(f"bg_{p}", f(N)); q = pr.buf(f"bq_{p}", f(N, i_)); acc = pr.buf(f"ba_{p}", f(N, o_))
        pr.k("rstat", [xin, r], (N, i_), n_out=N); pr.k("actg", [xin, r, g], (N, i_), n_out=N); pr.k("actq", [xin, r, g, q], (N, i_), n_out=N * i_)
        pr.gemm("gnt", q, t, "dummy", acc, N, o_, i_, i_, i_, o_, False, hint="int")   # int8 activations × trits
        pr.k("blout", [acc, g, s, base or "dummy", out], (N, o_, 1 if base else 0), n_out=N * o_)
        return r, g
    def plate_scores(l, a, tag):
        """φ(q), φ(k) of the rotated head slices + the masked plate scores A (earlier row, same page) — forward, recomputed in backward"""
        phQ = pr.buf(f"phQ{tag}_{l}", f(B, H, T, DH)); pr.k("pphi", [a["Q"], phQ], n_out=B * H * T * DH)
        phK = pr.buf(f"phK{tag}_{l}", f(B, H, T, DH)); pr.k("pphi", [a["K"], phK], n_out=B * H * T * DH)
        A = pr.buf(f"A{tag}_{l}", f(B * H, T, T))
        pr.k("pscore", [phQ, phK, a["pbq"], a["pbk"], "rsBH", A], (T, DH), n_out=T * T, rows=B * H, row_strides=[T * DH, T * DH, T, T, T], out_stride=T * T)
        return phQ, phK, A
    def plate_fwd(l, a):
        a["pbq"] = pr.buf(f"pbq_{l}", f(B, H, T)); pr.k("pbucket", [f"qkv0_{l}", "planes", "pw", a["pbq"]], (T, D, DH, H, 0), n_out=N * H)
        a["pbk"] = pr.buf(f"pbk_{l}", f(B, H, T)); pr.k("pbucket", [f"qkv0_{l}", "planes", "pw", a["pbk"]], (T, D, DH, H, 1), n_out=N * H)
        phQ, phK, A = plate_scores(l, a, "")
        a["pden"] = pr.buf(f"pden_{l}", f(B * H, T)); pr.k("pden", [A, a["pden"]], (T,), n_out=T, rows=B * H, row_strides=[T * T], out_stride=T)
        AV = pr.buf(f"pAV_{l}", f(B * H, T, DH)); pr.k("pv", [A, a["V"], AV], (T, DH), n_out=T * DH, rows=B * H, row_strides=[T * T, T * DH], out_stride=T * DH)
        a["Yp"] = pr.buf(f"pY_{l}", f(B * H, T, DH)); pr.k("pnorm", [AV, a["pden"], a["Yp"]], (DH,), n_out=T * DH, rows=B * H, row_strides=[T * DH, T], out_stride=T * DH)
        a["memy"] = pr.buf(f"memy_{l}", f(N, D)); pr.k("merge", [a["Yp"], a["memy"]], (B, T, H, DH), n_out=N * D)
    def plate_bwd(l, a, dY, dP, dQ, dK, dV, tg=""):
        """plate_core_bwd as masked linear attention: c_i = dy·y / den, G_ij = dP_ij / den_i − c_i on the plate mask, dφq = G φk,
        dφk = Gᵀ φq, dv += (A / den)ᵀ dy; dq += dφq ⊙ φ′(q), dk += dφk ⊙ φ′(k) — joined before the inverse rotation"""
        BH = B * H; phQ, phK, A = plate_scores(l, a, "b" + tg)
        c = pr.buf(f"pc_{l}{tg}", f(BH, T)); pr.k("pc", [dY, a["Yp"], a["pden"], c], (DH,), n_out=T, rows=BH, row_strides=[T * DH, T * DH, T], out_stride=T)
        G = pr.buf(f"pG_{l}{tg}", f(BH, T, T)); pr.k("pg", [A, dP, a["pden"], c, G], (T,), n_out=T * T, rows=BH, row_strides=[T * T, T * T, T, T], out_stride=T * T)
        Pp = pr.buf(f"pP_{l}{tg}", f(BH, T, T)); pr.k("pp", [A, a["pden"], Pp], (T,), n_out=T * T, rows=BH, row_strides=[T * T, T], out_stride=T * T)
        dpq = pr.buf(f"pdq_{l}{tg}", f(BH, T, DH)); pr.k("pv", [G, phK, dpq], (T, DH), n_out=T * DH, rows=BH, row_strides=[T * T, T * DH], out_stride=T * DH)
        dpk = pr.buf(f"pdk_{l}{tg}", f(BH, T, DH)); pr.k("ptv", [G, phQ, dpk], (T, DH), n_out=T * DH, rows=BH, row_strides=[T * T, T * DH], out_stride=T * DH)
        dpv = pr.buf(f"pdv_{l}{tg}", f(BH, T, DH)); pr.k("ptv", [Pp, dY, dpv], (T, DH), n_out=T * DH, rows=BH, row_strides=[T * T, T * DH], out_stride=T * DH)
        q2 = pr.buf(f"pdQ_{l}{tg}", f(BH, T, DH)); pr.k("pdphi", [dQ, dpq, a["Q"], q2], n_out=BH * T * DH)
        k2 = pr.buf(f"pdK_{l}{tg}", f(BH, T, DH)); pr.k("pdphi", [dK, dpk, a["K"], k2], n_out=BH * T * DH)
        v2 = pr.buf(f"pdV_{l}{tg}", f(BH, T, DH)); pr.k("wsum", [dV, dpv, v2], n_out=BH * T * DH)
        return q2, k2, v2
    acts = []
    xcur = "X0"
    for l in range(L):
        a = {"x0": xcur}
        a["r1"] = pr.buf(f"r1_{l}", f(N)); a["h1"] = pr.buf(f"h1_{l}", f(N, D))
        pr.k("rstat", [xcur, a["r1"]], (N, D), n_out=N); pr.k("rapply", [xcur, a["r1"], W[f"blocks.{l}.n1.weight"], a["h1"]], (N, D), n_out=N * D)
        a["qkv0"] = pr.buf(f"qkv0_{l}", f(N, 3 * D)); a["bq"] = bl_fwd(l, "qkv", a["h1"], a["qkv0"])
        a["qkv"] = pr.buf(f"qkv_{l}", f(N, 3 * D)); rot("qkv0_%d" % l, a["qkv"], 1)
        for w_, nm in enumerate("QKV"):
            a[nm] = pr.buf(f"{nm}_{l}", f(B, H, T, DH)); pr.k("split3", [a["qkv"], a[nm]], (B, T, H, DH, w_), n_out=B * H * T * DH)
        BH = B * H; sc = 1.0 / math.sqrt(DH)
        a["S"] = pr.buf(f"S_{l}", f(BH, T, T)); pr.k("qkT", [a["Q"], a["K"], a["S"]], (T, DH), n_out=T * T, rows=BH, row_strides=[T * DH, T * DH], out_stride=T * T)
        a["st"] = pr.buf(f"st_{l}", f(BH, T, 3)); a["P"] = pr.buf(f"P_{l}", f(BH, T, T))
        if PL:                                                                 # plates: the softmax over the row's own keys only
            pr.k("astatsR", [a["S"], "rsBH", a["st"]], (T, sc), n_out=T * 3, rows=BH, row_strides=[T * T, T], out_stride=T * 3)
            pr.k("aprobR", [a["S"], a["st"], "rsBH", a["P"]], (T, sc), n_out=T * T, rows=BH, row_strides=[T * T, T * 3, T], out_stride=T * T)
        else:
            pr.k("astats", [a["S"], a["st"]], (T, sc), n_out=T * 3, rows=BH, row_strides=[T * T], out_stride=T * 3)
            pr.k("aprob", [a["S"], a["st"], a["P"]], (T, sc), n_out=T * T, rows=BH, row_strides=[T * T, T * 3], out_stride=T * T)
        if HM:                                                                 # the heads heard on the rings → the penalty's weights per (head, ring)
            hz = pr.buf(f"hz_{l}", f(BH, T, 10)); pr.k("harmz", [a["P"], "htc", "hts", "hro", "hrp", hz], (T,), n_out=T * 10, rows=BH, row_strides=[T * T, 0, 0, 0, 0], out_stride=T * 10)
            a["hw"] = pr.buf(f"hw_{l}", f(BH, T, 10)); pr.k("harmw", [hz, a["hw"]], (H, T, float(HM[1]), float(HM[0]), float(N * 5), 1e-6), n_out=BH * T * 10)
            if RT:                                                             # rows that left below block l are not heard here
                lv = pr.buf(f"hlive_{l}", f(N)); pr.k("exmask", ["ex", lv], (l,), n_out=N)
                hm2 = pr.buf(f"hwm_{l}", f(BH, T, 10)); pr.k("hwmask", [a["hw"], lv, hm2], (H, T), n_out=BH * T * 10); a["hw"] = hm2
        a["O"] = pr.buf(f"O_{l}", f(BH, T, DH)); pr.k("pv", [a["P"], a["V"], a["O"]], (T, DH), n_out=T * DH, rows=BH, row_strides=[T * T, T * DH], out_stride=T * DH)
        a["att"] = pr.buf(f"att_{l}", f(N, D)); pr.k("merge", [a["O"], a["att"]], (B, T, H, DH), n_out=N * D)
        a["oin"] = a["att"]
        if PL:                                                                 # the plate read joins attention's output before o
            plate_fwd(l, a); a["oin"] = pr.buf(f"attm_{l}", f(N, D)); pr.k("wsum", [a["att"], a["memy"], a["oin"]], n_out=N * D)
        a["x1"] = pr.buf(f"x1_{l}", f(N, D)); a["bo"] = bl_fwd(l, "o", a["oin"], a["x1"], base=xcur)
        a["r2"] = pr.buf(f"r2_{l}", f(N)); a["h2"] = pr.buf(f"h2_{l}", f(N, D))
        pr.k("rstat", [a["x1"], a["r2"]], (N, D), n_out=N); pr.k("rapply", [a["x1"], a["r2"], W[f"blocks.{l}.n2.weight"], a["h2"]], (N, D), n_out=N * D)
        a["up"] = pr.buf(f"up_{l}", f(N, 4 * D)); a["bu"] = bl_fwd(l, "up", a["h2"], a["up"])
        a["u"] = pr.buf(f"u_{l}", f(N, 4 * D)); pr.k("relu2", [a["up"], a["u"]], n_out=N * 4 * D)
        xn = pr.buf(f"X{l + 1}", f(N, D)); a["bd"] = bl_fwd(l, "down", a["u"], xn, base=a["x1"])
        if RT and l > 0:                                                       # rows that left below block l keep their state through it
            xr = pr.buf(f"Xr{l + 1}", f(N, D)); pr.k("rowsel", [xcur, xn, "ex", xr], (D, l), n_out=N * D); xn = xr
        if LC and l < L - 1:                                                   # block l's own read-out norm (the local rule's read-out; routing reads it)
            a["rr"] = pr.buf(f"lr_{l}", f(N)); a["hn"] = pr.buf(f"lh_{l}", f(N, D)); a["xo"] = xn
            pr.k("rstat", [xn, a["rr"]], (N, D), n_out=N); pr.k("rapply", [xn, a["rr"], W[f"local.n{l}"], a["hn"]], (N, D), n_out=N * D)
            if RT:                                                             # route_check: a settled, offer-free, running row with margin ≥ θ leaves here
                lg = pr.buf(f"rtlg_{l}", f(N, V)); pr.gemm("gnt", a["hn"], E, "dummy", lg, N, V, D, D, D, V, False)
                rtcheck(pr, lg, xn, xcur, "ex", "pkind" if sw.get("port") else "nokind", N, V, D, l, L, float(LC["route"]), float(LC.get("sat", 0.0)), 1 if sw.get("port") else 0, f"t{l}")
                pr.k("rtce", [lg, "y", "ex", "rce", "rce"], (V, l), n_out=N)
        acts.append(a); xcur = xn
    if PT:                                                                     # port_fwd: x_final += g·U(w·E[prop]) on the offer rows; pointer bias
        K_ = int(PT["K"]); mid = f"X{L // 2}"; Wr = W["port.router.weight"]
        pr.buf("pr0", f(N, K_)); pr.gemm("gnt", mid, Wr, "dummy", "pr0", N, K_, D, D, D, K_, False)
        pr.buf("prr", f(N, K_)); pr.k("addbias", ["pr0", W["port.router.bias"], "prr"], (K_,), n_out=N * K_)
        pr.buf("pst", f(N, 5)); pr.k("pstat", ["prr", "pst"], (K_,), n_out=N * 5)
        pr.buf("pgw", f(N, 2)); pr.k("pgwH" if PT.get("hard") else "pgw", ["prr", "pst", "pkind", "pprop", "pgw"], (K_, float(PT["theta"]), float(PT["tau"])), n_out=N * 2)
        pr.buf("pvv", f(N, D)); pr.k("pvec", [E, "pgw", "pkind", "pprop", "pvv"], (K_, D), n_out=N * D)
        pr.buf("puv", f(N, D)); pr.gemm("gnt", "pvv", W["port.U.weight"], "dummy", "puv", N, D, D, D, D, D, False)
        pr.buf("xport", f(N, D)); pr.k("raxpy2", [xcur, "puv", "pgw", "xport"], (D, 2, 0), n_out=N * D)
        PB = "port.ptr" in W
        if PB: pr.buf("ppb", f(N)); pr.k("pptrb", ["pgw", W["port.ptr"], "pkind", "pprop", "ppb"], (K_,), n_out=N)
        xcur = "xport"
    # ── head ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    pr.buf("rf", f(N)); pr.buf("hf", f(N, D)); pr.k("rstat", [xcur, "rf"], (N, D), n_out=N); pr.k("rapply", [xcur, "rf", W["nf.weight"], "hf"], (N, D), n_out=N * D)
    pr.buf("logits", f(N, V)); pr.gemm("gnt", "hf", E, "dummy", "logits", N, V, D, D, D, V, False)
    if PT and PB: pr.k("hptr", ["logits", "ppb", "pprop", "logits"], (V,), n_out=N * V)   # pointer: the offered token's logit (before copy)
    CP = "copy.q" in W and sw.get("copy")                                      # context copy pointer (COPY): scores per sequence, logits += β g a
    if CP:
        C_ = 64; csc = 1.0 / math.sqrt(C_)
        pr.buf("cQ", f(N, C_)); pr.gemm("gnt", "hf", W["copy.q"], "dummy", "cQ", N, C_, D, D, D, C_, False)
        pr.buf("cK", f(N, C_)); pr.gemm("gnt", "hf", W["copy.k"], "dummy", "cK", N, C_, D, D, D, C_, False)
        pr.buf("cS", f(B, T, T)); pr.k("qkT", ["cQ", "cK", "cS"], (T, C_), n_out=T * T, rows=B, row_strides=[T * C_, T * C_], out_stride=T * T)
        pr.buf("cst", f(B, T, 3)); pr.k("astats", ["cS", "cst"], (T, csc), n_out=T * 3, rows=B, row_strides=[T * T], out_stride=T * 3)
        pr.buf("cA", f(B, T, T)); pr.k("aprob", ["cS", "cst", "cA"], (T, csc), n_out=T * T, rows=B, row_strides=[T * T, T * 3], out_stride=T * T)
        pr.buf("cg", f(N)); pr.k("cpgate", ["hf", W["copy.gw"], W["copy.gb"], "cg"], (D,), n_out=N)
        pr.k("cpadd", ["logits", "cA", "cg", W["copy.beta"], "eord", "est", "logits"], (T, V), n_out=N * V)
    if fwd_only:                                                               # the forward alone (eval / decode, GROW-RUN-0): head stats, loss, top-1
        assert not RT, "forward-only: depth routing off (the eval sets route 0)"
        pr.buf("hst", f(N, 3))
        if AV: hstats(pr, "logits", "y", "onesH", "pavoid", "hst", N, V, AV, "f0")
        else: pr.k("hstats", ["logits", "y", "hst"], (N, V), n_out=N * 3)
        pr.buf("loss", 4); pr.k("lsum", ["hst", "loss"], (N,), n_out=1)
        pr.buf("hit", f(N)); pr.k("thit", ["logits", "y", "hst", "hit"], (N, V), n_out=N)
        return {}, pr.tag + "loss", pr.tag + "hst"
    dl = "logits"                                                              # M0: dl written over the logits (each element reads only itself)
    if AV:                                                                     # avoid-aware head (+ the routing mask when routing is on)
        hm = "onesH"
        if RT: pr.buf("hmask", f(N)); pr.k("exmask", ["ex", "hmask"], (L,), n_out=N); hm = "hmask"
        pr.buf("hst", f(N, 3)); hstats(pr, "logits", "y", hm, "pavoid", "hst", N, V, AV, "hd")
        pr.buf("loss", 4)
        if RT: pr.k("lsumR", ["hst", "rce", "loss"], (N,), n_out=1)
        else: pr.k("lsum", ["hst", "loss"], (N,), n_out=1)
        pr.buf("skip", f(N))
        if sw.get("spark"): pr.k("hsparkA", ["logits", "y", "hst", hm, "pavoid", "skip"], (N, V, float(sw["spark"])), n_out=N)
        pr.k("hdlA", ["logits", "hst", "y", "skip", hm, "nN", "pavoid", dl], (V, float(AV)), n_out=N * V)
    elif RT:                                                                     # depth routing: rows that left early are y = −1 at the final head
        pr.buf("hmask", f(N)); pr.k("exmask", ["ex", "hmask"], (L,), n_out=N)
        pr.buf("hst", f(N, 3)); pr.k("hstatsM", ["logits", "y", "hmask", "hst"], (N, V), n_out=N * 3)
        pr.buf("loss", 4); pr.k("lsumR", ["hst", "rce", "loss"], (N,), n_out=1)
        pr.buf("skip", f(N))
        if sw.get("spark"): pr.k("hsparkM", ["logits", "y", "hst", "hmask", "skip"], (N, V, float(sw["spark"])), n_out=N)
        if "nN" not in pr.bufs: pr.buf("nN", data=np.array([float(N)], np.float32), glob=True, shared=True)
        pr.k("hdlN", ["logits", "hst", "y", "skip", "hmask", "nN", dl], (V,), n_out=N * V)
    else:
        pr.buf("hst", f(N, 3)); pr.k("hstats", ["logits", "y", "hst"], (N, V), n_out=N * 3)
        pr.buf("loss", 4); pr.k("lsum", ["hst", "loss"], (N,), n_out=1)
        if sw.get("spark"):                                                    # spark skip: confidently right rows carry no head gradient
            pr.buf("skip", f(N)); pr.k("hspark", ["logits", "y", "hst", "skip"], (N, V, float(sw["spark"])), n_out=N)
            pr.k("hdlx", ["logits", "hst", "y", "skip", dl], (N, V), n_out=N * V)
        else: pr.k("hdl", ["logits", "hst", "y", dl], (N, V), n_out=N * V)
    if sw.get("p3"):                                                           # P3 mask from this step's row losses (before any backward)
        p3p, p3f = sw["p3"]; pr.buf("p3m", f(N))
        if RT: pr.k("p3maskR", ["hst", "rce", "ex", "y", "stepv", "p3m"], (-math.log(p3p), int(p3f), L), n_out=N)
        else: pr.k("p3mask", ["hst", "y", "stepv", "p3m"], (-math.log(p3p), int(p3f)), n_out=N)
    def p3z(src, w, name):
        if not sw.get("p3"): return src
        o = pr.buf(name, f(N, w)); pr.k("rowmask", [src, "p3m", o], (w,), n_out=N * w); return o
    pr.buf("dh", f(N, D)); pr.gemm("gnn", dl, E, "dummy", "dh", N, D, V, V, D, D, False)
    pr.buf("gE0", f(V, D)); pr.gemm("gtn", dl, "hf", "dummy", "gE0", V, D, N, V, D, D, False)
    dhn = "dh"
    if CP:                                                                     # copy_bwd: its gradient joins the head's at hf
        pr.buf("cda", f(N, T)); pr.k("cpda", [dl, "cg", W["copy.beta"], "x", "cda"], (T, V), n_out=N * T)
        pr.buf("cds", f(N)); pr.k("cpdsum", ["cA", dl, "x", "cds"], (T, V), n_out=N)
        pr.buf("cs_", f(N)); pr.k("rdot", ["cA", "cda", "cs_"], (T,), n_out=N)
        pr.buf("cdS", f(B, T, T)); pr.k("ads", ["cA", "cda", "cs_", "cdS"], (T, csc), n_out=T * T, rows=B, row_strides=[T * T, T * T, T], out_stride=T * T)
        pr.buf("cdQ", f(N, C_)); pr.k("pv", ["cdS", "cK", "cdQ"], (T, C_), n_out=T * C_, rows=B, row_strides=[T * T, T * C_], out_stride=T * C_)
        pr.buf("cdK", f(N, C_)); pr.k("ptv", ["cdS", "cQ", "cdK"], (T, C_), n_out=T * C_, rows=B, row_strides=[T * T, T * C_], out_stride=T * C_)
        G["copy.q"] = pr.buf("g_cq", f(C_, D)); pr.gemm("gtn", "cdQ", "hf", "dummy", G["copy.q"], C_, D, N, C_, D, D, False)
        G["copy.k"] = pr.buf("g_ck", f(C_, D)); pr.gemm("gtn", "cdK", "hf", "dummy", G["copy.k"], C_, D, N, C_, D, D, False)
        pr.buf("dhc1", f(N, D)); pr.gemm("gnn", "cdQ", W["copy.q"], "dh", "dhc1", N, D, C_, C_, D, D, True)
        pr.buf("dhc2", f(N, D)); pr.gemm("gnn", "cdK", W["copy.k"], "dhc1", "dhc2", N, D, C_, C_, D, D, True)
        pr.buf("cdz", f(N)); pr.k("cpdz", ["cds", "cg", W["copy.beta"], "cdz"], n_out=N)
        G["copy.gw"] = pr.buf("g_cgw", f(D)); pr.k("colsum", ["cdz", "hf", G["copy.gw"]], (D,), n_out=D)
        pr.buf("dhc3", f(N, D)); pr.k("rowaxpy", ["dhc2", "cdz", W["copy.gw"], "dhc3"], (D,), n_out=N * D)
        G["copy.gb"] = pr.buf("g_cgb", 4); pr.k("vsum", ["cdz", G["copy.gb"]], n_out=1)
        G["copy.beta"] = pr.buf("g_cb", 4); pr.k("cpdb", ["cg", "cds", W["copy.beta"], G["copy.beta"]], n_out=1)
        dhn = "dhc3"
    pass                                                                       # zero buffers are global (setup)
    def rms_bwd(xin, g, r, dy, dxin, dxout, dgout, tag):
        s = pr.buf(f"rs_{tag}", f(N)); pr.k("rbs", [dy, g, xin, s], (N, D), n_out=N)
        pr.k("rbx", [dxin, dy, g, xin, r, s, dxout], (N, D), n_out=N * D)
        if dgout is not None: pr.k("rbg", ["zeroD", dy, xin, r, dgout], (N, D), n_out=D)
    G["nf.weight"] = pr.buf("g_nf", f(D)); pr.buf("dxL", f(N, D))
    rms_bwd(xcur, W["nf.weight"], "rf", p3z(dhn, D, "dh_p3"), "zeroND", "dxL", G["nf.weight"], "nf")
    dmid = None
    if PT:                                                                     # port_bwd from ∂L/∂x_final (the residual passes it on unchanged)
        if PB: pr.buf("pdl", f(N)); pr.k("pgather", [dl, "ppb", "pprop", "pdl"], (V,), n_out=N); beta = W["port.ptr"]
        else: pr.buf("pdl", f(N)); pr.buf("pbeta0", f(K_)); beta = "pbeta0"
        pr.buf("pgdx", f(N, D)); pr.k("pgdx", ["dxL", "pgw", "pkind", "pprop", "pgdx"], (K_, D), n_out=N * D)
        G["port.U.weight"] = pr.buf("g_pU", f(D, D)); pr.gemm("gtn", "pgdx", "pvv", "dummy", G["port.U.weight"], D, D, N, D, D, D, False)
        pr.buf("pdv", f(N, D)); pr.gemm("gnn", "pgdx", W["port.U.weight"], "dummy", "pdv", N, D, D, D, D, D, False)
        pr.buf("pdgw", f(N, 2)); pr.k("pdgw", ["dxL", "puv", "pdv", E, "pgw", "pkind", "pprop", beta, "pdl", "pdgw"], (K_, D), n_out=N * 2)
        pr.buf("pdrp", f(N, K_)); pr.k("pdr", ["prr", "pst", "pgw", "pdgw", "pkind", "pprop", "pdrp"], (K_, float(PT["tau"]), float(PT.get("rce", 0.0)), N, 0), n_out=N * K_)
        pr.buf("pdrc", f(N, K_))
        if PT.get("rce", 0.0) > 0: pr.k("pdr", ["prr", "pst", "pgw", "pdgw", "pkind", "pprop", "pdrc"], (K_, float(PT["tau"]), float(PT["rce"]), N, 1), n_out=N * K_)
        G["port.router.bias"] = pr.buf("g_pb", f(K_)); pr.k("colsum2", ["pdrp", "pdrc", G["port.router.bias"]], (K_,), n_out=K_)
        G["port.router.weight"] = pr.buf("g_pw0", f(K_, D))                  # the simplex router is fixed (never updated)
        if PB: G["port.ptr"] = pr.buf("g_pptr", f(K_)); pr.k("pdbeta", ["pgw", "pkind", "pprop", "pdl", G["port.ptr"]], (K_,), n_out=K_)
        dmid = pr.buf("pdmid", f(N, D)); pr.gemm("gnn", "pdrp", Wr, "dummy", dmid, N, D, K_, K_, D, D, False)
    def bl_bwd(l, nm, xin, rg, dy, dxout, wg=True, tg=""):
        w, s, t, wf, o_, i_ = BL[(l, nm)]; p = f"{l}_{nm}{tg}"; r, g = rg
        da = pr.buf(f"da_{p}", f(N, i_)); pr.gemm("gnn", dy, wf, "dummy", da, N, i_, o_, o_, i_, i_, False)
        sb = pr.buf(f"bs_{p}", f(N)); pr.k("bs", [da, xin, sb], (N, i_), n_out=N)
        pr.k("bx", [da, xin, r, sb, dxout], (N, i_), n_out=N * i_)
        if wg:
            xq = pr.buf(f"xq_{p}", f(N, i_)); pr.k("xq", [xin, r, g, xq], (N, i_), n_out=N * i_)
            gw = pr.buf(f"g_{p}", f(o_, i_)); pr.gemm("gtn", dy, xq, "dummy", gw, o_, i_, N, o_, i_, i_, False)
            G[f"blocks.{l}.{nm}.weight"] = gw
    def block_bwd(l, dxin, up, tg):
        """one block's backward (omni_train.cpp:1796): dxin = ∂L/∂(block output) → returns ∂L/∂(block input); up = this block's weight
        + gain gradients and harmony (False = input gradient only: the local rule's one-block carry)"""
        a = acts[l]; BH = B * H; sc = 1.0 / math.sqrt(DH); q = f"{l}{tg}"
        dx = p3z(dxin, D, f"dxin_p3_{q}")                                     # P3: confirmed rows carry no gradient into this block
        def dout(v, nm):                                                       # depth routing: rows that left below block l → no gradient into its o / MLP outputs
            if not RT: return v
            lv = pr.buf(f"blive_{q}_{nm}", f(N)); pr.k("exmask", ["ex", lv], (l,), n_out=N)
            o = pr.buf(f"dout_{q}_{nm}", f(N, D)); pr.k("rowmask", [v, lv, o], (D,), n_out=N * D); return o
        ub = pr.buf(f"ub_{q}", f(N, 4 * D)); pr.k("relu2", [a["up"], ub], n_out=N * 4 * D)   # M0: u recomputed, not kept from the forward
        t4 = pr.buf(f"t4_{q}", f(N, 4 * D)); bl_bwd(l, "down", ub, a["bd"], dout(dx, "d"), t4, up, tg)
        t4b = pr.buf(f"t4b_{q}", f(N, 4 * D)); pr.k("relu2b", [t4, a["up"], t4b], n_out=N * 4 * D)
        tn = pr.buf(f"tn_{q}", f(N, D)); bl_bwd(l, "up", a["h2"], a["bu"], t4b, tn, up, tg)
        dx1 = pr.buf(f"dx1_{q}", f(N, D))
        if up: G[f"blocks.{l}.n2.weight"] = pr.buf(f"g_n2_{l}", f(D))
        rms_bwd(a["x1"], W[f"blocks.{l}.n2.weight"], a["r2"], tn, dx, dx1, G[f"blocks.{l}.n2.weight"] if up else None, f"n2_{q}")
        datt = pr.buf(f"datt_{q}", f(N, D)); bl_bwd(l, "o", a["oin"], a["bo"], dout(dx1, "o"), datt, up, tg)
        dY = pr.buf(f"dY_{q}", f(B, H, T, DH)); pr.k("split1", [datt, dY], (B, T, H, DH, 0), n_out=B * H * T * DH)
        Sb = pr.buf(f"Sb_{q}", f(BH, T, T)); pr.k("qkT", [a["Q"], a["K"], Sb], (T, DH), n_out=T * T, rows=BH, row_strides=[T * DH, T * DH], out_stride=T * T)   # M0: scores recomputed
        Pb = pr.buf(f"Pb_{q}", f(BH, T, T))
        if PL: pr.k("apbR", [Sb, a["st"], "rsBH", Pb], (T, sc), n_out=T * T, rows=BH, row_strides=[T * T, T * 3, T], out_stride=T * T)
        else: pr.k("apb", [Sb, a["st"], Pb], (T, sc), n_out=T * T, rows=BH, row_strides=[T * T, T * 3], out_stride=T * T)
        dP = pr.buf(f"dP_{q}", f(BH, T, T)); pr.k("qkT", [dY, a["V"], dP], (T, DH), n_out=T * T, rows=BH, row_strides=[T * DH, T * DH], out_stride=T * T)
        Di = pr.buf(f"Di_{q}", f(BH, T)); pr.k("adi", [dY, a["O"], Di], (T, DH), n_out=T, rows=BH, row_strides=[T * DH, T * DH], out_stride=T)
        dS = pr.buf(f"dS_{q}", f(BH, T, T))
        if HM and up:                                                          # harmony trains the block's own weight pass, never the carry
            Dh = pr.buf(f"Dh_{q}", f(BH, T)); pr.k("harmdh", [Pb, a["hw"], "htc", "hts", "hro", "hrp", Dh], (T,), n_out=T, rows=BH, row_strides=[T * T, T * 10, 0, 0, 0, 0], out_stride=T)
            pr.k("adsH", [Pb, dP, Di, a["hw"], Dh, "htc", "hts", "hro", "hrp", dS], (T, sc), n_out=T * T, rows=BH, row_strides=[T * T, T * T, T, T * 10, T, 0, 0, 0, 0], out_stride=T * T)
        else: pr.k("ads", [Pb, dP, Di, dS], (T, sc), n_out=T * T, rows=BH, row_strides=[T * T, T * T, T], out_stride=T * T)
        dQ = pr.buf(f"dQ_{q}", f(BH, T, DH)); pr.k("pv", [dS, a["K"], dQ], (T, DH), n_out=T * DH, rows=BH, row_strides=[T * T, T * DH], out_stride=T * DH)
        dK = pr.buf(f"dK_{q}", f(BH, T, DH)); pr.k("ptv", [dS, a["Q"], dK], (T, DH), n_out=T * DH, rows=BH, row_strides=[T * T, T * DH], out_stride=T * DH)
        dV = pr.buf(f"dV_{q}", f(BH, T, DH)); pr.k("ptv", [Pb, dY, dV], (T, DH), n_out=T * DH, rows=BH, row_strides=[T * T, T * DH], out_stride=T * DH)
        if PL: dQ, dK, dV = plate_bwd(l, a, dY, dP, dQ, dK, dV, tg)
        dq0 = pr.buf(f"dq0_{q}", f(N, 3 * D)); pr.k("merge3", [dQ, dK, dV, dq0], (B, T, H, DH), n_out=N * 3 * D)
        dq = pr.buf(f"dq_{q}", f(N, 3 * D)); rot(dq0, dq, -1)
        dq = p3z(dq, 3 * D, f"dq_p3_{q}")                                      # P3: no K / V gradient into confirmed rows
        tn2 = pr.buf(f"tn2_{q}", f(N, D)); bl_bwd(l, "qkv", a["h1"], a["bq"], dq, tn2, up, tg)
        dx0 = pr.buf(f"dx0_{q}", f(N, D))
        if up: G[f"blocks.{l}.n1.weight"] = pr.buf(f"g_n1_{l}", f(D))
        rms_bwd(a["x0"], W[f"blocks.{l}.n1.weight"], a["r1"], tn2, dx1, dx0, G[f"blocks.{l}.n1.weight"] if up else None, f"n1_{q}")
        return dx0
    if LC:                                                                     # THE LOCAL RULE (local = 2, J 10-04): each block learns from its own read-out
        roles = LC.get("roles"); S_ = int(LC.get("S", 4))                      # + the block above's read-out carried one block back
        if not sw.get("p3") and "onesN" not in pr.bufs: pr.buf("onesN", N * 4); pr.k("fillc", ["onesN"], (N, 1.0), n_out=N)
        drce = None
        if PT and float(PT.get("rce", 0.0)) > 0:                               # supervised routing reaches the router's mid even under the local rule
            drce = pr.buf("pdrce", f(N, D)); pr.gemm("gnn", "pdrc", Wr, "dummy", drce, N, D, K_, K_, D, D, False)
        def readout(l):
            """local_readout:1763 — block l's selected rows read out through its own norm + the tied codebook (frozen there) → CE / Ns"""
            a = acts[l]; sel = pr.buf(f"lsel_{l}", f(N))
            pr.k("lsel", ["ex", "p3m" if sw.get("p3") else "onesN", "pstage" if roles else "x", "stepv", "pw32", sel],
                 (l, int(roles[l]) if roles else 0, S_, 1 if RT else 0, 1 if roles and roles[l] else 0), n_out=N)
            ns = pr.buf(f"lns_{l}", 4); pr.k("vsum", [sel, ns], n_out=1)
            lg = pr.buf(f"rlg_{l}", f(N, V)); pr.gemm("gnt", a["hn"], E, "dummy", lg, N, V, D, D, D, V, False)
            hs = pr.buf(f"rhst_{l}", f(N, 3)); sk = pr.buf(f"rskip_{l}", f(N))
            if AV:                                                             # the study's avoid push reaches every block's own read-out
                hstats(pr, lg, "y", sel, "pavoid", hs, N, V, AV, f"rl{l}")
                if sw.get("spark"): pr.k("hsparkA", [lg, "y", hs, sel, "pavoid", sk], (N, V, float(sw["spark"])), n_out=N)
                pr.k("hdlA", [lg, hs, "y", sk, sel, ns, "pavoid", lg], (V, float(AV)), n_out=N * V)
            else:
                pr.k("hstatsM", [lg, "y", sel, hs], (N, V), n_out=N * 3)
                if sw.get("spark"): pr.k("hsparkM", [lg, "y", hs, sel, sk], (N, V, float(sw["spark"])), n_out=N)
                pr.k("hdlN", [lg, hs, "y", sk, sel, ns, lg], (V,), n_out=N * V)
            dhl = pr.buf(f"rdh_{l}", f(N, D)); pr.gemm("gnn", lg, E, "dummy", dhl, N, D, V, V, D, D, False)
            own = pr.buf(f"own_{l}", f(N, D)); G[f"local.n{l}"] = pr.buf(f"g_ln_{l}", f(D))
            rms_bwd(a["xo"], W[f"local.n{l}"], a["rr"], dhl, "zeroND", own, G[f"local.n{l}"], f"ln_{l}")
            return own
        carry = None
        for l in reversed(range(L)):
            own = "dxL" if l == L - 1 else readout(l)
            if drce is not None and l == L // 2 - 1:
                o2 = pr.buf(f"ownrce_{l}", f(N, D)); pr.k("wsum", [own, drce, o2], n_out=N * D); own = o2
            gl = own
            if carry is not None: gl = pr.buf(f"gl_{l}", f(N, D)); pr.k("wsum", [own, carry, gl], n_out=N * D)
            block_bwd(l, gl, True, "u")                                        # weights learn from own + carried
            carry = block_bwd(l, own, False, "c")                              # what travels one block back: own only, input gradient only
        dx = carry
    else:
        dx = "dxL"
        for l in reversed(range(L)):
            if dmid is not None and l == L // 2 - 1:                           # the port's mid gradient joins at the output of block L/2 − 1
                dxm = pr.buf(f"dxmid_{l}", f(N, D)); pr.k("wsum", [dx, dmid, dxm], n_out=N * D); dx = dxm
            dx = block_bwd(l, dx, True, "")
    G["emb.weight"] = pr.buf("gE", f(V, D)); pr.k("embg", ["gE0", dx, "eord", "est", "gE"], (V, D), n_out=V * D)
    return G, pr.tag + "loss", pr.tag + "hst"

def plate_planes(DH):
    """omni_train.cpp:1134 mem_init_planes: the LSH planes [DH, 12] (xorshift64 from 1729 + Box–Muller in double, rounded to float32)"""
    M = (1 << 64) - 1; st = 1729; out = np.zeros(DH * 12, np.float32)
    def nxt(v): v ^= (v << 13) & M; v ^= v >> 7; v ^= (v << 17) & M; return v
    for i in range(DH * 12):
        st = nxt(st); u = (st >> 11) * (1.0 / 9007199254740992.0) + 1e-300
        st = nxt(st); w = (st >> 11) * (1.0 / 9007199254740992.0)
        out[i] = np.float32(math.sqrt(-2 * math.log(u)) * math.cos(2 * math.pi * w))
    return out

def row_starts(x, B, T, eos, H):
    """forward_backward:2076 each position's row start (rows end at eos), repeated per head → [B][H][T] (the plates' per-(b, h) rows)"""
    x = np.asarray(x).reshape(B, T); rs = np.zeros((B, T), np.int32)
    for b in range(B):
        st = 0
        for t in range(T):
            rs[b, t] = st
            if x[b, t] == eos: st = t + 1
    return np.repeat(rs[:, None, :], H, axis=1).reshape(-1)

def batch_index(x, V):
    """the embedding scatter's grouping: positions sorted by token (stable: n order inside a token) + each token's start"""
    order = np.argsort(np.asarray(x), kind="stable").astype(np.int32); st = np.zeros(V + 1, np.int32); np.add.at(st, np.asarray(x) + 1, 1)
    return order, np.cumsum(st).astype(np.int32)

def step_scalars(step, lr, wd=0.1, b1=0.9, b2=0.95, eps=1e-8):
    """opt_step's per-step constants, float32 as the engine (powf from libm): [coef (GPU), lr, wd, b1, b2, lr/bc1, √bc2, eps]"""
    import ctypes
    powf = ctypes.CDLL("libm.so.6").powf; powf.restype = ctypes.c_float; powf.argtypes = [ctypes.c_float, ctypes.c_float]
    f32 = np.float32; bc1 = f32(1) - f32(powf(f32(b1), f32(step + 1))); bc2 = f32(1) - f32(powf(f32(b2), f32(step + 1)))
    return np.array([0, lr, wd, b1, b2, f32(lr) / bc1, np.sqrt(bc2, dtype=np.float32), eps], np.float32)

def adamw(pr, params, W, M, Vm, G, step, lr, wd=0.1, b1=0.9, b2=0.95, clip=1.0, eps=1e-8, inplace=False, copy_w=True, frozen=()):
    """opt_step (omni_train.cpp:2304), mode 0, every parameter trained: clip norm in float64 (P order) → AdamW per parameter → new W, M, V"""
    import ctypes
    powf = ctypes.CDLL("libm.so.6").powf; powf.restype = ctypes.c_float; powf.argtypes = [ctypes.c_float, ctypes.c_float]
    f32 = np.float32
    bc1 = f32(1) - f32(powf(f32(b1), f32(step + 1))); bc2 = f32(1) - f32(powf(f32(b2), f32(step + 1)))
    sc = np.array([0, lr, wd, b1, b2, f32(lr) / bc1, np.sqrt(bc2, dtype=np.float32), eps], np.float32)
    if inplace: pr.buf("sc", 32); pr.buf("acc", 8)                           # step loop: the host writes sc (and zeroes acc) before every step
    else: pr.buf("sc", data=sc); pr.buf("acc", 8)
    for n, _ in params:
        if n in frozen: continue                                               # opt_step: a fixed parameter is outside the clip norm and the update
        pr.k("red_part", [G[n], "part"], (1,)); pr.k("red_fin", [G[n], "part", "acc"], (1,))
    pr.k("adam_scal", ["acc", "sc"], (clip,))
    W2, M2, V2 = {}, {}, {}
    for i, (n, w) in enumerate(params):
        if n in frozen: W2[n], M2[n], V2[n] = W[n], M[n], Vm[n]; continue
        sz = w.size * 4
        M2[n] = pr.buf(f"m_{i}", sz); pr.k("adam_m", [M[n], G[n], "sc", M2[n]], n_out=w.size)
        V2[n] = pr.buf(f"v_{i}", sz); pr.k("adam_v", [Vm[n], G[n], "sc", V2[n]], n_out=w.size)
        W2[n] = pr.buf(f"w_{i}", sz); pr.k("adam_w", [W[n], M2[n], V2[n], "sc", W2[n]], n_out=w.size)
        if inplace:                                                            # the step loop keeps one set: new values copied back in place
            for a_, b_ in ((M2[n], M[n]), (V2[n], Vm[n])) + (((W2[n], W[n]),) if copy_w else ()): pr.k("copy", [a_, b_], n_out=w.size)
    return ((W if copy_w else W2), M, Vm) if inplace else (W2, M2, V2)

def build(dims, params, x, y, wd, sw=None, aux=None):
    """S1 gate: one gradient step (om_grad) → (program text, {name: (buffer index, shape)}, passes, buffers)"""
    pr = Prog(wd); W = setup(pr, dims, params); pr.tag = "s0_"
    G, loss, hst = fwd_bwd(pr, dims, W, x, y, sw, aux)
    outs = {"loss": (loss, (1,)), "hst": (hst, None)}
    for n, _ in params: outs[f"g:{n}"] = (G[n], None)
    lines, idx = pr.program(pinned={b for b, _ in outs.values()}, plan=PLAN)
    reads = sorted({idx[b] for b, _ in outs.values()})
    return "\n".join(lines + [f"read {i}" for i in reads]) + "\n", {k: (idx[b], s) for k, (b, s) in outs.items()}, pr.passes, pr.nphys

def FROZEN(sw):
    return {"port.router.weight"} if (sw or {}).get("port") else set()

def build_train(dims, params, batches, lrs, wd, first_step=0):
    """K training steps (om_train_step each: forward, backward, AdamW) recorded back to back on resident buffers → (program text, outputs,
    passes, buffers); outputs: loss per step, final weights per parameter"""
    pr = Prog(wd); W = setup(pr, dims, params)
    M = {n: pr.buf(f"m0_{i}", w.size * 4, glob=True) for i, (n, w) in enumerate(params)}
    Vm = {n: pr.buf(f"v0_{i}", w.size * 4, glob=True) for i, (n, w) in enumerate(params)}
    outs = {}
    for s_, ((x, y), lr) in enumerate(zip(batches, lrs)):
        pr.tag = f"s{s_}_"; G, loss, hst = fwd_bwd(pr, dims, W, x, y); outs[f"loss:{s_}"] = (loss, (1,))
        W, M, Vm = adamw(pr, params, W, M, Vm, G, first_step + s_, lr)
    for n, _ in params: outs[f"w:{n}"] = (W[n], None)
    lines, idx = pr.program(pinned={b for b, _ in outs.values()}, plan=PLAN)
    reads = sorted({idx[b] for b, _ in outs.values()})
    return "\n".join(lines + [f"read {i}" for i in reads]) + "\n", {k: (idx[b], s) for k, (b, s) in outs.items()}, pr.passes, pr.nphys

def centre_split(params_R):
    """option 3's start: C = the replicas' mean (float64 sum in replica order, rounded once = hub_mean), Δ_h = W_h − C (float32)"""
    C, D = [], []
    for i, (n, _) in enumerate(params_R[0]):
        st = np.stack([p[i][1].astype(np.float32) for p in params_R]); c = st.astype(np.float64).mean(axis=0).astype(np.float32)
        C.append((n, c)); D.append(st - c)
    return C, D

def build_loop(dims, params, wd, params_R=None, form="replica", K=0.0, sw=None, aux=None, units=1, ring=None, fwd_only=False):
    """THE TRAINING LOOP: one recorded step (forward, backward, AdamW) on fixed resident buffers, re-submitted every step; before each step the
    host writes the batch (x, y, its token grouping) and the step scalars, zeroes the clip accumulator; after it, reads the loss.
    → (program text, buffer index by name: x y eord est sc acc loss + w:<param>), passes, buffers"""
    R = len(params_R) if params_R else 1; pr = Prog(wd, R, units); U = units; per = R // U
    assert U == 1 or (form == "centre" and R % U == 0), "units: the centre form with R = units · harnesses per unit"
    if form == "centre":                                                       # option 3 (plan § Model form): w0_* hold the deltas Δ_h, c0_* the cyclone's C
        PR_ = params_R or [params]; sp = [centre_split(PR_[u * per:(u + 1) * per]) for u in range(U)]   # G3b-3: one C per unit (the array)
        Cs = [(n, np.concatenate([sp[u][0][i][1] for u in range(U)])) for i, (n, _) in enumerate(params)]
        Ds = [np.concatenate([sp[u][1][i] for u in range(U)]) for i in range(len(params))]
        D = setup(pr, dims, params, [[(n, d[r]) for (n, _), d in zip(params, Ds)] for r in range(R)])
        C = {n: pr.buf(f"c0_{i}", data=c, glob=True, shared=True) for i, (n, c) in enumerate(Cs)}
        if ring:                                                               # the floor ring on the unit centres (cyclone W2c: centre unit ↔ the 4 around)
            F = U // 5; rep5 = lambda v, t: np.array([x for _ in range(F) for x in v], t)
            pr.buf("ko", data=rep5([0, 1, 1, 1, 1], np.uint32), glob=True, shared=True); pr.buf("kc", data=rep5([1, 0, 0, 0, 0], np.uint32), glob=True, shared=True)
            pr.buf("rko", data=rep5([0.0] + [ring["k2"]] * 4, np.float32), glob=True, shared=True)
            pr.buf("rkc", data=rep5([ring["k2c"], 0.0, 0.0, 0.0, 0.0], np.float32), glob=True, shared=True)
    else: W = setup(pr, dims, params, params_R)
    if form != "replica":
        pr.buf("keep", data=np.ones(R, np.uint32), glob=True, shared=True); pr.buf("kf", data=np.full(R, K, np.float32), glob=True, shared=True)
    M = {n: pr.buf(f"m0_{i}", w.size * 4, glob=True) for i, (n, w) in enumerate(params)}
    Vm = {n: pr.buf(f"v0_{i}", w.size * 4, glob=True) for i, (n, w) in enumerate(params)}
    pr.tag = "L_"
    if form == "centre":                                                       # W_h = C + Δ_h for this step
        W = {n: pr.buf(f"wh_{i}", w.size * 4) for i, (n, w) in enumerate(params)}
        for n, w in params: pr.k("wsum", [C[n], D[n], W[n]], n_out=w.size) if U == 1 else pr.k("wsum_g", [C[n], D[n], W[n]])
    if fwd_only:                                                               # forward only (eval / decode): no moments, no optimiser
        fwd_bwd(pr, dims, W, None, None, sw, aux, fwd_only=True)
        io = {k: "L_" + k for k in ("x", "y", "eord", "est", "loss", "hit", "hst") + tuple(k_ for k_ in ("t25res", "rsBH", "stepv", "pkind", "pprop", "pstage", "pavoid") if "L_" + k_ in pr.bufs)}
        for n, _ in params: io[f"w:{n}"] = W[n]
        lines, idx = pr.program(pinned=set(io.values()), plan=PLAN)
        return "\n".join(lines) + "\n", {k: idx[b] for k, b in io.items()}, pr.passes, pr.nphys
    G, loss, hst = fwd_bwd(pr, dims, W, None, None, sw, aux)
    W2, _, _ = adamw(pr, params, W, M, Vm, G, 0, 0.0, inplace=True, copy_w=(form != "centre"), frozen=FROZEN(sw))
    for i, (n, w) in enumerate(params):
        if form == "pull":                                                     # option 1 + the hub: every model pulled toward the unit's mean (shmbus.rs sync)
            hm = pr.buf(f"hm_{i}", w.size * 4, shared=True); pr.k("hub_mean", [W[n], "keep", hm]); pr.k("hub_pull", [W[n], hm, "kf"])
        elif form == "centre":                                                 # the cyclone: C = mean of the updated models; each harness keeps (1 − K)(W'_h − C)
            pr.k("hub_mean", [W2[n], "keep", C[n]])
            if ring:                                                           # floor ring: around-mean tc, centre-mean cc, then the two pulls (cyclone.rs order)
                tc = pr.buf(f"tc_{i}", (U // 5) * w.size * 4, shared=True); cc = pr.buf(f"cc_{i}", (U // 5) * w.size * 4, shared=True)
                pr.k("hub_mean", [C[n], "ko", tc], per=5, width=w.size); pr.k("hub_mean", [C[n], "kc", cc], per=5, width=w.size)
                pr.k("hub_pull", [C[n], cc, "rko"], per=5, width=w.size); pr.k("hub_pull", [C[n], tc, "rkc"], per=5, width=w.size)
            if U == 1: pr.k("dset", [W2[n], C[n], D[n]], (K,), n_out=w.size)
            else: pr.k("dset_g", [W2[n], C[n], D[n]], (K,))
    io = {k: "L_" + k for k in ("x", "y", "eord", "est", "sc", "acc", "loss") + tuple(k_ for k_ in ("t25res", "rsBH", "stepv", "pkind", "pprop", "pstage", "pavoid") if "L_" + k_ in pr.bufs)}
    for n, _ in params:
        if form == "centre": io[f"C:{n}"] = C[n]; io[f"D:{n}"] = D[n]
        else: io[f"w:{n}"] = W[n]
        io[f"m:{n}"] = M[n]; io[f"v:{n}"] = Vm[n]                              # the moments (the engine library's snapshot / restore)
    lines, idx = pr.program(pinned=set(io.values()), plan=PLAN)
    return "\n".join(lines) + "\n", {k: idx[b] for k, b in io.items()}, pr.passes, pr.nphys

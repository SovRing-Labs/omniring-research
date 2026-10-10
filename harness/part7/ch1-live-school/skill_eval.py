"""skill_eval — per-skill gates for the live school (LIVE-SCHOOL-0 L2, R3; J 10-08). On a run's checkpoint and a held-out build, the
top-1 per skill = (lesson, level) on the LEARNABLE positions only: tier-1 = transport (body plates), actions, operands, operators, the
state line — never the goal's first occurrence (R4 mask) nor the prompt stages; middle = the answer span. Level+1 rows of a frontier lesson
(R5 OOD) are reported under their own level, so the gate of level L+1 is measured before it is trained.
EVAL_B = rows per forward (default 1 = one row per call, as before); each row is padded at its END to the batch's longest row with target −1
(never scored; causal, so never seen by the row's own positions). With OMNI_TRAIN_LIB = the GPU engine library and OMR_GPU_EVAL=1 the
forward runs on the GPU (GROW-RUN-0: the eval off the CPU).
python3 skill_eval.py <run_dir> <heldout_build> <out.json> [min_n=24]"""
import collections, ctypes, json, os, sys
import numpy as np
import route_decode_check as rc
import tier1_symbols

L = rc.L
L.om_tok_hit.restype = ctypes.POINTER(ctypes.c_byte); L.om_tok_hit.argtypes = [ctypes.c_void_p]
SYM = tier1_symbols.load()
LEARN = {s["id"] for s in SYM["symbols"] if s["role"] not in ("PROMPT",)} | {6}          # every tier-1 symbol + [revise]
BODY = set(range(27, 31))


def main():
    R, HB, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; MIN_N = int(sys.argv[4]) if len(sys.argv) > 4 else 24
    L.om_threads(int(os.environ.get("OT_THREADS", "4"))); h, cfg = rc.load(R); assert L.om_set_route(h, 0.0) == 0
    man = json.load(open(f"{HB}/manifest.json")); book = man["port"]["domains"]; tier1 = "tier1" in man; nf = len(man["rows_sidecar"]["fields"])
    hit = collections.defaultdict(lambda: [0, 0]); rows_k = collections.Counter()   # rows = independent problems (GROW-RUN-0: PAC sample size)
    only = {int(x) for x in os.environ.get("PHASES", "").split(",") if x != ""}       # parallel scoring: one process per phase subset
    EB = int(os.environ.get("EVAL_B", "1"))
    for k in range(len(man["phases"])):
        if only and k not in only: continue
        d = np.fromfile(f"{HB}/phase_{k}.u16", dtype=np.uint16).astype(np.int32); kd = np.fromfile(f"{HB}/kind_{k}.u8", dtype=np.uint8)
        sg = np.fromfile(f"{HB}/stage_{k}.u8", dtype=np.uint8)
        mk = np.fromfile(f"{HB}/mask_{k}.u8", dtype=np.uint8) if os.path.exists(f"{HB}/mask_{k}.u8") else np.zeros(len(d), np.uint8)
        rows = np.fromfile(f"{HB}/rows_{k}.u32", dtype=np.uint32).reshape(-1, nf)
        todo = []
        for r in rows:
            s0 = int(r[0]); t = min(int(r[3]) - s0, 511, len(d) - s0 - 1)
            if t >= 4: todo.append((r, s0, t))
        for c0 in range(0, len(todo), EB):
            chunk = todo[c0:c0 + EB]; nb = len(chunk) if EB == 1 else EB; T_ = max(t for _, _, t in chunk) if EB == 1 else int(os.environ.get("EVAL_T", "511"))
            # batched: ONE shape (EB × EVAL_T) → one GPU program; a short last batch is filled with empty rows (target −1, never scored)
            X = np.zeros((nb, T_), np.int32); Y = np.full((nb, T_), -1, np.int32); KI = np.full((nb, T_), -1, np.int32)
            for i, (r, s0, t) in enumerate(chunk):
                X[i, :t] = d[s0:s0 + t]; Y[i, :t] = d[s0 + 1:s0 + t + 1]; KI[i, :t] = [int(v) if v != 255 else -1 for v in kd[s0:s0 + t]]
            PP = np.where(KI >= 0, Y, -1).astype(np.int32)
            X, Y, KI, PP = (np.ascontiguousarray(a_.reshape(-1)) for a_ in (X, Y, KI, PP))
            L.om_set_port_data(h, KI, PP, nb * T_); L.om_forward_loss(h, X, Y, nb, T_)
            HT = np.ctypeslib.as_array(L.om_tok_hit(h), shape=(nb * T_,)).copy()
            for i, (r, s0, t) in enumerate(chunk):
                ht = HT[i * T_:i * T_ + t]; y = Y[i * T_:i * T_ + t]; kinds = KI[i * T_:i * T_ + t]
                name, lv = book[int(r[5])], int(r[10])
                if tier1:
                    key = f"{name}@{lv}"; n0 = hit[key][1]
                    for j in range(t):
                        if mk[s0 + j] or int(sg[s0 + j]) in (0, 6): continue
                        if int(kinds[j]) in BODY or int(y[j]) in LEARN or int(sg[s0 + j]) == 7:
                            hit[key][0] += int(ht[j] != 0); hit[key][1] += 1
                else:
                    key = (f"hs.B.{name}@{lv}" if lv >= 6 else f"mid.{name}@{lv}"); n0 = hit[key][1]
                    for j in range(max(0, int(r[1]) - s0 - 1), min(t, int(r[2]) - s0 - 1)):
                        hit[key][0] += int(ht[j] != 0); hit[key][1] += 1
                if hit[key][1] > n0: rows_k[key] += 1
    skill = {k: round(a / n, 4) for k, (a, n) in hit.items() if n >= MIN_N}
    json.dump({"run": R, "heldout": HB, "skill": skill, "n": {k: n for k, (a, n) in hit.items()}, "hits": {k: a for k, (a, n) in hit.items()},
               "rows": dict(rows_k)}, open(OUT, "w"), indent=1)
    print("SKILL-EVAL", len(skill), "skills ·", sum(v >= 0.85 for v in skill.values()), "at ≥ 0.85")
    if os.environ.get("OMR_GPU_EVAL") == "1": sys.stdout.flush(); os._exit(0)   # the GPU driver's teardown at interpreter exit segfaulted (E1); the result is written


if __name__ == "__main__":
    main()

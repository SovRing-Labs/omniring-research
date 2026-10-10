#!/usr/bin/env python3
"""RG-1 — do exact reasoning traces teach a small trunk to REASON, or just add tokens? (<plan> §4, pre-registered
2026-10-03 BEFORE this harness was written.)

Trunk: CAL-3b size via cal3.LM("RESIDUE") — 4L d128 h4 ctx256, BitLinear, std-0.02 init — clean tokenizer
(~/gpurun-out-1003/tokenizer-clean), data from bin/reason-gen (rg-2). Four arms, same problems, same seed, same token budget:
  A  answers only           "Q: …\nA: …"
  B  full exact traces      "Q: …\n<trace lines with epistemic tags>\nA: …"
  C  B's trace lines shuffled (same tokens, order destroyed)
  D  forward-only traces    steps under guesses that were later retracted are removed, with the CONFLICT/RETRACT lines
Eval: greedy generation from "Q: …\n"; the text after the last "A: " must equal the answer exactly. Held-out problems
(different seed) at trained levels 1–3 (PRIMARY) and levels 4–5 (OOD, reported only).
PRE-REGISTERED (P1-SPEC §4): PASS = B ≥ A + 10 pts AND B ≥ C + 10 pts AND B ≥ D + 5 pts (primary). KILL: B ≤ A + 2.
DECLARED BEFORE RUNNING (deviation from the spec's domain list): ctx 256 is fixed, so only domains whose arm-B text fits in
CTX tokens at levels 1–3 for ≥ 90% of rows are used; the qualifying list is computed and written into the result.
Env: RG1_TOKENS (default 10M per arm), RG1_THREADS (4), RG1_OUT, SMOKE=1 (tiny dims, seconds).
"""
import importlib.machinery
import json
import math
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("CAL3_THREADS", os.environ.get("RG1_THREADS", "4"))
import torch  # noqa: E402
import torch.nn.functional as F  # noqa: E402
import cal3  # noqa: E402  (LM, V, CTX, B, DEV, BitLinear trunk; module import does not load data)
from cleanguard import require_clean  # noqa: E402
from ternary import BitLinear, ternary_weight  # noqa: E402

H = os.path.expanduser("~")
RG = importlib.machinery.SourceFileLoader("reason_gen", f"{H}/ai-stack/bin/reason-gen").load_module()
TOKF = os.environ.get("RG1_TOK", f"{H}/gpurun-out-1003/tokenizer-glyph-fix/tokenizer.json")
CTX = int(os.environ.get("RG1_CTX", "64" if os.environ.get("SMOKE") == "1" else "512"))   # amendment: ctx 512
BATCH = int(os.environ.get("RG1_BATCH", "8"))                                            # 8 × 512 = 16 × 256 tokens/step
OUT = os.path.expanduser(os.environ.get("RG1_OUT", "~/gpurun-out-1003/rg1/rg1.result.json"))
SMOKE = cal3.SMOKE
TOKENS = int(float(os.environ.get("RG1_TOKENS", "2e5" if SMOKE else "1e7")))
N_TRAIN, N_ID, N_OOD = (60, 10, 5) if SMOKE else (4000, 60, 30)
CANDIDATES = ["logic.chain", "graph.path", "units.dimension", "calendar.crt", "mind.revise", "mind.tom", "causal.dag",
              "struct.pushdown", "sat.dpll", "arith.mul", "arith.mrc_compare", "search.astar", "graph.group_walk",
              "calendar.ring_euclid", "numth.prime_trial", "code.debug"]
NATIVE = {old: new for new, old in RG.NATIVE_OF.items()}                                 # arm E swaps these in


def trace_lines(row, R, arm):
    steps = row["trace"]
    if arm == "D":                                       # forward-only: drop every failed branch and its conflict/retract
        keep, stack = [], []
        for s in steps:
            if s["op"] == "GUESS":
                stack.append(len(keep)); keep.append(s)
            elif s["op"] == "RETRACT":
                keep = keep[:stack.pop()] if stack else keep
            elif s["op"] == "CONFLICT":
                continue
            else:
                keep.append(s)
        steps = keep
    lines = [f"[{s['ep']}] " + R.choice(RG.RENDER[s["op"]]).format(a=s["a"], r=s["r"]) for s in steps]
    if arm == "C":
        R.shuffle(lines)
    return lines


def text(row, arm, R):
    ans = json.dumps(row["answer"], ensure_ascii=False) if not isinstance(row["answer"], str) else row["answer"]
    body = "" if arm == "A" else "\n".join(trace_lines(row, R, arm)) + "\n"
    return f"Q: {row['question']}\n{body}A: {ans}", ans


def main():
    require_clean(TOKF)
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(TOKF); eos = tok.token_to_id("<|eos|>")
    t0 = time.time()
    # 1. which domains fit the context (arm B at levels 1-3)?
    fit = {}
    for d in CANDIDATES:
        rows = [RG.make(d, i, 900, 1 + i % 3) for i in range(30)]
        lens = [len(tok.encode(text(r, "B", random.Random(i))[0]).ids) + 1 for i, r in enumerate(rows)]
        fit[d] = sum(x <= CTX for x in lens) / len(lens)
    doms = [d for d in CANDIDATES if fit[d] >= 0.9]
    if SMOKE:                                           # tiny smoke context: just take the two best-fitting domains
        doms = sorted(CANDIDATES, key=lambda d: -fit[d])[:2]
    print(f"RG-1 domains fitting CTX {CTX}: {doms} (fit {json.dumps({k: round(v, 2) for k, v in fit.items()})})", flush=True)
    # 2. problems (train seed 100, held-out seed 200 ID, 300 OOD)
    def rows_for(dlist, seed, n, lv):
        return [RG.make(d, i, seed, lv(i)) for d in dlist for i in range(n)]
    doms_e = [NATIVE.get(d, d) for d in doms]
    sets = {"long": (rows_for(doms, 100, N_TRAIN, lambda i: 1 + i % 3), rows_for(doms, 200, N_ID, lambda i: 1 + i % 3),
                     rows_for(doms, 300, N_OOD, lambda i: 4 + i % 2)),
            "native": (rows_for(doms_e, 100, N_TRAIN, lambda i: 1 + i % 3), rows_for(doms_e, 200, N_ID, lambda i: 1 + i % 3),
                       rows_for(doms_e, 300, N_OOD, lambda i: 4 + i % 2))}
    train, ev_id, ev_ood = sets["long"]
    print(f"problems: train {len(train):,} · held-out ID {len(ev_id)} · OOD {len(ev_ood)} ({time.time() - t0:.0f}s)", flush=True)
    res = {"domains": doms, "domains_arm_E": doms_e, "fit": fit, "tokens_budget": TOKENS, "ctx": CTX, "batch": BATCH,
           "tokenizer": TOKF, "smoke": SMOKE, "arms": {}}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    for arm in ("A", "B", "C", "D", "E"):
        R = random.Random(5)
        ids = []
        tr_rows, id_rows, ood_rows = sets["native"] if arm == "E" else sets["long"]
        for r in tr_rows:
            t, _ = text(r, "B" if arm == "E" else arm, R)
            e = tok.encode(t).ids[: CTX - 1]
            ids.extend(e + [eos])
        data = torch.tensor(ids, dtype=torch.long)
        res["arms"][arm] = run_arm(arm, data, tok, eos, id_rows, ood_rows)
        json.dump(res, open(OUT, "w"), indent=1)
    acc = {a: res["arms"][a]["acc_id"] for a in res["arms"]}
    res["verdict"] = {"B_minus_A": (acc["B"] - acc["A"]) * 100, "B_minus_C": (acc["B"] - acc["C"]) * 100,
                      "B_minus_D": (acc["B"] - acc["D"]) * 100,
                      "PASS": acc["B"] >= acc["A"] + 0.10 and acc["B"] >= acc["C"] + 0.10 and acc["B"] >= acc["D"] + 0.05,
                      "KILL": acc["B"] <= acc["A"] + 0.02,
                      "E_minus_B": (acc["E"] - acc["B"]) * 100, "E_no_worse": acc["E"] >= acc["B"] - 0.02,
                      "E_helps": acc["E"] >= acc["B"] + 0.05}
    json.dump(res, open(OUT, "w"), indent=1)
    print("RG-1 verdict", res["verdict"], flush=True)


def run_arm(arm, data, tok, eos, ev_id, ev_ood):
    torch.manual_seed(0)
    model = cal3.LM("RESIDUE").to(cal3.DEV)
    saved = os.path.join(os.path.dirname(OUT), f"rg1.arm{arm}.pt")
    if os.path.exists(saved):                                    # resume: the trained arm is on disk (same data, same seed)
        model.load_state_dict(torch.load(saved, map_location=cal3.DEV))
        eq = equivalence_test(model, tok, eos, ev_id)
        print(f"[{arm}] resumed from {saved}; cached-decode check {eq}", flush=True)
        r = {"resumed": True, "data_tokens": len(data), "decode_check": eq,
             "acc_id": evaluate(model, tok, eos, ev_id), "acc_ood": evaluate(model, tok, eos, ev_ood)}
        print(f"[{arm}] held-out ID {r['acc_id']:.3f} · OOD {r['acc_ood']:.3f} (resumed)", flush=True)
        return r
    opt = torch.optim.AdamW(model.parameters(), lr=1.5e-3, betas=(0.9, 0.95), weight_decay=0.1)
    g = torch.Generator().manual_seed(7)
    seen = step = 0; t0 = time.time()
    while seen < TOKENS:
        frac = seen / TOKENS
        for gr in opt.param_groups:
            gr["lr"] = 1.5e-3 * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * frac))) * min(1.0, (step + 1) / 100)
        x, y = cal3.corpus_batch(g, data, CTX, BATCH)
        loss = F.cross_entropy(model(x.to(cal3.DEV)).reshape(-1, cal3.V), y.to(cal3.DEV).reshape(-1))
        opt.zero_grad(set_to_none=True); loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
        step += 1; seen += BATCH * CTX
        if step % (20 if SMOKE else 500) == 0:
            print(f"  [{arm}] step {step} loss {loss.item():.3f} | {seen / 1e6:.2f}M tok | {seen / (time.time() - t0):,.0f} tok/s",
                  flush=True)
    torch.save(model.state_dict(), saved)                        # save BEFORE evaluating (a stop during eval loses nothing)
    eq = equivalence_test(model, tok, eos, ev_id)
    t_ev = time.time()
    r = {"steps": step, "tokens": seen, "train_seconds": time.time() - t0, "data_tokens": len(data), "decode_check": eq,
         "acc_id": evaluate(model, tok, eos, ev_id), "acc_ood": evaluate(model, tok, eos, ev_ood)}
    r["eval_seconds"] = time.time() - t_ev
    print(f"[{arm}] decode check {eq} · eval {r['eval_seconds']:.0f}s")
    print(f"[{arm}] held-out ID {r['acc_id']:.3f} · OOD {r['acc_ood']:.3f} ({r['train_seconds']:.0f}s train)", flush=True)
    return r


_ROPE = {}


@torch.no_grad()
def lm_step(model, ids, cache, pos0):
    """Incremental forward of cal3.LM (RESIDUE clock) with a PREALLOCATED per-layer K/V cache (fix 2026-10-04: torch.cat grew the
    cache every step — quadratic) and a position table computed once. ids: [1, n] new tokens at positions pos0 … pos0+n-1.
    Same maths as model(full_sequence)[:, pos0:] — checked by equivalence_test()."""
    x = model.emb(ids)
    n = ids.shape[1]
    if model.kind not in _ROPE:
        _ROPE[model.kind] = cal3.rope_angles(model.kind, CTX)
    cos, sin = _ROPE[model.kind]
    cs = (cos[pos0:pos0 + n], sin[pos0:pos0 + n])
    if "_w" not in cache:                                        # quantise each ternary layer ONCE per sequence (weights are fixed
        cache["_w"] = {}                                         # while decoding) — same expression as BitLinear.forward
        for mod in model.modules():
            if isinstance(mod, BitLinear):
                tq, sc = ternary_weight(mod.weight)
                cache["_w"][id(mod)] = mod.weight + (tq * sc - mod.weight)
    W = cache["_w"]

    def bl(mod, h):                                              # BitLinear forward with the cached ternary weight
        h = mod.norm(h)
        gq = mod.qmax / h.abs().amax(-1, keepdim=True).clamp(min=1e-5)
        hq = h + ((h * gq).round().clamp(-mod.qmax - 1, mod.qmax) / gq - h)
        return F.linear(hq, W[id(mod)].to(hq.dtype), None if mod.bias is None else mod.bias.to(hq.dtype))

    for li, blk in enumerate(model.blocks):
        b, t, _ = x.shape
        q, k, v = bl(blk.qkv, blk.n1(x)).view(b, t, 3, cal3.H, cal3.DH).permute(2, 0, 3, 1, 4)
        q, k = cal3.rotate(q, *cs), cal3.rotate(k, *cs)
        if li not in cache:
            cache[li] = (torch.empty(b, cal3.H, CTX, cal3.DH, dtype=k.dtype), torch.empty(b, cal3.H, CTX, cal3.DH, dtype=v.dtype))
        K, V = cache[li]
        K[:, :, pos0:pos0 + n] = k; V[:, :, pos0:pos0 + n] = v
        y = F.scaled_dot_product_attention(q, K[:, :, :pos0 + n], V[:, :, :pos0 + n],
                                           is_causal=(pos0 == 0 and n > 1)).transpose(1, 2).reshape(b, t, cal3.D)
        x = x + bl(blk.o, y)
        x = x + bl(blk.down, F.relu(bl(blk.up, blk.n2(x))) ** 2)
        if hasattr(model, "post_block"):                         # adapters (FWD-1 dials) — same maths as their forward hooks
            x = model.post_block(li, x)
    return model.nf(x) @ model.emb.weight.T


@torch.no_grad()
def greedy(model, prompt, eos, nl, tok, cached=True):
    """One sequence, no padding (amendment 2026-10-03 23:20Z: the batched left-pad decode let eos pads into the context)."""
    seq = list(prompt)
    if cached:
        cache = {}
        logits = lm_step(model, torch.tensor([seq], device=cal3.DEV), cache, 0)
    while len(seq) < CTX:
        if not cached:
            logits = model(torch.tensor([seq], device=cal3.DEV))
        t = int(logits[0, -1].argmax())
        if t == eos:
            break
        seq.append(t)
        if t in nl and "A: " in tok.decode(seq[len(prompt):]):
            break
        if cached:
            logits = lm_step(model, torch.tensor([[t]], device=cal3.DEV), cache, len(seq) - 1)
    return seq[len(prompt):]


_EV = {}


def _ev_init(model, eos, tokf):
    torch.set_num_threads(1)                                     # one thread per worker: the decode is a chain of tiny ops
    from tokenizers import Tokenizer
    _EV.update(model=model, eos=eos, tok=Tokenizer.from_file(tokf))
    _EV["nl"] = set(_EV["tok"].encode("\n").ids)


def _ev_one(prompt):
    out = greedy(_EV["model"], prompt, _EV["eos"], _EV["nl"], _EV["tok"])
    return out


def decode_many(model, eos, prompts, workers=None):
    """Greedy-decode many independent prompts in parallel PROCESSES (fork shares the weights copy-on-write).
    Same per-sequence decode as greedy(); only the scheduling changes (fix 2026-10-04: the serial decode left 1–2 cores working)."""
    import multiprocessing as mp
    workers = workers or int(os.environ.get("EVAL_WORKERS", str(max(1, (os.cpu_count() or 2) // 2))))
    model.eval()
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    ctx = mp.get_context("fork")
    with ctx.Pool(workers, initializer=_ev_init, initargs=(model, eos, TOKF)) as pool:
        outs = pool.map(_ev_one, prompts, chunksize=max(1, len(prompts) // (workers * 8)))
    model.train()
    return outs


@torch.no_grad()
def evaluate(model, tok, eos, rows):
    prompts = [tok.encode(f"Q: {r['question']}\n").ids[: CTX - 8] for r in rows]
    hit = 0
    for r, out_ids in zip(rows, decode_many(model, eos, prompts)):
        out = tok.decode(out_ids)
        ans = json.dumps(r["answer"], ensure_ascii=False) if not isinstance(r["answer"], str) else r["answer"]
        got = out.split("A: ", 1)[1].split("\n")[0].strip() if "A: " in out else None   # FIRST answer line
        hit += got == ans
    return hit / max(1, len(rows))


@torch.no_grad()
def equivalence_test(model, tok, eos, rows, n=12):
    """Cached decode must equal full-recompute decode, token for token, and logits must agree."""
    model.eval(); nl = set(tok.encode("\n").ids)
    same = 0; maxdiff = 0.0
    for r in rows[:n]:
        prompt = tok.encode(f"Q: {r['question']}\n").ids[: CTX - 8]
        a, b = greedy(model, prompt, eos, nl, tok, True), greedy(model, prompt, eos, nl, tok, False)
        same += a == b
        seq = prompt + a
        full = model(torch.tensor([seq], device=cal3.DEV))[0]
        cache = {}; inc = [lm_step(model, torch.tensor([seq[:len(prompt)]], device=cal3.DEV), cache, 0)[0]]
        for k in range(len(prompt), len(seq)):
            inc.append(lm_step(model, torch.tensor([[seq[k]]], device=cal3.DEV), cache, k)[0])
        maxdiff = max(maxdiff, float((torch.cat(inc, 0) - full).abs().max()))
    model.train()
    return {"greedy_identical": f"{same}/{min(n, len(rows))}", "max_logit_diff": maxdiff}


if __name__ == "__main__":
    main()

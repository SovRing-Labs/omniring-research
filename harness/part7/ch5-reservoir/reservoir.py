"""reservoir probe S1/S2: fixed random reservoir over token sequences, ridge readout to nomic vectors, scored on e6's held-out split and the pre-registered hub-3 gate.
Usage: reservoir.py KIND(ternary|float) N RHO FEATS(res|res+bag|bag) OUT.json [K=8] [seed=1]
Reservoir: x_t = tanh(rho * W x_{t-1} + I[token_t]);  W sparse, K nonzeros/row, ternary {-1,+1} (scaled by a global scalar) or Gaussian (float control);
I = PCA256 token table (embed-core e1) projected by a fixed ternary Win. No gradient anywhere; only the ridge readout is fit (closed form).
Features: mean state + last state over the valid tokens (+ SIF-free plain bag of PCA256 rows for 'bag'). Fit rows/targets = embed-core e6 fitset.npz (hub-3 targets + 20% held out)."""
import json, random, re, sys, time
from pathlib import Path
import numpy as np, scipy.sparse as sp
kind, N, rho, feats, out = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5]
K = int(sys.argv[6]) if len(sys.argv) > 6 else 8; seed = int(sys.argv[7]) if len(sys.argv) > 7 else 1
HERE = Path(__file__).resolve().parent; EC = HERE.parents[1] / "embed-core"
rng = np.random.default_rng(seed)
z = np.load(EC / "e6/fitset.npz"); Y = z["Y"].astype(np.float32); Y /= np.linalg.norm(Y, axis=1, keepdims=True) + 1e-12
fit = z["fit"]; corpus = z["corpus"]; tok = np.load(HERE / "tok.npy"); n, L = tok.shape; assert n == len(Y)
T = np.load(EC / "e1/token_table_f32.npy"); pc = np.load(EC / "e1/pca256.npy"); mean, P = pc[0], pc[1:].T; TP = ((T - mean) @ P).astype(np.float32); TP /= TP.std()
t0 = time.time()
# ---- the fixed core
rows = np.repeat(np.arange(N), K); cols = rng.integers(0, N, N * K)
vals = rng.choice([-1.0, 1.0], N * K) if kind == "ternary" else rng.standard_normal(N * K)
W = sp.csr_matrix((vals.astype(np.float32), (rows, cols)), shape=(N, N))
lam_max = float(np.abs(np.linalg.eigvals(W.toarray())).max()) if N <= 1536 else float(sp.linalg.eigs(W, k=1, return_eigenvectors=False)[0].real)
Wt = (W.T * (rho / lam_max)).astype(np.float32).tocsr()                     # spectral radius = rho (one global scalar)
Win = (rng.random((N, 256)) < 0.1) * rng.choice([-1.0, 1.0], (N, 256)); I = (TP @ Win.T.astype(np.float32)).astype(np.float32); I /= I.std()
zero_row = np.zeros((1, N), np.float32)
def run(idx, bs=4096):
    F = []
    for s in range(0, len(idx), bs):
        tk = tok[idx[s:s + bs]]; m = tk >= 0; X = np.zeros((len(tk), N), np.float32); acc = np.zeros_like(X); last = np.zeros_like(X)
        for t in range(L):
            if not m[:, t].any(): break
            u = np.where(m[:, t:t + 1], I[np.clip(tk[:, t], 0, None)], 0)
            Xn = np.tanh((X @ Wt) + u)
            X = np.where(m[:, t:t + 1], Xn, X); acc += np.where(m[:, t:t + 1], X, 0)
        cnt = np.maximum(m.sum(1, keepdims=True), 1); F.append(np.concatenate([acc / cnt, X], 1))
    return np.concatenate(F)
def bag(idx):
    tk = tok[idx]; m = tk >= 0; B = np.zeros((len(tk), 256), np.float32)
    for t in range(L): B += np.where(m[:, t:t + 1], TP[np.clip(tk[:, t], 0, None)], 0)
    return B / np.maximum(m.sum(1, keepdims=True), 1)
def features(idx):
    parts = []
    if "res" in feats: parts.append(run(idx))
    if "bag" in feats: parts.append(bag(idx))
    F = np.concatenate(parts, 1); return np.concatenate([F, np.ones((len(F), 1), np.float32)], 1)
allidx = np.arange(n); F = features(allidx); t_feat = time.time() - t0
fi = np.nonzero(fit)[0]; ho = np.nonzero(~fit)[0]; rs = np.random.default_rng(3).permutation(fi); va, tr = rs[:len(rs) // 10], rs[len(rs) // 10:]
mu, sd = F[tr].mean(0), F[tr].std(0) + 1e-6; Fz = (F - mu) / sd; Fz[:, -1] = 1
def ridge(idx, lam):
    A = Fz[idx]; G = A.T @ A; G[np.diag_indices_from(G)] += lam * len(idx); return np.linalg.solve(G.astype(np.float64), (A.T @ Y[idx]).astype(np.float64)).astype(np.float32)
def cosm(Wo, idx):
    P_ = Fz[idx] @ Wo; P_ /= np.linalg.norm(P_, axis=1, keepdims=True) + 1e-12; return (P_ * Y[idx]).sum(1)
best = max(((cosm(ridge(tr, l), va).mean(), l) for l in (1e-4, 1e-3, 1e-2, 1e-1, 1.0)))
lam = best[1]; Wo = ridge(fi, lam)
res = {"kind": kind, "N": N, "rho": rho, "feats": feats, "K": K, "seed": seed, "L": L, "lambda": lam, "val_cos": round(float(best[0]), 4),
       "fit_cos": round(float(cosm(Wo, fi).mean()), 4), "feat_dim": int(F.shape[1]), "feat_secs": round(t_feat)}
c = cosm(Wo, ho); res["heldout_cos"] = {"vault": round(float(c[corpus[ho] == 0].mean()), 4), "sessions": round(float(c[corpus[ho] == 1].mean()), 4)}
# ---- hub-3 gate (same 200 queries / FTS5 / RRF as e4-e6); documents embedded by the fitted core+readout, queries likewise (heading text)
sys.path.insert(0, "<workspace>/projects/omnid"); import shardd
from tokenizers import Tokenizer
tk_ = Tokenizer.from_file("<models>/nomic-embed-text-v1.5/tokenizer.json"); SPECIAL = {tk_.token_to_id(x) for x in ("[CLS]", "[SEP]", "[PAD]")}
IX = Path("<workspace>/vault-indexer/index"); data = json.load(open(IX / "docstore.json"))["docstore/data"]; ids = json.load(open(IX / "nomic_local" / "ids.json"))
cand = []
for k, i in enumerate(ids):
    m_ = re.search(r"^#+\s+(.{8,120})$", data[i]["__data__"]["text"], re.M)
    if m_: cand.append((k, m_.group(1).strip()))
random.Random(0).shuffle(cand); cand = cand[:200]
srv = shardd.Server(); st = srv.st; doc_ids = list(st.vault_ids); nv = len(doc_ids); assert nv == int((corpus == 0).sum())
D = Fz[:nv] @ Wo; D /= np.linalg.norm(D, axis=1, keepdims=True) + 1e-12
qt = np.full((len(cand), L), -1, np.int32)
for r, e in enumerate(tk_.encode_batch([q for _, q in cand], add_special_tokens=False)):
    t = [i for i in e.ids if i not in SPECIAL][:L]; qt[r, :len(t)] = t
tok_save = tok; tok = qt; Fq = features(np.arange(len(cand))); tok = tok_save                      # same fixed core, same readout, query tokens
Q = ((Fq - mu) / sd); Q[:, -1] = 1; Q = Q @ Wo; Q /= np.linalg.norm(Q, axis=1, keepdims=True) + 1e-12
arms = {"fts_only": 0, "core_only": 0, "hybrid_fts_core": 0}
for r, (k, q) in enumerate(cand):
    target = ids[k]; fts = st.fts_vault(q, 50)
    s = D @ Q[r]; top = np.argsort(-s)[:50]; cl = [(f"vault:{doc_ids[i]}", {"id": doc_ids[i]}) for i in top]
    arms["fts_only"] += target in [h[1]["id"] for h in fts[:5]]; arms["core_only"] += target in [h[1]["id"] for h in cl[:5]]
    arms["hybrid_fts_core"] += target in [p["id"] for p in shardd.rrf([("vault_fts", fts), ("vault_vec", cl)], 5)]
res["hub3"] = {a: round(v / len(cand), 3) for a, v in arms.items()}; res["secs_total"] = round(time.time() - t0)
res["bar"] = "hybrid_fts_core >= 0.775 (FTS 0.735; E6 hybrid 0.600, core-only 0.425)"; res["PASS"] = res["hub3"]["hybrid_fts_core"] >= 0.775
json.dump(res, open(out, "w"), indent=1); print(json.dumps(res))

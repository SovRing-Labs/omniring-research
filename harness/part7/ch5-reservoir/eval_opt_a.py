"""Option A probe: RRF weight calibration & shortlist tuning for peak ternary reservoir (N=1024, K=16, rho=0.95)."""
import json, random, re, sys, time
from pathlib import Path
import numpy as np, scipy.sparse as sp

HERE = Path(__file__).resolve().parent
EC = HERE.parents[1] / "embed-core"
sys.path.insert(0, "<workspace>/projects/omnid")
import shardd
from tokenizers import Tokenizer

kind = "ternary"; N = 1024; rho = 0.95; feats = "res+bag"; K = 16; seed = 1

rng = np.random.default_rng(seed)
z = np.load(EC / "e6/fitset.npz")
Y = z["Y"].astype(np.float32); Y /= np.linalg.norm(Y, axis=1, keepdims=True) + 1e-12
fit = z["fit"]; corpus = z["corpus"]; tok = np.load(HERE / "tok.npy")
n, L = tok.shape; assert n == len(Y)
T = np.load(EC / "e1/token_table_f32.npy")
pc = np.load(EC / "e1/pca256.npy")
mean, P = pc[0], pc[1:].T
TP = ((T - mean) @ P).astype(np.float32); TP /= TP.std()

t0 = time.time()
rows = np.repeat(np.arange(N), K); cols = rng.integers(0, N, N * K)
vals = rng.choice([-1.0, 1.0], N * K)
W = sp.csr_matrix((vals.astype(np.float32), (rows, cols)), shape=(N, N))
lam_max = float(np.abs(np.linalg.eigvals(W.toarray())).max())
Wt = (W.T * (rho / lam_max)).astype(np.float32).tocsr()
Win = (rng.random((N, 256)) < 0.1) * rng.choice([-1.0, 1.0], (N, 256))
I = (TP @ Win.T.astype(np.float32)).astype(np.float32); I /= I.std()

def run(idx, bs=4096):
    F = []
    for s in range(0, len(idx), bs):
        tk = tok[idx[s:s + bs]]; m = tk >= 0; X = np.zeros((len(tk), N), np.float32); acc = np.zeros_like(X); last = np.zeros_like(X)
        for t in range(L):
            if not m[:, t].any(): break
            u = np.where(m[:, t:t + 1], I[np.clip(tk[:, t], 0, None)], 0)
            Xn = np.tanh((X @ Wt) + u)
            valid = m[:, t:t + 1]
            acc += np.where(valid, Xn, 0)
            last = np.where(valid, Xn, last)
            X = np.where(valid, Xn, X)
        denom = np.maximum(m.sum(axis=1, keepdims=True), 1)
        mean_x = acc / denom
        f = [mean_x, last]
        bg = np.zeros((len(tk), 256), np.float32)
        for t in range(L):
            bg += np.where(m[:, t:t + 1], TP[np.clip(tk[:, t], 0, None)], 0)
        bg /= denom
        f.append(bg)
        F.append(np.concatenate(f, axis=1))
    return np.concatenate(F, axis=0)

allidx = np.arange(n)
Fall = run(allidx)
f_fit = Fall[fit]; y_fit = Y[fit]
mu = f_fit.mean(axis=0, keepdims=True)
sd = f_fit.std(axis=0, keepdims=True); sd[sd < 1e-6] = 1.0
Fz = (Fall - mu) / sd
Fz = np.concatenate([Fz, np.ones((len(Fz), 1), np.float32)], axis=1)

Xfit = Fz[fit]
d = Xfit.shape[1]
lam = 0.01
Wo = np.linalg.solve(Xfit.T @ Xfit + (lam * len(Xfit)) * np.eye(d, dtype=np.float32), Xfit.T @ y_fit)

tk_ = Tokenizer.from_file("<models>/nomic-embed-text-v1.5/tokenizer.json")
SPECIAL = {tk_.token_to_id(x) for x in ("[CLS]", "[SEP]", "[PAD]")}
IX = Path("<workspace>/vault-indexer/index")
data = json.load(open(IX / "docstore.json"))["docstore/data"]
ids = json.load(open(IX / "nomic_local" / "ids.json"))
cand = []
for k, i in enumerate(ids):
    m_ = re.search(r"^#+\s+(.{8,120})$", data[i]["__data__"]["text"], re.M)
    if m_: cand.append((k, m_.group(1).strip()))
random.Random(0).shuffle(cand); cand = cand[:200]
srv = shardd.Server(); st = srv.st; doc_ids = list(st.vault_ids); nv = len(doc_ids)

D = Fz[:nv] @ Wo
D /= np.linalg.norm(D, axis=1, keepdims=True) + 1e-12

qt = np.full((len(cand), L), -1, np.int32)
for r, e in enumerate(tk_.encode_batch([q for _, q in cand], add_special_tokens=False)):
    t = [i for i in e.ids if i not in SPECIAL][:L]
    qt[r, :len(t)] = t

tok_save = tok; tok = qt; Fq = run(np.arange(len(cand))); tok = tok_save
Q = (Fq - mu) / sd; Q = np.concatenate([Q, np.ones((len(Q), 1), np.float32)], axis=1)
Q = Q @ Wo
Q /= np.linalg.norm(Q, axis=1, keepdims=True) + 1e-12

# Pre-fetch FTS and Core hits for all 200 queries
print("Prefetching candidate rankings...")
cached = []
fts_only_hits = 0
core_only_hits = 0
for r, (k, q) in enumerate(cand):
    target = ids[k]
    fts = st.fts_vault(q, 100)
    s = D @ Q[r]
    top = np.argsort(-s)[:100]
    cl = [(f"vault:{doc_ids[i]}", {"id": doc_ids[i]}) for i in top]
    fts_only_hits += (target in [h[1]["id"] for h in fts[:5]])
    core_only_hits += (target in [h[1]["id"] for h in cl[:5]])
    cached.append((target, fts, cl))

print(f"Base: FTS recall@5: {fts_only_hits / len(cand):.3f}, Core recall@5: {core_only_hits / len(cand):.3f}")

# Grid search weights and RRF parameters
best_score = 0.0
best_params = None

results = []
for rrf_k in [20, 30, 40, 60]:
    for w_fts in [0.8, 1.0, 1.2, 1.4, 1.6]:
        for w_core in [0.4, 0.6, 0.8, 1.0, 1.2]:
            hits = 0
            for target, fts, cl in cached:
                score = {}
                for rank, (key, p) in enumerate(fts[:50]):
                    doc_id = p["id"]
                    score[doc_id] = score.get(doc_id, 0.0) + w_fts / (rrf_k + rank + 1)
                for rank, (key, p) in enumerate(cl[:50]):
                    doc_id = p["id"]
                    score[doc_id] = score.get(doc_id, 0.0) + w_core / (rrf_k + rank + 1)
                top5 = sorted(score, key=score.get, reverse=True)[:5]
                hits += (target in top5)
            rec = hits / len(cand)
            results.append({"rrf_k": rrf_k, "w_fts": w_fts, "w_core": w_core, "recall": rec})
            if rec > best_score:
                best_score = rec
                best_params = (rrf_k, w_fts, w_core)

print(f"Sweep completed. Best score: {best_score:.4f} with params: {best_params}")
out_path = HERE / "results" / "option_a_sweep.json"
with open(out_path, "w") as f:
    json.dump({"best_recall": best_score, "best_params": best_params, "all": results}, f, indent=1)
print(f"Results written to {out_path}")

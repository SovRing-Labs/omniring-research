"""reservoir probe S1 prep: token-id sequences (first L tokens, specials dropped) for the SAME 19,664 docs, SAME order as embed-core e6/fitset.npz
(vault docs then session chunks), so e6's fit mask / nomic targets Y apply unchanged. Writes tok.npy (int32 [n, L], -1 pad). Copied loading logic from e6/prep.py."""
import glob, json, re, sqlite3, sys
from pathlib import Path
import numpy as np
from tokenizers import Tokenizer
L = int(sys.argv[1]) if len(sys.argv) > 1 else 96
sys.path.insert(0, "<workspace>/projects/omnid"); import shardd
tok = Tokenizer.from_file("<models>/nomic-embed-text-v1.5/tokenizer.json")
SPECIAL = {tok.token_to_id(x) for x in ("[CLS]", "[SEP]", "[PAD]")}
IX = Path("<workspace>/vault-indexer/index"); data = json.load(open(IX / "docstore.json"))["docstore/data"]
st = shardd.Server().st; vid = list(st.vault_ids); vtext = [data[i]["__data__"]["text"] if i in data else st.vault_text.get(i, "") for i in vid]
V = Path("<workspace>/transcript-chewer/vectors")
rid = [r for f in ("rowids.json", "rowids2.json") if (V / f).exists() for part in json.load(open(V / f)) for r in part]
db = sqlite3.connect("<workspace>/data/shards/transcripts.db"); txt = dict(db.execute("select rowid, text from chunks").fetchall()); stext = [txt[r] for r in rid]
out = np.full((len(vtext) + len(stext), L), -1, np.int32)
for r, e in enumerate(tok.encode_batch(vtext + stext, add_special_tokens=False)):
    t = [i for i in e.ids if i not in SPECIAL][:L]; out[r, :len(t)] = t
np.save("tok.npy", out); np.save("vault_ids_order.npy", np.array(vid)); print(out.shape, (out >= 0).sum(1).mean())

"""ramkit common — paths, the reason-gen loader, build readers, hashing (RAM-KIT-0, J 10-08). stdlib + numpy only; every path resolves
from $HOME so the laptop (<home>) and a RunPod pod (/root) run the same files."""
import hashlib, importlib.machinery, json, os, sys
import numpy as np

HOME = os.path.expanduser("~")
AI = os.environ.get("AI_STACK", os.path.join(HOME, "ai-stack"))
TRIAL = os.path.join(AI, "projects", "thead-trial")
HERE = os.path.dirname(os.path.abspath(__file__))
TOKENIZER = os.path.expanduser(os.environ.get("RAMKIT_TOKENIZER", "~/gpurun-out-1003/tokenizer-glyph-fix/tokenizer.json"))
# the 26 faculties (VOCAB "the 26" = the literal first 26 DOMAINS of bin/reason-gen; school_graph.GENS has the same list)
GENS26 = ["arith.mul", "arith.mrc_compare", "logic.chain", "graph.path", "sat.dpll", "mind.revise", "struct.pushdown", "units.dimension",
          "calendar.crt", "code.debug", "science.bioreactor", "mind.tom", "search.astar", "causal.dag", "arith.mul_rns", "arith.mrc_plate",
          "sat.trit", "graph.group_walk", "graph.group", "calendar.ring_euclid", "calendar.clock", "science.factorial", "search.wave",
          "mind.tom_mask", "numth.prime_trial", "numth.prime"]
_RG = None


def rg():
    """bin/reason-gen as a module (it has no .py suffix); loaded once"""
    global _RG
    if _RG is None:
        _RG = importlib.machinery.SourceFileLoader("reason_gen", os.path.join(AI, "bin", "reason-gen")).load_module()
    return _RG


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def problem_key(domain, problem):
    """64-bit key of a canonical problem: sha256(domain | canonical JSON)[:8] as an unsigned int"""
    return int.from_bytes(hashlib.sha256((domain + "|" + canon(problem)).encode()).digest()[:8], "little")


def sha_file(p, bs=1 << 20):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(bs), b""): h.update(b)
    return h.hexdigest()


def build_rows(build):
    """yield (phase k, rows array [n,12], manifest) for a compiled build dir (rows_k.u32 sidecar)"""
    man = json.load(open(os.path.join(build, "manifest.json")))
    nf = len(man["rows_sidecar"]["fields"])
    for k in range(len(man["phases"])):
        p = os.path.join(build, f"rows_{k}.u32")
        if os.path.exists(p):
            yield k, np.fromfile(p, dtype=np.uint32).reshape(-1, nf), man


def build_is_generator(man):
    """a middle / high-school build (curriculum.py): port domains are the reason-gen generators, so gen_row/gen_seed/gen_level/base_domain
    regenerate the exact problem. Tier-1 builds (tier1_school.py) store a lesson book and draw env rows from R.randrange → not regenerable."""
    return "tier1" not in man and man.get("port", {}).get("domains", [])[:1] == ["arith.mul"]


def regen_problem(domain, i, seed, level, native=False):
    """the problem only (generator call, no solver): the same RNG reason-gen make() uses"""
    RG = rg()
    d = {v: k for k, v in RG.NATIVE_OF.items()}.get(domain, domain) if native else domain
    gen = RG.fns_of(d)[0]
    p, q = gen(RG.rng_for(d, i, seed), level)
    return d, p, q


def json_out(obj, path=None):
    s = json.dumps(obj, indent=1, sort_keys=True)
    if path:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        open(path + ".tmp", "w").write(s + "\n"); os.replace(path + ".tmp", path)
    return s


def rss_mb():
    try:
        for line in open("/proc/self/status"):
            if line.startswith("VmHWM:"): return round(int(line.split()[1]) / 1024, 1)
    except OSError:
        pass
    return None

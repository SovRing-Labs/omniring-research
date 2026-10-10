#!/usr/bin/env python3
"""Chapter 6 derived checks.  python3 -I checks.py <cmd> <package-root> <out-file> [args]
 speclines <root> <out>        : module doc -> 'Spec:' line (first 140 chars), 17 module docs
 leakwords <root> <out>        : words shared between the 32 wall-passed specification rows and the identifiers of the reader's source file
 ngram <root> <out> <chapter>  : shared n-grams (counts only, no text) between the five outside texts and the chapter / concept notes"""
import glob, json, os, re, sys
cmd, root, out = sys.argv[1:4]
R = lambda *p: os.path.join(root, *p)
lines = []
if cmd == "speclines":
    lines.append("module\tspec_line_first_140_chars")
    n = 0
    for f in sorted(glob.glob(R("lineage/projects/omni-spec/docs/*.md"))):
        b = os.path.basename(f)
        if b == "STATUS.md": continue
        sp = [l for l in open(f, encoding="utf-8") if l.startswith("- **Spec:**")]
        lines.append("%s\t%s" % (b[:-3], sp[0][len("- **Spec:**"):].strip()[:140].replace("\t", " ") if sp else "NONE"))
        n += bool(sp)
    lines.append("# module documents with a Spec line: %d of %d" % (n, len(lines) - 1))
elif cmd == "leakwords":
    d = R("lineage/projects/omni-render/results/doctor-interp/s1-s3/specs.layout.wall.jsonl")
    spec = open(d, encoding="utf-8").read()
    src = open(R("code/projects/omni-render/src/layout.rs"), encoding="utf-8").read()
    ident = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", src))
    words = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", spec))
    # the 64-digit source hashes are skipped by the wall too
    words = {w for w in words if not re.fullmatch(r"[0-9a-f]{64}", w)}
    rows = sum(1 for l in spec.splitlines() if l.strip())
    lines.append("spec rows %d; distinct words of 3+ chars in the rows %d; identifiers of 3+ chars in the source file %d" % (rows, len(words), len(ident)))
    lines.append("shared words: " + " ".join(sorted(words & ident)))
elif cmd == "ngram":
    ch = open(sys.argv[4], encoding="utf-8").read()
    def toks(t): return re.findall(r"[a-z0-9']+", t.lower())
    def grams(t, n):
        w = toks(t); return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}
    texts = [("A", "Provenance.txt"), ("B", "prov 2.txt"), ("C", "JIt 50t.txt"), ("D", "AST.txt"), ("E", "Parse.txt")]
    notes = [("concept note 1", R("lineage/<notes>/THEAD/PROVENANCE-CONCEPTS-2026-10-09.md")), ("concept note 2", R("lineage/<notes>/THEAD/JIT-T50-CONCEPTS-2026-10-09.md"))]
    tg = [("this chapter", ch)] + [(n, open(p, encoding="utf-8").read()) for n, p in notes]
    lines.append("text\tn\t" + "\t".join(n for n, _ in tg))
    for lab, fn in texts:
        t = open(R("lineage/research/downloads", fn), encoding="utf-8", errors="replace").read()
        for n in (8, 6):
            g = grams(t, n)
            lines.append("%s\t%d\t%s" % (lab, n, "\t".join(str(len(g & grams(x, n))) for _, x in tg)))
    lines.append("# counts of distinct shared word n-grams (lower-cased words); no text is printed")
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))

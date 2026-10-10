#!/usr/bin/env python3
"""T4.4 — generated-script differential: random programs over the language omni-sh implements (POSIX sh core + the bash
subset), each run by bash (oracle) and omni-sh in fresh temp dirs; compared = stdout bytes + exit status (plan bar >= 90 %
byte-identical). Deterministic per seed. Appends a summary to results/sh-fuzz.jsonl and every difference (script + both
outputs) to results/sh-fuzz-diffs.jsonl.  Usage: sh_fuzz.py [--n 500] [--seed 1] [--oracle bash]
"""
import argparse, json, os, random, signal, subprocess, tempfile, time

OMNI = "<workspace>/projects/omni-spec/posix/target/release/omni-sh"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
WORDS = ["a", "b", "ab", "x y", "", "a*", "c:d", "q"]
VARS = ["x", "y", "z", "n"]


class G:
    def __init__(self, R): self.R, self.depth, self.funcs = R, 0, []

    def word(self):
        R = self.R; k = R.random()
        if k < 0.3: return R.choice(["a", "b", "ab", "zz", "1", "42"])
        if k < 0.5: return '"$' + R.choice(VARS) + '"'
        if k < 0.6: return "$" + R.choice(VARS)
        if k < 0.7: return "'" + R.choice(WORDS) + "'"
        if k < 0.8: return '"${' + R.choice(VARS) + R.choice([":-d", "-d", ":+p", "%b", "#a", "##*b", "%%:*"]) + '}"'
        if k < 0.9: return '"$((' + self.arith() + '))"'
        return '"$(' + self.simple(pipe_ok=False) + ')"'

    def arith(self, d=0):
        R = self.R
        if d > 2 or R.random() < 0.4: return R.choice([str(R.randint(-9, 20)), R.choice(VARS), "${#" + R.choice(VARS) + "}"])
        op = R.choice(["+", "-", "*", "/", "%", "<", "==", "&&", "||"])
        rhs = self.arith(d + 1)
        if op in "/%": rhs = "((" + rhs + ")*0+" + str(R.randint(1, 5)) + ")"     # a divisor that is never 0
        return "(" + self.arith(d + 1) + " " + op + " " + rhs + ")"

    def assign(self):
        R = self.R; v = R.choice(VARS); k = R.random()
        if k < 0.4: return f"{v}={self.word()}"
        if k < 0.7: return f"{v}=$(({self.arith()}))"
        return f'{v}="${{{R.choice(VARS)}}}{R.choice(["", "x", "-"])}"'

    def simple(self, pipe_ok=True):
        R = self.R; k = R.random()
        if k < 0.25: return "printf '%s|' " + " ".join(self.word() for _ in range(R.randint(1, 3)))
        if k < 0.35: return "echo " + " ".join(self.word() for _ in range(R.randint(0, 3)))
        if k < 0.45: return self.assign()
        if k < 0.52 and pipe_ok: return self.word_printf() + " | " + R.choice(["tr a-z A-Z", "wc -c", "sort", "cat", "head -n 1", "tr -d a"])
        if k < 0.58: return "set -- " + " ".join(self.word() for _ in range(R.randint(0, 3))) + '; printf "%s;" "$#" "$@"'
        if k < 0.62: return R.choice(["true", "false", ":"])
        if k < 0.68 and self.funcs: return R.choice(self.funcs) + " " + " ".join(self.word() for _ in range(R.randint(0, 2)))
        if k < 0.74: return f'printf "%s\\n" {self.word()} > f{R.randint(0, 2)}; cat f{R.randint(0, 2)} 2>/dev/null; echo "<$?>"'
        if k < 0.80: return f'{self.word_printf()} | while IFS= read -r l; do printf "<%s>" "$l"; done'
        if k < 0.86: return f'(x={self.word()}; printf "%s" "$x"); printf "[%s]" "$x"'
        if k < 0.92: return "[ " + self.word() + " " + R.choice(["=", "!="]) + " " + self.word() + " ] && echo t || echo f"
        if self.depth == 0:                              # a here-document needs its own lines: top level only
            return f"cat <<EOF\n{R.choice(['v=$x', 'n=$((n+1))', 'plain', 'w=${y:-none}'])}\nEOF"
        return "printf '%s|' " + self.word()

    def word_printf(self): return "printf '%s\\n' " + " ".join(self.word() for _ in range(self.R.randint(1, 3)))

    def stmt(self):
        R = self.R
        if self.depth > 2: return self.simple()
        self.depth += 1
        k = R.random()
        try:
            if k < 0.55: return self.simple()
            if k < 0.65: return f"if {self.cond()}; then {self.body()}; elif {self.cond()}; then {self.body()}; else {self.body()}; fi"
            if k < 0.72: return f"i=0; while [ $i -lt {R.randint(0, 4)} ]; do {self.body()}; i=$((i+1)); done"
            if k < 0.80: return f"for w in {' '.join(self.word() for _ in range(R.randint(0, 3)))}; do printf '<%s>' \"$w\"; {self.body()}; done"
            if k < 0.87:
                pats = R.sample(["a*", "b", "*b", "[ab]*", "''", "x*|y*", "?"], 2)
                return f"case {self.word()} in {pats[0]}) {self.body()};; {pats[1]}) {self.body()};; *) echo other;; esac"
            if k < 0.93 and self.depth == 1:
                # top level only, fresh name, body may call EARLIER functions only: no self- or mutual recursion
                # (a self-calling f0 inside pipelines fork-bombed bash, 2026-10-06)
                name = f"f{len(self.funcs)}"; body = self.body()
                self.funcs.append(name)
                return f'{name}() {{ local v="$1"; printf "%s:" "$#" "$v"; {body}; return {R.randint(0, 3)}; }}'
            return "{ " + self.body() + "; } | " + R.choice(["cat", "wc -l", "tr -d '|'"])
        finally:
            self.depth -= 1

    def cond(self): return self.R.choice(["[ " + self.word() + " = " + self.word() + " ]", "[ -n " + self.word() + " ]", "[[ " + self.word() + " == a* ]]",
                                          "[ $((" + self.arith() + ")) -gt 0 ]", "true", "false"])

    def body(self): return "; ".join(self.stmt() for _ in range(self.R.randint(1, 3)))

    def program(self):
        lines = [f"x={self.word()}; y={self.word()}; z=ab; n=3"]
        lines += [self.stmt() for _ in range(self.R.randint(3, 8))]
        lines.append(f"exit {self.R.randint(0, 3)}")
        return "\n".join(lines) + "\n"


MAX_PROCS = 64        # per test case; RLIMIT_NPROC is per USER (would starve the whole desktop), so count the session


def session_procs(sid):
    n = 0
    for d in os.listdir("/proc"):
        if d.isdigit():
            try:
                st = open(f"/proc/{d}/stat").read()
                if int(st[st.rindex(")") + 2:].split()[3]) == sid: n += 1      # field 6 = session id
            except (OSError, ValueError, IndexError): pass
    return n


def run(shell, script):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "s.sh"); open(p, "w").write(script)
        # own process group, killed on every exit: a timeout used to kill only the top shell and leave its loops /
        # subshells orphaned (1,061 bash -> OOM, reboot 2026-10-06 09:28)
        pr = subprocess.Popen(shell + [p], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=d,
                              env=dict(os.environ, LC_ALL="C"), start_new_session=True)
        try:
            deadline = time.time() + 10
            while True:
                try:
                    out, _ = pr.communicate(timeout=0.1)
                    return pr.returncode, out
                except subprocess.TimeoutExpired:
                    if time.time() > deadline: return "timeout", b""
                    if session_procs(pr.pid) > MAX_PROCS: return "proc-cap", b""   # runaway forking: stop it here

        finally:
            try: os.killpg(pr.pid, signal.SIGKILL)
            except ProcessLookupError: pass
            pr.wait()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=500); ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--oracle", default="bash --posix")  # dialect core = POSIX (J 10-06): bash --posix exits on expansion errors
    a = ap.parse_args()
    R = random.Random(a.seed); ok = 0; diffs = []
    t0 = time.time()
    for k in range(a.n):
        g = G(R); s = g.program()
        o = run(a.oracle.split(), s); m = run([OMNI], s)
        if o == m: ok += 1
        else: diffs.append({"seed": a.seed, "k": k, "script": s, "oracle": [o[0], o[1].decode("latin-1")], "omni": [m[0], m[1].decode("latin-1")]})
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "sh-fuzz-diffs.jsonl"), "a") as f:
        for d in diffs: f.write(json.dumps(d) + "\n")
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "seed": a.seed, "n": a.n, "identical": ok, "rate": round(ok / a.n, 4),
           "oracle": a.oracle, "bar": 0.9, "secs": round(time.time() - t0, 1),
           "omni_commit": subprocess.run(["git", "-C", "<workspace>/projects/omni-spec", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()}
    with open(os.path.join(OUT, "sh-fuzz.jsonl"), "a") as f: f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec))


if __name__ == "__main__":
    main()

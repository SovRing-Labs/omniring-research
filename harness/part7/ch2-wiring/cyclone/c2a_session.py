#!/usr/bin/env python3
"""CYCLONE-ARRAY C2a gate — the resident session (`omni-gpu session`): buffers stay on the device, the step is a chain of passes recorded
ONCE and re-submitted, nothing crosses to the host between steps. Program: buffer 0 = N random u32, buffer 1 = zero; P pass pairs
copy_add(0 → 1, +1), copy_add(1 → 0, +1) per step; S steps. Oracle (host): buffer 0 = in + 2·P·S, buffer 1 = in + 2·P·S − 1 (mod 2^32),
byte-exact. Also measures the old one-shot way (`omni-gpu run`: create buffers + pipeline, upload, dispatch, read back, tear down) for one
pass, so the per-pass cost of both is on record.
Run OUTSIDE the kernel-bash Landlock domain (systemd-run / tw unit) so the Intel device is visible.
  c2a_session.py [--devices llvmpipe,Intel] [--out DIR]   → DIR/session.json; exit 1 on any mismatch or error"""
import hashlib, json, os, random, struct, subprocess, sys, tempfile
P = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BIN = f"{P}/target/release/omni-gpu"; SPV = f"{P}/kernels/copy_add.spv"

def main():
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    devices = opt("--devices", "llvmpipe,Intel").split(","); out = opt("--out", f"{P}/results/cyclone/c2a"); os.makedirs(out, exist_ok=True)
    fails, cases = [], []
    with tempfile.TemporaryDirectory(prefix="omni-gpu-c2a-") as T:
        rng = random.Random(20261008); n = 1 << 20; ls = 256; groups = n // ls
        words = [rng.getrandbits(32) for _ in range(n)]; src = f"{T}/in.bin"; open(src, "wb").write(struct.pack(f"<{n}I", *words))
        for dev in devices:
            for pairs, steps in ((1, 1), (50, 20)):
                prog = f"{T}/p-{pairs}.txt"
                lines = [f"buf file {src}", f"buf zero {4 * n}"]
                for _ in range(pairs):
                    lines.append(f"pass {SPV} {groups},1,1 spec 0=1 100={ls} bind 0 1")
                    lines.append(f"pass {SPV} {groups},1,1 spec 0=1 100={ls} bind 1 0")
                lines += ["read 0", "read 1"]; open(prog, "w").write("\n".join(lines) + "\n")
                od = f"{T}/o-{dev}-{pairs}-{steps}"
                r = subprocess.run([BIN, "session", prog, "--device", dev, "--steps", str(steps), "--out", od], capture_output=True, text=True, timeout=600)
                case = {"device": dev, "n": n, "pass_pairs": pairs, "passes_per_step": 2 * pairs, "steps": steps}
                if r.returncode:
                    case["error"] = r.stderr.strip()[-500:]; fails.append(f"{dev} {pairs}x{steps}: {case['error']}"); cases.append(case); continue
                info = json.loads(r.stdout.strip().splitlines()[-1]); k = 2 * pairs * steps
                bad = {}
                for bi, add in ((0, k), (1, k - 1)):
                    got = open(f"{od}/buf{bi}.bin", "rb").read(); want = struct.pack(f"<{n}I", *[(w + add) & 0xFFFFFFFF for w in words])
                    bad[bi] = 0 if got == want else sum(1 for i in range(0, 4 * n, 4) if got[i:i + 4] != want[i:i + 4])
                    case[f"buf{bi}_sha256"] = hashlib.sha256(got).hexdigest()
                case.update({k2: info[k2] for k2 in ("device", "device_local", "bytes", "passes", "setup_ms", "first_step_ms", "wall_ms", "ms_per_step", "gpu_ms_last")})
                case["ms_per_pass"] = round(info["ms_per_step"] / (2 * pairs), 4); case["mismatched_words"] = bad
                if any(bad.values()): fails.append(f"{dev} {pairs}x{steps}: mismatched {bad}")
                cases.append(case)
            # the old way, one pass: full setup + upload + dispatch + readback + teardown per call
            od = f"{T}/one-{dev}"
            r = subprocess.run([BIN, "run", SPV, "--device", dev, "--buf", src, "--zero", str(4 * n), "--spec", "0=1", "--spec", f"100={ls}",
                                "--groups", f"{groups},1,1", "--out", od], capture_output=True, text=True, timeout=300)
            if r.returncode: fails.append(f"{dev} one-shot: {r.stderr.strip()[-300:]}")
            else:
                info = json.loads(r.stdout.strip().splitlines()[-1])
                cases.append({"device": dev, "one_shot": True, "setup_ms": info["setup_ms"], "wall_ms": info["wall_ms"], "gpu_ms": info["gpu_ms"],
                              "ms_per_pass": round(info["setup_ms"] + info["wall_ms"], 3)})
    res = {"gate": "CYCLONE-ARRAY C2a resident session", "bin_sha256": hashlib.sha256(open(BIN, "rb").read()).hexdigest()[:12],
           "cases": cases, "fails": fails, "pass": not fails}
    json.dump(res, open(f"{out}/session.json", "w"), indent=1)
    for c in cases: print(json.dumps(c))
    print("PASS" if not fails else "FAIL: " + "; ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()

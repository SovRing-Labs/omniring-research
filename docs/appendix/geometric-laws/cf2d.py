#!/usr/bin/env python3
"""CORE-FIELD CF-2d: velocity-shifted bump control + a Burak & Fiete 2009 CAN oracle.
Pre-registered in the CORE-FIELD plan (unpublished working notes) (2026-10-02) before this file existed.

Arm ORACLE: Burak & Fiete 2009 (PLoS Comput Biol 5(2):e1000291) mechanism — 4 preferred-direction (PD)
subpopulations (E/W/N/S, 2x2 checkerboard tiling); each class's excitatory footprint is a small Gaussian
kernel centred not on itself but offset by L cells in its PD (the paper's offset-Mexican-hat connectivity,
W0(delta - L*e_d)); global scalar inhibition stands in for the Mexican-hat surround (CF-0b's proven
simplification); velocity modulates the directional subpopulations as feedforward gain (vel_gain * v.e_d),
not an added bias.

Arm OURS: CF-0b's proven rule and 6-hex-neighbour excitatory kernel, unchanged, but the field the kernel
reads from is shifted by an accumulated, fractional velocity-integrated displacement (kernel offset by the
commanded velocity) instead of adding an external bias bump.

MOVE/HOLD/RELEASE measurement structure (walk counts, tick counts, distance bars) reused unchanged from
cf2c.py: centre(), wrap_dist(), bump_at(), the hex NB table, 20x100-tick MOVE walks, 300-tick HOLD,
200-tick-capped RELEASE. No sweep this run (CF-2d tests two fixed mechanisms, not an operating point).
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.environ.get("OMNI_RING_PATH", "../omni-ring"))  # noqa: E402 (unused here; kept for parity with cf2c/cf0b imports)

OUT = os.path.expanduser("~/gpurun-out-0930/cf2d.result.json")
N = 48
rng = np.random.default_rng(0)

# ---- shared surface (unchanged from cf2c.py / cf0b.py) ----------------------------------------------------


def hex_neighbours():
    """6 neighbours on an offset-row hex grid, wrapped (torus)."""
    nb = np.zeros((N, N, 6, 2), dtype=int)
    for y in range(N):
        for x in range(N):
            odd = y % 2
            cand = [(x - 1, y), (x + 1, y), (x - 1 + odd, y - 1), (x + odd, y - 1), (x - 1 + odd, y + 1), (x + odd, y + 1)]
            nb[y, x] = [((cx % N), (cy % N)) for cx, cy in cand]
    return nb


NB = hex_neighbours()


def centre(a):
    th = 2 * np.pi * np.arange(N) / N
    wx = a.sum(0); wy = a.sum(1)
    cx = (np.angle((wx * np.exp(1j * th)).sum()) % (2 * np.pi)) * N / (2 * np.pi)
    cy = (np.angle((wy * np.exp(1j * th)).sum()) % (2 * np.pi)) * N / (2 * np.pi)
    return cx, cy


def bump_at(cx, cy, r=3.0):
    yy, xx = np.mgrid[0:N, 0:N]
    dx = (xx - cx + N / 2) % N - N / 2; dy = (yy - cy + N / 2) % N - N / 2
    return np.exp(-(dx ** 2 + dy ** 2) / (2 * r ** 2))


def wrap_dist(p, q):
    d = np.abs(np.array(p) - np.array(q)); d = np.minimum(d, N - d); return float(np.hypot(*d))


# ---- Arm OURS: CF-0b rule, kernel offset by accumulated velocity -----------------------------------------

OURS_KW = dict(w_ex=0.5, w_in=2.5, b0=0.05, tau=0.1)


def ours_step(a, off, v=(0.0, 0.0), extra=0.0, noise=0.0, w_ex=0.5, w_in=2.5, b0=0.05, tau=0.1):
    """CF-0b's proven 6-hex-neighbour excitatory rule, applied to a field shifted by the accumulated,
    fractional velocity displacement (off), instead of adding an external bias. off is (off_x, off_y),
    mutated in place: integer part consumed as this tick's roll, fractional remainder carried forward.
    extra is an external drive term (e.g. the HOLD/RELEASE distractor) entering the SAME way cf0b/cf2c's
    `inp` does -- added into the drive before the tau integration, never written straight into the state."""
    off[0] += v[0]; off[1] += v[1]
    sx, sy = int(round(off[0])), int(round(off[1]))
    off[0] -= sx; off[1] -= sy
    a_read = np.roll(a, shift=(sy, sx), axis=(0, 1)) if (sx or sy) else a
    s = np.zeros_like(a)
    for k in range(6):
        s += a_read[NB[:, :, k, 1], NB[:, :, k, 0]]
    drive = w_ex * s - w_in * 6 * a.mean() + b0 + extra
    if noise:
        drive = drive + noise * rng.normal(size=a.shape)
    return np.clip(a + tau * (-a + drive), 0.0, 1.0)


# ---- Arm ORACLE: Burak-Fiete offset-connectivity + PD velocity coupling ------------------------------------

DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # E, W, N, S unit vectors (dx, dy)
YY, XX = np.mgrid[0:N, 0:N]
MASK = [((XX % 2) == (d % 2)) & ((YY % 2) == (d // 2)) for d in range(4)]  # 2x2 checkerboard, one class per cell
L_OFFSET = 1
SIGMA_E = 1.0
KRAD = 2
BASE_TAPS = []
for dy in range(-KRAD, KRAD + 1):
    for dx in range(-KRAD, KRAD + 1):
        w = np.exp(-(dx * dx + dy * dy) / (2 * SIGMA_E ** 2))
        if w > 0.02:
            BASE_TAPS.append((dy, dx, w))
_tap_sum = sum(w for _, _, w in BASE_TAPS)
BASE_TAPS = [(dy, dx, w / _tap_sum) for dy, dx, w in BASE_TAPS]  # normalised so each class contributes unit gain

ORACLE_KW = dict(w_ex=2.0, w_in=2.5, b0=0.05, tau=0.1, vel_gain=3.0)


def oracle_excite(a):
    total = np.zeros_like(a)
    for d in range(4):
        a_d = a * MASK[d]
        ex, ey = L_OFFSET * DIRS[d][0], L_OFFSET * DIRS[d][1]
        for dy, dx, w in BASE_TAPS:
            total += w * np.roll(a_d, shift=(ey + dy, ex + dx), axis=(0, 1))
    return total


def oracle_step(a, v=(0.0, 0.0), extra=0.0, noise=0.0, w_ex=2.0, w_in=2.5, b0=0.05, tau=0.1, vel_gain=3.0):
    """Burak-Fiete: offset-per-PD-class excitatory connectivity (oracle_excite), global inhibitory surround
    (CF-0b's proven simplification), velocity as feedforward gain on the PD-aligned subpopulations. extra is
    an external drive term (HOLD/RELEASE distractor), entering the drive the same way cf0b/cf2c's `inp` does."""
    exc = oracle_excite(a)
    vx, vy = v
    ff = np.zeros_like(a)
    for d in range(4):
        align = vx * DIRS[d][0] + vy * DIRS[d][1]
        ff = ff + MASK[d] * (vel_gain * align)
    drive = w_ex * exc - w_in * 6 * a.mean() + b0 + ff + extra
    if noise:
        drive = drive + noise * rng.normal(size=a.shape)
    return np.clip(a + tau * (-a + drive), 0.0, 1.0)


# ---- measurement (structure reused unchanged from cf2c.py's point(); mechanism swapped per arm) -----------


def measure(step_fn, kw, is_ours):
    hits = 0
    for _ in range(20):
        a = bump_at(24, 24); target = np.array([24.0, 24.0])
        off = [0.0, 0.0]
        for t in range(30):
            a = step_fn(a, off, (0.0, 0.0), **kw) if is_ours else step_fn(a, (0.0, 0.0), **kw)
        for t in range(100):
            vx, vy = rng.normal(0, 0.3, 2); target += (vx, vy)
            a = step_fn(a, off, (vx, vy), **kw) if is_ours else step_fn(a, (vx, vy), **kw)
        hits += int(wrap_dist(centre(a), target % N) <= 2.0)
    move = hits / 20

    a = bump_at(10, 10); off = [0.0, 0.0]
    for t in range(30):
        a = step_fn(a, off, (0.0, 0.0), **kw) if is_ours else step_fn(a, (0.0, 0.0), **kw)
    held = 0
    distractor = 0.4 * bump_at(30, 30)
    for t in range(300):
        a = step_fn(a, off, (0.0, 0.0), extra=distractor, **kw) if is_ours else step_fn(a, (0.0, 0.0), extra=distractor, **kw)
        held += int(wrap_dist(centre(a), (10, 10)) <= 1.0)
    hold = held / 300

    rel = None
    distractor = 1.0 * bump_at(30, 30)
    for t in range(200):
        a = step_fn(a, off, (0.0, 0.0), extra=distractor, **kw) if is_ours else step_fn(a, (0.0, 0.0), extra=distractor, **kw)
        if wrap_dist(centre(a), (30, 30)) <= 2.0:
            rel = t; break
    return move, hold, rel


def main():
    out = {}
    for name, step_fn, kw, is_ours in (("ORACLE", oracle_step, ORACLE_KW, False), ("OURS", ours_step, OURS_KW, True)):
        mv, hd, rl = measure(step_fn, kw, is_ours)
        ok = mv >= 0.95 and hd >= 0.99 and rl is not None and rl <= 20
        out[name] = {"move": mv, "hold": hd, "release": rl, "pass": bool(ok)}
        print(name, out[name], flush=True)
    out["verdict"] = {"ORACLE_PASS": out["ORACLE"]["pass"], "OURS_PASS": out["OURS"]["pass"]}
    json.dump(out, open(OUT, "w"), indent=1)
    print("CF-2d", out["verdict"])


if __name__ == "__main__":
    main()

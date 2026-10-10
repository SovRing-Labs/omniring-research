#!/usr/bin/env python3
"""math core M1 reference driver (reader side): each concept's PUBLISHED definition, written plainly. One call per stdin line
"name args…" (lists as "n v1 … vn") → the value(s), or "x" when the inputs are outside the concept's domain."""
import math, sys

def rd(t):
    n = int(t.pop(0)); v = t[:n]; del t[:n]; return v

def call(f, t):
    I = lambda: int(t.pop(0))
    if f == "crt2":              # Chinese remainder theorem, two coprime moduli: the x in [0, m1·m2) with x ≡ r1 (m1), x ≡ r2 (m2)
        r1, m1, r2, m2 = I(), I(), I(), I()
        if m1 < 1 or m2 < 1 or math.gcd(m1, m2) != 1 or not (0 <= r1 < m1 and 0 <= r2 < m2): return None
        return next(x for x in range(m1 * m2) if x % m1 == r1 and x % m2 == r2)
    if f == "mixed_radix":       # mixed-radix numeral (d0, d1, d2) in bases (m0, m1, m2) → its value
        d0, d1, d2, m0, m1 = I(), I(), I(), I(), I()
        if not (0 <= d0 < m0 and 0 <= d1 < m1 and d2 >= 0): return None
        return d0 + m0 * (d1 + m1 * d2)
    if f == "mod_barrett":       # a mod m (the definition; the Barrett form is the authored equation, checked against it)
        a, m = I(), I()
        if m < 2 or m >= 65536 or not (0 <= a < m * m): return None
        return a % m
    if f == "hamming":           # Hamming distance of two non-negative integers = bits that differ
        a, b = I(), I()
        if a < 0 or b < 0 or a >= 2**31 or b >= 2**31: return None
        return bin(a ^ b).count("1")
    if f == "isqrt":             # integer square root: the largest r with r·r ≤ n
        n = I()
        if n < 0: return None
        return math.isqrt(n)
    if f == "period":            # smallest period p ≥ 1 of a sequence: v[i] = v[i+p] for every valid i (len if none shorter)
        v = [int(x) for x in rd(t)]
        if not v: return None
        return next(p for p in range(1, len(v) + 1) if all(v[i] == v[i + p] for i in range(len(v) - p)))
    if f == "absmean_quant":     # BitNet b1.58 weight quantisation: s = max(mean|w|, 1e-5); q = clamp(round(w/s), −1, 1)
        w = [float(x) for x in rd(t)]
        if not w: return None
        s = max(sum(abs(x) for x in w) / len(w), 1e-5); return [float(min(1, max(-1, round(x / s)))) for x in w]
    if f == "softmax":           # numerically stable softmax: exp(x − max) / Σ exp(x − max)
        x = [float(v) for v in rd(t)]
        if not x: return None
        m = max(x); e = [math.exp(v - m) for v in x]; z = sum(e); return [v / z for v in e]
    if f == "fib":               # Fibonacci F(n), F(0)=0, F(1)=1 (the golden-ratio recurrence)
        n = I()
        if not (0 <= n <= 80): return None
        a, b = 0, 1
        for _ in range(n): a, b = b, a + b
        return a
    if f == "clock_read":        # residue clock read: t in [0, 105) from its residues on rings 3, 5, 7
        r3, r5, r7 = I(), I(), I()
        if not (0 <= r3 < 3 and 0 <= r5 < 5 and 0 <= r7 < 7): return None
        return next(x for x in range(105) if x % 3 == r3 and x % 5 == r5 and x % 7 == r7)
    return None

for line in sys.stdin:
    t = line.split(); f = t.pop(0) if t else ""
    try: r = call(f, t)
    except Exception: r = None
    print("x" if r is None else (" ".join(repr(float(v)) for v in r) if isinstance(r, list) else r), flush=True)

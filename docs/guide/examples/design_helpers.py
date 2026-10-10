"""Design helpers from "Geometric Computing and You", "Using the laws in your own work".

    python3 design_helpers.py
No dependencies beyond the standard library.
"""
import math


def accuracy(D, n, C, a=1.046):
    """Law L1: recall accuracy for n items bundled in D dimensions, read among C candidates."""
    phi = 0.5 * (1 + math.erf(a * math.sqrt(D / n) / math.sqrt(2)))
    return phi ** (C - 1)


def max_items(D, C, target=0.99, a=1.046):
    """Largest n that keeps accuracy at or above target (fit a on your own data; ours ranged 1.02-1.33)."""
    n = 1
    while accuracy(D, n + 1, C, a) >= target:
        n += 1
    return n


def pick_rings(span, start=3):
    """Smallest run of primes from `start` whose product covers `span`, plus a check ring larger than all of them."""
    def isprime(p):
        return p > 1 and all(p % q for q in range(2, int(p ** 0.5) + 1))
    rings, prod, p = [], 1, start
    while prod < span:
        if isprime(p):
            rings.append(p)
            prod *= p
        p += 1
    check = p
    while not isprime(check):
        check += 1
    return rings, prod, check


if __name__ == "__main__":
    print("max items, D 5120, C 1000, 99 %:", max_items(5120, 1000))
    for D, n in ((5120, 250), (8192, 500), (10240, 500)):
        print("accuracy D %d n %d C 1000: %.4f" % (D, n, accuracy(D, n, 1000)))
    for span in (1000, 86400, 10 ** 6, 2 ** 32):
        rings, prod, check = pick_rings(span)
        print("range %d: rings %s -> %d, check ring %d (random pass about 1 in %d)" % (span, rings, prod, check, check))

"""Five recipes from "Hyperdimensional Computing and You", section 8.

Run against the public omni-ring package (https://github.com/SovRing-Labs/omni-ring):
    pip install -e <omni-ring checkout>
    python3 ring_recipes.py
Works on the NumPy path; the AVX2 kernel is optional.
"""
import math

import numpy as np
from omni_ring.chain import advance, bind, encode, get_tick
from omni_ring.check import ResidueDesyncError, check_anomaly
from omni_ring.codebook import generate_direct_codebooks, generate_rotations
from omni_ring.crt import direct_probe
from omni_ring.peel import read_all, read_one
from omni_ring.types import DEFAULT_SPEC

# Recipe 1: a clock you read without searching
mods = DEFAULT_SPEC.all_moduli  # (3, 5, 7, 13, 17)
CB = generate_direct_codebooks(seed=5)
x = 1234
slot = sum(cb[x % m] for cb, m in zip(CB, mods))
residues, got = direct_probe(slot, CB, mods)
print("1. residues", residues, "->", got, "verified", check_anomaly(residues))

# Recipe 2: the check ring refuses a slip
bad = list(residues)
bad[2] = (bad[2] + 1) % 7
try:
    check_anomaly(bad)
    print("2. accepted (unexpected)")
except ResidueDesyncError as e:
    print("2. refused:", e)

# Recipe 3: time as a turn
R = generate_rotations(seed=0)
v, tick = encode(41, R), get_tick(R)
print("3. one tick 41 -> 42:", np.allclose(bind(v, tick), encode(42, R)),
      "| ten ticks 41 -> 51:", np.allclose(advance(v, tick, 10), encode(51, R)))

# Recipe 4: a crowded slot, a cue, and peeling
rng = np.random.default_rng(7)
xs = [int(a) for a in rng.choice(1365, 8, replace=False)]
crowd = sum(encode(a, R) for a in xs)
found = read_all(crowd, R)
print("4. marks", sorted(xs))
print("   read_one(cue)", read_one(crowd, R, cue=xs[0] % 13),
      "| read_all", sorted(found), "| true", len(set(found) & set(xs)), "fakes", len(set(found) - set(xs)))


# Recipe 5: size a memory with law L1
def accuracy(D, n, C, a=1.046):
    phi = 0.5 * (1 + math.erf(a * math.sqrt(D / n) / math.sqrt(2)))
    return phi ** (C - 1)


for n in (100, 200, 300, 400):
    print("5. D=5120 C=1000 n=%d accuracy %.4f" % (n, accuracy(5120, n, 1000)))

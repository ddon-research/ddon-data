"""Cheap weakness checks on the captured login-server RSA moduli (moduli.csv)."""
import csv, math, sys
from math import gcd, isqrt
mods = sorted({int(r[2], 16) for r in csv.reader(open(sys.argv[1]))})
print("distinct moduli:", len(mods), "bits:", sorted({m.bit_length() for m in mods}))
# small primes
small = [p for p in range(2, 200000) if all(p % q for q in range(2, isqrt(p) + 1))]
print("small factor hits:", [p for m in mods for p in small if m % p == 0])
# pairwise gcd (batch GCD for so few keys)
print("shared factors:", [(i, j) for i in range(len(mods)) for j in range(i + 1, len(mods)) if gcd(mods[i], mods[j]) != 1])
# Fermat: p, q close together
def fermat(n, it=200000):
    a = isqrt(n) + (0 if isqrt(n) ** 2 == n else 1)
    for _ in range(it):
        b2 = a * a - n; b = isqrt(b2)
        if b * b == b2: return a - b
        a += 1
print("fermat hits:", [i for i, m in enumerate(mods) if fermat(m)])
# Pollard p-1, B = 1e5
def pm1(n, B=100000):
    a = 2
    for p in small:
        if p > B: break
        pk = p
        while pk * p <= B: pk *= p
        a = pow(a, pk, n)
    g = gcd(a - 1, n)
    return g if 1 < g < n else None
print("pollard p-1 hits:", [i for i, m in enumerate(mods) if pm1(m)])

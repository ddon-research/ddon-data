"""Enumerate symbolic final rng states produced by overlapping calls of sub_13B5E10.

Pre-race memory is [s0, s1, s2, s3] (the 4 most recent outputs, oldest first).
A derived value is written as g(x1, x2, w) = t ^ w ^ ((t ^ (w >> 17)) >> 4), t = (x1 << 15) ^ x2.
Prints one pattern per line as JSON: [word0, word1, word2, word3] where each word is an int index
into the value table: 0..3 = s0..s3, 4.. = derived entries listed in 'derived'.
"""
import json, sys
from itertools import count
OPS = 9

def run(nthreads):
    finals = set()
    def step(mem, r, pc):
        mem = list(mem); r = dict(r)
        if pc == 0: r['x1'] = mem[0]
        elif pc == 1: r['y'] = mem[1]
        elif pc == 2: r['w'] = mem[3]
        elif pc == 3: r['x2'] = mem[0]
        elif pc == 4: mem[0] = r['y']
        elif pc == 5: r['z'] = mem[2]
        elif pc == 6: mem[1] = r['z']
        elif pc == 7: mem[2] = r['w']
        elif pc == 8: mem[3] = ('g', r['x1'], r['x2'], r['w'])
        return tuple(mem), r
    seen = set()
    def rec(mem, regs, pcs):
        key = (mem, tuple(tuple(sorted(r.items())) for r in regs), pcs)
        if key in seen: return
        seen.add(key)
        if all(p == OPS for p in pcs):
            finals.add(mem); return
        for i in range(nthreads):
            if pcs[i] < OPS:
                m2, r2 = step(mem, regs[i], pcs[i])
                rr = list(regs); rr[i] = r2; pp = list(pcs); pp[i] += 1
                rec(m2, tuple(rr), tuple(pp))
    rec((('s',0),('s',1),('s',2),('s',3)), tuple({} for _ in range(nthreads)), (0,)*nthreads)
    return finals

if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    fin = run(n)
    # clean results: sequential application of n calls -> exclude
    print(len(fin), file=sys.stderr)
    table = {}; derived = []
    def idx(v):
        if v[0] == 's': return v[1]
        k = tuple(idx(a) for a in v[1:])
        if k not in table:
            table[k] = 4 + len(derived); derived.append(k)
        return table[k]
    pats = sorted({tuple(idx(v) for v in m) for m in fin})
    json.dump({'derived': derived, 'patterns': pats}, sys.stdout)

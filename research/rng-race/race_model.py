"""Interleave calls of the client's rng_next (PC 03040008 sub_13B5E10) at memory-op granularity.

Op order from the disassembly at 0x13B5E10:
  Rx1, Ry, Rw, Rx2, Wx<-y, Rz, Wy<-z, Wz<-w, Ww<-result
  result = t ^ w ^ ((t ^ (w >> 17)) >> 4), t = (x1 << 15) ^ x2
"""
M = 0xFFFFFFFF
OPS = 9

def step(mem, regs, pc):
    r = dict(regs); mem = list(mem); out = None
    if pc == 0: r['x1'] = mem[0]
    elif pc == 1: r['y'] = mem[1]
    elif pc == 2: r['w'] = mem[3]
    elif pc == 3: r['x2'] = mem[0]
    elif pc == 4: mem[0] = r['y']
    elif pc == 5: r['z'] = mem[2]
    elif pc == 6: mem[1] = r['z']
    elif pc == 7: mem[2] = r['w']
    elif pc == 8:
        t = ((r['x1'] << 15) & M) ^ r['x2']; w = r['w']
        out = (t ^ w ^ ((t ^ (w >> 17)) >> 4)) & M
        mem[3] = out
    return tuple(mem), r, out

def interleavings(mem0, nthreads):
    """Yield (outputs per thread, final mem) for every interleaving of nthreads concurrent calls."""
    def rec(mem, regs, pcs, outs):
        if all(p == OPS for p in pcs):
            yield tuple(outs), mem; return
        for i in range(nthreads):
            if pcs[i] < OPS:
                m2, r2, o = step(mem, regs[i], pcs[i])
                regs2 = list(regs); regs2[i] = r2
                pcs2 = list(pcs); pcs2[i] += 1
                outs2 = list(outs)
                if o is not None: outs2[i] = o
                yield from rec(m2, regs2, pcs2, outs2)
    yield from rec(tuple(mem0), [{}]*nthreads, [0]*nthreads, [None]*nthreads)

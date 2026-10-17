"""DDON client xorshift128 variant (as in ddon_common_key_bruteforce/src/ddon_random.hpp)."""
M = 0xFFFFFFFF
ALPHABET = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

def init(seed):
    v2 = 0x159A55E5; v3 = 521288629; v4 = 88675123; v5 = (seed ^ 0xAC9365) & M
    for _ in range(100):
        v7 = v2; v2 = v3; v3 = v4
        a = (v5 ^ (0x65AC9365 >> (v5 & 3))) & M
        v5 = (v5 ^ (0x65AC9365 >> (v5 & 3)) ^ (a >> 3) ^ (a >> 4) ^ ((8 * a) & M) ^ ((16 * a) & M)) & M
        v4 = (v4 ^ v5 ^ ((v5 << 15) & M) ^ (((v5 ^ (v5 << 15)) & M) >> 4) ^ (v4 >> 21)) & M
    return [v7, v2, v3, v4]

def out(x, w):
    t = (x ^ (x << 15)) & M
    return (t ^ w ^ ((t ^ (w >> 17)) >> 4)) & M

def nxt(s):
    x, y, z, w = s
    n = out(x, w)
    return [y, z, w, n], n

def seq(state, n):
    r = []
    s = list(state)
    for _ in range(n):
        s, v = nxt(s); r.append(v)
    return r

def inv_t(t):
    # invert t ^ (t>>4)
    r = t
    for _ in range(8): r = t ^ (r >> 4)
    return r & M

def inv_x(t):
    # invert x ^ (x<<15)
    r = t
    for _ in range(3): r = (t ^ (r << 15)) & M
    return r

def prev_x(w, n):
    """given old w and new output n, recover old x"""
    # n = t ^ w ^ (t>>4) ^ (w>>21)
    tt = n ^ w ^ (w >> 21)
    return inv_x(inv_t(tt))

def back(state, k):
    """return k values preceding state (oldest first): state=[x,y,z,w] are the 4 most recent outputs"""
    s = list(state); pre = []
    for _ in range(k):
        x, y, z, w = s
        # s came from [p, x, y, z] with out(p, z) == w
        p = prev_x(z, w)
        pre.append(p); s = [p, x, y, z]
    return pre[::-1]

def key_chars(vals):
    return bytes(ALPHABET[v & 63] for v in vals)

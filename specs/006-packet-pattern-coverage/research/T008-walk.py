"""006 T008 capture walk: groups 14 WARP, 10 ITEM, 50 ITEM_SORT (client 03040008).

Run from D:/ddon-data:  python -X utf8 -I specs/006-packet-pattern-coverage/research/T008-walk.py
Stdlib only. Reads packets/decrypted_raw/*/<n>_<NAME>_<time>.<g>_<id>_<sub>; writes nothing.

Header: u8 group, u16 id, u8 sub, u8 source (0x00 C2S, 0x34 S2C), 4 bytes; body from 0x09.
Fit: decode ends within the last 15 bytes of the file (cipher padding), no overrun.
Layouts are the PC 03040008 readers/writers of the T008 report (big-endian). Counter-tests
("ps4:" variants) are the PS4 02020005 bodies with PC framing; "ps4frame:" adds the PS4 u16 error
first on NTCs. "tally" prints the distinct values of the named top-level fields (code-only
differences that the 15-byte fit window cannot discriminate).
"""
import hashlib
import os
import re
import struct
import sys
from collections import Counter, defaultdict

ROOT = os.path.join("packets", "decrypted_raw")
SLACK = 15


class Overrun(Exception):
    pass


class R:
    def __init__(self, b, pos):
        self.b, self.p = b, pos
        self.lists = defaultdict(int)  # list path -> max count seen

    def take(self, n):
        if self.p + n > len(self.b):
            raise Overrun()
        v = self.b[self.p:self.p + n]
        self.p += n
        return v


PRIM = {"u8": ">B", "bool": ">B", "u16": ">H", "u32": ">I", "s32": ">i", "u64": ">Q", "f32": ">f"}


def rd(r, t, path=""):
    """t: prim name | 'str' | ('list', T) | ('arr', n, T) | ('raw', n) | [T, ...] (struct)."""
    if isinstance(t, str):
        if t == "str":
            n = struct.unpack(">H", r.take(2))[0]
            return r.take(n).decode("utf-8", "replace")
        f = PRIM[t]
        return struct.unpack(f, r.take(struct.calcsize(f)))[0]
    if isinstance(t, tuple) and t[0] == "list":
        n = struct.unpack(">I", r.take(4))[0]
        if n > 10000:
            raise Overrun()
        r.lists[path] = max(r.lists[path], n)
        return [rd(r, t[1], path + "[]") for _ in range(n)]
    if isinstance(t, tuple) and t[0] == "arr":
        return [rd(r, t[2], path) for _ in range(t[1])]
    if isinstance(t, tuple) and t[0] == "raw":
        return r.take(t[1])
    return [rd(r, x, "%s.%d" % (path, i)) for i, x in enumerate(t)]


def L(t):
    return ("list", t)


# --- shared PC 03040008 structures (VAs in the report) ---
EquipElementParam = ["u8", "u32", "u16"]          # 0x765a90 element
AddStatusParam = ["u8", "u8", "u16", "u16"]       # 0x765ba0 element
EquipStatParam = ["u8", "u16"]                    # 0x766210 element
ItemList = ["str", "u32", "u32", "u8", "u8", "u16", "u8", "u8", "bool", "u32", "u32", "u32",
            L(EquipElementParam), L(AddStatusParam), L(EquipStatParam)]   # 0x76aca0 (list 0x76abe0)
ItemUpdateResult = [ItemList, "s32"]              # list 0x76aec0
UpdateWalletPoint = ["u8", "u32", "s32", "u32"]   # list 0x77c1c0
MoveItemUIDFromTo = ["str", "u32", "u8", "u8", "u16"]  # writer 0x780090 element
ItemSort = ["u8", ("raw", 1024)]                  # list 0x75e6e0 (u8 + u8[0x400])

# --- PS4 02020005 variants for counter-tests ---
PS4_ItemList = ["u8", "u16", "str", "u32", "u32", "u32", "u32", "u32", "u8", L(["u8", "u32"]), "u8", "bool"]

RES = "res"    # s32 Error; if 0: s32 Result + body
NTC = "ntc"    # S2C notice, no header
REQ = "req"    # C2S (REQ or C2S NTC), source 0x00

IDS = {
    # id: (kind, body, {variant: body}, tally indices)
    "10.0.1": (REQ, ["str", "u32"], {}, ()),
    "10.0.2": (RES, [], {}, ()),
    "10.0.16": (NTC, ["u32", "u32", "u32"], {"ps4frame": ["u16", "u32", "u32", "u32"]}, ()),
    "10.3.1": (REQ, [L("u8")], {}, ()),
    "10.3.2": (RES, [L(ItemList)], {"ps4": [L(PS4_ItemList)]}, ()),
    "10.6.1": (REQ, [], {}, ()),
    "10.6.2": (RES, [L(ItemList)], {"ps4": [L(PS4_ItemList)]}, ()),
    "10.7.1": (REQ, ["u8", L(MoveItemUIDFromTo)], {}, ()),
    "10.7.2": (RES, [], {}, ()),
    "10.9.1": (REQ, [L("u8")], {}, ()),
    "10.10.16": (NTC, ["u8", "u16", "u16"], {"ps4frame": ["u16", "u8", "u16", "u16"]}, ()),
    "10.12.16": (NTC, ["u16", L(ItemUpdateResult), L(UpdateWalletPoint)],
                 {"ps4": ["u16", L([PS4_ItemList, "s32"]), L(UpdateWalletPoint)],
                  "ps4frame": ["u16", "u16", L([PS4_ItemList, "s32"]), L(UpdateWalletPoint)]}, ()),
    "10.13.16": (NTC, ["s32", "bool", L(["u8", "u16"])],
                 {"ps4": ["s32", "bool", L(["u8", "u8"])],
                  "ps4frame": ["u16", "s32", "bool", L(["u8", "u8"])]}, ()),
    "10.14.16": (NTC, ["u16", L(["u8", "u32"])], {}, (0,)),
    "14.1.1": (REQ, [], {}, ()),
    "14.1.2": (RES, [L("u32")], {}, ()),
    "14.2.1": (REQ, ["u32"], {}, ()),
    "14.2.2": (RES, [L(["u32", "u32"])], {}, ()),
    "14.3.1": (REQ, ["u32", "u32", "u32"], {}, ()),
    "14.3.2": (RES, ["u32", "u32"], {}, ()),
    "14.4.1": (REQ, ["u32"], {}, ()),
    "14.4.2": (RES, [L(["u32", "u32", "u32"]), "u32"], {}, ()),
    "14.8.1": (REQ, ["u32"], {}, ()),
    "14.8.2": (RES, [L(["u32", "u32", "u32"])], {}, ()),
    "14.9.1": (REQ, ["u32", "u32", "u32"], {}, ()),
    "14.9.2": (RES, ["u32", "u32"], {}, ()),
    "14.10.16": (REQ, [], {}, ()),
    "14.11.16": (REQ, ["u32"], {"empty": []}, (0,)),
    "14.12.1": (REQ, [], {}, ()),
    "14.12.2": (RES, ["u32", "u32"], {}, ()),
    "14.14.1": (REQ, [], {}, ()),
    "14.14.2": (RES, [L("u32")], {}, ()),
    "50.0.1": (REQ, [L("u32")], {}, ()),
    "50.0.2": (RES, [L(ItemSort)], {}, ()),
    "50.0.16": (NTC, [L(ItemSort)], {"ps4frame": ["u16", L(ItemSort)]}, ()),
    "50.1.1": (REQ, ["u8", ("raw", 1024), "bool"], {"ps4": ["u8", ("raw", 1024)]}, (2,)),
    "50.1.2": (RES, [], {}, ()),
}


def decode(b, kind, body):
    r = R(b, 9)
    err = None
    val = None
    if kind == RES:
        err = rd(r, "s32")
        if err == 0:
            rd(r, "s32")
            val = rd(r, body)
    else:
        val = rd(r, body)
    return r, err, val


def main():
    files = defaultdict(list)
    for d in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, d)
        if not os.path.isdir(p):
            continue
        for f in os.listdir(p):
            m = re.search(r"\.(\d+)_(\d+)_(\d+)$", f)
            if not m:
                continue
            key = "%s.%s.%s" % m.groups()
            if key in IDS:
                files[key].append(os.path.join(p, f))
    tot = hdr = fit = 0
    for key, (kind, body, variants, tally) in IDS.items():
        g, i, s = (int(x) for x in key.split("."))
        fs = sorted(files[key])
        n = len(fs)
        ok_h = ok_f = 0
        slacks, errs = [], 0
        lists = defaultdict(int)
        var_fail = defaultdict(int)
        tallies = defaultdict(Counter)
        mod8 = Counter()
        best = None
        for fp in fs:
            b = open(fp, "rb").read()
            mod8[len(b) % 8] += 1
            src = 0x34 if kind in (RES, NTC) else 0x00
            if len(b) >= 9 and b[0] == g and struct.unpack(">H", b[1:3])[0] == i and b[3] == s and b[4] == src:
                ok_h += 1
            try:
                r, err, val = decode(b, kind, body)
                sl = len(b) - r.p
                if 0 <= sl <= SLACK:
                    ok_f += 1
                    slacks.append(sl)
                    for k, v in r.lists.items():
                        lists[k] = max(lists[k], v)
                    if err:
                        errs += 1
                    if val is not None:
                        for ti in tally:
                            tallies[ti][val[ti] if not isinstance(val[ti], list) else len(val[ti])] += 1
                    score = (sum(r.lists.values()), len(b))
                    if best is None or score > best[0]:
                        best = (score, fp, len(b), r.p)
            except Overrun:
                pass
            for vn, vb in variants.items():
                try:
                    r2, _, _ = decode(b, kind, vb)
                    if not 0 <= len(b) - r2.p <= SLACK:
                        var_fail[vn] += 1
                except Overrun:
                    var_fail[vn] += 1
        tot += n
        hdr += ok_h
        fit += ok_f
        print("%-9s files %4d header %4d fit %4d slack %s err!=0 %d len%%8 %s" % (
            key, n, ok_h, ok_f, "%d-%d" % (min(slacks), max(slacks)) if slacks else "-", errs,
            dict(sorted(mod8.items()))))
        for vn in variants:
            print("          counter %-9s fails %d/%d" % (vn, var_fail[vn], n))
        if lists:
            print("          lists max:", ", ".join("%s=%d" % (k or "/", lists[k]) for k in sorted(lists)))
        for ti, c in tallies.items():
            print("          field %d values:" % ti, dict(c.most_common(8)))
        if best:
            _, fp, size, end = best
            h = hashlib.sha256(open(fp, "rb").read()).hexdigest()[:16]
            print("          sample %s (%d B, %s) end 0x%x" % (os.path.relpath(fp, ROOT).replace("\\", "/"), size, h, end))
    print("TOTAL files %d header %d fit %d" % (tot, hdr, fit))


if __name__ == "__main__":
    sys.exit(main())

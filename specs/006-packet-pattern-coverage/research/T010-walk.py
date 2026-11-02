"""006 T010 capture walk: groups 28 GP, 31 CLAN (client 03040008), plus the T009b StatusInfo check.

Run from D:/ddon-data:  python -X utf8 -I specs/006-packet-pattern-coverage/research/T010-walk.py
Stdlib only. Reads packets/decrypted_raw/*/<n>_<NAME>_<time>.<g>_<id>_<sub>; writes nothing.

Header: u8 group, u16 id, u8 sub, u8 source (0x00 C2S, 0x34 S2C), 4 bytes; body from 0x09.
Fit: decode ends within the last 15 bytes of the file (cipher padding), no overrun.
Layouts are the PC 03040008 readers/writers of the T010 report (big-endian). Counter-tests
("ps4:" variants) are the PS4 02020005 bodies with PC framing; "ps4frame:" adds the PS4 u16 error
first on NTCs. "tally" prints the distinct values of the named top-level fields.
The last block decodes CDataStatusInfo (PC 0x77a810) in every 2.0.2 capture and prints the
distinct (character, 12 values) tuples (T010 report section "StatusInfo").
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
        self.lists = defaultdict(int)

    def take(self, n):
        if self.p + n > len(self.b):
            raise Overrun()
        v = self.b[self.p:self.p + n]
        self.p += n
        return v


PRIM = {"u8": ">B", "bool": ">B", "u16": ">H", "u32": ">I", "s32": ">i", "u64": ">Q", "s64": ">q"}


def rd(r, t, path=""):
    """t: prim name | 'str' | ('list', T) | ('raw', n) | [T, ...] (struct)."""
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
    if isinstance(t, tuple) and t[0] == "raw":
        return r.take(t[1])
    return [rd(r, x, "%s.%d" % (path, i)) for i, x in enumerate(t)]


def L(t):
    return ("list", t)


# --- shared PC 03040008 structures (reader VAs in the report) ---
U32 = "u32"                                                               # CDataCommonU32 0x75e8e0
GPPeriod = ["u32", "bool", "u64"]                                         # list 0x7678e0
GPShopDisplayType = ["u32", "str", "u32"]                                 # list 0x767d00
GPShopDisplayLineup = ["u32", "u32", "u8", "u32", "u32", "u32", "str", "str", "u32", "str",
                       "u32", "u32", "u32", "u32"]                        # element 0x767be0
PS4_GPShopDisplayLineup = GPShopDisplayLineup[:9] + ["u32", "u32", "u32"]
GPCourseAvailable = ["u32", "str", "u64", "u32", "u32", "str"]            # element 0x7671a0
PS4_GPCourseAvailable = ["u32", "str", "u64", "u32", "u32", "u32", "u32"]
EditParam = ["u32", "u32", "bool", "bool", "bool"]                        # list 0x764b20
CommunityCharacterBaseInfo = ["u32", "str", "str", "str"]                 # 0x75ecf0
ClanJoinRequest = ["u32", "str", CommunityCharacterBaseInfo, "s64"]       # list 0x75d430
ClanHistoryElement = ["s64", "u8", "str", "str", "u32", "u32", "u32", "str"]  # element 0x75d390
FurnitureLayout = ["u32", "u32", "u8"]                                    # list 0x766f90
ClanBaseInfo = [L(U32), L(U32), ["u8", "u8", "u8"], [L(U32), L(U32)],
                ["u32", L(["u32", "u32", "bool", "u32"])], L(["u32", "str"]), L(["u8", "u32"])]
ClanShopBuffItem = ["u32", "u32", "u8", "u32", "str", L(["u32", "u8"]), L(U32)]  # element 0x75dee0
ClanShopInfo = ["u32", L(U32), L(U32)]                                    # 0x75e2a0 (not a function)
EquipItemInfo = ["u32", "u8", "u8", "u16", "u8", "u8", L(["u8", "u32", "u16"]),
                 L(["u8", "u8", "u16", "u16"]), L(["u8", "u16"])]         # 0x766070 (T009)
CharacterEquipData = [L(EquipItemInfo)]                                   # list 0x75c190
NoraPawnInfo = ["u32", "str", ("raw", 122), "u8", L(CharacterEquipData), L(CharacterEquipData)]  # 0x76f790
PS4_NoraPawnInfo = NoraPawnInfo[:-1]

RES = "res"    # s32 Error; if 0: s32 Result + body
NTC = "ntc"    # S2C notice, no header
REQ = "req"    # C2S, source 0x00

IDS = {
    # id: (kind, body, {variant: body}, tally indices)
    "28.0.1": (REQ, [], {}, ()),
    "28.0.2": (RES, ["u32", "s64", "u64", "u16"], {}, ()),
    "28.2.1": (REQ, [], {}, ()),
    "28.2.2": (RES, [L(GPPeriod)], {}, ()),
    "28.3.1": (REQ, [], {}, ()),
    "28.3.2": (RES, ["u32"], {}, ()),
    "28.6.1": (REQ, [], {}, ()),
    "28.6.2": (RES, ["str"], {}, ()),
    "28.7.1": (REQ, [], {}, ()),
    "28.7.2": (RES, [L(GPShopDisplayType)], {}, ()),
    "28.8.1": (REQ, ["u32"], {}, (0,)),
    "28.8.2": (RES, [L(GPShopDisplayLineup)], {"ps4": [L(PS4_GPShopDisplayLineup)]}, ()),
    "28.9.1": (REQ, ["u32", "u32"], {"ps4": ["u32"]}, (1,)),
    "28.9.2": (RES, ["u32", L(U32), "u32", "str"], {}, ()),
    "28.17.1": (REQ, [], {}, ()),
    "28.17.2": (RES, [L(GPCourseAvailable)], {"ps4": [L(PS4_GPCourseAvailable)]}, ()),
    "28.22.1": (REQ, [], {}, ()),
    "28.22.2": (RES, [L(EditParam)], {}, ()),
    "28.23.1": (REQ, ["u32", "u32", "u32"], {"ps4": ["u32"]}, (0, 1, 2)),
    "28.23.2": (RES, ["bool", "u32", "u32", "u32", "u32"], {"ps4": ["bool", "u32"]}, (0, 1, 2, 3, 4)),
    "28.24.16": (NTC, ["u32"], {"ps4frame": ["u16", "u32"]}, (0,)),
    "28.25.16": (NTC, ["u32", "u64", "u32"], {"ps4frame": ["u16", "u32", "u64", "u32"]}, (0, 2)),
    "28.26.16": (NTC, ["u32", "u64"], {"ps4frame": ["u16", "u32", "u64"]}, (0,)),
    "28.34.1": (REQ, [], {}, ()),
    "28.34.2": (RES, ["bool"], {}, (0,)),
    "31.4.1": (REQ, [], {}, ()),
    "31.9.1": (REQ, [], {}, ()),
    "31.9.2": (RES, [L(ClanJoinRequest)], {}, ()),
    "31.17.1": (REQ, ["bool"], {}, (0,)),
    "31.30.1": (REQ, [], {}, ()),
    "31.30.2": (RES, [L(ClanHistoryElement)], {}, ()),
    "31.31.1": (REQ, [], {}, ()),
    "31.31.2": (RES, ClanBaseInfo + [L(FurnitureLayout)], {"ps4": ClanBaseInfo}, ()),
    "31.34.1": (REQ, [], {}, ()),
    "31.34.2": (RES, [L(ClanShopBuffItem), "u32", ClanShopInfo], {}, ()),
    "31.40.1": (REQ, ["u32"], {}, ()),
    "31.40.2": (RES, ["u32"] + NoraPawnInfo, {"ps4": ["u32"] + PS4_NoraPawnInfo}, ()),
    "31.53.1": (REQ, [], {}, ()),
    "31.53.2": (RES, [L(FurnitureLayout)], {}, ()),
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


def collect(keys):
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
            if key in keys:
                files[key].append(os.path.join(p, f))
    return files


def walk():
    files = collect(IDS)
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
        names = Counter()
        best = None
        for fp in fs:
            names[re.sub(r"^\d+_|_\d{4}-\d\d-\d\dT.*$", "", os.path.basename(fp))] += 1
            b = open(fp, "rb").read()
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
                            x = val[ti]
                            tallies[ti][len(x) if isinstance(x, list) else x] += 1
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
        print("%-9s files %4d header %4d fit %4d slack %s err!=0 %d names %s" % (
            key, n, ok_h, ok_f, "%d-%d" % (min(slacks), max(slacks)) if slacks else "-", errs,
            dict(names)))
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


# --- StatusInfo check (2.0.2 S2C_CHARACTER_DECIDE_CHARACTER_ID_RES, layout from T009) ---
STATUS = ["u32", "u32", "u8"] + ["u32"] * 9                                # 0x77a810
STATUS_NAMES = ["Hp", "Stamina", "RevivePoint", "MaxHp", "MaxStamina", "WhiteHp", "GainHp",
                "GainStamina", "GainAttack", "GainDefense", "GainMagicAttack", "GainMagicDefense"]
JOBDATA = ["u8", "u32", "u32", "u32", ("raw", 20), ("raw", 30)]             # 0x75c770 (T009)


def status():
    fs = sorted(collect({"2.0.2"})["2.0.2"])
    seen = Counter()
    for fp in fs:
        b = open(fp, "rb").read()
        r = R(b, 9)
        try:
            if rd(r, "s32"):
                continue
            rd(r, ["s32", "u32"])                      # Result, RES u32 (T009 2.0.2)
            head = rd(r, ["u32", "u32", "u32", "str", "str", ("raw", 122)])
            st = rd(r, STATUS)
            job = rd(r, "u8")
        except Overrun:
            continue
        seen[(head[3], job, tuple(st))] += 1
    print("2.0.2 files %d; distinct (FirstName, Job, StatusInfo):" % len(fs))
    print("          " + ", ".join(STATUS_NAMES))
    for (nm, job, st), c in sorted(seen.items()):
        print("  %-8s job %2d x%-3d %s" % (nm, job, c, list(st)))


if __name__ == "__main__":
    walk()
    status()

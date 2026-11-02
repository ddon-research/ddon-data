"""006 T012 capture walk: groups 19 SKILL, 20 SHOP, 25 ORB_DEVOTE, 27 ACHIEVEMENT, 29 EQUIP, 39 GACHA,
43 LOADING_INFO (client 03040008).

Run from D:/ddon-data:  python -X utf8 -I specs/006-packet-pattern-coverage/research/T012-walk.py
Stdlib only. Reads packets/decrypted_raw/*/<n>_<NAME>_<time>.<g>_<id>_<sub>; writes nothing.

Header: u8 group, u16 id, u8 sub, u8 source (0x00 C2S, 0x34 S2C), 4 bytes; body from 0x09.
Fit: decode ends within the last 15 bytes of the file (cipher padding), no overrun.
Layouts are the PC 03040008 readers/writers of the T012 report (big-endian). Counter-tests
("ps4:" variants) are the PS4 02020005 bodies with PC framing; "ps4frame:" adds the PS4 u16 error
first on NTCs. "tally" prints the distinct values of the named top-level fields (lists: length).
29.23.16 has no PC reader (the handler returns 1 without reading); its layout here is the capture
shape only (I). The extra block prints value sets used by the report.
"""
import hashlib
import os
import re
import struct
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


PRIM = {"u8": ">B", "bool": ">B", "u16": ">H", "u32": ">I", "s32": ">i", "u64": ">Q", "s64": ">q",
        "f32": ">f", "f64": ">d"}


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


# --- PC 03040008 structures (reader/writer VAs in the report) ---
AchProgress = ["u32", "u32", "u32", "u32", "s64"]              # 0x758810 (loc, not a function)
AchRewardProgress = ["u32", "u32", "u32", "bool"]              # 0x758960
AchFurnitureReward = ["u32", "u32", "u32", "u32", "u32", "bool"]  # 0x7585a0, element 0x7586a0
AchRewardCommon = ["u8", "u32"]                                # 0x7584b0 (reader), writer 0x77d160
AchComplete = ["u32", "u8"]                                    # 0x758720 (Season 3 element)
EquipElementParam = ["u8", "u32", "u16"]                       # 0x765a90
AddStatusParam = ["u8", "u8", "u16", "u16"]                    # 0x765ba0
EquipStatParam = ["u8", "u16"]                                 # 0x766210
EquipItemInfo = ["u32", "u8", "u8", "u16", "u8", "u8", L(EquipElementParam), L(AddStatusParam),
                 L(EquipStatParam)]                            # 0x766070 (list 0x765fb0)
PS4_EquipItemInfo = ["u8", "u8", "u32", "u8", "u8", L(["u8", "u32"])]
S2CCharEquipInfo = ["str", "u8", "u8"]                         # 0x7776e0 (writer 0x77d2d0 same shape)
EquipJobItem = ["u32", "u8"]                                   # 0x766120
PawnEquipInfo = ["u32", L(S2CCharEquipInfo), L(EquipJobItem)]  # 0x7777e0
ItemEquipElement = ["str", L(EquipElementParam)]               # 0x76aad0
PS4_ItemEquipElement = ["str", L(["u8", "u32"])]
JobEquipStat = ["u8", L(EquipStatParam)]                       # 0x765f70 (Season 3)
NormalSkillParam = ["u8", "u32", "u32", "u32"]                 # 0x76f820
SetAcquirementParam = ["u8", "u8", "u8", "u32", "u8"]          # 0x777f10
GoodsRequirement = ["u32", "u32", "bool", "u32", "bool", "u32", "u32", "u32", "u32", "u32", "s64",
                    "s64"]                                     # 0x778770, element 0x7788a0
Goods = ["u32", "u32", "u32", "u8", "bool", "s64", "s64", L(GoodsRequirement)]  # 0x769330 / 0x769450
PS4_Goods = ["u32"] * 6
OrbGainExtendParam = ["u16"] * 13                              # 0x7701c0
GachaItemInfo = ["u32", "u32", "u32", "u32", "f64"]            # 0x7685e0
GachaSettlement = ["u32"] * 9                                  # 0x768720, element 0x768830 (Season 3)
PS4_GachaSettlement = ["u32"] * 8
GachaDrawInfo = ["u32", "bool", L(GachaItemInfo)]              # 0x768310


def gacha_info(settlement):
    group = [L(settlement), L(GachaDrawInfo)]                  # 0x7681e0
    return ["u32", "s64", "s64", "str", "str", "str", "u8", "str", "str", "str", "str", L(group)]  # 0x7684f0


LoadingInfoSchedule = ["str", "u32", "u32", "s64", "s64"]      # 0x76d550
Opaque29_23 = ["u32", L(["u32", "u32", "u32", "u8", "u32", "u8"])]  # capture shape only (I)

RES = "res"    # s32 Error; if 0: s32 Result + body
NTC = "ntc"    # S2C notice, no header
REQ = "req"    # C2S, source 0x00

IDS = {
    # id: (kind, body, {variant: body}, tally indices)
    "19.1.1": (REQ, ["u32", "u8"], {"ps4": ["u8"]}, (0, 1)),
    "19.2.1": (REQ, ["u32", "u8"], {"ps4": ["u8"]}, (0, 1)),
    "19.28.1": (REQ, [], {}, ()),
    "19.28.2": (RES, [L(NormalSkillParam), L(SetAcquirementParam), L(SetAcquirementParam)], {}, (0, 1, 2)),
    "20.0.1": (REQ, ["u32"], {}, (0,)),
    "20.0.2": (RES, ["u32", "u8", "u8", L(Goods)], {"ps4": [L(PS4_Goods)]}, (0, 1, 2, 3)),
    "20.1.1": (REQ, ["u32", "u32", "u8", "u32"], {}, (2,)),
    "20.1.2": (RES, ["u8"], {"ps4": ["u8", "u32"]}, (0,)),
    "25.5.1": (REQ, [], {}, ()),
    "25.5.2": (RES, [OrbGainExtendParam], {}, ()),
    "27.0.1": (REQ, [], {}, ()),
    "27.0.2": (RES, [L(AchProgress)], {}, (0,)),
    "27.1.1": (REQ, [], {}, ()),
    "27.1.2": (RES, [L(AchRewardProgress)], {}, (0,)),
    "27.2.1": (REQ, [], {}, ()),
    "27.2.2": (RES, [L(AchFurnitureReward)], {}, (0,)),
    "27.3.1": (REQ, [], {}, ()),
    "27.3.2": (RES, [L(AchRewardCommon)], {}, (0,)),
    "27.4.1": (REQ, [L(AchRewardCommon)], {}, (0,)),
    "27.4.2": (RES, [L(AchRewardCommon), L(AchRewardCommon)], {}, (0, 1)),
    "27.8.16": (NTC, [L(AchComplete)], {"ps4": [L("u32")], "ps4frame": ["u16", L(AchComplete)]}, (0,)),
    "27.9.16": (NTC, [L(AchRewardCommon)], {"ps4frame": ["u16", L(AchRewardCommon)]}, (0,)),
    "27.10.1": (REQ, ["u8"], {}, (0,)),
    "27.10.2": (RES, [L(AchProgress)], {}, (0,)),
    "29.0.1": (REQ, [], {}, ()),
    "29.0.2": (RES, [L(S2CCharEquipInfo), L(EquipJobItem), L(PawnEquipInfo)], {}, (0, 1, 2)),
    "29.1.1": (REQ, [L(S2CCharEquipInfo)], {}, (0,)),
    "29.1.2": (RES, [L(S2CCharEquipInfo), JobEquipStat], {"ps4": [L(S2CCharEquipInfo)]}, (0,)),
    "29.2.1": (REQ, [L(S2CCharEquipInfo)], {}, (0,)),
    "29.2.2": (RES, [L(S2CCharEquipInfo), JobEquipStat], {"ps4": [L(S2CCharEquipInfo)]}, (0,)),
    "29.15.1": (REQ, [], {}, ()),
    "29.15.2": (RES, [L(ItemEquipElement)], {"ps4": [L(PS4_ItemEquipElement)]}, (0,)),
    "29.17.16": (NTC, ["u32", "u8", L(EquipItemInfo), L(EquipItemInfo)],
                 {"ps4": ["u32", "u8", L(PS4_EquipItemInfo), L(PS4_EquipItemInfo)],
                  "ps4frame": ["u16", "u32", "u8", L(EquipItemInfo), L(EquipItemInfo)]}, (1, 2, 3)),
    "29.23.16": (NTC, Opaque29_23, {}, (0, 1)),
    "39.0.1": (REQ, [], {}, ()),
    "39.0.2": (RES, [L(gacha_info(GachaSettlement))], {"ps4": [L(gacha_info(PS4_GachaSettlement))]}, (0,)),
    "39.1.1": (REQ, ["u32", "u32", "u32", "u32"], {}, ()),
    "39.1.2": (RES, ["u32", L(GachaItemInfo)], {}, (1,)),
    "43.0.1": (REQ, [], {}, ()),
    "43.0.2": (RES, [L(LoadingInfoSchedule)], {}, (0,)),
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


EXTRA = defaultdict(Counter)


def extra(key, val):
    if val is None:
        return
    if key == "27.8.16":
        for e in val[0]:
            EXTRA["27.8.16 element u8"][e[1]] += 1
    if key in ("19.1.1", "19.2.1"):
        EXTRA[key + " (u32, Job)"][tuple(val)] += 1
    if key == "20.0.2":
        for g in val[3]:
            EXTRA["20.0.2 goods (u8, bool, reqs)"][(g[3], g[4], len(g[7]))] += 1
            for q in g[7]:
                EXTRA["20.0.2 requirement (u32_1, bool, bool)"][(q[1], q[2], q[4])] += 1
    if key in ("29.1.2", "29.2.2"):
        EXTRA[key + " JobEquipStat (u8, n)"][(val[1][0], len(val[1][1]))] += 1
    if key == "29.17.16":
        EXTRA["29.17.16 Job"][val[1]] += 1
    if key == "29.15.2":
        for e in val[0]:
            EXTRA["29.15.2 element params"][len(e[1])] += 1
    if key == "39.0.2":
        for gi in val[0]:
            for grp in gi[11]:
                for s in grp[0]:
                    EXTRA["39.0.2 settlement u32_8"][s[8]] += 1
    if key == "29.23.16":
        EXTRA["29.23.16 (u32, elements)"][(val[0], tuple(tuple(e) for e in val[1]))] += 1
    if key == "20.1.2":
        EXTRA["20.1.2 u8"][val[0]] += 1


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
                        extra(key, val)
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
    for k, c in EXTRA.items():
        print("%s: %d distinct; %s" % (k, len(c), dict(c.most_common(12))))


if __name__ == "__main__":
    walk()

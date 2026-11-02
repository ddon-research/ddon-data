"""006 T013 capture walk: groups 9, 15, 18, 30, 34, 41, 51, 52, 54, 57, 63 (client 03040008).

Run from D:/ddon-data:  python -X utf8 -I specs/006-packet-pattern-coverage/research/T013-walk.py
Stdlib only. Reads packets/decrypted_raw/*/<n>_<NAME>_<time>.<g>_<id>_<sub>; writes nothing.

Header: u8 group, u16 id, u8 sub, u8 source (0x00 C2S, 0x34 S2C), u32 (header word); body from 0x09.
Fit: decode ends within the last 15 bytes of the file (cipher padding), no overrun.
Layouts are the PC 03040008 readers/writers of the T013 report (big-endian). Counter-tests
("ps4:" variants) are the PS4 02020005 bodies with PC framing; "ps4frame:" adds the PS4 u16 error
first on NTCs. "tally" prints the distinct values of the named top-level fields (lists: length).
15.0.16, 15.1.16 and 63.5.16 are client-written notices (source 0x00).
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
CraftPawnInfo = ["u32", "str"]                                   # list 0x760870
CraftProgress = ["u32", "str", L(CraftPawnInfo), L("u32"), "u32", "u32", "s32", "u32", "u32", "u16",
                 "u32", "bool", "u32"]                           # 0x760c20 (list loc 0x760b60)
PS4_CraftProgress = ["u32", "str", L(CraftPawnInfo), "u32", "u32", "s32", "u32", "u32", "u32", "bool", "u32"]
CraftPawnList = ["u32", "u32", "u32", "u32"]                     # list 0x760960
PawnCraftSkill = ["u8", "u32"]                                   # list 0x771c80
CraftTimeSaveCost = ["u8", "u8", "u32", "u32"]                   # list 0x7611f0
CraftS3Pawn = ["u32", "u8", "u32", "u32", "str", "u32", L(PawnCraftSkill)]  # 0x77ace0 (list 0x77abd0)
CraftS3Elem = ["u32", "u32", "u32", "u32", "u32", "bool"]        # 0x760ea0 (list 0x760db0)
CraftSettingPS4 = [L("u32"), L(CraftTimeSaveCost), "u32", "u32", "u8"]
CraftSetting = CraftSettingPS4 + [L(CraftS3Pawn), "u32", "u32", L(CraftS3Elem)]  # 0x760f20
CraftSkillRate = ["u8", "u8", "u8"]                              # list 0x7610f0
EntryBoardS = ["u64", "u16", "u16", "u16", "u16", "u16", "bool", "u32"]  # 0x7652c0 (list loc 0x7651d0)
SearchParam = [L("u8"), "str", "str", "bool", "u32", "u32", "u32", "bool", "u32", "u32", "u32", "u32"]  # 0x77f170
PS4_SearchParam = SearchParam[:10]
RecruitData = ["u16", "u32", L("u8")]                            # 0x765750 / writer 0x77f340
PS4_RecruitData = ["u16", L("u8")]
ItemParamHead = ["bool", "bool", "s32", "s32", "u16", "u8", "u32", "u16", "u16", "str"]
EntryItemParam = ItemParamHead + [L(RecruitData)]                # 0x7654b0 / writer 0x77f260
PS4_EntryItemParam = ItemParamHead + [L(PS4_RecruitData)]
CharListElement = ["u32", "str", "str", "str", "u16", "u8", "u8", "u8", "u8", "u8", "str", "u8"]  # 0x75ccf0
PS4_CharListElement = CharListElement[:-1]
MemberData = ["u16", "bool", "u32", CharListElement]             # 0x7656f0 (list 0x765590)
PS4_MemberData = ["u16", "bool", PS4_CharListElement]
EntryItem = ["u32", EntryItemParam, L(MemberData), "u16", "u16", "u32", "bool"]  # 0x765420
PS4_EntryItem = ["u32", PS4_EntryItemParam, L(PS4_MemberData), "u16", "u16", "u32"]
EditInfo = ["u8", "u8", "u16"] + ["u8"] * 18 + ["u16"] * 50       # Write_CDataEditInfo_ 0x77eb40
WalletPoint = ["u8", "u32"]                                      # list 0x77c5a0
ShopPrice = ["u8", L(WalletPoint)]                               # list 0x764d70
DispelCategory = ["u32", "str"]                                  # list 0x763390
CraftMaterial = ["u32", "u32", "u32", "bool"]                    # list 0x76dee0
CraftRecipe = ["u32"] * 7 + ["s32", "bool", L(CraftMaterial)]    # 0x76e130 (list loc 0x76e000)
PS4_CraftRecipe = ["u32"] * 7 + ["s32", "bool", L(["u32", "u32", "u32"])]
LayoutSet = ["u32", "u8", "u32", "u32"]                          # list 0x762c50
Announce63 = ["u8", "u32", "str"]                                # list loc 0x762b40

RES = "res"    # s32 Error; if 0: s32 Result + body
NTC = "ntc"    # S2C notice, no header
REQ = "req"    # C2S, source 0x00

IDS = {
    # id: (kind, body, {variant: body}, tally indices)
    "9.1.2": (RES, [], {}, ()),
    "15.0.16": (REQ, [], {}, ()),
    "15.1.16": (REQ, [], {}, ()),
    "18.0.1": (REQ, ["u64"], {}, (0,)),
    "30.0.1": (REQ, [], {}, ()),
    "30.0.2": (RES, [L(CraftProgress), L(CraftPawnList), L("u32")],
               {"ps4": [L(PS4_CraftProgress), L(CraftPawnList), L("u32")]}, (0, 1, 2)),
    "30.10.1": (REQ, ["u32", "u32", "u32"], {}, (1, 2)),
    "30.10.2": (RES, ["u32"] * 5, {}, (1, 2)),
    "30.12.1": (REQ, ["u32"], {}, ()),
    "30.12.2": (RES, ["u32", L(PawnCraftSkill), "u32"], {}, (1, 2)),
    "30.13.1": (REQ, [], {}, ()),
    "30.13.2": (RES, CraftSetting, {"ps4": CraftSettingPS4}, (0, 1, 2, 3, 4, 5, 6, 7, 8)),
    "30.15.1": (REQ, [], {}, ()),
    "30.15.2": (RES, [L(CraftSkillRate)], {}, (0,)),
    "34.0.1": (REQ, [L("u64")], {}, (0,)),
    "34.0.2": (RES, [L(EntryBoardS)], {}, (0,)),
    "34.1.1": (REQ, ["u64", "u32", "u32", SearchParam], {"ps4": ["u64", "u32", "u32", PS4_SearchParam]}, (0, 1, 2)),
    "34.1.2": (RES, ["u64", L(EntryItem)], {"ps4": ["u64", L(PS4_EntryItem)]}, (0, 1)),
    "34.2.1": (REQ, ["u64", "str", EntryItemParam], {"ps4": ["u64", "str", PS4_EntryItemParam]}, (0,)),
    "34.2.2": (RES, ["u64", EntryItem], {"ps4": ["u64", PS4_EntryItem]}, (0,)),
    "34.6.1": (REQ, [], {}, ()),
    "34.6.2": (RES, [], {}, ()),
    "34.6.16": (NTC, ["u32", "u16"], {"ps4frame": ["u16", "u32", "u16"]}, (0, 1)),
    "34.7.1": (REQ, [], {}, ()),
    "34.7.2": (RES, [], {}, ()),
    "34.14.16": (NTC, ["bool", MemberData], {"ps4": ["bool", PS4_MemberData],
                                             "ps4frame": ["u16", "bool", MemberData]}, (0,)),
    "34.16.16": (NTC, ["u32", "u32"], {"ps4frame": ["u16", "u32", "u32"]}, (0, 1)),
    "41.3.1": (REQ, ["u8", "u8", WalletPoint, EditInfo], {"ps4": ["u8", "u8", EditInfo]}, (0, 1, 2)),
    "41.3.2": (RES, [], {"ps4": ["u32"]}, ()),
    "41.5.1": (REQ, ["u8", "u8", "u32", EditInfo, "str"], {}, (0, 1, 2, 4)),
    "41.5.2": (RES, [], {}, ()),
    "41.8.1": (REQ, [], {}, ()),
    "41.8.2": (RES, [L(ShopPrice)], {}, (0,)),
    "51.0.1": (REQ, ["u8"], {}, (0,)),
    "51.2.1": (REQ, ["u32"], {"ps4": []}, (0,)),
    "51.2.2": (RES, [L(DispelCategory), "bool"], {"ps4": [L(["u8", "str"])]}, (0, 1)),
    "52.1.1": (REQ, [], {}, ()),
    "54.0.1": (REQ, ["u8", "u32", "s32"], {}, (0, 1, 2)),
    "54.0.2": (RES, ["u8", L(CraftRecipe), "bool"], {"ps4": ["u8", L(PS4_CraftRecipe), "bool"]}, (0, 1, 2)),
    "57.0.1": (REQ, [], {}, ()),
    "63.0.16": (NTC, ["u32"], {}, (0,)),
    "63.1.16": (NTC, ["u32"], {}, (0,)),
    "63.2.16": (NTC, ["bool", "u8", "u32", "u32", "u32", "u32", L(Announce63)], {}, (0, 1, 2, 3, 4, 5, 6)),
    "63.3.16": (NTC, [], {}, ()),
    "63.5.16": (REQ, [], {}, ()),
    "63.6.16": (NTC, [L(LayoutSet)], {}, (0,)),
    "63.7.16": (NTC, [L(LayoutSet)], {}, (0,)),
    "63.10.16": (NTC, ["u32", "str", "u8"], {}, (0, 2)),
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


def extra(key, b, val):
    hdr = struct.unpack(">I", b[5:9])[0]
    if key.startswith("63.") or key in ("34.6.16", "34.16.16"):
        EXTRA[key + " header u32"][hdr] += 1
    if val is None:
        return
    if key == "30.0.2":
        for e in val[0]:
            EXTRA["30.0.2 progress (S3 u32 list len, u16, u32 after ToppingID?)"][(len(e[3]), e[9])] += 1
    if key == "30.13.2":
        for p in val[5]:
            EXTRA["30.13.2 S3 pawn (u32, u8, u32, u32, str, u32, n)"][tuple(p[:6]) + (len(p[6]),)] += 1
        for e in val[8]:
            EXTRA["30.13.2 S3 element"][tuple(e)] += 1
        EXTRA["30.13.2 S3 u32 pair"][(val[6], val[7])] += 1
    if key in ("34.1.2", "34.2.2"):
        items = val[1] if key == "34.1.2" else [val[1]]
        for it in items:
            EXTRA["34.x item tail (u16, u16, u32, bool)"][tuple(it[3:7])] += 1
            for rcd in it[1][10]:
                EXTRA["34.x recruit (u16, u32, jobs)"][(rcd[0], rcd[1], len(rcd[2]))] += 1
            for m in it[2]:
                EXTRA["34.x member (u16, bool, u32, charId, u8 tail)"][(m[0], m[1], m[2], m[3][0], m[3][11])] += 1
    if key == "34.2.1":
        for rcd in val[2][10]:
            EXTRA["34.2.1 recruit (u16, u32, jobs)"][(rcd[0], rcd[1], len(rcd[2]))] += 1
    if key == "34.1.1":
        EXTRA["34.1.1 search tail (u32 x4 after IsNoPassword)"][tuple(val[3][8:12])] += 1
    if key == "34.14.16":
        m = val[1]
        EXTRA["34.14.16 (EntryFlag, id, ready, u32, charId)"][(val[0], m[0], m[1], m[2], m[3][0])] += 1
    if key == "41.3.1":
        EXTRA["41.3.1 (slot, type, wallet u8, u32)"][(val[0], val[1], val[2][0], val[2][1])] += 1
    if key == "41.5.1":
        EXTRA["41.5.1 (u8, u8, u32, str)"][(val[0], val[1], val[2], val[4])] += 1
    if key == "41.8.2":
        EXTRA["41.8.2 prices"][tuple((e[0], tuple(tuple(w) for w in e[1])) for e in val[0])] += 1
    if key == "51.2.2":
        EXTRA["51.2.2 categories"][tuple(tuple(e) for e in val[0])] += 1
    if key == "54.0.2":
        for rc in val[1]:
            for mt in rc[9]:
                EXTRA["54.0.2 material bool"][mt[3]] += 1
    if key in ("63.6.16", "63.7.16"):
        for e in val[0]:
            EXTRA[key + " element"][tuple(e)] += 1
    if key == "63.2.16":
        for e in val[6]:
            EXTRA["63.2.16 element (u8, u32)"][(e[0], e[1])] += 1
        EXTRA["63.2.16 head"][tuple(val[:6])] += 1
    if key == "63.10.16":
        EXTRA["63.10.16 (u32, str, u8)"][tuple(val)] += 1


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
                    extra(key, b, val)
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
    for k, c in EXTRA.items():
        print("%s: %d distinct; %s" % (k, len(c), dict(c.most_common(12))))


if __name__ == "__main__":
    walk()

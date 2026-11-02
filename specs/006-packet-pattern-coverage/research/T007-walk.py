"""006 T007 capture walk: groups 8 PAWN, 58 PAWN_EXPEDITION, 53 PARTNER_PAWN (client 03040008).

Run from D:/ddon-data:  python -X utf8 -I specs/006-packet-pattern-coverage/research/T007-walk.py
Stdlib only. Reads packets/decrypted_raw/*/<n>_<NAME>_<time>.<g>_<id>_<sub>; writes nothing.

Header: u8 group, u16 id, u8 sub, u8 source (0x00 C2S, 0x34 S2C), 4 bytes; body from 0x09.
Fit: decode ends within the last 15 bytes of the file (cipher padding), no overrun.
Layouts are the PC 03040008 readers/writers of the T007 report (big-endian). Counter-tests
("ps4:" variants) are the PS4 02020005 bodies with PC framing; "ps4frame:" adds the PS4 u16 error
first on NTCs.
"""
import hashlib
import os
import re
import struct
import sys
from collections import defaultdict

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


def rd(r, t, path="", out=None):
    """t: prim name | 'str' | ('list', T) | ('arr', n, T) | [T, ...] (struct). Returns decoded value."""
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
    return [rd(r, x, "%s.%d" % (path, i)) for i, x in enumerate(t)]


def L(t):
    return ("list", t)


def A(n, t):
    return ("arr", n, t)


# --- shared PC 03040008 structures (VAs in the report) ---
CraftSkill = ["u8", "u32"]                                    # 0x771c80
PawnListData = ["u8", "u32", "u32", L(CraftSkill), "u32", "u64"]  # 0x772750
PartnerPawnData = ["u32", "u32", "u8"]                        # 0x7710a0
PawnListElem = ["s32", "u32", "str", "u8", "u8", "u8", PawnListData, "u32", "u32", "u32"]  # 0x772680
RentedPawn = ["s32", "u32", "str", "u8", "u8", "u8", "u8", PawnListData, "u8"]              # 0x776da0
LostPawn = ["s32", "u32", "str", "u8", "u8", "u8", "u32", PawnListData]                    # 0x76da40
CommBase = ["u32", "str", "str", "str"]                       # 0x75ecf0
Feedback = ["u8", "u8", "u8"]                                 # 0x771fd0 / 0x771ed0
PawnHistory = ["u32", CommBase, "u64", "u64", "u8", "u8", "u32", Feedback]  # 0x7720e0
ArisenProfile = ["u8", "u32", "u32", "u16", "u32"]            # 0x7596f0
PawnProfile = [CommBase, ArisenProfile, "str", "u32"]         # 0x7727d0
TotalScore = ["u32", "u32", "u32", L(Feedback)]               # 0x772a40
OrbPage = ["u8", L(["u8", "u8"])]                             # 0x7702d0 / 0x76fe50
JobOrbTree = ["u8", "bool", "f32"]                            # 0x76c270
JobData = ["u8", "u32", "u32", "u32", A(10, "u16"), A(30, "u8")]  # 0x75c770
EditInfo = ["u8", "u8", "u16", A(18, "u8"), A(50, "u16")]     # 0x764550 (122 B)
EquipItemInfo = ["u32", "u8", "u8", "u16", "u8", "u8", L(["u8", "u32", "u16"]),
                 L(["u8", "u8", "u16", "u16"]), L(["u8", "u16"])]  # 0x766070
CharEquipData = [L(EquipItemInfo)]                            # 0x765fb0
PawnInfo = ["u32", "str", EditInfo, "u8", "u32", "u32", "u8", L(JobData), L(CharEquipData),
            L(CharEquipData), L(["u32", "u8"]), "u8", L(["u8", "u16"]),
            ["u32", "u32", "u32", "u32", L(CraftSkill)], L(["u8", "u32"]),
            "bool", "bool", "u8", "u8", "u8", "u8", L(["u8"]), L(["u8", "u32", "u8"]),
            L(["u8", "u32", "u8"]), "u32", A(13, "u16"), "u8", "u8", "u32",
            A(64, "u8"), A(5, "u32"), L(["u8", "u8"])]        # 0x772180
CharListElem = [CommBase, "u16", "u8", ["u8", "u8"], ["u8", "u8"], "str", "u8"]  # 0x75ccf0
PartyMember = [CharListElem, "u8", "s32", "u32", "bool", "bool", "bool", "u8", A(8, "u8"), "u8"]  # 0x771580

# --- PS4 02020005 variants for counter-tests ---
PS4_PawnListElem = ["s32", "u32", "str", "u8", "u8", "u8", PawnListData]
PS4_EquipItemInfo = ["u8", "u8", "u32", "u8", "u8", L(["u8", "u32"])]
PS4_PawnInfo = ["u32", "str", EditInfo, "u8", "u32", "u32", "u8", L(JobData), L([L(PS4_EquipItemInfo)]),
                L([L(PS4_EquipItemInfo)]), L(["u32", "u8"]), "u8",
                ["u32", "u32", "u32", "u32", L(CraftSkill)], L(["u8", "u32"]),
                "bool", "bool", "u8", "u8", "u8", "u8", L(["u8"]), L(["u8", "u32", "u8"]),
                L(["u8", "u32", "u8"]), "u32", A(13, "u16"), "u8", "u8", "u32"]
PS4_CharListElem = CharListElem[:-1]
PS4_PartyMember = [PS4_CharListElem] + PartyMember[1:]

RES = "res"  # s32 Error; if 0: s32 Result + body
NTC = "ntc"
REQ = "req"

IDS = {
    # id: (kind, body, {variant: body})
    "8.2.1": (REQ, [], {}),
    "8.2.2": (RES, [L(PawnListElem), PartnerPawnData], {"ps4": [L(PS4_PawnListElem), PartnerPawnData]}),
    "8.3.1": (REQ, ["u8", "s32"], {}),
    "8.3.2": (RES, ["u32", PawnInfo], {"ps4": ["u32", PS4_PawnInfo]}),
    "8.8.1": (REQ, [], {}),
    "8.8.2": (RES, [L(RentedPawn)], {}),
    "8.9.1": (REQ, ["u8", "s32"], {}),
    "8.9.2": (RES, ["u32", PawnInfo], {"ps4": ["u32", PS4_PawnInfo]}),
    "8.12.1": (REQ, ["u8"], {}),
    "8.12.2": (RES, [], {}),
    "8.20.1": (REQ, [], {}),
    "8.20.2": (RES, [L(LostPawn)], {}),
    "8.28.1": (REQ, ["u32"], {}),
    "8.28.2": (RES, [L(PawnHistory)], {}),
    "8.30.1": (REQ, [], {}),
    "8.33.16": (NTC, ["u32", "u32", PawnProfile], {"ps4frame": ["u16", "u32", "u32", PawnProfile]}),
    "8.34.16": (NTC, ["u32", "u32", L(PawnHistory)], {"ps4frame": ["u16", "u32", "u32", L(PawnHistory)]}),
    "8.35.16": (NTC, ["u32", "u32", TotalScore], {"ps4frame": ["u16", "u32", "u32", TotalScore]}),
    "8.36.16": (NTC, ["u32", "u32", L(OrbPage), L(JobOrbTree), L(JobOrbTree)],
                {"ps4": ["u32", "u32", L(OrbPage), L(JobOrbTree)],
                 "ps4frame": ["u16", "u32", "u32", L(OrbPage), L(JobOrbTree)]}),
    "8.37.16": (NTC, [PartyMember], {"ps4": [PS4_PartyMember], "ps4frame": ["u16", PS4_PartyMember]}),
    "53.4.1": (REQ, [], {}),
    "53.4.2": (RES, [L(["u8", "u32", "u32"])], {}),
    "53.6.1": (REQ, [], {}),
    "53.6.2": (RES, [L(["u8", "u32", "u32"])], {}),
    "53.7.1": (REQ, [], {}),
    "53.7.2": (RES, ["u32", "bool"], {}),
    "53.8.1": (REQ, [L(["str", "u32"])], {}),
    "53.8.2": (RES, [PartnerPawnData], {}),
    "53.9.16": (NTC, ["u32"], {"ps4frame": ["u16", "u32"]}),
    "58.0.1": (REQ, [], {}),
    "58.0.2": (RES, ["u8", L(["u32"]), L(["u32", "u32"]), L(["u32"]), L(["u32", "u32", "u32"])], {}),
    "58.3.1": (REQ, ["u32", "u32"], {}),
    "58.3.2": (RES, [], {}),
    "58.4.1": (REQ, ["u8"], {}),
    "58.4.2": (RES, [], {}),
    "58.5.1": (REQ, [], {}),
    "58.5.2": (RES, [["u32", "u32"], "u8", L(["u32", "u32", "u32"]), "bool", "bool"],
               {"ps4": [["u32", "u32"], "u8", ["u32", "u32", "u32"], "bool"]}),
    "58.7.1": (REQ, [], {}),
    "58.7.2": (RES, ["u32", L(["u32"]), L(["u8"])], {}),
    "58.8.1": (REQ, ["u32"], {}),
    "58.8.2": (RES, ["u32", L(["u32", "u32", "u32", "u32", "bool"])],
               {"ps4": ["u32", L(["u32", "u32", "u32"])]}),
    "58.9.1": (REQ, ["u32", L(["u32", "u32"])], {}),
    "58.9.2": (RES, ["u32", L(["u32", "u32"]), "u8"], {}),
}

NAME_RE = re.compile(r"PAWN|PARTNER")


def decode(b, kind, body):
    r = R(b, 9)
    err = None
    if kind == RES:
        err = rd(r, "s32")
        if err == 0:
            rd(r, "s32")
            rd(r, body)
    else:
        rd(r, body)
    return r, err


def main():
    files = defaultdict(list)
    suffix_only = defaultdict(int)
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
                suffix_only[key] += 1
                if NAME_RE.search(f):
                    files[key].append(os.path.join(p, f))
    tot = hdr = fit = 0
    for key, (kind, body, variants) in IDS.items():
        g, i, s = (int(x) for x in key.split("."))
        fs = sorted(files[key])
        n = len(fs)
        ok_h = ok_f = 0
        slacks, errs = [], 0
        lists = defaultdict(int)
        var_fail = defaultdict(int)
        best = None
        for fp in fs:
            b = open(fp, "rb").read()
            src = 0x00 if kind == REQ else 0x34
            if len(b) >= 9 and b[0] == g and struct.unpack(">H", b[1:3])[0] == i and b[3] == s and b[4] == src:
                ok_h += 1
            try:
                r, err = decode(b, kind, body)
                sl = len(b) - r.p
                if 0 <= sl <= SLACK:
                    ok_f += 1
                    slacks.append(sl)
                    for k, v in r.lists.items():
                        lists[k] = max(lists[k], v)
                    if err:
                        errs += 1
                    score = (sum(r.lists.values()), len(b))
                    if best is None or score > best[0]:
                        best = (score, fp, len(b), r.p)
            except Overrun:
                pass
            for vn, vb in variants.items():
                try:
                    r2, _ = decode(b, kind, vb)
                    if not 0 <= len(b) - r2.p <= SLACK:
                        var_fail[vn] += 1
                except Overrun:
                    var_fail[vn] += 1
        tot += n
        hdr += ok_h
        fit += ok_f
        line = "%-8s files %4d (suffix-only %4d) header %4d fit %4d slack %s err!=0 %d" % (
            key, n, suffix_only[key], ok_h, ok_f,
            "%d-%d" % (min(slacks), max(slacks)) if slacks else "-", errs)
        print(line)
        for vn in variants:
            print("          counter %-9s fails %d/%d" % (vn, var_fail[vn], n))
        nonempty = {k: v for k, v in lists.items() if v}
        allpaths = sorted(lists)
        if allpaths:
            print("          lists max:", ", ".join("%s=%d" % (k or "/", lists[k]) for k in allpaths))
        if best:
            _, fp, size, end = best
            h = hashlib.sha256(open(fp, "rb").read()).hexdigest()[:16]
            print("          sample %s (%d B, %s) end 0x%x" % (os.path.relpath(fp, ROOT).replace("\\", "/"), size, h, end))
    print("TOTAL files %d header %d fit %d" % (tot, hdr, fit))


if __name__ == "__main__":
    sys.exit(main())

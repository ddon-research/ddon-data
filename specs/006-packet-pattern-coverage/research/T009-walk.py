"""006 T009 capture walk: groups 37 MAIL, 45 STAMP, 2 CHARACTER (client 03040008).

Run from D:/ddon-data:  python -X utf8 -I specs/006-packet-pattern-coverage/research/T009-walk.py
Stdlib only. Reads packets/decrypted_raw/*/<n>_<NAME>_<time>.<g>_<id>_<sub>; writes nothing.

Header: u8 group, u16 id, u8 sub, u8 source (0x00 C2S, 0x34 S2C), 4 bytes; body from 0x09.
Fit: decode ends within the last 15 bytes of the file (cipher padding), no overrun.
Layouts are the PC 03040008 readers/writers of the T009 report (big-endian). Counter-tests
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


PRIM = {"u8": ">B", "bool": ">B", "u16": ">H", "u32": ">I", "s32": ">i", "u64": ">Q", "s64": ">q",
        "f32": ">f"}


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
CommunityCharacterBaseInfo = ["u32", "str", "str", "str"]                 # 0x75ecf0
MailInfo = ["u64", "u8", "u8", CommunityCharacterBaseInfo, "str", "str", "s64"]  # 0x76e5a0
MailAttachmentList = [L(["u64", "bool", "u32", "u16"]),                  # 0x76e630 item
                      L(["u64", "bool", "u32", "u32"]),                  # 0x76e350 GP
                      L(["u64", "bool", "u32", "u32", "u32"]),           # 0x76e890 option course
                      L(["u64", "bool", "u32", "str"])]                  # 0x76e760 legend pawn
StampBonus = ["u32", "u32", "u32"]                                       # 0x77a380 element
StampBonusAsset = [L(StampBonus), "u16", "u8"]                           # 0x77a6b0 element
CharacterListElement = [CommunityCharacterBaseInfo, "u16", "u8", ["u8", "u8"], ["u8", "u8"],
                        "str", "u8"]                                     # 0x75ccf0
EquipItemInfo = ["u32", "u8", "u8", "u16", "u8", "u8", L(["u8", "u32", "u16"]),
                 L(["u8", "u8", "u16", "u16"]), L(["u8", "u16"])]        # 0x766070
CharacterJobData = ["u8", "u32", "u32", "u32", ("arr", 10, "u16"), ("raw", 30)]  # 0x75c770
StatusInfo = ["u32", "u32", "u8"] + ["u32"] * 9                          # 0x77a810
MatchingProfile = ["u8", "u32", "u8", "u32", "u32", "u32", "u32", "str", "bool"]  # 0x76ed10
ArisenProfile = ["u8", "u32", "u32", "u16", "u32"]                       # 0x7596f0


def character_info(s3_list=True):
    """PC 0x75c2a0 (s3_list=True); s3_list=False drops the Season 3 list 0x766210 (PS4 order)."""
    head = ["u32", "u32", "u32", "str", "str", ("raw", 122), StatusInfo, "u8",
            L(CharacterJobData), L(["u8", "u8", "u32"]), L([L(EquipItemInfo)]), L([L(EquipItemInfo)]),
            L(["u32", "u8"]), "u8"]
    s3 = [L(["u8", "u16"])] if s3_list else []
    tail = [L(["u8", "u16"]), L(["u8", "u32"]), "u8", "u8", L(["u8", L(["u8", "u8"])]),
            L(["u32", "str", L(["u32", "str", "u32", "bool"])]), L(["u32"] * 5 + ["u8"]),
            L(["u32", "u32", "u8", "u8", "u32"]), MatchingProfile, ArisenProfile,
            "bool", "bool", "bool", "bool", "u8", "u8"]
    return head + s3 + tail


# --- PS4 02020005 variants for counter-tests ---
PS4_StampAsset = [L(["u32", "u32"]), "u16", "u8"]
PS4_CharacterListElement = CharacterListElement[:-1]

RES = "res"    # s32 Error; if 0: s32 Result + body
NTC = "ntc"    # S2C notice, no header
REQ = "req"    # C2S, source 0x00

IDS = {
    # id: (kind, body, {variant: body}, tally indices)
    "2.0.1": (REQ, ["u32"], {}, ()),
    "2.0.2": (RES, ["u32", character_info(), "bool", ("raw", 1024), "u8"],
              {"ps4": ["u32", character_info(False), "bool", ("raw", 1024)],
               "nos3list": ["u32", character_info(False), "bool", ("raw", 1024), "u8"]}, (4,)),
    "2.5.16": (NTC, ["u8"], {"ps4frame": ["u16", "u8"]}, (0,)),
    "2.6.16": (NTC, [L("u32")], {"ps4frame": ["u16", L("u32")]}, ()),
    "2.7.16": (NTC, [L(CharacterListElement), L(["u32", "str"])],
               {"ps4": [L(PS4_CharacterListElement), L(["u32", "str"])],
                "ps4frame": ["u16", L(PS4_CharacterListElement), L(["u32", "str"])]}, ()),
    "2.12.1": (REQ, ["u32"], {}, (0,)),
    "2.12.2": (RES, [], {}, ()),
    "2.16.1": (REQ, ["u32"], {}, ()),
    "2.16.2": (RES, ["u8"], {}, ()),
    "2.18.1": (REQ, ["u32", "u32"], {"ps4": ["u32"]}, (1,)),
    "2.18.2": (RES, [], {}, ()),
    "2.24.1": (REQ, [], {}, ()),
    "2.24.2": (RES, ["u32"], {}, ()),
    "2.25.1": (REQ, [], {}, ()),
    "2.25.2": (RES, ["u8"], {}, ()),
    "2.27.16": (NTC, ["u32"], {"ps4frame": ["u16", "u32"]}, ()),
    "2.28.16": (NTC, [], {"ps4frame": ["u16"]}, ()),
    "2.29.16": (NTC, ["u32"], {"ps4frame": ["u16", "u32"]}, ()),
    "2.30.16": (NTC, ["u32"], {"ps4frame": ["u16", "u32"]}, ()),
    "2.31.16": (NTC, ["u32"], {"ps4frame": ["u16", "u32"]}, (0,)),
    "2.32.16": (NTC, [], {"ps4frame": ["u16"]}, ()),
    "2.38.1": (REQ, ["u8", "bool"], {}, ()),
    "2.38.2": (RES, ["u8"], {}, ()),
    "37.0.1": (REQ, [], {}, ()),
    "37.0.2": (RES, ["u32"], {}, ()),
    "37.1.1": (REQ, ["u32", "u32"], {}, ()),
    "37.1.2": (RES, [L(MailInfo)], {}, ()),
    "37.2.1": (REQ, [], {}, ()),
    "37.2.2": (RES, [], {}, ()),
    "37.6.1": (REQ, [], {}, ()),
    "37.6.2": (RES, ["u32"], {}, ()),
    "37.7.1": (REQ, ["u32", "u32"], {}, ()),
    "37.7.2": (RES, [L(MailInfo)], {}, ()),
    "37.8.1": (REQ, [], {}, ()),
    "37.8.2": (RES, [], {}, ()),
    "37.9.1": (REQ, ["u64"], {}, ()),
    "37.9.2": (RES, ["u64", "str"] + MailAttachmentList, {}, ()),
    "37.11.1": (REQ, ["u64", "u8"], {"ps4": ["u64"]}, (1,)),
    "37.11.2": (RES, ["u64"] + MailAttachmentList, {}, ()),
    "37.13.16": (NTC, MailInfo, {"ps4frame": ["u16"] + MailInfo}, ()),
    "45.0.1": (REQ, [], {}, ()),
    "45.0.2": (RES, [L(["u32", "u32", L(StampBonusAsset)]), "u16", L(StampBonusAsset)],
               {"ps4": ["u16", L(PS4_StampAsset), L(PS4_StampAsset)]}, ()),
    "45.1.1": (REQ, [], {}, ()),
    "45.1.2": (RES, [L(["u32", "u32"]), "u8", "u8"], {"ps4": ["u16", "u8", "u8"]}, ()),
    "45.3.1": (REQ, ["u32", "u32"], {"ps4": ["u8"]}, (0, 1)),
    "45.3.2": (RES, [], {}, ()),
    "45.4.1": (REQ, [], {"ps4": ["u8"]}, ()),
    "45.4.2": (RES, [], {}, ()),
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


if __name__ == "__main__":
    sys.exit(main())

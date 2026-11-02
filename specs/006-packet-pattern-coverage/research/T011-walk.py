"""006 T011 capture walk: groups 5, 6 PARTY, 16 FRIEND, 17 BLACK_LIST, 24 JOB_MASTER, 26 PROFILE
(client 03040008).

Run from D:/ddon-data:  python -X utf8 -I specs/006-packet-pattern-coverage/research/T011-walk.py
Stdlib only. Reads packets/decrypted_raw/*/<n>_<NAME>_<time>.<g>_<id>_<sub>; writes nothing.

Header: u8 group, u16 id, u8 sub, u8 source (0x00 C2S, 0x34 S2C), 4 bytes; body from 0x09.
Fit: decode ends within the last 15 bytes of the file (cipher padding), no overrun.
Layouts are the PC 03040008 readers/writers of the T011 report (big-endian). Counter-tests
("ps4:" variants) are the PS4 02020005 bodies with PC framing; "ps4frame:" adds the PS4 u16 error
first on NTCs. "tally" prints the distinct values of the named top-level fields (lists: length).
The extra block prints the distinct (JobID, flag, rate) entries of the 26.1.2 second
CDataJobOrbTreeStatus list and the 24.6.16 element tuples.
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
        "f32": ">f"}


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
CommunityBase = ["u32", "str", "str", "str"]                               # 0x75ecf0 / list 0x75ebc0
JobBase = ["u8", "u8"]                                                     # 0x76b190
CharListElem = [CommunityBase, "u16", "u8", JobBase, JobBase, "str", "u8"]  # 0x75ccf0 (S3 trailing u8)
PS4_CharListElem = CharListElem[:-1]
PartyMember = [CharListElem, "u8", "s32", "u32", "bool", "bool", "bool", "u8", ("raw", 8), "u8"]  # 0x771580
PS4_PartyMember = [PS4_CharListElem] + PartyMember[1:]
LobbyMember = [CommunityBase, "u32", "u8", "u8", "u8"]                     # 0x76d7f0 (list 0x76d6f0)
PS4_LobbyMember = LobbyMember + ["u8"]
FriendInfo = [CharListElem, "u8", "u32", "bool"]                           # list 0x766e20
PS4_FriendInfo = [PS4_CharListElem, "u8", "u32", "bool"]
HistoryElement = ["u8", "u32", "u32", "u64"]                               # list 0x7698c0
AchieveCategoryStatus = ["u8", "u16", "u16"]                               # list 0x7583b0
OrbPageStatus = ["u8", L(["u8", "u8"])]                                    # list 0x7702d0 (inner 0x76fe50)
JobOrbTreeStatus = ["u8", "bool", "f32"]                                   # list 0x76c270
ShortCut = ["u32", "u32", "u32", "u32", "u32", "u8"]                       # writer 0x780f20
CommunicationShortCut = ["u32", "u32", "u8", "u8", "u32"]                  # writer 0x77e0b0
JobMasterTarget = ["u8", "u32", "u8", "u8", "u32", "u32"]                  # list 0x76c500, element 0x76c5f0
PS4_JobOrderProgress = ["u8", "u32", "u32", "u32", "u32"]                  # PS4 Read_CDataJobOrderProgress_

RES = "res"    # s32 Error; if 0: s32 Result + body
NTC = "ntc"    # S2C notice, no header
REQ = "req"    # C2S, source 0x00

PROFILE = [L(HistoryElement), "str", "u32", L(AchieveCategoryStatus), L(OrbPageStatus),
           L(JobOrbTreeStatus), L(JobOrbTreeStatus)]

IDS = {
    # id: (kind, body, {variant: body}, tally indices)
    "5.2.16": (NTC, [L(LobbyMember)], {"ps4": [L(PS4_LobbyMember)], "ps4frame": ["u16", L(LobbyMember)]}, (0,)),
    "5.3.16": (NTC, [L("u32")], {"ps4frame": ["u16", L("u32")]}, (0,)),
    "6.0.1": (REQ, [], {}, ()),
    "6.0.2": (RES, ["u32", "u64"], {}, ()),
    "6.8.1": (REQ, ["u32"], {}, ()),
    "6.8.2": (RES, ["u8", "u64", "u32"], {}, (0,)),
    "6.8.16": (NTC, ["u32", "u32", L(PartyMember)],
               {"ps4": ["u32", "u32", L(PS4_PartyMember)], "ps4frame": ["u16", "u32", "u32", L(PartyMember)]}, (2,)),
    "6.10.1": (REQ, [], {}, ()),
    "6.10.2": (RES, [], {}, ()),
    "6.10.16": (NTC, ["u32"], {"ps4frame": ["u16", "u32"]}, ()),
    "6.15.1": (REQ, ["u8", "u8"], {}, (0, 1)),
    "6.15.2": (RES, [], {}, ()),
    "6.18.16": (NTC, ["u16", "u32", "u32", "u32", "u8"], {"ps4frame": ["u16", "u16", "u32", "u32", "u32", "u8"]},
                (0, 3, 4)),
    "16.0.1": (REQ, [], {}, ()),
    "16.0.2": (RES, [L(FriendInfo), L(CommunityBase), L(CommunityBase)],
               {"ps4": [L(PS4_FriendInfo), L(CommunityBase), L(CommunityBase)]}, (0, 1, 2)),
    "16.6.1": (REQ, [], {}, ()),
    "16.6.2": (RES, [L(CharListElem)], {"ps4": [L(PS4_CharListElem)]}, (0,)),
    "17.0.1": (REQ, [], {}, ()),
    "17.0.2": (RES, [L(CommunityBase)], {}, (0,)),
    "24.6.16": (NTC, [L(JobMasterTarget)], {"ps4": [L(PS4_JobOrderProgress)], "ps4frame": ["u16", L(JobMasterTarget)]},
                (0,)),
    "26.1.1": (REQ, [], {}, ()),
    "26.1.2": (RES, PROFILE, {"ps4": PROFILE[:-1]}, (0, 3, 4, 5, 6)),
    "26.12.1": (REQ, [L(ShortCut)], {}, (0,)),
    "26.12.2": (RES, [], {}, ()),
    "26.14.1": (REQ, [L(CommunicationShortCut)], {}, (0,)),
    "26.14.2": (RES, [], {}, ()),
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
    if key == "26.1.2":
        for e in val[6]:
            EXTRA["26.1.2 list7 (JobID, flag, rate)"][(e[0], e[1], round(e[2], 3))] += 1
        for e in val[5]:
            EXTRA["26.1.2 list6 (JobID, flag, rate)"][(e[0], e[1], round(e[2], 3))] += 1
    if key == "24.6.16":
        for e in val[0]:
            EXTRA["24.6.16 element"][tuple(e)] += 1
    if key == "6.8.16":
        for m in val[2]:
            EXTRA["6.8.16 CharListElem trailing u8"][m[0][-1]] += 1
    if key == "16.0.2":
        for m in val[0]:
            EXTRA["16.0.2 CharListElem trailing u8"][m[0][-1]] += 1
    if key == "5.2.16":
        for m in val[0]:
            EXTRA["5.2.16 (u8, SessionStatus, OnlineStatus)"][tuple(m[2:])] += 1


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

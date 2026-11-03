"""008 T003: independent stdlib walk of batches B5 and B2 (client 03040008).

usage (from D:/ddon-data):
  python -X utf8 -I specs/008-remaining-packets/research/t003/walk.py stats [id ...]
  python -X utf8 -I specs/008-remaining-packets/research/t003/walk.py check [id ...]
  python -X utf8 -I specs/008-remaining-packets/research/t003/walk.py fits [id ...]

stats: decode every raw file of each id (packets/decrypted_raw/*/*.<g>_<id>_<sub>) with the layout
below (the PC reader/writer width sequences of T001-triage.tsv, T002 for 70.0.1), report fit
(body from offset 9, no overrun, ends within the last 15 bytes), slack range, list counts and the
value histogram of every leaf field.
check: stratified sample of 2 files per id (smallest and largest raw file, by name order on ties):
decode the raw bytes here and compare every decoded leaf with the exported JSON
(packets/decrypted_json/<stream>/<file>.json, root `packet`); prints per-id match counts.
fits: per id, the exported JSON count with fits and sourceOk true against the raw count.
The field names are the pattern's names, so the comparison is leaf by leaf; the decoding logic
shares nothing with the ImHex pattern.
"""
import collections
import glob
import json
import os
import struct
import sys

SLACK = 15
RAW = os.path.join("packets", "decrypted_raw")
JSN = os.path.join("packets", "decrypted_json")

FMT = {"u8": ">B", "bool": ">B", "u16": ">H", "u32": ">I", "s32": ">i", "u64": ">Q", "s64": ">q"}


def L(name, *fields):
    return ("L", name, list(fields))


def S(name, *fields):
    return ("S", name, list(fields))


def LU32(name):  # MtTypedArray<u32>: entries are plain numbers
    return ("LU", name)


# ---- shared quest structures (include/Quest.hexpat) ----
WALLET = [("Type", "enum8"), ("Value", "u32")]
QEXP = [("unk_u8", "u8"), ("Type", "u8"), ("Value", "u32")]
REWARD = [("ItemId", "u32"), ("Num", "u16")]
COND = [("Type", "enum32"), ("Param01", "s32"), ("Param02", "s32")]
QLOG = [L("QuestAnnounceList", ("AnnounceNo", "u32")),
        L("QuestTalkInfoList", ("QuestId", "u32"), ("TalkNo", "u32"), ("NpcId", "u16"), ("IsOneOnly", "bool"))]
PWORK = [("CommandNo", "u32"), ("Work01", "s32"), ("Work02", "s32"), ("Work03", "s32"), ("Work04", "s32")]
QCMD = [("Command", "u16"), ("Param01", "s32"), ("Param02", "s32"), ("Param03", "s32"), ("Param04", "s32")]
QCHK = [("Command", "enum16"), ("Param01", "s32"), ("Param02", "s32"), ("Param03", "s32"), ("Param04", "s32")]
PSTATE = [("ProcessNo", "u16"), ("SequenceNo", "u16"), ("BlockNo", "u16"), L("WorkList", *PWORK),
          ("LL", "CheckCommandList", QCHK), L("ResultCommandList", *QCMD)]
ENEMY = [("GroupId", "u32"), ("unk_u32", "u32"), ("Lv", "u16"), ("IsPartyRecommend", "bool")]
LFSET = [("LayoutFlagNo", "u32"), L("SetInfoList", ("StageNo", "u32"), ("GroupId", "u32"))]
DELIV = [("ItemId", "u32"), ("Num", "u16"), ("MsgTagKey0", "u16"), ("MsgTagKey1", "u16")]

QUEST_LIST = [("KeyId", "u32"), ("QuestScheduleId", "u32"), ("QuestId", "u32"), ("BaseLevel", "u32"),
              ("ContentJoinItemRank", "u16"), L("BaseWalletPoint", *WALLET), L("BaseExp", *QEXP),
              ("OrderNpcId", "u32"), ("NameMsgId", "u32"), ("DetailMsgId", "u32"),
              ("DistributionStartDate", "u64"), ("EndDistributionDate", "u64"),
              L("FixedRewardItemList", *REWARD), L("FixedRewardSelectItemList", *REWARD),
              LU32("unk_u32_list"), L("QuestOrderConditionParamList", *COND), S("QuestLog", *QLOG),
              L("QuestFlagList", ("FlagId", "u32")), L("QuestLayoutFlagList", ("FlagId", "u32")),
              L("QuestProcessStateList", *PSTATE), L("QuestEnemyInfoList", *ENEMY),
              L("QuestLayoutFlagSetInfoList", *LFSET), L("DeliveryItemList", *DELIV), ("IsClientOrder", "bool")]

ORDER_LIST = [("KeyId", "u32"), ("QuestScheduleId", "u32"), ("QuestId", "u32"), ("AreaId", "u32"),
              ("BaseLevel", "u32"), ("ContentJoinItemRank", "u16"), L("BaseGold", *WALLET), L("BaseExp", *QEXP),
              ("OrderNpcId", "u32"), ("NameMsgId", "u32"), ("DetailMsgId", "u32"),
              ("DistributionStartDate", "u64"), ("OrderDate", "u64"), ("EndDistributionDate", "u64"),
              L("FixedRewardItemList", *REWARD), L("FixedRewardSelectItemList", *REWARD), LU32("unk_u32_list"),
              S("QuestLog", *QLOG), L("QuestFlagList", ("FlagId", "u32")),
              L("QuestLayoutFlagList", ("FlagId", "u32")), L("QuestProcessStateList", *PSTATE),
              L("QuestOrderConditionParamList", *COND), L("QuestEnemyInfoList", *ENEMY),
              L("QuestLayoutFlagSetInfoList", *LFSET), L("unk_u32_s64_list", ("TimerIdx", "u32"), ("EndTime", "s64")),
              L("DeliveryItemArray", *DELIV), ("IsClientOrder", "bool"), ("IsEnable", "bool"), ("CanProgress", "bool")]


def RES(*fields):
    return [("RES", list(fields))]


LAYOUTS = {
    "70.0.1": [L("ActionHistoryList", ("ActionType", "u8"), ("Num", "u32"))],
    "70.0.2": RES(),
    "60.0.2": RES(("NpcId", "u32"),
                  L("ExtendedMenuItemList", ("FunctionClass", "u32"), ("FunctionSelect", "u32"),
                    ("unk_u32_2", "u32"), ("unk_u32_3", "u32"), ("ShopId", "u32"), ("unk_u32_5", "u32"),
                    ("unk_bool", "bool"), ("str", "CustomLabel"), ("unk_u8", "u8"))),
    "11.121.1": [],
    "11.121.2": RES(L("LevelBonusList", ("unk_u32", "u32"),
                      L("BonusList", ("MinLevel", "u32"), ("MaxLevel", "u32"), ("GoldRatio", "u16"),
                        ("ExpRatio", "u16"), ("RimRatio", "u16"), ("AreaPointRatio", "u16")))),
    "11.123.1": [],
    "11.123.2": RES(("HasNotice", "bool")),
    "24.6.16": [L("TargetList", ("ReleaseType", "u8"), ("ReleaseId", "u32"), ("ReleaseLv", "u8"),
                  ("ConditionType", "u8"), ("TargetId", "u32"), ("TargetRank", "u32"))],
    "11.5.1": [("unk_u32", "u32")],
    "11.5.2": RES(("unk_u32", "u32"),
                  L("PackageQuestList", ("unk_u32", "u32"),
                    L("Details", ("unk_u32_0", "u32"), ("unk_s32_1", "s32"), ("unk_s32_2", "s32"),
                      L("unk_u32_list", ("m_unValue", "u32")), ("unk_bool_0", "bool"), ("unk_bool_1", "bool"),
                      L("QuestList", *QUEST_LIST)))),
    "28.24.16": [("unk_u32", "u32")],
    "14.11.16": [("StartPointId", "u32")],
    "11.122.1": [],
    "11.122.2": RES(L("QuestList", ("Category", "u8"), S("Param", *ORDER_LIST), ("Important", "bool"),
                      ("unk_bool", "bool"), ("QuestOrderBackgroundImage", "u32"))),
    "11.7.16": [L("MobHuntQuestListNum", ("unk_u32", "u32"), ("Num", "u8"))],
    "14.14.1": [],
    "14.14.2": RES(L("StartPointIdList", ("m_unValue", "u32"))),
    "28.34.1": [],
    "28.34.2": RES(("UpdateAppCourseBonusFlag", "bool")),
    "11.118.16": [("unk_u8", "u8")],
    "45.3.1": [("unk_u32_0", "u32"), ("unk_u32_1", "u32")],
    "45.3.2": RES(),
    "31.53.1": [],
    "31.53.2": RES(L("FurnitureLayouts", ("ItemID", "u32"), ("OmID", "u32"), ("LayoutID", "u8"))),
    "11.88.16": [],
    "61.2.1": [],
    "61.2.2": RES(("unk_u32", "u32"),
                  L("PreparationInfoList", ("PawnId", "u32"), ("unk_u32_1", "u32"), ("unk_u32_2", "u32"))),
    "64.0.1": [],
    "28.23.1": [("LineupId", "u32"), ("unk_u32_1", "u32"), ("unk_u32_2", "u32")],
    "28.23.2": RES(("CanBuy", "bool"), ("LineupId", "u32"), ("unk_u32_2", "u32"), ("unk_u32_3", "u32"),
                   ("unk_u32_4", "u32")),
    "11.68.16": [("unk_bool_0", "bool"), ("unk_bool_1", "bool"), ("Count", "u32")],
    "45.4.1": [],
    "45.4.2": RES(),
}

# The names above are the pattern's field names (check compares JSON leaves by them).


class Over(Exception):
    pass


class R:
    def __init__(self, b, p):
        self.b, self.p = b, p

    def get(self, fmt):
        n = struct.calcsize(fmt)
        if self.p + n > len(self.b):
            raise Over("overrun at %d" % self.p)
        v = struct.unpack(fmt, self.b[self.p:self.p + n])[0]
        self.p += n
        return v


def dec(r, lay, out, path, leaves):
    for t in lay:
        if t[0] == "RES":
            err = r.get(">i")
            out["Error"] = err
            leaves[path + "Error"].append(err)
            if err == 0:
                out["Result"] = r.get(">i")
                leaves[path + "Result"].append(out["Result"])
                dec(r, t[1], out, path, leaves)
        elif t[0] == "L":
            n = r.get(">I")
            if n > 5000:
                raise Over("count %d" % n)
            leaves[path + t[1] + "#"].append(n)
            ents = []
            for _ in range(n):
                e = {}
                dec(r, t[2], e, path + t[1] + ".", leaves)
                ents.append(e)
            out[t[1]] = {"count": n, "entries": ents}
        elif t[0] == "LU":
            n = r.get(">I")
            leaves[path + t[1] + "#"].append(n)
            ents = [r.get(">I") for _ in range(n)]
            for v in ents:
                leaves[path + t[1] + "[]"].append(v)
            out[t[1]] = {"count": n, "entries": ents}
        elif t[0] == "LL":
            n = r.get(">I")
            outer = []
            for _ in range(n):
                m = r.get(">I")
                inner = []
                for _ in range(m):
                    e = {}
                    dec(r, t[2], e, path + t[1] + ".", leaves)
                    inner.append(e)
                outer.append({"count": m, "entries": inner})
            out[t[1]] = {"count": n, "entries": outer}
        elif t[0] == "S":
            e = {}
            dec(r, t[2], e, path + t[1] + ".", leaves)
            out[t[1]] = e
        elif t[0] == "str":
            n = r.get(">H")
            if r.p + n > len(r.b):
                raise Over("string overrun")
            s = r.b[r.p:r.p + n].decode("utf-8", "replace")
            r.p += n
            out[t[1]] = {"length": n, "value": s}
            leaves[path + t[1]].append(s)
        else:
            name, typ = t
            fmt = FMT.get(typ, {"enum32": ">I", "enum16": ">H", "enum8": ">B"}.get(typ))
            v = r.get(fmt)
            out[name] = ("enum", v) if typ.startswith("enum") else (bool(v) if typ == "bool" else v)
            leaves[path + name].append(v)


def files_of(pid):
    g, i, s = pid.split(".")
    return sorted(glob.glob(os.path.join(RAW, "*", "*.%s_%s_%s" % (g, i, s))))


def walk(path, lay, leaves):
    with open(path, "rb") as f:
        b = f.read()
    r = R(b, 9)
    out = {}
    dec(r, lay, out, "", leaves)
    slack = len(b) - r.p
    return out, slack, b


def stats(ids):
    for pid in ids:
        fs = files_of(pid)
        leaves = collections.defaultdict(list)
        fit, slacks, bad = 0, collections.Counter(), []
        for f in fs:
            try:
                _, sl, _ = walk(f, LAYOUTS[pid], leaves)
                slacks[sl] += 1
                if sl <= SLACK:
                    fit += 1
                else:
                    bad.append((f, "slack %d" % sl))
            except Over as e:
                bad.append((f, str(e)))
        print("== %s files %d fit %d/%d slack %s" % (pid, len(fs), fit, len(fs), dict(sorted(slacks.items()))))
        for f, why in bad[:3]:
            print("   BAD", why, f)
        for k, vs in leaves.items():
            c = collections.Counter(vs)
            top = ", ".join("%r x%d" % (v, n) for v, n in c.most_common(8))
            print("   %-45s n=%d distinct=%d: %s" % (k, len(vs), len(c), top[:300]))


def cmp(a, j, path, res):
    if isinstance(a, dict):
        for k, v in a.items():
            if k not in j:
                res["miss"].append(path + k)
                continue
            cmp(v, j[k], path + k + ".", res)
    elif isinstance(a, list):
        if not isinstance(j, list) or len(j) != len(a):
            res["miss"].append(path + "[len]")
            return
        for i, (x, y) in enumerate(zip(a, j)):
            cmp(x, y, path + "%d." % i, res)
    elif isinstance(a, tuple):  # enum: JSON carries the name, the raw number is checked by the walk
        res["skip"] += 1
    else:
        if isinstance(a, bool):
            ok = (j is a) or (j == int(a))
        else:
            ok = j == a
        res["ok" if ok else "bad"] += 1 if ok else 0
        if not ok:
            res["badl"].append((path, a, j))
        else:
            pass


def check(ids):
    tot = 0
    for pid in ids:
        fs = files_of(pid)
        if not fs:
            print("== %s no raw files" % pid)
            continue
        by_size = sorted(fs, key=lambda f: (os.path.getsize(f), f))
        pick = [by_size[0]] if len(by_size) == 1 else [by_size[0], by_size[-1]]
        for f in pick:
            out, sl, _ = walk(f, LAYOUTS[pid], collections.defaultdict(list))
            jp = os.path.join(JSN, os.path.basename(os.path.dirname(f)), os.path.basename(f) + ".json")
            with open(jp, encoding="utf-8") as h:
                j = json.load(h)["packet"]
            res = {"ok": 0, "bad": 0, "skip": 0, "miss": [], "badl": []}
            cmp(out, j, "", res)
            ok = not res["miss"] and not res["badl"] and j.get("paddingSize") == sl and j.get("fits") is True
            tot += 0 if ok else 1
            print("== %s %s leaves ok %d bad %d enum-skipped %d missing %d slack walk %d json %s fits %s -> %s" % (
                pid, os.path.relpath(f, RAW), res["ok"], len(res["badl"]), res["skip"], len(res["miss"]), sl,
                j.get("paddingSize"), j.get("fits"), "MATCH" if ok else "DIFF"))
            for x in (res["miss"] + res["badl"])[:5]:
                print("   ", x)
    print("check: %d sample(s) differ" % tot)
    return tot


def fits(ids):
    """Count the exported JSON per id: files, fits and sourceOk true, slack values, .json.err files."""
    bad = 0
    for pid in ids:
        fs = files_of(pid)
        n = ok = err = 0
        sl = collections.Counter()
        for f in fs:
            jp = os.path.join(JSN, os.path.basename(os.path.dirname(f)), os.path.basename(f) + ".json")
            err += os.path.exists(jp + ".err")
            if not os.path.exists(jp):
                continue
            n += 1
            with open(jp, encoding="utf-8") as h:
                j = json.load(h)["packet"]
            if j.get("fits") is True and j.get("sourceOk") is True:
                ok += 1
                sl[j.get("paddingSize")] += 1
        bad += (ok != len(fs)) + err
        print("%-9s raw %4d json %4d fit+sourceOk %4d err %d slack %s" % (pid, len(fs), n, ok, err, sorted(sl)))
    print("fits: %d id(s) with a missing, unfit or failed file" % bad)
    return bad


def main():
    mode = sys.argv[1]
    ids = sys.argv[2:] or list(LAYOUTS)
    if mode == "stats":
        stats(ids)
    elif mode == "fits":
        sys.exit(1 if fits(ids) else 0)
    else:
        sys.exit(1 if check(ids) else 0)


if __name__ == "__main__":
    main()

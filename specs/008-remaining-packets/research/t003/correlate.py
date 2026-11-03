"""008 T003: value correlation for batch B5/B2 field names (client 03040008, stdlib only).

usage (from D:/ddon-data): python -X utf8 -I specs/008-remaining-packets/research/t003/correlate.py
Reads raw files with walk.py's layouts and, for the partner packets, the exported JSON of earlier
patterns (8.2.2 CDataPawnList, 14.14.2 is decoded here). Each check prints n/m with the rule.
"""
import collections
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import walk  # noqa: E402

RAW, JSN = walk.RAW, walk.JSN


def dec(pid):
    """[(stream, counter-ordered file index, decoded dict)] for every raw file of pid."""
    out = []
    for f in walk.files_of(pid):
        d, _, _ = walk.walk(f, walk.LAYOUTS[pid], collections.defaultdict(list))
        num = int(os.path.basename(f).split("_", 1)[0])
        out.append((os.path.basename(os.path.dirname(f)), num, d))
    return out


def cap(stream):
    """The capture a TCP stream belongs to (login and game streams of one session share it)."""
    return stream.split("_tcp-stream-")[0]


def pairs(req, res):
    """Pair each RES with the closest preceding REQ in the same stream (file number order)."""
    rq = collections.defaultdict(list)
    for s, n, d in dec(req):
        rq[s].append((n, d))
    got = []
    for s, n, d in dec(res):
        prev = [x for x in rq.get(s, []) if x[0] < n]
        if prev:
            got.append((max(prev, key=lambda x: x[0])[1], d))
    return got


def report(name, ok, tot, note=""):
    print("%-58s %d/%d %s" % (name, ok, tot, note))


def main():
    # 60.0.1 NpcID -> 60.0.2 NpcId (echo)
    p = pairs("60.0.1", "60.0.2")
    ok = sum(1 for q, r in p if r.get("NpcId") == q_npc(q))
    nz = [(q_npc(q), r.get("NpcId")) for q, r in p if r.get("NpcId")]
    report("60.0.2 NpcId == preceding 60.0.1 u32", ok, len(p), "nonzero RES pairs %s" % collections.Counter(nz))
    # 11.5.1 u32 -> 11.5.2 u32 (echo)
    p = pairs("11.5.1", "11.5.2")
    ok = sum(1 for q, r in p if r.get("unk_u32") == q["unk_u32"])
    report("11.5.2 unk_u32 == preceding 11.5.1 u32", ok, len(p))
    # 28.23.1 -> 28.23.2
    p = pairs("28.23.1", "28.23.2")
    report("28.23.2 LineupId == 28.23.1 field 1", sum(r["LineupId"] == q["LineupId"] for q, r in p), len(p))
    report("28.23.2 unk_u32_2 == 28.23.1 field 3", sum(r["unk_u32_2"] == q["unk_u32_2"] for q, r in p), len(p))
    report("28.23.2 unk_u32_2 == 28.23.1 field 2", sum(r["unk_u32_2"] == q["unk_u32_1"] for q, r in p), len(p))
    # 14.11.16 u32 in a 14.14.2 start point list of the same stream
    sp = collections.defaultdict(set)
    for s, n, d in dec("14.14.2"):
        for e in d.get("StartPointIdList", {}).get("entries", []):
            sp[cap(s)].add(e["m_unValue"])
    allsp = set().union(*sp.values()) if sp else set()
    rows = dec("14.11.16")
    same = sum(1 for s, n, d in rows if d["StartPointId"] in sp.get(cap(s), ()))
    anysp = sum(1 for s, n, d in rows if d["StartPointId"] in allsp)
    report("14.11.16 u32 in same-capture 14.14.2 StartPointIdList", same, len(rows),
           "(in any capture's list: %d; files whose capture has 14.14.2: %d; values %s)" % (
               anysp, sum(1 for s, n, d in rows if cap(s) in sp), collections.Counter(d["StartPointId"] for s, n, d in rows)))
    # 61.2.2 PawnId in 8.2.2 PawnList of the same stream; compare unk_u32_1/2 with CDataPawnList unks
    pl = collections.defaultdict(dict)
    for jf in glob.glob(os.path.join(JSN, "*", "*.8_2_2.json")):
        s = os.path.basename(os.path.dirname(jf))
        with open(jf, encoding="utf-8") as h:
            j = json.load(h)["packet"]
        for k, v in j.items():
            if isinstance(v, dict) and "entries" in v:
                for e in v["entries"]:
                    if isinstance(e, dict) and "PawnId" in e:
                        pl[s][e["PawnId"]] = e
    tot = ok = m1 = m2 = 0
    vals = collections.Counter()
    for s, n, d in dec("61.2.2"):
        for e in d.get("PreparationInfoList", {}).get("entries", []):
            tot += 1
            pe = pl.get(s, {}).get(e["PawnId"])
            if pe is not None:
                ok += 1
                m1 += pe.get("unk_u32_2") == e["unk_u32_1"]
                m2 += pe.get("unk_u32_0") == e["unk_u32_2"] or pe.get("unk_u32_1") == e["unk_u32_2"]
                vals[(e["unk_u32_1"], e["unk_u32_2"], pe.get("unk_u32_0"), pe.get("unk_u32_1"), pe.get("unk_u32_2"))] += 1
    report("61.2.2 PawnId in same-stream 8.2.2 pawn list", ok, tot)
    report("61.2.2 elem u32 #2 == that pawn's CDataPawnList.unk_u32_2", m1, ok)
    report("61.2.2 elem u32 #3 == that pawn's CDataPawnList.unk_u32_0 or _1", m2, ok)
    print("   (elem #2, elem #3, PawnList unk_u32_0, _1, _2):", dict(vals))


def q_npc(q):
    return q.get("NpcID")


if __name__ == "__main__":
    walk.LAYOUTS["60.0.1"] = [("NpcID", "u32")]
    main()

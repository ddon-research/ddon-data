"""008 T005: value correlation for batches B3, B7 and B6 (client 03040008).

usage (from D:/ddon-data): python -X utf8 -I specs/008-remaining-packets/research/t005/correlate.py
Decodes with t005/walk.py's layouts (the pattern's field names), pairs packets of one capture stream by
file sequence number, and checks values against client/03040008 extractor data:
base/etc/itemlist.ipa.json (ItemId), base/scr/stage_list.slt.json (StageId),
contents_buff/obj/pl/pl000000/param/etc/contents_buff_info.abl.json (AbilityId, ParamType).
Prints one line per check: name, matches/total, notes.
"""
import collections
import glob
import importlib.util
import json
import os
import re

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("t005walk", os.path.join(_here, "walk.py"))
w = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(w)
W = w.W
_cache = {}
C = os.path.join("client", "03040008")


def seq(f):
    return int(os.path.basename(f).split("_")[0])


def dec(pid):
    if pid not in _cache:
        out = []
        for f in W.files_of(pid):
            d, _, _ = W.walk(f, w.LAYOUTS[pid], collections.defaultdict(list))
            out.append((os.path.dirname(f), seq(f), d))
        _cache[pid] = out
    return _cache[pid]


def prev(items, stream, n):
    c = [x for x in items if x[0] == stream and x[1] < n]
    return max(c, key=lambda x: x[1])[2] if c else None


def near(items, stream, n):
    c = [x for x in items if x[0] == stream]
    return min(c, key=lambda x: abs(x[1] - n)) if c else None


def report(name, ok, tot, note=""):
    print("%-86s %d/%d %s" % (name, ok, tot, note))


def ents(d, *path):
    for p in path:
        d = d[p]
    return d["entries"]


def load_json(*p):
    with open(os.path.join(C, *p), encoding="utf-8") as h:
        return json.load(h)


def main():
    items = {}
    for v in load_json("base", "etc", "itemlist.ipa.json").values():
        if isinstance(v, list):
            for e in v:
                if isinstance(e, dict) and "ItemId" in e:
                    items[e["ItemId"]] = e.get("ItemCategoryName")
    stages = {}
    for e in re.findall(r'"StageId":(\d+),"StageName":\{"En":"([^"]*)"',
                        json.dumps(load_json("base", "scr", "stage_list.slt.json"), separators=(",", ":"))):
        stages[int(e[0])] = e[1]
    abl = {d["AbilityId"]: d for d in load_json("contents_buff", "obj", "pl", "pl000000", "param", "etc",
                                                "contents_buff_info.abl.json")["DataList"]}

    def item_check(name, vals):
        vals = list(vals)
        report(name + " in itemlist", sum(v in items for v in vals), len(vals),
               dict(collections.Counter(items.get(v, "MISSING") for v in vals).most_common(4)))

    # ---- 62.38.16 / 62.39.16 buffs ----
    b38, b39 = dec("62.38.16"), dec("62.39.16")
    els = [e for _, _, d in b38 for e in ents(d, "BuffEffectParamList")]
    report("62.38.16 BuffId is an AbilityId of contents_buff_info.abl",
           sum(e["BuffEffect"]["BuffId"] in abl for e in els), len(els))
    report("62.38.16 unk ParamType = ParamArray[0].ParamType of that AbilityId",
           sum(e["BuffEffect"]["BuffId"] in abl and abl[e["BuffEffect"]["BuffId"]]["ParamArray"]
               and abl[e["BuffEffect"]["BuffId"]]["ParamArray"][0]["ParamType"] == e["BuffEffect"]["ParamType"]
               for e in els), len(els))
    report("62.38.16 MaxLv = ParamDataArrayNum of that AbilityId",
           sum(abl[e["BuffEffect"]["BuffId"]]["ParamArray"][0]["ParamDataArrayNum"] == e["BuffEffect"]["MaxLv"]
               for e in els), len(els), dict(collections.Counter(e["BuffEffect"]["MaxLv"] for e in els)))
    report("62.38.16 Level = the 'Lv. n' suffix of BuffName",
           sum(e["BuffName"]["value"].endswith("Lv. %d" % e["Level"]) if "BuffName" in e
               else e["BuffEffect"]["BuffName"]["value"].endswith("Lv. %d" % e["Level"]) for e in els), len(els))
    ok = tot = 0
    for s, n, d in b39:
        p = near(b38, s, n)
        tot += 1
        a = sorted((e["BuffId"], e["Level"]) for e in ents(d, "BuffList"))
        b = sorted((e["BuffEffect"]["BuffId"], e["Level"]) for e in ents(p[2], "BuffEffectParamList")) if p else None
        ok += a == b
    report("62.39.16 BuffList (BuffId, Level) = the nearest 62.38.16 list of the stream", ok, tot)
    adj = sum(abs(near(b38, s, n)[1] - n) <= 3 for s, n, _ in b39)
    report("62.39.16 nearest 62.38.16 within 3 sequence numbers", adj, len(b39))
    # CharacterId: other packets of the same stream carrying it as "CharacterId"
    ids = collections.defaultdict(set)
    for s, _, d in b39:
        ids[s].add(d["CharacterId"])
    ok = 0
    for s, vals in ids.items():
        js = os.path.join(W.JSN, os.path.basename(s))
        found = set()
        for f in glob.glob(os.path.join(js, "*.json")):
            if "62_39_16" in f:
                continue
            with open(f, encoding="utf-8") as h:
                t = h.read()
            for v in vals - found:
                if re.search(r'"CharacterId": %d\b' % v, t):
                    found.add(v)
            if found == vals:
                break
        ok += len(found)
    report("62.39.16 CharacterId also a CharacterId field in another JSON of the stream (stream, id pairs)",
           ok, sum(len(v) for v in ids.values()))
    # ---- 62.8-62.10 epitaph / EX items ----
    r82 = dec("62.8.2")
    for pid in ("62.9.1", "62.10.1"):
        r = dec(pid)
        ok = sum(prev(r82, s, n) is not None and prev(r82, s, n)["EpitaphId"] == d["EpitaphId"] for s, n, d in r)
        report(pid + " EpitaphId = EpitaphId of the preceding 62.8.2", ok, len(r))
    r81 = dec("62.8.1")
    report("62.8.1 LayoutId.StageId in stage_list", sum(d["LayoutId"]["StageId"] in stages for _, _, d in r81),
           len(r81), sorted({stages.get(d["LayoutId"]["StageId"]) for _, _, d in r81}))
    pairs = sorted({(d["LayoutId"]["GroupId"], prev(r82, s, n + 2) and prev(r82, s, n + 2)["EpitaphId"])
                    for s, n, d in r81})
    report("62.8.1 GroupId -> 62.8.2 EpitaphId (next response)", 0, 0, pairs)
    r92 = dec("62.9.2")
    item_check("62.9.2 ItemList.ItemId", [e["ItemId"] for _, _, d in r92 for e in ents(d, "ItemList")])
    ok = 0
    r101 = dec("62.10.1")
    for s, n, d in r101:
        p = prev(r92, s, n)
        ok += bool(p) and sum(e["Num"] for e in ents(d, "ItemList")) == sum(e["Num"] for e in ents(p, "ItemList"))
    report("62.10.1 sum(ItemList.Num) = the preceding 62.9.2 ItemList Num", ok, len(r101),
           [sum(e["Num"] for e in ents(d, "ItemList")) for _, _, d in r101])
    # ---- 62.0-62.1 dungeon info ----
    r02, r11, r12 = dec("62.0.2"), dec("62.1.1"), dec("62.1.2")
    report("62.1.1 DungeonId = the preceding 62.0.2 DungeonId",
           sum(prev(r02, s, n) is not None and prev(r02, s, n)["DungeonId"] == d["DungeonId"] for s, n, d in r11),
           len(r11))
    report("62.1.2 DungeonInfo first u32 = the preceding 62.1.1 DungeonId",
           sum(prev(r11, s, n) is not None and prev(r11, s, n)["DungeonId"] == d["DungeonInfo"]["DungeonId"]
               for s, n, d in r12), len(r12))
    secs = [e for _, _, d in r12 for e in ents(d, "SectionList")]
    report("62.1.2 SectionList StageId in stage_list", sum(e["StageId"] in stages for e in secs), len(secs),
           sorted({stages.get(e["StageId"]) for e in secs}))
    report("62.1.2 DungeonInfo.Name = stage_list name of StageId 559 (Memory of Megadosys) / third u32",
           0, 0, sorted({(d["DungeonInfo"]["Name"]["value"], d["DungeonInfo"]["unk_u32"]) for _, _, d in r12}))
    # ---- 12.5 / 12.9.16 ----
    r51, r916 = dec("12.5.1"), dec("12.9.16")
    names = {e["SectionName"]["value"] for e in secs}
    report("12.5.1 SectionName is a 62.1.2 SectionName", sum(d["SectionName"]["value"] in names for _, _, d in r51),
           len(r51))
    report("12.9.16 ContentId = ContentId of the preceding 12.5.1",
           sum(prev(r51, s, n) is not None and prev(r51, s, n)["ContentId"] == d["DungeonStart"]["ContentId"]
               for s, n, d in r916), len(r916))
    report("12.9.16 StageId in stage_list", sum(d["DungeonStart"]["StageId"] in stages for _, _, d in r916), len(r916),
           sorted({stages.get(d["DungeonStart"]["StageId"]) for _, _, d in r916}))
    # ---- B7 ----
    item_check("65.3.2 ItemCost.ItemId", [x["unk_u32"] for _, _, d in dec("65.3.2") for e in ents(d, "ParamList")
                                          for x in e["ItemCost"]["entries"]])
    item_check("10.14.16 ItemId", [x["ItemId"] for _, _, d in dec("10.14.16") for x in ents(d, "unk_list")])
    p = [(e["Index"], [y["unk_u16_0"] for x in e["unk_list"]["entries"] for y in x["unk_list"]["entries"]])
         for _, _, d in dec("65.3.2")[:1] for e in ents(d, "ParamList")]
    report("65.3.2 (Index, inner unk_u16_0)", 0, 0, p)
    r01, r02b = dec("34.0.1"), dec("34.0.2")
    report("34.0.2 BoardId = the preceding 34.0.1 BoardIdList value",
           sum(prev(r01, s, n) is not None and any(x["m_ullValue"] == e["BoardId"]
                                                   for x in ents(prev(r01, s, n), "BoardIdList"))
               for s, n, d in r02b for e in ents(d, "EntryList")),
           sum(len(ents(d, "EntryList")) for _, _, d in r02b))
    r82b, r51b = dec("41.8.2"), dec("41.5.1")
    for s, n, d in r51b:
        p = prev(r82b, s, n)
        report("41.5.1 (UpdateType, EditPrice) vs the preceding 41.8.2 price list", 0, 0,
               (d["UpdateType"], d["EditPrice"], p and [(e["UpdateType"], e["PriceList"]["entries"])
                                                         for e in ents(p, "PriceInfoList")]))
    # ---- B6 ----
    c2, c17, p2 = dec("13.16.2"), dec("13.17.1"), dec("13.17.2")
    report("13.17.1 CategoryId in the preceding 13.16.2 CategoryList",
           sum(prev(c2, s, n) is not None and any(e["CategoryId"] == d["CategoryId"] for e in ents(prev(c2, s, n),
                                                                                                    "CategoryList"))
               for s, n, d in c17), len(c17))
    for s, n, d in p2:
        cat = prev(c2, s, n)
        u8 = [e["EntryCount"] for e in ents(cat, "CategoryList") if e["CategoryId"] == d["CategoryId"]] if cat else []
        report("13.17.2 TreasurePointList count vs the category's u8 in 13.16.2", int(u8 == [d["TreasurePointList"]["count"]]),
               1, (u8, d["TreasurePointList"]["count"]))
    tp = [e for _, _, d in p2 for e in ents(d, "TreasurePointList")]
    report("13.17.2 Name ends in 《Index + 1》", sum(e["Name"]["value"].endswith("《%d》" % (e["Index"] + 1)) for e in tp),
           len(tp))
    nt = dec("13.23.16")
    report("13.23.16 StageId in stage_list", sum(d["StageId"] in stages for _, _, d in nt), len(nt),
           sorted({stages.get(d["StageId"]) for _, _, d in nt}))
    # ValueOld = the Value an earlier 13.23.16/13.23.2/13.20.x of the stream set for (StageId, Key)
    last = {}
    ok = tot = 0
    for s, n, d in sorted(nt, key=lambda x: (x[0], x[1])):
        k = (s, d["StageId"], d["Value"]["Key"])
        if k in last:
            tot += 1
            ok += last[k] == d["ValueOld"]
        last[k] = d["Value"]["Value"]
    report("13.23.16 ValueOld = Value of the previous 13.23.16 for the same (stream, StageId, Key)", ok, tot)
    ch = dec("63.7.16") + dec("63.6.16")
    report("63.7.16/63.6.16 LayoutId.StageId in stage_list",
           sum(e["LayoutId"]["StageId"] in stages for _, _, d in ch for e in ents(d, "LayoutInfoList")),
           sum(len(ents(d, "LayoutInfoList")) for _, _, d in ch),
           sorted({stages.get(e["LayoutId"]["StageId"]) for _, _, d in ch for e in ents(d, "LayoutInfoList")}))


if __name__ == "__main__":
    main()

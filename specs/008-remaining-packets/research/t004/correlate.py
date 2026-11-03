"""008 T004: value correlation for batches B1 and B4 (client 03040008).

usage (from D:/ddon-data): python -X utf8 -I specs/008-remaining-packets/research/t004/correlate.py
Decodes with t004/walk.py's layouts (the pattern's field names), pairs packets of one capture stream
by file sequence number, and checks ids against client/03040008/base/etc/itemlist.ipa.json
(ItemId). Prints one line per check: name, matches/total, notes.
"""
import collections
import importlib.util
import json
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("t004walk", os.path.join(_here, "walk.py"))
w = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(w)
W = w.W
_cache = {}


def seq(f):
    return int(os.path.basename(f).split("_")[0])


def dec(pid):
    """[(stream, seq, decoded)] for every raw file of pid."""
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


def nxt(items, stream, n):
    c = [x for x in items if x[0] == stream and x[1] > n]
    return min(c, key=lambda x: x[1])[2] if c else None


def report(name, ok, tot, note=""):
    print("%-78s %d/%d %s" % (name, ok, tot, note))


def load_items():
    with open(os.path.join("client", "03040008", "base", "etc", "itemlist.ipa.json"), encoding="utf-8") as h:
        j = json.load(h)
    ids = {}
    for v in j.values():
        if isinstance(v, list):
            for e in v:
                if isinstance(e, dict) and "ItemId" in e:
                    ids[e["ItemId"]] = e.get("ItemCategoryName")
    return ids


def ents(d, *path):
    for p in path:
        d = d[p]
    return d["entries"]


def main():
    it = load_items()

    def item_check(name, vals):
        vals = list(vals)
        cats = collections.Counter(it.get(v, "MISSING") for v in vals)
        report(name + " in itemlist", sum(v in it for v in vals), len(vals), dict(cats.most_common(4)))

    # ---- group 62 ----
    p1424 = dec("62.14.16") + [(s, n, {"TrialId": d["TrialId"]}) for s, n, d in dec("62.24.1")]
    r = dec("62.15.16")
    ok = sum(prev(p1424, s, n) is not None and prev(p1424, s, n)["TrialId"] == d["TrialId"] for s, n, d in r)
    report("62.15.16 TrialId = TrialId of the preceding 62.14.16/62.24.1", ok, len(r))
    lst = dec("62.18.2")
    for pid in ("62.24.1", "62.20.1"):
        r = dec(pid)
        ok = 0
        for s, n, d in r:
            p = prev(lst, s, n)
            ok += bool(p) and any(e["TrialId"] == d["TrialId"] for e in ents(p, "ElementParamList"))
        report(pid + " TrialId in the preceding 62.18.2 ElementParamList", ok, len(r))
    r33, r341, r35 = dec("62.33.2"), dec("62.34.1"), dec("62.35.1")
    ok = tot = 0
    for s, n, d in r341:
        p = prev(r33, s, n)
        gi = {(e["Id"], e["Num"]) for e in ents(p, "ItemRewards")} if p else set()
        for e in ents(d, "RewardList"):
            tot += 1
            ok += (e["RewardIndex"], e["Amount"]) in gi
    report("62.34.1 (RewardIndex, Amount) = (Id, Num) of the preceding 62.33.2 ItemRewards", ok, tot)
    ok = 0
    for s, n, d in r35:
        p = prev(r33, s, n)
        ok += bool(p) and any(e["BuffId"] == d["BuffId"] for e in ents(p, "BuffRewards"))
    report("62.35.1 BuffId in the preceding 62.33.2 BuffRewards", ok, len(r35))
    lv = collections.Counter()
    for s, n, d in r33:
        for e in ents(d, "BuffRewards"):
            lv[(e["Level"], e["BuffName"]["value"][-5:])] += 1
    report("62.33.2 BuffRewards (Level, BuffName suffix)", 0, 0, dict(lv.most_common(6)))
    item_check("62.33.2 ItemRewards.ItemId", [e["ItemId"] for _, _, d in r33 for e in ents(d, "ItemRewards")])
    item_check("62.18.2 TrialCost.ItemId", [c["ItemId"] for _, _, d in lst for e in ents(d, "ElementParamList")
                                            for c in e["TrialCost"]["entries"]])
    item_check("62.18.2 TrialRewards.RewardList.ItemId",
               [x["ItemId"] for _, _, d in lst for e in ents(d, "ElementParamList")
                for t in e["TrialRewards"]["entries"] for x in t["RewardList"]["entries"]])
    om = dec("62.26.16")
    ok = tot = 0
    for name in ("62.12.16", "62.18.1", "62.33.1", "62.40.16"):
        for s, n, d in dec(name):
            tot += 1
            ok += any(x[0] == s and x[2]["OmState"]["LayoutId"] == d["LayoutId"] for x in om)
    report("62.12.16/18.1/33.1/40.16 LayoutId also in a 62.26.16 of the stream", ok, tot)
    # ---- group 71 ----
    r = dec("71.22.2")
    tot = c1 = c2 = c3 = 0
    for _, _, d in r:
        for i in ents(d, "BattleContentInfoList"):
            ids = [e["Id"] for e in i["BattleContentStageList"]["entries"]]
            tot += len(ids)
            prog = i["BattleContentStageProgressionList"]["entries"]
            c1 += sum(a["Id"] == b for a, b in zip(prog, ids))
            c3 += sum(all(x["m_unValue"] in ids for x in e["ConnectionList"]["entries"]) for e in prog)
        for st in ents(d, "BattleContentStatusList"):
            c2 += sum(e["Id"] in ids for e in st["BattleContentAvailableRewardsList"]["entries"])
    report("71.22.2 StageProgressionList[i].Id = StageList[i].Id", c1, tot)
    report("71.22.2 StageProgressionList ConnectionList values among the StageList ids", c3, tot)
    report("71.22.2 AvailableRewardsList.Id among the StageList ids", c2, tot)
    item_check("71.22.2 RareItemAppraisalList", [e["m_unValue"] for _, _, d in r for i in ents(d, "BattleContentInfoList")
                                                 for e in i["RareItemAppraisalList"]["entries"]])
    item_check("71.22.2 ItemTakeawayList", [e["m_unValue"] for _, _, d in r for i in ents(d, "BattleContentInfoList")
                                            for e in i["ItemTakeawayList"]["entries"]])
    # ---- group 59 ----
    cats = dec("59.8.2")
    for name in ("59.4.1", "59.9.1"):
        r = dec(name)
        ok = 0
        for s, n, d in r:
            p = prev(cats, s, n)
            ok += bool(p) and any(c["CategoryId"] == d["CategoryId"] for e in ents(p, "CategoryList")
                                  for c in e["DeliveryCategoryList"]["entries"])
        report(name + " CategoryId in the preceding 59.8.2 DeliveryCategoryList", ok, len(r))
    ev = dec("59.0.2")
    ok = tot = 0
    for s, n, d in cats:
        for e in ents(d, "CategoryList"):
            tot += 1
            ok += any(x[0] == s and any(y["EventId"] == e["EventId"] for y in ents(x[2], "EventList")) for x in ev)
    report("59.8.2 EventId = a 59.0.2 EventId of the stream", ok, tot)
    i92 = dec("59.9.2")
    item_check("59.9.2 DeliveryItemList.ItemId", [e["ItemId"] for _, _, d in i92
                                                  for e in d["Info"]["DeliveryItemList"]["entries"]])
    item_check("59.9.2 reward ItemList.ItemId", [x["ItemId"] for _, _, d in i92
                                                 for ln in ("PointRewardList", "RankingRewardList")
                                                 for e in d["Info"][ln]["entries"] for x in e["ItemList"]["entries"]])
    ranks = {e["Rank"] for _, _, d in i92 for e in d["Info"]["Status"]["RankingList"]["entries"]}
    rr = [e["Rank"] for _, _, d in i92 for e in d["Info"]["RankingRewardList"]["entries"]]
    report("59.9.2 RankingRewardList.Rank among the RankingList ranks", sum(x in ranks for x in rr), len(rr), rr)
    rk = [e for _, _, d in dec("59.4.2") for e in d["Status"]["RankingList"]["entries"]]
    rk += [e for _, _, d in i92 for e in d["Info"]["Status"]["RankingList"]["entries"]]
    report("59.4.2/59.9.2 RankingList ClanId == 0 iff ClanName empty",
           sum((e["ClanId"] == 0) == (e["ClanName"]["value"] == "") for e in rk), len(rk))
    ok = tot = 0
    for _, _, d in dec("59.4.2") + i92:
        pts = [e["Point"] for e in (d.get("Status") or d["Info"]["Status"])["RankingList"]["entries"]]
        tot += max(len(pts) - 1, 0)
        ok += sum(a >= b for a, b in zip(pts, pts[1:]))
    report("59.4.2/59.9.2 RankingList Point non-increasing with Rank (per list)", ok, tot)
    # ---- group 72 ----
    m = dec("72.0.2")
    ok = tot = 0
    for _, _, d in m:
        for ln in ("MissionList", "SpecialRewardList"):
            for e in ents(d, ln):
                tot += 1
                ok += e["MissionId"] == e["Reward"]["MissionId"]
    report("72.0.2 Reward.MissionId = MissionId", ok, tot)
    item_check("72.0.2/72.3.2 Reward.ItemList.ItemId",
               [x["ItemId"] for _, _, d in m + dec("72.3.2") for ln in ("MissionList", "SpecialRewardList", "EventMissionList")
                if ln in d for e in ents(d, ln) for x in e["Reward"]["ItemList"]["entries"]])
    st = collections.Counter()
    dur = collections.Counter()
    for _, _, d in m:
        for ln in ("MissionList", "SpecialRewardList"):
            for e in ents(d, ln):
                st[(e["State"], "progress>=target" if e["Progress"] >= e["TargetNum"] else "progress<target")] += 1
                dur[(e["Text"]["value"][-6:], (e["EndDate"] - e["StartDate"]) // 3600)] += 1
    report("72.0.2 (State, progress vs target)", 0, 0, dict(sorted(st.items())))
    report("72.0.2 (Text suffix, EndDate - StartDate in hours)", 0, 0, dict(sorted(dur.items())))
    for pid, want in (("72.1.16", (1, 2)), ("72.2.1", (2, 3))):
        ok = tot = 0
        for s, n, d in dec(pid):
            for e in ents(d, "MissionIdList"):
                tot += 1

                def state(x):
                    if x is None:
                        return None
                    for ln in ("MissionList", "SpecialRewardList"):
                        for y in ents(x, ln):
                            if y["MissionId"] == e["m_unValue"]:
                                return y["State"]
                    return "absent"
                a, b = state(prev(m, s, n)), state(nxt(m, s, n))
                ok += a == want[0] and b in (want[1], None)
        report("%s MissionIdList: State %d in the list before, %d (or no list) after" % (pid, want[0], want[1]), ok, tot)
    r = dec("72.2.1")
    report("72.2.1 StorageType in {13, 19, 20}", sum(d["StorageType"] in (13, 19, 20) for _, _, d in r), len(r),
           dict(collections.Counter(d["StorageType"] for _, _, d in r)))
    e3, e31 = dec("72.3.2"), dec("72.3.1")
    report("72.3.2 unk_u8 = the preceding 72.3.1 unk_u8",
           sum(prev(e31, s, n) is not None and prev(e31, s, n)["unk_u8"] == d["unk_u8"] for s, n, d in e3), len(e3))


if __name__ == "__main__":
    main()

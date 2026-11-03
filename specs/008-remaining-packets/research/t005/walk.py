"""008 T005: independent stdlib walk of batches B3, B7 and B6 (client 03040008).

usage (from D:/ddon-data):
  python -X utf8 -I specs/008-remaining-packets/research/t005/walk.py stats [id ...]
  python -X utf8 -I specs/008-remaining-packets/research/t005/walk.py check [id ...]
  python -X utf8 -I specs/008-remaining-packets/research/t005/walk.py fits [id ...]
  python -X utf8 -I specs/008-remaining-packets/research/t005/walk.py dump <id> [n]

The decoder, the fit rule (ends within the last 15 bytes) and the modes are T003's (`../t003/walk.py`,
loaded by path); this file supplies the B3/B7/B6 layouts (the PC reader/writer width sequences read in
IDA for T005, see T005-batches-B3-B7-B6.md § 2) with the pattern's field names, plus one decoder
addition: ("A", name, typ, n), a fixed array of n leaves (50.0.16's u8[1024] bin).
"""
import importlib.util
import json
import os
import re
import sys

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("t003walk", os.path.join(_here, "..", "t003", "walk.py"))
W = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(W)
L, S, RES = W.L, W.S, W.RES

_orig_dec = W.dec


def _dec(r, lay, out, path, leaves):
    """T003's decoder plus fixed arrays; the recursion goes through W.dec, i.e. here."""
    for t in lay:
        if t[0] == "A":
            fmt = W.FMT[t[2]]
            vals = [r.get(fmt) for _ in range(t[3])]
            out[t[1]] = vals
            leaves[path + t[1] + "[]"].extend(vals[:1])
        else:
            _orig_dec(r, [t], out, path, leaves)


W.dec = _dec


def A(name, typ, n):
    return ("A", name, typ, n)


def _edit_info():
    """CDataEditInfo names from include/Context.hexpat; widths asserted against PC writer 0x77eb40
    (Write_u8 x2, Write_u16, Write_u8 x18, Write_u16 x50, read in IDA for T005)."""
    p = os.path.join("research", "03040008", "packets", "include", "Context.hexpat")
    with open(p, encoding="utf-8") as h:
        txt = h.read()
    body = txt.split("struct CDataEditInfo {", 1)[1].split("};", 1)[0]
    fields = re.findall(r"^\s*(u8|u16)\s+(\w+);", body, re.M)
    want = ["u8", "u8", "u16"] + ["u8"] * 18 + ["u16"] * 50
    assert [t for t, _ in fields] == want, "CDataEditInfo widths differ from PC 0x77eb40"
    return [(n, t) for t, n in fields]


LAYOUT_ID = [("StageId", "u32"), ("LayerNo", "u8"), ("GroupId", "u32")]   # CDataStageLayoutId (Instance.hexpat)
OM = [S("LayoutId", *LAYOUT_ID), ("PosId", "u32")]
WALLET = [("Type", "enum8"), ("Value", "u32")]                            # CDataWalletPoint, PC 0x77c5a0
ITEM_NUM = [("ItemId", "u32"), ("Num", "u16")]                            # {u32, u16} elements
ITEM_UID = [("str", "UID"), ("Num", "u32")]                                # CDataItemUIDList (Quest.hexpat), writer 0x77fd30
BUFF_EFFECT = [("BuffId", "u32"), ("str", "BuffName"), ("MaxLv", "u32"), ("unk_u32_0", "u32"),
               ("unk_u32_1", "u32"), ("unk_u32_2", "u32"), ("ParamType", "u32")]  # PC 0x779540
BUFF_LEVEL = [("BuffId", "u32"), ("Level", "u32")]                        # PC 0x777c40 / 0x778fa0 element
ACH_PROGRESS = [S("AchieveIdenfier", ("Uid", "u32"), ("Index", "u32")), ("CurrentNum", "u32"),
                ("Seqence", "u32"), ("CompleteDate", "s64")]               # Achievement.hexpat, PC 0x758810
ITEM_AMOUNT = [("unk_u32", "u32"), ("unk_u16", "u16")]                     # GatheringItemListRes_unk_1 (Instance.hexpat), PC 0x7731b0
CHAIN_OM = [S("LayoutId", *LAYOUT_ID), ("unk_u32", "u32")]                # PC 0x762c50 element

LAYOUTS = {
    # ---- B3: group 62 SEASON_DUNGEON, group 12 STAGE ----
    "62.38.16": [L("BuffEffectParamList", ("Level", "u32"), S("BuffEffect", *BUFF_EFFECT))],
    "62.39.16": [("CharacterId", "u32"), L("BuffList", *BUFF_LEVEL)],
    "62.10.2": RES(),
    "62.8.1": OM,
    "62.8.2": RES(("EpitaphId", "u32")),
    "62.9.1": [("EpitaphId", "u32")],
    "62.9.2": RES(("unk_bool_0", "bool"), ("unk_bool_1", "bool"), L("ItemList", *ITEM_NUM)),
    "62.10.1": [("EpitaphId", "u32"), L("ItemList", *ITEM_UID), ("unk_bool", "bool")],
    "62.0.1": [("NpcId", "u32")],
    "62.0.2": RES(("DungeonId", "u32")),
    "62.1.1": [("DungeonId", "u32")],
    "62.1.2": RES(S("DungeonInfo", ("DungeonId", "u32"), ("str", "Name"), ("unk_u32", "u32")),
                  L("SectionList", ("unk_u32_0", "u32"), ("StageId", "u32"), ("unk_u32_1", "u32"),
                    ("unk_u32_2", "u32"), S("unk_Param", ("unk_u32_0", "u32"), ("unk_u32_1", "u32")), ("unk_bool", "bool"), ("str", "SectionName")),
                  ("unk_u8", "u8")),
    "62.7.1": [("NpcId", "u32")],
    "62.7.2": RES(L("BlockadeList", ("EpitaphId", "u32"), ("str", "Name"))),
    "62.27.16": [("unk_u32", "u32")],
    "12.5.1": [("ContentId", "u32"), L("EntryFeeList", *ITEM_UID), ("EntranceId", "u32"), ("str", "SectionName")],
    "12.5.2": RES(),
    "12.9.16": [S("DungeonStart", ("ContentId", "u32"), ("str", "unk_str"), ("StageId", "u32"), ("StartPos", "u32"),
                  ("unk_bool", "bool"), L("EntryCostList", *ITEM_NUM))],
    # ---- B7 ----
    "50.0.16": [L("SortData", ("StorageType", "u8"), A("Bin", "u8", 1024))],
    "27.10.1": [("Category", "u8")],
    "27.10.2": RES(L("AchievementProgressList", *ACH_PROGRESS)),
    "41.8.1": [],
    "41.8.2": RES(L("PriceInfoList", ("UpdateType", "u8"), L("PriceList", *WALLET))),
    "41.5.1": [("UpdateType", "u8"), S("EditPrice", *WALLET), S("EditInfo", *_edit_info()), ("str", "FirstName")],
    "41.5.2": RES(),
    "2.5.16": [("unk_u8", "u8")],
    "29.23.16": [("unk_u32", "u32"),
                 L("unk_list", ("unk_u32_0", "u32"), ("unk_u32_1", "u32"), ("unk_u32_2", "u32"), ("unk_u8_0", "u8"),
                   ("unk_u32_3", "u32"), ("unk_u8_1", "u8"))],
    "65.3.1": [("EnhanceType", "u8")],
    "65.3.2": RES(L("ParamList", ("Index", "u16"), ("Category", "u8"), ("str", "RowTitle"), ("unk_u16_0", "u16"),
                    ("unk_u16_1", "u16"), L("WalletPointCost", *WALLET), L("ItemCost", *ITEM_AMOUNT),
                    L("unk_WalletPointList", *WALLET), L("unk_ItemList", *ITEM_AMOUNT),
                    L("ShopTypeList", ("m_ucValue", "u8")),
                    L("unk_list", ("unk_u8", "u8"),
                      L("unk_list", ("unk_u16_0", "u16"), ("unk_u16_1", "u16"), ("unk_u8", "u8"))))),
    "10.14.16": [("unk_u16", "u16"), L("unk_list", ("unk_u8", "u8"), ("ItemId", "u32"))],
    "34.0.1": [L("BoardIdList", ("m_ullValue", "u64"))],
    "34.0.2": RES(L("EntryList", ("BoardId", "u64"), ("SortieMin", "u16"), ("NoPartyMembers", "u16"), ("unk_u16_0", "u16"),
                    ("TimeOut", "u16"), ("unk_u16_1", "u16"), ("unk_bool", "bool"), ("unk_u32", "u32"))),
    # ---- B6: group 63, group 13 INSTANCE ----
    "13.23.16": [("StageId", "u32"), S("Value", ("Key", "u64"), ("Value", "u32")), ("ValueOld", "u32")],
    "63.2.16": [("unk_bool", "bool"), ("unk_u8", "u8"), ("unk_u32_0", "u32"), ("unk_u32_1", "u32"),
                ("unk_u32_2", "u32"), ("unk_u32_3", "u32"),
                L("ObjectiveList", ("unk_u8", "u8"), ("unk_u32", "u32"), ("str", "Message"))],
    "63.10.16": [("unk_u32", "u32"), ("str", "unk_str"), ("unk_u8", "u8")],
    "63.7.16": [L("LayoutInfoList", *CHAIN_OM)],
    "63.6.16": [L("LayoutInfoList", *CHAIN_OM)],
    "13.16.1": [("unk_u32", "u32")],
    "13.16.2": RES(L("CategoryList", ("CategoryId", "u32"), ("str", "CategoryName"), ("EntryCount", "u8"))),
    "13.17.1": [("CategoryId", "u32")],
    "13.17.2": RES(("CategoryId", "u32"), L("TreasurePointList", ("Index", "u32"), ("str", "Name"),
                                              ("unk_bool", "bool"))),
    "63.0.16": [("unk_u32", "u32")],
    "63.1.16": [("unk_u32", "u32")],
    "63.3.16": [],
    "63.5.16": [],
}
W.LAYOUTS = LAYOUTS


def dump(pid, n):
    import collections
    for f in W.files_of(pid)[:n]:
        out, sl, _ = W.walk(f, LAYOUTS[pid], collections.defaultdict(list))
        print("==", os.path.relpath(f, W.RAW), "slack", sl)
        print(json.dumps(out, ensure_ascii=False, default=str)[:4000])


def main():
    mode = sys.argv[1]
    if mode == "dump":
        dump(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1)
        return
    ids = sys.argv[2:] or list(LAYOUTS)
    if mode == "stats":
        W.stats(ids)
    elif mode == "fits":
        sys.exit(1 if W.fits(ids) else 0)
    else:
        sys.exit(1 if W.check(ids) else 0)


if __name__ == "__main__":
    main()

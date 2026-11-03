"""008 T007: append the "Errata (T006, 2026-11-03)" section to the T003, T004 and T005 reports.

Reads marks-before.tsv (values and distinct values behind every I (value) mark, before T007) and
mark-changes.tsv (the rule's verdict); the hand-edited marks are listed in HAND.
usage (from D:/ddon-data): python -X utf8 -I specs/008-remaining-packets/research/t007/errata.py [--write]
"""
import collections
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPORTS = {"3": "T003-batches-B5-B2.md", "4": "T004-batches-B1-B4.md", "5": "T005-batches-B3-B7-B6.md"}
HAND = {
    ("S2C_ITEM_ACHIEVEMENT_REWARD_RECEIVE_NTC-pattern.cpp", "22"):
        "V (consumer): handler `0x7de260` passes element +8 to the sItemManager lookup `0xb98c80` and posts chat "
        "message 0x85 (T006 F1)",
    ("S2C_BATTLE_CONTENT_INFO_LIST_RES-pattern.cpp", "39"): "G (lead; value consistent: 1 distinct) (T006 F2)",
    ("S2C_BATTLE_CONTENT_INFO_LIST_RES-pattern.cpp", "54"): "G (lead; value consistent: 1 distinct) (T006 F2)",
    ("C2S_DAILY_MISSION_REWARD_RECEIVE_REQ-pattern.cpp", "24"): "G (lead; value consistent: 3 distinct) (T006 F2)",
    ("include/DailyMission.hexpat", "30"):
        "G (context; value consistent: 2 distinct); typed `E_WALLET_POINT_TYPE_U32` (PS4 DWARF "
        "E_WALLET_POINT_TYPE at u32 width: 4 WALLET_POINT_TYPE_TICKET, 12 UNK_12) (T006 F2)",
    ("S2C_JOB_MASTER_MARK_TARGETS_NTC-pattern.cpp", "28"): "I unchanged (width-parallel basis, no value basis)",
    ("S2C_JOB_MASTER_MARK_TARGETS_NTC-pattern.cpp", "30"): "I unchanged (width-parallel basis, no value basis)",
}
F3 = {
    "4": ["71.22.2: the 42 captures carry one identical BattleContentInfoList and one identical "
          "BattleContentStatusList: \"294/294\" is 7 comparisons x 42 copies of one list (7 distinct ids).",
          "72.0.2: the 3,393 missions are 29 MissionIds (30 with the 72.3.2 event mission's 0) and 187 distinct "
          "mission tuples; none breaks the State rule."],
    "5": ["62.39.16: \"148/148\" includes 121 empty lists; 27 are non-empty, 21 distinct lists, 3 CharacterIds.",
          "10.14.16 ItemId is now V (consumer); the \"I 1\" of the § 3 row reads \"V\".",
          "`Instance.hexpat` `GatheringItemListRes_unk_1` (§ 5 proposal): `unk_u32` -> `ItemId`, `unk_u16` -> `Num`, "
          "both G (lead; value consistent: 19 distinct, chance 0.21 / 1 distinct)."],
    "3": [],
}


def main():
    rows = list(csv.DictReader(open(os.path.join(HERE, "marks-before.tsv"), encoding="utf-8"), delimiter="\t",
                               quoting=csv.QUOTE_NONE))
    ch = {(r["file"], r["comment_line"]): r for r in
          csv.DictReader(open(os.path.join(HERE, "mark-changes.tsv"), encoding="utf-8"), delimiter="\t",
                         quoting=csv.QUOTE_NONE)}
    by = collections.defaultdict(list)
    for r in rows:
        t = re.search(r"T00([345])", r["mark"]).group(1)
        key = (r["file"], r["comment_line"])
        if key in HAND:
            new = HAND[key]
        elif key in ch:
            new = ch[key]["new"]
            if new.startswith("G"):
                new += " (was I)"
        else:
            new = "unchanged"
        chance = r["chance"].split("p=")[1] if "p=" in r["chance"] and not r["chance"].endswith("-1") else ""
        by[t].append((r["pids"], "%s.%s" % (r["struct"], r["field"]), r["n"], r["distinct"], chance, new))
    for t, name in REPORTS.items():
        lines = ["", "## Errata (T006, 2026-11-03)", "",
                 "Applied by 008 T007 (`specs/008-remaining-packets/briefs/T007-mark-fixes.md`) from the adversarial "
                 "review `T006-adversarial.md` F1-F3; the text above is unchanged. Counts above are values in "
                 "captures; this table gives the distinct values behind every `I (value)` mark of this task and "
                 "the mark after T007 (rule: README \"How value bases are counted\"). `chance`: probability that "
                 "every distinct value is an id of the item or stage table by luck (id claims only). Source: "
                 "`t007/marks-before.tsv`, `t007/mark-changes.tsv`.", ""]
        for note in F3[t] + ["The README table rows count the marks after T007; the tables above keep the marks "
                             "before it."]:
            lines.append("- " + note)
        lines.append("")
        lines += ["| id | field | values | distinct | chance | mark after T007 |", "| --- | --- | ---: | ---: | ---: | --- |"]
        for pid, field, n, d, c, new in sorted(by[t]):
            lines.append("| %s | `%s` | %s | %s | %s | %s |" % (pid, field, n, d, c, new))
        text = "\n".join(lines) + "\n"
        path = os.path.join(HERE, "..", name)
        if "--write" in sys.argv:
            body = open(path, encoding="utf-8").read()
            if "## Errata (T006, 2026-11-03)" in body:
                print("already has errata:", name)
                continue
            if not body.endswith("\n"):
                body += "\n"
            open(path, "w", encoding="utf-8", newline="\n").write(body + text)
            print("appended %d rows to %s" % (len(by[t]), name))
        else:
            print(text)


if __name__ == "__main__":
    main()

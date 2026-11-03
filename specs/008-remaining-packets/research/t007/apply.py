"""008 T007: rewrite the `I (... value: ...)` marks of the 008 patterns and includes by the T006 F1 rule.

Input: marks-before.tsv (marks.py). Each value basis gets its distinct count (and, for item/stage id claims, the
chance that every distinct value is a table id by luck). A value-only basis with 3 or fewer distinct values, or an
id claim with chance > 0.05, becomes `G (lead|context; value consistent: n distinct; ...)`. Kept I: marks with an
independent structural basis before the value part (same structure / same reader / width parallel) and stage-id
claims that also match the stage name (T006 F1). Special cases (10.14.16, F2) are handled by hand in the files.

usage (from D:/ddon-data): python -X utf8 -I specs/008-remaining-packets/research/t007/apply.py [--dry-run]
"""
import csv
import os
import re
import sys

PAT = os.path.join("research", "03040008", "packets")
HERE = os.path.dirname(os.path.abspath(__file__))
# (file, comment_line): edited by hand (T007 brief items 1-2), not by the rule
MANUAL = {
    ("S2C_ITEM_ACHIEVEMENT_REWARD_RECEIVE_NTC-pattern.cpp", 22),
    ("S2C_BATTLE_CONTENT_INFO_LIST_RES-pattern.cpp", 39),
    ("S2C_BATTLE_CONTENT_INFO_LIST_RES-pattern.cpp", 54),
    ("C2S_DAILY_MISSION_REWARD_RECEIVE_REQ-pattern.cpp", 24),
    ("include/DailyMission.hexpat", 30),
    ("S2C_JOB_MASTER_MARK_TARGETS_NTC-pattern.cpp", 28),   # width-parallel basis, no value basis
}
# stage-id / stage-name claims that match the stage name (T006 F1: these stand)
STAGE_NAME = {("S2C_STAGE_DUNGEON_START_NTC-pattern.cpp", 32), ("include/SeasonDungeon.hexpat", 112)}
# F3 notes: distinct lists behind the headline counts
F3 = {
    "71.22.2": "; the 42 captures carry one identical list",
}
F3_BUFF = ("include/SeasonDungeon.hexpat", 100)


def note(row):
    n = int(row["distinct"])
    s = "%d distinct" % n
    ch = row["chance"]
    text = row["mark"]
    is_id = bool(re.search(r"itemlist|item ids?\b|stage_list|StageId \d", text))
    p = None
    if is_id and "p=" in ch and not ch.endswith("p=-1"):
        p = float(ch.split("p=")[1])
        s += ", chance %s" % ("%.2g" % p if p >= 0.001 else "%.1e" % p)
    return n, p, s


def main():
    dry = "--dry-run" in sys.argv
    rows = list(csv.DictReader(open(os.path.join(HERE, "marks-before.tsv"), encoding="utf-8"), delimiter="\t",
                               quoting=csv.QUOTE_NONE))
    files = {}
    log = []
    for r in rows:
        key = (r["file"], int(r["comment_line"]))
        if key in MANUAL:
            continue
        path = os.path.join(PAT, r["file"])
        lines = files.setdefault(path, open(path, encoding="utf-8").read().split("\n"))
        lo, hi = key[1] - 1, int(r["line"]) - 1
        span = "\n".join(lines[lo:hi + 1])
        m = re.search(r"T00[345] I \(", span)
        v = re.search(r"\bvalue:", span[m.end():]) if m else None
        if not v:
            print("no value basis:", key, r["mark"][:80])
            continue
        vpos = m.end() + v.start()
        n, p, s = note(r)
        structural = re.search(r"same structure|same reader|width parallel", span[m.end():vpos]) is not None
        pid = r["pids"]
        extra = F3.get(pid, "")
        if key == F3_BUFF:
            extra = "; 121 of the 148 lists are empty: 27 non-empty, 21 distinct"
        demote = not structural and key not in STAGE_NAME and (n <= 3 or (p is not None and p > 0.05))
        if demote:
            kind = "lead" if re.search(r"\blead\b", span) else "context"
            # only a pure value basis is demoted: `I (value: X` -> `G (kind; value consistent: s; X`
            if span[m.end():vpos].strip():
                print("mixed basis, check by hand:", key, r["mark"][:80])
                continue
            new = span[:m.start() + 5] + "G (%s; value consistent: %s%s; " % (kind, s, extra) + \
                span[vpos + len("value:"):].lstrip(" ")
            verdict = "G (%s)" % kind
        else:
            new = span[:vpos] + "value, %s%s:" % (s, extra) + span[vpos + len("value:"):]
            verdict = "I"
        new_lines = new.split("\n")
        assert len(new_lines) == hi - lo + 1
        lines[lo:hi + 1] = new_lines
        log.append((r["file"], key[1], r["struct"], r["field"], pid, s, "I", verdict))
    if not dry:
        for path, lines in files.items():
            open(path, "w", encoding="utf-8", newline="").write("\n".join(lines))
    with open(os.path.join(HERE, "mark-changes.tsv"), "w", encoding="utf-8", newline="\n") as out:
        out.write("file\tcomment_line\tstruct\tfield\tpids\tdistinct\told\tnew\n")
        for x in log:
            out.write("\t".join(str(y) for y in x) + "\n")
    print("rewritten %d marks, demoted %d" % (len(log), sum(1 for x in log if x[-1] != "I")))


if __name__ == "__main__":
    main()

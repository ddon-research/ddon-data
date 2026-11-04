"""009 T004: move the text of the packet patterns README onto three reference pages, by script, so nothing is retyped.

    python -X utf8 -I specs/009-docs-structure/research/T004-split.py

Reads the README at the base commit and writes docs/reference/packet-ids.md (rows intact), packet-includes.md and
packet-open-questions.md. Every edit below must match, or the script stops: a text that moved changes only here.
"""

import csv
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BASE = "715f8f2305d"
README = "packets/patterns/03040008/README.md"
SECTIONS = REPO / "specs/009-docs-structure/research/T001-sections.tsv"

LABEL = (r"(?:008 )?(?:T\d{3}[a-z]?\d?|TC\d+|R\d[a-z]?|P\d{1,2}[a-z]?)"
         r"(?: (?:§ ?[\d.]+(?:, ?§ ?[\d.]+)*|F\d+(?:, F\d+)*|part \d+))?")


def wrap_labels(text):
    """Report citations go in code spans; text already in a code span stays as it is."""
    parts = re.split(r"(`[^`]*`)", text)
    for index, part in enumerate(parts):
        if not part.startswith("`"):
            parts[index] = re.sub(rf"(?<![\w`]){LABEL}(?![\w`])", lambda m: f"`{m.group(0)}`", part)
    return "".join(parts)


def replace_all(text, edits):
    for old, new in edits:
        if old not in text:
            raise SystemExit(f"edit does not match: {old!r}")
        text = text.replace(old, new)
    return text


# --- packet-ids.md -------------------------------------------------------------------------------------------------

SPEC5 = "specs/005-netmsg-patterns/research"
SPEC6 = "specs/006-packet-pattern-coverage/research"
SPEC8 = "specs/008-remaining-packets/research"

KEY = [
    ("P1", f"{SPEC5}/P1-ps4-wire-format.md", "PS4 wire format, nNetMsg"),
    ("P2", f"{SPEC5}/P2-pc-deltas.md", "PC differences from PS4, nNetMsg"),
    ("P3", "specs/005-netmsg-patterns/tasks.md", "the first nNetMsg patterns and export"),
    ("P4", f"{SPEC5}/P4-context-binary-character.md", "group 35 CONTEXT"),
    ("P5", f"{SPEC5}/P5-pc-send-side.md", "PC send side, 13.44-13.47.16, 63.11.16"),
    ("P7", f"{SPEC5}/P7-imhex-as-library.md", "ImHex as a library, the plbatch design"),
    ("P9, P10", "specs/005-netmsg-patterns/tasks.md", "6.24.16 and 6.26.16; the fit flag and slack"),
    ("P11a, P11b", f"{SPEC5}/P11a-old-patterns.md, {SPEC5}/P11b-old-patterns.md", "the older patterns"),
    ("R1, R2", f"{SPEC5}/R1-pattern-review.md, {SPEC5}/R2-old-patterns-review.md", "reviews of those patterns"),
    ("T001b", f"{SPEC6}/T001b-save-blob.md", "the save blob of 9.0.2 and 9.1.1, `include/CharacterData.hexpat`"),
    ("T001c", f"{SPEC6}/T001c-parked-static-items.md", "items parked before these reports"),
    ("T002, T002c", f"{SPEC6}/T002-login.md, {SPEC6}/T002c-challenge-decrypt.md", "the login group; first-packet decryption"),
    ("T003", f"{SPEC6}/T003-connection-server-cert.md", "groups 0 CONNECTION, 1 SERVER and 44 CERT of the game server"),
    ("T004", f"{SPEC6}/T004-instance.md", "group 13 INSTANCE"),
    ("T005", f"{SPEC6}/T005-quest.md", "group 11 QUEST"),
    ("T006", f"{SPEC6}/T006-job-lobby-area-stage.md", "groups 33 JOB, 3 LOBBY, 23 AREA and 12 STAGE"),
    ("T007", f"{SPEC6}/T007-pawn-partner.md", "groups 8 PAWN, 53 PARTNER_PAWN and 58 PAWN_EXPEDITION"),
    ("T008", f"{SPEC6}/T008-warp-item.md", "groups 14 WARP, 10 ITEM and 50 ITEM_SORT"),
    ("T009", f"{SPEC6}/T009-mail-stamp-character.md", "groups 2 CHARACTER, 37 MAIL and 45 STAMP"),
    ("T010", f"{SPEC6}/T010-gp-clan.md", "groups 28 GP and 31 CLAN"),
    ("T011", f"{SPEC6}/T011-party-profile-friend.md", "groups 5 (user list), 6 PARTY, 16 FRIEND, 17 BLACK_LIST and 26 PROFILE"),
    ("T012", f"{SPEC6}/T012-achievement-equip-skill.md", "groups 19 SKILL, 20 SHOP, 25 ORB_DEVOTE, 27 ACHIEVEMENT, 29 EQUIP, 39 GACHA and 43 LOADING_INFO"),
    ("T013", f"{SPEC6}/T013-small-groups.md", "groups 9 (save response), 15 (event notices), 18 (group chat request), 30 CRAFT, 34 ENTRY_BOARD, 41 CHARACTER_EDIT, 51 DISPEL, 52 (furniture request), 54 CRAFT_RECIPE and 57 (box gacha request)"),
    ("T014a, T014b", f"{SPEC6}/T014a-value-correlation.md, {SPEC6}/T014b-consumer-property-names.md", "value correlation of `unk_*` fields; consumer and property names"),
    ("R4", f"{SPEC6}/R4-adversarial-marks.md", "review of the marks"),
    ("T003b ... T013b, T005b, TC1, TC2, R1b, R2b", "specs/006-packet-pattern-coverage/tasks.md", "the patterns and re-export of a report (`b`), the naming sweep (`TC1`), the code-backed renames (`TC2`), the reviews"),
    ("008 T003", f"{SPEC8}/T003-batches-B5-B2.md", "33 ids of groups 11, 14, 24, 28, 31, 45, 60, 61, 64 and 70"),
    ("008 T004", f"{SPEC8}/T004-batches-B1-B4.md", "37 ids of groups 59 INFINITY_DELIVERY, 62 SEASON_DUNGEON, 71 BATTLE_CONTENT and 72 DAILY_MISSION"),
    ("008 T005", f"{SPEC8}/T005-batches-B3-B7-B6.md", "45 ids of groups 2, 10, 12, 13, 27, 29, 34, 41, 50, 62, 63 and 65"),
    ("008 T006, 008 T007", f"{SPEC8}/T006-adversarial.md, {SPEC8}/t007/", "review of those marks; the rewrite of the value bases (`marks.py`, `mark-changes.tsv`)"),
]


def key_table():
    rows = ["| Label | Report | Covers |", "| --- | --- | --- |"]
    for label, paths, covers in KEY:
        labels = ", ".join(f"`{x}`" for x in label.split(", "))
        spans = ", ".join(f"`{p}`" for p in paths.split(", "))
        rows.append(f"| {labels} | {spans} | {covers} |")
    return "\n".join(rows)


IDS_HEAD = """# Packet ids, client 03040008

Every packet pattern of the PC client 03040008, by packet id, for a reader who wants to know whether a packet is decoded, how often it was captured and which report holds its evidence. Read [Packet evidence marks](packet-marks.md) for the marks and the [glossary](glossary.md) for fit and slack. `tools/docs_check.py` compares this table with the patterns: the rows are edited by script, never by hand over the whole table.

## Report labels

The Report column of the table, and the labels in code spans on the other packet pages, name a report and a section of it (`T003 §9` is section 9 of `T003`). A bare label `T003` is the report of spec 006, and `008 T003` the report of spec 008.

{key}

## Reading the table

- **Status `n/m fit`:** n of the m JSON files of that packet in `packets/decrypted_json/` have `fits` true. No packet has a `.json.err`.
- **Status `no capture`:** no raw file exists, so the pattern was checked on synthetic input at most.
- **Pattern name:** the file `<name>-pattern.cpp`. A pattern file may carry a better name than its raw files, because the export selects by `// packet-id:`: the rows say so (62.39.16, 63.2.16 among them). `(was ...)` gives the name the raw files had before the code-backed rename.
- **`marks:`** the row counts the marks in the pattern file; the structures of an include carry their own.

## The table

Fit counts not recounted: run `tools/docs_check.py --packet-counts --write`.

"""


def packet_ids(lines):
    rows = lines[247:844]
    assert rows[0].startswith("| Id | Pattern") and rows[-1].startswith("| 72.3.2 ") and len(rows) == 597
    return IDS_HEAD.format(key=key_table()) + "\n".join(rows) + "\n"


# --- packet-includes.md --------------------------------------------------------------------------------------------

INCLUDE_EDITS = [
    ("`CDataCommonU32`/`CDataCommonU8` (and since 008 T005 `CDataCommonU64`, PS4 DWARF name)", "`CDataCommonU32`/`CDataCommonU8` (and `CDataCommonU64`, PS4 DWARF name)"),
    ("(P11a); since T005b also the Season 3", "(P11a); also the Season 3"),
    ("since T006b `CDataCharacterLevelParam`", "`CDataCharacterLevelParam`"),
    ("since T007b `CDataPartyMember`", "`CDataPartyMember`"),
    ("since T009b `CDataStatusInfo`", "`CDataStatusInfo`"),
    ("since T011b `CDataFriendInfo`", "`CDataFriendInfo`"),
    ("37.x through Mail, and since T011b 5.2.16", "37.x through Mail, and 5.2.16"),
    ("(P11b); since T010b the join request", "(P11b); the join request"),
    ("T010 §1.2), moved in T010b from the 52.1.2 pattern; includes", "T010 §1.2); includes"),
    ("(P11b); since T012b `CDataNormalSkillParam`", "(P11b); `CDataNormalSkillParam`"),
    ("and 19.28.2 since T012b", "and 19.28.2"),
    ("(P11b §13); since T008b the Season 3", "(P11b §13); the Season 3"),
    ("(P11b §14); since T007b the Season 3", "(P11b §14); the Season 3"),
    ("(T002 §10, §11); since T010b `CDataGPPeriod`", "(T002 §10, §11); `CDataGPPeriod`"),
    ("(fields `ItemId`, `Num` since 008 T007, G)", "(fields `ItemId`, `Num`, G)"),
    ("(008 T004 §1, §3): `CDataSeasonDungeonOmState`", "(008 T004 §1, §3): `CDataSeasonDungeonOmState`"),
    ("since 008 T005 the buff effect", "the buff effect"),
    ("62.38.16, 62.39.16, 62.1.2, 62.7.2, 62.9.2 (T005)", "62.38.16, 62.39.16, 62.1.2, 62.7.2, 62.9.2"),
    ("since 008 T007 the wallet element", "the wallet element"),
]

CHARACTER_DATA = ("| `CharacterData.hexpat` | the `cCharacterData` save blob, the 1024-byte body field of 9.0.2 and 9.1.1: "
                  "one LSB-first bit stream, plain big-endian fields up to bit 2432, then one bitfield (`T001b`) | {users} |")


def users_of_character_data():
    root = REPO / "packets/patterns/03040008"
    users = []
    for path in sorted(root.glob("*-pattern.cpp")):
        text = path.read_text(encoding="utf-8")
        if re.search(r'^\s*#include\s+"CharacterData\.hexpat"', text, re.M):
            users.append(re.search(r"^// packet-id: (\S+)", text, re.M).group(1))
    assert users
    return ", ".join(users)


def packet_includes(lines):
    rows = replace_all("\n".join(lines[12:49]), INCLUDE_EDITS).split("\n")
    assert rows[0].startswith("| Include |") and len(rows) == 37
    out = rows[:2]
    for row in rows[2:]:
        out.append(wrap_labels(row))
    at = next(i for i, r in enumerate(out) if r.startswith("| `Character.hexpat`"))
    out.insert(at + 1, CHARACTER_DATA.format(users=users_of_character_data()))
    return ("# Packet pattern includes, client 03040008\n\n"
            "The shared files of `packets/patterns/03040008/include/`, for a reader of a pattern who wants to know where a type lives and which patterns use it. "
            "Every pattern starts with `#pragma endian big` and includes what it needs from that directory. "
            "A label in a code span names a report: [the key](packet-ids.md#report-labels). "
            "After a change to an include, re-export every pattern that includes it, as [Export packets to JSON](../how-to/export-packets-to-json.md) says.\n\n"
            + "\n".join(out) + "\n")


# --- packet-open-questions.md --------------------------------------------------------------------------------------

BULLET_EDITS = [
    (": struct names neutral since TC1, the server's", ": struct names neutral, the server's"),
    ("`server: <name> (lead)` comments since R1b)", "`server: <name> (lead)` comments)"),
    ("named by role since T014b and R4: MessageKind", "named by role, T014b and R4: MessageKind"),
    ("server: TrainingProfile; `unk_List_1`, server: SpSkillList; names since TC1)", "server: TrainingProfile; `unk_List_1`, server: SpSkillList)"),
    ("with BonusType/BonusValue after it (I; T014c renamed them `unk_u32_1`/`unk_u32_2`, since T014b part 7 shows +4 is the bonus kind, +8 an id and +12 the amount)",
     "with `unk_u32_1`/`unk_u32_2` after it (not BonusType/BonusValue: T014b part 7 shows +4 is the bonus kind, +8 an id and +12 the amount)"),
    ("are V since TC1: the PS4 DWARF", "are V: the PS4 DWARF"),
    ("`unk_u32` (since TC1; was `CharacterId`: one value, 2144504,", "`unk_u32` (one value, 2144504,"),
    ("`EnableJobList` (V since TC1: PS4 DWARF", "`EnableJobList` (V: PS4 DWARF"),
    ("**Season 3 field names:** fields new in Season 3 are", "**Season 3 field names:** fields added in Season 3 are"),
    ("11.120.16 still has no capture.", "11.120.16 has no capture."),
    ("(its element is exercised by the unpatterned 50.0.16)", "(its element is exercised by 50.0.16)"),
    ("28.28/28.29.16 (START/END_PARTY) are outside this package.", "28.28/28.29.16 (START/END_PARTY) have no pattern."),
    ("the restriction element fields. Which", "the restriction element fields (`ItemId`, `Num` are G). Which"),
    ("**No existing pattern changed (T006b):** T006 shows no layout error in an existing pattern; `CDataStageInfo` stays local to 12.0.2 (one user), and the new types are new names in the includes (no include cycle:",
     "**Group 12 types and include order (T006b):** T006 shows no layout error in the patterns of its groups; `CDataStageInfo` is local to 12.0.2 (one user) (no include cycle:"),
    ("which u64 is new (`unk_u64`", "which u64 Season 3 added (`unk_u64`"),
    ("settle which of the five bools is new, and their", "settle which of the five bools Season 3 added, and their"),
    ("the `CDataStampBonus` new u32 (`unk_u32`", "the `CDataStampBonus` Season 3 u32 (`unk_u32`"),
    ("and where the new u32 sits, is open", "and where the added u32 sits, is open"),
]


CLOSE = """## Open at the close of the pattern work

From `specs/008-remaining-packets/tasks.md` § Close, 2026-11-03.

- **29.23.16 `S2C_EQUIP_29_23_16_NTC`:** no reader. The PC handler `0x7d5730` is `mov eax, 1; retn 4` and reads nothing (V), so its layout comes from captures alone and its marks are `G`. The PS4 candidate `CHANGE_CHARACTER_EQUIP_JOB_ITEM_NOTICE` is rejected: its element is 18 bytes, not 5 (`T012 §15`).
- **11.88.16 and 11.118.16:** they decode, and their meaning is open. The PC handler of 11.88.16 is `return 1` with an empty body (`T005 §32`), and that of 11.118.16 discards one u8 (`T005 §39`). With no-op PC handlers, neither shape nor behaviour selects a PS4 counterpart.
- **`G` names whose consumers were not traced:** the role-only `V` marks of 28.34.2 and 11.68.16 have consumers **not run**, and the `ValueOld` check of 13.23.16 is **not run**.

## By group

"""


def open_questions(lines):
    with SECTIONS.open(encoding="utf-8", newline="") as handle:
        rows = [r for r in csv.reader(handle, delimiter="\t", quoting=csv.QUOTE_NONE)
                if r[0] == "research/03040008/packets/README.md" and r[1].startswith("[sub] Open item:")]
    assert len(rows) == 61
    kept = []
    for row in rows:
        start, end = (int(x) for x in row[2].split("-"))
        if row[4] == "docs/reference/packet-open-questions.md":
            kept.append(" ".join(line.strip() for line in lines[start - 1:end]))
    assert len(kept) == 39, len(kept)
    text = replace_all("\n".join(kept), BULLET_EDITS)
    bullets = [wrap_labels(b) for b in text.split("\n")]
    return ("# Packet open questions, client 03040008\n\n"
            "What the packet patterns of client 03040008 leave unsettled, by group, for a reader about to rely on a decoded field or to settle one: names without code backing, fields that rest on PC code alone because captures cannot separate them, and PC code read only by linear decoding. "
            "Read [Packet evidence marks](packet-marks.md) first; a label in a code span names a report: [the key](packet-ids.md#report-labels).\n\n"
            + CLOSE + "\n".join(bullets) + "\n")


def main():
    text = subprocess.run(["git", "-C", str(REPO), "show", f"{BASE}:{README}"], check=True, capture_output=True).stdout.decode("utf-8")
    lines = text.split("\n")
    pages = {
        "docs/reference/packet-ids.md": packet_ids(lines),
        "docs/reference/packet-includes.md": packet_includes(lines),
        "docs/reference/packet-open-questions.md": open_questions(lines),
    }
    for path, page in pages.items():
        (REPO / path).write_bytes(page.encode("utf-8"))
        print(path, len(page))


if __name__ == "__main__":
    main()

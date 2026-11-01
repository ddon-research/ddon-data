005 P11 (T021): evidence for the 36 old packet patterns, two batches

Objective (build 03040008, seed PS4 02020005): the 36 packet patterns in `research/03040008/packets/`
created before 2026-11-01 were written in 2024-2026 without IDA checks and some were never
finished. For each pattern of your batch, establish the Season 3 PC wire format from the client and
list what the pattern gets wrong or leaves open, so P12 can fix, complete and refactor them.

Batch A (unfinished first): S2C_JOIN_LOBBY_QUEST_INFO_NOTICE, S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES,
S2C_PARTY_QUEST_PROGRESS_NOTICE, S2C_GET_PARTY_QUEST_PROGRESS_INFO_RES,
S2C_QUEST_GET_CYCLE_CONTENTS_NEWS_LIST_RES, S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES,
S2C_STAGE_GET_STAGE_LIST_RES, S2C_BOX_GACHA_BOX_GACHA_LIST_RES, S2C_QUEST_GET_AREA_BONUS_LIST_RES,
S2C_MY_ROOM_FURNITURE_LIST_GET_RES, S2C_QUEST_GET_AREA_INFO_LIST_RES,
S2C_GET_CYCLE_CONTENTS_STATE_LIST_RES, S2C_AREA_GET_AREA_QUEST_HINT_LIST_RES,
C2S_AREA_GET_AREA_QUEST_HINT_LIST_REQ, S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES,
S2C_AREA_GET_AREA_BASE_INFO_LIST_RES, S2C_AREA_GET_AREA_MASTER_INFO_RES, C2S_AREA_GET_AREA_MASTER_INFO_REQ.
Batch B: the other 18 (`git log --diff-filter=A` per `*-pattern.cpp` before 2026-11-01, minus A).

Per pattern: (1) status finished / partial / stub; (2) the PC reader (S2C) or writer (C2S) VA and how
it was found (P4's handler table, the 658 `WritePacket` call sites at `0x8bcbb0`, DDON_RE leads);
(3) the field table in wire order with Season 3 types, the PS4 counterpart matched by code (reader
body, callers, strings), never by packet number; (4) every pattern error or gap (width, order,
signedness, missing/extra field, enum not from DWARF, list count width, RES error handling) with
the VA; (5) shared CData structures across packets (include candidates, with their reader VAs);
(6) a byte walk of one capture to the end (raw files carry the 9-byte header; select by the
`.<g>_<id>_<sub>` suffix: names changed on 2026-11-01); (7) the packet's current raw name.
Server C# (Arrowgene) is a community lead, never evidence; list where it disagrees.

Owns: only `specs/005-netmsg-patterns/research/P11<a|b>-old-patterns.md` for your batch.
Never touch: patterns, packets/, client/, other reports, the user's .i64 files.
Source boundary: PC and PS4 IDA 9.5 via ida-mcp on private copies (`bash research/ida/private-copy.sh
<pc|ps4> p11<a|b>`); P2/P4/P5 for method and VAs; captures via `xxd`; PS4 DWARF types through IDA
(the reconstructor output folder named in P5's brief no longer exists). No `*.elf.c/.h` exports.
Libraries: ida-mcp `execute_python`; no own tooling.
Done: a section per pattern with items 1-7 marked V / I / unresolved; a shared-structure table; a
summary table (pattern, status, errors found, walk ok). Final message: report path + at most 15 lines.
Stop: budget 90 min of work time per batch; stop and report if ida-mcp will not open the copies.
Base: c748cd3a53.

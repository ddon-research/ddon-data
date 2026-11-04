010 T003: what the PC client does with each candidate

Question (PC 03040008, annotated database): for each candidate below, does the client's code make it an error, and what does a served client do? Read `specs/010-server-packet-fixes/spec.md`, `research/T001-inventory.md` § 5 and § 7, `research/T002-differential.md` § 3 to § 6. `docs/reference/packet-handler-tables.md` tells where handlers are and warns that 9 login handlers have no IDA function (disassemble at the address); `docs/reference/packet-wire-format.md` warns Hex-Rays leaves out send and receive logic. A candidate is a lead, the server C# is never evidence for itself, and a patch depends on your verdict: do not soften "not settled" into "probably".

Verdict for each: **error** (`V`, PC code contradicts the server, with the effect named), **harmless** (`V`, the client ignores or tolerates it), **not an error** (the server is right or the lead is refuted), or **not settled** (what would settle it: a live run, say which). Cite VAs; name what the consumer does with the value, not only the reader.

Priority order; do them in this order, and stop at a candidate boundary if budget ends:

1. **F06**: the error RES sent twice. Does the client's RES dispatch match a pending request by key? What does a second identical RES do when none is pending (drop, log, fault, a second handler run, a duplicate error dialog)? Follow the path through the receive dispatch and one error-showing handler, for example 13.3.2 or 18.0.2. Any counter check on the receive path (F04).
2. **62.33.2**: list reader `0x779420`: consumer of the fourth u32. Does the UI or logic use it as a level; effect of a buff id there? `CDataSeasonDungeonBuffEffectReward.cs:24`.
3. **W01 0.1.2**: reader `0x804a50`: u16 vs bool shifts `OneTimeToken`: what consumes it, what happens when empty? Every game login goes through this: the server evidently works with real clients, so explain how.
4. **W02 27.8.16**: list element {u32, u8}: the consumer of the u8. A list of 2 or more is shifted: does the client fault, misread or stop?
5. **W03 3.0.16**: reader `0x889ac0`: the consumer of the count at `this+36`; a read past the frame end: fault or stale bytes? General: `nPacket::Read_*` at the end of a buffer (F02).
6. **W04 2.1.2**: width, by the PC reader.
7. **W06 19.28.2**: reader `0x76f820`: who reads `+8` and `+0xc`? Which is the skill id, which the slot index? `JobManager.cs:642-643`. `docs/explanation/two-packet-decodings.md` presents this as an example: say whether its text stands.
8. **W05 62.1.2**: reader `0x777b00`: consumers of the first and third u32. **W15** enemy preset `+27`, `+28`. **W21** `CDataGoodsParamRequirement` flag polarity. **W22** `CDataTimeGainQuestList` bool order. **W12** `CDataCraftProgress` element. **W16** `CDataContentsPlayEnd`. Each by its consumer.
9. **D08** login 5.3.16 handler `0x8874b0` (no IDA function): does it read Error? **D06**: REQ on a non-request base: what does the client do if no RES ever comes (timeout, hang, retry)? Name the client's behaviour for one of the 7 (`LobbyLobbyLeaveHandler`).
10. **31.17.1 / 31.17.2**: PC writer `0x823a80` and reader `0x8043c0`: the bool's meaning, and whether the server's `ClanClanSettingUpdateHandler` drops a setting a player changes. The excess byte in the RES.
11. **11.60.16**, **14.11.16**, **W14 50.1.1**, **W09**: the bool or u32 the server does not read: does it carry something the server should act on?
12. **F03**: frame size limit of receive path `0x9d6d20`; **F09**: `nPacket::Read_MtString` `0x8bc5b0` above 0x800: truncate, fail or drop; **F12**: does the client verify `OpenHash`; **F02**: padding 1-16 and zero against 0-15.
13. **T05** 11.13.2 handler: the layout behind `OnPacket_QUEST_GET_RECOMMENDED_QUEST_INFO_LIST_RES`.

Report `specs/010-server-packet-fixes/research/T003-pc-evidence.md`: a verdict table first (row, id, verdict, effect on a served client, VA evidence, what a fix would have to do, whether a fix is safe given what you read); then the evidence per row, short; "Server structure misplacements" for anything new; a "Not settled" list with the live test that would settle each; "Not run". Mark `V` only for what you read in PC code; `recompilation` C++ (`D:/ddon-data-s2/recompilation/src/`) checks stack argument order where IDA may misorder them.

Source boundary: private copy only, `bash research/ida/private-copy.sh pc-handlers t003`; PS4 by `private-copy.sh ps4 t003` where its symbols name a consumer, marked as PS4 evidence and never as a packet name. Read-only: no annotations. Server code in `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Clean`, read only. Write only under `specs/010-server-packet-fixes/research/`. Leave the copies in place at the end and name them in your final message: the coordinator stops the workers and deletes them.
Libraries: ida-mcp `execute_python`.
Done: the report; final message: path, counts by verdict, the errors with their effect, anything not settled that blocks a fix. Stop: budget 120 min of work time; past 300k context, end `cut short:` with the next row. Base: the head when you start.

I found no blocking defects and no field-width errors in the 36 patterns. There are 2 medium findings (one is an export trap rather than a pattern defect) and 6 low ones. I had no git receipt for P12a/P12b, so I can't confirm that what I read is exactly what those commits changed (a few files only partly). Nothing was executed: no pattern compile, no re-export, no capture walk. Every "fits" or count below is quoted from P11a/P11b or tasks.md (historical). Labels: verified (I read it) or inferred.

**Baseline check.** The PS4 recompilation has no ReadPacket or WritePacket body for any of the 36:
- `JOIN_LOBBY_QUEST_INFO_NOTICE::ReadPacket` is a stub (S2C.cpp:6914) and `GET_CYCLE_CONTENTS_*` are stubs; I found no bodies for the others in S2C.cpp, C2S.cpp or LoginSession/.
- Only class layouts can be compared. QuestOrderList, SetQuestDetail, AreaBaseInfo/SpotInfo, PawnListData and ENEMY_KILL_RES members match what the patterns say about PS4 (verified).

**Medium**
1. **The second-u32 position in QuestEnemyInfo contradicts P11a.** `include/Quest.hexpat:285-291` says "the second u32 is Season 3" and puts `unk_u32` after `GroupId`. P11a §1.3 (P11a-old-patterns.md:97-98) says PS4 has "EnemyInfo/TalkInfo without the leading u32", which puts the new u32 first. TalkInfo (Quest.hexpat:340-345) follows P11a; EnemyInfo does not.
   - Consequence: if P11a is right, every exported `GroupId` in 11.89.16, 11.71.2, 11.120.16 and 11.15.2 holds the Season 3 value. The fit can't catch it because both fields are u32 (verified text; which order is right is unresolved).
   - Fix: name both `unk_u32_0` and `unk_u32_1` with a comment "position of the new u32 unresolved", or follow P11a and mark it I.
2. **The `@` selector is a trap for 0.1.1 and 0.1.2.**
   - Both login patterns declare `// packet-id: 0.1.1` and `0.1.2`. `packets/imhex-export.sh:142-154` turns `@` into a `*.0_1_1` file glob. The P12 brief (briefs/P12-old-patterns-fix.md:22) and the README (README-decrypt-annotate-streams.adoc:169-176) recommend `@` over name filters.
   - "Never with @" exists only as a comment in `C2L_LOGIN_REQ-pattern.cpp:7-8` and `L2C_LOGIN_RES-pattern.cpp:9-10`; the script and README don't enforce or mention it.
   - Failure case (inferred, not reproduced): `@ C2L_LOGIN_REQ` also decodes game-server `C2S_CONNECTION_LOGIN_REQ` (writer cstr, u8, u32; P11b §2). That leaves 4 unread bytes, so `fits` and `sourceOk` both stay true: a silent pass.
   - Current state (verified for one stream only): `decrypted_json/stream1-marked.pcapng_tcp-stream-34/` has no CONNECTION_LOGIN JSON, while stream-33 has the C2L/L2C JSON. So the P12b export looks to have used name filters.
   - Selecting by name relies on the CLI's stream labels (C2L vs C2S), which I infer come from the connection, not the server C#.
   - Fix: a `// packet-select: <name>` header that `@` honours, or have `@` refuse these two patterns, plus a README line. Spec 006 coverage counts by packet-id would also count 0.1.x as covered for the game server (inferred).

**Low**
3. **RES JSON shape split** (verified): the P10 RES uses `ResHeader res;` (`S2C_CONTEXT_GET_SET_CONTEXT_RES-pattern.cpp:16`), giving `packet.res.Error`. All 30 RES patterns of the 36 inline `s32 Error; if (Error == 0) {...}`, giving `packet.Error`. One jq query can't read both. `Packet.hexpat:30-35` `ResHeader` is now used once.
   - Fix: `ResHeader res; if (res.Error == 0) {...}` everywhere, or document the inline form as the convention.
4. **Dangling reference** (verified): `S2C_INSTANCE_ENEMY_KILL_RES-pattern.cpp:6` says 'see "Recompilation disagreements"'. No such section exists in the packets folder or spec 005; the only mention is tasks.md:80. Fix: point to tasks.md T022, or put the one-line reason inline.
5. **Inferred positions or names without an I mark** (verified text; positions unresolved):
   - `S2C_BOX_GACHA_BOX_GACHA_LIST_RES-pattern.cpp:30`: the new u32 is placed last of 5 consecutive u32s.
   - `S2C_QUEST_GET_AREA_BONUS_LIST_RES-pattern.cpp:24`: the new u16 is placed last of 5 u16s.
   - `S2C_MY_ROOM_FURNITURE_LIST_GET_RES-pattern.cpp:29`: second u32.
   - `Quest.hexpat:418-420`: `OrderNpcId`, `NameMsgId`, `DetailMsgId` keep PS4 names, though PC replaced PS4's six u32s with two lists plus three u32s.
   - The width can't show which field is new (the stage bools are fine: P11a says outright they are the last two). Fix: add "(I)" or make them `unk_*`.
6. **18.0.2 server tail** (`S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES-pattern.cpp:28-35`): the logic is sound. With slack over 15 after a non-zero Error it decodes 8 bytes, so slack goes 19 → 11 and `fits` is true. If the server ever wrote a non-empty list, the count would leave slack over 15 and `fits` would go false, so it isn't silent.
   - Caveat: from here on `fits` describes what the server wrote, not what the client reads. The comment says so.
   - Inferred: the tail matches the PS4 framing. The recompiled `ACTIVATE_JOB_ORDER_RES::ReadPacket` (S2C.cpp:188-206) reads Result after any Error and accepts a short packet. Worth one line in the comment.
7. **OnetimeToken in JSON** (verified): `11762_L2C_LOGIN_RES...json:13` holds the token value. P11b deliberately left it out. The raws already contain it, so nothing new is exposed; flagging for Sam only.
8. **Comment nit** (verified): `Character.hexpat:14-15` says values 9-16 are not in PS4 DWARF. DDOORBIS.elf.h:111944 names 9 `WALLET_POINT_TYPE_MAX`, a sentinel; `UNK_9` is still right. P11a G6 has the same wording.

**Checked and correct**
- **The two recorded disagreements:**
  - 13.3.2: PS4 declares `u32 m_unResult` (S2C.h:5514, verified) and the PC reads s32 (P11b V). Same width; keeping s32 is right.
  - RES Error: PS4 is `Read(m_usError)`, u16 (S2C.cpp:189). PC s32 is backed by the captures: Result at 0x0d and lists at 0x11 in the P11b walks. The comments are right.
- **RES guard:** all 30 RES patterns put Result and the body under `Error == 0`. 19.2.2's invented `s16 Result` is gone, 31.17.2 compiles, and the 0.1.2 pad is dropped. NTCs have no Error field (11.89.16, 11.120.16, 23.13.16).
- **Fixes against P11a/P11b:**
  - 11.89.16: LightQuestDetail is 7 u32, SetQuestDetail has the two lists, QuestOrderList has 3 u32 + 3 u64, and rows 6-7 are added.
  - 51.0.2: LotCrest, LotItem and the BaseItem tail are fixed.
  - 23.8.2 and 23.11.2: four lists; 23.13.16 has six fields.
  - Signedness fixes are in.
- **Includes:** one definition per structure in the includes and the 36. The only `struct CPacket` copies are in 6 nNetMsg patterns outside this scope. Each struct comment names the PC VA, the PS4 type and V/I.
- **Enums:** ORDER_CONDITION_TYPE, CYCLE_CONTENTS_(SUB_)CATEGORY and E_WALLET_POINT_TYPE match the DWARF lines I read; server names appear only as labelled leads. `unk_*` is used where names are open; the 60.0.1 `NpcID` is marked I.
- **P9/P10 conventions** are present in every pattern I read: the `sourceOk` direction, `paddingSize`/`fits`, `// packet-id:`, `count`/`entries`, lowercase header keys. Old file names are gone and have no remaining references.

**Not checked:** the git diff and the P12a/P12b receipts (no receipt in the brief); the full header comments of QUEST_HINT_RES, AREA_INFO, SKILL and the CLAN patterns; COMMAND_CHECK_LIST against DWARF value by value; the export counts and the "100% fit" claims; compiling the patterns.

Files:
- D:/ddon-data/research/03040008/packets/include/Quest.hexpat
- D:/ddon-data/research/03040008/packets/include/Packet.hexpat
- D:/ddon-data/research/03040008/packets/include/Character.hexpat
- D:/ddon-data/research/03040008/packets/C2L_LOGIN_REQ-pattern.cpp
- D:/ddon-data/research/03040008/packets/L2C_LOGIN_RES-pattern.cpp
- D:/ddon-data/research/03040008/packets/S2C_INSTANCE_ENEMY_KILL_RES-pattern.cpp
- D:/ddon-data/research/03040008/packets/S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES-pattern.cpp
- D:/ddon-data/packets/imhex-export.sh
- D:/ddon-data/packets/README-decrypt-annotate-streams.adoc

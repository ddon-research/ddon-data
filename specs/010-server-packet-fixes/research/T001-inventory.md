# 010 T001: baseline and inventory of packet-handling candidates

Server: `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Clean`, `develop` at `e2411fe8f9134fedd2b78f0db0bc561cadac98ce`. Client: PC **03040008**. ddon-data base `9f14b134b2f`. Date 2026-11-04.

Every candidate is in `T001-candidates.tsv` (64 rows, 8 columns, checked with `awk`). This report gives the reading, the contradictions and the questions. The scans are in `research/t001/`: `table_scan.py`, `dispatch_scan.py`, `robustness_scan.py`, `pattern_leads.py`. They are regex over C#, so a miss is a coverage gap, not a clean result.

**What `V` means here.** `V` says what the **server code** does, read at that line. It says nothing about a client: the effect of each candidate on a client is **not yet known** unless the row says otherwise. A wire row marked "V (PC, by report)" repeats a PC finding from an earlier report; no PC code was re-read in this package. All earlier reports were written against the fork at `88d82caf07`, and I re-read each cited server line at `e2411fe8f9`.

## Baseline: not run

**`dotnet build` and `dotnet test` did not run. There are no totals, warning counts or failing test names.**

The brief asks for them, but this role's instructions forbid builds and tests that write artifacts, and a brief cannot lift that. `tasks.md` assigns T001, baseline included, to `repository-researcher`; the role cannot do that half. The coordinator should give the baseline to `implementer`, for example as the first step of T002:

```bash
cd /d/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Clean
export DOTNET_CLI_TELEMETRY_OPTOUT=1
dotnet build Arrowgene.DragonsDogmaOnline.sln; echo "build exit $?"
dotnet test Arrowgene.DragonsDogmaOnline.sln; echo "test exit $?"
git status --short
```

CI differs: `.github/workflows/build.yaml` runs `dotnet build --configuration Release`, then `dotnet test --configuration Release --no-restore --no-build`, on `pull_request`. Run Release too, because `#if DEBUG` guards `TestSerializers` (`EntitySerializer.cs:1889-1891`) and the missing-serializer checks of the handler bases.

What static reading gives: `git status --short` in the clone has 0 lines, and no `bin/` or `obj/` exists. `Arrowgene.Ddon.Test` holds 37 `[Fact]`/`[Theory]` attributes in 15 files; that counts attributes, not test cases. Database tests may need more than a build, which is not checked.

## Summary

| Class | Rows | Notes |
| --- | --- | --- |
| framework | 17 | 12 server rows, 5 CLI patch rows |
| packet table | 8 | no wrong group, id or sub found |
| dispatch | 8 | 1 live missing serializer |
| robustness | 9 | |
| wire layout lead | 22 | 2 are refuted leads, kept so they are not patched |

Marks: 55 begin `V` (15 of them on the PC by report), 5 `I`, 4 `lead`.

Top 5, by what they do to a running server:

| Row | What | Risk if changed |
| --- | --- | --- |
| F06 | Every handled `ResponseErrorException` sends the error RES **twice** (`RequestPacketHandler.cs:87`, then `:101`); 329 throw sites | Low to medium. Reaches every player who hits an error. Read the PC RES path first |
| D01 + R01 | `CDataOcdImmuneLv` has no registered serializer: lists of it write no elements and read no bytes. A 35.9.16 count of `0xFFFFFFFF` loops `List.Add(null)` on the default single lane, with no login | Very low: one line, no change when the count is 0 (0 of 763 captures) |
| F01 | A TCP split inside a length prefix, after a frame over 16 bytes, rewinds into ciphertext and desynchronises the session | Low |
| R02 | A frame length not a multiple of 16 throws an exception type the kick path does not expect: no kick, the factory is stuck, its buffer grows without bound, no login needed | Low |
| W01 | 0.1.2 writes `IsCogLogin` as u16 where the PC reads bool, so the served client's `OneTimeToken` should arrive empty (inferred arithmetic) | Medium. Every game login. Needs the token's consumer read, perhaps a live run |

## 1. Framework

Files read: `PacketFactory.cs`, `Client.cs`, `Consumer.cs`, `Challenge.cs`, `RequestPacketHandler.cs`, `RequestPacketQueueHandler.cs`, `StructurePacketHandler.cs`, `PingRequestPacketHandler.cs`, `PacketQueue.cs`, `FallbackHandler.cs`, `ServerLogger.cs` (part), `EntitySerializer.cs:1880-2460`, `StructurePacket.cs`, `Packet.cs`, `ServerResponse.cs`, `ResponseErrorException.cs`, `Extension.cs`, `PacketId.cs:1-150`, `Camellia.cs` (part).

### 1.1 Control flow

1. `Consumer.HandleReceived` (`Consumer.cs:66`) calls `client.Receive`, which calls `PacketFactory.Read`.
2. `Read` decrypts and wraps each frame. `CreateStructurePacket` (`EntitySerializer.cs:2010`) only wraps: `StructurePacket.GetStructure` (`StructurePacket.cs:38`) parses lazily.
3. So a C2S structure is parsed at the handler's first `.Structure`, inside `ExecutePacketHandler`'s try (`Consumer.cs:112-123`) or `RequestPacketHandler`'s try (`:37`).
4. A truncated C2S packet therefore gives, for a request, a FAIL RES and a logged exception, and for an NTC a logged exception. The session continues in both.
5. An S2C structure's `Read` is never reached on a running server: no handler uses one. `Client.Send` passes the structure in, and the log prints the cached copy.

### 1.2 The RES guard and the CLI patches

| Patch (`packets/tools/arrowgene-cli.patch`) | Row | Verdict |
| --- | --- | --- |
| `if (obj.Error != 0) return obj;` in 4 structures | C1 | CLI-only need; the root is F05 |
| `ReadServerResponse` u16 (not patched, but the reason for the line above) | F05 | Reader bug in the server's code, with no run-time effect on a server |
| Debug log | C2 | CLI-only |
| First packet under the fixed key | C3 | CLI bug. The server's own path is right |
| Certificate notice relabel and header-less raw | C4 | CLI-only |
| One file per packet of a frame | C5 | CLI-only |
| 8 `Name` strings | C6 | Both for 14.10.16 and 14.11.16 (T01); the other 6 are out-of-scope renames |

F05 design note for T003 and T004. Reading a u32 fixes the width, yet each of the 492 call sites then reads on past where the client stops. The official 18.0.2 writes Result and an empty list, and `FallbackHandler.cs:27` writes Error alone, so a fixed-width read alone can still run out of bytes. The CLI catches that per packet (`PacketCommand.cs:137`). Options: guard each structure as the patches do, or give `ReadServerResponse` a return value. Neither changes a running server. The T002 differential should count which RES have Error != 0 in the captures before this is chosen.

### 1.3 Against `packet-wire-format.md`

| Item | Server | Page | Result |
| --- | --- | --- | --- |
| Frame length | u16 BE, ciphertext only (`:183`) | same | agrees |
| Minimum length | 16 (`:31`) | "a lead" | agrees with the page's note |
| Cipher, IV, fixed key | `:18-27` | same | agrees |
| Header | 9 bytes, u16 id BE, source, u32 count (`:167-171`) | same | agrees |
| Counter | sub 16 counts from 1, others 0 (`:155-164`) | NTC above 0, RES 0 (approximate) | agrees |
| Headerless first packets | `WriteDataWithLengthPrefix`, `_firstPacket` | same | agrees; 304 bytes as in the page |
| Padding | 1 to 16 bytes, zero | 0 to 15, not zeroed | F02 differs |
| RES header | writes u32, u32 always | client stops after non-zero Error | harmless excess (T002 §16 item 6) |
| List | u32 count, no element length | same | agrees; F10 on a missing serializer |
| String | u16 BE, bytes, UTF-8, no NUL | same; client reads up to 0x800 | agrees; F09 on null and long |

### 1.4 Concurrency, measured against the default

`ServerSetting.cs:53` sets `OrderingLaneCount = 1`, and neither local_dev config overrides it. So handlers run on one thread by default and F04 and F12 are mostly latent: F04's other senders are timers such as `PingRequestPacketHandler.cs:24-36`. The same single lane is what makes R01 a stall for all players, not one.

## 2. Packet table

`table_scan.py` over `PacketId.cs`, the 1,041 PC records in `research/03040008/ida-transfer/dumps/pc-ida.jsonl` (input SHA-256 `f1c974d0...`, read as a file, no IDA), 675 `OnPacket_` strings, the 595 rows of `packet-ids.md`, and the 20 login handlers of `packet-handler-tables.md`.

| Check | Count | Result |
| --- | --- | --- |
| Ids declared | 1,813 (1,778 Game, 35 Login including `UNKNOWN`) | |
| In an init list | all; game list 1,779 holds `UNKNOWN` | none missing |
| Duplicate key within a server type | 0 | |
| Sub against name suffix | 1 row, `C2S_LOBBY_LOBBY_DATA_MSG_REQ` 3.3.16, named REQ with sub 16; 3 ids have no suffix (15.65535.255, 68.0.1, 68.1.1, all with PC records) | matches the wire page; a name quirk, no row |
| PC record with no server id | 2: 73.0.16, 73.1.16 | T07, unimplemented |
| PC record the server marks client-sent | 0 | |
| Server S2C with no PC record | 6: 2.19, 2.20, 2.21, 11.60 (T02), 63.11 (T04), 11.81 (T06) | |
| `OnPacket_` name differs | 5 | T05 matters. 28.21.2 is a placeholder (PC `GP_EDIT_VOICE_GET_BUY_HISTORY_RES`). 11.123.2 NTC/NOTICE and the PC's own typos in 66.6.2 and 71.4.2 are out of scope |
| Pattern row with no server id | 1: 35.8.16 | T07 |
| Pattern name differs | 12 | placeholders, plus T01 |
| Login S2C without a PC login handler | 0 | |

**No wrong group, id or sub was found for any id the PC table can test.** The C2S side was tested only through pattern rows, since writers are not in that dump as keyed rows.

`PacketId.PacketSource` has **zero** readers in the clone. The wrong sources in T02 and T04 are metadata with no run-time effect; `PacketFactory` writes `Server` itself and reads the source byte from the wire.

## 3. Dispatch

`dispatch_scan.py`: 1,707 `Create(...)` registrations with no duplicate, 1,254 structure classes, 517 registered handlers (504 game, 13 login) with no duplicate.

| Check | Result |
| --- | --- |
| Handler structure without a serializer | 0 |
| Entity used by a serializer but unregistered | 2: `CDataOcdImmuneLv` (D01, live), `CDataSwitchStorage` (D02, CLI only) |
| Packet structure unregistered | 2, both dead (D03, D04) |
| Two structures on one id | 1: `S2CSwitchStorageNtc` on 5.2.16 (D03) |
| Request answered with a non-pairing response | 1 apparent, `LoadingInfoLoadingGetInfoHandler`: id override, RES pairs with the real id (D05) |
| Handler on a RES id | 0 |
| `ServerResponse` structure not calling `WriteServerResponse` first | 0 among RES |
| `sub 2` structure not a `ServerResponse` | 0 |
| `ServerResponse` on an NTC | 16: 15 write no header (harmless), `L2CCreateCharacterDataNtc` writes one (D08) |
| REQ on a non-request base | 7 (D06) |
| Game client ids with a handler | 499 of 733; the rest take `FallbackHandler`, which answers a REQ with Error `NOT_IMPLEMENTED` alone, the right shape for the client's reader |

RES paths writing Error plus a body: `RequestPacketHandler` always serialises a default `TResStruct` after an Error. The client stops after Error, so the body is harmless excess, except where the body's serializer can throw (R06, F08). The scan found no RES with a reference property left null and written unguarded.

## 4. Robustness

**What ends what:**

| Event | Result |
| --- | --- |
| Exception in a handler or in parsing | caught at `Consumer.cs:116`; session stays. REQ gets a FAIL RES unless the base is plain (D06) |
| `SQLiteException`, `PostgresException` | RES, close |
| Critical `ResponseErrorException` | RES (twice), close |
| Exception in `PacketFactory.Read` | no close unless it is `ResponseErrorException`, which nothing on that path throws (R02) |
| Length under 16, bad source | log, reset, no close (R03) |
| Server process | no path found that kills it from a packet, short of memory exhaustion by R01. F11 can stop a start |

**Reachability.** No login is needed for R01, R02, R03, R05, R06 and the lobby half of R04. The first frame is always treated as the challenge, and an attacker can run RSA against the server's public key with a self-chosen session key. After a failed challenge the session goes on under the fixed key (R05). I found no central gate in the handler bases I read; a handler fails only when it touches `client.Character`, which is null. I did not read the bodies of the 517 handlers, so that is a statement about the bases.

**Counts and lengths** (`robustness_scan.py`: 604 readers reachable from 513 handler request structures):

- 130 counted reads and 68 string reads; R09 explains why they stay bounded.
- The element consumes bytes in every reachable list except D01 and R01.
- No reference cycle, so no recursion from a packet.
- 5 reads with a dynamic length: `C2SBinarySaveSetCharacterBinSaveDataReq` uses a constant, `C2SCertClientChallengeReq` a u8, and 3 use a client s32 (R04).
- `CheckForOverflowUnderflow` is True in Debug and Release in all 12 projects, so narrowing casts throw rather than truncate. That is what turns F03 and F09 into exceptions.

The behaviour of `Arrowgene.Buffers` 1.0.2 `StreamBuffer` at end of data is unread: only the DLL is available. The docs report `EndOfStreamException`, and R04 and R09 lean on that, so they are `I`.

## 5. Server structure misplacements

This is the list for the next package, not a verdict. Each is a lead from `packets/patterns/03040008/` and the `Arrowgene leads` sections of `specs/006-packet-pattern-coverage/research/` (T002 §16, T003 §19, T004 §21, T005 §45, T006 §7, T007 §7, T008 §7, T009 §23, T010 §26, T011 §19, T012 §20, T013 §17), plus `specs/005-netmsg-patterns/research/P4-context-binary-character.md` §7.

| Row | Id | Server file | Difference | Pattern or report, mark | Harm on a served client |
| --- | --- | --- | --- | --- | --- |
| W01 | 0.1.2 | `S2CConnectionLoginRes.cs:19` | u16, PC bool | `S2C_CONNECTION_LOGIN_RES-pattern.cpp:7`, T003 §19, V | likely real |
| W02 | 27.8.16 | `S2CAchievementCompleteNtc.cs:22` | list u32, PC {u32, u8} | `include/Achievement.hexpat:58`, T012 §20, C | likely real |
| W03 | 3.0.16 | `L2CGetErrorMessageListNtc.cs:22` | no trailing u32 | `L2C_GET_ERROR_MESSAGE_LIST_NTC-pattern.cpp:8`, T002 §16, V | unknown |
| W04 | 2.1.2 | `L2CGetGameSessionKeyRes.cs:20` | u32, PC u16 | `L2C_GET_GAME_SESSION_KEY_RES-pattern.cpp:8`, V, code only | small |
| W05 | 62.1.2 | `CDataSeasonDungeonInfo.cs:21-23` | id in the third slot, first is 40 | `include/SeasonDungeon.hexpat:109`, G (lead), values | unknown |
| W06 | 19.28.2 | `CDataNormalSkillParam.cs:26-27` | names swapped, bytes probably right | `include/Skill.hexpat:58`, V | **do not swap the wire** |
| W07 | 10.14.16 | `S2CItemAchievementRewardReceiveNtc.cs:38-41` | count written as Unk1 = 1 | pattern `:4`, `:32`, V | none today |
| W08 | 14.11.16 | `C2SWarpWarpEndNtc.cs:12-16` | u32 unread | T008 §7, V | none |
| W09 | 0.1.1, 0.5.1 | `C2SConnectionLoginReq.cs:26-27`, `C2SConnectionMoveInServerReq.cs:23` | short reads | patterns `:7`, V | none |
| W10 | 1.0.1, 44.0.1 | `C2LClientChallengeReq.cs:39-43`, `C2SCertClientChallengeReq.cs:39-44` | u8[259], fixed u8[62] | patterns `:10`, V | none today |
| W11 | 1.0.2, 44.0.2 | `L2CClientChallengeRes.cs:26-27`, `S2CCertClientChallengeRes.cs:26-27` | 64 bytes, PC 62 | patterns `:8`, V | none |
| W12 | 30.x | `CDataCraftProgress.cs:49,66` | list element differs | `include/Craft.hexpat:35`, C, code only | real if filled |
| W13 | 28.x | `CDataGPCourseAvailable.cs:27-33` | PS4 layout | T010 §26, C | none: dead code |
| W14 | 50.1.1 | `C2SItemSortSetItemSortDataBinReq.cs:21,27` | trailing bool unread | T008 §7 | none |
| W15 | 13.x | `CDataStageLayoutEnemyPresetEnemyInfoClient.cs:65-66` | Repop names swapped | `include/Instance.hexpat:30`, T004 §21, V | unknown |
| W16 | quest end | `CDataContentsPlayEnd.cs:26-32` | play time slot | T005 §23, I | small |
| W17 | 13.16.2 | `S2CInstanceTreasurePointGetCategoryListRes.cs:33` | read dropped | T004 §21 | CLI only |
| W18 | 13.x | `C2SInstanceGetGatheringItemReq.cs:45` | byte for bool | T004 §21 | none |
| W19 | 34.0.1 | `C2SEntryBoardEntryBoardListReq.cs:23,29` | **refuted** | 008 T005 | none |
| W20 | 45.x | `CDataStampBonus.cs:23-25` | **refuted as a server fault** | T014b part 7, I | none |
| W21 | 20.x | `CDataGoodsParamRequirement.cs:13` | flag polarity | `include/Shop.hexpat:34`, contradicted | unknown |
| W22 | 11.10.2 | `CDataTimeGainQuestList.cs:36-40` | bool order, capture favours the server | `include/Quest.hexpat:733-735`, open | unknown |

Naming-only findings with no row, for a reader of the layout (same bytes):

- T003 §19 items 6-7: `S2CConnection_10_Ntc`, `CDataLobbyMemberInfo`.
- T009 §23: comment on 2.5.16.
- T011 §19 item 2: `CDataHistoryElement` signedness.
- T013 §17 items 2-3: `EntryFlag`, `PartyLeaderCharacterId`.
- P4 §7 rows 1, 7, 12, 13: 35.5.16 and 13.44-47 names.
- `include/nNetMsg.hexpat:208`: a server enum value contradicting the PS4 NUM.

Rows with no server structure (T005 §45, T010 §26, T012 §20, T013 §17, 008 T001) are unimplemented, so out of scope.

`pattern_leads.py` matched 538 comment lines of 631 files on its broad pattern, mostly `server: <name> (lead)` naming marks; the narrow filter left 54 lines, most of them boilerplate, and everything with a layout claim is in the table above. The narrow filter is a regex: read a pattern when a row depends on it.

## 6. Contradictions

1. **34.0.1 is not an error.** `spec.md` and the brief list it from `T001-triage.tsv`'s `ag_vs_pc`. `008 T005` line 15 corrected the PC shape to a u32 count plus `Write_u64` per element, which is the server's list of `CDataCommonU64`. The TSV was never regenerated, and `008 T006` line 49 still reads as if it differs. So the real `ag_vs_pc` count is 2 of 84, not 3.
2. **The stamp is not a server misplacement.** `specs/006-packet-pattern-coverage/tasks.md` line 75 faults "the pattern's" BonusType and BonusValue. `T009 §23` says the server agrees with PC, and order and width are equal.
3. **19.28.2 is framed as a swap to fix.** `two-packet-decodings.md` reports a layout difference, but the two u32 hold the same bytes either way. `JobManager.cs:642-643` writes its offset first and the skill id second, and the captures have 1 then 2, so the values look right as sent. This is inferred until a PC consumer is read. Swapping the wire on the current evidence could break skills.
4. **`Client.cs:92` comment against the code.** It says the Camellia cipher's complaint is a `ResponseErrorException`; `Camellia.cs:31,75` throws `ArgumentException`.
5. **`ClientChallengeHandler` in both servers.** The `if (challenge.Error)` branch cannot run, because `HandleChallenge` throws first on a null key (R05).
6. **`tasks.md` and the brief against this role.** They give the baseline to a role that may not build. See Baseline.

## 7. Questions for IDA (T003), PC 03040008

1. Does the RES dispatch match a pending request? What does a second identical RES do (F06)? Take one error-showing handler and read it.
2. 0.1.2: does anything consume `OneTimeToken` after reader `0x804a50`, and what on empty (W01)?
3. 3.0.16 reader `0x889ac0`: the consumer of the count at `this+36`; can a read past the frame end fault or return stale bytes (W03, F02)?
4. `nPacket::Read_*` at the end of a buffer in general: what follows an over-read?
5. 27.8.16: the consumer of the u8 (W02). 62.1.2 reader `0x777b00`: consumers of the first and third u32 (W05). 19.28.2 reader `0x76f820`: who reads `+8`, `+0xc` (W06). Enemy preset `+27`, `+28` (W15).
6. Login 5.3.16 handler `0x8874b0` (no IDA function there: disassemble at the address): does it read Error (D08)?
7. Frame size limit of the receive path `0x9d6d20` (F03); does it use the counter (F04)? Does the client verify `OpenHash` (F12)?
8. `nPacket::Read_MtString` `0x8bc5b0` above 0x800: truncate, fail or drop (F09)?
9. 11.13.2 handler: the layout behind `OnPacket_QUEST_GET_RECOMMENDED_QUEST_INFO_LIST_RES` (T05).

## 8. Next package: harness and tests

**Tests.** xunit 2.9.3, with references to Cli, Client, GameServer and Server. Three shapes:

- Inline bytes: `EntitySerializer.Get<T>().Read(new byte[] {...})` (`PacketUnderstanderHasLoggedInTest.cs`).
- Binary fixture and round trip: `TestUtils.GetTestPath("S2CLobbyJoinResTest.bin")` under `TestFiles/`, then Read, Write and compare (`S2CLobbyJoinResTest.cs`).
- Capture: YAML fixture plus key through `PacketCommand` (`PacketCommandTest.cs`, three cases; `TestDecryptPcap85SplitPacket` asserts 4 pcap packets give 32).

No test constructs a `ClientHandle` or a handler with a client. `Client.Send` is not virtual, so F06, F07, F08 and D06 need a seam; T004 must add one in the smallest way. `PacketFactory` is testable alone, with `PacketIdResolver.GamePacketIdResolver`.

**Serializers over a stream.** `Program.cs:112` registers `PacketCommand`; `Run` (`PacketCommand.cs:25`) calls `DecryptPackets` (`:47`), then `GetAnnotatedPacketDump` (`:107`), whose YAML or JSON dump triggers the lazy parse. `ReadYamlPcap` is at `:174`.

For raw files the harness can skip all that: `PacketId.GetPacketId(serverType, g, id, sub)` (`PacketId.cs:19`), `EntitySerializer.Get(PacketId)` (`EntitySerializer.cs:1987`), then `ReadObj(IBuffer)` and `WriteObj(IBuffer, object)` (`:2051-2052`), comparing `buffer.Position` with the file. Traps:

- Server type comes from the `C2L_`/`L2C_` prefix of the raw name, since login and game reuse ids.
- The first packets have no header.
- The raw names come from the patched CLI (8 renames), and the file extension `<g>_<id>_<sub>` is the safe key.
- F05 throws on Error != 0 unless guarded; report these apart.
- Padding is not zero and not part of the body, so compare up to the read position only, and expect a fit to prove little where slack exceeds a field.
- Re-encoding S2C compares what the emulator would write with what the official server wrote, while C2S only tests the reader.

## 9. Pull request conventions

The clone's `docs/` holds player and quest guides, with no contribution guide; no `CONTRIBUTING` or PR template was found. `git log upstream/develop --merges -20` shows `Merge pull request #1115 from RyanYappert/fix/hotfixes-08-19`, with branch names such as `fix/...` and `feat/...`, and 8 of the 20 merges are branch syncs, 12 are pull requests. Commit subjects are plain sentences ("Fix bad sql when deleting people from a blacklist."). PR bodies were not read: `gh pr view` is left to T006. CI only builds and tests.

## Not run

- `dotnet build`, `dotnet test`, `dotnet restore`: role limit, see Baseline.
- Any failing test the rows propose: `V` rows rest on reading only.
- The server, a client, a database, IDA: out of bounds per the brief.
- The PC readers and writers the reports cite: not re-read, only their reports.
- `Arrowgene.Buffers` and `Arrowgene.Networking` behaviour: DLLs only, not disassembled. Memory and time in R01, R02, R08 and F04's likelihood are inferred.
- Bodies of the 517 handlers: only those named in rows.
- Comparison of server layouts for ids outside the reports: that is the T002 differential.

## Sources

Server paths above are at `e2411fe8f9`. In this repository: `docs/reference/arrowgene-cli-patches.md`, `packet-wire-format.md`, `packet-ids.md`, `packet-handler-tables.md`, `packet-pattern-format.md`, `packet-open-questions.md`; `docs/explanation/wire-protocol.md`, `two-packet-decodings.md`; `packets/tools/arrowgene-cli.patch`; `packets/patterns/03040008/`; the sections of specs 005, 006 and 008 named above; `specs/008-remaining-packets/research/T001-triage.tsv`; `research/03040008/ida-transfer/dumps/pc-ida.jsonl`. `packets/decrypted_json/` was read only for `ocdImmuneLvCount` in `*.35_9_16.json` (763 files, 0 above 0).

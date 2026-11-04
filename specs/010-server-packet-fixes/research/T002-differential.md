# 010 T002: baseline and the differential, client 03040008

Server `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Clean`, `develop` at `e2411fe8f9134fedd2b78f0db0bc561cadac98ce`. Harness: local branch `harness/differential`, commit `7d114a556b7652f718c628311973733dc34f7eb3`, never pushed. Input: `packets/decrypted_raw/` and `packets/decrypted_json/` in this repository at base `ec22aea482a`, read only. Date 2026-11-04.

Every id is in `T002-per-id.tsv`; the smallest capture per id and class, with the server line where a read could be traced, is in `T002-examples.tsv`.

**A divergence below is a candidate for the PC-code package (T003), not yet an error.** Captures come from the official server, so this tests the emulator's reading against someone else's bytes. Capture evidence alone is at most `I` (`spec.md`, Method 2). No IDA was used.

## 1. Baseline

Unpatched `develop`, `e2411fe8f9`, `DOTNET_CLI_TELEMETRY_OPTOUT=1`, dotnet 10.0.403.

| Command | Exit | Warnings | Errors | Tests |
| --- | --- | --- | --- | --- |
| `dotnet build Arrowgene.DragonsDogmaOnline.sln` | 0 | 521 | 0 | |
| `dotnet test Arrowgene.DragonsDogmaOnline.sln` | 0 | | | 52 passed, 0 failed, 0 skipped, of 52 |
| `dotnet build Arrowgene.DragonsDogmaOnline.sln --configuration Release` | 0 | 521 | 0 | |
| `dotnet test Arrowgene.DragonsDogmaOnline.sln --configuration Release --no-restore --no-build` | 0 | | | 52 passed, 0 failed, 0 skipped, of 52 |

No test fails on develop, so none needs a database or anything else this machine lacks. `git status --short` afterwards: 0 lines. CI names no solution file (`dotnet build --configuration Release`); here the solution was named, as the brief says.

## 2. Result

| Measure | Count |
| --- | --- |
| Captures run | 160,615 of 160,615: **all of them** (section 7) |
| Ids with a capture, per server type | 587 rows, 577 distinct `g.h.s` (10 are used by both login and game) |
| With a server structure, so with a verdict | 517 |
| Captured with no server structure: no verdict | 70 (1,544 captures) |
| Server structure with no capture: no verdict | 734 |
| Rows in `T002-per-id.tsv` | 1321 = 587 + 734 |
| Patterns | 595 files, 585 distinct ids: 577 captured, 8 not (`2.14.16`, `2.21.16`, `6.24.16`, `6.26.16`, `9.0.2`, `11.120.16`, `35.8.16`, `35.12.16`). No captured id lacks a pattern |
| Reads that returned, outside `Error != 0` | 159,008 |
| **Exceptions outside `Error != 0`** | **0: no id throws on a capture with Error 0** |
| Headerless first packets | 250 (`1.0.1`, `1.1.16` login; `44.0.1`, `44.1.16` game) |
| Re-encode equal | 158,719 of 159,008 |
| JSON leaves equal, compared to the end | 35,843 of 36,886 |
| JSON compared only up to a blob | 122,122 (section 8) |
| JSON missing | 0 |

| Class | Rows |
| --- | --- |
| `agrees` | 494 |
| `reader throws` | 0 |
| `reader too long` | 1 |
| `reader too short` | 3, plus 2 headerless |
| `re-encode differs` | 4 |
| `values differ, other width` (added: section 7) | 10 |
| `values differ, same width` | 0 |
| `Error != 0 apart` (every capture of the id) | 3, plus 13.3.2 in part |

A row takes its worst class; `class_counts` in the TSV has the split. Of the 494 that agree, 138 have under 5 captures, 75 of them just 1.

23 ids diverge. That few is plausible, since the server's layouts were played against real clients, but this is inferred. The `V` rows of T001 that captures can test all hold (section 5).

## 3. New ids, never named in T001

Offsets are file offsets (the body starts at 9, except in headerless raws). Paths are under `packets/decrypted_raw/`. Each is `I` until T003 reads the PC code.

| Id | Reading | Counts | Smallest example | Server |
| --- | --- | --- | --- | --- |
| 62.33.2 `S2C_SEASON_DUNGEON_GET_SOUL_ORDEAL_REWARD_LIST_RES` | **The writer sends `BuffId` twice and never `Level`**: the reader takes `Level` from the fourth u32, the writer puts `BuffId` there. In the smallest capture the official fourth u32 reads 1, 4, 1, 4, 1 beside the names `...Lv.1`, `...Lv.Max`, and the buff ids are 10, 18, 1, 42, 66. A served client gets the buff id in that slot. `EpitaphRoadManager.cs:595` fills `BuffRewards`, with `Level` set (`EpitaphRoadAsset.cs:36`). What the client does with the value is for T003: PC list reader `0x779420`. | 21 captures; fit 21, re-encode equal 0/21, JSON equal 21/21 | `stream85-marked.pcapng_tcp-stream-11/67364_S2C_SEASON_DUNGEON_GET_SOUL_ORDEAL_REWARD_LIST_RES_2019-11-18T11_32_39.1070311-08_00.62_33_2`, 288 bytes, file offset 98: `0100000061000000120021E78AB6E685` | `Arrowgene.Ddon.Shared/Entity/Structure/CDataSeasonDungeonBuffEffectReward.cs:24` (read `:33`) |
| 31.17.2 `S2C_CLAN_CLAN_SETTING_UPDATE_RES` | Server reads and writes a bool after the RES header; the official body has only the header (pattern: PC reader `0x8043c0`, V). The 38 differences are padding bytes the reader took as a bool, then wrote back as 1. A served client gets 1 excess byte, probably harmless. | 42 captures; fit 42, re-encode equal 4/42, JSON equal 0/42 | `stream41-wildhunt-royalcook-marked.pcapng_tcp-stream-12/10106_S2C_CLAN_CLAN_SETTING_UPDATE_RES_2019-08-22T12_31_09.0030570-07_00.31_17_2`, 32 bytes, file offset 17: `BD20B8F80020B8F800000000000000` | `Arrowgene.Ddon.Shared/Entity/PacketStructure/S2CClanClanSettingUpdateRes.cs:21,28` |
| 31.17.1 `C2S_CLAN_CLAN_SETTING_UPDATE_REQ` | Reader takes nothing; the client writes a bool (pattern: PC writer `0x823a80`, V). Unread bytes are harmless, but the client's setting is ignored: `ClanClanSettingUpdateHandler.cs:21` answers `false` whatever was sent. Read with the row above, the bool seems to belong on the request (inferred). | 42 captures; fit 42, re-encode equal 42/42, JSON equal 0/42 | `stream10-musicplayer-marked.pcapng_tcp-stream-8/10192_C2S_CLAN_CLAN_SETTING_UPDATE_REQ_2019-07-15T09_48_31.0174610-07_00.31_17_1`, 16 bytes, file offset 9: `00000000393045` | `Arrowgene.Ddon.Shared/Entity/PacketStructure/C2SClanClanSettingUpdateReq.cs:20` |
| 11.4.2 `S2C_QUEST_GET_LOT_QUEST_LIST_RES` | Reader drops both values: `ReadUInt32(buffer);` and `ReadEntityList(...)` assign nothing, so a re-encode writes 0 and an empty list. Same kind as W17: the wire agrees (JSON 20/20). CLI and annotated dumps only, no effect on a served client. | 20 captures; fit 20, re-encode equal 0/20, JSON equal 20/20 | `stream21-failedlogin-marked.pcapng_tcp-stream-48/13012_S2C_QUEST_GET_LOT_QUEST_LIST_RES_2019-07-25T12_30_52.0389950-07_00.11_4_2`, 32 bytes, file offset 20: `0100000000000003A70005A2` | `Arrowgene.Ddon.Shared/Entity/PacketStructure/S2CQuestGetLotQuestListRes.cs:32-33` |
| 10.13.16 `S2C_SWITCH_STORAGE_NTC` | The id of T001's D02, shown by real captures: `CDataSwitchStorage` is unregistered, so the reader stops after the count while the elements remain. No server sender (T001), so CLI only. | 2 captures; fit 2, re-encode equal 2/2, JSON equal 0/2 | `stream85-marked.pcapng_tcp-stream-11/139320_S2C_SWITCH_STORAGE_NTC_2019-11-18T13_33_43.7191450-08_00.10_13_16`, 32 bytes, file offset 18: `01000A2C000000060021559B0000` | `Arrowgene.Ddon.Shared/Entity/PacketStructure/S2CItemSwitchStorageNtc.cs:35`; no `Create` in `EntitySerializer.cs` |
| 11.60.16 `C2S_QUEST_PRT_READY_SET_RETURN_SESSION_NTC` | T001 names this id only for its source (T02); the layout difference is new. Reader takes nothing; the pattern has a bool. Unread, harmless unless the handler should use it. | 7 captures; fit 7, re-encode equal 7/7, JSON equal 0/7 | `stream85-marked.pcapng_tcp-stream-11/106978_C2S_QUEST_PRT_READY_SET_RETURN_SESSION_NTC_2019-11-18T12_31_34.5952050-08_00.11_60_16`, 16 bytes, file offset 9: `0007D640010015` | `Arrowgene.Ddon.Shared/Entity/PacketStructure/C2S_QUEST_11_60_16_NTC.cs:21` |
| 63.11.16 `S2C_63_11_16_NTC` | T001 T04 says the class has a StageNo where the PC writes nothing; the one capture agrees: the reader takes 4 padding bytes as StageNo (3110). Its only sender is under `#if false`. | 1 capture; fit 1, re-encode equal 1/1, JSON equal 0/1 | `stream85-marked.pcapng_tcp-stream-11/139354_S2C_63_11_16_NTC_2019-11-18T13_33_49.8446080-08_00.63_11_16`, 16 bytes, file offset 9: `00000C2600F041` | `Arrowgene.Ddon.Shared/Entity/PacketStructure/C2S_63_11_16_NTC.cs:28` |
| 13.3.2, 19.1.2, 19.2.2 | Carry `Error != 0`: section 4. T001 named EnemyKill and the two acquirable lists by structure (C1), not by id | | section 4 | `EntitySerializer.cs:2317` |

**Worth attention first: 62.33.2.** It is the only new finding where a served client receives a wrong value in a field the official server fills. It is one word at `CDataSeasonDungeonBuffEffectReward.cs:24`, and it reaches players through Epitaph Road's soul ordeal rewards.

## 4. `Error != 0` (F05)

63 of 13,901 RES captures, on 4 ids. All 63 throw `EndOfStreamException` under `ReadServerResponse`, as T001 expected. These are not layout findings.

| Id | Name | Error != 0 | Of | Error code | Body bytes (file minus 9) |
| --- | --- | --- | --- | --- | --- |
| 13.3.2 | `S2C_INSTANCE_ENEMY_KILL_RES` | 2 | 414 | 16016 | 7 |
| 18.0.2 | `S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES` | 41 | 41 | 47003 | 23 |
| 19.1.2 | `S2C_SKILL_GET_ACQUIRABLE_SKILL_LIST_RES` | 4 | 4 | 15005 | 7 |
| 19.2.2 | `S2C_SKILL_GET_ACQUIRABLE_ABILITY_LIST_RES` | 16 | 16 | 15005 | 7 |

For the design in T001 § 1.2:

- These are exactly the 4 structures the CLI patch guards (C1), so that patch is complete for these captures. T001's "only the 18.0.2 row is capture-checked" can close.
- A fixed-width read of Result alone does not cure this. The 22 bodies of 7 bytes hold Error and 3 bytes of padding, so a u32 Result still runs past the end. The 41 of 18.0.2 hold 23 bytes and have room.
- A stop right after Error reads all 63 without an exception, and that is where the client stops. The count does not decide between a guard per structure and a return value from `ReadServerResponse`. It does show that captures name only 4 of 492 call sites, so a guard on those 4 covers what was seen and not the rest.

## 5. Reconciliation with `T001-candidates.tsv`, W rows

`no signal` means the row's claim is about order or names at equal widths. This test compares by position over the same bytes, so it cannot see those: they agree by construction. That is neither a confirmation nor a refutation.

| Row | Id | Differential | Reading |
| --- | --- | --- | --- |
| W01 | 0.1.2 (Game) | **confirmed** | 42/42 `reader too long`. u16 at body+8 takes `01 00`, then the string length comes out wrong and `ReadString` returns short with no exception. Re-encode differs at body+8 in all 42. Official: 1 byte. The effect on a served client stays I. |
| W02 | 27.8.16 | **confirmed** | 8/8 stop 1 byte before the pattern's end (the u8). All 8 captures hold 1 element, so the shift at 2 or more is not exercised. |
| W03 | 3.0.16 (Login) | **confirmed** | 410/410 stop 4 bytes before the pattern's end. T001's 410/410 fit is the pattern's: the server's reader fits 328 and leaves 16 or 17 bytes on 82 (41 each). |
| W04 | 2.1.2 (Login) | difference confirmed, width not settled | 42/42 read 2 bytes past the pattern's end; 40 differ only because those 2 bytes are non-zero padding. Both widths pad to the same block, so captures cannot decide. It rests on the PC by report. |
| W05 | 62.1.2 | no signal | 4/4 agree. Same widths: an id in the wrong slot is invisible to this test, and re-encode copies what was read, not what the handler would set. |
| W06 | 19.28.2 | no signal | 41/41 agree. Same widths, as T001 says. Nothing here argues for swapping the wire. |
| W07 | 10.14.16 | consistent | 1/1 agrees: bytes equal for 1 element, as T001 says. |
| W08 | 14.11.16 | **confirmed** | 57/57 read 0 bytes, pattern 4. |
| W09 | 0.1.1, 0.5.1 (Game) | **confirmed** | 42/42 stop 4 bytes early, 41/41 stop 5 early. |
| W10 | 1.0.1 (Login), 44.0.1 (Game) | **confirmed** | Headerless, read from offset 0: 42/42 stop at 279, 83/83 at 278, pattern 324. Constant positions, so no early 0 in these ciphertexts. Re-encode on login writes 278, one fewer (the terminator). |
| W11 | 1.0.2 (Login), 44.0.2 (Game) | **confirmed** | 42/42 and 83/83: reader takes 26 bytes (`PasswordEncSize` 16), writer writes 74, official body 72: 2 excess. Reader leaves more than 15 bytes, so `reader too short`. |
| W12 | 30.0.2 | no capture of the element | 10/10 agree, but `CraftProgressList` has count 0 in all 10, so the disputed element never occurs. |
| W13 | 28.x | no capture | `CDataGPCourseAvailable`: no packet structure reaches it (dead code, as T001 says). |
| W14 | 50.1.1 | **confirmed** | 59/59 stop 1 byte early (the trailing bool). |
| W15 | 13.0.2, 13.40.16 | no signal | 685/685 and 41/41 agree. Same widths: swapped names are invisible. |
| W16 | 11.45.16 | no signal | 1/1 agrees. Same widths. |
| W17 | 13.16.2 | **confirmed** | 1/1: reader takes 148 bytes, re-encode writes 12, since the list is dropped. JSON equal, so the wire agrees. |
| W18 | 13.8.1 | consistent | 51/51 agree. byte and bool have one width; not an error, as T001 says. |
| W19 | 34.0.1 | **refuted** (the lead) | 1/1 agrees, so the capture backs T001's correction. |
| W20 | 45.0.2 | **refuted** as a wire fault | 81/81 agree. |
| W21 | 20.0.2 | no signal | 18/18 agree. A flag's polarity is not a layout. |
| W22 | 11.10.2 | no signal | 3/3 agree; here the server's reading matches the pattern's bytes. Order of same-width bools is invisible. |

Other T001 rows the run touches:

- **D01**: 35.9.16 (763) and 35.13.16 (25) agree: the count is 0 in all, so captures do not exercise it. Section 6 does.
- **D02**: see 10.13.16 above.
- **T04**: see 63.11.16 above. **T05**: 11.13.2 has no capture, so it stays a lead.
- **R04, R09**: T001 left `StreamBuffer` at end of data unread. Measured (`Differential probe`):

| Call | Result |
| --- | --- |
| `ReadByte`, `ReadUInt16`, `ReadUInt32` past the end | `EndOfStreamException` |
| `ReadBytes(4)` over 2 bytes | **returns 2 bytes, no exception** |
| `ReadString(4)`, `ReadMtString` with length 0xFFFF, over too few bytes | **returns short, no exception** |
| `ReadBytes(-1)` | `ArgumentOutOfRangeException` |
| `ReadBytes(0x7FFFFFFF)` over 2 bytes | `OutOfMemoryException`, array dimensions |

So a bad length does not always end in an exception: 0.1.2 reads wrong for that reason and reports nothing. R09's bound holds, because the next fixed-width read throws. For R04: a length just under the array limit was not tried and may really allocate; that remains inferred.

## 6. Failing tests for T001's claims

`Arrowgene.Ddon.Test/T002ProofTests.cs` on the scratch branch. Run: `dotnet test Arrowgene.Ddon.Test/Arrowgene.Ddon.Test.csproj --filter FullyQualifiedName~T002ProofTests`. Each states the wanted behaviour, so failing is the proof. Total 4, failed 4.

| Test | Claim | Failure, verbatim |
| --- | --- | --- |
| `D01_CDataOcdImmuneLv_has_a_registered_serializer` | D01 | `CDataOcdImmuneLv is not registered, so lists of it write no elements and read no bytes` |
| `D01_a_list_of_two_consumes_its_elements` | D01 | `Assert.All() Failure: 2 out of 2 items in the collection did not pass.` / `Assert.NotNull() Failure: Value is null` |
| `R01_a_huge_count_ends_at_the_end_of_the_data` | R01 | `35.9.16 with ocdImmuneLv count 0xFFFFFFFF, 0x20000000 heap: exit 11 after 1063 ms: OutOfMemoryException after 675 ms` |
| `F06_a_handled_error_sends_one_response` | F06 | `Assert.Equal() Failure: Values differ` / `Expected: 1` / `Actual:   2` |

- **R01** ran in a child process under a 512 MiB heap limit and a 15 s kill. It never reaches the end of the data: the loop adds nulls until the limit stops it, in 675 ms for 512 MiB. A server with more memory runs longer on its single default lane. The time for the full 16 GB was not run.
- **F06: the seam is not trivial, and the claim is now proved anyway.** No `ClientHandle` exists without a socket: `ClientHandle` is a sealed struct, `Send` is not virtual, and `Client`'s constructor reads `Identity`, which throws on a default handle (`ObjectDisposedException`). `PacketHandler`'s constructor reads `server.Database`. The test makes `Client.SendRaw` virtual, **on the scratch branch only**, and skips both constructors with `GetUninitializedObject`. T004 needs a real seam: a virtual `SendRaw` is one word, plus a way to build a `Client` and a handler without a server. This shows that two frames leave the server. What a client does with the second stays T003's question.

## 7. Method, and where it departs from the brief

The harness is `Arrowgene.Ddon.Differential` on the scratch branch: a console project on `Arrowgene.Ddon.Shared` using `PacketId.GetPacketId`, `EntitySerializer.Get(PacketId)`, `ReadObj` and `WriteObj`. Output went to the session scratchpad; only the two TSVs were copied here. Rerun: `dotnet <dll> run --list <fd list> --root D:/ddon-data --out <dir> [--per-id 50]`, with `DOTNET_GCHeapHardLimit=0x300000000`. A watchdog ends the run if one read takes over 120 s; it never fired.

Departures:

1. **Every capture, not a sample.** The whole set takes 3 s of reading, so a stratified sample had nothing to save. The sampler exists (`--per-id`, fixed seed 10002, round robin over stream folders) and was used only to develop.
2. **The server's leaves are its reads, not a walk of the object's fields.** A `DispatchProxy` over `IBuffer` records each `Read*` in wire order with its offset and width. Declaration order is not wire order, and this needs no reflection over 1,254 classes. A read the object then drops is caught by re-encode (W17, 11.4.2).
3. **List counts:** a count is a leaf on both sides here: the server's `ReadUInt32` and the JSON's `count` (`{count, entries}`). String lengths the same: `{length, value}`. So neither needs inferring.
4. **Headerless packets** are outside every verdict, as the brief says, and their classes carry the prefix `headerless`. They were still read from offset 0, because W10 cannot be answered otherwise.
5. **An added class.** `values differ, other width`: it fits by the 15-byte rule but ends elsewhere than the pattern, or its leaves diverge with a different end. Without it W08, W09 and W14 would carry the label `same width`, which they are not.
6. **`values differ, same width` is empty, and has to be.** Reading the same bytes at equal widths gives equal values, so names and order cannot show; the rows it was meant for appear as `no signal` in section 5. All the first hits in this class were comparison artefacts, now handled:

| Rule | Effect |
| --- | --- |
| Integers compare modulo the server's read width | signedness is no difference |
| A whole float prints as an integer in the JSON | compare numerically; a true integer against a float compares by bits |
| Enums export as `NAME::VALUE` | numbers from the 420 values in the patterns' enum blocks |
| `NAME::???` (value outside the enum) | compares equal, unverified: 2,232 leaves, `COMMAND_CHECK_LIST`, `ORDER_CONDITION_TYPE` |
| `CategoryName` beside `Category` (a view, `[[export]]`, no bytes) | dropped: 192 leaves |
| A byte run against a JSON string; a byte not valid UTF-8 | by UTF-8 bytes; by ASCII skeleton |

Own code, since no library fits: the walk, the comparison and the classes. Libraries: `System.Text.Json`, `System.Reflection.DispatchProxy`, the server's own serializers.

## 8. What `agrees` does not say

- **Blobs.** On 6 ids the server takes bytes where the pattern decodes a structure: `2.0.2` (42), `3.3.16` (66,275), `3.4.16` (21,143), `6.23.16` (8), `6.25.16` (34,607), `9.1.1` (47): 122,122 captures, 76% of the run. Values past the blob's start were not compared. Their end position equals the pattern's, and re-encode is equal.
- **Empty lists.** A list that is empty in every capture says nothing of its element (W12). This was not counted per id.
- **Re-encode tests the serializer, not the handler.** It copies what was read, so a constant a handler sets (W05's 40) is invisible.
- **A fit is weak** (`docs/explanation/packet-decoding-method.md`). The pattern's end sharpens it here, but the pattern is itself not proof.
- **No capture, no verdict**: the 734 structures in section 9.

## 9. Ids with no verdict

**Captured, no server structure (70).** Per T001 § 3, a request here takes `FallbackHandler` or a handler with a canned dump; this was not checked per id:

10.0.16, 10.9.1, 10.9.2, 11.7.16, 11.23.1, 11.23.2, 11.38.1, 11.38.2, 11.68.16, 11.83.16, 11.88.16, 11.95.16, 11.103.16, 11.117.16, 11.118.16, 16.6.1, 16.6.2, 28.3.1, 28.3.2, 28.6.1, 28.6.2, 28.7.1, 28.7.2, 28.8.1, 28.8.2, 28.9.1, 28.9.2, 28.23.1, 28.23.2, 28.24.16, 28.34.1, 28.34.2, 29.23.16, 39.0.1, 39.0.2, 39.1.1, 39.1.2, 44.1.16, 57.0.1, 57.0.2, 58.3.1, 58.3.2, 58.4.1, 58.4.2, 58.5.1, 58.5.2, 58.7.1, 58.7.2, 58.8.1, 58.8.2, 58.9.1, 58.9.2, 59.0.1, 59.0.2, 59.4.1, 59.4.2, 59.8.1, 59.8.2, 59.9.1, 59.9.2, 62.27.16, 63.3.16, 72.0.1, 72.0.2, 72.1.16, 72.2.1, 72.2.2, 72.3.1, 72.3.2, 1.1.16 (login).

**Server structure, no capture (734):**

0.4.16, 0.9.16, 0.11.16, 0.12.16, 1.9.1, 1.9.2, 1.10.16, 2.2.1, 2.2.2, 2.3.16, 2.4.16, 2.8.16, 2.9.16, 2.10.16, 2.11.16, 2.14.16, 2.17.1, 2.17.2, 2.21.16, 2.22.1, 2.22.2, 2.23.1, 2.23.2, 2.33.16, 2.34.16, 2.35.16, 2.36.16, 2.37.16, 2.39.1, 2.39.2, 2.39.16, 2.40.1, 2.40.2, 4.0.1, 4.0.2, 6.1.16, 6.2.1, 6.2.2, 6.3.1, 6.3.2, 6.3.16, 6.4.1, 6.4.2, 6.5.1, 6.5.2, 6.5.16, 6.6.1, 6.6.2, 6.6.16, 6.11.1, 6.11.2, 6.11.16, 6.12.1, 6.12.2, 6.12.16, 6.13.1, 6.13.2, 6.13.16, 6.15.16, 6.16.16, 6.17.16, 6.19.16, 6.20.16, 6.21.16, 6.22.16, 6.24.16, 6.26.16, 8.0.1, 8.0.2, 8.1.1, 8.1.2, 8.4.1, 8.4.2, 8.6.1, 8.6.2, 8.7.1, 8.7.2, 8.10.1, 8.10.2, 8.11.1, 8.11.2, 8.13.1, 8.13.2, 8.14.1, 8.14.2, 8.15.1, 8.15.2, 8.16.1, 8.16.2, 8.17.1, 8.17.2, 8.19.1, 8.19.2, 8.19.16, 8.21.1, 8.21.2, 8.22.1, 8.22.2, 8.23.1, 8.23.2, 8.24.1, 8.24.2, 8.25.1, 8.25.2, 8.25.16, 8.26.1, 8.26.2, 8.26.16, 8.27.1, 8.27.2, 8.29.1, 8.29.2, 8.38.16, 8.40.16, 8.41.16, 10.1.1, 10.1.2, 10.5.1, 10.5.2, 10.8.1, 10.8.2, 10.11.16, 10.16.1, 10.16.2, 10.17.1, 10.17.2, 10.20.1, 10.20.2, 10.21.1, 10.21.2, 10.22.1, 10.22.2, 10.23.1, 10.23.2, 10.24.1, 10.24.2, 10.25.1, 10.25.2, 11.1.16, 11.2.16, 11.6.1, 11.6.2, 11.9.16, 11.11.1, 11.11.2, 11.13.1, 11.13.2, 11.16.1, 11.16.2, 11.17.1, 11.17.2, 11.18.1, 11.18.2, 11.20.16, 11.21.16, 11.22.1, 11.22.2, 11.22.16, 11.25.1, 11.25.2, 11.25.16, 11.26.16, 11.27.16, 11.28.1, 11.28.2, 11.29.1, 11.29.2, 11.33.1, 11.40.1, 11.40.2, 11.40.16, 11.42.16, 11.43.1, 11.43.2, 11.43.16, 11.44.1, 11.44.2, 11.58.1, 11.58.2, 11.58.16, 11.59.1, 11.59.2, 11.59.16, 11.61.1, 11.61.2, 11.87.16, 11.92.16, 11.93.16, 11.94.16, 11.102.16, 11.105.16, 11.107.16, 11.109.16, 11.114.16, 11.119.16, 11.120.16, 11.124.1, 11.124.2, 11.124.16, 11.125.1, 11.125.2, 11.125.16, 11.127.1, 11.127.2, 12.2.1, 12.2.2, 12.4.1, 12.4.2, 12.6.1, 12.6.2, 12.7.1, 12.7.2, 12.8.1, 12.8.2, 12.10.16, 12.11.1, 12.11.2, 12.12.1, 12.12.2, 13.12.16, 13.14.1, 13.14.2, 13.15.1, 13.15.2, 13.30.16, 13.33.16, 13.34.16, 13.35.16, 13.36.16, 14.0.1, 14.0.2, 14.6.1, 14.6.2, 14.7.1, 14.7.2, 14.13.16, 16.1.1, 16.1.2, 16.1.16, 16.2.1, 16.2.2, 16.2.16, 16.3.1, 16.3.2, 16.3.16, 16.4.1, 16.4.2, 16.5.1, 16.5.2, 16.5.16, 17.1.1, 17.1.2, 17.2.1, 17.2.2, 18.1.1, 18.1.2, 18.1.16, 18.2.1, 18.2.2, 18.2.16, 18.3.1, 18.3.2, 18.3.16, 18.4.16, 19.3.1, 19.3.2, 19.4.1, 19.4.2, 19.5.1, 19.5.2, 19.6.1, 19.6.2, 19.7.1, 19.7.2, 19.8.1, 19.8.2, 19.9.1, 19.9.2, 19.10.1, 19.10.2, 19.11.1, 19.11.2, 19.12.1, 19.12.2, 19.13.1, 19.13.2, 19.14.1, 19.14.2, 19.15.1, 19.15.2, 19.16.1, 19.16.2, 19.17.1, 19.17.2, 19.18.1, 19.18.2, 19.19.1, 19.19.2, 19.20.1, 19.20.2, 19.21.1, 19.21.2, 19.22.1, 19.22.2, 19.23.1, 19.23.2, 19.24.1, 19.24.2, 19.25.1, 19.25.2, 19.26.1, 19.26.2, 19.27.1, 19.27.2, 19.32.1, 19.32.2, 19.33.1, 19.33.2, 19.34.1, 19.34.2, 19.35.1, 19.35.2, 19.36.1, 19.36.2, 19.37.1, 19.37.2, 19.39.1, 19.39.2, 19.40.1, 19.40.2, 19.41.16, 19.42.16, 19.43.16, 19.44.16, 19.45.16, 19.46.16, 19.47.16, 19.48.16, 19.49.16, 19.50.16, 21.0.1, 21.0.2, 21.1.1, 21.1.2, 21.2.16, 21.5.1, 21.5.2, 21.6.1, 21.6.2, 23.1.1, 23.1.2, 23.2.1, 23.2.2, 23.7.1, 23.7.2, 23.10.1, 23.10.2, 23.14.16, 24.0.1, 24.0.2, 24.1.1, 24.1.2, 24.4.16, 24.5.16, 25.1.1, 25.1.2, 25.2.1, 25.2.2, 25.3.1, 25.3.2, 25.4.1, 25.4.2, 25.6.16, 26.0.1, 26.0.2, 26.2.1, 26.2.2, 26.3.1, 26.3.2, 26.5.1, 26.5.2, 26.6.1, 26.6.2, 26.10.1, 26.10.2, 26.16.1, 26.16.2, 28.1.1, 28.1.2, 28.27.16, 28.33.1, 28.33.2, 29.1.16, 29.4.1, 29.4.2, 29.4.16, 29.5.1, 29.5.2, 29.6.1, 29.6.2, 29.6.16, 29.7.1, 29.7.2, 29.7.16, 29.8.1, 29.8.2, 29.9.1, 29.9.2, 29.10.1, 29.10.2, 29.11.1, 29.11.2, 29.18.16, 30.1.1, 30.1.2, 30.2.1, 30.2.2, 30.3.1, 30.3.2, 30.4.1, 30.4.2, 30.5.1, 30.5.2, 30.6.1, 30.6.2, 30.7.1, 30.7.2, 30.8.1, 30.8.2, 30.9.1, 30.9.2, 30.14.1, 30.14.2, 30.17.1, 30.17.2, 30.18.16, 30.19.16, 30.20.16, 30.21.16, 31.1.1, 31.1.2, 31.2.1, 31.2.2, 31.2.16, 31.3.1, 31.3.2, 31.5.1, 31.5.2, 31.6.1, 31.6.2, 31.10.1, 31.10.2, 31.12.1, 31.12.2, 31.12.16, 31.13.1, 31.13.2, 31.14.1, 31.14.2, 31.14.16, 31.15.1, 31.15.2, 31.15.16, 31.18.1, 31.18.2, 31.18.16, 31.19.1, 31.19.2, 31.22.1, 31.22.2, 31.23.1, 31.23.2, 31.25.1, 31.25.2, 31.27.1, 31.27.2, 31.32.1, 31.32.2, 31.33.1, 31.33.2, 31.35.1, 31.35.2, 31.36.1, 31.36.2, 31.37.1, 31.37.2, 31.38.1, 31.38.2, 31.41.16, 31.42.16, 31.43.16, 31.44.16, 31.45.16, 31.46.16, 31.47.16, 31.48.16, 31.49.16, 31.50.16, 31.51.16, 31.52.1, 31.52.2, 33.1.1, 33.1.2, 33.1.16, 33.2.1, 33.2.2, 33.2.16, 33.3.16, 33.7.1, 33.7.2, 33.8.1, 33.8.2, 33.9.1, 33.9.2, 33.10.1, 33.10.2, 33.14.16, 33.18.16, 33.19.16, 34.3.1, 34.3.2, 34.3.16, 34.4.1, 34.4.2, 34.5.1, 34.5.2, 34.5.16, 34.8.1, 34.8.2, 34.9.1, 34.9.2, 34.10.1, 34.10.2, 34.12.1, 34.12.2, 34.12.16, 34.13.1, 34.13.2, 34.13.16, 34.15.16, 34.17.16, 34.18.16, 34.19.1, 34.19.2, 34.20.1, 34.20.2, 35.1.16, 35.2.16, 35.4.16, 35.10.1, 35.10.2, 35.10.16, 36.0.1, 36.0.2, 36.1.1, 36.1.2, 36.2.1, 36.2.2, 36.3.1, 36.3.2, 36.4.1, 36.4.2, 36.5.1, 36.5.2, 36.6.1, 36.6.2, 36.7.1, 36.7.2, 36.7.16, 36.8.1, 36.8.2, 36.9.1, 36.9.2, 36.11.1, 36.11.2, 37.3.1, 37.3.2, 37.4.1, 37.4.2, 37.5.1, 37.5.2, 37.5.16, 37.12.1, 37.12.2, 38.0.1, 38.0.2, 38.1.1, 38.1.2, 38.3.1, 38.3.2, 41.2.1, 41.2.2, 41.4.16, 41.6.1, 41.6.2, 41.7.16, 42.0.16, 49.0.1, 49.0.2, 49.1.1, 49.1.2, 51.1.1, 51.1.2, 51.3.1, 51.3.2, 51.4.1, 51.4.2, 52.2.1, 52.2.2, 52.3.1, 52.3.2, 52.4.1, 52.4.2, 52.5.1, 52.5.2, 52.5.16, 52.6.1, 52.6.2, 52.7.1, 52.7.2, 52.8.1, 52.8.2, 53.0.1, 53.0.2, 53.5.1, 53.5.2, 54.1.1, 54.1.2, 54.2.1, 54.2.2, 55.0.1, 55.0.2, 55.1.1, 55.1.2, 55.2.1, 55.2.2, 55.3.1, 55.3.2, 55.4.1, 55.4.2, 61.0.1, 61.0.2, 61.1.1, 61.1.2, 62.6.1, 62.6.2, 62.11.16, 62.19.1, 62.19.2, 62.21.1, 62.21.2, 62.25.1, 62.25.2, 62.28.16, 62.36.1, 62.36.2, 64.3.1, 64.3.2, 64.4.1, 64.4.2, 64.9.1, 64.9.2, 64.12.1, 64.12.2, 65.0.16, 65.4.1, 65.4.2, 66.0.1, 66.0.2, 66.2.1, 66.2.2, 66.3.1, 66.3.2, 66.4.1, 66.4.2, 66.5.1, 66.5.2, 66.6.1, 66.6.2, 67.0.1, 67.0.2, 67.1.1, 67.1.2, 67.2.1, 67.2.2, 67.3.1, 67.3.2, 69.0.1, 69.0.2, 69.1.1, 69.1.2, 69.3.1, 69.3.2, 69.4.1, 69.4.2, 71.1.1, 71.1.2, 71.2.1, 71.2.2, 71.2.16, 71.3.1, 71.3.2, 71.3.16, 71.4.1, 71.4.2, 71.5.1, 71.5.2, 71.5.16, 71.6.1, 71.6.2, 71.12.16, 71.13.16, 71.14.16, 71.15.16, 71.16.1, 71.16.2, 71.17.1, 71.17.2, 71.18.1, 71.18.2, 71.19.16, 71.20.1, 71.20.2, 71.21.1, 71.21.2, 71.21.16, 0.3.16 (login), 5.2.1 (login), 5.2.2 (login), 5.3.1 (login), 5.3.2 (login), 5.3.16 (login), 5.4.1 (login), 5.4.2 (login).

## Not run

- IDA and the PC code: out of bounds here, so every effect on a client above is a question for T003.
- A live server or client.
- `ReadBytes` just under the array limit (R04); the full 16 GB of R01.
- F05's fix, in any form.

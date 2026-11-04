# Arrowgene CLI patches

The local changes to `Arrowgene.Ddon.Cli` behind the annotated dumps and raw packets of client 03040008, each with the failure it removes, for a reader judging what those files can be trusted for. To build it, see [Patch the Arrowgene CLI](../how-to/patch-the-arrowgene-cli.md). A label in a code span names a report: [the key](packet-ids.md#report-labels).

## Build identity

The patched build sits in the clone `C:\Users\morph\Documents\GitHub\Sehkah\Arrowgene.DragonsDogmaOnline.Upstream` (branch `develop`, base `e2411fe8`, patches uncommitted), net10.0, Debug, built 2026-11-02. The hashes below match that clone's files on 2026-11-04. The other clone, under `D:\GitHub\Sehkah\`, holds no build.

| File | SHA-256 |
| --- | --- |
| `Arrowgene.Ddon.Cli.dll` | `78e33c4a9d544a02ec967482510771aa3aa54a2aaa6850244cc231b91f486052` |
| `Arrowgene.Ddon.Cli.exe` | `d624bc12ef8f661d48e6c104d2ae40a811d9663f260ba6de408d68f4b45ca344` |
| `Arrowgene.Ddon.Shared.dll` | `5d2455d51b2e1f0a0d482ab25d4743671885f23f8aabbefc2e51c377aad5ca6b` |

`packets/decrypted_raw/`, and the file names in `packets/decrypted_json/`, come from this build.

## Stop reading after a non-zero Error

`EntitySerializer.ReadServerResponse` reads `Result` as a `u16` whenever `Error != 0`, but servers keep writing the full response (`Error` and `Result` as `u32`, then the payload). Every field after `Result` is then read 2 bytes early: an empty list's count becomes a huge number, and parsing runs into the packet's block padding (`EndOfStreamException`). The Season 3 client does not read past a non-zero `Error` (for example `GROUP_CHAT_GET_MEMBER_LIST_RES` reader `0x809D80` in the PC 03040008 client), so the patches stop the same way:

```csharp
ReadServerResponse(buffer, obj);
if (obj.Error != 0) return obj;
```

| Patched file, under `Arrowgene.Ddon.Shared/Entity/PacketStructure/` | Packet | Observed error |
| --- | --- | --- |
| `S2CGroupChatGetMemberListRes.cs` | 18.0.2 | `0xB79B` ERROR_CODE_GROUP_CHAT_NOT_IN_GROUP in all 41 captures (for example stream85 tcp-stream-11, pcap 10290) |
| `S2CInstanceEnemyKillRes.cs` | | same pattern; captures not re-checked |
| `S2CSkillGetAcquirableSkillListRes.cs` | | same pattern; captures not re-checked |
| `S2CSkillGetAcquirableAbilityListRes.cs` | | same pattern; captures not re-checked |

Known limitation: the patched structures report `Result: 0` instead of the sent value, because `ReadServerResponse` consumed only two bytes of it.

## Patches in `PacketCommand.cs`

All in `Arrowgene.Ddon.Cli/Command/PacketCommand.cs`; the last three in `DecryptPackets`.

| Patch | Without it | What it does |
| --- | --- | --- |
| Debug log | a packet without a C# structure is silent | logs `No structure for packet: <name> <id>` at debug level |
| First packet under the fixed key (`T002c`) | both factories get the session key before the first packet, so the first packet of each direction holds wrong-key bytes | drops the up-front `SetCamelliaKey` calls, and switches each factory to the session key after its first resolved packet |
| Certificate notice relabel (`T003 §1, §15`) | the server's first packet carries the client challenge's name | labels the server factory's first resolved packet `S2C_CERT_GAME_SERVER_CERT_NTC` 44.1.16 (game) or `L2C_LOGIN_SERVER_CERT_NTC` 1.1.16 (login), source `Server`, counter 0 |
| One file per packet of a frame | the raw file name does not tell apart several packets of one id in one TCP frame, so each overwrites the one before | counts each name per frame first; the last packet keeps the unsuffixed name and each earlier one gets `_<n>`, its 1-based position among the frame's packets of that name, before the extension. Helpers `RawStem` and `RawExtension` build the two parts. The annotated dump code is unchanged |

The first packet of each direction is the server's RSA public key, and the client's `C2L_CLIENT_CHALLENGE_REQ` 1.0.1 or, on the game server, `C2S_CERT_CLIENT_CHALLENGE_REQ` 44.0.1. It is Camellia-256-CBC encrypted with the client's fixed key `f23e98HafJdSoaj80QBjhh23oajgklSa` and IV `$cbM6WP)aX=%J^zA`, which the `PacketFactory` constructor sets. The switch is safe for these captures because every first packet arrives in its own TCP segment (250/250, `T002c §3`).

The relabel follows the client's receive path (`0x9d6d20`), which dispatches the certificate notice under a synthesised header. Both ids are in the CLI's `PacketId.cs` (lines 1737 and 162). A helper `HeaderBytes` in `PacketCommand` keeps these two raw files header-less, as the client challenge is; `Packet.GetHeaderBytes()` itself is unchanged. The annotated dumps label them `Server #000000 (44.1.16) S2C_CERT_GAME_SERVER_CERT_NTC`, and do not try the client challenge structure on them.

## Names from code, in `PacketId.cs`

`Arrowgene.Ddon.Shared/Network/PacketId.cs` gives eight ids the name the client code backs, instead of Arrowgene's placeholder or contradicted one. Only the `Name` string changes: the C# fields keep their names, and Arrowgene's name moves to `originalName`. The rule: direction prefix, CLI group name, then the PS4 packet name without its direction, `NOTICE` -> `NTC` as the other names do, and `_NTC` appended where the PS4 name has no kind suffix (11.60.16).

| Id | Arrowgene's name | Name in the patched CLI | Evidence |
| --- | --- | --- | --- |
| 0.10.16 | `S2C_CONNECTION_0_10_16_NTC` | `S2C_CONNECTION_SESSION_STATUS_NTC` | `T003 § 9`, V by behaviour |
| 11.60.16 | `C2S_QUEST_11_60_16_NTC` | `C2S_QUEST_PRT_READY_SET_RETURN_SESSION_NTC` | `T005 § 25`, V by behaviour |
| 11.83.16 | `S2C_QUEST_11_83_16_NTC` | `S2C_QUEST_SET_QUEST_UNRELEASED_AREA_NTC` | `T005 § 31`, V by notice class |
| 11.95.16 | `S2C_QUEST_11_95_16_NTC` | `S2C_QUEST_FORT_DEFENSE_NTC` | `T005 § 35`, V by notice class |
| 11.103.16 | `S2C_QUEST_11_103_16_NTC` | `S2C_QUEST_PLAY_STOP_TIMER_NTC` | `T005 § 37`, V by notice class |
| 11.117.16 | `S2C_QUEST_11_117_16_NTC` | `S2C_QUEST_REWARD_BOX_LIST_NUM_NTC` | `T005 § 38`, V by behaviour |
| 14.10.16 | `C2S_WARP_WARP_START_NTC` | `C2S_WARP_WARP_END_NTC` | `T008 § 2.7`, V by call site (Arrowgene's name contradicted) |
| 14.11.16 | `C2S_WARP_WARP_END_NTC` | `C2S_WARP_14_11_16_NTC` | `T008 § 2.8`: PS4's WARP_END is 14.10.16, and no code name exists (a placeholder, which frees the name) |

Evidence for 14.10.16: the PC writer `0x840160` and PS4 `Send_C2S_WARP_END_NTC` are both called once, from `aStage::move_menu_warp`, after the same store, with the same empty body. PS4 has no WARP_START symbol.

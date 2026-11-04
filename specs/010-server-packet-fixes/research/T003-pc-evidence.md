# 010 T003: what the PC client does with each candidate

Client PC **03040008**. All addresses are VAs in `2022_01_29_DDO_DUMP_FIX.exe` as held by the `pc-handlers` database, private copy `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t003/2022_01_29_DDO_DUMP_FIX.exe.i64` (checked: 32-bit, image base `0x400000`). PS4 02020005 evidence comes from the private copy `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t003/DDOORBIS.elf.i64` (64-bit, base `0`), marked **PS4**, used only for names of consumers, never for a packet id. Server: `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Clean` `develop` at `e2411fe8f9`, read only. ddon-data base `7f6e5a98971`. Date 2026-11-04. Read-only: no annotation, rename or function creation.

`V` = read in PC code. `I` = inferred. A value from a capture is capture evidence, at most `I`, and is said so.

## Verdicts

| # | Id | Verdict | Effect on a served client | VA evidence | A fix would have to | Fix safe? |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **F06** | **error** `V` | The whole handler runs twice; there is no pending check. An ordinary error shows one dialog, because the second is dropped by the queue. On a request where the client asked to suppress the dialog once, the first RES uses up that flag and **the second RES shows the dialog the client meant to suppress** | `0x844be0`, `0x878860`, `0xbb3980`, `0x13ef380`, setters `0xc77fd8` etc. | Return after the send in `catch (ResponseErrorException)` | Yes. Nothing in the path read needs a second RES |
| 1b | F04 | **harmless** `V` (counter) | The receive path never compares the counter | `0x9d6eb6`-`0x9d6ef2`, `0x875b00`, `0x8758b0` | Nothing for the counter. A corrupted frame is a different question: not settled | n/a |
| 2 | **62.33.2** | **harmless** `V` | The fourth u32 reaches no consumer: buff id there has no effect | `0x779420`, getter `0x781fb0`, its 5 callers | Write `Level` (one word) | Yes; no client effect |
| 3 | **W01** 0.1.2 | **harmless** `V` | Bool reads 00, token reads as length 0 and succeeds; handler destroys both unread | `0x804a50`, `0x8bc5b0`, `0x7ce490` | Write a bool | Yes; same 1 byte as captures, token still unused |
| 4 | **W02** 27.8.16 | **error** `V` | The u8 comes from padding (0). The client's branch for category 6 never runs. The server sends one element only, so no shift today. With 2 or more it would misread, then disconnect | `0x758720`, `0x7c2f80` (`v26 == 6`), `0xb67c50` | New element {u32, u8}, the u8 from `AchievementAsset.Category` | Yes; check the enum values match first |
| 5 | **W03** 3.0.16 | **harmless** `V` | The count only reserves capacity. A failed read is ignored: this handler always returns 1 | `0x889ac0`, `0x887070`, `0x875b40` | Optional: write the remaining count | Yes |
| 6 | **W04** 2.1.2 | **harmless** `V` | PC reads u16, then ignores it | `0x889ce0`, `0x886d00` | Width u16 | Yes |
| 7 | **W06** 19.28.2 | **not an error** `V` | Bytes as sent are right: `+8` is the 1-based slot the client indexes with, as the server sends it; `+0xc` is not used by this consumer | `0x76f820`, `0x7fae10`, `0x4889e0`, `0xa24cb0`, `0x4885b0` | **Do not swap the wire** | Swap: unsafe |
| 8 | W05 62.1.2 | **harmless today** `V` consumers, `I` values | First u32 is the argument of 62.5.1, third is the argument of 13.17.1. Served values are crossed against captures, but the server has no 62.5.1 structure and ignores 13.17.1's value | `0x777b00`, getter `0x8713b0`, `0x5f4560`, `0x85d940`, `0x83ae80`, `0x5f49b0`, `0x872440`, `0x82c7f0` | Swap in `SeasonDungeonGetInfoHandler` | Not settled: 40 is known for dungeon 3 only |
| 9 | W15 | **not an error** on the wire `V` | `+27` is a zero/non-zero gate, `+28` the variant index. Server names are the reverse of PS4's, and its assets are written for the order as sent | `0x77a1b0`, `0x751a06`, `0x752590` | **Do not swap the wire**; rename at most | Swap: unsafe |
| 10 | W21 | **error** `V` | Client shows a requirement line only when the flag is non-zero. The server never sets it, so **those lines are never shown** | `0xf502f0` | Rename; set it true where a requirement should be shown | Yes; UI text only. Check which goods first |
| 11 | W22 | **not an error** `V`, part | Bools at `+358`, `+359` feed the join flags beside `+361` the pawn count: fits the server's order. `+356`, `+360` consumers not traced | `0x77b080`, `0xed89f0` | Nothing | n/a |
| 12 | W12 | **harmless today** `V` | PC element is `CDataCommonU32`, server's is {u32, MtString}, but the server always sends this list empty | `0x75e8e0`; `CraftGetCraftProgressListHandler.cs:59` | Change the element type | Yes |
| 13 | W16 | **error** `V` | The client keeps the 7th u32 and formats it as a time. The server puts the time in the 4th, which nothing reads, so **the quest-end time is blank** | `0xbd4b56`, `0x4cf380` | Write it in the 7th; see new row N1 | Yes |
| 14 | D08 | **not an error** `V` | PC reads s32 then u32, no RES guard; the server's "Result" is the character id the client stores | `0x8874b4`, `0x889600` | Nothing | n/a |
| 15 | **D06** | **error** `V` when a path sends no RES | No RES means timeout, then **dialog 33001 and disconnect**. No retry | `0x8855a0`, `0x85c860`, `0x876c70` | RES on every path of the 7 | Yes, per handler |
| 16 | 31.17.1, 31.17.2 | **harmless** `V` on the wire | The excess RES byte is unread. The request's bool is the player's clan notice option, dropped by the server; the client's own use of the option is local | `0x823a80`, `0xb5f934`, `0x8043c0`, `0x7c2f80` | Remove the byte; storing the bool is a feature, not a fix | Yes |
| 17 | 11.60.16 | **harmless** `V` | Bool from `cPRTManager`. Nothing the client waits on | `0x8395a0`, `0x883b30`, `0x9b1d4a` | Read it | Yes |
| 18 | 14.11.16 | **harmless** `V` | A u32 from callers passing `1` or a stored value | `0x840080`, `0x885a90`, `0xb61ab0` | Read it | Yes |
| 19 | W14 50.1.1 | **harmless** `V` | Trailing bool passed through; meaning not traced | `0x841860`, `0x82d630`, `0x880ff5` | Read it | Yes |
| 20 | W09 0.1.1, 0.5.1 | **harmless** `V` | `u8` constant 1 and a u32 from `0xa2abb0`; the server could check them but need not | `0x8243b0`, `0x824580`, `0x876e48`, `0x8773d8` | Read them | Yes |
| 21 | F03 | **harmless** `V`, part | No frame limit below the u16 in the receive path. Buffer growth not traced | `0x9d6d69`-`0x9d6dc5`, `0x9d7590` | Server side only | Yes |
| 22 | F09 | **not settled**, client `V` | Above 0x800 `Read_MtString` returns 0, the reader fails, the client **disconnects**. Whether the server ever sends one is unread | `0x8bc5b0` | A scan of server strings; a cap if any exceeds | A truncation is safe compared with a disconnect |
| 23 | F12 | **harmless at the default** `V` | The client does verify `OpenHash`: mismatch returns 0, then disconnect. So with more than 1 lane the SHA1 race could end a connection; at 1 lane it cannot occur | `0x886b46`-`0x886b6a`, `0x886bf7` | `SHA1.HashData` | Yes |
| 24 | F02 | **harmless, with a trap** `V` | Padding is never length-checked. But padding is what a short server layout reads into, and reading past it disconnects | `0x9d6f2e`-`0x9d6f53`, `0x8bc480` | Patch only after every short layout | **Not alone**: see below |
| 25 | T05 | **not an error** `V` | Top-level shape agrees; the name is wrong only; the handler returns an empty list | `0x7f2180`, `0x816c60`, `0x776300`, `0x778230` | Rename at most | Yes |

**Counts:** error 5 (F06, W02, W21, W16, D06); harmless 15 (F04, 62.33.2, W01, W03, W04, W05, W12, 31.17, 11.60.16, 14.11.16, W14, W09, F03, F12, F02); not an error 5 (W06, W15, W22, D08, T05); not settled 1 (F09) as a row, plus the list below.

## The general rule: what ends a served connection

Read before any patch: it explains most rows and is new. All `V` on the game connection unless marked.

1. `0x9d6d20` decrypts a frame and builds a `CPacket` whose reader limit is the **frame end including padding** (`0x9d6f2e`-`0x9d6f53`). It then calls vtable `+0x44`.
2. Game dispatch `0x844be0` looks up group, id and sub in the table and calls the handler. **A group of 0x4A or more, or a key with no record, returns 0.**
3. `nPacket::Read_*` check bounds and return 0 without moving (`0x8bc480`, `0x8bc4d0`, `0x8bc6e0`, `0x8bc750`): **no fault and no stale bytes**. Readers pass the 0 up, and most handlers return it (for example `0x7ff580`, `0x7cd0e0`).
4. When vtable `+0x44` returns 0, `0x9d6d20` returns `0xBB9` (3001) (`0x9d6f78`, `0x9d7048`). Its caller then calls vtable `+0x50` with the code and vtable `+0x18` with 7 (`0x9d79de`-`0x9d79ec`).
5. Game `+0x50` is `0x877990`: for 3000 and 3001 it calls `0x87c490` with mode 12, and turns every pending request into an error with code 3008. What `+0x18` does was not read (`0x85c8e0` has no function); that state 7 ends the session is `I`.

So: **an S2C key the client has no record for, or a read past the frame end in an ordinary handler, ends the session with error 3001.** Exception seen: `0x887070` (3.0.16) always returns 1. A long enough server layout never hits this, and a short one is rescued only by padding.

## Evidence

### F06: the error RES sent twice

Server: `RequestPacketHandler.cs:87` then `:101` send the same `Error`.

- **No pending match.** `0x844be0` compares group, id and sub only, and calls the handler. It reads no status.
- **Second run.** Every handler sampled reads the RES, then calls the function the database names `callOnPacketFunc` (`0x878860`, a misleading name: PS4's function of that name is another thing). It takes a slot, the "com id", one per RES.
- **`0x878860`** (PS4 body inlined in `OnPacket_S2C_CLAN_SETTING_UPDATE_RES` `0x31ab10`, which names the fields):

| Field | PC | PS4 name |
| --- | --- | --- |
| status, 1 pending, 2 ok, 4 error | `this[slot+1]` | `mStatus`, `NET_STAT` |
| error code | `this[slot+743]` | `mErrorCode` |
| timer | `this[slot+1485]` | `mComTimer` |
| never show a dialog | byte `slot+8912` | `mIsNgErrorDialog` |
| suppress the next dialog | byte `slot+9654` | `mIsOnceNgErrorDialog` |

With an error it sets status 4, then: if "never" is clear, and "once" is set, it clears "once" and shows nothing; if "once" is clear, it calls `0xbb3980`.

- **`0xbb3980`** is PS4's `sNetworkExt::requestNetworkErrorDialog` by body (PS4 `0x7edef0`): add to `MtNetServiceError` at level 1.
- **The queue drops a duplicate.** `0x13ef380` (PS4 `MtNetServiceError::add` `0xdb6cb0`) walks `while (entry.level < level)`, so at level 1 an occupied first entry ends the walk with nothing added. The entry is cleared only by `0xbb2580` (PS4 `closeErrorDisp`) and by `0xbb3430`'s failure path (PS4 `moveBefore`). The clear's own body `0x13ef490` was read on PS4 only (`0xdb6ea0`). **So a normal error shows one dialog.** That the first dialog cannot close between two frames sent back to back is `I`.
- **The real harm: the once flag.** The client sets it before these requests. Sites found by a byte scan for the flag range after a load of the game server pointer (`+0x9f4`). Slot-to-packet by `0x878860`'s argument in each handler:

| Set at | Slot | RES | Server handler can throw |
| --- | --- | --- | --- |
| `0x40f744`, `0x7d8ebe` | 515 | 18.0.2 | no |
| `0x551363`, `0x551b88` | 69 | 8.8.2 | no in the handler |
| `0x558c7c` | 381 | 16.0.2 | no in the handler |
| `0x996c0e` | 330 | 14.0.2 | no in the handler |
| `0xc77f75` | 62 | 8.3.2 | no in the handler |
| `0xc77fab` | 70 | 8.9.2 | **yes**, 1 |
| `0xc77fd8` | 66 | 8.6.2 | **yes**, 3 |
| `0xfd9ed0` | 463 | 33.1.2 | through `JobManager`, not traced |
| `0xfd9ed8` | 464 | 33.2.2 | through `JobManager`, not traced |
| `0x4ec364` | dynamic | caller's | not traced |

`0xc77fd8`, read: set, then the request is sent. So `PawnGetRegisteredPawnDataHandler.cs:31` (`ERROR_CODE_PAWN_NOT_FOUNDED`) puts up a dialog the client meant to hide. The byte scan can miss sites where the pointer load is further away: a coverage limit, not a clean result. "Handler can throw" counts `ResponseErrorException` in that file only.

- **Handler bodies on a second run.** 705 RES handlers from the table. 672 decompile to a call of `0x878860`; 33 have none and are unread. In 95 of the 672 the next statement is not an obvious guard. Sampled: 13.3.2 `0x7dac80` nothing after; 18.0.2 `0x7d8d40` guarded on Result, which holds the Error; 3.0.2 `0x7e2c60` and 12.0.2 `0x7fd960` guard inside; 19.28.2 `0x7fae10` no guard, redoes the same clear and fill on empty lists (idempotent, `I`). **The other 90 were not read**: a second run of something not idempotent is not excluded.
- **Status overwrite.** The second RES writes status 4 again. If the client reissued the same request between the two, it would see a false failure. Both frames leave together, so this is narrow (`I`). See Not settled.
- **Result, not only Error.** `v4 = Result; if (Error) v4 = Error`: a non-zero Result with Error 0 is also treated as an error, with a dialog. A note for anyone setting Result: `ntc.Result = CharacterId` on login 5.3.16 is safe only because that reader is different (D08).

**F04.** The counter is read at `0x9d6eb6`-`0x9d6ef2` into a local header copy. The header's users are the two filters `0x875b00`, `0x8758b0` (group, id, sub only), reached only when `[conn+4]` or `n4+0x34` is set, and a store at reader `this+12`. No compare exists on this path. Consumers of `this+12` were not traced.

### 62.33.2

Reader `0x779420`: element `0x14` bytes, `+4` u32, `+8` u32, `+0xc` MtString, `+0x10` u32. Handler `0x7f7bb0` keeps the RES at connection `+0x2a8`; the only getter found is `0x781fb0`. All 5 of its callers read: `0x5bf0be` (`+24` only), `0x5cdec4` (names at element `+0xc`), `0x5ce78f`, `0x5ce7d1` (count, `+24`), `0x5cd695` (element `+8`, passed on). **None reads element `+0x10`.** So no level is shown and a buff id there does nothing. T002's "wrong value" stands on the wire, without an effect. Worth fixing as one word, not urgent.

### W01

`0x804a50`: Error, Result, bool `+24`, MtString `+28`. Bytes `00 00` then the length. The bool takes `00`, the string length is `00` plus the high byte of the real length, which is 0 for a token under 256 bytes, and `0x8bc5b0` returns 2 for length 0: success. The rest stays in the buffer, unread. `0x7ce490` reads neither field, only releases the string. It calls `0x8815e0(1)` when Result is 0 (a store at manager `+0x181` through a stub, `I`). `0x804a50` has one caller. **That is why every login works.** `IsCogLogin` is never set in the server (`rg`), so `00 01` never occurs: it would ask for a 256-byte string and disconnect.

### W02

`0x758720` per element reads u32 and u8. Handler `0x7c2f80` per element: id and `v26 = u8`; chat and popup messages gated on game options `sGamePointer[2306]`, `[2307]` with a type check on the id's own table `0xb772f0`, not the u8; `if (v26 == 6) 0xb67c50(n3_0, 6, id, 1)` queues kind 33 in a 16-slot notice list. So the u8 matters only for 6. Captures (capture evidence): 8 of 8 hold one element with categories 1 to 4, none 6.

A served element: `count` 4 + `id` 4 = 8 bytes, 17 with the header, so 15 of padding, read as 0. `AchievementManager.cs:505-508` sends one element per NTC, so the shift is unreachable today. With 2 or more elements: the second id is misread, and the read can run out, which disconnects. Whether server `AchievementCategory` value 6 equals the client's 6 was not compared.

### W03

`0x889ac0` reads the list, then u32 at `+36`. `0x887070` first reserves capacity if `+36` exceeds it, and returns 1 whatever the reader returned. The list grows anyway, by count and by 16 (`0x887990`). Only `0x875b40` reads the object (getter `0x88c8a0`): it searches `+16` by message id. `+36` has no other consumer found by offset from that getter. A served client gets 0 or an ignored failed read. F02 does not change this.

### W04

`0x889ce0` (no IDA function, decoded raw): Error, guard, Result, MtString `+24`, `Read_u16` `+28`. `0x886d00` (no function, decoded raw) passes only the string on, to game server `+0x9f4`. The u16 is unread. The client takes the high half of the server's u32 and leaves 2 bytes.

### W06

`0x76f820` per element: u8 `+4`, u32 `+8`, `+0xc`, `+0x10`. The handler `0x7fae10` passes each to `0x4889e0` (also from `0x7fabe0`), decompiled badly; read in disassembly: job must equal the player's current (`cmp [esi+4], al`), `ebx = [esi+8]`, reject `0xFF` and `>= 0xB`; `0xa24cb0` is `x - 1`; then `0x4885b0` writes `array[(job+0x7e)*10 + (x-1)]`. So `+8` is a **1-based slot, at most 10 per job**. `+0xc` and `+0x10` are not touched here.

Server wire order: `Index` (comment "1, 2, 3 based offset", `JobManager.cs:642`), then `SkillNo` ("Skill ID"). Captures: first u32 1, 2, 3 and second 2, 4, 12. **So what the server sends in `+8` is what the client needs.** Consumers of `+0xc` elsewhere were not searched: this is the consumer of this packet, not all uses of the type.

**`docs/explanation/two-packet-decodings.md`:** its text stands as far as it goes: reader order, the PS4 names, a fit cannot settle it. Its "the code decides" can be read as a server fault. Add: the PC consumer `0x4889e0` uses the first u32 as a 1-based slot, so the bytes are right, and only the names differ from PS4 DWARF, whose `m_unSkillNo` is this slot. That is a docs change; I made none.

### W05

`0x777b00`: `+4` u32, `+8` MtString, `+0xc` u32, at RES `+24`, so RES `+0x1c`, `+0x20`, `+0x24`. Getter `0x8713b0`, 8 callers, all in the state machine `0x5f5f10`:

- `0x5f4560` passes `+0x1c` to `0x85d940`, slot 196 (62.5.2), writer `0x83ae80`: `WritePacket(0x3e, 5, 1)` + u32: **62.5.1**.
- `0x5f49b0` passes `+0x24` to `0x872440`, slot 259, writer `0x82c7f0`: `WritePacket(0xd, 17, 1)` + u32: **13.17.1**.
- `0x5f53a0` and `0x5f5bce` use the name.

No validation. Captures: 4 of 4 first 3 (the request's id), third 40. A served client sends 62.5.1 with 40 and 13.17.1 with the dungeon id. The server has no 62.5.1 structure (no `Create`, handler not found): it falls to `FallbackHandler`. `InstanceTreasurePointGetListHandler` echoes the category with no list. So nothing visible depends on it today (`I` for "nothing").

### W15

Reader `0x77a1b0`: `+27`, `+28` are consecutive u8. PC `0x751a06` and `0x752590` (element base +4, so `+0x1f`, `+0x20`): `if ([+0x1f] > 0) idx = [+0x20] % 31`. **PS4** names these `m_ucRepopNum` and `m_ucRepopCount`, in `cLayoutSetEnemy::setLayoutUnitSever`, `createUnitEnemy`; `cGroupParam::addEmSetInfo` keys on `+28`. PC analog of that one was not read.

Captures, all 685 of 13.0.2, pairs (+27, +28): (0,0) 667, (0,1) 536, (0,2) 269, (0,3) 127, (0,4) 39, (2,0) 33, (2,1) 33, (1,0) 17. The server sends `RepopCount` in +27, `RepopNum` in +28. `EnemySpawn.json` (9,222 rows): RepopCount 0 on 9,209, 1 on 12; RepopNum 0 on 9,221. Quest assets set `repop_count` to 1, 2, 3 or 50, which lands in the gate.

So the assets are written for a gate in the first byte. **Swapping the wire would turn those gates off**, and 50 would become an index. Asset `+28` is mostly 0 where official `+28` is 1 to 5: variants on a position may collide. Effect not read: see Not settled. Other consumers of +27 were not searched.

### W21

`0xf502f0`: `if (entry && entry[+20] != 0 && lines < 5) 0xf50470(...)`. `HideRequirementDetails` is written at `+20` (`CDataGoodsParamRequirement.cs:49`) and, by `rg`, set nowhere but its clone line. So it is false and the client shows no line. Assets that set it by reflection were not ruled out: `rg` covered `.cs` only.

### W22

`0xed89f0`: `[+358] == 1` sets bit 0, `[+359] == 1` sets bit 1 of `v1[1745]`; `[+361]` is `v1[1746]`; `+357` is read into a local later. The server's `IsJoinCharacter` and `IsJoinPawn` are `+358`, `+359`. PS4's position order would make them `+357`, `+358`. That favours the server, as the capture does. It does not name the bits on screen. `+356`, `+360`: 13 and 10 byte-scan hits, unread.

### W12

`0x75e8e0` is `Read_CDataCommonU32_`. The third list in `CDataCraftProgress.cs:49` is `CDataCraftPawnInfo` {u32, MtString}. `CraftGetCraftProgressListHandler.cs:59` sends `new List`. `CraftGetCraftSettingHandler.cs:192` fills a list of that name in another structure, not compared here. If it ever fills progress, the client misreads and probably disconnects.

### W16

`0xbd4b56`: `mov eax,[ebp+30h]; mov [ebx+30h],eax`, in callback `0xbd49b0` (no function, raw) on the packet: `+0x30` is the 7th u32 with base `+0x18`. It is stored on `sQuestManagerExt`. `0x4cf380` reads it: 0 gives an empty string, otherwise it divides by 1000 and 60 for a time text. The 4th to 6th are unread (T014b for the callback; the byte scan agrees). The capture's 7th is 1,045,461 and matches the elapsed time (T005 §23, `I`). Who calls `0x4cf380`, on which screen: not traced.

### D08

`0x8874b4`, no function, raw. `0x889600`: s32 `+16`, u32 `+20`, no guard. `0x88750a`: first non-zero means status 4, code stored, `0xbb3980` unless flag `+0xf1`. Then `+0x1294 = 0`, `+0x12a1 = 0`, `+0x1298 = u32`, plus a time. The server writes Error 0 and `Result = character.CharacterId` (`CreateCharacterHandler.cs:519`, comment: "Value will show up in DecideCharacterIdHandler"). **The server is right**; `ServerResponse` is an odd base with a correct layout.

### D06

No RES ever. `0x8855a0`, each tick (from `0x8771c0`, PS4 `cNetGameServer::move` calling `updateComTimer` `0x33f4b0`):

1. For each slot with status 1 and timer `>= 0`, add the delta.
2. Above `fps * 2.0` (`0x885609`): `0xb82480`, a wait indicator (`I` from what it writes).
3. Above `fps * 45.0` (`0x885601`, `0x1ae5744` is 45.0) first time: `0x879d40` records the slot and sends a ping (`0x877bf0`, writer `0x824750` = 0.0.1), sets flag `+0xa300`, returns.
4. Next tick, the slot still over: `0x85c860` (every pending slot to status 4, code 3008; connection state 6), dialog via `0xb434d0` with code 33001, status 4. **No retry of the request.** Slot 3 skips the dialog.

The flag is cleared only at `0x847359`, a reset routine. So the first request to time out ends the session within a tick of 45 s. That the timer's unit is seconds is `I`: `0x407940` did not decompile.

`LobbyLobbyLeaveHandler` as the example: requester `0x876c70`, slot 21, status 1, timer 0, normal. It sends its RES first (`LobbyLobbyLeaveHandler.cs:23`), so it does not reach this; the risk is the other 6, chiefly `QuestLeaderQuestProgressRequestHandler.cs:18`, and likewise F07 and F08. One difference: `this[1506] = 0` starts the timer; requests that set -1, like the ping at `0x877bf0`, are exempt.

### 31.17

`0x823a80`: `Write_bool(in_IsMemberNotice)`, from `cNetGameServer::updateClanSetting` `0x885510`, slot 375, called at `0xb5f934` with `HIBYTE(sGamePointer[2307])`, the same option that gates a message in `0x7c2f80`. `0x8043c0`: Error, Result only. Handler `0x7cd0e0` reads nothing further. The RES byte is padding to the client.

`ClanClanSettingUpdateHandler.cs:21` answers false and stores nothing, with its `TODO`. A player's setting is not kept; `CDataCharacterListInfo.IsClanMemberNotice` stays 0. What other clients do with that was not traced. A stub with the correct layout is out of scope under the spec.

### Others

- **11.60.16:** `0x8395a0` writes byte manager `+40294`, set in `0x883b30` from `0x9b1a60`, `cPRTManager::updatePRT`. No RES.
- **14.11.16:** T01's writer; `0x885a90`, `0xb61ab0`, from `0x407087` (`1`) and `0x412abd` (`[v10+48]`).
- **W14:** `0x841860` writes u8 and the bool `a3`; `0x82d630`, `0x880ff5` pass it through. Origin not traced.
- **W09:** `Write_cstr`, `Write_u8(1)`, `Write_u32(0xa2abb0())`.
- **F03:** frame size is the u16 (`0x9d6d69`-`0x9d6d89`), and the frame stream is sized `count + 9` with no cap (`0x9d6dc5`). `0x9d7590` shrinks the receive buffer to 0x1000; how it grows and whether it reaches 65,537 bytes was not traced.
- **F09:** `0x8bc5b0`: `n > 0x800` returns 0, cursor past the length. A short string with n in range: `ReadBytes` returns 0, so also a failure. At exactly 0x800 the 0x800-byte stack buffer has no terminator before the copy `0x4030a0` (`I`).
- **F12:** `0x886b00`, no function, decoded raw: `0x13ee820` with 272 and `+0x188` (hash; that it is SHA-1 is `I`, a thunk), then a 5-dword compare, `0x886b5b`-`0x886b6a`, `jne 0x886bf7`: `xor eax,eax`, return. Modulus and exponent are loaded only after it. The game handler 44.1.16 was not read: `I` that it is the same.
- **F02:** the padding is in the reader's window, and no code measures it. Zero against random matters only to an over-read (W02's u8, W03's u32).
- **T05:** `0x7f2180` (slot 137), `0x816c60`, list `0x776300` of `0xd0`-byte elements {u32, `0x778230`}; `0x778230` reads u32 u32 u64 u64 u32 u32 u16 u32 list list u32 list u8 u8 u16 bool list list list list. The server's {u32, `CDataSetQuestInfoList`} agrees over the 13 fields compared at the top; the rest was not compared. `QuestGetPartyBonusListHandler` returns an empty list.

## F02's trap

The server pads 1 to 16 bytes; official 0 to 15. Today, every frame has at least one spare byte, and short layouts survive on it. With padding 0 to 15, a frame landing exactly on a block boundary has none, and a client read of even 1 byte too many **disconnects** rather than reading 0 (general rule above). T001 said this for W03, but W03 is immune: `0x887070` returns 1. The rows it does touch are any layout still short. Known: W02 is at 17 bytes with one element, so not on a boundary. Unknown layouts are the risk. **Patch W02 first, and treat F02 as a change with real risk and no benefit to the client.** I would leave it out unless the coordinator wants the wire to match.

## Server structure misplacements (new)

| Row | Where | What | Evidence |
| --- | --- | --- | --- |
| N1 | `QuestPlayEndHandler.cs:42` | `(uint) elapsed.Milliseconds` is the 0-999 component, not `TotalMilliseconds` (read in code), and it goes in the wrong slot (W16). With W16 alone the time would show under a second | `V` server; `0x4cf380` formats ms |
| N2 | `S2CConnectionLoginRes`, `IsCogLogin` | Must not be set true while it is a u16: `00 01` asks for a 256-byte string, and fails on a short frame | `0x804a50`, `0x8bc5b0` |
| N3 | `PacketId` 2.19, 2.20, 2.21, 11.60, 63.11, 11.81 (T02, T04, T06) | S2C with no PC record. **If ever sent, the client ends the session with 3001** (`0x844c68`). T001's "metadata only" holds only while none is sent. `#if false` around 63.11's sender at `Quest.cs:1036` should stay | `0x844be0` |
| N4 | 62.5.1 | Client sends it from the state machine; no server structure, so Fallback answers NOT_IMPLEMENTED, and the client shows an error unless flagged. Unimplemented, out of scope; for the impact outline | `0x5f4560` |
| N5 | any RES with `Error == 0`, `Result != 0` | Client treats non-zero Result as an error, with a dialog (`v4 = Result`). A handler setting Result as data on a real RES would show one. Not surveyed | `0x7ff580` and every handler sampled |

## Not settled

| Item | What is open | What would settle it |
| --- | --- | --- |
| F06, status | A false failure if a request is reissued between the two RES | Live: local server, force a repeated error on 8.6.1 with the once flag set; watch the dialog and the next request. Same run proves the suppressed dialog |
| F06, bodies | 90 of 95 handlers with code after the status call unread; 33 with no call unread | Static: read them, or live per feature |
| F04, corruption | A corrupted frame's outcome. Inferred: garbage header, no record, 3001 | Live with lanes above 1 under load, or a crafted frame |
| F09 | Does any server string exceed 0x800 bytes? Client side is settled | Static scan of server strings; no live run needed |
| W05 | Is the third u32 always 40? Only dungeon 3 is captured | A capture of another dungeon, or `62.5.1`'s and `13.17`'s server semantics; a live run cannot answer it |
| W15 | Does asset `+28` being mostly 0 collide variants on a position? | Live: a stage with two spawns at one position, or read PC analog of `addEmSetInfo` |
| W16 | On which screen the time shows | Live: finish a quest on a patched server |
| D06 | The 45 is seconds | Live: a handler that sends no RES; time the dialog |
| W21 | Which goods should show the line | Compare captures' `+20` with server goods |

None of these blocks the F06 patch. W05 is the only row whose fix they should hold.

## Not run

- A live client or server; any patch; `dotnet` anything.
- `D:/ddon-data-s2/recompilation/src/` was not consulted: no row here depends on stack argument order; every argument cited was read in disassembly or is a thiscall with one or two arguments.
- PS4 was used for names only, on: `callOnPacketFunc` fields, `requestNetworkErrorDialog`, `MtNetServiceError`, `moveBefore`, `updateComTimer`, repop consumers.
- `binaries/PS4_02020005/DDOORBIS_{2,3}.elf.c` was searched for `RepopCount`, since xrefs to a member are not available; that is the IDA 9.3 export, not MCP.
- Login connection `+0x50`, `+0x18`, and the login dispatch `0x88aab0`: not read. The general rule is `V` for the game connection and `I` for login, though login handlers follow the same shape.
- Vtable `+0x18` `0x85c8e0`: not read.
- Consumers found by byte scan (once flags, `+27`, W22's offsets) are limited to the instruction forms and windows scanned; a miss is a coverage gap.
- Decoding at addresses with no IDA function used `rasm2` or the raw bytes; nothing was created in the database.
- Two capture reads used `jq` and a counter on `packets/decrypted_json/` (13.0.2 all 685; 27.8.16, 62.1.2, 19.28.2 samples of 8, 4 and 1). Capture values above are capture evidence only.

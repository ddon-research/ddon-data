# 009 T009c: page claims checked in the IDA databases

Role `evidence-researcher-ida`, base `303f080adb7`. All addresses are VAs. Tool: ida-mcp `execute_python`, read-only (no rename, retype, comment, patch or reanalysis).

| Copy | `idc.get_idb_path()` | Image base | Bitness, processor | Stored input SHA-256 | Stored input path |
| --- | --- | --- | --- | --- | --- |
| `private-copy.sh pc-handlers t009c`, PC 03040008 | `D:\research\DDON-binaries\IDA9.5\PC_DDON_03040008\ddon-data-t009c\2022_01_29_DDO_DUMP_FIX.exe.i64` | `0x400000` | 32-bit, metapc | `f1c974d0...fa20` | `...\IDA9.3\PC_DDON_03040008\...` |
| `private-copy.sh ps4 t009c`, PS4 02020005 | `D:\research\DDON-binaries\IDA9.5\PS4_DDON_02020005_2016_12_21\ddon-data-t009c\DDOORBIS.elf.i64` | `0` | 64-bit, metapc | `4236f598...63c0` | `...\IDA9.3\PS4_DDON_02020005_2016_12_21\...` |

Counts: 42 claims checked. 40 hold, 1 wrong, 1 not settled. Unless a row says PS4, the database is the PC copy.

## Wrong

**`docs/reference/packet-handler-tables.md:132`.** `0x889f40` and `0x88a980` are the starts of the first and last login writer functions, not bounds of the call sites. The 13 sites run from `0x889fb3` to `0x88a98e`, so the 13th (`0x88a98e`, writer 5.1.1) lies past the stated end, and the row above already gives `0x88a98e` as the last call. A reader filtering sites on the stated range gets 12 of 13.

Fix: `| Login writers | 13 sites from `0x889fb3` to `0x88a98e`, in the writers from `0x889f40` to `0x88a980` |`

## Item 1: send and receive

| Claim | Page:line | VA | What IDA shows | Verdict |
| --- | --- | --- | --- | --- |
| `cSeedServerConnection::Send` is this address | `packet-wire-format.md:78` | `0x9d6a20` | Named `cSeedServerConnection::Send`, `void __thiscall(cSeedServerConnection *self, char *buffer, unsigned int size)` | holds |
| It drops the 9 header bytes when group and id match the handshake command and sub is 1 | `packet-wire-format.md:78` | `0x9d6ad4`..`0x9d6b03`, `0x9d6bb4`..`0x9d6bff` | Compares the header's group with vtable `+0x5c`, its id with `+0x64`, its sub with 1 (`0x9d6aeb`..`0x9d6b01`), then mode 5: count `-9` (`add edi, 0FFFFFFF7h`), source `+9` (`0x9d6be8`), passed to `cSeedServerConnection__cryptCamellia` with `pKey`. The branch runs only after `sub_9D78C0` (the byte at `conn+0x109`) returns true; otherwise the mode is plain (`0x9d6acd`). The sentence omits that precondition, which does not make it false | holds |
| The writer builds a normal header | `packet-wire-format.md:78` | `0x88a900` | Login writer `push 1; push 0; push 1` with `-1`, a normal `WritePacket` call for 1.0.1 at `0x88a90e` | holds |
| The receive path synthesizes group and id from the connection, sub 0x10, counter 0 | `packet-wire-format.md:79` | `0x9d6e49`..`0x9d6e7d` | Group from vtable `+0x60` to `[ebx]`, id from `+0x68` to `[ebx+1]`, `mov word ptr [ebx+3], 10h`, `mov dword ptr [ebx+5], 0`; the body is decrypted to `buf+9` with `pKey` (`0x9d6e2c`..`0x9d6e44`) | holds |
| ...for the server's first packet | `packet-wire-format.md:79` | `0x9d6df7`..`0x9d6e24` | Mode 5 needs `sub_9D78C0` true and `sub_19A47B2` (a bounded string length) of the key copied by `sub_869E20` (`conn+0xd8`, 0x31 bytes) to be 0: cipher on, session key empty. That this is the first packet is inferred from that state | holds (inferred) |
| Game vtable, send 0x2c,0 and receive 0x2c,1 | `packet-wire-format.md:83` | `0x1bc5c38` | `+0x10` returns `dti_cSeedGameSvConnection`. Raw bytes: `+0x5c` `0x86c900` `mov eax,0x2c; ret`; `+0x64` `0x86c910` `xor eax,eax; ret`; `+0x60` `0x86c8e0` `mov eax,0x2c; ret`; `+0x68` `0x86c8f0` `mov eax,1; ret` | holds |
| Login vtable, send 1,0 and receive 1,1 | `packet-wire-format.md:84` | `0x1bd6af8` | `+0x10` returns `dti_cSeedLoginSvConnection`. `+0x5c` `0x88c8e0` = 1; `+0x64` `0x88c8f0` = 0; `+0x60` `0x88c8c0` = 1; `+0x68` `0x88c8d0` = 1 | holds |

Of the two pages the brief names, only `packet-wire-format.md` states these claims; `wire-protocol.md` holds no address of 5 or more hex digits. `docs/reference/arrowgene-cli-patches.md:50` also cites `0x9d6d20` for the synthesized header, which holds by the same reading.

## Item 2: the shift claim

The sentence at `ida-transfer-method.md:71`: a whole PS4 layout, even recomputed for 32 bits, fails on the Season 3 packet classes; often a per-class shift is constant, "but some classes change mid-way, with a list off the shift by an unrelated amount, so a shift rule is wrong exactly where a reader would rely on it."

| Claim | Page:line | VA | What IDA shows | Verdict |
| --- | --- | --- | --- | --- |
| Often the shift is constant | `ida-transfer-method.md:71` | PC `0x81dc00`; PS4 type `CPacket_S2C_WARP_RES` | PC reads `+0x18` and `+0x1c`. PS4 DWARF members are at `+0x10` and `+0x14`, with an 8-byte base, so `+0xc` and `+0x10` on 32 bits: shift `+0xc` on both. One class read here; the census is T012's (41 of 46 classes at `+0xc`, `specs/007-pc-handler-annotation/research/W2-T012-evidence.md`), not rerun | holds |
| Some classes change mid-way: `CHANGE_JOB_RES` | `ida-transfer-method.md:71` | PC `0x80cf80`; PS4 `0x19dc3a0` | PC list `lea`s: `CDataS2CCharacterEquipInfo` `+0x60`, then `CDataSetAcquirementParam` `+0x74` and `+0x88`, `sub_76CD60` `+0x9c`, `CDataEquipJobItem` `+0xb0`. PS4: `m_CharacterEquipList` `+0x60`, `m_EquipJobItemList` `+0x160`, with 7 lists between them. Between those two lists PC moves `0x50`; 8 lists of the PC's `0x14` would be `0xa0`. The list is `0x50` off the class's `+0xc` shift | holds |
| Second class: `CHANGE_PAWN_JOB_RES` | `ida-transfer-method.md:71` | PC `0x80d170`; PS4 type | PC `+0x64` to `CDataEquipJobItem` `+0xb4`, again `0x50`; PS4 `+0x68` to `+0x168`. So "some classes" is two at least | holds |
| "An unrelated amount" | `ida-transfer-method.md:71` | PC `0x80cf80`; PS4 `0x19dc411`..`0x19dc456` | `0x50` is 4 lists of `0x14`: PS4 reads 3 `CDataItemList` lists and `m_DifferentEquipList` here, and PC reads none of them between `+0x60` and `+0x74`. It is unrelated to the header shift, and it does have a cause (the removal the page names at line 65) | holds |

The 32-bit positions rest on PS4 member order and the PC array size, read here by hand; `transfer/layout.py` was not run. `W2-T012` line 149 states the same case as `-0x44` from the predicted offset, and `tasks.md:183` as "0x44 off the shift". The page gives no number, so neither wording reaches it.

## Item 3: sample of addresses

`docs/explanation/packet-decoding-method.md` holds no address, so the sample takes 22 rows from the other pages.

| # | Claim | Page:line | VA | What IDA shows | Verdict |
| --- | --- | --- | --- | --- | --- |
| 1 | Directory of 74 `{table, count}`, counts sum to 1,041; rows 0, 14, 15, 62, 73 | `packet-handler-tables.md:19`, `:27`, `:31`, `:45`, `:46`, `:93`, `:104` | `0x1bc0110` | Sum 1,041. The five rows sampled equal the page's; entry 74 is `{0xe, 0xb}`, not a table | holds |
| 2 | 14.3.2 is the fifth record of group 14, key at `+0x10` is `(sub<<16)\|id` | `packet-handler-tables.md:23`..`:27` | `0x212fe98` | `(0x212fe98-0x212fe38)/0x18 = 4`; `+0x10` is `0x20003` | holds |
| 3 | Its handler is `0x7ff580`, not in the file's data, written at start-up | `packet-handler-tables.md:25`, `:27` | `0x1a36631`, `0x1a36645` | The record's first dword is 0 in the database; `mov [esp], offset 0x7ff580` then `movq` to the record, inside `sub_1A36540` | holds |
| 4 | 74 initializers from `0x1a27560` to `0x1a36540` | `packet-handler-tables.md:25` | `0x1a27560`, `0x1a36540` | Taking each group's first record, 74 distinct writer functions, lowest and highest as stated | holds |
| 5 | Handler name for 14.3.2 | `packet-handler-tables.md:137` | `0x7ff580` | `cSeedGameSvConnection::OnPacket_WARP_WARP_RES`, the same text as string `0x1bcbda8`, passed at `0x7ff605` | holds |
| 6 | 675 diagnostic strings, none with `cSeedLoginSvConnection` | `packet-handler-tables.md:137` | whole image | 675 occurrences, 675 distinct. `OnPacket_L2C` and `LoginSvConnection::OnPacket`: 0. The bare class name exists once, at `0x1bd6ba0`, and is not a diagnostic string | holds |
| 7 | Login directory of 6 `{start, count}`; `0x1bd6270` is group 0, `0x1bd6294` group 1; each list ends in a u32 count; 20 handlers; all 20 rows | `packet-handler-tables.md:108`, `:112`..`:121` | `0x1bd67f4` | Counts 4, 2, 4, 2, 1, 7; a trailing count after each list equal to it; all 20 handler and key pairs equal the page's | holds |
| 8 | 1.1.16 is handler `0x886b00` | `write-a-packet-pattern.md:21`, `packet-handler-tables.md:117` | `0x886b00` | The list holds it. See the note below: IDA has no function here | holds |
| 9 | `WritePacket` is this address, called with group, id, sub, -1 | `packet-handler-tables.md:127` | `0x8bcbb0` | `nUserSession::CPacket::WritePacket`, `BOOL __cdecl(CPacket *packet, uint8_t groupId, __int16 id, uint8_t subId, int a5)`; pushes at `0x8400c4`..`0x8400e4` | holds |
| 10 | 658 direct `E8` calls, `0x81dd03` to `0x88a98e` | `packet-handler-tables.md:131` | `0x8bcbb0` | 658 code refs, all `E8`; a raw scan of `.text` agrees: 658, same bounds | holds |
| 11 | Login writers are the sites in `0x889f40`..`0x88a980` | `packet-handler-tables.md:132` | `0x889fb3`..`0x88a98e` | 13 sites; the last is past the stated end | **wrong** |
| 12 | `0x76f820` fills a `0x14`-byte object: vtable, u8 `+4`, u32 `+8`, `+0xc`, `+0x10` | `two-packet-decodings.md:71` | `0x76f820` | `nPacket::Read_CDataNormalSkillParam_`; `push 14h` to the allocator, `off_1BC3378` to `[esi]`, then `Read_u8` `+4`, `Read_u32` `+8`, `+0xc`, `+0x10` | holds |
| 13 | PS4 reader stores `+0xc`, `+0x10`, `+0x14`; DWARF names SkillNo, Index, PreSkillNo in that order | `two-packet-decodings.md:71` | PS4 `0x19f1cc0` | `nPacket::Read_CDataNormalSkillParam_`; `lea rsi,[rbx+0Ch]`, `[rbx+10h]`, `[rbx+14h]`, each to `Read_u32`. Type: `m_unSkillNo` `+0xc`, `m_unIndex` `+0x10`, `m_unPreSkillNo` `+0x14` | holds |
| 14 | 14.11.16's writer is `0x840080` and writes a u32 | `two-packet-decodings.md:73`, `write-a-packet-pattern.md:22` | `0x840080` | `push 0Eh`, `push 0Bh`, `push 10h`, `-1` to `WritePacket` (`0x8400f3`), one `Write_u32` (`0x840108`), `Send` (`0x840122`) | holds |
| 15 | 62.26.16 reader `0x766790` has a last u8 at `+28` | `two-packet-decodings.md:77` | `0x766790`, record `0x21304f8` | Record key `0x10001a`, handler `0x7f8970` by initializer write at `0x1a34c5d`, calling `0x766790` at `0x7f89e4`; last read is `Read_u8` to `[esi+1Ch]`, which is 28. Reads: u32, u8, u32, u32, u8. No `OnPacket_` name, as the pattern says | holds |
| 16 | Handler `0x7ff580` leads to reader `0x81dc00`; RES header, u32, u32 | `write-a-packet-pattern.md:34`, `:66`; `two-packet-decodings.md:57` | `0x7ff5da`, `0x81dc00` | `call sub_81DC00`; two `Read_s32` with the guard, `Read_u32` `+0x18`, `Read_u32` `+0x1c` | holds |
| 17 | PS4 `OnPacket_S2C_WARP_RES` reads u32 `m_unWarpPointID`, u32 `m_unrim` | `write-a-packet-pattern.md:66`..`:67` | PS4 `0x2f7190` | Named as stated; `Read_u16`, `Read_s32`, `Read_u32`, `Read_u32` into stack slots. Member names come from the type (`+0x10`, `+0x14`), mapped by offset and read order, inferred | holds |
| 18 | RES: `s32 Result` and the rest follow only when Error is 0 | `packet-wire-format.md:96` | `0x805340`, `0x8015b0`, `0x801530` | Each reads `+0x10` by `Read_s32`, and a non-zero value goes to `+0x14` and returns; the zero branch (`0x805379`, `0x8015e9`, `0x80156c`) reads `+0x14` | holds |
| 19 | `Write_MtString`: low 16 bits, 0 if null | `packet-wire-format.md:137` | `0x8bc790` | Named as stated; `LOWORD(length) = 0` when null, big-endian prefix | holds |
| 20 | `Write_cstr`: `strlen`, low 16 bits, NUL not copied | `packet-wire-format.md:138` | `0x8bca30` | Named as stated; `memcpy(.., str, (u16)strlen)` | holds |
| 21 | `Read_MtString`: the wire, a length up to 0x800 | `packet-wire-format.md:139` | `0x8bc5b0` | Named as stated; `mov eax,800h; cmp ax,di; jnb`, returns 0 above it | holds |
| 22 | `pKey` holds the fixed key string | `packet-wire-format.md:30` | `0x2135d90` | Named `pKey`, points to `0x1c088f0`, `f23e98HafJdSoaj80QBjhh23oajgklSadrhogh2IJnwJEF58` | holds |

Name matches beyond the pages' one example: 686 names start `cSeedGameSvConnection::OnPacket_`, and 669 equal a diagnostic string their own function references. Of the other 17, the 16 printed are 10 handler functions with `OnPacket_S2C_*` names and no string, and 6 labels on data in the record range, truncated (`0x212bcf8`); the 17th was not printed. No page sentence claims otherwise.

## Item 4: which database holds what

| Claim | Page:line | VA | What IDA shows | Verdict |
| --- | --- | --- | --- | --- |
| `pc-handlers` opens the database named, PC 03040008, annotated | `query-ida-read-only.md:11`, `inputs-and-builds.md:50` | n/a | `research/ida/private-copy.sh` copies `spec007-packet-handlers-20261103-wave2/2022_01_29_DDO_DUMP_FIX.exe.i64` (byte size equal, 112,433,230). It holds handler names, prototypes and types: rows 5 and 19 to 21, `CPacket_S2C_CHANGE_JOB_RES` | holds |
| The copy goes in `PC_DDON_03040008/ddon-data-<name>/` | `query-ida-read-only.md:27` | n/a | `idc.get_idb_path()` in the table above | holds |
| PC is `0x400000`, 32-bit; PS4 is `0`, 64-bit | `query-ida-read-only.md:45` | n/a | The table above | holds |
| The stored input path says `IDA9.3` | `query-ida-read-only.md:47` | n/a | Both databases | holds |
| `ps4` opens `PS4_DDON_02020005_2016_12_21\DDOORBIS.elf.i64` | `inputs-and-builds.md:51`, `query-ida-read-only.md:12` | n/a | The table above; holds symbols and DWARF types (rows 13, 17) | holds |
| The addresses name `f1c9...` | `packet-handler-tables.md:3` | n/a | The stored input SHA-256 equals the page's, whole | holds |
| PS4: the `strlen` slot holds `0x1be82b6`, inside `/PLstrlen` at `0x1be82b0` | `ps4-elf.md:59`..`:60` | PS4 `0x24fa958` | `__imp_strlen` in `SCE_RELRO`, value `0x1be82b6`; `0x1be82b0` is `jmp cs:__imp_strlen`, `0x1be82b6` is `push 1`. IDA calls it `strlen` with a 6-byte function; `/PLstrlen` of 16 bytes is from `binaries/PS4_02020005/elf-dumps/symbols/plt-stubs.derived.txt:4` | holds |
| PS4: `cWebsocketClient::move()` at `0xe41300` uses 82,344 bytes | `ps4-elf.md:83` | PS4 `0xe41300` | Named as stated; `push rbp`, 5 more pushes, `sub rsp, 14178h`: 48 + 82,296 = 82,344 | holds |
| Facts about the executable hold in all three PC databases | `query-ida-read-only.md:14` | n/a | Only `pc-handlers` was opened; the brief's boundary excludes `pc` and `pc-accepted`. Not settled by this check | not settled |

## Notes a reader may trip on

No page sentence is wrong because of these; they are for whoever edits the pages.

1. **Login handlers in the annotated database.** 9 of the 20 login handler addresses have no function: `0x886650`, `0x886750`, `0x886b00`, `0x886d00`, `0x886e00`, `0x886ec0`, `0x887130`, `0x8874b0`, `0x8875b0`. `0x886b00` shows `dd` data there; decoding without creating gives `sub esp,56Ch; push esi; push edi; mov edi,ecx`, then calls, so it is code IDA has not defined. `0x886820` and `0x886fd0` lie inside functions that start a little earlier, at `0x88681f` and `0x886fcd`. A reader of `write-a-packet-pattern.md:21` who opens `0x886b00` sees no function. Coverage gap, not evidence against the table.
2. **Hex-Rays hides the send claim.** The pseudocode of `0x9d6a20` and `0x9d6d20` elides the mode logic: it shows neither the sub check, the `-9` nor the synthesized header. Both claims stand only in the disassembly. Someone rechecking them by decompiling alone would wrongly call them false.
3. **Names.** `0x9d6d20`, `0x81dc00`, `0x766790` and `0x840080` remain `sub_*` in this database. No page gives them a name.

## Not run

- `pc` and `pc-accepted` databases: outside the boundary.
- `transfer/layout.py`, and any per-member census of shifts (T012's stand as cited).
- The other 69 directory rows in the database; the T009 review compared all 74 against raw bytes.
- `ps4-elf.md:108` (`0x194d8f0`, 1,014 compile units): a DWARF range count IDA does not settle. IDA names the address `std::error_category::default_error_condition`, which fits shared template code and proves nothing about the count.

## Copies

The `.i64` of both copies is deleted. `.id0`, `.id1` and `.nam` remain in both `ddon-data-t009c/` folders, because this session's two ida-mcp workers hold them and `close_database` is denied. They hold no needed data. After the server stops:

```sh
rm -rf /d/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t009c /d/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t009c
```

The originals' timestamps are unchanged at the end of the run (PC `2026-11-03 19:46:53`, PS4 `2026-10-17 11:06:16`); their hashes were not recomputed after the script's own check.

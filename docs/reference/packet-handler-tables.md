# Packet handler tables, client 03040008

Where the PC client 03040008 keeps its packet handlers, senders and packet names, for anyone going from a packet id to its code. [Write a packet pattern](../how-to/write-a-packet-pattern.md) uses them. The addresses are VAs of `2022_01_29_DDO_DUMP_FIX.exe` (SHA-256 `f1c974d0e529d4bb7dc5f0953d37eea6bbb023f2667f9a1d3a3b878f4919fa20`, [DUMP_FIX](glossary.md#builds-and-clients)), image base `0x400000`. They name no PS4 02020005 fact: its packet numbers are another scheme.

## Which database to read them in

The addresses below were checked in `pc-handlers`, whose stored input is `f1c9`. In `pc` and `pc-accepted`: not run. Records give those two the same stored input and image base, so the addresses should hold there too (inferred): for `pc`, `ddon-hook/specs/013-prng-state-recovery/research.md` on 2026-10-18, at the `.i64` hash `717e862d` it still has on 2026-11-04; for `pc-accepted`, `specs/007-pc-handler-annotation/research/T002-audit.md` on 2026-11-03, at the `.i64` hash `382e346e` that `CURRENT-RECOVERY.json` names. That file records no input hash itself. `pc-handlers` descends from a private copy of `pc-accepted` (`specs/007-pc-handler-annotation/spec.md`, Inputs).

| `research/ida/private-copy.sh` target | Database, under `D:\research\DDON-binaries\IDA9.5\PC_DDON_03040008\` | Use |
| --- | --- | --- |
| `pc` | `2022_01_29_DDO_DUMP_FIX.exe.i64` | the live PC database |
| `pc-accepted` | the path `accepted_PC.path` of `CURRENT-RECOVERY.json` gives | ddon-hook's accepted database |
| `pc-handlers` | `spec007-packet-handlers-20261103-wave2\2022_01_29_DDO_DUMP_FIX.exe.i64` | the annotated database: handler names, prototypes and partial types |

Without IDA: the directory, the record keys, the login lists and the strings are static data of the executable, and `research/03040008/ida-transfer/dumps/pc-ida.jsonl` (gitignored, local) holds the game handlers as rows of kind `table`, read with `jq`. The dump's fields `callback` and `record_va` are decimal. The checks under each section below ran on the executable on 2026-11-04.

## Game server: the directory

`0x1bc0110` holds 74 entries of 8 bytes, one per group 0-73, each `{u32 table, u32 count}`.

| Item | Form |
| --- | --- |
| A record of a table | `0x18` bytes |
| Key, at record `+0x10` | u32 `(sub << 16) \| id` |
| Handler pointer | not in the file's data: written at start-up by the 74 initializers whose starts run from `0x1a27560` to `0x1a36540` (`research/03040008/ida-transfer/extract_ida.py`) |

The counts sum to 1,041 records. For example 14.3.2 is the record at `0x212fe98`, the fifth of group 14, and its handler is `0x7ff580`. S2C packets have these records; a C2S packet has a sender instead.

| Group | Table | Count |
| --- | --- | --- |
| 0 | `0x212bb48` | 12 |
| 1 | `0x212f568` | 14 |
| 2 | `0x212b0f8` | 36 |
| 3 | `0x212d720` | 5 |
| 4 | `0x212b530` | 2 |
| 5 | `0x212fdd8` | 4 |
| 6 | `0x212dba0` | 36 |
| 7 | `0x212f3e8` | 9 |
| 8 | `0x212df00` | 48 |
| 9 | `0x212aff0` | 2 |
| 10 | `0x212d0d8` | 27 |
| 11 | `0x212e638` | 146 |
| 12 | `0x212fbe0` | 14 |
| 13 | `0x212cd30` | 39 |
| 14 | `0x212fe38` | 14 |
| 15 | `0x212c748` | 1 |
| 16 | `0x212c778` | 11 |
| 17 | `0x212b020` | 3 |
| 18 | `0x212cc10` | 8 |
| 19 | `0x212f718` | 51 |
| 20 | `0x212f6e8` | 2 |
| 21 | `0x212ccd0` | 4 |
| 22 | `0x21307e0` | 10 |
| 23 | `0x212ad38` | 16 |
| 24 | `0x212d5d0` | 7 |
| 25 | `0x212da08` | 7 |
| 26 | `0x212e488` | 18 |
| 27 | `0x212ac30` | 11 |
| 28 | `0x212c8b0` | 36 |
| 29 | `0x212c478` | 30 |
| 30 | `0x212be18` | 27 |
| 31 | `0x212b560` | 63 |
| 32 | `0x212f4c0` | 2 |
| 33 | `0x212d3a8` | 23 |
| 34 | `0x212c208` | 26 |
| 35 | `0x212bc68` | 18 |
| 36 | `0x212aeb8` | 13 |
| 37 | `0x212d798` | 15 |
| 38 | `0x212f4f0` | 5 |
| 39 | `0x212c880` | 2 |
| 40 | `0x212c0e8` | 1 |
| 41 | `0x212b458` | 9 |
| 42 | `0x212e470` | 1 |
| 43 | `0x212d708` | 1 |
| 44 | `0x212b0c8` | 2 |
| 45 | `0x212fd30` | 5 |
| 46 | `0x212d9f0` | 1 |
| 47 | `0x212c760` | 1 |
| 48 | `0x212c178` | 6 |
| 49 | `0x212fda8` | 2 |
| 50 | `0x212d360` | 3 |
| 51 | `0x212c100` | 5 |
| 52 | `0x212d900` | 10 |
| 53 | `0x212dab0` | 10 |
| 54 | `0x212c0a0` | 3 |
| 55 | `0x212d678` | 6 |
| 56 | `0x212f6b8` | 2 |
| 57 | `0x212b068` | 4 |
| 58 | `0x212e380` | 10 |
| 59 | `0x212ff88` | 12 |
| 60 | `0x21300a8` | 2 |
| 61 | `0x2130228` | 6 |
| 62 | `0x21302b8` | 38 |
| 63 | `0x2130cf0` | 7 |
| 64 | `0x21300d8` | 14 |
| 65 | `0x2130708` | 5 |
| 66 | `0x2130648` | 8 |
| 67 | `0x2130780` | 4 |
| 68 | `0x21308d0` | 2 |
| 69 | `0x2130900` | 8 |
| 70 | `0x21309c0` | 1 |
| 71 | `0x21309d8` | 29 |
| 72 | `0x2130c90` | 4 |
| 73 | `0x2130d98` | 2 |

## Login server: the lists

`0x1bd67f4` holds 6 entries, one per group 0-5, each `{u32 start, u32 count}`. A list holds `{u32 handler, u32 key}` pairs with the same key form and ends in a u32 count, so `0x1bd6270` is group 0 and `0x1bd6294` is group 1. There are 20 handlers.

| Id | Handler | Id | Handler |
| --- | --- | --- | --- |
| 0.0.2 | `0x887740` | 3.0.2 | `0x886fd0` |
| 0.1.2 | `0x886650` | 3.0.16 | `0x887070` |
| 0.2.2 | `0x886750` | 4.0.2 | `0x8870b0` |
| 0.3.16 | `0x886820` | 5.0.2 | `0x887130` |
| 1.0.2 | `0x886970` | 5.1.2 | `0x887240` |
| 1.1.16 | `0x886b00` | 5.2.2 | `0x887320` |
| 2.0.2 | `0x886c10` | 5.3.2 | `0x8873d0` |
| 2.1.2 | `0x886d00` | 5.3.16 | `0x8874b0` |
| 2.2.2 | `0x886e00` | 5.4.2 | `0x8875b0` |
| 2.3.16 | `0x886ec0` | 5.5.16 | `0x887670` |

The login server shares ids with the game server: a raw file's name prefix (`C2L_`, `L2C_`) tells them apart. The rows were read from the executable.

In `pc-handlers`, 9 of the 20 addresses have no IDA function: `0x886650`, `0x886750`, `0x886b00`, `0x886d00`, `0x886e00`, `0x886ec0`, `0x887130`, `0x8874b0`, `0x8875b0`. `0x886b00` shows `dd` data, and decoded without creating anything it is code: `sub esp,56Ch; push esi; push edi; mov edi,ecx`. `0x886820` and `0x886fd0` lie inside functions that start at `0x88681f` and `0x886fcd`. So disassemble at the address, or create the function in your private copy. This is a coverage gap of the database, not evidence against the table.

## What ends a served connection

What the PC 03040008 client does with a server packet it cannot take, for anyone changing a server layout or adding a server packet. Marks as in the [glossary](glossary.md#evidence-marks): all `V` on the game connection, read in code; on the login connection the dispatch `0x88aab0` and vtable `+0x50`, `+0x18` were not read, so the rule there is `I`, from login handlers of the same shape. Source: `specs/010-server-packet-fixes/research/T003-pc-evidence.md`.

| Step | VA | What happens |
| --- | --- | --- |
| 1 | `0x9d6d20`, limit set at `0x9d6f2e`-`0x9d6f53` | decrypts a frame and builds a `CPacket` whose reader limit is the frame end, padding included; calls vtable `+0x44` |
| 2 | `0x844be0` | looks up group, id and sub and calls the handler. A group of `0x4A` or more, or a key with no record, returns 0 |
| 3 | `0x8bc480`, `0x8bc4d0`, `0x8bc6e0`, `0x8bc750` | `nPacket::Read_*` check bounds and return 0 without moving: no fault and no stale bytes. Readers pass the 0 up, and most handlers return it (`0x7ff580`, `0x7cd0e0`) |
| 4 | `0x9d6f78`, `0x9d7048`, `0x9d79de`-`0x9d79ec` | a 0 from vtable `+0x44` makes `0x9d6d20` return `0xBB9` (3001); its caller calls vtable `+0x50` with the code and vtable `+0x18` with 7 |
| 5 | `0x877990`, `0x87c490` | game `+0x50`: for 3000 and 3001, mode 12 and every pending request turned into an error with code 3008. That state 7 ends the session is `I`: `0x85c8e0` has no function and was not read |

So an S2C key the client has no record for, or a read past the frame end in an ordinary handler, ends the session with error 3001. 3.0.16 is the exception seen: its handler `0x887070` always returns 1.

| Also ending a session | VA | Condition |
| --- | --- | --- |
| A string | `0x8bc5b0` | an `MtString` length above `0x800` fails the read, and step 3 follows. At exactly `0x800` the stack buffer has no terminator before its copy (`I`) |
| A certificate | `0x886b5b`-`0x886b6a`, `0x886bf7` | the hash of the login certificate does not match. The game handler 44.1.16 was not read: `I` that it is the same |
| A request with no response | `0x8855a0`, `0x85c860` | after the timer passes `fps * 45.0` the client pings; on the next tick with the slot still over, every pending slot goes to status 4 with code 3008, then dialog 33001. No retry. That the unit is seconds is `I` |

A layout that is too short survives only on padding: see [Padding](packet-wire-format.md#padding).

## Senders

`nUserSession::CPacket::WritePacket` is `0x8bcbb0`, called as `WritePacket(p, group, id, sub, -1)` with the id in pushed immediates. A C2S packet's writer is the call site with its key.

| Item | Value |
| --- | --- |
| Direct `E8` calls | 658, from `0x81dd03` to `0x88a98e` |
| Login writers | 13 sites from `0x889fb3` to `0x88a98e`, in the writers from `0x889f40` to `0x88a980` |
| Distinct keys | 651, from `specs/006-packet-pattern-coverage/research/T001-triage.md`; not recounted |

## Names

The source of a PC packet name is the handler's own diagnostic string, `cSeedGameSvConnection::OnPacket_<GROUP>_<NAME>`, in the executable's data: a handler whose code references one takes it (`V`). The executable holds 675 of them and none with `cSeedLoginSvConnection`, so login names have no such source on PC. A REQ takes the name of its RES handler by pairing, which is `I`. [The marks page](packet-marks.md) gives what else may name a packet.

[IDA transfer tools](ida-transfer-tools.md#matching-rules) holds the match rules that carry these names onto the functions of the annotated database.

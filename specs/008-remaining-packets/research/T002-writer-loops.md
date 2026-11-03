# 008 T002: the five inferred C2S writer loops and the `Write_cstr` wire form (client 03040008)

Date 2026-11-03, base `211e5c9a73`. All addresses are PC 03040008 VAs (image base `0x400000`). Marks:
V = read in the PC code, I = inferred, C = contradicted.

## 1. Answer

- **All five writer lists are V.** `0x77D1E0`, `0x77FD30` and `0x77F9D0` share one shape: read count = `[arr+4]`, fail
  if count > `[arr+8]` (capacity), then **u32 count before the elements** (`Write_u32`), then for `i < count`, element
  pointer `[[arr+0x10] + 4*i]`, each element written field by field. The elements are:
  - `0x77D1E0` (70.0.1): `Write_u8 [e+4]`, `Write_u32 [e+8]` → `L[1 4]`
  - `0x77FD30` (62.24.1, 62.10.1, 12.5.1): `Write_MtString [e+4]`, `Write_u32 [e+8]` → `L[S 4]`
  - `0x77F9D0` (62.34.1): `Write_u32 [e+4]`, `Write_u32 [e+8]` → `L[4 4]`
- **`Write_cstr` `0x8BCA30` is V**: a u16 big-endian length (`strlen` truncated to 16 bits), then exactly that many
  bytes. There is **no terminator** (it copies `strlen` bytes, not the NUL). An empty string writes only the
  `00 00` prefix. This is the same wire form as `Write_MtString` `0x8BC790`, which takes the length from the MtString
  and not from `strlen`. The T001 inference (from captures) is therefore confirmed.
- **The T001 TSV `width_seq` is confirmed (V) for all five ids**, and so is `lists` = `writer-lists <va>` (one list each).
  The only change is to the T001 § 3 text. "`0x77FD30` … empty in every capture" holds for 62.24.1 (28/28) and 12.5.1
  (3/3), but not for 62.10.1: its 6 captures hold 3 or 4 elements, each an 8-byte MtString plus a u32 (§ 3). That
  part is **C**.
- **Fit**: 370/370 captures fit the IDA-read layouts (per id: 312, 28, 6, 3, 21).

## 2. IDA reads

Headless `idat` batch, read-only (the script sets `DBFL_KILL`, then `qexit`), on a `cp` of the wave-2 database.
The source is `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/spec007-packet-handlers-20261103-wave2/2022_01_29_DDO_DUMP_FIX.exe.i64`
(sha256 `ee07f0b6870cf41fcc1e21ef2c8367c079574f26bfae46b14101faaad1c38c1d`), copied to `ddon-data-t002w/`. The script
logged `get_idb_path` = the copy, a 32-bit database with image base `0x400000`, and input sha256
`f1c974d0e529d4bb7dc5f0953d37eea6bbb023f2667f9a1d3a3b878f4919fa20`. After the two batches the copy's sha256 was still
`ee07f0b6…8c1d` (not re-saved). The copy has since been deleted.

Commands (Git Bash, from `D:/ddon-data`; `<copy>` = the `.i64` above in `ddon-data-t002w/`):

    bash specs/008-remaining-packets/research/t002/run.sh <copy> <scratch>/w1.txt <scratch>/w1.log
    bash specs/008-remaining-packets/research/t002/run.sh <copy> <scratch>/w2.txt <scratch>/w2.log \
        nPacket__Write_u8 nPacket__Write_u32 nPacket__Write_bool nPacket__Write_MtString

Both logs end `read_writers: ok`. The scripts decompile with Hex-Rays and confirm every call in the disassembly
(`call` order below = instruction order).

| id | sender (VA) | `WritePacket` key | wire sequence after the header (call order in the disasm) | mark |
| --- | --- | --- | --- | --- |
| 70.0.1 | `0x81E150` `Send_C2S_ACTION_SET_PLAYER_ACTION_HISTORY_REQ` | 0x46, 0, 1 | `0x77D1E0` only → `u32 n, n×{u8, u32}` | V |
| 62.24.1 | `0x8420E0` | 0x3E, 24, 1 | `Write_u32`, `0x77FD30`, `0x781020` (`Write_u32 [+4]`, `Write_u8 [+8]`, `Write_u32 [+0xC]`), `Write_u32` → `4 L[S 4] {4 1 4} 4` | V |
| 62.10.1 | `0x83ACA0` | 0x3E, 10, 1 | `Write_u32`, `0x77FD30`, `Write_bool` → `4 L[S 4] 1` | V |
| 12.5.1 | `0x842930` | 0x0C, 5, 1 | `Write_u32`, `0x77FD30`, `Write_u32`, `Write_cstr` → `4 L[S 4] 4 C` | V |
| 62.34.1 | `0x8423B0` | 0x3E, 34, 1 | `Write_u32 [a2+4]`, `Write_u8 [a2+8]`, `Write_u32 [a2+0xC]`, `Write_u32`, `0x77F9D0` → `4 1 4 4 L[4 4]` | V |

The inline `{4 1 4}` at the start of 62.34.1 reads the same offsets as `0x781020` (+4 u32, +8 u8, +0xC u32). This is
the shared C2S struct of T001 § 3 (I: same layout, inlined).

Codec widths (pseudocode of the second batch):

| codec | VA | wire |
| --- | --- | --- |
| `nPacket::Write_u8` | `0x8BC860` | 1 byte |
| `nPacket::Write_bool` | `0x8BCB80` | 1 byte (same body as `Write_u8`) |
| `nPacket::Write_u32` | `0x8BC920` | 4 bytes, byte-swapped (big-endian) |
| `nPacket::Write_MtString` | `0x8BC790` | u16 BE length (low 16 bits of `MtString` length; 0 if null) + bytes |
| `nPacket::Write_cstr` | `0x8BCA30` | u16 BE length (low 16 bits of `strlen`) + bytes, no NUL |

Return values do not change the wire: `Write_cstr`/`Write_MtString` return 1 for an empty string and the byte count
otherwise, so a sender's `!= 0` check passes. If the length fits but the payload does not, both return 0 after the
prefix has already been written; the sender then drops the packet.

## 3. Fit against every capture

`python -X utf8 -I specs/008-remaining-packets/research/t002/fit.py` (from `D:/ddon-data`). It reads the stream
directories listed for each id in `t001/inventory.json` (sha256 `a3d54d29…e1736`) under `packets/decrypted_raw/`.
Rule (006/T001): the body starts at offset 9; the decode must not overrun and must end within the last 15 bytes.

| id | files | fit | list counts seen | tail bytes | strings |
| --- | ---: | ---: | --- | --- | --- |
| 70.0.1 | 312 | 312/312 | 1:76, 2:95, 3:82, 4:45, 5:12, 6:2 | 4-15 | none |
| 62.24.1 | 28 | 28/28 | 0:28 | 2 | none (list always empty) |
| 62.10.1 | 6 | 6/6 | 3:5, 4:1 | 4, 6 | MtString len 8, no NUL (e.g. `AA854677`, 8 hex digits), u32 0x63/0x2A/0x28/0x02 |
| 12.5.1 | 3 | 3/3 | 0:3 | 15 | cstr len 0x2A = 42 UTF-8 bytes, no NUL (`第4区画 メガドシスの記憶 山道`) |
| 62.34.1 | 21 | 21/21 | 2:11, 3:10 | 6, 14 | none |

Total 370/370; the file counts equal the T001 inventory.

12.5.1 ends with exactly 15 tail bytes, the limit of the rule: 4+4+4+2+42 = 56 of a 71-byte body. The fit alone
cannot tell `C` with a NUL (tail 14) from `C` without one, but the writer code can: it copies `strlen` bytes.

## 4. What stays inferred or open

- The element layout of `0x77FD30` for 62.24.1 and 12.5.1, and the u32 in the second half of each element, come from
  code only: no capture of these ids has a non-empty list. 62.10.1 exercises the same writer in the captures.
- The meaning of the fields (count capacity `[arr+8]`, the 8-hex-digit strings in 62.10.1, and so on) is not addressed here.
- Signedness and int vs float are not given by the widths.
- Arrowgene agreement (T001) is a lead only; it was not re-checked here.

## 5. Files

- `specs/008-remaining-packets/research/t002/read_writers.py`: idat script (decompile + disasm per VA or name;
  `DBFL_KILL`, `qexit`).
- `specs/008-remaining-packets/research/t002/run.sh`: wrapper (`MSYS_NO_PATHCONV=1 idat -A -L<log> -S"<script> <out> [args]" <copy>`).
- `specs/008-remaining-packets/research/t002/fit.py`: capture fit (stdlib).
- The raw IDA text output stayed in the session scratchpad and is reproducible with the commands in § 2.
- `T001-triage.tsv` at the start of this task: sha256 `55603cf851135c2878c99df50ed95d27ce710659e2aaa895990b77ee55212a4d`
  (unchanged; this task does not edit it).

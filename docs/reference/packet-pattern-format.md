# Packet pattern format

The lines a packet pattern of client 03040008 must carry, the shape of the JSON it exports and the checks that JSON holds, plus how raw files are named, for anyone reading or writing a pattern or a reader of `packets/decrypted_json/`. The [glossary](glossary.md#packets) defines fit and slack; [imhex-export CLI](imhex-export-cli.md) gives the export options. A label in a code span names a report: [the key](packet-ids.md#report-labels).

## Files

Each packet type has one file, `packets/patterns/03040008/<packet name>-pattern.cpp`, named after the packet name the raw files carry. Every pattern starts with `#pragma endian big` and includes what it needs from [`include/`](packet-includes.md).

## Header comment

It gives the packet id and name, the evidence (report section, PC VAs), a body summary and the lines the export script reads:

| Line | Meaning |
| --- | --- |
| `// packet-id: <group>.<id>.<sub>` | The id that `imhex-export.sh @` selects by. |
| `// packet-select: <name>` | Only where another server uses the same id. `@` then keeps only the files of that id whose name holds `_<name>_`. |
| `// packet-size: <bytes>` | Only where two packets share both id and file name. `@` then keeps only files of that size. No pattern carries it; the feature and its test stay. |

Who carries `// packet-select:`:

- `C2L_LOGIN_REQ` (0.1.1) and `L2C_LOGIN_RES` (0.1.2), because the game server's `C2S_CONNECTION_LOGIN_REQ` and `S2C_CONNECTION_LOGIN_RES` use the same ids (`R2 F2`).
- Every login pattern (`C2L_`/`L2C_`): the game server reuses the login ids 0.0.x, 0.2.x, 1.0.x, 2.0.1, 2.0.2, 3.0.x and 5.3.16 (`PacketId.cs:164-187`, lead), and naming the packet keeps a later capture of the other server out of the export.
- The game-server patterns of the shared ids: 0.0.1-0.2.2, 1.0.1, 1.0.2 (`T003b`), and 2.0.1, 2.0.2 and 5.3.16, for which no login-server file is captured, so their selection does not change.

The certificate notice shows why the size line existed. The CLI once filed the server's 304-byte certificate notice under the same `.1_0_1` name as the 336-byte `C2L_CLIENT_CHALLENGE_REQ` (`T002c §3`). The notice is `1.1.16 L2C_LOGIN_SERVER_CERT_NTC`, so the challenge pattern needs no size line.

## JSON conventions

- The root key is `packet`. Header keys are lowercase: `group`, `id`, `subId`, `source`, `packetcounter`.
- Lists export as `{count, entries}` and strings as `{length, value}`.
- A NaN or infinite float is written as `null` (the default `--json-nonfinite=null`; no reader of `packets/decrypted_json/` needs a bare `nan`). The raw file keeps the float's bytes, so the value is recoverable from `packets/decrypted_raw/`. The only such values are the 65 group-35 CONTEXT packets of `stream85-marked.pcapng_tcp-stream-11` (35.9.16, 35.13.16; `"y": -nan`, `T014a`).
- String values are UTF-8 JSON strings, written as is with the standard escapes (`\"`, `\\`, `\n`, `\r`, `\t`, `\u00XX` for control characters), with no percent encoding. A byte that is not valid UTF-8 comes out as `\u00XX`, which reads the same as the code point U+00XX.
- The ImHex 1.38.1 fallback writes every byte outside `[A-Za-z0-9-_.~]` as `%XX` (`"Rumi%20Amestris"`).
- `CDataOmData.Key` carries the high bit (0x80000000_001415b3), so the JSON integer exceeds 2^53. A reader that parses numbers as doubles rounds it; Python `json` keeps it exact.
- `packets/decrypted_json/` holds only ImHex-format output (`packets/imhex-export.sh`), so a stream gets a JSON folder only when one of its packets was exported with a pattern. Every captured stream has one.

## RES error guard

The PC reads `s32 Error`, and reads Result and the body only when Error is 0 (`P11a` G1). PS4 reads a u16 Error; the captures back the PC's s32 (`R2`). Every RES pattern writes the guard inline, `s32 Error; if (Error == 0) { s32 Result; ... }`, so every RES JSON holds `packet.Error` and, on success, `packet.Result` (`R2 F3`). There is no `ResHeader` struct.

[Why the RES guard exists](../explanation/wire-protocol.md#why-the-res-guard-exists) gives the reason. There is one exception. On 18.0.2 the server writes Result and an empty list after a non-zero Error, although the client stops reading after Error. The pattern decodes those 8 bytes as `unk_serverResult` and `unk_serverListCount`, and only when more than 15 bytes remain.

## Exported checks

| Key | Meaning |
| --- | --- |
| `sourceOk` | The header source byte matches the direction in the name: 0x00 client for C2S/C2L, 0x34 server for S2C/L2C. Patterns whose name gives the direction export it. 63.11.16 has source 0x00 although its name says S2C (`P10`). |
| `paddingSize` | The bytes left after the decode: the slack. |
| `fits` | `paddingSize <= 15`. The raw files store no body length and are padded to 16-byte blocks, so a decode fits when it ends inside the cipher padding. Reading past the end fails the decode. The nNetMsg patterns export it after the packet's last field. |
| `msgFits` | nNetMsg patterns only: the message ended exactly at its `len` field. |

A fit proves that the decode did not overrun the packet and left less than one cipher block. It does not prove field widths or field order ([why](../explanation/packet-decoding-method.md#what-a-fit-proves)).

- When the slack is larger than a field, a body that is that field shorter or longer fits as well: a 16-byte packet fits any body of 0-7 bytes.
- Two same-width fields in swapped order fit identically (`R1 F3`, `R2 F1`).
- Widths and order rest on the PC readers and writers.

## Raw file names

A raw file under `packets/decrypted_raw/<stream>/` holds header plus payload, and is named by the patched CLI:

```text
<pcap no>_<PacketId.Name>_<timestamp>.<group>_<id>_<sub>
<pcap no>_<PacketId.Name>_<timestamp>_<n>.<group>_<id>_<sub>
```

- The name is the `Name` string of the CLI's `PacketId` table, not the C# field name. They differ for 63.11.16: field `C2S_63_11_16_NTC`, Name `S2C_63_11_16_NTC`, declared `PacketSource.Server` although the client sends it.
- Timestamps have 100 ns precision.
- A frame with several packets of one id gives the second form to all but the last of them (n = 1, 2, ...; up to 26 in these captures). The last keeps the unsuffixed name, and order within the frame is `_1`, `_2`, ..., then the unsuffixed file: `12008_S2C_QUEST_FORT_DEFENSE_NTC_2019-07-06T11_05_43.1647770-07_00_1.11_95_16` is the first of two packets whose second is `..._2019-07-06T11_05_43.1647770-07_00.11_95_16`.
- The suffix sits in the stem, so the id filters of `packets/imhex-export.sh` (extension) and `// packet-select:` (`_<name>_`) select these files unchanged.
- The header-less raw files hold only the body: the first packet of each direction, as `1.0.1`, `44.0.1`, `1.1.16` and `44.1.16`. A `C2S_SERVER_GET_SERVER_LIST_REQ` (1.0.1) file does start with the 9-byte header.

The JSON file of a raw file sits at the same relative path under `packets/decrypted_json/` with `.json` added.

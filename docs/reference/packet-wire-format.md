# Packet wire format, client 03040008

The bytes of a DDON connection of the PC client 03040008, from the TCP frame down to a string field, for anyone reading a capture or a raw file. The [glossary](glossary.md#packets) defines the terms; [Wire protocol](../explanation/wire-protocol.md) says why it is built this way; [Read one packet by hand](../tutorials/read-one-packet.md) walks one packet. A label in a code span names a report: [the key](packet-ids.md#report-labels). Every example below was read with `xxd` or `jq` on 2026-11-04.

## Framing

Each direction of a TCP stream is a run of frames. A frame can span TCP segments, and one segment can hold several frames.

| Part | Form |
| --- | --- |
| length | u16 big-endian: the size of the ciphertext that follows |
| ciphertext | Camellia-256-CBC, a whole number of 16-byte blocks |

The first frames of `packets/encrypted_streams/stream1-marked.pcapng_tcp-stream-33.yaml`, whose `data` fields are base64:

| Pcap packet | Direction | Length bytes | Frame size | Packet |
| --- | --- | --- | --- | --- |
| 11756 | server | `01 30` | 306 | 1.1.16 `L2C_LOGIN_SERVER_CERT_NTC` |
| 11758 | client | `01 50` | 338 | 1.0.1 `C2L_CLIENT_CHALLENGE_REQ` |
| 11759 | server | `00 60` | 98 | 1.0.2 `L2C_CLIENT_CHALLENGE_RES` |

The server emulator refuses a length below 16 (`PacketMinimumDataSize` in its `PacketFactory.cs`, a lead).

## Cipher

| Constant | Value | Used for |
| --- | --- | --- |
| Mode | Camellia-256-CBC | every frame |
| IV | `$cbM6WP)aX=%J^zA`, the same for every frame | every frame |
| Fixed client key | `f23e98HafJdSoaj80QBjhh23oajgklSa`: the first 32 characters of the client's string `f23e98HafJdSoaj80QBjhh23oajgklSadrhogh2IJnwJEF58` (pointer `pKey` at PC `0x2135d90`, `T003 §1`) | the first frame of each direction |
| Session key | 32 ASCII characters: the first 32 of the client's 48-character common key. Stored per stream in column `decryption_key` of `packets/keys/keys-all-in-one.csv` | every later frame |
| Password blob | Blowfish-ECB, key `mofumofu capcom(^-^)`, 32-bit words byte-swapped, plaintext `0123456789abcdef` | `PasswordEnc` inside the client challenge |

Checked on stream1 tcp-stream-33 with its CSV key `3jc6R11q__MGmP9YIn7fyiNVQgSUoiBc`: the decrypted frames of pcap packets 11756 and 11758 (fixed key) and 11759 (session key) equal their files under `packets/decrypted_raw/`, and the password blob of 11758 decrypts to that plaintext.

## Known plaintext

The first frame under the session key is the challenge response, always 96 bytes of ciphertext. Its plaintext makes the session key testable. The expected bytes `decrypt-pcapng-streams-all-in-one.sh` passes to the key search:

| Server | Response | Expected plaintext |
| --- | --- | --- |
| login | 1.0.2 | `0100000234000000` |
| game-select, game | 44.0.2 | `2C00000234000000` |

The first block is fully known, and the second was the same in all four files checked (one login stream, three game streams):

```text
$ xxd -l 32 packets/decrypted_raw/stream1-marked.pcapng_tcp-stream-33/11759_L2C_CLIENT_CHALLENGE_RES_2019-07-06T11_05_21.7244169-07_00.1_0_2
00000000: 0100 0002 3400 0000 0000 0000 0000 0000  ....4...........
00000010: 0010 1089 79ee d698 ad50 7855 02cc b988  ....y....PxU....
```

## Header

The 9 bytes every packet but the first of each direction starts with, declared as `CPacket` in `packets/patterns/03040008/include/Packet.hexpat`. Every multi-byte value of a packet is big-endian.

| Offset | Type | Field | Values |
| --- | --- | --- | --- |
| 0x00 | u8 | group | the first number of the [packet id](glossary.md#packets) |
| 0x01 | u16 | id | the second |
| 0x03 | u8 | sub | the third: 1 REQ, 2 RES, 16 NTC in the names of these packets |
| 0x04 | u8 | source | 0x00 client, 0x34 server |
| 0x05 | u32 | counter | see below |

The body starts at 0x09. A `sourceOk` key in the JSON states whether the source byte matches the name's direction; 63.11.16 is the known exception ([Exported checks](packet-pattern-format.md#exported-checks)).

The counter, as seen in two streams (stream1 tcp-stream-33 and stream3 tcp-stream-47, 749 files): a client packet and a server NTC carry a counter above 0, and a server RES carries 0. Client counters climb in capture order, with neighbours sometimes swapped. No pattern tests this: **Status:** approximate (a sample).

## First packet of each direction

These carry no header on the wire, and their raw files hold only the body from offset 0.

| Connection | Client sends | Server sends |
| --- | --- | --- |
| login | 1.0.1 `C2L_CLIENT_CHALLENGE_REQ`, 324-byte body plus 12 of padding | 1.1.16 `L2C_LOGIN_SERVER_CERT_NTC`, 292-byte body plus 12 of padding |
| game | 44.0.1 `C2S_CERT_CLIENT_CHALLENGE_REQ` | 44.1.16 `S2C_CERT_GAME_SERVER_CERT_NTC` |

- The client writer builds a normal header, and `cSeedServerConnection::Send` (PC `0x9d6a20`) drops those 9 bytes when group and id match the connection's handshake command and sub is 1.
- The receive path (PC `0x9d6d20`) synthesizes a header for the server's first packet: group and id from the connection, sub 0x10, counter 0.

| Connection, vtable | Send group, id | Receive group, id |
| --- | --- | --- |
| game, `0x1bc5c38` | 0x2c, 0 | 0x2c, 1 |
| login, `0x1bd6af8` | 1, 0 | 1, 1 |

The certificate body is `OpenModulo[256]`, `OpenExpo[16]` and `OpenHash` (20 bytes, SHA-1 of the two): `packets/patterns/03040008/include/Cert.hexpat`. The exponent is 17:

```text
$ xxd -s 256 -l 32 packets/decrypted_raw/stream1-marked.pcapng_tcp-stream-33/11756_L2C_LOGIN_SERVER_CERT_NTC_2019-07-06T11_05_21.5170779-07_00.1_1_16
00000100: 0000 0000 0000 0000 0000 0000 0000 0011  ................
00000110: 4154 5b39 d09a 60b5 7b8d 9634 8003 cb2b  AT[9..`.{..4...+
```

## RES header

A RES body starts with `s32 Error`. `s32 Result` and the rest follow only when Error is 0 (PC readers `0x805340`, `0x8015b0`, `0x801530`). [RES error guard](packet-pattern-format.md#res-error-guard) gives the pattern rule; [Why the RES guard exists](../explanation/wire-protocol.md#why-the-res-guard-exists) gives the reason.

An error, in `packets/decrypted_raw/stream85-marked.pcapng_tcp-stream-11/10290_S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES_2019-11-18T10_14_21.6860070-08_00.18_0_2`:

```text
00000000: 1200 0002 3400 0000 0000 00b7 9b00 00b7  ....4...........
00000010: 9b00 0000 0000 0000 0000 0007 d540 0100  .............@..
```

| Offset | Bytes | Field |
| --- | --- | --- |
| 0x09 | `00 00 b7 9b` | Error 47003 |
| 0x0d | `00 00 b7 9b` | what the server wrote as Result; the client does not read it |
| 0x11 | `00 00 00 00` | what the server wrote as an empty list's count; nor this |
| 0x15 | 11 bytes | padding |

## Lists

`MtTypedArray<T>` in `packets/patterns/03040008/include/Packet.hexpat`: a u32 count, then that many elements with no per-element length. Every PC list reader starts with `nPacket::Read_u32` into the count (`P11a`).

From `packets/decrypted_raw/stream65-epi1-4-marked.pcapng_tcp-stream-9/1957_S2C_ITEM_ACHIEVEMENT_REWARD_RECEIVE_NTC_2019-10-13T12_02_20.8803129-07_00.10_14_16`, a u16 and a list of `{u8, u32}`:

```text
00000000: 0a00 0e10 3400 0000 a800 0200 0000 0107  ....4...........
00000010: 0000 3f63 0100 003f 6300 0100 0000 0000  ..?c...?c.......
```

| Offset | Bytes | Field |
| --- | --- | --- |
| 0x09 | `00 02` | u16, 2 |
| 0x0b | `00 00 00 01` | count, 1 |
| 0x0f | `07` | element u8, 7 |
| 0x10 | `00 00 3f 63` | element u32 `ItemId`, 16227 |
| 0x14 | 12 bytes | padding |

## Strings

A u16 big-endian length, then that many bytes, with no terminator. An empty string is `00 00`. Text is UTF-8 in the captures.

| Client routine | PC VA | Length comes from |
| --- | --- | --- |
| `nPacket::Write_MtString` | `0x8BC790` | the `MtString`: low 16 bits, 0 if null |
| `nPacket::Write_cstr` | `0x8BCA30` | `strlen`, low 16 bits; the NUL is not copied |
| `nPacket::Read_MtString` | `0x8bc5b0` | the wire; a length up to 0x800 |

The writers are the same on the wire (`008 T002`), and both patterns use `MtString`. A `Write_cstr` string in `packets/decrypted_raw/stream85-marked.pcapng_tcp-stream-11/13597_C2S_STAGE_UNISON_AREA_CHANGE_BEGIN_RECRUITMENT_REQ_2019-11-18T10_19_19.2371139-08_00.12_5_1`:

```text
00000010: 0000 0004 5700 2ae7 acac 34e5 8cba e794  ....W.*...4.....
00000020: bb20 e383 a1e3 82ac e383 89e3 82b7 e382  . ..............
00000030: b9e3 81ae e8a8 98e6 86b6 20e5 b1b1 e981  .......... .....
00000040: 935e 0b5e 0000 064c 000f 0000 0000 0000  .^.^...L........
```

The length `00 2a` at 0x15 covers 42 bytes, 0x17 to 0x40, which the JSON gives as `"SectionName":{"length":42,"value":"第4区画 メガドシスの記憶 山道"}`. The last byte of the text is at 0x40, with no NUL after it; the 15 bytes from 0x41 are padding.

## Padding

- The cipher works in 16-byte blocks over header plus body, so a raw file's size is a multiple of 16 and the padding is 0 to 15 bytes. Both held for all 749 files of the two streams above.
- The raw files and the frames store no body length: a reader of a file finds the end of the body only by decoding it.
- Padding bytes are not zeroed and not constant. They can repeat earlier data, as the `3f 63` in the padding of the list example does.

## nNetMsg payloads

The lobby and party binary packets carry a message inside a counted byte array (`P1`, `P2`), decoded by `packets/patterns/03040008/include/nNetMsg.hexpat`.

| Packet | Body after the header |
| --- | --- |
| 3.3.16 `C2S_LOBBY_LOBBY_DATA_MSG_REQ` | u8 Type, u32 CharacterId, s32 len, u8[len] |
| 3.4.16 | u8 Type, u32 CharacterId, s32 len, u8[len], u8 OnlineStatus |
| 6.25.16 `C2S_PARTY_SEND_BINARY_MSG_NTC` | u32 count, u32 CharacterId[count], s32 len, u8[len] |
| 6.23.16 `C2S_PARTY_SEND_BINARY_MSG_ALL_NTC` | s32 len, u8[len] |
| 6.24.16, 6.26.16 | u32 CharacterId, s32 len, u8[len], u8 OnlineStatus |

The message starts with a 20-byte head: s32 `mSessionId`, u64 `mRpcId`, u32 `mMsgIdFull`, u32 `mSearchId`. `mMsgIdFull & 0xFFFFFF00` selects the message class. There is one message per packet, and `len` is its only length. From `packets/decrypted_raw/stream3-party-experiments-marked.pcapng_tcp-stream-47/12865_C2S_LOBBY_LOBBY_DATA_MSG_REQ_2019-07-08T10_35_53.4762110-07_00.3_3_16`:

```text
00000000: 0300 0310 0000 0000 8402 0000 0000 0000  ................
00000010: 009b 0000 0002 0000 0000 0000 07d0 4001  ..............@.
00000020: 0002 0000 0000 8000 0000 0000 0001 0001  ................
```

| Offset | Bytes | Field |
| --- | --- | --- |
| 0x09 | `02` | Type |
| 0x0a | `00 00 00 00` | CharacterId |
| 0x0e | `00 00 00 9b` | len, 155 |
| 0x12 | `00 00 00 02` | `mSessionId`, 2 |
| 0x16 | `00 00 00 00 00 00 07 d0` | `mRpcId`, 2000 |
| 0x1e | `40 01 00 02` | `mMsgIdFull`: class `cNetMsgCtrlAction` (0x40010000), message 2 |
| 0x22 | `00 00 00 00` | `mSearchId` |

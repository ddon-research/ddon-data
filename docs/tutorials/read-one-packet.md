# Read one packet by hand

This tutorial is for a reverse engineer who has never opened this repository's packet data: you decode one server response of client 03040008 from its bytes and match the result against the committed JSON. You need a full clone with the packet data, `xxd`, `jq` and `fd`. No IDA, game client, ImHex or build is involved and nothing is written. The commands and outputs below were run on 2026-11-04, and `tools/docs_check.py` keeps the inputs pinned.

The inputs are fixed:

| File | SHA-256 |
| --- | --- |
| `packets/decrypted_raw/stream3-party-experiments-marked.pcapng_tcp-stream-47/12863_S2C_WARP_WARP_RES_2019-07-08T10_35_53.3199119-07_00.14_3_2` | `4a693d40ba70f74a7b2af3b43ee028e96a5cb9f298abb533d5ba1dd27ac8759f` |
| `packets/decrypted_json/stream3-party-experiments-marked.pcapng_tcp-stream-47/12863_S2C_WARP_WARP_RES_2019-07-08T10_35_53.3199119-07_00.14_3_2.json` | `d93d890bc91a8c758d322f28b344fbd84044b979d0cebfd0ca3ce76786c79b1b` |
| `packets/patterns/03040008/S2C_WARP_WARP_RES-pattern.cpp` | `0e8e3f859a7d1b2988054ed97be3c83cdc597850ab0856a124cc37a68b63c044` |

## Step 1: Dump the raw file

From the repository root, name the file and dump it. A raw file is one decrypted packet, so its 32 bytes are the whole message.

```sh
R=packets/decrypted_raw/stream3-party-experiments-marked.pcapng_tcp-stream-47/12863_S2C_WARP_WARP_RES_2019-07-08T10_35_53.3199119-07_00.14_3_2
wc -c "$R"
xxd "$R"
```

```text
32 packets/decrypted_raw/stream3-party-experiments-marked.pcapng_tcp-stream-47/12863_S2C_WARP_WARP_RES_2019-07-08T10_35_53.3199119-07_00.14_3_2
00000000: 0e00 0302 3400 0000 0000 0000 0000 0000  ....4...........
00000010: 0000 0000 4200 0098 c55b ba26 6063 30a9  ....B....[.&`c0.
```

## Step 2: Read the header

Every multi-byte value is big-endian. The header is the first 9 bytes, and `packets/patterns/03040008/include/Packet.hexpat` declares it as `CPacket`.

| Offset | Bytes | Field | Value |
| --- | --- | --- | --- |
| 0x00 | `0e` | group | 14 |
| 0x01 | `00 03` | id | 3 |
| 0x03 | `02` | sub | 2 |
| 0x04 | `34` | source | server (0x00 is the client) |
| 0x05 | `00 00 00 00` | counter | 0 |

Group, id and sub form the [packet id](../reference/glossary.md#packets), 14.3.2. Look at the file name: it ends in `14_3_2`.

## Step 3: Read the pattern

The pattern states the body's layout.

```sh
sed -n '1,30p' packets/patterns/03040008/S2C_WARP_WARP_RES-pattern.cpp
```

The lines to look at are these:

```text
// PC handler 0x7ff580, reader 0x81dc00: RES header, u32, u32 (V). PS4 OnPacket_S2C_WARP_RES
// 0x2f7190: u32 m_unWarpPointID, u32 m_unrim (V). Walk: 44/44 fit, slack 7.
// Body: s32 Error [, s32 Result, u32 WarpPointID, u32 Rim] (16 bytes).
```

The `(V)` is an [evidence mark](../reference/glossary.md#evidence-marks): that layout was read in code.

## Step 4: Read the body

The body starts at offset 0x09. Walk it with the pattern's layout.

| Offset | Bytes | Field | Value |
| --- | --- | --- | --- |
| 0x09 | `00 00 00 00` | Error | 0 |
| 0x0d | `00 00 00 00` | Result | 0 (present because Error is 0) |
| 0x11 | `00 00 00 42` | WarpPointID | 66 |
| 0x15 | `00 00 98 c5` | Rim | 39109 |
| 0x19 | `5b ba 26 60 63 30 a9` | padding | 7 bytes, not part of the message |

The raw files store no body length and are padded to a multiple of 16 bytes, which is why the last 7 bytes carry no field.

## Step 5: Compare with the JSON

The export of that same pattern over that same file is committed.

```sh
jq -c . "packets/decrypted_json/${R#packets/decrypted_raw/}.json"
```

```text
{"packet":{"group":14,"id":3,"subId":2,"source":52,"packetcounter":0,"sourceOk":true,"Error":0,"Result":0,"WarpPointID":66,"Rim":39109,"paddingSize":7,"fits":true}}
```

Every value is the one you read by hand. `source` 52 is 0x34. `paddingSize` is your 7 bytes.

## Step 6: See what `fits` says

Count the flag across every capture of this packet.

```sh
fd -d 2 -t f S2C_WARP_WARP_RES packets/decrypted_json -x jq -r .packet.fits | sort | uniq -c
```

```text
     44 true
```

A decode [fits](../reference/glossary.md#packets) when it ends within the last 15 bytes of the file. So try the weaker reading yourself: drop `Rim` from your walk. The decode then ends at 0x15, leaves 11 bytes, and still fits. A fit shows that a layout is not too long; it does not prove the widths.

## What you learned

- A raw file is a 9-byte header, a big-endian body and cipher padding, and the file name carries the packet's id.
- A pattern's JSON is that walk, written down, and you can check it with `xxd`.
- The layout of 14.3.2 stands because PC reader `0x81dc00` of client 03040008 reads it, as the pattern's header says. The 44 fits only fail to contradict it.

Next: the [glossary](../reference/glossary.md) names the terms used here, and the pattern's first comment lines cite the evidence report behind it. [Two packet decodings](../explanation/two-packet-decodings.md) sets this JSON beside the server CLI's reading of the same packet, and [Write a packet pattern](../how-to/write-a-packet-pattern.md) goes from an id to a pattern of your own.

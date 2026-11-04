# Inspect captures in Wireshark

This page is for anyone who wants to see how DDON traffic splits into streams and messages in a `.pcapng`, before or without decrypting it. You load a small Lua postdissector and use the display filters beside it. You need Wireshark or `tshark` with Lua. It shows framing only: for decoded packets, see [Decrypt a capture](decrypt-a-capture.md).

The two files are `packets/wireshark/wireshark-ddon-tcp-postdissector.lua` and `packets/wireshark/wireshark-filters.txt`. Neither names a client build. The checks below ran on `stream85-marked.pcapng` with Wireshark 4.6.9.

## Install the dissector

Choose one:

- **For every run:** copy the Lua file into the personal Lua plugins folder, which `tshark -G folders` prints as `Personal Lua Plugins`.
- **For one run:** `tshark -X lua_script:<path> ...`.

Do not do both: a second load fails with `there cannot be two protocols with the same description`. Success is a `DDON` row, which this prints:

```sh
tshark -G protocols | rg DDON
```

## Point it at your stream

The dissector only looks at **TCP stream 11**. The test is hard-coded on its line 48: `tcp_payload and tcp_stream == 11 and` the source or destination port is 52000 or 52100. In any other stream it adds nothing, so change that number to the stream you want, in your copy. To find the number, see [Find streams](#find-streams).

## Read what it adds

Filter with `ddon`. Each matching frame gets a `DDON Protocol Data` subtree:

| Field | Value |
| --- | --- |
| `ddon.src`, `ddon.dst` | `S` for the port 52000 or 52100 side, `C` for the other |
| `ddon.conv` | `S2C` or `C2S` |
| `ddon.payload` | the TCP payload as hex |
| `ddon.datasize` | the first two bytes of the payload read as a big-endian size, when the dissector expects a message start |
| `ddon.buffersize` | the bytes counted towards that size, which includes the size field |

For a table of them:

```sh
tshark -X lua_script:<path> -r stream85-marked.pcapng -T fields -e frame.number -e tcp.stream -e ddon.conv -e ddon.datasize -e ddon.buffersize -Y ddon
```

Its first lines on that capture, output of 2026-11-04:

```text
10139	11	S2C	304	306
10141	11	C2S	336	338
10142	11	S2C	304	306
10144	11	C2S	336	338
10145	11	S2C	16	18
10147	11	S2C	16	18
```

## What it does not do

- **It does not decrypt.** The payload stays cipher text, with no packet id or name.
- **It does not reassemble.** It counts per TCP segment and keeps one running state per direction in global variables, which reset at relative sequence number 1. Clicking around in the Wireshark GUI re-dissects frames, so trust those two fields only in a first in-order pass.
- **`ddon.datasize` can be stale.** After a message completes, the next frame only closes that message and does not read a size. Frame 10147 above starts with `0020`, and still shows size 16.
- **It holds no field of a packet body.** For those, see the [packet patterns](../reference/packet-ids.md).

## Find streams

`packets/wireshark/wireshark-filters.txt` holds these display filters. They find the first packet of each stream kind:

| Stream | Filter |
| --- | --- |
| login | `data.len eq 98 && tcp.port eq 52100 && tcp.window_size eq 130560` |
| server select | `data.len eq 98 && tcp.port eq 52000 && tcp.window_size eq 130560` |
| game | `data.len eq 98 && tcp.port eq 52000 && tcp.window_size eq 65792` |

An alternative: filter `frame.len eq 360`, then look for the frame length sequence 360, 54, 392, 152. The first such sequence is login, the second server select and the third game.

The filters are empirical, and the key search in [Decrypt a capture](decrypt-a-capture.md) uses the same ones.

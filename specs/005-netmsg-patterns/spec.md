# 005 NetMsg ImHex patterns (lobby data and party binary messages)

**Status: active** (opened 2026-11-01, Sam's request)

## Goal

Decode, as faithfully as the evidence allows, the `nNetMsg` payloads that Season 3 PC clients
(build **03040008**) send through:

| Packet | Id | Count in `packets/decrypted_raw` |
| --- | --- | --- |
| `C2S_LOBBY_LOBBY_DATA_MSG_REQ` | 3.3.16 | 59,881 |
| `C2S_PARTY_SEND_BINARY_MSG_NTC` | 6.25.16 | 29,176 |
| `C2S_PARTY_SEND_BINARY_MSG_ALL_NTC` | 6.23.16 | 8 |
| `S2C_LOBBY_LOBBY_DATA_MSG_NTC` (server relay of 3.3.16, same payload) | 3.4.16 | 21,000 |

Deliverables:

1. ImHex patterns in `research/03040008/packets/`, replacing the three stubs
   (`C2S_LOBBY_DATA_MSG_REQ`, `C2S_SEND_BINARY_MSG_NOTICE`, `C2S_SEND_BINARY_MSG_ALL_NOTICE`)
   and sharing one include for the `nNetMsg` body, plus the S2C relay.
2. `packets/imhex-export.sh` able to run them over `packets/decrypted_raw` (any changes it needs).
3. A run over every matching packet with counts of decoded, partially decoded and failed packets,
   and the remaining unknown fields listed.

## Evidence order

- Wire format: PS4 02020005 `nNetMsgData::*::deserialize` (named, Season 2) is the seed; PC 03040008
  (`IDA9.5` database, headless ida-mcp on a private copy) decides Season 3 differences. Captured
  bytes corroborate. Arrowgene (`Arrowgene.DragonsDogmaOnline.Upstream`) documents the outer
  packet fields only.
- Fields not confirmed on PC are marked `// inferred` (or `// PS4 only`) in the pattern.

## Out of scope

Regenerating `packets/decrypted_json` for other packet types; changing the decrypt toolchain.

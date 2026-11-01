005 P3: nNetMsg ImHex patterns and the export over decrypted_raw

Objective (build: 03040008): write ImHex patterns that decode, field by field, the nNetMsg payloads
of the four packet types below, run them over every matching packet in `packets/decrypted_raw/`,
and report counts. The wire format is fully specified in two reports; transcribe it, do not
re-derive it:
- `specs/005-netmsg-patterns/research/P1-ps4-wire-format.md`: the PS4 02020005 baseline (framing
  section 1, decoders section 2, include table section 3, DTI ids and NET_MSG_ID enums section 4).
- `specs/005-netmsg-patterns/research/P2-pc-deltas.md`: the Season 3 PC deltas, which **override**
  P1 wherever they differ (u64 ids, widened fields, added fields, changed conditions, new msg ids
  0x3C/0x3D, GameNormal 0x0F-0x12, GameEasy ids +4, include table section 3, packet bodies section 5).
  P2's walker, with exactly those rules, ends all 89,065 captured C2S payloads at `len`;
  section 6.2 has byte-by-byte walks to compare your output with.

| Packet (file-name substring) | Count | Body (P1 1 / P2 5) |
| --- | --- | --- |
| `C2S_LOBBY_LOBBY_DATA_MSG_REQ` (3.3.16) | 59,881 | u8 Type, u32 CharacterId, s32 len, NetMsg[len] |
| `S2C_LOBBY_LOBBY_DATA_MSG_NTC` (3.4.16) | 21,000 | same + u8 OnlineStatus |
| `C2S_PARTY_SEND_BINARY_MSG_NTC` (6.25.16) | 29,176 | u32 count, u32 CharacterIds[count], s32 len, NetMsg[len] |
| `C2S_PARTY_SEND_BINARY_MSG_ALL_NTC` (6.23.16) | 8 | s32 len, NetMsg[len] |

Every file starts with the 9-byte packet header (`u8 group, u16 id, u8 subId, u8 source, u32
counter`, big-endian, as the current stubs have it). Bytes after the body are block padding of
the decrypted packet (inferred): export them as `padding`, not as fields.

Requirements:
1. `research/03040008/packets/include/nNetMsg.hexpat` (new): `#pragma endian big`-safe shared
   definitions: enums (NET_MSG_ID per group with P1 names; Season 3 ids without a name as
   `NET_MSG_ID_UNK_0x3C` etc.; LOBBY_MSG_TYPE; MSG_ADR if used; OnlineStatus from Arrowgene
   `Arrowgene.Ddon.Shared/Model/OnlineStatus.cs` in
   `C:/Users/morph/Documents/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Upstream`), the include
   table as a function of the msg id (P2 3), Head, CtrlBase, CtrlAction with every helper, GameNormal,
   GameEasy, SetNormal, ToolEasy, popNetPos/popNormalPos types, and one `NetMsg<len>`-style entry
   that dispatches on `msgIdFull & 0xFFFFFF00` and ends with `u8 unparsed[end - $]` for anything
   it does not know (never let an unknown id fail the pattern).
   Variable-width fields (P1/P2: mRegionRateBit by popcount, bit-packed condition bytes, clamped
   counts) follow the decoder exactly. Comment each struct with the PC VA (P2 1) and mark fields
   that are inferred (`// inferred`) or placeholders for unnamed Season 3 fields (`unk_...`).
2. Four packet patterns named after the packets: `<packet>-pattern.cpp` in
   `research/03040008/packets/`, each `#include "nNetMsg.hexpat"`. Each exports
   `msgFits` = (the NetMsg ended exactly at `len`) and the decoded msg id, so fits can be counted
   per msg id from the JSON. Remove (`git rm`) the stubs `C2S_LOBBY_DATA_MSG_REQ-pattern.cpp`,
   `C2S_SEND_BINARY_MSG_NOTICE-pattern.cpp`, `C2S_SEND_BINARY_MSG_ALL_NOTICE-pattern.cpp`
   (Sam: "feel free to completely revamp").
3. `packets/imhex-export.sh` already passes `include/` with `-I` (coordinator's uncommitted edit,
   tested; you own committing it). Update its usage example to one of the new patterns. Change it
   further only if the run needs it.
4. Run, in the background, one export per packet type with `--force` and 32 jobs:
   `bash packets/imhex-export.sh --force <packet> <packet> 32` (about 40 packets/s; ~110k packets,
   ~45 min). This rewrites the tracked JSON of these four types in `packets/decrypted_json/` (Sam
   asked to run the patterns over this data). Develop first on a sample with
   `RAW_DIR=<scratch> JSON_DIR=<scratch>` (copy ~200 files per type, all msg ids, into your
   scratch folder), compare with P2 6.2's walks, and start the full run only when the sample has
   0 failures and every sample fits.
5. Counts in the receipt, per packet type: exported, failed (`.json.err`), `msgFits` true/false
   per msgIdFull. Any non-fit or failure: list msg id, count, one file path.

Owns: `research/03040008/packets/include/nNetMsg.hexpat`, the four new patterns, the three stubs
(removal), `packets/imhex-export.sh`, and in `packets/decrypted_json/` only the `*.json` (and any
`*.json.err`) of the four packet types. Others own everything else.
Never touch: other packet patterns or JSON, `client/`, `packets/decrypted_raw/`, `research/03040008/flags/`,
`research/external-references.jsonl`, `binaries/`, the dirty paths in `git status` that are not yours.
Libraries: ImHex pattern language std library (`import std.mem;` etc.); ImHex at
`/e/Software/imhex-1.38.1-Windows-Portable-NoGPU-x86_64/imhex.exe` (not on PATH; the export script
finds it). `rg`/`jq` for counting. Own code only where none fits, reason in the receipt.
Done: the gate `bash tools/check.sh --since <base>` passes (shell syntax); the sample and full-run
counts above; commits: (1) include + patterns + stub removal + script, (2) the regenerated JSON
(stage it by explicit pathspec per packet type, e.g. `git add -- 'packets/decrypted_json/*/*C2S_LOBBY_LOBBY_DATA_MSG_REQ*'`;
never `git add -A`/`.`; check `git diff --cached --stat | tail -1` matches the export counts).
End with the receipt (role file).
Stop: budget 150 min including the run. Stop and ask if more than 1% of any packet type fails or
does not fit after the sample stage, or if a P1/P2 statement cannot be expressed in the ImHex
pattern language.
Base: <filled at spawn>. Commit trailer: Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>

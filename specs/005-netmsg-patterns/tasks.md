# 005 tasks

Coordinator: main session. One subagent at a time.

- [x] T001 Survey stubs, export script, packet counts, Arrowgene structures (coordinator).
- [x] T002 IDA access: `research/ida/private-copy.sh` + role `evidence-researcher-ida` (headless
  ida-mcp, the reconstructor's pattern); smoke-tested copy and server start.
- [x] T003 P1 PS4 02020005 wire format of every `nNetMsgData` decoder, the include table and the
  send/receive framing of 3.3.16 / 3.4.16 / 6.23.16 / 6.25.16 (`evidence-researcher-ida`, brief
  `briefs/P1-ps4-wire-format.md`, report `research/P1-ps4-wire-format.md`).
- [x] T004 P2 PC 03040008 deltas against P1 (include table, added fields, framing), brief
  `briefs/P2-pc-deltas.md`, report `research/P2-pc-deltas.md`.
- [ ] T005 Patterns: shared `nNetMsg` include + 4 packet patterns.
- [ ] T006 `packets/imhex-export.sh` updates; run over `decrypted_raw`; counts.
- [ ] T007 Review, docs, commit.

## Running agents

- (none)

## Next step (2026-11-01)

After P2 lands: brief P3 for an `implementer` (T005 + T006). Decisions taken:
- Patterns are named after the packets (`C2S_LOBBY_LOBBY_DATA_MSG_REQ`, `S2C_LOBBY_LOBBY_DATA_MSG_NTC`,
  `C2S_PARTY_SEND_BINARY_MSG_NTC`, `C2S_PARTY_SEND_BINARY_MSG_ALL_NTC`), so the export filter and
  pattern name are the same; the three stubs are removed (Sam: "feel free to completely revamp").
- One shared `include/nNetMsg.hexpat` (the export script passes `include/` with `-I`, done).
- Every pattern exports whether the message ended exactly at `len`, so fits can be counted per
  msg id; trailing bytes after the packet body are block padding (and `OnlineStatus` on S2C).
- The run rewrites the tracked JSON of these four packet types in `packets/decrypted_json`
  (110,065 files; Sam asked to run the patterns over this data).

# 005 tasks

Coordinator: main session. One subagent at a time.

- [x] T001 Survey stubs, export script, packet counts, Arrowgene structures (coordinator).
- [x] T002 IDA access: `research/ida/private-copy.sh` + role `evidence-researcher-ida` (headless
  ida-mcp, the reconstructor's pattern); smoke-tested copy and server start.
- [ ] T003 P1 PS4 02020005 wire format of every `nNetMsgData` decoder, the include table and the
  send/receive framing of 3.3.16 / 3.4.16 / 6.23.16 / 6.25.16 (`evidence-researcher-ida`, brief
  `briefs/P1-ps4-wire-format.md`, report `research/P1-ps4-wire-format.md`).
- [ ] T004 P2 PC 03040008 deltas against P1 (include table, added fields, framing).
- [ ] T005 Patterns: shared `nNetMsg` include + 4 packet patterns.
- [ ] T006 `packets/imhex-export.sh` updates; run over `decrypted_raw`; counts.
- [ ] T007 Review, docs, commit.

## Running agents

(none)

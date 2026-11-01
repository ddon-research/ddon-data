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

### Scope widening (Sam, 2026-11-01): relays, context, binary save, character notices

The raw file names come from an older name table: grouping `decrypted_raw` by the `.<g>_<id>_<sub>`
suffix finds 6.24.16 / 6.26.16 (the S2C party relays) in no capture, and shows character notices
named "Unknown" (2.13/2.15/2.19/2.20, 13.44-13.47). Counts in brief P4.

- [x] T013 P4 wire format of the CONTEXT group 35 (all ids), BINARY_SAVE group 9 (packet + save
  blob) and the character notices (`evidence-researcher-ida`, brief
  `briefs/P4-context-binary-character.md`, report `research/P4-context-binary-character.md`).
- [ ] T014 Patterns for S2C_PARTY_RECV_BINARY_MSG_ALL_NTC (6.24.16) and _NTC (6.26.16) from P1/P2
  (no captures; the live runs will produce them), and for every T013 packet; `imhex-export.sh`
  must select raw files by the id suffix, since their names may be "Unknown" or outdated.
- [ ] T015 P6 re-export `decrypted_raw`/`decrypted_json` (last exported 2024-05-13 by an older CLI)
  with the patched e2411fe8 CLI so files carry the server's current names: 51 ids, 1,958 raw files
  (`research/P6-name-diff.txt`); then re-run the ImHex export for the four nNetMsg patterns
  (`implementer`, brief `briefs/P6-reexport-current-names.md`; Sam, 2026-11-01).

### Phase 2: live Season 3 validation (Sam, 2026-11-01: only after the static path is exhausted)

The 2019 captures cover 30 CtrlAction ids, 4 GameEasy/GameNormal ids and no SetNormal/ToolEasy
message. Fresh traffic from the PC client against the local server tests the patterns on
messages the captures never exercise. Method: ddon-hook's
`docs/development/17-study-network-behaviour.md` (driver `scripts/automation/drive.py`,
`run_cycles.py`, server log as evidence and clock). Lab rules from that guide: server changes only
in `C:\ddon-automation\Arrowgene` (branch `automation`, never push), each change a `LAB-ONLY` patch
file; one client at a time on the fixed dump; restore after every run.

- [ ] T008 Static exhaustion check: list what static work leaves open after T007 (unnamed Season 3
  fields, CtrlAction 0x3D, GameNormal 0x0F-0x12, CREATE_CONTEXT bool polarity (P1 vs P2), the
  75 -> 100 clamp, SetNormal/ToolEasy/ToolNormal never captured, PC send methods not read), and
  close each one IDA can close (a P5 on the PC send side) before any live run. Also name, from
  PC-side evidence only, 35.5.16, 13.44-13.47.16, 35.8.16 and 35.12.16: PS4 02020005 numbers its
  packets differently (flat u16), so P4's numbering offsets are withdrawn as naming evidence
  (Sam, 2026-11-01; correction at the top of the P4 report).
- [ ] T009 Server lab patch, logging: `Arrowgene.Ddon.Cli/Program.cs` `IgnorePacketIds` mutes
  `C2S/S2C_LOBBY_LOBBY_DATA_MSG_*` and `C2S_PARTY_SEND_BINARY_MSG_NTC` at debug level; make that
  opt-in (a setting, default unchanged), and log each nNetMsg payload as one prefixed hex line
  (`NetMsg pkt=<id> len=<n> hex=<...>`) so a converter can rebuild `decrypted_raw`-style files.
- [ ] T010 Server lab patch, parsing: replace the stub `RpcHandler`/`RpcPacketHeader` reading
  (Season 2 widths: u32 RpcId, no u64 ids) with a decoder ported from P1/P2, logging the decoded
  msg id and fields; keep `RpcCtrlPeriodicTop`'s position line working.
- [ ] T011 Scenarios that trigger the uncovered messages (walk, combat, bow, catch/grab, climb,
  custom-skill palette change, stage change, objects), run with the driver; convert the logged
  payloads into raw files (same naming as `decrypted_raw`, a new `lab-<date>` stream folder) and
  run the patterns over them; fits per msg id, fixes back into the patterns.
- [ ] T012 Where it runs: T009-T011 touch ddon-hook (driver, scenarios, patch files) and the lab
  server, so they run in a session started in `C:\Users\morph\CLionProjects\ddon-hook` with its
  roles; this spec keeps the captures, the pattern fixes and the counts.

## Running agents

- P3 `implementer` finished (commit 2a9f798b05); its full export still runs in the background
  (75,725 of 110,065 JSON rewritten at 11:45); landing it is queue item 1.
- P4 done (T013, 15 min of IDA, report 344 lines): every group-35/9/2/13 type located on PC
  and PS4; Season 3 u64 widening and trailing fields in the context structures; 9.1.1 is a fixed
  u8[1024] bit-stream save blob; 20 captured types / 3,654 files end within the cipher padding
  (raws carry no `len`, so this is weaker than P2's walk); 15 server misplacements in report § 7
  (35.8.16 missing, 2.19-2.21 declared `PacketSource.Server` with one alias; rows 1 and 13 rest
  on PS4 numbering and are withdrawn).
  Open items in report § 5.

## Next step (2026-11-01)

Queue, in order (one subagent at a time; every spawn `effort: "medium"` until the edited role
files load in a new session):
1. Land P3 when its full export finishes: check the receipt, commit 2 (JSON), fits per msg id.
   Then commit the uncommitted coordinator edits: `.claude/agents/*.md` (`effort: medium`),
   `AGENTS.md` (effort rule), `specs/briefs/orchestration-port-from-reconstructor.md`, this file.
2. `repository-researcher` with `specs/briefs/orchestration-port-from-reconstructor.md` (Sam's
   request: the reconstructor's recent orchestration and role learnings); commit list for it in
   the scratchpad `recon-orch-commits.txt` (60 lines; regenerate with the brief's paths if gone).
3. T013 (P4) done.
4. The orchestration-port `repository-researcher` (item 2 above): done, filed as
   `specs/002-coordinator-tooling/research/orchestration-port-2026-11.md`, tasks T008-T016 there.
5. T015 (P6: re-export with current names), after P3's JSON is committed.
6. T008 (P5: PC send side and the open static items) via `evidence-researcher-ida`.
7. T014 (implementer: the new patterns and the id-based export selection).
8. A `reviewer` on all patterns (T007).

After P2 lands: brief P3 for an `implementer` (T005 + T006). Decisions taken:
- Patterns are named after the packets (`C2S_LOBBY_LOBBY_DATA_MSG_REQ`, `S2C_LOBBY_LOBBY_DATA_MSG_NTC`,
  `C2S_PARTY_SEND_BINARY_MSG_NTC`, `C2S_PARTY_SEND_BINARY_MSG_ALL_NTC`), so the export filter and
  pattern name are the same; the three stubs are removed (Sam: "feel free to completely revamp").
- One shared `include/nNetMsg.hexpat` (the export script passes `include/` with `-I`, done).
- Every pattern exports whether the message ended exactly at `len`, so fits can be counted per
  msg id; trailing bytes after the packet body are block padding (and `OnlineStatus` on S2C).
- The run rewrites the tracked JSON of these four packet types in `packets/decrypted_json`
  (110,065 files; Sam asked to run the patterns over this data).

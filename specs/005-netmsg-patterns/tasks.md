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
- [x] T005 Patterns: shared `nNetMsg` include + 4 packet patterns (P3, 2a9f798b05).
- [x] T006 `packets/imhex-export.sh` updates; run over `decrypted_raw`; counts (P3, JSON commit
  5ce0ff6988): 110,065 packets exported, 0 `.json.err`, every message `msgFits` true; 3.3.16
  59,881 (23 msg ids), 3.4.16 21,000 (8), 6.25.16 29,176 (25), 6.23.16 8 (1); per-id counts equal
  P2 6.1. The export took about 4 h (per-file imhex.exe), which led to P7/P8.
- [ ] T007 Review, docs, commit.

### Scope widening (Sam, 2026-11-01): relays, context, binary save, character notices

The raw file names come from an older name table: grouping `decrypted_raw` by the `.<g>_<id>_<sub>`
suffix finds 6.24.16 / 6.26.16 (the S2C party relays) in no capture, and shows character notices
named "Unknown" (2.13/2.15/2.19/2.20, 13.44-13.47). Counts in brief P4.

- [x] T013 P4 wire format of the CONTEXT group 35 (all ids), BINARY_SAVE group 9 (packet + save
  blob) and the character notices (`evidence-researcher-ida`, brief
  `briefs/P4-context-binary-character.md`, report `research/P4-context-binary-character.md`).
- [x] T014 (P9) Patterns for S2C_PARTY_RECV_BINARY_MSG_ALL_NTC (6.24.16) and _NTC (6.26.16) from P1/P2
  (no captures; the live runs will produce them), and for every T013 packet; `imhex-export.sh`
  must select raw files by the id suffix, since their names may be "Unknown" or outdated.
- [x] T015 P6 re-export `decrypted_raw`/`decrypted_json` (last exported 2024-05-13 by an older CLI)
  with the patched e2411fe8 CLI so files carry the server's current names: 51 ids, 1,958 raw files
  (`research/P6-name-diff.txt`); then re-run the ImHex export for the four nNetMsg patterns
  (`implementer`, brief `briefs/P6-reexport-current-names.md`; Sam, 2026-11-01). Done:
  171beb5082, 3a155a532f, ca504d234b (258,141 files); 125 streams, 146,891 raw files, bytes
  identical except the 43 `C2S_SERVER_GET_SERVER_LIST_REQ` (1.0.1) files that gained their 9-byte
  header; every name now carries 100 ns timestamps (Sam: "Yes, replace all"); 50/51 renames as
  listed, 63.11.16 = `S2C_63_11_16_NTC` (server Name string, see T008); plbatch re-export of the
  four types: 110,065, 0 failures, all fit. `decrypted_json` holds only ImHex output (83 streams).

- [x] T016 P7 ImHex as a library (Sam, 2026-11-01: P3's per-file `imhex.exe` export of 110,065
  files took over 2 h): clone PatternLanguage, ImHex, ImHex-Patterns, ImHex-Plugin-Template,
  measure, recommend a long-lived batch runner (`repository-researcher`, brief
  `briefs/P7-imhex-as-library.md`, report `research/P7-imhex-as-library.md`); an implementer
  package follows the recommendation, then `imhex-export.sh` uses it. Result: process start
  (150-450 ms) and ~8 Git Bash forks per packet dominate, not the pattern language (~0.3 ms per
  packet in-process); recommended a C++ driver linking libpl at ImHex 1.38.1's pin `fb6ea061`.
- [x] T017 P8 `plbatch` (`implementer`, brief `briefs/P8-plbatch.md`): build the driver, prove
  byte-identical JSON against `imhex --pl format`, switch `imhex-export.sh` to it. Done:
  2dbc15e036, a390e0d6fb; 3,028/3,028 files byte-identical to ImHex, failures match; ~35
  packets/s per process (parse 24-25 ms, evaluate 0.5-0.7 ms per file) vs ~1.9/s for imhex.exe,
  run as `JOBS` shards; build `bash research/imhex/plbatch/build.sh` (MSYS2 mingw64, PL pin
  fb6ea061).
- [ ] T018 Optional: parse each pattern once and evaluate per file in plbatch (~1,000 packets/s per
  process, estimated; uses PatternLanguage internals, `reset()` drops `#pragma` settings). Only if
  sharded plbatch turns out too slow for the full packet and `client/` exports.

### Phase 2: live Season 3 validation (Sam, 2026-11-01: only after the static path is exhausted)

The 2019 captures cover 30 CtrlAction ids, 4 GameEasy/GameNormal ids and no SetNormal/ToolEasy
message. Fresh traffic from the PC client against the local server tests the patterns on
messages the captures never exercise. Method: ddon-hook's
`docs/development/17-study-network-behaviour.md` (driver `scripts/automation/drive.py`,
`run_cycles.py`, server log as evidence and clock). Lab rules from that guide: server changes only
in `C:\ddon-automation\Arrowgene` (branch `automation`, never push), each change a `LAB-ONLY` patch
file; one client at a time on the fixed dump; restore after every run.

- [x] T008 Static exhaustion check (P5 done 2026-11-01, `research/P5-pc-send-side.md`: CREATE_CONTEXT
  reads on non-zero (P1 wrong); 75 -> 100 clamp already in the include; 0x3D is s32; GameNormal
  0x11/0x12 u32 optional; Set/Tool senders write no body; 35.5.16 = C2S_CHARACTER_START_BAD_STATUS_NOTICE
  and 35.8.16 = C2S_SET_CONTEXT_BASE_NOTICE by caller code match; 63.11.16 is C2S; 35.12.16 and
  13.44-13.47.16 unnamed. Small static leftovers in its last section: start/end pairing of 13.44-13.47
  (callers `0x8a2670`, `0x8a1d5a`), the CaughtResult/GameEasy sender comparison.) Original task: list what static work leaves open after T007 (unnamed Season 3
  fields, CtrlAction 0x3D, GameNormal 0x0F-0x12, CREATE_CONTEXT bool polarity (P1 vs P2), the
  75 -> 100 clamp, SetNormal/ToolEasy/ToolNormal never captured, PC send methods not read), and
  close each one IDA can close (a P5 on the PC send side) before any live run. Also name, from
  PC-side evidence only, 35.5.16, 13.44-13.47.16, 35.8.16 and 35.12.16: PS4 02020005 numbers its
  packets differently (flat u16), so P4's numbering offsets are withdrawn as naming evidence
  (Sam, 2026-11-01; correction at the top of the P4 report). Also 63.11.16: `PacketId.cs:2013`
  declares field `C2S_63_11_16_NTC` with Name `S2C_63_11_16_NTC` and `PacketSource.Server`
  (found by P6); settle its direction from the PC client.
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

## Resume point (2026-11-01, session restart)

Landed today: P3 (patterns + 110,065 JSON, all fit), P4 (context/binary/character wire format),
P6 (re-export with current names), P7 (ImHex research), P8 (plbatch), the 002 wave 2 tooling, the
repository tuning. Nothing runs. The index holds three files staged by **other** work
(`binaries/PS4_02020005/elf-dumps/ida/functions.ida-9.5.jsonl`, `research/external/*`): commit
only with `-- <paths>`. `research/external-references.jsonl` has 5 uncommitted lines of this spec
(DDON_RE + 4 WerWolv clones) among other work's lines.

In the new session the edited role files load (`effort: medium`, `repository-researcher` with
Bash/Write, spawn titles `<role> · <spec> <package>: <what>` checked by `agent_cap.py`), so spawn
the roles directly. Next, in order (one subagent at a time):
0. Done after the restart: P5 (T008) and P9 = T014 (04418e2c4b..b9c1cd5f90): every captured type
   of groups 2/13/35/63 and 9.1.1 exports and fits 100% (3,654 + 47 files), the nNetMsg JSON is
   unchanged (110,065), 6.24/6.26, 9.0.2, 35.8, 2.14, 2.21 checked on synthetic files only;
   `imhex-export.sh @` selects by the pattern's `// packet-id:`. Open: the 9.1.1 save blob beyond
   its two version fields (P4 § 3.1 does not line up byte-aligned: needs a bit-level walk); the
   35.12.16 tail; ImHex/plbatch writes NaN as `-nan`, which is not valid JSON (35.9.16).
   Next: the reviewer (T007), then docs.
   R1 review done (`research/R1-pattern-review.md`): no layout contradicts P1/P2/P5; 10 findings
   (stale JSON on failed `--force`, `-nan` counted ok, weak 15-byte fit flags, group-2 PS4 citations
   from withdrawn numbering, ONLINE_STATUS from server C#, script hygiene). Its fit-flag analysis
   replaces the planned adversarial check. Running: P10 fixes (`briefs/P10-review-fixes.md`).
   Then: docs, the save-blob bit walk (optional, IDA), spec closing.
1. (done) P5 (T008) was stopped for the restart before any IDA analysis: `research/P5-pc-send-side.md`
   (`state: cut short`) lists all 8 items as not done, with leads. Spawn a fresh
   `evidence-researcher-ida` with brief `briefs/P5-pc-send-side.md` plus that report; it may reuse
   the private copies `ddon-data-p5/` it made beside the PC and PS4 databases.
2. T014 (implementer): patterns for 6.24.16/6.26.16 and the P4/P5 packets; `imhex-export.sh`
   selects raw files by the `.<g>_<id>_<sub>` suffix.
3. A `reviewer` on all patterns (T007), then docs.
4. Phase 2 (T009-T012) from a ddon-hook session, after the static path is exhausted.

## Earlier queue (history)

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
5. T017 (P8: plbatch) done, before P6, because P6 re-runs the ImHex export of the four types. P3's
   JSON is committed after P8 lands (no coordinator commits in `packets/` while it runs).
6. T015 (P6: re-export with current names), after P3's JSON is committed; its ImHex step uses plbatch.
7. T008 (P5: PC send side and the open static items) via `evidence-researcher-ida`.
8. T014 (implementer: the new patterns and the id-based export selection).
9. A `reviewer` on all patterns (T007).

After P2 lands: brief P3 for an `implementer` (T005 + T006). Decisions taken:
- Patterns are named after the packets (`C2S_LOBBY_LOBBY_DATA_MSG_REQ`, `S2C_LOBBY_LOBBY_DATA_MSG_NTC`,
  `C2S_PARTY_SEND_BINARY_MSG_NTC`, `C2S_PARTY_SEND_BINARY_MSG_ALL_NTC`), so the export filter and
  pattern name are the same; the three stubs are removed (Sam: "feel free to completely revamp").
- One shared `include/nNetMsg.hexpat` (the export script passes `include/` with `-I`, done).
- Every pattern exports whether the message ended exactly at `len`, so fits can be counted per
  msg id; trailing bytes after the packet body are block padding (and `OnlineStatus` on S2C).
- The run rewrites the tracked JSON of these four packet types in `packets/decrypted_json`
  (110,065 files; Sam asked to run the patterns over this data).

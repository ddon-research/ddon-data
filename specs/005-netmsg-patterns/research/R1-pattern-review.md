**R1 review of spec 005 (T007): patterns, export script and plbatch, client 03040008**

I found no field that disagrees with P1, P2 or P5, and no V item that a pattern leaves out. The real problems are in the fit-flag evidence, naming, the export tooling and two stale comments. I read the current files at HEAD c7fb7133db. I had no git receipt and no diffs for the nine listed commits, so this reviews their result, not each change. Nothing was run and no file was touched.

**Findings, most severe first** (V = I read the code, I = inferred)

1. **Medium (V). A failed `--force` re-export leaves the previous JSON in place.** `research/imhex/plbatch/plbatch.cpp:131-137`: on failure, `fail()` writes `.json.err` and removes the temp file but never removes the existing `<rel>.json`. The ImHex path does the same (`packets/imhex-export.sh:189-192`). After a pattern change, a packet that now fails keeps last run's JSON beside the `.err`. Counts taken with `fd … -X jq` (script line 36) then include stale `msgFits`/`fits` values. Fix: on failure in force mode, delete or rename the old JSON, or have the counting step skip any file that has a `.err`.

2. **Medium (V/I). `-nan` makes invalid JSON that still counts as "ok".** plbatch writes whatever `FormatterJson` returns (`plbatch.cpp:184-192`), and the script counts only `ok`/`FAIL` lines (`imhex-export.sh:213-218`). A NaN float (35.9.16 per `tasks.md:115`) gives a JSON file that `jq` rejects, while the run reports success. Fix: add a plbatch option that parses the output (PatternLanguage builds with nlohmann json, I) and either fails or counts these files, or run a `jq empty` pass in the script with its own count. I did not count the affected files (no bounded search was possible).

3. **Medium (V). The 15-byte fit flag passes without the Season 3 trailing u32 of `CDataContextSetBase`.**
   - Rule: `include/Packet.hexpat:8-10`; field: `include/Context.hexpat:36`.
   - The 35.7.1 and 35.11.16 bodies end at 37 in 48-byte files (P4 § 2.4 lines 188, 191). Without `unk_u32` they end at 33, padding 15, and still fit.
   - In 35.14.16 a u32 `UniqueId` also fits (P4 says so itself). Extra fields of up to 3 bytes (35.7.1, 35.11.16) or 11 bytes (35.9.16, padding 12) would pass too.
   - Every 16-byte file (2.13, 2.15, 2.19, 2.20, 13.44, 13.45, 35.5, 35.15 with count 0, 63.11) "fits" any body of 0-7 bytes.

   Consequence: the "100% fit" for these types (`tasks.md:111`) is no evidence for those widths; they rest on the PC writers alone. Fix: say this in the docs and the counts. Where possible check a second constraint, as P4 did by matching the 35.14.16 UID to 35.11.16.

4. **Medium (V). Group-2 patterns cite PS4 `Send_` names that were linked by number or by server name.**
   - Files: `C2S_CHARACTER_CHARACTER_DOWN_NTC-pattern.cpp:2`, `…DOWN_CANCEL_NTC…:2`, `…PAWN_DOWN_NTC…:2`, `…PAWN_DOWN_CANCEL_NTC…:2`, `…PAWN_DEAD_NTC…:2`.
   - Example text: "PS4 m_unPawnId by the PS4 Send_ of the same name, I".
   - The PS4 links come from P4's numbering anchors (`P4:42-47`, PC id = PS4 no. − 0x1C3), which the coordinator correction withdraws (`P4:23-30`). "Same name" means the server name matched to the PS4 symbol, so the server is being used as evidence.
   - This breaks both of Sam's rules. Fix: drop the PS4 citations, or add a PC caller-code match as P5 did for 35.5.16 and 35.8.16.

5. **Medium (V). The `ONLINE_STATUS` enum comes from server C#.** `include/nNetMsg.hexpat:205-222` cites `Arrowgene…/OnlineStatus.cs`. PS4 DWARF has `nCharacter::E_ONLINE_STATUS` (`binaries/PS4_02020005/DDOORBIS.elf.h:97775-97788`): 0-0xC, with NUM = 0xD. The server's `PtPawn = 0xD` and `Num = 0xE` are a lead only, and 0xD contradicts the PS4 NUM. AGENTS.md says enums come from debug symbols. Fix: use the DWARF names and mark 0xD as "Season 3?, server lead".

6. **Low (V). The bin-save comments make an observation no report records.** `C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ-pattern.cpp:15-17` and `S2C_…_RES-pattern.cpp:15-17` say the 9.1.1 captures do not show the P4 § 3.1 layout. P4 3.1 (lines 244-265) predicts byte-aligned rows 1-6, and its bit-level walk was "not run". The comment names no file, hash or offset. Fix: record the walk (file, SHA-256, offsets) in P4 or `tasks.md`, or call it "not run".

7. **Low (V). P4 states the wrong size; the pattern is right.** P4 § 2.2 line 125 says "575 B + 2 x (4+2n)" for SetAdditional, which counts the two list counts twice. Fixed fields sum to 567 (the `Context.hexpat:61-62` comment is right), and 567 + 8 = 575 matches the walk (612 − 37). Fix the report.

8. **Low (V). A negative `len` silently moves the cursor backwards.** `nNetMsg.hexpat:906-951`: `msgEnd = msgStart + Len` with an s32 `len` below 0 rewinds `$` with no error. The result is only "SHORT" with fits false. Fix: `std::assert(Len >= 0, …)` or clamp it.

9. **Low (V). Script hygiene in `packets/imhex-export.sh`.**
   - `sed`, `cat`, `dirname` and `nproc` are used but not in `require` (line 68). `sed` also violates the rg/sd preference.
   - `usage()` prints only lines 2-19, so the environment overrides never appear (line 43).
   - The substring filter `**/*"$FILTER"*` (line 130) also matches directory names. Any match becomes a plbatch "cannot read input" failure.

10. **Low (V). Small pattern and coverage gaps.**
    - Copy-paste comment "LOBBY_DUMMY" in `C2S_PARTY_SEND_BINARY_MSG_NTC-pattern.cpp:24` and `…_ALL_NTC-pattern.cpp:22`; `NetMsg` never sets it.
    - The 3.3, 3.4, 6.23 and 6.25 patterns export no padding check (≤ 15 bytes) after `len`/`OnlineStatus`, unlike 6.24 and 6.26. A trailing field the writer adds would go unnoticed.
    - No pattern checks the header `source` byte (0x00 client / 0x34 server). Id-based selection would decode a wrong-direction file without complaint (I).

**Checked and found correct (V)**
- Head is 20 bytes. These match P1 2.x, P2 2.0-2.27, P5 items 1-5 and P2 § 3: the include-mask switch, `CtrlAction` order (CORE_POINT before DAMAGE_ACT), all u64 widenings and the three u32 exceptions, `mActFreeWork` u64, `mBowNetBit` u16, both catch triples, the shell-owner test `& 0xF`, region-rate widths, the 100 clamps, SET_EM_DIE rejection, GameEasy +4 ids marked I, CREATE_CONTEXT read only when the bool is non-zero, `0x3D` as s32, `0x11`/`0x12` u32 optional, the ToolEasy/SetNormal tables and the `0x3C`/`0x3D` comments.
- `LOBBY_PACKET_TYPE` matches DWARF `nNetSv::LOBBY_MSG_TYPE` (`DDOORBIS.elf.h:219368-219372`).
- `CDataContextSetAdditional` and `CDataContextPlayerInfo` follow the DWARF order (`DDOORBIS.elf.h:70347-70401`, `114586-114628`) with exactly P4's widenings and new fields.
- 35.5.16, 35.8.16 and 35.9.16 are named by P5's caller-code match, not by PS4 number. 13.44-13.47, 35.12.16 and 63.11.16 stay unresolved, and server names appear only as leads.
- Export script:
  - selection by id: the `@` regex and the `*.g_i_s` glob are anchored, so `.13_3_16` cannot match `3.3.16`;
  - shards are dealt round-robin;
  - lost results are caught by the `ok+skip+fail == inputs` check (line 217);
  - `trap rm -rf` runs only on the `mktemp -d` directory;
  - header has `set -o errexit/nounset/pipefail` and `command -v` checks.
- plbatch:
  - temp file plus rename, and a 260-character guard on the absolute temp path;
  - `build.sh` pins `fb6ea061`, never builds in the reference clone, and checks its tools.

**Could not check**
- The commit diffs: no git receipt was available.
- Any pattern or plbatch run, or the JSON outputs. The T006/T015 fit counts and the 3,028 byte-identical comparison are historical.
- The NaN file count.
- Whether libstdc++ `fs::rename` replaces an existing file on Windows (I: the T015 `--force` run reported 0 failures).
- `#pragma pattern_limit` needs on large GameNormal counts.
- The PC binary itself (no IDA).

**Paths**
- `D:/ddon-data/research/03040008/packets/include/nNetMsg.hexpat`
- `D:/ddon-data/research/03040008/packets/include/Context.hexpat`
- `D:/ddon-data/research/03040008/packets/include/Packet.hexpat`
- `D:/ddon-data/packets/imhex-export.sh`
- `D:/ddon-data/research/imhex/plbatch/plbatch.cpp`
- `D:/ddon-data/specs/005-netmsg-patterns/research/P4-context-binary-character.md`

005 P9 (T014): patterns for the relays, context, binary-save and character packets

Objective (build 03040008): turn the P1/P2/P4/P5 reports into ImHex patterns, run them over
`packets/decrypted_raw` with plbatch, and commit the JSON. Read first: `research/P5-pc-send-side.md`
("Pattern changes"), `research/P4-context-binary-character.md` (§ 2.2-2.4, 3, 4; the coordinator
correction at its top), P2 § on 6.24/6.26, and the existing `research/03040008/packets/include/nNetMsg.hexpat`
and the four nNetMsg patterns (P3) for style: one shared include per family, every pattern exports a
fit flag so fits can be counted per type.

Do, in priority order (commit after each group):
1. `include/nNetMsg.hexpat`: P5's changes 1-4 (0x3D s32; GameNormal 0x11/0x12 optional u32; comments).
   Re-run the four nNetMsg types; fits must stay 110,065/110,065.
2. Patterns for S2C_PARTY_RECV_BINARY_MSG_ALL_NTC (6.24.16) and _NTC (6.26.16) from P1/P2 (no
   captures: validate on a synthetic file built from a 6.25.16 capture's payload, kept in scratch).
3. Character notices: 2.13-2.15 (empty), 2.19-2.21 (u32 pawn id), 13.44-13.47, 63.11.16 (empty),
   35.5.16 (u32), from P4 § 4 and P5 item 7.
4. Group 35 context packets with a shared `include/Context.hexpat` (CDataContextSetBase,
   SetAdditional, MasterInfo, PlayerInfo, EquipData, PawnInfo with the Season 3 u64 widening and
   trailing fields), captured types first (35.0.16, 35.3.16, 35.7.1/.2, 35.9.16, 35.11.16, 35.13.16,
   35.14.16, 35.15.16, 35.5.16), then 35.8.16 and 35.12.16.
5. Binary save 9.1.1 / 9.0.2: the packet body; the u8[1024] blob as P4 § 3.1's bit-stream fields if
   it fits in the budget, else as bytes with a TODO.
6. `packets/imhex-export.sh`: select raw files by the `.<g>_<id>_<sub>` suffix (a pattern declares
   its id), so outdated or "Unknown" names cannot hide packets; keep name selection working.

Fit flag for non-nNetMsg packets: the raws store no body length, so a decode "fits" when it ends
within the last 15 bytes (cipher block padding); say so in each pattern's header comment.
Pattern file names: the packet's current name as the raw files carry it (server `PacketId.Name`);
where P5 names a packet differently (35.5.16, 35.8.16, 63.11.16 direction), note the client name in
the header comment. Server C# structures are community leads, never evidence; layouts come from the
reports.

Owns: `research/03040008/packets/**` (new patterns and includes, the include edits),
`packets/imhex-export.sh`, the matching README section, `packets/decrypted_json/**` for the types
you export. Never touch: `packets/decrypted_raw/`, client/, other research, the three files staged by
other work (commit only with `-- <paths>`; stage large path lists with
`git update-index --add --remove -z --stdin`, never `git add --pathspec-from-file`).
Libraries: ImHex std includes, plbatch (`research/imhex/plbatch/`); no new tooling.
Done: signed commits; per type exported/failed/fit counts; the nNetMsg re-run unchanged; check.sh;
receipt (write it from git if `receipt.py --print` fails with WinError 206).
Stop: budget 120 min of work time; stop and report if a captured type fits under 95%.
Base: 7062b530f2.

006 R1b: fix the R1 review findings (T002-T004 patterns, README, report errata)

Objective: fix the eight findings of the R1 review (verified by the coordinator against its reading;
quoted here, the reviewer's message is not in the repository):

1. `include/Server.hexpat:52-55, 66-68`: `CDataWalletLimit {WalletType, MaxValue}` and
   `CDataExpSetting.Type` carry Arrowgene names as field names with only "I (server lead)". No PS4
   or PC name exists (T003 § 11, § 20). Rename to `unk_*` with `// server: <name> (lead)` as
   `include/Instance.hexpat:118-119` does; re-export 1.1.2 (and any other pattern using these
   structs) and show the only JSON change is those keys (sample 2 files).
2. `C2L_DECIDE_CHARACTER_ID_REQ-pattern.cpp:9-10` says 14 B; the fields are 15 B (JSON paddingSize 8
   in the 32-byte file agrees). Fix the comment.
6. `README.md:15`: `Packet.hexpat` is not used by the four header-less patterns (1.0.1, 1.1.16,
   44.0.1, 44.1.16); say so.
7. `README.md:162`: 0.10.16 "V" → "V by behaviour" (T003 § 9; README open item 289-291).
8. `README.md:29` ("not proven stays `unk_*`") contradicts `README.md:120` ("marked (I) or stays
   `unk_*`"); the patterns follow line 120 (I by position names in `Login.hexpat:94-99`, …). Make
   line 29 state the rule line 120 states: a name is code-backed (V), inferred and marked (I) with
   its basis, or `unk_*`; a server name alone never becomes a field name.
3-5. Report errata (the reports are evidence records: do not rewrite their sections; append a dated
   "## Errata (R1, 2026-11-02)" section to each report naming the section, the wrong statement and
   the correction with its source):
   - T002-login.md § 12: the sample byte grouping is wrong; ClientVersion 0x3040001b, Type 1,
     RotationServerID 2 (export of `11853_…5_1_1.json`; T003 § 3).
   - T002-login.md § 5: session-key length is 0x1f (31), not 0x20 (export `11860_…2_1_2.json`; the
     report's own end 0x34).
   - T002-login.md § 3, § 14, § 17: superseded by T002c/T002d (walk now run, 336 = 324 + 12 padding,
     no header).
   - T002c § 3: the 304-byte packet's last 12 bytes are cipher padding (T003 § 1(b), § 15).
   - T003 § 10, § 15: `packet-size` recommendation superseded by T002e (files renamed); § 1(b)
     cites a nonexistent "§ 27".
   Then check that pattern headers citing those sections (`L2C_LOGIN_SERVER_CERT_NTC-pattern.cpp:2-3`,
   `C2L_CLIENT_CHALLENGE_REQ-pattern.cpp:2`) also cite the errata or the superseding report.

Owns: the named patterns/includes, the packets README, the JSON the renames change, the errata
sections of the three reports. Never touch raws, client/, other specs; `tasks.md` is the
coordinator's. Commit with `git commit -m <msg> -- <paths>`.
Libraries: plbatch via `packets/imhex-export.sh`; jq for the JSON sample.
Done: signed commits; re-export counts and fit; sample diff (keys only); `bash tools/check.sh --since
<base>`; receipt from `receipt.py --print` with "For Sam's inspection" (the renamed 1.1.2 keys).
Stop: budget 45 min of work time; finish the scope.
Base: the head when you start.

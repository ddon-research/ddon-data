005 P13: R2 fixes and the spec 005 documentation

Objective (build 03040008): apply `research/R2-old-patterns-review.md` findings 1-6 and 8, then write
the documentation spec 005 closes with.

Fixes (commit per group):
1. F1 `include/Quest.hexpat:285-291` QuestEnemyInfo: the position of the Season 3 u32 is unresolved
   (P11a says it leads; the include puts it after GroupId). Name both `unk_u32_0`/`unk_u32_1`, keep
   `GroupId` only in the comment as "one of these, position unresolved (P11a §1.3 vs include)".
2. F2 `packets/imhex-export.sh`: a pattern header `// packet-select: <name>` overrides `@` id
   selection (the 0.1.1/0.1.2 login patterns share their id with game-server CONNECTION_LOGIN); add
   it to `C2L_LOGIN_REQ`/`L2C_LOGIN_RES`; `@` without it on a shared id refuses with a message; README
   line. A synthetic test like P10's.
3. F3 one RES convention: the inline `s32 Error; if (Error == 0) {...}` form of the 30 old RES
   patterns; convert the one `ResHeader res;` user (`S2C_CONTEXT_GET_SET_CONTEXT_RES`) and drop or
   document `ResHeader` in `Packet.hexpat`. Re-export 35.7.2 (608 files); inspection line for Sam.
4. F4 the dangling "Recompilation disagreements" reference: inline the one-line reason.
5. F5 mark inferred positions/names (I) or rename to `unk_*` (BoxGacha u32, AreaBonus u16,
   MyRoomFurniture u32, Quest.hexpat:418-420 PS4 names).
6. F6 one comment line in 18.0.2 on the PS4 framing (recompiled `ACTIVATE_JOB_ORDER_RES::ReadPacket`
   reads Result after any Error); F8 `WALLET_POINT_TYPE_MAX` = 9 is a sentinel in the comment.

Documentation (one commit): `research/03040008/packets/README.md` (new): how the patterns are built
(includes and what each holds, JSON conventions, the RES error guard, `sourceOk`/`paddingSize`/`fits`
and what a fit does and does not prove, `// packet-id:`/`// packet-select:`), how to export
(`imhex-export.sh`, plbatch build, nonfinite/badjson counts), the evidence rules (PC code first, PS4
match by code, recompilation baseline, server C# as lead, enums from DWARF), a table of every
pattern (packet id, name, report section, status) and the open items (save blob bit walk, 35.12.16
tail, unnamed 13.44-13.47, QuestEnemyInfo u32 position, Season 3 field names). Link it from
`packets/README-decrypt-annotate-streams.adoc`. Keep it factual; cite the reports.

Owns: `research/03040008/packets/**`, `packets/imhex-export.sh`, `packets/README-decrypt-annotate-streams.adoc`,
`packets/decrypted_json/**` for 35.7.2 only. Never touch: other JSON, raws, client/, other research.
Commit with `git commit -m <msg> -- <paths or owned folders>`.
Done: signed commits; plbatch re-export of the changed types with counts (only predicted JSON changes,
checked on a sample); `bash tools/check.sh --since <base>`; receipt via `receipt.py --print`, with a
"For Sam's inspection" section. Stop: budget 75 min of work time.
Base: 13e3d4c12f.

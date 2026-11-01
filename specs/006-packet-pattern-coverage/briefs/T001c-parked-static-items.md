006 T001c: finish spec 005's parked static items (evidence)

Objective (build 03040008, seed PS4 02020005): spec 005 left these in-scope static items open.
Finish every one (Sam's rule: no "if time allows"); each ends as V (read in IDA), or with the
concrete reason it cannot be settled statically.

1. 35.12.16: the second structure read via `0x760480` (ctor `0x783270`, 200 bytes) and the list(s)
   P4 left undecompiled: full field table in wire order (spec 005 `research/P4-context-binary-character.md`
   § 2.3, § 5; `include/Context.hexpat` and the 35.12.16 pattern show what is decoded today).
2. Readers never decompiled: 35.0.2, 35.1.x, 35.2.x, 35.4.x (P4 § 5): field tables vs the existing
   Context include.
3. Start/end pairing of 13.44/13.45 and 13.46/13.47 (spec 005 `research/P5-pc-send-side.md` item 7:
   callers `0x8a2670`, `0x8a1d5a` not read): which writer fires on status start and which on end;
   names only if PC strings or a PS4 function matched by code give them.
4. The CaughtResult and GameEasy sender-vs-decoder comparison P5 did not run (P5 item 6).
5. QuestEnemyInfo: the position of the Season 3 u32 (P11a § 1.3 vs `include/Quest.hexpat`; today
   both are `unk_u32_0/1`): read the PC reader and the PS4 reader/recompilation member order.
6. Season 3 nNetMsg field names left `unk_*` in `include/nNetMsg.hexpat` (P5 item 1): name any the PC
   code (strings, consumers) or PS4 DWARF settles; list the rest with what they feed.

Cross-check every layout against the PS4 recompilation C++
(`D:/ddon-data-s2/recompilation/src/DD_ONLINE/prog/Protocol/`, believed accurate where it has a body;
IDA can misread stack arguments: read widths from the disassembly pushes). Server C# is a lead only.
Owns: only `specs/006-packet-pattern-coverage/research/T001c-parked-static-items.md`.
Never touch: patterns, packets/, client/. Private copies: `bash research/ida/private-copy.sh
<pc|ps4> t001c`. Walk one capture per changed layout with `xxd` (select by the id suffix).
Done: per item the answer, VAs, V/I, the exact pattern change needed; final message: report path +
at most 15 lines. Stop: budget 120 min of work time; finish the scope.
Base: 0e06e13453.

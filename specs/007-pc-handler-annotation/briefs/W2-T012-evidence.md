007 W2 T012: evidence for wave 2: codec destinations (packet member mapping) and anchored gap pairs

Questions (PC 03040008, PS4 02020005). Wave 1 (`tasks.md` § Close) wrote 972 pairs, but packet classes got no
layouts (PS4 layouts contradicted by Season 3 changes, e.g. `CHANGE_JOB_RES` shifted 0xc) and locals stayed at
0-3 (T010: callees unpaired). Wave 2 maps packet members **by operation**, not by PS4 offsets, and widens the
pair set with the anchors wave 1 now has. Read `spec.md`, `tasks.md` § Close, `research/T005b-role-anchors.md`
§ 2-3, `research/T010-locals.md` § 3-5.

1. **Codec destinations.** In a paired reader (rule 1/2 pairs; codec call sites aligned in
   `research/03040008/ida-transfer/manifest/callsites.tsv`), each codec call reads one value into a
   destination: how does the destination appear at the call site on each side (a pointer argument
   `lea reg,[obj+X]` / `obj+X` passed, or the return value stored to `[obj+X]` after the call), and is `obj` the
   reader's object argument (or a member pointer of it)? On PS4, map the destination offset to the DWARF member
   (`dumps/ps4-dwarf.jsonl` types). Over all aligned codec call sites: how many give a PC offset X and a PS4
   member M with the same width (a "member link"), how many conflict (the same PC offset linked to two
   members, or one member to two offsets, within one class), per class. Sample 3 classes incl.
   `nUserSession::CPacket_S2C_CHANGE_JOB_RES` (`0x80cf80`), checked by hand against the listing: PC offset,
   width and PS4 member agree.
2. **What the extractor lacks** for 1 (e.g. the register value of a pushed pointer argument: `lea`+`push`),
   stated precisely for an implementer.
3. **Anchored gap pairs (offline over the dumps, no IDA needed).** Rerun the gap rule of T005 propagation
   (`matcher/propagate.py`) with all anchors wave 1 has: accepted pairs, aligned codec call sites (as an
   equivalence class: a PC codec call aligned to a PS4 overload call is an anchor) and identical externs.
   Count 1:1 gaps that propose a callee pair in handler, reader and requester pairs, and list the 20 most
   frequent proposed PC callees with their PS4 partner (e.g. `sContextManager::getContextMyPlayer`). Do not
   accept anything: this measures what the gates would see. Use a throwaway script in your scratchpad.

Databases (only if 1 needs the listing): private copies `bash research/ida/private-copy.sh pc-accepted w2e` and
`... ps4 w2e` (batch or ida-mcp, read-only; delete them at the end; if ida-mcp workers hold files, say so);
never open `ddon-data-007work` in ida-mcp. Output: `specs/007-pc-handler-annotation/research/W2-T012-evidence.md`
(+ TSVs beside it). Owns only those. Never touch scripts, manifest, dumps, ddon-hook, client/, packets/.
Done: the report with counts, the hand checks and the extractor gap; final message with the path and at most
15 lines. Stop: budget 120 min of work time. Base: the head when you start.

006 T008 (patterns): groups 14 WARP, 10 ITEM, 50 ITEM

Objective (build 03040008): implement `specs/006-packet-pattern-coverage/research/T008-warp-item.md`
(read it whole: § 0 method, the per-id sections, § 5 summary, § 6 shared types, § 8 open items; `T008-walk.py` re-runs the walk) as one
`research/03040008/packets/<RAW_NAME>-pattern.cpp` per id with `// packet-id:` lines, following
`research/03040008/packets/README.md` (naming rule after R1b: V, I with its basis, or `unk_*`; a server
name alone never becomes a field name) and the T007b patterns (RES header `s32 Error` then `s32 Result`
+ body only when Error == 0; NTCs per the report).

Scope: the PS4-matched ids, incl. 10.0.16 = USE_BAG_ITEM_NOTICE, 10.10.16 = EXTEND_ITEM_SLOT_NTC and
14.10.16 = C2S_WARP_END_NTC (settled; the raw name `…WARP_START_NTC` stays: name the pattern after the
raw name and put the code-backed name in its header comment and the README). Out of scope (Season 3
additions): 14.14.1/2, 14.11.16, 10.14.16, 50.0.16; list them in the README notes with their report
sections. Shared types per the report: Season 3 `CDataItemList` and the other new item types in
`include/Item.hexpat`, a new `include/Warp.hexpat`; reuse Packet/Item/Context types; no include
cycles, no duplicate type names (move a type an older pattern defines locally into the include only
if both uses match, and show that pattern's re-exported JSON is byte-identical). Existing patterns
that use the PS4 `CDataItemList` or `CDataSwitchStorage` layout (search the patterns) are wrong for
Season 3: fix them, re-export, and list each before/after with fit counts.

Export each new pattern with plbatch (`packets/imhex-export.sh @ <name>`): per-id fit counts (the
report: 2,038/2,038 fit across the three groups), no `.json.err`; spot-check 2 files per id against the
report's samples (end offset, a few values). README table, notes, open items (§ 8).
Owns: the new patterns, the include additions and new includes, changed patterns as above, the
packets README, the JSON of these ids. Never touch raws, client/, other specs,
`packets/imhex-export.sh`; `tasks.md` is the coordinator's. Commit with `git commit -m <msg> -- <paths>`;
long lists via `git update-index --add --remove -z --stdin`.
Libraries: ImHex std, plbatch, stdlib Python/jq.
Done: signed commits; per-id fit counts; `bash tools/check.sh --since <base>`; receipt from
`receipt.py --print` with "For Sam's inspection" (per id: file count, one example with decoded
values, e.g. an item list entry, a warp point list). Stop: budget 120 min of work time;
finish the scope. If your context passes 300k tokens, commit what is done and end `cut short:` with
the next id.
Base: the head when you start.

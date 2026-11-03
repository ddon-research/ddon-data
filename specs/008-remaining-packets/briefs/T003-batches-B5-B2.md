008 T003: patterns, JSON and names for batches B5 and B2 (33 ids, 2,677 files)

Objective (client 03040008): an ImHex pattern for each id of batches B5 and B2 in
`specs/008-remaining-packets/research/T001-triage.tsv` (layouts from the PC readers/writers there, all fitting;
writer-loop corrections in `research/T002-writer-loops.md`), exported to JSON, with the best names the sources
allow. Read `specs/008-remaining-packets/spec.md` (sources, marks V/I/G, naming rule) and
`research/03040008/packets/README.md` (how patterns are built and exported, the mark format, includes).

Per id:
1. Pattern `research/03040008/packets/<RAW_NAME or better name>-pattern.cpp` with `// packet-id:`, following the
   PC width sequence exactly (count fields, lists, element structures, strings in the codec's wire form), shared
   structures in the group's include (`include/<Group>.hexpat`, existing ones reused: a structure already defined
   for a 006 pattern is reused, not redefined). Packet name: the PC `OnPacket_` string where the handler has one
   (V); else the Arrowgene name `G (lead)`, or a better name from context with its basis.
2. Field names and marks, strongest first: PC consumer/property names (006 T014b method; `research/pc-property-names.tsv`)
   -> `V`/`I (consumer)`; the same structure decoded elsewhere (006/007 patterns, PS4 DWARF of a structure the PC
   reader shares) -> `I (same structure)`; value correlation in the captures with known fields and with
   `client/03040008/` extractor data (item ids, quest ids, stage numbers, NPC ids, enums; say which file and how
   many values match) -> `I (value: n/m ...)`; Arrowgene field names (`Entity/PacketStructure/*.cs`) -> `G (lead)`
   or `I (<basis>; lead agrees)`; context (the packet's purpose, neighbouring fields) -> `G (context)`. Keep
   `unk_*` only where nothing gives a name, with the leads in a comment.
3. Export: `packets/imhex-export.sh --force @ <name>` (stdin `</dev/null` in loops); every capture fits (count per id);
   README table rows with fit counts and the mark summary.
4. 29.23.16 and other no-reader ids (if in these batches): captures only, marks G.
Verification: per id all files exported and fit; a stratified sample of 2 JSON per id read back against the raw
bytes by an independent walk (stdlib); "For Sam's inspection": new JSON files per id, renamed packets, any field
whose server name you replaced and why.

Owns: the new patterns, the includes you extend (additions only; never change existing fields), the README table,
the new JSON under `packets/decrypted_json/` for these ids, `specs/008-remaining-packets/research/T003-*`. Never touch
raws, client/, other ids' patterns or JSON, ddon-hook.
Libraries: plbatch via `imhex-export.sh`, stdlib Python, jq.
Done: per-id fit table; `bash tools/check.sh --since <base>`; signed commits with `git commit -m <msg> -- <paths>`
(stage directories explicitly, `git add -- <dir> <dir>`); receipt with "For Sam's inspection". Stop: budget 240 min
of work time; if the scope does not fit, commit what fits and end `cut short:` with the next id.
Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

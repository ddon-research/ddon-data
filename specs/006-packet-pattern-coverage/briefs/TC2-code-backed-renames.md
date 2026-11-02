006 TC2 (closing): rename raws whose file names are placeholders or wrong, where code names them

Objective (Sam, 2026-11-01: rename to code-backed names): the CLI names raw files from Arrowgene's
`PacketId.cs`. Where that name is a placeholder (`*_<g>_<id>_<sub>_NTC`-style) or contradicted by code,
and a spec 006 report names the packet from PC/PS4 code (V), relabel it.

1. Collect the list from the reports (`specs/006-packet-pattern-coverage/research/T002-*.md` …
   `T013-*.md`; known: 0.10.16 = SESSION_STATUS_NTC (T003 § 9, V by behaviour), 14.10.16 =
   C2S_WARP_END_NTC (T008, raw name `…WARP_START_NTC`), 33.20.16 = UPDATE_PLAY_POINT_NOTICE (T006) if
   its raw name is a placeholder, and every "unresolved → settled" id whose raw name is a placeholder).
   Per id: current raw name, new name, the report section, V/I. Only V names are renamed; I names are
   listed, not renamed. New names follow the CLI's naming (direction prefix, group name, PS4 packet name
   with `NOTICE` → `NTC` where the existing names do so): say the rule you used.
2. Patch the CLI's local `PacketId` (the patched-CLI source; `packets/README-decrypt-annotate-streams.adoc`
   § arrowgene-patches; T002e's entry is the model), rebuild, record the DLL SHA-256, add the README entry.
3. Export all streams to a scratch `OUT_DIR`; compare with `packets/decrypted_raw/` by content hash:
   exactly the listed ids' files reappear byte-identical under the new names; nothing else changes.
   Replace them (`git mv`), re-annotate the affected streams as T002e did.
4. Rename the patterns (`<RAW_NAME>-pattern.cpp`, their `// packet-select:` lines if any), re-export
   their JSON under the new names (old JSON removed), README rows; every file still fits.

Owns: the CLI local patch + README entry, the renamed raws, affected annotated files, the renamed
patterns, the packets README, the JSON of those ids. Never touch other raws, client/, other specs;
`tasks.md` is the coordinator's. Commit with `git commit -m <msg> -- <paths>`; long lists via
`git update-index --add --remove -z --stdin`.
Libraries: the existing CLI, scripts, plbatch; stdlib Python (hashlib) for the comparison.
Done: signed commits; the rename table; comparison counts (identical / renamed / other); fit counts;
`bash tools/check.sh --since <base>`; receipt with "For Sam's inspection" (the rename table).
Stop: budget 90 min of work time; finish the scope.
Base: the head when you start (after TC1).

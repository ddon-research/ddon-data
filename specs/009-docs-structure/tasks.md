# 009 tasks

Coordinator: main session. One subagent at a time. Target structure and rules: `spec.md`.

- [x] T001 Census (`research/T001-census.md`, `T001-sections.tsv`, `T001-files.tsv`): 28 living docs, 6,228 lines, 285
  heading rows; 58 pages proposed; 121 file rows (27 move); tutorial proven on committed input (14.3.2); four more
  outside readers; 31 of the packet table's 587 fit counts stale.
- [x] T002 Skeleton, writing contract, gate, tutorial, safe moves (5d3b3df8cd, de59764b4e, da9815ac68): 7 pages;
  `tools/docs_check.py` + `docs` gate section (links case-sensitive against git, anchors, reachability, code-span paths,
  wording, tutorial pins; 39 tests, 13/13 condition removals caught); `research/scripts/`, `research/prompts/`,
  `research/03040008/notes/`; `research/README.adoc` case fixed; `editor` role installed by the coordinator. Gate
  `check.sh --since 7d50e1feb86`: hooks, shell, mcp, docs passed.
- [x] T003 Move the packet work to `packets/` (5e6d4d220a, 015b1b69d4): patterns to `packets/patterns/03040008/`,
  `tools/`, `tests/`, `plbatch/` (with its build tree), `wireshark/`; guard narrowed to the data trees. 595 = 595
  patterns; 6 ids / 676 JSON re-exported byte-identical; plbatch test passes from its home; `git log --follow` crosses the
  move. Gate `check.sh --since cfa36beb405`: hooks, shell, export, mcp, docs passed.
- [x] T004 Packet docs restructured (4a4a1540f4, f8e757a267, 631a5b18e4): 17 pages, short READMEs, adoc deleted;
  `packet-ids.md` checked against the patterns; `--packet-counts` 595 rows, 0 differences after 31 counts corrected;
  spot-check 728 ids/addresses, 0 misses; `guard_paths` normalizes dot segments. Not run, read against the scripts: the
  decrypt, annotate and export-stream scripts, `dotnet build`, `plbatch/build.sh`. Gate `check.sh --since 715f8f2305d`:
  hooks, shell, export, mcp, docs, packet-counts passed.
- [x] T004b Season 1 and 2 patterns removed here (decision 8), after both pushes confirmed on GitHub: 61 files;
  constitution 1.0.1, `AGENTS.md`, `readme.adoc`, `research/README.adoc` updated.
- [x] T005 New knowledge pages (186d5c6681): wire format, handler tables, decoding method, write-a-pattern,
  verify-a-regeneration, evidence model, `two-packet-decodings` (decision 7; examples 14.3.2, 19.28.2, 14.11.16, 62.26.16
  checked against bytes); `packets/tools/arrowgene-cli.patch` saved, `git apply --check` passes on the clean clone; 170
  JSON byte-identical after the comment edits. Unchecked, stated on the pages: 651 `WritePacket` keys, build from patch,
  counter behaviour (approximate). `ag_vs_pc` recount: 81 same, 3 differ, 31 empty. Gate: hooks, shell, export, mcp, docs.
- [x] T006 IDA and transfer pages (7814428fa9, 198a0a51a8): query and write how-tos, transfer how-to, tools reference,
  method explanation; `ida-transfer/README.md` short; `private-copy.sh pc-handlers`. Matcher and wave-2 transfer re-run into
  scratch: identical to the manifest. Not run: repair, extract, apply. Holdout tests role pairs only (page says so). Gate:
  hooks, shell, idacopy (22), mcp, docs (44 pages, 0 findings); xfer by hand: 473 passed, ruff clean.
- [x] T007 Client pages (d956348da6, cd59ee87b5): 12 pages (patches, protections, ELF dumps, Pharos, textures, rng-race);
  `protections/README.md` keeps sections 1, 5, 6; ELF README keeps § 3, § 7, `--verify` OK. Found: radare2 6.1.0 writes 0 bytes
  from the 10 UTF-16 `.r2` scripts (how-to adds `iconv`); the 23 PEB reads read `PEB.Ldr`, not `BeingDebugged`; the old crash
  ranking superseded by ddon-hook spec 009; rng-race page follows ddon-hook 013. Gate: hooks, shell, export, xfer (473),
  mcp, docs (61 pages, 0 findings).
- [x] T008 Repository pages (f1db706e14): 10 pages (resource how-tos, layout, inputs, tools, conventions, gate and hooks,
  community resources, quest flag sources); `research/README.md`, `tools/README.md`; short root `readme.adoc`; index regrouped;
  `research/README.adoc`, `rLandInfo-example`, `wikis-and-resources` and the quest-flag note deleted after their facts
  landed. Corrected: extractor's third argument, rLandInfo magic `0x49414C`. Gate: hooks, shell, mcp, docs (75 pages, 579
  links, 0 findings); ImHex not run (not on PATH).
- [ ] T009 Review (`adversarial-reviewer`, `briefs/T009-review.md`): accuracy sample, lost facts, live readers, the gate,
  a reader's walk.
- [ ] T010 Editor pass, `AGENTS.md` / `CLAUDE.md` shortened, close: `check.sh --all`, retro, merge and push.

## Decisions (coordinator, 2026-11-04, from T001 § 12)

1. Packet table: one Markdown reference file `docs/reference/packet-ids.md` with a check in the gate, edited by script.
2. `protections/README.md` and `elf-dumps/README.adoc` keep their paths and the sections outside readers cite (§1, §5;
   § 3, § 7): no outside repository needs an edit, so none is made. Also unmoved: `research/rng-race/`, `packets/keys/`,
   `research/claude-vision-tokens.md`, `binaries/PS4_02020005/elf-dumps/`.
3. `research/<build>/r*-pattern.cpp` stay flat; the 5 notes move out.
4. Moves: census § 8 steps 1-7 and 9. No `packets/statistics/`; `research/PS4`, `bbm`, `wireshark` stay.
5. Page count: the census's 58 is the map; thin pages merge (`run-flag-investigation` and `external-references`
   become index links).
6. Sam, 2026-11-04: packet work moves from `research/` to top-level `packets/`, including plbatch and the Wireshark
   dissectors (overrides decision 4 for `research/wireshark`). Checked: 0 dirty files in those trees, no sibling repository
   and no JSON names their paths. The build stays in the pattern path (`packets/patterns/03040008/`). `research/rng-race/`
   stays: ddon-hook's `tools/rng/` reads it by path (Sam confirmed: "Leave it in research").
7. Sam, 2026-11-04, a required page for T004: "annotated packages are based on server CLI/knowledge while JSON is based
   on raw understanding and inference of the binaries. So the annotated stuff will have figured things out during
   runtime more but might also still have some erroneous orders/sizes that need to still be checked." So
   `explanation/` states the two decodings and how to weigh them: `packets/decrypted_annotated/` (Arrowgene CLI and server
   structures: meaning tested against a running client, sizes and order unproven) against `packets/decrypted_json/`
   (patterns from the client binaries: layout from code, meaning often inferred, marks `V`/`I`/`G`). What to do when
   they disagree; linked from the `packets/` README, the repository layout, the glossary and write-a-pattern.
8. Sam, 2026-11-04: "move all resource class related patterns to their respective season 1 / season 2 repositories".
   Overrides the spec's rule keeping `research/02030004/`. Copied by the coordinator (blob hashes identical, 9 and 52
   files) and pushed to each sibling's `main` after Sam chose "Fix guard, then push" (a2dc9a527a: the push guard now
   follows `cd` and Git Bash paths): `ddon-data-s1` 88f5fc8e `research/01020003/`, `ddon-data-s2` 8a0a74c73
   `research/02030004/`.
   Plain copies citing 715f8f2305, as s1's first commit did; the history stays here. Reader check: no live reader;
   DDOn-Tools' two credit URLs already name files absent from that folder (report, not ours). Season 3 patterns stay.
   Removal here is package T004b, after T004 lands (pushes confirmed): `git rm` both folders, constitution line 47, `AGENTS.md` lines 28,
   43, `readme.adoc`, `research/README.adoc`, pages naming the sibling repositories' paths.

## Running

- T009 (adversarial-reviewer, brief `briefs/T009-review.md`), started 2026-11-04. Next: file its report, fixes, editor,
  `AGENTS.md` shortened, close. Then spec 010.

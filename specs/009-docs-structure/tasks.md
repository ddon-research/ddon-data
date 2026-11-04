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
- [ ] T005 New knowledge pages (`implementer`, `briefs/T005-packet-knowledge.md`): wire format, handler tables, decoding
  method, write-a-pattern, verify-a-regeneration, evidence model, `two-packet-decodings` (decision 7); CLI patches saved.
- [ ] T006 IDA and transfer pages: `ida-transfer/README.md` split, query and write how-tos, transfer method.
- [ ] T007 The rest: protections, patches, ELF dumps, Pharos, textures, rng-race, `research/README.adoc`,
  `rLandInfo-example`, wikis; repository layout, inputs, tools, conventions, gate and hooks; root `readme.adoc`.
- [ ] T008 Review: accuracy sample, a reader's walk, adversarial check of the new gate.
- [ ] T009 Editor pass, `AGENTS.md` / `CLAUDE.md` shortened, close: `check.sh --all`, retro, merge and push.

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

- T005 (implementer, brief `briefs/T005-packet-knowledge.md`), started 2026-11-04. Next: land, brief T006. `readme.adoc`
  line 115 still credits DDOn-Tools as a path reader: fix in T007.

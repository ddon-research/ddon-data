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
- [x] T009 Review (`research/T009-adversarial.md`): 19 findings (6 block, 13 route), coordinator reproduced 1, 3, 5, 8, 17.
  Held: packet table (595/595, 564 identical, 31 counts only), 30/30 facts located, no stale live reader, 298/298 and 32/34
  outside references. IDA batch not run (role conflict): addresses in the databases unchecked.
- [x] T009b Review fixes (2177ea81dd, 1a5041ed65, e39c75d468, 5c45e9a149, c892552a7d, 18ecd25f21): 19 of 19 closed; each
  new guard and gate condition removed in turn, 0 survivors. Newly refused: pushes after any non-literal `cd` chain, data
  trees through `cd`, `git -C`, `--search-path`, `git show`, `git grep`; `guard_paths` every spelling. Known gap, stated: a
  fence's later words; `git show <rev>:<path>`, `cat`/`wc` over a data glob stay allowed. Gate: hooks (65 + 14), shell, mcp,
  docs (75 pages, 582 links, 456 spans, 91 tests, 0 findings), packet-counts (595, 0 differences).
- [x] T009c IDA claims (`research/T009c-ida-claims.md`): 42 claims, 40 hold, 1 wrong (login writers' range; fixed by the
  coordinator), 1 not settled (`query-ida-read-only.md:14`: facts in all three PC databases, only `pc-handlers` opened).
  Copies: `.i64` deleted; `.id0`/`.id1` under both `ddon-data-t009c/` are held by this session's IDA workers: delete at the close.
- [x] T010 Editor pass (49e15dd4b9 .. 23168c8a59; `research/reviews/T010-editor.md`): every page group edited, no fact
  changed; 5 doubted facts, 2 facts without a page, 6 contract proposals. Gate: docs (75 pages, 0 findings).
- [x] T010b Editor's doubts settled (a6ff00e507): `0x888000`-`0x88E000` was a guessed code region, dropped; addresses
  checked in `pc-handlers` only, stated (`pc`, `pc-accepted` not run; same input inferred); seeding per ddon-hook 013; FIX_4's
  three runs named; `01020003` link to the PS4 export inferred; T009c's traps on their pages; `ps4-elf-structure.md` split out.
- [x] T011 `AGENTS.md` shortened to rules and hazards (220 -> about 200 lines; layout and steps now on pages), close.

## Close (2026-11-04)

- Result: `docs/` holds 76 pages by Diataxis type, reached from a short `readme.adoc` through `docs/index.md`, under a written
  contract (`docs/reference/documentation-style.md`). Directory READMEs are short. Paths outside readers cite stayed, with their
  section numbers.
- Moves: packet work to `packets/` (`patterns/03040008/`, `tools/`, `tests/`, `plbatch/`, `wireshark/`); Season 1 and 2 patterns to
  their repositories (88f5fc8e, 8a0a74c73; pushed, blob hashes identical); loose files to `research/scripts/`, `research/prompts/`,
  `research/03040008/notes/`. `packets/tools/arrowgene-cli.patch` preserves patches that existed in one clone only.
- Corrections the rewrite found in the old records: radare2 6.1.0 writes nothing from UTF-16 `.r2` scripts; 26 PEB reads, all
  `PEB.Ldr`, not 23 of `BeingDebugged`; 31 packet fit counts too low; old crash ranking superseded; extractor's third argument; rLandInfo magic.
- Review: adversarial sample (40 claims, 30 lost-fact checks, gate and guards): 19 findings, all closed; IDA sample 42 claims, 40 hold, 1
  fixed, 1 stated as not run. Packet table 595/595.
- Guards tightened: `guard_bash` (push follows only literal `cd` chains and `git -C`; data trees resolved through `cd`), `guard_paths` (every path
  spelling). Each new condition proven by removal, 0 survivors. Known gaps stated on `gate-and-hooks.md`.
- Gate: `bash tools/check.sh --all` at a6ff00e507: hooks (65 + 14), shell (23), flags (41), export (9), idacopy (22), xfer (473), mcp, docs (76
  pages, 616 links, 463 spans, 0 findings, 91 tests), packet-counts (595, 0 differences) passed; kg failed (`test_production_size_budgets`: `bundle_io.py`
  853 lines) in the untracked `research/knowledge-graph/` tree of other work, which no 009 commit touches; imhex not run (not on PATH); shellcheck not run (missing).
- Not run: the decrypt, annotate and export-stream scripts, `dotnet build`, `plbatch/build.sh` (its cached CMake path is stale: inferred, README says so), IDA in `pc` and
  `pc-accepted`, external URLs of `community-resources.md`, repair, extract and apply of the transfer.
- Open, not ours: DDOn-Tools' credit URLs name files absent from `research/02030004/`; `flags/TODO.md:10` names the absent `plan/` (other work).
- Retro (`retro.py --since 2026-11-04T06:17 --label 009`): top ten rows $58, 5 h wall. Findings: (1) page packages over about 8 pages reach the 300k limit, as T004, T005,
  T007 did: brief at most 8 written pages or 15 moved; (2) the review role cannot open IDA: brief database claims to `evidence-researcher-ida` from the
  start; (3) `editor`'s guard allows `specs/*/research/reviews/*`: briefs name that path; (4) ida-mcp workers outlive their agent and hold copies: a
  reviewer's brief says the coordinator stops named workers by PID once their database path is confirmed.

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

- (none). Spec closed 2026-11-04. Spec 010 follows.

# 009 T008: where the sections of the repository-level documents went

Base `77f3ad1216c`. `T008-split.py` moved the wikis page by script; the rest was written by hand. Spot check: `python -X utf8 -I specs/009-docs-structure/research/T008-spotcheck.py 77f3ad1216c`.

## `research/README.adoc` (renamed to `research/README.md`, shortened)

No outside reader: `git grep` for `research/README`, `research/readme`, `rLandInfo-example`, `wikis-and-resources`, `quest-flag-data-source` in ddon-explorer-server, DDON-translation, ddon-hook, both reconstructors, ddon-extractor, ddon-ghidra-scripts, ddon-data-s1, ddon-data-s2, DDOn-Tools, outside `specs`, `client`, `packets`, `recompilation`, `testdata`: 0 hits (2026-11-04).

| Old section | Went to |
| --- | --- |
| Prerequisites | `docs/how-to/decode-a-resource-format.md` opening, § The archived alternative |
| Step 1 | `docs/how-to/choose-a-resource-target.md` § 2, § 1 of the decode page |
| Step 2 | decode § 2: IDA first, Ghidra as the alternative |
| Step 3 | decode § 3, the table |
| Step 4 | decode § 4 |
| Step 5 | decode § 5 |
| Common Error Patterns | decode § 4, the table |
| Directory Structure | `docs/reference/repository-layout.md` |
| Reference Files | decode opening and § 2-3 |
| Quick Reference | decode § 2, § 4: duplicates of the steps |
| Identifying Next Potential Targets, Extension Coverage Analysis | choose § 1 |
| Current Coverage Analysis Results | `docs/reference/status.md` § Resource extensions, both builds re-run 2026-11-04: same numbers |
| Target Selection Criteria | choose § 3 |

## `research/rLandInfo-example.adoc` (deleted)

| Old section | Went to |
| --- | --- |
| all | decode § Worked example: rLandInfo; each step checked against the file bytes, `DDOORBIS_2.elf.c`, `DDOORBIS.elf.h`, both patterns, both JSON files |

## `readme.adoc` (shortened)

| Old section | Went to |
| --- | --- |
| About | stays, shorter; the build bullets to the layout page |
| Repository layout | `docs/reference/repository-layout.md`; the root keeps a small table |
| Data flow | layout § Data flow, as Mermaid, `packets/` holding its patterns and engine |
| Downstream tools | layout § What outside tools read; the DDOn-Tools claim corrected |
| Toolchain | `docs/reference/tools-and-shell.md` |
| Client resource extraction | `docs/how-to/extract-client-resources.md` |
| Resource format research | decode page |
| Packet capture to decrypted streams | already `docs/how-to/decrypt-a-capture.md` |
| Working with AI agents | tools-and-shell § Agents and planning; one line stays |
| Credits | stays, verbatim |

## `research/wikis-and-resources.adoc` (deleted)

`docs/reference/community-resources.md`, by script. Every heading and URL moves; the chat log of backups becomes one block per site.

## `research/03040008/notes/quest-flag-data-source-mapping.adoc` (deleted)

`docs/reference/quest-flag-sources.md`. Neither `research/03040008/flags/README.md` nor its `TODO.md` cites the file, so it does not stay in `notes/` too. Windows paths became repository paths, which the gate now checks.

## `research/rng-race/README.md`

§ Video to `docs/reference/inputs-and-builds.md` § Longplay videos. "about 88" became 87 `.mkv`, counted with `fd -e mkv`.

## Disagreements: the page follows the source

| Source said | The code or data says | Page |
| --- | --- | --- |
| `readme.adoc`, `AGENTS.md`: third extractor argument is `<out>` (AGENTS) | `ExtractResourceCommand.java`: index 2 is the input relative to `rom`; output is always `output/` under the working directory | the how-to; `AGENTS.md` line proposed |
| both show only the `-u -x` run as "the" extraction | `-x` only unpacks; ddon-extractor's README has a second run | the how-to has both |
| `readme.adoc`: "regenerate the summary CSV/TXT files" | no script found in this repository or ddon-extractor for most of them | **Status:** open on the how-to |
| rLandInfo: magic `0x49414c00` | `4800844` = `0x49414C`; bytes `4C 41 49 00` | the bytes |
| rLandInfo: Season 3 fields "hypothetical", `exact fields unknown` | `research/03040008/rLandInfo-pattern.cpp` has `mIsDispNews`, `mGameMode`; extractor JSON has `IsDispNews`, `GameMode` | the committed pattern |
| Targets: `.gui` (`ui\05_edit\camera_param.cecp`), `.col` (`collision\hm_common.col`) | script output 2026-11-04: `.gui` `ui\01_hud\action00.gui`, `.cecp` `ui\05_edit\camera_param.cecp`, `.col` `param\game_common.col` | the run's output |
| base struct `char magicString[4]` | 15 of the 60 patterns use `char magicString[]`, 9 use `[4]` | both named |
| Ghidra outputs written into `research/` | those files are absent and untracked | the page keeps them out of the repository |
| Census: DDOn-Tools reads `research/02030004/`; `readme.adoc` "keep those paths stable" | credit URLs only; the path is not here at all | layout page |

## Gate check of season paths (the brief's question)

`tools/docs_check.py` `[path]`: a code span whose first word starts `research/` must exist here, so `research/02030004/x` fails on any page, short README and `readme.adoc`, with no exclusion. A span starting with the repository's name (`ddon-data-s2/research/02030004/`) passes, since its first part is no top directory, and it says which repository it means. Tests: `test_season_pattern_path_as_if_local_fails`, `test_season_pattern_path_naming_its_repository_passes`, `test_readme_adoc_is_checked_by_default`. Not caught: the path in plain prose, in a fence, or as a later word of a span (`imhex --pattern research/02030004/x`).

## Cut

Not moved, and why:

- `research/README.adoc` § LLM Integration Points, the "LLM Automation Prompt" blocks, "~80% automation": selling points and prompts with no fact beyond the steps. In Git.
- `.ext`, `--pl`, `02030004/rResourceName-pattern.cpp`, `season2_file.ext`, `season3_file.ext`, `/path/to/DDON_02030004/.../resource.ext`, `rResourceName.h`, `rResourceName_load.cpp`, `/d/ddon-data/research/rResourceName.h`, `02030004/rLandInfo-pattern.cpp`, `rLandInfo.h`, `rLandInfo_load.cpp`, `research/rLandInfo.h`: placeholder forms and the Ghidra run's untracked output names; relative to a `research/` working directory that holds no such folder. `readme.adoc`, `rLandInfo-example.adoc`, `README.adoc`: the source pages' own names and their links to each other.
- `research/rLandInfo-example.adoc` § Lessons Learned: stated as the steps of decode § 5.
- `wikis-and-resources.adoc`: the second copy of the playlist `jrsd7JbGK6g`; "Currently playing around", "I intend to create backups", "Sam — <date>" chat lines (the crawl dates 2025-01-23 to 2025-01-30 stay in Git).
- `0x49414c00`: a wrong reading of the magic, see Disagreements. `-managed`: a false token, from `uv`-managed.
- `readme.adoc`: `client/` "also holds benchmark-client statistics" reworded; `plan/` absent.

009 T009b: fix the review's findings

Objective: every finding in `specs/009-docs-structure/research/T009-adversarial.md` closed, with its canary from `.agent-ledger/canaries/009-T009/` (`guard_canary.py`, `gate_canary.py`, `packet_ids_canary.py`, `verify_exe2.py`) as the proof. Read that report whole. Client 03040008 (`f1c9` database addresses where a page says so).

**Pages**: findings 1, 2, 3, 4, 17, 18, 19 as the report says. For 3 and 17, verify with the canary first, restate counts per section. `0x237B733`'s `jmp` target: follow it in the raw bytes if cheap, else say "not read". `R1-R3` stay whole: corrections go on the pages. Finding 18: settle the 749 by counting, then state it. Reader's walk: `readme.adoc` links `patches/`'s how-to and names where Season 1 and 2 patterns live (`research/01020003/` in `ddon-data-s1`, `research/02030004/` in `ddon-data-s2`); the index line for Write to an IDA database says "annotate"; `transfer-annotations-ps4-to-pc.md`'s "What was run" moves to `docs/reference/status.md`. `readme.adoc:12` wording.

**`tools/hooks/guard_paths.py`** (5): normalize before matching: strip `\\?\`, join a relative path to `cwd`, map `/d/` and `/mnt/d/` to `D:/`, compare case-insensitively (the filesystem is), keep `..` normalized. Tests per spelling, and `packets/patterns/` stays writable by every spelling. This only tightens.

**`tools/hooks/guard_bash.py`** (7, 8): this only tightens, except where it stops refusing a correct command.
- Push: follow `cd` only as a plain `cd <literal>` in a `&&` chain at the top level. On anything else that changes directory before the push (subshell, pipeline, `;` after a possibly failing `cd`, `pushd`, `cd --`, `cd -P`, `$VAR`, a missing directory), the branch is unknown. With an unknown branch and a refspec naming a branch, refuse with a message saying to run from the repository. A bare `git push` and `git push origin HEAD` stay allowed as they are. `git -C <literal>` stays honoured. Note the standing workflow: `cd /d/ddon-data-s1 && git push origin main` must pass when that repository is on `main`, and separate calls `git checkout main`, `git merge --ff-only ...`, `git push origin main` keep working.
- Data trees: apply `in_large_tree` after resolving each argument against the tracked `cwd` and `git -C`; add `fd --search-path=`, `--base-directory=`, `ls --recursive`, `git log -up` (short flags clustered), `git show <rev> -- <path>`, `git grep`. Keep the bounded forms working (`rg -c`, `-l`, `-m N`, `| wc -l`, `git diff --stat`, `fd -d 2`). Exempt subtrees stay exempt.
Update `tools/hooks/test_guard_bash.py`, both sides. Existing tests pass unchanged, unless one asserts the wrong behaviour: name it.

**`tools/docs_check.py`** (6, 9, 10, 11, 12, 13, 14, 15):
- A missing `readme.adoc` is a finding; `readme.adoc` must link `docs/index.md`.
- External only for `http(s)` and `mailto`; `file:`, `D:/`, `//` are findings; scan `html_*` tokens for `href`/`src`; undefined reference links; adoc `<<...>>`, `image::`, `include::`.
- A link or span target must exist in the index **and** on disk; a tracked file deleted from disk is a finding.
- `docs/**` with any Markdown or adoc extension, in any case, is a finding unless it is `.md`.
- `[path]`: `./`, `../` and every word of a span that begins with a known top directory, case-sensitive, trailing slash means directory; absolute repository spellings refused. Fences: only `[path]` for the first word if that stays free of false findings on the real tree, otherwise leave and say so.
- `[wording]`: across line breaks, lower-case ids where they cannot be a false match, image alt, `readme.adoc`.
- `[packet-ids]`: every mark tag the patterns carry (`T014b`, `T007` and the rest; read the patterns to enumerate), the Report column compared with `// Evidence:` where one exists (`T001-census.md` § 6 says 31 patterns have none), file name must be `-pattern.cpp`, the `marks: none` row correct.
- `--packet-counts --write` returns 1 when a difference was not written.
Fixtures for each, each proven to fail without its condition. Keep the gate fast.

**`tools/check.sh`** (16): `shell` prints `not run (no script changed)` when none changed; `gate-and-hooks.md:12` follows. Check every section for the same pattern.

Update `docs/reference/gate-and-hooks.md` for the guards' and gate's new behaviour.

Owns: `docs/**`, `readme.adoc`, `research/03040008/protections/README.md`, `tools/docs_check.py`, `tools/test_docs_check.py`, `tools/check.sh`, `tools/hooks/guard_paths.py`, `tools/hooks/guard_bash.py`, their tests, `specs/009-docs-structure/research/T009b-*`.
Never touch (other work, dirty): `research/03040008/flags/**`, `research/knowledge-graph/`, `binaries/PS4_02020005/DDOORBIS.elf.h`, `packets/decrypt-annotate-streams.sh`, `research/external-references.jsonl`, `research/external/*`, `patches/2026_10_17_*`, `specs/*-1.md`, `client/`, packet data, `R1-R3`. Canaries are read-only inputs: copy before changing.
Libraries: stdlib; `markdown-it-py` as the gate uses it.
Done: `guard_canary.py` and `gate_canary.py` re-run with each previously allowed spelling's new outcome listed; `bash tools/check.sh --since <base>` with hooks, shell, docs, packet-counts where touched; a table of the 19 findings: fixed by which commit, or why not; signed commits with `git commit -m <msg> -- <paths>`; receipt with "For Sam's inspection" (guard behaviour changes old -> new, every command form newly refused).
Stop: budget 90 min of work time; past 300k context, commit what passes and end `cut short:` with what is left. Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

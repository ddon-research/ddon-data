# 009 T007: where the sections of the client READMEs went

Base `3c6506d0ca5`. Whole text moved by `T007-split.py`; spot check: `python -X utf8 -I specs/009-docs-structure/research/T007-spotcheck.py 3c6506d0ca5`.

## `patches/README.md`

| Old section | Went to | Left out, and why |
| --- | --- | --- |
| Title, intro | the short README | |
| Table of Contents | | manual TOC: cut |
| How to Apply Patches | `docs/how-to/apply-a-client-patch.md`; `radiff2 -r`, `-j` to `docs/how-to/add-a-client-patch-layer.md`; `.json` to `docs/reference/client-patches.md` | |
| Caveats of layered patching | the apply how-to; UTF-16 to the reference | "radare2 reads them": false for radare2 6.1.0, see Disagreements |
| Vanilla, Modded hashes (all tables) | `docs/reference/client-patches.md`, verbatim but for code spans on `.r2` paths | |

## `research/03040008/protections/README.md`

Headings 1-6 stay with a short paragraph; §3's heading is reworded without the task label.

| Old section | Went to | Left out, and why |
| --- | --- | --- |
| Intro, report table | stay | |
| §1 | `docs/explanation/client-lineage-and-protections.md` | |
| §1 Lineage | `docs/reference/client-patches.md` § Lineage, and the explanation | "`patches/README.md` says otherwise": stale, cut |
| §2 table | `docs/reference/protection-inventory.md`, verbatim but the PEB row | |
| §2 Bunie's DLLs | the explanation § What Bunie's DLLs add | ddon-hook task label |
| §3 | the explanation § Why a code patch crashes the client | ranked candidates: see Cut |
| §4 | `docs/how-to/triage-a-client-crash.md` § When a hook writes `.text` | step 3 restated as done |
| §5 | the how-to § The protocol, verbatim, step numbers kept | |
| §6 | stays short, facts on the pages | list kept in `R3-patches.md` §7 |

## `binaries/PS4_02020005/elf-dumps/README.adoc`

§ 1, § 3, § 5 and § 7 stay in place. § 3 only changes its two "below" pointers and one path form.

| Old section | Went to | Left out, and why |
| --- | --- | --- |
| § 2 Tools, Procedure | `docs/how-to/regenerate-elf-dumps.md` | |
| § 2 Provenance, Storage | `docs/reference/elf-dumps.md` | set sizes to `docs/reference/status.md` |
| § 4 Program headers to DWARF, Code | `docs/explanation/ps4-elf.md`, converted by script | |
| § 4 Inline chains | format to the reference, commands to the how-to, why to the explanation | `L-10`, a chat label |
| § 4 IDA's jump tables | the same split | |
| § 6 | the reference § Verification | |

## `research/pharos/README.md`, `research/textures/*`, `research/rng-race/README.md`

| Old section | Went to | Left out, and why |
| --- | --- | --- |
| Pharos, all | `docs/how-to/run-pharos.md` | |
| `how-to-extract-images.adoc` | `docs/how-to/convert-textures.md`; the file is removed | |
| `texture-research.md` | stays as the note file | |
| rng-race Current understanding | `docs/explanation/rng-race.md`, reconciled | |
| rng-race Resume here | cut as stale | see Cut |
| rng-race Video | stays in the README until the inputs page of the next package | |
| rng-race Files, build line | stay | |

## Disagreements between the sources and what the pages say

- **radare2 and UTF-16.** The old README and `R3-patches.md` §7 say radare2 copes with UTF-16 `.r2` files. radare2 6.1.0 does not: `radare2 -qnw -i 2022_01_21_ddo_dump_fix_mutex_e.r2` on a blank 68 MB scratch file prints `Invalid command`, and 0 bytes change; after `iconv` 1 byte changes. R3's replay was in memory ("replayed in memory"), so it never tested radare2. `AGENTS.md` Patches states the command without the conversion.
- **PEB reads.** `R2-static.md` §3, `R3-patches.md` §6 and the old §2 call the 23 `fs:[30h]` sites `BeingDebugged` reads. The bytes of `f1c9` show `mov eax,[eax+0Ch]` after all 23 (20 directly, 3 after one `jmp`, followed): `PEB.Ldr`. ddon-hook 009's P-unprotect says the same. The page follows the bytes. R2 and R3 stay whole.
- **The crash of §3.** The old §3 ranks causes with a delayed integrity reaction first, marked inferred. ddon-hook 009 caught the protector's worker delivering it (tasks, run `20261018T000216`). `SafetyHook`'s VEH and re-encryption are out by that, and by MinHook dying at the same address.
- **§4 step 3.** A layer exists (other work, untracked): `2026_10_17_ddo_dump_fix_4.r2`, with more than the step said: also 4 `IsDebuggerPresent` sites. Its smoke runs crashed.
- **Brief vs ddon-hook.** The brief lists §1 and §5 as cited. ddon-hook `docs/development/09:206-207` cites **§1 and §6** for the lineage of the two executables, so §6 keeps that sentence. `docs/development/14:41` cites §5 "from step 1", so the how-to keeps the step numbers.
- **`run_cycles.py` vs the protocol.** The protocol's command gives an executable and args; `run_cycles.py` attaches by pid and adds `-n 5`. Both are on the page.
- **Call sites of `nrand`.** "About 420" (notes, old §4) is a count over a decompiler export. ddon-hook's count in the database is 345 references to the global, 299 of them to `nrand`; its own abstract still says about 420. The pages say "hundreds" and give both.
- **rng-race vs ddon-hook.** `research/rng-race/IDEAS.md` and `NOTES.md` stay as records at 2026-10-17. Stale there against `ddon-hook/specs/013-prng-state-recovery/`: H2's seed window, M1 and S4 as blocked, the 185 M/s figure, the two-call model as the whole mechanism. ddon-hook has both `reverse-engineering/` and `investigations/` as the home of its pages (the second uncommitted at 2026-11-04), so the pages name it by file name.
- **Pharos.** The old README says a re-run can resume from `.ser` or `-facts.pl`. `scripts/analyze.sh` always runs step 1 and has no resume; the page says to run later tools by hand. `--new-method` has no route through `run.sh`.
- **`.json` encoding.** All 12 tracked `.json` files are UTF-16LE; the old README named only the `.r2` files.

## Cut

Tokens the spot check accepts here are history or stale run details, kept in the sources named.

- `T026`, `E4`, ~50 s on `f2a8`, ~20 s on `f1c9`: the story of the crash in `specs/003-client-protections/` and ddon-hook spec 009. The candidates by rank: `R1-online.md` §7, `R2-static.md` §9.
- Resume here, of 2026-10-17: `rng-monitor`, `specs/010-agentic-practices/tasks.md`, `e71c454c`, `ead89`, `dinput8.dll`, `dinput8.dll.bak-2026-10-17-752695bd`, `ddon_hook.env`, `config/rng-monitor.env`, `ddon_hook_artifacts/evidence/rng_monitor.jsonl`, `scratch-2026-10-17`, `docs/reverse-engineering/17-rng-monitor.md`: stale deployment and resume lines, kept in Git and ddon-hook spec 009.
- `original.exe`, `patched.exe`, `patch.r2`: placeholders of the old commands, written `parent.exe`, `modified.exe`, `<target>.exe`, `<date>_<name>.r2` on the pages. `tools/check.sh` in the rng-race Resume lines is ddon-hook's.
- `c93f7e4d` keeps its place on the explanation page. `-L<log>` and other placeholders of old commands.

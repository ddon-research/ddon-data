# 009 T009: adversarial review of the documentation, its gate and the guards

Reviewer `adversarial-reviewer`, base `2ec944124c6`, seed 20261104 (`sample.py`). Canaries `.agent-ledger/canaries/009-T009/`.
Filed by the coordinator from the reviewer's final message; the coordinator reproduced findings 1, 3, 5, 8, 17 (`radare2`,
`verify_exe2.py`, `guard_canary.py`). Not run: the IDA batch (the role forbids touching databases, against the brief), so raw bytes of
`D:/research/DDON-binaries/PC/2022_01_29_DDO_DUMP_FIX.exe` (`f1c9`) were read instead; "every address holds in each database", the annotated names and
the `0x9d6a20` / `0x9d6d20` send and receive claims are unchecked.

## Verdict

19 findings (6 block, 13 route). The packet table, the moves and the live readers held; the defects are in a few explanation or reference
sentences, overstated marks, and gate and guard spellings.

## Block

1. `docs/explanation/two-packet-decodings.md:71`: PS4 offsets given as PC. PC `0x76f820` holds a `0x14`-byte object: vtable, u8 `+4`, u32s `+8, +0xc, +0x10`; `+0xc, +0x10, +0x14` is PS4 `0x19f1cc0`.
2. `docs/explanation/client-lineage-and-protections.md:9`: `0x200F000` is an RVA. Second `.text` is at VA `0x240F000` (agrees with `client-patches.md:103`).
3. PEB read count, in `protection-inventory.md:16,40-44`, `client-lineage-and-protections.md:39`, `protections/README.md:35`: 26 `64 A1 30 00 00 00`, not 23: a 24th in `.text#2` at `0x25099C0` (`8b 40 0c` follows), two in `.reloc` at `0x23BA639` (direct) and `0x237B733` (`jmp`, target not read).
4. `client-lineage-and-protections.md:35`: "since the jobs run inside the engine" has no `[inference]` mark (`protection-inventory.md:18` marks it); "each of its smoke runs" overstates: the JSON's three runs are compares only, this layer, this layer plus rdtsc.
5. `tools/hooks/guard_paths.py:54-66,76-81`: evidence writable through other spellings under `--deny-owned`: `CLIENT/`, `PACKETS/decrypted_json`, `packets/Decrypted_JSON`, `/d/ddon-data/client/x`, `/mnt/d/...`, relative `client/x`, `\\?\D:\...`, `agents.md`, `.CLAUDE/settings.json`.
6. `tools/docs_check.py:526-528`: a missing `readme.adoc` is skipped, against its docstring; a readme with no link to `docs/index.md` passes.

## Route

7. `guard_bash.py:195-199`: `cd` tracking misjudges pushes: `(cd B); git push origin beta`, `cd B | true; ...`, `cd B/missing; ...` allowed; `(cd B); git push origin alpha` refused; `pushd B`, `cd -- B`, `cd -P B`, `cd $D` push another branch unrefused; `check_push` fails open on an unknown branch (`cd ~/nonesuch && git push origin main`).
8. `guard_bash.py:441-482` ignores `cwd` over data: `cd packets && rg foo decrypted_json`, `cd client && fd .`, `cd packets && git diff -- decrypted_json`, `git -C packets diff -- decrypted_json`, `fd --search-path=packets/decrypted_json`, `fd . --base-directory=client`, `ls --recursive packets/decrypted_json`, `git log -up -- client`, `git show HEAD -- packets/decrypted_json`, `git grep foo packets/decrypted_json`.
9. `docs_check.py:236-238`: `D:/x.md`, `D:\x.md`, `file:///...`, `//x` count as external; `<a>`, `<img>`, HTML blocks, `[x][undefined]`, adoc `<<x#,y>>`, `image::`, `include::` unseen. None in the real tree.
10. The gate reads the index, not the disk: a page or linked file deleted from disk but still in the index passes.
11. `docs/b.MD`, `docs/b.markdown`, `docs/b.adoc` escape every check.
12. `[path]` spans that pass when wrong: `Tools/real.sh`, `./tools/missing.sh`, `../tools/...`, `/d/...`, `D:/...`, `tools/real.sh/`; later words of a span and fences. `sweep_paths.py` finds no wrong path in the real tree for the forms it scans.
13. `[wording]` gaps: `no\nlonger`, `t009`, image alt, HTML, all of `readme.adoc`. Real instance: `readme.adoc:12` "New to the repository?".
14. `[packet-ids]` `docs_check.py:120-122`: counts only `T00[345]` marks; `T014b` (250) and `T007` (2) unchecked; an emptied Report column passes; `*_pattern.cpp` passes; `T003 marks: none; T004 marks: ...` falsely refused.
15. `docs_check.py:477`: `--packet-counts --write` exits 0 with differences left.
16. `tools/check.sh:100` prints `shell passed 0 scripts changed`, against its header's "never reported as passed"; `gate-and-hooks.md:12` documents it.
17. `protection-inventory.md:13`, from `R3-patches.md:321`: FIX_3 has 121 `8b 02` plus one `8b 08` (`mov ecx,[eax]`) at `0x2F500BE`; 121 sites at or above `0x22CE8E9`, not 120.
18. `packet-wire-format.md:154` "all 749 files": the two folders hold 753, all multiples of 16; 749 presumably excludes the four headerless first packets (inferred).
19. `verify-a-regeneration.md:39`: `git diff --stat -- packets/` is allowed; only the form with no summary flag is refused.

## Checked and right

- Accuracy, 40 sampled lines: 29 verified from source (bytes, cipher decrypts, the executable's tables, patch JSON, tool versions, parsers, `plbatch`, `radare2`), including all 74 directory and 20 login rows, the sum 1,041, 675 strings, 658 calls, and the bf51 layer's UTF-16 failure then `bf5107ef` after `iconv`. 4 defective (findings 3, 4, 17). 7 argument with nothing byte-checkable. `ida-transfer-method.md:71` (the shift claim) unconfirmed.
- `two-packet-decodings.md`: every other example holds.
- Lost facts: 30 of 30 on a page, in a kept file or in a cut list with a sound reason.
- `packet-ids.md`: 595 rows against 595, 564 byte-identical, 31 differing only in counts. `--packet-counts`: 0 differences.
- Live readers: of 69 deleted files, 61 byte-identical in s1 and s2, 8 documents with pages. No stale reader outside closed specs here, but `flags/TODO.md:10`'s `plan/` (other work, absent at the base). ddon-hook: 32 of 34 references resolve (`research/wireshark` in its `specs/013-prng-state-recovery/pitch.md:167`, a future `runs/` folder: spec records). Reconstructor: 298 of 298. Protections §1, §5 hold.
- Gate: 52 of 81 fixtures as intended; caught include case, `./`, `..`, URL-encoded, reference-style, table links, directories, anchors, listed twice, reachable only from itself, a dropped or duplicate row, a pattern with no row, a changed mark. `in_large_tree` spellings without `cd` refused.

## Reader's walk from `readme.adoc`

New packet id 2 clicks; `V`/`I`/`G` 2; annotated vs JSON 2; patch a client 2 (3 with the hash row; the readme's `patches/` row has no link); Season 2 `rItemList`: 1 to GitHub then browsing (the readme does not name `research/02030004/`); annotate the PC database 2, but the index line for Write to an IDA database lacks "annotate" (3 through Transfer annotations). Two purposes: `transfer-annotations-ps4-to-pc.md` ("What was run" is status), `packet-ids.md` (report key plus table), `client-patches.md` (lookup plus lineage).

# 009 T001: census of the documentation and of the loose files

Brief: `specs/009-docs-structure/briefs/T001-census.md`. Base: `06457ec5bc1` (the spec-opening commit on `d221d60a166`).
Every fact below is marked **V** (verified: read or run here) or **I** (inferred). Client facts name their build.
Companions: `T001-sections.tsv` (357 rows), `T001-files.tsv` (121 rows), their producers `t001/sections.py`, `t001/files.py`.

## 1. Answer in brief

- 28 living docs, 6,228 lines, 281 headings. 142 of the 285 heading rows go to a page, 140 stay (`keep`: agent files, evidence
  reports, directory READMEs, other work), 3 are `spec-history`. 72 further `[sub]` rows split the packets README.
- Proposed: 1 tutorial, 24 how-tos, 25 reference pages, 8 explanations.
- A tutorial on committed input works with `xxd` and `jq` alone (§4, run).
- The census adds four outside readers the spec does not list: `research/rng-race/`, `packets/keys/`, `research/claude-vision-tokens.md`,
  `binaries/PS4_02020005/elf-dumps/` (§7). ddon-hook also cites protections README **section numbers** (§1, §5).
- The packets table's Id, Pattern, marks and n/m counts can be checked from patterns and JSON in seconds; 31 of its 587 counts are stale,
  and 281 rows carry hand notes, so a check fits better than a generator (§6).
- All 60 `research/03040008/r*-pattern.cpp` should stay: move the notes out instead (§9).

## 2. Proposed pages

Source names are short: `packets` = `research/03040008/packets/README.md`, `adoc` = `packets/README-decrypt-annotate-streams.adoc`, `xfer` =
`research/03040008/ida-transfer/README.md`, `prot` = `research/03040008/protections/README.md`, `elf` = `binaries/PS4_02020005/elf-dumps/README.adoc`,
`rwf` = `research/readme.adoc`. Exact rows: `T001-sections.tsv`. "(gap)" = the page's main content has no doc today (§3).

### Tutorial

| Page | Purpose | Sources |
| --- | --- | --- |
| `tutorials/read-one-packet.md` | Decode one committed 03040008 packet by hand and match the committed JSON | §4; `include/Packet.hexpat` |

### How-to

| Page | Purpose | Sources |
| --- | --- | --- |
| `how-to/extract-client-resources.md` | Re-extract `client/<build>/` and review the diff | `readme.adoc` Typical workflows; `AGENTS.md` Workflows |
| `how-to/decode-a-resource-format.md` | Go from a class to a validated ImHex pattern, IDA first | `rwf` Steps 1-5, errors; `research/rLandInfo-example.adoc`; `readme.adoc` |
| `how-to/choose-a-resource-target.md` | Find unsupported extensions and pick one | `rwf` Step 1, Identifying targets; `research/find-unsupported-extensions.sh` |
| `how-to/decrypt-a-capture.md` | Turn a pcapng into decrypted streams and keys | `readme.adoc` Packet capture; `AGENTS.md` Packets; `packets/keys/*.sh` |
| `how-to/reannotate-streams.md` | Re-run annotate, raw export and split over streams | `adoc` Purpose to Concurrency, Splitting, Exporting raw |
| `how-to/patch-the-arrowgene-cli.md` | Build the patched CLI the exports need | `adoc` Required patches |
| `how-to/export-packets-to-json.md` | Export a pattern to `decrypted_json/`, read the summary | `packets` How to export; `adoc` Exporting with ImHex |
| `how-to/refresh-packet-statistics.md` | Regenerate the count files | `adoc` Packet statistics |
| `how-to/write-a-packet-pattern.md` (gap) | From a packet id to a pattern, its marks and a re-export | `specs/00[5-8]` briefs and reports; `packets` How the patterns are built |
| `how-to/name-an-unknown-field.md` | Name an `unk_*` field with a stated basis | `packets` Naming unknown fields; 006 T014a; `research/03040008/packets/tools/unk_correlate.py` |
| `how-to/build-plbatch.md` | Build the batch engine | `research/imhex/plbatch/README.md` Build |
| `how-to/apply-a-client-patch.md` | Apply and verify one `.r2` layer | `patches/README.md` How to apply, Caveats |
| `how-to/add-a-client-patch-layer.md` | Record a new layer with its hash chain | `patches/README.md`; `prot` §4 step 3 |
| `how-to/triage-a-client-crash.md` | Capture, classify and record a crash | `prot` §4, §5 |
| `how-to/query-ida-read-only.md` | Open a private copy and query it (`pc`, `pc-accepted`, `ps4`) | `CLAUDE.md` Tools; `research/ida/private-copy.sh`; `xfer` Read path |
| `how-to/write-to-an-ida-database.md` | Run a write as a headless batch; check the save | `xfer` Write path; `CLAUDE.md` Learnings; 007 T004d |
| `how-to/transfer-annotations-ps4-to-pc.md` | Extract, match, transfer, apply, verify | `xfer` Function repair, Apply script, wave 2 commands; 007 `spec.md` |
| `how-to/regenerate-elf-dumps.md` | Rebuild or verify the PS4 dump set | `elf` §2; `AGENTS.md` PS4 ELF dumps |
| `how-to/convert-textures.md` | Extract images | `research/textures/how-to-extract-images.adoc` |
| `how-to/run-pharos.md` | Run OOAnalyzer | `research/pharos/README.md` |
| `how-to/verify-a-regeneration.md` (gap) | Check a 100k-file re-export by prediction and a stratified sample | 008 `spec.md`, 006 `spec.md`, `packets` T014c and TC1 notes |
| `how-to/run-the-gate.md` | Run `tools/check.sh` and read its lines | `tools/check.sh:2-16` |
| `how-to/write-documentation.md` | Change a page and pass the link check | reconstructor `docs/how-to/write-documentation.md` |
| `how-to/run-flag-investigation.md` | Pointer only: `research/03040008/flags/README.md` stays whole | other work; may merge into the index |

### Reference

| Page | Purpose | Sources |
| --- | --- | --- |
| `reference/documentation-style.md` | The writing contract | reconstructor contract; spec § Target structure |
| `reference/glossary.md` (gap) | Terms used on two pages: marks, fit, slack, tier 0, f1c9, DUMP_FIX, nNetMsg, CData, `(g.id.sub)` | new, from the sources below |
| `reference/repository-layout.md` | Every top path, producer, outside reader | `AGENTS.md` Facts; `readme.adoc` Repository layout, Data flow |
| `reference/inputs-and-builds.md` | Builds, clients, databases, captures, videos | `AGENTS.md` Facts; `xfer` wave 2; `research/rng-race/README.md` Video; `CURRENT-RECOVERY.json` rule |
| `reference/tools-and-shell.md` | Tools and versions a human needs | `readme.adoc` Toolchain; `AGENTS.md` Shell tools (summary only) |
| `reference/conventions.md` | Naming and file formats | `AGENTS.md` Conventions |
| `reference/gate-and-hooks.md` | Gate sections and what each hook refuses | `tools/check.sh`; `AGENTS.md` Agents; `tools/hooks/` |
| `reference/packet-ids.md` | The 595 rows, intact, and the id-to-report key | `packets` Patterns |
| `reference/packet-includes.md` | The 36 includes and their users | `packets` Include table |
| `reference/packet-marks.md` | Mark legend V, I, G, open; comment forms; bases | `packets` lines 51-84, 222-246; 008 `spec.md` Marks |
| `reference/packet-pattern-format.md` | Header lines, JSON shape, exported checks | `packets` lines 86-132; `adoc` Exporting raw |
| `reference/packet-wire-format.md` (gap) | Framing, source byte, RES header, list and string forms, cipher constants, known plaintext | `include/Packet.hexpat`; `adoc:110-115`; 005 P1, P2, P4; 006 T002c, T003; 008 T002 |
| `reference/packet-handler-tables.md` (gap) | PC 03040008 directory `0x1bc0110`, per-group `{table, count}`, login table `0x1bd6270`, PC string names | 006 T001, T002, T003, T006-T013 headers; 007 `spec.md` |
| `reference/packet-open-questions.md` | The open unknowns by group | `packets` Open items (39 of 61 bullets); 008 `tasks.md` Close |
| `reference/imhex-export-cli.md` | Options, filter forms, summary counts, environment | `packets` How to export; `packets/imhex-export.sh:4-51`; `adoc` |
| `reference/plbatch-cli.md` | Flags, output lines, exit codes | `research/imhex/plbatch/README.md` Use |
| `reference/arrowgene-cli-patches.md` | The patch table | `adoc` Required patches |
| `reference/client-patches.md` | Hash chain, lineage, `.r2` encoding | `patches/README.md` tables; `prot` Lineage; R3 §1 |
| `reference/protection-inventory.md` | Mechanisms, sites, state per build | `prot` §2; R2, R3 §6 |
| `reference/elf-dumps.md` | Provenance, storage, verification; links `elf` § 3, § 7 | `elf` §2, §6 |
| `reference/ida-transfer-tools.md` | Scripts, extractor schema, manifest columns, rule list | `xfer` version sections, Transfer rules, Layout rules |
| `reference/community-resources.md` | Wikis, repositories, videos | `research/wikis-and-resources.adoc` |
| `reference/quest-flag-sources.md` | Where each flag command lives in 03040008 | `research/03040008/quest-flag-data-source-mapping.adoc` |
| `reference/external-references.md` | Pointer page to `research/external-references.*` (path stays) | `research/external-references.md` |
| `reference/status.md` | The dated counts: coverage, fit totals, what was not run | `rwf` Coverage; 008 `tasks.md` Close |

### Explanation

| Page | Purpose | Sources |
| --- | --- | --- |
| `explanation/evidence-model.md` | Why authority goes by fact type; PC decides Season 3; PS4 by code; server names as leads; a not-run check | `AGENTS.md` Evidence rules; constitution; `packets` Evidence rules; 006, 007, 008 `spec.md` rules; `readme.adoc` Data flow |
| `explanation/wire-protocol.md` (gap) | Transport, encryption, handshake, packet framing, nNetMsg RPC, RES guard | `adoc` patch reasons; `packets` RES guard; 005 P1, P2; 006 T002c, T003 |
| `explanation/packet-decoding-method.md` (gap) | Reader first; the fit rule and what it does not prove; value bases and distinct counts; include-change rule | `packets` lines 134-138, 235-246; 008 T006, T007; 006 R4 |
| `explanation/ida-transfer-method.md` | Why matching by code gates, not names; false positives met | 007 `spec.md` Method; `xfer` Matcher, Role anchors, wave 2 |
| `explanation/client-lineage-and-protections.md` | What the PC client is, what layers do, why hooks crash | `prot` §1, §3 lesson; R1, R2 §2, R3 §5 |
| `explanation/rng-race.md` | Why long-session captures do not decrypt | `research/rng-race/README.md`, `NOTES.md`; reconcile with ddon-hook `specs/013-prng-state-recovery/` first |
| `explanation/ps4-elf.md` | Structure of `DDOORBIS.elf` (PS4_02020005) | `elf` §4 |
| `explanation/plbatch-design.md` | Why a batch driver, the pin, the cost per file | `research/imhex/plbatch/README.md` Why, Verification, Cost |

Directory READMEs (short, per the spec): root `readme.adoc`, `research/`, `research/03040008/packets/`, `research/03040008/ida-transfer/`,
`research/03040008/protections/`, `patches/`, `packets/`, `research/rng-race/`, `research/imhex/plbatch/`, `research/pharos/`; new ones for
`research/03040008/dumps/`, `xfs/`, `notes/`, `research/scripts/`, `research/prompts/`, `research/textures/`, `tools/`.
Left whole: `research/03040008/protections/R1-R3`, `research/rng-race/NOTES.md`, `IDEAS.md`, `research/claude-vision-tokens.md` (evidence reports,
cited by section); `research/03040008/flags/*`, `research/knowledge-graph/` (other work).
Not counted as docs: `.claude/agents/*.md`, `.claude/skills/**`, `.specify/templates/*` (agent and tool files); `elf-dumps/archive/**` and
`research/rng-race/scratch-*` (gitignored, fixed records); `.pytest_cache` and `plbatch/build/**` READMEs (tool output).

## 3. Gaps: knowledge with no page

Checked with `rg` over the live tree outside `specs/`, `client/`, packet data, patterns and includes. **V** for the count of files.

| Knowledge | Where it lives | Live docs naming it | Goes to |
| --- | --- | --- | --- |
| PC handler directory `0x1bc0110` (74 groups, `{table, count}`; 03040008) and login table `0x1bd6270` | 006 T001:36, T002:22, T003:23; 007 `spec.md:15` | 0 | `reference/packet-handler-tables.md` |
| How a pattern is written: triage, batch per group, reader walk, header, marks | 005-008 briefs and reports; only its output format is in `packets` | none as steps | `how-to/write-a-packet-pattern.md` |
| Marks `G`, `G (lead)` and the source order | 008 `spec.md:14-36`; `packets:222-246`, inside the Patterns legend | `packets` only, buried | `reference/packet-marks.md` |
| Wire format as one text | scattered: `include/Packet.hexpat`, `adoc:110-115`, `rng-race/NOTES.md`, 005 P1, 006 T003 | 0 whole | `packet-wire-format.md`, `wire-protocol.md` |
| `Write_cstr` (u16 BE length, no NUL) | 008 T002 | 0 | `packet-wire-format.md` |
| After an include change, re-export every includer | 008 `tasks.md:50-52` | 0 | `explanation/packet-decoding-method.md`, write-a-pattern how-to |
| Verify by prediction plus stratified sample | 006 `spec.md:31`, 008 `spec.md:42`; user memory | 0 | `how-to/verify-a-regeneration.md` |
| `unk_correlate.py` | `research/03040008/packets/tools/` | 0 | `how-to/name-an-unknown-field.md` |
| Annotated PC database `spec007-packet-handlers-20261103-wave2`, and `private-copy.sh pc-accepted` | 007 `tasks.md:223`; `xfer:500-501`; `research/ida/private-copy.sh:7,42` | `xfer` only; `AGENTS.md` and `CLAUDE.md` name `pc` and `ps4` | `reference/inputs-and-builds.md`, `how-to/query-ida-read-only.md` |
| Matching gates and tiers (why, without run counts) | 007 `spec.md:41-89` | `xfer` as implementation notes | `explanation/ida-transfer-method.md` |
| IDA batch-write recipe | `xfer:7-29`; `CLAUDE.md:51-52`; 007 T004d | present, inside a tool README | `how-to/write-to-an-ida-database.md` |
| The fit rule | `packets:134-138`, `include/Packet.hexpat:8-12`, every pattern header | present, no page | `explanation/packet-decoding-method.md` |
| Season 3 list of exclusive ids | 006 `research/season3-exclusive.tsv` | 0; all now patterned | history |
| Open at the close of 008: 29.23.16, 11.88.16, 11.118.16 | 008 `tasks.md:41-42` | 0 | `reference/packet-open-questions.md` |
| Recompilation C++ as baseline; IDA misorders stack arguments | 006 `spec.md:28-29`, 007 `spec.md:104`; `packets:177-178` | partial | `explanation/evidence-model.md` |
| Glossary | none | 0 | `reference/glossary.md` |

No page anywhere for these workflows: writing a packet pattern, verifying a regeneration, running the gate, adding a patch layer as steps of its own.
`.claude/` process and `specs/orchestration.md` stay out of `docs/` (contract: process vocabulary belongs to the development setup).

## 4. Tutorial: read one packet by hand (run, V)

Input (client 03040008, tracked at the base; last JSON commit `4abc0b4b80e`):

| File | SHA-256 |
| --- | --- |
| `packets/decrypted_raw/stream3-party-experiments-marked.pcapng_tcp-stream-47/12863_S2C_WARP_WARP_RES_2019-07-08T10_35_53.3199119-07_00.14_3_2` | `4a693d40ba70f74a7b2af3b43ee028e96a5cb9f298abb533d5ba1dd27ac8759f` |
| the same path under `packets/decrypted_json/` plus `.json` | `d93d890bc91a8c758d322f28b344fbd84044b979d0cebfd0ca3ce76786c79b1b` |
| `research/03040008/packets/S2C_WARP_WARP_RES-pattern.cpp` | `0e8e3f859a7d1b2988054ed97be3c83cdc597850ab0856a124cc37a68b63c044` |

Needs `xxd`, `jq`, `fd`. No IDA, client, ImHex, plbatch or build; nothing is written. Commands (from the repo root), as run on 2026-11-04:

```sh
R=packets/decrypted_raw/stream3-party-experiments-marked.pcapng_tcp-stream-47/12863_S2C_WARP_WARP_RES_2019-07-08T10_35_53.3199119-07_00.14_3_2
wc -c "$R"                 # 32
xxd "$R"
# 00000000: 0e00 0302 3400 0000 0000 0000 0000 0000
# 00000010: 0000 0000 4200 0098 c55b ba26 6063 30a9
sed -n '1,30p' research/03040008/packets/S2C_WARP_WARP_RES-pattern.cpp
jq -c . "packets/decrypted_json/${R#packets/decrypted_raw/}.json"
# {"packet":{"group":14,"id":3,"subId":2,"source":52,"packetcounter":0,"sourceOk":true,"Error":0,"Result":0,"WarpPointID":66,"Rim":39109,"paddingSize":7,"fits":true}}
fd -d 2 -t f S2C_WARP_WARP_RES packets/decrypted_json -x jq -r .packet.fits | sort | uniq -c    # 44 true
```

What the reader works out: `0e` group 14; `0003` id 3; `02` sub 2 (name suffix `14_3_2`); `34` source server; `00000000` counter; body from 0x09: Error 0,
Result 0, `00000042` = 66, `000098c5` = 39109; the last 7 bytes are cipher padding, `paddingSize` 7, under 16, so `fits`. The tutorial closes on the
fit rule (a shorter body would fit too; PC reader `0x81dc00` is why the layout stands) and links the marks and the wire page.

A variant running `plbatch` was **not run**: it needs a local build (present here, not committed) and writes output. T002 can add the tutorial to the docs gate:
verify the three hashes and compare the `jq` line. Requires a full clone with the packet data (160,615 raw files, tracked).

## 5. Stale facts

| Fact | Evidence | State |
| --- | --- | --- |
| `plan/` is a path (`AGENTS.md:32`, `CLAUDE.md:12`, `readme.adoc:95`) | absent; `git ls-files plan` 0 | V stale. `tools/check.sh:23` SMALL_TREES also lists `plan` and lacks `docs`: T002 must add `docs` or the new gate section never sees it |
| `research/README.adoc` (`AGENTS.md:126`, `readme.adoc:147`, `rwf:192`) | index holds `research/readme.adoc`; **disk holds `README.adoc`**; `core.ignorecase=true` | V. Works locally, 404 on GitHub; a local link check on Windows cannot see it, so the gate must compare against `git ls-files` case-sensitively. Rename in two `git mv` steps |
| `CLAUDE.md:7` "no active feature" | spec 009 open; no `.specify/feature.json` | V stale |
| `packets` "not patterned" bullets: 11 bullets, 51 distinct ids | all 51 have a pattern today | V stale since 008 |
| `packets:185-234` status legend dated 2026-11-01..03 | 31 n/m differ from the JSON (§6) | V stale |
| `packets` Include table: 35 rows | `include/` holds 36 files; `CharacterData.hexpat` is named only in prose | V |
| `adoc:38,40` `./run-parallel-packet.sh`; title "Parallel CLI Runner" | absent; the script is `packets/decrypt-annotate-streams.sh` | V stale |
| `adoc:60` Arrowgene clone under `C:\Users\morph\Documents\GitHub\Sehkah\` vs `AGENTS.md` `D:\GitHub\Sehkah\` | both folders exist; D: clone at `e2411fe8`, the adoc's base; the C: clone's HEAD not read | V contradiction; which one the patched build used: not checked |
| `prot:40-41` "`patches/README.md` says otherwise", `prot` §6 corrections | `patches/README.md:91,118,119` already state them | V stale |
| `prot` §4 step 3 as future work | `patches/2026_10_17_ddo_dump_fix_4.r2` exists, untracked | V; other work |
| `patches/README.md:55` "10 of the 12" | 12 tracked, 13 on disk | V true of tracked |
| `AGENTS.md:44` "the Arrowgene server docs ... DDOn-Tools hex patterns (read `research/02030004/`)" | Arrowgene `docs/quests/generic_quest_state_machine.md:77` links the repo root only; DDOn-Tools (`D:/research/DDOn-Tools` `795cd6c`) has provenance URLs to `rstagecustom*-season2-pattern`, names not in `research/02030004` | V: credit, not a live read. The spec's rule to keep the path still stands |
| `AGENTS.md`, `CLAUDE.md`: `private-copy.sh <pc\|ps4>` | the script also takes `pc-accepted` | V incomplete |
| `AGENTS.md:136-139` IDA databases do not mention spec 007's published copy | §3 | V incomplete |
| `research/rng-race/README.md` Resume, "Nothing is pushed", deployed DLL | dated 2026-10-17 | I stale; ddon-hook has `specs/013-prng-state-recovery/`, not read here |
| `rwf` line 10 "PS4 debug symbo automation"; Ghidra as required tool | text; `AGENTS.md` prefers IDA MCP | V |
| `rwf` Coverage for 03040008: 186 / 145 / 56% | re-run 2026-11-04: same | V **not** stale; 02030004 not re-run; undated on the page |
| `research/external-references.md` report index: 2 topics | jsonl `report` values also name `specs/005.../P7`, `specs/005.../research.md`, `xfer`, ddon-hook specs | V incomplete; the jsonl is dirty, other work |
| `readme.adoc:90-92`, `AGENTS.md` Facts table | no row for `tools/`, `specs/`, `research/03040008/packets`, `research/imhex`, `research/rng-race` | V incomplete |

## 6. Splitting `research/03040008/packets/README.md`

Measured (V): 117,079 bytes: build section 17,743 (include table 10,744), export 2,307, legend 5,856, table 56,553 (48%), open items 34,239.

| Lines | Becomes |
| --- | --- |
| 1-7 | short directory README: holds, produced by, links; plus a pointer to `docs/` |
| 13-49 include table | `reference/packet-includes.md`; add the missing `CharacterData.hexpat`; "since Tn" wording goes, content stays |
| 51-56, 74-84, 222-234 marks | `reference/packet-marks.md` (the legend) |
| 58-73 naming bases | `how-to/name-an-unknown-field.md` |
| 86-114, 125-132 | `reference/packet-pattern-format.md` |
| 116-123 RES guard | `explanation/wire-protocol.md`, the rule also in the format reference |
| 134-138, 235-246 | `explanation/packet-decoding-method.md`, rule also in the marks |
| 140-169 | `how-to/export-packets-to-json.md`, `reference/imhex-export-cli.md` |
| 171-181 | `explanation/evidence-model.md` |
| 185-221 | key from report label to spec path, at the top of `reference/packet-ids.md` |
| 248-844 | `reference/packet-ids.md`, rows intact |
| 846-1215 (61 bullets) | 39 open questions to `reference/packet-open-questions.md`; 11 stale "not patterned" and 11 batch-history bullets stay in their specs and are cut (`T001-sections.tsv`) |

**Generation test** (run over 595 patterns and all JSON, V):

| Column | Generatable from | Result |
| --- | --- | --- |
| Id, Pattern | `// packet-id:` and the file name | 595/595, once 6 rows' `(was ...)` is stripped |
| Marks in Status (115 rows) | `T00[345] (V\|I\|G\|open)\b` anywhere in the pattern | 115/115 equal |
| n/m fit | `rg -l '"fits": true'` plus `rg --files`, keyed by id and `packet-select` (2.9 s, 160,615/160,615 fit) | 556 equal, **31 differ**, 8 no-capture rows still have none. In the 12 differences printed, the table is lower, e.g. 3.3.16 59,881 vs 66,275, 11.95.16 48 vs 96 (I: table not recounted after 006 TC3 restored raws) |
| Report | `// Evidence:` line | 564 patterns have it, 31 do not; equality not checked |
| Notes | none | 281 rows hold hand text; 67 marks only; 247 bare |

**Proposal:** first move the rows intact (spec rule). Then a check, not a generator, in `tools/check.sh`: id and name against the pattern files, marks against pattern
comments; n/m in the same check since it costs seconds. Correct the 31 counts in one dated data change. Full generation would need a sidecar for the 281 notes, with no use yet.

The table file is still about 56 KB, so a table edit via the Edit tool will still echo about half of what the retro complained of (I). Either write rows with a script, or split by
group (55 groups; largest group 11, 7.8 KB). I recommend the single file: lookups and the check stay simple. Decision for the coordinator.

## 7. Paths that must not move

| Path (build) | Reader | Spec lists it? |
| --- | --- | --- |
| `client/03040008/` | `ddon-explorer-server` `src/main/resources/application-dev.yaml:7` | yes |
| `client/03040008/quest` | `DDON-translation` `Tools/Speaker_and_Quest_Text_Type_Filler.py:313`, `Tools/last_archive_folder.txt:1` | yes |
| `client/03040008-layout-npc-location.csv` | ddon-hook `scripts/automation/stream49_constants.json:63` (source note) | new (out of scope anyway) |
| `research/02030004/` | constitution:47; DDOn-Tools credit URLs | yes |
| `research/03040008/protections/README.md`, **with §1, §5** | ddon-hook `AGENTS.md:57`, `docs/development/08:70`, `09:206`, `14:12`, `14:41`, `15:142`, `scripts/automation/run_cycles.py:614` | path yes; **sections new** |
| `research/external-references.{md,jsonl}` | ddon-hook `AGENTS.md:84-85` | yes |
| `research/claude-vision-tokens.md` | ddon-hook `docs/development/11:113`, `13:91` | **new** |
| `research/rng-race/` (`ddonrng.py`, `race_model.py`, `pat2.json`, `cbcdec.exe`) | ddon-hook `tools/rng/timeline.py:48`, `corpus.py:50`, tests | **new** |
| `packets/keys/keys-all-in-one.csv`, `decrypt-pcapng-streams-all-in-one.sh` | ddon-hook `tools/rng/corpus.py:48`, `tear_search.py:819,901`, `test/core/domain/test_mt_random.cpp:23` | **new** |
| `binaries/PS4_02020005/elf-dumps/` (`README.adoc`, `manifest.jsonl`, `dwarf/inline-chains.orbis-addr2line.tsv`, `local/`, `archive/`, `ida/`) | reconstructor `AGENTS.md:8`, `docs/how-to/*`, `docs/reference/prerequisites.md:119`, `tools/orchestration/{aba,corpus_slot}.sh`, `tools/release/pgo_train.sh`, `tools/llm/tests/support/machine.py:26` | **new** |

Internal (movable only with their readers, no benefit): `research/ida/private-copy.sh` (`guard_ida.py:2,20`, `check.sh:166`), `research/03040008/ida-transfer` (`check.sh:182`, `.gitignore:71-72`),
`research/imhex/plbatch` and `research/03040008/packets` (relative in `packets/imhex-export.sh:105,126-127`; `check.sh:152,155`), `research/03040008/flags` (`src/ddon_flags/_paths.py:10` by depth),
`packets/*.sh` (`check.sh:24` glob; each `cd`s to its folder).

Search: `git grep` over tracked files at ddon-explorer-server `fbf3264`, DDON-translation `1617282d`, ddon-hook `36a61a6`, reconstructor `36a2216e2`, ddon-extractor `e6c358ea`, ddon-ghidra-scripts `613c24f`,
ddon-data-s1 `b0ce4b9a`, ddon-data-s2 `371a082ce`; each excluding `specs`, `client`, `packets`, `recompilation`, testdata, fixtures. Also Arrowgene `88d82caf`, upstream `e2411fe8`, `ddon-dwarf-reconstructor` `f006ce4`, DDOn-Tools `795cd6c`.
ddon-extractor, ddon-ghidra-scripts, ddon-data-s1 and s2 read nothing here by path (V; the first two name the repo in prose; s2 only its own `recompilation` in `.vscode`).

## 8. Proposed moves, largest benefit first

Reader updates go in the same package; `T001-files.tsv` has the rows. 27 rows move, 94 stay.

1. **Packets README split** (§6): the retro's cost and the largest body of method. Outside the closed specs, the live files searched (`AGENTS.md`, `CLAUDE.md`, `tools/`, `.claude/`, includes, `packets/imhex-export.sh`, plbatch README) name no `research/03040008/packets/README.md` (V); 3 pattern comments mention a README; the links from `packets:168,850` into the adoc move with their text.
2. **`adoc` to pages**, `packets/README.md` short. Update `AGENTS.md:131`, `readme.adoc:167`, `packets/decrypt-export-streams.sh:15`, `packets/statistics-commands.sh:14`. `packets/decrypt-annotate-streams.sh` is dirty and names no adoc path, so it needs no edit (V).
3. **`xfer` to pages**, directory README short. Update `CLAUDE.md:52`.
4. **`research/readme.adoc`, `research/rLandInfo-example.adoc`, `research/wikis-and-resources.adoc` to pages**; short `research/README.md`. Case-rename trap (§5). Update `AGENTS.md:126`, `readme.adoc:147`.
5. **`research/scripts/`**: `find-unsupported-extensions.sh`, `validate_pattern.sh`, `dump-season{1,2,3}-headers.sh`, `jq-npc-shops.sh`, `jq-setinfo.sh`. No relative path breaks (V: `/d` absolute or cwd-relative to the root). Update `AGENTS.md:121,125`, `readme.adoc:141`, `tools/check.sh:215`.
6. **`research/03040008/notes/`**: `q00030260_*`, `q50204000-*`, `release-contents-research.txt`, `release-elements.txt`, `quest-flag-data-source-mapping.adoc`. No reader found. After it the directory holds patterns and subdirectories only.
7. **`prot`, `patches/README.md`, plbatch, pharos, textures, `research/rng-race/README.md`, `elf` § 2, § 4** to pages; paths and §1, §5 pointers stay.
8. **`packets/statistics/`** for the 6 output files. Needs `statistics-commands.sh` changed where it publishes to its own folder (I: the stage files move to `.`; exact lines to read in T002). Small benefit: can be dropped.
9. **`research/prompts/`** for the 3 `gpt-*` files. No reader. Small.
10. `research/PS4/` only if its build is checked (build not stated in the file); `research/bbm/`, `research/wireshark/` stay.

Not moved, per spec: `research/external/*`, `research/external-references.jsonl`, `research/03040008/flags/**`, `research/knowledge-graph/`, `patches/2026_10_17_*`, `specs/*-1.md`.

## 9. Per-build pattern layout

**Leave `research/<build>/r*-pattern.cpp` as it is** (V for the facts, I for the judgment). `research/02030004/` must stay, so a `resources/` subfolder under 03040008 alone makes the builds differ, and `AGENTS.md`'s convention would then need two forms.
Benefit of moving: tidier listing only, and step 8.6 gives that by removing the 5 notes. Cost is low either way: no include is relative (only `research/02030004/rStageInfo-pattern.cpp` includes, `<std/core.pat>`), no outside reader names one (0 sibling hits), and live mentions are only in `research/rLandInfo-example.adoc` plus an example string in `validate_pattern.sh:21`.
Alternative if the coordinator prefers symmetry with `packets/`: `research/03040008/resources/`, 60 `git mv`s, 01020003 and 02030004 flat.

## 10. Contradictions and missing checks

- Spec lists outside readers "plus whatever the census finds": §7's four additions extend it.
- `research/03040008/protections/README.md` both must stay (spec) and must become a short README (spec: no method in a directory README), while ddon-hook cites §5 for the method. Resolved by a section map in the README that keeps the numbers; the outside edit is reported to Sam. See decision 2.
- `elf` same shape: outside readers read § 3, § 7, so those stay in the README, against "short". See decision 2.
- Marks in `packets` are the authority for `T00[345]`; T014b marks (77 in patterns) have no table count: not compared.
- **Not run:** ImHex (not on PATH), plbatch, `tools/check.sh` (no code changed), link checks; `research/pharos/*` beyond the README; external URLs of `wikis-and-resources.adoc`; `research/knowledge-graph` as a reader: one test, `tests/test_resource_observations.py`, matched a path regex by file name only, not read (brief scope), so its owner should check it before any move under `research/03040008/dumps/`; ddon-hook `specs/013` not read; `find-unsupported-extensions.sh 02030004` not run.
- Run although read-only in effect: `research/find-unsupported-extensions.sh 03040008`, which writes only its own temp folder, removed by its trap (V: `git status` clean for those paths).
- `t001/*.py` were added under `research/` because Bash heredocs lost text to the shell's `eval` and the Write hook refuses the scratchpad. One list written by redirection to the session scratchpad before that refusal was deleted.

## 11. How the row counts were checked (V)

`t001/sections.py` asserts per file: every heading has a classification row and every classification matches a heading; the line ranges sum to the file's line count. Headings: fenced-block-aware `^#{1,6} ` or `^={1,6} `.
Independent count without fences: 288 raw vs 281; all 7 differences are `#` comment lines in `research/03040008/flags/README.md` code blocks (26 raw, 19 real). Four files add a preamble row (`how-to-extract-images.adoc`, `wikis-and-resources.adoc`) or a whole-file row (`texture-research.md`, `quest-flag-data-source-mapping.adoc`): 281 + 4 = 285 heading rows, plus 72 `[sub]` rows = 357. All rows have 6 columns (`awk`, 0 exceptions in both TSVs).
Files: one row per `research/03040008/r*-pattern.cpp` (60 by `ls`, 60 by `rg -c` in the TSV) and per listed loose file; git status computed per path from `git ls-files` and `git status --porcelain`.
Reader tokens that hit quest ids in `DDON-translation` CSVs (`q50204000`, `q00030260`) or the siblings' own `tools/` were narrowed and re-run; remaining rows may still carry a mention that is not a read, such as `validate_pattern.sh:21`'s example path.

## 12. Decisions for the coordinator

1. **Packet table**: one Markdown reference file with a check in the gate, written by script (recommended), against per-group files or a full generator.
2. **READMEs with outside readers** (`protections/README.md`, `elf-dumps/README.adoc`): keep the file, keep the cited sections as pointers or in place (recommended), and report ddon-hook and reconstructor updates to Sam; or edit those repositories in the same package.
3. **Loose patterns**: stay flat in `research/<build>/` (recommended), or add `research/03040008/resources/`.
4. **Scope of moves**: do steps 1-7 and 9, drop `packets/statistics/` (step 8) and leave `research/PS4`, `bbm`, `wireshark` (recommended)?
5. **Page count**: 58 pages is the complete map; land the packet and evidence wave first and merge thin pages (`run-flag-investigation`, `external-references`, `status`) if they stay under a screen.

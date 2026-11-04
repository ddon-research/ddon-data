# 009 T010: editor pass over the documentation

Role `editor`, base `db01c0774b5`. All five page groups are done; no page remains. Gate: `bash tools/check.sh --since db01c0774b5`, `docs` passed, 0 findings.

This report sits under `research/reviews/`: the brief names `specs/009-docs-structure/research/T010-editor.md`, and the role's guard refuses that path.

## Pages

| Page | Changed | Cut |
| --- | --- | --- |
| `readme.adoc`, `docs/index.md` | opening, double colons | |
| `docs/tutorials/read-one-packet.md` | "packet id", one heading; inputs, hashes and `jq` line untouched | |
| `two-packet-decodings.md`, `evidence-model.md`, `packet-decoding-method.md`, `wire-protocol.md`, `plbatch-design.md`, `ida-transfer-method.md`, `client-lineage-and-protections.md`, `ps4-elf.md` | openings in one form (reader, gain, what first), glossary links, active voice; the `lea` incident in the present tense | hedges, "Note that"; `ps4-elf.md`'s remark on `archive/` |
| `rng-race.md` | the open list's lead | the name of who closed it; corrections of `NOTES.md` |
| `docs/how-to/*` | `apply-a-client-patch.md` (no count), `choose-a-resource-target.md`, `convert-textures.md`, `export-packets-to-json.md`, `inspect-captures-in-wireshark.md` (`game-select`), `patch-the-arrowgene-cli.md`, `reannotate-streams.md` ("raw files"), `transfer-annotations-ps4-to-pc.md`, `triage-a-client-crash.md` (report paths in full), `write-to-an-ida-database.md` ("original", not "the user's") | a sentence of `name-an-unknown-field.md` repeating its opening. The others met the bar: no change |
| `client-patches.md` | Lineage as Mermaid, with the arrow's meaning corrected in wording (it read "was built from" on parent-to-child arrows) | year bullet lists that repeat the Lineage table |
| `packet-pattern-format.md`, `arrowgene-cli-patches.md`, `imhex-export-cli.md`, `protection-inventory.md` | tense, a term, blank lines | the size line's history |
| `glossary.md` | added: capture, plbatch, FIX names, and a section for Arrowgene, ddon-hook, reconstructor | |
| `patches/README.md`, `research/03040008/ida-transfer/README.md` | short form | method, history, gate commands |
| `packets/README.md`, its pattern, plbatch and wireshark READMEs | "hand-written" | |
| Read, unchanged | `research/README.md`, `tools/README.md`, `research/03040008/protections/README.md`, `binaries/PS4_02020005/elf-dumps/README.adoc`; every other page of `docs/reference/` (`packet-ids.md`'s table and `packet-marks.md`'s marks untouched). Of `ida-transfer-tools.md` and `community-resources.md`, I read the opening, the headings and the prose lines rather than every row | |

`client-patches.md` and `packet-ids.md` keep both of their parts: neither misleads a reader. `client-patches.md` is a lookup whose lineage is a lookup too; the reasons are on the explanation page. `packet-ids.md` keeps the report key as its key.

## Facts I doubt

1. `docs/explanation/ida-transfer-method.md:91`: "the login handler table at `0x888000`-`0x88E000`". `docs/reference/packet-handler-tables.md:108-121` gives the login directory at `0x1bd67f4` and handlers from `0x886650` to `0x887740`; the range holds neither.
2. `docs/how-to/query-ida-read-only.md:14` and `docs/reference/packet-handler-tables.md:7` state more than is known. Only `pc-handlers` was opened (`T009c`, item 4: "not settled"; `T009` lists it as unchecked). **Proposal:** run a read-only check of `pc` and `pc-accepted` (stored input SHA-256, the directory, a sample of addresses). Until then, write: "The addresses were checked in `pc-handlers`, whose stored input is `f1c9`; `pc` and `pc-accepted` are not run."
3. `docs/explanation/wire-protocol.md:32`: "seeded once from a millisecond timer". `docs/explanation/rng-race.md:13` has a static initializer, `init(0)` and `init(seed)` twice.
4. `docs/how-to/triage-a-client-crash.md:46`: "in its smoke runs ... the hooked client still crashed", without what `T009` finding 4 corrected on the lineage page: the three runs are compares only, this layer, this layer plus `rdtsc`.
5. `docs/reference/repository-layout.md:87`, `readme.adoc`: Season 1 is client `01010004`, with patterns under `ddon-data-s1/research/01020003/`. The two numbers differ; I did not check why.

## Facts cut or moved

| Fact | From | To |
| --- | --- | --- |
| The plain dump's tools; what the layers of each period are for | `patches/README.md` | `docs/reference/client-patches.md`, Lineage |
| `2026_10_17_*` not tracked | `patches/README.md` | already on `client-patches.md`, "A layer outside the index" |
| The chain "stays verifiable" | `patches/README.md` | cut: the sentence before it states the rule |
| Year bullet lists of layer changes | `client-patches.md` | same page, Lineage table |
| "Ten" UTF-16 `.r2` files | `apply-a-client-patch.md` | already on `client-patches.md`, `.r2` row, and Status |
| "65" group-35 packets | `export-packets-to-json.md` | already on `packet-pattern-format.md`, JSON conventions |
| Gate commands, spec pointer | `research/03040008/ida-transfer/README.md` | already on `ida-transfer-tools.md`, Scripts and Published results |
| The CLI once filed the certificate notice under `.1_0_1` | `packet-pattern-format.md` | stays in `T002c §3` |
| `archive/` says "resolves all 648" | `ps4-elf.md` | cut: the page already gives the right count, and `archive/` is a fixed local record |
| Closed "by Sam's decision" | `rng-race.md` | cut; the date and result stay. Restore it if the decision's author matters |
| Notes' "seeded once", "185 M/s" | `rng-race.md` | stay in `research/rng-race/NOTES.md`, which the opening says this page overrides |
| Pointers to `research/rng-race/README.md` and `NOTES.md` | `wire-protocol.md` | replaced by a link to `rng-race.md`, which cites them |

**Facts that need a home.** A search of the pages finds neither `T009c` note. I added none of these, since they are new to the pages:

- `T009c` note 1: 9 of the 20 login handlers have no IDA function in the annotated database (`0x886650`, `0x886750`, `0x886b00`, `0x886d00`, `0x886e00`, `0x886ec0`, `0x887130`, `0x8874b0`, `0x8875b0`), and `0x886820`, `0x886fd0` lie inside functions starting a little earlier. A reader of `write-a-packet-pattern.md:21` opening `0x886b00` sees `dd` data. Home: `packet-handler-tables.md`, Login server.
- `T009c` note 2: Hex-Rays leaves out the send and receive logic of `0x9d6a20` and `0x9d6d20`; both claims stand only in the disassembly. Home: `packet-wire-format.md`, First packet of each direction.
- `extract-client-resources.md:47` and `repository-layout.md:28`: "about 173k files" has no row on Status. Left in place.
- `rng-race.md`: its counts are measurements of a closed investigation, which no re-export can change, but no contract clause covers them. Left in place (see amendment 1).

## Contract amendments I propose

1. "Facts about fixed inputs" should also cover the dated measurements of a closed investigation, so `rng-race.md` keeps them.
2. `docs/explanation/ps4-elf.md` is mostly lookup lists on a fixed input, with two "why" sections. Decide whether the lists move to `docs/reference/`. Not done: it is a structure decision, and links cite the page.
3. The contract says a report is cited by its path; the packet pages use labels in code spans through the key of `packet-ids.md`. State that exception.
4. `AGENTS.md` says "Hand-authored" where the pages and `tools/README.md` say "hand-written": align it.
5. The brief lists `tools/README.md` and also says never touch `tools/`, and the role's guard does not cover it. It needed no edit; remove it from the editor's list or add it to the guard.
6. The role's guard allows `specs/*/research/reviews/*`, while the brief's report path is `specs/*/research/`. Align the two.

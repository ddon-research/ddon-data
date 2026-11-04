# Glossary

The terms that more than one page uses, for a reader who knows x86, ELF and DWARF but not this project. Nothing is needed first. A term is defined once, here; a page links it on first use.

## Builds and clients

| Term | Meaning |
| --- | --- |
| build | A client version number: `03040008` (PC, Season 3), `02030004` (PC, Season 2), `01010004` (PC, Season 1), `PS4_02020005` (PS4, with debug symbols). Every client fact names one. |
| DUMP_FIX, `f1c9` | The patched PC executable of build 03040008 that `research/03040008/protections/README.md` analyses. `f1c9` is the start of its SHA-256; that README and `patches/README.md` name client executables by such prefixes. |
| recompilation | The C++ of client 02030004 in the sibling repository `D:\ddon-data-s2`, directory `recompilation/`. |

## Packets

| Term | Meaning |
| --- | --- |
| packet id | The three numbers `group.id.sub` of a packet's header, for example 14.3.2, also written `(g,id,sub)`. A raw file's name ends in them, as `14_3_2`. On PS4 02020005 packets use other numbers: PS4 numbers never name PC packets. |
| raw file | One decrypted packet under `packets/decrypted_raw/`: 9-byte header, body, cipher padding. |
| pattern | An ImHex pattern that decodes a packet or a resource file. `packets/patterns/03040008/<packet name>-pattern.cpp` holds one per packet of client 03040008. |
| fit | The flag `fits` a pattern exports: the decode ends within the last 15 bytes of the file, and reading past the end fails the decode. A fit is weak evidence: it does not prove field widths when the slack exceeds a field. |
| slack | The bytes left after a decode, exported as `paddingSize`. In a raw file they are cipher block padding. |
| nNetMsg | The RPC payload (`cNetMsg*` messages) carried by the lobby and party binary packets, decoded by `packets/patterns/03040008/include/nNetMsg.hexpat`. |
| annotated dump | The Arrowgene CLI's text dump of one stream under `packets/decrypted_annotated/`, decoded with the server emulator's C# structures. |
| stream | One TCP stream of a capture, stored as YAML under `packets/encrypted_streams/`. Its folder names under `packets/decrypted_raw/` and `packets/decrypted_json/` end in `tcp-stream-<n>`. |
| report label | A short name such as `T003` or `P11a` for an evidence report under `specs/`, written in a code span. [Packet ids](packet-ids.md#report-labels) holds the key. |
| CData | The prefix of the shared wire structures (`CDataCommonU32`), as PS4 02020005 DWARF names them. |

## Evidence marks

A decoded field or layout carries one mark, in a comment of its pattern.

| Mark | Meaning |
| --- | --- |
| `V` | Verified: read in code, for client 03040008 the PC code. A layout the PC reader proves is `V` even when its field names are guesses. |
| `I (<basis>)` | Inferred, with the basis stated: code shape, capture fit plus value correlation, extractor data, a PS4 structure on the same path. |
| `G (<basis>)` | Guess: a server lead alone (`G (lead)`), capture shape alone, or a name from context. |
| `open` | Left unknown: the field keeps its `unk_*` name, and any leads stay in the comment. |

A lead is a name or layout from the server emulator (Arrowgene). It is a candidate only, since its sizes and order may be wrong.

## Disassembly and transfer

| Term | Meaning |
| --- | --- |
| tier 0 | The first match rule of the PC 03040008 handler annotation: a handler-table entry whose function references exactly one `cSeed*Connection::OnPacket_*` string takes that string as its name. It needs the PC database alone. `research/03040008/ida-transfer/README.md` has the rules. |
| private copy | A copy of an IDA database made by `research/ida/private-copy.sh`, the only form the hook `tools/hooks/guard_ida.py` lets ida-mcp open. |

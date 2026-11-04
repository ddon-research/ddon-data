# Conventions

The names and file formats this repository uses, for anyone adding a file or reading one by its name. How to write a page is on the [writing contract](documentation-style.md); the packet pattern format has [its own page](packet-pattern-format.md).

## Names

| What | Form | Example |
| --- | --- | --- |
| Build | the client build number; always named when reading, writing or comparing | `03040008`, `02030004`, `PS4_02020005` |
| Resource class | the `r<Name>` prefix; one file extension maps to one class | `rItemList`, `rLayout` |
| Enum | its DWARF name | `rItemList_ITEM_CATEGORY` |
| Resource pattern | `r<ResourceType>-pattern.cpp` | `research/03040008/rLandInfo-pattern.cpp` |
| Packet pattern | `<packet name>-pattern.cpp` | `packets/patterns/03040008/S2C_WARP_WARP_RES-pattern.cpp` |
| Summary CSV | `<build>-<type>.csv` | `client/03040008-headers.csv` |
| Client patch | `<date>_<name>.r2` with a `.json` beside it | [Client patches](client-patches.md) |
| Spec Kit feature | `specs/<NNN>-<slug>/` | `specs/009-docs-structure/` |
| Commit subject | short, imperative, sentence case, no prefix | `Fix EST param parsing order` |

## File formats

| What | Form |
| --- | --- |
| ImHex resource pattern | enums from debug symbols; `#pragma pattern_limit` for large files; the structure follows the binary layout exactly |
| Hex dump | `00000000: 0100 0000 ....`, as `xxd` prints it |
| Position | `{X, Y, Z}` |
| Documentation | Markdown under `docs/` and in short READMEs; AsciiDoc only for `readme.adoc` and files outside readers cite, such as `binaries/PS4_02020005/elf-dumps/README.adoc` |
| Scripts | bash `.sh`; `research/knowledge-graph/scripts/*.ps1` stay until replaced |

## Keys across sources

The fields that join data from different sources are `NpcId`, `ItemId`, `QuestId` and the stage number.

## Packet id forms

A PC packet is named `group.id.sub`, as the [wire format](packet-wire-format.md) says. PS4 flat `u16` numbers are not the same numbers: [Packet decoding method](../explanation/packet-decoding-method.md).

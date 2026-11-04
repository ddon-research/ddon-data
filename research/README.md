# Research

This directory holds hand-written research on Dragon's Dogma Online, mostly on client 03040008: ImHex resource patterns, notes, research projects and external material, for anyone looking for evidence behind the data. The documentation map is [`docs/index.md`](../docs/index.md); the full list of what is here and who reads it is the [repository layout](../docs/reference/repository-layout.md#research).

| Path | Holds |
| --- | --- |
| `03040008/` | client 03040008: resource patterns `r<Type>-pattern.cpp`, `dumps/`, `xfs/`, `notes/`, `protections/`, `ida-transfer/` and the `flags/` project |
| `knowledge-graph/` | the evidence graph project, with its own documents |
| `ida/`, [`pharos/`](pharos/README.md) | IDA helpers and OOAnalyzer |
| [`scripts/`](scripts/README.md), [`prompts/`](prompts/README.md) | survey and validation scripts, LLM prompts |
| [`rng-race/`](rng-race/README.md), [`textures/`](textures/README.md) | lab tools on long-session captures, texture helpers |
| `external/`, [`external-references.md`](external-references.md), `external-references.jsonl` | community files as received; the outside repositories and documents the research relies on |
| `claude-vision-tokens.md`, `claude-vision/`, `PS4/`, `bbm/` | smaller notes |

Season 1 and Season 2 patterns are in the sibling repositories: `ddon-data-s1/research/01020003/` and `ddon-data-s2/research/02030004/`.

To decode a format, see [Choose a resource target](../docs/how-to/choose-a-resource-target.md) and [Decode a resource format](../docs/how-to/decode-a-resource-format.md).

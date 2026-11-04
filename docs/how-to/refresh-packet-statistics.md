# Refresh packet statistics

This page is for anyone who re-annotated streams of client 03040008 and wants the count files in `packets/` to follow. You run `packets/statistics-commands.sh`, which reads every dump in one pass. You need the dumps in `packets/decrypted_annotated/`, from [Re-annotate streams](reannotate-streams.md), and Git Bash, MSYS2 or WSL.

## Run it

```sh
packets/statistics-commands.sh [-k] [-f]
```

| Option | Effect |
| --- | --- |
| `-k`, `--keep-unique` | also writes the unique packet lists, `decrypted-tcp-streams-unique-*-packets.txt` |
| `-f`, `--freq-sort` | sorts count files by count, descending, then by key; the default is by key |
| `-h`, `--help` | prints the help |

`ANNOTATED_DIR` overrides the input folder (default `decrypted_annotated`). The script changes to its own directory, and replaces its output only after a successful run.

Success ends with a line on stderr that counts packets, packet types, types without structure and types failing to parse, then `Done (unique lists kept: 0; freq-sort: 0).`

## What it writes

Next to the script:

| File | Content |
| --- | --- |
| `decrypted-tcp-streams-unique-{c2s,s2c,c2l,l2c}-packets-count.txt` | `(group.id.sub) NAME,count` per packet type, by direction |
| `decrypted-tcp-streams-unique-unknown-packets-count.txt` | the same for a name without a known direction prefix; removed when empty |
| `packets-missing-structure-dumps.txt` | `NAME group.id.sub`: packet types without a C# structure (no `StructDump:` line) |
| `packets-structure-parse-failures.txt` | `(group.id.sub) NAME,count`: packets whose structure failed to parse; see [When a packet fails to parse](patch-the-arrowgene-cli.md#when-a-packet-fails-to-parse) |

## Read it with care

- Only packet header lines are counted.
- It refuses to run when a stream exists both unsplit and as `_N` pieces, since that would count it twice.
- The results mix CLI versions until every stream is re-exported with one build: packet names come from the CLI that produced each dump.

**Status:** not run for this page: the options and outputs are checked against the script, which rewrites tracked files.

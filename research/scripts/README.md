# Survey and validation scripts

This directory holds hand-written bash scripts that survey the client files and validate ImHex patterns, for anyone choosing or checking a resource format. The documentation map is [`docs/index.md`](../../docs/index.md).

| Script | What it does | Needs | Writes |
| --- | --- | --- | --- |
| `find-unsupported-extensions.sh [build]` | Lists the extensions of a build that ddon-extractor does not support; the default build is 02030004 | the `client/<build>-resources.csv` and `client/<build>.csv` summaries, under `/d` | its own temporary folder, removed on exit |
| `validate_pattern.sh <pattern> <file or dir> <fields>` | Runs a pattern over files and checks the named fields in its output | `imhex` on `PATH` | nothing in the repository |
| `dump-season1-headers.sh` | Prints the first 4 bytes of one file per extension, client 01010004 | `/d/DDON_01010004` | `season1headers.csv` in the working directory |
| `dump-season2-headers.sh` | The same, client 02030004 | `/d/DDON_02030004` | `season2headers.csv` in the working directory |
| `dump-season3-headers.sh` | The same, client 03040008 | `/d/DDON_03040008` | `season3headers.csv` in the working directory |
| `jq-npc-shops.sh` | `jq` queries over the NPC ledger JSON of client 03040008; run it from the repository root | `jq` | nothing |
| `jq-setinfo.sh` | `jq` queries over quest set info JSON of client 03040008; run it from the repository root | `jq` | nothing |

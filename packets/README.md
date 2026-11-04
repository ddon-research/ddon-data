# Packets

The network traffic of Dragon's Dogma Online captures, decoded for the PC client 03040008, and the tools that decode it. Its data is producer output, which is never edited by hand; its code and patterns are hand-authored.

## Data

Produced by the `D:\research\DDON-pcaps` toolchain and the scripts here. Never list or diff it unbounded: it holds hundreds of thousands of files.

| Path | Holds | Producer |
| --- | --- | --- |
| `encrypted_streams/` | cleaned TCP streams as YAML | [Decrypt a capture](../docs/how-to/decrypt-a-capture.md) |
| `keys/` | session keys per stream, and their script | [Decrypt a capture](../docs/how-to/decrypt-a-capture.md) |
| `decrypted_raw/` | one file per packet: header, body, cipher padding | [Re-annotate streams](../docs/how-to/reannotate-streams.md) |
| `decrypted_annotated/` | the Arrowgene CLI's text dump per stream, decoded with the server emulator's C# structures, which are leads | [Re-annotate streams](../docs/how-to/reannotate-streams.md) |
| `decrypted_json/` | one JSON file per packet, decoded with this repository's patterns checked against the PC client's code | [Export packets to JSON](../docs/how-to/export-packets-to-json.md) |
| `decrypted-tcp-streams-unique-*-packets-count.txt`, `packets-*.txt` | packet counts and C# structure gaps | [Refresh packet statistics](../docs/how-to/refresh-packet-statistics.md) |

## Hand-authored

| Path | Holds | Read |
| --- | --- | --- |
| `patterns/03040008/` | ImHex patterns and shared includes | [its README](patterns/03040008/README.md) |
| `plbatch/` | the export engine | [its README](plbatch/README.md) |
| `tools/` | `unk_correlate.py`, value correlation of unknown fields | [Name an unknown field](../docs/how-to/name-an-unknown-field.md) |
| `tests/` | the export selection tests, part of [the gate](../docs/how-to/run-the-gate.md) | |
| `wireshark/` | a postdissector and display filters | [its README](wireshark/README.md) |
| the `*.sh` files here | the scripts the pages above call | |

# ddon-ida-transfer

The scripts and manifest of the annotation transfer from PS4 02020005 onto the PC 03040008 IDA database: the fact extractors, the function repair, the matcher, the transfer rules and the apply script. Hand-written code; `manifest/` is its output, and the gitignored `dumps/` hold the extracted facts and logs (`dumps/MANIFEST.tsv` is committed). The result is the annotated database, `private-copy.sh pc-handlers`.

| To | Read |
| --- | --- |
| Query a database, the annotated one among them | [Query an IDA database read-only](../../../docs/how-to/query-ida-read-only.md) |
| Run a write safely | [Write to an IDA database](../../../docs/how-to/write-to-an-ida-database.md) |
| Re-run the transfer | [Transfer annotations from PS4 to PC](../../../docs/how-to/transfer-annotations-ps4-to-pc.md) |
| Look up flags, records, columns and rules | [IDA transfer tools](../../../docs/reference/ida-transfer-tools.md) |
| Understand why it works this way | [IDA transfer method](../../../docs/explanation/ida-transfer-method.md) |

Gates, from this directory: `uv run pytest`, `uv run ruff check --no-fix .`. The history is in `specs/007-pc-handler-annotation/`.

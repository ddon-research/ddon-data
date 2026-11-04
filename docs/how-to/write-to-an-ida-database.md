# Write to an IDA database

This page is for anyone who must change names, types or comments in a DDON IDA database (PC 03040008, PS4 02020005) and keep the change. The write runs as a headless batch job on a private copy, keeps its before-state and is checked afterwards. You need a [private copy](query-ida-read-only.md#2-make-a-private-copy) and a script that takes its arguments from `idc.ARGV`. Never write to an original `.i64`, by this route or any other: publish the result as a folder of its own.

## Rules

- **Never an original database.** Work on a copy under `ddon-data-<name>/`. The originals may be open in the IDA GUI.
- **Never through an ida-mcp worker.** `save_database` and `close_database` are denied, so a worker cannot save. Its writes live only in the unpacked `.id0`, `.id1`, `.nam` and `.til` beside the copy, and the packed `.i64` keeps its hash. When the worker is killed, the next open offers "Restore packed base (DISCARD unpacked)". In the run of 2026-11-03 that recorded this, none of 116 repairs survived (`specs/007-pc-handler-annotation/research/T004d-repair.md`).
- **Names, types and comments only**, unless the task authorizes more. Research never implies a byte patch.

## 1. Keep the before-state

```bash
IDAT="C:/Program Files/IDA Professional 9.5/idat.exe"
DB=D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-<name>/2022_01_29_DDO_DUMP_FIX.exe.i64
sha256sum "$DB"
cp -p "$DB" "${DB%.i64}.before-<step>.i64"
sha256sum "${DB%.i64}.before-<step>.i64"    # must equal the line above
```

The rollback copy is the undo of last resort. The folder must hold only `.i64` files before the run; any `.id0` means a worker holds it.

## 2. Write the script

Each script ends in one of two ways, and the difference decides whether anything is kept.

| The script | Ends with | The `.i64` |
| --- | --- | --- |
| writes, and succeeds | `idc.qexit(0)` | saved and packed: another hash and mtime |
| reads only, or dry-runs | `ida_loader.set_database_flag(ida_loader.DBFL_KILL)`, then `idc.qexit(0)` | byte-identical |
| fails | `DBFL_KILL`, then `idc.qexit(1)` | byte-identical |

Without `DBFL_KILL`, `qexit(0)` rewrites the file even when nothing was changed. `repair_functions.py`'s dry run does so (its size grew by 242 bytes on 2026-11-03), so its hash moves with no repair in it.

A script that writes also does this for every item:

1. Reads the before-state and appends an undo record to its log, flushed.
2. Writes one item.
3. Reads it back and compares. A mismatch is logged as failed, with both values and no retry.

It writes its log to `<OUT>.tmp` and renames it at the end, so a crash leaves the undo records written until then. Its last log line is a summary. `research/03040008/ida-transfer/apply_transfer.py` is the worked example; its function `batch` holds the exit logic.

## 3. Run it

```bash
export MSYS_NO_PATHCONV=1
"$IDAT" -A -L<log> "-S<script> <args>" "$DB"          # the script's dry run, if it has one
"$IDAT" -A -L<log> "-S<script> <args> --apply" "$DB"
```

`-A` runs without dialogs, `-L` names the log, and `-S` takes the script and its arguments as one argument. Run the dry run first and read its refusals before you apply anything.

## 4. Check the save

| Check | Success | Failure |
| --- | --- | --- |
| Exit status of `idat` | 0 | anything else: nothing was saved if the script's exit logic ran; go by the hash |
| `sha256sum "$DB"` and its mtime | changed after a write; unchanged after a read-only or dry run | an unchanged hash after a write: the writes are lost |
| The folder | only `.i64` files | `.id0` or `.id1` beside the copy: the job did not close |
| `rg -c -i "unpacked\|restore\|traceback" <log>` | no match (exit status 1) | a match: read that log |
| The log's last line | the script's summary, without `"error"` | an error summary or no summary |
| A second run of the write | every row already written | any write: the script is not idempotent, or the first run did not save |
| A read-only batch of a sample | the sample decompiles and reads as the rows say | stop and undo |

Compare the counts of user names, typed functions and local types before and after against the rows you wrote. Nothing else may have changed.

## 5. Undo

Prefer the script's own undo, which replays the log's undo records in reverse order and reads each back (for the transfer: [undo](transfer-annotations-ps4-to-pc.md#9-undo)). When that is not possible, restore the rollback copy:

```bash
mv "$DB" "${DB%.i64}.failed-<step>.i64"
cp -p "${DB%.i64}.before-<step>.i64" "$DB"
sha256sum "$DB"    # must equal the hash from step 1
```

Keep the failed copy until the reason is understood, and delete it then.

## 6. Publish

Only after the checks pass: copy the work copy with `cp -p` into a folder of its own beside the original, compare the hashes and record them. Never copy it over an original or a published folder. [Query an IDA database read-only](query-ida-read-only.md) then needs a target for it in `research/ida/private-copy.sh`.

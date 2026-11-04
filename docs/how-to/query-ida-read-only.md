# Query an IDA database read-only

This page is for anyone who wants to read a function, a type or a cross-reference from the DDON IDA databases of PC 03040008 or PS4 02020005 without any risk to them. You make a private copy, open it in the headless `ida` server or read it with a batch script, and delete the copy afterwards. You need IDA 9.5 at `C:\Program Files\IDA Professional 9.5` and the databases under `D:\research\DDON-binaries\IDA9.5\`. To change a database, see [Write to an IDA database](write-to-an-ida-database.md).

## 1. Choose the database

| Target | Build | Database, under `D:/research/DDON-binaries/IDA9.5/` | Choose it for |
| --- | --- | --- | --- |
| `pc` | PC 03040008 | `PC_DDON_03040008/2022_01_29_DDO_DUMP_FIX.exe.i64` | the live PC database |
| `pc-accepted` | PC 03040008 | the path `accepted_PC.path` of `PC_DDON_03040008/CURRENT-RECOVERY.json` gives | ddon-hook's accepted database; refused unless it lies inside `PC_DDON_03040008/` and its SHA-256 equals `accepted_PC.sha256` |
| `pc-handlers` | PC 03040008 | `PC_DDON_03040008/spec007-packet-handlers-20261103-wave2/2022_01_29_DDO_DUMP_FIX.exe.i64` | the annotated database: packet handler names, prototypes and types transferred from PS4 02020005 ([what they mean](../explanation/ida-transfer-method.md#what-the-results-mean-for-a-reader)) |
| `ps4` | PS4 02020005 | `PS4_DDON_02020005_2016_12_21/DDOORBIS.elf.i64` | the PS4 symbols and DWARF names |

Facts about the executable hold in all three PC databases; the [packet handler tables](../reference/packet-handler-tables.md) are one example.

## 2. Make a private copy

```bash
bash research/ida/private-copy.sh pc-handlers mylook
```

The script reads and hashes the original, copies it, compares the hashes and prints the copy's path. The name takes letters, digits, `_` and `-`, at most 64 characters, and starts with a letter or digit.

| Target | The copy goes to |
| --- | --- |
| `pc`, `ps4` | `ddon-data-<name>/` beside the original |
| `pc-accepted`, `pc-handlers` | `PC_DDON_03040008/ddon-data-<name>/`, not the folder that holds the original |

The copy always lies outside this repository.

A copy of the same name is **deleted and replaced**, with every other file in its folder. The script refuses only when a worker holds that copy open (`.id0`, `.id1`, `.nam` or `.til` beside it). So never reuse a name whose folder you still need; `ddon-data-007work` is one ([the transfer's work copy](transfer-annotations-ps4-to-pc.md#the-work-copy)).

Exit status 2 and a line starting `ERROR:` mean nothing usable was made.

## 3. Read it through the `ida` server

The `ida` server is ida-mcp, running headless. It is registered at local scope:

```bash
claude mcp add -s local ida -- uv run --no-dev --project <ida-mcp plugin cache dir> ida-mcp stdio --agent=claude
```

1. `open_database` with the path the script printed. The hook `tools/hooks/guard_ida.py` allows only `D:/research/DDON-binaries/IDA9.5/<PC or PS4 folder>/ddon-data-<name>/<file>.i64`; it refuses any other path, an original among them, and a call with no path.
2. Keep the `instance_id` of the answer and pass it on every `execute_python`. Call `reference(query)` before guessing an API shape.
3. Confirm the target before relying on an answer: `idc.get_idb_path()` must be your copy, and the image base must be `0x400000` on PC (32-bit) or `0` on PS4 (64-bit).

The database's stored input path says `...\IDA9.3\...`. That is metadata from the original import; go by `idc.get_idb_path()`.

The hook exists because the worker saves what it opens (on close, on shutdown, after `execute_python`), and the original may be open in the IDA GUI at the same time. Never rely on a worker to keep an edit: `save_database` and `close_database` are denied in `.claude/settings.json`, and [Write to an IDA database](write-to-an-ida-database.md) says what happens to it.

## 4. Or read it with a batch script

A batch job leaves the copy byte-identical when its script sets `DBFL_KILL`, and it needs no server.

```python
# look.py
import ida_auto, ida_loader, idc

ida_loader.set_database_flag(ida_loader.DBFL_KILL)  # discard the session: the packed .i64 stays as it was
ida_auto.auto_wait()
print("db", idc.get_idb_path())
idc.qexit(0)
```

```bash
MSYS_NO_PATHCONV=1 "C:/Program Files/IDA Professional 9.5/idat.exe" -A -Llook.log "-Slook.py" <private copy .i64>
```

The output is in the log. Compare `sha256sum` of the copy before and after: an equal hash is the proof that nothing was saved. `research/03040008/ida-transfer/extract_ida.py` runs this way too ([command](transfer-annotations-ps4-to-pc.md#2-extract-the-facts)).

**Status:** not run as written here; `extract_ida.py` uses the same three calls, and its runs of 2026-11-03 left the `.i64` hash unchanged (`specs/007-pc-handler-annotation/research/T004f-repair-batch.md`).

## 5. Delete the copy

When no worker holds it, the folder holds the `.i64` alone. Delete it:

```bash
rm -rf -- "D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-mylook"
```

A worker holds its copy until its server stops, because `close_database` is denied. Ending the session stops it. A folder that still holds `.id0` or `.id1` files after that comes from a killed worker: its unpacked files hold nothing you need on a read-only copy, and `rm -rf` of that one folder clears it. Check the path names `ddon-data-` before you run it.

## Other routes

- `ida-domain-scripting` runs headless idalib, but its `--save` copies its cached database over the original, and it reuses that cache after later GUI edits. Use it for other or throwaway binaries only.
- The raw exports `binaries/PS4_02020005/DDOORBIS_1.elf.c` and its siblings, and the [ELF dumps](../../binaries/PS4_02020005/elf-dumps/README.adoc), need no IDA. Prefer the server when you need cross-references or decompilation of a function.

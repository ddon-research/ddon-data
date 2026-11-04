# Transfer annotations from PS4 to PC

This page is for anyone who wants to re-run the transfer of packet subsystem names, prototypes, types and locals from PS4 02020005 onto the PC 03040008 database, or to extend it. The order is repair, extract, match, transfer, apply, verify. You need the rules of [Write to an IDA database](write-to-an-ida-database.md), IDA 9.5 and `uv`. Flags, columns and rules are in [IDA transfer tools](../reference/ida-transfer-tools.md); why the method is what it is, in [IDA transfer method](../explanation/ida-transfer-method.md). The result of the run on record is already published: to read it, use [the `pc-handlers` target](query-ida-read-only.md#1-choose-the-database) and stop here.

```bash
T=D:/ddon-data/research/03040008/ida-transfer
IDAT="C:/Program Files/IDA Professional 9.5/idat.exe"
DB=D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64
export MSYS_NO_PATHCONV=1
```

Run the `uv run` commands from `research/03040008/ida-transfer/`, and every `idat` command with `-A -L<log>` as below.

## The work copy

`apply_transfer.py` refuses a database whose path does not contain `ddon-data-007work` or `ddon-data-007smoke`, or whose input SHA-256 is not `f1c974d0e529d4bb7dc5f0953d37eea6bbb023f2667f9a1d3a3b878f4919fa20`.

**Decide before you make a copy.** `ddon-data-007work/` holds the work copy (equal to the published annotated database) and its rollback `...exe.before-W2.i64`. `private-copy.sh <target> 007work` deletes both. To try something, use `007smoke`:

```bash
bash research/ida/private-copy.sh pc-handlers 007smoke   # the annotated state: an apply finds every row already written
```

To repeat the run from its start, the base is ddon-hook's accepted database (`bash research/ida/private-copy.sh pc-accepted 007work`), SHA-256 `382e346e0b48b157e261119cf803c7b10d072b40ba3ae187a79291d640a58c0f` on 2026-11-03. Move what `ddon-data-007work/` holds aside first.

## 1. Repair the function starts

PC handler callbacks and call targets that IDA did not make functions cannot be matched, so they are repaired on the work copy first.

```bash
"$IDAT" -A -L$T/dumps/logs/repair-dryrun.log "-S$T/repair_functions.py $T/dumps/repair-dryrun.jsonl" $DB
"$IDAT" -A -L$T/dumps/logs/repair-apply.log  "-S$T/repair_functions.py $T/dumps/repair-apply.jsonl --apply" $DB
```

The script's dry run also re-saves the `.i64`. Read `by_status` and `by_check` in the last log line before you apply: `refused` rows are never forced, and each has its `check`. Success: `failed` is absent. The run on record ends with `{"by_status": {"already-ok": 1039, "refused": 1}, "call_targets": {"by_status": {"refused": 7, "repaired": 118}, ...}}` (2026-11-03, `dumps/logs/repair3-apply.log`; an earlier run had repaired the callbacks).

The extraction reads the repaired state, so the order is repair, then extract. Extract once before it if you want the list of roots that are not function starts: the `missing_root` records.

## 2. Extract the facts

Read-only: both scripts set `DBFL_KILL`. PC from the work copy, PS4 from a private copy of its own.

```bash
P=$(bash research/ida/private-copy.sh ps4 myps4)
"$IDAT" -A -L$T/dumps/logs/pc-ida.log  "-S$T/extract_ida.py $T/dumps/pc-ida.jsonl pc"  $DB
"$IDAT" -A -L$T/dumps/logs/ps4-ida.log "-S$T/extract_ida.py $T/dumps/ps4-ida.jsonl ps4" $P
uv run python extract_dwarf.py --ida-dump dumps/ps4-ida.jsonl
uv run python manifest.py
```

- `extract_dwarf.py` reads the staged `binaries/PS4_02020005/elf-dumps/.staging/input/DDOORBIS.elf` and refuses it unless its SHA-256 equals the header of `binaries/PS4_02020005/elf-dumps/dwarf/inline-chains.orbis-addr2line.tsv`. It takes minutes.
- `manifest.py` rewrites `dumps/MANIFEST.tsv`. The matcher and the transfer refuse a dump whose hash differs from it.
- Success: the `.i64` hash is unchanged, the last log line has `"table_ok": true` on PC, and `missing_roots` is what the repair left.

The dumps are gitignored, and a committed `dumps/MANIFEST.tsv` names the set a committed manifest came from.

## 3. Match

```bash
uv run python match.py
```

It rewrites `manifest/*.tsv` and exits 1 on a wrong pair in the holdout or on an acceptance in the shuffled-partner control. Output is identical on a rerun. Success: exit status 0, and the `precision rng` and `control rng` lines print `wrong 0` and `accepted {}`.

Read `manifest/crosscheck.tsv` next: its disagreements with earlier work are findings to settle, not noise.

## 4. Transfer

The whole-type pass reads dumps taken **before** its rows were applied:

```bash
uv run python transfer.py      # rewrites manifest/transfer/*; about 5 s
```

It exits 2 when `pairs.tsv` differs from the matcher's run on these dumps, or when a row of `--decisions` (default `specs/007-pc-handler-annotation/research/T009-decisions.tsv`) finds no conflict. Dumps taken after the apply fail in that way: `decision for name 0x7da410: the row is not a conflict (action equal)` is what the committed dumps give. Read `conflict` rows in `manifest/transfer/skipped.tsv` and settle each in a decisions file, with evidence.

Apply it (steps 6 to 8), and re-extract as in step 2 before the partial-type pass, which reads dumps taken **after** that apply:

```bash
uv run python transfer.py --wave2     # rewrites manifest/transfer/wave2/*; about 8 s
```

Success: exit status 0 and unchanged output on a rerun. `--out` writes elsewhere when you only want to compare.

## 5. Smoke-test a changed apply script

After any change to `apply_transfer.py`, run it on `ddon-data-007smoke` with a limit, before a whole manifest. Its IDA adapter has no unit test: the tests use a fake.

```bash
SMOKE=${DB/ddon-data-007work/ddon-data-007smoke}
mkdir -p "$(dirname "$SMOKE")"
cp -p ${DB%.i64}.before-W2.i64 "$SMOKE"   # the state before the partial types, so their rows are unwritten
"$IDAT" -A -L$T/dumps/logs/smoke.log "-S$T/apply_transfer.py $T/manifest/transfer/wave2 $T/dumps/smoke.jsonl --apply --limit-types 5 --limit-locals 10" "$SMOKE"
```

Then a dry run first if you like, `--verify` with the same limits, and `--undo`; each must end clean. Delete the folder afterwards. Each limit counts rows of `types.h` and `locals.tsv`; `--limit-types` and `--limit-locals` work on a manifest of the partial-type pass only.

## 6. Dry run

```bash
cp -p $DB ${DB%.i64}.before-<step>.i64
"$IDAT" -A -L$T/dumps/logs/apply-dryrun.log "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply-dryrun.jsonl" $DB
```

Use `$T/manifest/transfer/wave2` for the partial-type pass. The dry run ends with `DBFL_KILL`, so the hash does not move. Read `refused` rows and stop on any you cannot explain. A forward declaration or layout that differs is usually a comparison rule to fix, not a row to force. The log's last line for the run on record:

```text
apply_transfer summary: {"counts_after": {"local_types": 965, "names": 52148, "typed_functions": 1464}, "mode": "dry-run", "steps": {"locals": {"refused": 1, "would-set": 23}, "types": {"already": 21, "would-define": 48}}}
```

## 7. Apply

```bash
"$IDAT" -A -L$T/dumps/logs/apply.log   "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply.jsonl --apply" $DB
"$IDAT" -A -L$T/dumps/logs/apply-2.log "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply-2.jsonl --apply" $DB
```

Success: no `failed` in `steps`, and the second apply finds every row `already` (the refused rows stay refused). The second apply saves, so the hash moves once more with no writes in it. Keep `apply.jsonl`: it holds the undo records and is the log `--verify` and `--undo` take.

## 8. Verify

```bash
"$IDAT" -A -L$T/dumps/logs/apply-verify.log "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply-verify.jsonl --verify --apply-log $T/dumps/apply.jsonl" $DB
```

Success: `"counts_ok": true` and only `ok` in `steps`, as in this line of the run on record:

```text
apply_transfer summary: {"counts_ok": true, "mode": "verify", "steps": {"locals": {"ok": 23}, "types": {"ok": 69}}}
```

The manifest's hash must be the one in the apply log's header, so regenerating it means applying again. Then do by hand what `--verify` cannot:

1. Re-extract the PC database to a file of its own (`pc-ida-applied.jsonl`), and compare it with the dump before the apply: the changes must equal the rows written.
2. Decompile a stratified sample in a read-only batch, and read it. In a handler with a retyped `packet` local, the local spans its type, no other stack variable overlaps it and no line says `OVERLAPPED`.
3. Have someone re-derive a sample of pairs and types from the disassembly, independently.
4. Publish as in [Write to an IDA database](write-to-an-ida-database.md#6-publish).

## 9. Undo

```bash
"$IDAT" -A -L$T/dumps/logs/apply-undo.log "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply-undo.jsonl --undo $T/dumps/apply.jsonl" $DB
```

Every record must read `restored`. It replays the undo records in reverse order and saves. It deletes a type the apply created and clears a name that was default. A forward declaration that was defined is deleted and declared again, so the count of local type ordinals grows by one per type even though the state is restored.

To go further back, or when the undo fails, restore the rollback copy ([how](write-to-an-ida-database.md#5-undo)). `repair_functions.py` has no undo mode: its `undo` records are data for a manual repair, so a repair is undone only by the rollback copy.

## What was run for this page

On 2026-11-04, at the commit of this page, against the committed manifest and the local dumps:

| Command | Result |
| --- | --- |
| `uv run python match.py --help`, `transfer.py --help`, `extract_dwarf.py --help` | flags as above |
| `uv run python match.py --out <scratch>` | exit status 0; all 8 files equal `manifest/` |
| `uv run python transfer.py --wave2 --out <scratch>` | exit status 0; the 7 `.tsv` files compared equal `manifest/transfer/wave2/` |
| `uv run python transfer.py --no-holdout --out <scratch>` | exit status 2: the message quoted in step 4, as designed for these dumps |
| `parse_batch_args` of `apply_transfer.py` and `repair_functions.py`, called on the argument lists above | parsed into the modes above; `--verify` without `--apply-log`, `--apply-log` without `--verify`, and `--apply --verify` refused |

**Status:** not run for this page: `extract_ida.py`, `extract_dwarf.py`, `manifest.py`, `repair_functions.py` and `apply_transfer.py` in any mode, since they would rewrite the dumps or need a database. Their commands are those of `specs/007-pc-handler-annotation/research/T004f-repair-batch.md`, `T005g-extract-v4.md` and `W2-T013e-reapply.md` there.

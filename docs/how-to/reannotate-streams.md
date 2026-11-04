# Re-annotate streams

This page is for anyone who rebuilt the Arrowgene CLI, or changed a C# structure, and needs the annotated dumps or raw files of client 03040008 to follow. You run the CLI over `packets/encrypted_streams/` with the known keys, split the large dumps and export the raw files. You need the [patched CLI](patch-the-arrowgene-cli.md), Git Bash and `packets/keys/keys-all-in-one.csv`. To decrypt a capture from the start, see [Decrypt a capture](decrypt-a-capture.md).

## Annotate in parallel

`packets/decrypt-annotate-streams.sh` runs one CLI per `*.yaml` in `STREAM_DIR`, with the key that `KEYS_FILE` holds for that stream. It needs GNU `awk` (the three-argument `match`), `find`, `sed` and `head`.

1. Change to `packets/`: the script does not change directory, and its defaults are relative.

   ```sh
   cd packets
   ./decrypt-annotate-streams.sh
   ```

   To tune it: `MAX_JOBS=6 ./decrypt-annotate-streams.sh`.

2. Read the per-job output. Each job prints, with its log between two marker lines (the first 2000 lines of it):

   ```text
   ==== JOB DONE: stream85_tcp11 (exit 0) ====
   file=...
   streamName=stream85, tcpStreamNumber=11
   ```

3. **Check every `JOB DONE` line.** The script exits 0 even when a job fails. Exit 2 means no key for that stream. Parallel CLI instances share one log file (`bin/Debug/net10.0/Logs/<date>.log.txt`), so a job that loses the race crashes with `IOException ... being used by another process` and exit code 127, without output. Rerun failed streams with `MAX_JOBS=1`.

The CLI writes `<stream>.yaml.annotated.txt` beside its input, under `encrypted_streams/`.

To re-export a subset, hard-link the YAMLs into a short-named folder and set `STREAM_DIR` to it.

### Variables

| Variable | Default | Meaning |
| --- | --- | --- |
| `CLI_PATH` | the build under `C:\Users\morph\Documents\GitHub\Sehkah\Arrowgene.DragonsDogmaOnline.Upstream` | `Arrowgene.Ddon.Cli.exe` |
| `KEYS_FILE` | `keys/keys-all-in-one.csv` | stream keys |
| `STREAM_DIR` | `encrypted_streams` | input YAMLs |
| `MAX_JOBS` | the logical CPU count | concurrent CLI processes |

If the CLI is I/O-bound, a higher `MAX_JOBS` can help; if CPU-bound, use the number of physical cores or fewer. Test with small values first, and lower it if the machine becomes unresponsive.

Per-job logs live in a `mktemp -d` folder that the script removes on exit. To keep them, set `tmpdir` to a permanent location in a copy of the script and remove the `trap` that deletes it.

## Split large dumps

`packets/decrypted_annotated/` keeps files under 50 MiB. Split a larger dump at packet boundaries, from `packets/`:

```sh
./split-annotated.sh [--force] encrypted_streams/<stream>.yaml.annotated.txt [decrypted_annotated] [max_bytes]
```

It writes `<stream>_1.yaml.annotated.txt` ... `<stream>_N.yaml.annotated.txt`, or the unsuffixed name if the dump fits, and never cuts a packet in two. It verifies with `cmp` that concatenating the pieces reproduces the input before replacing anything. `--force` replaces the stream's pieces; without it, the script refuses when pieces exist. `max_bytes` defaults to 52428800.

## Export raw files

`packets/decrypt-export-streams.sh` decrypts every stream, or the ones given, and writes one file per packet to `decrypted_raw/<stream>/`, under the [names the format page lists](../reference/packet-pattern-format.md#raw-file-names):

```sh
packets/decrypt-export-streams.sh [stream.yaml ...]
```

- It takes the same `CLI_PATH`, `KEYS_FILE` and `STREAM_DIR`, plus `OUT_DIR` (default `decrypted_raw`), and changes to its own directory.
- Streams run one at a time, because of the shared log file. Each YAML is copied to a temporary folder first, because the CLI writes `<yaml>.annotated.txt` beside its input, so `packets/encrypted_streams/` is never written to.
- A stream whose output folder exists is refused, so exports of different builds never mix. Move the folder away first, or export to another `OUT_DIR` and compare.
- Success is `ok   <stream>` per stream and `Done: <n> exported, 0 failed`. The exit status is 1 when a stream failed.

After a change to the raw files, [export their JSON](export-packets-to-json.md).

**Status:** not run: the annotate and raw export steps, read against their scripts, since they rewrite tracked data. `split-annotated.sh` ran on 2026-11-04 on a copy of one dump, into a scratch folder.

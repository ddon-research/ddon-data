# Decrypt a capture

This page is for anyone with a DDON `.pcapng` of client 03040008 who wants its session keys and decrypted streams. You run `packets/keys/decrypt-pcapng-streams-all-in-one.sh`, which finds the session key of each stream by brute force and decrypts it. You need the tools below. To reprocess streams whose keys are known, see [Re-annotate streams](reannotate-streams.md).

## What you need

The script checks the first three and stops with an error when one is missing.

| Tool | Where |
| --- | --- |
| `tshark` | on `PATH` |
| `ddon_common_key_bruteforce` | in the working directory: [fork](https://github.com/ddon-research/ddon_common_key_bruteforce) of [the original](https://github.com/Andoryuuta/ddon_common_key_bruteforce) |
| `Arrowgene.Ddon.Cli` | in the working directory: [Patch the Arrowgene CLI](patch-the-arrowgene-cli.md) |
| `awk`, `perl`, `grep`, `sort`, `tee` | on `PATH`, not checked by the script |

## Run it

Change to the folder that holds the two executables, since the script calls them as `./ddon_common_key_bruteforce` and `./Arrowgene.Ddon.Cli`. Then give it a capture or a folder of `*.pcapng`, and an output folder (default `decrypted`):

```sh
bash /d/ddon-data/packets/keys/decrypt-pcapng-streams-all-in-one.sh <capture.pcapng|folder> [output_dir]
```

For each capture and each of the three stream kinds it does this:

1. **Find the first packet of each TCP stream** with a `tshark` filter:

   | Kind | Filter | Expected plaintext |
   | --- | --- | --- |
   | `login` | `tcp && tcp.port eq 52100 && tcp.window_size eq 130560 && data.len eq 98 && data contains 00:60` | `0100000234000000` |
   | `game-select` | `tcp && tcp.port eq 52000 && tcp.window_size eq 130560 && data.len eq 98 && data contains 00:60` | `2C00000234000000` |
   | `game` | `tcp && tcp.port eq 52000 && tcp.window_size eq 65792 && data.len eq 98 && data contains 00:60` | `2C00000234000000` |

   It keeps the first packet per stream, and takes the first 32 hex characters after the `0060` size field.
2. **Search the key:** `ddon_common_key_bruteforce <data> <plaintext> --end_second 40 --key_depth 15000`. Most keys of a first session turn up within 50 s; the deepest key known is about 7k.
3. **Export the stream as YAML** to `<output_dir>/<capture>_tcp-stream-<n>.yaml` with `tshark -2 -q -z follow,tcp,yaml,<n>`.
4. **Decrypt it:** `./Arrowgene.Ddon.Cli packet <yaml> <key>`, which writes `<yaml>.annotated.txt` beside its input.
5. **Log the key** to `<output_dir>/<capture>-keys.csv`, or `keys-all-in-one.csv` for a folder.

## Read the result

Each row of the key file has these columns:

```text
#stream_file,packet_series_counter,packet_number,packet_time_relative,packet_tcp_stream,packet_header_data,packet_type,decryption_key_milliseconds,decryption_key_depth,decryption_key
```

A row with empty last columns means no key was found within the bounds, and its stream was neither exported nor decrypted. The filters are empirical and false positives are possible: review ambiguous streams by hand ([Inspect captures in Wireshark](inspect-captures-in-wireshark.md) has further filters).

The script overwrites the key file of its output folder. The repository's record is `packets/keys/keys-all-in-one.csv`, which outside readers use, so write to another folder and merge. The manual steps are in `packets/keys/dump-and-decrypt-packet-headers-manual-process.sh`.

**Status:** not run for this page: the commands above are checked against the script, and no capture was decrypted with them.

# imhex-export CLI

The options, filter forms, environment and summary line of `packets/imhex-export.sh`, which decodes raw files of client 03040008 with a pattern and writes one JSON file per packet. For the steps, see [Export packets to JSON](../how-to/export-packets-to-json.md). Running it without arguments prints the same options from its header comment.

## Usage

```text
packets/imhex-export.sh [--force] [--json-nonfinite=keep|null] <packet-filter> <pattern-name> [jobs]
```

| Argument | Meaning |
| --- | --- |
| `<packet-filter>` | What to select in `decrypted_raw/<stream>/`, files only: see below. It must not be empty or hold `/`. |
| `<pattern-name>` | The pattern `patterns/03040008/<name>-pattern.cpp`, without the suffix. It must not hold `/`. |
| `[jobs]` | Parallel worker processes. Default: `nproc` with plbatch, `nproc / 2` with ImHex. |
| `--force` | Re-export packets whose JSON already exists. |
| `--json-nonfinite=null` | plbatch only, its default: a NaN or Inf float is written as `null`. |
| `--json-nonfinite=keep` | plbatch only: keeps the formatter's bare `nan`/`inf`, byte-identical to ImHex and not valid JSON, so `jq` rejects it. The ImHex path always keeps them, and refuses `--json-nonfinite=null`. |

The script changes to its own directory first, so it works from any working directory, and its relative defaults below are under `packets/`.

## Filter forms

| Form | Selects |
| --- | --- |
| `@` | The id the pattern declares in `// packet-id:`. With `// packet-select: <name>`, only the files of that id whose name holds `_<name>_`; with `// packet-size: <bytes>`, only files of that size. |
| `<group>.<id>.<sub>`, for example `35.5.16` | Files whose name ends in `.35_5_16`. |
| anything else | A substring of the file names; a matching directory name selects nothing. |

`@` refuses an id that login-server (`C2L_`/`L2C_`) and game-server (`C2S_`/`S2C_`) files share, unless the pattern names its packet with `// packet-select:`, since a shorter layout would still fit (`R2 F2`; test: `packets/tests/imhex-export-select.sh`).

The id forms do not depend on the packet name in the file name, which the CLI took from the server's `PacketId` at export time: an outdated or "Unknown" name cannot hide packets from them.

## Environment

| Variable | Default | Meaning |
| --- | --- | --- |
| `PLBATCH` | `plbatch/build/bin/plbatch.exe` if built | plbatch executable; `PLBATCH=none` forces the ImHex path |
| `IMHEX` | `imhex` on `PATH`, then the portable install in the script | ImHex executable; with plbatch, its `includes/` folder supplies the std library |
| `IMHEX_INCLUDES` | `<dir of IMHEX>/includes` | std library folder for plbatch |
| `RAW_DIR` | `decrypted_raw` | input root |
| `JSON_DIR` | `decrypted_json` | output root |
| `PATTERN_DIR` | `patterns/03040008` | pattern directory; its `include/` folder, when present, is passed with `-I` |

## Engines

The two engines give the same JSON byte for byte, except that ImHex percent-encodes string bytes outside `[A-Za-z0-9-_.~]`.

| Engine | When | How it runs |
| --- | --- | --- |
| plbatch | default when built ([Build plbatch](../how-to/build-plbatch.md)): PatternLanguage master `300d7388`, UTF-8 strings | The file list is dealt into `jobs` shards, one process per shard, with no process started per packet. Every output is parsed with nlohmann json. |
| ImHex | fallback: `imhex --pl format`, ImHex 1.38.1, which embeds PatternLanguage `fb6ea061` | One process per packet, about 0.25-0.5 s each for process start and plugin init. It does not validate its output. The default is `nproc / 2` jobs, since every MSYS process creation slows down as more jobs fork at once. |

Error logs (`.json.err`) differ in wording between the two; plbatch adds the stack trace.

## Output

- `decrypted_json/<stream>/<packet-file>.json`, one file per packet.
- A failed packet writes `<packet-file>.json.err` and removes any `<packet-file>.json` an earlier run left, so counts over `packets/decrypted_json/` never mix runs.
- Output paths must stay under 260 characters, the limit of the Windows build; a longer one fails with a `.json.err`.

## Summary line

The last line reads:

```text
Done: <n> exported, <n> skipped, <n> failed; <n> nonfinite (null), <n> badjson
```

On the ImHex path the part after `;` reads `JSON not validated (ImHex path)`.

| Count | Meaning |
| --- | --- |
| `exported` | packets written, the nonfinite ones included |
| `skipped` | JSON exists and no `--force` |
| `failed` | packets that failed; each leaves a `.json.err` |
| `nonfinite` | outputs holding a NaN or infinite float, written as `null`, or bare under `keep` |
| `badjson` | output invalid for any other reason, a failure |

The exit status is 0 when nothing failed or was badjson, 1 when something was, and 2 on a usage or setup error.

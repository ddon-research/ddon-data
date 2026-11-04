# plbatch CLI

The flags, input, output lines and exit codes of plbatch, the batch driver for ImHex patterns, for anyone calling it directly or reading a log of `packets/imhex-export.sh`. To build it, see [Build plbatch](../how-to/build-plbatch.md).

## Usage

```text
plbatch --pattern P [-I DIR]... --in-root IN --out-root OUT [--force] [--time] [--json-nonfinite=keep|null] < list
```

| Flag | Meaning |
| --- | --- |
| `--pattern P` | the pattern file |
| `-I DIR` | an include path: pass the ImHex std library (`<imhex>/includes`, which `imhex --pl` adds by itself) and the pattern includes (`packets/patterns/03040008/include`) |
| `--in-root IN` | the root of the input paths |
| `--out-root OUT` | the root of the outputs |
| `--force` | re-export a file whose JSON exists |
| `--time` | also parses each pattern once more on its own and prints parse, execute and format totals to stderr; it doubles the parse work, so it is for measurement only |
| `--json-nonfinite=keep` | the default: a file with NaN or Inf floats is written unchanged, byte-identical to ImHex |
| `--json-nonfinite=null` | a file with NaN or Inf floats is written with `null` in their place |

`list` on stdin holds newline-separated paths relative to `IN`.

## Output files

- For each `rel`: `OUT/rel.json`, written to `OUT/rel.json.tmp.<pid>` and renamed into place.
- On failure: no JSON, and `OUT/rel.json.err` with the compile or evaluation error and the stack trace. Paths of 260 characters or more fail like the export script's guard.
- On failure, also under `--force`, an `OUT/rel.json` from an earlier run is removed, so counts never mix runs.
- Every output is parsed with nlohmann json (the copy PatternLanguage bundles). The formatter prints NaN and Inf floats as bare `nan`/`inf`, which is not JSON.

## Stdout lines

One line per file:

| Line | Meaning |
| --- | --- |
| `ok   rel` | written |
| `ok-nan rel` | written with bare `nan`/`inf`, under `keep` |
| `ok-null rel` | written with `null` in their place, under `null` |
| `skip rel` | JSON exists, no `--force` |
| `badjson rel (see <err>)` | output invalid for another reason: a failure with a `.json.err`, no JSON |
| `FAIL rel (see <err>)` | compile or evaluation failure |

## Exit status

| Code | Meaning |
| --- | --- |
| 0 | nothing failed |
| 1 | a file failed or was badjson |
| 2 | a usage error |

## What it does per file

The driver does what ImHex does per run: `reset()`, dangerous functions refused, include paths, `setDataSource` over the file in memory, `executeString(pattern, patternPath)`, then `FormatterJson::format()`. Nothing calls `std::exit` per file.

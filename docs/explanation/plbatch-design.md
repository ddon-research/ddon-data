# plbatch design

Why the packet export of client 03040008 runs through a batch driver of its own and not `imhex --pl format`, why that driver pins a PatternLanguage commit different from ImHex's, and what it leaves on the table. For anyone changing the export or doubting its output. The flags are in the [plbatch CLI](../reference/plbatch-cli.md) reference; the measurements are on [Status](../reference/status.md#export-engine-measured-2026-11-01). The background report is `specs/005-netmsg-patterns/research/P7-imhex-as-library.md`.

## Why a batch driver

The packet tree has on the order of a hundred thousand small files, and each is one run of a pattern. `imhex --pl format` costs hundreds of milliseconds of process start and plugin init per packet, before anything is decoded, and a shell script around it adds several MSYS process creations per packet. That rate turns a re-export into a long job, and re-exports are routine: every change to an include calls for one.

plbatch links PatternLanguage (`libpl`, `libpl-gen`) directly, keeps one runtime per process and never forks per file. It writes one JSON file per input, as `imhex --pl format` does. The export scales by running one process per shard.

## Why the output can be trusted

A peer would ask whether a second driver changes what the patterns mean. The check is byte comparison: the same patterns and includes, through `imhex.exe` and through plbatch, compared output by output at the same PatternLanguage commit, with no difference in the sample and a truncated packet failing in both. Only the `.err` text differs, since plbatch adds the stack trace.

## Why this pin

ImHex 1.38.1 embeds PatternLanguage `fb6ea061` (tag `ImHex-v1.38.1`), which writes every string byte outside `[A-Za-z0-9-_.~]` as `%XX`, so `"Rumi Amestris"` comes out as `"Rumi%20Amestris"`. Upstream `f910448` and `5764389` (`generators/include/pl/formatters/formatter_json.hpp`) write valid UTF-8 as is, with the JSON escapes `\"`, `\\`, `\b`, `\f`, `\n`, `\r`, `\t`, `\u00XX` for other control characters and 0x7F, a surrogate pair above U+FFFF, and `\u00XX` for each byte of invalid UTF-8. That last form is ambiguous with the real code point U+00XX.

A JSON tree that readers can use as it stands is worth that ambiguity, so plbatch pins master `300d7388475dd7ffd04239dfc889b72fe08bae18`. The cost is that the two engines agree byte for byte only on files without string bytes outside that set: the ImHex fallback of `packets/imhex-export.sh` percent-encodes.

The pin brings other changes since `fb6ea061` that touch evaluation or output. A comparison of the packet re-export, on a sample per pattern, showed no difference other than the string encoding:

| Commit | Change |
| --- | --- |
| `27220d5`, `3aeccbb` | transform functions in the formatter: a value whose `getValue()` throws prints `"<error: ...>"` |
| `2751a95` | `std::mem` reads default to the current section |
| `ca1ab93` | string display values trim trailing NULs: the ImHex view only, not `toString()` |
| `cf44545` | an optional string codec and `#pragma encoding`: none is set, so raw bytes as before |
| `075eaf9` | `\u`/`\U` escapes in pattern source give a code point: the packet patterns use none |
| | `executeString` returns an exit code (0 = success) instead of `bool` |

## Why it parses per file

Parsing dominates the cost per file: tens of milliseconds to preprocess, parse and validate the large `nNetMsg.hexpat` and its std imports, against under a millisecond of evaluation. Parsing once and evaluating many (`parseString` once, `evaluator->evaluate(ast)` per file) would be some twenty-five times faster per process. It is not done: it uses PatternLanguage internals, and must replicate the pragma and data-source setup that `executeString` and `reset()` do. Shards give enough speed without that risk, and the per-file path stays the one ImHex itself runs.

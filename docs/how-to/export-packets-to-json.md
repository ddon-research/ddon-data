# Export packets to JSON

This page is for anyone who changed a packet pattern of client 03040008 and needs its JSON under `packets/decrypted_json/` to follow. You run `packets/imhex-export.sh` and read its summary. You need plbatch built ([Build plbatch](build-plbatch.md)), or ImHex as a fallback, and the raw files under `packets/decrypted_raw/`. The options are in the [imhex-export CLI](../reference/imhex-export-cli.md) reference.

## Export one pattern

1. Run the script from anywhere; it changes to its own directory. Use `@` so that the pattern's own `// packet-id:` line selects the files:

   ```sh
   packets/imhex-export.sh --force @ S2C_CONTEXT_GET_SET_CONTEXT_RES
   ```

   Without `--force`, a packet whose JSON exists is skipped.

2. Read the last line. Success has `0 failed` and `0 badjson`, and the exit status is 0:

   ```text
   Done: <n> exported, <n> skipped, 0 failed; 0 nonfinite (null), 0 badjson
   ```

3. Check the fit of the packets you touched, with the same name:

   ```sh
   fd -d 2 -g '*_S2C_CONTEXT_GET_SET_CONTEXT_RES_*.json' packets/decrypted_json -X jq -r .packet.fits | sort | uniq -c
   ```

   Success is a single line that says `true`. A [fit](../reference/glossary.md#packets) is weak evidence ([what a fit proves](../reference/packet-pattern-format.md#exported-checks)).

4. Correct the row of the packet in [Packet ids](../reference/packet-ids.md):

   ```sh
   python -X utf8 tools/docs_check.py --packet-counts --write
   ```

## When a packet fails

A failed packet leaves `<file>.json.err` beside where its JSON would be, and its earlier JSON is removed. The `.err` holds the compile or evaluation error. Reading past the end of the file fails the decode.

| Symptom | Cause | Fix |
| --- | --- | --- |
| `failed` with `path too long` in the `.err` | an output path of 260 characters or more | use a shorter `JSON_DIR` |
| `@` refuses the id | login-server and game-server files share it | add `// packet-select: <name>` to the pattern ([format](../reference/packet-pattern-format.md#header-comment)) |
| `badjson` above 0 | output invalid for a reason other than NaN or Inf | read the `.err`; the file has no JSON |
| `nonfinite` above 0 | a NaN or Inf float | expected in the 65 group-35 packets the [format page](../reference/packet-pattern-format.md#json-conventions) names; elsewhere suspect the layout |

## After changing an include

Re-export every pattern that includes the file, not only the one you worked on: a structure added to a shared include can clash with a pattern's local structure of the same name, and only a re-export shows it. [Packet pattern includes](../reference/packet-includes.md) lists the users, and this lists them from the source:

```sh
rg -l '#include "Warp.hexpat"' packets/patterns/03040008
```

## Use the fallback engine

Set `PLBATCH=none` to run ImHex instead, with `IMHEX` if it is not on `PATH`. Its JSON differs from the committed export wherever a string holds a byte outside `[A-Za-z0-9-_.~]`, so use it for a comparison, not to replace the tree.

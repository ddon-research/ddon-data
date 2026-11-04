# Verify a regeneration

This page is for anyone who re-exported many packet JSON files of client 03040008 and must decide whether the result is right. You write down what the diff should be, run the checks that are cheap over the whole tree, and compare a stratified sample. You never diff every file: over the tree that takes tens of minutes and reports nothing a prediction does not. You need the export of [Export packets to JSON](export-packets-to-json.md).

## 1. Predict from the change

Read the diff of what you changed, and write down per pattern what its JSON should do, before you run the export.

| The change | Prediction for the JSON |
| --- | --- |
| A comment only | byte-identical |
| A field renamed | that key differs; values, shapes and `fits` are the same |
| A field's width, or a field added | that pattern's shape changes and `paddingSize` moves by the width; the prediction states which way `fits` could go |
| A shared include | the same, over every pattern that reaches it ([list them](write-a-packet-pattern.md#7-after-an-include-changes)) |
| A marks-only comment rewrite | byte-identical |
| The export engine's pin | what its changelog names, and nothing else |

Note the expected number of files per pattern: the row of [Packet ids](../reference/packet-ids.md) states it.

## 2. Export where you can compare

Export into a scratch folder, so that the committed tree stays the comparison:

```sh
JSON_DIR=$(cygpath -m "$(mktemp -d)") packets/imhex-export.sh --force @ <pattern-name>
```

The path must stay short. Output paths of 260 characters or more fail, and the longest stream and file names take about 190 of them: a deep scratch folder shows up as `failed` with `path too long` on those streams.

## 3. Run what is cheap over everything

| Check | Command | Success |
| --- | --- | --- |
| Summary line | the last line of each export | `0 failed`, `0 badjson`; `exported` equals the prediction |
| Failed files | `fd -t f -e err . <json dir> \| wc -l` | 0 |
| Fit flags | `python -X utf8 tools/docs_check.py --packet-counts` over the committed tree, once the export is there | no differences, or those you predicted |
| What changed, per stream | `git diff --stat -- packets/decrypted_json/<stream>` | only predicted packet names |

`git diff` over all of `packets/` is refused here: name a stream.

## 4. Compare a stratified sample

One stratum per packet name, a fixed seed, about 20 files each. Save this as a script outside the repository, and run it from the repository root with the scratch folder:

```python
import json, random, re, sys
from collections import defaultdict
from pathlib import Path

new, old = Path(sys.argv[1]), Path("packets/decrypted_json")
strata = defaultdict(list)
for f in new.rglob("*.json"):
    strata[re.match(r"\d+_(.+?)_\d{4}-", f.name).group(1)].append(f)

def keys(v, at=""):
    if isinstance(v, dict):
        return {k for n, x in v.items() for k in keys(x, f"{at}.{n}")}
    if isinstance(v, list):
        return {k for x in v for k in keys(x, f"{at}[]")}
    return {at}

rng = random.Random(20261104)
for name, files in sorted(strata.items()):
    same = shape = other = 0
    for f in rng.sample(sorted(files), min(20, len(files))):
        a, b = f.read_bytes(), (old / f.relative_to(new)).read_bytes()
        if a == b:
            same += 1
        elif keys(json.loads(a)) != keys(json.loads(b)):
            shape += 1
        else:
            other += 1
    print(f"{name}: {len(files)} files, sampled {same + shape + other}: {same} identical, {shape} other keys, {other} other values")
```

Compare each line with the prediction. For a rename, add the rule to the script: map the key's former name to its replacement, then require equality.

Example: the comment change of four patterns on 2026-11-04, predicted byte-identical.

```text
C2L_CLIENT_CHALLENGE_REQ: 42 files, sampled 20: 20 identical, 0 other keys, 0 other values
L2C_LOGIN_SERVER_CERT_NTC: 42 files, sampled 20: 20 identical, 0 other keys, 0 other values
S2C_CERT_GAME_SERVER_CERT_NTC: 83 files, sampled 20: 20 identical, 0 other keys, 0 other values
S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_LIST_RES: 3 files, sampled 3: 3 identical, 0 other keys, 0 other values
```

## 5. Decide

| Result | Do |
| --- | --- |
| Every stratum as predicted | Export into `packets/decrypted_json/`, correct the [Packet ids](../reference/packet-ids.md) counts and commit. Name the prediction and the seed in the report. |
| A stratum you predicted no change for changed | A miss: see below. |
| A predicted change did not appear | A miss too: the pattern you changed may not be the one that runs, or the export skipped it (no `--force`). |
| A `.err`, or `fits` false, where the prediction had none | A miss. Read the `.err`: a compile error across a pattern's files is usually a type clash from an include. |

## On a miss

1. Keep the committed tree as it is: do not export into it.
2. Do not widen the sample in the hope of an average, and do not start a per-file diff of the tree. Take one file of the failing stratum and compare it with `jq`, with its raw file beside it.
3. Explain the difference from the diff of your change. Either the prediction missed a consequence, and you can name it, or the change is wrong.
4. If the prediction was wrong, correct it in writing and say why, then re-run that stratum and every stratum the reason touches. A prediction changed only so that it matches the output proves nothing.
5. If the change was wrong, correct it and go back to step 1.

The check is **approximate** by design: a sample bounds the error and does not exclude it. The exhaustive checks of step 3 are what covers every file, and they cover only what they name.

006 T014a: value-correlation analysis of the unknown fields (tool + report)

Objective (build 03040008; Sam, 2026-11-02, spec § "Naming unknown fields by inference", basis 2):
for every `unk_*` field in the PS4-matched packet patterns (`research/03040008/packets/*-pattern.cpp`
and `include/*.hexpat`; about 340 occurrences in 62 files), find from the exported JSON
(`packets/decrypted_json/`) whether its values match a field of known meaning, and propose a name
with its counts.

1. Tool `research/03040008/packets/tools/unk_correlate.py` (uv project or stdlib script, CPython 3.14,
   with tests): walk the JSON of the patterned ids (bounded: per pattern, never an unbounded listing
   of `packets/`), collect per stream (session) the value sets of every leaf field by key path, and
   for each `unk_*` leaf compute: value count, distinct count, constant/0-1/small-enum flags, range,
   and overlap with the value sets of named reference fields in the same stream: ids (`*Id`, `*ID`,
   `*UID`, `CharacterId`, `PawnId`, `ItemId`, `StageId`, `QuestId`, …), timestamps (epoch range),
   and the other named fields. Score matches by share of the unknown's distinct values found in the
   reference set across streams, and by how many streams agree; flag weak evidence (constants, small
   integers, < 3 distinct values).
2. Run it; write `specs/006-packet-pattern-coverage/research/T014a-value-correlation.tsv` (one row per
   unknown field: pattern/include, key path, stats, best matches with share and stream count, flags)
   and a `.md` with the method, thresholds, the strong candidates (top tier, with two example
   value pairs each and the packets they come from), the weak ones, and the fields no correlation
   explains. Do not rename anything here.

Owns: the tool + its tests, the two research files. Never touch patterns, includes, JSON, raws,
client/; `tasks.md` is the coordinator's. Commit with `git commit -m <msg> -- <paths>`.
Libraries: stdlib (`json`, `collections`, `statistics`); `orjson` or `pandas` only through `uv add`
in a project if measurement shows the stdlib too slow; record the choice.
Done: signed commits; tests; the run's input count (patterns, JSON files, streams) and runtime;
`bash tools/check.sh --since <base>`; receipt from `receipt.py --print` with "For Sam's inspection"
(the 10 strongest candidates). Stop: budget 90 min of work time; finish the scope.
Base: the head when you start (after 006 TC1).

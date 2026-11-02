006 T014c: apply the inferred names to the patterns and re-export

Objective (build 03040008): apply `specs/006-packet-pattern-coverage/research/T014b-consumer-property-names.tsv`
(and the T014a value-correlation candidates T014b confirmed) to `research/03040008/packets/` per spec
§ "Naming unknown fields by inference": each renamed field gets its mark and basis in a comment (V, or
I with consumer / value counts / hint; `lead agrees` where the server name matches); rejected or
unsettled fields stay `unk_*`. Update the README naming rule section with the four bases and the
mark format.

Also: 65 group-35 CONTEXT JSON files in `stream85-marked.pcapng_tcp-stream-11` are invalid JSON
(`"y": -nan`; T014a). Re-export them with `--json-nonfinite=null` (the raw keeps the bytes; say so in the
README conventions) and make that the export default if no reader needs the literal `nan`; check
that no other JSON file holds `nan`/`inf`.

Re-export every pattern whose JSON keys change (`packets/imhex-export.sh --force @ <name>`, with
`</dev/null` in loops); 2-file-per-pattern sample: only the renamed keys differ, values identical,
every file still fits.
Owns: the patterns and includes, the packets README, the re-exported JSON. Never touch raws, client/,
other specs; `tasks.md` is the coordinator's. Commit with `git commit -m <msg> -- <paths>`; long lists
via `git update-index --add --remove -z --stdin`.
Libraries: plbatch; jq / stdlib Python for the sample.
Done: signed commits; counts (fields renamed by mark, fields left `unk_*`); re-export counts and fit;
sample result; `bash tools/check.sh --since <base>`; receipt from `receipt.py --print` with "For Sam's
inspection" (old -> new key, mark and basis per field). Stop: budget 90 min of work time; finish the
scope.
Base: the head when you start (after T014b).

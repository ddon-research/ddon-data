006 TC3: raw file name collisions drop packets (measure, fix, re-export)

Objective: the patched CLI names each raw `<frame>_<Id.Name>_<ts>.<group>_<id>_<sub>`
(`PacketCommand.cs:92-94`, T002c § 2). When one TCP frame carries several packets of the same id,
they get the same name and later ones overwrite earlier ones: TC2 found 11.95.16 with 96 packets in
`packets/decrypted_annotated/` but 48 raw files (47 frames with two packets). Other ids lose files too.

1. Measure: per id, packets in the annotated dumps vs raw files in `packets/decrypted_raw/` over all
   125 streams (the annotated header lines carry frame, id and name; bounded reads per stream, never an
   unbounded listing of `packets/`). Report the ids and streams with losses and the total lost.
2. Fix the CLI's file naming so no two packets share a name, keeping every existing name stable: the
   first packet of a (frame, timestamp, id) keeps today's name; later ones get a deterministic suffix
   in the stem (e.g. `_2`, `_3` before the `.<g>_<id>_<sub>` extension, so `imhex-export.sh` id
   selection still works; check its selectors and tests). Add the patch to
   `packets/README-decrypt-annotate-streams.adoc` § arrowgene-patches (T002e/TC2 entries are the model),
   rebuild, record the DLL SHA-256.
3. Export all streams to a scratch folder under a short path, compare by content hash: every existing
   raw reappears byte-identical under its current name, the only additions are the recovered files,
   and their count equals step 1's loss. Then copy the new files in. Annotated dumps do not change (say
   so if they do).
4. Export JSON for the recovered files with every pattern whose id they carry
   (`packets/imhex-export.sh @ <name>`, `</dev/null` in loops; the existing JSON stays): fit counts per
   id. Note in the packets README how the suffix works.

Scratch folders: create them under a short path and delete them yourself at the end (the
coordinator removes `D:/tc2raw` and `D:/tc2ann` from TC2 separately; leave those alone).
Owns: the CLI patch + README entry, the new raw files, their JSON, the packets README note,
`imhex-export.sh` and its tests only if the suffix needs a selector change. Never touch existing raws,
client/, other specs; `tasks.md` is the coordinator's. Stage with explicit paths or
`git update-index --add --remove -z --stdin`; commit with `git commit -m <msg> -- <paths>`.
Libraries: the existing CLI and scripts; stdlib Python (hashlib) for the comparison.
Done: signed commits; loss table (per id: annotated, raw before, recovered); comparison counts; fit
counts; `bash tools/check.sh --since <base>`; receipt with "For Sam's inspection" (the loss table and
one recovered file's name next to its sibling). Stop: budget 120 min of work time; finish the scope.
Base: the head when you start.

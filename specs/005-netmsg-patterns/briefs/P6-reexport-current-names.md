005 P6: re-export decrypted_raw and decrypted_json with the server's current packet names

Objective: Sam (2026-11-01): "fix our raw exports to use the newly identified naming schemes the
server uses". `packets/decrypted_raw/` (125 stream folders) and `packets/decrypted_json/` (83) were
last exported on 2024-05-13 (commit 1a09a81a605) by an older `Arrowgene.Ddon.Cli`; the annotated
dumps already come from the locally patched build of the Upstream clone at e2411fe8
(`packets/README-decrypt-annotate-streams.adoc` § "Required Arrowgene CLI patches"). Grouped by the
`.<g>_<id>_<sub>` suffix, 51 ids (1,958 raw files) carry a name that differs from
`Arrowgene.Ddon.Shared/Network/PacketId.cs` today: 13 are "Unknown" (2.13/2.15/2.19/2.20.16,
13.44-13.47.16, 35.5.16, 62.12/62.40.16, 63.5/63.11.16) and 38 are placeholders such as
`S2C_PAWN_8_33_16_NTC` (now `S2C_PAWN_GET_PAWN_PROFILE_NTC`). The full list (id, old name, new
name, count) is `specs/005-netmsg-patterns/research/P6-name-diff.txt`.

Do:
1. Find the CLI that `packets/decrypt-export-streams.sh` runs (it calls `Arrowgene.Ddon.Cli` from
   PATH) and the patched e2411fe8 build in the Upstream clone
   (`C:/Users/morph/Documents/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Upstream`, 8 uncommitted
   patch files: keep them; never commit, pull, reset or push there). Build it as the README says if
   no current build exists. Make the export script take the CLI path as a variable (as
   `decrypt-annotate-streams.sh` does with `CLI_PATH`) and add the script's missing `set -o errexit
   -o nounset -o pipefail` and `command -v` checks.
2. Find out why some JSON folders are missing (83 of 125) and whether the CLI's file names come
   from `PacketId.Name` or another field; the export must name files by the current `Name`.
3. Re-run the export for every stream into a scratch folder first; compare against the tracked
   trees: raw file bytes must be identical apart from renames (report any byte difference, it would
   mean a decryption change, and stop), the file count per stream must match, and the old-name ->
   new-name pairs must equal P6-name-diff.txt. Report every id still "Unknown" and why (e.g.
   `C2S_CHARACTER_PAWN_DOWN_CANCEL_NTC` 2.20.16 is declared `PacketSource.Server` at
   `PacketId.cs:315`); fix such a declaration only as a further local CLI patch, listed in the README
   patch table. Input for those fixes: `research/P4-context-binary-character.md` § 7 (client-verified
   misplacements, e.g. 2.19-2.21.16 sources and aliases, 35.8.16 missing); patch only names,
   sources and ids, never a structure layout in this package. Read the report's coordinator
   correction first: PS4 packet numbers never name a PC packet, so do not rename 35.5.16 or
   13.44-13.47.16 from P4; a new PacketId such as 35.8.16 keeps a placeholder name
   (`C2S_CONTEXT_35_8_16_NTC`) until PC-side evidence names it.
4. Replace `decrypted_raw/` and `decrypted_json/` with the verified output. JSON order: the CLI
   rewrites the four nNetMsg packet types that `imhex-export.sh` decodes into `decrypted_json`
   (those JSON files are committed by the coordinator before you start). Re-run `imhex-export.sh` for
   the four patterns afterwards so their JSON stays the ImHex decode; report its fits.
5. Regenerate the counts with `packets/statistics-commands.sh` (the
   `decrypted-tcp-streams-unique-*-packets-count.txt` files, `packets-missing-structure-dumps.txt`)
   if the script covers them; update README text that names the 2024 export.

Owns: `packets/decrypted_raw/`, `packets/decrypted_json/`, `packets/decrypt-export-streams.sh`,
`packets/README-decrypt-annotate-streams.adoc`, the count/statistics files under `packets/`, and the
Upstream clone's local CLI patches. Never touch: `packets/encrypted_streams/`, `packets/keys/`,
`packets/decrypted_annotated/` (report if it should be re-run too; do not run it),
`packets/decrypt-annotate-streams.sh` (it has someone else's uncommitted edit), research/, client/.
Libraries: the existing CLI and scripts; `diff -rq`/`cmp` and `sha256sum` for the comparison.
Done: commits (signed, explicit paths; large trees as their own commit: "Re-export packet dumps
with current packet names"), and a receipt with the build used (clone commit + patch list), per
stream file counts before/after, renamed ids with counts, byte-identity result, remaining Unknown
ids with causes, the ImHex fits, `bash tools/check.sh --since <base>`.
Stop: budget 90 min. Stop and report on any raw byte difference, a build failure you cannot fix in
15 min, or a count mismatch you cannot explain.
Base: a02d06b093.

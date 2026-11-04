# 010 Server packet handling: find the errors, patch them, draft the pull request

**Status: done** (opened and closed 2026-11-04, after spec 009; output draft [PR 8](https://github.com/Sehkah/Arrowgene.DragonsDogmaOnline/pull/8) on the fork; Sam's rulings on upstream and on merging the reports to the public `main` are open: `tasks.md` T007f)

## Goal

Sam, 2026-11-04: "Create a new clean copy of my fork of the server: https://github.com/Sehkah/Arrowgene.DragonsDogmaOnline.git
In there, check for errors in the server code related to packet handling. Devise a patch and draft pull request. Outline
impact of changes."

The deliverable is a reviewable patch to the server, with evidence for every change and an honest account of what each
change does to a running server and its clients. Client build **03040008** decides, unless the server code is shown to
target another.

## The working copy

- `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Clean`: fresh clone made 2026-11-04, branch `develop` at `e2411fe8f9`,
  remotes `origin` (the fork) and `upstream` (`sebastian-heinz/Arrowgene.DragonsDogmaOnline`). Fork and upstream `develop` are
  the same commit, so a patch here applies to both. net10.0; `dotnet` 10.0.403 is installed; CI in `.github/workflows/build.yaml`.
- This clone is a working copy: the "clones are read-only, never build or run them" rule does not apply to it. It may be
  built and tested, and takes a branch.
- Not to be touched: `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline` (an unresolved merge in progress: 4 conflicted files)
  and the `.Upstream` clones (the patched CLI that produced `packets/decrypted_raw/` lives in one).

## What counts as an error

| Class | Example lead | Decided by |
| --- | --- | --- |
| Wire layout: a `PacketStructure`/`CData` serializer's order, width or missing field differs from the client's | spec 008 T001 `ag_vs_pc`: 3 differ of 84 compared, 31 not comparable (10.14.16, 34.0.1, 14.11.16, confirmed against code); 19.28.2 Index/SkillNo swapped in `CDataNormalSkillParam.cs` (`docs/explanation/two-packet-decodings.md`); 62.1.2 DungeonId; stamp `BonusType`/`BonusValue` (006 T014b7) | PC reader or writer in the client, then every capture fits |
| Framework: framing, RES guard, padding, packet factory | `EntitySerializer.ReadServerResponse` reads `Result` as `u16` when `Error != 0` while servers write `u32` and the client stops reading (`docs/reference/arrowgene-cli-patches.md`, which also lists the rest of the CLI's patches) | PC reader, captures, a failing test |
| Packet table: wrong id, source or name; a response under the wrong key | 14.10.16 is `C2S_WARP_END_NTC` (006 T008); `L2C`/`S2C` source mismatches | PC handler table and `OnPacket_` strings; never PS4 ids |
| Dispatch: missing, duplicate or unreachable handlers; a request answered with the wrong response | registration against `PacketId.cs` | server code |
| Robustness: a client-supplied count or length that allocates or throws unchecked; an exception that drops a session | list counts in readers | server code, a failing test |

Out of scope: renames for taste, refactors, gameplay logic, unimplemented packets (a stub with a correct layout is not an error),
and field names (a name changes only where it misleads a reader of the wire layout, and is then a separate commit).

## Method

1. **Differential first**: run the server's own serializers over the committed captures, `packets/decrypted_raw/`, the way
   `Arrowgene.Ddon.Cli` does: read, re-encode, compare with the raw bytes; compare fields with `packets/decrypted_json/`. Divergence is a
   candidate. Mind `docs/explanation/two-packet-decodings.md` (spec 009 decision 7): the annotated dumps carry the server's understanding,
   tested by play, so meaning there is strong evidence and sizes and order are what needs checking; the JSON comes from the binaries.
2. **Evidence per candidate**: the PC 03040008 reader or writer (`evidence-researcher-ida`, annotated database through
   `private-copy.sh pc-handlers`), the PS4 structure where Season 3 kept it, the recompilation C++ for argument order, every capture fits. A
   server layout that the PC code contradicts is an error (`V`); capture evidence alone is at most `I`, and goes in the report unpatched unless the
   coordinator rules otherwise. Both directions matter: a wrong server layout may be the one that captures from another server show.
3. **Patch**: branch `fix/packet-handling` in the clean clone, one commit per error class or a coherent small group, following the
   server's own style; a test per fix in `Arrowgene.Ddon.Test` built from a real capture's bytes; `dotnet build` and `dotnet test` pass, with
   the failures on an unpatched `develop` recorded for comparison.
4. **Verify**: adversarial review of every claim, framed as: which of these fixes would break a working client? Static before live. A live run
   (`C:\ddon-automation`, local server and client, never pushed) only for a change whose effect static evidence cannot settle.

## Draft pull request

- Push `fix/packet-handling` to the fork and open a **draft PR on the fork** (base `develop`), so the diff is reviewable and nothing reaches upstream. Pushing that branch and opening that draft are authorized by Sam's request.
- Opening or retargeting a PR on upstream `sebastian-heinz/Arrowgene.DragonsDogmaOnline` stays Sam's decision, asked at the end, as it reaches other people.
- Upstream etiquette: read `docs/` and recent merged PRs for its conventions before writing the body.

## Impact outline (a section of the PR body and `research/impact.md`)

Per change: the packets touched (group.id.sub, name); the symptom on an unpatched server; what a client sees after it; who is affected (all players, a
feature, none in normal play); the risk (saved data, other code depending on the old field or order, tools such as the CLI's annotated exports); how it was verified and what was not run. Plus: effect on `packets/decrypted_annotated/` if the CLI re-runs; candidates found but not patched, with the reason.

## Rules

- Server C# is a lead, never evidence for itself; PS4 flat ids never name PC packets; a check not run is "not run".
- Every report names the build. Reports go in `specs/010-server-packet-fixes/research/`.
- No secrets, game assets or whole captures in the PR: test fixtures are the few bytes they need, from packets carrying no account data (checked).

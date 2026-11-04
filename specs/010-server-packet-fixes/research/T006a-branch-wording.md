# 010 T006a: the branch's wording, before a push

Server clone `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Clean`, branch `fix/packet-handling`: `b8be1e19` became `64c676b9`, 29 commits on `develop` `e2411fe8`. Nothing was pushed or fetched; `develop` and `harness/differential` did not move. `backup/before-wording` holds `b8be1e19` and is never pushed.

This file names no value and no reproduction, since it may become public with this repository.

## What changed

**Messages.** The five bodies T006 proposes are in, word for word; the coordinator shortened the MtString one in a follow-up to state the client's limit and the cap only, and T006 now holds that text. The task ids and row labels went from six more: the id tables and SHA1 commit, the quest play time, the 62-byte block, the soul ordeal level, the five trailing fields, and the two response readers. Subjects, authors and author dates are identical. The other commits changed no message.

**Comments, each in the commit that introduced it.** The old side is described, not quoted, as the full text has what this file does not name; `git diff backup/before-wording fix/packet-handling` in the clone shows it. That diff is 6 files, 9 lines on each side, every line a comment, fixtures untouched:

| File | Lines | Was | Is now |
| --- | --- | --- | --- |
| `GameServer/Handler/ClientChallengeHandler.cs` | 22 | What a session would go on doing | `// Critical: a failed challenge closes the connection.` |
| `LoginServer/Handler/ClientChallengeHandler.cs` | 25 | The same | The same |
| `Test/Shared/Entity/SerializerRegistrationTest.cs` | 33 | Ended with two row labels | The labels are gone |
| `Test/Shared/Entity/SerializerRegistrationTest.cs` | 186 | The fault, its measurement, a task id | `// First, since the read below relies on the element being registered.` |
| `Shared/Entity/EntitySerializer.cs` | 2303 | What each bad length did | `/// One that does not reads as a short packet.` |
| `Shared/Extension.cs` | 33, 34 | The limit, and more than the limit | `/// The most bytes an MtString may have. PC 0x8bc5b0 fails the read above 0x800,` then `/// so the cap stays one below that.` |
| `Test/Server/Network/ClientSuppliedLengthTest.cs` | 145 | The size, and where it threw | `// Padding takes it past the u16.` |
| `Test/Server/Network/ClientSuppliedLengthTest.cs` | 147 | The size, and what reached the send | `// Over the limit before padding too.` |

Paths are under `Arrowgene.Ddon.`. T006 named the two handlers and line 186; the read of the whole diff found line 33, line 2303 and the two in `ClientSuppliedLengthTest.cs`; the coordinator's follow-up named `Extension.cs`. In `ClientSuppliedLengthTest.cs` only the two trailing comments changed: its cases stay, for Sam.

## Proof

All of it was run at `64c676b9`. The first rewrite, `bc542581`, passed the same checks and was replaced by the follow-up. An interim `2ce2025b` was also replaced: Git Bash's path conversion turned one `///` into `//` in the new doc comment, seen in the tree diff, and fixed in the introducing commit.

| Check, over `develop..fix/packet-handling` | Result |
| --- | --- |
| `terminator\|stack buffer\|session of the recipient`, and the address and word `recipient` the follow-up also removes, in messages and `git log -p --text` with `-- '*.cs' '*.bin'` | 0 hits |
| `git log --format='%G?'` | 29 of 29 `G` |
| Subjects, by `diff` of the two `git log --format=%s` lists | Identical |
| Author, email and author date, by `diff` | Identical |
| `git diff --stat` against `develop` | 97 files, 2,688 insertions, 174 deletions: unchanged, so `pr-body.md`'s size line stays as it is |
| The 29 subjects `pr-body.md` quotes (Changes table and Test only list) against the log | 29 of 29, none left over |
| The 4 original session tokens, taken from the fixtures of the commit before the fixture rewrite, in messages and `git log -p --text` (239,585 bytes) | 0 hits; the script prints no value |
| `dotnet build Arrowgene.DragonsDogmaOnline.sln --no-incremental`, Debug and Release | 0 errors, 520 warnings on both |
| `dotnet test`, Debug and Release | 177 of 177 on both |

The search ran over `git log -p --text`, with `-- '*.cs' '*.bin'` since the guard refuses an unbounded `git log -p`; those are all the branch's file types and all 29 commits touch them. `rg -a -i` with these patterns:

```text
\b[TFWRDN]\d{1,3}[a-z]?\b
specs/   research/   [A-Za-z]:[/\\]   /mnt/   ddon-data
\bMiB\b   \bOOM\b   out ?of ?memory   memory runs out
login.{0,40}\b(no|without|before)\b   \b(no|without|before|pre-?)\b.{0,40}login
-marked    \.stream\d+\.   tcp-stream-
anyone   attacker   unauth   recipe   one player   reproduc   exploit   hostile   malicious
```

Before the rewrite: 29 lines. After: 7, none of them the branch's wording:

| Hits | Where | Why it stays |
| --- | --- | --- |
| 1 | A log string in `Client.cs`, a context line: the drive-path pattern matches `Packet:` before an escaped quote | Already on `develop`; not a path |
| 1 | `PacketFactoryReadTest` loads a capture by its file name, which has `-marked` and `tcp-stream-` | The file is on `develop`: public upstream |
| 1 | A commented-out hex dump in `PacketFactory.cs`, context line, `F8` | Already on `develop`; not a label |
| 4 | `RecipeId` in `CDataCraftProgress` and its handler | The word "recipe" in a game field |

## Reading of the brief

- **"Show that diff" and "name no value"** pull against each other here, as the old lines hold the measurement and the sizes. The table above describes the old side and gives the new side whole.
- **The comments in `ClientSuppliedLengthTest.cs`.** The brief keeps that file's cases. Its two trailing comments stated the faults that T006 took out of the matching commit message, so they were trimmed and the cases left alone.
- **The MtString cap:** the first rewrite kept T006's sentence on why the cap has its value. The coordinator decided a public server diff needs the limit only, so the message and the comment now state just that.

The old commits stay in this clone's reflog and in the backup branch. A push of `fix/packet-handling` does not send them. **Hashes of this branch in earlier reports no longer resolve on it**: subjects are unchanged, so look up by subject.

Libraries: git, `sd`, `rg`, the existing test projects. Own code: throwaway scripts outside this repository to drive the rebase and to check subjects and tokens, as git has no such step of its own.

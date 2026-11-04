# 010 T007c: the review's fixes and F04, client PC 03040008

Server clone `Arrowgene.DragonsDogmaOnline.Clean`, branch `fix/packet-handling`, `64c676b9` to `bc3dc199`, one new signed commit on top, not pushed. Rulings of `T007b-review.md`. Date 2026-11-04.

## F04

**Fix.** One private `Lock` in `PacketFactory`, held in two places: around the count in `Write`, and inside `Encrypt`, which `Write` and `WriteDataWithLengthPrefix` both call. The brief asks for the smallest span covering both. I took that as two short holds of one lock rather than one span with the buffer work inside, because nothing needs the count and the encryption to happen as a unit (below). It also covers the certificate frame and the public `Encrypt`, which a span in `Write` would miss.

**Does a frame's cipher state depend on the frame before it? No.** `Encrypt` passes `Util.Copy(CamelliaIv)` for every frame, so chaining stops at the frame's end. The client does not compare the counter (T003 F04, `V`).

**Socket: outside the lock.** Frames need no order there, and the library keeps each one whole. `TcpServer.Send` calls `Client.QueueSend`, which calls `ArenaBackedSendQueue.Enqueue`, a copy of the whole frame under the queue's lock. Read in Arrowgene.Networking source at `4998646c`, the commit the 2.1.7 package names, cloned to scratch. T001 listed this DLL as not read. Two overlapping frames may leave in either order, as before.

**`SetCamelliaKey`: outside the lock, and no overlap found by reading.** Not run under load.

- `TrySend` writes only the challenge's own response until `_challengeCompleted`.
- That flag is set on the thread that set the key, after the key.
- `HandleChallenge` clears `_challenge`, so a second challenge throws before it reaches the key.
- So a timer can not write while the key changes.
- `InitializeChallenge` runs on the client's lane as receive does (T001's reading, not re-derived here).

The lock did not need more than the write path.

**Noted, not touched.**

- `Decrypt` shares the subkey and has its own scratch, on the receive path.
- `Camellia` is static and holds only read-only tables, so factories share nothing else.
- A `Packet` object sent to several clients has `Count` written by each, as on `develop`. `Client.Send<T>` makes one per send; callers passing one `Packet` to several clients were not surveyed.

## Mutation

`Arrowgene.Ddon.Test/Server/Network/PacketFactoryWriteTest.cs`, 4 threads on one factory, each frame decrypted by a second factory and compared with what was written. Debug, 10 runs each, production file restored afterwards and compared by `git diff --stat`.

| Production code | Test | Failing runs | Detail |
| --- | --- | --- | --- |
| No lock (the code at `64c676b9`) | frames | 10 of 10 | 11,894 to 11,999 of 12,000 frames wrong |
| No lock on `Encrypt` | frames | 10 of 10 | 11,937 to 11,996 of 12,000 wrong |
| No lock on the count | frames | 7 of 10 | So the frames test alone is not enough for this half |
| No lock on the count | count, added for that | 10 of 10 | 2 to 8 counts lost of 400,000 |
| With the lock | all | 0 of 15 | 10 runs with 2 tests, 5 with 3 |

Runtime of the 3 tests: about 4 s in Debug (the frames test 1 s, the count test about 3 s, the pin 2 ms). Release mutations: not run. A machine with one core could pass with no lock: not run on one.

**Bytes of a frame from one thread: unchanged.** `Frames_written_on_one_thread_keep_their_bytes` pins three frames whose hex was printed by the code at `64c676b9`, before the lock was added. The pin also covers an NTC's count and a RES's zero. The differential harness: not run, as the diff adds only the lock and the pin compares the bytes.

## Gates at `bc3dc199`

| Gate | Result |
| --- | --- |
| `dotnet build Arrowgene.DragonsDogmaOnline.sln -c Debug --no-incremental` | 0 errors, 520 warnings |
| The same, `-c Release` | 0 errors, 520 warnings |
| `dotnet test` Debug, Release | 180 of 180 each |
| `git log --format=%G? develop..fix/packet-handling` | 30 `G` of 30 |
| Subjects in `pr-body.md` | all 30 match `git log` |
| `git apply -R --check`, the 23 commits of the drop table | 15 clean, 8 conflict, as at `64c676b9` |
| `rg` over `pr-body.md`: task ids, `D:/`, `C:/`, `terminator`, `stack buffer` | no hits |
| `rg` over `pr-body.md`: `login` beside `no`, `without`, `before` | 1 hit, line 99: the SQL message `no such column`, about a migrated database. Left as it is |

## Findings closed

| # | Where | What changed |
| --- | --- | --- |
| 1 | `pr-body.md`, `impact.md` | Banner narrowed as the brief words it |
| 3 | `impact.md` | A section for the new commit; rows for W07, W13, W18, W19, W20, D03, D04, D05, T03, T07. T001 gives their reasons; T003 has no row for any of them |
| 4 | `impact.md` | Both lines now say what is true of the branch |
| 5 | both | "On any frame looked at"; the unexplained client exit recorded |
| 6 | `pr-body.md` | Scope of "one response" narrowed |
| 7 | both | 33001 on login `CreateCharacter` marked inferred |
| 8 | both | Where the time shows is not known |
| 9 | `pr-body.md` | "Not run live" completed; test-only build and forced 8.8.2 stated. Also one clause in `impact.md`'s evidence line |
| 10 | `inputs-and-builds.md` | Head and PR 8 |
| 11 | `packet-handler-tables.md` | Sentence dropped; `T003` keeps the finding |
| 12 | `status.md` | CLI patch row says what ran. The how-to moved out of the row above, which said not run |
| 13 | `two-packet-decodings.md` | Heading renamed. `rg` finds no link to its anchor, so no anchor needed fixing |
| 14 | `pr-body.md` | "a client's responses". Also the same two phrases in `impact.md`, which the brief's list does not name |
| 15 | `pr-body.md` | The limit kept |
| 16 | both | The default-lane sentence is F12's only |
| 17 | `impact.md` | "Not run" for the 8 commits, risk for the 3 |
| 18 | `docs/index.md` | New section named |

**Recount for finding 16, from `PacketId.cs` at the head.** 1,778 ids are declared with `ServerType.Game`. The game table holds 1,779 entries, as it also holds `UNKNOWN`, declared as Login. T001 has the same two numbers, so neither text was wrong. The collision estimate rounds the same for both.

**Not mine:** finding 2, and `AGENTS.md` and `CLAUDE.md` of finding 18.

## For later

- The commit `df93c60d`'s message speaks of 1,778 game ids and the branch is not rewritten: it agrees with the recount.
- `pr-body.md` and `impact.md` now say the differential, replay and live smoke predate the last commit.
- Arrowgene.Networking should be recorded in `research/external-references.jsonl`, which this brief may not touch. See the receipt.

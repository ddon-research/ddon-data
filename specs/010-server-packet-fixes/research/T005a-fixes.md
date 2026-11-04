# 010 T005a: fixes after the adversarial review, client PC 03040008

Server: `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Clean`, branch `fix/packet-handling`, head `b8be1e19b5a68c57c317461bdd607f52be71158d`, 29 signed commits on `develop` `e2411fe8f9`, not pushed. Old head `924094e0`. dotnet 10.0.403. ddon-data base `0001d26bb4a`. Date 2026-11-04.

No live server or client was run. One loopback socket was. Client bytes come from `packets/decrypted_raw/` (160,615 files) and from radare2 on `2022_01_29_DDO_DUMP_FIX.exe`; no IDA database was touched.

## F1: closed

Folded into the commit that made it (`f8683307`, was `c423c48b`): `response.CamelliaKey.Length < MinimumSessionKeySize` in both overloads, the constant renamed from `CamelliaKeySize`. Tests are a new commit, `71a686f3`.

| Check | Result |
| --- | --- |
| Canary `010-T005/canary` copied, run at the head | 48: PASS, 32: PASS, exit 0 (exit 1 at `924094e0`) |
| Mutation: `!=` back in | 6 fail: good path both overloads, captured request both overloads, the 48 case of the overload test, the socket test |
| Mutation: check removed | 7 fail: too short (1, 16, 31) on both overloads, the socket test of a failed challenge |

`ClientCreateChallengeRequest` still takes the key, as the too-short tests need to pass others; `Challenge.ClientCommonKeySize` (48) sizes it in every good-path test, and those tests hold only the first 32 on the client's side. `A_captured_*_request_passes_under_this_key` use a captured request's sizes and 62-byte block with this key's RSA.

### Why a whole class of test missed it

The check and its tests shared one assumption with no capture behind it. T004a took 32 from `keys-all-in-one.csv`, which holds the truncated session key and not the RSA plaintext; then the test client was given that same 32, so test and code agreed. The replay could not reach the handler without the official private key. That covers the one path no capture can replay: the first client frame's RSA plaintext.

**New tests and the seam, every client value in them:**

| Test | Value assumed | Against captures | Action |
| --- | --- | --- | --- |
| `ChallengeTest`, `ClientCreateChallengeRequest` | key 32 | 48 on 125 of 125 | **wrong, fixed** |
| `ChallengeTest` good path | block of 16, padded by the writer to 62 | sizes 16/16 on 125 of 125; block 62, frame 336 on 125 of 125 | right; captured block now also tested |
| `ChallengeTest` | certificate 304, "docs" | 304 on 125 of 125 | right, comment says so |
| `ErrorMessageListNtcTest` | one capture "the last, with 0 to come" | **both captures carry 50** | **wrong comment, fixed**: they differ only in padding, so one fixture stays (`b8be1e19`) |
| `ErrorResponseReadTest` | 7-byte body, "the shortest" | 16-byte frames less 9 of header: 8,817 frames | right |
| `PacketFactoryReadTest` source bytes | 0 and 0x34 | table below | right |
| `MtStringWriteTest` | 0x7FF | PC `0x8bc5b0`, no capture reaches it | PC only |
| `CraftProgressTest` element | u32 | PC `0x75e8e0`, no capture holds one | PC only |
| `AchievementCompleteNtcServedTest`, two elements | {u32, u8} twice | PC; captures hold one each | PC only |
| `ErrorMessageListHandlerTest` | 500-character messages | synthetic, forces more frames | not a client value |
| `ClientSuppliedLengthTest`, `A_failed_*`, too-short keys | hostile values | not claims about a real client | fine |
| Recording clients | `Close` counts; `SendRaw` records | no client value; the real socket path now has its own test | fine |

**New conditions in the close, reject and guard paths, what backs each:**

| Condition | Value | Captured | PC |
| --- | --- | --- | --- |
| R05 key at least 32 | RSA plaintext 48 | `CommonKeySrcSize` 48 on 125 of 125 | `0x88aecd`, `0x88afbb` push 0x30 (T005) |
| R02 frame at least 16, whole blocks | | 160,615 of 160,615 | client limit none below u16, `0x9d6d69` (T004a) |
| R03 source byte | client 0x00 | byte 4 is 0 on every client frame with a header: 116,354 + 44 named `C2S_SERVER_GET_SERVER_LIST_REQ` that my filter set apart + the 1 client 63.11.16 named `S2C_` | **not read**: captured only |
| R03, server direction, CLI only | 0x34 | 43,968; the other S2C values are the 124 headerless certificates | not read |
| R04 3 s32 lengths | fit what is left | 3.3.16 66,275, 6.23.16 8, 6.25.16 34,607 read with no throw (T005) | **not read** |
| R06 guard | none on a client value: the writers pad `62 - PasswordEnc.Length`, the array and not the size | n/a | n/a |
| W10 u8[62] each way | fixed read; frame short of it throws | frame 336, gap bytes 0, sizes 16/16, on 125 of 125; **password block identical on 125 of 125** | reader comment `0x77cfe0`, patterns `:10` (T001) |
| W11 u8[62] | written, not compared | 16/16 and the same password echoed on 125 of 125 response frames of 96 | patterns `:8` (T001) |
| W08, W09, W14, 11.60.16, 31.17.1 | fixed reads, throw if short | 42, 41, 57, 59, 7, 42 read with no throw (T005) | T003 |

The two "not read" rows rest on captures alone, 116,000 and 100,000 reads wide. Nothing else compares a client value with an assumption. The `CreateCharacter` Result branch and F06 are server-side.

## F2: closed

Every commit from the one adding a fixture carries the new form: `git filter-branch --index-filter` over `develop..fix/packet-handling`, signing each with `git commit-tree -S`. 4 commits had nothing to change and keep their hashes; 22 were rewritten. Author and dates kept. The backup ref is deleted.

**Fixtures hold now:**

| Field | Files | Filler |
| --- | --- | --- |
| Session keys, one-time tokens, 31 bytes | `0_1_1`, `0_5_1`, `0_1_2`, `2_1_2` | `X` |
| RSA-wrapped key, 256 | `1_0_1`, `44_0_1` | 0xEE |
| 46 stale bytes after the password | `1_0_1`, `44_0_1`, `1_0_2`, `44_0_2` | 0xEE |
| Pawn id, a player's (was not named by T005) | `30_0_2`, `CraftMyPawnList[0].PawnId` | 0xEE |
| Client heap in `Bin`, including `wall`, `Produ`, pointers (was not named by T005) | `50_1_1`, after the two sort lists | 0xEE |
| Padding past each layout | all 24 | 0xEE |

Kept on purpose: the 16 bytes of the password block, the same on 125 of 125, a client constant, which the captured-request tests use; the client version; ids and values of game data. Names: `G_H_S.bin`, one per id. Test comments no longer name streams. `PacketFactoryReadTest`'s `CaptureKey` is the key of `PacketCommandTest`, already on `develop`, so **it is public upstream with its capture**, untouched here.

The scan, decoded as UTF-8: no IP-like run in any fixture; text only in `13_16_2`, `62_33_2` and `3_0_16`, all game text (dungeon and buff names, official error messages). Inline hex in new tests: lengths, `3E 90`, ids and times, 10.13.16's body, none of it identifying.

**Proof.** `git log -p` shows a binary fixture as "Binary files differ", so that alone would prove nothing; both were run.

| Search over `develop..fix/packet-handling`, 29 commits | Result |
| --- | --- |
| 4 original tokens in `git log -p --text` (248,483 bytes) | 0 hits |
| 20 original keys, RSA blocks and tails of 8 bytes or more, in 191 distinct blobs of every commit | 0 hits |
| Fixture blobs in any commit against the filled set | 23 of 23 in it |
| `-marked `, `.stream10.`, `.stream85.` on added lines | 0; `tcp-stream-` 1, `PacketFactoryReadTest` naming the upstream yaml |
| Signatures, `%G?` | 29 of 29 `G` |

The old commits stay in this clone's reflog until it expires. A push of the branch does not send them; `git reflog expire` + `git gc --prune=now` removes them, not done, as it is not asked and costs the old hashes T004a, T004b and T005 cite. **Those reports' hashes for rewritten commits no longer resolve on the branch**: subjects are unchanged, so look up by subject.

## Not checked, settled

**Canned dumps.** All 851 `Packet` dumps in `GameDump`, `GameFull`, `InGameDump`, `SelectedDump`, `MissionDumps`, `LoginDump`, each through `ReadObj` and direct `Read(IBuffer)` with re-encode, on `develop` and on the head (same program). 47 have no structure. 16 differ, every one better or equal:

- 14 of 16: read further or re-encode equal, in structures of this patch (44.0.1, 44.0.2, 0.1.1, 0.1.2, 0.5.1, 14.11.16, 31.17, 11.4.2).
- **2 of 16: `GameFull.Dump_74`, `InGameDump.Dump_75`, 18.0.2 with Error 47003**: `ReadObj` now returns; direct `Read(IBuffer)` throws `ResponseEndsAtError`, where `develop` threw `EndOfStreamException`. **It escapes on that call**, as T005 asked. No production code reads either.
- 3 throw on both: `Dump_712`, `InGameDump.Dump_107`, `Dump_109`, unread by production, unchanged.

The 3 direct `Read(IBuffer)` sites on a dump in production (`Dump_93`, `Dump_708`, `Dump_10`) have Error 0 and read identically; `Read(byte[])` goes through `ReadPacket`. The 16 production sites (2 on private `PcapData`, not in this run) read structures this branch leaves unchanged. **So nothing reaches a server. No change.**

**RES before close.** New `ChallengeOverSocketTest`: real `TcpServer`, `LoginClient`, handler. A failed challenge delivers its RES under the fixed key, then an orderly end, 25 of 25 connections; a key of 48 stays open with its RES under the first 32. A scratch measurement of the library alone (20 connections each, Windows loopback), RES then `Disconnect`:

| Ahead of the RES | Delivered whole |
| --- | --- |
| nothing | 20 of 20 |
| 64 KiB, 1 MiB, 8 MiB, client slow to read | 20 of 20 each |
| client still sending when the server closes | **0 of 20: reset, RES lost** |

By reading, a RES behind a send still pending is dropped: `Close` clears `_isAlive`, and `TryPrepareSendChunk` then refuses. The measurement did not reach that, as these sends complete into the kernel. **Not fixed, for these reasons.** The library has no flush, so a fix means deferring the close by a timer, which leaves a socket open to a client we meant to drop. At a failed challenge neither case can meet a real client: only the 304-byte certificate has gone ahead, and the client answered it; and **0 client frames sit between request and RES on 125 of 125** captures. A critical error in a session can meet the reset case; it closes on `develop` too, and the client is disconnected either way, only without the specific dialog.

**`0x4cf380`.** Read here. Unsigned: `ms / 1000` by `0x10624dd3`, minutes `/ 60`, then `"%02d'%02d''%02d"` of minutes, seconds, hundredths, through `0x13b62c0`, which uses `vsnprintf` into 1024 stack bytes with limit 0x3ff. 0 gives an empty string. `uint.MaxValue` gives `71582'47''29`, no sign or buffer fault. **`QuestPlayEndHandler`'s clamp is right as it stands**, and a negative clamps to 0, the empty string. Whether a screen fits over 99 minutes: unread, for the live run.

**F10.** Independent of T004a's IL walk: regex over 2,884 `.cs`/`.csx` files, 453 entity types named in `Read`/`Write`, `Entity`/`EntityList`/`MtArray`, against 1,710 registrations: **0 named and not registered**. 14 did not resolve by regex: 3 by hand are registered (`CDataCraftSupportPawnID`, `CDataItemEmbodyCostParam`, `CDataCommonPair<uint>`); the rest are delegates, which use no serializer, and the generic line itself. Only `WriteEntity` and `ReadEntity` throw, and only for a type no list names.

**Hot path.** Confirmed: `ResponseEndsAtError` does not run on a running server for a real client. Only `S2C*`/`L2C*` readers reach `ReadServerResponse`; the server reads those from canned dumps with Error 0 (above), and at start. No client frame in the captures has a response structure. A hostile client could send an S2C id with Error set; `LogIncomingPackets` defaults to true, and the read is then caught in `ReadPacket`: one caught exception per such frame, where `develop` threw one too. No handler takes those ids. Cost not measured.

**Pins**, new tests that pass on `develop`, plus seam where they need it. Mutation was run on F1 only; the rest rest on reading.

| Test | Why it stays |
| --- | --- |
| `ClientSeamTest` (2) | **Deleted** (`71a0b1ea`): every recording-client test covers it |
| New 48-byte good paths, captured requests and overload cases (6), socket 48 (1) | `develop` has no check: they pin F1, and fail at `924094e0` and under mutation |
| `A_length_that_fits_...` (3) | R04's check must not refuse a real length |
| `A_real_password_size_...`, `A_captured_response_still_round_trips` | Layout must stay on real data |
| `The_largest_body_...`, `A_body_over_the_u16_length_...` (65511, 65524) | Boundary of F03; off by one fails them |
| `Sources_0_and_0x34_...` (2) | R03 must not refuse a real source byte, now backed above |
| `A_success_...`, `Lobby_leave_...`, `Quest_play_entry_...`, `A_handled_error_in_a_queue_handler_...` | "Never two" on paths this patch left alone |
| `Canned_dumps_...`, `An_unknown_id_...`, `Every_declared_id_...`, `Every_registered_response_can_be_written_as_an_error` | Guards over all ids: a new row breaking them shows |
| `A_queued_response_over_the_frame_limit_...` | T004a called it weak; T005 read `TcpServer.Send(null)`, which dereferences as the recorder does, so it is sound |
| `A_string_under_the_cap_...` (0x7FE, 0x7FF) | The cap must not cut what fits |

## Gates

| Command | T004b | Now, at `b8be1e19` |
| --- | --- | --- |
| `dotnet build Arrowgene.DragonsDogmaOnline.sln --no-incremental` | exit 0, 520 warnings, 0 errors | exit 0, 520, 0 |
| `dotnet test ... --no-build` | 170 of 170 | 177 of 177 |
| `dotnet build ... --configuration Release --no-incremental` | 520, 0 | 520, 0 |
| `dotnet test ... --configuration Release --no-restore --no-build` | 170 of 170 | 177 of 177 |

177 = 170 + 10 at `71a686f3`, - 2 seam tests, - 1 fixture case.

Differential: `Arrowgene.Ddon.Differential` restored untracked from `harness/differential` onto the head, removed afterwards; tree clean; 160,615 captures, 7 s, `DOTNET_GCHeapHardLimit=0x300000000`. Fixtures are tests, not captures, so as expected:

| Measure | T004b | Now |
| --- | --- | --- |
| Reads returned, fit, re-encode equal | 159,008 each | 159,008 each |
| JSON equal | 36,885 of 36,886 | 36,885 of 36,886 |
| Class `agrees` | 511 + 2 headerless | 511 + 2 headerless |
| `values differ, other width` | 1 | 1 (63.11.16) |
| Ids with a counted change, of 1,321 | | **0** |

## For Sam's inspection

- **New head** `b8be1e19`, 29 signed commits, not pushed. **Rewritten** 22, with new hashes and unchanged subjects, from `ef78efed` (was `9a1d04a8`) to `9532dcca` (was `924094e0`); `f8683307` also carries F1. New: `71a686f3` tests, `71a0b1ea` seam tests dropped, `b8be1e19` one 3.0.16 fixture.
- **Fixtures** hold real layouts and real non-identifying values, with filler over keys, tokens, RSA blocks, a pawn id, client heap and padding. 24 files, no stream in any name or comment.
- **What a running server does differently from T004b:** only F1. It now accepts any RSA plaintext of 32 bytes or more; under 32 fails.
- **Live run must still cover:** full login and game-select with the real client, including W11, W01, W04, with RSA under this server's key; moving between servers (0.5.1); one error path and one with the once flag (F06); one quest end, the screen and a time over 99 minutes (W16); a category 6 achievement and its notice (W02), with T005's category 6 catch-up flood. The failed challenge from a test client is settled above and needs no client.

## Not run

- A live server or client.
- Non-Windows sockets: the reset result is Windows loopback.
- Mutation of the pins other than F1's; R03's and R04's PC writers.
- `develop` comparison of the canary: it needs the seam commit, and the mutation answers the same question.
- Handler-private `PcapData` through the dump run: 2 production reads of structures unchanged here.
- Building each intermediate commit: the rewrite changes fixtures, comments and F1 only; the head was built.

## Libraries and own code

Libraries: xunit, BCL sockets, `Arrowgene.Networking`, `git filter-branch`. Own code in the clone: only tests. Scratch, not committed: fixture filler and index filter (a tree filter risks line endings, and `git filter-repo` is not installed), dump and F10 walkers, capture audits.

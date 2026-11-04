# 010 T006: impact of `fix/packet-handling`, client PC 03040008

For Sam. Server clone `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Clean`, branch `fix/packet-handling`, head `bc3dc199`, 30 signed commits on `develop` `e2411fe8f9`. The fork's draft [PR 8](https://github.com/Sehkah/Arrowgene.DragonsDogmaOnline/pull/8) has the first 29, to `64c676b9`; `bc3dc199` waits for the coordinator's push. Hashes below are the pushed ones (T006a rewrote messages and comments; subjects are unchanged). `git diff --stat`: 98 files, 2,881 insertions, 185 deletions: 45 files of production code (474 insertions, 184 deletions), 53 of tests and fixtures in `Arrowgene.Ddon.Test` (2,407 insertions, 1 deletion). Date 2026-11-04.

**This file holds reproduction detail and says what is reachable before login. It stays out of the pull request, and this repository is public: decide before merging spec 010 to `main`** (`tasks.md`). `pr-body.md` is the public text.

Evidence levels used below: **read** in client code (T003, `V`), **captures** (160,615 frames of `packets/decrypted_raw/`), **live** (T005b, real client, local server; 0.7.2, 8.8.2, the move and the banner on a build of the branch with scratch lab additions, and 8.8.2 forced), **not run**. "Who" is who meets the change on a real client.

## At a glance

| Group | Effect a player can see | Commits |
| --- | --- | --- |
| Error and missing responses | One error RES; a request always answered, so a 33001 disconnect becomes an error dialog on the paths named | 3 |
| Stream and hostile input | Nothing in normal play. A connection that cannot be followed closes; bad lengths are bounded | 5 |
| Client-visible layout | The byte that chooses the category 6 banner is sent (banner seen once, see `909b92a6`); quest play time is sent where read (where it shows is not known); over-long text is cut rather than disconnecting | 3 |
| Layouts with no client effect | Bytes match the client; same behaviour | 7 |
| Readers for the CLI and tools | None on a server, but see strict readers | 3 |
| Test seam and test fixes | None | 8 |
| Overlapping sends | None when sends do not overlap; overlapping ones no longer corrupt a frame | 1 |

## Per change

Grouped by commit, in branch order. Row labels are those of `T001-candidates.tsv` and T003.

### `30e6ba71` Allow a client and a handler to be built without a socket.

- **Packets:** none. **Symptom:** no test could build a client (`ClientHandle` is a sealed struct).
- **After:** protected constructors, virtual `SendRaw` and `Close`, `server?.Database`. **Who:** none.
- **Risk:** low; a subclass may now override `SendRaw`/`Close`. Needed by every recording-client test, so it cannot be dropped alone.
- **Verified:** whole suite. **Not run:** nothing specific.

### `ab34e8ea` Send one response when a request handler reports an error. (F06)

- **Packets:** every RES whose handler throws `ResponseErrorException`; 329 throw sites (T001).
- **Symptom on `develop`:** 2 RES. The client has no pending check (`0x844be0`, `0x878860`), so its handler runs twice. An ordinary error shows one dialog, since the queue drops the duplicate (`0x13ef380`). Where the client set the once flag (`0xc77fd8` for 8.6.1, table in T003), the second RES shows the dialog it meant to hide.
- **After:** 1 RES. A critical error still sends its RES and closes. **Who:** all players who meet a handled error.
- **Risk:** low. Nothing read needs a second RES. T003 did not read 90 of the 95 handlers with code after the status call, nor the 33 with no call; a second run was never needed by those read.
- **Verified:** tests; live on 0.7.2 and 8.8.2: `develop` 2, branch 1, one dialog each, and the session continues after 0.7.2. `develop` also gave 2 on 16.0.2 and 18.0.2.
- **Not run:** the once-flag path, the one user-visible gain. It stays **read only**: Pawns and Pawn Order were greyed on that database, so no site was reached.

### `751b6ad4` Answer a request when its response can not be written. (F07, F08)

- **Packets:** any RES on a not-implemented path (only `QuestStateManager.cs:1637` throws it), a serializer failure, a frame over the limit.
- **Symptom:** no RES, so a 45 s timer (`I` for the unit), dialog 33001 and a disconnect, no retry (`0x8855a0`).
- **After:** 1 RES with `NOT_IMPLEMENTED` or `FAIL`. New public members `Client.SendResponse`, `Client.TrySend`; `Send` keeps its behaviour. **Who:** a player on one of those paths: rare.
- **Risk:** low. A handler that sends its own RES and then throws still gets a second one: not surveyed.
- **Verified:** tests; T005 read `TcpServer.Send(null)`, so the queue test is sound. **Not run:** live.

### `e210142c` Answer every request on a handler that had no request base. (D06)

- **Packets:** 11.x quest leader progress, `CreateCharacter` on login 5.x. 5 other handlers pinned unchanged.
- **Symptom:** an exception before the RES meant the same 33001 disconnect (`V` on the game connection, T003; `I` for login `CreateCharacter`, whose dispatch `0x88aab0` was not read). A failed `CreateCharacter` sent Result 1, went on writing rows for a character that does not exist, then sent Result 0.
- **After:** an error RES; a failed creation answers once and stops. **Who:** a leader with a null party; a failed character creation.
- **Risk:** **saved data**: this is the one commit that writes fewer rows on a failure path. The Result 1 branch has **no test** (needs a whole asset repository): read only.
- **Verified:** tests on the other paths. **Not run:** Result 1 branch, live.

### `c75ac712` Register the serializers for CDataOcdImmuneLv and CDataSwitchStorage. (D01, R01, D02, F10)

- **Packets:** 35.9.16 `C2S_CONTEXT_SET_CONTEXT_NTC` and what nests the list; 10.13.16 `S2C_SWITCH_STORAGE_NTC`.
- **Symptom:** a list of these wrote a count and no elements and read no bytes. A non-zero count misaligned the rest of the packet. **35.9.16 with immune count `0xFFFFFFFF` at body +178 looped `List.Add(null)` on the default single lane, with no login needed: out of memory at 512 MiB in 675 ms** (T002, child process).
- **After:** the count ends at the end of the data with `EndOfStreamException`. An entity with no serializer throws. 10.13.16 agrees on 2 of 2 captures. **Who:** none in normal play (0 of 763 captures have a non-zero count).
- **Risk:** low: an independent walk found 0 entities named and not registered (T005a, 2,884 files), and only `WriteEntity`/`ReadEntity` throw.
- **Verified:** tests, differential, **live**: 1 frame then 200 in 23 ms, no stall, the real client stayed answered, a new login's challenge took 86 ms.
- **Not run:** `develop` live, on purpose. Open: see R01 under "Open risks".

### `2e283e93` Close a connection whose stream can not be followed, and keep split frames. (F01, R02, R03)

- **Packets:** all, at the frame level.
- **Symptom:** F01: a TCP split inside a length prefix after a frame over 16 bytes rewound into ciphertext and desynchronised the session; a split right after the prefix of a 16-byte frame lost the prefix. **R02, no login needed:** a length not a multiple of 16 threw an exception the kick path did not expect; no close, the factory stuck, the buffer grew. R03: a length under 16 or a bad source byte logged and read ciphertext as a frame start.
- **After:** split frames reassemble. Bad frames close: see "Close cases". **Who:** F01: any player whose TCP segments land that way. The rest: no real client.
- **Risk:** a close is new behaviour, and R03 rests on **captures only**: the client's writer of the source byte was not read. Byte 4 is 0 on every client frame with a header (116,354 + 44 + 1). CLI: one change, a length not a multiple of 16 logs and goes on instead of ending its run.
- **Verified:** tests (split at every offset, both servers); T005 replay of 125 streams, 116,523 C2S packets, 0 closes; 130,521 packets at random and 1-byte splits, 0 mismatches; **live** R02 and R03 on login and game: orderly FIN, real client unaffected.
- **Not run:** F01 on a live socket. `_buffer` resets only on a frame boundary, so a session whose reads always end mid-frame keeps growing it: noticed, not measured.

### `b48dca89` Bound the lengths a client supplies and the frames a server sends. (R04, R06, R07, F03)

- **Packets:** 3.3.16 `C2S_LOBBY_LOBBY_DATA_MSG_REQ`, 6.23.16 `C2S_PARTY_SEND_BINARY_MSG_ALL_NTC`, 6.25.16 `C2S_PARTY_SEND_BINARY_MSG_NTC`; 1.0.2, 44.0.2; any frame near the limit.
- **Symptom:** R04: a length of -1 threw, `0x7FFFFFFF` threw `OutOfMemoryException`, one past the end returned short and was relayed. The lobby half of R04 and R06 (a password size over 64 from the client) need no login. R07: with `LogIncomingPacketStructure` on, logging a malformed packet threw into the networking library. F03: a body of 65511 to 65524 threw after using a counter; over that, `SendRaw(null)`.
- **After:** a bad length is a short packet with a log line; nothing relayed. Padding stops at 0. The log failure is caught per packet. An over-long frame is not sent and uses no counter. **Who:** none in normal play.
- **Risk:** R04 rests on **captures only**: writers not read. 3.3.16 66,275, 6.23.16 8, 6.25.16 34,607 read with no throw.
- **Verified:** tests, replay. **Not run:** live; PC writers of those three.

### `df93c60d` Key packet ids by group, id and sub, and stop sharing a SHA1 instance. (F11, F12)

- **Packets:** the id tables; the certificate hash in 1.1.16 and 44.1.16.
- **Symptom:** F11: id tables keyed by a per-process seeded `HashCode.Combine`; a collision among the game ids would stop a start, or an unknown id resolve wrongly, about 3.7e-4 per start (`I`), at any lane count. Recounted from `PacketId.cs` at the head: 1,778 declared with `ServerType.Game`, and 1,779 in the game table, which also holds `UNKNOWN`. T001's numbers are the same two, and 3.7e-4 holds for either. F12: a shared `SHA1`, not thread safe; the client checks the hash and disconnects on a mismatch (`0x886b5b`-`0x886b6a`). At the default 1 lane it cannot occur, and that sentence is F12's only.
- **After:** a tuple key; `SHA1.HashData`. **Who:** none at the default.
- **Risk:** very low. F12's test fails on `develop` at its reflection check: **no wrong hash was ever observed.**
- **Verified:** tests; certificate hash accepted live. **Not run:** the concurrent loop on `develop`.

### `64db1373` Close the session after a failed challenge. (R05; carries the fix of T005 F1)

- **Packets:** 1.0.1, 1.0.2, 44.0.1, 44.0.2.
- **Symptom:** **no login needed:** a failed RSA decrypt threw inside `SetCamelliaKey(null)`, so the error branch could not run: a `FAIL` RES under the fixed key, the connection open, and the session went on under that key, reaching every handler that needs no character (T001).
- **After:** key set only on success; one error RES under the fixed key, then close. A key under 32 bytes fails (the client encrypts 48: `0x88aecd`, `0x88afbb`, 125 of 125). **Who:** no real client.
- **Risk:** this check broke every real client at an earlier head (T005 F1), caught by review. It is now pinned by mutation: `!=` fails 6 tests, removal fails 7. The commit message, as pushed, says "under 32 bytes".
- **Verified:** tests, a real socket test, **live**: 3 of 3 on each port, 96-byte RES then orderly FIN; a key of 48 stays open.
- **Not run:** nothing specific.

### `89148f72`, `8b8385c9`, `c8870ac3`, `7d84bbef`, `66bb114e`, `9e11b91e`, `64c676b9`: tests only

`TestBase` could kill the Debug test host on a late log line; a capture helper; a warning in Release; a test that compared the wrong bytes; 48-byte challenge tests with a socket; dead seam tests; one fixture. `66bb114e` adds the constant `Challenge.ClientCommonKeySize` to production, unused by a server. **Who:** none. `89148f72` should stay: without it the suite is flaky.

### `909b92a6` Send the category with each completed achievement. (W02)

- **Packets:** 27.8.16 `S2C_ACHIEVEMENT_ACHIEVEMENT_COMPLETE_NTC`.
- **Symptom:** the client reads {u32, u8} (`0x758720`); the u8 fell on padding, read 0, so the branch for category 6 (`0x7c2f80`) never ran.
- **After:** the byte is the asset's category, the byte `0x7c2f80` branches on. **That the one-element notice the server sends shows the banner is not established**: see Verified. **Who:** a feature, if so: 19 assets of category 6.
- **Risk:** low. Enum values match: 19 of 19 captured replies; 8 of 8 completions. An offline catch-up could queue many: `0xb67c50` scans 16 slots and is bounded by reading.
- **Verified:** tests, **live** by pushed notices, once each: a one-element notice with 6 gave a chat line with a menu open, and no banner was checked; a two-element notice with 6 first gave a banner and two chat lines; a one-element notice with 0 gave a chat line only. So the control has the same visible result as the form the server sends, and the one banner came with another count and id: "the byte decides" rests on the reading of `0x7c2f80` and that one run.
- **Not run:** earning one in play; the catch-up flood.

### `fc793694` Send the quest play time where the client reads it, in whole milliseconds. (W16, N1)

- **Packets:** 11.45.16 `S2C_QUEST_PLAY_END_NTC`.
- **Symptom:** time in the 4th u32, which nothing reads; the 7th read 0, formatted empty (`0xbd4b56`, `0x4cf380`). And `.Milliseconds`, the 0-999 part.
- **After:** whole milliseconds in the 7th, clamped to u32. **Who:** a feature, wherever the client shows it: not known.
- **Risk:** low; only this handler sets the field; read of `0x4cf380` is safe up to `uint.MaxValue` (`71582'47''29`).
- **Verified:** capture holds 1,045,461 there; tests; **live** only that the frame reads safely at 1,045,461, 6,000,000 and 4,294,967,295.
- **Not run: W16 was not seen live.** No quest was finished, nothing appeared in the 4 s watched. `0x4cf380` has one direct call site, `0x4d0285`, which looks like a timed notice on a countdown and not a result screen (`I`). The screen and the over-99-minute format are unconfirmed.

### `dae73ac2` Cap an MtString at what the client can read, and write null as empty. (F09)

- **Packets:** every S2C with an MtString.
- **Symptom:** `0x8bc5b0` fails above 0x800, which ends the recipient's session. **After login, chat, mail and pawn comment text is relayed with no cap, so one player could disconnect another**, once per read for stored text (`T004a`). A null threw.
- **After:** at most 0x7FF bytes, whole characters. Null is length 0. **Who:** none in normal play: longest string in the streams 587 bytes, in assets 207, and re-encode is equal on every capture.
- **Risk:** low. Whether the unmodified client can send that much was not read.
- **Verified:** tests, differential. **Not run:** live; storage of mail bodies not traced.

### `f9e2bae9` Write the login response flag as the bool the client reads. (W01, N2)

- **Packets:** 0.1.2 `S2C_CONNECTION_LOGIN_RES`.
- **Symptom:** u16 for a bool: the token read as length 0, and every login works only because `0x7ce490` uses neither. Setting the flag true on the u16 would have asked for 256 bytes and disconnected.
- **After:** a bool, and 1 byte less. The token arrives, unused. **Who:** all players; same behaviour.
- **Risk:** every game login passes here. The flag stays false where captures have 1 on 42 of 42, as nothing says what true means.
- **Verified:** capture, **live** login.
- **Not run:** the flag set true; any other client build.

### `14ba8537` Send the count of error messages still to come. (W03)

- **Packets:** 3.0.16 `L2C_GET_ERROR_MESSAGE_LIST_NTC`.
- **Symptom:** no trailing u32; padding or a failed read, both ignored (`0x887070` returns 1). **After:** the count, 4 bytes more per frame; the client only reserves capacity. **Who:** all players; same behaviour.
- **Risk:** every login passes here. **Verified:** captures (410 of 410), tests, **live** login. The handler test uses synthetic messages. **Not run:** any other client build.

### `2db00761` Write the last field of the game session key response as a u16. (W04)

- **Packets:** 2.1.2 `L2C_GET_GAME_SESSION_KEY_RES`.
- **Symptom:** u32 where the client reads u16 and ignores it. **After:** 2 bytes fewer. **Who:** all players; same behaviour. **Risk:** every login passes here; `Unknown` changes C# type, with no other user. **Verified:** 42 of 42 captures, **live** login. **Not run:** any other client build.

### `31c84a39` Read and write the 62-byte password block of the challenge as the client does. (W10, W11)

- **Packets:** 1.0.1, 44.0.1, 1.0.2, 44.0.2.
- **Symptom:** the login reader stopped at the first 0, the game reader at the size, both writers sent 64. Harmless by luck: a real block has its size.
- **After:** u8[62] each way; only `PasswordEncSize` bytes decrypted. 2 bytes shorter; frame stays 96. **Who:** all players; same behaviour.
- **Risk:** **every connection passes here.** Annotated dumps now print the whole block, including 46 stale client bytes. **Verified:** 125 of 125 frames of 336, 96 on the response, block identical; tests; **live** login. **Not run:** any other client build.

### `0aedc8bb` Give the third list of a craft progress the element the client reads. (W12)

- **Packets:** 30.0.2 `S2C_CRAFT_GET_CRAFT_PROGRESS_LIST_RES`.
- **Symptom:** {u32, MtString} where the client reads u32 (`0x75e8e0`); the list is always sent empty. **After:** nothing on the wire. **Who:** none. **Risk:** a property changes C# type; one writer. **Verified:** test with a synthetic element; no capture holds one. **Not run:** live; a filled list.

### `5e2fa4c9` Write the level of a soul ordeal buff reward. (62.33.2)

- **Packets:** 62.33.2 `S2C_SEASON_DUNGEON_GET_SOUL_ORDEAL_REWARD_LIST_RES`.
- **Symptom:** `BuffId` twice where the official server sends a level; no consumer reads it (`0x781fb0`'s 5 callers). **After:** `Level`; no client effect. **Who:** none. **Risk:** none seen, as nothing reads the field. **Verified:** 21 of 21 re-encode. **Not run:** live.

### `f2dace3c` Move the clan notice flag from the response to the request. (31.17)

- **Packets:** 31.17.1, 31.17.2 `C2S`/`S2C_CLAN_CLAN_SETTING_UPDATE`.
- **Symptom:** an excess byte in the RES, unread; the request's bool not read. **After:** 1 byte fewer; read and unused, since storing it is a feature. **Who:** all players; same behaviour. **Risk:** see strict readers below. **Verified:** captures, **live** login. **Not run:** any other client build; storing the option.

### `059cb593` Read the fields the client writes at the end of five notices and requests. (W08, W09, W14, 11.60.16)

- **Packets:** 14.11.16, 0.1.1, 0.5.1, 50.1.1, 11.60.16.
- **Symptom:** the server stopped early; handlers do not use the fields. **After:** the whole packet read; annotated dumps and the CLI see it. **Who:** none on a PC 03040008 client.
- **Risk: strict readers.** A client that sends less than this build writes (another build, a modified client, a PS3 or PS4 `PlatformType`) now gets `EndOfStreamException` on 0.1.1, 0.5.1, 14.11.16, 50.1.1, 11.60.16 or 31.17.1 where it passed. 0.1.1 is every login. Names `StartPointId`, `IsReturnSession` are inferred.
- **Verified:** 42, 41, 57, 59, 7, 42 captured reads with no throw; **live** 0.1.1, 0.5.1. **Not run:** any other client build.

### `b9883379` Keep what two response readers read. (W17, 11.4.2)

- **Packets:** 13.16.2, 11.4.2. **Symptom:** lists read and dropped, so the CLI re-encoded empty ones. **After:** kept. **Who:** none: the server never reads these from a client at run time. **Risk:** none seen; only what the CLI re-encodes changes. **Verified:** re-encode 1 and 20. **Not run:** live: no server path reads them.

### `54139fae` Stop reading a response at its Error, as the client does. (F05)

- **Packets:** every RES read with `Error != 0`; captured on 13.3.2, 18.0.2, 19.1.2, 19.2.2.
- **Symptom:** `ReadServerResponse` read a u16 and then fields past the frame: `EndOfStreamException` on all 63 captures. Server structures write Result as u32 and the client stops. **After:** a private `ResponseEndsAtError` caught in `ReadPacket`; `Result` stays 0. **Who:** none: the server does not read a client's RES at run time.
- **Risk:** a direct `Read(IBuffer)` on an error RES lets it escape: 2 of 851 canned dumps do (18.0.2), and production reads neither. A client sending an S2C id with Error set costs one caught exception per frame, as `develop` did.
- **Verified:** 63 of 63, 851 dumps both ways (T005a). **Cost not measured. Not run:** live: no server path reads them.

### `bc3dc199` Keep overlapping sends to one client from corrupting its frames. (F04)

Not pushed yet: the coordinator pushes.

- **Packets:** all, on one connection.
- **Symptom:** `Client.Send` runs on the lane thread and on timers such as `PingRequestPacketHandler.cs:24-36`, so two sends to one client can overlap at the default of one lane. Each `PacketFactory` has one `_t8Encrypt`, which every Camellia round writes, and `_packetCount++` had no lock. An overlap gives a frame that decrypts to garbage. How often that happens in play was not measured.
- **After:** one private lock, held twice in a send: around the count and inside `Encrypt`, which `Write` and `WriteDataWithLengthPrefix` both call. Bytes unchanged from one thread. **Who:** a player whose send meets a timer's.
- **Not one span, and no socket inside:** `Encrypt` copies the fixed IV for every frame, so a frame's cipher state does not depend on the frame before it. The client does not compare the counter (T003 F04, `V`). `TcpServer.Send` copies each frame whole into the client's send queue under a lock (Arrowgene.Networking 2.1.7, source at the commit the package names, `4998646c`, `Client.QueueSend`, `ArenaBackedSendQueue.Enqueue`). So frames need no order here, and two overlapping frames may leave in either order, as before.
- **`SetCamelliaKey` is outside the lock, and needs no lock:** `TrySend` writes nothing but the challenge's own response until `_challengeCompleted`, the handlers write that response on the thread that set the key, and `HandleChallenge` clears `_challenge`, so a second challenge throws before it reaches the key. `Decrypt` shares the subkey and has its own scratch, on the receive path: not touched. `Camellia` itself is static and holds only read-only tables, so factories share nothing else. Not touched: a `Packet` object sent to several clients gets its `Count` written by each, as on `develop`.
- **Risk:** low. A send holds the lock for a frame's encryption. Cost not measured.
- **Verified:** `PacketFactoryWriteTest`, in the suite (180 of 180 Debug and Release, 520 warnings), its 3 tests about 4 s together. Mutations, 10 runs each, restored after: no lock at all, 10 of 10 fail, with 11,894 to 11,999 of 12,000 frames wrong; no lock on `Encrypt` only, 10 of 10, 11,937 to 11,996 wrong; no lock on the count only, the frames test failed 7 of 10, so a test of its own was added, which fails 10 of 10 with 2 to 8 counts lost of 400,000. With the lock: 15 runs, none failing. Frames from one thread are pinned against bytes printed by the code before the lock.
- **Not run:** live; the differential and the replay at this head (the pin stands in for them); a corrupted frame against a client, whose outcome is inferred: garbage header, no record, 3001 (T003).

## Behaviour a running server newly has: the four close cases

It closes a connection it left open before, when:

1. A frame length is under 16 or not a multiple of 16. Before: under 16 logged and read on; not a multiple threw on every later read, with a growing buffer.
2. A decrypted frame's source byte is neither 0x00 nor 0x34. Before: logged and read on.
3. Anything else throws out of `PacketFactory.Read`. Before: logged, connection open.
4. A challenge fails: RSA or Blowfish failure, or a session key under 32 bytes. One error RES goes out under the fixed key first. Before: a `FAIL` RES, and the session went on.

Packets decoded earlier in the same read are still handled in 1 and 2. Later data on a closed connection is dropped. It closes nothing else it did not close before. Case 1, 2 and 4 were seen live; **case 3 was not provoked live**: it rests on the code and on tests. No real client is expected to reach any of them: the replay of 125 streams gave 0 closes, and all 125 captured first frames put 48 bytes under RSA.

## `packets/decrypted_annotated/` if the CLI re-runs

**Not re-run over all streams.** The patched CLI was built on the branch in a scratch clone (Debug, `Arrowgene.Ddon.Cli` project, 0 errors, 508 warnings) and run on 3 streams, compared with the committed dumps. Same packets and same id order on all three. Only `StructDump` lines of the ids below change.

| Stream | Packets | Changed `StructDump` | Ids |
| --- | --- | --- | --- |
| `stream31-loginfail` tcp-stream-12 | 28 | 6 | 0.1.1, 0.1.2, 31.17.1, 31.17.2, 44.0.1, 44.0.2 |
| `stream31-loginfail` tcp-stream-13 | 306 | 4 | 0.5.1, 14.11.16, 44.0.1, 44.0.2 |
| `stream3-party-experiments` tcp-stream-47 | 719 | 6 | 0.5.1, 13.16.2, 14.11.16, 44.0.1, 44.0.2, 50.1.1 |

Examples: 0.1.1 gains `ClientVersion`; 0.1.2's token stops running into padding; 31.17.2 loses an `IsMemberNotice` that read padding; 13.16.2 gains its list; 44.0.2's `PasswordEnc` shows all 62 bytes.

Predicted for the rest, from the differential's per-id table (`T004b-per-id.tsv`), **not observed in a dump**: 1.0.1, 1.0.2, 2.1.2, 3.0.16, 10.13.16, 11.4.2, 11.45.16, 11.60.16, 27.8.16. Predicted unchanged: 62.33.2 (its reader was right) and the four error RES (the CLI patch's guards already stopped there). F01 could add packets on a stream that once split inside a prefix: none in these 3, and the other streams not run. `packets/decrypted_raw/` names do not change, as the name hunks stay in. Nothing needs regenerating unless someone wants the dumps to follow the fixes.

## `packets/tools/arrowgene-cli.patch`

`git apply --check` on `fix/packet-handling`: **exit 0, all 16 hunks apply**, the 7 of `PacketId.cs` at an offset of -2 lines. The clone's tree stayed clean. It also builds on the branch (above).

| Hunks | File | Still needed? |
| --- | --- | --- |
| 5 | `Arrowgene.Ddon.Cli/Command/PacketCommand.cs` | Yes: first packet under the fixed key, certificate relabel, one file per packet, debug log, header-less raw. The branch changes none of these |
| 4, 1 each | `S2CGroupChatGetMemberListRes.cs`, `S2CInstanceEnemyKillRes.cs`, `S2CSkillGetAcquirableSkillListRes.cs`, `S2CSkillGetAcquirableAbilityListRes.cs` | **No, once the branch lands.** `ReadServerResponse` throws before each guard runs, so the line is dead code (by reading; not run with the hunks removed). Harmless left in |
| 7 | `Arrowgene.Ddon.Shared/Network/PacketId.cs` | Yes: the branch makes no renames, and raw file names depend on these 8 |

`docs/reference/arrowgene-cli-patches.md` describes the patch against `develop` and was left so: it changes when the branch lands, not before.

## Candidates not patched

| Id | What | Why not |
| --- | --- | --- |
| F02 | Padding 1 to 16, official 0 to 15 | Real risk and no client benefit: a frame on a block boundary would leave a short layout no spare byte, and a read past the end disconnects (T003) |
| W05 | 62.1.2: first and third u32 crossed against captures | Harmless today: the server has no 62.5.1 structure and ignores 13.17.1's value. 40 is known for dungeon 3 only, so the fix's value is not known |
| **W06** | 19.28.2 `CDataNormalSkillParam` Index and SkillNo | **Not an error, and a swap is unsafe**: `+8` is the 1-based slot the client indexes with, as the server sends it (`0x4889e0`) |
| **W15** | 13.x `CDataStageLayoutEnemyPresetEnemyInfoClient` RepopCount and RepopNum | **Not an error on the wire, and a swap is unsafe**: `+27` is a gate, `+28` a variant index; the assets are written for that order, and a swap would turn gates off and make 50 an index |
| W21 | 20.x `HideRequirementDetails`, never set | Nothing to fix: all 1,443 goods of `Shop.json` have an empty requirement list (`Unk7`, which would not bind to `Requirements` anyway), so the flag never reaches a client. Captures have it true on 45 of 45 entries, 27 distinct; 26 of those are on shop 230 goods `Shop.json` does not hold. The data is the gap: a feature |
| W22 | 11.10.2 bool order | Not an error: `0xed89f0` fits the server's order; `+356`, `+360` not traced |
| D08 | Login 5.3.16 `ServerResponse` | Not an error: reader `0x889600` has no guard, and "Result" is the character id the client stores |
| T05 | 11.13.2 name | Not an error: shape agrees over the 13 fields compared, name only; list is empty |
| R08 | An RSA-2048 key per connection on the consumer lane: **CPU cost with no login** | Design, not parsing. A shared key changes the certificate behaviour; cost not measured. Report only |
| Renames | `HideRequirementDetails`, `IgnoreRequirements`, `Unknown`, W06's and W15's names, 8 `PacketId` names (14.10.16 is `C2S_WARP_END_NTC`) | Out of scope by the spec; follow-ups in the PR |
| W07 | 10.14.16: `Unk1` is the list count, and both senders set 1 | Report only: the bytes equal the client's for one element, 1 of 1 capture. Sending two is a refactor nobody needs today |
| W13 | 28.x `CDataGPCourseAvailable`: PS4 layout where PC reads another | Dead code: only its own file and its `Create` line name it, and captures have the lists empty |
| W18 | 13.x `C2SInstanceGetGatheringItemReq.EquipToCharacter` read as a byte, written by PC as a bool | Not an error: same width |
| W19 | 34.0.1 `C2SEntryBoardEntryBoardListReq` | Refuted: the "differs" came from a wrong PC shape in spec 008; the server's list of `CDataCommonU64` agrees, 1 of 1 capture |
| W20 | 45.x `CDataStampBonus` `BonusType`, `BonusValue` | Refuted as a server fault (`I`): same 3 u32 in the same order; the lead was about the pattern's names |
| D03 | `S2CSwitchStorageNtc` on 5.2.16, where PC reads another list | Dead code, unregistered and unreferenced: no behaviour |
| D04 | `S2CQuestBoardReloadNtc`, `S2CQuestQuestEnableNtc`, `S2CPartyPartyQuestProgressNtc` | Dead structures, with no server sender: not worth a patch |
| D05 | `LoadingInfoLoadingGetInfoHandler` declares `C2SConnectionGetLoginAnnouncementReq` for 43.0.1 | Works: the consumer keys on the override, and neither request reads anything. Very low value |
| T03 | 11.58.16 is named `C2S_...` and is server to client | A rename only, out of scope by the spec. The source in the table is right |
| T07 | 73.0.16, 73.1.16, 35.8.16 absent from the table | Unimplemented, out of scope. 35.8.16 from a client falls to `FallbackHandler`, which ignores non-REQ |
| Central login gate | No base handler refuses a packet before login: a handler fails only when it touches a null `client.Character`. T001 read the bases, not the 517 bodies | A design change for the maintainers, reported only (brief T004a). **Not in the PR body**: it is a statement about what is reachable before login. Which ids belong before login is in T005b's sequence of 40 |

Also open and outside the patch: N3 (6 table ids with no PC record: none is sent; `#if false` at `Quest.cs:1036` should stay), N4 (62.5.1 falls to `FallbackHandler`), N5 (a non-zero Result is an error to the client, not surveyed), 63.11.16 (the one remaining `values differ`, sender under `#if false`).

## Open risks

- **RES lost to a reset at a close.** A RES is lost if the client is still sending when the server closes: 0 of 20 delivered on Windows loopback, against 20 of 20 otherwise. Not fixed: the library has no flush, and a timer leaves open a socket we meant to drop. A failed challenge cannot meet it with a real client (0 client frames between request and RES on 125 of 125). A critical error in a session can, as on `develop`: the client is disconnected either way, only without the specific dialog. Non-Windows not run.
- **R01's sender stays open.** A frame that fails in a structure read logs one caught exception and a stack trace (60 log lines each), with no limit and no close. 201 frames took the second they arrived, with no stall. So a logged-out flood costs log volume and CPU. Not a defect of the brief; a decision for a next package.
- **R03, R04 on captures only.** The PC writers of the source byte and the three s32 lengths were not read.
- **Every live run used executable f2a8, not f1c9.** The addresses here were read in the dump f1c9 (`2022_01_29_DDO_DUMP_FIX.exe`); the runs used the installed `C:\DDON\DDO.exe` f2a80229, title `03.04.007 : 3040008`, the build players have. So what they show is on the players' build, and no run was on the dump.
- **W16 not seen live**, see its commit.
- **The live watch for 3001 and 33001 has limits.** T005b looked at frames, not every moment, and its log is server side: a client-side 3001 shows there only as a disconnect. None was seen on any frame looked at. One client exit, at 13:47 on the lab build, after `ERROR_CODE_AUTH_MULTIPLE_LOGIN` left by the test set-up, is **unexplained**: no WER event, no exception log, no dump looked for.
- **The banner**, see `909b92a6`: seen once, on a two-element pushed notice.
- **Once-flag path not reached**, see F06. **So the suppressed dialog, the user-visible gain of F06, is read only.**
- **Strict readers**, see `059cb593`: only PC 03040008 was tried.
- **The migrated database.** Every login on both branches logged `no such column: ddon_pawn.craft_exp` on a copy migrated from 54 to 68. Not from the patch, and not investigated; it may be why Pawns was greyed.
- **The branch's own text.** T006a took the reproduction detail out of the commit messages and comments before the push. `SerializerRegistrationTest.cs` and `ClientSuppliedLengthTest.cs` still show the shape of a count in their bodies with the packet named, as the fixes do against `develop`: Sam's call (T007b finding 2).

## Dropping a commit

Each commit tested with `git show --format= --binary <c> | git apply -R --check` at the head, in the clone (its tree stayed clean). The 15 production commits that reverse cleanly were then reversed one at a time in a scratch clone, with their own tests and fixtures, and built and tested in Debug. The head itself gave 177 of 177 there.

| Result | Commits |
| --- | --- |
| Suite passes (11) | `e210142c` 172, `c75ac712` 172, `909b92a6` 174, `dae73ac2` 168, `f9e2bae9` 175, `2db00761` 176, `0aedc8bb` 175, `5e2fa4c9` 176, `059cb593` 172, `b9883379` 175, `54139fae` 171 |
| Builds, tests of later commits fail (4) | `751b6ad4` 4 of 170 (`A_body_over_the_u16_length_is_not_sent`); `df93c60d` 1 of 172 (`A_session_key_too_short_is_a_failed_login_challenge`, not looked into: perhaps the shared `SHA1` under parallel tests, `I`, which would be the wrong hash never yet observed); `31c84a39` 3 of 171 (from `66bb114e`); `f2dace3c` 1 of 175 (`A_response_without_an_error_reads_on`) |
| Reverse-apply conflicts (8) | `30e6ba71`, `ab34e8ea`, `2e283e93`, `b48dca89`, `64db1373`, `fc793694`, `14ba8537`, `89148f72` |

Test-only commits were not dropped and built. A passing suite does not say a drop is wise: dropping `c75ac712` removes its own guard with the fix. These runs were at `64c676b9`. At `bc3dc199` the same check gave the same 15 clean and 8 conflicts, not rebuilt; reverting `bc3dc199` gives the tree of `64c676b9`. To drop one: `git revert <sha>`, `dotnet build`, `dotnet test`.

## Not run

- Nothing is missing from `dotnet test` at `bc3dc199`: 180 of 180 and 520 warnings, Debug and Release, in the clone. The Debug scratch-clone run above was at `64c676b9`.
- A full re-annotate, and the raw export.
- Building each intermediate commit in order: the drop runs above check from the head.
- The differential on the drop runs.

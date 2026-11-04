Title: Fix packet handling against the 03040008 client

Fixes to how the server frames, reads, writes and answers packets, each checked against the PC 03040008 client. Addresses below are VAs in that client. Evidence is stated per row as one of: read in the client's code, in captures from the official servers, seen live with a real client, or not run.

## What and why

**Requests and responses.** A handled error sent its response twice: the client has no pending check (`0x844be0`, `0x878860`), so its handler ran twice. Some paths sent no response at all, and the client answers that with a timer, dialog 33001 and a disconnect, with no retry (`0x8855a0`). Every request now gets one response.

**Connections.** Frames split across TCP reads now reassemble. The server now closes a connection in four cases: a frame length under 16 or not a multiple of 16; a decrypted source byte other than 0x00 or 0x34; any other exception out of `PacketFactory.Read`; a failed challenge, after one error response under the fixed key. In the first two, packets decoded earlier in the same read are still handled. Lengths a client supplies are checked against the bytes left.

**Layouts the client acts on.** The category in 27.8.16, so a category 6 achievement now shows its banner, and the quest play time in 11.45.16. An `MtString` is never written longer than the client's reader takes (`0x8bc5b0`).

**Layouts the client does not act on.** These change bytes and no behaviour, and each has its own commit, so that the wire matches the client and a later change can trust it.

**Readers.** The server now reads the whole of what the client sends, and response readers stop at a non-zero `Error` as the client does. This matters to the CLI's annotated exports and to tests. The server does not read responses at run time.

## Changes

| Commit | Packet | What a client sees | Risk |
| --- | --- | --- | --- |
| Send one response when a request handler reports an error. | Any RES whose handler throws `ResponseErrorException` | 1 RES, where `develop` sends 2; 1 dialog on both, seen live on 0.7.2 and 8.8.2. Where the client set its suppress-once flag, the dialog stays hidden: read at `0x878860`, not seen live | Low. Nothing read needs a second RES; not every handler body was read |
| Answer a request when its response can not be written. | Any RES on a not-implemented path, a failed serializer or an over-long frame | An error dialog in place of 33001 and a disconnect. Read in the client; tested; not run live | Low |
| Answer every request on a handler that had no request base. | 11.x quest leader progress, login `CreateCharacter` | The same, and a failed creation answers once and writes no further rows. **The failed-creation branch has no test** | Medium for saved data on that path only; read only |
| Register the serializers for CDataOcdImmuneLv and CDataSwitchStorage. | Lists of those types; 10.13.16 `S2C_SWITCH_STORAGE_NTC` | Lists of both types read and write their elements. An entity with no serializer throws. 2 of 2 captures of 10.13.16 now agree | Low: no entity in the code is named and unregistered |
| Close a connection whose stream can not be followed, and keep split frames. | All | Nothing in normal play: split frames keep their place | A close is new behaviour. The source byte rule rests on captures: 0 on every client frame with a header. Seen live: only the bad connection closes |
| Bound the lengths a client supplies and the frames a server sends. | 3.3.16, 6.23.16, 6.25.16; 1.0.2, 44.0.2; any frame at the limit | Nothing in normal play. A length that does not fit reads as a short packet; a frame over the limit is not sent and uses no counter | Rests on captures: 66,275, 8 and 34,607 reads with no throw. Client writers not read |
| Key packet ids by group, id and sub, and stop sharing a SHA1 instance. | The id tables; the certificate hash | Nothing at the default single lane. The client does check that hash (`0x886b5b`) | Very low. No wrong hash was ever observed: the change rests on `SHA1`'s contract |
| Close the session after a failed challenge. | 1.0.1, 1.0.2, 44.0.1, 44.0.2 | Nothing for a real client: it puts 48 bytes under RSA (`0x88aecd`, 125 of 125 captures), and under 32 now fails. Seen live: one response, then an orderly close | Every connection passes here. Good path tested on a real socket and live |
| Send the category with each completed achievement. | 27.8.16 `S2C_ACHIEVEMENT_ACHIEVEMENT_COMPLETE_NTC` | The banner of a category 6 achievement (`0x7c2f80`). Seen live with a pushed notice; earning one in play not run. Enum values match: 19 of 19 captured replies | Low |
| Send the quest play time where the client reads it, in whole milliseconds. | 11.45.16 `S2C_QUEST_PLAY_END_NTC` | The time goes in the 7th u32, which the client keeps and formats (`0xbd4b56`, `0x4cf380`). **The screen was not seen live**: only that the frame reads safely | Low. The value is clamped to u32 |
| Cap an MtString at what the client can read, and write null as empty. | Every S2C string | Nothing for text that fits: re-encode is equal on every capture. Longer text is cut on a character boundary at 0x7FF bytes | Low |
| Write the login response flag as the bool the client reads. | 0.1.2 `S2C_CONNECTION_LOGIN_RES` | Same behaviour; 1 byte fewer. `0x804a50` reads a bool, then the token; `0x7ce490` uses neither | Every game login passes here. Seen live. Captures have the flag as 1 and the server still sends 0, as nothing says what it means |
| Send the count of error messages still to come. | 3.0.16 `L2C_GET_ERROR_MESSAGE_LIST_NTC` | Same behaviour; 4 bytes more per frame. The client only reserves capacity (`0x887070`) | Every login passes here. Seen live |
| Write the last field of the game session key response as a u16. | 2.1.2 `L2C_GET_GAME_SESSION_KEY_RES` | Same behaviour; 2 bytes fewer. Read and ignored (`0x889ce0`) | Seen live |
| Read and write the 62-byte password block of the challenge as the client does. | 1.0.1, 44.0.1, 1.0.2, 44.0.2 | Same behaviour; a response 2 bytes shorter in the same 96-byte frame. All 125 of 125 captured frames have this shape | Every connection passes here. Seen live |
| Give the third list of a craft progress the element the client reads. | 30.0.2 `S2C_CRAFT_GET_CRAFT_PROGRESS_LIST_RES` | Nothing: the list is always sent empty. `0x75e8e0` reads a u32 per element; a filled list would have shifted the reads | A property changes type; one writer |
| Write the level of a soul ordeal buff reward. | 62.33.2 `S2C_SEASON_DUNGEON_GET_SOUL_ORDEAL_REWARD_LIST_RES` | Nothing: no consumer of `0x781fb0` reads it. Matches 21 of 21 captures | None seen |
| Move the clan notice flag from the response to the request. | 31.17.1, 31.17.2 | Same behaviour; 1 byte fewer. Read and unused: storing the setting is a feature | See strict readers below |
| Read the fields the client writes at the end of five notices and requests. | 0.1.1, 0.5.1, 14.11.16, 50.1.1, 11.60.16 | Nothing: handlers do not use them. 42, 41, 57, 59 and 7 captured reads, with no throw | **Strict readers**: a client that writes less than PC 03040008 now fails to read on these and on 31.17.1, and 0.1.1 is every login. Only this client was tried |
| Keep what two response readers read. | 13.16.2, 11.4.2 | Nothing on a server | None seen |
| Stop reading a response at its Error, as the client does. | Any RES read with `Error != 0` | Nothing on a server. 63 of 63 captured error responses now read | Direct `Read(IBuffer)` on such a response sees a private exception; production has no such call |
| Allow a client and a handler to be built without a socket. | None | Nothing: a test seam, needed by the tests above | Low |

Test only:

- Keep a late log line from ending the test run. (Stops the Debug test host dying on a late log line; keep it.)
- Add a helper for tests built from captured frames.
- Declare the test log handler only where it is used.
- Look at the right bytes in the served play time test.
- Test the challenge with the key size the client sends, on both overloads and a real socket.
- Drop two tests that only exercised the test seam.
- Keep one 3.0.16 fixture: both captures carry 50 still to come.

Size: 97 files, 2,688 insertions, 174 deletions: 45 files of production code (452 insertions, 173 deletions), the rest tests and fixtures. Fixtures are real frames, one per packet id, with tokens, keys, RSA blocks, player ids and padding replaced by filler.

## What a client depends on

Read at `0x844be0`, `0x8bc480` and `0x9d6d20` on the game connection: an S2C key the client has no record for, or a read past the frame end, ends the session with error 3001. Padding is inside that limit, so a layout shorter than the client's reader survives only on padding. That is why several rows above were harmless by luck, and why the padding is left alone below.

## How to verify

- `dotnet test Arrowgene.DragonsDogmaOnline.sln`: 177 of 177 in Debug and Release, against 52 of 52 on `develop`. `dotnet build`: 0 errors, 520 warnings, against 521. New tests that pass on `develop` are pins of behaviour that must not change; the others fail there.
- A differential ran the server's serializers over all 160,615 decrypted frames of the official captures, on a local harness that is not part of this branch. 1,544 frames are of ids with no server structure and 63 are error responses; the other 159,008 read with no exception on both:

  | Measure | `develop` | This branch |
  | --- | --- | --- |
  | Re-encoded bytes equal the capture | 158,719 | 159,008 of 159,008 |
  | Reader's length fits the frame | 158,634 | 159,008 of 159,008 |
  | Fields equal a decoding made from the client's code, where comparable | 35,843 of 36,886 | 36,885 of 36,886 |
  | Error responses read | 0 of 63 | 63 of 63 |

  The one left is 63.11.16, whose sender is under `#if false`. Nothing that agreed before differs.
- 125 captured sessions replayed through `Client.Receive`, 116,523 client packets: 0 closes and 0 exceptions. The client streams at random splits and one byte at a time: 130,521 packets, 0 mismatches.
- A live smoke with a real 03040008 client on a local server: login and game-select with the same 40 packet ids in the same order as `develop`, play, a move between worlds (one process posing as two), an error path with 1 response against 2, the category 6 banner. A test client sent malformed frames and a failed challenge: each closed only its own connection, and the real client's session stayed up. No 3001 or 33001. It ran on the installed executable, not on the dump the addresses were read in.
- **Not run live:** the quest end screen; the suppress-once dialog; earning a category 6 achievement in play; a served string at the cap; the paths that formerly sent no response.

Known limit, as on `develop`: a response can be lost to a TCP reset when the client is still sending at the moment the server closes. The networking library has no flush, and captures show no client frame between a challenge and its response.

## Deliberately not changed

- **19.28.2 `CDataNormalSkillParam`, `Index` then `SkillNo`: do not swap.** `0x4889e0` takes the first u32, rejects 0xFF and anything of 0xB or more, subtracts 1 and uses it as the slot. The bytes the server sends are what the client needs. PS4 DWARF calls that field `m_unSkillNo`, so the names are arguable and the wire is not.
- **13.x `CDataStageLayoutEnemyPresetEnemyInfoClient`, `RepopCount` then `RepopNum`: do not swap.** `0x751a06` and `0x752590` read `+27` as a gate and `+28` as a variant index. Assets set `repop_count` for the first byte, and a swap would turn those gates off and make a value of 50 an index. Again, only names differ.
- **Padding of 1 to 16 bytes**, where the official server sends 0 to 15. With 0 on a block boundary, a short layout has no spare byte, and a read past the end disconnects. There is no client benefit.
- 62.1.2 first and third u32, crossed against captures. Harmless while the server has no 62.5.1 structure, and the right value is known for one dungeon only.
- 20.x `HideRequirementDetails`, which nothing sets: no requirement reaches a client at all (below).
- 11.10.2 bool order (`0xed89f0` fits the server's) and 5.3.16's `ServerResponse` base (the client reads s32, u32 with no guard at `0x889600`, and stores the "Result" as the character id). Neither is an error.
- The name of the 11.13.2 structure: its shape agrees over the fields compared, and it is a rename at most.

## Suggested follow-ups

- Renames, each a separate change: the two pairs above; `HideRequirementDetails` and `IgnoreRequirements`; `Unknown` on 2.1.2; 14.10.16 is the warp end notice (PC writer `0x840160` matches PS4 `Send_C2S_WARP_END_NTC` by call site) and 14.11.16 is not; names the client's code backs for 0.10.16, 11.60.16, 11.83.16, 11.95.16, 11.103.16, 11.117.16.
- Shop requirement data: all 1,443 goods in `Shop.json` have an empty requirement list, under `Unk7`, which would not bind to the property `Requirements` anyway. Captures show 45 entries with the flag true on all 45 (`0xf502f0` shows a line only then). Adding the data is a feature, and whoever adds it should set the flag.
- Store the clan notice option the client sends in 31.17.1.
- 62.5.1 has no structure and falls to the fallback handler.
- 2.19.16, 2.20.16, 2.21.16, 11.60.16, 63.11.16 and 11.81.16 have no S2C record in the client: if ever sent, it ends the session. None is sent; the `#if false` at `Quest.cs:1036` should stay.
- A real RES with `Error` 0 and a non-zero `Result` is an error to the client, with a dialog. Not surveyed.
- On a database migrated from version 54 to 68, every login logged `no such column: ddon_pawn.craft_exp`, on `develop` as well. Not looked into.

## Dropping a commit

`git revert <sha>`, then `dotnet build` and `dotnet test`. Tried from the head, with the commit's own tests and fixtures going with it:

- **Whole suite passes without it:** Answer every request on a handler that had no request base; Register the serializers; Send the category; Cap an MtString; the login response flag; the game session key u16; the craft progress element; the soul ordeal level; Read the fields the client writes; Keep what two response readers read; Stop reading a response at its Error.
- **Builds, and tests of a later commit fail:** Answer a request when its response can not be written (4 frame limit cases); Key packet ids and SHA1 (1 challenge case; not looked into); the 62-byte password block (3 challenge cases); the clan notice flag (1 case of the error response test).
- **Later commits touch the same lines, so a plain revert conflicts:** the test seam, which every recording-client test needs; Send one response (it shares lines with Answer a request); Close a connection; Bound the lengths; Close the session; the quest play time and the error message count (their tests were corrected in later commits); the log line fix.

Please build after dropping anything else: the intermediate commits were not built one by one.

# Checklist:
- [x] The project compiles
- [x] The PR targets `develop` branch

🤖 Generated with [Claude Code](https://claude.com/claude-code)

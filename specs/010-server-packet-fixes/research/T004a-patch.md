# 010 T004a: patch part 1, network path, dispatch and robustness

Server: `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Clean`, branch `fix/packet-handling`, head `c423c48be457ce394a6cdd96c97c84ef7423923a`, 9 signed commits on `develop` `e2411fe8f9`, not pushed. Client: PC **03040008** (T003). dotnet 10.0.403. ddon-data base `f1f14ac30eb`. Date 2026-11-04.

No live server or client was run. Every statement about a client comes from T003's reading of the PC code.

## Rows

"Before" is develop plus the seam commit plus the new tests (see Proof). Test classes are in `Arrowgene.Ddon.Test/Server/Network/`, except `SerializerRegistrationTest` (`Shared/Entity/`) and `PacketIdTest` (`Shared/Network/`).

| Row | Commit | Deciding test | Before | After |
| --- | --- | --- | --- | --- |
| seam | `2ec9f649` | `ClientSeamTest` (2) | no client could be built without a socket | pass |
| F06 | `8b4a056f` | `RequestHandlerResponseTest.A_handled_error_sends_one_response`, `A_critical_error_sends_one_response_and_closes` | 2 frames | 1 frame; critical also closes once |
| F07 | `099c2a66` | `Not_implemented_sends_one_response`, `..._in_a_queue_handler_...` | 0 frames | 1 frame, `NOT_IMPLEMENTED` |
| F08 | `099c2a66` | `A_response_that_can_not_be_serialized_sends_one_error`, `A_response_over_the_frame_limit_sends_one_error`, `A_failure_after_the_queued_response_left_does_not_send_a_second` | 0, 0, 2 frames | 1 frame each |
| D06 | `2edc799f` | `RequestOnPlainHandlerTest.Quest_leader_...`, `Create_character_...` | 0 frames | 1 frame, `FAIL` |
| D01 | `9a1d04a8` | `SerializerRegistrationTest.A_list_of_ocd_immune_levels_consumes_its_elements` | not registered | 2 elements, position at the end |
| R01 | `9a1d04a8` | `A_huge_list_count_ends_at_the_end_of_the_data` | stops at its guard: not registered (T002 measured the loop in a child process: out of memory at 512 MiB in 675 ms) | `EndOfStreamException` |
| D02 | `9a1d04a8` | `A_captured_switch_storage_notice_reads_its_element` | null element | {1, 10}, from capture 10.13.16 |
| F10 | `9a1d04a8` | `Every_entity_reached_by_a_registered_serializer_is_registered`, `An_entity_with_no_serializer_fails_loudly` | names `CDataContextSetAdditional -> CDataOcdImmuneLv`; no exception | no entity missing; `InvalidOperationException` |
| F01 | `7ede78a2` | `PacketFactoryReadTest.A_split_at_any_offset_...` (login, game), `A_frame_fed_one_byte_at_a_time_...` (login, game), `A_split_inside_the_next_length_prefix_keeps_the_byte`, `A_split_after_the_length_prefix_of_a_16_byte_frame_keeps_the_prefix` | packets lost or wrong | same packets as one read |
| R02 | `7ede78a2` | `A_bad_frame_length_closes_and_keeps_what_was_decoded` (17, 65535) | packets of the read dropped, no close | packet kept, 1 close |
| R03 | `7ede78a2` | same (0, 15), `A_bad_source_byte_...`, `Nothing_is_read_after_a_bad_frame` | no close | 1 close, packet kept, later data dropped |
| R04 | `ed537824` | `ClientSuppliedLengthTest.A_negative_...`, `A_huge_...`, `A_length_past_the_end_...` (3 readers each) | other exception types; past the end returned short with no exception | `EndOfStreamException` |
| R06 | `ed537824` | `A_large_password_size_can_be_written` | `OverflowException` | written |
| R07 | `ed537824` | `Logging_a_malformed_packet_does_not_escape_receive` | `EndOfStreamException` out of `Receive` | packet returned, no close |
| F03 | `ed537824` | `A_body_over_the_u16_length_is_not_sent` (65525, 70000), `A_notice_over_the_limit_uses_no_counter` | reached `SendRaw(null)`; overflow in the cast | nothing sent, counter unused |
| F11 | `069bc5a1` | `PacketIdTest.The_lookup_is_keyed_by_group_id_and_sub_not_by_a_hash` (2) | key is `int` | key is the tuple |
| F12 | `069bc5a1` | `ChallengeHashTest.The_hash_of_a_certificate_is_right_on_several_threads` | static `SHA1` field found | no such field; 4 threads, 20,000 hashes right |
| R05 | `c423c48b` | `ChallengeTest.A_failed_game_challenge_...`, `A_failed_login_challenge_...`, `A_session_key_of_the_wrong_length_...` (1, 16, 31) | `NullReferenceException` out of the handler code path, no close | 1 error RES, 1 close |
| R05, good path | `c423c48b` | `The_good_path_keeps_its_sizes_and_moves_to_the_session_key` | pass (a pin) | pass: certificate 304 bytes with a correct hash, response 96, next packet under the session key |

## Decisions and departures

- **Seam.** A protected constructor on `Client`, `GameClient` and `LoginClient` taking the identity, `SendRaw` and `Close` virtual, `server?.Database` in `PacketHandler`. `ClientHandle` is a sealed struct, so it cannot be faked. Skipping constructors with `GetUninitializedObject`, as T002 did, leaves `Logger` null, and `~Client` reads it. Two handlers whose constructors read the server (`CreateCharacterHandler`, `LobbyLobbyLeaveHandler`) are still built that way in tests: they have no finalizer.
- **F07, F08.** `client.SendResponse` moved inside the handler's `try`, so a write failure reaches the existing `FAIL` path and still reaches the consumer's log and metric. New public members: `Client.SendResponse`, `Client.TrySend`. `Send` behaves as before for every other caller. `TrySend` returns true for a packet held back before the challenge completes, as that is intended.
- **Beyond the rows, needed for "never two".** A log failure after `SendRaw` is caught in `TrySend`, and the queue handler tracks whether its own response left. A handler that sends its own RES and then throws still gets a second one: the base cannot see that. Not surveyed.
- **D06: 2 of 7 changed.** `QuestLeaderQuestProgressRequestHandler` and `CreateCharacterHandler` moved to a request base. `LobbyLobbyLeaveHandler` and `QuestPlayEntryHandler` send the RES first; the 3 dump handlers send only a dump. These 5 are pinned by tests. `CreateCharacterHandler` also sent Result 1 and carried on writing rows, then sent a second RES with Result 0; it now answers once and stops. **That branch has no test**: reaching it needs a whole asset repository. It is by reading only.
- **F10 throws.** The walk decodes the IL of every registered serializer, including nested closures, and finds no missing entity, so nothing live relies on the silence. Generic-parameter lookups are skipped, and unregistered serializers (D03, D04) are not walked, since no packet reaches them.
- **R07 differs from the brief's wording.** The log call has its own `try` per packet rather than moving into `Receive`'s `try`, whose catch now closes the connection. A logging failure should not close a session; the handler answers the malformed packet as it does with the setting off.
- **R02, R03.** `PacketFactory.ReadFailed` carries the outcome, rather than an exception, so decoded packets survive and the CLI is unchanged in what it reads. One CLI change: a length that is not a multiple of 16 used to end its run with `PacketCommandException`; it now logs, resets and goes on. Any other exception out of `Read` now closes too.
- **R05.** Added a key length check of 32 bytes: a shorter key would throw in the schedule and leave the fixed key in place. All 125 keys in `packets/keys/keys-all-in-one.csv` are 32 bytes. `SetChallengeCompleted` moved after the check in the game handler; its RES is allowed either way.
- **A gap noticed, left alone.** `_buffer` is reset only when a read ends on a frame boundary, so a session whose reads always end mid-frame keeps growing it. Not measured. Frames of one read are also decrypted before a handler changes the key, so a frame sent in the same segment as a failed challenge is still handled under the fixed key before the close takes effect. It gives nothing a self-chosen key does not.

Libraries: xunit, the BCL (`SHA1.HashData`, `System.Reflection.Emit.OpCodes`). Own code: the IL walk in `SerializerRegistrationTest`, because the BCL has no method body reader and Mono.Cecil is not worth a dependency for one test; `ReadLengthPrefixedByteArray`, because `IBuffer` has no bounded read.

## Baseline

| Command | T002 | Now |
| --- | --- | --- |
| `dotnet build Arrowgene.DragonsDogmaOnline.sln --no-incremental` | exit 0, 521 warnings, 0 errors | exit 0, 520 warnings, 0 errors |
| `dotnet test Arrowgene.DragonsDogmaOnline.sln --no-build` | 52 of 52 | 125 of 125 |
| `dotnet build ... --configuration Release --no-incremental` | exit 0, 521, 0 | exit 0, 520, 0 |
| `dotnet test ... --configuration Release --no-restore --no-build` | 52 of 52 | 125 of 125 |

125 = 52 + 73 new test cases.

## Proof that the new tests fail on develop

Run: a throwaway branch of `e2411fe8f9` plus cherry-picked `2ec9f649` (tests cannot compile without the seam) plus all new test files; `dotnet test Arrowgene.Ddon.Test/Arrowgene.Ddon.Test.csproj`. Branch since deleted; the steps are in this paragraph.

**125 total: 52 failed, 73 passed. All 52 failures are new tests, and all 52 old tests passed.** 21 new cases pass on develop:

| Cases | Why they pass there |
| --- | --- |
| `ClientSeamTest` (2) | They test the seam, which that run contains |
| `The_good_path_...`, `A_length_that_fits_...` (3), `A_real_password_size_...`, `The_largest_body_...`, `Sources_0_and_0x34_...` (2), `A_success_...`, `Canned_dumps_...`, `Lobby_leave_...`, `Quest_play_entry_...`, `An_unknown_id_...`, `Every_declared_id_...` | Pins: behaviour that must not change |
| `A_handled_error_in_a_queue_handler_...` | Pin: T001 said the queue handler has no fall-through |
| `Every_registered_response_can_be_written_as_an_error` | A guard: already true, and the F08 path depends on it |
| `A_body_over_the_u16_length_...` (65511, 65524) | `Client.Send` already caught that overflow. The counter test shows the fault |
| `A_queued_response_over_the_frame_limit_...` | **Weak.** On develop the recorder's own null dereference on `SendRaw(null)` reaches the `FAIL` path. What the real `ClientHandle.Send(null)` does was not read, so this test does not prove the queue half of F08 |

For F12 the failure on develop is the reflection assertion: the concurrent loop after it did not run there, so **no wrong hash was ever observed**. For R01 the failure is the registration guard, on purpose: running the read in-process on develop could take the machine's memory.

## Differential

Harness `Arrowgene.Ddon.Differential` from `harness/differential` on a throwaway branch of the patch, deleted afterwards; `harness/differential` itself was not merged. All 160,615 captures under `packets/decrypted_raw/`, 5 s, compared with `T002-per-id.tsv` over 1,321 rows.

| Measure | T002 | Patched |
| --- | --- | --- |
| Reads returned, outside `Error != 0` | 159,008 | 159,008 |
| Fit | 158,634 | 158,634 |
| Re-encode equal | 158,719 of 159,008 | 158,719 of 159,008 |
| JSON equal | 35,843 of 36,886 | 35,845 of 36,886 |
| JSON opaque | 122,122 | 122,122 |
| `Error != 0` | 63 | 63 |
| Class `agrees` | 494 | 495 |
| Class `values differ, other width` | 10 | 9 |

**Nothing that agreed before differs.** The only change of a counted column is 10.13.16 `S2C_SWITCH_STORAGE_NTC`, 0 of 2 JSON equal to 2 of 2, `agrees`: D02. On 4 more ids (6.25.16, 44.0.2, 2.1.2, 3.0.16) only the text of the first-divergence sample changed, at the same leaf with another value: which capture is seen first depends on thread order (inferred from the values, no second run on one tree). This is a per-id comparison, since T002 kept no per-capture file.

This covers the serializers only. Framing has its own evidence: `PacketCommandTest` still gives 688 and 32 packets.

## Report only: F09

Client: above 0x800 bytes `Read_MtString` fails and the client disconnects (T003, `0x8bc5b0`). Regex over `Arrowgene.Ddon.Shared/Entity`, plus reading the paths below; a miss is a coverage gap.

**Yes, a path exists: client text is relayed with no cap.** `ReadMtString` accepts a u16 length, and I found no length check on these paths (`rg` for length checks over `Chat/` and the chat, mail, profile and clan handlers: only `ProfileSetMessageSetHandler.cs:43`, a non-empty test).

| Text | In | Out | Who is disconnected |
| --- | --- | --- | --- |
| Chat | `C2SLobbyChatMsgReq.Message`, `C2SChatSendTellMsgReq.Message` | `S2CLobbyChatMsgNotice`, tell; `ChatManager.cs:122,276,291,307` | Recipients, and the sender if echoed |
| Mail | `C2SMailMailSendReq.MailText` | `MailMailGetTextHandler.cs:31` | The reader, each time it is opened, if the body is stored as sent (storage not traced) |
| Pawn comment | `C2SProfileSetPawnProfileCommentReq`, `C2SProfileSetPawnProfileReq` | `ProfileSetPawnProfile*Handler.cs:17-18`, then `PawnGet*PawnDataHandler` | Anyone who reads that pawn, while it stays set |

Also carrying client text, same shape, not traced to a send: entry board `Comment`, matching profile `Comment`, skill `PresetName`, character and pawn names on edit.

All need a login, and a client that can send more than its input box allows: whether the unmodified client caps these was not read. Server-made strings: the login announcement is a dump, and I found no unbounded one, but chat command output and asset text were not read. A cap at 0x800 **bytes** on these inputs is the likely fix (T003: truncating is safe compared with a disconnect); it would have to respect UTF-8 boundaries. T003 also notes exactly 0x800 has no terminator before a copy (`I`), so the cap should sit below it. Not patched, per the brief.

**Null strings:** 176 `WriteMtString` calls over 67 field names. Regex found 3 without a default in their file's declaration form, and by hand all 3 have one in the constructor (`CDataBattleContentUnk4.UnknownString`, `CDataClanScoutEntrySearchResult.Comment`, `CDataUpdateMatchingProfileInfo.Comment`). So a default instance is safe, which `Every_registered_response_can_be_written_as_an_error` confirms for responses. A handler assigning a null, for example from a database value, was not traced. The result would be `ArgumentNullException`: on a RES, now a `FAIL` RES; on an NTC, a logged error and no packet. Neither is a client disconnect.

## Report only: N3

**None of the 6 is sent by live code.**

| Id | Server name | Uses outside the table |
| --- | --- | --- |
| 2.19.16, 2.20.16, 2.21.16 | `C2S_CHARACTER_PAWN_*` | `C2S` structures read by `CharacterPawn*Handler`; no send |
| 11.60.16 | `C2S_QUEST_11_60_16_NTC` | `Quest_11_60_16_Handler` reads it; no send |
| 63.11.16 | `C2S_63_11_16_NTC` | `S2C_63_11_16_NTC` constructed only at `Quest.cs:1039`, inside `#if false` |
| 11.81.16 | `S2C_QUEST_11_81_16_NTC` | no use |

Searched with `git grep` at the branch head: constants, class names and `new PacketId(<g>, <h>` over `*.cs` outside the table (dumps included), and those names over the 536 `*.csx` scripts. A send built some other way would not show.

## For Sam's inspection: what a running server now does differently

**It now closes a connection it left open before, when:**

1. A frame length is under 16 or not a multiple of 16. Before: under 16 logged and read on; not a multiple threw on every later read, with a growing buffer.
2. A decrypted frame's source byte is neither 0x00 nor 0x34. Before: logged and read on.
3. Anything else throws out of `PacketFactory.Read`. Before: logged, connection open.
4. A challenge fails: RSA or Blowfish failure, or a session key that is not 32 bytes. One error RES goes out under the fixed key first. Before: a `FAIL` RES, and the session went on under the fixed key.

Packets decoded earlier in the same read are still handled in cases 1 and 2. The first three should only meet a client that has lost its place or is not a real one, and a TCP split no longer causes that (F01). A real client is not expected to reach case 4. This rests on the capture fixtures, the 160,615 captures and the code; **it has not been tried against a live client**.

It closes nothing else that it did not close before. Critical errors and database exceptions behave as they did.

**It now answers differently:**

- A handled error sends one RES, not two: visible on requests where the client set the once flag, whose dialog stays suppressed as the client meant.
- A not-implemented path, a response that cannot be serialized, a RES over the frame limit, a null party on 11.x quest leader progress and an exception in character creation now send an error RES. The client shows an error dialog where it used to wait 45 s (`I` for the unit), then show 33001 and disconnect. So these sessions survive.
- A failed `CreateCharacter` now returns Result 1 and stops, with no second RES and no further rows.
- A 3.3.16, 6.23.16 or 6.25.16 with a length that does not fit is dropped as a short packet, with a log line. One running past the end used to be relayed short.
- Normal play: wire bytes unchanged, by the differential's re-encode counts and the good-path test.

## Not run

- A live server or client, so also T003's open F06 items (status overwrite, the 90 handler bodies not read).
- The `CreateCharacter` Result 1 branch; the queue half of F08 against a real `ClientHandle`; `ClientHandle.Send(null)`.
- The concurrent hash loop on develop.
- A second differential on one tree, to confirm the 4 sample changes are thread order.

# 010 T004b: patch part 2, wire layouts

Server: `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Clean`, branch `fix/packet-handling`, head `924094e08a8cd209f4ef19c9c6b8a93a99e81bbf`, 17 signed commits on T004a's `c423c48b`, not pushed. Client: PC **03040008**. dotnet 10.0.403. ddon-data base `15e2a16d0d7`. Date 2026-11-04.

No live server or client was run. Statements about a client rest on T003's reading of the PC code, plus `0x8bc5b0` decoded here with radare2 from the raw `2022_01_29_DDO_DUMP_FIX.exe` (no IDA database touched).

## Rows

Test classes are in `Arrowgene.Ddon.Test/Shared/Entity/PacketStructure/`, except where a path is given. Fixtures are raw decrypted frames in `TestFiles/Captures/`; each test names its capture. "Before" is T004a's head (see Proof).

| Row | Commit | Test | Before | After |
| --- | --- | --- | --- | --- |
| test run | `5675057a`, `d5fceb28` | the whole suite | test host could die on a late log line (below) | 170 pass, repeatedly |
| helper | `dd1ffba2` | `CapturedFrame` | none | read length and re-encode against a capture |
| **W02** 27.8.16 | `812db727` | `AchievementCompleteNtcTest`, `...ServedTest` (2) | reader stops 1 byte short; element {u32} | {u32, u8}; a served NTC equals the capture's 9 bytes; 2 elements keep their places |
| **W16 + N1** | `7a41e4da`, test fixed `924094e0` | `QuestPlayEndNtcTest`, `...ServedTest` (2) | 7th u32 reads 0, time in the 4th, 0-999 only | 1,045,461 from the capture; whole milliseconds in the 7th; clamped to u32 |
| **F09** | `c3116dd4` | `Shared/Entity/MtStringWriteTest` (9) | any length; null throws | at most 0x7FF bytes, whole characters; null is length 0 |
| **W21** | none | none | see decision | unchanged |
| **W01** + N2 | `44d16806` | `ConnectionLoginResTest` (2) | u16, reader runs past | bool; a served frame equals the capture but for the flag's value |
| **W03** 3.0.16 | `6461cc8f` | `ErrorMessageListNtcTest` (2), `Server/Network/ErrorMessageListHandlerTest` | no trailing u32 | u32 written and read; handler sends the count still to come, as captures do |
| **W04** 2.1.2 | `214900a2` | `GetGameSessionKeyResTest` | u32, reads 2 too many | u16 |
| **W10, W11** | `d7794cec` | `ClientChallengeTest` (6), `ClientSuppliedLengthTest` | 278/279 read; 64 written | u8[62] each way; R06's guard kept |
| **W12** | `09c30fd4` | `CraftProgressTest` (2) | element {u32, MtString} | element u32 |
| **62.33.2** | `013e0ec2` | `SoulOrdealRewardListResTest` | writes `BuffId` twice | writes `Level` |
| **31.17** | `236d16a4` | `ClanSettingUpdateTest` (2) | RES has a bool, REQ reads nothing | RES is its header; REQ reads the bool, unused |
| **W08, W09, W14, 11.60.16** | `29833d86` | `ClientTrailingFieldTest` (5) | stop early | read to the end of what the PC writes |
| **W17, 11.4.2** | `00581694` | `DroppedListResTest` (2) | lists dropped | lists kept |
| **F05** | `c3210832` | `Shared/Entity/ErrorResponseReadTest` (6) | `EndOfStreamException` on all 63 | stops after `Error` |

## Decisions

**W21: leave it; nothing to fix today.** T003 called this an error because the server never sets the flag. By looking, no requirement ever reaches a client:

- Captures: all 18 of 20.0.2, 129 goods, **45 requirement entries, 27 distinct by shop, item, condition: `+20` is true on 45 of 45**, `IsCleared` false on 45, conditions 4, 5, 6.
- Server: `Shop.json` has 51 shops and 1,443 goods, and every requirement list (`Unk7`) is empty; the C# property is `Requirements`, so that name would not bind anyway. Nothing but `Clone` builds a `CDataGoodsParamRequirement` (`rg` over `.cs`, `.json`, `.csx`).

So the flag's value has no wire effect: the client shows no line because the list is empty, not because of the flag. What is missing is **the requirement data itself** (which goods, which condition, its parameters), which captures give for only 27 entries, 26 of them on shop 230, which `Shop.json` does not hold those items for (1 of 27 is on a shop and item the server has). Adding that is a feature. Whoever adds it should set this flag true and rename it: 45 of 45 captures show it, and T003 read the polarity.

**F09: cap 0x7FF, one place.** `0x8bc5b0`: `cmp ax, di` with 0x800 in `ax`, `jae` continue: **0x800 passes, above it returns 0**. It zeroes a 0x800-byte stack buffer, reads n bytes, then copies with `0x4030a0`. At exactly 0x800 nothing terminates the buffer before that copy (`I`: the copy is taken to stop at a 0), so 0x7FF is the longest safe length. `Utf8.FromUtf16` does the cut, since it stops on a scalar boundary, surrogate pairs included. The writer in `EntitySerializer` now calls the extension in `Extension.cs`. **Over-long capture: none.** Re-encode is equal on 159,008 of 159,008, so no captured MtString reaches the cap.

**W02: enums match.** Client category 6 is the server's 6: the 19 of 19 captured replies to a 27.10.1 asking for category 6 hold 19 ids, and those are exactly the 19 the assets give category 6. The 8 captured 27.8.16 carry the asset's category on all 8 (values 1 to 4).

**F05: a private exception, caught in one place.** 492 `ReadServerResponse` sites follow the same shape, and `Read` is abstract with no return path from the helper. A guard per site is 492 edits; 4 guards cover what was captured and no others. So `ReadServerResponse` throws `ResponseEndsAtError` (internal, carries the object) when `Error != 0`, and `EntitySerializer<T>.ReadPacket` returns the object. `ReadObj`, `Read(byte[])` and `StructurePacket` go through it. This departs from the ruling's "the 4 guards", as the brief allows. `Result` stays 0 on such a response, since the client does not read it either. A direct `Read(IBuffer)` on an error RES would see the exception: production has no such caller on a RES (`StructurePacket` was the one, now changed). `Every_registered_response_stops_at_an_error` walks every structure that writes a RES header (over 480). Some classes derive from `ServerResponse` and write no header (notices); that test skips them.

**W10.** The login reader's `ReadBytesTerminated(0)` and the game reader's size-based read both become `ReadByteArray(62)`. Trap avoided: the block is now 62 bytes, so `Challenge` decrypts only `PasswordEncSize` of them, as it did before. The padding in the writers follows the array, not the client's size, so R06's overflow can not return; `A_large_password_size_can_be_written` is unchanged. Sizes: certificate 304 and request 324 unchanged, response frame 96 (81 + 15 of padding, was 83 + 13); `The_good_path_...` still passes. The `C2S*` writers pad too, so the server's own test client sends 324.

**W01.** Captures have the flag as **1** on 42 of 42; the server still sends 0. T003: the client's handler reads neither field. Left false: the brief asks for the width, and nothing says what true would mean.

**W03.** Beyond "trailing u32": the handler now fills it, as a small addition. Captures: 950, 850, ..., 50, then 0 on the last, each the count after that frame. Client: capacity only.

**W12.** Other users checked: `CraftGetCraftProgressListHandler.cs:59` is the only writer (empty list). `S2CCraftGetCraftSettingRes.CraftMasterLegendPawnInfoList` has the same name and another type, untouched. No capture holds an element, so the element test is synthetic from PC `0x75e8e0`.

## A fault in the test run, fixed

With these tests the Debug test host died most runs: `InvalidOperationException: There is no currently active test`. `TestBase` (upstream) leaves its handler on `LogProvider`, so a line logged after its test, here `~Client`'s `Final Packets` from T004a's `RecordingClient` and the in-memory database's connection line, reached a finished output helper on the log thread. It happens whenever the GC runs late, so T004a's 125 of 125 was partly timing. Commits `5675057a`, `d5fceb28`: unsubscribe and catch that one exception. Test code only; Debug only.

## Baseline

| Command | T004a | Now |
| --- | --- | --- |
| `dotnet build Arrowgene.DragonsDogmaOnline.sln --no-incremental` | exit 0, 520 warnings, 0 errors | exit 0, 520, 0 |
| `dotnet test Arrowgene.DragonsDogmaOnline.sln --no-build` | 125 of 125 | 170 of 170 |
| `dotnet build ... --configuration Release --no-incremental` | exit 0, 520, 0 | exit 0, 520, 0 |
| `dotnet test ... --configuration Release --no-restore --no-build` | 125 of 125 | 170 of 170 |

170 = 125 + 45 new cases. One old test was renamed and changed: `A_real_password_size_writes_the_same_bytes_as_before` is now `..._the_block_of_62`, 8 + 2 + 62, which is the row itself.

## Proof that new tests fail before

**Run 1:** throwaway branch of `c423c48b`, plus the fixed `TestBase`, the fixtures and the test files that compile there (one assert on `ClientVersion` removed for that run); `dotnet test Arrowgene.Ddon.Test/Arrowgene.Ddon.Test.csproj`. Deleted afterwards. **163 total: 37 failed, 126 passed.** The failures are 36 of the 38 new cases, plus the renamed old test; the other 124 old tests pass. The 2 new cases that pass are pins: `A_string_under_the_cap_is_unchanged` (0x7FE, 0x7FF). `A_response_without_an_error_reads_on` fails there because of 31.17's excess bool, not for an F05 reason, so it pins rather than proves F05.

**Run 2:** the 7 cases that name a member `c423c48b` does not have do not compile there. At the patch head, on a throwaway branch deleted afterwards, the behaviour was undone with the member kept (no category written; `.Milliseconds`; time in the 4th u32; handler not setting the count; a string after the u32), and those tests run. **6 of 7 fail.** The seventh, `A_captured_response_still_round_trips` (30.0.2), is a pin: no capture has the element.

That run found a test of mine that passed with the fault in place: `A_served_play_time_...` compared offset 24, zeros in both, because the notice has a u32 before the structure. Fixed in `924094e0` (offset 28, and it pins the captured bytes), then re-run: it fails with `.Milliseconds` and fails with the time in the 4th u32.

## Differential

Harness `Arrowgene.Ddon.Differential` from `harness/differential` (`7d114a55`) on a throwaway branch of the patch at `c3210832`, deleted afterwards; not merged. The two commits after it change only test code. All 160,615 captures under `packets/decrypted_raw/`, 8 s. Compared with `T002-per-id.tsv` over 1,321 rows. Per-id output: `T004b-per-id.tsv`.

| Measure | T002 (develop) | T004a | T004b |
| --- | --- | --- | --- |
| Reads returned, outside `Error != 0` | 159,008 | 159,008 | 159,008 |
| Fit | 158,634 | 158,634 | **159,008** |
| Re-encode equal | 158,719 | 158,719 | **159,008 of 159,008** |
| JSON equal | 35,843 of 36,886 | 35,845 | **36,885 of 36,886** |
| JSON opaque | 122,122 | 122,122 | 122,122 |
| `Error != 0` reads returned | 0 of 63 | 0 of 63 | **63 of 63, no exception** |
| Class `agrees` | 494 | 495 | **511, plus 2 `headerless agrees`** |
| `values differ, other width` | 10 | 9 | 1 |
| `re-encode differs` | 4 | 4 | 0 |
| `reader too short` | 3 + 2 headerless | same | 0 |
| `reader too long` | 1 | 1 | 0 |

**Nothing that agreed before differs.** Every id that moved:

| Id | Old class -> new class | Counted change |
| --- | --- | --- |
| 0.1.1 | other width -> agrees | JSON 0 -> 42 |
| 0.1.2 | reader too long -> agrees | fit 0 -> 42, re-encode 0 -> 42, JSON 0 -> 42 |
| 0.5.1 | other width -> agrees | JSON 0 -> 41 |
| 1.0.1 | headerless too short -> headerless agrees | fit 0 -> 42, re-encode 0 -> 42, JSON 0 -> 42 |
| 1.0.2 | too short -> agrees | fit 0 -> 42, re-encode 0 -> 42, JSON 0 -> 42 |
| 2.1.2 | other width -> agrees | JSON 2 -> 42 |
| 3.0.16 | too short -> agrees | fit 328 -> 410, JSON 0 -> 410 |
| 10.13.16 | other width -> agrees | JSON 0 -> 2: T004a's D02, in the T002 comparison |
| 11.4.2 | re-encode differs -> agrees | re-encode 0 -> 20 |
| 11.60.16 | other width -> agrees | JSON 0 -> 7 |
| 13.16.2 | re-encode differs -> agrees | re-encode 0 -> 1 |
| 14.11.16 | other width -> agrees | JSON 0 -> 57 |
| 27.8.16 | other width -> agrees | JSON 0 -> 8 |
| 31.17.1 | other width -> agrees | JSON 0 -> 42 |
| 31.17.2 | re-encode differs -> agrees | re-encode 4 -> 42, JSON 0 -> 42 |
| 44.0.1 | headerless too short -> headerless agrees | fit 0 -> 83, JSON 0 -> 83 |
| 44.0.2 | too short -> agrees | fit 0 -> 83, re-encode 0 -> 83, JSON 0 -> 83 |
| 50.1.1 | other width -> agrees | JSON 0 -> 59 |
| 62.33.2 | re-encode differs -> agrees | re-encode 0 -> 21 |
| 13.3.2 | agrees, unchanged | error reads 0 -> 2 |
| 18.0.2, 19.1.2, 19.2.2 | `Error != 0 apart`, unchanged | error reads 0 -> 41, 4, 16 |

All are in the brief, except 10.13.16 (T004a). **Re-encode now equals the raw bytes on all captures** of W01 (42), W03 (410), W04 (42), W10 (42 + 83), W11 (42 + 83), 62.33.2 (21): no remainder.

Not visible here, by construction: W02's and W16's handlers, W03's count on a served frame (tested above), W12's element (no capture). The one remaining `values differ` is 63.11.16: T04, its sender under `#if false`, not in this brief.

## For Sam's inspection: what a served client now sees differently

Visible, as T003 read the code:

- **W16 + N1:** a quest end now carries the real time. It was blank. Which screen shows it is not traced: T005b should look.
- **W02:** an achievement of category 6 (19 of the assets, `RoyalFamilyRestoration`) now also queues the client's notice (`0xb67c50`, kind 33). Other categories: no change, and the one element per NTC stays.
- **F09:** a chat, mail or pawn comment over 0x7FF bytes is cut to fit, where the recipient used to disconnect. A shorter one is byte-identical. Whether the unmodified client can send that much was not read.

Same behaviour, different bytes, per T003:

- **W01:** every game login: one byte less in 0.1.2, the token now arrives, and the handler reads neither.
- **W03:** every login: 4 more bytes per 3.0.16; the client only reserves capacity.
- **W04:** 2 bytes fewer in 2.1.2, unread.
- **W11:** 1.0.2 and 44.0.2 are 2 bytes shorter; the frame stays 96. The 46 bytes after the password are the client's own, as sent. Every connection passes here: **T005b should confirm it.**
- **62.33.2:** the level, in a field no consumer reads.
- **31.17.2:** 1 byte fewer, unread.
- **W12:** nothing: the list stays empty.

Not on the wire:

- **W08, W09, W10, W14, 11.60.16, 31.17.1:** the server now reads more of what the client sends. All captures hold those bytes. A client that sent less than the PC 03040008 writes (another build, a modified client) now gets `EndOfStreamException` on 0.1.1, 0.5.1, 14.11.16, 50.1.1, 11.60.16 or 31.17.1 where it used to pass. That is the one way these "readers" touch a running server. Worth T005's attention, since 0.1.1 is every login.
- **W17, 11.4.2, F05:** CLI and dumps only.

## For later

- Annotated dumps and JSON made through the Arrowgene CLI change for every id above. With F05 the four guards in `packets/tools/arrowgene-cli.patch` are no longer needed once this lands; I changed nothing there.
- `Unknown`, `HideRequirementDetails`, `IgnoreRequirements` and other names stay wrong: renames were out of scope.
- T003's count of errors should read W21 as "not observable today" rather than an error a client meets.

## Libraries and own code

Libraries: xunit, the BCL (`System.Text.Unicode.Utf8.FromUtf16`). Own code: `ResponseEndsAtError` and `ReadPacket`, because no library can add a return path to 492 hand-written readers; `CapturedFrame`, a few lines over the serializers.

## Not run

- A live server or client.
- A second differential on the two test-only commits after `c3210832`.
- Row-by-row build of the intermediate commits: the tree was built and tested whole, then committed row by row. A maintainer dropping a commit should build. Known ties: `dd1ffba2` is needed by the later tests; `5675057a` should stay.
- `GetErrorMessageListHandler` against real assets: its test uses an uninitialised server with messages of 500 characters, to force more than one frame.
- `AchievementManager`'s one line: the test covers the element, not the call.

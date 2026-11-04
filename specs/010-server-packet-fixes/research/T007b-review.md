# 010 T007b: whole-spec review, client PC 03040008, server `fix/packet-handling`

Filed by the coordinator from the reviewer's final message, condensed. Inputs: ddon-data `33d042ca594`, server clone `64c676b9`. Read-only: nothing run, no git, no IDA. Line numbers are of those heads. Value of finding 2 left out on purpose.

**Verdict.** The code does what seven sampled rows say and every Ruling row is accounted for. The problems are in the text, one candidate is missing, and two tests are Sam's call.

## Findings

| # | Rank | Where | Finding | Ruling (coordinator) |
| --- | --- | --- | --- | --- |
| 1 | High | `pr-body.md:11,29,74`; `impact.md:107` | Banner stated flat. T005b:111-116: the one-element category 6 notice, the form `AchievementManager.cs:505-508` sends, gave a chat line with a menu open and no banner checked; the banner appeared once, on a two-element notice with another id. Control row 113 has the same visible result as row 111, so "the byte decides" rests on one run that also changed count and id | Fix the text. No new live run: the code read stands and the claim gets narrower |
| 2 | High | `SerializerRegistrationTest.cs:184-193`, `ClientSuppliedLengthTest.cs:48-64` | Test bodies on the pushed branch show the count shape with the packet named. The fixes show the same against `develop` | Sam's call, named in T007e |
| 3 | High | T001 `F04`; `PacketFactory.cs:164-168,335` | Candidate on no list: `Client.Send` and `PacketFactory.Write` take no lock, timers are other threads, the Camellia scratch is shared. T003 cleared the counter only. Also with no row in `impact.md`: W07, W13, D03, D04, D05, T03, T07, W18, W19, W20 | **Fix F04** (T007c); give the others rows |
| 4 | High | `impact.md:95,253` | Says the published branch still carries what T006a removed | Fix |
| 5 | Medium | `pr-body.md:74`; T005b:148,154,156 | "No 3001 or 33001" is absolute; T005b limits it to frames looked at, and one client exit is unexplained | Narrow; record in `impact.md` |
| 6 | Medium | `pr-body.md:7`; T004a:38-39; `impact.md:45` | "Every request now gets one response" overreaches: a handler that sends its own RES then throws was not surveyed; 5 of 7 non-request-base handlers are pinned, not changed | Narrow |
| 7 | Medium | `pr-body.md:23`; `impact.md:51`; T003:167,232 | The 33001 outcome is stated for login `CreateCharacter` on game-connection evidence | Mark inferred |
| 8 | Medium | `pr-body.md:11,30,75`; T003:159; T005b:103 | "Quest end screen" is presupposed: which screen shows the time is not traced, and the one direct call site looks like a countdown notice (inferred) | Say where it shows is not known |
| 9 | Medium | `pr-body.md:25,74,75`; `impact.md:72,80,110,197`; T005b:22-31,91 | "Not run live" reads as complete: close case 3, split frames on a socket, the bounded lengths, the catch-up flood are missing. 0.7.2, 8.8.2, the move and the banner came from a build with scratch lab additions; 8.8.2 was forced | Complete the list; say so |
| 10 | Medium | `docs/reference/inputs-and-builds.md:85` | Names `b8be1e19`, which the fork does not have | Give the head and PR 8 |
| 11 | Medium | `docs/reference/packet-handler-tables.md:143` | "At exactly `0x800` the stack buffer has no terminator" is the note ruled off the branch | Remove from `docs/`, as a reader needs the limit only; T003 keeps the finding |
| 12 | Low | `docs/reference/status.md:149-150` | CLI patch "not run", but T006 applied it to the branch, built it and ran 3 streams | Update |
| 13 | Low | `docs/explanation/two-packet-decodings.md:59,71` | Body is right; the heading can be skimmed as a layout difference | Rename the heading, fix anchors |
| 14 | Low | `pr-body.md:15`; T005a:95,111 | "The server does not read responses at run time" is too broad: canned dumps | "does not read a client's responses" |
| 15 | Low | `pr-body.md:86`; T003:22 | 11.10.2 "Neither is an error" drops T003's "part"; `+356`, `+360` not traced | Keep the limit |
| 16 | Low | `pr-body.md:27`; `impact.md:85` | "Nothing at the default single lane" covers F12 only; F11's collision is per process start (`I`). 1,778 against T001's 1779 game ids | Fix; recount |
| 17 | Low | `impact.md:129-186`; `spec.md:60` | No "not run" for 8 commits, no risk for 3. The body's table has no symptom or who column: that narrowing came from the T006 brief | Fill in `impact.md`; the narrowing is ruled at close: the body is the short form, `impact.md` the full outline |
| 18 | Low | `docs/index.md:66`; `AGENTS.md:42`; `CLAUDE.md:7` | The index line omits the new section; the other two are T007d's | Fix the index; T007d |

## Checked and found right

- **Code, read against source:** 27.8.16, 11.45.16, the `MtString` cap, close cases 1 to 3, failed challenge, one response, frame limit and bounded length.
- **Numbers agreeing with their reports:** 177/177 and 52/52; warnings 520 and 521; 160,615 = 1,544 + 63 + 159,008; the differential table; 116,523 and 130,521; the capture counts per row; 40 ids in order; the size arithmetic; the drop lists.
- **Client claims against T003**, not re-read in IDA: the addresses of the "Deliberately not changed" and layout rows agree.
- **Public wording:** no task id, machine path, count value, "no login" or memory claim in `pr-body.md`; comments as T006a states; 24 fixtures, no stream names.
- **Docs:** `packet-handler-tables.md` § What ends a served connection and `packet-wire-format.md` § Padding against T003, marks honest; `status.md` 2 of 84.
- **Ruling coverage:** every Fix row is in a commit; every not-patched row is listed, except R08 from the body (left out on purpose).

## Not checked

Commit messages and the comments-only diff (no git; T006a's report only). That PR 8's live body equals `pr-body.md`. Any address in IDA; whether `f2a8` shares addresses with `f1c9`. Any test or build result. `T001-inventory.md`, `T002-per-id.tsv`, `T004b-per-id.tsv`, `T002-examples.tsv`. Fixture bytes. A word scan of production `.cs` outside the files named.

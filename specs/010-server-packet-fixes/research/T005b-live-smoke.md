# 010 T005b: live smoke of `fix/packet-handling` with a real PC 03040008 client

Date 2026-11-04. Local server only, nothing pushed. ddon-data base `fdd5aa5be1a`.

**Verdict: the real client logs in, plays and moves between worlds on the patched server. No defect in the patch was found. The category 6 fix (W02) and the single error RES (F06) were seen live. W16's screen and F06's once flag were not reached.**

## Environment

| Item | Value |
| --- | --- |
| Server under test | Scratch clone of `Arrowgene.DragonsDogmaOnline.Clean`, detached at `b8be1e19b5a68c57c317461bdd607f52be71158d`: all 29 commits on `develop` `e2411fe8`, 29 of 29 `G`. Debug build, dotnet SDK 10.0.403, 0 errors |
| Control | Second scratch clone at `develop` `e2411fe8f9134fedd2b78f0db0bc561cadac98ce`, same build |
| Build choice | **Neither option in the brief quite**: clean clone's commits, built in scratch clones, with the automation setup's config. The `automation` branch sits on an older base (`88d82caf`), so nothing was merged and no conflict was tested. Its one local commit (template character) is not needed with the tutorial-done database |
| Database | Copy of the automation `db.sqlite` (`85c1477e…`), migrated 54 to 68 in each scratch build. Original unchanged, same hash afterwards |
| Client | Installed **`C:\DDON\DDO.exe` f2a80229…**, title screen version `03.04.007 : 3040008`. See "Two departures" |
| Hook | ddon-hook `36a61a6` (branch `rng-monitor`), built out of tree (preset `x86-release-zen5-vs2026`, `dinput8.dll` `5ba1b644…`), the repository had no build. Automation only: `DDON_GAME_HOOKS=none` |
| Driver | Copy of `scripts/automation`, so that ddon-hook stayed read only |

### Three server states

1. **Pristine**: `b8be1e19` exactly, one world. Scenarios 1, 6, 7, and the same-world path of World Select.
2. **Lab, inert unless triggered**: added below to both clones, with two more rows in the build's `GameServerList.csv`. Scenarios 2, 3, 5, 4's push.
3. **Control**: `develop` with the same `LabHook` and rows.

Lab additions, in scratch only and now deleted. In `RequestPacketHandler.Handle`, before the handler runs:

```csharp
if (LabHook.ForcedError(request.Id.Name) is uint labCode) { throw new ResponseErrorException((Arrowgene.Ddon.Shared.Model.ErrorCode)labCode, "lab"); }
```

`LabHook` reads `PACKET_NAME code` lines from a file, and is inert with no file. On the fix clone only, `LabPush` sends a chosen 27.8.16 or 11.45.16 from a timer to the client that last asked for the server list. Rows: `11,Second World,…,127.0.0.1,52000,…,52099,…` (same process, RPC answers) and `12,Dead World,…,127.0.0.1,52000,…,1,…` (RPC refused).

### Two departures

- **Client folder.** The brief names `D:\DDON_03040008`. ddon-hook `AGENTS.md` (Sam, 2026-10-18), doc 17 and doc 09 say live runs use `C:\DDON` and never deploy to `D:`. I took the later, explicit rule. `D:\DDON_03040008` was not touched.
- **Executable.** Doc 17 says to run on the fixed dump f1c9. `drive.py start` without `--exe` launched the installed f2a8: doc 09 gives that default to `run_cycles.py`, not to `drive.py`. I found this only at the end, so **every run here is on f2a8**, which is the build real players have. Doc 17's "`drive.py --exe` default to it" reads as if `drive.py` defaulted too. Nothing was copied over the executable (`DDO.exe` still f2a8, 2025-08-27).

## Scenarios

| # | Scenario | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Login, game-select, into the game | **Pass** | Below |
| 2 | Moving between servers (0.5.1) | **Pass**, one process posing as two worlds | Below |
| 3 | Error path (F06) | **Pass**: 1 RES, 1 dialog; `develop` sends 2 | Below |
| 3b | F06 with the once flag | **Not reached** | Below |
| 4 | Quest end (W16 + N1) | **Not reached**: no quest finished, no screen seen | Below |
| 5 | Category 6 achievement (W02) | **Pass**, by a pushed notice, not by earning one | Below |
| 6 | Failed challenge (R05) | **Pass**: RES, then orderly close | Below |
| 7 | Malformed frames (R02, R03), huge count (R01) | **Pass** | Below |
| 8 | 3001, 33001, new exceptions | **None seen** | Below |

### 1. Login

Pristine, first attempt, nothing adjusted.

- **Sequence, 40 packets, the same ids in the same order on `b8be1e19` and `develop`:** `1.0.1 1.0.2 0.1.1 0.1.2 3.0.1 3.0.16 3.0.2 2.2.1 2.2.2 4.0.1 4.0.2 5.0.1 5.0.2 5.1.1 5.1.2 2.3.16 2.1.1 2.1.2 44.0.1 44.0.2 0.1.1 0.1.2 1.4.1 1.4.2 0.2.1 0.2.2 1.1.1 1.1.2 2.0.1 2.0.2 2.6.16 28.25.16 31.17.1 31.17.2 12.0.1 12.0.2 43.0.1 43.0.2 1.0.1 1.0.2`. Frame sizes were not compared: the server log has ids, not lengths. The login and game connections are mixed in this order.
- **Covers:** W11 and R05's good path (1.0.2, 44.0.2, RSA under this server's key, RSA plaintext 48), W01 (0.1.2), W04 (2.1.2), W10 (44.0.1), W03 (3.0.16), W09 (game 0.1.1), 31.17 and 31.17.2 with the moved flag.
- **Log:** `ClientLoginHandler … Logged In`, `ConnectionLoginHandler … [Cha:(1)Sehkah Bugfix] Logged Into GameServer`.
- **On screen:** in the White Dragon Temple, HUD `World: 010`.
- **Staying up:** the session ran 3 min 58 s until the driver ended it, and 339 client and 156 server packets, tests included, went through. The hook's `presents` kept rising. No crash at the known 30-50 s.

**Not from the patch:** every login on both branches logs `no such column: ddon_pawn.craft_exp` once (`DdonSqlDb`). So the migrated copy lacks a column and that pawn query fails. It is a property of this database and the migration chain, and it happens on `develop` the same way. Whether it is why Pawns is greyed in the menu was not checked.

### 2. Moving between servers

Options, World Select lists all three rows. Second World, destination White Dragon Temple, on the lab fix build:

```
Client #000280 (0.7.1) C2S_CONNECTION_RESERVE_SERVER_REQ
Server #000000 (0.7.2) S2C_CONNECTION_RESERVE_SERVER_RES
Client #000286 (0.6.1) C2S_CONNECTION_MOVE_OUT_SERVER_REQ
Server #000000 (0.6.2) S2C_CONNECTION_MOVE_OUT_SERVER_RES
Client #000000 (44.0.1) C2S_CERT_CLIENT_CHALLENGE_REQ
Server #000000 (44.0.2) S2C_CERT_CLIENT_CHALLENGE_RES
Client #000288 (0.5.1) C2S_CONNECTION_MOVE_IN_SERVER_REQ
Server #000000 (0.5.2) S2C_CONNECTION_MOVE_IN_SERVER_RES
```

The client then shows `You moved to world 011`, HUD `World: 011`, and goes on playing on the new connection. **Limit:** source and target are one process, so this is the client's whole flow, not two servers. `develop` was not moved, so the comparison is against 41 captured 0.5.1 reads, not a live control.

### 3. Error path

An ordinary error, nothing forced: Dead World, whose RPC port refuses, so `ConnectionReserveServerHandler` throws `ERROR_CODE_NET_NOT_CONNECT_GAME_SERVER`.

| | `develop` | `b8be1e19` |
| --- | --- | --- |
| 0.7.2 after one 0.7.1 | **2** | **1** |
| Dialog | 1, `ERROR_CODE_NET_NOT_CONNECT_GAME_SERVER (S-3008)` | 1, the same |
| After dismissing | | Session continues, the next move works |

A forced 8.8.1 during the game-entry load (error 11000, lab): `develop` 2 RES of 8.8.2, `b8be1e19` 1. Both show the same one dialog `A pawn could not be found; try relogging` (S-11000), and dismissing it logs out to the title, on both. On `develop`, 16.0.1 and 18.0.1 forced in a later pass also gave 2 each.

A natural one by accident, on the login connection: `ERROR_CODE_AUTH_MULTIPLE_LOGIN` gave 1 of 0.1.2, then the client closed. See "Client exits".

**3b, once flag: not reached.** The forced 8.8.1 shows a dialog on both, so that load does not set the flag: the T003 sites for 8.8.2 are elsewhere. The menus that would reach the sites did not: Pawns and Pawn Order are greyed (cause not checked: no registered pawn, or the query above), and opening Community List and Group Chat with 16.0.1 and 18.0.1 forced sent neither. **It would need:** a character with registered pawns on a database with that column, then `PawnGetRegisteredPawnDataHandler` (8.6.1) forced from a pawn screen, on both branches. **So the suppressed dialog, the one user-visible gain T003 gives F06, is still by reading only.**

### 4. Quest end: not reached

No timed quest was finished. Isaac (`Adventure Guide / Extreme Missions`) stands near the spawn, but reaching him needs the position lab patch and closed-loop walking, then a mission a level 1 character can start, then Exit Content. That was not attempted within this package.

What was run: `LabPush` sent 11.45.16 directly to the live client with 1,045,461, 6,000,000 and 4,294,967,295 ms. **All three arrived with no disconnect and no 3001, and nothing appeared on screen in the 4 s observed.** That only shows the frame reads safely at those values. It does not show the time displays, so **W16, N1 and the over-99-minute format stay unconfirmed live.**

A lead for whoever goes on, from `2022_01_29_DDO_DUMP_FIX.exe` (radare2 plus a scan of `.text` for direct calls): `0x4cf380` has **one direct call site, `0x4d0285`**. It follows a countdown at `[edi+0xcc]`, and what it formats goes with message index `0x1d3` to `0xb797a0`. So it looks like a timed notice on a countdown rather than a result screen (inferred; message 467 not looked up, indirect calls not searched). If that is right, a 4 s wait may have been too short.

### 5. Category 6 achievement

Pushed to the live client on the moved connection, as T003 had noted the enum values still needed comparing:

| Notice | On screen |
| --- | --- |
| One element, 2860, category **6** | Chat `Earned achievement`, `War Mission "Jifule Fortress Capture Battle" Cleared!` |
| Two elements, 2856 category **6** + 2861 category 1 | Full-screen banner **GREAT PURPOSE, Royal Family Restoration, Acre Selund "Rathnite Foothills" Restoration Accomplished!**, and a chat line each for both elements |
| One element, 2860, category **0**: what `develop` delivers, as its reader falls on padding | Chat line only, **no banner** |

- **So W02 is real and right:** the byte decides the banner, the server's value 6 is the client's 6, and a two-element notice reads whole, which T003 said misreads without the u8.
- **Limit:** the first row's menu was open and no banner was checked at that moment. The banner was seen once, on the second row.
- **Not run:** earning one in play; T005's catch-up flood of many notices. `AchievementManager` queues one element per notice as before.

### 6. Failed challenge

A test client built on the server's own `Challenge` and `PacketFactory`, 16-byte key, 3 connections each, pristine, with the real client in session:

| Port | RES | Close |
| --- | --- | --- |
| Login 52100 | 1.0.2, error 6011 `AUTH_LOGIN_FAILED`, frame 96, under the fixed key | Orderly FIN, 3 of 3 |
| Game 52000 | 44.0.2, error 2001 `SYSTEM_INTERNAL`, frame 96, under the fixed key | Orderly FIN, 3 of 3 |

A key of 48 stayed open with its RES under the first 32.

### 7. Malformed frames and the huge count

Same conditions, after a good challenge:

| Test | Sent | Server log | Result |
| --- | --- | --- | --- |
| R02 | Length 17 login, 17, 0, 15 game, 65535 login | `DataSize:N is under 16 or not a multiple of 16` | Orderly FIN each |
| R03 | Source byte 7, login and game | `Invalid packet source:7` | Orderly FIN each |
| R01 | 35.9.16, immune count 0xFFFFFFFF at body +178, 1 frame, then 200 in 23 ms | 201 `PACKET ERROR` with `EndOfStreamException`, the last by 13:15:34, the second the frames were sent | No stall. Connection left open |

- **The real client's session stayed up:** `GameClient#1` was not disconnected until the driver stopped it at 13:18:31, and its later menu requests were answered (27.0.1 as `#000204`, 27.1.1, 27.2.1, 27.3.1, then World Select).
- **A new login connection** after the 200 answered its challenge in 86 ms.
- **"The real client's ping keeps flowing": not as worded.** This client sent **no ping** in the idle window, or anywhere in the run, so the proof is the requests above, not a ping series.
- **Observation, not a defect by this brief:** R01's sender is **not closed**: it can go on sending, at the cost of one caught exception and a stack trace per frame, 60 log lines each here. No limit or close applies to frames that fail in a structure read. Whether that deserves one is for the next package.
- **`develop` was not run with R01**, on purpose: T002 measured 512 MiB in 675 ms, and this machine had other work running.

### 8. Watching for 3001, 33001, new exceptions

- **3001, 33001:** no such dialog on any frame looked at, and no session ended unexpectedly. Log search: 0 lines. The log is server side: a client-side 3001 shows only as a disconnect, and there was none outside the "Client exits" below.
- **Log comparison over `b8be1e19` and `develop`:** the only errors `develop` lacks are those the tests provoke on purpose (R01, R02, R03, R05). The SQL error, `Send - Client handle is stale` (1 to 3 per run, on both) and `ProcessReceive` lines are on both.
- **Not compared:** `Send - Client handle is stale` around a move, as `develop` did not move.

### Client exits

- **One exit, 13:47, lab fix build.** My third run began with `ERROR_CODE_AUTH_MULTIPLE_LOGIN` (`Already logged in`), and the client process was gone a few seconds and two key presses later. No WER event 1000 in the Application log, no `exceptions.log` (the exception log was off), no dump looked for, and the last hook log lines are input set-up at 14:47:27 local, not a shutdown. By 14's rule, **unexplained, not recorded as a crash**. It is plausibly my own keys on the dialog and the title behind it (inferred, Exit not seen).
- **The cause of the error is lab state:** `ddon_connection` held `(server 11, account 1)`, left by the move to Second World, which is this same process, so nothing cleared the row for 11. Deleting the row from the scratch database fixed it. **This is not from the patch.** Whether a real second server clears its row was not tested.
- **The known 30-50 s crash** did not occur in the other 5 sessions, on f2a8 with automation only. Each of those was ended by `drive.py stop`. Five sessions is too few to call it gone.

## Patch defects

**None found.** Clean clone unchanged: head `b8be1e19`, tree clean.

## Clean-up

| Item | State |
| --- | --- |
| `C:\DDON\dinput8.dll`, `ddon_hook.env` | Removed by `drive.py stop` after each session: neither was there before. No `.ddon-restore-pending.json` |
| `C:\DDON\ddon_hook.log`, `ddon_hook_artifacts\` | Overwritten or added to by the runs: these are the hook's own output, and the log was there before |
| `config.ini` under `%LOCALAPPDATA%` | Restored by `drive.py stop` each time |
| `DDO.exe` | Unchanged, f2a8 |
| `D:\DDON_03040008` | Not touched |
| Servers, clients | Stopped: no `DDO.exe`, ports 52099, 52100, 52000 free |
| `C:\ddon-automation\Arrowgene` | Unchanged: head `70866dd9`, its 3 uncommitted lab files as found, database hash as found |
| `C:\ddon-automation\t005b\` | Scratch deleted (clones, builds, driver copy). Logs, the test client's source and five frames kept at `C:\ddon-automation\t005b-evidence\` |

## Libraries and own code

Libraries: `Arrowgene.Ddon.Server`'s own `Challenge`, `PacketFactory`, `EntitySerializer` in the test client; BCL sockets; radare2. Own code, all scratch, none in the server under test or the clean clone: test client (nothing exists that sends hostile frames at a running server), `LabHook` and `LabPush` (the server has no way to force an error or push a notice from outside), log compare and call-site scripts (one use).

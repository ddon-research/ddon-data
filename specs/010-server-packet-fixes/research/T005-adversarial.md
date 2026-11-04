# 010 T005: adversarial review of `fix/packet-handling`, client PC 03040008

Reviewer `adversarial-reviewer`, base `15abeea47cc`. Server clone head `924094e0`, base `e2411fe8f9`. Client binary `D:/research/DDON-binaries/PC/2022_01_29_DDO_DUMP_FIX.exe` (`f1c974d0...`), radare2. Canaries `.agent-ledger/canaries/010-T005/`. Filed by the coordinator from the reviewer's final message. The review stopped before its budget; unfinished risks are under "Not checked". No live server or client.

**Verdict: 2 findings. F1 blocks: as it stands, the branch refuses every real client at the first packet.**

## F1 (block): R05's key length check rejects every real client (`c423c48b`)

`Arrowgene.Ddon.Server/Network/Challenge.cs`, both `HandleClientCertChallenge` overloads: `response.Error = response.CamelliaKey.Length != CamelliaKeySize; // 32`.

The real client encrypts 48 bytes under RSA: PC `0x88ae70`-`0x88ae8c` draws 48 characters; `0x88aecd` `push 0x30`, then `0x88aee2` `call 0x13edf20` (that this is the RSA encrypt is inferred from its arguments and from 006 T002c); `0x88afbb` `push 0x30` passes the size to `0x889e70`. `CommonKeySrcSize` is 48 on 125 of 125 first frames. `docs/explanation/wire-protocol.md` and `docs/reference/packet-wire-format.md` already say the session key is the first 32 of 48 characters. T004a's check (125 keys in `keys-all-in-one.csv` are 32 bytes) looked at the truncated session key, not the RSA plaintext.

Result at the head: a failed challenge, one error RES (2001) under the fixed key, then a close, on login and game connections. Reproduced by `canary/` (exit 1, `out.head.txt`) on the game handler; the login overload has the identical line, not run.

Fix: `response.CamelliaKey.Length < CamelliaKeySize` in both overloads. A 48-byte key already ciphers as its first 32 bytes. Tried on the scratch branch: the 48-byte canary passes, tests 170/170 in Debug. Add a regression test with a 48-byte key. Why the tests missed it: `The_good_path_keeps_its_sizes_and_moves_to_the_session_key` uses 32, `ClientCreateChallengeRequest` sends 32 where the PC sends 48, and replay could not reach the handler because the official RSA private key is not available.

## F2 (route): fixtures carry session tokens

`Arrowgene.Ddon.Test/TestFiles/Captures/`: `0_1_1.stream10.10164.bin` (31-character session key), `0_5_1.stream47.10686.bin` (session key), `0_1_2.stream10.10165.bin` (one-time token, then padding `08.220.136`, what looks like the tail of an IP address, owner not established), `2_1_2.stream20.12111.bin` (session key, stale text in padding), `31_17_1.stream10.10192.bin` (padding `90E`, inferred fragment of the stream's session key). `1_0_1`, `44_0_1`, `1_0_2`, `44_0_2` hold the RSA-wrapped key and 46 stale client bytes; `44_0_2`'s tail looks like stack pointers. File names tie fixtures to streams whose keys are in `packets/keys/`. No character names in a printable scan of the 25 `.bin` files; that scan does not decode non-ASCII names reliably. Fix: fixed filler of the same length over tokens and padding tails, layout kept, round-trip tests re-run.

## Checked and found right

| Risk | Check | Result |
| --- | --- | --- |
| Replay | All 125 keyed streams through `Client.Receive` at the head: 95,407 client TCP segments, 116,523 C2S packets | 0 closes, 0 `ReadFailed`, 0 throws |
| C2S readers | 116,033 structure reads, including 0.1.1 42, 0.5.1 41, 14.11.16 57, 50.1.1 59, 11.60.16 7, 31.17.1 42, 3.3.16 66,275, 6.23.16 8, 6.25.16 34,607 | 0 throws |
| Headerless first frames | 125/125 read: block 62, password sizes 16/16, frame 336 | Fine |
| Split reads | Whole client stream at random splits on 125, one byte at a time on 124 | 130,521 packets, 0 mismatches |
| S2C direction | 43,967 packets read | 0 `ReadFailed`, 0 throws, 63 error responses read |
| Other users | `Arrowgene.Ddon.Client` (first 30 files listed), `.csx` scripts | No shorter sender found |
| Null RES | `rg` | No new FAIL path |
| NotImplemented | Only `QuestStateManager.cs:1637` | Narrow; callers not traced |
| Result as data | `CreateCharacterHandler:459,519`, `WarpPartyWarpHandler:27`, none new | Fine |
| F05 | Only `S2C*`/`L2C*` and `ServerRes` call `ReadServerResponse`, none nested | A client cannot reach it through a C2S reader |
| F09 | Longest string in the streams 587 bytes; in 958 asset files 207 bytes | Nothing currently sent changes |
| W16 | Only `QuestPlayEndHandler` sets the field; clamped before the cast | No overflow path by reading |
| W02 | `0xb67c50` scans 16 slots, jumps past the insert when full | Bounded by reading; jump target unread |
| F11 | Old key combined the same 3 fields; `Consumer` keys on `PacketId` | Fine by reading |
| Close | `Receive` on the lane thread; `Disconnect` idempotent; pending receive defers finalization | No lane deadlock found, by reading decompiled `Arrowgene.Networking` 2.1.7 |
| F08 test | Real `TcpServer.Send(null)` dereferences `data.Length`: recorder's failure matches | T004a's open question answered |

## Not checked

RES before close on a real socket (a RES queued behind an in-flight send could be lost); a category 6 catch-up flood; `0x4cf380` on a very large time; a canned dump with `Error != 0` read through direct `Read(IBuffer)`, letting `ResponseEndsAtError` escape, or using a changed structure; F10 independent walk; mutation of the new tests, the 21 + 3 pins; inline hex in test files; hot-path performance; a flood; `develop` comparison of the canary (needs the seam commit).

## T005b must cover

Apply F1's fix first. Then: full login and game-select with the real client, including W11, W01, W04; moving between servers (0.5.1); one error path and one with the once flag set (F06); one quest end, which screen shows the time and how a long time formats (W16); a category 6 achievement, watching the notices (W02); a failed challenge from a test client, confirming the RES arrives before the close.

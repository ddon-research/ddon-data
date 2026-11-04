010 T004b: patch part 2: wire layouts

Objective: continue `fix/packet-handling` in `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Clean` (head `c423c48b`): the server's layouts match the PC 03040008 client where the ruling says, each with a test built from real capture bytes. Read `specs/010-server-packet-fixes/tasks.md` § Ruling, `research/T003-pc-evidence.md` (verdict table, general rule, F02's trap), `research/T002-differential.md` § 3-5, `research/T004a-patch.md` (test seam), `T001-candidates.tsv`. One commit per row or small group, plain sentence subjects, so a maintainer can drop any. No renames, no refactor.

**Client-visible errors first**
1. **W02** 27.8.16: element {u32, u8}, the u8 from `AchievementAsset.Category`, after checking the enum values match the client's (`0x7c2f80` branches on 6). `S2CAchievementCompleteNtc.cs:22`.
2. **W16 + N1**: `CDataContentsPlayEnd.cs:26-32`: the time goes in the 7th u32, where the client reads it (`0xbd4b56`); `QuestPlayEndHandler.cs:42` uses `TotalMilliseconds`, not the 0-999 component. Check the type and overflow.
3. **F09**: `WriteMtString`: T003: above 0x800 bytes `Read_MtString` returns 0 and the client disconnects; T004a: chat, mail and pawn comment text relays with no cap. Truncate at 0x800 bytes on a UTF-8 boundary in the writer, one place; read `0x8bc5b0`'s limit in T003 exactly (inclusive or exclusive). Null writes length 0, as the client's writer does. Runtime writes only; a CLI re-encode of an over-long capture, if any, is reported.
4. **W21**: decide by looking: compare captures' `+20` in shop JSON (`packets/decrypted_json`, bounded, `rg -l`/`jq` on the ids T003 names) with what the server knows about those goods. If the data says which goods need the line, fix it; otherwise leave it and write down what is missing. Do not guess.

**Harmless, wire should match**
5. **W01** 0.1.2 `S2CConnectionLoginRes.cs:19`: write a bool. Every game login: the frame must equal the capture's shape; a test compares with a captured frame. **N2**: must not be true while u16 (moot after this).
6. **W03** 3.0.16: trailing u32 as captured. **W04** 2.1.2: u16 (T003: PC reads u16). **W10, W11** challenge sizes: reader 1.0.1, 44.0.1 and writers 1.0.2, 44.0.2: 62 bytes where the PC has 62, with T004a's R06 guard kept. The 304-byte first-packet size must stay right. **W12** `CDataCraftProgress` element as `CDataCommonU32` where the list is sent empty today: check the writer's other users first.
7. **62.33.2** `CDataSeasonDungeonBuffEffectReward.cs:24`: write `Level`. **31.17.2** remove the excess bool from the RES; 31.17.1 reads the client's bool (kept unused; storing it is a feature).
8. **Readers** (CLI and annotated dumps only; no running-server effect): W08 14.11.16, W09 0.1.1 and 0.5.1, W14 50.1.1, W17 13.16.2, 11.4.2, 11.60.16 read what the PC writes. The handlers stay as they are.
9. **F05**: `ReadServerResponse`: T002 § 4: a u32 `Result` still overruns on 22 of 63 captures, stopping after `Error` reads all 63; the client stops there too. Choose the smallest form covering all 492 call sites, for example a guard returning the object early through a helper, or the 4 guards plus u32, and say why. No running-server effect.

**Do not touch**: F02, W05, W06, W15, W22, D08, T05, R08, renames.

Gates, in the clone: Debug and Release build and test as T004a; warnings not above 520; 125 plus yours pass; each new test fails before its commit (list the runs). Differential harness on a throwaway branch: the expected changes only: list per id old class -> new class, every id that moved must be in this brief; `agrees` rises; nothing that agreed now differs; 63 `Error != 0` captures no longer throw. For W01, W03, W04, W10, W11 and 62.33.2 show re-encode now equals the raw bytes on all captures, or explain any remainder.
Commits in the clone stay local: no push.

Report `specs/010-server-packet-fixes/research/T004b-patch.md`: row -> commit -> test -> before/after; the W21 decision; the differential's before and after. Owns: the clone (`fix/packet-handling`, throwaway branches), `specs/010-server-packet-fixes/research/T004b-*`. Never touch: packet data, patterns, `docs/`, other clones, other work here.
Done: signed report commit in ddon-data with `git commit -m <msg> -- <paths>`; receipt with "For Sam's inspection" (what a served client now sees differently, per row). Stop: budget 90 min of work time; past 300k context, commit what passes and end `cut short:` with the next row. Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

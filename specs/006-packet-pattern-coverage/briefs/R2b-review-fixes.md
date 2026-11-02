006 R2b: fix the R2 review findings (T005-T008 patterns, report errata)

Objective: fix the five findings of the R2 review (quoted; the reviewer's message is not in the
repository):

F1. `include/Pawn.hexpat:287-292` and T007 § 1.1 (line 85) say items 30-32 of `CDataPawnInfo`
    (u8[64], u32 x5, SpSkill list) are "the same three additions as Context's CDataContextPawnInfo
    (V)". `include/Context.hexpat:316-322` (PC 0x75f8d0) has only the reaction list, `unk_u8[64]` and
    `unk_SpSkillList`, no u32 x5 (the 35.3.16 export fits with those two). Fix the comment: two of
    the three are shared; the u32 x5 (PC 0x772e80) has only the PawnInfo reader behind it.
F2. `include/Quest.hexpat:647-654` names the five `CDataTimeGainQuestList` bools by PS4 position
    (IsNoTimeup, IsJoinCharacter, IsJoinPawn, IsJoinSupportPawn, unk_bool). Capture
    `stream85-marked.pcapng_tcp-stream-11/138774_S2C_QUEST_GET_END_CONTENTS_GROUP_RES_…11_10_2.json`
    gives IsJoinCharacter false beside IsJoinPawn/IsJoinSupportPawn true and JoinPawnNum 3, which is
    implausible; the server order (IsNoTimeup, Unk0, IsJoinCharacter, IsJoinPawn, Unk1) reads it as
    true. The order is not settled by code: rename all five to `unk_bool_0..4` with both candidate
    readings in a comment (I), and add an open item "settle from the PC consumer of the element".
F3. Server names reach exported keys behind an `unk_` prefix: `Pawn.hexpat:279` type
    `CDataPawnTrainingProfile` / field `unk_TrainingProfile` (`:325`); `Quest.hexpat:657-658`
    `unk_Restriction`, `unk_RequirementList` (types at `:621`, `:637` follow the server too). Use neutral
    names (e.g. `unk_u32x5`, `unk_List_0`; types `CDataPawnInfo_unk_0` or similar) with the server name
    only in a `// server: <name> (lead)` comment. Make the README naming rule say that the `unk_`
    suffix carries no server name either.
F4. `Quest.hexpat:400-407` `CDataQuestDeliveryItem.ItemNum`/`NeedNum`: add the basis (PS4 element
    {u32 ItemId, u16 Num}, T005 § 1.1 row 23) and mark what is inferred; rename to `unk_*` what has no
    basis.
F5. `include/Character.hexpat:72-73`: add 8.37.16 (via `CDataPartyMember`) to the users comment of
    `CDataCharacterListElement`.
Report slip: T008 § 2.7 line 164 gives `aStage::move_menu_warp 0x107bd`, not a PS4 VA (likely an
offset): add a dated "## Errata (R2, 2026-11-02)" section to T008 (and the F1 sentence to T007's
errata section); do not rewrite the original text.

Re-export every pattern whose JSON keys change (F2, F3, F4: find the users of the touched types),
show by a 2-file-per-pattern sample that only the renamed keys differ (values identical), and that
every file still fits.
Owns: the named includes and the patterns that need it, the packets README, the re-exported JSON, the
errata sections of T007/T008. Never touch raws, client/, other specs; `tasks.md` is the coordinator's.
Commit with `git commit -m <msg> -- <paths>`; long lists via `git update-index --add --remove -z --stdin`.
Libraries: plbatch via `packets/imhex-export.sh`; jq / stdlib Python for the sample.
Done: signed commits; re-export counts and fit; sample result (keys only); `bash tools/check.sh
--since <base>`; receipt from `receipt.py --print` with "For Sam's inspection" (old -> new key per
renamed field, per pattern file count). Stop: budget 60 min of work time; finish the scope.
Base: the head when you start.

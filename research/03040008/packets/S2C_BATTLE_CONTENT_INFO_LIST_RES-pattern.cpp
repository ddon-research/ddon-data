// 71.22.2 S2C_BATTLE_CONTENT_INFO_LIST_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T004-batches-B1-B4.md § 71.22.2.
// PC handler 0x7c5220 cSeedGameSvConnection::OnPacket_BATTLE_CONTENT_INFO_LIST_RES (V name), reader
// 0x8006f0: RES header, list 0x759850 of 0x759910 {u32, MtString, list 0x759ac0 {u32, MtString, u32},
// list 0x759990 {u32, u32, list 0x75e8e0}, list 0x75e8e0, list 0x75e8e0}, list 0x75beb0 {0x75bdc0
// {u32, s64, bool, bool, u8, u32 x3, u8, s64, u32, u32}, list 0x75bf90 {u32, u8}} (V).
// Server: S2CBattleContentInfoListRes and its CDataBattleContent* classes, same order and widths (lead).
// PS4 counterpart: none (Season 3 group).
// Walk: 42/42 fit, slack 12; one content (Bitterblack Maze) with 7 stages in 42/42.
// Body: s32 Error [, s32 Result, list, list].
// packet-id: 71.22.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

// Element of PC list 0x759ac0 {u32 +4, MtString +8, u32 +12} (V). Struct name: server (lead).
struct CDataBattleContentStage {
    u32 Id;             // T004 I (value: the ids that the progression and reward lists repeat, 294/294); server: Id (lead agrees)
    MtString StageName; // T004 I (value: Bitterblack Maze stage names); server: StageName (lead agrees)
    u32 Mode;           // T004 G (lead): server Mode (BattleContentMode); captured 6 and 7
};

// Element of PC list 0x759990 {u32 +4, u32 +8, list 0x75e8e0} (V). Struct name: server (lead).
struct CDataBattleContentStageProgression {
    u32 Id;             // T004 I (value: equals the StageList Id at the same index, 294/294); server: Id (lead agrees)
    u32 Tier;           // T004 G (lead): server Tier; captured 1-4
    // T004 I (value: every value is a StageList Id, 294/294 lists); server: ConnectionList (lead agrees)
    MtTypedArray<CDataCommonU32> ConnectionList;    // PC 0x75e8e0
};

// CDataBattleContentInfo: PC element reader 0x759910 of list 0x759850 (V). Struct name: server (lead).
struct CDataBattleContentInfo {
    // T004 I (value: 2 for the Bitterblack Maze (ContentName), the server's GameMode.BitterblackMaze;
    // lead agrees)
    u32 GameMode;
    MtString ContentName;   // T004 I (value: "Bitterblack Maze" in Japanese); server: ContentName (lead agrees)
    MtTypedArray<CDataBattleContentStage> BattleContentStageList;                   // PC 0x759ac0
    MtTypedArray<CDataBattleContentStageProgression> BattleContentStageProgressionList;    // PC 0x759990
    // T004 I (value: 126/126 item ids, ITEM_CATEGORY_MATERIAL); server: RareItemAppraisalList (lead)
    MtTypedArray<CDataCommonU32> RareItemAppraisalList;     // PC 0x75e8e0
    // T004 I (value: 1,176/1,176 item ids, 798 equipment); server: ItemTakeawayList (lead)
    MtTypedArray<CDataCommonU32> ItemTakeawayList;          // PC 0x75e8e0
};

// PC reader 0x75bdc0 {u32 +4, s64 +8, bool +16, bool +17, u8 +18, u32 +20, +24, +28, u8 +32, s64 +40,
// u32 +48, u32 +52} (V). Struct name: server CDataBattleContentSituationData (lead).
struct CDataBattleContentSituationData {
    u32 GameMode;           // T004 I (value: 2, as CDataBattleContentInfo.GameMode); server: GameMode (lead agrees)
    s64 StartTime;          // T004 G (lead): server StartTime; captured 0
    bool RewardReceived;    // T004 G (lead): server RewardReceived; captured 0
    bool unk_bool;          // T004 open, kept unk: captured 0; server: Unk3 (lead)
    u8 RewardBonus;         // T004 G (lead): server RewardBonus; captured 1
    u32 ReportReset;        // T004 G (lead): server ReportReset; captured 0
    u32 ReportSearchResults;    // T004 G (lead): server ReportSearchResults; captured 0
    u32 unk_u32_0;          // T004 open, kept unk: captured 0, 23, 1; server: Unk7 (lead)
    u8 unk_u8;              // T004 open, kept unk: captured 0; server: Unk8 (lead)
    // T004 open, kept unk: Unix seconds 2019-07-20/2019-08-07 or 0 (unk_u32_0 is 0 exactly when this
    // is 0, 42/42); server: Unktime (lead, "reset time?")
    s64 unk_s64;
    u32 ContentId;          // T004 G (lead): server ContentId; captured 0 in 42/42
    u32 unk_u32_1;          // T004 open, kept unk: captured 0; server: Unk11 (lead)
};

// Element of PC list 0x75bf90 {u32 +4, u8 +8} (V). Struct name: server (lead).
struct CDataBattleContentAvailableRewards {
    u32 Id;                 // T004 I (value: a StageList Id, 294/294); server: Id (lead agrees)
    u8 Amount;              // T004 G (lead): server Amount; captured 1
};

// Element of PC list 0x75beb0 {0x75bdc0, list 0x75bf90} (V). Struct name: server (lead).
struct CDataBattleContentStatus {
    CDataBattleContentSituationData BattleContentSituationData;     // PC 0x75bdc0
    MtTypedArray<CDataBattleContentAvailableRewards> BattleContentAvailableRewardsList;    // PC 0x75bf90
};

struct S2C_BATTLE_CONTENT_INFO_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataBattleContentInfo> BattleContentInfoList;     // PC 0x759850; server name (lead)
        MtTypedArray<CDataBattleContentStatus> BattleContentStatusList; // PC 0x75beb0; server name (lead)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_BATTLE_CONTENT_INFO_LIST_RES packet @ 0x00;

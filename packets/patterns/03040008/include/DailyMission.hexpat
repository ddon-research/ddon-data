// Group 72 DAILY_MISSION ("Reward Mission") CData of client 03040008 (PC, Season 3), shared by the
// daily mission packet patterns (72.0.2, 72.3.2).
//
// Source: specs/008-remaining-packets/research/T004-batches-B1-B4.md § 3 and § 4. "PC 0x..." is the
// reader VA in the PC 03040008 database (image base 0x400000). No PS4 02020005 type and no server
// (Arrowgene) structure exists: every name is the T004 one, marked I (value correlation in the
// captures and client/03040008 data) or G (context: the UI text in
// client/03040008/ui/uGUIDailyMission/ui/00_message/**.gmd.json). Comments read `// T004 <mark>: <basis>`.
// The consumer 0x580b90 copies the lists into the mission manager; field consumers were not traced.
// Includes Packet.hexpat and Mail.hexpat (CDataMailAttachmentList, CDataMailOptionCourseInfo);
// neither includes this file.
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"
#include "Mail.hexpat"

// Element of PC list 0x762960 {u32 +4, u32 +8} (V). Struct name G (context).
struct CDataDailyMissionRewardItem {
    // T004 G (context; value consistent: 7 distinct, chance 0.57; 1,880/1,880 values over 72.0.2/72.3.2 are item ids of
    // base/etc/itemlist.ipa.json, e.g. 24727 the White Dragon daily medal, 23502-23505 4th
    // anniversary furniture)
    u32 ItemId;
    u32 Num;        // T004 G (context: 1-20 beside an item id)
};

// E_WALLET_POINT_TYPE (Character.hexpat, PS4 DWARF nCharacter::E_WALLET_POINT_TYPE, declared __int32)
// read as u32: the 0x762a50 element reads its type with Read_u32, while CDataWalletPoint reads a u8, and
// an ImHex enum has one width. Same names and values as Character.hexpat (T007).
enum E_WALLET_POINT_TYPE_U32 : u32 {
    WALLET_POINT_TYPE_INVALID = 0x0,
    WALLET_POINT_TYPE_GOLD = 0x1,
    WALLET_POINT_TYPE_RIM = 0x2,
    WALLET_POINT_TYPE_ORB = 0x3,
    WALLET_POINT_TYPE_TICKET = 0x4,
    WALLET_POINT_TYPE_GP = 0x5,
    WALLET_POINT_TYPE_SUPPORT = 0x6,
    WALLET_POINT_TYPE_JP_RESET = 0x7,
    WALLET_POINT_TYPE_CP_RESET = 0x8,
    UNK_9 = 0x9,
    UNK_10 = 0xA,
    UNK_11 = 0xB,
    UNK_12 = 0xC,
    UNK_13 = 0xD,
    UNK_14 = 0xE,
    UNK_15 = 0xF,
    UNK_16 = 0x10
};

// Element of PC list 0x762a50 {u32 +4, u32 +8} (V). Struct name G (context).
struct CDataDailyMissionRewardWallet {
    // T004 G (context: a wallet type beside a value; value consistent: 2 distinct, 4 (819) and 12 (585));
    // T007 (T006 F2): values named by the PS4 DWARF enum nCharacter::E_WALLET_POINT_TYPE as in
    // Character.hexpat (V names for 1-8: 4 WALLET_POINT_TYPE_TICKET; 12 stays UNK_12), read as u32 here
    // (E_WALLET_POINT_TYPE_U32 below); server: WalletType SilverTickets / CustomMadeServiceTickets (lead)
    E_WALLET_POINT_TYPE_U32 Type;
    u32 Value;      // T004 G (context: 1-10 beside a wallet type)
};

// CDataDailyMissionReward: PC reader 0x762640 {u32 +4, u32 +8, s64 +16, s64 +24, list 0x762960,
// list 0x762a50, MtString +72, CDataMailAttachmentList 0x76e2f0 +76} (V). Struct name G (context).
struct CDataDailyMissionReward {
    // T004 I (value, 30 distinct: equals the owning mission's MissionId in 3,393/3,393 72.0.2 missions; 0 in the
    // 72.3.2 event mission)
    u32 MissionId;
    u32 unk_u32;    // T004 open, kept unk: captured 999 (72.0.2, 3,393/3,393) and 0 (72.3.2)
    s64 unk_s64_0;  // T004 open, kept unk: captured 0 everywhere
    s64 unk_s64_1;  // T004 open, kept unk: captured 0 everywhere
    MtTypedArray<CDataDailyMissionRewardItem> ItemList;         // PC 0x762960; T004 G (context)
    MtTypedArray<CDataDailyMissionRewardWallet> WalletPointList; // PC 0x762a50; T004 G (context)
    MtString unk_str;   // T004 open, kept unk: captured empty everywhere
    // T004 I (same structure: PC 0x76e2f0 is the mail attachment list reader); GP list captured
    // once (Type 4, Num 1), the other lists empty
    CDataMailAttachmentList AttachmentList;
};

// CDataDailyMission: PC element reader 0x762530 of list 0x762460 {u32 +8, u32 +12, u32 +16,
// 0x762640 +24, MtString +184, +188, +192, u32 +196, u8 +200, s64 +208, s64 +216, u32 +224} (V).
// Struct name G (context). Users: 72.0.2 (two lists), 72.3.2.
struct CDataDailyMission {
    // T004 I (value, 30 distinct: the ids that 72.1.16 and 72.2.1 name, 121/121, and Reward.MissionId 3,393/3,393)
    u32 MissionId;
    // T004 I (value, 10 distinct: 1-9 match the purpose texts of daily_mission/purpose.gmd DAILY_MISSION_PURPOSE_<n>
    // with the mission text, 9/9 values, e.g. 3 "clear high difficulty dungeon", 7-9 "clear Reward
    // Mission <VAL> times"; 0 in the time event mission)
    u32 Purpose;
    // T004 I (value, 16 distinct: State 2 and 3 only with Progress >= this, State 1 only with Progress < it, 3,393/3,393)
    u32 TargetNum;
    CDataDailyMissionReward Reward;     // PC 0x762640 (V)
    MtString Text;      // T004 I (value, 10 distinct: the mission text, e.g. "clear a quest <daily update>")
    MtString IconUrl;   // T004 I (value, 10 distinct: .../daily_icon_000nn.jpg URLs)
    MtString ImageUrl;  // T004 I (value, 10 distinct: .../daily_image_000nn.jpg URLs)
    u32 Progress;       // T004 I (value, 34 distinct: 0..TargetNum; see TargetNum)
    // T004 I (value, 4 distinct: 1 in progress, 2 achieved (72.1.16 moves 1 -> 2, 113/113), 3 received (72.2.1
    // moves 2 -> 3, 8/8); gmd "Receivable"/"Received"); 0 open (231 missions with Progress 0, and the
    // event mission at 4/4)
    u8 State;
    // T004 I (value, 51 distinct: Unix seconds; EndDate - StartDate is 24 h for texts marked <daily update>
    // (1,053/1,053), 168 h for <weekly update> (2,223/2,223), 840 h for <5-weekly update> (117/117))
    s64 StartDate;
    s64 EndDate;        // T004 I (value, 57 distinct: see StartDate)
    // T004 G (context: 1-5 and 10 by purpose, 998-1000 for purposes 7-9, 50 for the event mission;
    // read as the list order)
    u32 SortNo;
};

// Element of PC list 0x7627f0: {vtable, ..., CDataMailOptionCourseInfo +8 (vtable 0x1b2662c, the
// one Read_CDataMailOptionCourseInfo_ 0x76e890 allocates), MtString +56} (V: u64, bool, u32 x3,
// MtString). Never captured non-empty. Struct name G (context).
struct CDataDailyMissionCourseReward {
    CDataMailOptionCourseInfo OptionCourseInfo;     // T004 I (same structure, vtable)
    MtString unk_str;   // T004 open, kept unk (code only)
};

// Element of PC list 0x7626e0 {u32 +4, list 0x7627f0 +8} (V). Never captured non-empty (72.0.2
// 117/117, 72.3.2 4/4). Struct name G (context).
struct CDataDailyMissionUnkCourseList {
    u32 unk_u32;        // T004 open, kept unk (code only)
    MtTypedArray<CDataDailyMissionCourseReward> unk_list;   // PC 0x7627f0; T004 open (code only)
};

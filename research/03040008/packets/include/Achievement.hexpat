// Achievement CData structures of client 03040008 (PC, Season 3) shared by the packet patterns.
//
// Source (transcribed, not re-derived): specs/006-packet-pattern-coverage/research/
// T012-achievement-equip-skill.md sections 1, 9, 10 and 19. "PC 0x..." is the reader VA in the PC
// 03040008 database (image base 0x400000); "PS4" names the PS4 02020005 reader and DWARF type, whose
// member names the fields carry (m_ and type prefix dropped, DWARF spellings kept) unless marked.
// Marks: V = read in IDA, I = inferred. Server C# (Arrowgene) names are leads only.
// Includes Packet.hexpat and Pawn.hexpat (CDataAchievementIdentifier; Pawn -> Login -> Character,
// Context, GP); none of them includes this file (no include cycle).
// Users: 27.0.2, 27.1.2, 27.2.2, 27.3.2, 27.4.1, 27.4.2, 27.8.16, 27.9.16.
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"
#include "Pawn.hexpat"

// CDataAchievementProgress: PC list reader 0x758810 (loc, not a function) {u32, u32, u32, u32, s64}
// (V); PS4 Read_CDataAchievementProgress_ 0x19f0970 {CAchievementIdentifier m_AchieveIdenfier, u32
// m_unCurrentNum, u32 m_unSeqence, s64 m_llCompleteDate}: same (V).
struct CDataAchievementProgress {
    CDataAchievementIdentifier AchieveIdenfier;   // DWARF spelling
    u32 CurrentNum;
    u32 Seqence;                                  // DWARF spelling
    s64 CompleteDate;
};

// CDataAchievementRewardProgress: PC list reader 0x758960 {u32, u32, u32, bool} (V); PS4 0x19f05f0
// {u32 m_unRewardId, u32 m_unCurrentNum, u32 m_unTargetNum, b8 m_bIsRecieved}: same (V).
struct CDataAchievementRewardProgress {
    u32 RewardId;
    u32 CurrentNum;
    u32 TargetNum;
    bool IsRecieved;                              // DWARF spelling
};

// CDataAchievementFurnitureReward: PC list reader 0x7585a0, element 0x7586a0 {u32 x5, bool} (V); PS4
// 0x19e6bd0 {u32 m_unRewardId, u32 m_unSortId, CAchievementIdentifier m_AchieveIdenfier, u32
// m_unFurnitureItemId, b8 m_bIsRecieved}: same (V).
struct CDataAchievementFurnitureReward {
    u32 RewardId;
    u32 SortId;
    CDataAchievementIdentifier AchieveIdenfier;   // DWARF spelling
    u32 FurnitureItemId;
    bool IsRecieved;                              // DWARF spelling
};

// CDataAchieveRewardCommon: PC list reader 0x7584b0, writer 0x77d160 {u8, u32} (V); PS4 0x19e6810
// {u8 m_ucType, u32 m_unRewardId}: same (V).
struct CDataAchieveRewardCommon {
    u8 Type;
    u32 RewardId;
};

// CDataAchievementCompleteElement (struct name I): the Season 3 element of 27.8.16, PC list reader
// 0x758720 {Read_u32 +4, Read_u8 +8} (V). PS4 sends a list of CDataCommonU32 (the achievement ids)
// and tests mCategory == 6 of its own achievement table; PC tests this u8 == 6 instead, so the u8 is
// the category (I, by that behaviour; captures 1-4). Server: S2CAchievementCompleteNtc writes CDataCommonU32 only
// (lead; contradicted by the PC reader, T012 20).
struct CDataAchievementCompleteElement {
    u32 AchievementId;                            // I: PS4 list of achievement ids
    u8 Category;                                  // Season 3; I: PC tests == 6 where PS4 tests mCategory
};

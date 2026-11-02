// Entry-board CData of client 03040008 (PC, Season 3) shared by the packet patterns of group 34
// ENTRY_BOARD.
//
// Source: specs/006-packet-pattern-coverage/research/T013-small-groups.md sections 1, 6, 8 and 16
// (T013b). Names are PS4 02020005 DWARF members (m_/type prefix dropped, V) unless marked (I) or
// `unk_*`; the PS4 recompilation PacketData/EntryBoard.h declares the same members. Users: 34.1.1,
// 34.1.2, 34.2.1, 34.2.2, 34.14.16. The Season 3-exclusive 34.0.x list element is not here (34.0.x
// is not patterned, see the README open items).
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"
#include "Character.hexpat"

// CDataEntryRecruitData (Season 3): PC list reader 0x765750, C2S writer 0x77f340 {u16, u32, list u8}
// (V); PS4 0x19fc7c0 {u16 m_usID, list CDataEntryRecruitJob {u8 m_ucjob}}: Season 3 adds the u32
// (0 in all 12 captured entries). server: Unk1 (lead). EnableJobList: PS4 m_EnableJobList (V, DDOORBIS.elf.h:71284,
// TC1); the PS4 element is CDataEntryRecruitJob, the PC u8 list reader the CDataCommonU8 one.
struct CDataEntryRecruitData {
    u16 ID;
    u32 unk_u32;
    MtTypedArray<CDataCommonU8> EnableJobList;
};

// CDataEntryItemParam: PC reader 0x7654b0, writer 0x77f260 (V); PS4 0x19fc370 / Write_ 0x1a33da0
// {b8 m_bPasswordOn, b8 m_bPawnOn, s32 m_nBottomEntryJobLevel, s32 m_nTopEntryJobLevel,
// u16 m_usRequiredItemRank, u8 m_ucItemRankType, u32 m_unItemRankCheckRoleType, u16 m_usMinEntryNum,
// u16 m_usMaxEntryNum, MtString m_wstrComment, m_EntryRecruitList}: same widths and order, Season 3
// recruit element (V).
struct CDataEntryItemParam {
    bool PasswordOn;
    bool PawnOn;
    s32 BottomEntryJobLevel;
    s32 TopEntryJobLevel;
    u16 RequiredItemRank;
    u8 ItemRankType;
    u32 ItemRankCheckRoleType;
    u16 MinEntryNum;
    u16 MaxEntryNum;
    MtString Comment;
    MtTypedArray<CDataEntryRecruitData> EntryRecruitList;
};

// CDataEntryMemberData (Season 3): PC list reader 0x765590, element 0x7656f0 {u16, bool, u32,
// CDataCharacterListElement (Season 3)} (V); PS4 0x19fc460 {u16 m_usID, b8 m_bIsReady,
// CCharacterListElement m_CharacterListElement}: Season 3 adds the u32 (0 in all 12 captured members).
// server: Unk0 (lead); the server names the bool EntryFlag (DWARF: m_bIsReady).
struct CDataEntryMemberData {
    u16 ID;
    bool IsReady;
    u32 unk_u32;
    CDataCharacterListElement CharacterListElement;
};

// CDataEntryItem (Season 3): PC list reader 0x765360, element 0x765420 (V); PS4 0x19fd460
// {u32 m_unID, m_Param, m_EntryMemberList, u16 m_usBoardRequiredAvgItemRank, u16 m_usTimeOut,
// u32 m_unLeaderPartyId}: Season 3 adds a trailing bool (0 in both captured items with members).
// server: Unk0 (lead); the server names the u32 PartyLeaderCharacterId (DWARF: m_unLeaderPartyId).
struct CDataEntryItem {
    u32 ID;
    CDataEntryItemParam Param;
    MtTypedArray<CDataEntryMemberData> EntryMemberList;
    u16 BoardRequiredAvgItemRank;
    u16 TimeOut;
    u32 LeaderPartyId;
    bool unk_bool;
};

// CDataEntryBoardItemSearchParameter (Season 3): PC writer 0x77f170 (u8 list writer 0x77e050) (V);
// PS4 Write_ 0x1a34100 {m_SearchGroups (CDataCommonU8), MtString m_wstrFirstName, m_wstrLastName,
// b8 m_bRankSetting, u32 m_unRankMin, m_unRankMax, m_unJob, b8 m_bIsNoPassword,
// u32 m_unRequiredItemRankMin, m_unRequiredItemRankMax}: Season 3 appends two u32 (0 in 3/3).
// server: Unk0, Unk1 (lead).
struct CDataEntryBoardItemSearchParameter {
    MtTypedArray<CDataCommonU8> SearchGroups;
    MtString FirstName;
    MtString LastName;
    bool RankSetting;
    u32 RankMin;
    u32 RankMax;
    u32 Job;
    bool IsNoPassword;
    u32 RequiredItemRankMin;
    u32 RequiredItemRankMax;
    u32 unk_u32_0;
    u32 unk_u32_1;
};

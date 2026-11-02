// Character-side CData structures of client 03040008 (PC, Season 3) shared by the packet patterns.
//
// Source (transcribed, not re-derived): specs/005-netmsg-patterns/research/P11a-old-patterns.md
// (shared-structure table, G6) and P11b-old-patterns.md (its extension). "PC 0x..." is the reader VA
// in the PC 03040008 database (image base 0x400000); "PS4" names the PS4 02020005 DWARF type.
// Marks: V = read in IDA, I = inferred. Enums come from PS4 DWARF only; values without a DWARF
// name are UNK_<value>. Server C# names are leads only and appear only as "server: <name>".
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"

// nCharacter::E_WALLET_POINT_TYPE (PS4 DWARF, __int32; values 1-8 named there). Read as u8 on the
// wire. PS4 DWARF names 9 only as WALLET_POINT_TYPE_MAX, a sentinel (DDOORBIS.elf.h:111944), so
// 9-16 stay UNK_<value> (server lead: HighOrbs, DominionPoints, AdventurePassPoints,
// UnknownTickets, BitterBlackMazeResetTicket / CustomMadeServiceTickets, GoldenDragonMark,
// SilverDragonMark, RedDragonMark).
enum E_WALLET_POINT_TYPE : u8 {
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

// CDataWalletPoint: PC list reader 0x77c5a0 {u8, u32} (V); PS4 CDataWalletPoint {u8 m_ucType,
// u32 m_unValue}. Users: CDataQuestOrderList, CDataSetQuestDetail, CDataDispelBaseItem.
struct CDataWalletPoint {
    E_WALLET_POINT_TYPE Type;
    u32 Value;
};

// CDataJobBaseInfo: PC reader 0x76b190 {u8, u8} (P11b shared table, V); PS4 CDataJobBaseInfo
// {u8 m_ucJob, u8 m_ucLv}.
struct CDataJobBaseInfo {
    u8 Job;
    u8 Lv;
};

// CDataCharacterName: read inline by PC 0x75ccf0 as two MtStrings (P11b 4, V); PS4
// CDataCharacterName {MtString m_wstrFirstName, MtString m_wstrLastName}.
struct CDataCharacterName {
    MtString FirstName;
    MtString LastName;
};

// CDataCommunityCharacterBaseInfo: read inline by PC 0x75ccf0 {u32, MtString x3} (V); PS4
// CDataCommunityCharacterBaseInfo {u32 m_unCharacterID, CDataCharacterName m_CharacterName,
// MtString m_wstrClanName}.
struct CDataCommunityCharacterBaseInfo {
    u32 CharacterID;
    CDataCharacterName CharacterName;
    MtString ClanName;
};

// CDataCharacterListElement: PC reader 0x75ccf0 (nPacket::Read_CDataCharacterListElement_), list
// reader 0x75cbd0 {u32, MtString x3, u16, u8, JobBaseInfo x2, MtString, u8} (P11b shared table, V).
// PS4 CDataCharacterListElement (and the PS4 recompilation, PacketData/Community.h) has the same
// members up to m_wstrMatchingPlofile and no trailing u8: the u8 is Season 3, name open. Users:
// CDataClanMemberInfo (31.29.2, 31.4.2), 18.0.2, CDataPartyMember (8.37.16), CDataCharacterListInfo
// (login character list), 2.7.16 (T009 5: the PS4 element without the u8 fails 107/111).
struct CDataCharacterListElement {
    CDataCommunityCharacterBaseInfo BaseInfo;
    u16 ServerID;
    u8 OnlineStatus;
    CDataJobBaseInfo CurrentJobInfo;
    CDataJobBaseInfo EntryJobInfo;
    MtString MatchingPlofile;   // PS4 DWARF spelling (m_wstrMatchingPlofile)
    u8 unk_u8;                  // Season 3 (PC 0x75ccf0), no PS4 member
};

// CDataCharacterLevelParam: PC reader 0x75cb00, 10 x u16 (T006 1.3, V); PS4
// Read_CDataCharacterLevelParam_, CDataCharacterLevelParam {u16 m_usAttack .. m_usGuts}: same widths,
// count and order (V). Users: 33.12.16, 33.13.16, 33.16.16, 33.17.16.
struct CDataCharacterLevelParam {
    u16 Attack;
    u16 MagAttack;
    u16 Defence;
    u16 MagDefence;
    u16 Strength;
    u16 DownPower;
    u16 ShakePower;
    u16 StunPower;
    u16 Constitution;
    u16 Guts;
};

// CDataLobbyMemberInfo: PC element reader 0x76d7f0 (list 0x76d6f0, read linearly) {u32, MtString x3,
// u32, u8, u8, u8} into a 0x24-byte element (u8 at +0x20, +0x21, +0x22) (T006 2.1, T003 9; V). PS4
// Read_CDataLobbyMemberInfo__0 0x1a2f460: {CDataCommunityCharacterBaseInfo
// m_CommunityCharacterBaseInfo, u32 m_unPawnId, u8 m_ucPlatform, u8 m_ucClientVersion,
// u8 m_ucSessionStatus, u8 m_ucOnlineStatus} (V). Season 3 reads 3 u8, PS4 4 (V by code).
// SessionStatus: 0.10.16 (SESSION_STATUS_NTC) writes the element's +0x21, the second u8 (T003 9, V
// by behaviour). Which of Platform/ClientVersion was dropped is open: the first u8 stays unk.
// OnlineStatus on the third is I (position: it follows SessionStatus as in PS4). The PS4 4-u8 body
// also fits every capture (T006 2.1): the 3-u8 count rests on the PC reader. User: 3.0.2.
struct CDataLobbyMemberInfo {
    CDataCommunityCharacterBaseInfo CommunityCharacterBaseInfo;
    u32 PawnId;
    u8 unk_u8;                  // PS4 Platform or ClientVersion (open); server: Unk0 "most likely Platform" (lead)
    u8 SessionStatus;           // V (T003 9: 0.10.16 writes +0x21)
    u8 OnlineStatus;            // I (position after SessionStatus, PS4 order); server: OnlineStatus (lead)
};

// CDataPartyMember: PC reader 0x771580 {CDataCharacterListElement 0x75ccf0, u8, s32, u32, bool x3,
// u8, u8[8] (0x757ce0), u8} (T007 1.3, V); PS4 Read_CDataPartyMember_ 0x1a2b2f0 {m_CharacterListElement,
// u8 m_ucMemberType, s32 m_nMemberIndex, u32 m_unPawnId, b8 m_bIsLeader, b8 m_bIsPawn,
// b8 m_bIsPlayEntry, u8 m_ucJoinState, u8 m_ucAnyValueList[8], u8 m_ucSessionStatus} (V). It differs
// from PS4 only by the list element's Season 3 trailing u8. User: 8.37.16.
struct CDataPartyMember {
    CDataCharacterListElement CharacterListElement;
    u8 MemberType;
    s32 MemberIndex;
    u32 PawnId;
    bool IsLeader;
    bool IsPawn;
    bool IsPlayEntry;
    u8 JoinState;
    u8 AnyValueList[8];
    u8 SessionStatus;
};

// CDataStatusInfo: PC reader 0x77a810 {u32, u32, u8, u32 x9} (T009 1.3 item 7, V); PS4 CStatusInfo
// {u32 m_unHp, m_unStamina, u8 m_ucRevivePoint, u32 m_unMaxHp, m_unMaxStamina, m_unWhiteHp,
// m_unGainHp, m_unGainStamina, m_unGainAttack, m_unGainDefense, m_unGainMagicAttack,
// m_unGainMagicDefense}: same widths and order (V). User: CDataCharacterInfo (2.0.2).
struct CDataStatusInfo {
    u32 Hp;
    u32 Stamina;
    u8 RevivePoint;
    u32 MaxHp;
    u32 MaxStamina;
    u32 WhiteHp;
    u32 GainHp;
    u32 GainStamina;
    u32 GainAttack;
    u32 GainDefense;
    u32 GainMagicAttack;
    u32 GainMagicDefense;
};

// CDataCharacterMessage: PC list reader 0x75cdc0, element {u32, MtString, u32, bool} (T009 1.3
// item 21, V); PS4 CDataCharacterMessage {u32 m_unMessageNo, MtString m_wstrMessage,
// u32 m_unEmotion, b8 m_bEmotoChat} (V).
struct CDataCharacterMessage {
    u32 MessageNo;
    MtString Message;
    u32 Emotion;
    bool EmotoChat;             // PS4 DWARF spelling (m_bEmotoChat)
};

// CDataCharacterMsgSet: PC list reader 0x75cee0, element {u32, MtString, list 0x75cdc0} (T009 1.3
// item 21, V); PS4 CDataCharacterMsgSet {u32 m_unSetNo, MtString m_wstrMsgSetName,
// MtTypedArray<CDataCharacterMessage>} (V).
struct CDataCharacterMsgSet {
    u32 SetNo;
    MtString MsgSetName;
    MtTypedArray<CDataCharacterMessage> CharacterMessageList;  // PC 0x75cdc0; field name I (element type)
};

// CDataShortCut: PC list reader 0x778990, element 0x778a80 {u32 x5, u8} (T009 1.3 item 22, V); PS4
// CDataShortCut {u32 m_unPageNo, m_unButtonNo, m_unShortcutID, m_unU32Data, m_unF32Data,
// u8 m_ucExexType} (V).
struct CDataShortCut {
    u32 PageNo;
    u32 ButtonNo;
    u32 ShortcutID;
    u32 U32Data;
    u32 F32Data;                // u32 on the wire (PS4 m_unF32Data)
    u8 ExexType;                // PS4 DWARF spelling (m_ucExexType)
};

// CDataCommunicationShortCut: PC list reader 0x75ea80, element {u32, u32, u8, u8, u32} (T009 1.3
// item 23, V); PS4 CDataCommunicationShortCut {u32 m_unPageNo, m_unButtonNo, u8 m_ucType,
// m_ucCategory, u32 m_unId} (V).
struct CDataCommunicationShortCut {
    u32 PageNo;
    u32 ButtonNo;
    u8 Type;
    u8 Category;
    u32 Id;
};

// CDataUpdateMatchingProfileInfo: PC list reader 0x77c0d0, element {u32, MtString} (T009 5, V); PS4
// CDataUpdateMatchingProfileInfo {u32 m_unCharacterID, MtString m_wstrComment} (V). User: 2.7.16.
struct CDataUpdateMatchingProfileInfo {
    u32 CharacterID;
    MtString Comment;
};

// CDataCharacterReleaseElement: PC list reader 0x75d050, element {u32} (T009 4, V); PS4
// Read_CDataCharacterReleaseElement_ {u32 m_unReleaseElementNo} (V). User: 2.6.16.
struct CDataCharacterReleaseElement {
    u32 ReleaseElementNo;
};

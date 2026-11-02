// Login-server CData structures of client 03040008 (PC, Season 3) shared by the login packet
// patterns (C2L_/L2C_).
//
// Source (transcribed, not re-derived): specs/006-packet-pattern-coverage/research/T002-login.md
// sections 6, 7, 9, 11 and 15. "PC 0x..." is the reader VA in the PC 03040008 database (image base
// 0x400000); "PS4" names the PS4 02020005 DWARF type, whose member names the fields carry unless
// marked. Marks: V = read in IDA, I = inferred, C = contradicted. Server C# names are leads only.
// The character-list types live here, not in Character.hexpat, because they need Context.hexpat
// (CDataEditInfo, EquipElementParam, CDataContextEquipData_unk_0, CDataContextBase_unk_0) and GP.hexpat; this file
// includes all of them, and none of them includes this one (no include cycle).
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"
#include "Character.hexpat"
#include "Context.hexpat"
#include "GP.hexpat"

// CDataURLInfo: PC list reader 0x77bbd0 {u32, MtString} (V); PS4 CDataURLInfo {u32 m_unType,
// MtString m_wstrUrl}.
struct CDataURLInfo {
    u32 Type;
    MtString Url;
};

// CDataLoginSetting: PC reader 0x887ab0 {u32, u32, u8, bool, u32, list 0x77bbd0, u32} (V); PS4
// CDataLoginSetting {u32 m_unJobLevelMax, u32 m_unClanMemberMax, u8 m_ucCharacterNumMax,
// b8 m_bEnableVisualEquip, u32 m_unFriendListMax, MtTypedArray<CDataURLInfo> m_UrlInfoList,
// u32 m_unNoOperationTimeOutTime}: same order and widths, no Season 3 change (V).
struct CDataLoginSetting {
    u32 JobLevelMax;
    u32 ClanMemberMax;
    u8 CharacterNumMax;
    bool EnableVisualEquip;
    u32 FriendListMax;
    MtTypedArray<CDataURLInfo> UrlInfoList;
    u32 NoOperationTimeOutTime;
};

// CDataGameServerListInfo: PC reader 0x768ae0 {u16, MtString x3, u32 x3, MtString, u16, bool} (V);
// PS4 CGameServerListInfo / CDataGameServerListInfo {u16 m_usId, MtString m_wstrName,
// MtString m_wstrBrief, MtString m_wstrTrafficName, u32 m_unTrafficLevel, u32 m_unMaxLoginNum,
// u32 m_unLoginNum, MtString m_wstrAddr, u16 m_usPort, b8 m_bIsHide}: PC agrees (V).
struct CDataGameServerListInfo {
    u16 Id;
    MtString Name;
    MtString Brief;
    MtString TrafficName;
    u32 TrafficLevel;
    u32 MaxLoginNum;
    u32 LoginNum;
    MtString Addr;
    u16 Port;
    bool IsHide;
};

// CDataErrorMessage: PC list reader 0x887990 {u32, u32, MtString, MtString} (V); PS4
// CDataErrorMessage {u32 m_unMessageID, u32 m_unErrorID, MtString m_wstrMessage,
// MtString m_wstrDevelopMessage} (V).
struct CDataErrorMessage {
    u32 MessageID;
    u32 ErrorID;
    MtString Message;
    MtString DevelopMessage;
};

// CDataMatchingProfile: PC reader 0x76ed10 {u8, u32, u8, u32, u32, u32, u32, MtString, bool} (V);
// PS4 Read_CDataMatchingProfile_ 0x19f2ff0, same sequence; DWARF {u8 m_ucEntryJob,
// u32 m_unEntryJobLevel, u8 m_ucCurrentJob, u32 m_unCurrentJobLevel, u32 m_unObjectiveType1,
// u32 m_unObjectiveType2, u32 m_unPlayStyle, MtString m_wstrComment, b8 m_bIsJoinParty} (V).
struct CDataMatchingProfile {
    u8 EntryJob;
    u32 EntryJobLevel;
    u8 CurrentJob;
    u32 CurrentJobLevel;
    u32 ObjectiveType1;
    u32 ObjectiveType2;
    u32 PlayStyle;
    MtString Comment;
    bool IsJoinParty;
};

// CDataEquipItemInfo: PC reader 0x766070 (list 0x765fb0) {u32, u8, u8, u16, u8, u8, list 0x765a90
// {u8, u32, u16}, list 0x765ba0 {u8, u8, u16, u16}, list 0x766210 {u8, u16}} (V). Season 3: PS4
// Read_CDataEquipItemInfo_ 0x19e36a0 reads {u8 m_ucEquipType, u8 m_ucEquipSlot, u32 m_unItemID,
// u8 m_ucColor, u8 m_ucPlusValue, list CDataEquipElementParam {u8 m_ucSlotNo, u32 m_unItemID}}, so
// no PS4 name carries over by position. ItemID, Color and PlusValue are I (width sequence); the
// u8/u8/u16 triple has no code-backed name (server: SafetySetting, EquipType, u16 EquipSlot, lead).
// The first two lists use the readers of Context.hexpat's EquipElementParam (0x765a90) and
// CDataContextEquipData_unk_0 (0x765ba0) (V); the third has the shape of CDataContextBase_unk_0 {u8, u16} but its own
// reader 0x766210 (Context uses 0x7605e0): shape only.
struct CDataEquipItemInfo {
    u32 ItemID;                 // I
    u8 unk_u8_0;
    u8 unk_u8_1;
    u16 unk_u16;
    u8 Color;                   // I
    u8 PlusValue;               // I
    MtTypedArray<EquipElementParam> unk_ElementList;     // PC 0x765a90
    MtTypedArray<CDataContextEquipData_unk_0> unk_List_0;   // PC 0x765ba0
    MtTypedArray<CDataContextBase_unk_0> unk_List_1;        // PC 0x766210, shape {u8, u16}
};

// CDataCharacterListInfo: PC reader 0x8878c0 (list 0x8877f0) (V): CDataCharacterListElement
// (0x75ccf0, Character.hexpat, with its Season 3 trailing u8), CDataEditInfo (0x764550,
// Context.hexpat), CDataMatchingProfile (0x76ed10), list of CDataEquipItemInfo (0x765fb0), list of
// CDataGPCourseValid (0x7674d0, GP.hexpat), u8, MtString, MtString, bool. PS4 CDataCharacterListInfo
// {CCharacterListElement, CEditInfo, CMatchingProfile, MtTypedArray<CDataEquipItemInfo> m_EquipList,
// MtTypedArray<CDataGPCourseValid> m_GpCourseValidList, u8 m_ucNextFlowType, MtString
// m_wstrClanName, MtString m_wstrClanShortName, b8 m_bIsClanMemberNotice}: same order (V).
struct CDataCharacterListInfo {
    CDataCharacterListElement CharacterListElement;
    CDataEditInfo EditInfo;
    CDataMatchingProfile MatchingProfile;
    MtTypedArray<CDataEquipItemInfo> EquipList;
    MtTypedArray<CDataGPCourseValid> GpCourseValidList;
    u8 NextFlowType;
    MtString ClanName;
    MtString ClanShortName;
    bool IsClanMemberNotice;
};

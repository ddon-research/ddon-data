// CDataCharacterInfo of client 03040008 (PC, Season 3): the character body of 2.0.2
// S2C_CHARACTER_DECIDE_CHARACTER_ID_RES.
//
// Source (transcribed, not re-derived): specs/006-packet-pattern-coverage/research/
// T009-mail-stamp-character.md sections 1.3 and 22. "PC 0x..." is the reader VA in the PC 03040008
// database (image base 0x400000); "PS4" names the PS4 02020005 DWARF type, whose member names the
// fields carry (m_ and type prefix dropped). Marks: V = read in IDA, I = inferred.
// Its own include because it needs Character, Context, Pawn, Job, Login and Server, and Login
// includes Character: no include cycle (none of those includes this file).
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"
#include "Character.hexpat"
#include "Context.hexpat"
#include "Login.hexpat"
#include "Pawn.hexpat"
#include "Job.hexpat"
#include "Server.hexpat"

// CDataCharacterInfo: PC reader 0x75c2a0 (T009 1.3, V); PS4 Read_CDataCharacterInfo_ 0x1a2f950,
// CDataCharacterInfo. Items 1-14 and 16-31 match the PS4 members in order (V), with the Season 3
// CDataEquipItemInfo (Login.hexpat) inside the two equip lists. Season 3 adds item 15, a list
// {u8, u16} read by 0x766210: the reader of CDataPawnInfo.unk_List (Pawn.hexpat) and of
// CDataEquipItemInfo's third list, EquipStatParam shape (Context.hexpat). The PS4 body (without
// item 15) fails 22/42 captures of 2.0.2, the 22 with a non-empty list (up to 17 elements).
// User: 2.0.2.
struct CDataCharacterInfo {
    u32 CharacterId;
    u32 UserId;
    u32 Version;
    MtString FirstName;
    MtString LastName;
    CDataEditInfo EditInfo;                                                 // PC 0x764550
    CDataStatusInfo StatusInfo;                                             // PC 0x77a810
    u8 Job;
    MtTypedArray<CDataCharacterJobData> CharacterJobDataList;               // PC 0x75c660
    MtTypedArray<CDataJobPlayPoint> PlayPointList;                          // PC 0x76c670
    MtTypedArray<CDataCharacterEquipData> CharacterEquipDataList;           // PC 0x75c190
    MtTypedArray<CDataCharacterEquipData> CharacterEquipViewDataList;       // PC 0x75c190
    MtTypedArray<CDataEquipJobItem> CharacterEquipJobItemList;              // PC 0x766120
    u8 JewelrySlotNum;
    MtTypedArray<EquipStatParam> unk_List;                                  // Season 3, PC 0x766210 {u8, u16}; server: EmblemStatList (lead)
    MtTypedArray<CDataCharacterItemSlotInfo> CharacterItemSlotInfoList;     // PC 0x75c570
    MtTypedArray<CDataWalletPoint> WalletPointList;                         // PC 0x77c5a0
    u8 MyPawnSlotNum;
    u8 RentalPawnSlotNum;
    MtTypedArray<CDataOrbPageStatus> OrbStatusList;                         // PC 0x7702d0
    MtTypedArray<CDataCharacterMsgSet> MsgSetList;                          // PC 0x75cee0
    MtTypedArray<CDataShortCut> ShortCutList;                               // PC 0x778990; field name I (PS4 member not in T009)
    MtTypedArray<CDataCommunicationShortCut> CommunicationShortCutList;     // PC 0x75ea80; field name I (PS4 member not in T009)
    CDataMatchingProfile MatchingProfile;                                   // PC 0x76ed10
    CDataArisenProfile ArisenProfile;                                       // PC 0x7596f0
    bool HideEquipHead;
    bool HideEquipLantern;
    bool HideEquipHeadPawn;
    bool HideEquipLanternPawn;
    u8 ArisenProfileShareRange;
    u8 OnlineStatus;
};

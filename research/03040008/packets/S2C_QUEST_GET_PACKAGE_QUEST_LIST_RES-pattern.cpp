// 11.5.2 S2C_QUEST_GET_PACKAGE_QUEST_LIST_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T003-batches-B5-B2.md § 11.5.2.
// 006 T005 § 7. PC handler 0x7f1bb0 (string
// cSeedGameSvConnection::OnPacket_QUEST_GET_PACKAGE_QUEST_LIST_RES, V name), reader 0x816830: RES header,
// u32, list 0x7704d0 of {u32, list 0x770d30 of 0x770e50 {u32, s32, s32, list u32 0x75e8e0, bool, bool, list
// 0x7708c0 of CDataQuestList 0x774530}} (V widths). PS4 counterpart: none (V).
// Walk: 146/146 fit, slack 7; the list is empty in every capture (elements code-only).
// Body: s32 Error [, s32 Result, u32, list].
// packet-id: 11.5.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Quest.hexpat"

// Element of PC list 0x770d30, reader 0x770e50 {u32, s32, s32, list u32, bool, bool, list} (V
// widths). Never captured. Struct name: server CDataPackageQuestDetail (lead; fields Unk0-Unk6).
struct CDataPackageQuestDetail {
    u32 unk_u32_0;                                   // T003 open (never captured); server: Unk0 (lead)
    s32 unk_s32_1;                                   // T003 open (never captured); server: Unk1 (lead)
    s32 unk_s32_2;                                   // T003 open (never captured); server: Unk2 (lead)
    MtTypedArray<CDataCommonU32> unk_u32_list;       // PC 0x75e8e0 (V); server: Unk3 (lead)
    bool unk_bool_0;                                 // T003 open (never captured); server: Unk4 (lead)
    bool unk_bool_1;                                 // T003 open (never captured); server: Unk5 (lead)
    // T003 I (same structure: PC 0x774530 = CDataQuestList, Quest.hexpat); server: Unk6 (lead)
    MtTypedArray<CDataQuestList> QuestList;          // PC 0x7708c0 (V)
};

// Element of PC list 0x7704d0 {u32, list 0x770d30} (V widths). Never captured. Struct name: server (lead).
struct CDataPackageQuestList {
    u32 unk_u32;                                     // T003 open (never captured); server: Unk0 (lead)
    MtTypedArray<CDataPackageQuestDetail> Details;   // T003 G (lead): server Details
};

struct S2C_QUEST_GET_PACKAGE_QUEST_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        // T003 I (value: 146/146 equal the preceding 11.5.1 request's u32: an echo); name open, kept unk;
        // server: Unk0 (lead)
        u32 unk_u32;
        // T003 G (lead): server PackageQuestList; empty in 146/146
        MtTypedArray<CDataPackageQuestList> PackageQuestList;   // PC 0x7704d0 (V)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_GET_PACKAGE_QUEST_LIST_RES packet @ 0x00;

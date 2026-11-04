// 64.0.2 S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11a-old-patterns.md section 2. PC handler 0x7e4dc0
// (string 0x1bd39d8), ctor 0x78a2d0 (64, 0, 2), reader 0x80f730 (V). PS4 counterpart: none (no
// Mandragora handler, reader or type in PS4 02020005). The layout matches the PC reader field for
// field; the field names are the earlier pattern's guesses (no DWARF, no PC string; the PC function
// names Read_CDataMyMandragora* are earlier user names, not evidence): treat them as leads.
// Body: s32 Error [, s32 Result, body] (P11a G1).
// packet-id: 64.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

// PC list 0x75bcd0 {u32, u32}.
struct CDataMyMandragoraFurnitureItem {
    u32 MandragoraId;
    u32 FurnitureItemId;
};

// PC list 0x75b360 {u32, u16}.
struct CDataMyMandragoraUnkItem {
    // T014b open (V store; no reader found), kept unk: 0x10dbff0 copies each list element (+52
    // list) into a 12-byte object: u32 +4
    u32 unk_u32;
    // T014b open (V store; no reader found), kept unk: same copy: u16 +8
    u16 unk_u16;
};

// PC 0x75bc70 {u32, u32, list, s64}.
struct CDataMyMandragoraUnkState {
    // T014b open (V store; no reader found), kept unk: 0x10dbff0 copies element +44 (struct +4) to
    // the manager slot table [387 + 10*index]; no reader found in the manager range
    u32 unk_u32_0;
    // T014b V (consumer); I (role: state input): copied to [388 + 10*index]; != 0 selects slot
    // state 5 (with a time) or 6 (without), == 0 allows state 2
    u32 unk_u32_1;
    MtTypedArray<CDataMyMandragoraUnkItem> unk_list;
    // T014b V (consumer); I (role: time): copied to [394..395 + 10*index] and compared with the
    // current time: >= now -> state 4
    s64 unk_s64;
};

// PC list 0x75bb10.
struct CDataMyMandragora {
    // T014b open (V store; no reader found), kept unk: handler 0x7e4dc0 passes each element (packet
    // +44 list) to 0x10dbff0, which copies +4 into the slot object +12 (slot index = MandragoraId
    // +12, < 4); no reader of the slot +12 found
    u32 unk_u32_0;
    // T014b open (V store; no reader found), kept unk: 0x10dbff0 copies +8 into the slot object +16
    u8 unk_u8;
    u32 MandragoraId;          // name guessed by the earlier pattern ("Maybe")
    MtString MandragoraName;
    // T014b V (consumer); I (role: state input): 0x10dbff0 copies +20 to slot +20; slot state 2 is
    // set when u32_2 != 0, this == 0 and UnkState.unk_u32_1 == 0
    u32 unk_u32_1;
    // T014b V (consumer); I (role: time): 0x10dbff0 copies +24 to slot +32 (qword) and compares it
    // with the current time (sGame +2856): >= now -> state 4; nonzero with UnkState.unk_u32_1 != 0
    // -> state 5
    s64 unk_s64;
    // T014b V (consumer); I (role: state input): 0x10dbff0 copies +32 to slot +40; 0 -> state 3
    // (when not in states 4..6)
    u32 unk_u32_2;
    CDataMyMandragoraUnkState unk_state;
};

// PC list 0x75b690 {u8, MtString}.
struct CDataMyMandragoraCraftCategory {
    u8 CategoryId;
    MtString CategoryName;     // UTF-8
};

// PC list 0x75b270 {u8, u32}.
struct CDataMyMandragoraUnkU8U32 {
    // T014b V (consumer); I (role: kind selector): 0x7e4dc0 copies each element (packet +84 list)
    // into a 12-byte object and, when the u8 is 5, stores the u32 at manager +1880
    u8 unk_u8;
    // T014b open (V store; no reader found), kept unk: value of the kind above; kind 5 goes to
    // manager +1880, read by no other function in the displacement scan
    u32 unk_u32;
};

// PC list 0x75b870 {u32, u32}.
struct CDataMyMandragoraFertilizerItem {
    u32 ItemId;
    u32 ItemNum;
};

// PC list 0x75b160 {u32, MtString, u32}.
struct CDataMyMandragoraBreedType {
    u32 BreedId;
    MtString BreedName;
    u32 DiscoveredBreedNum;    // name guessed by the earlier pattern ("Maybe")
};

// PC list 0x75b450 {u32, MtString}.
struct CDataMyMandragoraRarityLevel {
    u32 RarityId;
    MtString Rarity;
};

struct S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataMyMandragoraFurnitureItem> MandragoraFurnitureItemList;
        MtTypedArray<CDataMyMandragora> MandragoraList;
        MtTypedArray<CDataMyMandragoraCraftCategory> MandragoraCraftCategories;   // name guessed
        MtTypedArray<CDataMyMandragoraUnkU8U32> unk_list_3;
        MtTypedArray<CDataMyMandragoraFertilizerItem> MandragoraFertilizerItemList;
        u32 MandragoraCultivationMaterialMax;                                   // name guessed
        MtTypedArray<CDataMyMandragoraBreedType> MandragoraBreedTypeList;
        MtTypedArray<CDataMyMandragoraRarityLevel> RarityLevelList;
        MtTypedArray<CDataCommonU8> FreeMandragoraIdList;   // PC 0x75e9b0; name guessed
        // T014b open (V store; no reader found), kept unk: 0x7e4dc0 stores packet +188 at manager
        // +1904 (v6[476]); the displacement scan finds no other function using +1904 in the handler
        // and manager ranges
        u32 unk_u32;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES packet @ 0x00;

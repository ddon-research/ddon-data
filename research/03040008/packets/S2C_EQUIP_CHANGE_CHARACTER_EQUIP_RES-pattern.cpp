// 29.1.2 S2C_EQUIP_CHANGE_CHARACTER_EQUIP_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T012-achievement-equip-skill.md
// section 13 (1, 19 for the types).
// PC handler 0x7d47e0, reader 0x807910: header, list 0x7776e0, then 0x765f70 {Read_u8, list 0x766210
// {u8, u16}} (V). PS4 0x30f1a0: header, m_CharacterEquipList only. Season 3: + the 0x765f70 tail
// (CDataEquipChangeUnk); the PS4 body fits too (the tail is 5 bytes, inside slack): the PC reader
// decides.
// Walk: 5/5 fit, slack 6-10; 1 or 2 entries; tail Job 10 with an empty list in 5/5.
// Body: s32 Error [, s32 Result, list CDataS2CCharacterEquipInfo, CDataEquipChangeUnk (Season 3)].
// packet-id: 29.1.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Equip.hexpat"

struct S2C_EQUIP_CHANGE_CHARACTER_EQUIP_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataS2CCharacterEquipInfo> CharacterEquipList;   // PC 0x7776e0
        CDataEquipChangeUnk unk_0;                                     // Season 3, PC 0x765f70
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_EQUIP_CHANGE_CHARACTER_EQUIP_RES packet @ 0x00;

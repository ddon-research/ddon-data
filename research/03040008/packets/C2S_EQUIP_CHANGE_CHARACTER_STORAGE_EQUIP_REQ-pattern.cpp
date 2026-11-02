// 29.2.1 C2S_EQUIP_CHANGE_CHARACTER_STORAGE_EQUIP_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T012-achievement-equip-skill.md
// section 13 (1, 19 for the types).
// PC writer 0x8279c0 (29, 2, 1): writer 0x77d2d0, count + {MtString, u8, u8} (V). PS4
// Send_C2S_CHANGE_CHARACTER_STORAGE_EQUIP_REQ 0x19b6b20(MtTypedArray<CDataC2SChangeCharacterEquipInfo>
// in_ChangeCharacterEquipList) (V).
// Walk: 2/2 fit, slack 7; 1 entry each.
// Body: list CDataS2CCharacterEquipInfo (same members as PS4 CDataC2SChangeCharacterEquipInfo).
// packet-id: 29.2.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Equip.hexpat"

struct C2S_EQUIP_CHANGE_CHARACTER_STORAGE_EQUIP_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    MtTypedArray<CDataS2CCharacterEquipInfo> ChangeCharacterEquipList;   // PC writer 0x77d2d0
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_EQUIP_CHANGE_CHARACTER_STORAGE_EQUIP_REQ packet @ 0x00;

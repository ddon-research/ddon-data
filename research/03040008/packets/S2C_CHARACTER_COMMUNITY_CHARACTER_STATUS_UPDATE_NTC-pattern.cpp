// 2.7.16 S2C_CHARACTER_COMMUNITY_CHARACTER_STATUS_UPDATE_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T009-mail-stamp-character.md
// section 5.
// PC handler 0x7c7da0, reader 0x801f60, no error header: list 0x75cbd0 of CDataCharacterListElement
// (Season 3 trailing u8), list 0x77c0d0 of {u32, MtString} (V). PS4
// OnPacket_S2C_COMMUNITY_CHARACTER_STATUS_UPDATE_NTC 0x2f7ed0: m_UpdateCharacterList,
// m_UpdateMatchinfProfileList (V). The PS4 element (no u8) fails 107/111. Walk: 111/111 fit,
// slack 8-15.
// Body: list CDataCharacterListElement, list CDataUpdateMatchingProfileInfo (variable).
// packet-id: 2.7.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Character.hexpat"

struct S2C_CHARACTER_COMMUNITY_CHARACTER_STATUS_UPDATE_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    MtTypedArray<CDataCharacterListElement> UpdateCharacterList;                 // PC 0x75cbd0
    MtTypedArray<CDataUpdateMatchingProfileInfo> UpdateMatchinfProfileList;     // PC 0x77c0d0; PS4 DWARF spelling
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CHARACTER_COMMUNITY_CHARACTER_STATUS_UPDATE_NTC packet @ 0x00;

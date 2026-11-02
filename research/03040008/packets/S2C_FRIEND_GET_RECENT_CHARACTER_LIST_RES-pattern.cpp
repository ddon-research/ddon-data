// 16.6.2 S2C_FRIEND_GET_RECENT_CHARACTER_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T011-party-profile-friend.md
// section 11.
// PC handler 0x7d6840, reader 0x8089a0: header, list 0x75cbd0 (CDataCharacterListElement) (V). PS4
// 0x2fa830 {m_RecentCharacterList}: same except the Season 3 trailing u8 of the element (V).
// Walk: 41/41 fit, slack 11; the list is always empty (element code-only).
// Body: s32 Error [, s32 Result, list CDataCharacterListElement].
// packet-id: 16.6.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Character.hexpat"

struct S2C_FRIEND_GET_RECENT_CHARACTER_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataCharacterListElement> RecentCharacterList;  // PC 0x75cbd0
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_FRIEND_GET_RECENT_CHARACTER_LIST_RES packet @ 0x00;

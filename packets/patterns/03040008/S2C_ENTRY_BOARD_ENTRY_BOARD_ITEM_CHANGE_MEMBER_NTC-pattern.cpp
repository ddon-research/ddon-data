// 34.14.16 S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_CHANGE_MEMBER_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T013-small-groups.md
// section 8 (1 and 16 for the types).
// PC handler 0x7d2b70 -> 0x806be0: Read_bool, element 0x7656f0 (CDataEntryMemberData, Season 3), no
// header (V). PS4 OnPacket_S2C_ENTRY_BOARD_ITEM_CHANGE_MEMBER_NOTICE 0x3236b0 {u16 error, b8
// m_bEntryFlag, CEntryMemberData m_MemberData}, the only PS4 entry-board packet with bool + member
// data: match V. The PS4 element and the PS4 framing each fail 1/1.
// Walk: 1/1 fit; EntryFlag 1, ID 1, not ready, CharacterID 2184603.
// Body: bool EntryFlag, CDataEntryMemberData MemberData (no RES header).
// packet-id: 34.14.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "EntryBoard.hexpat"

struct S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_CHANGE_MEMBER_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    // Notice: the PC reader reads no RES header (T013 0).
    bool EntryFlag;
    CDataEntryMemberData MemberData;   // PC 0x7656f0
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_CHANGE_MEMBER_NTC packet @ 0x00;

// 34.6.16 S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_READY_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T013-small-groups.md
// section 7.
// PC handler 0x7d3960 (object tagged 34, 6, 16) -> 0x807330: Read_u32, Read_u16, no header; then
// sNetworkExt::setEntryBoardReadyWait(1), u16 * 30.0, sGUIExt::requestInfomation(.., 0xE, ..),
// requestSE_0(.., 0, 0x134) (V). PS4 OnPacket_S2C_ENTRY_BOARD_ITEM_READY_NOTICE 0x323ab0 {u16 error,
// u32 m_unMaxMember, u16 m_usTimeOut} with the same calls and SE id: match V by behaviour.
// The PS4 framing fails 1/1. Walk: 1/1 fit; MaxMember 1, TimeOut 120.
// Body: u32 MaxMember, u16 TimeOut (6 bytes, no RES header).
// packet-id: 34.6.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_READY_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    // Notice: the PC reader reads no RES header (T013 0).
    u32 MaxMember;
    u16 TimeOut;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_READY_NTC packet @ 0x00;

// 34.1.1 C2S_ENTRY_BOARD_ENTRY_BOARD_ITEM_LIST_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T013-small-groups.md
// section 6 (1 and 16 for the types).
// PC writer 0x840ec0 (34, 1, 1): u64, u32, u32, 0x77f170 (search parameter, Season 3 + u32 x2) (V).
// PS4 CPacket_C2S_ENTRY_BOARD_ITEM_LIST_REQ::WritePacket 0x1a34040 {u64 m_ullID, u32 m_unOffset,
// u32 m_unNum, m_SearchParam}: match V, Season 3 via the parameter (include/EntryBoard.hexpat).
// The PS4 body fits 3/3 too (the two u32 sit in the slack): the PC writer decides.
// Walk: 3/3 fit.
// Body: u64 ID, u32 Offset, u32 Num, CDataEntryBoardItemSearchParameter SearchParam.
// packet-id: 34.1.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "EntryBoard.hexpat"

struct C2S_ENTRY_BOARD_ENTRY_BOARD_ITEM_LIST_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u64 ID;
    u32 Offset;
    u32 Num;
    CDataEntryBoardItemSearchParameter SearchParam;   // PC 0x77f170
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_ENTRY_BOARD_ENTRY_BOARD_ITEM_LIST_REQ packet @ 0x00;
